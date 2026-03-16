"""
Authentication service: registration, login, JWT tokens, password management.
"""

import logging
import secrets
from datetime import datetime, timedelta, timezone
from typing import Optional, Tuple

from jose import JWTError, jwt
from passlib.context import CryptContext
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.config import settings
from app.exceptions import UnauthorizedError, ConflictError, NotFoundError, ValidationError
from app.models.user import User, UserRole
from app.models.affiliate_profile import AffiliateProfile, AffiliateStatus
from app.models.affiliate_balance import AffiliateBalance
from app.schemas.auth import RegisterRequest, UserResponse

logger = logging.getLogger(__name__)

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def hash_password(password: str) -> str:
    return pwd_context.hash(password)


def verify_password(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(plain_password, hashed_password)


def create_access_token(data: dict) -> str:
    to_encode = data.copy()
    expire = datetime.now(timezone.utc) + timedelta(minutes=settings.access_token_expire_minutes)
    to_encode.update({"exp": expire, "type": "access"})
    return jwt.encode(to_encode, settings.secret_key, algorithm=settings.algorithm)


def create_refresh_token(data: dict) -> str:
    to_encode = data.copy()
    expire = datetime.now(timezone.utc) + timedelta(days=settings.refresh_token_expire_days)
    to_encode.update({"exp": expire, "type": "refresh"})
    return jwt.encode(to_encode, settings.secret_key, algorithm=settings.algorithm)


def decode_token(token: str) -> dict:
    try:
        payload = jwt.decode(token, settings.secret_key, algorithms=[settings.algorithm])
        return payload
    except JWTError as e:
        raise UnauthorizedError(f"Invalid token: {str(e)}")


async def register_affiliate(
    db: AsyncSession,
    data: RegisterRequest,
) -> Tuple[User, AffiliateProfile]:
    # Check email not taken
    result = await db.execute(select(User).where(User.email == data.email, User.is_deleted == False))
    existing = result.scalar_one_or_none()
    if existing:
        raise ConflictError("Email already registered")

    # Create user
    user = User(
        email=data.email,
        password_hash=hash_password(data.password),
        role=UserRole.affiliate,
        is_active=True,
        email_verified=False,
        email_verification_token=secrets.token_urlsafe(32),
    )
    db.add(user)
    await db.flush()  # Get user.id

    # Create affiliate profile
    profile = AffiliateProfile(
        user_id=user.id,
        status=AffiliateStatus.pending if settings.affiliate_require_approval else AffiliateStatus.approved,
        full_name=data.full_name,
        phone=data.phone,
        tiktok_url=data.tiktok_url,
        instagram_url=data.instagram_url,
        terms_version_accepted=1 if data.terms_accepted else None,
        terms_accepted_at=datetime.now(timezone.utc) if data.terms_accepted else None,
    )
    db.add(profile)

    # Create empty balance record
    balance = AffiliateBalance(affiliate_id=user.id)
    db.add(balance)

    await db.commit()
    await db.refresh(user)
    await db.refresh(profile)

    logger.info(f"New affiliate registered: {user.email} (id={user.id})")
    return user, profile


async def login(db: AsyncSession, email: str, password: str) -> Tuple[str, str, User]:
    result = await db.execute(
        select(User).where(User.email == email, User.is_deleted == False, User.is_active == True)
    )
    user = result.scalar_one_or_none()

    if not user or not verify_password(password, user.password_hash):
        raise UnauthorizedError("Invalid email or password")

    # Update last login
    user.last_login = datetime.now(timezone.utc)
    await db.commit()

    token_data = {"sub": str(user.id), "email": user.email, "role": user.role}
    access_token = create_access_token(token_data)
    refresh_token = create_refresh_token(token_data)

    return access_token, refresh_token, user


async def refresh_tokens(db: AsyncSession, refresh_token: str) -> Tuple[str, str]:
    payload = decode_token(refresh_token)
    if payload.get("type") != "refresh":
        raise UnauthorizedError("Invalid token type")

    user_id = int(payload["sub"])
    result = await db.execute(
        select(User).where(User.id == user_id, User.is_deleted == False, User.is_active == True)
    )
    user = result.scalar_one_or_none()
    if not user:
        raise UnauthorizedError("User not found")

    token_data = {"sub": str(user.id), "email": user.email, "role": user.role}
    new_access = create_access_token(token_data)
    new_refresh = create_refresh_token(token_data)
    return new_access, new_refresh


async def get_current_user(db: AsyncSession, token: str) -> UserResponse:
    payload = decode_token(token)
    if payload.get("type") != "access":
        raise UnauthorizedError("Invalid token type")

    user_id = int(payload["sub"])
    result = await db.execute(
        select(User).where(User.id == user_id, User.is_deleted == False, User.is_active == True)
    )
    user = result.scalar_one_or_none()
    if not user:
        raise UnauthorizedError("User not found")
    return UserResponse.model_validate(user)
