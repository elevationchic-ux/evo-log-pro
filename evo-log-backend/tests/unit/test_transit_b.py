"""Tests transit B : taux de conformite des inspections."""
import pytest

from app.models.transit_b_deep import TransitbInspectionRecord
from app.services.transit_b_service import TransitBService


def _insp(db, bureau="Douala", conformite=None, reference="INSP-1", agent=None):
    i = TransitbInspectionRecord(company_id=1, reference=reference,
                                 bureau=bureau, agent=agent,
                                 conformite=conformite,
                                 is_active=True)
    db.add(i)
    db.commit()
    db.refresh(i)
    return i


def test_taux_conformite(db):
    """3 conformes / 4 verdicts = 75 % (1 sans verdict exclu)."""
    _insp(db, conformite=True, reference="C1")
    _insp(db, conformite=True, reference="C2")
    _insp(db, conformite=True, reference="C3")
    _insp(db, conformite=False, reference="NC1")
    _insp(db, conformite=None, reference="NV1")

    r = TransitBService.taux_conformite(db, bureau="Douala")
    assert r["inspections_total"] == 5
    assert r["avec_verdict"] == 4
    assert r["sans_verdict"] == 1
    assert r["taux_conformite_pct"] == 75.0


def test_vide_honnete(db):
    r = TransitBService.taux_conformite(db, bureau="BureauVide")
    assert r["inspections_total"] == 0
    assert r["taux_conformite_pct"] is None


def test_filtre_agent(db):
    _insp(db, bureau="PNR", agent="Agent1", conformite=True, reference="A1")
    _insp(db, bureau="PNR", agent="Agent2", conformite=False, reference="A2")
    r = TransitBService.taux_conformite(db, agent="Agent1")
    assert r["taux_conformite_pct"] == 100.0
