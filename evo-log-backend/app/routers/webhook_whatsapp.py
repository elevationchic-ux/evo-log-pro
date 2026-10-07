from fastapi import APIRouter, Request, Response, HTTPException, status, Query
from pydantic import BaseModel, Field
from typing import Optional, Dict, Any, List
import os
import logging
from datetime import datetime

# Pas de prefix interne : les routes portent leur chemin complet pour eviter
# tout double prefix au include (main.py monte ce router sans prefix).
router = APIRouter(tags=["WhatsApp Business"])
logger = logging.getLogger(__name__)

WHATSAPP_VERIFY_TOKEN = os.getenv("WHATSAPP_VERIFY_TOKEN", "evo-log-whatsapp-verify-token-2026")
WHATSAPP_CLOUD_API_TOKEN = os.getenv("WHATSAPP_CLOUD_API_TOKEN", "")
WHATSAPP_PHONE_NUMBER_ID = os.getenv("WHATSAPP_PHONE_NUMBER_ID", "")

class SendWhatsAppMessageSchema(BaseModel):
    to_number: str = Field(..., example="+237699001122")
    template_name: str = Field("mission_assigned", example="mission_assigned")
    parameters: List[str] = Field(..., example=["OT-2026-089", "Douala Port", "Yaoundé Depot"])

# Journal ChatOps en mémoire (ring buffer) : alimente la page /transport/chatops.
# Volontairement sans persistance : les échanges réels vivent dans WhatsApp/Meta,
# ce buffer ne garde que les traces courtes pour le moniteur du bot.
_CHATOPS_LOGS: List[Dict[str, Any]] = []
_CHATOPS_MAX = 100
_LOG_SEQ = {"n": 0}


def _chatops_append(entry: Dict[str, Any]) -> None:
    _LOG_SEQ["n"] += 1
    _CHATOPS_LOGS.append({"id": _LOG_SEQ["n"], **entry})
    if len(_CHATOPS_LOGS) > _CHATOPS_MAX:
        del _CHATOPS_LOGS[: len(_CHATOPS_LOGS) - _CHATOPS_MAX]


@router.get("/api/v1/webhooks/chatops/logs")
def get_chatops_logs(limit: int = Query(50, ge=1, le=100)):
    """Journal des échanges WhatsApp entrants/sortants vus par le bot K-Bot."""
    return {"logs": _CHATOPS_LOGS[-limit:], "total": len(_CHATOPS_LOGS)}

# Meta verifie le webhook en GET sur l'URL exacte /api/v1/webhooks/whatsapp
# (appelee par la page ChatOps du frontend).
@router.get("/api/v1/webhooks/whatsapp")
def verify_whatsapp_webhook(
    hub_mode: Optional[str] = Query(None, alias="hub.mode"),
    hub_challenge: Optional[str] = Query(None, alias="hub.challenge"),
    hub_verify_token: Optional[str] = Query(None, alias="hub.verify_token")
):
    """
    Verification endpoint for Meta WhatsApp Business Cloud API.
    """
    if hub_mode == "subscribe" and hub_verify_token == WHATSAPP_VERIFY_TOKEN:
        logger.info("WhatsApp Webhook verified successfully!")
        return Response(content=hub_challenge, media_type="text/plain")
    
    raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Verification token mismatch")

@router.post("/api/v1/webhooks/whatsapp")
async def receive_whatsapp_notification(request: Request):
    """
    Receive incoming messages and status callbacks from WhatsApp Business Cloud API.
    Handles driver responses (e.g. "CONFIRM OT-2026-089" or POD uploads via WhatsApp).
    """
    payload = await request.json()
    logger.info(f"Incoming WhatsApp notification: {payload}")

    # Trace pour le moniteur ChatOps du frontend (page transport/chatops)
    if "message" in payload or "sender" in payload:
        _chatops_append({
            "sender": payload.get("sender", "inconnu"),
            "text": payload.get("message", ""),
            "timestamp": datetime.utcnow().isoformat(),
            "is_bot": False,
        })

    entries = payload.get("entry", [])
    processed_messages = []

    for entry in entries:
        changes = entry.get("changes", [])
        for change in changes:
            value = change.get("value", {})
            messages = value.get("messages", [])
            for msg in messages:
                from_num = msg.get("from")
                msg_type = msg.get("type")
                
                if msg_type == "text":
                    body = msg.get("text", {}).get("body", "")
                    processed_messages.append({
                        "from": from_num,
                        "text": body,
                        "received_at": datetime.utcnow().isoformat()
                    })
                    _chatops_append({
                        "sender": from_num or "inconnu",
                        "text": body,
                        "timestamp": datetime.utcnow().isoformat(),
                        "is_bot": False,
                    })

    return {
        "status": "processed",
        "messages_count": len(processed_messages),
        "messages": processed_messages
    }

@router.post("/api/v1/whatsapp/send")
def send_whatsapp_template_message(payload: SendWhatsAppMessageSchema):
    """
    Send outbound WhatsApp Business notification (Transport orders, delivery updates, alert notifications).
    Requires WHATSAPP_CLOUD_API_TOKEN + WHATSAPP_PHONE_NUMBER_ID env vars.
    """
    if not WHATSAPP_CLOUD_API_TOKEN or not WHATSAPP_PHONE_NUMBER_ID:
        raise HTTPException(
            status_code=503,
            detail=(
                "WhatsApp Business Cloud API non configuree : definir les variables "
                "d'environnement WHATSAPP_CLOUD_API_TOKEN et WHATSAPP_PHONE_NUMBER_ID "
                "pour activer l'envoi reel de notifications. Aucun message n'a ete emis."
            ),
        )

    # Real dispatch via Meta Graph API (executed only when credentials present)
    import httpx

    url = f"https://graph.facebook.com/v21.0/{WHATSAPP_PHONE_NUMBER_ID}/messages"
    headers = {
        "Authorization": f"Bearer {WHATSAPP_CLOUD_API_TOKEN}",
        "Content-Type": "application/json",
    }
    body = {
        "messaging_product": "whatsapp",
        "to": payload.to_number,
        "type": "template",
        "template": {
            "name": payload.template_name,
            "language": {"code": "fr"},
            "components": [{
                "type": "body",
                "parameters": [{"type": "text", "text": p} for p in payload.parameters],
            }],
        },
    }
    try:
        resp = httpx.post(url, json=body, headers=headers, timeout=15)
        resp.raise_for_status()
        meta_data = resp.json()
    except Exception as exc:
        logger.error(f"WhatsApp dispatch failed: {exc}")
        raise HTTPException(status_code=502, detail=f"Meta API erreur: {exc}")

    messages = meta_data.get("messages", [])
    return {
        "status": "sent",
        "to": payload.to_number,
        "template": payload.template_name,
        "message_id": messages[0]["id"] if messages else None,
        "meta_response": meta_data,
    }
