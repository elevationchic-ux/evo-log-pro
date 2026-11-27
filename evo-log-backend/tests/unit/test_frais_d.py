"""Tests frais D : rapports, avances, TVA."""
from datetime import date
import pytest
from decimal import Decimal

from app.models.frais_d_deep import FraExpenseReport, FraExpenseAdvance, FraVatRecovery
from app.services.frais_d_service import FraisDService


def _rep(db, reference, collaborateur, total, statut="soumis", periode="2026-03"):
    r = FraExpenseReport(company_id=1, reference=reference,
                         collaborateur=collaborateur, periode=periode,
                         total=Decimal(str(total)), nb_justificatifs=3,
                         statut=statut, is_active=True)
    db.add(r)
    db.commit()
    db.refresh(r)
    return r


def _av(db, reference, collaborateur, montant, statut="en_attente"):
    a = FraExpenseAdvance(company_id=1, reference=reference,
                          collaborateur=collaborateur,
                          montant=Decimal(str(montant)), motif="Mission",
                          statut=statut, is_active=True)
    db.add(a)
    db.commit()
    db.refresh(a)
    return a


def _vat(db, reference, frais, ht, tva, statut="en_attente"):
    v = FraVatRecovery(company_id=1, reference=reference, frais=frais,
                       montant_ht=Decimal(str(ht)), tva=Decimal(str(tva)),
                       statut=statut, is_active=True)
    db.add(v)
    db.commit()
    db.refresh(v)
    return v


def test_rapports(db):
    """2 rapports CHF-1 : 100k soumis + 200k valide."""
    _rep(db, "FR-1", "CHF-1", 100_000, "soumis")
    _rep(db, "FR-2", "CHF-1", 200_000, "valide")
    _rep(db, "FR-3", "CHF-2", 50_000, "soumis")
    r = FraisDService.rapports(db, collaborateur="CHF-1")
    assert r["rapports_total"] == 2
    assert r["en_attente"] == 1
    assert r["total_frais_xaf"] == 300_000


def test_avances(db):
    _av(db, "AV-1", "CHF-1", 500_000, "en_attente")
    _av(db, "AV-2", "CHF-2", 200_000, "solde")
    r = FraisDService.avances(db)
    assert r["avances_total"] == 2
    assert r["a_regulariser"] == 1
    assert r["details"][0]["montant"] == 500_000


def test_tva_recuperable(db):
    """2 en attente (HT 800k + 400k, TVA 152k + 76k)."""
    _vat(db, "VAT-1", "frais_deplacement", 800_000, 152_000)
    _vat(db, "VAT-2", "frais_representation", 400_000, 76_000)
    _vat(db, "VAT-3", "frais_deplacement", 100_000, 19_000, statut="recuperee")
    r = FraisDService.tva_recuperable(db)
    assert r["recoveries_total"] == 3
    assert r["en_attente"] == 2
    assert r["montant_ht_attente_xaf"] == 1_200_000
    assert r["tva_attente_xaf"] == 228_000


def test_vide_honnete(db):
    r = FraisDService.rapports(db)
    assert r["rapports"] == 0
