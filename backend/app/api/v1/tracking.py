from fastapi import APIRouter, Depends, Request
from fastapi.responses import RedirectResponse
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.database import get_db
from app.services.tracking_service import record_click
from app.models.campaign import Campaign
from app.models.product import Product

router = APIRouter()

COOKIE_NAME = "yu_aff_ref"


@router.get("/track/{code}")
async def track_click(
    code: str,
    request: Request,
    db: AsyncSession = Depends(get_db),
):
    """
    Public click tracking endpoint.
    Records the click, sets a first-party cookie, and redirects to the product page.
    """
    link = await record_click(db, code, request)

    if not link:
        # Invalid code — redirect to homepage
        response = RedirectResponse(url="/", status_code=302)
        return response

    # Find redirect URL from campaign -> product
    result = await db.execute(select(Campaign).where(Campaign.id == link.campaign_id))
    campaign = result.scalar_one_or_none()

    redirect_url = "/"
    if campaign and campaign.product_id:
        result = await db.execute(select(Product).where(Product.id == campaign.product_id))
        product = result.scalar_one_or_none()
        if product and product.product_url:
            redirect_url = f"{product.product_url}?ref={code}"
        elif product:
            redirect_url = f"/?ref={code}"
    else:
        redirect_url = f"/?ref={code}"

    response = RedirectResponse(url=redirect_url, status_code=302)

    # Set first-party cookie with configurable expiry
    from app.config import settings
    from datetime import timedelta
    max_age = int(timedelta(days=settings.cookie_days).total_seconds())
    response.set_cookie(
        key=COOKIE_NAME,
        value=code,
        max_age=max_age,
        httponly=True,
        samesite="lax",
        secure=settings.is_production,
    )
    return response
