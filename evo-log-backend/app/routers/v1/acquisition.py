"""Acquisition router - Procurement and supplier management"""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from datetime import datetime, date

from app.core.database import get_db
from app.core.security import get_current_user
from app.models.user import User
from app.schemas.acquisition import (
    AppelOffresCreate, AppelOffresUpdate, AppelOffresResponse,
    CahierChargesCreate, CahierChargesUpdate, CahierChargesResponse,
    LigneCDCCreate, LigneCDCUpdate, LigneCDCResponse,
    OffreCreate, OffreUpdate, OffreResponse,
    LigneOffreCreate, LigneOffreUpdate, LigneOffreResponse,
    EvaluationOffreCreate, EvaluationOffreResponse,
    ComparatifCreate, ComparatifUpdate, ComparatifResponse,
    LigneComparatifCreate, LigneComparatifResponse,
    ContratCadreCreate, ContratCadreUpdate, ContratCadreResponse,
    BonCommandeCreate, BonCommandeUpdate, BonCommandeResponse,
    LigneBCCreate, LigneBCUpdate, LigneBCResponse,
    ReceptionCreate, ReceptionUpdate, ReceptionResponse,
    LigneReceptionCreate, LigneReceptionUpdate, LigneReceptionResponse,
    LitigeFournisseurCreate, LitigeFournisseurUpdate, LitigeFournisseurResponse,
    HistoriqueLitigeCreate, HistoriqueLitigeResponse,
    EvaluationFournisseurCreate, EvaluationFournisseurUpdate, EvaluationFournisseurResponse,
    RapportFournisseurResponse
)
from app.services.acquisition_service import (
    AppelOffresService, CahierChargesService, OffreService, ComparatifService,
    ContratCadreService, BonCommandeService, ReceptionService, LitigeFournisseurService,
    EvaluationFournisseurService, AcquisitionReportingService
)
from app.models.acquisition import AppelOffres, CahierCharges, Comparatif, ContratCadre, BonCommande

router = APIRouter(prefix="/acquisition", tags=["Acquisition"])


# ============ APPELS D'OFFRES ============
@router.post("/appels-offres", response_model=AppelOffresResponse, status_code=status.HTTP_201_CREATED)
def creer_appel_offres(
    appel: AppelOffresCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Create tender/call for bids"""
    return AppelOffresService.creer_appel_offres(
        db, appel.numero_appel, appel.titre, appel.type_appel,
        appel.budget_estime, appel.date_limite, appel.responsable,
        appel.departement, appel.description
    )


@router.put("/appels-offres/{appel_id}/publier", response_model=AppelOffresResponse)
def publier_appel(
    appel_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Publish tender"""
    return AppelOffresService.publier_appel(db, appel_id)


@router.put("/appels-offres/{appel_id}", response_model=AppelOffresResponse)
def mettre_a_jour_appel(
    appel_id: int,
    appel: AppelOffresUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Update tender"""
    a = db.query(AppelOffres).filter(AppelOffres.id == appel_id).first()
    if not a:
        raise HTTPException(status_code=404, detail="Appel d'offres non trouvé")
    
    for field, value in appel.model_dump(exclude_unset=True).items():
        setattr(a, field, value)
    
    db.commit()
    db.refresh(a)
    return a


# ============ CAHIERS DES CHARGES ============
@router.post("/cahiers-charges", response_model=CahierChargesResponse, status_code=status.HTTP_201_CREATED)
def creer_cahier_charges(
    cdc: CahierChargesCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Create cahier des charges"""
    return CahierChargesService.creer_cahier_charges(
        db, cdc.numero_cdc, cdc.appel_offres_id, cdc.objet,
        cdc.description_technique, cdc.specifications,
        cdc.delai_livraison, cdc.penalites_retard
    )


@router.post("/cahiers-charges/{cdc_id}/lignes", response_model=LigneCDCResponse, status_code=status.HTTP_201_CREATED)
def ajouter_ligne_cdc(
    cdc_id: int,
    ligne: LigneCDCCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Add line to cahier des charges"""
    return CahierChargesService.ajouter_ligne_cdc(
        db, cdc_id, ligne.article_id, ligne.designation,
        ligne.quantite, ligne.unite, ligne.specifications_detaillees,
        ligne.budget_unitaire, ligne.priorite
    )


@router.put("/cahiers-charges/{cdc_id}", response_model=CahierChargesResponse)
def mettre_a_jour_cdc(
    cdc_id: int,
    cdc: CahierChargesUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Update cahier des charges"""
    c = db.query(CahierCharges).filter(CahierCharges.id == cdc_id).first()
    if not c:
        raise HTTPException(status_code=404, detail="Cahier des charges non trouvé")
    
    for field, value in cdc.model_dump(exclude_unset=True).items():
        setattr(c, field, value)
    
    db.commit()
    db.refresh(c)
    return c


# ============ OFFRES ============
@router.post("/offres", response_model=OffreResponse, status_code=status.HTTP_201_CREATED)
def enregistrer_offre(
    offre: OffreCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Register supplier bid"""
    return OffreService.enregistrer_offre(
        db, offre.numero_offre, offre.appel_offres_id, offre.fournisseur_id,
        offre.montant_total, offre.delai_livraison, offre.validite_offre
    )


@router.post("/offres/{offre_id}/evaluations", response_model=EvaluationOffreResponse, status_code=status.HTTP_201_CREATED)
def evaluer_offre(
    offre_id: int,
    evaluation: EvaluationOffreCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Evaluate bid on criterion"""
    return OffreService.evaluer_offre(
        db, offre_id, evaluation.critere, evaluation.note,
        evaluation.poids, evaluation.evaluateur
    )


@router.put("/offres/{offre_id}", response_model=OffreResponse)
def mettre_a_jour_offre(
    offre_id: int,
    offre: OffreUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Update bid"""
    o = db.query(Offre).filter(Offre.id == offre_id).first()
    if not o:
        raise HTTPException(status_code=404, detail="Offre non trouvée")
    
    for field, value in offre.model_dump(exclude_unset=True).items():
        setattr(o, field, value)
    
    db.commit()
    db.refresh(o)
    return o


# ============ COMPARATIFS ============
@router.post("/comparatifs", response_model=ComparatifResponse, status_code=status.HTTP_201_CREATED)
def creer_comparatif(
    comparatif: ComparatifCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Create comparison matrix"""
    return ComparatifService.creer_comparatif(
        db, comparatif.numero_comparatif, comparatif.appel_offres_id,
        comparatif.cree_par
    )


@router.post("/comparatifs/{comparatif_id}/lignes", response_model=LigneComparatifResponse, status_code=status.HTTP_201_CREATED)
def ajouter_ligne_comparatif(
    comparatif_id: int,
    ligne: LigneComparatifCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Add line to comparison"""
    return ComparatifService.ajouter_ligne_comparatif(
        db, comparatif_id, ligne.fournisseur_id, ligne.offre_id,
        ligne.ligne_cdc_id, ligne.prix, ligne.delai,
        ligne.note_qualite, ligne.note_technique, ligne.note_financiere
    )


@router.put("/comparatifs/{comparatif_id}", response_model=ComparatifResponse)
def mettre_a_jour_comparatif(
    comparatif_id: int,
    comparatif: ComparatifUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Update comparison matrix"""
    c = db.query(Comparatif).filter(Comparatif.id == comparatif_id).first()
    if not c:
        raise HTTPException(status_code=404, detail="Comparatif non trouvé")
    
    for field, value in comparatif.model_dump(exclude_unset=True).items():
        setattr(c, field, value)
    
    db.commit()
    db.refresh(c)
    return c


# ============ CONTRATS CADRE ============
@router.post("/contrats-cadre", response_model=ContratCadreResponse, status_code=status.HTTP_201_CREATED)
def creer_contrat_cadre(
    contrat: ContratCadreCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Create framework contract"""
    return ContratCadreService.creer_contrat_cadre(
        db, contrat.numero_contrat, contrat.fournisseur_id, contrat.type_contrat,
        contrat.date_signature, contrat.date_debut, contrat.date_fin, contrat.montant_annuel
    )


@router.put("/contrats-cadre/{contrat_id}", response_model=ContratCadreResponse)
def mettre_a_jour_contrat_cadre(
    contrat_id: int,
    contrat: ContratCadreUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Update framework contract"""
    c = db.query(ContratCadre).filter(ContratCadre.id == contrat_id).first()
    if not c:
        raise HTTPException(status_code=404, detail="Contrat cadre non trouvé")
    
    for field, value in contrat.model_dump(exclude_unset=True).items():
        setattr(c, field, value)
    
    db.commit()
    db.refresh(c)
    return c


# ============ BONS DE COMMANDE ============
@router.post("/bons-commande", response_model=BonCommandeResponse, status_code=status.HTTP_201_CREATED)
def creer_bon_commande(
    bc: BonCommandeCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Create purchase order"""
    return BonCommandeService.creer_bon_commande(
        db, bc.numero_bc, bc.fournisseur_id, bc.date_prevue_livraison,
        bc.destinataire, bc.lieu_livraison, bc.conditions_paiement
    )


@router.put("/bons-commande/{bc_id}/valider", response_model=BonCommandeResponse)
def valider_bc(
    bc_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Validate purchase order"""
    return BonCommandeService.valider_bc(db, bc_id, current_user.username)


@router.put("/bons-commande/{bc_id}", response_model=BonCommandeResponse)
def mettre_a_jour_bc(
    bc_id: int,
    bc: BonCommandeUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Update purchase order"""
    b = db.query(BonCommande).filter(BonCommande.id == bc_id).first()
    if not b:
        raise HTTPException(status_code=404, detail="Bon de commande non trouvé")
    
    for field, value in bc.model_dump(exclude_unset=True).items():
        setattr(b, field, value)
    
    db.commit()
    db.refresh(b)
    return b


# ============ RÉCEPTIONS ============
@router.post("/receptions", response_model=ReceptionResponse, status_code=status.HTTP_201_CREATED)
def creer_reception(
    reception: ReceptionCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Create goods receipt"""
    return ReceptionService.creer_reception(
        db, reception.numero_reception, reception.bc_id, reception.fournisseur_id,
        reception.type_reception, reception.lieu_reception, reception.responsable
    )


@router.put("/receptions/{reception_id}/valider", response_model=ReceptionResponse)
def valider_reception(
    reception_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Validate goods receipt"""
    return ReceptionService.valider_reception(
        db, reception_id, current_user.username, "conforme"
    )


@router.put("/receptions/{reception_id}", response_model=ReceptionResponse)
def mettre_a_jour_reception(
    reception_id: int,
    reception: ReceptionUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Update goods receipt"""
    r = db.query(Reception).filter(Reception.id == reception_id).first()
    if not r:
        raise HTTPException(status_code=404, detail="Réception non trouvée")
    
    for field, value in reception.model_dump(exclude_unset=True).items():
        setattr(r, field, value)
    
    db.commit()
    db.refresh(r)
    return r


# ============ LITIGES FOURNISSEURS ============
@router.post("/litiges", response_model=LitigeFournisseurResponse, status_code=status.HTTP_201_CREATED)
def creer_litige(
    litige: LitigeFournisseurCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Create supplier dispute"""
    return LitigeFournisseurService.creer_litige(
        db, litige.numero_litige, litige.fournisseur_id, litige.type_litige,
        litige.description, litige.gravite, litige.montant_en_litige
    )


@router.post("/litiges/{litige_id}/historique", response_model=HistoriqueLitigeResponse, status_code=status.HTTP_201_CREATED)
def ajouter_historique(
    litige_id: int,
    historique: HistoriqueLitigeCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Add dispute history entry"""
    return LitigeFournisseurService.ajouter_historique(
        db, litige_id, historique.action, historique.description,
        historique.auteur, historique.resultat
    )


@router.put("/litiges/{litige_id}", response_model=LitigeFournisseurResponse)
def mettre_a_jour_litige(
    litige_id: int,
    litige: LitigeFournisseurUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Update supplier dispute"""
    l = db.query(LitigeFournisseur).filter(LitigeFournisseur.id == litige_id).first()
    if not l:
        raise HTTPException(status_code=404, detail="Litige non trouvé")
    
    for field, value in litige.model_dump(exclude_unset=True).items():
        setattr(l, field, value)
    
    db.commit()
    db.refresh(l)
    return l


# ============ ÉVALUATIONS FOURNISSEURS ============
@router.post("/evaluations-fournisseur", response_model=EvaluationFournisseurResponse, status_code=status.HTTP_201_CREATED)
def creer_evaluation_fournisseur(
    evaluation: EvaluationFournisseurCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Create supplier evaluation"""
    return EvaluationFournisseurService.creer_evaluation(
        db, evaluation.fournisseur_id, evaluation.periode,
        evaluation.note_qualite, evaluation.note_delai,
        evaluation.note_prix, evaluation.note_service, evaluation.evaluateur
    )


@router.put("/evaluations-fournisseur/{evaluation_id}", response_model=EvaluationFournisseurResponse)
def mettre_a_jour_evaluation_fournisseur(
    evaluation_id: int,
    evaluation: EvaluationFournisseurUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Update supplier evaluation"""
    e = db.query(EvaluationFournisseur).filter(EvaluationFournisseur.id == evaluation_id).first()
    if not e:
        raise HTTPException(status_code=404, detail="Évaluation non trouvée")
    
    for field, value in evaluation.model_dump(exclude_unset=True).items():
        setattr(e, field, value)
    
    db.commit()
    db.refresh(e)
    return e


@router.get("/fournisseurs/{fournisseur_id}/rapport", response_model=RapportFournisseurResponse)
def rapport_fournisseur(
    fournisseur_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Generate supplier report"""
    return AcquisitionReportingService.rapport_fournisseur(db, fournisseur_id)
