"""Tests parc automobile : consommation et pneus."""
from decimal import Decimal
import pytest

from app.models.parc_deep import FuelConsumption, TyreRecord
from app.services.parc_service import ParcService


def _plein(db, vehicule, litres, km, conso=None, reference="P-1"):
    p = FuelConsumption(company_id=1, reference=reference, vehicule_id=vehicule,
                        litres=Decimal(str(litres)), km_etape=Decimal(str(km)),
                        conso_l100km=Decimal(str(conso)) if conso else None,
                        is_active=True)
    db.add(p)
    db.commit()
    db.refresh(p)
    return p


def _pneu(db, numero, profondeur, reference):
    p = TyreRecord(company_id=1, numero_gomme=numero,
                   profondeur_couronne_mm=Decimal(str(profondeur)),
                   is_active=True)
    db.add(p)
    db.commit()
    db.refresh(p)
    return p


def test_conso_recalculee(db):
    """40 L / 500 km = 8 L/100km (conso non saisie -> recalculee)."""
    _plein(db, vehicule=1, litres=40, km=500)
    r = ParcService.consommation_reelle(db, vehicule_id=1)
    assert r["conso_moyenne_l100km"] == 8.0


def test_conso_saisie_et_calculee(db):
    """1 plein conso saisie 9, 1 recalculee 8 -> moyenne 8,5."""
    _plein(db, vehicule=2, litres=45, km=500, conso=9, reference="P2")
    _plein(db, vehicule=2, litres=40, km=500, reference="P3")
    r = ParcService.consommation_reelle(db, vehicule_id=2)
    assert r["conso_moyenne_l100km"] == 8.5


def test_pneus_sous_seuil(db):
    """1 pneu a 1,2 mm (< 1,6) -> a_remplacer."""
    _pneu(db, "GOMME-1", 1.2, "T1")
    _pneu(db, "GOMME-2", 4.5, "T2")
    r = ParcService.pneus_a_remplacer(db)
    assert r["a_remplacer"] == 1
    assert r["details"][0]["numero_gomme"] == "GOMME-1"


def test_parc_vide_honnete(db):
    r = ParcService.consommation_reelle(db, vehicule_id=999)
    assert r["pleins"] == 0
