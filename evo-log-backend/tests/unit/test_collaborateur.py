"""Tests collaborateur : conformite qualite."""
import pytest

from app.models.collaborateur_d_deep import CollQualityCheck
from app.services.collaborateur_service import CollaborateurService


def _qc(db, collab, points, anomalies, reference):
    c = CollQualityCheck(company_id=1, reference=reference,
                         collaborateur=collab, controle="controle qualite",
                         point_testes=points, anomalies=anomalies,
                         is_active=True)
    db.add(c)
    db.commit()
    db.refresh(c)
    return c


def test_conformite_par_collaborateur(db):
    """3 controles : 2 sans anomalie, 1 avec -> 66,7 %."""
    _qc(db, "COLL-1", 10, 0, "QC1")
    _qc(db, "COLL-1", 10, 0, "QC2")
    _qc(db, "COLL-1", 10, 2, "QC3")
    r = CollaborateurService.conformite(db, "COLL-1")
    assert r["controles_total"] == 3
    assert r["anomalies"] == 2
    assert r["taux_conformite_pct"] == 66.7


def test_global_tous_collaborateurs(db):
    _qc(db, "COLL-A", 5, 0, "QA")
    _qc(db, "COLL-B", 5, 1, "QB")
    r = CollaborateurService.conformite(db)
    assert r["controles_total"] == 2
    assert r["taux_conformite_pct"] == 50.0


def test_vide_honnete(db):
    r = CollaborateurService.conformite(db, "COLL-INCONNU")
    assert r["controles"] == 0
