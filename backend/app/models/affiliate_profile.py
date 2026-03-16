import enum
from sqlalchemy import Boolean, Column, DateTime, Enum, ForeignKey, Integer, String, Text, func
from app.database import Base


class AffiliateStatus(str, enum.Enum):
    pending = "pending"
    approved = "approved"
    rejected = "rejected"
    suspended = "suspended"


class AffiliateProfile(Base):
    __tablename__ = "affiliate_profiles"

    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False, unique=True, index=True)
    status = Column(Enum(AffiliateStatus), nullable=False, default=AffiliateStatus.pending)
    full_name = Column(String(255), nullable=True)
    phone = Column(String(50), nullable=True)
    bio = Column(Text, nullable=True)
    tiktok_url = Column(String(500), nullable=True)
    instagram_url = Column(String(500), nullable=True)
    twitter_url = Column(String(500), nullable=True)
    payout_method = Column(String(50), nullable=True, default="paystack")
    bank_name = Column(String(255), nullable=True)
    bank_code = Column(String(50), nullable=True)
    account_number = Column(String(50), nullable=True)
    paystack_recipient_code = Column(String(255), nullable=True)
    last_payout_at = Column(DateTime(timezone=True), nullable=True)
    terms_version_accepted = Column(Integer, nullable=True)
    terms_accepted_at = Column(DateTime(timezone=True), nullable=True)
    approved_by = Column(Integer, ForeignKey("users.id", ondelete="SET NULL"), nullable=True)
    approved_at = Column(DateTime(timezone=True), nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), nullable=True)
