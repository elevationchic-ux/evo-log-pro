"""Tests admin billing : factures en retard et encours."""
from datetime import date, timedelta
import pytest
from decimal import Decimal

from app.models.admin_c_deep import AdmCBillingInvoice
from app.services.admin_billing_service import AdminBillingService


def _facture(db, tenant, montant, statut, echeance=None, reference="F-1"):
    f = AdmCBillingInvoice(company_id=1, reference=reference, tenant=tenant,
                           periode_facturee="2026-03", montant_ht=Decimal(str(montant)),
                           tva=Decimal("0"), montant_ttc=Decimal(str(montant)),
                           date_echeance=echeance, statut=statut, is_active=True)
    db.add(f)
    db.commit()
    db.refresh(f)
    return f


def test_factures_impayees_et_retard(db):
    """1 payee, 1 impayee en retard, 1 impayee a jour."""
    _facture(db, "T-A", 100_000, "payee", date.today() - timedelta(days=5), "F1")
    _facture(db, "T-A", 200_000, "impayee", date.today() - timedelta(days=5), "F2")
    _facture(db, "T-B", 150_000, "impayee", date.today() + timedelta(days=10), "F3")
    r = AdminBillingService.factures(db)
    assert r["factures_total"] == 3
    assert r["payees"] == 1
    assert r["impayees"] == 2
    assert r["en_retard_echeance"] == 1
    assert r["encours_par_tenant"]["T-A"] == 200_000
    assert r["encours_par_tenant"]["T-B"] == 150_000


def test_vide_honnete(db):
    r = AdminBillingService.factures(db)
    assert r["factures"] == 0
