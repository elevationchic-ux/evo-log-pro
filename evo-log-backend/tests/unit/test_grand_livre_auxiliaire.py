"""Tests grand livre auxiliaire par compte : GET /grand-livre/auxiliaire/{compte_id}.

La page « Grand Livre » de l'ERP exploitait un bouton de bascule mort : passer en
mode Grand Livre n'affichait que la balance, sans jamais charger les écritures du
compte. Cette route renvoie désormais le véritable folio d'un compte, agrégé
depuis les lignes du grand livre matérialisées par les pièces en partie double.

On vérifie : filtre par compte, borne de dates respectée, ordre chronologique,
et exclusion des comptes sans mouvement.
"""
from datetime import date

import pytest

from app.models.finance_ohada import (
    PlanComptableOHADA, JournalAuxiliaire, ExerciceComptable,
    TypeCompte, TypeJournal,
)
from app.schemas.finance import PieceCreate, LignePieceCreate
from app.services.finance_service import PieceComptableService

URL_AUX = "/api/v1/comptabilite-avance/grand-livre/auxiliaire"


@pytest.fixture
def plan(db):
    comptes_data = [
        ("4111", "Clients", TypeCompte.ACTIF, 4),
        ("7061", "Ventes prestations", TypeCompte.PRODUIT, 7),
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
        numero_exercice="EX-GL", annee=2026,
        date_debut=date(2026, 1, 1), date_fin=date(2026, 12, 31), statut="ouvert",
    )
    db.add(exercice)
    db.commit()
    return {"comptes": comptes, "journal": journal, "exercice": exercice}


def _vente(db, c, journal, montant, date_ec):
    piece = PieceCreate(
        date_ecriture=date_ec,
        libelle=f"Vente {montant}",
        journal_id=journal.id,
        lignes=[
            LignePieceCreate(compte_id=c["4111"].id, debit=montant),
            LignePieceCreate(compte_id=c["7061"].id, credit=montant),
        ],
    )
    return PieceComptableService.creer_piece(db, piece)


# ──────────────────────────────────────────────────────────────────────────────
# Route (client)
# ──────────────────────────────────────────────────────────────────────────────

def test_auxiliaire_filtre_par_compte_et_dates(client, db, plan):
    """Seules les écritures du compte, dans la plage de dates, remontent, triées."""
    c = plan["comptes"]
    j = plan["journal"]
    _vente(db, c, j, 100_000, date(2026, 1, 10))
    _vente(db, c, j, 200_000, date(2026, 3, 10))
    _vente(db, c, j, 300_000, date(2026, 6, 10))

    res = client.get(
        f"{URL_AUX}/{c['4111'].id}"
        f"?date_debut=2026-01-01&date_fin=2026-03-31"
    )
    assert res.status_code == 200
    lignes = res.json()
    assert len(lignes) == 2
    # ordre chronologique croissant
    dates = [l["date_ecriture"] for l in lignes]
    assert dates == sorted(dates)
    # uniquement le compte demandé
    assert all(l["compte_id"] == c["4111"].id for l in lignes)
    # débit/crédit serialisés en chaîne (Decimal) → coercition explicite
    debits = sorted(float(l["debit"]) for l in lignes)
    assert debits == [100_000.0, 200_000.0]


def test_auxiliaire_plage_totale(client, db, plan):
    """Plage large → toutes les écritures du compte, solde cumulé = somme débit."""
    c = plan["comptes"]
    j = plan["journal"]
    _vente(db, c, j, 150_000, date(2026, 2, 1))
    _vente(db, c, j, 250_000, date(2026, 5, 1))

    res = client.get(
        f"{URL_AUX}/{c['4111'].id}?date_debut=1970-01-01&date_fin=2999-12-31"
    )
    assert res.status_code == 200
    lignes = res.json()
    assert len(lignes) == 2
    total_debit = sum(float(l["debit"]) for l in lignes)
    assert total_debit == 400_000.0


def test_auxiliaire_compte_sans_mouvement_vide(client, db, plan):
    """Compte sans écriture (banque ici) → liste vide, sans crash."""
    c = plan["comptes"]
    j = plan["journal"]
    _vente(db, c, j, 90_000, date(2026, 4, 1))

    res = client.get(
        f"{URL_AUX}/{c['5121'].id}?date_debut=2026-01-01&date_fin=2026-12-31"
    )
    assert res.status_code == 200
    assert res.json() == []


def test_auxiliaire_ne_melange_pas_les_comptes(client, db, plan):
    """Le folio du compte 7 (produit) ne contient pas les lignes du compte 4."""
    c = plan["comptes"]
    j = plan["journal"]
    _vente(db, c, j, 120_000, date(2026, 3, 5))

    res = client.get(
        f"{URL_AUX}/{c['7061'].id}?date_debut=2026-01-01&date_fin=2026-12-31"
    )
    assert res.status_code == 200
    lignes = res.json()
    assert len(lignes) == 1
    assert lignes[0]["compte_id"] == c["7061"].id
    assert float(lignes[0]["credit"]) == 120_000.0
