"""
Celery worker configuration for background tasks
"""
from celery import Celery
from app.core.config import settings

# Initialize Celery app
celery_app = Celery(
    "evo-log-worker",
    broker=getattr(settings, "CELERY_BROKER_URL", "redis://localhost:6379/1"),
    backend=getattr(settings, "CELERY_RESULT_BACKEND", "redis://localhost:6379/2"),
)

celery_app.conf.update(
    task_serializer="json",
    accept_content=["json"],
    result_serializer="json",
    timezone="Africa/Douala",
    enable_utc=True,
    task_track_started=True,
    task_acks_late=True,
    worker_prefetch_multiplier=1,
)

# Auto-discover tasks from installed apps
celery_app.autodiscover_tasks(["app.services"], force=True)


@celery_app.task(bind=True, name="app.worker.health_check")
def health_check_task(self):
    """Periodic health check task for Celery workers."""
    return {"status": "ok", "worker": "evo-log-worker"}
