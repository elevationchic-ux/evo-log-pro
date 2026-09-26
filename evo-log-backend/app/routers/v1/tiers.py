"""
Tiers router - manages clients, suppliers, and partners
"""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List, Optional

from app.core.database import get_db
from app.schemas.tiers import TiersCreate, TiersUpdate, TiersResponse, ClientCreate, ClientResponse, FournisseurCreate, FournisseurResponse
from app.models.tiers import Tiers, Client, Fournisseur, Partenaire, TiersType

router = APIRouter()


# ORDRE DES ROUTES : les chemins litteraux (/clients/, /fournisseurs/) doivent
# etre declares AVANT /{tiers_id}. Starlette traduit un parametre `{tiers_id}`
# en `[^/]+` (et non `[0-9]+`) : declaree en premier, la route parametrique
# capturait « clients » et renvoyait un 422, ce qui vidait silencieusement la
# liste des fournisseurs cote achat.
@router.get("/", response_model=List[TiersResponse])
@router.get("", response_model=List[TiersResponse], include_in_schema=False)
async def get_all_tiers(
    skip: int = 0,
    limit: int = 100,
    type_tiers: Optional[str] = None,
    db: Session = Depends(get_db),
):
    """Get all tiers (clients, suppliers, partners).

    `type_tiers` etait envoye par le frontend mais jamais applique : un ecran
    « clients » pouvait donc proposer des fournisseurs. Le type est stocke en
    Enum, on filtre sur l'enum et non sur la chaine.
    """
    query = db.query(Tiers)
    if type_tiers:
        try:
            type_enum = TiersType(type_tiers.lower())
        except ValueError:
            raise HTTPException(
                status_code=422,
                detail=f"type_tiers inconnu: {type_tiers} (attendu: client, fournisseur, partenaire)",
            )
        query = query.filter(Tiers.type == type_enum)
    return query.offset(skip).limit(limit).all()


@router.post("/", response_model=TiersResponse, status_code=status.HTTP_201_CREATED)
@router.post("", response_model=TiersResponse, status_code=status.HTTP_201_CREATED, include_in_schema=False)
async def create_tiers(tiers_data: TiersCreate, db: Session = Depends(get_db)):
    """Creer un tiers generique (client/fournisseur/partenaire).

    Le front maitre-donnees poste ici ; on resout la sous-classe heritee
    correspondant au type pour que les tables jointes (clients, fournisseurs,
    partenaires) restent coherentes avec le polymorphisme SQLAlchemy.
    """
    if db.query(Tiers).filter(Tiers.code == tiers_data.code).first():
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Code already exists")

    type_enum = TiersType(tiers_data.type)
    klass = {
        TiersType.CLIENT: Client,
        TiersType.FOURNISSEUR: Fournisseur,
        TiersType.PARTENAIRE: Partenaire,
    }.get(type_enum, Tiers)

    payload = tiers_data.model_dump()
    payload["type"] = type_enum
    row = klass(**payload)
    db.add(row)
    db.commit()
    db.refresh(row)
    return row


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


@router.get("/{tiers_id}", response_model=TiersResponse)
async def get_tiers(tiers_id: int, db: Session = Depends(get_db)):
    """Get a specific tiers by ID"""
    tiers = db.query(Tiers).filter(Tiers.id == tiers_id).first()
    if not tiers:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Tiers not found")
    return tiers


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
