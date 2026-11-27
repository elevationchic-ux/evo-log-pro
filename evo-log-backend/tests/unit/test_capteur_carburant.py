"""Tests capteurs carburant : niveau cuve et alertes."""
import pytest

from app.models.new_k_modules import FuelTankSensor
from app.services.capteur_carburant_service import CapteurCarburantService


def _cap(db, immat, niveau, capacite=400, vol=False):
    c = FuelTankSensor(immatriculation_camion=immat,
                       niveau_actuel_litres=niveau,
                       capacite_totale_litres=capacite,
                       alerte_vol_detectee=vol)
    db.add(c)
    db.commit()
    db.refresh(c)
    return c


def test_cuve_en_alerte(db):
    """50 L / 400 = 12,5 % < 20 % -> alerte."""
    _cap(db, "CM-001", 50)
    r = CapteurCarburantService.statut_cuve(db, "CM-001")
    assert r["niveau_pct"] == 12.5
    assert r["en_alerte"] is True


def test_cuve_ok(db):
    """300 L / 400 = 75 % -> pas d'alerte."""
    _cap(db, "CM-002", 300)
    r = CapteurCarburantService.statut_cuve(db, "CM-002")
    assert r["en_alerte"] is False
    assert r["niveau_pct"] == 75.0


def test_jours_avant_epuisement(db):
    """80 L / 20 L/j = 4 jours."""
    _cap(db, "CM-003", 80)
    r = CapteurCarburantService.statut_cuve(db, "CM-003", conso_l_jour=20)
    assert r["jours_avant_epuisement"] == 4.0


def test_cuve_absente_honnete(db):
    r = CapteurCarburantService.statut_cuve(db, "CM-INCONNU")
    assert r["capteur"] is False


def test_alertes_vol(db):
    _cap(db, "CM-004", 100, vol=True)
    _cap(db, "CM-005", 100)
    r = CapteurCarburantService.cuves_en_alerte(db)
    assert "CM-004" in r["alertes_vol"]
