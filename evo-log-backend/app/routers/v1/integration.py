"""Integration router - External integrations for Cameroon/CEMAC"""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from datetime import datetime, date

from app.core.database import get_db
from app.core.security import get_current_user
from app.models.user import User
from app.schemas.integration import (
    IntegrationCreate, IntegrationUpdate, IntegrationResponse,
    RequeteIntegrationCreate, RequeteIntegrationUpdate, RequeteIntegrationResponse,
    WebhookIntegrationCreate, WebhookIntegrationUpdate, WebhookIntegrationResponse,
    SYDONIAPlusCreate, SYDONIAPlusUpdate, SYDONIAPlusResponse,
    GuichetUniqueCreate, GuichetUniqueUpdate, GuichetUniqueResponse,
    PCSCreate, PCSUpdate, PCSResponse,
    IntegrationBanqueCreate, IntegrationBanqueUpdate, IntegrationBanqueResponse,
    IntegrationAssureurCreate, IntegrationAssureurUpdate, IntegrationAssureurResponse,
    IntegrationTransitaireCreate, IntegrationTransitaireUpdate, IntegrationTransitaireResponse,
    SynchronisationCreate, SynchronisationUpdate, SynchronisationResponse,
    RapportIntegrationResponse
)
from app.services.integration_service import (
    IntegrationService, RequeteIntegrationService, SYDONIAPlusService, GuichetUniqueService,
    PCSService, IntegrationBanqueService, IntegrationAssureurService, IntegrationTransitaireService,
    SynchronisationService, IntegrationReportingService
)
from app.models.integration import Integration, SYDONIAPlus, GuichetUnique, PCS, IntegrationBanque, IntegrationAssureur, IntegrationTransitaire

router = APIRouter(tags=["Integration"])


# ============ INTEGRATIONS ============
@router.post("/integrations", response_model=IntegrationResponse, status_code=status.HTTP_201_CREATED)
def creer_integration(
    integration: IntegrationCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Create external integration"""
    return IntegrationService.creer_integration(
        db, integration.code_integration, integration.type_integration,
        integration.nom, integration.url_api, integration.api_key
    )


@router.put("/integrations/{integration_id}/activer", response_model=IntegrationResponse)
def activer_integration(
    integration_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Activate integration"""
    return IntegrationService.activer_integration(db, integration_id)


@router.put("/integrations/{integration_id}", response_model=IntegrationResponse)
def mettre_a_jour_integration(
    integration_id: int,
    integration: IntegrationUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Update integration"""
    i = db.query(Integration).filter(Integration.id == integration_id).first()
    if not i:
        raise HTTPException(status_code=404, detail="Intégration non trouvée")
    
    for field, value in integration.model_dump(exclude_unset=True).items():
        setattr(i, field, value)
    
    db.commit()
    db.refresh(i)
    return i


# ============ REQUETES INTEGRATION ============
@router.post("/requetes", response_model=RequeteIntegrationResponse, status_code=status.HTTP_201_CREATED)
def creer_requete(
    requete: RequeteIntegrationCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Create integration request"""
    return RequeteIntegrationService.creer_requete(
        db, requete.integration_id, requete.numero_requete,
        requete.type_requete, requete.direction, requete.donnees_envoyees
    )


@router.put("/requetes/{requete_id}/reponse", response_model=RequeteIntegrationResponse)
def mettre_a_jour_reponse(
    requete_id: int,
    donnees_recues: str,
    code_reponse: int,
    duree_ms: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Update request response"""
    return RequeteIntegrationService.mettre_a_jour_reponse(
        db, requete_id, donnees_recues, code_reponse, duree_ms
    )


@router.put("/requetes/{requete_id}", response_model=RequeteIntegrationResponse)
def mettre_a_jour_requete(
    requete_id: int,
    requete: RequeteIntegrationUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Update request"""
    r = db.query(RequeteIntegration).filter(RequeteIntegration.id == requete_id).first()
    if not r:
        raise HTTPException(status_code=404, detail="Requête non trouvée")
    
    for field, value in requete.model_dump(exclude_unset=True).items():
        setattr(r, field, value)
    
    db.commit()
    db.refresh(r)
    return r


# ============ SYDONIA PLUS ============
@router.post("/sydonia", response_model=SYDONIAPlusResponse, status_code=status.HTTP_201_CREATED)
def creer_dossier_sydonia(
    dossier: SYDONIAPlusCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Create SYDONIA+ dossier"""
    return SYDONIAPlusService.creer_dossier_sydonia(
        db, dossier.numero_dossier, dossier.bureau_douane,
        dossier.type_operation, dossier.regime
    )


@router.put("/sydonia/{dossier_id}", response_model=SYDONIAPlusResponse)
def mettre_a_jour_dossier_sydonia(
    dossier_id: int,
    dossier: SYDONIAPlusUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Update SYDONIA+ dossier"""
    d = db.query(SYDONIAPlus).filter(SYDONIAPlus.id == dossier_id).first()
    if not d:
        raise HTTPException(status_code=404, detail="Dossier SYDONIA+ non trouvé")
    
    for field, value in dossier.model_dump(exclude_unset=True).items():
        setattr(d, field, value)
    
    db.commit()
    db.refresh(d)
    return d


# ============ GUICHET UNIQUE ============
@router.post("/guichet-unique", response_model=GuichetUniqueResponse, status_code=status.HTTP_201_CREATED)
def creer_transaction(
    transaction: GuichetUniqueCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Create GUICHET UNIQUE transaction"""
    return GuichetUniqueService.creer_transaction(
        db, transaction.numero_transaction, transaction.service,
        transaction.type_service, transaction.utilisateur
    )


@router.put("/guichet-unique/{transaction_id}", response_model=GuichetUniqueResponse)
def mettre_a_jour_transaction(
    transaction_id: int,
    transaction: GuichetUniqueUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Update GUICHET UNIQUE transaction"""
    t = db.query(GuichetUnique).filter(GuichetUnique.id == transaction_id).first()
    if not t:
        raise HTTPException(status_code=404, detail="Transaction GUICHET UNIQUE non trouvée")
    
    for field, value in transaction.model_dump(exclude_unset=True).items():
        setattr(t, field, value)
    
    db.commit()
    db.refresh(t)
    return t


# ============ PCS ============
@router.post("/pcs", response_model=PCSResponse, status_code=status.HTTP_201_CREATED)
def creer_operation_pcs(
    operation: PCSCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Create PCS operation"""
    return PCSService.creer_operation_pcs(
        db, operation.reference_pcs, operation.type_operation,
        operation.navire, operation.port
    )


@router.put("/pcs/{operation_id}", response_model=PCSResponse)
def mettre_a_jour_operation_pcs(
    operation_id: int,
    operation: PCSUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Update PCS operation"""
    o = db.query(PCS).filter(PCS.id == operation_id).first()
    if not o:
        raise HTTPException(status_code=404, detail="Opération PCS non trouvée")
    
    for field, value in operation.model_dump(exclude_unset=True).items():
        setattr(o, field, value)
    
    db.commit()
    db.refresh(o)
    return o


# ============ INTEGRATIONS BANQUE ============
@router.post("/integrations-banque", response_model=IntegrationBanqueResponse, status_code=status.HTTP_201_CREATED)
def creer_integration_banque(
    integration: IntegrationBanqueCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Create bank integration"""
    return IntegrationBanqueService.creer_integration_banque(
        db, integration.banque_id, integration.code_banque,
        integration.nom_banque, integration.bic, integration.iban
    )


@router.put("/integrations-banque/{integration_id}", response_model=IntegrationBanqueResponse)
def mettre_a_jour_integration_banque(
    integration_id: int,
    integration: IntegrationBanqueUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Update bank integration"""
    i = db.query(IntegrationBanque).filter(IntegrationBanque.id == integration_id).first()
    if not i:
        raise HTTPException(status_code=404, detail="Intégration banque non trouvée")
    
    for field, value in integration.model_dump(exclude_unset=True).items():
        setattr(i, field, value)
    
    db.commit()
    db.refresh(i)
    return i


# ============ INTEGRATIONS ASSUREUR ============
@router.post("/integrations-assureur", response_model=IntegrationAssureurResponse, status_code=status.HTTP_201_CREATED)
def creer_integration_assureur(
    integration: IntegrationAssureurCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Create insurer integration"""
    return IntegrationAssureurService.creer_integration_assureur(
        db, integration.assureur_id, integration.code_assureur,
        integration.nom_assureur, integration.type_assurance
    )


@router.put("/integrations-assureur/{integration_id}", response_model=IntegrationAssureurResponse)
def mettre_a_jour_integration_assureur(
    integration_id: int,
    integration: IntegrationAssureurUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Update insurer integration"""
    i = db.query(IntegrationAssureur).filter(IntegrationAssureur.id == integration_id).first()
    if not i:
        raise HTTPException(status_code=404, detail="Intégration assureur non trouvée")
    
    for field, value in integration.model_dump(exclude_unset=True).items():
        setattr(i, field, value)
    
    db.commit()
    db.refresh(i)
    return i


# ============ INTEGRATIONS TRANSITAIRE ============
@router.post("/integrations-transitaire", response_model=IntegrationTransitaireResponse, status_code=status.HTTP_201_CREATED)
def creer_integration_transitaire(
    integration: IntegrationTransitaireCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Create forwarder integration"""
    return IntegrationTransitaireService.creer_integration_transitaire(
        db, integration.transitaire_id, integration.code_transitaire,
        integration.nom_transitaire, integration.type_service
    )


@router.put("/integrations-transitaire/{integration_id}", response_model=IntegrationTransitaireResponse)
def mettre_a_jour_integration_transitaire(
    integration_id: int,
    integration: IntegrationTransitaireUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Update forwarder integration"""
    i = db.query(IntegrationTransitaire).filter(IntegrationTransitaire.id == integration_id).first()
    if not i:
        raise HTTPException(status_code=404, detail="Intégration transitaire non trouvée")
    
    for field, value in integration.model_dump(exclude_unset=True).items():
        setattr(i, field, value)
    
    db.commit()
    db.refresh(i)
    return i


# ============ SYNCHRONISATIONS ============
@router.post("/synchronisations", response_model=SynchronisationResponse, status_code=status.HTTP_201_CREATED)
def creer_synchronisation(
    synchronisation: SynchronisationCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Create synchronization"""
    return SynchronisationService.creer_synchronisation(
        db, synchronisation.integration_id, synchronisation.type_synchronisation,
        synchronisation.lance_par
    )


@router.put("/synchronisations/{synchronisation_id}/completer", response_model=SynchronisationResponse)
def completer_synchronisation(
    synchronisation_id: int,
    enregistrements_traites: int,
    enregistrements_echoues: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Complete synchronization"""
    return SynchronisationService.completer_synchronisation(
        db, synchronisation_id, enregistrements_traites, enregistrements_echoues
    )


@router.put("/synchronisations/{synchronisation_id}", response_model=SynchronisationResponse)
def mettre_a_jour_synchronisation(
    synchronisation_id: int,
    synchronisation: SynchronisationUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Update synchronization"""
    s = db.query(Synchronisation).filter(Synchronisation.id == synchronisation_id).first()
    if not s:
        raise HTTPException(status_code=404, detail="Synchronisation non trouvée")
    
    for field, value in synchronisation.model_dump(exclude_unset=True).items():
        setattr(s, field, value)
    
    db.commit()
    db.refresh(s)
    return s


@router.get("/integrations/{integration_id}/rapport", response_model=RapportIntegrationResponse)
def rapport_integration(
    integration_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Generate integration report"""
    return IntegrationReportingService.rapport_integration(db, integration_id)
