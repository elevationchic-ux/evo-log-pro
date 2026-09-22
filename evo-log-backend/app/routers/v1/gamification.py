from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from pydantic import BaseModel, Field
from typing import List, Optional
from datetime import datetime

from app.database import get_db
from app.utils.tenant import get_current_tenant_context, TenantContext

router = APIRouter()

@router.get("/driver-scores")
def get_driver_gamification_scores(context: TenantContext = Depends(get_current_tenant_context)):
    """Retrieve driver eco-driving, safety scores, and earned badges."""
    return {
        "status": "unavailable",
        "organization_id": context.organization_id,
        "leaderboard": []
    }
