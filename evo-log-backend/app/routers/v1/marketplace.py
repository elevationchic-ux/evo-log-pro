from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from pydantic import BaseModel, Field
from typing import List, Optional
from datetime import datetime

from app.database import get_db
from app.utils.tenant import get_current_tenant_context, TenantContext
from app.core.not_implemented import not_implemented

router = APIRouter()

class APIKeyCreateSchema(BaseModel):
    key_name: str = Field(..., example="Intégration Odoo / SAP B2B")
    allowed_ips: Optional[List[str]] = Field(None, example=["197.239.12.4"])

@router.get("/api-keys")
def list_tenant_api_keys(context: TenantContext = Depends(get_current_tenant_context)):
    """Cles API : 501 (cle inventee, aucune table de cles d'integration)."""
    not_implemented(
        "Listage des cles API du tenant",
        "une table persistante des cles d'api (hash + prefixe + etat) pour les "
        "integrations tierces (la cle retournee etait fabrique)",
    )

@router.post("/api-keys", status_code=status.HTTP_201_CREATED)
def create_tenant_api_key(payload: APIKeyCreateSchema, context: TenantContext = Depends(get_current_tenant_context)):
    """Generation de cle API : 501 (ne generait/persistait rien de verifiable)."""
    not_implemented(
        "Generation d'une cle API tenant",
        "une generation cryptographique reelle + persistance du hash de la cle "
        "et verification a l'usage (la cle retournee etait une chaine fabrique)",
    )
