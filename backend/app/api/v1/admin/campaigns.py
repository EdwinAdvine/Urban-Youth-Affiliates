"""
Admin campaigns CRUD.
"""

from fastapi import APIRouter, Depends, Query, HTTPException
from typing import Optional

from sqlalchemy.ext.asyncio import AsyncSession

from app.deps import get_db, get_current_user
from app.models.user import User, UserRole
from app.services.catalog_service import (
    list_campaigns,
    get_campaign,
    create_campaign,
    update_campaign,
    delete_campaign,
)
from app.schemas.campaign import CampaignListResponse, CampaignCreate, CampaignUpdate

router = APIRouter()

@router.get("/", response_model=list[Campaign])
async def list_admin_campaigns(
    db: AsyncSession = Depends(get_db),
    store_id: Optional[int] = Query(None),
    product_id: Optional[int] = Query(None),
    active_only: bool = Query(False),
    current_user: User = Depends(get_current_user)
):
    if current_user.role not in (UserRole.super_admin, UserRole.admin):
        raise HTTPException(status_code=403, detail="Admin access required")
    campaigns = await list_campaigns(db, store_id=store_id, product_id=product_id, active_only=active_only)
    return campaigns

@router.post("/", response_model=Campaign, status_code=201)
async def create_admin_campaign(
    data: CampaignCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    if current_user.role not in (UserRole.super_admin, UserRole.admin):
        raise HTTPException(status_code=403, detail="Admin access required")
    campaign = await create_campaign(db, data)
    return campaign

@router.get("/{campaign_id}", response_model=Campaign)
async def get_admin_campaign(
    campaign_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    if current_user.role not in (UserRole.super_admin, UserRole.admin):
        raise HTTPException(status_code=403, detail="Admin access required")
    campaign = await get_campaign(db, campaign_id)
    return campaign

@router.patch("/{campaign_id}", response_model=Campaign)
async def update_admin_campaign(
    campaign_id: int,
    data: CampaignUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    if current_user.role not in (UserRole.super_admin, UserRole.admin):
        raise HTTPException(status_code=403, detail="Admin access required")
    campaign = await update_campaign(db, campaign_id, data)
    return campaign

@router.delete("/{campaign_id}", status_code=204)
async def delete_admin_campaign(
    campaign_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    if current_user.role not in (UserRole.super_admin, UserRole.admin):
        raise HTTPException(status_code=403, detail="Admin access required")
    await delete_campaign(db, campaign_id)