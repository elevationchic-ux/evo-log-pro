from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from pydantic import BaseModel, Field
from typing import List, Optional
from datetime import datetime

from app.database import get_db
from app.utils.tenant import get_current_tenant_context, TenantContext
from app.core.not_implemented import not_implemented

router = APIRouter()

class FreightOfferSchema(BaseModel):
    origin: str = Field(..., example="Port de Douala Quai 10")
    destination: str = Field(..., example="N'Djamena Tchad")
    cargo_type: str = Field(..., example="Conteneur 40ft HC")
    weight_tons: float = Field(..., example=28.5)
    offered_price_xaf: float = Field(..., example=2800000.0)

@router.get("/offers")
def list_freight_offers():
    """Offres de fret : 501 (offre inventee, aucune table d'change de fret)."""
    not_implemented(
        "Listage des offres de fret (bourse fret)",
        "une table persistante des offres publiees par les transporteurs "
        "(l'offre retournee etait fabrique)",
    )

@router.post("/offers", status_code=status.HTTP_201_CREATED)
def publish_freight_offer(payload: FreightOfferSchema, context: TenantContext = Depends(get_current_tenant_context)):
    """Publication d'offre : 501 (ne persistait rien, faux succes)."""
    not_implemented(
        "Publication d'une offre de fret",
        "une table d'offres de fret pour reellement publier la ligne "
        "(l'ID retourne etait un simple horodatage)",
    )
