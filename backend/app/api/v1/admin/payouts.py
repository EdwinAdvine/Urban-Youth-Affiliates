from typing import List, Optional
from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.database import get_db
from app.deps import require_admin
from app.models.user import User
from app.models.payout_request import PayoutRequest, PayoutStatus
from app.schemas.payout import PayoutRequestResponse
from app.services.payout_service import approve_and_transfer

router = APIRouter()


@router.get("/admin/payouts", response_model=List[PayoutRequestResponse])
async def list_payouts(
    status: Optional[str] = Query(None),
    db: AsyncSession = Depends(get_db),
    user: User = Depends(require_admin),
):
    q = select(PayoutRequest)
    if status:
        q = q.where(PayoutRequest.status == status)
    q = q.order_by(PayoutRequest.requested_at.desc())
    result = await db.execute(q)
    return result.scalars().all()


@router.post("/admin/payouts/{payout_id}/approve", response_model=PayoutRequestResponse)
async def approve_payout(
    payout_id: int,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(require_admin),
):
    return await approve_and_transfer(db, payout_id, user.id)
