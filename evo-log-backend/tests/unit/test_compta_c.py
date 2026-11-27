"""Tests compta C : rapprochements et contre-passations."""
import pytest
from decimal import Decimal

from app.models.compta_c_deep import CmptcBankReconciliation, CmptcJournalReversal
from app.services.compta_c_service import ComptaCService


def _rap(db, compte, solde_c, solde_b, ecart, statut="ouvert", reference="R1"):
    r = CmptcBankReconciliation(company_id=1, reference=reference,
                                compte_banque=compte,
                                solde_comptable=Decimal(str(solde_c)),
                                solde_bancaire=Decimal(str(solde_b)),
                                ecart=Decimal(str(ecart)), statut=statut,
                                is_active=True)
    db.add(r)
    db.commit()
    db.refresh(r)
    return r


def _rev(db, reference, montant, statut="en_attente"):
    r = CmptcJournalReversal(company_id=1, reference=reference,
                             ecriture_origine="ECR-100", montant=Decimal(str(montant)),
                             statut=statut, is_active=True)
    db.add(r)
    db.commit()
    db.refresh(r)
    return r


def test_rapprochements(db):
    """1 avec ecart non rapproche, 1 sans ecart valide."""
    _rap(db, "CIE-1", 1_000_000, 995_000, 5_000, "ouvert", "R1")
    _rap(db, "CIE-2", 500_000, 500_000, 0, "valide", "R2")
    r = ComptaCService.rapprochements(db)
    assert r["rapprochements_total"] == 2
    assert r["avec_ecart"] == 1
    assert r["non_rapproches"] == 1


def test_contre_passations(db):
    """2 en attente (100k + 50k), 1 validee."""
    _rev(db, "REV-1", 100_000)
    _rev(db, "REV-2", 50_000)
    _rev(db, "REV-3", 200_000, statut="valide")
    r = ComptaCService.contre_passations(db)
    assert r["reversals_total"] == 3
    assert r["en_attente"] == 2
    assert r["montant_total_en_attente_xaf"] == 150_000


def test_vide_honnete(db):
    r = ComptaCService.rapprochements(db)
    assert r["rapprochements"] == 0
