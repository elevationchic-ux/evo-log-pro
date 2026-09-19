"""Repository and delivery primitives for the transactional outbox."""

from datetime import datetime, timedelta, timezone
from typing import Awaitable, Callable, List

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.outbox import OutboxEvent
from app.schemas.events import EventEnvelope


def enqueue(session: Session, event: EventEnvelope) -> OutboxEvent:
    """Stage an event in the caller's transaction; the caller owns commit/rollback."""

    existing = session.scalar(
        select(OutboxEvent).where(
            OutboxEvent.company_id == event.company_id,
            OutboxEvent.event_type == event.event_type,
            OutboxEvent.aggregate_type == event.aggregate_type,
            OutboxEvent.aggregate_id == event.aggregate_id,
            OutboxEvent.dedupe_key == event.dedupe_key,
        )
    )
    if existing:
        return existing

    now = datetime.now(timezone.utc)
    record = OutboxEvent(
        event_id=str(event.event_id),
        company_id=event.company_id,
        event_type=event.event_type,
        aggregate_type=event.aggregate_type,
        aggregate_id=event.aggregate_id,
        payload=event.payload,
        occurred_at=event.occurred_at,
        dedupe_key=event.dedupe_key,
        available_at=now,
        created_at=now,
    )
    session.add(record)
    return record


def claim_pending(session: Session, limit: int = 100) -> List[OutboxEvent]:
    """Claim a bounded batch. PostgreSQL workers use row locks; SQLite remains testable."""

    if limit < 1:
        raise ValueError("limit must be positive")
    now = datetime.now(timezone.utc)
    query = (
        select(OutboxEvent)
        .where(
            OutboxEvent.status == "pending",
            OutboxEvent.available_at <= now,
        )
        .order_by(OutboxEvent.created_at)
        .limit(limit)
    )
    if session.bind is not None and session.bind.dialect.name != "sqlite":
        query = query.with_for_update(skip_locked=True)
    records = list(session.scalars(query))
    for record in records:
        record.status = "processing"
        record.attempts += 1
        record.locked_at = now
    session.flush()
    return records


def mark_published(session: Session, record: OutboxEvent) -> None:
    record.status = "published"
    record.processed_at = datetime.now(timezone.utc)
    record.locked_at = None
    record.last_error = None


def mark_failed(
    session: Session,
    record: OutboxEvent,
    error: Exception,
    retry_delay: timedelta = timedelta(minutes=1),
) -> None:
    """Return an event to pending with an explicit retry time and error."""

    record.status = "pending"
    record.available_at = datetime.now(timezone.utc) + retry_delay
    record.locked_at = None
    record.last_error = str(error)[:4000]


def requeue_stale(
    session: Session,
    stale_after: timedelta = timedelta(minutes=10),
) -> int:
    """Recover claims left processing after a worker crash."""

    cutoff = datetime.now(timezone.utc) - stale_after
    records = list(
        session.scalars(
            select(OutboxEvent).where(
                OutboxEvent.status == "processing",
                OutboxEvent.locked_at < cutoff,
            )
        )
    )
    for record in records:
        record.status = "pending"
        record.available_at = datetime.now(timezone.utc)
        record.locked_at = None
        record.last_error = "worker claim expired; event requeued"
    session.flush()
    return len(records)


async def deliver_batch(
    session: Session,
    publish: Callable[[EventEnvelope], Awaitable[None]],
    limit: int = 100,
) -> int:
    """Deliver claimed events and persist each result; exceptions are never hidden."""

    records = claim_pending(session, limit)
    delivered = 0
    for record in records:
        occurred_at = record.occurred_at
        if occurred_at.tzinfo is None:
            occurred_at = occurred_at.replace(tzinfo=timezone.utc)
        envelope = EventEnvelope(
            event_id=record.event_id,
            event_type=record.event_type,
            company_id=record.company_id,
            aggregate_type=record.aggregate_type,
            aggregate_id=record.aggregate_id,
            payload=record.payload,
            occurred_at=occurred_at,
            dedupe_key=record.dedupe_key,
        )
        try:
            await publish(envelope)
        except Exception as error:
            mark_failed(session, record, error)
        else:
            mark_published(session, record)
            delivered += 1
    session.commit()
    return delivered
