from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from pydantic import BaseModel, Field
from typing import List, Optional
from datetime import datetime

from app.database import get_db
from app.utils.tenant import get_current_tenant_context, TenantContext

router = APIRouter()

class APIKeyCreateSchema(BaseModel):
    key_name: str = Field(..., example="Intégration Odoo / SAP B2B")
    allowed_ips: Optional[List[str]] = Field(None, example=["197.239.12.4"])

@router.get("/api-keys")
def list_tenant_api_keys(context: TenantContext = Depends(get_current_tenant_context)):
    """Retrieve API Keys for 3rd party integrations and marketplace apps."""
    return {
        "status": "unavailable",
        "organization_id": context.organization_id,
        "api_keys": []
    }

@router.post("/api-keys", status_code=status.HTTP_501_NOT_IMPLEMENTED)
def create_tenant_api_key(payload: APIKeyCreateSchema, context: TenantContext = Depends(get_current_tenant_context)):
    """Generate a new public API key for the active tenant."""
    raise HTTPException(
        status_code=501,
        detail="La génération de clés API n'est pas encore configurée pour ce tenant."
    )
