from typing import List
from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.database import get_db
from app.deps import require_affiliate
from app.models.user import User
from app.models.referral_link import ReferralLink
from app.schemas.referral import GenerateLinkRequest, ReferralLinkResponse, ReferralLinkWithStats
from app.services.tracking_service import generate_referral_link, get_link_stats

router = APIRouter()


@router.post("/affiliate/links", response_model=ReferralLinkResponse, status_code=status.HTTP_201_CREATED)
async def generate_link(
    data: GenerateLinkRequest,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(require_affiliate),
):
    return await generate_referral_link(db, user.id, data.campaign_id)


@router.get("/affiliate/links", response_model=List[ReferralLinkWithStats])
async def list_links(
    db: AsyncSession = Depends(get_db),
    user: User = Depends(require_affiliate),
):
    result = await db.execute(
        select(ReferralLink)
        .where(ReferralLink.affiliate_id == user.id)
        .order_by(ReferralLink.created_at.desc())
    )
    links = result.scalars().all()

    links_with_stats = []
    for link in links:
        stats = await get_link_stats(db, link.id)
        link_data = ReferralLinkWithStats(
            id=link.id,
            affiliate_id=link.affiliate_id,
            campaign_id=link.campaign_id,
            code=link.code,
            short_url=link.short_url,
            is_custom=link.is_custom,
            created_at=link.created_at,
            **stats,
        )
        links_with_stats.append(link_data)
    return links_with_stats
