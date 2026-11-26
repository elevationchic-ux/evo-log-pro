"""
Transit router - manages customs and transit operations
"""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from datetime import datetime

from app.core.database import get_db
from app.schemas.transit import DossierTransitCreate, DossierTransitUpdate, DossierTransitResponse, DeclarationDouaniereCreate, DeclarationDouaniereResponse
from app.models.transit import DossierTransit, DeclarationDouaniere

router = APIRouter()


@router.get("/dossiers", response_model=List[DossierTransitResponse])
async def get_all_dossiers(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    """Get all transit dossiers"""
    dossiers = db.query(DossierTransit).offset(skip).limit(limit).all()
    return dossiers


@router.post("/dossiers", response_model=DossierTransitResponse, status_code=status.HTTP_201_CREATED)
async def create_dossier_transit(dossier_data: DossierTransitCreate, db: Session = Depends(get_db)):
    """Create a new transit dossier"""
    import random
    import string
    
    numero_dossier = f"DTR-{datetime.now().strftime('%Y%m%d')}-{''.join(random.choices(string.ascii_uppercase + string.digits, k=6))}"
    
    db_dossier = DossierTransit(numero_dossier=numero_dossier, **dossier_data.model_dump())
    db.add(db_dossier)
    db.commit()
    db.refresh(db_dossier)
    return db_dossier


@router.post("/declarations", response_model=DeclarationDouaniereResponse, status_code=status.HTTP_201_CREATED)
async def create_declaration_douaniere(declaration_data: DeclarationDouaniereCreate, db: Session = Depends(get_db)):
    """Create a new customs declaration - SYDONIA+ integration"""
    import random
    import string
    
    numero_declaration = f"DEC-{datetime.now().strftime('%Y%m%d')}-{''.join(random.choices(string.ascii_uppercase + string.digits, k=6))}"
    
    db_declaration = DeclarationDouaniere(numero_declaration=numero_declaration, **declaration_data.model_dump())
    db.add(db_declaration)
    db.commit()
    db.refresh(db_declaration)
    return db_declaration