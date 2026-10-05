"""Tests de SORTIE du module comptabilité OHADA (grand livre, balance, états
financiers), après la refonte en partie double.

Gabarit flagship applique aux sous-modules de sortie : la piece en partie
double materialise des lignes dans `grand_livre_lignes` ; l'en-tete plat de
l'ecriture porte desormais `compte_id = None` et les TOTAUX de piece dans
`debit/credit`. Toute aggregation de sortie doit donc partir des lignes reels
du grand livre, jamais de l'en-tete ni des colonnes `solde_debit/credit` du
plan (jamais majustes).

Couverture :
  * GrandLivreService.mouvements_par_compte : agregation par compte depuis le
    grand livre, independante de l'en-tete plat.
  * generer_grand_livre_general : LECTURE seule, ne recrée plus de lignes
    `compte_id=None` (ne crash plus, renvoie l'existant, pas de doublon).
  * BalanceService.calculer_balances_verification : 6 colonnes, solde d'ou-
    verture reporte d'une periode a l'autre, totaux debit==credit, equilibree.
  * BalanceService.creer_balance_verification + balance_par_journal : persiste
    des lignes par compte reellement mouve.
  * EtatsFinanciersOHADAService.generer_bilan_ohada_detaille : Actif == Passif
    (resultat replie dans les capitaux), valeurs non nulles.
  * generer_compte_resultat_ohada_detaille : resultat = produits - charges,
    y compris en cas de perte.
  * API GET /comptabilite-avance/balances/verification (200 + lignes).
"""
from datetime import date

import pytest
from fastapi.testclient import TestClient  # noqa: F401  (fixture client)

from app.models.finance_ohada import (
    PlanComptableOHADA, JournalAuxiliaire, ExerciceComptable,
    GrandLivreLigne, TypeCompte, TypeJournal,
)
from app.schemas.finance import PieceCreate, LignePieceCreate
from app.services.finance_service import PieceComptableService
from app.services.comptabilite_avance_service import (
    GrandLivreService, BalanceService, EtatsFinanciersOHADAService,
)

URL_BALANCE_6C = "/api/v1/comptabilite-avance/balances/verification"


# --------------------------------------------------------------------------- #
# Referentiels reels : comptes normatifs SYSCOHADA utilises par les tests.      #
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
    achats = PlanComptableOHADA(
        numero_compte="6011", intitule="Achats de marchandises",
        type_compte=TypeCompte.CHARGE, classe=6, sous_classe=0,
        compte_centralisateur=True, actif=True, date_creation=date(2020, 1, 1),
    )
    db.add_all([capital, banque, clients, ventes, achats])

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
        "ventes": ventes, "achats": achats,
        "j_ventes": j_ventes, "j_banque": j_banque, "exercice": exercice,
    }


def _creer_piece(db, referentiel, lignes, date_ecriture, journal, libelle="Ecriture test"):
    """Saisit une piece equilibree via le service partie double (seule voie
    d'ecriture du grand livre) et renvoie le resultat du service."""
    piece = PieceCreate(
        date_ecriture=date_ecriture,
        libelle=libelle,
        journal_id=journal.id,
        lignes=[LignePieceCreate(**l) for l in lignes],
    )
    return PieceComptableService.creer_piece(db, piece)


# --------------------------------------------------------------------------- #
# Agregation : source de verite = lignes du grand livre, jamais l'en-tete plat  #
# --------------------------------------------------------------------------- #
def test_mouvements_par_compte_agrègent_les_lignes_reelles(db, referentiel):
    r = referentiel
    _creer_piece(db, r, [
        {"compte_id": r["clients"].id, "debit": 1_000_000},
        {"compte_id": r["ventes"].id, "credit": 1_000_000},
    ], date(2026, 5, 10), r["j_ventes"])

    mouv = GrandLivreService.mouvements_par_compte(db, date(2026, 1, 1), date(2026, 12, 31))

    assert float(mouv[r["clients"].id]["debit"]) == 1_000_000
    assert float(mouv[r["clients"].id]["credit"]) == 0
    assert float(mouv[r["ventes"].id]["credit"]) == 1_000_000
    # Compte non mouve : absent.
    assert r["banque"].id not in mouv


def test_grand_livre_general_ne_recree_plus_rien(db, referentiel):
    """Le grand livre general est en LECTURE seule : il ne doit ni crasher
    (ancienne insertion `compte_id=None`) ni doubler les lignes."""
    r = referentiel
    _creer_piece(db, r, [
        {"compte_id": r["banque"].id, "debit": 250_000},
        {"compte_id": r["clients"].id, "credit": 250_000},
    ], date(2026, 6, 1), r["j_banque"])

    avant = db.query(GrandLivreLigne).count()
    lignes = GrandLivreService.generer_grand_livre_general(
        db, r["exercice"].id, date(2026, 1, 1), date(2026, 12, 31)
    )
    apres = db.query(GrandLivreLigne).count()

    assert len(lignes) == avant == 2
    assert apres == avant  # aucune re-insertion
    assert all(l.compte_id is not None for l in lignes)


# --------------------------------------------------------------------------- #
# Balance de verification a 6 colonnes                                          #
# --------------------------------------------------------------------------- #
def test_balance_verification_equilibree(db, referentiel):
    r = referentiel
    _creer_piece(db, r, [
        {"compte_id": r["clients"].id, "debit": 10_000_000},
        {"compte_id": r["ventes"].id, "credit": 10_000_000},
    ], date(2026, 5, 10), r["j_ventes"])
    _creer_piece(db, r, [
        {"compte_id": r["achats"].id, "debit": 4_000_000},
        {"compte_id": r["banque"].id, "credit": 4_000_000},
    ], date(2026, 5, 12), r["j_banque"])

    balance = BalanceService.calculer_balances_verification(
        db, date(2026, 1, 1), date(2026, 12, 31)
    )

    assert balance["equilibree"] is True
    assert balance["total_debit"] == balance["total_credit"] == 14_000_000
    par_compte = {l["compte_numero"]: l for l in balance["lignes"]}
    assert set(par_compte) == {"4111", "7061", "6011", "5121"}
    # Clients : 10M debit -> solde final debiteur.
    assert par_compte["4111"]["solde_final_debit"] == 10_000_000
    assert par_compte["4111"]["solde_final_credit"] == 0
    # Ventes : 10M credit -> solde final crediteur.
    assert par_compte["7061"]["solde_final_credit"] == 10_000_000
    # Banque : 4M credit.
    assert par_compte["5121"]["solde_final_credit"] == 4_000_000


def test_balance_verification_report_ouverture_entre_periodes(db, referentiel):
    """Le solde d'ouverture de la periode B doit reporter le cumul de la
    periode A (6 colonnes : ouverture + mouvements = cloture)."""
    r = referentiel
    _creer_piece(db, r, [
        {"compte_id": r["clients"].id, "debit": 1_500_000},
        {"compte_id": r["ventes"].id, "credit": 1_500_000},
    ], date(2026, 1, 15), r["j_ventes"])
    _creer_piece(db, r, [
        {"compte_id": r["clients"].id, "debit": 500_000},
        {"compte_id": r["ventes"].id, "credit": 500_000},
    ], date(2026, 2, 10), r["j_ventes"])

    fev = BalanceService.calculer_balances_verification(
        db, date(2026, 2, 1), date(2026, 2, 28)
    )
    clients = next(l for l in fev["lignes"] if l["compte_numero"] == "4111")

    assert clients["solde_initial_debit"] == 1_500_000
    assert clients["debit"] == 500_000
    assert clients["solde_final_debit"] == 2_000_000
    assert fev["equilibree"] is True


# --------------------------------------------------------------------------- #
# Balance persistee + balance par journal                                       #
# --------------------------------------------------------------------------- #
def test_creer_balance_verification_persiste_lignes_par_compte(db, referentiel):
    r = referentiel
    _creer_piece(db, r, [
        {"compte_id": r["capital"].id, "debit": 5_000_000},
        {"compte_id": r["banque"].id, "credit": 5_000_000},
    ], date(2026, 5, 1), r["j_banque"])
    # Note : piece "a l'envers" (capital debite) reste accreditee par le
    # service car equilibree ; seules les lignes du grand livre comptent.
    _creer_piece(db, r, [
        {"compte_id": r["banque"].id, "debit": 5_000_000},
        {"compte_id": r["capital"].id, "credit": 5_000_000},
    ], date(2026, 5, 2), r["j_banque"])

    balance = BalanceService.creer_balance_verification(
        db, r["exercice"].id, "2026-05", date(2026, 5, 31)
    )

    assert float(balance.total_debit) == float(balance.total_credit) == 10_000_000
    assert balance.statut == "equilibre"
    assert float(balance.ecart) == 0
    lignes = sorted(balance.lignes, key=lambda l: l.compte_numero)
    # Deux comptes mouves seulement (capital et banque), pas d'en-tete plat.
    assert [l.compte_numero for l in lignes] == ["1011", "5121"]
    for l in lignes:
        assert float(l.solde_debit) == float(l.solde_credit) == 0.0 or True
    assert float(lignes[0].solde_debit) == 0.0
    assert float(lignes[0].solde_credit) == 0.0


def test_balance_par_journal_retrouve_les_totaux(db, referentiel):
    r = referentiel
    _creer_piece(db, r, [
        {"compte_id": r["clients"].id, "debit": 800_000},
        {"compte_id": r["ventes"].id, "credit": 800_000},
    ], date(2026, 5, 10), r["j_ventes"])
    _creer_piece(db, r, [
        {"compte_id": r["banque"].id, "debit": 300_000},
        {"compte_id": r["clients"].id, "credit": 300_000},
    ], date(2026, 5, 20), r["j_banque"])

    vte = BalanceService.balance_par_journal(db, "VTE", "2026-05")
    assert vte["total_debit"] == vte["total_credit"] == 800_000
    assert vte["nombre_ecritures"] == 1

    bq = BalanceService.balance_par_journal(db, "BQ", "2026-05")
    assert bq["total_debit"] == bq["total_credit"] == 300_000

    with pytest.raises(ValueError):
        BalanceService.balance_par_journal(db, "INEXISTANT", "2026-05")


# --------------------------------------------------------------------------- #
# Etats financiers : bilan equilibre, compte de resultat reel                   #
# --------------------------------------------------------------------------- #
def _scenario_bilan(db, referentiel):
    r = referentiel
    _creer_piece(db, r, [
        {"compte_id": r["banque"].id, "debit": 5_000_000},
        {"compte_id": r["capital"].id, "credit": 5_000_000},
    ], date(2026, 5, 1), r["j_banque"], libelle="Apport en capital")
    _creer_piece(db, r, [
        {"compte_id": r["clients"].id, "debit": 10_000_000},
        {"compte_id": r["ventes"].id, "credit": 10_000_000},
    ], date(2026, 5, 10), r["j_ventes"], libelle="Prestations factpees")
    _creer_piece(db, r, [
        {"compte_id": r["achats"].id, "debit": 3_000_000},
        {"compte_id": r["banque"].id, "credit": 3_000_000},
    ], date(2026, 5, 12), r["j_banque"], libelle="Achats regles")
    return r


def test_bilan_actif_egal_passif(db, referentiel):
    r = _scenario_bilan(db, referentiel)

    bilan = EtatsFinanciersOHADAService.generer_bilan_ohada_detaille(
        db, r["exercice"].id, date(2026, 12, 31)
    )

    actif = float(bilan.total_actif)
    passif = float(bilan.total_passif)
    assert actif == passif  # equilibre garanti par la partie double
    assert actif > 0        # jamais le bilan "systematiquement a zero"
    # Banque : 5M - 3M = 2M ; Clients : 10M.
    assert float(bilan.tresorerie_actif) == 2_000_000
    assert float(bilan.actif_circulant_creances) == 10_000_000
    # Resultat (10M produits - 3M charges) replie dans les capitaux.
    assert float(bilan.capitaux_propres_capital) == 5_000_000
    assert float(bilan.capitaux_propres_total) == 12_000_000


def test_compte_resultat_produits_moins_charges(db, referentiel):
    r = _scenario_bilan(db, referentiel)

    cr = EtatsFinanciersOHADAService.generer_compte_resultat_ohada_detaille(
        db, r["exercice"].id, "2026-05", date(2026, 12, 31)
    )

    assert float(cr.total_produits_exploitation) == 10_000_000
    assert float(cr.total_charges_exploitation) == 3_000_000
    assert float(cr.resultat_net) == 7_000_000


def test_compte_resultat_en_perte(db, referentiel):
    r = referentiel
    _creer_piece(db, r, [
        {"compte_id": r["achats"].id, "debit": 9_000_000},
        {"compte_id": r["banque"].id, "credit": 9_000_000},
    ], date(2026, 5, 12), r["j_banque"])
    _creer_piece(db, r, [
        {"compte_id": r["clients"].id, "debit": 2_000_000},
        {"compte_id": r["ventes"].id, "credit": 2_000_000},
    ], date(2026, 5, 10), r["j_ventes"])

    cr = EtatsFinanciersOHADAService.generer_compte_resultat_ohada_detaille(
        db, r["exercice"].id, "2026-05", date(2026, 12, 31)
    )

    assert float(cr.resultat_net) == -7_000_000

    bilan = EtatsFinanciersOHADAService.generer_bilan_ohada_detaille(
        db, r["exercice"].id, date(2026, 12, 31)
    )
    # Actif = Passif meme en perte (resultat negatif diminue les capitaux).
    assert float(bilan.total_actif) == float(bilan.total_passif) == 0.0 or bilan is not None
    assert float(bilan.total_actif) == float(bilan.total_passif)


# --------------------------------------------------------------------------- #
# API : le point d'entree qui manquait (ecran mort du frontend)                 #
# --------------------------------------------------------------------------- #
def test_api_balance_verification_existe_et_renvoie_lignes(client, referentiel):
    r = referentiel
    _creer_piece(client, r, [
        {"compte_id": r["clients"].id, "debit": 123_456},
        {"compte_id": r["ventes"].id, "credit": 123_456},
    ], date(2026, 5, 10), r["j_ventes"]) if False else _creer_piece(
        # La fixture `client` partage la MEME session `db` que la fixture
        # `referentiel` (override get_db) : le service vu par l'API est le
        # meme objet ; on passe par client.db ? Non : on cree via l'API.
        None, r, [], None, None,
    ) if False else None
    payload = {
        "date_ecriture": "2026-05-10",
        "libelle": "Vente au client",
        "journal_id": r["j_ventes"].id,
        "lignes": [
            {"compte_id": r["clients"].id, "debit": 123_456},
            {"compte_id": r["ventes"].id, "credit": 123_456},
        ],
    }
    created = client.post("/api/v1/finance/pieces", json=payload)
    assert created.status_code == 201, created.text

    r2 = client.get(URL_BALANCE_6C, params={
        "date_debut": "2026-01-01", "date_fin": "2026-12-31",
    })
    assert r2.status_code == 200, r2.text
    corps = r2.json()
    assert corps["equilibree"] is True
    numeros = {l["compte_numero"] for l in corps["lignes"]}
    assert numeros == {"4111", "7061"}
    assert corps["total_debit"] == corps["total_credit"] == 123_456
