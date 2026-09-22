"""Transactional outbox enqueueing and explicit delivery failure handling."""
import json
from datetime import datetime, timezone

from sqlalchemy.orm import Session

from app.models.outbox import OutboxEvent


def enqueue_event(
    db: Session,
    *,
    event_type: str,
    aggregate_type: str,
    aggregate_id: str,
    payload: dict,
) -> OutboxEvent:
    event = OutboxEvent(
        event_type=event_type,
        aggregate_type=aggregate_type,
        aggregate_id=aggregate_id,
        payload=json.dumps(payload, separators=(",", ":")),
        status="pending",
    )
    db.add(event)
    db.flush()
    return event


def mark_delivery_failed(db: Session, event: OutboxEvent, error: str) -> None:
    event.status = "failed"
    event.attempts += 1
    event.last_error = error[:2000]
    event.processed_at = datetime.now(timezone.utc)
    db.add(event)
