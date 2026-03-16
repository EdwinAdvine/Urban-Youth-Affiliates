import enum
from sqlalchemy import Column, DateTime, Enum, ForeignKey, Integer, Numeric, String, Text, func, UniqueConstraint
from app.database import Base


class ConversionStatus(str, enum.Enum):
    pending = "pending"
    approved = "approved"
    rejected = "rejected"
    paid = "paid"


class ConversionSource(str, enum.Enum):
    api = "api"
    webhook = "webhook"
    manual = "manual"


class Conversion(Base):
    __tablename__ = "conversions"
    __table_args__ = (
        UniqueConstraint("store_id", "external_order_id", name="uq_conversion_order"),
    )

    id = Column(Integer, primary_key=True)
    referral_link_id = Column(Integer, ForeignKey("referral_links.id", ondelete="RESTRICT"), nullable=False, index=True)
    store_id = Column(Integer, ForeignKey("stores.id", ondelete="RESTRICT"), nullable=False, index=True)
    external_order_id = Column(String(255), nullable=False)
    sale_amount = Column(Numeric(12, 2), nullable=False)
    commission_earned = Column(Numeric(12, 2), nullable=False)
    status = Column(Enum(ConversionStatus), nullable=False, default=ConversionStatus.pending, index=True)
    conversion_source = Column(Enum(ConversionSource), nullable=False, default=ConversionSource.api)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False, index=True)
    approved_at = Column(DateTime(timezone=True), nullable=True)
    approved_by = Column(Integer, ForeignKey("users.id", ondelete="SET NULL"), nullable=True)
    notes = Column(Text, nullable=True)
