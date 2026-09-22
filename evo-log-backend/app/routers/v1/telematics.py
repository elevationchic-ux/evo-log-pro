"""Compatibility telematics router stub."""

from fastapi import APIRouter

router = APIRouter()


@router.get("/health")
def telematics_health():
    return {"status": "ok", "service": "telematics"}
