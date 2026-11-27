"""Tests fret fluvial : calcul LCV bateliere selon grille tarifaire."""
from datetime import date, timedelta
import pytest
from fastapi import HTTPException

from app.models.fluvial_deep import FluvialTariff, FluvialWaybill
from app.services.fluvial_service import FluvialFreightService


def _tarif(db, code="TF-CONGO-1", prix=80000, remise=5, produit="bois"):
    t = FluvialTariff(company_id=1, code_tarif=code, prix_par_tonne_xaf=prix,
                      remise_volume_pct=remise, produit=produit,
                      validite_debut=date.today() - timedelta(days=30),
                      validite_fin=date.today() + timedelta(days=365),
                      is_active=True)
    db.add(t)
    db.commit()
    db.refresh(t)
    return t


def _waybill(db, tonnes=50, produit="bois", numero="LCV-1"):
    w = FluvialWaybill(company_id=1, numero=numero, produit=produit,
                       quantite_tonnes=tonnes)
    db.add(w)
    db.commit()
    db.refresh(w)
    return w


def test_fret_avec_remise(db):
    """50 t x 80 000 = 4 000 000, remise 5 % -> 3 800 000."""
    _tarif(db)
    w = _waybill(db)
    r = FluvialFreightService.calculer_fret(db, w.id, "TF-CONGO-1")
    assert r["base_xaf"] == 4_000_000
    assert r["fret_xaf"] == 3_800_000


def test_produit_incompatible_refuse(db):
    """Tarif 'bois' sur LCV 'cereales' -> 422."""
    _tarif(db)
    w = _waybill(db, produit="cereales", numero="LCV-2")
    with pytest.raises(HTTPException) as exc:
        FluvialFreightService.calculer_fret(db, w.id, "TF-CONGO-1")
    assert "incompatible" in exc.value.detail


def test_waybill_sans_tonnage_refuse(db):
    _tarif(db)
    w = _waybill(db, tonnes=None, numero="LCV-3")
    with pytest.raises(HTTPException) as exc:
        FluvialFreightService.calculer_fret(db, w.id, "TF-CONGO-1")
    assert exc.value.status_code == 422


def test_tarif_inconnu_refuse(db):
    w = _waybill(db, numero="LCV-4")
    with pytest.raises(HTTPException) as exc:
        FluvialFreightService.calculer_fret(db, w.id, "INCONNU")
    assert exc.value.status_code == 404
