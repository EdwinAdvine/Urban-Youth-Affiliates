"""Structured audit log: logs every mutating request with user, IP, status."""

import logging
import time

from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import Response

logger = logging.getLogger("yua.audit")

_MUTATING_METHODS = {"POST", "PUT", "PATCH", "DELETE"}
_SKIP_PATHS = {"/health", "/healthz", "/static"}


class AuditLogMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next) -> Response:
        if request.method not in _MUTATING_METHODS or any(
            request.url.path.startswith(p) for p in _SKIP_PATHS
        ):
            return await call_next(request)

        start = time.perf_counter()
        response = await call_next(request)
        duration_ms = round((time.perf_counter() - start) * 1000, 1)

        user_id = getattr(getattr(request.state, "user", None), "id", None)
        request_id = getattr(request.state, "request_id", "-")

        logger.info(
            "%s %s | status=%d | user=%s | ip=%s | req_id=%s | %.1fms",
            request.method,
            request.url.path,
            response.status_code,
            user_id or "anon",
            request.client.host if request.client else "unknown",
            request_id,
            duration_ms,
        )
        return response
