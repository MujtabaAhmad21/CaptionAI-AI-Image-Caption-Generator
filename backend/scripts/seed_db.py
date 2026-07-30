import asyncio
import uuid
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker
from sqlalchemy import text
import sys
import os

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from app.core.config import settings

engine = create_async_engine(settings.DATABASE_URL, echo=True)
AsyncSessionLocal = async_sessionmaker(engine, expire_on_commit=False)

async def seed():
    async with AsyncSessionLocal() as session:
        # Create a test user
        user_id = uuid.uuid4()
        await session.execute(
            text("INSERT INTO users (id, email, display_name) VALUES (:id, :email, :display_name)"),
            {"id": user_id, "email": "test@example.com", "display_name": "Test User"}
        )
        
        # Create a test image for the user
        image_id = uuid.uuid4()
        await session.execute(
            text("INSERT INTO images (id, user_id, storage_path, mime_type, size_bytes) VALUES (:id, :user_id, :path, :mime, :size)"),
            {"id": image_id, "user_id": user_id, "path": "images/test.jpg", "mime": "image/jpeg", "size": 1024}
        )
        
        # Create a test anonymous image
        anon_session_id = uuid.uuid4()
        anon_image_id = uuid.uuid4()
        await session.execute(
            text("INSERT INTO images (id, anon_session_id, storage_path, mime_type, size_bytes) VALUES (:id, :anon_session_id, :path, :mime, :size)"),
            {"id": anon_image_id, "anon_session_id": anon_session_id, "path": "images/anon.jpg", "mime": "image/jpeg", "size": 2048}
        )
        
        await session.commit()
        print(f"Seeded DB with User ID: {user_id}")
        print(f"Seeded DB with Image ID: {image_id}")
        print(f"Seeded DB with Anon Image ID: {anon_image_id} (Session: {anon_session_id})")

if __name__ == "__main__":
    asyncio.run(seed())
