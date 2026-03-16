"""
Commission calculation and approval logic.
"""

import logging
from datetime import datetime, timezone
from decimal import Decimal
from typing import Optional

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.config import settings
from app.exceptions import NotFoundError, ValidationError
from app.models.campaign import Campaign, CommissionType
from app.models.conversion import Conversion, ConversionStatus
from app.models.affiliate_balance import AffiliateBalance

logger = logging.getLogger(__name__)


async def calculate_commission(
    db: AsyncSession,
    campaign: Optional[Campaign],
    sale_amount: Decimal,
) -> Decimal:
    """
    Calculate commission amount.
    Priority: product-level campaign > store-level campaign > global default.
    """
    if campaign is None:
        # Global default
        rate = Decimal(str(settings.default_commission_rate))
        return (sale_amount * rate).quantize(Decimal("0.01"))

    if campaign.commission_type == CommissionType.percent:
        commission = (sale_amount * campaign.rate).quantize(Decimal("0.01"))
    else:
        commission = campaign.rate.quantize(Decimal("0.01"))

    # Apply min sale threshold check
    if campaign.min_sale_amount and sale_amount < campaign.min_sale_amount:
        return Decimal("0.00")

    return commission


async def approve_conversion(
    db: AsyncSession,
    conversion_id: int,
    approved_by: int,
) -> Conversion:
    result = await db.execute(select(Conversion).where(Conversion.id == conversion_id))
    conversion = result.scalar_one_or_none()
    if not conversion:
        raise NotFoundError("Conversion")

    if conversion.status != ConversionStatus.pending:
        raise ValidationError(f"Cannot approve conversion in status: {conversion.status}")

    # Move from pending to approved balance
    result_link = await db.execute(
        select(type("ReferralLink", (), {"__tablename__": "referral_links"}))
    )
    from app.models.referral_link import ReferralLink
    result_link = await db.execute(
        select(ReferralLink).where(ReferralLink.id == conversion.referral_link_id)
    )
    link = result_link.scalar_one_or_none()
    if link:
        result_balance = await db.execute(
            select(AffiliateBalance).where(AffiliateBalance.affiliate_id == link.affiliate_id)
        )
        balance = result_balance.scalar_one_or_none()
        if balance:
            balance.pending = (balance.pending or Decimal("0")) - conversion.commission_earned
            balance.approved = (balance.approved or Decimal("0")) + conversion.commission_earned
            balance.updated_at = datetime.now(timezone.utc)

    conversion.status = ConversionStatus.approved
    conversion.approved_at = datetime.now(timezone.utc)
    conversion.approved_by = approved_by

    await db.commit()
    await db.refresh(conversion)
    logger.info(f"Conversion {conversion_id} approved by user {approved_by}")
    return conversion


async def reject_conversion(
    db: AsyncSession,
    conversion_id: int,
    approved_by: int,
    notes: Optional[str] = None,
) -> Conversion:
    result = await db.execute(select(Conversion).where(Conversion.id == conversion_id))
    conversion = result.scalar_one_or_none()
    if not conversion:
        raise NotFoundError("Conversion")

    if conversion.status != ConversionStatus.pending:
        raise ValidationError(f"Cannot reject conversion in status: {conversion.status}")

    # Remove from pending balance
    from app.models.referral_link import ReferralLink
    result_link = await db.execute(
        select(ReferralLink).where(ReferralLink.id == conversion.referral_link_id)
    )
    link = result_link.scalar_one_or_none()
    if link:
        result_balance = await db.execute(
            select(AffiliateBalance).where(AffiliateBalance.affiliate_id == link.affiliate_id)
        )
        balance = result_balance.scalar_one_or_none()
        if balance:
            balance.pending = max(
                Decimal("0"),
                (balance.pending or Decimal("0")) - conversion.commission_earned,
            )
            balance.updated_at = datetime.now(timezone.utc)

    conversion.status = ConversionStatus.rejected
    conversion.approved_by = approved_by
    conversion.notes = notes

    await db.commit()
    await db.refresh(conversion)
    return conversion
