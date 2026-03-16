from typing import Optional
from pydantic import BaseModel, EmailStr, Field
from app.models.user import UserRole


class LoginRequest(BaseModel):
    email: EmailStr
    password: str


class RegisterRequest(BaseModel):
    email: EmailStr
    password: str = Field(min_length=8)
    full_name: str = Field(min_length=2, max_length=255)
    phone: Optional[str] = None
    tiktok_url: Optional[str] = None
    instagram_url: Optional[str] = None
    terms_accepted: bool = Field(default=False)


class TokenResponse(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"
    user_id: int
    email: str
    role: UserRole


class RefreshRequest(BaseModel):
    refresh_token: str


class UserResponse(BaseModel):
    id: int
    email: str
    role: UserRole
    is_active: bool
    email_verified: bool

    model_config = {"from_attributes": True}
