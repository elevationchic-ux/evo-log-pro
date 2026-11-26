"""Tests heavylift : validation de plans de levage vs capacite grue."""
import pytest
from fastapi import HTTPException

from app.models.heavylift_deep import HeavyLiftCrane, HeavyLiftLiftPlan
from app.services.heavylift_service import HeavyLiftPlanService


def _grue(db, numero="GRUE-01", capacite=100, hauteur=50):
    g = HeavyLiftCrane(company_id=1, numero_grue=numero,
                       capacite_max_t=capacite, hauteur_max_m=hauteur,
                       is_active=True)
    db.add(g)
    db.commit()
    db.refresh(g)
    return g


def _plan(db, charge=50, grue_prevue="GRUE-01", **kw):
    p = HeavyLiftLiftPlan(company_id=1, reference=f"PL-{charge}-{kw.get('hauteur_m', 0)}",
                          charge_t=charge, grue_prevue=grue_prevue,
                          statut="brouillon", is_active=True, **kw)
    db.add(p)
    db.commit()
    db.refresh(p)
    return p


def test_plan_valide_sous_capacite(db):
    _grue(db)
    p = _plan(db, charge=50)
    r = HeavyLiftPlanService.valider_plan(db, p.id)
    assert r["statut"] == "valide"
    assert p.statut == "valide"


def test_surcharge_refusee(db):
    """Charge 120 t > capacite 100 t : refuse, jamais approuve."""
    _grue(db)
    p = _plan(db, charge=120)
    r = HeavyLiftPlanService.valider_plan(db, p.id)
    assert r["statut"] == "refuse"
    assert any("capacite" in m for m in r["motifs_refus"])


def test_charge_elevée_a_verifier(db):
    """90 t sur 100 t (>80 %) : a_verifier."""
    _grue(db)
    p = _plan(db, charge=90)
    r = HeavyLiftPlanService.valider_plan(db, p.id)
    assert r["statut"] == "a_verifier"


def test_centre_gravite_haut_sans_coeff_refuse(db):
    _grue(db)
    p = _plan(db, charge=40, centre_gravite_haut=True)
    r = HeavyLiftPlanService.valider_plan(db, p.id)
    assert r["statut"] == "refuse"
    assert any("coefficient" in m for m in r["motifs_refus"])


def test_hauteur_superieure_refusee(db):
    _grue(db, hauteur=40)
    p = _plan(db, charge=40, hauteur_m=60)
    r = HeavyLiftPlanService.valider_plan(db, p.id)
    assert r["statut"] == "refuse"


def test_grue_inconnue_avertit_honnetement(db):
    p = _plan(db, charge=40, grue_prevue="GRUE-INCONNUE")
    r = HeavyLiftPlanService.valider_plan(db, p.id)
    assert any("non identifiee" in a for a in r["avertissements"])
    assert r["capacite_grue_t"] is None


def test_plan_inconnu_404(db):
    with pytest.raises(HTTPException):
        HeavyLiftPlanService.valider_plan(db, 999999)
