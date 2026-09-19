"""
Error handlers and monitoring setup
"""
from fastapi import FastAPI, Request, HTTPException
from fastapi.responses import JSONResponse
import logging
# prometheus_fastapi_instrumentator disabled - see main.py

logger = logging.getLogger(__name__)


def setup_error_handlers(app: FastAPI):
    """Setup custom error handlers"""
    
    @app.exception_handler(HTTPException)
    async def http_exception_handler(request: Request, exc: HTTPException):
        """Handle HTTP exceptions with consistent format"""
        return JSONResponse(
            status_code=exc.status_code,
            content={
                "error": True,
                "message": exc.detail,
                "status_code": exc.status_code,
                "path": str(request.url.path),
                "method": request.method
            }
        )
    
    @app.exception_handler(Exception)
    async def general_exception_handler(request: Request, exc: Exception):
        """Handle general exceptions"""
        logger.error(f"Unhandled exception: {exc}", exc_info=True)
        return JSONResponse(
            status_code=500,
            content={
                "error": True,
                "message": "Internal server error",
                "status_code": 500,
                "path": str(request.url.path),
                "method": request.method
            }
        )


def setup_monitoring(app: FastAPI):
    """Setup Prometheus monitoring - safely disabled to prevent _IncludedRouter crash in FastAPI 0.115+"""
    pass