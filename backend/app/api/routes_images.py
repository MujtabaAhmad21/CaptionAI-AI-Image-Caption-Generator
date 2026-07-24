import uuid
import json
from fastapi import APIRouter, Depends, File, UploadFile, Request, Response, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from PIL import Image as PILImage
import io

from app.db.session import get_db
from app.db.models.image import Image
from app.db.models.job import Job
from app.schemas.image import ImageUploadResponse
from app.core.config import settings
from app.core.redis_client import get_redis_client
from app.services.storage_service import save_upload_file
from app.services.cache_service import compute_file_hash, get_cached_result
from app.workers.tasks import generate_caption_task

router = APIRouter()

# Simple sliding window rate limiter
def check_rate_limit(request: Request):
    client_ip = request.client.host
    r = get_redis_client()
    key = f"rate_limit:upload:{client_ip}"
    current = r.get(key)
    if current and int(current) >= settings.RATE_LIMIT_PER_MINUTE:
        raise HTTPException(status_code=status.HTTP_429_TOO_MANY_REQUESTS, detail="Too many requests. Please try again later.")
    r.incr(key)
    if not current:
        r.expire(key, 60)

def validate_image(upload_file: UploadFile):
    # Check size
    upload_file.file.seek(0, 2)
    size_bytes = upload_file.file.tell()
    upload_file.file.seek(0)
    
    if size_bytes > settings.MAX_UPLOAD_SIZE_MB * 1024 * 1024:
        raise HTTPException(status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE, detail=f"File too large. Max size is {settings.MAX_UPLOAD_SIZE_MB}MB.")
    
    # Check content via Pillow
    try:
        img = PILImage.open(upload_file.file)
        img.verify()  # Verify it's an image
        upload_file.file.seek(0)
        img = PILImage.open(upload_file.file) # Need to reopen to get dimensions after verify
        return size_bytes, img.width, img.height, img.format.lower()
    except Exception:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid image file.")
    finally:
        upload_file.file.seek(0)

@router.post("", response_model=ImageUploadResponse)
async def upload_image(
    request: Request,
    response: Response,
    image: UploadFile = File(...),
    db: AsyncSession = Depends(get_db)
):
    check_rate_limit(request)
    
    size_bytes, width, height, fmt = validate_image(image)
    mime_type = f"image/{fmt}"
    
    # Session handling
    # For MVP, we use anon_session_id.
    anon_session_id_str = request.cookies.get("anon_session_id")
    if not anon_session_id_str:
        anon_session_id = uuid.uuid4()
        response.set_cookie(key="anon_session_id", value=str(anon_session_id), httponly=True, samesite="lax")
    else:
        try:
            anon_session_id = uuid.UUID(anon_session_id_str)
        except ValueError:
            anon_session_id = uuid.uuid4()
            response.set_cookie(key="anon_session_id", value=str(anon_session_id), httponly=True, samesite="lax")

    # Cache check
    file_hash = compute_file_hash(image)
    cached_result = get_cached_result(file_hash)
    
    # Save file
    file_path = save_upload_file(image)
    
    # DB entry for image
    db_image = Image(
        anon_session_id=anon_session_id,
        storage_path=file_path,
        original_filename=image.filename,
        mime_type=mime_type,
        size_bytes=size_bytes,
        width=width,
        height=height,
        status="pending"
    )
    db.add(db_image)
    await db.commit()
    await db.refresh(db_image)
    
    # DB entry for job
    db_job = Job(
        image_id=db_image.id,
        status="queued"
    )
    db.add(db_job)
    await db.commit()
    await db.refresh(db_job)
    
    if cached_result:
        # If cache hit, update DB synchronously
        from app.workers.tasks import save_captions_and_embedding
        await save_captions_and_embedding(str(db_image.id), cached_result["embedding"], cached_result["captions"])
        db_job.status = "succeeded"
        from datetime import datetime
        db_job.completed_at = datetime.utcnow()
        await db.commit()
        return ImageUploadResponse(image_id=db_image.id, job_id=db_job.id, status="succeeded", message="Image processed from cache.")
    
    # Enqueue task
    generate_caption_task.delay(str(db_job.id), str(db_image.id), file_path, file_hash)
    
    return ImageUploadResponse(image_id=db_image.id, job_id=db_job.id, status="queued", message="Image uploaded and queued for processing.")
