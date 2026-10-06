"""Connecteurs externes pilotes par la configuration (Zero-Mock).

Regle d'honnetete :
- Aucun fournisseur configure  -> HTTP 503 explicite (jamais un faux 200, jamais
  de donnee inventee).
- Fournisseur configure        -> VERITABLE appel HTTP vers la gateway declaree
  (URL + cle secrete en variables d'environnement). Erreur reseau/API -> 502.

Un fournisseur est consideré configure si <PREFIX>_ENABLED est vrai ET
<PREFIX>_API_URL et <PREFIX>_API_KEY sont non vides.
"""
from typing import Any, Dict, Optional

import httpx
from fastapi import HTTPException, status

from app.core.config import settings


def provider_configured(prefix: str) -> bool:
    enabled = getattr(settings, f"{prefix}_ENABLED", False)
    url = getattr(settings, f"{prefix}_API_URL", "") or ""
    key = getattr(settings, f"{prefix}_API_KEY", "") or ""
    return bool(enabled and url and key)


def _detail(prefix: str, fonction: str) -> str:
    return (
        f"{fonction} : connecteur externe '{prefix}' non configure "
        f"({prefix}_ENABLED / {prefix}_API_URL / {prefix}_API_KEY). "
        "Aucun appel n'a eu lieu et aucun resultat n'est invente. "
        "Renseignez la gateway du fournisseur pour activer cette fonction."
    )


def call_provider(
    prefix: str,
    fonction: str,
    *,
    path: str = "",
    method: str = "POST",
    payload: Optional[Dict[str, Any]] = None,
    timeout: float = 25.0,
    extra_headers: Optional[Dict[str, str]] = None,
) -> Dict[str, Any]:
    """Appel reel a la gateway du fournisseur. 503 si non configure, 502 si
    l'appel echoue. Retourne la reponse JSON reelle du fournisseur."""
    if not provider_configured(prefix):
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=_detail(prefix, fonction),
        )
    base = getattr(settings, f"{prefix}_API_URL", "").rstrip("/")
    key = getattr(settings, f"{prefix}_API_KEY", "")
    endpoint = base + (path or "")
    headers = {"Authorization": f"Bearer {key}", "content-type": "application/json"}
    if extra_headers:
        headers.update(extra_headers)
    try:
        resp = httpx.request(
            method.upper(), endpoint, headers=headers, json=payload, timeout=timeout
        )
        resp.raise_for_status()
    except httpx.HTTPStatusError as exc:
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail=(
                f"{fonction} : le fournisseur '{prefix}' a repondu "
                f"{exc.response.status_code}. Aucun succes simule."
            ),
        )
    except httpx.HTTPError as exc:
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail=f"{fonction} : echec d'appel au fournisseur '{prefix}' ({exc}).",
        )
    try:
        return {"provider": prefix, "response": resp.json(), "status_code": resp.status_code}
    except ValueError:
        return {"provider": prefix, "response": resp.text, "status_code": resp.status_code}
