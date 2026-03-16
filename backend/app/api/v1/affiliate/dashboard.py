from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func

from app.database import get_db
from app.deps import require_affiliate
from app.models.user import User
from app.models.affiliate_balance import AffiliateBalance
from app.models.referral_link import ReferralLink
from app.models.referral_click import ReferralClick
from app.models.conversion import Conversion, ConversionStatus
from app.models.affiliate_profile import AffiliateProfile

router = APIRouter()


@router.get("/affiliate/dashboard")
async def affiliate_dashboard(
    db: AsyncSession = Depends(get_db),
    user: User = Depends(require_affiliate),
):
    # Balance
    result = await db.execute(
        select(AffiliateBalance).where(AffiliateBalance.affiliate_id == user.id)
    )
    balance = result.scalar_one_or_none()

    # Profile status
    result = await db.execute(
        select(AffiliateProfile).where(AffiliateProfile.user_id == user.id)
    )
    profile = result.scalar_one_or_none()

    # Link count
    link_count = await db.execute(
        select(func.count(ReferralLink.id)).where(ReferralLink.affiliate_id == user.id)
    )

    # Click count (all links)
    click_count = await db.execute(
        select(func.count(ReferralClick.id))
        .join(ReferralLink, ReferralClick.link_id == ReferralLink.id)
        .where(ReferralLink.affiliate_id == user.id)
    )

    # Conversion count
    conversion_count = await db.execute(
        select(func.count(Conversion.id))
        .join(ReferralLink, Conversion.referral_link_id == ReferralLink.id)
        .where(
            ReferralLink.affiliate_id == user.id,
            Conversion.status.in_([ConversionStatus.approved, ConversionStatus.paid]),
        )
    )

    return {
        "profile_status": profile.status if profile else "unknown",
        "balance": {
            "pending": float(balance.pending or 0) if balance else 0,
            "approved": float(balance.approved or 0) if balance else 0,
            "paid_out": float(balance.paid_out or 0) if balance else 0,
        },
        "stats": {
            "total_links": link_count.scalar() or 0,
            "total_clicks": click_count.scalar() or 0,
            "total_conversions": conversion_count.scalar() or 0,
        },
    }
