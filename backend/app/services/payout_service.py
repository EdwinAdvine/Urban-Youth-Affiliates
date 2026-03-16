"""
Payout request management: creation, approval, and Paystack transfer initiation.
"""

import logging
from datetime import datetime, timezone
from decimal import Decimal

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.config import settings
from app.exceptions import ValidationError, NotFoundError, PaymentError
from app.models.payout_request import PayoutRequest, PayoutStatus
from app.models.affiliate_balance import AffiliateBalance
from app.models.affiliate_profile import AffiliateProfile, AffiliateStatus
from app.models.conversion import Conversion, ConversionStatus
from app.models.referral_link import ReferralLink

logger = logging.getLogger(__name__)


async def request_payout(
    db: AsyncSession,
    affiliate_id: int,
    amount: Decimal,
) -> PayoutRequest:
    # Check approved balance
    result = await db.execute(
        select(AffiliateBalance).where(AffiliateBalance.affiliate_id == affiliate_id)
    )
    balance = result.scalar_one_or_none()
    if not balance:
        raise ValidationError("Balance record not found")

    approved = balance.approved or Decimal("0")
    if amount > approved:
        raise ValidationError(f"Insufficient balance. Available: {approved}")

    min_threshold = Decimal(str(settings.min_payout_threshold))
    if amount < min_threshold:
        raise ValidationError(f"Minimum payout is KES {min_threshold}")

    # Get affiliate profile for recipient code
    result = await db.execute(
        select(AffiliateProfile).where(AffiliateProfile.user_id == affiliate_id)
    )
    profile = result.scalar_one_or_none()
    if not profile or profile.status != AffiliateStatus.approved:
        raise ValidationError("Affiliate account not approved for payouts")

    # Deduct from approved balance (hold)
    balance.approved = approved - amount
    balance.updated_at = datetime.now(timezone.utc)

    payout = PayoutRequest(
        affiliate_id=affiliate_id,
        amount=amount,
        status=PayoutStatus.pending,
        paystack_recipient_code=profile.paystack_recipient_code,
    )
    db.add(payout)
    await db.commit()
    await db.refresh(payout)
    logger.info(f"Payout request created: affiliate={affiliate_id} amount={amount}")
    return payout


async def approve_and_transfer(
    db: AsyncSession,
    payout_id: int,
    processed_by: int,
) -> PayoutRequest:
    result = await db.execute(select(PayoutRequest).where(PayoutRequest.id == payout_id))
    payout = result.scalar_one_or_none()
    if not payout:
        raise NotFoundError("Payout request")

    if payout.status != PayoutStatus.pending:
        raise ValidationError(f"Payout already in status: {payout.status}")

    if not payout.paystack_recipient_code:
        raise PaymentError("Affiliate has no Paystack recipient code. Ask them to add bank details.")

    # Initiate Paystack transfer
    from app.services.payments.paystack import initiate_transfer
    transfer_code = await initiate_transfer(
        recipient_code=payout.paystack_recipient_code,
        amount_kes=float(payout.amount),
        reason=f"Y&U Affiliates payout #{payout.id}",
    )

    payout.status = PayoutStatus.processing
    payout.paystack_transfer_code = transfer_code
    payout.processed_by = processed_by

    # Update affiliate paid_out balance
    result = await db.execute(
        select(AffiliateBalance).where(AffiliateBalance.affiliate_id == payout.affiliate_id)
    )
    balance = result.scalar_one_or_none()
    if balance:
        balance.paid_out = (balance.paid_out or Decimal("0")) + payout.amount
        balance.updated_at = datetime.now(timezone.utc)

    # Update affiliate profile last_payout_at
    result = await db.execute(
        select(AffiliateProfile).where(AffiliateProfile.user_id == payout.affiliate_id)
    )
    profile = result.scalar_one_or_none()
    if profile:
        profile.last_payout_at = datetime.now(timezone.utc)

    await db.commit()
    await db.refresh(payout)
    logger.info(f"Payout {payout_id} transfer initiated: {transfer_code}")

    # Fire notification (fail silently)
    try:
        from app.models.user import User
        from app.tasks.notifications import notify_payout_approved

        user_result = await db.execute(
            select(User).where(User.id == payout.affiliate_id)
        )
        affiliate_user = user_result.scalar_one_or_none()
        if affiliate_user and profile:
            notify_payout_approved.delay(
                user_id=affiliate_user.id,
                email=affiliate_user.email,
                full_name=profile.full_name or affiliate_user.email,
                amount=float(payout.amount),
            )
    except Exception:
        pass

    return payout


async def handle_paystack_webhook(db: AsyncSession, event: str, data: dict) -> None:
    """Handle Paystack transfer webhook events."""
    transfer_code = data.get("transfer_code")
    if not transfer_code:
        return

    result = await db.execute(
        select(PayoutRequest).where(PayoutRequest.paystack_transfer_code == transfer_code)
    )
    payout = result.scalar_one_or_none()
    if not payout:
        logger.warning(f"No payout found for transfer_code: {transfer_code}")
        return

    if event == "transfer.success":
        payout.status = PayoutStatus.paid
        payout.paid_at = datetime.now(timezone.utc)
        logger.info(f"Payout {payout.id} marked as paid")

    elif event in ("transfer.failed", "transfer.reversed"):
        payout.status = PayoutStatus.failed
        payout.failure_reason = data.get("gateway_response", event)

        # Refund approved balance
        result = await db.execute(
            select(AffiliateBalance).where(AffiliateBalance.affiliate_id == payout.affiliate_id)
        )
        balance = result.scalar_one_or_none()
        if balance:
            balance.approved = (balance.approved or Decimal("0")) + payout.amount
            balance.paid_out = max(
                Decimal("0"),
                (balance.paid_out or Decimal("0")) - payout.amount,
            )
            balance.updated_at = datetime.now(timezone.utc)
        logger.warning(f"Payout {payout.id} failed: {payout.failure_reason}")

        # Fire failure notification
        try:
            from app.models.user import User
            from app.models.affiliate_profile import AffiliateProfile as AffProfile
            from app.tasks.notifications import notify_payout_failed

            u_result = await db.execute(
                select(User).where(User.id == payout.affiliate_id)
            )
            p_result = await db.execute(
                select(AffProfile).where(AffProfile.user_id == payout.affiliate_id)
            )
            aff_user = u_result.scalar_one_or_none()
            aff_profile = p_result.scalar_one_or_none()
            if aff_user:
                notify_payout_failed.delay(
                    user_id=aff_user.id,
                    email=aff_user.email,
                    full_name=(aff_profile.full_name if aff_profile else aff_user.email),
                    amount=float(payout.amount),
                    reason=payout.failure_reason or "",
                )
        except Exception:
            pass

    await db.commit()
