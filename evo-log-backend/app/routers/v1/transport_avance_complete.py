"""Router API pour le transport avancé - Dispatch, E-POD, Analytics"""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from datetime import date

from app.core.database import get_db
from app.core.auth import get_current_user
from app.models.user import User
from app.schemas.transport_avance import (
    DispatchCreate, DispatchUpdate, DispatchResponse,
    OptimisationTourneesRequest, EquilibreChargeResponse,
    ArretCreate, ArretResponse,
    PODCreate, PODUpdate, PODResponse,
    DocumentPODCreate, DocumentPODResponse,
    TableauBordTransportResponse, KPIResponse, AlertPerformanceResponse
)
from app.services.transport_avance_service import (
    DispatchIntelligentService, EPODService, AnalyticsTransportService
)
from app.models.transport_avance import Dispatch, Arret, POD, DocumentPOD

router = APIRouter(tags=["Transport Avancé"])  # monte sur /api/v1/transport-avance-complete par main.py


# ============ DISPATCH INTELLIGENT ============

@router.post("/dispatch/optimisation", response_model=DispatchResponse)
def optimisation_tournees(
    request: OptimisationTourneesRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Optimisation de tournées"""
    try:
        dispatch = DispatchIntelligentService.optimisation_tournees(
            db,
            request.missions_ids,
            request.contraintes
        )
        return dispatch
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.post("/dispatch/planification-automatique", response_model=List[DispatchResponse])
def planification_automatique(
    date_jour: date,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Planification automatique des missions pour une journée"""
    dispatches = DispatchIntelligentService.planification_automatique(db, date_jour)
    return dispatches


@router.get("/dispatch/equilibre-charge", response_model=EquilibreChargeResponse)
def equilibre_charge_chauffeurs(
    periode_debut: date,
    periode_fin: date,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Équilibrage de la charge entre chauffeurs"""
    return DispatchIntelligentService.equilibre_charge_chauffeurs(db, periode_debut, periode_fin)


@router.post("/dispatch/attribution-intelligente/{mission_id}", response_model=DispatchResponse)
def attribution_intelligente(
    mission_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Attribution intelligente d'une mission"""
    try:
        dispatch = DispatchIntelligentService.attribution_intelligente(db, mission_id)
        return dispatch
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.post("/dispatch/{dispatch_id}/recalcul", response_model=DispatchResponse)
def recalcul_itineraire(
    dispatch_id: int,
    evenement: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Recalculer l'itinéraire suite à un événement"""
    try:
        dispatch = DispatchIntelligentService.recalcul_itineraire(db, dispatch_id, evenement)
        return dispatch
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/dispatch", response_model=List[DispatchResponse])
def lister_dispatches(
    statut: str = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Lister les dispatches"""
    query = db.query(Dispatch)
    if statut:
        query = query.filter(Dispatch.statut == statut)
    return query.all()


@router.get("/dispatch/{dispatch_id}", response_model=DispatchResponse)
def obtenir_dispatch(
    dispatch_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Obtenir un dispatch par ID"""
    dispatch = db.query(Dispatch).filter(Dispatch.id == dispatch_id).first()
    if not dispatch:
        raise HTTPException(status_code=404, detail="Dispatch non trouvé")
    return dispatch


@router.put("/dispatch/{dispatch_id}", response_model=DispatchResponse)
def modifier_dispatch(
    dispatch_id: int,
    dispatch_update: DispatchUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Modifier un dispatch"""
    dispatch = db.query(Dispatch).filter(Dispatch.id == dispatch_id).first()
    if not dispatch:
        raise HTTPException(status_code=404, detail="Dispatch non trouvé")
    
    for field, value in dispatch_update.model_dump(exclude_unset=True).items():
        setattr(dispatch, field, value)
    
    db.commit()
    db.refresh(dispatch)
    return dispatch


# ============ ARRETS ============

@router.post("/arrets", response_model=ArretResponse, status_code=status.HTTP_201_CREATED)
def creer_arret(
    arret: ArretCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Créer un arrêt"""
    arret_db = Arret(**arret.model_dump())
    db.add(arret_db)
    db.commit()
    db.refresh(arret_db)
    return arret_db


@router.get("/arrets/{dispatch_id}", response_model=List[ArretResponse])
def lister_arrets_dispatch(
    dispatch_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Lister les arrêts d'un dispatch"""
    return db.query(Arret).filter(Arret.dispatch_id == dispatch_id).order_by(Arret.ordre_sequence).all()


# ============ E-POD ============

@router.post("/pod", response_model=PODResponse, status_code=status.HTTP_201_CREATED)
def creer_pod(
    pod: PODCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Créer une preuve de livraison"""
    return EPODService.creer_pod(
        db,
        pod.livraison_id,
        pod.signature_client,
        pod.photo_marchandise,
        pod.coordonnees
    )


@router.post("/pod/{pod_id}/valider", response_model=PODResponse)
def valider_pod(
    pod_id: int,
    valide_par: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Valider une preuve de livraison"""
    try:
        return EPODService.valider_pod(db, pod_id, valide_par)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.post("/pod/{pod_id}/integration-facturation")
def integration_facturation(
    pod_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Intégration avec la facturation"""
    try:
        return EPODService.integration_facturation(db, pod_id)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.post("/pod/{pod_id}/archivage-legal")
def archivage_legal(
    pod_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Archivage légal des preuves"""
    try:
        return EPODService.archivage_legal(db, pod_id)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/pod", response_model=List[PODResponse])
def lister_pods(
    statut: str = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Lister les PODs"""
    query = db.query(POD)
    if statut:
        query = query.filter(POD.statut == statut)
    return query.all()


# ============ DOCUMENTS POD ============

@router.post("/documents-pod", response_model=DocumentPODResponse, status_code=status.HTTP_201_CREATED)
def ajouter_document_pod(
    document: DocumentPODCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Ajouter un document POD"""
    doc_db = DocumentPOD(**document.model_dump(), upload_par=current_user.id)
    db.add(doc_db)
    db.commit()
    db.refresh(doc_db)
    return doc_db


@router.get("/documents-pod/{pod_id}", response_model=List[DocumentPODResponse])
def lister_documents_pod(
    pod_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Lister les documents d'un POD"""
    return db.query(DocumentPOD).filter(DocumentPOD.pod_id == pod_id).all()


# ============ ANALYTICS ============

@router.get("/analytics/tableau-bord", response_model=TableauBordTransportResponse)
def tableau_bord_transport(
    date_dashboard: date,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Tableau de bord transport"""
    return AnalyticsTransportService.tableau_bord_transport(db, date_dashboard)


@router.get("/analytics/kpi", response_model=KPIResponse)
def kpi_transport(
    periode: str,
    conducteur_id: int = None,
    camion_id: int = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """KPIs transport"""
    return AnalyticsTransportService.kpi_transport(db, periode, conducteur_id, camion_id)


@router.get("/analytics/alertes", response_model=List[AlertPerformanceResponse])
def alertes_performance(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Alertes de performance"""
    return AnalyticsTransportService.alertes_performance(db)