"""
Admin Agency router - manages company agencies and branches
Administration des agences et succursales régionales (Douala, Kribi, Yaoundé, Garoua)
"""
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session
from sqlalchemy import func, desc, or_
from typing import Optional, List
from datetime import datetime
from pydantic import BaseModel

from app.core.database import get_db
from app.core.security import get_current_user
from app.models.user import User
from app.models.agency import Agency

router = APIRouter()


class AgencyCreate(BaseModel):
    code: str
    name: str
    address: Optional[str] = None
    city: Optional[str] = "Douala"
    country: Optional[str] = "Cameroun"
    phone: Optional[str] = None
    email: Optional[str] = None
    is_active: Optional[bool] = True
    is_headquarters: Optional[bool] = False
    organization_id: Optional[int] = None


class AgencyUpdate(BaseModel):
    name: Optional[str] = None
    address: Optional[str] = None
    city: Optional[str] = None
    country: Optional[str] = None
    phone: Optional[str] = None
    email: Optional[str] = None
    is_active: Optional[bool] = None
    is_headquarters: Optional[bool] = None


@router.get("/")
async def get_agencies(
    city: Optional[str] = Query(None),
    is_active: Optional[bool] = Query(None),
    search: Optional[str] = Query(None),
    skip: int = 0,
    limit: int = 50,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Liste de toutes les agences et succursales de l'entreprise"""
    query = db.query(Agency)

    if city:
        query = query.filter(Agency.city.ilike(f"%{city}%"))
    if is_active is not None:
        query = query.filter(Agency.is_active == is_active)
    if search:
        query = query.filter(
            or_(
                Agency.code.ilike(f"%{search}%"),
                Agency.name.ilike(f"%{search}%"),
                Agency.city.ilike(f"%{search}%"),
                Agency.email.ilike(f"%{search}%")
            )
        )

    total = query.count()
    items = query.order_by(Agency.is_headquarters.desc(), Agency.name.asc()).offset(skip).limit(limit).all()

    return {
        "total": total,
        "skip": skip,
        "limit": limit,
        "items": [
            {
                "id": a.id,
                "code": a.code,
                "name": a.name,
                "address": a.address,
                "city": a.city,
                "country": a.country,
                "phone": a.phone,
                "email": a.email,
                "is_active": a.is_active,
                "is_headquarters": a.is_headquarters,
                "users_count": len(a.users) if a.users else 0,
                "created_at": a.created_at.isoformat() if a.created_at else None
            }
            for a in items
        ]
    }


@router.get("/stats")
async def get_agency_stats(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Statistiques de déploiement territorial des agences"""
    total = db.query(func.count(Agency.id)).scalar() or 0
    actives = db.query(func.count(Agency.id)).filter(Agency.is_active == True).scalar() or 0
    sieges = db.query(func.count(Agency.id)).filter(Agency.is_headquarters == True).scalar() or 0

    repartition_villes = db.query(
        Agency.city,
        func.count(Agency.id)
    ).group_by(Agency.city).all()

    return {
        "total_agences": total,
        "actives": actives,
        "sieges_sociaux": sieges,
        "repartition_villes": [
            {"ville": ville or "Non renseigné", "agences": count}
            for ville, count in repartition_villes
        ]
    }


@router.post("/", status_code=status.HTTP_201_CREATED)
async def create_agency(
    payload: AgencyCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Crée une nouvelle agence ou succursale"""
    # Vérification code unique
    existing = db.query(Agency).filter(Agency.code == payload.code).first()
    if existing:
        raise HTTPException(status_code=400, detail=f"Une agence avec le code '{payload.code}' existe déjà")

    agency = Agency(
        code=payload.code.upper(),
        name=payload.name,
        address=payload.address,
        city=payload.city or "Douala",
        country=payload.country or "Cameroun",
        phone=payload.phone,
        email=payload.email,
        is_active=payload.is_active if payload.is_active is not None else True,
        is_headquarters=payload.is_headquarters or False,
        organization_id=payload.organization_id
    )

    db.add(agency)
    db.commit()
    db.refresh(agency)

    return {
        "message": "Agence créée avec succès",
        "id": agency.id,
        "code": agency.code,
        "name": agency.name
    }


@router.get("/{id}")
async def get_agency_detail(
    id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Détail d'une agence avec la liste de ses collaborateurs"""
    agency = db.query(Agency).filter(Agency.id == id).first()
    if not agency:
        raise HTTPException(status_code=404, detail=f"Agence #{id} non trouvée")

    return {
        "id": agency.id,
        "code": agency.code,
        "name": agency.name,
        "address": agency.address,
        "city": agency.city,
        "country": agency.country,
        "phone": agency.phone,
        "email": agency.email,
        "is_active": agency.is_active,
        "is_headquarters": agency.is_headquarters,
        "created_at": agency.created_at.isoformat() if agency.created_at else None,
        "collaborateurs": [
            {
                "id": u.id,
                "email": u.email,
                "full_name": u.full_name,
                "role": u.role.value if hasattr(u.role, 'value') else str(u.role),
                "is_active": u.is_active
            }
            for u in (agency.users or [])
        ]
    }


@router.put("/{id}")
async def update_agency(
    id: int,
    payload: AgencyUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Met à jour les informations d'une agence"""
    agency = db.query(Agency).filter(Agency.id == id).first()
    if not agency:
        raise HTTPException(status_code=404, detail=f"Agence #{id} non trouvée")

    data = payload.dict(exclude_unset=True)
    for field, value in data.items():
        setattr(agency, field, value)

    agency.updated_at = datetime.utcnow()
    db.commit()
    db.refresh(agency)

    return {"message": "Agence mise à jour avec succès", "id": agency.id}


@router.delete("/{id}")
async def delete_agency(
    id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Désactive ou supprime une agence"""
    agency = db.query(Agency).filter(Agency.id == id).first()
    if not agency:
        raise HTTPException(status_code=404, detail=f"Agence #{id} non trouvée")

    if agency.users and len(agency.users) > 0:
        # Désactivation douce si des utilisateurs y sont rattachés
        agency.is_active = False
        db.commit()
        return {"message": f"Agence #{id} désactivée (car des utilisateurs y sont associés)"}

    db.delete(agency)
    db.commit()
    return {"message": f"Agence #{id} supprimée définitivement"}