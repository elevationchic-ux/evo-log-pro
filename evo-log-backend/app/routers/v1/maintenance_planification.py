"""Planification preventive GMAO : evaluation des plans et génération d'OT."""
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.permissions import require_perm
from app.models.user import User
from app.services.maintenance_planification_service import MaintenancePlanificationService


router = APIRouter(tags=["Maintenance — Planification préventive"])


class EvaluationRequest(BaseModel):
    company_id: Optional[int] = None


@router.post("/evaluer")
def evaluer_planification(
    request: Optional[EvaluationRequest] = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_perm("maintindustrielle.work_orders.create")),
):
    """Évalue les plans de maintenance et calendriers de lubrification,
    puis génère les ordres de travail preventifs déclenchés.

    Idempotent par jour : une seconde exécution le même jour ne duplique
    aucun OT."""
    try:
        return MaintenancePlanificationService.evaluer(
            db,
            company_id=(request.company_id if request else None),
        )
    except Exception as exc:
        raise HTTPException(status_code=500, detail=str(exc))
