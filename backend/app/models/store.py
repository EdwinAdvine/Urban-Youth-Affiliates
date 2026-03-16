from sqlalchemy import Boolean, Column, DateTime, ForeignKey, Integer, String, Text, func
from app.database import Base


class Store(Base):
    __tablename__ = "stores"

    id = Column(Integer, primary_key=True)
    name = Column(String(255), nullable=False)
    slug = Column(String(100), nullable=False, unique=True, index=True)
    website_url = Column(String(500), nullable=True)
    description = Column(Text, nullable=True)
    logo_url = Column(String(500), nullable=True)
    admin_id = Column(Integer, ForeignKey("users.id", ondelete="SET NULL"), nullable=True)
    api_key = Column(String(255), nullable=True)
    active = Column(Boolean, nullable=False, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
