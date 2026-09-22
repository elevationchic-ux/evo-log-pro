"""
Celery worker configuration for background tasks
"""
import asyncio
import json
from datetime import datetime, timezone
from celery import Celery
from app.core.config import settings
from app.core.database import SessionLocal
from app.models.outbox import OutboxEvent
from app.services.outbox_service import mark_delivery_failed
from app.services.events.event_service import event_service

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


@celery_app.task(bind=True, name="app.worker.process_outbox_event")
def process_outbox_event(self, event_id: int):
    """Deliver a persisted event to the tenant event bus."""
    db = SessionLocal()
    try:
        event = db.query(OutboxEvent).filter(OutboxEvent.id == event_id).first()
        if not event:
            return {"status": "not_found", "event_id": event_id}
        if event.status != "pending":
            return {"status": event.status, "event_id": event_id}
        payload = json.loads(event.payload)
        company_id = payload.get("company_id")
        if company_id is None:
            mark_delivery_failed(db, event, "Event payload is missing company_id")
            db.commit()
            return {"status": "failed", "event_id": event_id}
        asyncio.run(event_service.emit_tenant_event(
            company_id=int(company_id),
            event_type=event.event_type,
            data=payload,
        ))
        event.status = "published"
        event.processed_at = datetime.now(timezone.utc)
        event.last_error = None
        db.add(event)
        db.commit()
        return {"status": "published", "event_id": event_id}
    except (ValueError, TypeError, json.JSONDecodeError) as exc:
        if 'event' in locals() and event:
            mark_delivery_failed(db, event, str(exc))
            db.commit()
        raise
    finally:
        db.close()
