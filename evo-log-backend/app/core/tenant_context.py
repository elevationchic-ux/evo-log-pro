"""
Tenant isolation context.

A single source of truth for the "current company" of an in-flight request,
propagated via contextvars so it is visible to SQLAlchemy session events
without threading parameters through every router.

Design
------
- The request-scoped tenant id is set by ``TenantContextMiddleware`` after the
  JWT is decoded, and cleared in a finally block.
- ``bypass_tenant_filter()`` is a context manager used by cross-tenant
  super-admin / billing / system jobs (and by the seed scripts) to see ALL
  companies for the duration of a block. It is re-entrant (nesting safe).
- When no tenant id is set AND bypass is not active, the enforcement layer is
  INACTIVE (fails open) so background workers, login, and system startup are
  never blocked. Isolation only kicks in for authenticated tenant requests.
"""
from contextlib import contextmanager
from contextvars import ContextVar
from typing import Optional

# Current authenticated company id for the in-flight request/operation.
_current_company_id: ContextVar[Optional[int]] = ContextVar(
    "current_company_id", default=None
)

# Depth counter for bypass_tenant_filter(); >0 means "see everything".
_bypass_depth: ContextVar[int] = ContextVar("bypass_tenant_depth", default=0)


def set_current_tenant(company_id: Optional[int]) -> None:
    _current_company_id.set(company_id)


def get_current_tenant() -> Optional[int]:
    return _current_company_id.get()


def clear_current_tenant() -> None:
    _current_company_id.set(None)


def is_tenant_bypass() -> bool:
    return _bypass_depth.get() > 0


@contextmanager
def bypass_tenant_filter():
    """Temporarily disable tenant filtering for the wrapped block."""
    token = _bypass_depth.set(_bypass_depth.get() + 1)
    try:
        yield
    finally:
        _bypass_depth.reset(token)


def is_enforcement_active() -> bool:
    """
    True only when we have a concrete tenant to scope to and no bypass.
    The ORM event hooks consult this before rewriting any statement.
    """
    return (not is_tenant_bypass()) and (_current_company_id.get() is not None)
