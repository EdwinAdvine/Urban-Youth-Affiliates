"""
Admin products CRUD.
"""

from fastapi import APIRouter, Depends, Query, HTTPException
from typing import Optional

from sqlalchemy.ext.asyncio import AsyncSession

from app.deps import get_db, get_current_user
from app.models.user import User, UserRole
from app.services.catalog_service import (
    list_products,
    get_product,
    create_product,
    update_product,
    soft_delete_product,
)
from app.schemas.product import ProductListResponse, ProductCreate, ProductUpdate

router = APIRouter()

@router.get("/", response_model=list[Product])
async def list_admin_products(
    db: AsyncSession = Depends(get_db),
    store_id: Optional[int] = Query(None),
    category: Optional[str] = Query(None),
    search: Optional[str] = Query(None),
    active_only: bool = Query(True),
    current_user: User = Depends(get_current_user)
):
    if current_user.role not in (UserRole.super_admin, UserRole.admin):
        raise HTTPException(status_code=403, detail="Admin access required")
    products = await list_products(
        db, store_id=store_id, category=category, search=search, active_only=active_only
    )
    return products

@router.post("/", response_model=Product, status_code=201)
async def create_admin_product(
    data: ProductCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    if current_user.role not in (UserRole.super_admin, UserRole.admin):
        raise HTTPException(status_code=403, detail="Admin access required")
    product = await create_product(db, data)
    return product

@router.get("/{product_id}", response_model=Product)
async def get_admin_product(
    product_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    if current_user.role not in (UserRole.super_admin, UserRole.admin):
        raise HTTPException(status_code=403, detail="Admin access required")
    product = await get_product(db, product_id)
    return product

@router.patch("/{product_id}", response_model=Product)
async def update_admin_product(
    product_id: int,
    data: ProductUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    if current_user.role not in (UserRole.super_admin, UserRole.admin):
        raise HTTPException(status_code=403, detail="Admin access required")
    product = await update_product(db, product_id, data)
    return product

@router.delete("/{product_id}", status_code=204)
async def delete_admin_product(
    product_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    if current_user.role not in (UserRole.super_admin, UserRole.admin):
        raise HTTPException(status_code=403, detail="Admin access required")
    await soft_delete_product(db, product_id)
