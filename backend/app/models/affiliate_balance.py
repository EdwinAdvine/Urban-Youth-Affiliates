from sqlalchemy import Column, DateTime, ForeignKey, Integer, Numeric, func
from app.database import Base


class AffiliateBalance(Base):
    __tablename__ = "affiliate_balances"

    id = Column(Integer, primary_key=True)
    affiliate_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False, unique=True, index=True)
    pending = Column(Numeric(12, 2), nullable=False, default=0)
    approved = Column(Numeric(12, 2), nullable=False, default=0)
    paid_out = Column(Numeric(12, 2), nullable=False, default=0)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
