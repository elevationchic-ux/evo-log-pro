"""Tests aerien B : charge utile vol affrete vs capacite."""
import pytest
from fastapi import HTTPException

from app.models.aerien_b_deep import (
    CharteredFlight, PerishableCargo, LiveAnimalShipment,)
from app.services.aerien_b_service import AirBService


def _charter(db, numero="MAWB-1", capacite=10):
    c = CharteredFlight(company_id=1, numero_affretement=numero,
                        capacite_tonnes=capacite, is_active=True)
    db.add(c)
    db.commit()
    db.refresh(c)
    return c


def _perissable(db, mawb, poids, reference="PER-1"):
    p = PerishableCargo(company_id=1, reference=reference, numero_mawb=mawb,
                        poids_kg=poids, is_active=True)
    db.add(p)
    db.commit()
    db.refresh(p)
    return p


def test_charge_dans_capacite(db):
    """6 000 kg / 10 t = 60 % -> conforme."""
    _charter(db)
    _perissable(db, "MAWB-1", 4000, "PER-A")
    _perissable(db, "MAWB-1", 2000, "PER-B")
    r = AirBService.charge_vol_affrete(db, "MAWB-1")
    assert r["poids_charge_kg"] == 6000
    assert r["taux_charge_pct"] == 60.0
    assert r["conforme"] is True


def test_charge_depasse_capacite(db):
    """12 000 kg > 10 t -> non conforme."""
    _charter(db, numero="MAWB-2", capacite=10)
    _perissable(db, "MAWB-2", 12000, "PER-C")
    r = AirBService.charge_vol_affrete(db, "MAWB-2")
    assert r["conforme"] is False


def test_mawb_sans_affretement_honnete(db):
    """Cargo sans charter -> capacite non verifiable, note honnete."""
    _perissable(db, "MAWB-SOLO", 5000, "PER-D")
    r = AirBService.charge_vol_affrete(db, "MAWB-SOLO")
    assert r["affretement"] is None
    assert "capacite non verifiable" in r["note"]


def test_mawb_vide(db):
    r = AirBService.charge_vol_affrete(db, "MAWB-VIDE")
    assert r["poids_charge_kg"] == 0
    assert r["nb_lignes_perissables"] == 0
