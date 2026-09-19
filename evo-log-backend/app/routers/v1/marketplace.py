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
        "status": "success",
        "organization_id": context.organization_id,
        "api_keys": [
            {
                "id": "KEY-001",
                "key_name": "Intégration Odoo / SAP B2B",
                "key_prefix": "evo_live_89a...",
                "created_at": datetime.utcnow().isoformat(),
                "is_active": True
            }
        ]
    }

@router.post("/api-keys", status_code=status.HTTP_201_CREATED)
def create_tenant_api_key(payload: APIKeyCreateSchema, context: TenantContext = Depends(get_current_tenant_context)):
    """Generate a new public API key for the active tenant."""
    raw_key = f"evo_live_{datetime.utcnow().strftime('%Y%m%d%H%M%S')}_sec99"
    return {
        "status": "success",
        "message": "API key generated successfully! Store this secret key securely.",
        "api_key": {
            "id": f"KEY-00{datetime.utcnow().strftime('%S')}",
            "key_name": payload.key_name,
            "secret_key": raw_key,
            "created_at": datetime.utcnow().isoformat()
        }
    }
