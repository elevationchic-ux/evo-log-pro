from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from pydantic import BaseModel, Field
from typing import List, Optional
from datetime import datetime

from app.database import get_db
from app.utils.tenant import get_current_tenant_context, TenantContext

router = APIRouter()

class FreightOfferSchema(BaseModel):
    origin: str = Field(..., example="Port de Douala Quai 10")
    destination: str = Field(..., example="N'Djamena Tchad")
    cargo_type: str = Field(..., example="Conteneur 40ft HC")
    weight_tons: float = Field(..., example=28.5)
    offered_price_xaf: float = Field(..., example=2800000.0)

@router.get("/offers")
def list_freight_offers(context: TenantContext = Depends(get_current_tenant_context)):
    """Retrieve public/partner carrier freight exchange offers."""
    return {"status": "unavailable", "offers": []}

@router.post("/offers", status_code=status.HTTP_201_CREATED)
def publish_freight_offer(payload: FreightOfferSchema, context: TenantContext = Depends(get_current_tenant_context)):
    raise HTTPException(status_code=501, detail="La persistance Freight Exchange n'est pas encore implémentée.")
