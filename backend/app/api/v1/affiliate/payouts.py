from typing import List
from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.database import get_db
from app.deps import require_affiliate
from app.models.user import User
from app.models.payout_request import PayoutRequest
from app.schemas.payout import PayoutRequestCreate, PayoutRequestResponse
from app.services.payout_service import request_payout

router = APIRouter()


@router.post("/affiliate/payouts", response_model=PayoutRequestResponse, status_code=status.HTTP_201_CREATED)
async def create_payout_request(
    data: PayoutRequestCreate,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(require_affiliate),
):
    return await request_payout(db, user.id, data.amount)


@router.get("/affiliate/payouts", response_model=List[PayoutRequestResponse])
async def list_payout_requests(
    db: AsyncSession = Depends(get_db),
    user: User = Depends(require_affiliate),
):
    result = await db.execute(
        select(PayoutRequest)
        .where(PayoutRequest.affiliate_id == user.id)
        .order_by(PayoutRequest.requested_at.desc())
    )
    return result.scalars().all()
