import enum
from sqlalchemy import Boolean, Column, DateTime, Enum, ForeignKey, Integer, Numeric, String, func
from app.database import Base


class CommissionType(str, enum.Enum):
    percent = "percent"
    fixed = "fixed"


class Campaign(Base):
    __tablename__ = "campaigns"

    id = Column(Integer, primary_key=True)
    name = Column(String(255), nullable=False)
    product_id = Column(Integer, ForeignKey("products.id", ondelete="SET NULL"), nullable=True, index=True)
    store_id = Column(Integer, ForeignKey("stores.id", ondelete="SET NULL"), nullable=True, index=True)
    commission_type = Column(Enum(CommissionType), nullable=False, default=CommissionType.percent)
    rate = Column(Numeric(10, 4), nullable=False)
    min_sale_amount = Column(Numeric(12, 2), nullable=True)
    cookie_days = Column(Integer, nullable=False, default=30)
    active = Column(Boolean, nullable=False, default=True, index=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    expires_at = Column(DateTime(timezone=True), nullable=True)
