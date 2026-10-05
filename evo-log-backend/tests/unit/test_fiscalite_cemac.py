"""Tests fiscalité CEMAC : TVA agrégée depuis le Grand Livre, IS dérivé du
Compte de Résultat, DIPE agrégé depuis la table salaires.

Vérifie que les endpoints et services retournent des valeurs réelles calculées
à partir des écritures comptables, sans aucune fabrication client-side.
"""
from datetime import date

import pytest

from app.models.finance_ohada import (
    PlanComptableOHADA, JournalAuxiliaire, ExerciceComptable,
    GrandLivreLigne, EcritureComptableNew, CompteResultatOHADADetaille,
    TypeCompte, TypeJournal,
)
from app.models.rh import Salaire
from app.schemas.finance import PieceCreate, LignePieceCreate
from app.services.finance_service import PieceComptableService
from app.services.comptabilite_avance_service import TVAService, ISService

URL_TVA = "/api/v1/comptabilite-avance/declarations-tva"
URL_TVA_VAL = "/api/v1/comptabilite-avance/declarations-tva/valider"
URL_IS = "/api/v1/comptabilite-avance/declarations-is"
URL_DIPE = "/api/v1/rh-avance/dipe-mensuel"


# ──────────────────────────────────────────────────────────────────────────────
# Fixtures
# ──────────────────────────────────────────────────────────────────────────────

@pytest.fixture
def plan_tva(db):
    """Plan comptable avec comptes TVA SYSCOHADA + journal + exercice."""
    comptes_data = [
        ("4111", "Clients", TypeCompte.ACTIF, 4),
        ("4011", "Fournisseurs", TypeCompte.PASSIF, 4),
        ("7061", "Ventes prestations", TypeCompte.PRODUIT, 7),
        ("6051", "Achats non stockés", TypeCompte.CHARGE, 6),
        ("4431", "TVA collectée", TypeCompte.PASSIF, 4),
        ("4451", "TVA déductible charges", TypeCompte.ACTIF, 4),
        ("4452", "TVA déductible immobilisations", TypeCompte.ACTIF, 4),
        ("5121", "Banque", TypeCompte.ACTIF, 5),
    ]
    comptes = {}
    for num, intitule, typ, classe in comptes_data:
        c = PlanComptableOHADA(
            numero_compte=num, intitule=intitule, type_compte=typ,
            classe=classe, sous_classe=0, compte_centralisateur=True,
            actif=True, date_creation=date(2020, 1, 1),
        )
        db.add(c)
        comptes[num] = c
    db.flush()

    journal = JournalAuxiliaire(
        code_journal="VTE", nom_journal="Ventes",
        type_journal=TypeJournal.VENTES, statut="actif",
    )
    db.add(journal)

    exercice = ExerciceComptable(
        numero_exercice="EX-TVA", annee=2026,
        date_debut=date(2026, 1, 1), date_fin=date(2026, 12, 31),
        statut="ouvert",
    )
    db.add(exercice)
    db.commit()
    return {"comptes": comptes, "journal": journal, "exercice": exercice}


def _piece(db, compte_ids, lignes, date_ec, journal):
    """Crée une pièce équilibrée."""
    piece = PieceCreate(
        date_ecriture=date_ec,
        libelle="Test fiscalité",
        journal_id=journal.id,
        lignes=[LignePieceCreate(**l) for l in lignes],
    )
    return PieceComptableService.creer_piece(db, piece)


# ──────────────────────────────────────────────────────────────────────────────
# TVA : agrégation depuis le Grand Livre
# ──────────────────────────────────────────────────────────────────────────────

def test_tva_agregation_from_gl(db, plan_tva):
    """Une vente avec TVA génère les lignes GL 4431 crédit et 7061 crédit."""
    p = plan_tva
    c = p["comptes"]
    # Vente : Client 1 192 500 = Ventes HT 1 000 000 + TVA 192 500
    _piece(db, c, [
        {"compte_id": c["4111"].id, "debit": 1_192_500},
        {"compte_id": c["7061"].id, "credit": 1_000_000},
        {"compte_id": c["4431"].id, "credit": 192_500},
    ], date(2026, 3, 15), p["journal"])

    result = TVAService.calculer_tva_periode(db, "2026-03")
    assert result["tva_collectee"] == 192_500.0
    assert result["ca_taxable"] == 1_000_000.0
    assert result["net_tva_payer"] == 192_500.0  # no deductions yet
    assert result["statut"] == "BROUILLON"


def test_tva_avec_deductible_charges_et_immo(db, plan_tva):
    """Achat de charges et d'immobilisation avec TVA déductible."""
    p = plan_tva
    c = p["comptes"]
    # Vente TVA collectée 192 500
    _piece(db, c, [
        {"compte_id": c["4111"].id, "debit": 1_192_500},
        {"compte_id": c["7061"].id, "credit": 1_000_000},
        {"compte_id": c["4431"].id, "credit": 192_500},
    ], date(2026, 3, 10), p["journal"])
    # Achat charges : 605 192.50 = 525 000 HT + TVA 60 192.50 (compte 4451)
    _piece(db, c, [
        {"compte_id": c["6051"].id, "debit": 525_000},
        {"compte_id": c["4451"].id, "debit": 60_192.50},
        {"compte_id": c["4011"].id, "credit": 585_192.50},
    ], date(2026, 3, 12), p["journal"])
    # Achat immo : TVA 4452 = 50 000
    _piece(db, c, [
        {"compte_id": c["4452"].id, "debit": 50_000},
        {"compte_id": c["4011"].id, "credit": 50_000},
    ], date(2026, 3, 14), p["journal"])

    result = TVAService.calculer_tva_periode(db, "2026-03")
    assert result["tva_collectee"] == 192_500.0
    assert result["tva_deductible_immo"] == 50_000.0
    assert result["tva_deductible_charges"] == 60_192.50
    # net = 192500 - 50000 - 60192.50 = 82307.50
    assert abs(result["net_tva_payer"] - 82_307.50) < 0.01


def test_tva_periode_vide(db, plan_tva):
    """Période sans écritures → tout à zéro, aucun crash."""
    result = TVAService.calculer_tva_periode(db, "2026-06")
    assert result["tva_collectee"] == 0
    assert result["ca_taxable"] == 0
    assert result["net_tva_payer"] == 0


def test_tva_valider_cree_declaration(db, plan_tva):
    """Valider enregistre TVADeclarable et passe statut à VALIDE."""
    p = plan_tva
    c = p["comptes"]
    _piece(db, c, [
        {"compte_id": c["4111"].id, "debit": 1_192_500},
        {"compte_id": c["7061"].id, "credit": 1_000_000},
        {"compte_id": c["4431"].id, "credit": 192_500},
    ], date(2026, 4, 15), p["journal"])

    res = TVAService.valider_declaration(db, "2026-04", "Testeur")
    assert res["statut"] == "VALIDEE"
    assert "e-bulletin" in res["message"].lower()

    # check statut updated in subsequent call
    calc = TVAService.calculer_tva_periode(db, "2026-04")
    assert calc["statut"] == "VALIDE"


def test_tva_valider_double_rejette(db, plan_tva):
    """Impossible de valider deux fois la même période."""
    p = plan_tva
    c = p["comptes"]
    _piece(db, c, [
        {"compte_id": c["4111"].id, "debit": 500_000},
        {"compte_id": c["7061"].id, "credit": 420_000},
        {"compte_id": c["4431"].id, "credit": 80_000},
    ], date(2026, 5, 10), p["journal"])

    TVAService.valider_declaration(db, "2026-05", "Testeur")
    with pytest.raises(ValueError, match="déjà été déclarée"):
        TVAService.valider_declaration(db, "2026-05", "Testeur")


def test_tva_valider_vide_rejette(db, plan_tva):
    """Valider sans écritures → ValueError."""
    with pytest.raises(ValueError, match="rien à déclarer"):
        TVAService.valider_declaration(db, "2026-07", "Testeur")


# ──────────────────────────────────────────────────────────────────────────────
# IS : dérivé du Compte de Résultat
# ──────────────────────────────────────────────────────────────────────────────

def test_is_derivation_from_cr(db, plan_tva):
    """IS = 30% du résultat net si > minimum perception."""
    ex = plan_tva["exercice"]
    cr = CompteResultatOHADADetaille(
        exercice_id=ex.id,
        periode="2026-12",
        date_arrete=date(2026, 12, 31),
        resultat_net=20_000_000,
        total_produits_exploitation=50_000_000,
        total_charges_exploitation=30_000_000,
    )
    db.add(cr)
    db.commit()

    res = ISService.deriver_is(db, 2026)
    assert res["base_imposable"] == 20_000_000.0
    assert res["is_brut"] == 6_000_000.0
    assert res["is_exigible"] == 6_000_000.0  # > minimum 1M
    assert res["solde_is"] == 6_000_000.0
    assert res["taux_is"] == 30


def test_is_minimum_perception(db, plan_tva):
    """Si résultat < ~3.33M, IS = minimum 1 000 000."""
    ex = plan_tva["exercice"]
    cr = CompteResultatOHADADetaille(
        exercice_id=ex.id,
        periode="2026-12",
        date_arrete=date(2026, 12, 31),
        resultat_net=1_000_000,
    )
    db.add(cr)
    db.commit()

    res = ISService.deriver_is(db, 2026)
    assert res["is_brut"] == 300_000.0
    assert res["is_exigible"] == 1_000_000.0  # minimum perception


def test_is_pas_de_cr_rejette(db, plan_tva):
    """Aucun compte de résultat → ValueError."""
    with pytest.raises(ValueError, match="compte de résultat"):
        ISService.deriver_is(db, 2026)


def test_is_pas_exercice_rejette(db):
    """Aucun exercice pour cette année → ValueError."""
    with pytest.raises(ValueError, match="Aucun exercice"):
        ISService.deriver_is(db, 2099)


# ──────────────────────────────────────────────────────────────────────────────
# DIPE : agrégation depuis la table salaires
# ──────────────────────────────────────────────────────────────────────────────

@pytest.fixture
def salaires(db):
    """Deux salariés avec fiches de paie pour mars 2026."""
    from app.models.user import User
    emp1 = User(email="emp1@test.com", full_name="Emp One", is_active=True)
    emp2 = User(email="emp2@test.com", full_name="Emp Two", is_active=True)
    db.add_all([emp1, emp2])
    db.flush()

    s1 = Salaire(
        employe_id=emp1.id, mois=3, annee=2026,
        salaire_brut=500_000, heures_sup=0, primes=0, deductions=50_000,
        periode_debut=date(2026, 3, 1), periode_fin=date(2026, 3, 31),
        salaire_base=500_000, salaire_net=450_000,
        deductions_cnps=21_000, deductions_impot=29_000,
    )
    s2 = Salaire(
        employe_id=emp2.id, mois=3, annee=2026,
        salaire_brut=750_000, heures_sup=0, primes=0, deductions=75_000,
        periode_debut=date(2026, 3, 1), periode_fin=date(2026, 3, 31),
        salaire_base=750_000, salaire_net=675_000,
        deductions_cnps=31_500, deductions_impot=43_500,
    )
    db.add_all([s1, s2])
    db.commit()
    return {"emp1": emp1, "emp2": emp2, "s1": s1, "s2": s2}


def test_dipe_agregation(client, salaires):
    """GET /rh-avance/dipe-mensuel agrège les salaires réels."""
    res = client.get(URL_DIPE + "?periode=2026-03")
    assert res.status_code == 200
    d = res.json()
    assert d["nb_employes"] == 2
    assert d["masse_salariale_brute"] == 1_250_000.0
    assert d["cnps_employe"] == 52_500.0
    assert d["ircm_verse"] == 72_500.0
    assert d["cnps_patron"] == round(1_250_000.0 * 0.174, 2)
    assert d["fne_verse"] == round(1_250_000.0 * 0.01, 2)
    assert d["statut"] == "CONFORME"


def test_dipe_vide(client, db):
    """DIPE sans salariés → statut AUCUNE_DONNEE."""
    res = client.get(URL_DIPE + "?periode=2030-01")
    assert res.status_code == 200
    d = res.json()
    assert d["nb_employes"] == 0
    assert d["statut"] == "AUCUNE_DONNEE"


# ──────────────────────────────────────────────────────────────────────────────
# API endpoint tests
# ──────────────────────────────────────────────────────────────────────────────

def test_api_tva_get(client, db, plan_tva):
    """GET /declarations-tva?periode= retourne l'agrégation TVA."""
    p = plan_tva
    c = p["comptes"]
    _piece(db, c, [
        {"compte_id": c["4111"].id, "debit": 1_192_500},
        {"compte_id": c["7061"].id, "credit": 1_000_000},
        {"compte_id": c["4431"].id, "credit": 192_500},
    ], date(2026, 8, 15), p["journal"])

    res = client.get(URL_TVA + "?periode=2026-08")
    assert res.status_code == 200
    d = res.json()
    assert d["tva_collectee"] == 192_500.0
    assert d["ca_taxable"] == 1_000_000.0
    assert d["statut"] == "BROUILLON"


def test_api_tva_valider(client, db, plan_tva):
    """POST /declarations-tva/valider enregistre la déclaration."""
    p = plan_tva
    c = p["comptes"]
    _piece(db, c, [
        {"compte_id": c["4111"].id, "debit": 1_000_000},
        {"compte_id": c["7061"].id, "credit": 839_000},
        {"compte_id": c["4431"].id, "credit": 161_000},
    ], date(2026, 9, 10), p["journal"])

    res = client.post(URL_TVA_VAL, json={"periode": "2026-09"})
    assert res.status_code == 200
    assert res.json()["statut"] == "VALIDEE"


def test_api_is_get(client, db, plan_tva):
    """GET /declarations-is?annee= retourne l'IS dérivé du CR."""
    ex = plan_tva["exercice"]
    cr = CompteResultatOHADADetaille(
        exercice_id=ex.id, periode="2026-12", date_arrete=date(2026, 12, 31),
        resultat_net=15_000_000,
    )
    db.add(cr)
    db.commit()

    res = client.get(URL_IS + "?annee=2026")
    assert res.status_code == 200
    d = res.json()
    assert d["base_imposable"] == 15_000_000.0
    assert d["is_brut"] == 4_500_000.0
    assert d["is_exigible"] == 4_500_000.0


def test_api_is_404_sans_cr(client, db, plan_tva):
    """GET /declarations-is sans CR → 404."""
    res = client.get(URL_IS + "?annee=2026")
    assert res.status_code == 404
