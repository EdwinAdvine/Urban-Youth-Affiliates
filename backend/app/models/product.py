from sqlalchemy import Boolean, Column, DateTime, ForeignKey, Integer, Numeric, String, Text, func
from app.database import Base


class Product(Base):
    __tablename__ = "products"

    id = Column(Integer, primary_key=True)
    store_id = Column(Integer, ForeignKey("stores.id", ondelete="CASCADE"), nullable=False, index=True)
    name = Column(String(255), nullable=False)
    sku = Column(String(100), nullable=True)
    price = Column(Numeric(12, 2), nullable=False)
    currency = Column(String(10), nullable=False, default="KES")
    description = Column(Text, nullable=True)
    image_url = Column(String(500), nullable=True)
    product_url = Column(String(500), nullable=True)
    category = Column(String(100), nullable=True, index=True)
    active = Column(Boolean, nullable=False, default=True, index=True)
    is_deleted = Column(Boolean, nullable=False, default=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), nullable=True)
