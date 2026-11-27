"""Tests 3PL B : fret transporteur base + prix/kg."""
from datetime import date, timedelta
import pytest
from fastapi import HTTPException

from app.models.log3pl_b_deep import TplCarrierRate
from app.services.log3pl_b_service import TplCarrierService


def _tarif(db, code="TR-A", base=50000, par_kg=800):
    t = TplCarrierRate(company_id=1, code_tarif=code, transporteur="TransCam",
                       zone="DLA-BZV", prix_base_xaf=base, prix_par_kg_xaf=par_kg,
                       validite_debut=date.today() - timedelta(days=30),
                       validite_fin=date.today() + timedelta(days=365),
                       is_active=True)
    db.add(t)
    db.commit()
    db.refresh(t)
    return t


def test_fret_base_plus_kilo(db):
    """50 000 + 200 kg x 800 = 210 000."""
    _tarif(db)
    r = TplCarrierService.calculer_fret(db, "TR-A", poids_kg=200)
    assert r["fret_total_xaf"] == 210_000
    assert r["prix_base_xaf"] == 50_000


def test_tarif_sans_prix_refuse(db):
    t = TplCarrierRate(company_id=1, code_tarif="TR-VIDE",
                       validite_debut=date.today() - timedelta(days=1), is_active=True)
    db.add(t)
    db.commit()
    with pytest.raises(HTTPException) as exc:
        TplCarrierService.calculer_fret(db, "TR-VIDE", poids_kg=100)
    assert exc.value.status_code == 422


def test_tarif_inconnu_404(db):
    with pytest.raises(HTTPException):
        TplCarrierService.calculer_fret(db, "INCONNU", poids_kg=100)


def test_poids_invalide_refuse(db):
    _tarif(db)
    with pytest.raises(HTTPException):
        TplCarrierService.calculer_fret(db, "TR-A", poids_kg=0)
