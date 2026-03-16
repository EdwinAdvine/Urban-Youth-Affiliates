from datetime import datetime
from decimal import Decimal
from typing import Optional
from pydantic import BaseModel
from app.models.conversion import ConversionStatus, ConversionSource


class ConversionWebhookRequest(BaseModel):
    ref_code: str
    external_order_id: str
    sale_amount: Decimal
    store_api_key: Optional[str] = None


class ConversionResponse(BaseModel):
    id: int
    referral_link_id: int
    store_id: int
    external_order_id: str
    sale_amount: Decimal
    commission_earned: Decimal
    status: ConversionStatus
    conversion_source: ConversionSource
    created_at: datetime
    approved_at: Optional[datetime]

    model_config = {"from_attributes": True}


class ConversionApprovalRequest(BaseModel):
    action: str  # "approve" | "reject"
    notes: Optional[str] = None
