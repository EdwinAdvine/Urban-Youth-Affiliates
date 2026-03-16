from sqlalchemy import Column, DateTime, ForeignKey, Integer, String, Text, func
from app.database import Base


class PlatformSetting(Base):
    __tablename__ = "platform_settings"

    key = Column(String(100), primary_key=True)
    value = Column(Text, nullable=True)
    description = Column(Text, nullable=True)
    updated_by = Column(Integer, ForeignKey("users.id", ondelete="SET NULL"), nullable=True)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
