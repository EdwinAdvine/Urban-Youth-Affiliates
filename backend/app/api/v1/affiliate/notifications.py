from typing import List

from fastapi import APIRouter, Depends
from sqlalchemy import update
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select

from app.database import get_db
from app.deps import require_affiliate
from app.models.notification import Notification
from app.models.user import User

router = APIRouter()


@router.get("/affiliate/notifications", response_model=List[dict])
async def list_notifications(
    db: AsyncSession = Depends(get_db),
    user: User = Depends(require_affiliate),
):
    result = await db.execute(
        select(Notification)
        .where(Notification.user_id == user.id)
        .order_by(Notification.created_at.desc())
        .limit(50)
    )
    rows = result.scalars().all()
    return [
        {
            "id": n.id,
            "title": n.title,
            "message": n.message,
            "notification_type": n.notification_type,
            "read": n.read,
            "action_url": n.action_url,
            "created_at": n.created_at.isoformat() if n.created_at else None,
        }
        for n in rows
    ]


@router.get("/affiliate/notifications/unread-count")
async def unread_count(
    db: AsyncSession = Depends(get_db),
    user: User = Depends(require_affiliate),
):
    from sqlalchemy import func

    result = await db.execute(
        select(func.count()).where(
            Notification.user_id == user.id, Notification.read == False  # noqa: E712
        )
    )
    count = result.scalar_one()
    return {"unread": count}


@router.patch("/affiliate/notifications/{notification_id}/read")
async def mark_read(
    notification_id: int,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(require_affiliate),
):
    from datetime import datetime, timezone

    await db.execute(
        update(Notification)
        .where(Notification.id == notification_id, Notification.user_id == user.id)
        .values(read=True, read_at=datetime.now(timezone.utc))
    )
    await db.commit()
    return {"ok": True}


@router.post("/affiliate/notifications/read-all")
async def mark_all_read(
    db: AsyncSession = Depends(get_db),
    user: User = Depends(require_affiliate),
):
    from datetime import datetime, timezone

    await db.execute(
        update(Notification)
        .where(Notification.user_id == user.id, Notification.read == False)  # noqa: E712
        .values(read=True, read_at=datetime.now(timezone.utc))
    )
    await db.commit()
    return {"ok": True}
