"""Tests rentabilite : CA par client et type."""
import pytest
from datetime import date
from decimal import Decimal

from app.models.finance_ohada import FactureNew
from app.services.rentabilite_service import RentabiliteService


def _fac(db, numero, client_id, type_facture, ht, ttc, statut="emise",
         solde=None):
    f = FactureNew(numero_facture=numero, client_id=client_id,
                   conteneur_id=None, escale_id=None,
                   type_facture=type_facture, date_emission=date.today(),
                   montant_ht=Decimal(str(ht)), taux_tva=Decimal("19.25"),
                   montant_tva=Decimal("0"), montant_ttc=Decimal(str(ttc)),
                   statut=statut, solde_restant=Decimal(str(solde)) if solde else None)
    db.add(f)
    db.commit()
    db.refresh(f)
    return f


def test_ca_par_client(db):
    """Client 1 : 2 factures (100k HT + 200k HT) ; client 2 : 1."""
    _fac(db, "F-1", 1, "vente", 100_000, 119_250, "payee")
    _fac(db, "F-2", 1, "prestation", 200_000, 238_500, "emise", solde=238_500)
    _fac(db, "F-3", 2, "vente", 50_000, 59_625, "emise")
    _fac(db, "F-4", 1, "avoir", 10_000, 11_925, "annulee")
    r = RentabiliteService.par_client(db)
    assert r["factures_total"] == 3  # annulee exclue
    assert r["ca_ht_xaf"] == 350_000
    assert r["ca_ttc_xaf"] == 417_375
    assert r["par_client"][1]["nb"] == 2
    assert r["par_client"][2]["ht"] == 50_000
    assert r["par_type"]["prestation"] == 238_500


def test_filtre_client(db):
    _fac(db, "F-5", 1, "vente", 100_000, 119_250, "payee")
    _fac(db, "F-6", 2, "vente", 300_000, 358_750, "payee")
    r = RentabiliteService.par_client(db, client_id=2)
    assert r["factures_total"] == 1
    assert r["ca_ttc_xaf"] == 358_750


def test_vide_honnete(db):
    r = RentabiliteService.par_client(db)
    assert r["factures"] == 0
