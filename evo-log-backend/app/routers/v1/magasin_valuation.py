"""Valorisation et allocation FEFO des stocks."""
from typing import Any, Dict

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.permissions import require_perm
from app.models.user import User
from app.services.stock_valuation_service import StockValuationService


router = APIRouter(tags=["Magasin — Valorisation & FEFO"])


@router.get("/valorisation/{stock_id}")
def valoriser_article(
    stock_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_perm("magasin.stock.read")),
):
    try:
        return StockValuationService.valoriser_stock(db, stock_id)
    except ValueError as exc:
        raise HTTPException(status_code=404, detail=str(exc))


@router.get("/valorisation")
def valorisation_globale(
    db: Session = Depends(get_db),
    current_user: User = Depends(require_perm("magasin.stock.read")),
):
    return StockValuationService.valorisation_globale(db)


@router.get("/fefo/{stock_id}")
def allocation_fefo(
    stock_id: int,
    quantite: float = Query(..., gt=0),
    db: Session = Depends(get_db),
    current_user: User = Depends(require_perm("magasin.stock.read")),
):
    """Allocation FEFO d'une sortie : lots tries par peremption croissante."""
    try:
        return StockValuationService.allocation_fefo(db, stock_id, quantite)
    except ValueError as exc:
        raise HTTPException(status_code=404, detail=str(exc))
