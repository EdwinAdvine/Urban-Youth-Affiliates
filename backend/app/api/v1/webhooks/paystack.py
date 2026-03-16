import json
import logging
from fastapi import APIRouter, Header, Request, status
from fastapi.responses import JSONResponse
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import Depends

from app.database import get_db
from app.services.payout_service import handle_paystack_webhook

logger = logging.getLogger(__name__)
router = APIRouter()


@router.post("/webhooks/paystack", status_code=status.HTTP_200_OK)
async def paystack_webhook(
    request: Request,
    x_paystack_signature: str = Header(None),
    db: AsyncSession = Depends(get_db),
):
    body = await request.body()

    # Verify signature
    from app.services.payments.paystack import verify_webhook_signature
    if x_paystack_signature:
        is_valid = await verify_webhook_signature(body, x_paystack_signature)
        if not is_valid:
            logger.warning("Invalid Paystack webhook signature")
            return JSONResponse(status_code=400, content={"error": "Invalid signature"})

    try:
        payload = json.loads(body)
        event = payload.get("event", "")
        data = payload.get("data", {})
        logger.info(f"Paystack webhook event: {event}")
        await handle_paystack_webhook(db, event, data)
    except Exception as e:
        logger.error(f"Paystack webhook error: {str(e)}", exc_info=True)

    return {"status": "ok"}
