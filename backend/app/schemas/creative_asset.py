from datetime import datetime
from typing import Optional
from pydantic import BaseModel, HttpUrl


class CreativeAssetCreate(BaseModel):
    campaign_id: Optional[int] = None
    asset_type: str  # banner | video | image | text
    title: Optional[str] = None
    url: str
    size: Optional[str] = None
    embed_code: Optional[str] = None


class CreativeAssetUpdate(BaseModel):
    title: Optional[str] = None
    url: Optional[str] = None
    size: Optional[str] = None
    embed_code: Optional[str] = None


class CreativeAssetResponse(BaseModel):
    id: int
    campaign_id: Optional[int]
    asset_type: str
    title: Optional[str]
    url: str
    size: Optional[str]
    embed_code: Optional[str]
    created_at: datetime

    model_config = {"from_attributes": True}
