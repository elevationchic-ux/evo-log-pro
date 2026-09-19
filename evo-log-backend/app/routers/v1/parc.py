"""
Parc router - manages fleet and equipment
"""
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.orm import Session
from typing import List

from app.core.database import get_db
from app.schemas.parc import VehiculeCreate, VehiculeUpdate, VehiculeResponse, EquipementCreate, EquipementResponse
from app.models.parc import Vehicule, Equipement
from app.models.user import User
from app.core.security import decode_token

router = APIRouter()
security = HTTPBearer()


def get_parc_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: Session = Depends(get_db),
) -> User:
    payload = decode_token(credentials.credentials)
    subject = payload.get("sub")
    if not subject:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Session non valide.")
    query = db.query(User).filter(User.is_active == True)
    user = query.filter(User.id == int(subject)).first() if str(subject).isdigit() else query.filter(
        (User.username == str(subject)) | (User.email == str(subject))
    ).first()
    if not user:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Utilisateur non authentifié.")
    return user


@router.get("/vehicules", response_model=List[VehiculeResponse])
async def get_all_vehicules(skip: int = 0, limit: int = 100, db: Session = Depends(get_db), current_user: User = Depends(get_parc_user)):
    """Get all vehicles"""
    query = db.query(Vehicule)
    if not current_user.is_superuser:
        query = query.filter(Vehicule.company_id == current_user.company_id)
    vehicules = query.offset(skip).limit(limit).all()
    return vehicules


@router.post("/vehicules", response_model=VehiculeResponse, status_code=status.HTTP_201_CREATED)
async def create_vehicule(vehicule_data: VehiculeCreate, db: Session = Depends(get_db), current_user: User = Depends(get_parc_user)):
    """Create a new vehicle"""
    if current_user.company_id is None:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="L'utilisateur n'est rattaché à aucune société.")
    if db.query(Vehicule).filter(
        Vehicule.immatriculation == vehicule_data.immatriculation,
        Vehicule.company_id == current_user.company_id,
    ).first():
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Vehicle registration already exists")
    
    db_vehicule = Vehicule(**vehicule_data.model_dump(), company_id=current_user.company_id)
    db.add(db_vehicule)
    db.commit()
    db.refresh(db_vehicule)
    return db_vehicule


@router.get("/equipements", response_model=List[EquipementResponse])
async def get_all_equipements(skip: int = 0, limit: int = 100, db: Session = Depends(get_db), current_user: User = Depends(get_parc_user)):
    """Get all equipment"""
    equipements = db.query(Equipement).offset(skip).limit(limit).all()
    return equipements


@router.post("/equipements", response_model=EquipementResponse, status_code=status.HTTP_201_CREATED)
async def create_equipement(equipement_data: EquipementCreate, db: Session = Depends(get_db), current_user: User = Depends(get_parc_user)):
    """Create new equipment"""
    if db.query(Equipement).filter(Equipement.code == equipement_data.code).first():
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Equipment code already exists")
    
    db_equipement = Equipement(**equipement_data.model_dump())
    db.add(db_equipement)
    db.commit()
    db.refresh(db_equipement)
    return db_equipement


@router.get("/vehicles", response_model=List[VehiculeResponse], include_in_schema=False)
async def get_vehicles_alias(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_parc_user),
):
    return await get_all_vehicules(skip=skip, limit=limit, db=db, current_user=current_user)


@router.post("/vehicles", response_model=VehiculeResponse, status_code=status.HTTP_201_CREATED, include_in_schema=False)
async def create_vehicle_alias(
    vehicule_data: VehiculeCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_parc_user),
):
    return await create_vehicule(vehicule_data=vehicule_data, db=db, current_user=current_user)