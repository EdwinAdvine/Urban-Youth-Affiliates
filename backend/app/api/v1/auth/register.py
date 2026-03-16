"""
Register endpoint for affiliates.
"""

from fastapi import APIRouter, Depends, status

from sqlalchemy.ext.asyncio import AsyncSession

from app.deps import get_db
from app.services.auth_service import register_affiliate
from app.schemas.auth import RegisterRequest
from app.models.affiliate_profile import AffiliateStatus

router = APIRouter()

@router.post("/register", status_code=status.HTTP_201_CREATED)
async def register_endpoint(
    request: RegisterRequest,
    db: AsyncSession = Depends(get_db)
):
    user, profile = await register_affiliate(db, request)
    return {
        "message": "Registration successful.",
        "user_id": user.id,
        "profile_id": profile.id,
        "status": profile.status,
        "requires_approval": profile.status == AffiliateStatus.pending
    }