"""
Security & Alert Escalation Policies Router for EVO-LOG ERP
Manages notification thresholds, N+1/DG escalation rules, SMS/Email/Push triggers.
"""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import Dict, Any, Optional
from datetime import datetime

from app.core.database import get_db

router = APIRouter()

# In-memory settings state with fallback defaults (can be persisted to Company/Tenant configuration)
_CURRENT_ESCALATION_SETTINGS = {
    "emailAlerts": True,
    "smsAlerts": True,
    "inAppPush": True,
    "escalateToN1AfterMinutes": 30,
    "escalateToDgAfterMinutes": 120,
    "notifyOnBruteForce": True,
    "notifyOnGeofenceBreach": True,
    "notifyOnOverdueCredit": True,
    "notifyOnCustomsDelay": True,
    "destinataireAstreinte": "direction-securite@evo-log.cm",
    "last_updated": "2026-08-27T10:00:00"
}


@router.get("/escalation-rules")
def get_escalation_rules():
    """Retrieve active alert escalation and notification policies"""
    return _CURRENT_ESCALATION_SETTINGS


@router.post("/escalation-rules")
def save_escalation_rules(payload: Dict[str, Any]):
    """Update and persist alert escalation policies"""
    global _CURRENT_ESCALATION_SETTINGS
    _CURRENT_ESCALATION_SETTINGS.update(payload)
    _CURRENT_ESCALATION_SETTINGS["last_updated"] = datetime.utcnow().isoformat()

    return {
        "success": True,
        "message": "Politique d'escalade et règles d'alerte enregistrées avec succès.",
        "settings": _CURRENT_ESCALATION_SETTINGS
    }
