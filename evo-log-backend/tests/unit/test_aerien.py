"""Tests fret aerien : calcul AWB selon grille tarifaire."""
from datetime import date, timedelta
import pytest
from fastapi import HTTPException

from app.services.aerien_service import AirFreightService, AirTariff


def _tarif(db, code="TAF-DLA-1", prix=900, surcharges=15000, poids_min=45):
    from app.models.aerien_deep import AirTariff as _AT
    t = _AT(company_id=1, code_tarif=code, prix_par_kg_xaf=prix,
                 surcharges_xaf=surcharges, poids_min_kg=poids_min,
                 validite_debut=date.today() - timedelta(days=30),
                 validite_fin=date.today() + timedelta(days=365),
                 is_active=True)
    db.add(t)
    db.commit()
    db.refresh(t)
    return t


def test_fret_avec_surcharges(db):
    """100 kg x 900 + 15 000 surcharges = 105 000 XAF."""
    _tarif(db)
    r = AirFreightService.calculer_fret(db, "TAF-DLA-1", poids_kg=100)
    assert r["base_xaf"] == 90_000
    assert r["surcharges_xaf"] == 15_000
    assert r["fret_total_xaf"] == 105_000


def test_tranche_poids_minimale(db):
    """20 kg < poids_min 45 kg -> 422 honnete."""
    _tarif(db)
    with pytest.raises(HTTPException) as exc:
        AirFreightService.calculer_fret(db, "TAF-DLA-1", poids_kg=20)
    assert "tranche" in exc.value.detail


def test_tarif_inconnu_refuse(db):
    with pytest.raises(HTTPException) as exc:
        AirFreightService.calculer_fret(db, "INCONNU", poids_kg=100)
    assert exc.value.status_code == 404


def test_tarif_expire_refuse(db):
    t = _tarif(db, code="TAF-OLD")
    t.validite_fin = date.today() - timedelta(days=1)
    db.commit()
    with pytest.raises(HTTPException) as exc:
        AirFreightService.calculer_fret(db, "TAF-OLD", poids_kg=100)
    assert "expire" in exc.value.detail.lower()


def test_poids_invalide_refuse(db):
    _tarif(db)
    with pytest.raises(HTTPException):
        AirFreightService.calculer_fret(db, "TAF-DLA-1", poids_kg=0)
