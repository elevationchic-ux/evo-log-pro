from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session
from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any
from datetime import date

from app.database import get_db
from app.utils.tenant import get_current_tenant_context, TenantContext, require_module_access
from app.models.advanced_crud import FixedAsset

router = APIRouter()


class FixedAssetSchema(BaseModel):
    asset_code: str = Field(..., example="IMM-TR-045")
    name: str = Field(..., example="Tracteur Routier Mercedes Actros 3344")
    category: str = Field("FLEET", example="FLEET")  # FLEET, MACHINERY, REAL_ESTATE, IT
    acquisition_date: str = Field(..., example="2024-01-15")
    acquisition_value: float = Field(..., example=65000000.0)
    residual_value: float = Field(0.0, example=5000000.0)
    amortization_years: int = Field(5, example=5)
    amortization_method: str = Field("LINEAR", example="LINEAR")  # LINEAR, DEGRESSIVE


class FixedAssetOut(BaseModel):
    id: int
    asset_code: str
    name: str
    category: str
    acquisition_date: Optional[str]
    acquisition_value: float
    residual_value: float
    amortization_years: int
    amortization_method: str
    amortization: Dict[str, Any]

    class Config:
        from_attributes = True


def _serialize(asset: FixedAsset, as_of: date) -> FixedAssetOut:
    return FixedAssetOut(
        id=asset.id,
        asset_code=asset.asset_code,
        name=asset.name,
        category=asset.category,
        acquisition_date=asset.acquisition_date,
        acquisition_value=float(asset.acquisition_value or 0),
        residual_value=float(asset.residual_value or 0),
        amortization_years=asset.amortization_years,
        amortization_method=asset.amortization_method,
        amortization=asset.amortization_schedule(as_of),
    )


def _scope(context: TenantContext, query):
    if context.organization_id is not None:
        return query.filter(FixedAsset.organization_id == context.organization_id)
    return query


@router.get("/", response_model=List[FixedAssetOut], dependencies=[Depends(require_module_access("parc"))])
def list_fixed_assets(
    context: TenantContext = Depends(get_current_tenant_context),
    db: Session = Depends(get_db),
    as_of: Optional[str] = None,
):
    """Registre immobilisations avec tableau d'amortissement CALCULE (lineaire/degressif)."""
    ref = date.fromisoformat(as_of) if as_of else date.today()
    rows = _scope(context, db.query(FixedAsset)).order_by(FixedAsset.created_at.desc()).all()
    return [_serialize(a, ref) for a in rows]


@router.post("/", response_model=FixedAssetOut, status_code=status.HTTP_201_CREATED,
             dependencies=[Depends(require_module_access("parc"))])
def create_fixed_asset(
    payload: FixedAssetSchema,
    context: TenantContext = Depends(get_current_tenant_context),
    db: Session = Depends(get_db),
):
    """Enregistrement d'une immobilisation : fiche + planning d'amortissement reels."""
    asset = FixedAsset(organization_id=context.organization_id, **payload.model_dump())
    db.add(asset)
    db.commit()
    db.refresh(asset)
    return _serialize(asset, date.today())
