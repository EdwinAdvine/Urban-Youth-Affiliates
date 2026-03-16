"""
Refresh token endpoint.
"""

from fastapi import APIRouter, Depends, HTTPException, status

from sqlalchemy.ext.asyncio import AsyncSession

from app.deps import get_db
from app.services.auth_service import refresh_tokens, decode_token
from app.schemas.auth import RefreshRequest, TokenResponse

router = APIRouter()

@router.post("/refresh", response_model=TokenResponse)
async def refresh_endpoint(
    request: RefreshRequest,
    db: AsyncSession = Depends(get_db)
) -> TokenResponse:
    payload = decode_token(request.refresh_token)
    if payload.get("type") != "refresh":
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token type")
    
    access_token, refresh_token = await refresh_tokens(db, request.refresh_token)
    
    return TokenResponse(
        access_token=access_token,
        refresh_token=refresh_token,
        user_id=int(payload["sub"]),
        email=payload["email"],
        role=payload["role"]
    )
