"""
Brand Battle - Celery Background Task Worker Configuration
Configures Redis as task broker and result backend.
"""

from celery import Celery
from config import settings

celery_app = Celery(
    "brand_battle_tasks",
    broker=settings.REDIS_URL,
    backend=settings.REDIS_URL,
    include=["tasks"]
)

celery_app.conf.update(
    task_serializer="json",
    accept_content=["json"],
    result_serializer="json",
    timezone="UTC",
    enable_utc=True,
    result_expires=3600,
    worker_prefetch_multiplier=1,
)
