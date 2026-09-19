from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from app.utils.logger import logger

def setup_error_handlers(app: FastAPI) -> None:
    """Configure les gestionnaires d'exceptions globaux."""
    @app.exception_handler(Exception)
    async def global_exception_handler(request: Request, exc: Exception):
        logger.error(f"Global exception caught: {exc}", exc_info=True)
        return JSONResponse(
            status_code=500,
            content={"detail": "Une erreur interne du serveur s'est produite.", "error": str(exc)},
        )
