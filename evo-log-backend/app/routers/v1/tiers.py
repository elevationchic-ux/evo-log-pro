"""
Tiers router - manages clients, suppliers, and partners
"""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List

from app.core.database import get_db
from app.schemas.tiers import TiersCreate, TiersUpdate, TiersResponse, ClientCreate, ClientResponse, FournisseurCreate, FournisseurResponse
from app.models.tiers import Tiers, Client, Fournisseur

router = APIRouter()


@router.get("/", response_model=List[TiersResponse])
async def get_all_tiers(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    """Get all tiers (clients, suppliers, partners)"""
    tiers = db.query(Tiers).offset(skip).limit(limit).all()
    return tiers


@router.get("/{tiers_id}", response_model=TiersResponse)
async def get_tiers(tiers_id: int, db: Session = Depends(get_db)):
    """Get a specific tiers by ID"""
    tiers = db.query(Tiers).filter(Tiers.id == tiers_id).first()
    if not tiers:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Tiers not found")
    return tiers


@router.post("/clients", response_model=ClientResponse, status_code=status.HTTP_201_CREATED)
async def create_client(client_data: ClientCreate, db: Session = Depends(get_db)):
    """Create a new client"""
    # Check if code exists
    if db.query(Tiers).filter(Tiers.code == client_data.code).first():
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Code already exists")
    
    db_client = Client(**client_data.model_dump())
    db.add(db_client)
    db.commit()
    db.refresh(db_client)
    return db_client


@router.get("/clients/", response_model=List[ClientResponse])
async def get_all_clients(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    """Get all clients"""
    clients = db.query(Client).offset(skip).limit(limit).all()
    return clients


@router.post("/fournisseurs", response_model=FournisseurResponse, status_code=status.HTTP_201_CREATED)
async def create_fournisseur(fournisseur_data: FournisseurCreate, db: Session = Depends(get_db)):
    """Create a new supplier"""
    if db.query(Tiers).filter(Tiers.code == fournisseur_data.code).first():
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Code already exists")
    
    db_fournisseur = Fournisseur(**fournisseur_data.model_dump())
    db.add(db_fournisseur)
    db.commit()
    db.refresh(db_fournisseur)
    return db_fournisseur


@router.get("/fournisseurs/", response_model=List[FournisseurResponse])
async def get_all_fournisseurs(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    """Get all suppliers"""
    fournisseurs = db.query(Fournisseur).offset(skip).limit(limit).all()
    return fournisseurs


@router.put("/{tiers_id}", response_model=TiersResponse)
async def update_tiers(tiers_id: int, tiers_data: TiersUpdate, db: Session = Depends(get_db)):
    """Update a tiers"""
    tiers = db.query(Tiers).filter(Tiers.id == tiers_id).first()
    if not tiers:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Tiers not found")
    
    for field, value in tiers_data.model_dump(exclude_unset=True).items():
        setattr(tiers, field, value)
    
    db.commit()
    db.refresh(tiers)
    return tiers


@router.delete("/{tiers_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_tiers(tiers_id: int, db: Session = Depends(get_db)):
    """Delete a tiers"""
    tiers = db.query(Tiers).filter(Tiers.id == tiers_id).first()
    if not tiers:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Tiers not found")
    
    db.delete(tiers)
    db.commit()
    return None