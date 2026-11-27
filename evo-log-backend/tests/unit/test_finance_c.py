"""Tests finance C : previsions et affacturage."""
from datetime import date, timedelta
import pytest
from decimal import Decimal

from app.models.finance_c_deep import FincCashFlowForecast, FincInvoiceFinancing
from app.services.finance_c_service import FinanceCService


def _prev(db, reference, entrees, sorties, position=None, periode="2026-03"):
    p = FincCashFlowForecast(company_id=1, reference=reference, periode=periode,
                            solde_debut=Decimal("0"),
                            entrees_prevues=Decimal(str(entrees)),
                            sorties_prevues=Decimal(str(sorties)),
                            position_finale=Decimal(str(position)) if position is not None else None,
                            is_active=True)
    db.add(p)
    db.commit()
    db.refresh(p)
    return p


def _fin(db, reference, facture, montant, pct, echeance, statut="en_cours"):
    f = FincInvoiceFinancing(company_id=1, reference=reference,
                             affacteur="Factor-X", facture=facture,
                             montant_facture=Decimal(str(montant)),
                             avance_pct=pct, date_echeance=echeance,
                             statut=statut, is_active=True)
    db.add(f)
    db.commit()
    db.refresh(f)
    return f


def test_previsions(db):
    """M1 : +500k/-300k pos +200k ; M2 : +100k/-400k pos -300k."""
    _prev(db, "CF-1", 500_000, 300_000, position=200_000)
    _prev(db, "CF-2", 100_000, 400_000, position=-300_000)
    r = FinanceCService.previsions(db)
    assert r["previsions_total"] == 2
    assert r["solde_net_previsionnel_xaf"] == -100_000  # 600k entrees - 700k sorties
    assert r["risques_decouvert"] == 1


def test_affacturage(db):
    """1 en cours avance 80% de 100k = 80k, echeance passee."""
    _fin(db, "AF-1", "FAC-100", 100_000, 80,
         date.today() - timedelta(days=5), "en_cours")
    _fin(db, "AF-2", "FAC-200", 200_000, 90,
         date.today() + timedelta(days=30), "solde")
    r = FinanceCService.affacturage(db)
    assert r["financements_total"] == 2
    assert r["en_cours"] == 1
    assert r["avances_en_cours_xaf"] == 80_000
    assert r["echus_non_rembourses"] == 1


def test_vide_honnete(db):
    r = FinanceCService.previsions(db)
    assert r["previsions"] == 0
