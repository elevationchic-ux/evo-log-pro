"""Tests transport B : tournees et PODs."""
from datetime import datetime, timezone
import pytest

from app.models.transport_b_deep import TransportbDispatch, TransportbPod
from app.services.transport_b_service import TransportBService


def _t(db, reference, chauffeur, km, statut="terminee",
       depart=None, arrivee=None):
    t = TransportbDispatch(company_id=1, reference=reference, chauffeur=chauffeur,
                           vehicule="IM-1", point_depart="A", point_arrivee="B",
                           km_parcourus=km, statut=statut,
                           date_depart=depart, date_arrivee=arrivee, is_active=True)
    db.add(t)
    db.commit()
    db.refresh(t)
    return t


def _pod(db, reference, colis, signe, incidents=None):
    p = TransportbPod(company_id=1, reference=reference, mission="M-1",
                      destinataire="Dest", nb_colis_livres=colis,
                      incidents=incidents, signature_recu=signe, is_active=True)
    db.add(p)
    db.commit()
    db.refresh(p)
    return p


def test_tournees(db):
    """2 tournees chauffeur CHF-1 : 100+150 km, 1 completee."""
    _t(db, "T-1", "CHF-1", 100, depart=datetime.now(timezone.utc),
       arrivee=datetime.now(timezone.utc))
    _t(db, "T-2", "CHF-1", 150, statut="en_cours")
    _t(db, "T-3", "CHF-2", 200)
    r = TransportBService.tournees(db, chauffeur="CHF-1")
    assert r["tournees_total"] == 2
    assert r["km_total"] == 250
    assert r["avec_dates_completes"] == 1
    assert r["par_statut"]["en_cours"] == 1


def test_pods(db):
    _pod(db, "P-1", 10, signe=True)
    _pod(db, "P-2", 5, signe=False, incidents="retard")
    r = TransportBService.pods(db)
    assert r["pods_total"] == 2
    assert r["signes"] == 1
    assert r["avec_incidents"] == 1
    assert r["colis_livres_total"] == 15


def test_vide_honnete(db):
    r = TransportBService.tournees(db)
    assert r["tournees"] == 0
