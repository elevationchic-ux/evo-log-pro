"""
Audit middleware for tracking API requests.

Historiquement, l'ecriture de la ligne d'audit (`db.commit()`) se faisait
directement dans `dispatch`, c'est-a-dire SUR LE FILTRE D'EVENTUALITES (event
loop) de la boucle asynchrone unique d'uvicorn. Sous une rafale de requetes
(concurrentes, ex. chargement d'un module qui declenche nomenclatures + listes),
chaque commit bloquait la boucle : les requetes se serialisaient et depassaient
le timeout axios (15s) du frontend, qui affichait alors « serveur injoignable ».

Corrections :
  1. L'ecriture d'audit est deleguee a un pool de threads borne, en mode
     best-effort non bloque : la reponse est renvoyee immediatement, le commit
     se draine en arriere-plan.
  2. Les requetes purement techniques (OPTIONS preflight CORS, /health, /docs,
     /openapi) ne sont PAS persistees : elles inondaient la table d'audit et
     saturent le verrou euniqueur de SQLite sans valeur de conformite.
"""
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
import asyncio
import time
import logging
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime
from app.core.database import SessionLocal
from app.models.audit import AuditLog

logger = logging.getLogger(__name__)

# Pool borne : au plus 4 ecrivains d'audit concurrently. Evite d'ouvrir un
# thread par requete tout en dechargeant completement la boucle asynchrone.
_audit_executor = ThreadPoolExecutor(max_workers=4, thread_name_prefix="audit")

# Sous-chemins purement techniques : jamais persistes (bruit, pas de conformite).
_SKIP_PREFIXES = ("/health", "/docs", "/openapi", "/redoc", "/api/docs", "/api/openapi")


def _persist_audit(method, url, status_code, client_host, user_agent, process_time):
    """Execute hors de la boucle asynchrone (thread) : best-effort."""
    db = SessionLocal()
    try:
        db.add(AuditLog(
            method=method,
            url=url,
            status_code=status_code,
            client_host=client_host,
            user_agent=user_agent,
            process_time=process_time,
            timestamp=datetime.utcnow(),
        ))
        db.commit()
    except Exception as e:  # jamais remonter : l'audit ne doit pas casser une reponse
        logger.error(f"Failed to store audit log: {e}")
        db.rollback()
    finally:
        db.close()


class AuditMiddleware(BaseHTTPMiddleware):
    """Middleware to audit API requests (non-blocking persistence)."""

    async def dispatch(self, request: Request, call_next):
        start_time = time.time()

        method = request.method
        url = str(request.url)
        path = request.url.path
        client_host = request.client.host if request.client else "unknown"
        user_agent = request.headers.get("user-agent", "unknown")

        # Traiter la requete.
        response = await call_next(request)

        process_time = time.time() - start_time
        logger.info(
            f"{method} {url} - Status: {response.status_code} - "
            f"Time: {process_time:.3f}s - Client: {client_host}"
        )

        # OPTIONS (preflight CORS) et endpoints techniques : pas de persistance.
        skip = (
            method == "OPTIONS"
            or any(path.startswith(p) for p in _SKIP_PREFIXES)
        )
        if not skip:
            # Fire-and-forget hors de la boucle evenementielle : la reponse est
            # deja calculee, on ne bloque plus jamais le loop sur un commit SQLite.
            try:
                loop = asyncio.get_running_loop()
                loop.run_in_executor(
                    _audit_executor,
                    _persist_audit,
                    method, url, response.status_code, client_host, user_agent, process_time,
                )
            except Exception as e:
                logger.error(f"Failed to schedule audit log: {e}")

        return response
