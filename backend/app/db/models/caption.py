import uuid
from datetime import datetime
from sqlalchemy import Column, String, Integer, DateTime, ForeignKey, Boolean, Text, Float
from sqlalchemy.dialects.postgresql import UUID
from app.db.base_class import Base

class Caption(Base):
    __tablename__ = "captions"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    image_id = Column(UUID(as_uuid=True), ForeignKey("images.id", ondelete="CASCADE"), nullable=False, index=True)
    
    text = Column(Text, nullable=False)
    beam_rank = Column(Integer, nullable=False, default=0)
    beam_score = Column(Float, nullable=True)
    is_edited = Column(Boolean, nullable=False, default=False)
    edited_text = Column(Text, nullable=True)
    
    created_at = Column(DateTime(timezone=True), nullable=False, default=datetime.utcnow)
