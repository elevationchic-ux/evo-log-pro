"""Centralised RBAC dependencies.

Role model (``User.role_level``):
    0 = Super Admin   (plateforme, n'appartient a AUCUNE entreprise)
    1 = Admin Entreprise (administrateur complet de SA societe)
    2 = Chef de departement
    3 = Utilisateur / operateur

These helpers are the single source of truth for authorisation across routers.
Previously ``require_role`` was a no-op stub returning the user unconditionally;
it is now enforced. Everything builds on ``is_superuser``, ``role_level`` and
``company_id`` so the Super Admin / Admin Entreprise separation stays coherent.
"""
from typing import Callable, List, Optional

from fastapi import Depends, HTTPException, status

from app.core.security import get_current_user
from app.core.tenant_access import ensure_company_scope, ensure_module_access
from app.models.user import User

# Role level constants ------------------------------------------------------- #
LEVEL_SUPERADMIN = 0
LEVEL_COMPANY_ADMIN = 1
LEVEL_DEPARTMENT_HEAD = 2
LEVEL_USER = 3


def _is_superadmin(user: User) -> bool:
    return bool(getattr(user, "is_superuser", False)) or getattr(user, "role_level", 99) == LEVEL_SUPERADMIN


def require_role(roles: List[str]) -> Callable:
    """Dependency factory enforcing that the user holds one of ``roles``.

    A super admin always passes. Role comparison is case-insensitive and also
    accepts the numeric ``role_level`` encoded as a string (e.g. ``"1"``).
    """
    wanted = {str(r).strip().upper() for r in roles}

    def dependency(current_user: User = Depends(get_current_user)) -> User:
        if _is_superadmin(current_user):
            return current_user
        user_roles = {str(r.name).strip().upper() for r in (current_user.roles or [])}
        if user_roles & wanted:
            return current_user
        # allow matching by role_level encoded as string
        if str(getattr(current_user, "role_level", None)) in wanted:
            return current_user
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=f"Role requis : {'/'.join(sorted(wanted))}",
        )

    return dependency


def require_superadmin(current_user: User = Depends(get_current_user)) -> User:
    """Platform Super Admin only. Never belongs to a company.

    These console routes must be invisible to everyone else, including Admin
    Entreprise, so we require the super admin flag / level 0 explicitly.
    """
    if not _is_superadmin(current_user):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Acces reserve : Super Administrateur plateforme",
        )
    return current_user


def require_company_admin(current_user: User = Depends(get_current_user)) -> User:
    """Admin Entreprise (level 1) or Super Admin.

    An Admin Entreprise must be attached to a company to act. A Super Admin is
    allowed through so they can operate on any company via an explicit
    ``company_id`` argument (the caller still has to honour tenancy scoping).
    """
    if _is_superadmin(current_user):
        return current_user
    level = getattr(current_user, "role_level", 99)
    if level <= LEVEL_COMPANY_ADMIN and getattr(current_user, "company_id", None):
        return current_user
    raise HTTPException(
        status_code=status.HTTP_403_FORBIDDEN,
        detail="Acces reserve : Administrateur d'entreprise",
    )


def require_min_role_level(max_level: int) -> Callable:
    """Allow users whose ``role_level`` is at or above the requested authority.

    Lower number == more authority. ``require_min_role_level(2)`` permits
    Super Admin (0), Admin Entreprise (1) and Chef de departement (2).
    """

    def dependency(current_user: User = Depends(get_current_user)) -> User:
        if _is_superadmin(current_user):
            return current_user
        if getattr(current_user, "role_level", 99) <= max_level:
            return current_user
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Privileges insuffisants pour cette operation",
        )

    return dependency


def require_module(module_name: str) -> Callable:
    """Dependency factory enforcing access to a business module.

    Combines the company scope check with the module entitlement logic from
    :mod:`app.core.tenant_access` (role/department ``modules_allowed``).
    """

    def dependency(current_user: User = Depends(get_current_user)) -> User:
        ensure_company_scope(
            current_user,
            getattr(current_user, "company_id", None),
            allow_none=True,
        )
        ensure_module_access(current_user, module_name)
        return current_user

    return dependency


def resolve_scope_company_id(current_user: User, requested: Optional[int]) -> int:
    """Return the company id an admin-entreprise action should target.

    * Super Admin must pass an explicit ``requested`` company id.
    * Admin Entreprise is always pinned to their own company; a mismatch is
      rejected so they can never act on another tenant.
    """
    if _is_superadmin(current_user):
        if not requested:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="company_id requis pour un Super Admin",
            )
        return requested
    own = getattr(current_user, "company_id", None)
    if not own:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Aucune entreprise associee a ce compte",
        )
    if requested and requested != own:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access denied to this company",
        )
    return own
