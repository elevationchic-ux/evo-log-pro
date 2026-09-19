from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any
from datetime import datetime

from app.database import get_db
from app.models.organization import Organization
from app.models.user import User
from app.models.agency import Agency
from app.utils.rbac import get_current_user

router = APIRouter()

# ─── Pydantic Schemas ───
class OrganizationCreateSchema(BaseModel):
    code: str = Field(..., example="ORG-CADC")
    name: str = Field(..., example="Transport Logistics SARL")
    slug: str = Field(..., example="transport-logistics-sarl")
    plan: str = Field("STARTER", example="STARTER")
    max_users: int = Field(10, example=15)
    allowed_modules: Optional[List[str]] = [
        "transport", "magasin", "finance", "parc", "master-data", "qhse", 
        "documents", "acconage", "maintenance", "fuelguard", "cotations"
    ]
    tenant_config: Optional[Dict[str, Any]] = None

class OrganizationUpdateSchema(BaseModel):
    name: Optional[str] = None
    plan: Optional[str] = None
    status: Optional[str] = None
    max_users: Optional[int] = None
    allowed_modules: Optional[List[str]] = None
    tenant_config: Optional[Dict[str, Any]] = None
    is_active: Optional[bool] = None

class OrganizationResponseSchema(BaseModel):
    id: int
    code: str
    name: str
    slug: str
    plan: str
    status: str
    max_users: int
    allowed_modules: Optional[List[str]]
    tenant_config: Optional[Dict[str, Any]]
    is_active: bool
    created_at: datetime
    user_count: Optional[int] = 0
    agency_count: Optional[int] = 0

    class Config:
        from_attributes = True

# ─── Superadmin Verification ───
def require_superadmin(user: User = Depends(get_current_user)):
    is_sup = bool(getattr(user, 'is_superuser', False) or getattr(user, 'is_superadmin', False))
    user_roles = [getattr(r, 'name', '') or getattr(r, 'code', '') for r in (user.roles or [])]
    if not is_sup and "SUPER_ADMIN" not in user_roles and "SUPERADMIN" not in user_roles:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Accès interdit : Privilèges Super Administrateur SaaS requis pour accéder à cette console."
        )
    return user

# ─── Endpoints ───
@router.get("/organizations", response_model=List[OrganizationResponseSchema])
def list_organizations(
    db: Session = Depends(get_db),
    admin: User = Depends(require_superadmin)
):
    """List all tenant organizations registered on the platform."""
    orgs = db.query(Organization).all()
    results = []
    for org in orgs:
        u_count = db.query(User).filter(User.organization_id == org.id).count()
        a_count = db.query(Agency).filter(Agency.organization_id == org.id).count()
        res = OrganizationResponseSchema(
            id=org.id,
            code=org.code,
            name=org.name,
            slug=org.slug,
            plan=org.plan,
            status=org.status,
            max_users=org.max_users,
            allowed_modules=org.allowed_modules,
            tenant_config=org.tenant_config,
            is_active=org.is_active,
            created_at=org.created_at,
            user_count=u_count,
            agency_count=a_count
        )
        results.append(res)
    return results

@router.post("/organizations", response_model=OrganizationResponseSchema, status_code=status.HTTP_201_CREATED)
def create_organization(
    payload: OrganizationCreateSchema,
    db: Session = Depends(get_db),
    admin: User = Depends(require_superadmin)
):
    """Create and provision a new tenant organization."""
    existing = db.query(Organization).filter(
        (Organization.code == payload.code) | (Organization.slug == payload.slug)
    ).first()
    if existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="An Organization with this code or slug already exists."
        )

    default_config = {
        "warehouse_management_mode": "ZONES",
        "document_numbering_prefix": f"EVO-{payload.code[:4].upper()}-",
        "logo_url": None,
        "primary_color": "#4f46e5",
        "legal_name": payload.name,
        "tax_id": None,
        "address": None,
        "city": "Douala",
        "country": "Cameroun",
        "currency": "XAF",
        "payment_terms_days": 30,
        "allow_offline_mode": True
    }
    if payload.tenant_config:
        default_config.update(payload.tenant_config)

    org = Organization(
        code=payload.code,
        name=payload.name,
        slug=payload.slug,
        plan=payload.plan,
        status="ACTIVE",
        max_users=payload.max_users,
        allowed_modules=payload.allowed_modules,
        tenant_config=default_config,
        is_active=True
    )
    db.add(org)
    db.commit()
    db.refresh(org)

    # Create primary default agency for tenant
    agency = Agency(
        organization_id=org.id,
        code=f"AG-{org.code}-01",
        nom=f"Siège Principal - {org.name}",
        ville="Douala",
        pays="Cameroun",
        is_active=True
    )
    db.add(agency)
    db.commit()

    return OrganizationResponseSchema(
        id=org.id,
        code=org.code,
        name=org.name,
        slug=org.slug,
        plan=org.plan,
        status=org.status,
        max_users=org.max_users,
        allowed_modules=org.allowed_modules,
        tenant_config=org.tenant_config,
        is_active=org.is_active,
        created_at=org.created_at,
        user_count=0,
        agency_count=1
    )

@router.get("/organizations/{org_id}", response_model=OrganizationResponseSchema)
def get_organization_detail(
    org_id: int,
    db: Session = Depends(get_db),
    admin: User = Depends(require_superadmin)
):
    org = db.query(Organization).filter(Organization.id == org_id).first()
    if not org:
        raise HTTPException(status_code=404, detail="Organization not found")
    u_count = db.query(User).filter(User.organization_id == org.id).count()
    a_count = db.query(Agency).filter(Agency.organization_id == org.id).count()
    return OrganizationResponseSchema(
        id=org.id,
        code=org.code,
        name=org.name,
        slug=org.slug,
        plan=org.plan,
        status=org.status,
        max_users=org.max_users,
        allowed_modules=org.allowed_modules,
        tenant_config=org.tenant_config,
        is_active=org.is_active,
        created_at=org.created_at,
        user_count=u_count,
        agency_count=a_count
    )

@router.patch("/organizations/{org_id}", response_model=OrganizationResponseSchema)
def update_organization(
    org_id: int,
    payload: OrganizationUpdateSchema,
    db: Session = Depends(get_db),
    admin: User = Depends(require_superadmin)
):
    org = db.query(Organization).filter(Organization.id == org_id).first()
    if not org:
        raise HTTPException(status_code=404, detail="Organization not found")

    if payload.name is not None:
        org.name = payload.name
    if payload.plan is not None:
        org.plan = payload.plan
    if payload.status is not None:
        org.status = payload.status
    if payload.max_users is not None:
        org.max_users = payload.max_users
    if payload.allowed_modules is not None:
        org.allowed_modules = payload.allowed_modules
    if payload.is_active is not None:
        org.is_active = payload.is_active
    if payload.tenant_config is not None:
        curr_cfg = org.tenant_config or {}
        curr_cfg.update(payload.tenant_config)
        org.tenant_config = curr_cfg

    db.commit()
    db.refresh(org)
    u_count = db.query(User).filter(User.organization_id == org.id).count()
    a_count = db.query(Agency).filter(Agency.organization_id == org.id).count()
    return OrganizationResponseSchema(
        id=org.id,
        code=org.code,
        name=org.name,
        slug=org.slug,
        plan=org.plan,
        status=org.status,
        max_users=org.max_users,
        allowed_modules=org.allowed_modules,
        tenant_config=org.tenant_config,
        is_active=org.is_active,
        created_at=org.created_at,
        user_count=u_count,
        agency_count=a_count
    )
