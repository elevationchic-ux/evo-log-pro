"""Tests cycle conteneur : durees par phase et enregistrement sortie."""
from datetime import datetime, timedelta
import pytest
from fastapi import HTTPException

from app.models.conteneur_cycle import (
    ConteneurCycle, CycleConteneur, TypeConteneur, StatutConteneur,)
from app.services.conteneur_cycle_service import ConteneurCycleService


def _cycle(db, **kw):
    c = ConteneurCycle(company_id=1, numero="MSKU1234567",
                       type_conteneur=TypeConteneur.DRY_40,
                       taille_pieds=40)
    db.add(c)
    db.commit()
    db.refresh(c)
    cyc = CycleConteneur(company_id=1, conteneur_id=c.id,
                         voyage="V123", statut=StatutConteneur.QUAI, **kw)
    db.add(cyc)
    db.commit()
    db.refresh(cyc)
    return cyc


def test_analyse_phases_completes(db):
    """Navire -> dechargement 6 h, -> quai 4 h, -> sortie 10 h = 20 h."""
    t0 = datetime(2026, 1, 1, 6, 0)
    cyc = _cycle(
        db,
        date_arrivee_navire=t0,
        date_dechargement=t0 + timedelta(hours=6),
        date_mise_quai=t0 + timedelta(hours=10),
        date_sortie=t0 + timedelta(hours=20),
    )
    r = ConteneurCycleService.analyser_cycle(db, cyc.id)
    assert r["phases_h"]["arrivee_navire_a_dechargement_h"] == 6.0
    assert r["phases_h"]["quai_a_sortie_h"] == 10.0
    assert r["temps_total_cycle_h"] == 20.0


def test_analyse_honnete_dates_manquantes(db):
    """Sans dates : phases None, jamais de duree inventee."""
    cyc = _cycle(db)
    r = ConteneurCycleService.analyser_cycle(db, cyc.id)
    assert all(v is None for v in r["phases_h"].values())
    assert r["temps_total_cycle_h"] is None


def test_marquer_sortie_calcule_temps_cycle(db):
    t0 = datetime(2026, 1, 1, 0, 0)
    cyc = _cycle(db, date_arrivee_navire=t0)
    sortie = t0 + timedelta(hours=30)
    r = ConteneurCycleService.marquer_sortie(db, cyc.id, sortie)
    assert r["temps_cycle_heures"] == 30.0


def test_double_sortie_refusee(db):
    cyc = _cycle(db, date_sortie=datetime(2026, 1, 5))
    with pytest.raises(HTTPException) as exc:
        ConteneurCycleService.marquer_sortie(db, cyc.id, datetime(2026, 1, 6))
    assert exc.value.status_code == 409


def test_cycle_inconnu_404(db):
    with pytest.raises(HTTPException):
        ConteneurCycleService.analyser_cycle(db, 999999)
