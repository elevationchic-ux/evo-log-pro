"""Tests lettrage réel : rapprochement sur les lignes du grand livre.

L'ancienne implémentation filtrait l'en-tête plat `ecritures_comptables_ohada`
dont `compte_id` est désormais NULL (il porte les totaux de la pièce) : le
lettrage ne voyait donc AUCUNE écriture réelle, et lorsqu'il en voyait il
 lumpait tout dans un lettrage unique sans vérifier l'équilibre.

Le lettrage opère désormais sur `grand_livre_lignes` (un mouvement = une ligne
d'UN compte), exclut ce qui est déjà soldé (idempotence), apparie en FIFO les
montants égaux (auto) et impose solde nul sur la sélection (manuel). Aucune
donnée n'est inventée : on rapproche l'état réel du grand livre.
"""
from datetime import date

import pytest

from app.models.finance_ohada import (
    PlanComptableOHADA, JournalAuxiliaire, ExerciceComptable, GrandLivreLigne,
    TypeCompte, TypeJournal, StatutLettrage, Lettrage,
)
from app.schemas.finance import PieceCreate, LignePieceCreate
from app.services.finance_service import PieceComptableService
from app.services.comptabilite_avance_service import LettrageService

URL_SUGG = "/api/v1/comptabilite-avance/lettrage/suggestions"
URL_AUTO = "/api/v1/comptabilite-avance/lettrage/automatique"
URL_MAN = "/api/v1/comptabilite-avance/lettrage/manuel"
URL_LIST = "/api/v1/comptabilite-avance/lettrages"


@pytest.fixture
def plan(db):
    comptes_data = [
        ("4111", "Clients", TypeCompte.ACTIF, 4),
        ("5121", "Banque", TypeCompte.ACTIF, 5),
        ("7061", "Ventes prestations", TypeCompte.PRODUIT, 7),
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

    jventes = JournalAuxiliaire(
        code_journal="VTE", nom_journal="Ventes",
        type_journal=TypeJournal.VENTES, statut="actif",
    )
    jbanque = JournalAuxiliaire(
        code_journal="BNQ", nom_journal="Banque",
        type_journal=TypeJournal.BANQUE, statut="actif",
    )
    db.add_all([jventes, jbanque])
    exercice = ExerciceComptable(
        numero_exercice="EX-LET", annee=2026,
        date_debut=date(2026, 1, 1), date_fin=date(2026, 12, 31), statut="ouvert",
    )
    db.add(exercice)
    db.commit()
    return {"comptes": comptes, "jventes": jventes, "jbanque": jbanque, "exercice": exercice}


def _vente(db, c, journal, montant, date_ec):
    """Facture client : débit 4111 / crédit 7061."""
    piece = PieceCreate(
        date_ecriture=date_ec, libelle=f"Vente {montant}", journal_id=journal.id,
        lignes=[
            LignePieceCreate(compte_id=c["4111"].id, debit=montant),
            LignePieceCreate(compte_id=c["7061"].id, credit=montant),
        ],
    )
    return PieceComptableService.creer_piece(db, piece)


def _reglement(db, c, journal, montant, date_ec):
    """Encaissement : débit 5121 / crédit 4111 (solde une facture)."""
    piece = PieceCreate(
        date_ecriture=date_ec, libelle=f"Règlement {montant}", journal_id=journal.id,
        lignes=[
            LignePieceCreate(compte_id=c["5121"].id, debit=montant),
            LignePieceCreate(compte_id=c["4111"].id, credit=montant),
        ],
    )
    return PieceComptableService.creer_piece(db, piece)


def _lignes(db, compte_id):
    return (
        db.query(GrandLivreLigne)
        .filter(GrandLivreLigne.compte_id == compte_id)
        .order_by(GrandLivreLigne.date_ecriture.asc(), GrandLivreLigne.id.asc())
        .all()
    )


# ──────────────────────────────────────────────────────────────────────────────
# Logique service (db)
# ──────────────────────────────────────────────────────────────────────────────

def test_suggestion_list_items_ouverts(db, plan):
    """La suggestion renvoie les lignes débit ET crédit réelles, solde ouvert dérivé."""
    c, jv, jb = plan["comptes"], plan["jventes"], plan["jbanque"]
    _vente(db, c, jv, 100_000, date(2026, 1, 10))
    _reglement(db, c, jb, 100_000, date(2026, 2, 10))

    res = LettrageService.suggestion_lettrage(db, c["4111"].id)
    assert res["compte_numero"] == "4111"
    assert len(res["lignes"]) == 2
    assert float(res["total_debit"]) == 100_000.0
    assert float(res["total_credit"]) == 100_000.0
    assert float(res["solde_ouvert"]) == 0.0


def test_lettrage_automatique_fifo_apparie_montants_egaux(db, plan):
    """FIFO : une facture et son règlement de même montant sont soldées ensemble."""
    c, jv, jb = plan["comptes"], plan["jventes"], plan["jbanque"]
    _vente(db, c, jv, 100_000, date(2026, 1, 10))
    _reglement(db, c, jb, 100_000, date(2026, 2, 10))

    lettrage = LettrageService.lettrage_automatique(db, c["4111"].id, date(2026, 2, 11))
    assert float(lettrage.montant_lettre) == 100_000.0
    assert lettrage.type_lettrage.value == "automatique"

    lignes = _lignes(db, c["4111"].id)
    assert all(l.statut_lettrage == StatutLettrage.LETTRE for l in lignes)
    assert all(l.lettrage_id == lettrage.id for l in lignes)


def test_lettrage_automatique_refuse_si_aucune_paire(db, plan):
    """Sans écriture débit/crédit de même montant, on refuse plutôt que de forcer."""
    c, jv, jb = plan["comptes"], plan["jventes"], plan["jbanque"]
    _vente(db, c, jv, 100_000, date(2026, 1, 10))
    _reglement(db, c, jb, 40_000, date(2026, 2, 10))  # montant différent

    with pytest.raises(ValueError):
        LettrageService.lettrage_automatique(db, c["4111"].id, date(2026, 2, 11))
    # rien n'a été soldé
    assert all(l.lettrage_id is None for l in _lignes(db, c["4111"].id))


def test_lettrage_automatique_idempotent(db, plan):
    """Relancer l'auto-lettrage après succès ne re-lettre rien (items déjà soldés)."""
    c, jv, jb = plan["comptes"], plan["jventes"], plan["jbanque"]
    _vente(db, c, jv, 100_000, date(2026, 1, 10))
    _reglement(db, c, jb, 100_000, date(2026, 2, 10))

    LettrageService.lettrage_automatique(db, c["4111"].id, date(2026, 2, 11))
    with pytest.raises(ValueError):
        LettrageService.lettrage_automatique(db, c["4111"].id, date(2026, 2, 12))


def test_lettrage_manuel_exige_solde_nul(db, plan):
    """Sélection déséquilibrée → refusée avec l'écart ; sélection soldée → acceptée."""
    c, jv, jb = plan["comptes"], plan["jventes"], plan["jbanque"]
    _vente(db, c, jv, 100_000, date(2026, 1, 10))
    _reglement(db, c, jb, 100_000, date(2026, 2, 10))
    lignes_ids = [l.id for l in _lignes(db, c["4111"].id)]

    # Une seule ligne → non soldée → refus
    with pytest.raises(ValueError):
        LettrageService.lettrage_manuel(
            db, c["4111"].id, [lignes_ids[0]], date(2026, 2, 11), "TEST"
        )

    # Les deux lignes → solde nul → accepté
    lettrage = LettrageService.lettrage_manuel(
        db, c["4111"].id, lignes_ids, date(2026, 2, 11), "TEST", reference="CHK-01"
    )
    assert float(lettrage.montant_lettre) == 100_000.0
    assert lettrage.reference_lettrage == "CHK-01"
    assert all(l.statut_lettrage == StatutLettrage.LETTRE for l in _lignes(db, c["4111"].id))


def test_annulation_relibere_lignes(db, plan):
    """Annuler un lettrage redonne un statut NON_LETRE et décroche lettrage_id."""
    c, jv, jb = plan["comptes"], plan["jventes"], plan["jbanque"]
    _vente(db, c, jv, 100_000, date(2026, 1, 10))
    _reglement(db, c, jb, 100_000, date(2026, 2, 10))
    lettrage = LettrageService.lettrage_automatique(db, c["4111"].id, date(2026, 2, 11))

    LettrageService.annuler_lettrage(db, lettrage.id, "Erreur de rapprochement")

    for l in _lignes(db, c["4111"].id):
        assert l.statut_lettrage == StatutLettrage.NON_LETRE
        assert l.lettrage_id is None
    db.refresh(lettrage)
    assert lettrage.date_annulation is not None


# ──────────────────────────────────────────────────────────────────────────────
# Endpoints (client)
# ──────────────────────────────────────────────────────────────────────────────

def test_endpoint_suggestions(client, db, plan):
    c, jv = plan["comptes"], plan["jventes"]
    _vente(db, c, jv, 100_000, date(2026, 1, 10))

    res = client.get(f"{URL_SUGG}/{c['4111'].id}")
    assert res.status_code == 200
    body = res.json()
    assert body["compte_numero"] == "4111"
    assert len(body["lignes"]) == 1


def test_endpoint_automatique(client, db, plan):
    c, jv, jb = plan["comptes"], plan["jventes"], plan["jbanque"]
    _vente(db, c, jv, 100_000, date(2026, 1, 10))
    _reglement(db, c, jb, 100_000, date(2026, 2, 10))

    res = client.post(f"{URL_AUTO}/{c['4111'].id}?date_reference=2026-02-11")
    assert res.status_code == 200
    assert float(res.json()["montant_lettre"]) == 100_000.0

    listing = client.get(f"{URL_LIST}?compte_id={c['4111'].id}")
    assert listing.status_code == 200
    assert len(listing.json()) == 1


def test_endpoint_automatique_refus_sans_paire(client, db, plan):
    c, jv = plan["comptes"], plan["jventes"]
    _vente(db, c, jv, 100_000, date(2026, 1, 10))  # facture seule, jamais réglée

    res = client.post(f"{URL_AUTO}/{c['4111'].id}?date_reference=2026-01-11")
    assert res.status_code == 400


def test_endpoint_manuel(client, db, plan):
    c, jv, jb = plan["comptes"], plan["jventes"], plan["jbanque"]
    _vente(db, c, jv, 100_000, date(2026, 1, 10))
    _reglement(db, c, jb, 100_000, date(2026, 2, 10))
    lignes_ids = [l.id for l in _lignes(db, c["4111"].id)]

    res = client.post(URL_MAN, json={
        "compte_id": c["4111"].id,
        "lignes_ids": lignes_ids,
        "date_lettrage": "2026-02-11",
        "effectue_par": "AGENT",
        "reference": "VIR-42",
    })
    assert res.status_code == 200
    assert float(res.json()["montant_lettre"]) == 100_000.0


def test_endpoint_manuel_desequilibre_rejete(client, db, plan):
    c, jv, jb = plan["comptes"], plan["jventes"], plan["jbanque"]
    _vente(db, c, jv, 100_000, date(2026, 1, 10))
    _reglement(db, c, jb, 100_000, date(2026, 2, 10))
    lignes_ids = [l.id for l in _lignes(db, c["4111"].id)]

    # une seule ligne → déséquilibré → rejet 400
    res = client.post(URL_MAN, json={
        "compte_id": c["4111"].id,
        "lignes_ids": [lignes_ids[0]],
        "date_lettrage": "2026-02-11",
        "effectue_par": "AGENT",
    })
    assert res.status_code == 400
