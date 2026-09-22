"""Role router - Hierarchical RBAC for multi-tenant SAAS"""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List

from app.core.database import get_db
from app.core.security import get_current_user
from app.models.user import User
from app.schemas.role import RoleCreate, RoleUpdate, RoleResponse, UserRoleAssignment
from app.services.role_service import RoleService
from app.models.user import Role


router = APIRouter(tags=["Role Management"])


@router.post("/init-system-roles", status_code=status.HTTP_201_CREATED)
def initialiser_roles_systeme(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Initialize system-wide predefined roles (Super Admin only)"""
    if not current_user.is_superuser:
        raise HTTPException(status_code=403, detail="Super Admin required")
    
    RoleService.initialiser_roles_systeme(db)
    return {"message": "Système roles initialisés avec succès"}


@router.post("/roles", response_model=RoleResponse, status_code=status.HTTP_201_CREATED)
def creer_role(
    role: RoleCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Create a role"""
    if current_user.role_level > 1:
        raise HTTPException(status_code=403, detail="Admin Entreprise required")
    if not current_user.is_superuser and (
        not current_user.company_id
        or role.company_id != current_user.company_id
        or role.level <= current_user.role_level
    ):
        raise HTTPException(status_code=403, detail="Role hors du périmètre autorisé")
    
    return RoleService.creer_role(
        db, role.name, role.description, role.level,
        role.company_id, role.modules_allowed
    )


@router.get("/roles", response_model=List[RoleResponse])
def lister_roles(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """List roles (filtered by company for non-super-admins)"""
    if current_user.is_superuser:
        return db.query(Role).all()
    elif current_user.company_id:
        return db.query(Role).filter(
            (Role.company_id == current_user.company_id) | (Role.company_id == None)
        ).all()
    else:
        return db.query(Role).filter(Role.company_id == None).all()


@router.put("/roles/{role_id}/modules", response_model=RoleResponse)
def mettre_a_jour_modules_role(
    role_id: int,
    modules_allowed: List[str],
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Update allowed modules for a role"""
    if current_user.role_level > 1:
        raise HTTPException(status_code=403, detail="Admin Entreprise required")
    
    try:
        return RoleService.mettre_a_jour_modules_role(
            db, role_id, modules_allowed, actor=current_user
        )
    except (ValueError, PermissionError) as exc:
        raise HTTPException(status_code=403, detail=str(exc))


@router.post("/users/{user_id}/roles")
def assigner_role_user(
    user_id: int,
    assignment: UserRoleAssignment,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Assign role to user"""
    if current_user.role_level > 1:
        raise HTTPException(status_code=403, detail="Admin Entreprise required")
    
    try:
        RoleService.assigner_role_user(
            db, user_id, assignment.role_id, actor=current_user
        )
    except PermissionError as exc:
        raise HTTPException(status_code=403, detail=str(exc))
    except ValueError as exc:
        raise HTTPException(status_code=404, detail=str(exc))
    return {"message": "Role assigné avec succès"}


@router.delete("/users/{user_id}/roles/{role_id}")
def retirer_role_user(
    user_id: int,
    role_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Remove role from user"""
    if current_user.role_level > 1:
        raise HTTPException(status_code=403, detail="Admin Entreprise required")
    
    try:
        RoleService.retirer_role_user(db, user_id, role_id, actor=current_user)
    except PermissionError as exc:
        raise HTTPException(status_code=403, detail=str(exc))
    except ValueError as exc:
        raise HTTPException(status_code=404, detail=str(exc))
    return {"message": "Role retiré avec succès"}
