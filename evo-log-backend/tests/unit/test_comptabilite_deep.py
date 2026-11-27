"""Tests comptabilite deep : rapprochements et budgets."""
import pytest
from decimal import Decimal

from app.models.comptabilite_deep import BankReconciliation, BudgetControl, BankReconciliation_statut
from app.services.comptabilite_deep_service import ComptabiliteDeepService


def _rap(db, reference, solde_b, solde_c, ecart, statut):
    r = BankReconciliation(company_id=1, reference=reference, compte_banque="CIE-001",
                           solde_banque_xaf=Decimal(str(solde_b)),
                           solde_compta_xaf=Decimal(str(solde_c)),
                           ecart_xaf=Decimal(str(ecart)), statut=statut,
                           is_active=True)
    db.add(r)
    db.commit()
    db.refresh(r)
    return r


def _budget(db, reference, prevu, consomme, centre="CC-LOG"):
    b = BudgetControl(company_id=1, reference=reference, centre_cout=centre,
                      exercice=2026, budget_prevu_xaf=Decimal(str(prevu)),
                      consomme_xaf=Decimal(str(consomme)), is_active=True)
    db.add(b)
    db.commit()
    db.refresh(b)
    return b


def test_rapprochements_ecarts(db):
    """1 rap avec ecart ouvert, 1 sans ecart cloture."""
    _rap(db, "RAP-1", 1_000_000, 990_000, 10_000, BankReconciliation_statut.OUVERT)
    _rap(db, "RAP-2", 500_000, 500_000, 0, BankReconciliation_statut.VALIDE)
    r = ComptabiliteDeepService.rapprochements(db)
    assert r["rapprochements_total"] == 2
    assert r["avec_ecart"] == 1
    assert r["details_ecarts"][0]["ecart_xaf"] == 10_000


def test_controle_budgetaire_depassement(db):
    """2 budgets : 1 dans les clous, 1 depasse de 50k."""
    _budget(db, "BUD-1", 1_000_000, 800_000, "CC-A")
    _budget(db, "BUD-2", 500_000, 550_000, "CC-B")
    r = ComptabiliteDeepService.controle_budgetaire(db)
    assert r["budgets_total"] == 2
    assert r["budget_prevu_xaf"] == 1_500_000
    assert r["consomme_xaf"] == 1_350_000
    assert r["depassements"] == 1
    assert r["details_depassements"][0]["depassement_xaf"] == 50_000


def test_vide_honnete(db):
    r = ComptabiliteDeepService.rapprochements(db)
    assert r["rapprochements"] == 0
