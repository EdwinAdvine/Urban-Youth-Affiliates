from sqlalchemy import Boolean, Column, DateTime, ForeignKey, Integer, String, Text, func
from app.database import Base


class ReferralClick(Base):
    __tablename__ = "referral_clicks"

    id = Column(Integer, primary_key=True)
    link_id = Column(Integer, ForeignKey("referral_links.id", ondelete="CASCADE"), nullable=False, index=True)
    ip_address = Column(String(50), nullable=True, index=True)
    user_agent = Column(Text, nullable=True)
    referrer_url = Column(Text, nullable=True)
    country_code = Column(String(10), nullable=True)
    is_flagged = Column(Boolean, nullable=False, default=False)
    clicked_from_tiktok = Column(Boolean, nullable=False, default=False)
    clicked_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False, index=True)
