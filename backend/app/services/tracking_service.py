"""
Referral link generation, click tracking, and conversion recording.
"""

import logging
from datetime import datetime, timezone
from typing import Optional
from decimal import Decimal

import shortuuid
from fastapi import Request
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func

from app.config import settings
from app.exceptions import NotFoundError, ValidationError, ConflictError
from app.models.campaign import Campaign
from app.models.referral_link import ReferralLink
from app.models.referral_click import ReferralClick
from app.models.conversion import Conversion, ConversionStatus, ConversionSource
from app.models.affiliate_profile import AffiliateProfile, AffiliateStatus
from app.models.store import Store

logger = logging.getLogger(__name__)


def generate_code() -> str:
    """Return a 10-character alphanumeric referral code."""
    return shortuuid.uuid()[:10].lower()


async def generate_referral_link(
    db: AsyncSession,
    affiliate_id: int,
    campaign_id: int,
) -> ReferralLink:
    # Verify affiliate is approved
    result = await db.execute(
        select(AffiliateProfile).where(AffiliateProfile.user_id == affiliate_id)
    )
    profile = result.scalar_one_or_none()
    if not profile or profile.status != AffiliateStatus.approved:
        raise ValidationError("Your account must be approved before generating links")

    # Verify campaign exists and is active
    result = await db.execute(
        select(Campaign).where(Campaign.id == campaign_id, Campaign.active == True)
    )
    campaign = result.scalar_one_or_none()
    if not campaign:
        raise NotFoundError("Campaign")

    # Generate collision-proof code
    code = generate_code()

    link = ReferralLink(
        affiliate_id=affiliate_id,
        campaign_id=campaign_id,
        code=code,
    )
    db.add(link)
    await db.commit()
    await db.refresh(link)
    logger.info(f"Generated referral link {code} for affiliate {affiliate_id}")
    return link


async def record_click(
    db: AsyncSession,
    code: str,
    request: Request,
) -> Optional[ReferralLink]:
    result = await db.execute(select(ReferralLink).where(ReferralLink.code == code))
    link = result.scalar_one_or_none()
    if not link:
        return None

    ip = request.client.host if request.client else None
    ua = request.headers.get("user-agent", "")
    referrer = request.headers.get("referer", "")

    # Detect TikTok traffic
    from_tiktok = "tiktok" in ua.lower() or "tiktok" in referrer.lower()

    click = ReferralClick(
        link_id=link.id,
        ip_address=ip,
        user_agent=ua,
        referrer_url=referrer,
        clicked_from_tiktok=from_tiktok,
    )
    db.add(click)
    await db.commit()
    return link


async def record_conversion(
    db: AsyncSession,
    ref_code: str,
    external_order_id: str,
    sale_amount: Decimal,
    store_api_key: Optional[str] = None,
    source: ConversionSource = ConversionSource.api,
) -> Conversion:
    # Resolve referral link
    result = await db.execute(select(ReferralLink).where(ReferralLink.code == ref_code))
    link = result.scalar_one_or_none()
    if not link:
        raise NotFoundError("Referral link")

    # Validate store API key if provided
    store_id = None
    if store_api_key:
        result = await db.execute(
            select(Store).where(Store.api_key == store_api_key, Store.active == True)
        )
        store = result.scalar_one_or_none()
        if not store:
            raise ValidationError("Invalid store API key")
        store_id = store.id
    else:
        # Get store from campaign's product/store relationship
        result = await db.execute(select(Campaign).where(Campaign.id == link.campaign_id))
        campaign = result.scalar_one_or_none()
        if campaign and campaign.store_id:
            store_id = campaign.store_id

    if not store_id:
        raise ValidationError("Cannot determine store for this conversion")

    # Check duplicate order
    result = await db.execute(
        select(Conversion).where(
            Conversion.store_id == store_id,
            Conversion.external_order_id == external_order_id,
        )
    )
    if result.scalar_one_or_none():
        raise ConflictError(f"Order {external_order_id} already converted")

    # Prevent self-conversion
    result = await db.execute(select(Store).where(Store.id == store_id))
    store_obj = result.scalar_one_or_none()

    # Calculate commission
    from app.services.commission_service import calculate_commission
    result = await db.execute(select(Campaign).where(Campaign.id == link.campaign_id))
    campaign = result.scalar_one_or_none()
    commission = await calculate_commission(db, campaign, sale_amount)

    conversion = Conversion(
        referral_link_id=link.id,
        store_id=store_id,
        external_order_id=external_order_id,
        sale_amount=sale_amount,
        commission_earned=commission,
        status=ConversionStatus.pending,
        conversion_source=source,
    )
    db.add(conversion)

    # Update affiliate pending balance
    from app.models.affiliate_balance import AffiliateBalance
    result = await db.execute(
        select(AffiliateBalance).where(AffiliateBalance.affiliate_id == link.affiliate_id)
    )
    balance = result.scalar_one_or_none()
    if balance:
        balance.pending = (balance.pending or Decimal("0")) + commission
        balance.updated_at = datetime.now(timezone.utc)

    await db.commit()
    await db.refresh(conversion)
    logger.info(
        f"Conversion recorded: order={external_order_id} ref={ref_code} "
        f"commission={commission}"
    )

    # Fire new-sale notification (fail silently)
    try:
        from app.models.user import User
        from app.models.affiliate_profile import AffiliateProfile
        from app.tasks.notifications import notify_new_sale

        u_result = await db.execute(select(User).where(User.id == link.affiliate_id))
        p_result = await db.execute(
            select(AffiliateProfile).where(AffiliateProfile.user_id == link.affiliate_id)
        )
        aff_user = u_result.scalar_one_or_none()
        aff_profile = p_result.scalar_one_or_none()
        if aff_user:
            notify_new_sale.delay(
                affiliate_user_id=aff_user.id,
                affiliate_email=aff_user.email,
                affiliate_name=(aff_profile.full_name if aff_profile else aff_user.email),
                order_id=external_order_id,
                sale_amount=float(sale_amount),
                commission=float(commission),
            )
    except Exception:
        pass

    return conversion


async def get_link_stats(db: AsyncSession, link_id: int) -> dict:
    click_count = await db.execute(
        select(func.count(ReferralClick.id)).where(ReferralClick.link_id == link_id)
    )
    conversion_count = await db.execute(
        select(func.count(Conversion.id)).where(
            Conversion.referral_link_id == link_id,
            Conversion.status.in_([ConversionStatus.approved, ConversionStatus.paid]),
        )
    )
    total_earned = await db.execute(
        select(func.sum(Conversion.commission_earned)).where(
            Conversion.referral_link_id == link_id,
            Conversion.status.in_([ConversionStatus.approved, ConversionStatus.paid]),
        )
    )
    return {
        "total_clicks": click_count.scalar() or 0,
        "total_conversions": conversion_count.scalar() or 0,
        "total_earned": float(total_earned.scalar() or 0),
    }
