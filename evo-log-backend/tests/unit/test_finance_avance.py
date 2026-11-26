"""Tests finance avancee : balance agee clients reelle."""
from datetime import date
from decimal import Decimal

from app.models.tiers import Client, TiersType
from app.models.finance_ohada import FactureNew
from app.services.finance_avance_service import GestionCreancesService


def _client(db, code="CLI-T1", nom="Client Test"):
    t = Client(code=code, type=TiersType.CLIENT, name=nom)
    db.add(t)
    db.commit()
    db.refresh(t)
    return t


def _facture_vente(db, client_id, numero, solde, statut="emise"):
    f = FactureNew(
        numero_facture=numero, client_id=client_id, type_facture="vente",
        date_emission=date(2026, 6, 1), montant_ht=Decimal("100000"),
        montant_tva=Decimal("19250"), montant_ttc=Decimal("119250"),
        solde_restant=Decimal(str(solde)), statut=statut)
    db.add(f)
    db.commit()
    return f


def test_balance_agee_vide_honnete(db):
    assert GestionCreancesService.balance_agee_clients(db, date.today()) == []


def test_balance_agee_somme_les_soldes_reels(db):
    """Un client avec 2 factures impayees : total_solde = somme reelle."""
    c = _client(db)
    _facture_vente(db, c.id, "FAC-001", 119250)
    _facture_vente(db, c.id, "FAC-002", 50000)

    bal = GestionCreancesService.balance_agee_clients(db, date.today())

    assert len(bal) == 1
    assert bal[0]["client_id"] == c.id
    assert float(bal[0]["total_solde"]) == 169250
    assert bal[0]["nombre_factures"] == 2


def test_balance_agee_ignore_les_solde_nuls(db):
    """Facture soldee (solde 0) ou statut hors suivi : pas de ligne."""
    c = _client(db, code="CLI-T2", nom="Client Solde")
    _facture_vente(db, c.id, "FAC-010", 0, statut="payee")

    bal = GestionCreancesService.balance_agee_clients(db, date.today())
    assert all(b["client_id"] != c.id for b in bal)
