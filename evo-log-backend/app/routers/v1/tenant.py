"""Tenant router - Multi-tenant SAAS management for Companies, Subscriptions, B2B Portals"""
from fastapi import APIRouter, Depends, HTTPException, status, UploadFile, File
from sqlalchemy import or_
from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import datetime, date
import json, os, shutil, uuid

from app.core.database import get_db
from app.core.security import (
    get_current_user, get_password_hash, validate_password_strength,
)
from app.utils.rbac import (
    require_superadmin, require_company_admin, resolve_scope_company_id,
    _is_superadmin,
)
from app.models.user import User
from app.schemas.tenant import (
    CompanyCreate, CompanyUpdate, CompanyResponse,
    SubscriptionPlanCreate, SubscriptionPlanUpdate, SubscriptionPlanResponse,
    SubscriptionCreate, SubscriptionUpdate, SubscriptionResponse,
    DepartmentCreate, DepartmentUpdate, DepartmentResponse,
    B2BPortalCreate, B2BPortalUpdate, B2BPortalResponse,
    RapportCompaniesResponse, RapportRevenusResponse
)
from app.services.tenant_service import (
    CompanyService, SubscriptionPlanService, SubscriptionService,
    DepartmentService, B2BPortalService, TenantReportingService
)
from app.models.tenant import Company, SubscriptionPlan, Subscription, Department, B2BPortal

router = APIRouter(tags=["Tenant Management"])


# ============ COMPANY PROFILE (tenant's own company) ============
@router.get("/company-profile")
def get_company_profile(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Return the legal profile of the current user's company (for document headers)"""
    company: Optional[Company] = None
    if hasattr(current_user, 'company_id') and current_user.company_id:
        company = db.query(Company).filter(Company.id == current_user.company_id).first()
    elif hasattr(current_user, 'company') and current_user.company:
        company = current_user.company
    if not company:
        return {}
    return {
        "raison_sociale": company.nom,
        "sigle": company.sigle,
        "forme_juridique": company.legal_form,
        "capital_social": company.capital_social,
        "nif": company.tax_id,
        "rccm": company.rccm,
        "agrement_douane": company.agrement_douane,
        "agrement_pad": company.agrement_pad,
        "agrement_pak": company.agrement_pak,
        "adresse": company.adresse,
        "ville": company.ville,
        "pays": company.pays,
        "telephone": company.telephone,
        "email": company.email,
        "site_web": company.website,
        "logo_url": company.logo_url,
        "rib": company.rib,
    }


@router.put("/company-profile/legal")
def update_company_legal_info(
    payload: dict,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Update legal information of the current tenant's company (Super Admin or tenant Admin)"""
    if not current_user.is_superuser and getattr(current_user, 'role_level', 99) > 1:
        raise HTTPException(status_code=403, detail="Admin requis pour modifier les informations légales")

    company: Optional[Company] = None
    if current_user.is_superuser and payload.get('company_id'):
        company = db.query(Company).filter(Company.id == payload['company_id']).first()
    elif hasattr(current_user, 'company_id') and current_user.company_id:
        company = db.query(Company).filter(Company.id == current_user.company_id).first()

    if not company:
        raise HTTPException(status_code=404, detail="Société non trouvée")

    allowed_fields = ['nom', 'sigle', 'legal_form', 'capital_social', 'tax_id', 'rccm',
                      'agrement_douane', 'agrement_pad', 'agrement_pak', 'rib',
                      'adresse', 'ville', 'pays', 'telephone', 'email', 'website',
                      'primary_color', 'secondary_color']
    for field in allowed_fields:
        if field in payload:
            setattr(company, field, payload[field])

    db.commit()
    db.refresh(company)
    return {"success": True, "message": "Informations légales mises à jour"}


@router.post("/company-profile/upload-logo")
def upload_company_logo(
    file: UploadFile = File(...),
    company_id: Optional[int] = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Upload company logo (PNG/JPG/SVG). Stored and URL saved to company profile."""
    if not current_user.is_superuser and getattr(current_user, 'role_level', 99) > 1:
        raise HTTPException(status_code=403, detail="Admin requis")

    company: Optional[Company] = None
    if current_user.is_superuser and company_id:
        company = db.query(Company).filter(Company.id == company_id).first()
    elif hasattr(current_user, 'company_id') and current_user.company_id:
        company = db.query(Company).filter(Company.id == current_user.company_id).first()

    if not company:
        raise HTTPException(status_code=404, detail="Société non trouvée")

    # Validate file type
    allowed_types = {'image/png', 'image/jpeg', 'image/svg+xml', 'image/webp'}
    if file.content_type not in allowed_types:
        raise HTTPException(status_code=400, detail="Format non autorisé. PNG, JPG, SVG, WEBP uniquement.")

    # Save file
    upload_dir = os.path.join("static", "logos")
    os.makedirs(upload_dir, exist_ok=True)
    ext = file.filename.split('.')[-1] if file.filename and '.' in file.filename else 'png'
    filename = f"logo_{company.code}_{uuid.uuid4().hex[:8]}.{ext}"
    filepath = os.path.join(upload_dir, filename)
    with open(filepath, "wb") as f:
        shutil.copyfileobj(file.file, f)

    logo_url = f"/static/logos/{filename}"
    company.logo_url = logo_url
    db.commit()
    return {"success": True, "logo_url": logo_url}


@router.put("/companies/{company_id}/modules")
def update_company_modules(
    company_id: int,
    payload: dict,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Update active module flags for a tenant company (Super Admin only)"""
    if not current_user.is_superuser:
        raise HTTPException(status_code=403, detail="Super Admin required")
    company = db.query(Company).filter(Company.id == company_id).first()
    if not company:
        raise HTTPException(status_code=404, detail="Société non trouvée")
    modules = payload.get('modules_actives', [])
    company.modules_actives = json.dumps(modules)
    db.commit()
    return {"success": True, "modules_actives": modules}




# ============ COMPANIES ============
@router.post("/companies", response_model=CompanyResponse, status_code=status.HTTP_201_CREATED)
def creer_company(
    company: CompanyCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Create a new company (Super Admin only)"""
    if not current_user.is_superuser:
        raise HTTPException(status_code=403, detail="Super Admin required")
    
    return CompanyService.creer_company(
        db, company.code, company.nom, company.legal_form, company.tax_id,
        company.email, company.telephone, company.subscription_plan_id, current_user.id
    )


@router.put("/companies/{company_id}/activer", response_model=CompanyResponse)
def activer_company(
    company_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Activate a company"""
    if not current_user.is_superuser:
        raise HTTPException(status_code=403, detail="Super Admin required")
    
    return CompanyService.activer_company(db, company_id)


@router.put("/companies/{company_id}/suspendre", response_model=CompanyResponse)
def suspendre_company(
    company_id: int,
    raison: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Suspend a company"""
    if not current_user.is_superuser:
        raise HTTPException(status_code=403, detail="Super Admin required")
    
    return CompanyService.suspendre_company(db, company_id, raison)


@router.put("/companies/{company_id}/quota", response_model=CompanyResponse)
def mettre_a_jour_quota(
    company_id: int,
    max_users: int,
    max_storage_mb: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Update company quotas"""
    if not current_user.is_superuser:
        raise HTTPException(status_code=403, detail="Super Admin required")
    
    return CompanyService.mettre_a_jour_quota(db, company_id, max_users, max_storage_mb)


@router.get("/companies", response_model=List[CompanyResponse])
def lister_companies(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """List all companies (Super Admin only)"""
    if not current_user.is_superuser:
        raise HTTPException(status_code=403, detail="Super Admin required")
    
    return db.query(Company).all()


# ============ SUBSCRIPTION PLANS ============
@router.post("/plans", response_model=SubscriptionPlanResponse, status_code=status.HTTP_201_CREATED)
def creer_plan(
    plan: SubscriptionPlanCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Create a subscription plan (Super Admin only)"""
    if not current_user.is_superuser:
        raise HTTPException(status_code=403, detail="Super Admin required")
    
    return SubscriptionPlanService.creer_plan(
        db, plan.code, plan.nom, plan.type_plan, plan.prix_mensuel,
        plan.prix_annuel, plan.max_users, plan.max_storage_mb
    )


@router.get("/plans", response_model=List[SubscriptionPlanResponse])
def lister_plans(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """List all subscription plans"""
    return db.query(SubscriptionPlan).filter(SubscriptionPlan.is_active == True).all()


# ============ SUBSCRIPTIONS ============
@router.post("/subscriptions", response_model=SubscriptionResponse, status_code=status.HTTP_201_CREATED)
def creer_subscription(
    subscription: SubscriptionCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Create a subscription"""
    if not current_user.is_superuser:
        raise HTTPException(status_code=403, detail="Super Admin required")
    
    return SubscriptionService.creer_subscription(
        db, subscription.company_id, subscription.plan_id,
        subscription.start_date, subscription.end_date, subscription.amount
    )


@router.put("/subscriptions/{subscription_id}/renouveler", response_model=SubscriptionResponse)
def renouveler_subscription(
    subscription_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Renew a subscription"""
    if not current_user.is_superuser:
        raise HTTPException(status_code=403, detail="Super Admin required")
    
    return SubscriptionService.renouveler_subscription(db, subscription_id)


# ============ DEPARTMENTS ============
@router.post("/departments", response_model=DepartmentResponse, status_code=status.HTTP_201_CREATED)
def creer_department(
    department: DepartmentCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Create a department (Admin Entreprise)"""
    # Check if user is admin of the company
    if current_user.role_level > 1:
        raise HTTPException(status_code=403, detail="Admin Entreprise required")
    
    return DepartmentService.creer_department(
        db, department.company_id, department.code, department.nom,
        department.description, department.manager_id
    )


@router.get("/companies/{company_id}/departments", response_model=List[DepartmentResponse])
def lister_departments(
    company_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """List departments for a company"""
    return db.query(Department).filter(Department.company_id == company_id).all()


# ============ B2B PORTALS ============
@router.put("/portals/{portal_id}/personnaliser", response_model=B2BPortalResponse)
def personnaliser_portal(
    portal_id: int,
    primary_color: str,
    secondary_color: str,
    logo_url: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Customize B2B portal"""
    if current_user.role_level > 1:
        raise HTTPException(status_code=403, detail="Admin Entreprise required")
    
    return B2BPortalService.personnaliser_portal(
        db, portal_id, primary_color, secondary_color, logo_url
    )


@router.get("/companies/{company_id}/portal", response_model=B2BPortalResponse)
def get_portal(
    company_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get B2B portal for a company"""
    portal = db.query(B2BPortal).filter(B2BPortal.company_id == company_id).first()
    if not portal:
        raise HTTPException(status_code=404, detail="Portal non trouvé")
    return portal


# ============ REPORTING ============
@router.get("/reports/companies", response_model=RapportCompaniesResponse)
def rapport_companies(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Generate companies report (Super Admin only)"""
    if not current_user.is_superuser:
        raise HTTPException(status_code=403, detail="Super Admin required")
    
    return TenantReportingService.rapport_companies(db)


@router.get("/reports/revenus/{periode}", response_model=RapportRevenusResponse)
def rapport_revenus(
    periode: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Generate revenue report (Super Admin only)"""
    if not current_user.is_superuser:
        raise HTTPException(status_code=403, detail="Super Admin required")
    
    return TenantReportingService.rapport_revenus(db, periode)


# ============================================================================
# HELPERS (console compute)
# ============================================================================
def _company_or_404(db: Session, company_id: int) -> Company:
    company = db.query(Company).filter(Company.id == company_id).first()
    if not company:
        raise HTTPException(status_code=404, detail="Societe non trouvee")
    return company


def _parse_modules(raw) -> List[str]:
    if not raw:
        return []
    try:
        val = json.loads(raw)
        return val if isinstance(val, list) else [str(val)]
    except (json.JSONDecodeError, TypeError):
        return [raw]


def _company_console_view(db: Session, company: Company) -> dict:
    """Rich company payload for the Super Admin console.

    All numbers are computed from live data (employees) or from the quota
    columns already persisted on the tenant. No invented metric.
    """
    employees = db.query(User).filter(User.company_id == company.id).count()
    plan = company.subscription_plan
    modules = _parse_modules(company.modules_actives)

    max_storage = int(company.max_storage_mb or 0)
    used_storage = int(company.current_storage_mb or 0)

    admin_entreprise = (
        db.query(User)
        .filter(
            User.company_id == company.id,
            User.role_level <= 1,
            User.is_superuser.is_(False),
        )
        .first()
    )

    return {
        "id": company.id,
        "code": company.code,
        "nom": company.nom,
        "sigle": company.sigle,
        "legal_form": company.legal_form,
        "capital_social": company.capital_social,
        "tax_id": company.tax_id,
        "rccm": company.rccm,
        "agrement_douane": company.agrement_douane,
        "agrement_pad": company.agrement_pad,
        "agrement_pak": company.agrement_pak,
        "rib": company.rib,
        "adresse": company.adresse,
        "ville": company.ville,
        "pays": company.pays,
        "telephone": company.telephone,
        "email": company.email,
        "website": company.website,
        "logo_url": company.logo_url,
        "is_active": company.is_active,
        "is_verified": company.is_verified,
        "suspension_reason": company.suspension_reason,
        # Plan / avantage
        "plan_id": company.subscription_plan_id,
        "plan_code": plan.code if plan else None,
        "plan_nom": plan.nom if plan else None,
        "plan_type": (plan.type_plan.value if plan and plan.type_plan else None),
        # Employes (reel)
        "employees_count": employees,
        "max_users": company.max_users,
        # Stockage alloue / restant
        "storage": {
            "allocated_mb": max_storage,
            "used_mb": used_storage,
            "remaining_mb": max(max_storage - used_storage, 0),
            "usage_percent": round((used_storage / max_storage) * 100, 1) if max_storage else 0.0,
        },
        # Modules disponibles pour cette entreprise
        "modules_actives": modules,
        "primary_color": company.primary_color,
        "secondary_color": company.secondary_color,
        "banner_url": company.banner_url,
        "subscription_start": company.subscription_start.isoformat() if company.subscription_start else None,
        "subscription_end": company.subscription_end.isoformat() if company.subscription_end else None,
        "created_at": company.created_at.isoformat() if company.created_at else None,
        # Admin entreprise attitre (0 ou 1)
        "admin_entreprise": {
            "id": admin_entreprise.id,
            "username": admin_entreprise.username,
            "email": admin_entreprise.email,
            "full_name": admin_entreprise.full_name,
        } if admin_entreprise else None,
    }


def _compute_company_alerts(db: Session, company: Company) -> List[dict]:
    """Quota / storage / subscription alerts for a single company (real data)."""
    alerts: List[dict] = []

    employees = db.query(User).filter(User.company_id == company.id).count()
    max_users = int(company.max_users or 0)
    if max_users and employees >= max_users:
        alerts.append({
            "type": "quota_utilisateurs", "severity": "critique", "company_id": company.id,
            "message": f"{company.nom} : quota d'utilisateurs atteint ({employees}/{max_users})",
        })
    elif max_users and employees >= max_users * 0.9:
        alerts.append({
            "type": "quota_utilisateurs", "severity": "avertissement", "company_id": company.id,
            "message": f"{company.nom} : proche du quota d'utilisateurs ({employees}/{max_users})",
        })

    max_storage = int(company.max_storage_mb or 0)
    used_storage = int(company.current_storage_mb or 0)
    if max_storage and used_storage >= max_storage:
        alerts.append({
            "type": "stockage", "severity": "critique", "company_id": company.id,
            "message": f"{company.nom} : stockage satur\u00e9 ({used_storage}/{max_storage} Mo)",
        })
    elif max_storage and used_storage >= max_storage * 0.85:
        alerts.append({
            "type": "stockage", "severity": "avertissement", "company_id": company.id,
            "message": f"{company.nom} : stockage pres de la limite ({used_storage}/{max_storage} Mo)",
        })

    if company.subscription_end:
        days_left = (company.subscription_end - date.today()).days
        if days_left < 0:
            alerts.append({
                "type": "abonnement", "severity": "critique", "company_id": company.id,
                "message": f"{company.nom} : abonnement expire depuis {-days_left} jour(s)",
            })
        elif days_left <= 30:
            alerts.append({
                "type": "abonnement", "severity": "avertissement", "company_id": company.id,
                "message": f"{company.nom} : abonnement expire dans {days_left} jour(s)",
            })

    if not company.is_active:
        alerts.append({
            "type": "entreprise", "severity": "info", "company_id": company.id,
            "message": f"{company.nom} : entreprise suspendue"
            + (f" ({company.suspension_reason})" if company.suspension_reason else ""),
        })

    return alerts


# ============================================================================
# SUPER ADMIN CONSOLE (invisible to everyone else  require_superadmin)
# ============================================================================
@router.get("/companies/detailed")
def lister_companies_detail(
    db: Session = Depends(get_db),
    current_user: User = Depends(require_superadmin),
):
    """List all companies with live employee counts, storage & modules (Super Admin)."""
    companies = db.query(Company).order_by(Company.id.asc()).all()
    return [_company_console_view(db, c) for c in companies]


@router.get("/companies/{company_id}")
def get_company_detail(
    company_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_superadmin),
):
    """Full detail of one company for the Super Admin console."""
    company = _company_or_404(db, company_id)
    payload = _company_console_view(db, company)
    payload["alerts"] = _compute_company_alerts(db, company)
    return payload


@router.patch("/companies/{company_id}")
def update_company(
    company_id: int,
    payload: dict,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_superadmin),
):
    """Update a company (logo, raison sociale, coordonnees, quotas...). Super Admin."""
    company = _company_or_404(db, company_id)
    allowed = ['nom', 'sigle', 'legal_form', 'capital_social', 'tax_id', 'rccm',
               'agrement_douane', 'agrement_pad', 'agrement_pak', 'rib', 'adresse',
               'ville', 'pays', 'telephone', 'email', 'website', 'logo_url',
               'banner_url', 'primary_color', 'secondary_color', 'subdomain',
               'custom_domain', 'max_users', 'max_storage_mb', 'max_apis_per_day',
               'max_camions', 'is_active', 'is_verified']
    for field in allowed:
        if field in payload:
            setattr(company, field, payload[field])
    if 'modules_actives' in payload:
        company.modules_actives = json.dumps(payload['modules_actives'])
    db.commit()
    db.refresh(company)
    return {"success": True, "company": _company_console_view(db, company)}


@router.delete("/companies/{company_id}")
def delete_company(
    company_id: int,
    force: bool = False,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_superadmin),
):
    """Delete a company (Super Admin). Refuses if users/departments still attached
    unless ``force=true`` (which first detaches users). Prefer suspension."""
    company = _company_or_404(db, company_id)
    employees = db.query(User).filter(User.company_id == company.id).count()
    departments = db.query(Department).filter(Department.company_id == company.id).count()
    if (employees or departments) and not force:
        raise HTTPException(
            status_code=409,
            detail=(f"Entreprise encore liee a {employees} utilisateur(s) et {departments} departement(s). "
                    "Utilisez ?force=true pour supprimer, ou suspendez-la."),
        )
    if force:
        db.query(User).filter(User.company_id == company.id).update({"company_id": None})
        db.query(Department).filter(Department.company_id == company.id).delete()
    db.delete(company)
    db.commit()
    return {"success": True, "message": f"Entreprise {company_id} supprimee"}


@router.get("/companies/{company_id}/storage")
def get_company_storage(
    company_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_superadmin),
):
    """Allocated / used / remaining storage for a company."""
    company = _company_or_404(db, company_id)
    max_storage = int(company.max_storage_mb or 0)
    used = int(company.current_storage_mb or 0)
    return {
        "company_id": company.id,
        "allocated_mb": max_storage,
        "used_mb": used,
        "remaining_mb": max(max_storage - used, 0),
        "usage_percent": round((used / max_storage) * 100, 1) if max_storage else 0.0,
    }


@router.get("/companies/{company_id}/modules")
def get_company_modules(
    company_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_superadmin),
):
    """List the modules enabled for a company (pairs with PUT .../modules)."""
    company = _company_or_404(db, company_id)
    return {"company_id": company.id, "modules_actives": _parse_modules(company.modules_actives)}


@router.post("/companies/{company_id}/admin-entreprise", status_code=status.HTTP_201_CREATED)
def create_company_admin(
    company_id: int,
    payload: dict,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_superadmin),
):
    """Create EXACTLY ONE admin-entreprise profile for a company (Super Admin).

    The Super Admin configures the company but never becomes a member of it;
    the single admin-entreprise is the highest authority inside the tenant.
    """
    company = _company_or_404(db, company_id)

    existing = (
        db.query(User)
        .filter(User.company_id == company.id, User.role_level <= 1, User.is_superuser.is_(False))
        .first()
    )
    if existing:
        raise HTTPException(
            status_code=409,
            detail=(f"Un admin-entreprise existe deja pour cette entreprise "
                    f"({existing.email}). Modifiez-le ou supprimez-le d'abord."),
        )

    email = (payload.get("email") or "").strip().lower()
    username = (payload.get("username") or email.split("@")[0]).strip()
    password = payload.get("password")
    full_name = payload.get("full_name") or payload.get("nom") or username
    if not email or not password:
        raise HTTPException(status_code=400, detail="email et password requis")
    validate_password_strength(password, username)

    if db.query(User).filter(or_(User.email == email, User.username == username)).first():
        raise HTTPException(status_code=400, detail="Email ou nom d'utilisateur deja utilise")

    admin = User(
        username=username,
        email=email,
        hashed_password=get_password_hash(password),
        full_name=full_name,
        phone=payload.get("phone"),
        company_id=company.id,
        role_level=1,           # Admin Entreprise
        is_superuser=False,     # n'est PAS un super admin plateforme
        is_active=True,
        created_by=current_user.id,
    )
    db.add(admin)
    db.commit()
    db.refresh(admin)
    return {
        "success": True,
        "message": "Admin-entreprise cree",
        "admin": {
            "id": admin.id, "username": admin.username, "email": admin.email,
            "full_name": admin.full_name, "role_level": admin.role_level,
        },
    }


@router.get("/alerts/platform")
def platform_alerts(
    db: Session = Depends(get_db),
    current_user: User = Depends(require_superadmin),
):
    """Platform-wide alerts across every company (quota, storage, subscriptions)."""
    alerts: List[dict] = []
    for company in db.query(Company).all():
        alerts.extend(_compute_company_alerts(db, company))
    severity_rank = {"critique": 0, "avertissement": 1, "info": 2}
    alerts.sort(key=lambda a: severity_rank.get(a["severity"], 9))
    return {"total": len(alerts), "alerts": alerts}


# ============================================================================
# ADMIN ENTREPRISE (company-scoped  require_company_admin)
# ============================================================================
@router.get("/company/dashboard")
def company_dashboard(
    db: Session = Depends(get_db),
    current_user: User = Depends(require_company_admin),
):
    """Global dashboard for the caller's company ONLY (never cross-tenant)."""
    cid = resolve_scope_company_id(current_user, None)
    company = _company_or_404(db, cid)
    employees = db.query(User).filter(User.company_id == cid).count()
    departments = db.query(Department).filter(Department.company_id == cid).count()
    max_storage = int(company.max_storage_mb or 0)
    used_storage = int(company.current_storage_mb or 0)
    return {
        "company": _company_console_view(db, company),
        "employees_count": employees,
        "departments_count": departments,
        "modules_actives": _parse_modules(company.modules_actives),
        "storage": {
            "allocated_mb": max_storage,
            "used_mb": used_storage,
            "remaining_mb": max(max_storage - used_storage, 0),
        },
        "alerts": _compute_company_alerts(db, company),
    }


@router.get("/company/alerts")
def company_alerts(
    db: Session = Depends(get_db),
    current_user: User = Depends(require_company_admin),
):
    """System alerts scoped to the caller's company."""
    cid = resolve_scope_company_id(current_user, None)
    company = _company_or_404(db, cid)
    alerts = _compute_company_alerts(db, company)
    return {"company_id": cid, "total": len(alerts), "alerts": alerts}


@router.get("/departments")
def list_own_departments(
    db: Session = Depends(get_db),
    current_user: User = Depends(require_company_admin),
):
    """List the caller's company departments with hierarchy."""
    cid = resolve_scope_company_id(current_user, None)
    depts = db.query(Department).filter(Department.company_id == cid).all()
    return [
        {
            "id": d.id, "company_id": d.company_id, "code": d.code, "nom": d.nom,
            "description": d.description,
            "parent_id": d.parent_id, "manager_id": d.manager_id,
            "modules_allowed": _parse_modules(d.modules_allowed),
            "is_active": d.is_active,
            "users_count": db.query(User).filter(User.department_id == d.id).count(),
        }
        for d in depts
    ]


@router.put("/departments/{department_id}")
def update_department(
    department_id: int,
    payload: dict,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_company_admin),
):
    """Update a department (nom, hierarchie parent, responsable). Company-scoped."""
    cid = resolve_scope_company_id(current_user, None)
    dept = db.query(Department).filter(Department.id == department_id).first()
    if not dept or dept.company_id != cid:
        raise HTTPException(status_code=404, detail="Departement introuvable")
    for field in ("nom", "description", "manager_id", "is_active"):
        if field in payload:
            setattr(dept, field, payload[field])
    if "parent_id" in payload:
        parent_id = payload["parent_id"]
        if parent_id == dept.id:
            raise HTTPException(status_code=400, detail="Un departement ne peut pas etre son propre parent")
        if parent_id is not None:
            parent = db.query(Department).filter(Department.id == parent_id).first()
            if not parent or parent.company_id != cid:
                raise HTTPException(status_code=400, detail="Parent invalide")
        dept.parent_id = parent_id
    db.commit()
    db.refresh(dept)
    return {"success": True, "id": dept.id, "message": "Departement mis a jour"}


@router.delete("/departments/{department_id}")
def delete_department(
    department_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_company_admin),
):
    """Delete a department. Refuses if it still has users or children."""
    cid = resolve_scope_company_id(current_user, None)
    dept = db.query(Department).filter(Department.id == department_id).first()
    if not dept or dept.company_id != cid:
        raise HTTPException(status_code=404, detail="Departement introuvable")
    members = db.query(User).filter(User.department_id == dept.id).count()
    children = db.query(Department).filter(Department.parent_id == dept.id).count()
    if members or children:
        raise HTTPException(
            status_code=409,
            detail=f"Departement occupe ({members} utilisateur(s), {children} sous-departement(s))",
        )
    db.delete(dept)
    db.commit()
    return {"success": True, "message": "Departement supprime"}


@router.put("/departments/{department_id}/modules")
def update_department_modules(
    department_id: int,
    payload: dict,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_company_admin),
):
    """Grant/revoke the modules a department can access (Admin Entreprise)."""
    cid = resolve_scope_company_id(current_user, None)
    dept = db.query(Department).filter(Department.id == department_id).first()
    if not dept or dept.company_id != cid:
        raise HTTPException(status_code=404, detail="Departement introuvable")
    modules = payload.get("modules_allowed", [])
    dept.modules_allowed = json.dumps(modules)
    db.commit()
    return {"success": True, "id": dept.id, "modules_allowed": modules}
