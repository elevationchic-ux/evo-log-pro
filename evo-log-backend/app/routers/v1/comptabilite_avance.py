"""Router API pour la comptabilité avancée - Journaux, lettrage, grand livre, balance"""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import date

from app.core.database import get_db
from app.core.permissions import require_perm
from app.models.user import User
from app.schemas.comptabilite_avance import (
    JournalAuxiliaireCreate, JournalAuxiliaireUpdate, JournalAuxiliaireResponse,
    LigneJournalCreate, LigneJournalResponse,
    LettrageCreate, LettrageUpdate, LettrageResponse, LettrageManuelRequest,
    EcritureLettreeCreate, EcritureLettreeResponse,
    GrandLivreLigneResponse, GrandLivreGenerateRequest, HistoriqueCompteResponse,
    BalanceVerificationCreate, BalanceVerificationResponse, LigneBalanceResponse,
    BalanceResponse, BalanceParJournalResponse,
    BilanOHADADetailleCreate, BilanOHADADetailleResponse,
    CompteResultatOHADADetailleCreate, CompteResultatOHADADetailleResponse,
    TAFIRECreate, TAFIREResponse,
    AnnexesOHDACreate, AnnexesOHDAResponse, AnnexesGenererRequest,
    ClotureMensuelleRequest, ClotureMensuelleResponse,
    ClotureAnnuelleRequest, ClotureAnnuelleResponse,
    ReportANouveauRequest, ReportANouveauResponse,
    AffectationResultatRequest, AffectationResultatResponse,
    PeriodeClosingItem, EtatsPeriodesResponse
)
from app.services.comptabilite_avance_service import (
    JournalAuxiliaireService, LettrageService, GrandLivreService, BalanceService, EtatsFinanciersOHADAService, ClotureService
)
from app.models.finance_ohada import JournalAuxiliaire, Lettrage, GrandLivreLigne, BalanceVerification, BilanOHADADetaille, CompteResultatOHADADetaille, TAFIRE, AnnexesOHADA

router = APIRouter(tags=["Comptabilité Avancée"])  # monte sur /api/v1/comptabilite-avance par main.py


# ============ JOURNAUX AUXILIAIRES ============

@router.post("/journaux", response_model=JournalAuxiliaireResponse, status_code=status.HTTP_201_CREATED)
def creer_journal_auxiliaire(
    journal: JournalAuxiliaireCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_perm("comptabilite.journal.create"))
):
    """Créer un journal auxiliaire"""
    from app.models.finance_ohada import TypeJournal
    
    service_journal = JournalAuxiliaireService.creer_journal_auxiliaire(
        db,
        journal.code_journal,
        journal.nom_journal,
        TypeJournal(journal.type_journal),
        journal.compte_centralisateur,
        journal.description
    )
    return service_journal


@router.get("/journaux", response_model=List[JournalAuxiliaireResponse])
def lister_journaux(
    db: Session = Depends(get_db),
    current_user: User = Depends(require_perm("comptabilite.journal.read"))
):
    """Lister tous les journaux auxiliaires"""
    return db.query(JournalAuxiliaire).all()


@router.get("/journaux/{journal_id}", response_model=JournalAuxiliaireResponse)
def obtenir_journal(
    journal_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_perm("comptabilite.journal.read"))
):
    """Obtenir un journal auxiliaire par ID"""
    journal = db.query(JournalAuxiliaire).filter(JournalAuxiliaire.id == journal_id).first()
    if not journal:
        raise HTTPException(status_code=404, detail="Journal non trouvé")
    return journal


@router.put("/journaux/{journal_id}", response_model=JournalAuxiliaireResponse)
def modifier_journal(
    journal_id: int,
    journal_update: JournalAuxiliaireUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_perm("comptabilite.journal.modify"))
):
    """Modifier un journal auxiliaire"""
    journal = db.query(JournalAuxiliaire).filter(JournalAuxiliaire.id == journal_id).first()
    if not journal:
        raise HTTPException(status_code=404, detail="Journal non trouvé")
    
    for field, value in journal_update.model_dump(exclude_unset=True).items():
        setattr(journal, field, value)
    
    db.commit()
    db.refresh(journal)
    return journal


@router.post("/journaux/initialiser", response_model=List[JournalAuxiliaireResponse])
def initialiser_tous_les_journaux(
    db: Session = Depends(get_db),
    current_user: User = Depends(require_perm("comptabilite.journal.create"))
):
    """Initialiser tous les journaux auxiliaires standards"""
    return JournalAuxiliaireService.initialiser_tous_les_journaux(db)


# ============ LETTRAGE ============

@router.post("/lettrage/automatique/{compte_id}", response_model=LettrageResponse)
def lettrage_automatique(
    compte_id: int,
    date_reference: date,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_perm("comptabilite.lettrage.modify"))
):
    """Lettrage automatique des écritures d'un compte"""
    try:
        lettrage = LettrageService.lettrage_automatique(db, compte_id, date_reference)
        return lettrage
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.post("/lettrage/manuel", response_model=LettrageResponse)
def lettrage_manuel(
    request: LettrageManuelRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_perm("comptabilite.lettrage.modify"))
):
    """Lettrage manuel d'écritures sélectionnées"""
    try:
        lettrage = LettrageService.lettrage_manuel(
            db,
            request.compte_id,
            request.ecritures_ids,
            request.date_lettrage,
            request.effectue_par,
            request.reference
        )
        return lettrage
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.post("/lettrage/{lettrage_id}/annuler", response_model=LettrageResponse)
def annuler_lettrage(
    lettrage_id: int,
    motif: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_perm("comptabilite.lettrage.modify"))
):
    """Annuler un lettrage"""
    try:
        lettrage = LettrageService.annuler_lettrage(db, lettrage_id, motif)
        return lettrage
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/lettrage/suggestions/{compte_id}")
def suggestion_lettrage(
    compte_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_perm("comptabilite.lettrage.read"))
):
    """Suggérer des écritures à lettrer"""
    return LettrageService.suggestion_lettrage(db, compte_id)


@router.get("/lettrages", response_model=List[LettrageResponse])
def lister_lettrages(
    compte_id: int = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_perm("comptabilite.lettrage.read"))
):
    """Lister les lettrages"""
    query = db.query(Lettrage)
    if compte_id:
        query = query.filter(Lettrage.compte_id == compte_id)
    return query.all()


# ============ GRAND LIVRE ============

@router.post("/grand-livre/generer", response_model=List[GrandLivreLigneResponse])
def generer_grand_livre(
    request: GrandLivreGenerateRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_perm("comptabilite.grand_livre.read"))
):
    """Générer le grand livre général pour une période"""
    lignes = GrandLivreService.generer_grand_livre_general(
        db,
        request.exercice_id,
        request.date_debut,
        request.date_fin
    )
    return lignes


@router.get("/grand-livre/auxiliaire/{compte_id}", response_model=List[GrandLivreLigneResponse])
def grand_livre_auxiliaire(
    compte_id: int,
    date_debut: date,
    date_fin: date,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_perm("comptabilite.grand_livre.read"))
):
    """Générer le grand livre auxiliaire pour un compte"""
    lignes = GrandLivreService.grand_livre_auxiliaire(db, compte_id, date_debut, date_fin)
    return lignes


@router.get("/grand-livre/historique/{compte_id}", response_model=HistoriqueCompteResponse)
def historique_compte(
    compte_id: int,
    periode: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_perm("comptabilite.grand_livre.read"))
):
    """Obtenir l'historique complet d'un compte pour une période"""
    return GrandLivreService.historique_compte(db, compte_id, periode)


# ============ BALANCE ============

@router.post("/balance/creer", response_model=BalanceResponse)
def creer_balance_verification(
    request: BalanceVerificationCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_perm("comptabilite.balance.read"))
):
    """Créer une balance de vérification"""
    balance = BalanceService.creer_balance_verification(
        db,
        request.exercice_id,
        request.periode,
        request.date_balance
    )
    
    # Récupérer les lignes
    lignes = db.query(LigneBalance).filter(LigneBalance.balance_id == balance.id).all()
    
    return BalanceResponse(
        **balance.__dict__,
        lignes=lignes
    )


@router.get("/balance/{balance_id}", response_model=BalanceResponse)
def obtenir_balance(
    balance_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_perm("comptabilite.balance.read"))
):
    """Obtenir une balance de vérification par ID"""
    balance = db.query(BalanceVerification).filter(BalanceVerification.id == balance_id).first()
    if not balance:
        raise HTTPException(status_code=404, detail="Balance non trouvée")
    
    lignes = db.query(LigneBalance).filter(LigneBalance.balance_id == balance_id).all()
    
    return BalanceResponse(
        **balance.__dict__,
        lignes=lignes
    )


@router.get("/balance/journal/{journal_code}", response_model=BalanceParJournalResponse)
def balance_par_journal(
    journal_code: str,
    periode: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_perm("comptabilite.balance.read"))
):
    """Balance par journal"""
    return BalanceService.balance_par_journal(db, journal_code, periode)


@router.get("/balances", response_model=List[BalanceVerificationResponse])
def lister_balances(
    exercice_id: int = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_perm("comptabilite.balance.read"))
):
    """Lister les balances de vérification"""
    query = db.query(BalanceVerification)
    if exercice_id:
        query = query.filter(BalanceVerification.exercice_id == exercice_id)
    return query.all()


@router.get("/balances/verification")
def balances_verification(
    date_debut: date = None,
    date_fin: date = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_perm("comptabilite.balance.read"))
):
    """Balance de verification a 6 colonnes, calculee en direct sur le grand
    livre reel (materialise par les pieces en partie double).

    C'est le chemin consomme par la page Grand Livre / Balance. Les colonnes
    retournees (par compte) : soldes d'ouverture, mouvements de la periode,
    soldes de cloture. Sans date : tout l'historique, ouverture a zero."""
    return BalanceService.calculer_balances_verification(db, date_debut, date_fin)


# ============ ÉTATS FINANCIERS OHADA ============

@router.post("/etats-financiers/bilan", response_model=BilanOHADADetailleResponse)
def generer_bilan_ohada(
    request: BilanOHADADetailleCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_perm("comptabilite.bilan.read"))
):
    """Générer le bilan OHADA détaillé"""
    bilan = EtatsFinanciersOHADAService.generer_bilan_ohada_detaille(
        db,
        request.exercice_id,
        request.date_bilan
    )
    return bilan


@router.get("/etats-financiers/bilan/{bilan_id}", response_model=BilanOHADADetailleResponse)
def obtenir_bilan(
    bilan_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_perm("comptabilite.bilan.read"))
):
    """Obtenir un bilan OHADA par ID"""
    bilan = db.query(BilanOHADADetaille).filter(BilanOHADADetaille.id == bilan_id).first()
    if not bilan:
        raise HTTPException(status_code=404, detail="Bilan non trouvé")
    return bilan


@router.post("/etats-financiers/compte-resultat", response_model=CompteResultatOHADADetailleResponse)
def generer_compte_resultat_ohada(
    request: CompteResultatOHADADetailleCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_perm("comptabilite.bilan.read"))
):
    """Générer le compte de résultat OHADA détaillé"""
    compte_resultat = EtatsFinanciersOHADAService.generer_compte_resultat_ohada_detaille(
        db,
        request.exercice_id,
        request.periode,
        request.date_arrete
    )
    return compte_resultat


@router.get("/etats-financiers/compte-resultat/{cr_id}", response_model=CompteResultatOHADADetailleResponse)
def obtenir_compte_resultat(
    cr_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_perm("comptabilite.bilan.read"))
):
    """Obtenir un compte de résultat OHADA par ID"""
    cr = db.query(CompteResultatOHADADetaille).filter(CompteResultatOHADADetaille.id == cr_id).first()
    if not cr:
        raise HTTPException(status_code=404, detail="Compte de résultat non trouvé")
    return cr


@router.post("/etats-financiers/tafire", response_model=TAFIREResponse)
def generer_tafire(
    request: TAFIRECreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_perm("comptabilite.bilan.read"))
):
    """Générer le TAFIRE (Tableau Financier des Ressources et Emplois)"""
    tafire = EtatsFinanciersOHADAService.generer_tafire(
        db,
        request.exercice_id,
        request.date_tafire
    )
    return tafire


@router.get("/etats-financiers/tafire/{tafire_id}", response_model=TAFIREResponse)
def obtenir_tafire(
    tafire_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_perm("comptabilite.bilan.read"))
):
    """Obtenir un TAFIRE par ID"""
    tafire = db.query(TAFIRE).filter(TAFIRE.id == tafire_id).first()
    if not tafire:
        raise HTTPException(status_code=404, detail="TAFIRE non trouvé")
    return tafire


@router.post("/etats-financiers/annexes", response_model=AnnexesOHDAResponse)
def generer_annexes_ohada(
    request: AnnexesGenererRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_perm("comptabilite.bilan.read"))
):
    """Générer les annexes OHADA"""
    annexes = EtatsFinanciersOHADAService.generer_annexes_ohada(
        db,
        request.exercice_id,
        request.date_annexes,
        request.denomination,
        request.forme_juridique,
        request.siege
    )
    return annexes


@router.get("/etats-financiers/annexes/{annexes_id}", response_model=AnnexesOHDAResponse)
def obtenir_annexes(
    annexes_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_perm("comptabilite.bilan.read"))
):
    """Obtenir les annexes OHADA par ID"""
    annexes = db.query(AnnexesOHADA).filter(AnnexesOHADA.id == annexes_id).first()
    if not annexes:
        raise HTTPException(status_code=404, detail="Annexes non trouvées")
    return annexes


# ============ CLÔTURE ============

@router.get("/cloture/etats", response_model=EtatsPeriodesResponse)
def cloture_etats(
    exercice_id: int,
    annee: int = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_perm("comptabilite.balance.read"))
):
    """Etat reel de chaque periode de l'exercice (nombre de pieces validees,
    cloture effectivite par presence d'une balance de verification equilibree).

    C'est la source d'affichage de la page Clotures ; elle remplace la liste
    precedemment fabriquee cote client depuis la date du jour."""
    try:
        return ClotureService.etats_periodes(db, exercice_id, annee)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))


@router.post("/cloture/mensuelle", response_model=ClotureMensuelleResponse)
def cloture_mensuelle(
    request: ClotureMensuelleRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_perm("comptabilite.bilan.approve"))
):
    """Clôture mensuelle des comptes de gestion"""
    try:
        result = ClotureService.cloture_mensuelle(
            db,
            request.exercice_id,
            request.periode,
            request.cloture_par
        )
        return result
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.post("/cloture/annuelle", response_model=ClotureAnnuelleResponse)
def cloture_annuelle(
    request: ClotureAnnuelleRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_perm("comptabilite.bilan.approve"))
):
    """Clôture annuelle complète"""
    try:
        result = ClotureService.cloture_annuelle(
            db,
            request.exercice_id,
            request.cloture_par
        )
        return result
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.post("/cloture/report-a-nouveau", response_model=ReportANouveauResponse)
def report_a_nouveau(
    request: ReportANouveauRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_perm("comptabilite.bilan.approve"))
):
    """Report à nouveau des soldes de bilan"""
    result = ClotureService.report_a_nouveau(
        db,
        request.exercice_source_id,
        request.exercice_cible_id
    )
    return result


@router.post("/cloture/affectation-resultat", response_model=AffectationResultatResponse)
def affectation_resultat(
    request: AffectationResultatRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_perm("comptabilite.bilan.approve"))
):
    """Affectation du résultat de l'exercice"""
    try:
        result = ClotureService.affectation_resultat(
            db,
            request.exercice_id,
            request.mode_affectation,
            request.montant_reserve,
            request.montant_dividende
        )
        return result
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


# ============ ECRITURES COMPTABLES GENERALES ============

@router.get("/ecritures")
def lister_ecritures(
    journal: Optional[str] = None,
    compte: Optional[str] = None,
    date_debut: Optional[date] = None,
    date_fin: Optional[date] = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_perm("comptabilite.journal.read"))
):
    """Lister les ecritures comptables avec filtres multicriteres.

    Retourne l'EN-TETE de piece enrichi de ses lignes reelles (partie double) :
    le frontend journal a besoin de voir les comptes debit/credit d'une
    operation, pas une ligne plate inventee. Le filtre `journal` accepte le
    code (VTE, BQ...), le nom ou le type (VENTES, BANQUE...).
    """
    from app.models.finance_ohada import EcritureComptableNew, JournalAuxiliaire, TypeJournal
    from app.services.finance_service import PieceComptableService

    query = db.query(EcritureComptableNew)
    if journal and journal != 'ALL':
        codes = [journal]
        cle = journal.strip().upper()
        if cle in TypeJournal.__members__:
            codes += [
                j.code_journal
                for (j,) in db.query(JournalAuxiliaire.code_journal).filter(
                    JournalAuxiliaire.type_journal == TypeJournal[cle]
                ).all()
            ]
        noms = {r[0] for r in db.query(JournalAuxiliaire.nom_journal).filter(
            JournalAuxiliaire.code_journal.in_(codes)
        ).all()}
        codes += sorted(noms)
        query = query.filter(EcritureComptableNew.journal.in_(codes))
    if compte:
        query = query.filter(EcritureComptableNew.compte_id == compte)
    if date_debut:
        query = query.filter(EcritureComptableNew.date_ecriture >= date_debut)
    if date_fin:
        query = query.filter(EcritureComptableNew.date_ecriture <= date_fin)
    ecritures = query.order_by(
        EcritureComptableNew.date_ecriture.desc(), EcritureComptableNew.id.desc()
    ).all()

    resultats = []
    for e in ecritures:
        d = PieceComptableService.serializer(e)
        # Retro-compat du contrat d'honnetete : les champs de l'en-tete plat
        # restent exposes tels qu'enregistres (jamais reinventes).
        d["compte_id"] = e.compte_id
        d["debit"] = float(e.debit or 0)
        d["credit"] = float(e.credit or 0)
        d["valider"] = bool(e.valider)
        resultats.append(d)
    return resultats


@router.post("/ecritures", status_code=status.HTTP_410_GONE, deprecated=True)
def creer_ecriture(
    data: dict = None,
    current_user: User = Depends(require_perm("comptabilite.journal.create"))
):
    """410 Gone : l'ecriture "plate" (un compte, un debit et un credit sur la
    meme ligne, sans contrepartie ni controle d'equilibre) est SUPPRIMEE.

    Aucune ecriture desequilibree ne doit pouvoir entrer en comptabilite.
    Le chemin reel est POST /api/v1/finance/pieces (PieceComptableService) :
    >= 2 lignes, une contrepartie par ligne, somme(debit) == somme(credit),
    exercice ouvert, journal existant, ecrit atomiquement avec le grand livre.
    """
    raise HTTPException(
        status_code=status.HTTP_410_GONE,
        detail=(
            "Cet endpoint est supprime (il acceptait des ecritures plates "
            "desequilibrees). Utilisez POST /api/v1/finance/pieces."
        ),
    )

