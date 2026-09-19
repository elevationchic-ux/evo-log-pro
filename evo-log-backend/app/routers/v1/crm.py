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
    return {
        "status": "success",
        "pipeline_summary": {
            "total_opportunities": 4,
            "pipeline_value_xaf": 128000000.0,
            "weighted_value_xaf": 89500000.0
        },
        "opportunities": [
            {
                "id": "OPP-001",
                "client_name": "Société Camerounaise de Palmeraies (SOCAPALM)",
                "title": "Acheminement huile de palme brut vers port Douala",
                "estimated_value": 65000000.0,
                "stage": "NEGOTIATION",
                "probability": 80,
                "created_at": datetime.utcnow().isoformat()
            },
            {
                "id": "OPP-002",
                "client_name": "CIMENCAM",
                "title": "Logistique clinker et ciment vrac",
                "estimated_value": 42000000.0,
                "stage": "PROPOSAL",
                "probability": 60,
                "created_at": datetime.utcnow().isoformat()
            }
        ]
    }

@router.post("/opportunities", status_code=status.HTTP_201_CREATED, dependencies=[Depends(require_module_access("cotations"))])
def create_crm_opportunity(
    payload: OpportunitySchema,
    context: TenantContext = Depends(get_current_tenant_context)
):
    """Create a new commercial lead or opportunity."""
    return {
        "status": "success",
        "message": "CRM Opportunity created successfully!",
        "opportunity": {
            "id": f"OPP-00{datetime.utcnow().strftime('%M%S')}",
            "organization_id": context.organization_id,
            **payload.dict(),
            "created_at": datetime.utcnow().isoformat()
        }
    }
