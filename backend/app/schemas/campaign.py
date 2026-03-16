from datetime import datetime
from decimal import Decimal
from typing import Optional
from pydantic import BaseModel
from app.models.campaign import CommissionType


class CampaignCreate(BaseModel):
    name: str
    product_id: Optional[int] = None
    store_id: Optional[int] = None
    commission_type: CommissionType = CommissionType.percent
    rate: Decimal
    min_sale_amount: Optional[Decimal] = None
    cookie_days: int = 30
    expires_at: Optional[datetime] = None


class CampaignUpdate(BaseModel):
    name: Optional[str] = None
    commission_type: Optional[CommissionType] = None
    rate: Optional[Decimal] = None
    min_sale_amount: Optional[Decimal] = None
    cookie_days: Optional[int] = None
    active: Optional[bool] = None
    expires_at: Optional[datetime] = None


class CampaignResponse(BaseModel):
    id: int
    name: str
    product_id: Optional[int]
    store_id: Optional[int]
    commission_type: CommissionType
    rate: Decimal
    min_sale_amount: Optional[Decimal]
    cookie_days: int
    active: bool
    created_at: datetime
    expires_at: Optional[datetime]

    model_config = {"from_attributes": True}
