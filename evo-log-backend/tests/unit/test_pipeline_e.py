"""Tests pipeline avance : corrosion et releves pompe."""
from datetime import date
import pytest

from app.models.pipeline_e_deep import Pipe2CorrosionReading, Pipe2PumpStationRead
from app.services.pipeline_e_service import PipelineEService


def _corr(db, troncon, epaisseur, reference):
    r = Pipe2CorrosionReading(company_id=1, reference=reference, troncon=troncon,
                              epaisseur_mm=epaisseur, date=date.today(), is_active=True)
    db.add(r)
    db.commit()
    db.refresh(r)
    return r


def _pompe(db, station, debit, vibration, reference):
    r = Pipe2PumpStationRead(company_id=1, reference=reference, station=station,
                             debit=debit, vibration=vibration, is_active=True)
    db.add(r)
    db.commit()
    db.refresh(r)
    return r


def test_corrosion_sous_seuil(db):
    """3 releves : 8, 7.5, 6 mm ; seuil 7 -> 1 sous seuil."""
    _corr(db, "TR-1", 8, "C1")
    _corr(db, "TR-1", 7.5, "C2")
    _corr(db, "TR-1", 6, "C3")
    r = PipelineEService.analyse_corrosion(db, "TR-1", seuil_min_mm=7.0)
    assert r["epaisseur_min_mm"] == 6.0
    assert r["releves_sous_seuil"] == 1
    assert r["alerte"] is True


def test_corrosion_vide_honnete(db):
    r = PipelineEService.analyse_corrosion(db, "TR-INEXISTANT", seuil_min_mm=7.0)
    assert r["releves"] == 0


def test_pompe_stats(db):
    _pompe(db, "P-1", 120, 4.5, "P1")
    _pompe(db, "P-1", 140, 5.2, "P2")
    r = PipelineEService.analyse_pompe(db, "P-1")
    assert r["debit_moyen"] == 130.0
    assert r["vibration_max"] == 5.2
