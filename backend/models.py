from sqlalchemy import Column, Integer, String, DateTime
from datetime import datetime, timezone
from database import Base

class ImageRecord(Base):
    __tablename__ = "images"

    id = Column(Integer, primary_key=True, index=True)
    prompt = Column(String, index=True)
    file_path = Column(String)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))
