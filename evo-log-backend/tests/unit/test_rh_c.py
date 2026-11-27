"""Tests RH C : formation et discipline."""
from datetime import date, timedelta
import pytest

from app.models.rh_c_deep import RhCTrainingPlan, RhCDisciplinaryRecord
from app.services.rh_c_service import RhCService


def _plan(db, reference, intitule, fin, rea, statut="en_cours"):
    p = RhCTrainingPlan(company_id=1, reference=reference, intitule=intitule,
                        categorie="securite", collaborateur="Coll-1",
                        heures_financees=fin, heures_realisees=rea,
                        statut=statut, is_active=True)
    db.add(p)
    db.commit()
    db.refresh(p)
    return p


def _san(db, reference, type_s, fin_effet=None, statut="actif"):
    s = RhCDisciplinaryRecord(company_id=1, reference=reference,
                              collaborateur="Coll-2", type_sanction=type_s,
                              motif="Motif", date_effet=date.today(),
                              date_fin_effet=fin_effet, decideur="RH",
                              statut=statut, is_active=True)
    db.add(s)
    db.commit()
    db.refresh(s)
    return s


def test_formation(db):
    """1 complet (20/20), 1 incomplet (10/20)."""
    _plan(db, "TP-1", "CACES", 20, 20, "termine")
    _plan(db, "TP-2", "Secourisme", 20, 10, "en_cours")
    r = RhCService.formation(db)
    assert r["plans_total"] == 2
    assert r["heures_financees"] == 40
    assert r["heures_realisees"] == 30
    assert r["taux_realisation_pct"] == 75.0
    assert len(r["incomplets"]) == 1


def test_discipline(db):
    """1 sanction active (fin dans 30j), 1 expiree."""
    _san(db, "S-1", "avertissement", fin_effet=date.today() + timedelta(days=30))
    _san(db, "S-2", "blame", fin_effet=date.today() - timedelta(days=10))
    _san(db, "S-3", "mise_a_pied", fin_effet=None, statut="annulee")
    r = RhCService.discipline(db)
    assert r["sanctions_total"] == 3
    assert r["actives"] == 1
    assert r["details_actives"][0]["reference"] == "S-1"


def test_vide_honnete(db):
    r = RhCService.formation(db)
    assert r["plans"] == 0
