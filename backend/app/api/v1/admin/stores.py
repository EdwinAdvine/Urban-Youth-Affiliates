"""
Admin stores CRUD.
"""

from fastapi import APIRouter, Depends, Query

from sqlalchemy.ext.asyncio import AsyncSession
from typing import Any

from app.deps import get_db, get_authenticated_user
from app.schemas.auth import UserResponse
from app.models.user import UserRole
from app.services.catalog_service import (
    list_stores,
    get_store,
    create_store,
    update_store,
    deactivate_store,
    rotate_store_api_key,
)
from app.schemas.store import StoreResponse, StoreCreate, StoreUpdate

router = APIRouter()

from fastapi import HTTPException

@router.get("/", response_model=None)
async def list_admin_stores(
    db: Any = Depends(get_db),
    active_only: bool = Query(False),
    current_user: UserResponse = Depends(get_authenticated_user)
):
    if current_user.role not in (UserRole.super_admin, UserRole.admin):
        raise HTTPException(status_code=403, detail="Admin access required")
    stores = await list_stores(db, active_only=active_only)
    return stores

@router.post("/", response_model=StoreResponse, status_code=201)
async def create_admin_store(
    data: StoreCreate,
    db: Any = Depends(get_db),
    current_user: UserResponse = Depends(get_authenticated_user)
):
    if current_user.role not in (UserRole.super_admin, UserRole.admin):
        raise HTTPException(status_code=403, detail="Admin access required")
    store = await create_store(db, data, current_user.id)
    return store

@router.get("/{store_id}", response_model=StoreResponse)
async def get_admin_store(
    store_id: int,
    db: Any = Depends(get_db),
    current_user: UserResponse = Depends(get_authenticated_user)
):
    if current_user.role not in (UserRole.super_admin, UserRole.admin):
        raise HTTPException(status_code=403, detail="Admin access required")
    store = await get_store(db, store_id)
    return store

@router.patch("/{store_id}", response_model=StoreResponse)
async def update_admin_store(
    store_id: int,
    data: StoreUpdate,
    db: Any = Depends(get_db),
    current_user: UserResponse = Depends(get_authenticated_user)
):
    if current_user.role not in (UserRole.super_admin, UserRole.admin):
        raise HTTPException(status_code=403, detail="Admin access required")
    store = await update_store(db, store_id, data)
    return store

@router.delete("/{store_id}", status_code=204)
async def deactivate_admin_store(
    store_id: int,
    db: Any = Depends(get_db),
    current_user: UserResponse = Depends(get_authenticated_user)
):
    if current_user.role not in (UserRole.super_admin, UserRole.admin):
        raise HTTPException(status_code=403, detail="Admin access required")
    await deactivate_store(db, store_id)

@router.post("/{store_id}/rotate-api-key", response_model=StoreResponse)
async def rotate_admin_store_api_key(
    store_id: int,
    db: Any = Depends(get_db),
    current_user: UserResponse = Depends(get_authenticated_user)
):
    if current_user.role not in (UserRole.super_admin, UserRole.admin):
        raise HTTPException(status_code=403, detail="Admin access required")
    store = await rotate_store_api_key(db, store_id)
    return store
