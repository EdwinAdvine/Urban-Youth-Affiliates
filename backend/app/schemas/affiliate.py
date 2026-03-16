from datetime import datetime
from typing import Optional
from pydantic import BaseModel
from app.models.affiliate_profile import AffiliateStatus


class AffiliateProfileResponse(BaseModel):
    id: int
    user_id: int
    status: AffiliateStatus
    full_name: Optional[str]
    phone: Optional[str]
    bio: Optional[str]
    tiktok_url: Optional[str]
    instagram_url: Optional[str]
    twitter_url: Optional[str]
    payout_method: Optional[str]
    bank_name: Optional[str]
    paystack_recipient_code: Optional[str]
    last_payout_at: Optional[datetime]
    terms_version_accepted: Optional[int]
    approved_at: Optional[datetime]
    created_at: datetime

    model_config = {"from_attributes": True}


class AffiliateProfileUpdate(BaseModel):
    full_name: Optional[str] = None
    phone: Optional[str] = None
    bio: Optional[str] = None
    tiktok_url: Optional[str] = None
    instagram_url: Optional[str] = None
    twitter_url: Optional[str] = None
    bank_name: Optional[str] = None
    bank_code: Optional[str] = None
    account_number: Optional[str] = None


class AffiliateApprovalRequest(BaseModel):
    action: str  # "approve" | "reject" | "suspend"
    notes: Optional[str] = None


class AffiliateBankDetailsUpdate(BaseModel):
    bank_name: str
    bank_code: str
    account_number: str
