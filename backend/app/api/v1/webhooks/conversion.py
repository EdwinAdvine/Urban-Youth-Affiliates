from fastapi import APIRouter, Depends, Header, status
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Optional

from app.database import get_db
from app.schemas.conversion import ConversionWebhookRequest, ConversionResponse
from app.services.tracking_service import record_conversion
from app.models.conversion import ConversionSource
from app.exceptions import ValidationError
from app.config import settings

router = APIRouter()


@router.post("/webhooks/conversion", response_model=ConversionResponse, status_code=status.HTTP_201_CREATED)
async def store_conversion(
    data: ConversionWebhookRequest,
    x_store_api_key: Optional[str] = Header(None),
    db: AsyncSession = Depends(get_db),
):
    """
    Stores call this endpoint to report a completed sale.

    Required headers: X-Store-Api-Key
    Body: ref_code, external_order_id, sale_amount
    """
    api_key = x_store_api_key or data.store_api_key
    if not api_key:
        raise ValidationError("Store API key required (X-Store-Api-Key header)")

    return await record_conversion(
        db=db,
        ref_code=data.ref_code,
        external_order_id=data.external_order_id,
        sale_amount=data.sale_amount,
        store_api_key=api_key,
        source=ConversionSource.webhook,
    )
