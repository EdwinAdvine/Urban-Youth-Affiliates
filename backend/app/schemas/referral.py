from datetime import datetime
from typing import Optional
from pydantic import BaseModel


class GenerateLinkRequest(BaseModel):
    campaign_id: int


class ReferralLinkResponse(BaseModel):
    id: int
    affiliate_id: int
    campaign_id: int
    code: str
    short_url: Optional[str]
    is_custom: bool
    created_at: datetime

    model_config = {"from_attributes": True}


class ReferralLinkWithStats(ReferralLinkResponse):
    total_clicks: int = 0
    total_conversions: int = 0
    total_earned: float = 0.0
