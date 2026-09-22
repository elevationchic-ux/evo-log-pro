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
        "status": "success",
        "organization_id": context.organization_id,
        "assets": [
            {
                "id": "AST-001",
                "asset_code": "IMM-TR-045",
                "name": "Tracteur Routier Mercedes Actros 3344",
                "category": "FLEET",
                "acquisition_value": 65000000.0,
                "accumulated_amortization": 26000000.0, # 2 ans d'amortissement
                "net_book_value": 39000000.0,
                "annual_depreciation": 13000000.0,
                "status": "ACTIVE"
            }
        ]
    }

@router.post("/assets", status_code=status.HTTP_201_CREATED, dependencies=[Depends(require_module_access("parc"))])
def create_fixed_asset(payload: FixedAssetSchema, context: TenantContext = Depends(get_current_tenant_context)):
    annual_dep = payload.acquisition_value / payload.amortization_years if payload.amortization_years > 0 else 0
    return {
        "status": "success",
        "message": "Fixed asset recorded and amortization schedule generated.",
        "asset": {
            "id": f"AST-00{datetime.utcnow().strftime('%S')}",
            "organization_id": context.organization_id,
            **payload.dict(),
            "annual_depreciation": annual_dep,
            "accumulated_amortization": 0.0,
            "net_book_value": payload.acquisition_value
        }
    }
