# app/auth/redis.py
"""
Redis token blacklist management.
Uses modern redis library (aioredis is deprecated for Python 3.12).
"""

import redis
from app.core.config import get_settings

settings = get_settings()

# Initialize Redis client
_redis_client = None

def get_redis_client():
    """Get or create Redis client"""
    global _redis_client
    if _redis_client is None:
        try:
            _redis_client = redis.Redis(
                host=getattr(settings, 'REDIS_HOST', 'localhost'),
                port=getattr(settings, 'REDIS_PORT', 6379),
                db=0,
                decode_responses=True,
                socket_connect_timeout=5
            )
            _redis_client.ping()
        except Exception as e:
            print(f"Warning: Could not connect to Redis: {e}")
            _redis_client = None
    return _redis_client


async def add_to_blacklist(jti: str, exp: int):
    """Add a token's JTI to the blacklist"""
    redis_client = get_redis_client()
    if redis_client:
        try:
            redis_client.setex(f"blacklist:{jti}", exp, "1")
        except Exception as e:
            print(f"Error adding to blacklist: {e}")


async def is_blacklisted(jti: str) -> bool:
    """Check if a token's JTI is blacklisted"""
    redis_client = get_redis_client()
    if redis_client:
        try:
            return redis_client.exists(f"blacklist:{jti}") > 0
        except Exception as e:
            print(f"Error checking blacklist: {e}")
    return False