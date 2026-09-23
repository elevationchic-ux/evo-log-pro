from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from pydantic import BaseModel, Field
from typing import List, Optional
from datetime import datetime

from app.database import get_db
from app.utils.tenant import get_current_tenant_context, TenantContext, require_module_access
from app.core.not_implemented import not_implemented

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
    """Pipeline commercial : 501 (donnees de pipeline inventees, aucune table CRM)."""
    not_implemented(
        "Listage des opportunites CRM",
        "un modele/une table d'opportunites commerciales persistantes (le pipeline "
        "retourne etait fabrique)",
    )

@router.post("/opportunities", status_code=status.HTTP_201_CREATED, dependencies=[Depends(require_module_access("cotations"))])
def create_crm_opportunity(
    payload: OpportunitySchema,
    context: TenantContext = Depends(get_current_tenant_context)
):
    """Creation d'opportunite : 501 (ne persistait rien, faux succes)."""
    not_implemented(
        "Creation d'une opportunite CRM",
        "un modele/une table d'opportunites commerciales pour reellement "
        "enregistrer la ligne (l'ID retourne etait un simple horodatage)",
    )
