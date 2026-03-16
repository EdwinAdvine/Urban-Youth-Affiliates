from typing import Optional
from datetime import date, datetime, timezone
from fastapi import APIRouter, Depends, Query
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.deps import require_affiliate
from app.models.affiliate_balance import AffiliateBalance
from app.models.conversion import Conversion
from app.models.referral_link import ReferralLink
from app.models.user import User
from app.schemas.conversion import ConversionResponse

router = APIRouter()


@router.get("/affiliate/earnings/conversions")
async def list_conversions(
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    status: Optional[str] = Query(None),
    date_from: Optional[date] = Query(None, alias="from"),
    date_to: Optional[date] = Query(None, alias="to"),
    db: AsyncSession = Depends(get_db),
    user: User = Depends(require_affiliate),
):
    q = (
        select(Conversion)
        .join(ReferralLink, Conversion.referral_link_id == ReferralLink.id)
        .where(ReferralLink.affiliate_id == user.id)
    )
    if status:
        q = q.where(Conversion.status == status)
    if date_from:
        dt_from = datetime(date_from.year, date_from.month, date_from.day, tzinfo=timezone.utc)
        q = q.where(Conversion.created_at >= dt_from)
    if date_to:
        dt_to = datetime(date_to.year, date_to.month, date_to.day, 23, 59, 59, tzinfo=timezone.utc)
        q = q.where(Conversion.created_at <= dt_to)

    total = (await db.execute(select(func.count()).select_from(q.subquery()))).scalar() or 0
    items = (
        await db.execute(
            q.order_by(Conversion.created_at.desc())
            .offset((page - 1) * page_size)
            .limit(page_size)
        )
    ).scalars().all()

    import math
    return {
        "items": items,
        "total": total,
        "page": page,
        "page_size": page_size,
        "pages": max(1, math.ceil(total / page_size)),
    }


@router.get("/affiliate/earnings/balance")
async def get_balance(
    db: AsyncSession = Depends(get_db),
    user: User = Depends(require_affiliate),
):
    result = await db.execute(
        select(AffiliateBalance).where(AffiliateBalance.affiliate_id == user.id)
    )
    balance = result.scalar_one_or_none()
    if not balance:
        return {"affiliate_id": user.id, "pending": 0.0, "approved": 0.0, "paid_out": 0.0, "total_earned": 0.0}

    total_earned = (balance.approved or 0) + (balance.paid_out or 0)
    return {
        "affiliate_id": user.id,
        "pending": float(balance.pending or 0),
        "approved": float(balance.approved or 0),
        "paid_out": float(balance.paid_out or 0),
        "total_earned": float(total_earned),
    }
