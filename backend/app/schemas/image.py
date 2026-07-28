from pydantic import BaseModel
from typing import Optional, List
from uuid import UUID
from datetime import datetime

class ImageUploadResponse(BaseModel):
    image_id: UUID
    job_id: UUID
    status: str
    message: str

class ImageResponse(BaseModel):
    id: UUID
    original_filename: Optional[str]
    status: str
    created_at: datetime
    
    class Config:
        from_attributes = True
