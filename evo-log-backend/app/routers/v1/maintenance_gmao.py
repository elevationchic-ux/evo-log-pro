"""Maintenance GMAO router - CMMS for Cameroon/CEMAC"""
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import datetime, date

from app.core.database import get_db
from app.core.security import get_current_user
from app.models.user import User
from app.schemas.maintenance_gmao import (
    OrdreMaintenanceCreate, OrdreMaintenanceUpdate, OrdreMaintenanceResponse,
    EquipementGMAOCreate, EquipementGMAOUpdate, EquipementGMAOResponse,
    PlanMaintenanceCreate, PlanMaintenanceUpdate, PlanMaintenanceResponse,
    PieceRechangeGMAOCreate, PieceRechangeGMAOUpdate, PieceRechangeGMAOResponse,
    CalibrationCreate, CalibrationUpdate, CalibrationResponse,
    PerformanceEquipementCreate, PerformanceEquipementResponse,
    RapportMaintenanceResponse
)
from app.services.maintenance_gmao_service import (
    OrdreMaintenanceService, EquipementGMAOService, PlanMaintenanceService,
    PieceRechangeGMAOService, CalibrationService, PerformanceEquipementService,
    MaintenanceReportingService
)
from app.models.maintenance_gmao import OrdreMaintenance, EquipementGMAO, PlanMaintenance, PieceRechangeGMAO, Calibration

router = APIRouter(tags=["Maintenance GMAO"])


def _valeur(brut):
    """Les colonnes Enum rendent leur valeur; les autres restent telles quelles."""
    return brut.value if hasattr(brut, "value") else brut


# ============ ORDRES MAINTENANCE ============
@router.get("/ordres")
def lister_ordres(
    skip: int = 0,
    limit: int = Query(100, le=500),
    statut: Optional[str] = None,
    equipement_id: Optional[int] = None,
    priorite: Optional[str] = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Liste des ordres de travail réellement enregistrés (GMAO)."""
    q = db.query(OrdreMaintenance)
    if statut:
        q = q.filter(OrdreMaintenance.statut == statut)
    if equipement_id:
        q = q.filter(OrdreMaintenance.equipement_id == equipement_id)
    if priorite:
        q = q.filter(OrdreMaintenance.priorite == priorite)
    total = q.count()
    rows = q.order_by(OrdreMaintenance.id.desc()).offset(skip).limit(limit).all()
    return {
        "items": [
            {
                "id": o.id,
                "numero_ordre": o.numero_ordre,
                "equipement_id": o.equipement_id,
                "type_maintenance": _valeur(o.type_maintenance),
                "priorite": _valeur(o.priorite),
                "statut": o.statut,
                "date_planifiee": o.date_planifiee.isoformat() if o.date_planifiee else None,
                "date_debut": o.date_debut.isoformat() if o.date_debut else None,
                "date_fin": o.date_fin.isoformat() if o.date_fin else None,
                "duree_estimee": o.duree_estimee,
                "duree_reelle": o.duree_reelle,
                "technicien_id": o.technicien_id,
                "description": o.description,
                "cout_total": float(o.cout_total) if o.cout_total is not None else None,
                "devise": o.devise,
            }
            for o in rows
        ],
        "total": total,
        "pending": False,
    }


@router.get("/ordres/{ordre_id}")
def detail_ordre(
    ordre_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Un ordre inconnu repond 404 : rien n'est invente pour remplir la page."""
    o = db.query(OrdreMaintenance).filter(OrdreMaintenance.id == ordre_id).first()
    if not o:
        raise HTTPException(status_code=404, detail="Ordre de maintenance introuvable")
    return {
        "id": o.id,
        "numero_ordre": o.numero_ordre,
        "equipement_id": o.equipement_id,
        "type_maintenance": _valeur(o.type_maintenance),
        "priorite": _valeur(o.priorite),
        "statut": o.statut,
        "date_creation": o.date_creation.isoformat() if o.date_creation else None,
        "date_planifiee": o.date_planifiee.isoformat() if o.date_planifiee else None,
        "date_debut": o.date_debut.isoformat() if o.date_debut else None,
        "date_fin": o.date_fin.isoformat() if o.date_fin else None,
        "duree_estimee": o.duree_estimee,
        "duree_reelle": o.duree_reelle,
        "description": o.description,
        "travaux": o.travaux,
        "technicien_id": o.technicien_id,
        "cout_pieces": float(o.cout_pieces) if o.cout_pieces is not None else None,
        "cout_main_oeuvre": float(o.cout_main_oeuvre) if o.cout_main_oeuvre is not None else None,
        "cout_total": float(o.cout_total) if o.cout_total is not None else None,
        "devise": o.devise,
        "observations": o.observations,
        "valide_par": o.valide_par,
        "date_validation": o.date_validation.isoformat() if o.date_validation else None,
        "pending": False,
    }


@router.post("/ordres", response_model=OrdreMaintenanceResponse, status_code=status.HTTP_201_CREATED)
def creer_ordre(
    ordre: OrdreMaintenanceCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Create maintenance work order"""
    return OrdreMaintenanceService.creer_ordre(
        db, ordre.numero_ordre, ordre.equipement_id, ordre.type_maintenance,
        ordre.priorite, ordre.description, ordre.date_planifiee, ordre.technicien_id
    )


@router.put("/ordres/{ordre_id}/completer", response_model=OrdreMaintenanceResponse)
def completer_ordre(
    ordre_id: int,
    date_fin: datetime,
    duree_reelle: int,
    observations: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Complete maintenance work order"""
    return OrdreMaintenanceService.completer_ordre(db, ordre_id, date_fin, duree_reelle, observations)


@router.put("/ordres/{ordre_id}", response_model=OrdreMaintenanceResponse)
def mettre_a_jour_ordre(
    ordre_id: int,
    ordre: OrdreMaintenanceUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Update maintenance work order"""
    o = db.query(OrdreMaintenance).filter(OrdreMaintenance.id == ordre_id).first()
    if not o:
        raise HTTPException(status_code=404, detail="Ordre de maintenance non trouvé")
    
    for field, value in ordre.model_dump(exclude_unset=True).items():
        setattr(o, field, value)
    
    db.commit()
    db.refresh(o)
    return o


# ============ EQUIPEMENTS ============
@router.get("/equipements")
def lister_equipements(
    skip: int = 0,
    limit: int = Query(100, le=500),
    statut: Optional[str] = None,
    type_equipement: Optional[str] = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Liste des équipements réellement saisis dans le parc GMAO."""
    q = db.query(EquipementGMAO)
    if statut:
        q = q.filter(EquipementGMAO.statut == statut)
    if type_equipement:
        q = q.filter(EquipementGMAO.type_equipement == type_equipement)
    total = q.count()
    rows = q.order_by(EquipementGMAO.id.desc()).offset(skip).limit(limit).all()
    return {
        "items": [
            {
                "id": e.id,
                "numero_serie": e.numero_serie,
                "designation": e.designation,
                "type_equipement": _valeur(e.type_equipement),
                "marque": e.marque,
                "modele": e.modele,
                "localisation": e.localisation,
                "departement": e.departement,
                "responsable": e.responsable,
                "statut": e.statut,
                "date_mise_service": e.date_mise_service.isoformat() if e.date_mise_service else None,
                "cout_achat": float(e.cout_achat) if e.cout_achat is not None else None,
                "devise": e.devise,
            }
            for e in rows
        ],
        "total": total,
        "pending": False,
    }


@router.post("/equipements", response_model=EquipementGMAOResponse, status_code=status.HTTP_201_CREATED)
def creer_equipement(
    equipement: EquipementGMAOCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Create equipment"""
    return EquipementGMAOService.creer_equipement(
        db, equipement.numero_serie, equipement.designation, equipement.type_equipement,
        equipement.marque, equipement.modele, equipement.localisation
    )


@router.put("/equipements/{equipement_id}", response_model=EquipementGMAOResponse)
def mettre_a_jour_equipement(
    equipement_id: int,
    equipement: EquipementGMAOUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Update equipment"""
    e = db.query(EquipementGMAO).filter(EquipementGMAO.id == equipement_id).first()
    if not e:
        raise HTTPException(status_code=404, detail="Équipement non trouvé")
    
    for field, value in equipement.model_dump(exclude_unset=True).items():
        setattr(e, field, value)
    
    db.commit()
    db.refresh(e)
    return e


# ============ PLANS MAINTENANCE ============
@router.post("/plans", response_model=PlanMaintenanceResponse, status_code=status.HTTP_201_CREATED)
def creer_plan(
    plan: PlanMaintenanceCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Create maintenance plan"""
    return PlanMaintenanceService.creer_plan(
        db, plan.numero_plan, plan.equipement_id, plan.type_maintenance,
        plan.frequence, plan.intervalle_jours, plan.date_debut
    )


@router.put("/plans/{plan_id}", response_model=PlanMaintenanceResponse)
def mettre_a_jour_plan(
    plan_id: int,
    plan: PlanMaintenanceUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Update maintenance plan"""
    p = db.query(PlanMaintenance).filter(PlanMaintenance.id == plan_id).first()
    if not p:
        raise HTTPException(status_code=404, detail="Plan de maintenance non trouvé")
    
    for field, value in plan.model_dump(exclude_unset=True).items():
        setattr(p, field, value)
    
    db.commit()
    db.refresh(p)
    return p


# ============ PIECES RECHANGE ============
@router.post("/pieces-rechange", response_model=PieceRechangeGMAOResponse, status_code=status.HTTP_201_CREATED)
def creer_piece(
    piece: PieceRechangeGMAOCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Create spare part"""
    return PieceRechangeGMAOService.creer_piece(
        db, piece.reference, piece.designation, piece.equipement_id,
        piece.categorie, piece.prix_unitaire
    )


@router.put("/pieces-rechange/{piece_id}", response_model=PieceRechangeGMAOResponse)
def mettre_a_jour_piece(
    piece_id: int,
    piece: PieceRechangeGMAOUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Update spare part"""
    p = db.query(PieceRechangeGMAO).filter(PieceRechangeGMAO.id == piece_id).first()
    if not p:
        raise HTTPException(status_code=404, detail="Pièce de rechange non trouvée")
    
    for field, value in piece.model_dump(exclude_unset=True).items():
        setattr(p, field, value)
    
    db.commit()
    db.refresh(p)
    return p


# ============ CALIBRATIONS ============
@router.post("/calibrations", response_model=CalibrationResponse, status_code=status.HTTP_201_CREATED)
def creer_calibration(
    calibration: CalibrationCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Create calibration record"""
    return CalibrationService.creer_calibration(
        db, calibration.numero_calibration, calibration.equipement_id,
        calibration.instrument, calibration.date_calibration, calibration.intervalle_mois
    )


@router.put("/calibrations/{calibration_id}", response_model=CalibrationResponse)
def mettre_a_jour_calibration(
    calibration_id: int,
    calibration: CalibrationUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Update calibration record"""
    c = db.query(Calibration).filter(Calibration.id == calibration_id).first()
    if not c:
        raise HTTPException(status_code=404, detail="Calibration non trouvée")
    
    for field, value in calibration.model_dump(exclude_unset=True).items():
        setattr(c, field, value)
    
    db.commit()
    db.refresh(c)
    return c


# ============ PERFORMANCE ============
@router.post("/performance", response_model=PerformanceEquipementResponse, status_code=status.HTTP_201_CREATED)
def enregistrer_performance(
    performance: PerformanceEquipementCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Record equipment performance"""
    return PerformanceEquipementService.enregistrer_performance(
        db, performance.equipement_id, performance.periode, performance.temps_fonctionnement,
        performance.temps_arret, performance.nombre_pannes, performance.temps_maintenance
    )


@router.get("/equipements/{equipement_id}/rapport", response_model=RapportMaintenanceResponse)
def rapport_maintenance(
    equipement_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Generate maintenance report"""
    return MaintenanceReportingService.rapport_maintenance(db, equipement_id)
