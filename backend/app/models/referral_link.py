from sqlalchemy import Boolean, Column, DateTime, ForeignKey, Integer, String, func
from app.database import Base


class ReferralLink(Base):
    __tablename__ = "referral_links"

    id = Column(Integer, primary_key=True)
    affiliate_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    campaign_id = Column(Integer, ForeignKey("campaigns.id", ondelete="RESTRICT"), nullable=False, index=True)
    code = Column(String(32), nullable=False, unique=True, index=True)
    short_url = Column(String(500), nullable=True)
    is_custom = Column(Boolean, nullable=False, default=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
