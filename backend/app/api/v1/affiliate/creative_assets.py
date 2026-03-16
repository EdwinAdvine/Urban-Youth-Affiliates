"""Affiliate-facing creative assets endpoint.

Returns assets for a given campaign so affiliates can copy embed codes / links.
"""

from typing import List, Optional

from fastapi import APIRouter, Depends, Query
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.deps import require_affiliate
from app.models.creative_asset import CreativeAsset
from app.models.user import User
from app.schemas.creative_asset import CreativeAssetResponse

router = APIRouter()


@router.get("/affiliate/creative-assets", response_model=List[CreativeAssetResponse])
async def list_campaign_assets(
    campaign_id: int = Query(..., description="Filter by campaign"),
    db: AsyncSession = Depends(get_db),
    user: User = Depends(require_affiliate),
):
    result = await db.execute(
        select(CreativeAsset)
        .where(CreativeAsset.campaign_id == campaign_id)
        .order_by(CreativeAsset.asset_type, CreativeAsset.created_at.desc())
    )
    return result.scalars().all()
