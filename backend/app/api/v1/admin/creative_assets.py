"""Admin routes for creative assets (banners, videos, images, text copy).

Admins upload/link assets per campaign.
Affiliates browse them on the marketplace.
"""

from typing import List, Optional

from fastapi import APIRouter, Depends, Query, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.deps import require_admin
from app.exceptions import NotFoundError
from app.models.creative_asset import CreativeAsset
from app.models.user import User
from app.schemas.creative_asset import (
    CreativeAssetCreate,
    CreativeAssetResponse,
    CreativeAssetUpdate,
)

router = APIRouter()


@router.get("/admin/creative-assets", response_model=List[CreativeAssetResponse])
async def list_assets(
    campaign_id: Optional[int] = Query(None),
    asset_type: Optional[str] = Query(None),
    db: AsyncSession = Depends(get_db),
    user: User = Depends(require_admin),
):
    q = select(CreativeAsset).order_by(CreativeAsset.created_at.desc())
    if campaign_id is not None:
        q = q.where(CreativeAsset.campaign_id == campaign_id)
    if asset_type:
        q = q.where(CreativeAsset.asset_type == asset_type)
    result = await db.execute(q)
    return result.scalars().all()


@router.post(
    "/admin/creative-assets",
    response_model=CreativeAssetResponse,
    status_code=status.HTTP_201_CREATED,
)
async def create_asset(
    data: CreativeAssetCreate,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(require_admin),
):
    asset = CreativeAsset(**data.model_dump())
    db.add(asset)
    await db.commit()
    await db.refresh(asset)
    return asset


@router.get("/admin/creative-assets/{asset_id}", response_model=CreativeAssetResponse)
async def get_asset(
    asset_id: int,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(require_admin),
):
    result = await db.execute(select(CreativeAsset).where(CreativeAsset.id == asset_id))
    asset = result.scalar_one_or_none()
    if not asset:
        raise NotFoundError("Creative asset")
    return asset


@router.patch("/admin/creative-assets/{asset_id}", response_model=CreativeAssetResponse)
async def update_asset(
    asset_id: int,
    data: CreativeAssetUpdate,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(require_admin),
):
    result = await db.execute(select(CreativeAsset).where(CreativeAsset.id == asset_id))
    asset = result.scalar_one_or_none()
    if not asset:
        raise NotFoundError("Creative asset")
    for field, value in data.model_dump(exclude_none=True).items():
        setattr(asset, field, value)
    await db.commit()
    await db.refresh(asset)
    return asset


@router.delete("/admin/creative-assets/{asset_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_asset(
    asset_id: int,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(require_admin),
):
    result = await db.execute(select(CreativeAsset).where(CreativeAsset.id == asset_id))
    asset = result.scalar_one_or_none()
    if not asset:
        raise NotFoundError("Creative asset")
    await db.delete(asset)
    await db.commit()
