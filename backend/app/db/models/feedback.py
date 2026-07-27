import uuid
from datetime import datetime
from sqlalchemy import Column, String, DateTime, ForeignKey, Text
from sqlalchemy.dialects.postgresql import UUID
from app.db.base_class import Base

class CaptionFeedback(Base):
    __tablename__ = "caption_feedback"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    caption_id = Column(UUID(as_uuid=True), ForeignKey("captions.id", ondelete="CASCADE"), nullable=False)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="SET NULL"), nullable=True)
    
    rating = Column(String(10), nullable=False) # 'up' or 'down'
    comment = Column(Text, nullable=True)
    
    created_at = Column(DateTime(timezone=True), nullable=False, default=datetime.utcnow)
