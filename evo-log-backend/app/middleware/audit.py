"""
Audit middleware for tracking API requests
"""
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
import time
import logging
from datetime import datetime
from app.core.database import SessionLocal
from app.models.audit import AuditLog

logger = logging.getLogger(__name__)


class AuditMiddleware(BaseHTTPMiddleware):
    """Middleware to audit all API requests"""
    
    async def dispatch(self, request: Request, call_next):
        start_time = time.time()
        
        # Extract request info
        method = request.method
        url = str(request.url)
        client_host = request.client.host if request.client else "unknown"
        user_agent = request.headers.get("user-agent", "unknown")
        
        # Process request
        response = await call_next(request)
        
        # Calculate duration
        process_time = time.time() - start_time
        
        # Log request
        logger.info(
            f"{method} {url} - Status: {response.status_code} - "
            f"Time: {process_time:.3f}s - Client: {client_host}"
        )
        
        # Store audit log in database (async)
        try:
            db = SessionLocal()
            try:
                audit_log = AuditLog(
                    method=method,
                    url=url,
                    status_code=response.status_code,
                    client_host=client_host,
                    user_agent=user_agent,
                    process_time=process_time,
                    timestamp=datetime.utcnow()
                )
                db.add(audit_log)
                db.commit()
            except Exception as e:
                logger.error(f"Failed to store audit log: {e}")
                db.rollback()
            finally:
                db.close()
        except Exception as e:
            logger.error(f"Database connection failed for audit log: {e}")
        
        return response