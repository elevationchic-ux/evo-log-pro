"""
Parc router - manages fleet and equipment
"""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List

from app.core.database import get_db
from app.schemas.parc import VehiculeCreate, VehiculeUpdate, VehiculeResponse, EquipementCreate, EquipementResponse
from app.models.parc import Vehicule, Equipement

router = APIRouter()


@router.get("/vehicules", response_model=List[VehiculeResponse])
async def get_all_vehicules(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    """Get all vehicles"""
    vehicules = db.query(Vehicule).offset(skip).limit(limit).all()
    return vehicules


@router.post("/vehicules", response_model=VehiculeResponse, status_code=status.HTTP_201_CREATED)
async def create_vehicule(vehicule_data: VehiculeCreate, db: Session = Depends(get_db)):
    """Create a new vehicle"""
    if db.query(Vehicule).filter(Vehicule.immatriculation == vehicule_data.immatriculation).first():
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Vehicle registration already exists")
    
    db_vehicule = Vehicule(**vehicule_data.model_dump())
    db.add(db_vehicule)
    db.commit()
    db.refresh(db_vehicule)
    return db_vehicule


@router.get("/equipements", response_model=List[EquipementResponse])
async def get_all_equipements(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    """Get all equipment"""
    equipements = db.query(Equipement).offset(skip).limit(limit).all()
    return equipements


@router.post("/equipements", response_model=EquipementResponse, status_code=status.HTTP_201_CREATED)
async def create_equipement(equipement_data: EquipementCreate, db: Session = Depends(get_db)):
    """Create new equipment"""
    if db.query(Equipement).filter(Equipement.code == equipement_data.code).first():
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Equipment code already exists")
    
    db_equipement = Equipement(**equipement_data.model_dump())
    db.add(db_equipement)
    db.commit()
    db.refresh(db_equipement)
    return db_equipement