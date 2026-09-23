"""
Security & Alert Escalation Policies Router for EVO-LOG ERP
Manages notification thresholds, N+1/DG escalation rules, SMS/Email/Push triggers.
"""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import Dict, Any, Optional
from datetime import datetime

from app.core.database import get_db
from app.core.not_implemented import not_implemented

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
    """Persistance des regles d'escalade : 501 (modifiait seulement la memoire)."""
    not_implemented(
        "Enregistrement des regles d'escalade et d'alerte",
        "une table de configuration par tenant pour persister ces regles "
        "(les valeurs modifiees etaient perdues au redemarrage)",
    )
