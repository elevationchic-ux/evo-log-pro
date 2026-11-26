"""Compatibility collaboration router stub."""

from fastapi import APIRouter

router = APIRouter()


@router.get("/health")
def collaboration_health():
    return {"status": "ok", "service": "collaboration"}
