import enum
from sqlalchemy import Column, DateTime, Enum, ForeignKey, Integer, Numeric, String, Text, func
from app.database import Base


class PayoutStatus(str, enum.Enum):
    pending = "pending"
    processing = "processing"
    paid = "paid"
    failed = "failed"


class PayoutRequest(Base):
    __tablename__ = "payout_requests"

    id = Column(Integer, primary_key=True)
    affiliate_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    amount = Column(Numeric(12, 2), nullable=False)
    status = Column(Enum(PayoutStatus), nullable=False, default=PayoutStatus.pending, index=True)
    paystack_transfer_code = Column(String(255), nullable=True)
    paystack_recipient_code = Column(String(255), nullable=True)
    failure_reason = Column(Text, nullable=True)
    notes = Column(Text, nullable=True)
    requested_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False, index=True)
    paid_at = Column(DateTime(timezone=True), nullable=True)
    processed_by = Column(Integer, ForeignKey("users.id", ondelete="SET NULL"), nullable=True)
