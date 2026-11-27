"""Tests parc B : affectations et inspections."""
from datetime import date, timedelta
import pytest

from app.models.parc_b_deep import ParcDriverAssignment, ParcInspectionChecklist
from app.services.parc_b_service import ParcBService


def _aff(db, chauffeur, immat, debut, fin, reference):
    a = ParcDriverAssignment(company_id=1, reference=reference,
                             chauffeur=chauffeur, immatriculation=immat,
                             date_debut=debut, date_fin=fin, is_active=True)
    db.add(a)
    db.commit()
    db.refresh(a)
    return a


def _insp(db, reference, anomalies, immat="IM-1"):
    i = ParcInspectionChecklist(company_id=1, reference=reference,
                                immatriculation=immat, anomalies_nb=anomalies,
                                is_active=True)
    db.add(i)
    db.commit()
    db.refresh(i)
    return i


def test_affectations_actives(db):
    """1 active (fin dans 10j), 1 terminee (fin -5j)."""
    _aff(db, "CHF-1", "IM-1", date.today() - timedelta(days=10),
         date.today() + timedelta(days=10), "A1")
    _aff(db, "CHF-1", "IM-2", date.today() - timedelta(days=20),
         date.today() - timedelta(days=5), "A2")
    r = ParcBService.affectations_actives(db, chauffeur="CHF-1")
    assert r["affectations_total"] == 2
    assert r["actives"] == 1
    assert r["terminees"] == 1


def test_inspections_anomalies(db):
    """3 inspections : 1 avec anomalies."""
    _insp(db, "I1", 0)
    _insp(db, "I2", 2, "IM-2")
    _insp(db, "I3", 0)
    r = ParcBService.inspections(db)
    assert r["inspections_total"] == 3
    assert r["avec_anomalies"] == 1
    assert r["details"][0]["reference"] == "I2"


def test_vide_honnete(db):
    r = ParcBService.affectations_actives(db, chauffeur="CHF-INCONNU")
    assert r["affectations"] == 0
