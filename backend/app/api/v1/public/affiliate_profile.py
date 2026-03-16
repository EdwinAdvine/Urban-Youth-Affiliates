"""Public affiliate profile endpoint — no auth required."""

from fastapi import APIRouter, Depends
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.exceptions import NotFoundError
from app.models.affiliate_profile import AffiliateProfile, AffiliateStatus
from app.models.conversion import Conversion, ConversionStatus
from app.models.referral_click import ReferralClick
from app.models.referral_link import ReferralLink

router = APIRouter()


@router.get("/public/affiliates/{affiliate_id}")
async def get_public_affiliate_profile(
    affiliate_id: int,
    db: AsyncSession = Depends(get_db),
):
    """Return a sanitised public view of an approved affiliate's profile and stats."""
    result = await db.execute(
        select(AffiliateProfile).where(
            AffiliateProfile.id == affiliate_id,
            AffiliateProfile.status == AffiliateStatus.approved,
        )
    )
    profile = result.scalar_one_or_none()
    if not profile:
        raise NotFoundError("Affiliate profile")

    # Aggregate stats — only approved/paid conversions visible publicly
    stats_row = (
        await db.execute(
            select(
                func.count(Conversion.id).label("total_conversions"),
                func.coalesce(func.sum(Conversion.commission_earned), 0).label("total_earned"),
            )
            .join(ReferralLink, Conversion.referral_link_id == ReferralLink.id)
            .where(
                ReferralLink.affiliate_id == affiliate_id,
                Conversion.status.in_([ConversionStatus.approved, ConversionStatus.paid]),
            )
        )
    ).one()

    total_clicks = (
        await db.execute(
            select(func.count(ReferralClick.id))
            .join(ReferralLink, ReferralClick.link_id == ReferralLink.id)
            .where(ReferralLink.affiliate_id == affiliate_id)
        )
    ).scalar() or 0

    total_links = (
        await db.execute(
            select(func.count(ReferralLink.id)).where(
                ReferralLink.affiliate_id == affiliate_id
            )
        )
    ).scalar() or 0

    total_conversions = stats_row.total_conversions or 0
    conversion_rate = (
        round(total_conversions / total_clicks * 100, 1) if total_clicks > 0 else 0.0
    )

    return {
        "id": profile.id,
        "full_name": profile.full_name or "Y&U Affiliate",
        "bio": profile.bio,
        "tiktok_url": profile.tiktok_url,
        "instagram_url": profile.instagram_url,
        "twitter_url": profile.twitter_url,
        "member_since": profile.created_at.isoformat() if profile.created_at else None,
        "stats": {
            "total_links": total_links,
            "total_clicks": total_clicks,
            "total_conversions": total_conversions,
            "conversion_rate": conversion_rate,
        },
    }
