"""Tests finance deep : previsions tresorerie et alertes."""
from datetime import date
import pytest
from decimal import Decimal

from app.models.finance_deep import CashForecast, TreasuryAlert, TreasuryAlert_statut, TreasuryAlert_type_alerte
from app.services.finance_deep_service import FinanceDeepService


def _prev(db, reference, horizon, entrees, sorties, projete=None):
    p = CashForecast(company_id=1, reference=reference, horizon_mois=horizon,
                     entree_attendue_xaf=Decimal(str(entrees)),
                     sortie_attendue_xaf=Decimal(str(sorties)),
                     tresorerie_projete_xaf=Decimal(str(projete)) if projete is not None else None,
                     is_active=True)
    db.add(p)
    db.commit()
    db.refresh(p)
    return p


def _alerte(db, statut, reference="AL-1"):
    a = TreasuryAlert(company_id=1, reference=reference,
                      type_alerte=TreasuryAlert_type_alerte.SEUIL_BANCAIRE,
                      statut=statut, is_active=True)
    db.add(a)
    db.commit()
    db.refresh(a)
    return a


def test_previsions_solde_et_risque(db):
    """M1 : +500k/-200k projete +300k ; M2 : +100k/-400k projete -300k."""
    _prev(db, "CF-1", 1, 500_000, 200_000, projete=300_000)
    _prev(db, "CF-2", 2, 100_000, 400_000, projete=-300_000)
    r = FinanceDeepService.previsions(db)
    assert r["previsions_total"] == 2
    assert r["solde_net_xaf"] == 0  # 600k - 600k
    assert r["risques_decouvert"] == 1
    assert r["details_risques"][0]["reference"] == "CF-2"


def test_alertes_ouvertes(db):
    _alerte(db, TreasuryAlert_statut.OUVERTE, "AL-1")
    _alerte(db, TreasuryAlert_statut.CLOTUREE if hasattr(TreasuryAlert_statut, "CLOTUREE") else TreasuryAlert_statut.OUVERTE, "AL-2")
    r = FinanceDeepService.alertes_ouvertes(db)
    assert r["alertes_total"] >= 1


def test_vide_honnete(db):
    r = FinanceDeepService.previsions(db)
    assert r["previsions"] == 0
