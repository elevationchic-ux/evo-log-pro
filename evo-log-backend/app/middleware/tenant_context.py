"""
Pure-ASGI tenant-context middleware.

Registered in app.main. Resolves the authenticated company from the JWT and
publishes it via contextvars so the ORM enforcement layer
(app.core.tenant_enforcement) can scope every query for the request.

Why pure ASGI and not BaseHTTPMiddleware:
    Starlette's BaseHTTPMiddleware runs the downstream app in a separate task,
    so contextvars set inside dispatch() are NOT visible to the request
    handlers / SQLAlchemy events. A pure ASGI middleware awaits the inner app
    inline, in the SAME context, which makes the propagation reliable.

Behaviour
---------
* No Authorization header        -> enforcement off (public/worker/login).
* Superuser / role_level 0       -> enforcement off (sees all companies).
* Tenant user with company_id    -> enforcement scoped to that company.
* Tenant user without company_id -> enforcement off (legacy/unprovisioned).
"""
import logging

from starlette.requests import Request

from app.core.security import decode_token
from app.core.tenant_context import (
    clear_current_tenant,
    set_current_tenant,
)

logger = logging.getLogger(__name__)


class TenantContextMiddleware:
    def __init__(self, app):
        self.app = app

    async def __call__(self, scope, receive, send):
        if scope.get("type") != "http":
            await self.app(scope, receive, send)
            return

        company_id = None
        try:
            request = Request(scope)
            authorization = request.headers.get("authorization", "")
            if authorization.lower().startswith("bearer "):
                token = authorization[7:].strip()
                payload = decode_token(token)
                subject = payload.get("sub") if payload else None
                if subject is not None and str(subject).isdigit():
                    company_id = self._resolve_company(int(subject))
        except Exception as exc:  # never block a request on tenant resolution
            logger.debug("Tenant resolution skipped: %s", exc)
            company_id = None

        set_current_tenant(company_id)
        try:
            await self.app(scope, receive, send)
        finally:
            clear_current_tenant()

    @staticmethod
    def _resolve_company(user_id: int):
        """Return the company_id to scope to, or None for no scoping."""
        from app.core.database import SessionLocal
        from app.models.user import User

        db = SessionLocal()
        try:
            user = (
                db.query(User)
                .filter(User.id == user_id, User.is_active.is_(True))
                .first()
            )
            if user is None:
                return None
            # Super admins / platform operators bypass tenant scoping.
            if getattr(user, "is_superuser", False) or getattr(user, "role_level", 9) == 0:
                return None
            return getattr(user, "company_id", None)
        finally:
            db.close()
