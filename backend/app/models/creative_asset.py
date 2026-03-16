import enum
from sqlalchemy import Column, DateTime, Enum, ForeignKey, Integer, String, Text, func
from app.database import Base


class AssetType(str, enum.Enum):
    banner = "banner"
    video = "video"
    image = "image"
    text = "text"


class CreativeAsset(Base):
    __tablename__ = "creative_assets"

    id = Column(Integer, primary_key=True)
    campaign_id = Column(Integer, ForeignKey("campaigns.id", ondelete="SET NULL"), nullable=True, index=True)
    asset_type = Column(Enum(AssetType), nullable=False)
    title = Column(String(255), nullable=True)
    url = Column(Text, nullable=False)
    size = Column(String(50), nullable=True)
    embed_code = Column(Text, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
