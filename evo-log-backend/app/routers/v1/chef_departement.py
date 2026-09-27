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

Ce routeur n'accorde AUCUN module : la liste des collaborateurs est une lecture
du perimetre humain du departement. L'octroi d'accreditation interne et le
planning sont des tranches suivantes (cf. plan Phase 3 / Phase 4).
"""
import json
from typing import Any, Dict, Optional

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.models.tenant import Department
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
