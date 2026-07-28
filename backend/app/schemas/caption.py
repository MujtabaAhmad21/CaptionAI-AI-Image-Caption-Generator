from pydantic import BaseModel
from typing import Optional
from uuid import UUID
from datetime import datetime

class CaptionResponse(BaseModel):
    id: UUID
    text: str
    beam_rank: int
    is_edited: bool
    edited_text: Optional[str]
    
    class Config:
        from_attributes = True
