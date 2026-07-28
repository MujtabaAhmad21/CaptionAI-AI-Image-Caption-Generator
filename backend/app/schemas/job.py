from pydantic import BaseModel
from typing import Optional, List
from uuid import UUID
from datetime import datetime
from app.schemas.caption import CaptionResponse

class JobStatusResponse(BaseModel):
    job_id: UUID
    status: str
    error_message: Optional[str]
    captions: Optional[List[CaptionResponse]] = None
    
    class Config:
        from_attributes = True
