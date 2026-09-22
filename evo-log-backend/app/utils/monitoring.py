from fastapi import FastAPI
from prometheus_fastapi_instrumentator import Instrumentator
from app.utils.logger import logger

def setup_monitoring(app: FastAPI) -> None:
    """Initialise le suivi des métriques Prometheus pour FastAPI."""
    try:
        Instrumentator().instrument(app).expose(app, endpoint="/metrics", include_in_schema=False)
        logger.info("Prometheus monitoring initialized successfully.")
    except Exception as exc:
        logger.warning(f"Could not initialize Prometheus monitoring: {exc}")
