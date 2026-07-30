import asyncio
import uuid
import requests
import os
from datetime import datetime
from app.workers.celery_app import celery_app
from app.core.config import settings
from app.db.session import AsyncSessionLocal
from app.db.models.job import Job
from app.db.models.image import Image
from app.db.models.caption import Caption
from app.services.cache_service import set_cached_result

async def update_job_status(job_id: str, status: str, error_message: str = None):
    async with AsyncSessionLocal() as session:
        job = await session.get(Job, uuid.UUID(job_id))
        if job:
            job.status = status
            if error_message:
                job.error_message = error_message
            if status in ["succeeded", "failed"]:
                job.completed_at = datetime.utcnow()
            elif status == "running":
                job.started_at = datetime.utcnow()
            await session.commit()

async def save_captions_and_embedding(image_id: str, embedding: list, captions_data: list):
    async with AsyncSessionLocal() as session:
        # Update image embedding
        image = await session.get(Image, uuid.UUID(image_id))
        if image:
            image.embedding = embedding
            image.status = "done"
            
        # Insert captions
        for cap in captions_data:
            new_caption = Caption(
                image_id=uuid.UUID(image_id),
                text=cap.get("text", ""),
                beam_rank=cap.get("beam_rank", 0),
                beam_score=cap.get("beam_score", 0.0)
            )
            session.add(new_caption)
        
        await session.commit()

async def _generate_caption_async(job_id: str, image_id: str, image_path: str, file_hash: str):
    await update_job_status(job_id, "running")
    try:
        if not os.path.exists(image_path):
            raise FileNotFoundError(f"Image not found at {image_path}")

        def make_request():
            with open(image_path, "rb") as f:
                files = {"image": (os.path.basename(image_path), f, "image/jpeg")}
                return requests.post(settings.ML_INFERENCE_URL, files=files, timeout=30)
                
        loop = asyncio.get_running_loop()
        response = await loop.run_in_executor(None, make_request)
            
        response.raise_for_status()
        result = response.json()
        
        captions = result.get("captions", [])
        embedding = result.get("embedding", [])
        
        await save_captions_and_embedding(image_id, embedding, captions)
        await update_job_status(job_id, "succeeded")
        
        # Save to cache
        set_cached_result(file_hash, captions, embedding)
        
    except Exception as exc:
        await update_job_status(job_id, "failed", str(exc))
    finally:
        from app.db.session import engine
        await engine.dispose()

@celery_app.task(bind=True, max_retries=3)
def generate_caption_task(self, job_id: str, image_id: str, image_path: str, file_hash: str):
    asyncio.run(_generate_caption_async(job_id, image_id, image_path, file_hash))
