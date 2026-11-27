"""Tests coldchain avance : ouvertures de porte et bilan chambre."""
import pytest
from fastapi import HTTPException

from app.models.coldchain_e_deep import Cold2DoorOpenEvent
from app.services.coldchain_e_service import Cold2DoorService


def _event(db, chambre="CH-1", duree=120, reference="OPD-1"):
    e = Cold2DoorOpenEvent(company_id=1, reference=reference, chambre=chambre,
                           duree_sec=duree, is_active=True)
    db.add(e)
    db.commit()
    db.refresh(e)
    return e


def test_ouverture_normale(db):
    e = _event(db, duree=120)
    r = Cold2DoorService.evaluer_ouverture(db, e.id)
    assert r["alerte"] is False
    assert r["criticite"] == "normale"


def test_ouverture_depasse_seuil(db):
    """1000 s > 900 s (3x seuil) -> alerte majeure."""
    e = _event(db, duree=1000, reference="OPD-2")
    r = Cold2DoorService.evaluer_ouverture(db, e.id)
    assert r["alerte"] is True
    assert r["criticite"] == "majeure"


def test_seuil_personnalise(db):
    e = _event(db, duree=60, reference="OPD-3")
    r = Cold2DoorService.evaluer_ouverture(db, e.id, seuil_sec=30)
    assert r["alerte"] is True


def test_bilan_chambre(db):
    """3 ouvertures, 1 au-dela du seuil -> taux 33,3 %."""
    _event(db, chambre="CH-B", duree=100, reference="B1")
    _event(db, chambre="CH-B", duree=1000, reference="B2")
    _event(db, chambre="CH-B", duree=200, reference="B3")
    r = Cold2DoorService.bilan_chambre(db, "CH-B")
    assert r["ouvertures_total"] == 3
    assert r["depassements_seuil"] == 1
    assert r["taux_depassement_pct"] == 33.3


def test_bilan_chambre_vide_honnete(db):
    r = Cold2DoorService.bilan_chambre(db, "CH-INEXISTANTE")
    assert r["ouvertures"] == 0
    assert "Aucun evenement" in r["note"]


def test_event_inconnu_404(db):
    with pytest.raises(HTTPException):
        Cold2DoorService.evaluer_ouverture(db, 999999)
