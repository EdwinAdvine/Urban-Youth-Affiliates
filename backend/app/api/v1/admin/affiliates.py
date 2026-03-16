"""
Admin affiliates management: list, approve/reject/suspend, update profile.
"""

from fastapi import APIRouter, Depends, Query, HTTPException, status
from typing import Optional
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_
from sqlalchemy.orm import selectinload

from app.deps import get_db, get_current_user
from app.models.user import User, UserRole
from app.models.affiliate_profile import AffiliateProfile, AffiliateStatus
from app.schemas.affiliate import (
    AffiliateProfileResponse,
    AffiliateProfileUpdate,
    AffiliateApprovalRequest,
)
from app.services.auth_service import get_current_user as get_user_service  # not used

router = APIRouter()

@router.get("/", response_model=list[AffiliateProfileResponse])
async def list_admin_affiliates(
    db: AsyncSession = Depends(get_db),
    status: Optional[AffiliateStatus] = Query(None),
    current_user: User = Depends(get_current_user)
):
    if current_user.role not in (UserRole.super_admin, UserRole.admin):
        raise HTTPException(status_code=403, detail="Admin access required")
    q = select(AffiliateProfile).options(selectinload(AffiliateProfile.user)).order_by(AffiliateProfile.created_at.desc())
    if status:
        q = q.where(AffiliateProfile.status == status)
    result = await db.execute(q)
    affiliates = result.scalars().all()
    return affiliates

@router.patch("/{profile_id}", response_model=AffiliateProfileResponse)
async def update_admin_affiliate(
    profile_id: int,
    data: AffiliateProfileUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    if current_user.role not in (UserRole.super_admin, UserRole.admin):
        raise HTTPException(status_code=403, detail="Admin access required")
    result = await db.execute(select(AffiliateProfile).where(AffiliateProfile.id == profile_id))
    profile = result.scalar_one_or_none()
    if not profile:
        raise HTTPException(status_code=404, detail="Affiliate not found")
    for field, value in data.model_dump(exclude_none=True).items():
        setattr(profile, field, value)
    profile.updated_at = datetime.now(timezone.utc)
    await db.commit()
    await db.refresh(profile)
    return profile

@router.post("/{profile_id}/approve", status_code=200)
async def approve_admin_affiliate(
    profile_id: int,
    data: AffiliateApprovalRequest,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    if current_user.role not in (UserRole.super_admin, UserRole.admin):
        raise HTTPException(status_code=403, detail="Admin access required")
    result = await db.execute(select(AffiliateProfile).where(AffiliateProfile.id == profile_id))
    profile = result.scalar_one_or_none()
    if not profile:
        raise HTTPException(status_code=404, detail="Affiliate not found")
    if profile.status != AffiliateStatus.pending:
        raise HTTPException(status_code=400, detail="Only pending affiliates can be approved")
    profile.status = AffiliateStatus.approved
    profile.approved_by_id = current_user.id
    profile.approved_at = datetime.now(timezone.utc)
    profile.notes = data.notes
    await db.commit()
    await db.refresh(profile)
    return {"message": "Affiliate approved", "profile": profile}

@router.post("/{profile_id}/reject", status_code=200)
async def reject_admin_affiliate(
    profile_id: int,
    data: AffiliateApprovalRequest,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    if current_user.role not in (UserRole.super_admin, UserRole.admin):
        raise HTTPException(status_code=403, detail="Admin access required")
    result = await db.execute(select(AffiliateProfile).where(AffiliateProfile.id == profile_id))
    profile = result.scalar_one_or_none()
    if not profile:
        raise HTTPException(status_code=404, detail="Affiliate not found")
    if profile.status != AffiliateStatus.pending:
        raise HTTPException(status_code=400, detail="Only pending affiliates can be rejected")
    profile.status = AffiliateStatus.rejected
    profile.approved_by_id = current_user.id
    profile.approved_at = datetime.now(timezone.utc)
    profile.notes = data.notes
    await db.commit()
    await db.refresh(profile)
    return {"message": "Affiliate rejected", "profile": profile}

@router.post("/{profile_id}/suspend", status_code=200)
async def suspend_admin_affiliate(
    profile_id: int,
    data: AffiliateApprovalRequest,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    if current_user.role not in (UserRole.super_admin, UserRole.admin):
        raise HTTPException(status_code=403, detail="Admin access required")
    result = await db.execute(select(AffiliateProfile).where(AffiliateProfile.id == profile_id))
    profile = result.scalar_one_or_none()
    if not profile:
        raise HTTPException(status_code=404, detail="Affiliate not found")
    profile.status = AffiliateStatus.suspended
    profile.notes = data.notes
    await db.commit()
    await db.refresh(profile)
    return {"message": "Affiliate suspended", "profile": profile}