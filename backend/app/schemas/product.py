from datetime import datetime
from decimal import Decimal
from typing import Optional
from pydantic import BaseModel


class ProductCreate(BaseModel):
    store_id: int
    name: str
    sku: Optional[str] = None
    price: Decimal
    currency: str = "KES"
    description: Optional[str] = None
    image_url: Optional[str] = None
    product_url: Optional[str] = None
    category: Optional[str] = None


class ProductUpdate(BaseModel):
    name: Optional[str] = None
    sku: Optional[str] = None
    price: Optional[Decimal] = None
    description: Optional[str] = None
    image_url: Optional[str] = None
    product_url: Optional[str] = None
    category: Optional[str] = None
    active: Optional[bool] = None


class ProductResponse(BaseModel):
    id: int
    store_id: int
    name: str
    sku: Optional[str]
    price: Decimal
    currency: str
    description: Optional[str]
    image_url: Optional[str]
    product_url: Optional[str]
    category: Optional[str]
    active: bool
    created_at: datetime

    model_config = {"from_attributes": True}
