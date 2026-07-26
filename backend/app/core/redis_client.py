import redis
from app.core.config import settings

# Global Redis connection pool
redis_pool = redis.ConnectionPool.from_url(settings.REDIS_URL, decode_responses=True)

def get_redis_client() -> redis.Redis:
    """Return a Redis client from the global pool."""
    return redis.Redis(connection_pool=redis_pool)
