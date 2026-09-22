"""Compatibility IoT router stub."""

from fastapi import APIRouter

router = APIRouter()


@router.get("/health")
def iot_health():
    return {"status": "ok", "service": "iot"}
