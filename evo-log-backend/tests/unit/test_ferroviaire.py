"""Tests ferroviaire : calcul de fret LCV selon grille tarifaire."""
from datetime import date, timedelta
import pytest
from decimal import Decimal
from fastapi import HTTPException

from app.models.ferroviaire_deep import RailTariff
from app.services.ferroviaire_service import RailFreightService


def _tarif(db, code="TARIF-A", prix=50, remise=10):
    t = RailTariff(company_id=1, code_tarif=code, prix_par_tonne_km_xaf=prix,
                   remise_volume_pct=remise, is_active=True,
                   date_debut_validite=date.today() - timedelta(days=30),
                   date_fin_validite=date.today() + timedelta(days=365))
    db.add(t)
    db.commit()
    db.refresh(t)
    return t


def test_fret_avec_remise_volume(db):
    """100 t x 200 km x 50 XAF = 1 000 000, remise 10 % -> 900 000."""
    _tarif(db)
    r = RailFreightService.calculer_fret(db, "TARIF-A", tonnes=100, distance_km=200)
    assert r["base_xaf"] == 1_000_000
    assert r["fret_xaf"] == 900_000
    assert r["remise_volume_pct"] == 10.0


def test_tarif_inconnu_refuse(db):
    with pytest.raises(HTTPException) as exc:
        RailFreightService.calculer_fret(db, "INCONNU", tonnes=10, distance_km=50)
    assert exc.value.status_code == 404


def test_tarif_expire_refuse(db):
    t = _tarif(db, code="TARIF-OLD")
    t.date_fin_validite = date.today() - timedelta(days=1)
    db.commit()
    with pytest.raises(HTTPException) as exc:
        RailFreightService.calculer_fret(db, "TARIF-OLD", tonnes=10, distance_km=50)
    assert "expire" in exc.value.detail.lower()


def test_parametres_invalides_refuses(db):
    _tarif(db)
    with pytest.raises(HTTPException):
        RailFreightService.calculer_fret(db, "TARIF-A", tonnes=0, distance_km=100)
    with pytest.raises(HTTPException):
        RailFreightService.calculer_fret(db, "TARIF-A", tonnes=10, distance_km=-5)
