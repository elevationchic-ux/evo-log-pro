"""Tests états financiers réels : TAFIRE agrégé depuis le Grand Livre et
endpoint /etats-financiers/dernier honnête.

On vérifie que le TAFIRE est dérivé des écritures comptables réelles
(CAF = résultat net + dotations, ressources/emplois agrégés par classe
SYSCOHADA, variation = ressources - emplois) et que /dernier retourne
null tant qu'un document n'a pas été généré, puis le document persisté
une fois généré. Aucune valeur n'est inventée côté client.
"""
from datetime import date

import pytest

from app.models.finance_ohada import (
    PlanComptableOHADA, JournalAuxiliaire, ExerciceComptable,
    CompteResultatOHADADetaille, TypeCompte, TypeJournal,
)
from app.schemas.finance import PieceCreate, LignePieceCreate
from app.services.finance_service import PieceComptableService
from app.services.comptabilite_avance_service import EtatsFinanciersOHADAService

URL_DERNIER = "/api/v1/comptabilite-avance/etats-financiers/dernier"
URL_TAFIRE = "/api/v1/comptabilite-avance/etats-financiers/tafire"


# ──────────────────────────────────────────────────────────────────────────────
# Fixtures
# ──────────────────────────────────────────────────────────────────────────────

@pytest.fixture
def plan_tafire(db):
    """Plan comptable multi-classes + journal + exercice ouvert 2026."""
    comptes_data = [
        ("1011", "Capital", TypeCompte.PASSIF, 1),
        ("1651", "Emprunts", TypeCompte.PASSIF, 1),
        ("2055", "Matériel et outillage", TypeCompte.ACTIF, 2),
        ("3055", "Stocks", TypeCompte.ACTIF, 3),
        ("4011", "Fournisseurs", TypeCompte.PASSIF, 4),
        ("4111", "Clients", TypeCompte.ACTIF, 4),
        ("5121", "Banque", TypeCompte.ACTIF, 5),
        ("7061", "Ventes prestations", TypeCompte.PRODUIT, 7),
        ("7751", "Produits cessions immobilisations", TypeCompte.PRODUIT, 7),
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
        code_journal="BQ", nom_journal="Banque",
        type_journal=TypeJournal.VENTES, statut="actif",
    )
    db.add(journal)

    exercice = ExerciceComptable(
        numero_exercice="EX-TAF", annee=2026,
        date_debut=date(2026, 1, 1), date_fin=date(2026, 12, 31),
        statut="ouvert",
    )
    db.add(exercice)
    db.commit()
    return {"comptes": comptes, "journal": journal, "exercice": exercice}


def _piece(db, c, lignes, journal):
    piece = PieceCreate(
        date_ecriture=date(2026, 6, 15),
        libelle="Mouvement TAFIRE",
        journal_id=journal.id,
        lignes=[LignePieceCreate(**l) for l in lignes],
    )
    return PieceComptableService.creer_piece(db, piece)


def _mouvementsComplets(db, plan):
    """Série d'écritures équilibrées couvrant chaque rubrique du TAFIRE."""
    c = plan["comptes"]
    j = plan["journal"]
    _piece(db, c, [
        {"compte_id": c["5121"].id, "debit": 10_000_000},
        {"compte_id": c["1011"].id, "credit": 10_000_000},
    ], j)  # augmentation de capital
    _piece(db, c, [
        {"compte_id": c["5121"].id, "debit": 5_000_000},
        {"compte_id": c["1651"].id, "credit": 5_000_000},
    ], j)  # nouvel emprunt
    _piece(db, c, [
        {"compte_id": c["2055"].id, "debit": 8_000_000},
        {"compte_id": c["5121"].id, "credit": 8_000_000},
    ], j)  # investissement
    _piece(db, c, [
        {"compte_id": c["1651"].id, "debit": 1_000_000},
        {"compte_id": c["5121"].id, "credit": 1_000_000},
    ], j)  # remboursement emprunt
    _piece(db, c, [
        {"compte_id": c["5121"].id, "debit": 2_000_000},
        {"compte_id": c["7751"].id, "credit": 2_000_000},
    ], j)  # cession d'immobilisation
    _piece(db, c, [
        {"compte_id": c["4111"].id, "debit": 3_000_000},
        {"compte_id": c["7061"].id, "credit": 3_000_000},
    ], j)  # créance client (hausse BFR)


# ──────────────────────────────────────────────────────────────────────────────
# TAFIRE : dérivation réelle depuis le Grand Livre
# ──────────────────────────────────────────────────────────────────────────────

def test_tafire_caf_egale_resultat_plus_dotations(db, plan_tafire):
    """CAF = résultat net + dotations amortissements (charges non décaissées)."""
    plan = plan_tafire
    ex = plan["exercice"]
    cr = CompteResultatOHADADetaille(
        exercice_id=ex.id, periode="2026-06", date_arrete=date(2026, 6, 30),
        resultat_net=4_000_000, dotations_amortissements=1_000_000,
    )
    db.add(cr)
    db.commit()

    taf = EtatsFinanciersOHADAService.generer_tafire(db, ex.id, date(2026, 6, 30))
    assert float(taf.capacit_autofinancement) == 5_000_000.0


def test_tafire_ressources_emplois_variation(db, plan_tafire):
    """TAFIRE complet agrégé depuis les écritures réelles."""
    plan = plan_tafire
    ex = plan["exercice"]
    cr = CompteResultatOHADADetaille(
        exercice_id=ex.id, periode="2026-06", date_arrete=date(2026, 6, 30),
        resultat_net=4_000_000, dotations_amortissements=1_000_000,
    )
    db.add(cr)
    db.commit()
    _mouvementsComplets(db, plan)

    taf = EtatsFinanciersOHADAService.generer_tafire(db, ex.id, date(2026, 6, 30))

    assert float(taf.capacit_autofinancement) == 5_000_000.0
    assert float(taf.augmentation_capital) == 10_000_000.0
    assert float(taf.nouveaux_emprunts) == 5_000_000.0
    assert float(taf.cession_immobilisations) == 2_000_000.0
    assert float(taf.total_ressources) == 22_000_000.0

    assert float(taf.investissements_immobilisations) == 8_000_000.0
    assert float(taf.remboursement_emprunts) == 1_000_000.0
    assert float(taf.distribution_dividendes) == 0.0  # pas de compte dédié
    assert float(taf.augmentation_besoin_fdr) == 3_000_000.0
    assert float(taf.total_emplois) == 12_000_000.0

    # Variation = ressources - emplois (identité comptable, jamais inventée)
    assert float(taf.variation_tresorerie) == 10_000_000.0
    assert (
        float(taf.total_ressources) - float(taf.total_emplois)
        == float(taf.variation_tresorerie)
    )


def test_tafire_vide_sans_cr(db, plan_tafire):
    """Sans CR ni écritures : tout à zéro, aucun crash, rien d'inventé."""
    ex = plan_tafire["exercice"]
    taf = EtatsFinanciersOHADAService.generer_tafire(db, ex.id, date(2026, 6, 30))
    assert float(taf.capacit_autofinancement) == 0.0
    assert float(taf.total_ressources) == 0.0
    assert float(taf.total_emplois) == 0.0
    assert float(taf.variation_tresorerie) == 0.0


def test_tafire_exercice_inexistant_rejette(db):
    """Exercice introuvable → ValueError (pas de document vide)."""
    with pytest.raises(ValueError, match="Exercice introuvable"):
        EtatsFinanciersOHADAService.generer_tafire(db, 999_999, date(2026, 6, 30))


# ──────────────────────────────────────────────────────────────────────────────
# API /etats-financiers/dernier : lecture honnête
# ──────────────────────────────────────────────────────────────────────────────

def test_dernier_null_sans_documents(client, db, plan_tafire):
    """Aucun document généré → chaque état est null (pas de 0 mensonger)."""
    res = client.get(URL_DERNIER)
    assert res.status_code == 200
    d = res.json()
    assert d["annee"] == 2026
    assert d["exercice_id"] == plan_tafire["exercice"].id
    assert d["bilan"] is None
    assert d["compte_resultat"] is None
    assert d["tafire"] is None
    assert d["annexes"] is None


def test_dernier_apres_generation_tafire(client, db, plan_tafire):
    """Après POST /tafire, /dernier renvoie le TAFIRE persisté, les autres null."""
    ex = plan_tafire["exercice"]
    res = client.post(URL_TAFIRE, json={
        "exercice_id": ex.id,
        "date_tafire": "2026-06-30",
    })
    assert res.status_code == 200

    res2 = client.get(URL_DERNIER)
    assert res2.status_code == 200
    d = res2.json()
    assert d["tafire"] is not None
    assert d["tafire"]["exercice_id"] == ex.id
    # Les autres documents restent honnêtement null
    assert d["bilan"] is None
    assert d["compte_resultat"] is None
    assert d["annexes"] is None


def test_dernier_exercice_specifie_par_id(client, db, plan_tafire):
    """On peut cibler un exercice précis via exercice_id."""
    ex = plan_tafire["exercice"]
    res = client.get(URL_DERNIER + f"?exercice_id={ex.id}")
    assert res.status_code == 200
    assert res.json()["exercice_id"] == ex.id


def test_dernier_404_sans_exercice(client, db):
    """Aucun exercice en base → 404 honnête."""
    res = client.get(URL_DERNIER)
    assert res.status_code == 404
