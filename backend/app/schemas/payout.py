from datetime import datetime
from decimal import Decimal
from typing import Optional
from pydantic import BaseModel
from app.models.payout_request import PayoutStatus


class PayoutRequestCreate(BaseModel):
    amount: Decimal


class PayoutRequestResponse(BaseModel):
    id: int
    affiliate_id: int
    amount: Decimal
    status: PayoutStatus
    paystack_transfer_code: Optional[str]
    failure_reason: Optional[str]
    notes: Optional[str]
    requested_at: datetime
    paid_at: Optional[datetime]

    model_config = {"from_attributes": True}


class BalanceResponse(BaseModel):
    affiliate_id: int
    pending: Decimal
    approved: Decimal
    paid_out: Decimal
    total_earned: Decimal

    model_config = {"from_attributes": True}
