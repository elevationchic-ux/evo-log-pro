"""Espace departement (Phase 3 — niveau 2, Chef de departement).

Perimetre strict : un chef de departement (role_level 2) ne voit et ne pilote
QUE les collaborateurs de SON departement. L'Admin Entreprise (1) et le CADC (0)
peuvent cibler n'importe quel departement, mais toujours a l'interieur de leur
entreprise (403 cross-tenant), ce que verifie ``_scoped_department``.

Garde (invisibilite double, cf. plan) :
- ``require_department_head`` (utils/rbac.py) : niveau <= 2 ; un niveau 2 doit
  porter un ``department_id`` ; niveau 3 -> 403.
- ``_scoped_department`` : epingle un chef a son departement ; un admin/CADC
  doit passer un ``department_id`` explicite et l'appartenance d'entreprise est
  controlee.

Tranche A (lecture) : roster humain + fiche du departement. Tranche B (ecriture) :
- un chef (2) AFFECTE / RETIRE des COLLABORATEURS (niveau 3) de SON departement ;
  il ne touche jamais un niveau 1/2, ni un compte d'une autre entreprise, ni un
  Super Admin ;
- l'ALLOCATION des modules d'un departement releve de l'Admin Entreprise (1) /
  CADC (0) UNIQUEMENT (un chef ne se auto-grantit pas de module) et reste STRICTEMENT
  bornee par ``Company.modules_actives`` (un departement ne peut pas depasser son
  entreprise). Le planning/presence reste une tranche suivante (cf. plan Phase 4).
"""
import json
from typing import Any, Dict, List, Optional

from fastapi import APIRouter, Depends, HTTPException, Query, status
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.models.tenant import Company, Department
from app.models.user import User
from app.utils.rbac import _is_superadmin, require_department_head

router = APIRouter(dependencies=[Depends(require_department_head)])


def _loads(raw: Optional[str], default: Any) -> Any:
    if not raw:
        return default
    try:
        return json.loads(raw)
    except (json.JSONDecodeError, TypeError):
        return default


def _scoped_department(db: Session, current: User, requested: Optional[int]) -> Department:
    """Resout le departement cible selon le niveau de l'appelant.

    - Chef (2) : epingle a ``current.department_id`` ; un ``requested`` divergent
      -> 403 (il ne peut pas telecharger un autre departement).
    - Admin entreprise (1) : ``department_id`` requis ; le departement doit
      appartenir a SON entreprise, sinon 403.
    - CADC (0) : ``department_id`` explicite requis (un super-admin ne porte
      aucune entreprise/departement par defaut).
    """
    own_level = getattr(current, "role_level", 99)

    if _is_superadmin(current):
        if not requested:
            raise HTTPException(
                status_code=400,
                detail="department_id requis pour un Super Admin",
            )
        dept = db.query(Department).filter(Department.id == requested).first()
        if not dept:
            raise HTTPException(status_code=404, detail="Departement introuvable")
        return dept

    if own_level == 2:
        own_dept_id = getattr(current, "department_id", None)
        if requested and requested != own_dept_id:
            raise HTTPException(
                status_code=403,
                detail="Hors de votre departement",
            )
        dept = db.query(Department).filter(Department.id == own_dept_id).first()
        if not dept:
            raise HTTPException(status_code=403, detail="Departement introuvable pour ce compte")
        return dept

    # Admin entreprise (1) : gere n'importe quel departement de SON entreprise.
    if not requested:
        raise HTTPException(
            status_code=400,
            detail="department_id requis (choisissez un departement de votre entreprise)",
        )
    dept = db.query(Department).filter(Department.id == requested).first()
    if not dept:
        raise HTTPException(status_code=404, detail="Departement introuvable")
    if dept.company_id != getattr(current, "company_id", None):
        raise HTTPException(
            status_code=403,
            detail="Departement d'une autre entreprise",
        )
    return dept


def _member_dict(u: User) -> Dict[str, Any]:
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
        "department_id": u.department_id,
        "roles": [r.name for r in (u.roles or [])],
    }


def _guard_target(db: Session, current: User, dept: Department, member_id: int) -> User:
    """Cible d'une ecriture membre : existe, meme entreprise que le departement,
    et jamais un compte Super Admin.

    Un chef de departement (niveau 2) ne pilote QUE des collaborateurs (niveau 3) :
    il ne peut ni deplacer un pair/superieur (niveau 1 ou 2), ni toucher un autre
    tenant. L'admin entreprise (1) et le CADC (0) gerent tout compte non-superieur
    de leur perimetre (regle alignee sur company_admin).
    """
    target = db.query(User).filter(User.id == member_id).first()
    if not target:
        raise HTTPException(status_code=404, detail="Utilisateur non trouve")
    if getattr(target, "company_id", None) != dept.company_id:
        raise HTTPException(
            status_code=403,
            detail="Collaborateur hors de l'entreprise de ce departement",
        )
    if getattr(target, "role_level", 99) == 0:
        raise HTTPException(status_code=403, detail="Compte Super Admin non modifiable ici")
    if getattr(current, "role_level", 99) == 2 and getattr(target, "role_level", 99) != 3:
        raise HTTPException(
            status_code=403,
            detail="Un chef de departement ne pilote que des collaborateurs (niveau 3)",
        )
    return target


@router.get("/overview", summary="Fiche de mon departement (nom, modules, effectif)")
def department_overview(
    department_id: Optional[int] = Query(None, description="Reserve admin/CADC ; ignore pour un chef"),
    db: Session = Depends(get_db),
    current: User = Depends(require_department_head),
):
    dept = _scoped_department(db, current, department_id)
    members = (
        db.query(User)
        .filter(User.department_id == dept.id, User.company_id == dept.company_id)
        .all()
    )
    manager = None
    if dept.manager_id:
        mgr = db.query(User).filter(User.id == dept.manager_id).first()
        if mgr:
            manager = {"id": mgr.id, "username": mgr.username, "full_name": mgr.full_name}
    return {
        "id": dept.id,
        "company_id": dept.company_id,
        "code": dept.code,
        "nom": dept.nom,
        "description": dept.description,
        "modules_allowed": _loads(dept.modules_allowed, []),
        "effectif": len(members),
        "manager": manager,
        "is_active": dept.is_active,
        "role_level_callant": current.role_level,
    }


@router.get("/membres", summary="Lister les collaborateurs de mon departement")
def list_members(
    department_id: Optional[int] = Query(None, description="Reserve admin/CADC ; ignore pour un chef"),
    search: Optional[str] = Query(None),
    include_inactive: bool = Query(True, description="Inclure les comptes desactives"),
    db: Session = Depends(get_db),
    current: User = Depends(require_department_head),
):
    """Roster humain du departement, scope par ``department_id`` ET ``company_id``.

    Le chef de departement (2) ne peut jamais telecharger un autre departement :
    ``_scoped_department`` l'y epingle. On filtre aussi sur ``company_id`` pour
    qu'un identifiant de departement devine ne fuite jamais une autre entreprise.
    """
    dept = _scoped_department(db, current, department_id)
    q = db.query(User).filter(
        User.department_id == dept.id,
        User.company_id == dept.company_id,
    )
    if not include_inactive:
        q = q.filter(User.is_active.is_(True))
    if search:
        like = f"%{search.strip()}%"
        q = q.filter(
            (User.username.ilike(like))
            | (User.email.ilike(like))
            | (User.full_name.ilike(like))
            | (User.matricule.ilike(like))
        )
    return [_member_dict(u) for u in q.order_by(User.id.asc()).all()]


# ── Tranche B : ecritures (affectation / retrait de membres, allocation modules) ──
class DepartmentModulesPayload(BaseModel):
    modules: List[str] = Field(default_factory=list, description="Cles de modules autorisees pour ce departement")


@router.post(
    "/membres/{member_id}/affecter",
    summary="Affecter un collaborateur a mon departement",
)
def affect_member(
    member_id: int,
    department_id: Optional[int] = Query(None, description="Reserve admin/CADC ; ignore pour un chef"),
    db: Session = Depends(get_db),
    current: User = Depends(require_department_head),
):
    """Rattache ``member_id`` au departement resolu (epingle au dept du chef).

    Un chef ne peut que faire ENTRER un collaborateur (niveau 3) de SON entreprise
    dans SON departement ; un admin/CADC peut placer un niveau 2/3 dans n'importe
    quel departement de son entreprise.
    """
    dept = _scoped_department(db, current, department_id)
    target = _guard_target(db, current, dept, member_id)
    previous = target.department_id
    target.department_id = dept.id
    db.commit()
    db.refresh(target)
    return {
        "id": target.id,
        "department_id": target.department_id,
        "previous_department_id": previous,
        "member": _member_dict(target),
    }


@router.post(
    "/membres/{member_id}/retirer",
    summary="Retirer un collaborateur de mon departement",
)
def remove_member(
    member_id: int,
    department_id: Optional[int] = Query(None, description="Reserve admin/CADC ; ignore pour un chef"),
    db: Session = Depends(get_db),
    current: User = Depends(require_department_head),
):
    """Decroche ``member_id`` du departement resolu (``department_id`` -> None).

    Le collaborateur doit ACTUELLEMENT appartenir a ce departement ; on ne retire
    jamais quelqu'un d'un departement qui n'est pas le sien, et jamais de soi-meme.
    """
    dept = _scoped_department(db, current, department_id)
    target = _guard_target(db, current, dept, member_id)
    if target.id == current.id:
        raise HTTPException(status_code=400, detail="Impossible de vous retirer vous-meme")
    if target.department_id != dept.id:
        raise HTTPException(
            status_code=400,
            detail="Ce collaborateur n'appartient pas a ce departement",
        )
    target.department_id = None
    db.commit()
    db.refresh(target)
    return {"id": target.id, "department_id": None, "member": _member_dict(target)}


@router.put(
    "/modules",
    summary="Definir les modules autorises d'un departement (admin entreprise / CADC)",
)
def set_department_modules(
    payload: DepartmentModulesPayload,
    department_id: Optional[int] = Query(None, description="Reserve admin/CADC ; ignore pour un chef"),
    db: Session = Depends(get_db),
    current: User = Depends(require_department_head),
):
    """Allocation des modules d'un departement — GARELEE aux niveaux <= 1.

    Un chef (niveau 2) ne peut pas se auto-grantir un module : toute ecriture ici
    est refusee 403. Les modules demandes doivent etre SOUS-ENSEMBLE des modules
    alloues a l'entreprise (``Company.modules_actives``) : un departement ne peut
    jamais depasser son tenant.
    """
    if getattr(current, "role_level", 99) == 2 and not _is_superadmin(current):
        raise HTTPException(
            status_code=403,
            detail="Allocation des modules reservee a l'Admin Entreprise / CADC",
        )
    dept = _scoped_department(db, current, department_id)
    company = db.query(Company).filter(Company.id == dept.company_id).first()
    if not company:
        raise HTTPException(status_code=404, detail="Entreprise du departement introuvable")

    allocated = {str(m).lower() for m in _loads(company.modules_actives, [])}
    # Dedoupage conservant l'ordre, normalise en minuscules.
    requested: List[str] = []
    for raw in payload.modules:
        mod = str(raw).strip().lower()
        if mod and mod not in requested:
            requested.append(mod)
    for mod in requested:
        if mod not in allocated:
            raise HTTPException(
                status_code=400,
                detail=f"Module non alloue a l'entreprise : {mod}",
            )
    dept.modules_allowed = json.dumps(requested, ensure_ascii=False)
    db.commit()
    db.refresh(dept)
    return {"id": dept.id, "modules_allowed": requested}
