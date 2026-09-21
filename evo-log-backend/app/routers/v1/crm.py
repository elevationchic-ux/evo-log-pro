from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from pydantic import BaseModel, Field
from typing import List, Optional
from datetime import datetime

from app.database import get_db
from app.utils.tenant import get_current_tenant_context, TenantContext, require_module_access

router = APIRouter()

class OpportunitySchema(BaseModel):
    client_name: str = Field(..., example="Brasseries du Cameroun")
    title: str = Field(..., example="Contrat annuel transport vrac et palettes")
    estimated_value: float = Field(..., example=45000000.0)
    stage: str = Field("PROSPECT", example="NEGOTIATION") # PROSPECT, QUALIFIED, PROPOSAL, NEGOTIATION, WON, LOST
    probability: int = Field(70, example=70)
    contact_person: str = Field(..., example="M. Alain Mbarga")
    contact_email: Optional[str] = Field(None, example="a.mbarga@boissons.cm")

@router.get("/opportunities", dependencies=[Depends(require_module_access("cotations"))])
def list_crm_opportunities(
    context: TenantContext = Depends(get_current_tenant_context)
):
    """Retrieve commercial pipeline and opportunities."""
    return {"status": "unavailable", "pipeline_summary": None, "opportunities": []}

@router.post("/opportunities", status_code=status.HTTP_201_CREATED, dependencies=[Depends(require_module_access("cotations"))])
def create_crm_opportunity(
    payload: OpportunitySchema,
    context: TenantContext = Depends(get_current_tenant_context)
):
    """Create a new commercial lead or opportunity."""
    raise HTTPException(status_code=501, detail="La persistance CRM n'est pas encore implémentée.")
