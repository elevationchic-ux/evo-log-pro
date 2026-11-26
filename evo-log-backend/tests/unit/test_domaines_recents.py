"""Tests des derniers services livres : valorisation/FEFO, ecriture
d'ecarts d'inventaire, recapitulatif annuel de paie."""
from datetime import date, timedelta
from decimal import Decimal

import pytest

from app.models.finance_ohada import (
    PlanComptableOHADA, JournalAuxiliaire, ExerciceComptable,
    GrandLivreLigne, TypeCompte, TypeJournal,)
from app.models.magasin import Stock
from app.models.magasin_avance import InventaireTournant, LigneInventaire, Peremption
from app.models.rh import Salaire
from app.models.user import User
from app.services.stock_valuation_service import StockValuationService
from app.services.inventaire_ecriture_service import InventaireEcritureService
from app.services.rh_avance_service import PaieOHADAService


# --------------------------------------------------------------------------- #
# Valorisation + FEFO
# --------------------------------------------------------------------------- #
@pytest.fixture
def stock(db):
    s = Stock(company_id=None, code_article="ART-001", designation="Huile moteur 15W40",
              quantite_disponible=100, quantite_reservee=0, prix_unitaire=Decimal("8500"),
              is_active=True)
    db.add(s)
    db.flush()
    return s


def test_valorisation_stock_reelle(db, stock):
    v = StockValuationService.valoriser_stock(db, stock.id)
    assert v["quantite"] == 100
    assert v["valorisation"] == 850_000


def test_allocation_fefo_trie_par_peremption(db, stock):
    for i, (lot, qte, date_p) in enumerate([
            ("LOT-B", 40, date(2027, 6, 1)), ("LOT-A", 60, date(2026, 3, 1))]):
        db.add(Peremption(stock_id=stock.id, lot_numero=lot, date_peremption=date_p,
                          quantite=qte, statut="actif"))
    db.commit()

    res = StockValuationService.allocation_fefo(db, stock.id, 50)

    assert res["quantite_couverte"] == 50
    assert res["quantite_non_couverte"] == 0
    assert res["lots"][0]["lot_numero"] == "LOT-A"   # peremption la plus proche d'abord
    assert res["lots"][0]["quantite_allouee"] == 50


def test_fefo_signale_le_non_couvert(db, stock):
    db.add(Peremption(stock_id=stock.id, lot_numero="LOT-A", quantite=10,
                      date_peremption=date(2026, 3, 1), statut="actif"))
    db.commit()
    res = StockValuationService.allocation_fefo(db, stock.id, 50)
    assert res["quantite_non_couverte"] == 40


# --------------------------------------------------------------------------- #
# Ecriture comptable des ecarts d'inventaire
# --------------------------------------------------------------------------- #
@pytest.fixture
def referentiel_compta(db):
    def compte(numero, intitule, nature, classe):
        return PlanComptableOHADA(
            numero_compte=numero, intitule=intitule, type_compte=nature,
            classe=classe, sous_classe=0, compte_centralisateur=True,
            actif=True, date_creation=date(2020, 1, 1))
    stocks = compte("371", "Stocks de marchandises", TypeCompte.ACTIF, 3)
    variation = compte("6031", "Variation de stocks", TypeCompte.CHARGE, 6)
    db.add_all([stocks, variation])
    j = JournalAuxiliaire(code_journal="OD", nom_journal="Journal des operations diverses",
                          type_journal=TypeJournal.OD, statut="actif")
    db.add(j)
    ex = ExerciceComptable(numero_exercice="EX-2026", annee=2026,
                           date_debut=date(2026, 1, 1), date_fin=date(2026, 12, 31), statut="ouvert")
    db.add(ex)
    db.commit()
    return {"stocks": stocks, "variation": variation, "journal": j, "exercice": ex}


def _inventaire_avec_ecart(db, stock, ecart_val, suffixe="T1"):
    inv = InventaireTournant(numero_inventaire=f"INV-{suffixe}", entrepot_id=1,
                             date_debut=date(2026, 6, 1), statut="termine")
    db.add(inv)
    db.flush()
    db.add(LigneInventaire(inventaire_id=inv.id, stock_id=stock.id,
                           quantite_theorique=100, quantite_comptee=100 + ecart_val,
                           ecart=ecart_val, statut="compte"))
    db.commit()
    return inv


def test_ecriture_surplus_debite_stocks(db, stock, referentiel_compta):
    inv = _inventaire_avec_ecart(db, stock, 10)  # +10 x 8500 = +85 000
    res = InventaireEcritureService.generer_ecriture_ecarts(
        db, inv.id, date(2026, 6, 30), "371", "6031")

    assert res["sens"] == "surplus"
    assert res["montant"] == 85_000
    lignes = db.query(GrandLivreLigne).filter(
        GrandLivreLigne.periode == "2026-06").all()
    assert len(lignes) == 2
    debit = next(l for l in lignes if l.compte_id == referentiel_compta["stocks"].id)
    credit = next(l for l in lignes if l.compte_id == referentiel_compta["variation"].id)
    assert float(debit.debit) == 85_000 and float(credit.credit) == 85_000


def test_ecriture_depere_inverse_le_sens(db, stock, referentiel_compta):
    inv = _inventaire_avec_ecart(db, stock, -5)  # -5 x 8500 = -42 500
    res = InventaireEcritureService.generer_ecriture_ecarts(
        db, inv.id, date(2026, 6, 30), "371", "6031")

    assert res["sens"] == "dépérissement"
    assert res["montant"] == 42_500


def test_ecriture_idempotente_et_sans_ecart(db, stock, referentiel_compta):
    inv = _inventaire_avec_ecart(db, stock, 10)
    InventaireEcritureService.generer_ecriture_ecarts(
        db, inv.id, date(2026, 6, 30), "371", "6031")
    with pytest.raises(ValueError):
        InventaireEcritureService.generer_ecriture_ecarts(
            db, inv.id, date(2026, 6, 30), "371", "6031")

    inv2 = _inventaire_avec_ecart(db, stock, 0, suffixe="T2")
    with pytest.raises(ValueError):
        InventaireEcritureService.generer_ecriture_ecarts(
            db, inv2.id, date(2026, 6, 30), "371", "6031")


# --------------------------------------------------------------------------- #
# Recapitulatif annuel de paie
# --------------------------------------------------------------------------- #
def test_recapitulatif_annuel_cumule_et_patronal(db):
    employe = User(username="emp1", email="emp1@test.cm", hashed_password="x", is_active=True)
    db.add(employe)
    db.flush()
    for mois in (1, 2):
        db.add(Salaire(employe_id=employe.id, mois=mois, annee=2026,
                       salaire_brut=500000, salaire_net=400000,
                       deductions_cnps=23500, deductions_impot=30000,
                       periode_debut=date(2026, mois, 1), periode_fin=date(2026, mois, 28),
                       salaire_base=500000))
    db.commit()

    recap = PaieOHADAService.recapitulatif_annuel(db, 2026)

    assert len(recap) == 1
    l = recap[0]
    assert l["mois_payes"] == 2
    assert l["salaire_brut"] == 1_000_000
    assert l["salaire_net"] == 800_000
    assert l["cnps_salarial"] == 47_000
    assert l["cnps_patronal"] == round(1_000_000 * (0.042 + 0.0175), 2)
    assert l["cout_total_employeur"] == l["salaire_brut"] + l["cnps_patronal"]
