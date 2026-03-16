"""
Login endpoint.
"""

from fastapi import APIRouter, Depends, HTTPException, status

from sqlalchemy.ext.asyncio import AsyncSession

from app.deps import get_db
from app.services.auth_service import login
from app.schemas.auth import LoginRequest, TokenResponse
from app.models.user import User

router = APIRouter()

@router.post("/login", response_model=TokenResponse, status_code=status.HTTP_200_OK)
async def login_endpoint(
    request: LoginRequest,
    db: AsyncSession = Depends(get_db)
) -> TokenResponse:
    try:
        access_token, refresh_token, user = await login(db, request.email, request.password)
        return TokenResponse(
            access_token=access_token,
            refresh_token=refresh_token,
            user_id=user.id,
            email=user.email,
            role=user.role
        )
    except Exception:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid credentials")