"""Administration interne Enterprise (Phase 2 — niveau 1, Admin Entreprise).

Surface scopee pour l'administrateur d'une entreprise SaaS : il gere LIBREMENT
son capital humain (collaborateurs, roles/casquettes, responsabilites) et suit
les modules alloues par le CADC, mais uniquement a l'interieur de son perimetre.

Gardes (invisibilite double, cf. plan) :
- ``require_company_admin`` (utils/rbac.py) : niveau 1 rattache a une entreprise,
  ou Super Admin (level 0) qui agit sur n'importe quelle entreprise via un
  ``company_id`` explicite — le CADC doit pouvoir piloter une entreprise meme
  avant la designation de son admin.
- ``resolve_scope_company_id`` : un admin entreprise est epingle a son
  ``company_id`` ; toute tentative d'agir sur une autre entreprise -> 403.
  NB : un Super Admin sans entreprise (compte CADC) doit passer un
  ``company_id`` explicite en query, sinon 400.

Les routes generalistes ``/api/v1/admin/users`` (admin.py) restent en place et
sont deja scopees ; ce routeur ajoute la surface CADC-visible (profil, modules
alloues/demandes, requetes d'accreditation) sans rien retirer.

Demandes d'accreditation : reuses le modele ``Accreditation`` avec un statut
metier additionnel ``demande`` (colonne String existante, aucune migration).
Une demande n'accorde RIEN (le moteur ignore tout statut != "actif") ; le CADC
la convertit en grant date via POST /saas/console/companies/{id}/accreditations.
"""
import json
import secrets
from typing import Any, Dict, List, Optional

from fastapi import APIRouter, Depends, HTTPException, Query, status
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.permission_catalog import DOMAINS
from app.core.security import get_password_hash, validate_password_strength
from app.models.accreditation import ACC_TYPE_PERMISSION, Accreditation
from app.models.tenant import Company, SubscriptionPlan
from app.models.user import Role, User
from app.utils.rbac import _is_superadmin, require_company_admin, resolve_scope_company_id

router = APIRouter(dependencies=[Depends(require_company_admin)])

# Statut metier d'une demande d'accreditation en attente d'arbitrage CADC.
ACC_STATUT_DEMANDE = "demande"


def _loads(raw: Optional[str], default: Any) -> Any:
    if not raw:
        return default
    try:
        return json.loads(raw)
    except (json.JSONDecodeError, TypeError):
        return default


def _scoped_company(db: Session, current: User, requested: Optional[int]) -> Company:
    """Resout l'entreprise ciblee (admin entreprise = sienne ; CADC = explicite)
    et garantit qu'elle existe."""
    company_id = resolve_scope_company_id(current, requested)
    company = db.query(Company).filter(Company.id == company_id).first()
    if not company:
        raise HTTPException(status_code=404, detail="Entreprise introuvable")
    return company


def _user_dict(u: User) -> Dict[str, Any]:
    return {
        "id": u.id,
        "username": u.username,
        "email": u.email,
        "full_name": u.full_name,
        "matricule": u.matricule,
        "job_title": u.job_title,
        "phone": u.phone,
        "role_level": u.role_level,
        "is_active": u.is_active,
        "is_superuser": bool(u.is_superuser),
        "must_change_password": bool(u.must_change_password),
        "department_id": u.department_id,
        "roles": [r.name for r in (u.roles or [])],
        "created_at": u.created_at,
        "last_login": u.last_login,
    }


def _catalog_keys() -> List[str]:
    keys: List[str] = []
    for ddata in DOMAINS.values():
        for mod_key in ddata.get("modules", {}):
            if mod_key not in keys:
                keys.append(mod_key)
    return keys


# ── Profil entreprise (lecture + champs de marque gerables par l'admin) ──────
class CompanyProfileUpdate(BaseModel):
    nom: Optional[str] = Field(None, max_length=200)
    sigle: Optional[str] = Field(None, max_length=50)
    telephone: Optional[str] = Field(None, max_length=40)
    email: Optional[str] = None
    website: Optional[str] = None
    ville: Optional[str] = Field(None, max_length=100)
    primary_color: Optional[str] = Field(None, max_length=20)


@router.get("/profil", summary="Profil de mon entreprise (plan, modules, quotas)")
def get_company_profile(
    company_id: Optional[int] = Query(None, description="Reserve au CADC ; ignore pour un admin entreprise"),
    db: Session = Depends(get_db),
    current: User = Depends(require_company_admin),
):
    company = _scoped_company(db, current, company_id)
    plan: Optional[SubscriptionPlan] = None
    if company.subscription_plan_id:
        plan = db.query(SubscriptionPlan).filter(
            SubscriptionPlan.id == company.subscription_plan_id
        ).first()
    modules = _loads(company.modules_actives, [])
    user_count = db.query(User).filter(User.company_id == company.id).count()
    return {
        "id": company.id,
        "code": company.code,
        "nom": company.nom,
        "sigle": company.sigle,
        "ville": company.ville,
        "pays": company.pays,
        "telephone": company.telephone,
        "email": company.email,
        "website": company.website,
        "logo_url": company.logo_url,
        "primary_color": company.primary_color,
        "is_active": company.is_active,
        "plan": {
            "id": plan.id,
            "nom": plan.nom,
            "code": plan.code,
            "max_modules": plan.max_modules,
            "max_users": plan.max_users,
        } if plan else None,
        "modules_actives": modules,
        "user_count": user_count,
        "role_level": current.role_level,
    }


@router.patch("/profil", summary="Modifier les informations gerables de mon entreprise")
def update_company_profile(
    payload: CompanyProfileUpdate,
    company_id: Optional[int] = Query(None),
    db: Session = Depends(get_db),
    current: User = Depends(require_company_admin),
):
    company = _scoped_company(db, current, company_id)
    for key, value in payload.dict(exclude_unset=True).items():
        setattr(company, key, value)
    db.commit()
    db.refresh(company)
    return {"id": company.id, "nom": company.nom, "message": "Profil mis a jour"}


# ── Gestion interne : collaborateurs (CRUD scope entreprise) ─────────────────
class MemberCreate(BaseModel):
    username: str = Field(..., max_length=50)
    email: str = Field(..., max_length=100)
    password: Optional[str] = Field(
        None, description="Temporaire ; genere si absent ; changer au premier login."
    )
    full_name: Optional[str] = None
    matricule: Optional[str] = Field(None, max_length=50)
    job_title: Optional[str] = Field(None, max_length=100)
    phone: Optional[str] = Field(None, max_length=20)
    role_level: int = Field(3, description="1 admin, 2 chef de departement, 3 utilisateur")
    role: Optional[str] = Field(None, description="Nom du Role (casquette) a attacher")
    department_id: Optional[int] = None


class MemberUpdate(BaseModel):
    full_name: Optional[str] = None
    email: Optional[str] = None
    phone: Optional[str] = None
    matricule: Optional[str] = None
    job_title: Optional[str] = None
    is_active: Optional[bool] = None
    department_id: Optional[int] = None


class MemberRoles(BaseModel):
    roles: List[str] = Field(..., description="Noms des roles (casquettes) ; remplacement complet")


@router.get("/utilisateurs", summary="Lister les collaborateurs de mon entreprise")
def list_members(
    company_id: Optional[int] = Query(None),
    search: Optional[str] = Query(None),
    db: Session = Depends(get_db),
    current: User = Depends(require_company_admin),
):
    company = _scoped_company(db, current, company_id)
    q = db.query(User).filter(User.company_id == company.id)
    if search:
        like = f"%{search.strip()}%"
        q = q.filter(
            (User.username.ilike(like))
            | (User.email.ilike(like))
            | (User.full_name.ilike(like))
            | (User.matricule.ilike(like))
        )
    return [_user_dict(u) for u in q.order_by(User.id.asc()).all()]


def _ensure_quota(db: Session, company: Company) -> None:
    plan = None
    if company.subscription_plan_id:
        plan = db.query(SubscriptionPlan).filter(
            SubscriptionPlan.id == company.subscription_plan_id
        ).first()
    if plan is not None and plan.max_users:
        used = db.query(User).filter(User.company_id == company.id).count()
        if used >= plan.max_users:
            raise HTTPException(
                status_code=400,
                detail=f"Quota du plan atteint ({plan.max_users} utilisateurs).",
            )


@router.post(
    "/utilisateurs",
    status_code=status.HTTP_201_CREATED,
    summary="Creer un collaborateur dans mon entreprise",
)
def create_member(
    payload: MemberCreate,
    company_id: Optional[int] = Query(None),
    db: Session = Depends(get_db),
    current: User = Depends(require_company_admin),
):
    company = _scoped_company(db, current, company_id)
    _ensure_quota(db, company)

    # Anti-escalade : un admin entreprise ne peut pas creer un niveau superieur
    # au sien. Le CADC (level 0) passe sans restriction.
    own_level = getattr(current, "role_level", 99)
    if own_level != 0 and payload.role_level < own_level:
        raise HTTPException(
            status_code=403,
            detail="Vous ne pouvez pas creer un compte plus privilegie que vous",
        )
    if db.query(User).filter(User.username == payload.username).first():
        raise HTTPException(status_code=400, detail="Ce nom d'utilisateur existe deja")
    if db.query(User).filter(User.email == payload.email).first():
        raise HTTPException(status_code=400, detail="Cet email est deja utilise")

    temp_password = payload.password or f"Emb-{secrets.token_hex(6)}!"
    try:
        validate_password_strength(temp_password, payload.username)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc))

    member = User(
        username=payload.username,
        email=payload.email,
        hashed_password=get_password_hash(temp_password),
        full_name=payload.full_name or payload.username,
        matricule=payload.matricule,
        job_title=payload.job_title,
        phone=payload.phone,
        company_id=company.id,
        department_id=payload.department_id,
        role_level=payload.role_level,
        is_active=True,
        is_superuser=False,
        must_change_password=True,
    )
    if payload.role:
        db_role = db.query(Role).filter(Role.name == payload.role.upper()).first()
        if db_role:
            member.roles.append(db_role)
    db.add(member)
    db.commit()
    db.refresh(member)
    out = _user_dict(member)
    out["temporary_password"] = temp_password
    return out


def _get_member(db: Session, current: User, member_id: int) -> User:
    target = db.query(User).filter(User.id == member_id).first()
    if not target:
        raise HTTPException(status_code=404, detail="Utilisateur non trouve")
    if current.role_level != 0 and target.company_id != current.company_id:
        raise HTTPException(status_code=403, detail="Utilisateur hors de votre entreprise")
    if target.role_level == 0:
        raise HTTPException(status_code=403, detail="Compte Super Admin non modifiable ici")
    return target


@router.put("/utilisateurs/{member_id}", summary="Modifier un collaborateur (profil/responsabilites)")
def update_member(
    member_id: int,
    payload: MemberUpdate,
    db: Session = Depends(get_db),
    current: User = Depends(require_company_admin),
):
    member = _get_member(db, current, member_id)
    data = payload.dict(exclude_unset=True)
    if "email" in data and data["email"]:
        clash = db.query(User).filter(User.email == data["email"], User.id != member.id).first()
        if clash:
            raise HTTPException(status_code=400, detail="Cet email est deja utilise")
    for key, value in data.items():
        setattr(member, key, value)
    db.commit()
    db.refresh(member)
    return _user_dict(member)


@router.patch("/utilisateurs/{member_id}/responsabilites", summary="Attacher les roles (casquettes) d'un collaborateur")
def set_member_roles(
    member_id: int,
    payload: MemberRoles,
    db: Session = Depends(get_db),
    current: User = Depends(require_company_admin),
):
    """Utilisateur != Role : un collaborateur peut porter plusieurs casquettes.

    Un admin entreprise ne peut attacher que des roles de niveau >= 1 (jamais un
    role level 0) et uniquement des roles systeme ou de SON entreprise.
    """
    member = _get_member(db, current, member_id)
    names = [n.strip().upper() for n in payload.roles if n.strip()]
    resolved: List[Role] = []
    for name in names:
        role = db.query(Role).filter(Role.name == name).first()
        if not role:
            raise HTTPException(status_code=400, detail=f"Role inconnu : {name}")
        if current.role_level != 0:
            if role.level == 0:
                raise HTTPException(
                    status_code=403,
                    detail=f"Role reserve au CADC : {role.name}",
                )
            if role.company_id is not None and role.company_id != current.company_id:
                raise HTTPException(
                    status_code=403,
                    detail=f"Role d'une autre entreprise : {role.name}",
                )
        resolved.append(role)
    member.roles = resolved
    db.commit()
    db.refresh(member)
    return {"id": member.id, "roles": [r.name for r in member.roles]}


@router.patch("/utilisateurs/{member_id}/statut", summary="Activer / desactiver un collaborateur")
def toggle_member_status(
    member_id: int,
    db: Session = Depends(get_db),
    current: User = Depends(require_company_admin),
):
    member = _get_member(db, current, member_id)
    if member.id == current.id:
        raise HTTPException(status_code=400, detail="Impossible de se desactiver soi-meme")
    member.is_active = not member.is_active
    db.commit()
    db.refresh(member)
    return {"id": member.id, "is_active": member.is_active}


# ── Modules alloues / demandes d'accreditation vers le CADC ──────────────────
@router.get("/modules", summary="Modules alloues, demandes en cours, modules verrouilles")
def modules_overview(
    company_id: Optional[int] = Query(None),
    db: Session = Depends(get_db),
    current: User = Depends(require_company_admin),
):
    """Ecran ``Modules alloues / demandes`` : le catalogue complet est rendu,
    chaque module porte son etat :

    - ``alloue``            : dans ``Company.modules_actives`` ;
    - ``accredite``         : une accreditation active (delai en cours) le debloque ;
    - ``demande``           : une demande est en attente d'arbitrage CADC ;
    - ``verrouille``        : ni alloue ni accredite — visible mais non accessible.
    """
    company = _scoped_company(db, current, company_id)
    allocated = {str(m).lower() for m in _loads(company.modules_actives, [])}

    plan = None
    if company.subscription_plan_id:
        plan = db.query(SubscriptionPlan).filter(
            SubscriptionPlan.id == company.subscription_plan_id
        ).first()

    accrs = (
        db.query(Accreditation)
        .filter(Accreditation.company_id == company.id, Accreditation.type == ACC_TYPE_PERMISSION)
        .all()
    )
    accredited, pending = set(), set()
    pending_items: List[Dict[str, Any]] = []
    for a in accrs:
        mod = (a.module or "").lower()
        if not mod:
            continue
        if a.statut == ACC_STATUT_DEMANDE:
            pending.add(mod)
            pending_items.append({
                "id": a.id,
                "code": a.code,
                "module": a.module,
                "libelle": a.libelle,
                "motif": a.motif,
                "created_at": a.created_at,
            })
        elif a.est_valide():
            accredited.add(mod)

    catalog = []
    for key in _catalog_keys():
        if key in allocated:
            etat = "alloue"
        elif key in accredited:
            etat = "accredite"
        elif key in pending:
            etat = "demande"
        else:
            etat = "verrouille"
        catalog.append({"key": key, "etat": etat})

    return {
        "company_id": company.id,
        "modules_actives": sorted(allocated),
        "max_modules": plan.max_modules if plan else None,
        "user_count": db.query(User).filter(User.company_id == company.id).count(),
        "max_users": plan.max_users if plan else None,
        "modules": catalog,
        "demandes": pending_items,
    }


class ModuleRequestCreate(BaseModel):
    module: str = Field(..., max_length=50, description="Cle de module (ex: transport)")
    libelle: Optional[str] = None
    motif: Optional[str] = None


@router.post(
    "/modules/demandes",
    status_code=status.HTTP_201_CREATED,
    summary="Demander un module au CADC (accreditation future)",
)
def request_module(
    payload: ModuleRequestCreate,
    company_id: Optional[int] = Query(None),
    db: Session = Depends(get_db),
    current: User = Depends(require_company_admin),
):
    company = _scoped_company(db, current, company_id)
    mod = payload.module.strip().lower()
    if mod not in _catalog_keys():
        raise HTTPException(status_code=400, detail=f"Module inconnu : {payload.module}")
    allocated = {str(m).lower() for m in _loads(company.modules_actives, [])}
    if mod in allocated:
        raise HTTPException(
            status_code=400,
            detail="Ce module est deja alloue a votre entreprise ; aucune demande n'est necessaire.",
        )
    dup = (
        db.query(Accreditation)
        .filter(
            Accreditation.company_id == company.id,
            Accreditation.module == mod,
            Accreditation.statut == ACC_STATUT_DEMANDE,
        )
        .first()
    )
    if dup:
        raise HTTPException(status_code=400, detail="Une demande est deja en attente pour ce module")

    # Le porteur de la demande est l'admin qui la emits ; la demande ne vaut
    # pas droit d'acces (statut != actif -> ignoree par le moteur d'autorisation).
    req = Accreditation(
        user_id=current.id if current.id else 1,
        company_id=company.id,
        code=f"REQ-{secrets.token_hex(4).upper()}",
        libelle=payload.libelle or f"Demande d'acces au module {mod}",
        type=ACC_TYPE_PERMISSION,
        permission_code=f"{mod}.*.*",
        module=mod,
        statut=ACC_STATUT_DEMANDE,
        motif=payload.motif,
    )
    db.add(req)
    db.commit()
    db.refresh(req)
    return {
        "id": req.id,
        "code": req.code,
        "module": req.module,
        "statut": req.statut,
        "message": "Demande transmise au CADC ; en attente d'arbitrage.",
    }


@router.delete(
    "/modules/demandes/{request_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Retirer une demande d'accreditation en attente",
)
def cancel_module_request(
    request_id: int,
    db: Session = Depends(get_db),
    current: User = Depends(require_company_admin),
):
    req = db.query(Accreditation).filter(Accreditation.id == request_id).first()
    if not req or req.statut != ACC_STATUT_DEMANDE:
        raise HTTPException(status_code=404, detail="Demande introuvable ou deja traitee")
    # Un admin entreprise ne retire que les demandes de SON entreprise ; le CADC
    # (level 0 / superuser) arbitre sur toutes.
    if not _is_superadmin(current) and req.company_id != getattr(current, "company_id", None):
        raise HTTPException(status_code=403, detail="Demande d'une autre entreprise")
    db.delete(req)
    db.commit()
    return None
