"""
Security & Alert Escalation Policies Router for EVO-LOG ERP
Manages notification thresholds, N+1/DG escalation rules, SMS/Email/Push triggers.

Les regles sont desormais REELLEMENT persistees par tenant (table
security_escalation_settings) au lieu d'un dictionnaire en memoire perdu au
redemarrage. GET renvoie la configuration enregistree, ou les valeurs par defaut
documentees si rien n'a encore ete enregistre.
"""
from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session
from typing import Dict, Any

from app.core.database import get_db
from app.utils.tenant import get_current_tenant_context, TenantContext
from app.models.advanced_crud import SecurityEscalationSetting

router = APIRouter()

# Valeurs par defaut DOCUMENTEES (affichees tant qu'aucune regle n'est enregistree).
DEFAULT_ESCALATION_SETTINGS: Dict[str, Any] = {
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
}


def _row(db: Session, organization_id):
    return db.query(SecurityEscalationSetting).filter(
        SecurityEscalationSetting.organization_id == organization_id
    ).first()


@router.get("/escalation-rules")
def get_escalation_rules(
    context: TenantContext = Depends(get_current_tenant_context),
    db: Session = Depends(get_db),
):
    """Regles d'escalade lues en base (defaults documentes si aucune ligne)."""
    row = _row(db, getattr(context, "organization_id", None))
    if row is None:
        return {**DEFAULT_ESCALATION_SETTINGS, "source": "defaults (aucune regle enregistree)"}
    return {**DEFAULT_ESCALATION_SETTINGS, **row.config, "source": "persiste"}


@router.post("/escalation-rules", status_code=status.HTTP_201_CREATED)
def save_escalation_rules(
    payload: Dict[str, Any],
    context: TenantContext = Depends(get_current_tenant_context),
    db: Session = Depends(get_db),
):
    """Persistance REELLE des regles d'escalade par tenant (upsert)."""
    org = getattr(context, "organization_id", None)
    row = _row(db, org)
    if row is None:
        row = SecurityEscalationSetting(organization_id=org, config=payload)
        db.add(row)
    else:
        row.config = payload
    db.commit()
    db.refresh(row)
    return {"id": row.id, "persiste": True, "regles": row.config}
