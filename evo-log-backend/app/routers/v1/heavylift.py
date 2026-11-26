"""API metier heavylift : validation des plans de levage."""
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.security import get_current_user
from app.core.permissions import require_perm
from app.models.user import User
from app.services.heavylift_service import HeavyLiftPlanService

router = APIRouter()


@router.post("/lift-plans/{plan_id}/valider")
def valider_plan(
    plan_id: int,
    db: Session = Depends(get_db),
    user: User = Depends(require_perm("heavylift.lift_plans.modify")),
):
    return HeavyLiftPlanService.valider_plan(db, plan_id)
