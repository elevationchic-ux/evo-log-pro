"""Tests du sous-module CLOTURES (arretes des comptes) de la comptabilite OHADA.

Gabarit flagship applique : la page Clotures affichait jadis des periodes
FABRIQUEES depuis `new Date()` (statut CLOTURE/EN_COURS invente, checklist a
`done:true` codee en dur, boutton "Cloture annuelle" = faux toast). Desormais
la page consomme un etat REEL calcule cote serveur.

Couverture :
  * ClotureService.etats_periodes : compte les pieces reellement validees par
    periode, ne declare une periode « cloturee » que si une balance de
    verification equilibree existe ; resout l'exercice ouvert sans identifiant
    en dur.
  * cloture_mensuelle : ecrit une balance reelle, puis refuse une double
    cloture (regle serveur), refuse une periode sans ecriture.
  * report_a_nouveau : ne plante plus (ancien NameError `exercice_cible`) et
    rend un apercu honnete non persiste.
  * API GET /comptabilite-avance/cloture/etats (200, 12 periodes) et
    POST /comptabilite-avance/cloture/mensuelle (200 puis 400 en double).
"""
from datetime import date

import pytest
from fastapi import HTTPException  # noqa: F401

from app.models.finance_ohada import (
    PlanComptableOHADA, JournalAuxiliaire, ExerciceComptable,
    TypeCompte, TypeJournal,
)
from app.schemas.finance import PieceCreate, LignePieceCreate
from app.services.finance_service import PieceComptableService
from app.services.comptabilite_avance_service import ClotureService

URL_ETATS = "/api/v1/comptabilite-avance/cloture/etats"
URL_MENSUELLE = "/api/v1/comptabilite-avance/cloture/mensuelle"
URL_PIECES = "/api/v1/finance/pieces"


@pytest.fixture
def referentiel(db):
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
    banque = PlanComptableOHADA(
        numero_compte="5121", intitule="Banque", type_compte=TypeCompte.ACTIF,
        classe=5, sous_classe=1, compte_centralisateur=True, actif=True,
        date_creation=date(2020, 1, 1),
    )
    db.add_all([clients, ventes, banque])

    j_ventes = JournalAuxiliaire(
        code_journal="VTE", nom_journal="Journal des Ventes",
        type_journal=TypeJournal.VENTES, compte_centralisateur="411",
        statut="actif",
    )
    db.add(j_ventes)

    exercice = ExerciceComptable(
        numero_exercice="EX-CLOT", annee=2026,
        date_debut=date(2026, 1, 1), date_fin=date(2026, 12, 31),
        statut="ouvert",
    )
    db.add(exercice)
    db.commit()
    return {
        "clients": clients, "ventes": ventes, "banque": banque,
        "j_ventes": j_ventes, "exercice": exercice,
    }


def _creer_piece(db, r, lignes, date_ecriture):
    piece = PieceCreate(
        date_ecriture=date_ecriture,
        libelle="Ecriture de test cloture",
        journal_id=r["j_ventes"].id,
        lignes=[LignePieceCreate(**l) for l in lignes],
    )
    return PieceComptableService.creer_piece(db, piece)


def _vente(db, r, date_ecriture, montant=1000):
    return _creer_piece(db, r, [
        {"compte_id": r["clients"].id, "debit": montant},
        {"compte_id": r["ventes"].id, "credit": montant},
    ], date_ecriture)


# --------------------------------------------------------------------------- #
# etats_periodes : etat REEL, rien d'invente                                    #
# --------------------------------------------------------------------------- #
def test_etats_compte_pieces_validees_par_periode(db, referentiel):
    r = referentiel
    _vente(db, r, date(2026, 5, 10))
    _vente(db, r, date(2026, 5, 20))
    _vente(db, r, date(2026, 6, 5))

    etats = ClotureService.etats_periodes(db, r["exercice"].id)

    par_periode = {p["periode"]: p for p in etats["periodes"]}
    assert len(etats["periodes"]) == 12
    assert par_periode["2026-05"]["entries_count"] == 2
    assert par_periode["2026-06"]["entries_count"] == 1
    assert par_periode["2026-07"]["entries_count"] == 0
    # Aucune cloture encore : rien n'est ferme, solde d'attente honnete.
    assert par_periode["2026-05"]["closed"] is False
    assert par_periode["2026-05"]["balance_statut"] is None
    assert etats["exercice_statut"] == "ouvert"


def test_etats_resout_exercice_ouvert_sans_identifiant(db, referentiel):
    """La page ne code plus d'identifiant d'exercice en dur : le serveur rend
    l'exercice ouvert le plus recent."""
    r = referentiel
    etats = ClotureService.etats_periodes(db)
    assert etats["exercice_id"] == r["exercice"].id
    assert etats["annee"] == 2026


def test_etats_sans_exercice_rejet(db):
    with pytest.raises(ValueError):
        ClotureService.etats_periodes(db)


# --------------------------------------------------------------------------- #
# cloture_mensuelle : ecrit une balance reelle puis verrouille (regle serveur)  #
# --------------------------------------------------------------------------- #
def test_cloture_mensuelle_puis_periode_clos(db, referentiel):
    r = referentiel
    _vente(db, r, date(2026, 5, 10), montant=5000)

    resultat = ClotureService.cloture_mensuelle(db, r["exercice"].id, "2026-05", "DAF")
    assert resultat["statut"] == "cloturee"

    etats = ClotureService.etats_periodes(db, r["exercice"].id)
    mai = next(p for p in etats["periodes"] if p["periode"] == "2026-05")
    assert mai["closed"] is True
    assert mai["balance_statut"] == "equilibre"
    assert mai["balance_date"] == date.today()


def test_cloture_mensuelle_refuse_double(db, referentiel):
    r = referentiel
    _vente(db, r, date(2026, 5, 10))
    ClotureService.cloture_mensuelle(db, r["exercice"].id, "2026-05", "DAF")
    with pytest.raises(ValueError) as exc:
        ClotureService.cloture_mensuelle(db, r["exercice"].id, "2026-05", "DAF")
    assert "déjà clôturée" in str(exc.value)


def test_cloture_mensuelle_refuse_periode_vide(db, referentiel):
    r = referentiel
    with pytest.raises(ValueError) as exc:
        ClotureService.cloture_mensuelle(db, r["exercice"].id, "2026-09", "DAF")
    assert "Aucune écriture" in str(exc.value)


# --------------------------------------------------------------------------- #
# report_a_nouveau : plus de crash, retour honnete                              #
# --------------------------------------------------------------------------- #
def test_report_a_nouveau_ne_plante_plus(db, referentiel):
    r = referentiel
    resultat = ClotureService.report_a_nouveau(db, r["exercice"].id, r["exercice"].id)
    # L'ancien code levait NameError (`exercice_cible`) ; on attend un apercu.
    assert resultat["statut"] == "apercu_non_persiste"
    assert resultat["exercice_cible_id"] == r["exercice"].id
    assert resultat["nombre_comptes"] >= 3  # comptes de classes 4,5 presents


# --------------------------------------------------------------------------- #
# API : endpoints reels consommes par la page                                    #
# --------------------------------------------------------------------------- #
def test_api_etats_periodes(client, referentiel):
    r = referentiel
    payload = {
        "date_ecriture": "2026-05-10",
        "libelle": "Vente",
        "journal_id": r["j_ventes"].id,
        "lignes": [
            {"compte_id": r["clients"].id, "debit": 7000},
            {"compte_id": r["ventes"].id, "credit": 7000},
        ],
    }
    created = client.post(URL_PIECES, json=payload)
    assert created.status_code == 201, created.text

    r2 = client.get(URL_ETATS)
    assert r2.status_code == 200, r2.text
    corps = r2.json()
    assert len(corps["periodes"]) == 12
    mai = next(p for p in corps["periodes"] if p["periode"] == "2026-05")
    assert mai["entries_count"] == 1
    assert mai["closed"] is False


def test_api_cloture_mensuelle_puis_verrou(client, referentiel):
    r = referentiel
    payload = {
        "date_ecriture": "2026-05-12",
        "libelle": "Vente",
        "journal_id": r["j_ventes"].id,
        "lignes": [
            {"compte_id": r["clients"].id, "debit": 9000},
            {"compte_id": r["ventes"].id, "credit": 9000},
        ],
    }
    assert client.post(URL_PIECES, json=payload).status_code == 201

    clos = client.post(URL_MENSUELLE, json={
        "exercice_id": r["exercice"].id, "periode": "2026-05", "cloture_par": "DAF",
    })
    assert clos.status_code == 200, clos.text
    assert clos.json()["statut"] == "cloturee"

    # Double cloture = refus serveur (400), pas un faux succes.
    again = client.post(URL_MENSUELLE, json={
        "exercice_id": r["exercice"].id, "periode": "2026-05", "cloture_par": "DAF",
    })
    assert again.status_code == 400, again.text
    assert "déjà clôturée" in again.json()["detail"]

    # L'etat expose le verrouillage reel.
    etats = client.get(URL_ETATS).json()
    mai = next(p for p in etats["periodes"] if p["periode"] == "2026-05")
    assert mai["closed"] is True
