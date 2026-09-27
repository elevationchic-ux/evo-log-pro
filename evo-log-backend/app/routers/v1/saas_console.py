"""Console Super-Admin CADC (SaaS : entreprises, plans, modules, accréditations).

Source de verite tenant = ``Company`` + ``SubscriptionPlan`` (modele deja cable
au moteur RBAC et aux accreditations). Ce routeur est l'interface unique du
Super Administrateur plateforme (compte CADC) :

- CRUD total des entreprises, avec upload de logo ;
- CRUD des plans d'abonnement, dont ``max_modules`` verrouille le nombre de
  modules allouables une fois le plan cree ;
- allocation des modules a une entreprise (bornee par le plan) ;
- accreditations d'entreprise datees (delai) debloquant un module pour un
  collaborateur cible au-dela de l'allocation de base ;
- annuaire prestataires : ecriture reservee au CADC (lecture annuaire libre
  ailleurs, module commun).

INVISIBILITE : toutes les routes exigent ``require_superadmin`` (utils/rbac.py)
-> 403 pour tout autre niveau, y compris admin entreprise.

NB : les modules sont designes par leur cle de premier niveau (ex.
``transport``), coherent a la fois avec ``Company.modules_actives`` et avec les
codes d'accreditation ``module.*.*`` servis au moteur d'autorisation.
"""
import json
import secrets
import uuid
from pathlib import Path
from typing import Any, Dict, List, Optional

from fastapi import APIRouter, Depends, File, HTTPException, UploadFile, status
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session

from app.core.config import settings
from app.core.database import get_db
from app.core.permission_catalog import DOMAINS
from app.core.security import get_password_hash, validate_password_strength
from app.models.accreditation import ACC_TYPE_PERMISSION, Accreditation
from app.models.prestataire import Prestataire
from app.models.tenant import Company, SubscriptionPlan, SubscriptionPlanType
from app.models.user import Role, User
from app.utils.rbac import require_superadmin

router = APIRouter(dependencies=[Depends(require_superadmin)])

# Types MIME acceptes pour un logo + taille max (2 Mo).
_ALLOWED_LOGO_TYPES = {
    "image/png": ".png",
    "image/jpeg": ".jpg",
    "image/webp": ".webp",
    "image/svg+xml": ".svg",
    "image/gif": ".gif",
}
_MAX_LOGO_BYTES = 2 * 1024 * 1024


# ── Aides serialisation ───────────────────────────────────────────────────────
def _loads(raw: Optional[str], default: Any) -> Any:
    if not raw:
        return default
    try:
        return json.loads(raw)
    except (json.JSONDecodeError, TypeError):
        return default


def _company_dict(c: Company) -> Dict[str, Any]:
    return {
        "id": c.id,
        "code": c.code,
        "nom": c.nom,
        "sigle": c.sigle,
        "legal_form": c.legal_form,
        "tax_id": c.tax_id,
        "rccm": c.rccm,
        "agrement_douane": c.agrement_douane,
        "ville": c.ville,
        "pays": c.pays,
        "telephone": c.telephone,
        "email": c.email,
        "website": c.website,
        "logo_url": c.logo_url,
        "is_active": c.is_active,
        "is_verified": c.is_verified,
        "subscription_plan_id": c.subscription_plan_id,
        "subscription_start": c.subscription_start,
        "subscription_end": c.subscription_end,
        "max_users": c.max_users,
        "subdomain": c.subdomain,
        "primary_color": c.primary_color,
        "modules_actives": _loads(c.modules_actives, []),
        "created_at": c.created_at,
    }


def _plan_dict(p: SubscriptionPlan) -> Dict[str, Any]:
    return {
        "id": p.id,
        "code": p.code,
        "nom": p.nom,
        "type_plan": p.type_plan.value if hasattr(p.type_plan, "value") else p.type_plan,
        "description": p.description,
        "prix_mensuel": p.prix_mensuel,
        "prix_annuel": p.prix_annuel,
        "devise": p.devise,
        "modules_inclus": _loads(p.modules_inclus, []),
        "max_modules": p.max_modules,
        "max_users": p.max_users,
        "max_storage_mb": p.max_storage_mb,
        "max_apis_per_day": p.max_apis_per_day,
        "trial_days": p.trial_days,
        "is_active": p.is_active,
    }


def _accred_dict(a: Accreditation) -> Dict[str, Any]:
    return {
        "id": a.id,
        "user_id": a.user_id,
        "company_id": a.company_id,
        "code": a.code,
        "libelle": a.libelle,
        "type": a.type,
        "permission_code": a.permission_code,
        "module": a.module,
        "date_debut": a.date_debut,
        "date_fin": a.date_fin,
        "statut": a.statut,
        "motif": a.motif,
        "octroye_par": a.octroye_par,
        "valide": a.est_valide(),
    }


def _get_company(db: Session, company_id: int) -> Company:
    company = db.query(Company).filter(Company.id == company_id).first()
    if not company:
        raise HTTPException(status_code=404, detail="Entreprise introuvable")
    return company


def _plan_module_cap(plan: Optional[SubscriptionPlan]) -> Optional[int]:
    """Nombre max de modules allouables pour ce plan (None = illimite)."""
    if plan is None:
        return None
    return plan.max_modules


# ── Catalogue des modules (pour le selecteur de l'UI) ─────────────────────────
@router.get("/modules-catalog", summary="Catalogue des modules allouables")
def modules_catalog():
    """Cles de premier niveau + libelles, derives du catalogue de permissions."""
    items: List[Dict[str, str]] = []
    seen = set()
    for dom_key, ddata in DOMAINS.items():
        for mod_key, mdata in ddata.get("modules", {}).items():
            if mod_key in seen:
                continue
            seen.add(mod_key)
            items.append({"key": mod_key, "label": mdata.get("label", mod_key), "domain": dom_key})
    return {"modules": items}


# ── Entreprises : CRUD total ──────────────────────────────────────────────────
class CompanyCreate(BaseModel):
    code: str = Field(..., max_length=50)
    nom: str = Field(..., max_length=200)
    sigle: Optional[str] = None
    legal_form: Optional[str] = None
    tax_id: Optional[str] = None
    rccm: Optional[str] = None
    agrement_douane: Optional[str] = None
    ville: Optional[str] = None
    pays: Optional[str] = "Cameroun"
    telephone: Optional[str] = None
    email: Optional[str] = None
    website: Optional[str] = None
    subdomain: Optional[str] = None
    subscription_plan_id: Optional[int] = None
    max_users: int = 10
    is_active: bool = True
    modules_actives: Optional[List[str]] = None


class CompanyUpdate(BaseModel):
    nom: Optional[str] = None
    sigle: Optional[str] = None
    legal_form: Optional[str] = None
    tax_id: Optional[str] = None
    rccm: Optional[str] = None
    agrement_douane: Optional[str] = None
    ville: Optional[str] = None
    pays: Optional[str] = None
    telephone: Optional[str] = None
    email: Optional[str] = None
    website: Optional[str] = None
    subdomain: Optional[str] = None
    logo_url: Optional[str] = None
    subscription_plan_id: Optional[int] = None
    max_users: Optional[int] = None
    primary_color: Optional[str] = None
    is_active: Optional[bool] = None
    is_verified: Optional[bool] = None


@router.get("/companies", summary="Lister les entreprises")
def list_companies(
    search: Optional[str] = None,
    db: Session = Depends(get_db),
):
    q = db.query(Company)
    if search:
        like = f"%{search}%"
        q = q.filter((Company.nom.ilike(like)) | (Company.code.ilike(like)))
    rows = q.order_by(Company.id.desc()).all()
    out = []
    for c in rows:
        d = _company_dict(c)
        d["user_count"] = db.query(User).filter(User.company_id == c.id).count()
        out.append(d)
    return out


@router.get("/companies/{company_id}", summary="Detail d'une entreprise")
def get_company(company_id: int, db: Session = Depends(get_db)):
    c = _get_company(db, company_id)
    d = _company_dict(c)
    d["user_count"] = db.query(User).filter(User.company_id == c.id).count()
    return d


@router.post("/companies", status_code=status.HTTP_201_CREATED, summary="Creer une entreprise")
def create_company(payload: CompanyCreate, db: Session = Depends(get_db)):
    if db.query(Company).filter(Company.code == payload.code).first():
        raise HTTPException(status_code=400, detail="Un code d'entreprise existe deja")
    if payload.subdomain and db.query(Company).filter(Company.subdomain == payload.subdomain).first():
        raise HTTPException(status_code=400, detail="Ce sous-domaine est deja pris")
    plan = None
    if payload.subscription_plan_id:
        plan = db.query(SubscriptionPlan).filter(SubscriptionPlan.id == payload.subscription_plan_id).first()
        if not plan:
            raise HTTPException(status_code=400, detail="Plan d'abonnement introuvable")
    modules = payload.modules_actives or []
    cap = _plan_module_cap(plan)
    if cap is not None and len(modules) > cap:
        raise HTTPException(
            status_code=400,
            detail=f"Ce plan limite a {cap} module(s) ; {len(modules)} demande(s)",
        )
    company = Company(
        code=payload.code,
        nom=payload.nom,
        sigle=payload.sigle,
        legal_form=payload.legal_form,
        tax_id=payload.tax_id,
        rccm=payload.rccm,
        agrement_douane=payload.agrement_douane,
        ville=payload.ville,
        pays=payload.pays,
        telephone=payload.telephone,
        email=payload.email,
        website=payload.website,
        subdomain=payload.subdomain,
        subscription_plan_id=payload.subscription_plan_id,
        max_users=payload.max_users,
        is_active=payload.is_active,
        modules_actives=json.dumps(modules),
    )
    db.add(company)
    db.commit()
    db.refresh(company)
    return _company_dict(company)


@router.patch("/companies/{company_id}", summary="Modifier une entreprise")
def update_company(company_id: int, payload: CompanyUpdate, db: Session = Depends(get_db)):
    c = _get_company(db, company_id)
    data = payload.dict(exclude_unset=True)
    if "subdomain" in data and data["subdomain"]:
        clash = db.query(Company).filter(
            Company.subdomain == data["subdomain"], Company.id != c.id
        ).first()
        if clash:
            raise HTTPException(status_code=400, detail="Ce sous-domaine est deja pris")
    if "subscription_plan_id" in data and data["subscription_plan_id"]:
        plan = db.query(SubscriptionPlan).filter(
            SubscriptionPlan.id == data["subscription_plan_id"]
        ).first()
        if not plan:
            raise HTTPException(status_code=400, detail="Plan d'abonnement introuvable")
        cap = _plan_module_cap(plan)
        current = _loads(c.modules_actives, [])
        if cap is not None and len(current) > cap:
            raise HTTPException(
                status_code=400,
                detail=(
                    f"L'entreprise a {len(current)} module(s) ; le plan cible "
                    f"limite a {cap}. Retirez des modules avant de changer de plan."
                ),
            )
    for key, value in data.items():
        setattr(c, key, value)
    db.commit()
    db.refresh(c)
    return _company_dict(c)


@router.delete("/companies/{company_id}", status_code=status.HTTP_204_NO_CONTENT, summary="Supprimer une entreprise")
def delete_company(company_id: int, db: Session = Depends(get_db)):
    c = _get_company(db, company_id)
    if db.query(User).filter(User.company_id == c.id).count() > 0:
        raise HTTPException(
            status_code=400,
            detail="Entreprise encore associee a des utilisateurs ; desactivez-la a la place.",
        )
    db.delete(c)
    db.commit()
    return None


class LogoResponse(BaseModel):
    company_id: int
    logo_url: str


@router.post("/companies/{company_id}/logo", response_model=LogoResponse, summary="Televerser le logo")
async def upload_company_logo(
    company_id: int,
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
):
    c = _get_company(db, company_id)
    ctype = (file.content_type or "").lower()
    ext = _ALLOWED_LOGO_TYPES.get(ctype)
    if ext is None:
        raise HTTPException(
            status_code=400,
            detail="Type d'image non supporte (PNG, JPEG, WEBP, SVG, GIF)",
        )
    content = await file.read()
    if len(content) > _MAX_LOGO_BYTES:
        raise HTTPException(status_code=400, detail="Logo trop volumineux (max 2 Mo)")
    if not content:
        raise HTTPException(status_code=400, detail="Fichier vide")

    logo_dir = Path(settings.UPLOAD_DIR) / "logos"
    logo_dir.mkdir(parents=True, exist_ok=True)
    fname = f"company_{c.id}_{uuid.uuid4().hex}{ext}"
    (logo_dir / fname).write_bytes(content)

    c.logo_url = f"/static/uploads/logos/{fname}"
    db.commit()
    db.refresh(c)
    return LogoResponse(company_id=c.id, logo_url=c.logo_url)


class ModulesAllocation(BaseModel):
    modules: List[str]


@router.put("/companies/{company_id}/modules", summary="Allouer les modules de l'entreprise")
def allocate_modules(company_id: int, payload: ModulesAllocation, db: Session = Depends(get_db)):
    c = _get_company(db, company_id)
    modules = sorted(set(payload.modules or []))
    plan = None
    if c.subscription_plan_id:
        plan = db.query(SubscriptionPlan).filter(SubscriptionPlan.id == c.subscription_plan_id).first()
    cap = _plan_module_cap(plan)
    if cap is not None and len(modules) > cap:
        raise HTTPException(
            status_code=400,
            detail=f"Ce plan limite a {cap} module(s) ; {len(modules)} demande(s)",
        )
    c.modules_actives = json.dumps(modules)
    db.commit()
    db.refresh(c)
    return {"company_id": c.id, "modules_actives": _loads(c.modules_actives, []), "max_modules": cap}


# ── Admins d'entreprise (Phase 2) : cree par le CADC ─────────────────────────
class CompanyAdminCreate(BaseModel):
    username: str = Field(..., max_length=50)
    email: str = Field(..., max_length=100)
    password: Optional[str] = Field(
        None,
        description="Mot de passe temporaire ; genere automatiquement si absent. "
                    "must_change_password est toujours force a True.",
    )
    full_name: Optional[str] = None
    matricule: Optional[str] = None
    job_title: Optional[str] = None
    phone: Optional[str] = None


def _safe_user_dict(u: User) -> Dict[str, Any]:
    """Representation d'un utilisateur sans aucun champ sensible."""
    return {
        "id": u.id,
        "username": u.username,
        "email": u.email,
        "full_name": u.full_name,
        "matricule": u.matricule,
        "job_title": u.job_title,
        "phone": u.phone,
        "company_id": u.company_id,
        "role_level": u.role_level,
        "is_active": u.is_active,
        "is_superuser": bool(u.is_superuser),
        "must_change_password": bool(u.must_change_password),
        "roles": [r.name for r in (u.roles or [])],
        "created_at": u.created_at,
    }


@router.get("/companies/{company_id}/admins", summary="Lister les admins de l'entreprise")
def list_company_admins(company_id: int, db: Session = Depends(get_db)):
    _get_company(db, company_id)
    rows = (
        db.query(User)
        .filter(User.company_id == company_id, User.role_level == 1)
        .order_by(User.id.asc())
        .all()
    )
    return [_safe_user_dict(u) for u in rows]


@router.post(
    "/companies/{company_id}/admins",
    status_code=status.HTTP_201_CREATED,
    summary="Creer un admin entreprise (niveau 1)",
)
def create_company_admin(
    company_id: int,
    payload: CompanyAdminCreate,
    db: Session = Depends(get_db),
):
    """Le CADC designe un administrateur pour SON entreprise.

    Regles metier (plan Phase 2) :
    - ``role_level=1``, rattle a l'entreprise ciblee, jamais super-utilisateur ;
    - ``must_change_password=True`` : le mot de passe (temporaire, eventuellement
      genere) doit etre changee a la premiere connexion ;
    - quota du plan ``max_users`` respecte ;
    - unicite username/email verifiee.
    """
    company = _get_company(db, company_id)
    if db.query(User).filter(User.username == payload.username).first():
        raise HTTPException(status_code=400, detail="Ce nom d'utilisateur existe deja")
    if db.query(User).filter(User.email == payload.email).first():
        raise HTTPException(status_code=400, detail="Cet email est deja utilise")

    # Quota utilisateurs du plan d'abonnement (NULL/absent = pas de limite).
    plan = None
    if company.subscription_plan_id:
        plan = db.query(SubscriptionPlan).filter(
            SubscriptionPlan.id == company.subscription_plan_id
        ).first()
    if plan is not None and plan.max_users:
        current_users = db.query(User).filter(User.company_id == company.id).count()
        if current_users >= plan.max_users:
            raise HTTPException(
                status_code=400,
                detail=f"Quota du plan atteint ({plan.max_users} utilisateurs) ; "
                       "augmentez le plan avant d'ajouter un admin.",
            )

    temp_password = payload.password or f"Adm-{secrets.token_hex(6)}!"
    try:
        validate_password_strength(temp_password, payload.username)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc))

    admin = User(
        username=payload.username,
        email=payload.email,
        hashed_password=get_password_hash(temp_password),
        full_name=payload.full_name or payload.username,
        matricule=payload.matricule,
        job_title=payload.job_title or "Administrateur Entreprise",
        phone=payload.phone,
        company_id=company.id,
        role_level=1,
        is_active=True,
        is_superuser=False,
        must_change_password=True,
    )
    db_role = db.query(Role).filter(Role.name == "ADMIN").first()
    if db_role:
        admin.roles.append(db_role)
    db.add(admin)
    db.commit()
    db.refresh(admin)
    out = _safe_user_dict(admin)
    out["temporary_password"] = temp_password
    return out


@router.get("/accreditations/demandes", summary="Demandes d'accreditation en attente (toutes entreprises)")
def list_pending_accreditation_requests(db: Session = Depends(get_db)):
    """File de lecture CADC : demandes emises par les admins entreprise (statut
    ``demande``). L'octroi effectif reste datee via POST /companies/{id}/accreditations."""
    rows = (
        db.query(Accreditation)
        .filter(Accreditation.statut == "demande")
        .order_by(Accreditation.id.desc())
        .all()
    )
    out = []
    for a in rows:
        d = _accred_dict(a)
        company = db.query(Company).filter(Company.id == a.company_id).first()
        d["company_nom"] = company.nom if company else None
        out.append(d)
    return out


# ── Accreditations d'entreprise (delai) ───────────────────────────────────────
class CompanyAccreditationCreate(BaseModel):
    user_id: int
    module: str = Field(..., description="Cle de module debloque (ex: transport)")
    libelle: Optional[str] = None
    date_debut: Optional[str] = None  # ISO YYYY-MM-DD
    date_fin: Optional[str] = None     # ISO YYYY-MM-DD (delai)
    motif: Optional[str] = None


def _parse_date(value: Optional[str]):
    if not value:
        return None
    from datetime import date as _date
    try:
        return _date.fromisoformat(value)
    except ValueError:
        raise HTTPException(status_code=400, detail=f"Date invalide (attendu AAAA-MM-JJ) : {value}")


@router.get("/companies/{company_id}/accreditations", summary="Accreditations de l'entreprise")
def list_company_accreditations(company_id: int, db: Session = Depends(get_db)):
    _get_company(db, company_id)
    rows = db.query(Accreditation).filter(Accreditation.company_id == company_id).order_by(
        Accreditation.id.desc()
    ).all()
    return [_accred_dict(a) for a in rows]


@router.post(
    "/companies/{company_id}/accreditations",
    status_code=status.HTTP_201_CREATED,
    summary="Accorder une accreditation module datee",
)
def grant_company_accreditation(
    company_id: int,
    payload: CompanyAccreditationCreate,
    db: Session = Depends(get_db),
    current: User = Depends(require_superadmin),
):
    _get_company(db, company_id)
    target = db.query(User).filter(User.id == payload.user_id).first()
    if not target:
        raise HTTPException(status_code=404, detail="Utilisateur cible introuvable")
    if target.company_id != company_id:
        raise HTTPException(status_code=400, detail="Cet utilisateur n'appartient pas a cette entreprise")
    date_debut = _parse_date(payload.date_debut)
    date_fin = _parse_date(payload.date_fin)
    if date_debut and date_fin and date_fin < date_debut:
        raise HTTPException(status_code=400, detail="La date de fin precede la date de debut")
    acc = Accreditation(
        user_id=payload.user_id,
        company_id=company_id,
        code=f"ACC-CADC-{secrets.token_hex(4).upper()}",
        libelle=payload.libelle or f"Acces module {payload.module}",
        type=ACC_TYPE_PERMISSION,
        permission_code=f"{payload.module}.*.*",
        module=payload.module,
        date_debut=date_debut,
        date_fin=date_fin,
        statut="actif",
        motif=payload.motif,
        octroye_par=current.id,
    )
    db.add(acc)
    db.commit()
    db.refresh(acc)
    return _accred_dict(acc)


@router.delete(
    "/companies/{company_id}/accreditations/{accred_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Revoquer une accreditation d'entreprise",
)
def revoke_company_accreditation(company_id: int, accred_id: int, db: Session = Depends(get_db)):
    acc = db.query(Accreditation).filter(
        Accreditation.id == accred_id, Accreditation.company_id == company_id
    ).first()
    if not acc:
        raise HTTPException(status_code=404, detail="Accreditation introuvable")
    db.delete(acc)
    db.commit()
    return None


# ── Plans d'abonnement : CRUD + verrou max_modules ────────────────────────────
class PlanCreate(BaseModel):
    code: str = Field(..., max_length=50)
    nom: str = Field(..., max_length=100)
    type_plan: str = Field("pro", description="starter | pro | enterprise | custom")
    description: Optional[str] = None
    prix_mensuel: float = 0.0
    prix_annuel: float = 0.0
    devise: str = "XAF"
    modules_inclus: Optional[List[str]] = None
    max_modules: Optional[int] = Field(None, description="NULL = illimite")
    max_users: int = 10
    max_storage_mb: int = 1024
    max_apis_per_day: int = 1000
    trial_days: int = 14
    is_active: bool = True


class PlanUpdate(BaseModel):
    nom: Optional[str] = None
    type_plan: Optional[str] = None
    description: Optional[str] = None
    prix_mensuel: Optional[float] = None
    prix_annuel: Optional[float] = None
    devise: Optional[str] = None
    modules_inclus: Optional[List[str]] = None
    max_modules: Optional[int] = None
    max_users: Optional[int] = None
    max_storage_mb: Optional[int] = None
    max_apis_per_day: Optional[int] = None
    trial_days: Optional[int] = None
    is_active: Optional[bool] = None


def _coerce_plan_type(value: str) -> SubscriptionPlanType:
    try:
        return SubscriptionPlanType(value.lower())
    except ValueError:
        allowed = ", ".join(t.value for t in SubscriptionPlanType)
        raise HTTPException(status_code=400, detail=f"type_plan invalide (attendu : {allowed})")


@router.get("/plans", summary="Lister les plans d'abonnement")
def list_plans(db: Session = Depends(get_db)):
    rows = db.query(SubscriptionPlan).order_by(SubscriptionPlan.id.asc()).all()
    out = []
    for p in rows:
        d = _plan_dict(p)
        d["company_count"] = db.query(Company).filter(Company.subscription_plan_id == p.id).count()
        out.append(d)
    return out


@router.post("/plans", status_code=status.HTTP_201_CREATED, summary="Creer un plan")
def create_plan(payload: PlanCreate, db: Session = Depends(get_db)):
    if db.query(SubscriptionPlan).filter(SubscriptionPlan.code == payload.code).first():
        raise HTTPException(status_code=400, detail="Un code de plan existe deja")
    plan = SubscriptionPlan(
        code=payload.code,
        nom=payload.nom,
        type_plan=_coerce_plan_type(payload.type_plan),
        description=payload.description,
        prix_mensuel=payload.prix_mensuel,
        prix_annuel=payload.prix_annuel,
        devise=payload.devise,
        modules_inclus=json.dumps(payload.modules_inclus or []),
        max_modules=payload.max_modules,
        max_users=payload.max_users,
        max_storage_mb=payload.max_storage_mb,
        max_apis_per_day=payload.max_apis_per_day,
        trial_days=payload.trial_days,
        is_active=payload.is_active,
    )
    db.add(plan)
    db.commit()
    db.refresh(plan)
    return _plan_dict(plan)


@router.patch("/plans/{plan_id}", summary="Modifier un plan")
def update_plan(plan_id: int, payload: PlanUpdate, db: Session = Depends(get_db)):
    plan = db.query(SubscriptionPlan).filter(SubscriptionPlan.id == plan_id).first()
    if not plan:
        raise HTTPException(status_code=404, detail="Plan introuvable")
    data = payload.dict(exclude_unset=True)
    if "type_plan" in data and data["type_plan"]:
        data["type_plan"] = _coerce_plan_type(data["type_plan"])
    if "modules_inclus" in data and data["modules_inclus"] is not None:
        data["modules_inclus"] = json.dumps(data["modules_inclus"])
    # Retrait du verrou max_modules : refuser si des entreprises depasseraient.
    if "max_modules" in data and data["max_modules"] is not None:
        new_cap = data["max_modules"]
        for c in db.query(Company).filter(Company.subscription_plan_id == plan.id).all():
            used = len(_loads(c.modules_actives, []))
            if used > new_cap:
                raise HTTPException(
                    status_code=400,
                    detail=(
                        f"L'entreprise '{c.nom}' utilise {used} module(s) > nouveau "
                        f"verrou {new_cap}. Ajustez d'abord ses modules."
                    ),
                )
    for key, value in data.items():
        setattr(plan, key, value)
    db.commit()
    db.refresh(plan)
    return _plan_dict(plan)


@router.delete("/plans/{plan_id}", status_code=status.HTTP_204_NO_CONTENT, summary="Supprimer un plan")
def delete_plan(plan_id: int, db: Session = Depends(get_db)):
    plan = db.query(SubscriptionPlan).filter(SubscriptionPlan.id == plan_id).first()
    if not plan:
        raise HTTPException(status_code=404, detail="Plan introuvable")
    if db.query(Company).filter(Company.subscription_plan_id == plan.id).count() > 0:
        raise HTTPException(
            status_code=400,
            detail="Des entreprises utilisent ce plan ; archivez-le (is_active=false) a la place.",
        )
    db.delete(plan)
    db.commit()
    return None


# ── Annuaire prestataires : ecriture reservee au CADC ─────────────────────────
class PrestataireCreate(BaseModel):
    code: str = Field(..., max_length=50)
    raison_sociale: str = Field(..., max_length=150)
    specialite: str = Field(..., max_length=80)
    sigle: Optional[str] = None
    tax_id: Optional[str] = None
    rccm: Optional[str] = None
    agrement_portuaire: Optional[str] = None
    statut_agrement: str = "VALIDE"
    ville: Optional[str] = "Douala"
    zone_portuaire: Optional[str] = None
    adresse: Optional[str] = None
    contact_nom: Optional[str] = None
    contact_telephone: str = Field(..., max_length=40)
    contact_email: Optional[str] = None
    telephone_astreinte_24h: Optional[str] = None
    company_id: Optional[int] = None
    est_actif: bool = True
    observations: Optional[str] = None


class PrestataireUpdate(BaseModel):
    raison_sociale: Optional[str] = None
    specialite: Optional[str] = None
    sigle: Optional[str] = None
    tax_id: Optional[str] = None
    rccm: Optional[str] = None
    agrement_portuaire: Optional[str] = None
    statut_agrement: Optional[str] = None
    ville: Optional[str] = None
    zone_portuaire: Optional[str] = None
    adresse: Optional[str] = None
    contact_nom: Optional[str] = None
    contact_telephone: Optional[str] = None
    contact_email: Optional[str] = None
    telephone_astreinte_24h: Optional[str] = None
    company_id: Optional[int] = None
    est_actif: Optional[bool] = None
    observations: Optional[str] = None


def _prestataire_dict(p: Prestataire) -> Dict[str, Any]:
    return {
        "id": p.id,
        "company_id": p.company_id,
        "code": p.code,
        "raison_sociale": p.raison_sociale,
        "sigle": p.sigle,
        "specialite": p.specialite,
        "tax_id": p.tax_id,
        "rccm": p.rccm,
        "agrement_portuaire": p.agrement_portuaire,
        "statut_agrement": p.statut_agrement,
        "est_homologue": p.est_homologue,
        "ville": p.ville,
        "zone_portuaire": p.zone_portuaire,
        "contact_nom": p.contact_nom,
        "contact_telephone": p.contact_telephone,
        "contact_email": p.contact_email,
        "note_globale": p.note_globale,
        "est_actif": p.est_actif,
        "created_at": p.created_at,
    }


@router.get("/prestataires", summary="Lister l'annuaire des prestataires")
def list_prestataires(
    search: Optional[str] = None,
    specialite: Optional[str] = None,
    db: Session = Depends(get_db),
):
    q = db.query(Prestataire)
    if search:
        like = f"%{search}%"
        q = q.filter((Prestataire.raison_sociale.ilike(like)) | (Prestataire.code.ilike(like)))
    if specialite:
        q = q.filter(Prestataire.specialite == specialite)
    return [_prestataire_dict(p) for p in q.order_by(Prestataire.id.desc()).all()]


@router.post("/prestataires", status_code=status.HTTP_201_CREATED, summary="Ajouter un prestataire")
def create_prestataire(payload: PrestataireCreate, db: Session = Depends(get_db)):
    if db.query(Prestataire).filter(Prestataire.code == payload.code).first():
        raise HTTPException(status_code=400, detail="Un code de prestataire existe deja")
    p = Prestataire(**payload.dict())
    db.add(p)
    db.commit()
    db.refresh(p)
    return _prestataire_dict(p)


@router.patch("/prestataires/{prestataire_id}", summary="Modifier un prestataire")
def update_prestataire(prestataire_id: int, payload: PrestataireUpdate, db: Session = Depends(get_db)):
    p = db.query(Prestataire).filter(Prestataire.id == prestataire_id).first()
    if not p:
        raise HTTPException(status_code=404, detail="Prestataire introuvable")
    for key, value in payload.dict(exclude_unset=True).items():
        setattr(p, key, value)
    db.commit()
    db.refresh(p)
    return _prestataire_dict(p)


@router.delete("/prestataires/{prestataire_id}", status_code=status.HTTP_204_NO_CONTENT, summary="Retirer un prestataire")
def delete_prestataire(prestataire_id: int, db: Session = Depends(get_db)):
    p = db.query(Prestataire).filter(Prestataire.id == prestataire_id).first()
    if not p:
        raise HTTPException(status_code=404, detail="Prestataire introuvable")
    db.delete(p)
    db.commit()
    return None
