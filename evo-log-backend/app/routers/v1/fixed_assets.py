from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from pydantic import BaseModel, Field
from typing import List, Optional
from datetime import datetime

from app.database import get_db
from app.utils.tenant import get_current_tenant_context, TenantContext, require_module_access
from app.core.not_implemented import not_implemented

router = APIRouter()

class FixedAssetSchema(BaseModel):
    asset_code: str = Field(..., example="IMM-TR-045")
    name: str = Field(..., example="Tracteur Routier Mercedes Actros 3344")
    category: str = Field("FLEET", example="FLEET") # FLEET, MACHINERY, REAL_ESTATE, IT
    acquisition_date: str = Field(..., example="2024-01-15")
    acquisition_value: float = Field(..., example=65000000.0)
    amortization_years: int = Field(5, example=5)
    amortization_method: str = Field("LINEAR", example="LINEAR") # LINEAR, DEGRESSIVE

@router.get("/", dependencies=[Depends(require_module_access("parc"))])
def list_fixed_assets(context: TenantContext = Depends(get_current_tenant_context)):
    """Registre immobilisations : 501 (actif inventorie, aucune table d'immobilisation)."""
    not_implemented(
        "Registre des immobilisations et tableau d'amortissement",
        "une table d'immobilisations portee par le tenant avec calcul de "
        "dotation reel (la ligne retournee etait fabriquee)",
    )

@router.post("/", status_code=status.HTTP_201_CREATED, dependencies=[Depends(require_module_access("parc"))])
def create_fixed_asset(payload: FixedAssetSchema, context: TenantContext = Depends(get_current_tenant_context)):
    """Creation d'immobilisation : 501 (ne persistait rien, faux succes)."""
    not_implemented(
        "Enregistrement d'une immobilisation",
        "un modele/une table d'immobilisations pour reellement creer la fiche et "
        "son planning d'amortissement (l'ID retourne etait un simple horodatage)",
    )
