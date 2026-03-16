from datetime import datetime
from typing import Optional
from pydantic import BaseModel


class StoreCreate(BaseModel):
    name: str
    slug: str
    website_url: Optional[str] = None
    description: Optional[str] = None


class StoreUpdate(BaseModel):
    name: Optional[str] = None
    website_url: Optional[str] = None
    description: Optional[str] = None
    active: Optional[bool] = None


class StoreResponse(BaseModel):
    id: int
    name: str
    slug: str
    website_url: Optional[str]
    description: Optional[str]
    logo_url: Optional[str]
    active: bool
    created_at: datetime

    model_config = {"from_attributes": True}
