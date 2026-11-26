"""Compatibility WhatsApp webhook router stub."""

from fastapi import APIRouter

router = APIRouter()


@router.get("/health")
def whatsapp_health():
    return {"status": "ok", "service": "webhook_whatsapp"}
