"""Redis connection helper.

Usage:
    redis = await get_redis()
    await redis.set("key", "value", ex=60)
"""

from __future__ import annotations

import redis.asyncio as aioredis

from app.config import get_settings

_redis_client: aioredis.Redis | None = None


async def get_redis() -> aioredis.Redis | None:
    """Return the shared Redis client, initialising on first call."""
    global _redis_client
    if _redis_client is None:
        settings = get_settings()
        try:
            _redis_client = aioredis.from_url(
                settings.redis_url,
                password=settings.redis_password or None,
                encoding="utf-8",
                decode_responses=True,
            )
            await _redis_client.ping()
        except Exception:
            _redis_client = None
    return _redis_client


async def close_redis() -> None:
    global _redis_client
    if _redis_client:
        await _redis_client.aclose()
        _redis_client = None
