"""Tests pipeline : evaluation des releves de pression."""
import pytest
from fastapi import HTTPException

from app.models.pipeline_deep import PipelineSection, PipelinePressureReading
from app.services.pipeline_service import PipelineSafetyService


def _section(db, code="SEC-1", pmax=100):
    s = PipelineSection(company_id=1, code_section=code,
                        pression_max_bar=pmax, is_active=True)
    db.add(s)
    db.commit()
    db.refresh(s)
    return s


def _releve(db, section="SEC-1", pe=80, ps=75):
    r = PipelinePressureReading(company_id=1, reference=f"REL-{pe}-{ps}",
                                section_associee=section,
                                pression_entree_bar=pe,
                                pression_sortie_bar=ps, is_active=True)
    db.add(r)
    db.commit()
    db.refresh(r)
    return r


def test_releve_normal_aucune_alerte(db):
    _section(db)
    r = _releve(db, pe=80, ps=75)
    res = PipelineSafetyService.evaluer_releve(db, r.id)
    assert res["nb_alertes"] == 0


def test_surpression_detectee(db):
    """98 bar > 95 % de 100 = alerte majeure ; > 100 = critique."""
    _section(db)
    r = _releve(db, pe=98, ps=95)
    res = PipelineSafetyService.evaluer_releve(db, r.id)
    types = [a["type"] for a in res["alertes"]]
    assert "surpression" in types


def test_surpression_critique(db):
    _section(db)
    r = _releve(db, pe=105, ps=100)
    res = PipelineSafetyService.evaluer_releve(db, r.id)
    critique = [a for a in res["alertes"] if a.get("criticite") == "critique"]
    assert critique


def test_chute_charge_detectee(db):
    """Entree 90 -> sortie 70 : chute 20 bar > seuil 5 -> a_investiguer."""
    _section(db)
    r = _releve(db, pe=90, ps=70)
    res = PipelineSafetyService.evaluer_releve(db, r.id)
    types = [a["type"] for a in res["alertes"]]
    assert "chute_charge" in types


def test_section_sans_seuil_honnete(db):
    """Section sans pression_max : alerte config, pas de surpression inventee."""
    _section(db, code="SEC-NOSEUIL", pmax=None)
    r = _releve(db, section="SEC-NOSEUIL", pe=80, ps=75)
    res = PipelineSafetyService.evaluer_releve(db, r.id)
    assert any(a["type"] == "config" for a in res["alertes"])
    assert not any(a["type"] == "surpression" for a in res["alertes"])


def test_releve_inconnu_404(db):
    with pytest.raises(HTTPException):
        PipelineSafetyService.evaluer_releve(db, 999999)
