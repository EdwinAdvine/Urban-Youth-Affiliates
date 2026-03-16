from datetime import datetime, timezone
from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.database import get_db
from app.deps import require_affiliate
from app.models.user import User
from app.models.affiliate_profile import AffiliateProfile
from app.schemas.affiliate import AffiliateProfileResponse, AffiliateProfileUpdate, AffiliateBankDetailsUpdate
from app.exceptions import NotFoundError

router = APIRouter()


@router.get("/affiliate/banks")
async def list_supported_banks(
    country: str = "kenya",
    user: User = Depends(require_affiliate),
):
    """Return Paystack-supported banks for the given country (default: kenya)."""
    from app.services.payments.paystack import list_banks
    banks = await list_banks(country=country)
    return {"banks": banks}


@router.get("/affiliate/profile", response_model=AffiliateProfileResponse)
async def get_profile(
    db: AsyncSession = Depends(get_db),
    user: User = Depends(require_affiliate),
):
    result = await db.execute(
        select(AffiliateProfile).where(AffiliateProfile.user_id == user.id)
    )
    profile = result.scalar_one_or_none()
    if not profile:
        raise NotFoundError("Affiliate profile")
    return profile


@router.patch("/affiliate/profile", response_model=AffiliateProfileResponse)
async def update_profile(
    data: AffiliateProfileUpdate,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(require_affiliate),
):
    result = await db.execute(
        select(AffiliateProfile).where(AffiliateProfile.user_id == user.id)
    )
    profile = result.scalar_one_or_none()
    if not profile:
        raise NotFoundError("Affiliate profile")

    for field, value in data.model_dump(exclude_none=True).items():
        setattr(profile, field, value)
    profile.updated_at = datetime.now(timezone.utc)
    await db.commit()
    await db.refresh(profile)
    return profile


@router.patch("/affiliate/profile/bank-details")
async def update_bank_details(
    data: AffiliateBankDetailsUpdate,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(require_affiliate),
):
    result = await db.execute(
        select(AffiliateProfile).where(AffiliateProfile.user_id == user.id)
    )
    profile = result.scalar_one_or_none()
    if not profile:
        raise NotFoundError("Affiliate profile")

    profile.bank_name = data.bank_name
    profile.bank_code = data.bank_code
    profile.account_number = data.account_number
    profile.updated_at = datetime.now(timezone.utc)

    # Create Paystack recipient
    from app.services.payments.paystack import create_transfer_recipient
    recipient_code = await create_transfer_recipient(
        name=profile.full_name or user.email,
        bank_code=data.bank_code,
        account_number=data.account_number,
    )
    profile.paystack_recipient_code = recipient_code

    await db.commit()
    return {"message": "Bank details updated and Paystack recipient created", "recipient_code": recipient_code}
