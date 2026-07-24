import uuid
from fastapi import APIRouter, Depends, Request, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select

from app.db.session import get_db
from app.db.models.job import Job
from app.db.models.image import Image
from app.db.models.caption import Caption
from app.schemas.job import JobStatusResponse

router = APIRouter()

@router.get("/{job_id}", response_model=JobStatusResponse)
async def get_job_status(
    job_id: uuid.UUID,
    request: Request,
    db: AsyncSession = Depends(get_db)
):
    result = await db.execute(
        select(Job).where(Job.id == job_id)
    )
    job = result.scalar_one_or_none()
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")
        
    image = await db.get(Image, job.image_id)
    if not image:
        raise HTTPException(status_code=404, detail="Associated image not found")

    # Verify authorization
    anon_session_id_str = request.cookies.get("anon_session_id")
    if image.user_id is None:
        if not anon_session_id_str or str(image.anon_session_id) != anon_session_id_str:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not authorized to view this job")

    captions_data = None
    if job.status == "succeeded":
        caps_result = await db.execute(
            select(Caption).where(Caption.image_id == image.id).order_by(Caption.beam_rank)
        )
        captions = caps_result.scalars().all()
        captions_data = captions

    return JobStatusResponse(
        job_id=job.id,
        status=job.status,
        error_message=job.error_message,
        captions=captions_data
    )
