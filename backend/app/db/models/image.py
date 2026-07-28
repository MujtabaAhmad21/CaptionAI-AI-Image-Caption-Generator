import uuid
from datetime import datetime
from sqlalchemy import Column, String, Integer, DateTime, ForeignKey, CheckConstraint, Text, Float
from sqlalchemy.dialects.postgresql import UUID
from pgvector.sqlalchemy import Vector
from app.db.base_class import Base

class Image(Base):
    __tablename__ = "images"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="SET NULL"), nullable=True, index=True)
    anon_session_id = Column(UUID(as_uuid=True), nullable=True, index=True)
    
    storage_path = Column(Text, nullable=False)
    original_filename = Column(String(255), nullable=True)
    mime_type = Column(String(50), nullable=False)
    size_bytes = Column(Integer, nullable=False)
    width = Column(Integer, nullable=True)
    height = Column(Integer, nullable=True)
    
    caption = Column(Text, nullable=True)
    embedding = Column(Vector(768), nullable=True)
    processing_time_ms = Column(Float, nullable=True)
    status = Column(String(20), nullable=False, default="pending")
    error_message = Column(Text, nullable=True)
    created_at = Column(DateTime(timezone=True), nullable=False, default=datetime.utcnow)

    __table_args__ = (
        CheckConstraint(
            "(user_id IS NOT NULL AND anon_session_id IS NULL) OR "
            "(user_id IS NULL AND anon_session_id IS NOT NULL)",
            name="images_owner_check"
        ),
    )
