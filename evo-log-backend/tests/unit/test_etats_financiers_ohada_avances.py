"""Tests des etats financiers et modules ajoutes au chantier SYSCOHADA :

  * TFT (Tableau des Flux de Tresorerie) : les trois flux somment a la
    variation de tresorerie, qui reconcilie les comptes de classe 5.
  * SIG (Situation Globale des Entreprises) : CA, EBE, CAF, resultat et
    tresorerie calcules sur les lignes reelles du grand livre.
  * Immobilisations amortissables : dotation lineaire, echeancier, et
    ecriture de dotation validee 681/28x idempotente par periode.
  * Liasse fiscale CEMAC : consolide les declarations TVA et IS reelles.

Gabarit identique a test_comptabilite_sortie : les etats sont calcules
depuis `grand_livre_lignes`, jamais depuis des soldes inventes.
"""
from datetime import date
from decimal import Decimal

import pytest

from app.models.finance_ohada import (
    PlanComptableOHADA, JournalAuxiliaire, ExerciceComptable,
    GrandLivreLigne, TVADeclarable, ISDeclarable,
    RegimeTVA, RegimeIS, StatutTaxe, TypeCompte, TypeJournal,)
from app.schemas.finance import PieceCreate, LignePieceCreate
from app.services.finance_service import PieceComptableService
from app.services.comptabilite_avance_service import (
    EtatsFinanciersOHADAService, ImmobilisationService, LiasseFiscaleService,)


@pytest.fixture
def referentiel(db):
    def compte(numero, intitule, nature, classe):
        return PlanComptableOHADA(
            numero_compte=numero, intitule=intitule, type_compte=nature,
            classe=classe, sous_classe=0, compte_centralisateur=True,
            actif=True, date_creation=date(2020, 1, 1),)

    comptes = [
        compte("1011", "Capital", TypeCompte.PASSIF, 1),
        compte("2151", "Materiel", TypeCompte.ACTIF, 2),
        compte("2815", "Amortissements materiel", TypeCompte.ACTIF, 2),
        compte("4111", "Clients", TypeCompte.ACTIF, 4),
        compte("5121", "Banque", TypeCompte.ACTIF, 5),
        compte("6011", "Achats", TypeCompte.CHARGE, 6),
        compte("6815", "Dotations aux amortissements", TypeCompte.CHARGE, 6),
        compte("7061", "Prestations de services", TypeCompte.PRODUIT, 7),
    ]
    db.add_all(comptes)
    j = JournalAuxiliaire(
        code_journal="VTE", nom_journal="Journal des Ventes",
        type_journal=TypeJournal.VENTES, statut="actif",)
    db.add(j)
    exercice = ExerciceComptable(
        numero_exercice="EX-2026", annee=2026,
        date_debut=date(2026, 1, 1), date_fin=date(2026, 12, 31),
        statut="ouvert",)
    db.add(exercice)
    db.commit()
    return {"comptes": {c.numero_compte: c for c in comptes},
            "journal": j, "exercice": exercice}


def _piece(db, r, lignes, date_ecriture, libelle="Ecriture test"):
    return PieceComptableService.creer_piece(db, PieceCreate(
        date_ecriture=date_ecriture, libelle=libelle,
        journal_id=r["journal"].id,
        lignes=[LignePieceCreate(**l) for l in lignes],))


def _scenario(db, r):
    """Capital 5M, vente 10M, achats 3M : resultat +7M, treso +2M."""
    c = r["comptes"]
    _piece(db, r, [
        {"compte_id": c["5121"].id, "debit": 5_000_000},
        {"compte_id": c["1011"].id, "credit": 5_000_000},
    ], date(2026, 1, 5), libelle="Apport")
    _piece(db, r, [
        {"compte_id": c["4111"].id, "debit": 10_000_000},
        {"compte_id": c["7061"].id, "credit": 10_000_000},
    ], date(2026, 5, 10), libelle="Vente")
    _piece(db, r, [
        {"compte_id": c["6011"].id, "debit": 3_000_000},
        {"compte_id": c["5121"].id, "credit": 3_000_000},
    ], date(2026, 5, 12), libelle="Achats")


# --------------------------------------------------------------------------- #
# TFT : coherence interne des trois flux #
# --------------------------------------------------------------------------- #
def test_tft_les_trois_flux_somment_a_la_variation(db, referentiel):
    r = referentiel
    _scenario(db, r)

    tft = EtatsFinanciersOHADAService.generer_tft(
        db, r["exercice"].id, date(2026, 12, 31))

    somme = (float(tft.flux_exploitation) + float(tft.flux_investissement)
             + float(tft.flux_financement))
    assert abs(somme - float(tft.variation_tresorerie)) < 0.01
 # Trésorerie de fin = variation + début, par construction du service.
    assert abs(float(tft.tresorerie_fin) - float(tft.tresorerie_debut)
               - float(tft.variation_tresorerie)) < 0.01


def test_tft_reflète_les_mouvements_reels_de_classe_5(db, referentiel):
    r = referentiel
    _scenario(db, r)

    tft = EtatsFinanciersOHADAService.generer_tft(
        db, r["exercice"].id, date(2026, 12, 31))

 # Banque : +5M - 3M = 2M debiteur -> tresorerie positive +2M.
    assert float(tft.tresorerie_fin) == 2_000_000


# --------------------------------------------------------------------------- #
# SIG : indicateurs calcules sur le grand livre #
# --------------------------------------------------------------------------- #
def test_sig_indicateurs_reels(db, referentiel):
    r = referentiel
    _scenario(db, r)

    sig = EtatsFinanciersOHADAService.generer_sig(
        db, r["exercice"].id, date(2026, 12, 31), Decimal("12"))

    assert float(sig.chiffre_affaires) == 10_000_000
    assert float(sig.resultat_net) == 7_000_000
    assert float(sig.masse_salariale) == 0
    assert float(sig.effectif_moyen) == 12
    assert float(sig.tresorerie_nette) == 2_000_000


# --------------------------------------------------------------------------- #
# Immobilisations : dotation lineaire + ecriture comptable idempotente #
# --------------------------------------------------------------------------- #
def _immobilisation(db, r, **kw):
    data = dict(
        numero_immobilisation="IMM-001",
        designation="Chariot elevateur",
        date_acquisition=date(2026, 1, 15),
        valeur_acquisition=Decimal("2_400_000"),
        valeur_residuelle=Decimal("0"),
        duree_mois=48,
        compte_immobilisation="2151",
        compte_amortissement="2815",
        compte_dotation="6815",
    )
    data.update(kw)
    return ImmobilisationService.creer_immobilisation(db, data)


def test_dotation_mensuelle_lineaire_et_echeancier(db, referentiel):
    imm = _immobilisation(db, referentiel)

    dotation = ImmobilisationService.dotation_mensuelle(imm)
    assert dotation == Decimal("50000.00")  # 2 400 000 / 48

    echeancier = ImmobilisationService.tableau_echeancier(imm)
    assert len(echeancier) == 48
    assert echeancier[0]["periode"] == "2026-01"
    assert echeancier[-1]["net_comptable"] == 0.0


def test_ecriture_amortissement_equilibree_et_unique(db, referentiel):
    r = referentiel
    c = r["comptes"]
    imm = _immobilisation(db, r)

    res = ImmobilisationService.generer_ecriture_amortissement(
        db, imm.id, date(2026, 2, 28), "2026-02")

    assert res["montant"] == 50_000.0
    lignes = db.query(GrandLivreLigne).filter(
        GrandLivreLigne.periode == "2026-02").all()
    assert len(lignes) == 2
    debit = next(l for l in lignes if l.compte_id == c["6815"].id)
    credit = next(l for l in lignes if l.compte_id == c["2815"].id)
    assert float(debit.debit) == 50_000 and float(debit.credit) == 0
    assert float(credit.credit) == 50_000 and float(credit.debit) == 0

 # Idempotence : une seconde dotation sur la meme periode est refusee.
    with pytest.raises(ValueError):
        ImmobilisationService.generer_ecriture_amortissement(
            db, imm.id, date(2026, 2, 28), "2026-02")


# --------------------------------------------------------------------------- #
# Liasse fiscale CEMAC : consolidation des declarations reelles #
# --------------------------------------------------------------------------- #
def test_liasse_fiscale_consolide_tva_et_is(db, referentiel):
    db.add(TVADeclarable(
        numero_declaration="TVA-2026-01", periode="2026-01",
        regime_tva=RegimeTVA.NORMAL, base_imposable=10_000_000,
        tva_collectee=1_900_000, tva_deductible=800_000,
        tva_a_payer=1_100_000, statut=StatutTaxe.DUE,))
    db.add(TVADeclarable(
        numero_declaration="TVA-2026-02", periode="2026-02",
        regime_tva=RegimeTVA.NORMAL, base_imposable=5_000_000,
        tva_collectee=950_000, tva_deductible=300_000,
        tva_a_payer=650_000, statut=StatutTaxe.PAYEE, montant_paye=650_000))
    db.add(ISDeclarable(
        numero_declaration="IS-2026", annee=2026, regime_is=RegimeIS.NORMAL,
        benefice_fiscal=8_000_000, is_du=2_640_000, is_a_payer=2_640_000,
        statut=StatutTaxe.DUE,))
    db.commit()

    liasse = LiasseFiscaleService.generer_liasse(db, 2026)

    assert liasse.annee == 2026
    assert liasse.nombre_declarations_tva == 2
    assert float(liasse.total_tva_collectee) == 2_850_000
    assert float(liasse.total_tva_a_payer) == 1_750_000
    assert float(liasse.total_is) == 2_640_000
    assert float(liasse.total_impots) == 4_390_000
    assert liasse.detail_json and "TVA-2026-01" in liasse.detail_json


def test_liasse_vide_reste_honnete(db, referentiel):
    """Sans declaration : la liasse affiche des zeros, pas de montants inventes."""
    liasse = LiasseFiscaleService.generer_liasse(db, 2026)

    assert float(liasse.total_impots) == 0
    assert liasse.nombre_declarations_tva == 0
    assert liasse.statut == "brouillon"
