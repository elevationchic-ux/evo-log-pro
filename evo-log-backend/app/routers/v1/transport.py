"""
Transport router - manages vehicles, drivers, and missions
"""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List

from app.core.database import get_db
from app.schemas.transport import CamionCreate, CamionUpdate, CamionResponse, ConducteurCreate, ConducteurResponse, MissionCreate, MissionUpdate, MissionResponse
from app.models.transport import Camion, Conducteur, Mission

router = APIRouter()


@router.get("/camions", response_model=List[CamionResponse])
async def get_all_camions(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    """Get all trucks"""
    camions = db.query(Camion).offset(skip).limit(limit).all()
    return camions


@router.post("/camions", response_model=CamionResponse, status_code=status.HTTP_201_CREATED)
async def create_camion(camion_data: CamionCreate, db: Session = Depends(get_db)):
    """Create a new truck"""
    if db.query(Camion).filter(Camion.immatriculation == camion_data.immatriculation).first():
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Truck registration already exists")
    
    db_camion = Camion(**camion_data.model_dump())
    db.add(db_camion)
    db.commit()
    db.refresh(db_camion)
    return db_camion


@router.get("/camions/{camion_id}", response_model=CamionResponse)
async def get_camion(camion_id: int, db: Session = Depends(get_db)):
    """Get a specific truck by ID"""
    camion = db.query(Camion).filter(Camion.id == camion_id).first()
    if not camion:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Truck not found")
    return camion


@router.put("/camions/{camion_id}", response_model=CamionResponse)
async def update_camion(camion_id: int, camion_data: CamionUpdate, db: Session = Depends(get_db)):
    """Update a truck"""
    camion = db.query(Camion).filter(Camion.id == camion_id).first()
    if not camion:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Truck not found")
    
    for field, value in camion_data.model_dump(exclude_unset=True).items():
        setattr(camion, field, value)
    
    db.commit()
    db.refresh(camion)
    return camion


@router.get("/conducteurs", response_model=List[ConducteurResponse])
async def get_all_conducteurs(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    """Get all drivers"""
    conducteurs = db.query(Conducteur).offset(skip).limit(limit).all()
    return conducteurs


@router.get("/chauffeurs", response_model=List[ConducteurResponse])
async def get_all_chauffeurs(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    """Compatibility alias for the frontend's driver terminology."""
    return db.query(Conducteur).offset(skip).limit(limit).all()


@router.post("/chauffeurs", response_model=ConducteurResponse, status_code=status.HTTP_201_CREATED)
async def create_chauffeur(conducteur_data: ConducteurCreate, db: Session = Depends(get_db)):
    """Compatibility alias that persists drivers in the conducteurs table."""
    return await create_conducteur(conducteur_data, db)


@router.post("/conducteurs", response_model=ConducteurResponse, status_code=status.HTTP_201_CREATED)
async def create_conducteur(conducteur_data: ConducteurCreate, db: Session = Depends(get_db)):
    """Create a new driver"""
    if db.query(Conducteur).filter(Conducteur.numero_permis == conducteur_data.numero_permis).first():
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="License number already exists")
    
    db_conducteur = Conducteur(**conducteur_data.model_dump())
    db.add(db_conducteur)
    db.commit()
    db.refresh(db_conducteur)
    return db_conducteur


# NOTE /chauffeurs/{id} et /chauffeurs/{id}/documents : ces routes sont SERVES
# par app/routers/v1/transport_exploitation.py (fiche complete avec statut
# d'derive, dossier de pieces en tableau nu  contrat des pages frontend et
# des tests de la Tranche D). transport.router etant monte AVANT exploitation,
# toute redeclaration ici masquerait la version riche : ne pas reintroduire.


@router.get("/missions", response_model=List[MissionResponse])
async def get_all_missions(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    """Get all missions"""
    missions = db.query(Mission).offset(skip).limit(limit).all()
    return missions


@router.get("/missions/{mission_id}", response_model=MissionResponse)
async def get_mission(mission_id: int, db: Session = Depends(get_db)):
    mission = db.query(Mission).filter(Mission.id == mission_id).first()
    if not mission:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Mission not found")
    return mission


@router.patch("/missions/{mission_id}/statut", response_model=MissionResponse)
async def update_mission_status(mission_id: int, mission_data: MissionUpdate, db: Session = Depends(get_db)):
    return await update_mission(mission_id, mission_data, db)


@router.post("/missions", response_model=MissionResponse, status_code=status.HTTP_201_CREATED)
async def create_mission(mission_data: MissionCreate, db: Session = Depends(get_db)):
    """Create a new mission"""
    db_mission = Mission(**mission_data.model_dump())
    db.add(db_mission)
    db.commit()
    db.refresh(db_mission)
    return db_mission


@router.put("/missions/{mission_id}", response_model=MissionResponse)
async def update_mission(mission_id: int, mission_data: MissionUpdate, db: Session = Depends(get_db)):
    """Update a mission"""
    mission = db.query(Mission).filter(Mission.id == mission_id).first()
    if not mission:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Mission not found")
    
    for field, value in mission_data.model_dump(exclude_unset=True).items():
        setattr(mission, field, value)
    
    db.commit()
    db.refresh(mission)
    return mission


@router.get("", response_model=List[MissionResponse])
@router.get("/", response_model=List[MissionResponse])
async def list_missions_root(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    """List all transport missions from root endpoint"""
    return db.query(Mission).offset(skip).limit(limit).all()


# ============ TMS VRP ROUTE OPTIMIZER ============
@router.post("/vrp-optimize")
async def optimiser_tournees_vrp(payload: dict = None):
    """Run VRP route optimizer with backhaul reduction and quai time-window constraints"""
    from app.services.transport_international_service import TMSAdvancedOptimizerService
    return TMSAdvancedOptimizerService.optimiser_tournees_vrp(payload or {})


# ============ CORRIDORS INTERNATIONAUX CEMAC ============
@router.get("/corridors-cemac")
async def obtenir_statut_corridors_cemac():
    """Live status of international CEMAC transit corridors with TRIE carnet & customs convoys"""
    from app.services.transport_international_service import TMSAdvancedOptimizerService
    return TMSAdvancedOptimizerService.get_corridor_cemac_status()


# ============ TCO FLOTTE & MAINTENANCE PRÉDICTIVE ============
@router.get("/flotte/tco")
async def obtenir_tco_flotte():
    """TCO cost per km and predictive maintenance alerts for the fleet"""
    from app.services.transport_international_service import TMSAdvancedOptimizerService
    return TMSAdvancedOptimizerService.get_tco_fleet_analytics()


# ============ KPIS TRANSPORT ============
@router.get("/kpis")
async def get_transport_kpis(db: Session = Depends(get_db)):
    """KPIs consolidés de la flotte et des opérations de transport.

    Filtres alignés sur les enums réels du modèle (CamionStatus, MissionStatus) :
    les anciennes comparisons sur 'disponible'/'en_mission'/'termine' faisaient
    planter l'endpoint (AttributeError) ou comptaient toujours 0.
    """
    from sqlalchemy import func
    from app.models.transport import CamionStatus, MissionStatus

    total_camions = db.query(func.count(Camion.id)).scalar() or 0
    camions_actifs = (
        db.query(func.count(Camion.id))
        .filter(Camion.status == CamionStatus.ACTIVE)
        .scalar() or 0
    )
    camions_en_maintenance = (
        db.query(func.count(Camion.id))
        .filter(Camion.status == CamionStatus.IN_MAINTENANCE)
        .scalar() or 0
    )

    # Camions affectés à une mission en cours (disponibles = actifs non affectés)
    camions_en_mission_rows = (
        db.query(Mission.camion_id)
        .filter(Mission.statut == MissionStatus.EN_COURS, Mission.camion_id != None)  # noqa: E711
        .distinct()
        .all()
    )
    camions_en_mission = len({r[0] for r in camions_en_mission_rows})
    camions_dispos = max(0, camions_actifs - camions_en_mission)

    total_chauffeurs = db.query(func.count(Conducteur.id)).scalar() or 0
    total_missions = db.query(func.count(Mission.id)).scalar() or 0
    missions_en_cours = (
        db.query(func.count(Mission.id))
        .filter(Mission.statut == MissionStatus.EN_COURS)
        .scalar() or 0
    )
    missions_terminees = (
        db.query(func.count(Mission.id))
        .filter(Mission.statut == MissionStatus.TERMINEE)
        .scalar() or 0
    )

    taux_dispo = round((camions_dispos / total_camions * 100), 1) if total_camions > 0 else 0.0

    return {
        "vehicules_total": total_camions,
        "vehicules_actifs": camions_actifs,
        "camions_disponibles": camions_dispos,
        "camions_en_mission": camions_en_mission,
        "camions_en_maintenance": camions_en_maintenance,
        "taux_disponibilite": taux_dispo,
        "chauffeurs_total": total_chauffeurs,
        "missions_total": total_missions,
        "missions_en_cours": missions_en_cours,
        "missions_terminees": missions_terminees
    }