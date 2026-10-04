"""Comptabilite SYSCOHADA : verification de la VRAIE partie double.

Ce module verrouille le comportement qui manquait au module : une piece
comptable doit obligatoirement equilibree (somme debit == somme credit) et
porter au moins deux comptes (un debit et une contrepartie en credit). Les
anciens chemins "plats" (une ligne unique portant a la fois un compte, un
debit et un credit, sans contrepartie) acceptaient n'importe quoi ; ils sont
supprimes.

Couverture :
  * service PieceComptableService : rejet < 2 lignes, rejet ligne cumulant
    debit+credit, rejet ligne sans cote, rejet compte inexistant, rejet compte
    inactif, rejet piece desequilibree (ecart affiche), rejet date hors
    exercice ouvert, acceptation d'une piece equilibree + verification des
    totaux et de la materialisation du grand livre.
  * API POST /finance/pieces (201 equilibre / 422 desequilibre) et
    GET /finance/pieces/{id} (renvoie les lignes).
  * Le chemin plat POST /finance/ecritures repond 410 (supprime).
  * Idempotence de la migration de seed 041 (re-run sans doublon).
"""
import importlib.util
import os
from datetime import date

import pytest
from fastapi import HTTPException
from fastapi.testclient import TestClient

from app.models.finance_ohada import (
    PlanComptableOHADA, JournalAuxiliaire, ExerciceComptable,
    LigneJournal, GrandLivreLigne, EcritureComptableNew,
    TypeCompte, TypeJournal,
)
from app.schemas.finance import PieceCreate, LignePieceCreate
from app.services.finance_service import PieceComptableService

URL_PIECES = "/api/v1/finance/pieces"
URL_ECRITURES_PLAT = "/api/v1/finance/ecritures"


# --------------------------------------------------------------------------- #
# Referentiels reels (plan, journaux, exercice) : aucune donnee inventee, ce    #
# sont les comptes normatifs SYSCOHADA utilises par les tests.                  #
# --------------------------------------------------------------------------- #
@pytest.fixture
def referentiel(db):
    capital = PlanComptableOHADA(
        numero_compte="1011", intitule="Capital", type_compte=TypeCompte.PASSIF,
        classe=1, sous_classe=0, compte_centralisateur=True, actif=True,
        date_creation=date(2020, 1, 1),
    )
    banque = PlanComptableOHADA(
        numero_compte="5121", intitule="Banque", type_compte=TypeCompte.ACTIF,
        classe=5, sous_classe=1, compte_centralisateur=True, actif=True,
        date_creation=date(2020, 1, 1),
    )
    clients = PlanComptableOHADA(
        numero_compte="4111", intitule="Clients", type_compte=TypeCompte.ACTIF,
        classe=4, sous_classe=1, compte_centralisateur=True, actif=True,
        date_creation=date(2020, 1, 1),
    )
    ventes = PlanComptableOHADA(
        numero_compte="7061", intitule="Prestations de services",
        type_compte=TypeCompte.PRODUIT, classe=7, sous_classe=0,
        compte_centralisateur=True, actif=True, date_creation=date(2020, 1, 1),
    )
    inactif = PlanComptableOHADA(
        numero_compte="9999", intitule="Compte fermé", type_compte=TypeCompte.ACTIF,
        classe=9, sous_classe=9, compte_centralisateur=False, actif=False,
        date_creation=date(2020, 1, 1),
    )
    db.add_all([capital, banque, clients, ventes, inactif])

    j_ventes = JournalAuxiliaire(
        code_journal="VTE", nom_journal="Journal des Ventes",
        type_journal=TypeJournal.VENTES, compte_centralisateur="411",
        statut="actif",
    )
    j_banque = JournalAuxiliaire(
        code_journal="BQ", nom_journal="Journal de Banque",
        type_journal=TypeJournal.BANQUE, compte_centralisateur="512",
        statut="actif",
    )
    db.add_all([j_ventes, j_banque])

    exercice = ExerciceComptable(
        numero_exercice="EX-TEST", annee=2020,
        date_debut=date(2000, 1, 1), date_fin=date(2100, 12, 31),
        statut="ouvert",
    )
    db.add(exercice)
    db.commit()
    return {
        "capital": capital, "banque": banque, "clients": clients,
        "ventes": ventes, "inactif": inactif,
        "j_ventes": j_ventes, "j_banque": j_banque, "exercice": exercice,
    }


def _piece(lignes, date_ecriture=None, journal_id=None, type_journal=None, libelle="Vente"):
    return PieceCreate(
        date_ecriture=date_ecriture or date(2026, 5, 10),
        libelle=libelle,
        journal_id=journal_id,
        type_journal=type_journal,
        lignes=[LignePieceCreate(**l) for l in lignes],
    )


# --------------------------------------------------------------------------- #
# Service : regles de la partie double                                          #
# --------------------------------------------------------------------------- #
def test_rejette_moins_de_deux_lignes(db, referentiel):
    piece = _piece([{"compte_id": referentiel["clients"].id, "debit": 100}])
    with pytest.raises(HTTPException) as exc:
        PieceComptableService.creer_piece(db, piece)
    assert exc.value.status_code == 422
    assert "2 lignes" in exc.value.detail


def test_rejette_ligne_portant_debit_et_credit(db, referentiel):
    piece = _piece([
        {"compte_id": referentiel["clients"].id, "debit": 100, "credit": 100},
        {"compte_id": referentiel["ventes"].id, "credit": 100},
    ])
    with pytest.raises(HTTPException) as exc:
        PieceComptableService.creer_piece(db, piece)
    assert exc.value.status_code == 422


def test_rejette_ligne_sans_cote(db, referentiel):
    piece = _piece([
        {"compte_id": referentiel["clients"].id, "debit": 0, "credit": 0},
        {"compte_id": referentiel["ventes"].id, "credit": 0},
    ])
    with pytest.raises(HTTPException) as exc:
        PieceComptableService.creer_piece(db, piece)
    assert exc.value.status_code == 422


def test_rejette_piece_desequilibree_et_affiche_ecart(db, referentiel):
    piece = _piece([
        {"compte_id": referentiel["clients"].id, "debit": 1000},
        {"compte_id": referentiel["ventes"].id, "credit": 700},
    ])
    with pytest.raises(HTTPException) as exc:
        PieceComptableService.creer_piece(db, piece)
    assert exc.value.status_code == 422
    assert "300" in exc.value.detail  # ecart debit-credit


def test_rejette_compte_inexistant(db, referentiel):
    piece = _piece([
        {"compte_id": 999999, "debit": 100},
        {"compte_id": referentiel["ventes"].id, "credit": 100},
    ])
    with pytest.raises(HTTPException) as exc:
        PieceComptableService.creer_piece(db, piece)
    assert exc.value.status_code == 422
    assert "inexistant" in exc.value.detail


def test_rejette_compte_inactif(db, referentiel):
    piece = _piece([
        {"compte_id": referentiel["inactif"].id, "debit": 100},
        {"compte_id": referentiel["ventes"].id, "credit": 100},
    ])
    with pytest.raises(HTTPException) as exc:
        PieceComptableService.creer_piece(db, piece)
    assert exc.value.status_code == 422
    assert "inactif" in exc.value.detail


def test_rejette_date_hors_exercice_ouvert(db, referentiel):
    # Fermer l'exercice : plus aucune date n'est couverte.
    referentiel["exercice"].statut = "cloture"
    db.commit()
    piece = _piece([
        {"compte_id": referentiel["clients"].id, "debit": 100},
        {"compte_id": referentiel["ventes"].id, "credit": 100},
    ])
    with pytest.raises(HTTPException) as exc:
        PieceComptableService.creer_piece(db, piece)
    assert exc.value.status_code == 422
    assert "exercice" in exc.value.detail.lower()


def test_accepte_piece_equilibree_et_materialise_grand_livre(db, referentiel):
    piece = _piece(
        [
            {"compte_id": referentiel["clients"].id, "debit": 5000},
            {"compte_id": referentiel["ventes"].id, "credit": 5000},
        ],
        journal_id=referentiel["j_ventes"].id,
    )
    resultat = PieceComptableService.creer_piece(db, piece)

    assert resultat["equilibree"] is True
    assert resultat["total_debit"] == 5000
    assert resultat["total_credit"] == 5000
    assert len(resultat["lignes"]) == 2

    # En-tete reellement persiste avec ses lignes.
    entete = db.get(EcritureComptableNew, resultat["id"])
    assert float(entete.total_debit) == 5000
    assert float(entete.total_credit) == 5000
    assert db.query(LigneJournal).filter(LigneJournal.ecriture_id == entete.id).count() == 2

    # Grand livre materialise pour chaque compte mouve.
    gl = db.query(GrandLivreLigne).filter(GrandLivreLigne.ecriture_id == entete.id).all()
    assert len(gl) == 2
    assert sum(float(l.debit or 0) for l in gl) == 5000
    assert sum(float(l.credit or 0) for l in gl) == 5000


def test_numerotation_continue_par_periode(db, referentiel):
    lignes = [
        {"compte_id": referentiel["clients"].id, "debit": 100},
        {"compte_id": referentiel["ventes"].id, "credit": 100},
    ]
    p1 = PieceComptableService.creer_piece(db, _piece(lignes, date_ecriture=date(2026, 5, 1), journal_id=referentiel["j_ventes"].id))
    p2 = PieceComptableService.creer_piece(db, _piece(lignes, date_ecriture=date(2026, 5, 20), journal_id=referentiel["j_ventes"].id))
    assert p1["numero_ecriture"] == "ECR-202605-0001"
    assert p2["numero_ecriture"] == "ECR-202605-0002"


# --------------------------------------------------------------------------- #
# API : un seul chemin d'ecriture reel, plus d'ecriture plate                   #
# --------------------------------------------------------------------------- #
def test_api_piece_equilibree_cree_et_relit_lignes(client, referentiel):
    payload = {
        "date_ecriture": "2026-06-15",
        "libelle": "Encaissement client",
        "type_journal": "VENTES",
        "lignes": [
            {"compte_id": referentiel["banque"].id, "debit": 250000},
            {"compte_id": referentiel["clients"].id, "credit": 250000},
        ],
    }
    r = client.post(URL_PIECES, json=payload)
    assert r.status_code == 201, r.text
    corps = r.json()
    assert corps["equilibree"] is True
    assert corps["total_debit"] == 250000

    r2 = client.get(f"{URL_PIECES}/{corps['id']}")
    assert r2.status_code == 200, r2.text
    relue = r2.json()
    assert len(relue["lignes"]) == 2
    comptes = sorted(l["compte_numero"] for l in relue["lignes"])
    assert comptes == ["4111", "5121"]


def test_api_piece_desequilibree_rejetee(client, referentiel):
    payload = {
        "date_ecriture": "2026-06-15",
        "libelle": "Piece fausse",
        "type_journal": "OD",
        "journal_id": referentiel["j_ventes"].id,
        "lignes": [
            {"compte_id": referentiel["clients"].id, "debit": 10},
            {"compte_id": referentiel["ventes"].id, "credit": 9},
        ],
    }
    r = client.post(URL_PIECES, json=payload)
    assert r.status_code == 422, r.text


def test_api_chemin_plat_supprime(client):
    r = client.post(URL_ECRITURES_PLAT, json={
        "numero_ecriture": "ECR-FLAT-1", "date_ecriture": "2026-06-15",
        "libelle": "plate", "compte_id": 1, "debit": 5, "credit": 0,
        "journal": "OD", "periode": "2026-06",
    })
    assert r.status_code == 410, r.text


# --------------------------------------------------------------------------- #
# Migration de seed : idempotence                                              #
# --------------------------------------------------------------------------- #
def _charger_module_seed():
    racine = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
    chemin = os.path.join(racine, "migrations", "versions", "041_seed_syscohada_referentiels.py")
    spec = importlib.util.spec_from_file_location("seed_041", chemin)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def test_seed_migration_idempotente(db):
    from alembic.migration import MigrationContext
    from alembic.operations import Operations

    module = _charger_module_seed()
    connexion = db.connection()
    ctx = MigrationContext.configure(connexion)
    ops = Operations(ctx)  # `alembic.op` n'est utilisable qu'avec le proxy installe
    ops._install_proxy()
    try:
        module.upgrade()
        premiere = db.query(PlanComptableOHADA).count()
        journaux_1 = db.query(JournalAuxiliaire).count()
        # Re-run : ne doit creer AUCUN doublon (insertion conditionnee par cle).
        module.upgrade()
        module.upgrade()
        db.commit()
        deuxieme = db.query(PlanComptableOHADA).count()
        journaux_2 = db.query(JournalAuxiliaire).count()
    finally:
        ops._remove_proxy()

    assert premiere == deuxieme
    assert journaux_1 == journaux_2
    assert premiere >= len(module.PLAN)
