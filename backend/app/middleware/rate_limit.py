"""Sliding-window rate limiter backed by Redis.

Default: 200 requests / 60 seconds per IP.
The click-tracking endpoint uses 50 requests / 3600 seconds — enforced at the
route level by passing custom limits via query params on the Redis key.
"""

import time

from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import JSONResponse, Response

from app.config import get_settings

settings = get_settings()


def _client_ip(request: Request) -> str:
    forwarded_for = request.headers.get("X-Forwarded-For")
    if forwarded_for:
        return forwarded_for.split(",")[0].strip()
    return request.client.host if request.client else "unknown"


class RateLimitMiddleware(BaseHTTPMiddleware):
    """Global rate limiter: skip if Redis is not available (fail open)."""

    def __init__(self, app, requests_per_window: int = 200, window_seconds: int = 60):
        super().__init__(app)
        self.requests_per_window = requests_per_window
        self.window_seconds = window_seconds

    async def dispatch(self, request: Request, call_next) -> Response:
        # Skip health check and static files
        if request.url.path in ("/health", "/healthz") or request.url.path.startswith(
            "/static"
        ):
            return await call_next(request)

        try:
            from app.cache import get_redis  # lazy import — avoids circular deps

            redis = await get_redis()
            if redis is None:
                return await call_next(request)

            ip = _client_ip(request)
            now = int(time.time())
            window_start = now - self.window_seconds
            key = f"rl:{ip}"

            pipe = redis.pipeline()
            pipe.zremrangebyscore(key, 0, window_start)
            pipe.zadd(key, {str(now): now})
            pipe.zcard(key)
            pipe.expire(key, self.window_seconds)
            results = await pipe.execute()

            count = results[2]
            if count > self.requests_per_window:
                return JSONResponse(
                    status_code=429,
                    content={"detail": "Too many requests. Please slow down."},
                    headers={"Retry-After": str(self.window_seconds)},
                )
        except Exception:
            pass  # fail open — never block legitimate traffic on Redis error

        return await call_next(request)
