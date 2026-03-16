"""
Central router registration.
"""

from fastapi import FastAPI

from app.api.v1.auth.login import router as login_router
from app.api.v1.auth.register import router as register_router
from app.api.v1.auth.refresh import router as refresh_router
from app.api.v1.admin.stores import router as admin_stores_router
from app.api.v1.admin.products import router as admin_products_router
from app.api.v1.admin.campaigns import router as admin_campaigns_router
from app.api.v1.admin.affiliates import router as admin_affiliates_router
from app.api.v1.admin.conversions import router as admin_conversions_router
from app.api.v1.admin.payouts import router as admin_payouts_router
from app.api.v1.admin.analytics import router as admin_analytics_router
from app.api.v1.admin.settings import router as admin_settings_router
from app.api.v1.admin.creative_assets import router as admin_creative_assets_router
from app.api.v1.affiliate.dashboard import router as affiliate_dashboard_router
from app.api.v1.affiliate.links import router as affiliate_links_router
from app.api.v1.affiliate.earnings import router as affiliate_earnings_router
from app.api.v1.affiliate.payouts import router as affiliate_payouts_router
from app.api.v1.affiliate.marketplace import router as affiliate_marketplace_router
from app.api.v1.affiliate.profile import router as affiliate_profile_router
from app.api.v1.affiliate.notifications import router as affiliate_notifications_router
from app.api.v1.affiliate.stats import router as affiliate_stats_router
from app.api.v1.affiliate.creative_assets import router as affiliate_creative_assets_router
from app.api.v1.webhooks.conversion import router as webhook_conversion_router
from app.api.v1.webhooks.paystack import router as webhook_paystack_router
from app.api.v1.tracking import router as tracking_router
from app.api.v1.public.affiliate_profile import router as public_affiliate_router


def register_all_routers(app: FastAPI) -> None:
    prefix = "/api/v1"

    # Auth
    app.include_router(login_router, prefix=prefix, tags=["Auth"])
    app.include_router(register_router, prefix=prefix, tags=["Auth"])
    app.include_router(refresh_router, prefix=prefix, tags=["Auth"])

    # Admin
    app.include_router(admin_stores_router, prefix=prefix, tags=["Admin - Stores"])
    app.include_router(admin_products_router, prefix=prefix, tags=["Admin - Products"])
    app.include_router(admin_campaigns_router, prefix=prefix, tags=["Admin - Campaigns"])
    app.include_router(admin_affiliates_router, prefix=prefix, tags=["Admin - Affiliates"])
    app.include_router(admin_conversions_router, prefix=prefix, tags=["Admin - Conversions"])
    app.include_router(admin_payouts_router, prefix=prefix, tags=["Admin - Payouts"])
    app.include_router(admin_analytics_router, prefix=prefix, tags=["Admin - Analytics"])
    app.include_router(admin_settings_router, prefix=prefix, tags=["Admin - Settings"])
    app.include_router(admin_creative_assets_router, prefix=prefix, tags=["Admin - Creative Assets"])

    # Affiliate portal
    app.include_router(affiliate_dashboard_router, prefix=prefix, tags=["Affiliate - Dashboard"])
    app.include_router(affiliate_links_router, prefix=prefix, tags=["Affiliate - Links"])
    app.include_router(affiliate_earnings_router, prefix=prefix, tags=["Affiliate - Earnings"])
    app.include_router(affiliate_payouts_router, prefix=prefix, tags=["Affiliate - Payouts"])
    app.include_router(affiliate_marketplace_router, prefix=prefix, tags=["Affiliate - Marketplace"])
    app.include_router(affiliate_profile_router, prefix=prefix, tags=["Affiliate - Profile"])
    app.include_router(affiliate_notifications_router, prefix=prefix, tags=["Affiliate - Notifications"])
    app.include_router(affiliate_stats_router, prefix=prefix, tags=["Affiliate - Stats"])
    app.include_router(affiliate_creative_assets_router, prefix=prefix, tags=["Affiliate - Creative Assets"])

    # Webhooks
    app.include_router(webhook_conversion_router, prefix=prefix, tags=["Webhooks"])
    app.include_router(webhook_paystack_router, prefix=prefix, tags=["Webhooks"])

    # Tracking (public)
    app.include_router(tracking_router, tags=["Tracking"])

    # Public (no auth)
    app.include_router(public_affiliate_router, prefix=prefix, tags=["Public"])
