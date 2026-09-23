"""Tests du relais outbox -> bus temps reel (cablage du chat)."""
import asyncio
import json

import pytest

from app.models.outbox import OutboxEvent
from app.services.events import outbox_delivery
from app.services.outbox_service import enqueue_event


@pytest.fixture
def recorded_events(monkeypatch):
    """Capture les emissions au lieu de toucher Redis/WebSocket."""
    calls = []

    async def fake_emit(self, company_id, event_type, data, target_departments=None, target_users=None):
        calls.append({
            "company_id": company_id,
            "event_type": event_type,
            "data": data,
            "target_users": target_users,
        })

    monkeypatch.setattr(
        outbox_delivery.event_service.__class__, "emit_tenant_event", fake_emit
    )
    return calls


def _make_chat_event(db, company_id=7, message_id=42):
    return enqueue_event(
        db,
        event_type="chat.message.created",
        aggregate_type="chat_message",
        aggregate_id=str(message_id),
        payload={
            "company_id": company_id,
            "message_id": message_id,
            "sender_id": 3,
            "recipient_id": 9,
            "_target_users": [3, 9],
        },
    )


def test_pump_delivers_pending_chat_event(db, recorded_events):
    event = _make_chat_event(db)
    db.commit()

    delivered = asyncio.run(outbox_delivery.pump_outbox(db))

    assert delivered == 1
    assert len(recorded_events) == 1
    call = recorded_events[0]
    assert call["company_id"] == 7
    assert call["event_type"] == "chat.message.created"
    # la cle interne _target_users est retiree du wire format, mais bien appliquee
    assert "_target_users" not in call["data"]
    assert call["target_users"] == [3, 9]
    db.refresh(event)
    assert event.status == "published"


def test_pump_is_idempotent_across_claimers(db, recorded_events):
    event = _make_chat_event(db)
    db.commit()

    # Premier claimant gagne ; le second ne doit rien publier.
    claimed = outbox_delivery.claim_pending_event(db, event.id)
    assert claimed is not None
    assert outbox_delivery.claim_pending_event(db, event.id) is None
    asyncio.run(outbox_delivery.deliver_outbox_event(db, claimed))

    assert asyncio.run(outbox_delivery.pump_outbox(db)) == 0
    assert len(recorded_events) == 1


def test_failed_event_returns_to_pending_for_retry(db, recorded_events, monkeypatch):
    async def broken_emit(self, *args, **kwargs):
        raise RuntimeError("redis down")

    monkeypatch.setattr(
        outbox_delivery.event_service.__class__, "emit_tenant_event", broken_emit
    )
    event = _make_chat_event(db)
    db.commit()

    assert asyncio.run(outbox_delivery.pump_outbox(db)) == 0
    db.refresh(event)
    # statut remis a pending (reessai) jusqu'a MAX_ATTEMPTS, avec attempts incrementes
    assert event.status == "pending"
    assert event.attempts == 1
    assert "redis down" in event.last_error


def test_event_without_company_id_is_not_published(db, recorded_events):
    event = OutboxEvent(
        event_type="chat.message.created",
        aggregate_type="chat_message",
        aggregate_id="1",
        payload=json.dumps({"message_id": 1}),
        status="pending",
    )
    db.add(event)
    db.commit()

    asyncio.run(outbox_delivery.pump_outbox(db))

    assert recorded_events == []
    db.refresh(event)
    assert event.status == "pending"
    assert event.attempts == 1
