from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session
from pydantic import BaseModel, Field
from typing import List, Optional

from app.database import get_db
from app.utils.tenant import get_current_tenant_context, TenantContext, require_module_access
from app.models.advanced_crud import CRMOpportunity

router = APIRouter()


class OpportunitySchema(BaseModel):
    client_name: str = Field(..., example="Brasseries du Cameroun")
    title: str = Field(..., example="Contrat annuel transport vrac et palettes")
    estimated_value: float = Field(..., example=45000000.0)
    stage: str = Field("PROSPECT", example="NEGOTIATION")  # PROSPECT, QUALIFIED, PROPOSAL, NEGOTIATION, WON, LOST
    probability: int = Field(70, example=70)
    contact_person: str = Field(..., example="M. Alain Mbarga")
    contact_email: Optional[str] = Field(None, example="a.mbarga@boissons.cm")
    notes: Optional[str] = None


class OpportunityOut(BaseModel):
    id: int
    client_name: str
    title: str
    estimated_value: float
    currency: str
    stage: str
    probability: int
    contact_person: Optional[str]
    contact_email: Optional[str]
    notes: Optional[str]

    class Config:
        from_attributes = True


def _scope(context: TenantContext, query):
    """Filtre par tenant ; un superadmin sans entete organisation voit tout le pipeline."""
    if context.organization_id is not None:
        return query.filter(CRMOpportunity.organization_id == context.organization_id)
    return query


@router.get("/opportunities", response_model=List[OpportunityOut],
            dependencies=[Depends(require_module_access("cotations"))])
def list_crm_opportunities(
    context: TenantContext = Depends(get_current_tenant_context),
    db: Session = Depends(get_db),
):
    """Pipeline commercial reellement persiste, porte par le tenant."""
    rows = _scope(context, db.query(CRMOpportunity)).order_by(CRMOpportunity.created_at.desc()).all()
    return rows


@router.post("/opportunities", response_model=OpportunityOut, status_code=status.HTTP_201_CREATED,
             dependencies=[Depends(require_module_access("cotations"))])
def create_crm_opportunity(
    payload: OpportunitySchema,
    context: TenantContext = Depends(get_current_tenant_context),
    db: Session = Depends(get_db),
):
    """Creation d'opportunite : la ligne est reellement enregistree en base."""
    opp = CRMOpportunity(
        organization_id=context.organization_id,
        created_by=getattr(context.user, "id", None),
        **payload.model_dump(),
    )
    db.add(opp)
    db.commit()
    db.refresh(opp)
    return opp
