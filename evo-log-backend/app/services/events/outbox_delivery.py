"""Livraison des evenements persistes en outbox vers le bus temps reel.

L'outbox transactionnel (``enqueue_event``) garantit qu'aucun evenement metier
n'est perdu si le bus Redis est indisponible. Ce module bascule ces evenements
vers ``event_service`` (WebSocket multi-processus via Redis, ou in-process en
mode degrade) :

- ``deliver_outbox_event`` : publie un evenement revendique, avec politique de
  reessai (``max_attempts``) avant passage en ``failed``.
- ``pump_outbox`` : rebondit tous les evenements ``pending`` (revendication
  atomique ``pending -> processing`` pour cohabiter avec le worker Celery).
"""
import json
import logging
from datetime import datetime, timezone
from typing import Optional

from sqlalchemy.orm import Session

from app.models.outbox import OutboxEvent
from app.services.events.event_service import event_service

logger = logging.getLogger(__name__)

MAX_ATTEMPTS = 5


async def deliver_outbox_event(db: Session, event: OutboxEvent) -> bool:
    """Publie un evenement sur le bus tenant puis le marque ``published``.

    En cas d'echec, l'evenement retourne en ``pending`` (rejoue par le pump)
    jusqu'a ``MAX_ATTEMPTS`` tentatives, puis passe en ``failed``.
    """
    try:
        payload = json.loads(event.payload)
        company_id = payload.get("company_id")
        if company_id is None:
            raise ValueError("Event payload is missing company_id")
        data = dict(payload)
        # cle interne : destinataires restreints (DM, salon prive), retiree
        # avant diffusion pour ne pas exposer la meta au wire format.
        target_users = data.pop("_target_users", None)
        await event_service.emit_tenant_event(
            company_id=int(company_id),
            event_type=event.event_type,
            data=data,
            target_users=target_users,
        )
    except Exception as exc:  # bus/Redis/JSON invalides : jamais bloquant
        logger.warning("Outbox delivery failed (event %s): %s", event.id, exc)
        event.attempts += 1
        event.last_error = str(exc)[:2000]
        if event.attempts >= MAX_ATTEMPTS:
            event.status = "failed"
            event.processed_at = datetime.now(timezone.utc)
        else:
            event.status = "pending"  # rejoue par le pump
        db.add(event)
        db.commit()
        return False
    event.status = "published"
    event.processed_at = datetime.now(timezone.utc)
    event.last_error = None
    db.add(event)
    db.commit()
    return True


def claim_pending_event(db: Session, event_id: int) -> Optional[OutboxEvent]:
    """Revendique atomiquement un evenement ``pending`` (``pending -> processing``).

    Retourne None si un autre processus (pump d'une autre instance ou worker
    Celery) a deja revendique l'evenement.
    """
    claimed = (
        db.query(OutboxEvent)
        .filter(OutboxEvent.id == event_id, OutboxEvent.status == "pending")
        .update({"status": "processing"}, synchronize_session=False)
    )
    db.commit()
    if not claimed:
        return None
    return db.query(OutboxEvent).filter(OutboxEvent.id == event_id).first()


async def pump_outbox(db: Session, limit: int = 50) -> int:
    """Livreur generique : publie les evenements pending les plus anciens.

    Appelle par la boucle d'evenements de l'application (main.lifespan).
    Retourne le nombre d'evenements publies avec succes.
    """
    pending_ids = [
        row.id
        for row in db.query(OutboxEvent.id)
        .filter(OutboxEvent.status == "pending")
        .order_by(OutboxEvent.id)
        .limit(limit)
        .all()
    ]
    delivered = 0
    for event_id in pending_ids:
        event = claim_pending_event(db, event_id)
        if event is None:
            continue  # deja revendique par un autre processus
        if await deliver_outbox_event(db, event):
            delivered += 1
    return delivered
