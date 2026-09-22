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
def list_freight_offers():
    """Retrieve public/partner carrier freight exchange offers."""
    return {
        "status": "success",
        "offers": [
            {
                "id": "FRT-OFF-001",
                "origin": "Port de Douala Quai 10",
                "destination": "N'Djamena Tchad",
                "cargo_type": "Conteneur 40ft HC",
                "weight_tons": 28.5,
                "offered_price_xaf": 2800000.0,
                "publisher_name": "EVO-LOG Transports SARL",
                "status": "AVAILABLE",
                "created_at": datetime.utcnow().isoformat()
            }
        ]
    }

@router.post("/offers", status_code=status.HTTP_201_CREATED)
def publish_freight_offer(payload: FreightOfferSchema, context: TenantContext = Depends(get_current_tenant_context)):
    return {
        "status": "success",
        "message": "Freight offer published on Freight Exchange platform.",
        "offer": {
            "id": f"FRT-OFF-{datetime.utcnow().strftime('%M%S')}",
            "organization_id": context.organization_id,
            **payload.dict(),
            "status": "AVAILABLE",
            "created_at": datetime.utcnow().isoformat()
        }
    }
