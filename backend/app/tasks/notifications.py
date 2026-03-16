"""Celery notification tasks.

These run in the worker process (not the FastAPI process), so they use
synchronous SQLAlchemy sessions, not the async ones used by route handlers.
"""

import logging

from celery import shared_task
from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker

from app.config import settings
from app.tasks.celery_app import celery_app  # noqa: F401 — ensures tasks are registered

logger = logging.getLogger(__name__)

# Synchronous engine for worker use (Celery is sync by default)
_sync_engine = None
_SyncSession = None


def _get_sync_session() -> Session:
    global _sync_engine, _SyncSession
    if _SyncSession is None:
        sync_url = settings.database_url.replace("+asyncpg", "").replace("+aiopg", "")
        _sync_engine = create_engine(sync_url, pool_pre_ping=True)
        _SyncSession = sessionmaker(bind=_sync_engine)
    return _SyncSession()


def _create_notification(
    session: Session, *, user_id: int, title: str, message: str,
    notification_type: str = "info", action_url: str | None = None
) -> None:
    from app.models.notification import Notification

    notif = Notification(
        user_id=user_id,
        title=title,
        message=message,
        notification_type=notification_type,
        action_url=action_url,
    )
    session.add(notif)
    session.commit()


# ─── Tasks ────────────────────────────────────────────────────────────────────

@celery_app.task(bind=True, name="tasks.notify_affiliate_approved", max_retries=3)
def notify_affiliate_approved(self, *, user_id: int, email: str, full_name: str) -> None:
    try:
        from app.tasks.email_helper import affiliate_approved_email

        # In-app notification
        session = _get_sync_session()
        try:
            _create_notification(
                session,
                user_id=user_id,
                title="Application Approved!",
                message="Your affiliate application has been approved. You can now generate referral links.",
                notification_type="success",
                action_url="/affiliate/marketplace",
            )
        finally:
            session.close()

        # Email
        affiliate_approved_email(to=email, full_name=full_name)

    except Exception as exc:
        logger.error("notify_affiliate_approved failed for user %d: %s", user_id, exc)
        raise self.retry(exc=exc, countdown=60)


@celery_app.task(bind=True, name="tasks.notify_affiliate_rejected", max_retries=3)
def notify_affiliate_rejected(
    self, *, user_id: int, email: str, full_name: str, reason: str = ""
) -> None:
    try:
        from app.tasks.email_helper import affiliate_rejected_email

        session = _get_sync_session()
        try:
            _create_notification(
                session,
                user_id=user_id,
                title="Application Not Approved",
                message=f"Your affiliate application was not approved. {reason}".strip(),
                notification_type="error",
            )
        finally:
            session.close()

        affiliate_rejected_email(to=email, full_name=full_name, reason=reason)

    except Exception as exc:
        logger.error("notify_affiliate_rejected failed for user %d: %s", user_id, exc)
        raise self.retry(exc=exc, countdown=60)


@celery_app.task(bind=True, name="tasks.notify_new_sale", max_retries=3)
def notify_new_sale(
    self,
    *,
    affiliate_user_id: int,
    affiliate_email: str,
    affiliate_name: str,
    order_id: str,
    sale_amount: float,
    commission: float,
) -> None:
    try:
        from app.tasks.email_helper import new_sale_email

        session = _get_sync_session()
        try:
            _create_notification(
                session,
                user_id=affiliate_user_id,
                title="New Sale!",
                message=f"You earned KES {commission:,.2f} commission on order {order_id}.",
                notification_type="success",
                action_url="/affiliate/earnings",
            )
        finally:
            session.close()

        new_sale_email(
            to=affiliate_email,
            full_name=affiliate_name,
            order_id=order_id,
            sale_amount=sale_amount,
            commission=commission,
        )

    except Exception as exc:
        logger.error("notify_new_sale failed for user %d: %s", affiliate_user_id, exc)
        raise self.retry(exc=exc, countdown=60)


@celery_app.task(bind=True, name="tasks.notify_payout_approved", max_retries=3)
def notify_payout_approved(
    self, *, user_id: int, email: str, full_name: str, amount: float
) -> None:
    try:
        from app.tasks.email_helper import payout_approved_email

        session = _get_sync_session()
        try:
            _create_notification(
                session,
                user_id=user_id,
                title="Payout Sent",
                message=f"Your payout of KES {amount:,.2f} has been initiated.",
                notification_type="success",
                action_url="/affiliate/payouts",
            )
        finally:
            session.close()

        payout_approved_email(to=email, full_name=full_name, amount=amount)

    except Exception as exc:
        logger.error("notify_payout_approved failed for user %d: %s", user_id, exc)
        raise self.retry(exc=exc, countdown=60)


@celery_app.task(bind=True, name="tasks.notify_payout_failed", max_retries=3)
def notify_payout_failed(
    self, *, user_id: int, email: str, full_name: str, amount: float, reason: str = ""
) -> None:
    try:
        from app.tasks.email_helper import payout_failed_email

        session = _get_sync_session()
        try:
            _create_notification(
                session,
                user_id=user_id,
                title="Payout Failed",
                message=f"Your payout of KES {amount:,.2f} could not be processed. {reason}".strip(),
                notification_type="error",
                action_url="/affiliate/payouts",
            )
        finally:
            session.close()

        payout_failed_email(to=email, full_name=full_name, amount=amount, reason=reason)

    except Exception as exc:
        logger.error("notify_payout_failed failed for user %d: %s", user_id, exc)
        raise self.retry(exc=exc, countdown=60)
