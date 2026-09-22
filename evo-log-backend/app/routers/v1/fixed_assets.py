from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from pydantic import BaseModel, Field
from typing import List, Optional
from datetime import datetime

from app.database import get_db
from app.utils.tenant import get_current_tenant_context, TenantContext, require_module_access

router = APIRouter()

class FixedAssetSchema(BaseModel):
    asset_code: str = Field(..., example="IMM-TR-045")
    name: str = Field(..., example="Tracteur Routier Mercedes Actros 3344")
    category: str = Field("FLEET", example="FLEET") # FLEET, MACHINERY, REAL_ESTATE, IT
    acquisition_date: str = Field(..., example="2024-01-15")
    acquisition_value: float = Field(..., example=65000000.0)
    amortization_years: int = Field(5, example=5)
    amortization_method: str = Field("LINEAR", example="LINEAR") # LINEAR, DEGRESSIVE

@router.get("/assets", dependencies=[Depends(require_module_access("parc"))])
def list_fixed_assets(context: TenantContext = Depends(get_current_tenant_context)):
    """Retrieve fixed assets registry and amortization schedules."""
    return {
        "status": "unavailable",
        "organization_id": context.organization_id,
        "assets": []
    }

@router.post("/assets", status_code=status.HTTP_501_NOT_IMPLEMENTED, dependencies=[Depends(require_module_access("parc"))])
def create_fixed_asset(payload: FixedAssetSchema, context: TenantContext = Depends(get_current_tenant_context)):
    raise HTTPException(
        status_code=501,
        detail="L'enregistrement des immobilisations n'est pas encore configuré pour ce tenant."
    )
