"""
Y&U Affiliates - FastAPI Main Application

Composition root: creates the FastAPI app, attaches middleware, registers routes.
Business logic lives in services/; route handlers in api/; middleware in middleware/.
"""

import logging
import os

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.exceptions import RequestValidationError
from starlette.exceptions import HTTPException as StarletteHTTPException
from starlette.staticfiles import StaticFiles

from app.config import settings
from app.database import check_db_connection
from app.lifespan import lifespan

logger = logging.getLogger(__name__)

# ── Configure basic logging ──────────────────────────────────────────
logging.basicConfig(
    level=logging.DEBUG if settings.debug else logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)

# ── Create FastAPI application ──────────────────────────────────────

app = FastAPI(
    title=settings.app_name,
    version=settings.app_version,
    description="""
    **Y&U Affiliates** — Commission-based referral marketing platform for Youth & Urbanism.

    ## Features

    * **Multi-Role System**: Super Admin, Admin, Affiliate
    * **Product Catalog**: Multi-store product/service listings
    * **Referral Tracking**: Click tracking with first-party cookies
    * **Commission Engine**: Per-product, per-store, or global commission rules
    * **Paystack Payouts**: Automated affiliate commission payments
    * **Real-Time Analytics**: Clicks, conversions, revenue dashboards

    ## Authentication

    All protected endpoints require JWT authentication via Bearer token:
    ```
    Authorization: Bearer <your-jwt-token>
    ```

    ## API Versioning

    Current API version: v1 (prefix: `/api/v1`)
    """,
    docs_url=None if settings.environment == "testing" else "/docs",
    redoc_url=None if settings.environment == "testing" else "/redoc",
    openapi_url=None if settings.environment == "testing" else "/openapi.json",
    lifespan=lifespan,
    contact={
        "name": "Y&U Affiliates Support",
        "email": "support@yuaffiliates.co.ke",
    },
)

# ── Middleware (order matters: last added = first executed) ──────────
from app.middleware import AuditLogMiddleware, RateLimitMiddleware, RequestIDMiddleware

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins_list,
    allow_credentials=settings.cors_allow_credentials,
    allow_methods=settings.cors_allow_methods,
    allow_headers=settings.cors_allow_headers,
    expose_headers=[
        "Content-Range",
        "X-Total-Count",
        "X-Request-ID",
    ],
)
app.add_middleware(RequestIDMiddleware)
app.add_middleware(AuditLogMiddleware)
app.add_middleware(RateLimitMiddleware, requests_per_window=200, window_seconds=60)

# ── Exception handlers ──────────────────────────────────────────────

from app.exceptions import AppError
from app.exception_handlers import (
    app_error_handler,
    http_exception_handler,
    validation_exception_handler,
    general_exception_handler,
)

app.add_exception_handler(AppError, app_error_handler)
app.add_exception_handler(StarletteHTTPException, http_exception_handler)
app.add_exception_handler(RequestValidationError, validation_exception_handler)
app.add_exception_handler(Exception, general_exception_handler)

# ── Root & health endpoints ─────────────────────────────────────────


@app.get("/", tags=["Root"])
async def root():
    return {
        "name": settings.app_name,
        "version": settings.app_version,
        "status": "running",
        "environment": settings.environment,
        "docs": "/docs",
        "api": settings.api_v1_prefix,
    }


@app.get("/health", tags=["Health"])
async def health_check():
    db_healthy = await check_db_connection()
    return {
        "status": "healthy" if db_healthy else "degraded",
        "version": settings.app_version,
        "environment": settings.environment,
        "database": {
            "status": "connected" if db_healthy else "disconnected",
            "healthy": db_healthy,
        },
    }


# ── Register all API routes ─────────────────────────────────────────

from app.routers import register_all_routers

register_all_routers(app)


# ── Static file serving for uploads ─────────────────────────────────
_uploads_dir = os.path.join(os.getcwd(), settings.upload_dir)
os.makedirs(_uploads_dir, exist_ok=True)
app.mount("/uploads", StaticFiles(directory=_uploads_dir), name="uploads")

logger.info("Y&U Affiliates API configured successfully")
