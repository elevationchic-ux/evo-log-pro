"""Tests magasinier C : precision des comptages cycliques."""
import pytest

from app.models.magasinier_c_deep import MagcCycleCount
from app.services.magasinier_c_service import MagasinierCService


def _cc(db, emplacement, theorique, physique, reference):
    c = MagcCycleCount(company_id=1, reference=reference, emplacement=emplacement,
                       theorique=theorique, physique=physique, is_active=True)
    db.add(c)
    db.commit()
    db.refresh(c)
    return c


def test_precision_emplacement(db):
    """3 comptees : 2 exactes, 1 ecart ; 1 sans comptage."""
    _cc(db, "A-01", 100, 100, "CC1")
    _cc(db, "A-01", 50, 50, "CC2")
    _cc(db, "A-01", 80, 75, "CC3")
    _cc(db, "A-01", 30, None, "CC4")
    r = MagasinierCService.precision_emplacement(db, "A-01")
    assert r["lignes_total"] == 4
    assert r["lignes_comptees"] == 3
    assert r["sans_comptage"] == 1
    assert r["ecarts"] == 1
    assert r["taux_precision_pct"] == 66.7
    assert r["details_ecarts"][0]["ecart"] == -5


def test_emplacement_vide_honnete(db):
    r = MagasinierCService.precision_emplacement(db, "Z-99")
    assert r["lignes"] == 0
