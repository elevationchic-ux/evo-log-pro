"""Router FastAPI  RBAC Multi-tenant EVO-LOG SaaS"""
from typing import List
from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.services.rbac_service import RBACService
from app.schemas.rbac import (
    TenantCreate, TenantResponse, RoleCreate, RoleResponse,
    UserRoleAssignRequest, UserRoleAssignResponse,
    PermissionCheckRequest, PermissionCheckResponse
)

router = APIRouter()


# ── Tenants ───────────────────────────────────────────────────────────────────
@router.get("/tenants", summary="Lister tous les tenants (SuperAdmin uniquement)")
def list_tenants(db: Session = Depends(get_db)):
    return RBACService.get_all_tenants(db)


@router.get("/tenants/{tenant_id}/users", summary="Lister les utilisateurs d'un tenant")
def list_tenant_users(tenant_id: int, db: Session = Depends(get_db)):
    return RBACService.get_users_by_tenant(db, tenant_id)


# ── Rôles ─────────────────────────────────────────────────────────────────────
@router.get("/roles", summary="Lister tous les rôles disponibles avec leurs permissions")
def list_roles(db: Session = Depends(get_db)):
    return RBACService.get_all_roles(db)


# ── Permissions ───────────────────────────────────────────────────────────────
@router.post("/permissions/check", response_model=PermissionCheckResponse, summary="Vérifier si un utilisateur a une permission")
def check_permission(payload: PermissionCheckRequest, db: Session = Depends(get_db)):
    """Vérifie dynamiquement si un utilisateur dispose d'une permission atomique."""
    return RBACService.check_permission(
        db=db,
        user_id=payload.user_id,
        tenant_id=payload.tenant_id,
        permission_code=payload.permission_code
    )
