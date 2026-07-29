import hashlib
import json
from typing import Optional, List, Dict, Any
from fastapi import UploadFile
from app.core.redis_client import get_redis_client

def compute_file_hash(upload_file: UploadFile) -> str:
    """Computes a SHA-256 hash of an uploaded file."""
    hasher = hashlib.sha256()
    upload_file.file.seek(0)
    while chunk := upload_file.file.read(8192):
        hasher.update(chunk)
    upload_file.file.seek(0)
    return hasher.hexdigest()

def get_cached_result(file_hash: str) -> Optional[Dict[str, Any]]:
    """Retrieve cached captions and embedding by file hash."""
    r = get_redis_client()
    data = r.get(f"cache:image:{file_hash}")
    if data:
        return json.loads(data)
    return None

def set_cached_result(file_hash: str, captions: List[Dict[str, Any]], embedding: List[float], ttl_seconds: int = 86400):
    """Store captions and embedding in cache."""
    r = get_redis_client()
    cache_data = {"captions": captions, "embedding": embedding}
    r.setex(f"cache:image:{file_hash}", ttl_seconds, json.dumps(cache_data))
