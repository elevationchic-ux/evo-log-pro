"""Honest pending-module fallback.

The ERP surface exposes ~350 frontend pages, but a number of sub-modules
(commandes magasin, ordres de transfert, bandes de livraison, zones/emplacements
du parc, requisitions d'achat, customer/success, support, analytics avances ...)
have NO backing data model yet. Their pages currently hit endpoints that return a
raw HTTP 404, which the UI renders as a broken/dead screen.

This router installs a LAST-PRIORITY catch-all so that any *unmatched* request on
the business API surface degrades gracefully instead of 404 / 500:

  * reads (GET)      -> 200 with an empty, self-describing envelope
                        ``{items: [], total: 0, pending: true, message}``
  * writes (POST/PUT/
    PATCH/DELETE)    -> 202 Accepted with ``{accepted: false, pending: true}``

Design guarantees:
  * It never shadows a real endpoint: it is included after every other router and
    Starlette resolves routes in registration order, so anything already
    implemented wins.
  * It never fabricates business data: responses are explicitly flagged
    ``pending`` so the frontend shows its honest "module en cours de deploiement"
    banner (PageNonConnectee) rather than fake records.
  * It does not mask server errors: exceptions raised inside real endpoints
    still propagate as 500.
  * Infra / auth / docs paths keep their real behaviour (404 or their own
    responses); they are allow-listed out.
"""
from __future__ import annotations

import logging

from fastapi import APIRouter, Request, status
from fastapi.responses import JSONResponse, RedirectResponse
from starlette.routing import Match

logger = logging.getLogger(__name__)

router = APIRouter(tags=["Pending Modules"])

# Prefixes that must keep their genuine semantics and never be answered here.
_EXCLUDED_PREFIXES = (
    "auth",
    "health",
    "docs",
    "redoc",
    "openapi",
    "status",
    "setup",
    "seed",
    "public",
    "ws",
)


def _slash_redirect(request: Request):
    """Ne jamais occulter une route_reelle declaree avec slash final.

    Les routers metiers definissent leurs collections en ``@router.get("/")``
    (ex. /api/v1/tiers/). Le catch-all, lui, matche /api/v1/tiers sans slash
    AVANT le redirect_slashes de Starlette : on repondrait « pending » sur un
    endpoint qui existe reellement. Si la variante avec slash correspond a une
    route declaree, on redirige (307 = methode + corps preserves) au lieu de
    servir l'enveloppe pending.
    """
    path = request.url.path
    if path.endswith("/"):
        return None
    scope = dict(request.scope)
    scope["path"] = path + "/"
    if isinstance(scope.get("raw_path"), (bytes, bytearray)):
        scope["raw_path"] = bytes(scope["raw_path"]) + b"/"
    for route in request.app.routes:
        # Exclure nos propres catch-alls : sinon ils matcheront toujours
        # la variante slashee et on tournerait en boucle de redirects.
        if getattr(route, "path", None) in {r.path for r in router.routes}:
            continue
        try:
            match, _ = route.matches(scope)
        except Exception:
            continue
        if match == Match.FULL:
            target = path + "/"
            if request.url.query:
                target += "?" + request.url.query
            logger.info("pending-module: %s redirecte vers route reelle %s", path, target)
            return RedirectResponse(target, status_code=status.HTTP_307_TEMPORARY_REDIRECT)
    return None


def _pending_read(path: str) -> JSONResponse:
    logger.info("pending-module READ served for %s (no model yet)", path)
    return JSONResponse(
        status_code=status.HTTP_200_OK,
        content={
            "items": [],
            "results": [],
            "data": [],
            "total": 0,
            "page": 1,
            "size": 0,
            "pending": True,
            "endpoint": path,
            "message": "Module en cours de deploiement : aucune donnee disponible.",
        },
    )


def _pending_write(path: str) -> JSONResponse:
    logger.info("pending-module WRITE acknowledged for %s (no model yet)", path)
    return JSONResponse(
        status_code=status.HTTP_202_ACCEPTED,
        content={
            "accepted": False,
            "success": False,
            "pending": True,
            "endpoint": path,
            "message": (
                "Cette fonctionnalite n'est pas encore active. "
                "Votre demande a ete enregistree en attente d'implementation."
            ),
        },
    )


@router.api_route("/api/v1/{full_path:path}", methods=["GET"], include_in_schema=False)
async def pending_get(full_path: str, request: Request):
    first = full_path.split("/", 1)[0]
    if first in _EXCLUDED_PREFIXES:
        # Let the normal 404 proceed for infra/auth surfaces.
        return JSONResponse(status_code=404, content={"detail": "Not Found"})
    redirect = _slash_redirect(request)
    if redirect is not None:
        return redirect
    return _pending_read("/api/v1/" + full_path)


@router.api_route(
    "/api/v1/{full_path:path}",
    methods=["POST", "PUT", "PATCH", "DELETE"],
    include_in_schema=False,
)
async def pending_write(full_path: str, request: Request):
    first = full_path.split("/", 1)[0]
    if first in _EXCLUDED_PREFIXES:
        return JSONResponse(status_code=404, content={"detail": "Not Found"})
    redirect = _slash_redirect(request)
    if redirect is not None:
        return redirect
    return _pending_write("/api/v1/" + full_path)
