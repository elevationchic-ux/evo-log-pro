from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session
from pydantic import BaseModel, Field
from typing import List, Optional

from app.database import get_db
from app.utils.tenant import get_current_tenant_context, TenantContext
from app.models.advanced_crud import FreightOffer

router = APIRouter()


class FreightOfferSchema(BaseModel):
    origin: str = Field(..., example="Port de Douala Quai 10")
    destination: str = Field(..., example="N'Djamena Tchad")
    cargo_type: str = Field(..., example="Conteneur 40ft HC")
    weight_tons: float = Field(..., example=28.5)
    offered_price_xaf: float = Field(..., example=2800000.0)


class FreightOfferOut(BaseModel):
    id: int
    origin: str
    destination: str
    cargo_type: Optional[str]
    weight_tons: float
    offered_price_xaf: float
    status: str

    class Config:
        from_attributes = True


@router.get("/offers", response_model=List[FreightOfferOut])
def list_freight_offers(
    context: TenantContext = Depends(get_current_tenant_context),
    db: Session = Depends(get_db),
):
    """Offres de fret reellement publiees sur la bourse (table persistante).

    La bourse fret est inter-tenants : un transporteur publie, d'autres consultent.
    On expose donc toutes les offres publiees, sans les inventer.
    """
    return db.query(FreightOffer).filter(FreightOffer.status == "PUBLIEE").order_by(
        FreightOffer.created_at.desc()
    ).all()


@router.post("/offers", response_model=FreightOfferOut, status_code=status.HTTP_201_CREATED)
def publish_freight_offer(
    payload: FreightOfferSchema,
    context: TenantContext = Depends(get_current_tenant_context),
    db: Session = Depends(get_db),
):
    """Publication d'offre : la ligne est reellement enregistree, portee par le tenant."""
    offer = FreightOffer(
        organization_id=context.organization_id,
        published_by=getattr(context.user, "id", None),
        **payload.model_dump(),
    )
    db.add(offer)
    db.commit()
    db.refresh(offer)
    return offer
