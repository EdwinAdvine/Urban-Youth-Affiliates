"""
Database seed script.

Run after migrations:
    alembic upgrade head && python -m app.seed

Creates:
  - super_admin user
  - One test store
  - Global platform settings
  - One default global campaign
  - One test affiliate (pending)
"""

import asyncio
import os
import sys
import logging
from datetime import datetime, timezone

# Add backend directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession
from sqlalchemy import select

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Load environment
from dotenv import load_dotenv
load_dotenv()


async def seed():
    db_url = os.environ.get("DATABASE_URL", "")
    if db_url.startswith("postgresql://"):
        db_url = db_url.replace("postgresql://", "postgresql+asyncpg://", 1)

    engine = create_async_engine(db_url, echo=False)
    SessionLocal = async_sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)

    async with SessionLocal() as db:
        from app.models.user import User, UserRole
        from app.models.affiliate_profile import AffiliateProfile, AffiliateStatus
        from app.models.affiliate_balance import AffiliateBalance
        from app.models.store import Store
        from app.models.campaign import Campaign, CommissionType
        from app.models.platform_setting import PlatformSetting
        from app.services.auth_service import hash_password

        # ── Super Admin ─────────────────────────────────────────────
        result = await db.execute(select(User).where(User.email == "admin@yuaffiliates.co.ke"))
        if not result.scalar_one_or_none():
            admin = User(
                email="admin@yuaffiliates.co.ke",
                password_hash=hash_password("Admin@1234!"),
                role=UserRole.super_admin,
                is_active=True,
                email_verified=True,
            )
            db.add(admin)
            await db.flush()
            logger.info(f"Created super_admin: admin@yuaffiliates.co.ke / Admin@1234!")
        else:
            logger.info("super_admin already exists")

        # ── Test Store ───────────────────────────────────────────────
        result = await db.execute(select(Store).where(Store.slug == "yu-store"))
        if not result.scalar_one_or_none():
            store = Store(
                name="Y&U Main Store",
                slug="yu-store",
                website_url="https://yuaffiliates.co.ke",
                description="Youth & Urbanism flagship store",
                api_key="test-store-api-key-change-in-production",
                active=True,
            )
            db.add(store)
            await db.flush()
            logger.info(f"Created store: Y&U Main Store")
        else:
            logger.info("Test store already exists")

        await db.commit()

        # ── Default Global Campaign ──────────────────────────────────
        result = await db.execute(select(Campaign).where(Campaign.name == "Default Global Campaign"))
        if not result.scalar_one_or_none():
            campaign = Campaign(
                name="Default Global Campaign",
                product_id=None,
                store_id=None,
                commission_type=CommissionType.percent,
                rate=0.10,  # 10%
                cookie_days=30,
                active=True,
            )
            db.add(campaign)
            logger.info("Created default global campaign (10% commission)")
        else:
            logger.info("Default campaign already exists")

        # ── Platform Settings ───────────────────────────────────────
        defaults = {
            "default_commission_rate": "0.10",
            "min_payout_threshold": "500",
            "cookie_days": "30",
            "require_affiliate_approval": "true",
            "terms_version": "1",
        }
        for key, value in defaults.items():
            result = await db.execute(select(PlatformSetting).where(PlatformSetting.key == key))
            if not result.scalar_one_or_none():
                db.add(PlatformSetting(key=key, value=value))

        # ── Test Affiliate ───────────────────────────────────────────
        result = await db.execute(select(User).where(User.email == "affiliate@test.com"))
        if not result.scalar_one_or_none():
            aff_user = User(
                email="affiliate@test.com",
                password_hash=hash_password("Affiliate@1234!"),
                role=UserRole.affiliate,
                is_active=True,
                email_verified=True,
            )
            db.add(aff_user)
            await db.flush()

            aff_profile = AffiliateProfile(
                user_id=aff_user.id,
                status=AffiliateStatus.approved,
                full_name="Test Affiliate",
                phone="+254700000000",
                tiktok_url="https://tiktok.com/@testaffiliate",
                terms_version_accepted=1,
                terms_accepted_at=datetime.now(timezone.utc),
            )
            db.add(aff_profile)

            aff_balance = AffiliateBalance(affiliate_id=aff_user.id)
            db.add(aff_balance)
            logger.info("Created test affiliate: affiliate@test.com / Affiliate@1234!")
        else:
            logger.info("Test affiliate already exists")

        await db.commit()
        logger.info("Seed complete!")

    await engine.dispose()


if __name__ == "__main__":
    asyncio.run(seed())
