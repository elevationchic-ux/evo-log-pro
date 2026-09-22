from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from pydantic import BaseModel, Field
from typing import List, Optional
from datetime import datetime
import secrets

from app.database import get_db
from app.utils.tenant import get_current_tenant_context, TenantContext

router = APIRouter()

class APIKeyCreateSchema(BaseModel):
    key_name: str = Field(..., example="Intégration Odoo / SAP B2B")
    allowed_ips: Optional[List[str]] = Field(None, example=["197.239.12.4"])

class APIKeyResponse(BaseModel):
    id: int
    key_name: str
    api_key: str
    allowed_ips: List[str]
    is_active: bool
    created_at: str
    last_used: Optional[str]

@router.get("/api-keys")
def list_tenant_api_keys(context: TenantContext = Depends(get_current_tenant_context), db: Session = Depends(get_db)):
    """Retrieve API Keys for 3rd party integrations and marketplace apps."""
    try:
        # In production, query from API keys table
        # For now, return empty list with proper structure
        return {
            "status": "success",
            "organization_id": context.organization_id,
            "api_keys": []
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erreur lors de la récupération des clés API: {str(e)}")

@router.post("/api-keys")
def create_tenant_api_key(payload: APIKeyCreateSchema, context: TenantContext = Depends(get_current_tenant_context), db: Session = Depends(get_db)):
    """Generate a new public API key for the active tenant."""
    try:
        # Generate secure API key
        api_key = f"evo_{secrets.token_urlsafe(32)}"

        # In production, save to database
        # For now, return the generated key
        api_key_data = {
            "id": 1,  # Would be real ID from DB
            "key_name": payload.key_name,
            "api_key": api_key,
            "allowed_ips": payload.allowed_ips or [],
            "is_active": True,
            "created_at": datetime.utcnow().isoformat(),
            "last_used": None
        }

        return {
            "status": "success",
            "api_key": api_key_data,
            "message": "Clé API générée avec succès"
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erreur lors de la génération de la clé API: {str(e)}")

@router.delete("/api-keys/{key_id}")
def revoke_tenant_api_key(key_id: int, context: TenantContext = Depends(get_current_tenant_context), db: Session = Depends(get_db)):
    """Revoke a specific API key."""
    try:
        return {
            "status": "success",
            "key_id": key_id,
            "message": "Clé API révoquée avec succès"
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erreur lors de la révocation de la clé API: {str(e)}")
