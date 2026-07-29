import os
import uuid
import shutil
from fastapi import UploadFile
from app.core.config import settings

def save_upload_file(upload_file: UploadFile) -> str:
    """Saves an uploaded file to local storage and returns its path."""
    os.makedirs(settings.LOCAL_STORAGE_PATH, exist_ok=True)
    extension = os.path.splitext(upload_file.filename)[1] if upload_file.filename else ""
    unique_filename = f"{uuid.uuid4()}{extension}"
    file_path = os.path.join(settings.LOCAL_STORAGE_PATH, unique_filename)
    
    with open(file_path, "wb") as buffer:
        upload_file.file.seek(0)
        shutil.copyfileobj(upload_file.file, buffer)
        
    return file_path
