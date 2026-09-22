"""Tenant and module access helpers for multi-company ERP operations."""

import json
from typing import Iterable, Optional, Set, Type

from fastapi import Depends, HTTPException, status

from app.core.security import get_current_user
from app.models.tenant import Department
from app.models.user import User


def scope_query(query, model: Type, user: User, *, include_department: bool = True):
    """Apply the tenant boundary shared by ORM list/detail queries."""
    if user.is_superuser:
        return query
    company_column = getattr(model, "company_id", None)
    if company_column is not None:
        query = query.filter(company_column == user.company_id)
    if include_department and user.department_id:
        department_column = getattr(model, "department_id", None)
        if department_column is not None:
            query = query.filter(department_column == user.department_id)
    return query


def _normalize_modules(raw) -> Set[str]:
    if raw in (None, "", []):
        return set()
    if isinstance(raw, str):
        try:
            values = json.loads(raw)
        except json.JSONDecodeError:
            return {raw.strip()}
    else:
        values = raw

    if isinstance(values, str):
        return {values.strip()}
    if isinstance(values, Iterable):
        return {str(item).strip().lower() for item in values if str(item).strip()}
    return set()


def can_access_module(user: Optional[User], module_name: str) -> bool:
    """Check whether a user may access a module within their company and department."""
    if user is None:
        return False
    if user.is_superuser:
        return True
    if not module_name:
        return True

    allowed_modules: Set[str] = set()
    if getattr(user, "roles", None):
        for role in user.roles:
            allowed_modules |= _normalize_modules(getattr(role, "modules_allowed", None))

    if getattr(user, "department_id", None):
        department = user.department
        if department is not None:
            allowed_modules |= _normalize_modules(getattr(department, "modules_allowed", None))

    module_key = str(module_name).strip().lower()
    if not allowed_modules:
        return True
    return module_key in allowed_modules


def ensure_company_scope(user: User, company_id: Optional[int], *, allow_none: bool = False):
    if company_id is None and allow_none:
        return
    if user.is_superuser:
        return
    if company_id is None or user.company_id != company_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access denied to this company",
        )


def ensure_department_scope(user: User, department_id: Optional[int], *, allow_none: bool = False):
    if department_id is None and allow_none:
        return
    if user.is_superuser:
        return
    if department_id is None or user.department_id != department_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access denied to this department",
        )


def ensure_module_access(user: User, module_name: str):
    if not can_access_module(user, module_name):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=f"Access denied to module: {module_name}",
        )


def require_module_access(
    module_name: str,
    *,
    company_id: Optional[int] = None,
    department_id: Optional[int] = None,
    enforce_company_scope: bool = True,
    enforce_department_scope: bool = True,
):
    """FastAPI dependency enforcing company department and module access."""

    def _dependency(current_user: User = Depends(get_current_user)) -> User:
        if enforce_company_scope:
            target_company_id = company_id if company_id is not None else getattr(current_user, "company_id", None)
            ensure_company_scope(current_user, target_company_id, allow_none=(target_company_id is None))

        if enforce_department_scope:
            target_department_id = department_id if department_id is not None else getattr(current_user, "department_id", None)
            ensure_department_scope(current_user, target_department_id, allow_none=(target_department_id is None))

        ensure_module_access(current_user, module_name)
        return current_user

    return _dependency


def require_company_access(
    module_name: Optional[str] = None,
    *,
    company_id: Optional[int] = None,
    department_id: Optional[int] = None,
):
    """Convenience dependency for company-scoped endpoints."""
    module = module_name or "general"
    return require_module_access(
        module,
        company_id=company_id,
        department_id=department_id,
        enforce_company_scope=True,
        enforce_department_scope=True,
    )
