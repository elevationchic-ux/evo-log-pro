"""Maintenance GMAO router - CMMS for Cameroon/CEMAC"""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
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


# ============ ORDRES MAINTENANCE ============
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
