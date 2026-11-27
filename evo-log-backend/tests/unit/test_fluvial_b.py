"""Tests fluvial B : navigabilite et convoi."""
from datetime import datetime, timezone
import pytest

from app.models.fluvial_b_deep import FluvialWaterGauge, FluvialConvoy
from app.services.fluvial_b_service import FluvialBService


def _jauge(db, poste, cote, seuil, bief="Congo", reference="J1"):
    j = FluvialWaterGauge(company_id=1, code_poste=poste, nom_poste=poste,
                          bief=bief, cote_cm=cote, cote_seuil_restr_cm=seuil,
                          is_active=True)
    db.add(j)
    db.commit()
    db.refresh(j)
    return j


def _convoi(db, numero, masse, longueur, reference="CV-1"):
    c = FluvialConvoy(company_id=1, numero_convoi=numero, pousseur="Pousseur-A",
                      nb_peniches=4, masse_total_t=masse, longueur_total_m=longueur,
                      is_active=True)
    db.add(c)
    db.commit()
    db.refresh(c)
    return c


def test_navigabilite_restrictions(db):
    """1 poste restreint (cote <= seuil), 1 libre."""
    _jauge(db, "POSTE-A", cote=50, seuil=100, reference="J1")
    _jauge(db, "POSTE-B", cote=200, seuil=100, reference="J2")
    r = FluvialBService.navigabilite(db)
    assert r["jauges_total"] == 2
    assert r["postes_restreints"] == 1
    assert r["postes_libres"] == 1
    assert r["details_restrictions"][0]["poste"] == "POSTE-A"


def test_convoi_dans_limites(db):
    """1500 t / 200 m vs limites 2000 t / 220 m -> conforme."""
    _convoi(db, "CV-1", 1500, 200)
    r = FluvialBService.verifier_convoi(db, "CV-1", masse_max_t=2000, longueur_max_m=220)
    assert r["masse_conforme"] is True
    assert r["longueur_conforme"] is True
    assert r["marge_masse_t"] == 500


def test_convoi_depasse_limite(db):
    """2500 t > 2000 t -> non conforme."""
    _convoi(db, "CV-2", 2500, 200, reference="CV-2")
    r = FluvialBService.verifier_convoi(db, "CV-2", masse_max_t=2000)
    assert r["masse_conforme"] is False


def test_convoi_sans_limites_honnete(db):
    """Sans limites : mesures rapportees, note honnete."""
    _convoi(db, "CV-3", 1000, 100, reference="CV-3")
    r = FluvialBService.verifier_convoi(db, "CV-3")
    assert "mesures rapportees" in r["note"]
