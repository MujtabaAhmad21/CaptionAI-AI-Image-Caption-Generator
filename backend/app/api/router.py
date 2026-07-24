from fastapi import APIRouter
from app.api.v1 import routes_images, routes_jobs

api_router = APIRouter()
api_router.include_router(routes_images.router, prefix="/images", tags=["images"])
api_router.include_router(routes_jobs.router, prefix="/jobs", tags=["jobs"])
