"""Tests support client : tickets et documents expirants."""
from datetime import datetime, timedelta, timezone
import pytest

from app.models.customer_support import SupportTicket, FleetDocument
from app.services.support_service import SupportService


def _ticket(db, statut, priorite="normale", reference="T1",
            resolved=None, created=None):
    t = SupportTicket(company_id=1, reference=reference, sujet="Problème",
                      statut=statut, priorite=priorite, is_active=True,
                      resolved_at=resolved, created_at=created or datetime.now(timezone.utc))
    db.add(t)
    db.commit()
    db.refresh(t)
    return t


def test_stats_tickets(db):
    """2 ouverts (1 haute), 1 resolu en 4h -> delai moyen 4h."""
    t0 = datetime.now(timezone.utc) - timedelta(hours=4)
    _ticket(db, "ouvert", "haute", "T1")
    _ticket(db, "ouvert", "normale", "T2")
    _ticket(db, "resolu", "normale", "T3",
            resolved=datetime.now(timezone.utc), created=t0)
    r = SupportService.stats_tickets(db)
    assert r["tickets_total"] == 3
    assert r["par_statut"]["ouvert"] == 2
    assert r["par_priorite"]["haute"] == 1
    assert r["delai_moyen_resolution_h"] == 4.0


def test_documents_expirants(db):
    """1 doc expire dans 10j, 1 dans 60j -> 1 expirant."""
    d1 = FleetDocument(company_id=1, vehicule_id=1, type_document="assurance",
                       nom_fichier="a.pdf", url="/a",
                       date_expiration=datetime.now(timezone.utc) + timedelta(days=10),
                       statut="valide")
    d2 = FleetDocument(company_id=1, vehicule_id=1, type_document="visite",
                       nom_fichier="v.pdf", url="/v",
                       date_expiration=datetime.now(timezone.utc) + timedelta(days=60),
                       statut="valide")
    db.add_all([d1, d2])
    db.commit()
    r = SupportService.documents_expirants(db)
    assert r["expirants_30j"] == 1


def test_vide_honnete(db):
    r = SupportService.stats_tickets(db)
    assert r["tickets"] == 0
