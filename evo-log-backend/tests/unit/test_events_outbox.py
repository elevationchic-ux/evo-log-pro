import asyncio
from datetime import datetime, timedelta, timezone

import pytest
from sqlalchemy import create_engine, select
from sqlalchemy.orm import sessionmaker

from app.core.database import Base
from app.models.outbox import OutboxEvent
from app.schemas.events import EventEnvelope
from app.services.events.outbox import (
    claim_pending,
    deliver_batch,
    enqueue,
    requeue_stale,
)


@pytest.fixture
def session():
    engine = create_engine("sqlite:///:memory:")
    Base.metadata.create_all(engine, tables=[OutboxEvent.__table__])
    with sessionmaker(bind=engine)() as db:
        yield db


def event(dedupe_key="shipment-1"):
    return EventEnvelope(
        event_type="shipment.created",
        company_id=7,
        aggregate_type="shipment",
        aggregate_id="1",
        payload={"status": "created"},
        dedupe_key=dedupe_key,
    )


def test_enqueue_is_transactional_and_idempotent(session):
    first = enqueue(session, event())
    second = enqueue(session, event())
    session.commit()

    assert first.id == second.id
    assert len(session.scalars(select(OutboxEvent)).all()) == 1


def test_delivery_publishes_and_records_failure(session):
    enqueue(session, event("ok"))
    enqueue(session, event("failure"))
    session.commit()

    published = []

    async def publish(envelope):
        if envelope.dedupe_key == "failure":
            raise RuntimeError("broker unavailable")
        published.append(envelope.event_id)

    assert asyncio.run(deliver_batch(session, publish)) == 1
    rows = session.scalars(select(OutboxEvent).order_by(OutboxEvent.dedupe_key)).all()
    assert rows[0].status == "pending"
    assert rows[0].last_error == "broker unavailable"
    assert rows[1].status == "published"
    assert len(published) == 1


def test_claim_is_bounded(session):
    for index in range(3):
        enqueue(session, event(str(index)))
    session.commit()
    assert len(claim_pending(session, limit=2)) == 2
    assert session.query(OutboxEvent).filter_by(status="processing").count() == 2


def test_stale_claims_are_requeued(session):
    record = enqueue(session, event("stale"))
    session.commit()
    claim_pending(session)
    record.locked_at = datetime.now(timezone.utc) - timedelta(hours=1)
    session.commit()

    assert requeue_stale(session, timedelta(minutes=5)) == 1
    assert record.status == "pending"
