"""Tests gap bridge : calcul prix + TVA."""
import pytest
from decimal import Decimal
from fastapi import HTTPException

from app.models.gap_bridge import Tarif
from app.services.gap_bridge_service import TarifService


def _tarif(db, code="TAR-1", prix=10000, tva=19.25):
    t = Tarif(company_id=1, code=code, designation="Prestation", categorie="LOG",
              unite="UNITE", prix=Decimal(str(prix)), tva=Decimal(str(tva)),
              is_active=True)
    db.add(t)
    db.commit()
    db.refresh(t)
    return t


def test_prix_avec_tva(db):
    """10 x 10 000 = 100 000 HT, TVA 19,25 % = 19 250, TTC 119 250."""
    _tarif(db)
    r = TarifService.calculer_prix(db, "TAR-1", quantite=10)
    assert r["base_ht"] == 100_000
    assert r["tva"] == 19_250
    assert r["total_ttc"] == 119_250


def test_tarif_inconnu_404(db):
    with pytest.raises(HTTPException):
        TarifService.calculer_prix(db, "INCONNU", quantite=1)


def test_quantite_invalide_refuse(db):
    _tarif(db)
    with pytest.raises(HTTPException):
        TarifService.calculer_prix(db, "TAR-1", quantite=0)
