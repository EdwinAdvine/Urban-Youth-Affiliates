"""
Integration test fixtures.

Requires a running PostgreSQL and Redis instance. Set the following env vars
before running (or use a .env.test file):

    TEST_DATABASE_URL=postgresql+asyncpg://yua_user:password@localhost:5432/yua_test
    TEST_REDIS_URL=redis://localhost:6379/1
    SECRET_KEY=test-secret-key-must-be-at-least-32-chars

Run with:
    pytest tests/ -m integration -v
"""

import os
import pytest
import pytest_asyncio

# Force test environment before any app imports
os.environ.setdefault(
    "DATABASE_URL",
    os.getenv("TEST_DATABASE_URL", "postgresql+asyncpg://yua_user:password@localhost:5432/yua_test"),
)
os.environ.setdefault(
    "REDIS_URL",
    os.getenv("TEST_REDIS_URL", "redis://localhost:6379/1"),
)
os.environ.setdefault("SECRET_KEY", "test-secret-key-must-be-at-least-32-characters-long")
os.environ.setdefault("ENVIRONMENT", "testing")
os.environ.setdefault("STORE_API_KEY", "test-store-api-key")

from httpx import ASGITransport, AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_sessionmaker

from app.main import app
app.openapi_schema = None  # Disable OpenAPI schema for tests (avoids deps type validation)
from app.database import Base, get_db
from app.config import settings


@pytest_asyncio.fixture(scope="session")
async def engine():
    """Create a test database engine and run all migrations."""
    from alembic.config import Config
    from alembic import command

    alembic_cfg = Config("alembic.ini")
    alembic_cfg.set_main_option("sqlalchemy.url", settings.database_url)
    command.upgrade(alembic_cfg, "head")

    _engine = create_async_engine(settings.database_url, echo=False)
    yield _engine
    await _engine.dispose()


@pytest_asyncio.fixture()
async def db(engine) -> AsyncSession:
    """Return a session that rolls back after each test."""
    async with engine.connect() as conn:
        await conn.begin()
        session_factory = async_sessionmaker(bind=conn, expire_on_commit=False)
        async with session_factory() as session:
            yield session
        await conn.rollback()


@pytest_asyncio.fixture()
async def client(db) -> AsyncClient:
    """HTTP client wired to the test DB session."""

    async def override_get_db():
        yield db

    app.dependency_overrides[get_db] = override_get_db
    async with AsyncClient(
        transport=ASGITransport(app=app), base_url="http://test"
    ) as ac:
        yield ac
    app.dependency_overrides.clear()
