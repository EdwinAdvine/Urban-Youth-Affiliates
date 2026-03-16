"""
Application lifespan: startup and shutdown events.
"""

import logging
from contextlib import asynccontextmanager
from fastapi import FastAPI

from app.database import init_db, close_db
from app.cache import get_redis, close_redis

logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    logger.info("Starting Y&U Affiliates API...")
    await init_db()
    await get_redis()  # warm up connection; fail-open if Redis unavailable
    logger.info("Application startup complete")

    yield

    # Shutdown
    logger.info("Shutting down Y&U Affiliates API...")
    await close_db()
    await close_redis()
    logger.info("Application shutdown complete")
