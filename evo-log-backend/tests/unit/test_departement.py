"""Tests departements : demandes de service internes."""
import pytest

from app.models.departement_d5_deep import DepServiceRequest
from app.services.departement_service import DepartementService


def _dem(db, service, urgence, statut, reference):
    d = DepServiceRequest(company_id=1, reference=reference, objet="Demande",
                          service_destinataire=service, urgence=urgence,
                          statut=statut, is_active=True)
    db.add(d)
    db.commit()
    db.refresh(d)
    return d


def test_demandes_par_service(db):
    """2 sur IT (1 urgente ouverte), 1 sur RH resolue."""
    _dem(db, "IT", "urgente", "en_cours", "D1")
    _dem(db, "IT", "normale", "resolue", "D2")
    _dem(db, "RH", "basse", "resolue", "D3")
    r = DepartementService.demandes(db, service="IT")
    assert r["demandes_total"] == 2
    assert r["par_urgence"]["urgente"] == 1
    assert r["ouvertes"] == 1


def test_vide_honnete(db):
    r = DepartementService.demandes(db, service="ServiceVide")
    assert r["demandes"] == 0
