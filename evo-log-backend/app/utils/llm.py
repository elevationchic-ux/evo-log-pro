"""Connecteur LLM reel (Anthropic / OpenAI) pilote par la configuration.

Aucune reponse n'est simulee : si aucun fournisseur n'est configure, llm_available()
renvoie False et l'appelant doit renvoyer un 503 explicite. Quand il est configure,
ask_llm() effectue un VERITABLE appel HTTP vers l'API du fournisseur et retourne sa
reponse brute.
"""
from typing import Optional

import httpx

from app.core.config import settings


def llm_available() -> bool:
    return bool(
        settings.AI_ENABLED
        and settings.AI_API_KEY
        and (settings.AI_PROVIDER or "").lower() in {"anthropic", "openai"}
    )


def ask_llm(prompt: str, system: Optional[str] = None, timeout: float = 30.0) -> str:
    """Appel reel au fournisseur LLM configure. Leve RuntimeError si indisponible,
    HTTPError si l'appel echoue (jamais de repli fabrique)."""
    if not llm_available():
        raise RuntimeError("Aucun fournisseur LLM configure")
    provider = settings.AI_PROVIDER.lower()
    sys_text = system or "Tu es l'assistant de l'ERP logistique KAMLOG."

    if provider == "anthropic":
        resp = httpx.post(
            "https://api.anthropic.com/v1/messages",
            headers={
                "x-api-key": settings.AI_API_KEY,
                "anthropic-version": "2023-06-01",
                "content-type": "application/json",
            },
            json={
                "model": settings.AI_MODEL or "claude-3-5-sonnet-latest",
                "max_tokens": 1024,
                "system": sys_text,
                "messages": [{"role": "user", "content": prompt}],
            },
            timeout=timeout,
        )
        resp.raise_for_status()
        data = resp.json()
        return "".join(b.get("text", "") for b in data.get("content", []))

    # openai
    resp = httpx.post(
        "https://api.openai.com/v1/chat/completions",
        headers={
            "Authorization": f"Bearer {settings.AI_API_KEY}",
            "content-type": "application/json",
        },
        json={
            "model": settings.AI_MODEL or "gpt-4o-mini",
            "messages": [
                {"role": "system", "content": sys_text},
                {"role": "user", "content": prompt},
            ],
        },
        timeout=timeout,
    )
    resp.raise_for_status()
    data = resp.json()
    return data["choices"][0]["message"]["content"]
