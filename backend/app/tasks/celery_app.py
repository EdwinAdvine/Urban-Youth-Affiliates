"""Celery application factory.

Start the worker with:
    celery -A app.tasks.celery_app worker --loglevel=info --concurrency=4
"""

from celery import Celery

from app.config import settings

celery_app = Celery(
    "yua",
    broker=settings.celery_broker_url,
    backend=settings.celery_result_backend,
    include=["app.tasks.notifications"],
)

celery_app.conf.update(
    task_serializer="json",
    result_serializer="json",
    accept_content=["json"],
    timezone="Africa/Nairobi",
    enable_utc=True,
    task_track_started=True,
    task_acks_late=True,
    worker_prefetch_multiplier=1,
    # Retry settings
    task_default_retry_delay=60,
    task_max_retries=3,
)
