"""Router FastAPI RBAC Multi-tenant EVO-LOG SaaS.

Securise : la liste des tenants (toutes entreprises) est reservee au
SuperAdmin ; la lecture des roles et le controle de permission sont reservés
aux administrateurs (level <= 1). Un endpoint de catalogue expose l'arborescence
domaine > module > sous-module > actions pour l'UI d'administration.
"""
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.services.rbac_service import RBACService
from app.schemas.rbac import PermissionCheckRequest, PermissionCheckResponse
from app.utils.rbac import require_company_admin, require_min_role_level, require_superadmin
from app.core.permission_catalog import build_catalog_tree
from app.models.user import User, Role, Permission

router = APIRouter()


class RolePermissionsPayload(BaseModel):
    codes: List[str]


def _load_editable_role(db: Session, role_id: int, current: User) -> Role:
    """Charge un role editables par l'admin courant et le verrouille au tenant."""
    role = db.query(Role).filter(Role.id == role_id).first()
    if not role:
        raise HTTPException(status_code=404, detail="Role introuvable")
    # Un admin entreprise ne touche ni aux roles d'une autre entreprise, ni aux
    # roles d'administration (level <= 1) pour eviter toute auto-escalade.
    if not current.is_superuser:
        if role.company_id not in (None, current.company_id):
            raise HTTPException(status_code=403, detail="Role hors de votre entreprise")
        if role.level is not None and role.level <= 1:
            raise HTTPException(status_code=403, detail="Role d'administration non modifiable")
    return role


# ── Arbre de permissions granulaires d'un role (UI d'administration) ──────────
@router.get("/roles/{role_id}/permissions", summary="Codes de permissions d'un role")
def get_role_permissions(
    role_id: int,
    db: Session = Depends(get_db),
    current: User = Depends(require_company_admin),
):
    role = _load_editable_role(db, role_id, current)
    return {
        "role_id": role.id,
        "role_name": role.name,
        "codes": sorted({p.code for p in (role.permissions or [])}),
    }


@router.put("/roles/{role_id}/permissions", summary="Remplacer les permissions d'un role")
def set_role_permissions(
    role_id: int,
    payload: RolePermissionsPayload,
    db: Session = Depends(get_db),
    current: User = Depends(require_company_admin),
):
    role = _load_editable_role(db, role_id, current)
    wanted = {(c or "").strip() for c in payload.codes if (c or "").strip()}
    perms: List[Permission] = []
    for code in sorted(wanted):
        perm = db.query(Permission).filter(Permission.code == code).first()
        if not perm:
            module, sub_module, action = Permission.parse_code(code)
            perm = Permission(
                code=code, name=code, module=module,
                sub_module=sub_module, action=action, resource=sub_module,
            )
            db.add(perm)
            db.flush()
        perms.append(perm)
    role.permissions = perms
    db.commit()
    return {"role_id": role.id, "granted": len(perms), "codes": sorted(wanted)}



# ── Catalogue des permissions (lecture : admins) ──────────────────────────────
@router.get("/permissions/catalog", summary="Arborescence complete des permissions")
def permissions_catalog(_: User = Depends(require_min_role_level(2))):
    return build_catalog_tree()


# ── Tenants (SuperAdmin uniquement) ───────────────────────────────────────────
@router.get("/tenants", summary="Lister tous les tenants (SuperAdmin uniquement)")
def list_tenants(db: Session = Depends(get_db), _: User = Depends(require_superadmin)):
    return RBACService.get_all_tenants(db)


@router.get("/tenants/{tenant_id}/users", summary="Lister les utilisateurs d'un tenant")
def list_tenant_users(
    tenant_id: int,
    db: Session = Depends(get_db),
    current: User = Depends(require_company_admin),
):
    # Un admin entreprise ne peut consulter que SON entreprise.
    if not current.is_superuser and current.company_id and current.company_id != tenant_id:
        return []
    return RBACService.get_users_by_tenant(db, tenant_id)


# ── Rôles ─────────────────────────────────────────────────────────────────────
@router.get("/roles", summary="Lister les roles disponibles avec leurs permissions")
def list_roles(
    db: Session = Depends(get_db),
    current: User = Depends(require_min_role_level(2)),
):
    company_id: Optional[int] = None if current.is_superuser else current.company_id
    return RBACService.get_all_roles(db, company_id)


# ── Permissions ───────────────────────────────────────────────────────────────
@router.post("/permissions/check", response_model=PermissionCheckResponse, summary="Verifier si un utilisateur a une permission")
def check_permission(
    payload: PermissionCheckRequest,
    db: Session = Depends(get_db),
    current: User = Depends(require_company_admin),
):
    """Evalue reellement une permission atomique pour un utilisateur donne."""
    return RBACService.check_permission(
        db=db,
        user_id=payload.user_id,
        tenant_id=payload.tenant_id,
        permission_code=payload.permission_code,
    )
