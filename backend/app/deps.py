"""
FastAPI dependencies: current user, role guards.
"""

from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.exceptions import UnauthorizedError, ForbiddenError
from app.schemas.auth import UserResponse
from app.models.user import UserRole
from app.services.auth_service import get_current_user

security = HTTPBearer()


async def get_authenticated_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: AsyncSession = Depends(get_db),
) -> UserResponse:
    return await get_current_user(db, credentials.credentials)


async def require_affiliate(user: UserResponse = Depends(get_authenticated_user)) -> UserResponse:
    if user.role not in (UserRole.affiliate, UserRole.admin, UserRole.super_admin):
        raise ForbiddenError("Affiliates only")
    return user


async def require_admin(user: UserResponse = Depends(get_authenticated_user)) -> UserResponse:
    if user.role not in (UserRole.admin, UserRole.super_admin):
        raise ForbiddenError("Admins only")
    return user


async def require_super_admin(user: UserResponse = Depends(get_authenticated_user)) -> UserResponse:
    if user.role != UserRole.super_admin:
        raise ForbiddenError("Super admins only")
    return user
