from typing import List, Optional
from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.database import get_db
from app.deps import require_affiliate
from app.models.user import User
from app.models.product import Product
from app.models.campaign import Campaign
from app.models.store import Store
from app.schemas.product import ProductResponse

router = APIRouter()


@router.get("/affiliate/marketplace")
async def marketplace(
    search: Optional[str] = Query(None),
    store_id: Optional[int] = Query(None),
    category: Optional[str] = Query(None),
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    db: AsyncSession = Depends(get_db),
    user: User = Depends(require_affiliate),
):
    q = (
        select(Product, Store, Campaign)
        .join(Store, Product.store_id == Store.id)
        .outerjoin(Campaign, Campaign.product_id == Product.id)
        .where(Product.active == True, Product.is_deleted == False, Store.active == True)
    )
    if search:
        q = q.where(Product.name.ilike(f"%{search}%"))
    if store_id:
        q = q.where(Product.store_id == store_id)
    if category:
        q = q.where(Product.category == category)

    q = q.offset((page - 1) * page_size).limit(page_size)
    result = await db.execute(q)
    rows = result.all()

    items = []
    for product, store, campaign in rows:
        item = {
            "id": product.id,
            "name": product.name,
            "price": float(product.price),
            "currency": product.currency,
            "description": product.description,
            "image_url": product.image_url,
            "category": product.category,
            "store_name": store.name,
            "store_id": store.id,
            "commission_rate": float(campaign.rate) if campaign else None,
            "commission_type": campaign.commission_type if campaign else None,
            "campaign_id": campaign.id if campaign else None,
        }
        items.append(item)

    return {"items": items, "page": page, "page_size": page_size}
