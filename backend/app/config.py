"""
Application configuration using Pydantic Settings.

Type-safe configuration management with environment variable loading,
validation, and defaults.
"""

from functools import lru_cache
from typing import List, Optional
from pydantic import Field, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env", env_file_encoding="utf-8", case_sensitive=False, extra="ignore"
    )

    # Environment
    environment: str = Field(default="development")
    debug: bool = Field(default=False)

    # Application
    app_name: str = Field(default="Y&U Affiliates")
    app_version: str = Field(default="1.0.0")
    api_v1_prefix: str = Field(default="/api/v1")

    # Database
    database_url: str = Field(..., description="PostgreSQL connection URL (required)")
    database_read_url: Optional[str] = Field(default=None)
    database_pool_size: int = Field(default=20)
    database_max_overflow: int = Field(default=30)
    database_pool_timeout: int = Field(default=10)
    database_pool_recycle: int = Field(default=1800)
    database_echo: bool = Field(default=False)
    database_statement_timeout: int = Field(default=30000)
    database_idle_in_transaction_timeout: int = Field(default=60000)

    # Redis
    redis_url: str = Field(..., description="Redis connection URL (required)")
    redis_password: str = Field(default="", description="Optional Redis password")
    redis_cache_ttl: int = Field(default=300)
    redis_session_ttl: int = Field(default=86400)

    # Security / JWT
    secret_key: str = Field(..., min_length=32)
    algorithm: str = Field(default="HS256")
    access_token_expire_minutes: int = Field(default=30)
    refresh_token_expire_days: int = Field(default=7)

    # CORS
    cors_origins: str = Field(default="http://localhost:3000")
    cors_allow_credentials: bool = Field(default=True)
    cors_allow_methods: List[str] = Field(default=["*"])
    cors_allow_headers: List[str] = Field(default=["*"])

    @property
    def cors_origins_list(self) -> List[str]:
        return [origin.strip() for origin in self.cors_origins.split(",")]

    # Paystack
    paystack_secret_key: str = Field(default="")
    paystack_public_key: str = Field(default="")
    paystack_webhook_secret: str = Field(default="")

    # Email
    smtp_host: str = Field(default="smtp.gmail.com")
    smtp_port: int = Field(default=587)
    smtp_user: str = Field(default="")
    smtp_password: str = Field(default="")
    smtp_from_email: str = Field(default="noreply@yuaffiliates.co.ke")
    smtp_from_name: str = Field(default="Y&U Affiliates")
    email_backend: str = Field(default="smtp")

    # Celery
    celery_broker_url: str = Field(default="redis://redis:6379/0")
    celery_result_backend: str = Field(default="redis://redis:6379/0")

    # Affiliate Platform Settings
    affiliate_require_approval: bool = Field(default=True)
    default_commission_rate: float = Field(default=0.10, description="Default 10% commission")
    min_payout_threshold: int = Field(default=500, description="Minimum KES for payout")
    cookie_days: int = Field(default=30, description="Days referral cookie stays valid")

    # Store webhook security
    store_api_key: str = Field(default="", description="Shared API key for store conversion webhooks")

    # Observability
    sentry_dsn: str = Field(default="")
    enable_tracing: bool = Field(default=False)
    enable_metrics: bool = Field(default=True)

    # File uploads
    max_upload_size_mb: int = Field(default=10)
    upload_dir: str = Field(default="uploads")

    @property
    def is_development(self) -> bool:
        return self.environment == "development"

    @property
    def is_production(self) -> bool:
        return self.environment == "production"

    @property
    def is_testing(self) -> bool:
        return self.environment == "testing"


settings = Settings()


@lru_cache
def get_settings() -> Settings:
    return settings
