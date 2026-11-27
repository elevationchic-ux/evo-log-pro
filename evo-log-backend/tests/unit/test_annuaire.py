"""Tests annuaire : performance, documents expires, incidents."""
from datetime import date, timedelta
import pytest

from app.models.annuaire_d_deep import (
    ProvEvaluation, ProvCertification, ProvInsuranceAttestation, ProvIncident)
from app.services.annuaire_service import AnnuaireService


def _eval(db, prestataire, score, reference):
    e = ProvEvaluation(company_id=1, reference=reference, prestataire=prestataire,
                       periode="2026-T1", score=score, is_active=True)
    db.add(e)
    db.commit()
    db.refresh(e)
    return e


def _cert(db, prestataire, expire, reference):
    c = ProvCertification(company_id=1, reference=reference, prestataire=prestataire,
                          intitule="ISO", expire_le=expire, is_active=True)
    db.add(c)
    db.commit()
    db.refresh(c)
    return c


def _ass(db, prestataire, expire, reference):
    a = ProvInsuranceAttestation(company_id=1, reference=reference,
                                 prestataire=prestataire, type_assurance="RC",
                                 expire_le=expire, is_active=True)
    db.add(a)
    db.commit()
    db.refresh(a)
    return a


def _inc(db, prestataire, statut, reference):
    i = ProvIncident(company_id=1, reference=reference, prestataire=prestataire,
                     statut=statut, is_active=True)
    db.add(i)
    db.commit()
    db.refresh(i)
    return i


def test_performance(db):
    """2 evals prestataire A (80, 90), 1 prestataire B (70)."""
    _eval(db, "PROV-A", 80, "E1")
    _eval(db, "PROV-A", 90, "E2")
    _eval(db, "PROV-B", 70, "E3")
    r = AnnuaireService.performance(db)
    assert r["prestataires_evalues"] == 2
    assert r["par_prestataire"]["PROV-A"] == 85.0
    assert r["score_moyen_global"] == 77.5


def test_documents_expires(db):
    """1 cert expiree, 1 assurance expiree -> 1 prestataire a risque."""
    _cert(db, "PROV-A", date.today() - timedelta(days=10), "C1")
    _cert(db, "PROV-B", date.today() + timedelta(days=90), "C2")
    _ass(db, "PROV-C", date.today() - timedelta(days=5), "A1")
    r = AnnuaireService.documents_expires(db)
    assert r["certifications_expirees"] == 1
    assert r["assurances_expirees"] == 1
    assert "PROV-A" in r["prestataires_a_risque"]
    assert "PROV-C" in r["prestataires_a_risque"]


def test_incidents_ouverts(db):
    _inc(db, "PROV-A", "ouvert", "I1")
    _inc(db, "PROV-A", "clos", "I2")
    _inc(db, "PROV-B", "en_cours", "I3")
    r = AnnuaireService.incidents_ouverts(db)
    assert r["incidents_total"] == 3
    assert r["ouverts"] == 2
    assert r["par_prestataire"]["PROV-A"] == 1


def test_vide_honnete(db):
    r = AnnuaireService.performance(db)
    assert r["evaluations"] == 0
