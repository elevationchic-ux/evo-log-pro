"""Tests RH deep : performance, discipline, departs."""
from datetime import date
import pytest
from decimal import Decimal

from app.models.rh_deep import PerformanceReview, DisciplinaryCase, EmployeeExit
from app.services.rh_deep_service import RhDeepService


def _rev(db, employe, note, objectifs, periode="2026-T1", reference="R1"):
    r = PerformanceReview(company_id=1, reference=reference, employe_id=employe,
                          periode=periode, note_global=Decimal(str(note)),
                          objectifs_atteints_pct=Decimal(str(objectifs)),
                          is_active=True)
    db.add(r)
    db.commit()
    db.refresh(r)
    return r


def _case(db, reference, sanction, statut="ouverte"):
    c = DisciplinaryCase(company_id=1, reference=reference, employe_id=1,
                         type_sanction=sanction, statut=statut, is_active=True)
    db.add(c)
    db.commit()
    db.refresh(c)
    return c


def _exit(db, reference, type_depart, ttc, statut="ouvert"):
    e = EmployeeExit(company_id=1, reference=reference, employe_id=1,
                     type_depart=type_depart, solde_tout_compte_xaf=Decimal(str(ttc)),
                     statut=statut, is_active=True)
    db.add(e)
    db.commit()
    db.refresh(e)
    return e


def test_performance_moyenne(db):
    """2 evals : notes 14+16=15, objectifs 80+100=90 %."""
    _rev(db, 1, 14, 80, "2026-T1", "R1")
    _rev(db, 2, 16, 100, "2026-T1", "R2")
    r = RhDeepService.performance(db, periode="2026-T1")
    assert r["evaluations_total"] == 2
    assert r["note_moyenne"] == 15.0
    assert r["objectifs_moyen_pct"] == 90.0


def test_discipline(db):
    _case(db, "DC-1", "avertissement")
    _case(db, "DC-2", "revoication", statut="cloture")
    r = RhDeepService.discipline(db)
    assert r["cas_total"] == 2
    assert r["ouvertes"] == 1


def test_departs_soldes(db):
    """2 departs : demission 500k + retraite 800k = 1,3M."""
    _exit(db, "EX-1", "demision", 500_000)
    _exit(db, "EX-2", "retraite", 800_000)
    r = RhDeepService.departs(db)
    assert r["departs_total"] == 2
    assert r["soldes_ttc_total_xaf"] == 1_300_000


def test_vide_honnete(db):
    r = RhDeepService.performance(db)
    assert r["evaluations"] == 0
