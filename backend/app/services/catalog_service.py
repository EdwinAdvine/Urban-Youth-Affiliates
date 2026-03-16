"""Catalog service — CRUD for stores, products, and campaigns.

Route handlers should call these functions instead of querying the DB directly,
keeping route files thin and business logic testable.
"""

from __future__ import annotations

import secrets
from datetime import datetime, timezone
from typing import Optional

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.exceptions import ConflictError, NotFoundError
from app.models.campaign import Campaign
from app.models.product import Product
from app.models.store import Store
from app.schemas.campaign import CampaignCreate, CampaignUpdate
from app.schemas.product import ProductCreate, ProductUpdate
from app.schemas.store import StoreCreate, StoreUpdate

# ─── Stores ───────────────────────────────────────────────────────────────────


async def list_stores(db: AsyncSession, *, active_only: bool = False) -> list[Store]:
    q = select(Store)
    if active_only:
        q = q.where(Store.active == True)  # noqa: E712
    q = q.order_by(Store.created_at.desc())
    result = await db.execute(q)
    return list(result.scalars().all())


async def get_store(db: AsyncSession, store_id: int) -> Store:
    result = await db.execute(select(Store).where(Store.id == store_id))
    store = result.scalar_one_or_none()
    if not store:
        raise NotFoundError("Store")
    return store


async def get_store_by_api_key(db: AsyncSession, api_key: str) -> Optional[Store]:
    result = await db.execute(
        select(Store).where(Store.api_key == api_key, Store.active == True)  # noqa: E712
    )
    return result.scalar_one_or_none()


async def create_store(db: AsyncSession, data: StoreCreate, admin_id: int) -> Store:
    existing = await db.execute(select(Store).where(Store.slug == data.slug))
    if existing.scalar_one_or_none():
        raise ConflictError(f"Store with slug '{data.slug}' already exists")

    store = Store(
        **data.model_dump(),
        admin_id=admin_id,
        api_key=secrets.token_urlsafe(32),
    )
    db.add(store)
    await db.commit()
    await db.refresh(store)
    return store


async def update_store(db: AsyncSession, store_id: int, data: StoreUpdate) -> Store:
    store = await get_store(db, store_id)
    for field, value in data.model_dump(exclude_none=True).items():
        setattr(store, field, value)
    await db.commit()
    await db.refresh(store)
    return store


async def deactivate_store(db: AsyncSession, store_id: int) -> None:
    store = await get_store(db, store_id)
    store.active = False
    await db.commit()


async def rotate_store_api_key(db: AsyncSession, store_id: int) -> Store:
    """Generate a new API key for a store (e.g. after suspected compromise)."""
    store = await get_store(db, store_id)
    store.api_key = secrets.token_urlsafe(32)
    await db.commit()
    await db.refresh(store)
    return store


# ─── Products ─────────────────────────────────────────────────────────────────


async def list_products(
    db: AsyncSession,
    *,
    store_id: Optional[int] = None,
    category: Optional[str] = None,
    search: Optional[str] = None,
    active_only: bool = True,
) -> list[Product]:
    q = select(Product).where(Product.is_deleted == False)  # noqa: E712
    if store_id:
        q = q.where(Product.store_id == store_id)
    if category:
        q = q.where(Product.category == category)
    if active_only:
        q = q.where(Product.active == True)  # noqa: E712
    if search:
        q = q.where(Product.name.ilike(f"%{search}%"))
    q = q.order_by(Product.created_at.desc())
    result = await db.execute(q)
    return list(result.scalars().all())


async def get_product(db: AsyncSession, product_id: int) -> Product:
    result = await db.execute(
        select(Product).where(Product.id == product_id, Product.is_deleted == False)  # noqa: E712
    )
    product = result.scalar_one_or_none()
    if not product:
        raise NotFoundError("Product")
    return product


async def create_product(db: AsyncSession, data: ProductCreate) -> Product:
    product = Product(**data.model_dump())
    db.add(product)
    await db.commit()
    await db.refresh(product)
    return product


async def update_product(db: AsyncSession, product_id: int, data: ProductUpdate) -> Product:
    product = await get_product(db, product_id)
    for field, value in data.model_dump(exclude_none=True).items():
        setattr(product, field, value)
    product.updated_at = datetime.now(timezone.utc)
    await db.commit()
    await db.refresh(product)
    return product


async def soft_delete_product(db: AsyncSession, product_id: int) -> None:
    product = await get_product(db, product_id)
    product.is_deleted = True
    await db.commit()


# ─── Campaigns ────────────────────────────────────────────────────────────────


async def list_campaigns(
    db: AsyncSession,
    *,
    store_id: Optional[int] = None,
    product_id: Optional[int] = None,
    active_only: bool = False,
) -> list[Campaign]:
    q = select(Campaign)
    if store_id:
        q = q.where(Campaign.store_id == store_id)
    if product_id:
        q = q.where(Campaign.product_id == product_id)
    if active_only:
        q = q.where(Campaign.active == True)  # noqa: E712
    q = q.order_by(Campaign.created_at.desc())
    result = await db.execute(q)
    return list(result.scalars().all())


async def get_campaign(db: AsyncSession, campaign_id: int) -> Campaign:
    result = await db.execute(select(Campaign).where(Campaign.id == campaign_id))
    campaign = result.scalar_one_or_none()
    if not campaign:
        raise NotFoundError("Campaign")
    return campaign


async def create_campaign(db: AsyncSession, data: CampaignCreate) -> Campaign:
    campaign = Campaign(**data.model_dump())
    db.add(campaign)
    await db.commit()
    await db.refresh(campaign)
    return campaign


async def update_campaign(
    db: AsyncSession, campaign_id: int, data: CampaignUpdate
) -> Campaign:
    campaign = await get_campaign(db, campaign_id)
    for field, value in data.model_dump(exclude_none=True).items():
        setattr(campaign, field, value)
    await db.commit()
    await db.refresh(campaign)
    return campaign


async def delete_campaign(db: AsyncSession, campaign_id: int) -> None:
    campaign = await get_campaign(db, campaign_id)
    campaign.active = False
    await db.commit()


async def resolve_campaign_for_product(
    db: AsyncSession, product_id: int, store_id: int
) -> Optional[Campaign]:
    """Return the best-matching active campaign using resolution order:
    1. Product-level campaign
    2. Store-level campaign
    3. None (caller falls back to global default rate)
    """
    # Product-level
    result = await db.execute(
        select(Campaign).where(
            Campaign.product_id == product_id,
            Campaign.active == True,  # noqa: E712
        )
    )
    campaign = result.scalars().first()
    if campaign:
        return campaign

    # Store-level
    result = await db.execute(
        select(Campaign).where(
            Campaign.store_id == store_id,
            Campaign.product_id == None,  # noqa: E711
            Campaign.active == True,  # noqa: E712
        )
    )
    campaign = result.scalars().first()
    return campaign
