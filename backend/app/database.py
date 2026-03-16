"""
Database connection and session management.

SQLAlchemy 2.0 async engine configuration, session management, and utilities.
"""

from typing import AsyncGenerator, Any
import logging

from sqlalchemy.ext.asyncio import (
    AsyncSession,
    AsyncEngine,
    create_async_engine,
    async_sessionmaker,
)
from sqlalchemy.orm import declarative_base
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy import text

from app.config import settings

logger = logging.getLogger(__name__)

Base = declarative_base()

engine: AsyncEngine = None  # type: ignore
AsyncSessionLocal: async_sessionmaker[AsyncSession] = None  # type: ignore

read_engine: AsyncEngine = None  # type: ignore
AsyncReadSessionLocal: async_sessionmaker[AsyncSession] = None  # type: ignore


def get_database_url() -> str:
    db_url = settings.database_url
    if db_url.startswith("postgresql://"):
        db_url = db_url.replace("postgresql://", "postgresql+asyncpg://", 1)
    elif not db_url.startswith("postgresql+asyncpg://"):
        logger.warning("Database URL should use postgresql+asyncpg:// for async support")
    return db_url


async def init_db() -> None:
    global engine, AsyncSessionLocal

    try:
        db_url = get_database_url()
        logger.info("Initializing database connection...")

        engine = create_async_engine(
            db_url,
            echo=settings.database_echo,
            pool_size=settings.database_pool_size,
            max_overflow=settings.database_max_overflow,
            pool_timeout=settings.database_pool_timeout,
            pool_pre_ping=True,
            pool_recycle=settings.database_pool_recycle,
            connect_args={
                "server_settings": {
                    "statement_timeout": str(settings.database_statement_timeout),
                    "idle_in_transaction_session_timeout": str(
                        settings.database_idle_in_transaction_timeout
                    ),
                }
            },
        )

        AsyncSessionLocal = async_sessionmaker(
            engine,
            class_=AsyncSession,
            expire_on_commit=False,
            autocommit=False,
            autoflush=False,
        )

        async with engine.begin() as conn:
            await conn.execute(text("SELECT 1"))
            logger.info("Database connection test successful")

        await _init_read_engine()

    except SQLAlchemyError as e:
        logger.error(f"Failed to initialize database: {str(e)}")
        raise
    except Exception as e:
        logger.error(f"Unexpected error during database initialization: {str(e)}")
        raise


async def _init_read_engine() -> None:
    global read_engine, AsyncReadSessionLocal

    if settings.database_read_url:
        read_url = settings.database_read_url
        if read_url.startswith("postgresql://"):
            read_url = read_url.replace("postgresql://", "postgresql+asyncpg://", 1)

        read_engine = create_async_engine(
            read_url,
            echo=settings.database_echo,
            pool_size=settings.database_pool_size,
            max_overflow=settings.database_max_overflow,
            pool_timeout=settings.database_pool_timeout,
            pool_pre_ping=True,
            pool_recycle=settings.database_pool_recycle,
            connect_args={
                "server_settings": {
                    "statement_timeout": str(settings.database_statement_timeout),
                    "default_transaction_read_only": "on",
                }
            },
        )

        AsyncReadSessionLocal = async_sessionmaker(
            read_engine,
            class_=AsyncSession,
            expire_on_commit=False,
            autocommit=False,
            autoflush=False,
        )

        async with read_engine.begin() as conn:
            await conn.execute(text("SELECT 1"))
        logger.info("Read replica engine initialized successfully")
    else:
        read_engine = engine
        AsyncReadSessionLocal = AsyncSessionLocal
        logger.info("No read replica configured; reads use the primary engine")


async def get_db() -> AsyncGenerator[Any, None]:
    if AsyncSessionLocal is None:
        raise RuntimeError("Database not initialized. Call init_db() during startup.")

    async with AsyncSessionLocal() as session:
        try:
            yield session
        except SQLAlchemyError as e:
            await session.rollback()
            logger.error(f"Database session error: {str(e)}")
            raise
        except Exception as e:
            await session.rollback()
            logger.error(f"Unexpected error in database session: {str(e)}")
            raise
        finally:
            await session.close()


async def get_read_db() -> AsyncGenerator[Any, None]:
    if AsyncReadSessionLocal is None:
        raise RuntimeError("Database not initialized. Call init_db() during startup.")

    async with AsyncReadSessionLocal() as session:
        try:
            yield session
        except SQLAlchemyError as e:
            await session.rollback()
            logger.error(f"Read session error: {e}")
            raise
        finally:
            await session.close()


async def close_db() -> None:
    global engine, read_engine

    if read_engine and read_engine is not engine:
        logger.info("Closing read replica connection...")
        await read_engine.dispose()
        read_engine = None

    if engine:
        logger.info("Closing database connection...")
        await engine.dispose()
        logger.info("Database connection closed successfully")
        engine = None


async def check_db_connection() -> bool:
    if engine is None:
        return False
    try:
        async with engine.begin() as conn:
            await conn.execute(text("SELECT 1"))
        return True
    except Exception as e:
        logger.error(f"Database connection check failed: {str(e)}")
        return False


class DatabaseSession:
    def __init__(self):
        if AsyncSessionLocal is None:
            raise RuntimeError("Database not initialized. Call init_db() during startup.")
        self.session: AsyncSession = None  # type: ignore

    async def __aenter__(self) -> AsyncSession:
        self.session = AsyncSessionLocal()
        return self.session

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        if self.session:
            if exc_type is not None:
                await self.session.rollback()
            else:
                await self.session.commit()
            await self.session.close()
        return False
