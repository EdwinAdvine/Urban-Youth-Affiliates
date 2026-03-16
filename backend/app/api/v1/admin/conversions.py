from typing import List, Optional
from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.database import get_db
from app.deps import require_admin
from app.models.user import User
from app.models.conversion import Conversion, ConversionStatus
from app.schemas.conversion import ConversionResponse, ConversionApprovalRequest
from app.services.commission_service import approve_conversion, reject_conversion

router = APIRouter()


@router.get("/admin/conversions", response_model=List[ConversionResponse])
async def list_conversions(
    status: Optional[str] = Query(None),
    db: AsyncSession = Depends(get_db),
    user: User = Depends(require_admin),
):
    q = select(Conversion)
    if status:
        q = q.where(Conversion.status == status)
    q = q.order_by(Conversion.created_at.desc())
    result = await db.execute(q)
    return result.scalars().all()


@router.post("/admin/conversions/{conversion_id}/action", response_model=ConversionResponse)
async def conversion_action(
    conversion_id: int,
    data: ConversionApprovalRequest,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(require_admin),
):
    if data.action == "approve":
        return await approve_conversion(db, conversion_id, user.id)
    elif data.action == "reject":
        return await reject_conversion(db, conversion_id, user.id, data.notes)
    else:
        from app.exceptions import ValidationError
        raise ValidationError(f"Unknown action: {data.action}")
