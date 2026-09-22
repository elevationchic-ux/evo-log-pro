"""Magasin Douane router - Warehouse under customs management"""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from datetime import datetime, date

from app.core.database import get_db
from app.core.security import get_current_user
from app.models.user import User
from app.schemas.magasin_douane import (
    EntrepotDouaneCreate, EntrepotDouaneUpdate, EntrepotDouaneResponse,
    DeclarationEntrepotCreate, DeclarationEntrepotUpdate, DeclarationEntrepotResponse,
    LigneEntrepotCreate, LigneEntrepotUpdate, LigneEntrepotResponse,
    FicheMagasinCreate, FicheMagasinUpdate, FicheMagasinResponse,
    MouvementFicheCreate, MouvementFicheResponse,
    InventaireDouanierCreate, InventaireDouanierUpdate, InventaireDouanierResponse,
    LigneInventaireDouanierCreate, LigneInventaireDouanierResponse,
    SurveillanceMagazinCreate, SurveillanceMagazinUpdate, SurveillanceMagazinResponse,
    MiseConsommationCreate, MiseConsommationUpdate, MiseConsommationResponse,
    ReexportationCreate, ReexportationUpdate, ReexportationResponse,
    DestructionCreate, DestructionUpdate, DestructionResponse,
    EntretienStockCreate, EntretienStockUpdate, EntretienStockResponse,
    AssuranceStockCreate, AssuranceStockUpdate, AssuranceStockResponse,
    CompteRenduManutentionCreate, CompteRenduManutentionUpdate, CompteRenduManutentionResponse,
    RapportEntrepotResponse
)
from app.services.magasin_douane_service import (
    EntrepotDouaneService, DeclarationEntrepotService, LigneEntrepotService,
    FicheMagasinService, InventaireDouanierService, SurveillanceMagazinService,
    MiseConsommationService, ReexportationService, DestructionService,
    EntretienStockService, AssuranceStockService, CompteRenduManutentionService,
    MagasinDouaneReportingService
)
from app.models.magasin_douane import EntrepotDouane, DeclarationEntrepot, FicheMagasin

router = APIRouter(tags=["Magasin Douane"])


# ============ ENTREPOTS DOUANE ============
@router.post("/entrepots", response_model=EntrepotDouaneResponse, status_code=status.HTTP_201_CREATED)
def creer_entrepot_douane(
    entrepot: EntrepotDouaneCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Create customs warehouse"""
    return EntrepotDouaneService.creer_entrepot_douane(
        db, entrepot.code, entrepot.nom, entrepot.type_entrepot, entrepot.regime,
        entrepot.adresse, entrepot.surface_m2, entrepot.capacite_tonnage,
        entrepot.numero_agrement, entrepot.date_agrement, entrepot.date_expiration_agrement
    )


@router.get("/entrepots", response_model=List[EntrepotDouaneResponse])
def lister_entrepots_douane(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """List all customs warehouses"""
    return db.query(EntrepotDouane).filter(EntrepotDouane.statut == "actif").all()


@router.put("/entrepots/{entrepot_id}", response_model=EntrepotDouaneResponse)
def mettre_a_jour_entrepot(
    entrepot_id: int,
    entrepot: EntrepotDouaneUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Update customs warehouse"""
    e = db.query(EntrepotDouane).filter(EntrepotDouane.id == entrepot_id).first()
    if not e:
        raise HTTPException(status_code=404, detail="Entrepôt non trouvé")
    
    for field, value in entrepot.model_dump(exclude_unset=True).items():
        setattr(e, field, value)
    
    db.commit()
    db.refresh(e)
    return e


@router.get("/entrepots/{entrepot_id}/rapport", response_model=RapportEntrepotResponse)
def rapport_entrepot(
    entrepot_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Generate warehouse report"""
    return MagasinDouaneReportingService.rapport_entrepot(db, entrepot_id)


# ============ DECLARATIONS ENTREPOT ============
@router.post("/declarations", response_model=DeclarationEntrepotResponse, status_code=status.HTTP_201_CREATED)
def creer_declaration_entrepot(
    declaration: DeclarationEntrepotCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Create warehouse declaration"""
    return DeclarationEntrepotService.creer_declaration_entrepot(
        db, declaration.numero_declaration, declaration.entrepot_id,
        declaration.dossier_transit_id, declaration.regime, declaration.valeur_marchandise
    )


@router.put("/declarations/{declaration_id}/accepter", response_model=DeclarationEntrepotResponse)
def accepter_declaration(
    declaration_id: int,
    valide_par: str,
    fonction: str,
    reference_sygdonia: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Accept warehouse declaration"""
    return DeclarationEntrepotService.accepter_declaration(
        db, declaration_id, valide_par, fonction, reference_sygdonia
    )


@router.put("/declarations/{declaration_id}", response_model=DeclarationEntrepotResponse)
def mettre_a_jour_declaration(
    declaration_id: int,
    declaration: DeclarationEntrepotUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Update warehouse declaration"""
    d = db.query(DeclarationEntrepot).filter(DeclarationEntrepot.id == declaration_id).first()
    if not d:
        raise HTTPException(status_code=404, detail="Déclaration non trouvée")
    
    for field, value in declaration.model_dump(exclude_unset=True).items():
        setattr(d, field, value)
    
    db.commit()
    db.refresh(d)
    return d


# ============ LIGNES ENTREPOT ============
@router.post("/lignes-entrepot", response_model=LigneEntrepotResponse, status_code=status.HTTP_201_CREATED)
def ajouter_ligne(
    ligne: LigneEntrepotCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Add line to warehouse declaration"""
    return LigneEntrepotService.ajouter_ligne(
        db, ligne.declaration_id, ligne.article_id, ligne.designation,
        ligne.quantite, ligne.unite, ligne.poids_net, ligne.poids_brut,
        ligne.valeur_unitaire, ligne.emplacement, ligne.numero_lot
    )


@router.put("/lignes-entrepot/{ligne_id}", response_model=LigneEntrepotResponse)
def mettre_a_jour_ligne(
    ligne_id: int,
    ligne: LigneEntrepotUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Update warehouse declaration line"""
    l = db.query(LigneEntrepot).filter(LigneEntrepot.id == ligne_id).first()
    if not l:
        raise HTTPException(status_code=404, detail="Ligne non trouvée")
    
    for field, value in ligne.model_dump(exclude_unset=True).items():
        setattr(l, field, value)
    
    db.commit()
    db.refresh(l)
    return l


# ============ FICHES MAGASIN ============
@router.post("/fiches-magasin", response_model=FicheMagasinResponse, status_code=status.HTTP_201_CREATED)
def creer_fiche_magasin(
    fiche: FicheMagasinCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Create stock card"""
    return FicheMagasinService.creer_fiche_magasin(
        db, fiche.numero_fiche, fiche.entrepot_id, fiche.article_id,
        fiche.designation, fiche.numero_lot, fiche.stock_initial,
        fiche.unite, fiche.emplacement, fiche.valeur_unitaire
    )


@router.put("/fiches-magasin/{fiche_id}", response_model=FicheMagasinResponse)
def mettre_a_jour_fiche(
    fiche_id: int,
    fiche: FicheMagasinUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Update stock card"""
    f = db.query(FicheMagasin).filter(FicheMagasin.id == fiche_id).first()
    if not f:
        raise HTTPException(status_code=404, detail="Fiche non trouvée")
    
    for field, value in fiche.model_dump(exclude_unset=True).items():
        setattr(f, field, value)
    
    db.commit()
    db.refresh(f)
    return f


# ============ MOUVEMENTS FICHE ============
@router.post("/mouvements-fiche", response_model=MouvementFicheResponse, status_code=status.HTTP_201_CREATED)
def enregistrer_mouvement(
    mouvement: MouvementFicheCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Record stock movement"""
    return FicheMagasinService.enregistrer_mouvement(
        db, mouvement.fiche_id, mouvement.type_mouvement, mouvement.quantite,
        mouvement.type_operation, mouvement.document_reference,
        mouvement.operateur, mouvement.motif
    )


# ============ INVENTAIRES DOUANIERS ============
@router.post("/inventaires", response_model=InventaireDouanierResponse, status_code=status.HTTP_201_CREATED)
def creer_inventaire(
    inventaire: InventaireDouanierCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Create customs inventory"""
    return InventaireDouanierService.creer_inventaire(
        db, inventaire.numero_inventaire, inventaire.entrepot_id,
        inventaire.type_inventaire, inventaire.operateur
    )


@router.post("/inventaires/{inventaire_id}/lignes", response_model=LigneInventaireDouanierResponse, status_code=status.HTTP_201_CREATED)
def ajouter_ligne_inventaire(
    inventaire_id: int,
    ligne: LigneInventaireDouanierCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Add line to customs inventory"""
    return InventaireDouanierService.ajouter_ligne_inventaire(
        db, inventaire_id, ligne.article_id, ligne.designation,
        ligne.numero_lot, ligne.emplacement, ligne.stock_theorique,
        ligne.stock_reel, ligne.unite, ligne.valeur_unitaire
    )


@router.put("/inventaires/{inventaire_id}/completer", response_model=InventaireDouanierResponse)
def completer_inventaire(
    inventaire_id: int,
    inspecteur_douane: str,
    resultat: str,
    ecart_tonnage: float,
    ecart_valeur: float,
    motif_ecart: str = "",
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Complete customs inventory"""
    return InventaireDouanierService.completer_inventaire(
        db, inventaire_id, inspecteur_douane, resultat,
        ecart_tonnage, ecart_valeur, motif_ecart
    )


@router.put("/inventaires/{inventaire_id}", response_model=InventaireDouanierResponse)
def mettre_a_jour_inventaire(
    inventaire_id: int,
    inventaire: InventaireDouanierUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Update customs inventory"""
    i = db.query(InventaireDouanier).filter(InventaireDouanier.id == inventaire_id).first()
    if not i:
        raise HTTPException(status_code=404, detail="Inventaire non trouvé")
    
    for field, value in inventaire.model_dump(exclude_unset=True).items():
        setattr(i, field, value)
    
    db.commit()
    db.refresh(i)
    return i


# ============ SURVEILLANCE MAGAZIN ============
@router.post("/surveillance", response_model=SurveillanceMagazinResponse, status_code=status.HTTP_201_CREATED)
def enregistrer_patrouille(
    surveillance: SurveillanceMagazinCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Record patrol"""
    return SurveillanceMagazinService.enregistrer_patrouille(
        db, surveillance.entrepot_id, surveillance.gardien,
        surveillance.type_controle, surveillance.zones_controlees,
        surveillance.incidents, surveillance.anomalies
    )


@router.put("/surveillance/{surveillance_id}", response_model=SurveillanceMagazinResponse)
def mettre_a_jour_surveillance(
    surveillance_id: int,
    surveillance: SurveillanceMagazinUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Update surveillance record"""
    s = db.query(SurveillanceMagazin).filter(SurveillanceMagazin.id == surveillance_id).first()
    if not s:
        raise HTTPException(status_code=404, detail="Surveillance non trouvée")
    
    for field, value in surveillance.model_dump(exclude_unset=True).items():
        setattr(s, field, value)
    
    db.commit()
    db.refresh(s)
    return s


# ============ MISE CONSOMMATION ============
@router.post("/mises-consommation", response_model=MiseConsommationResponse, status_code=status.HTTP_201_CREATED)
def creer_mise_consommation(
    mise: MiseConsommationCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Create release to consumption"""
    return MiseConsommationService.creer_mise_consommation(
        db, mise.numero_mise, mise.declaration_entrepot_id,
        mise.valide_par, mise.fonction
    )


@router.put("/mises-consommation/{mise_id}", response_model=MiseConsommationResponse)
def mettre_a_jour_mise_consommation(
    mise_id: int,
    mise: MiseConsommationUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Update release to consumption"""
    m = db.query(MiseConsommation).filter(MiseConsommation.id == mise_id).first()
    if not m:
        raise HTTPException(status_code=404, detail="Mise à consommation non trouvée")
    
    for field, value in mise.model_dump(exclude_unset=True).items():
        setattr(m, field, value)
    
    db.commit()
    db.refresh(m)
    return m


# ============ REEXPORTATION ============
@router.post("/reexportations", response_model=ReexportationResponse, status_code=status.HTTP_201_CREATED)
def creer_reexportation(
    reexport: ReexportationCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Create re-export"""
    return ReexportationService.creer_reexportation(
        db, reexport.numero_reexport, reexport.declaration_entrepot_id,
        reexport.pays_destination, reexport.code_pays_destination,
        reexport.motif, reexport.moyen_transport
    )


@router.put("/reexportations/{reexport_id}", response_model=ReexportationResponse)
def mettre_a_jour_reexportation(
    reexport_id: int,
    reexport: ReexportationUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Update re-export"""
    r = db.query(Reexportation).filter(Reexportation.id == reexport_id).first()
    if not r:
        raise HTTPException(status_code=404, detail="Réexportation non trouvée")
    
    for field, value in reexport.model_dump(exclude_unset=True).items():
        setattr(r, field, value)
    
    db.commit()
    db.refresh(r)
    return r


# ============ DESTRUCTION ============
@router.post("/destructions", response_model=DestructionResponse, status_code=status.HTTP_201_CREATED)
def creer_destruction(
    destruction: DestructionCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Create destruction request"""
    return DestructionService.creer_destruction(
        db, destruction.numero_destruction, destruction.declaration_entrepot_id,
        destruction.motif, destruction.type_destruction
    )


@router.put("/destructions/{destruction_id}/autoriser", response_model=DestructionResponse)
def autoriser_destruction(
    destruction_id: int,
    autorise_par: str,
    fonction: str,
    temoin: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Authorize destruction"""
    return DestructionService.autoriser_destruction(
        db, destruction_id, autorise_par, fonction, temoin
    )


@router.put("/destructions/{destruction_id}/effectuer", response_model=DestructionResponse)
def effectuer_destruction(
    destruction_id: int,
    poids_destruct: float,
    valeur_destruct: float,
    rapport_destruction: str,
    photos: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Record destruction execution"""
    return DestructionService.effectuer_destruction(
        db, destruction_id, poids_destruct, valeur_destruct,
        rapport_destruction, photos
    )


@router.put("/destructions/{destruction_id}", response_model=DestructionResponse)
def mettre_a_jour_destruction(
    destruction_id: int,
    destruction: DestructionUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Update destruction"""
    d = db.query(Destruction).filter(Destruction.id == destruction_id).first()
    if not d:
        raise HTTPException(status_code=404, detail="Destruction non trouvée")
    
    for field, value in destruction.model_dump(exclude_unset=True).items():
        setattr(d, field, value)
    
    db.commit()
    db.refresh(d)
    return d


# ============ ENTRETIEN STOCK ============
@router.post("/entretiens-stock", response_model=EntretienStockResponse, status_code=status.HTTP_201_CREATED)
def creer_entretien(
    entretien: EntretienStockCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Create stock maintenance"""
    return EntretienStockService.creer_entretien(
        db, entretien.numero_entretien, entretien.declaration_entrepot_id,
        entretien.type_entretien, entretien.article_id, entretien.quantite,
        entretien.unite, entretien.operateur, entretien.description
    )


@router.put("/entretiens-stock/{entretien_id}", response_model=EntretienStockResponse)
def mettre_a_jour_entretien(
    entretien_id: int,
    entretien: EntretienStockUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Update stock maintenance"""
    e = db.query(EntretienStock).filter(EntretienStock.id == entretien_id).first()
    if not e:
        raise HTTPException(status_code=404, detail="Entretien non trouvé")
    
    for field, value in entretien.model_dump(exclude_unset=True).items():
        setattr(e, field, value)
    
    db.commit()
    db.refresh(e)
    return e


# ============ ASSURANCE STOCK ============
@router.post("/assurances-stock", response_model=AssuranceStockResponse, status_code=status.HTTP_201_CREATED)
def creer_assurance(
    assurance: AssuranceStockCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Create stock insurance"""
    return AssuranceStockService.creer_assurance(
        db, assurance.entrepot_id, assurance.numero_police, assurance.assureur,
        assurance.type_couverture, assurance.valeur_assuree, assurance.prime_annuelle,
        assurance.date_debut, assurance.date_fin, assurance.franchise
    )


@router.put("/assurances-stock/{assurance_id}", response_model=AssuranceStockResponse)
def mettre_a_jour_assurance(
    assurance_id: int,
    assurance: AssuranceStockUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Update stock insurance"""
    a = db.query(AssuranceStock).filter(AssuranceStock.id == assurance_id).first()
    if not a:
        raise HTTPException(status_code=404, detail="Assurance non trouvée")
    
    for field, value in assurance.model_dump(exclude_unset=True).items():
        setattr(a, field, value)
    
    db.commit()
    db.refresh(a)
    return a


# ============ COMPTE RENDU MANUTENTION ============
@router.post("/comptes-rendus", response_model=CompteRenduManutentionResponse, status_code=status.HTTP_201_CREATED)
def creer_compte_rendu(
    cr: CompteRenduManutentionCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Create handling operations report"""
    return CompteRenduManutentionService.creer_compte_rendu(
        db, cr.numero_cr, cr.entrepot_id, cr.type_operation,
        cr.equipe, cr.equipement, cr.duree_heures,
        cr.nombre_mouvements, cr.tonnage_total
    )


@router.put("/comptes-rendus/{cr_id}", response_model=CompteRenduManutentionResponse)
def mettre_a_jour_compte_rendu(
    cr_id: int,
    cr: CompteRenduManutentionUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Update handling operations report"""
    c = db.query(CompteRenduManutention).filter(CompteRenduManutention.id == cr_id).first()
    if not c:
        raise HTTPException(status_code=404, detail="Compte rendu non trouvé")
    
    for field, value in cr.model_dump(exclude_unset=True).items():
        setattr(c, field, value)
    
    db.commit()
    db.refresh(c)
    return c
