"""Routeur CRUD genere pour finance-ohada (expansion)."""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import Optional, List

from app.core.database import get_db
from app.core.permissions import require_perm
from app.models.user import User
from app.models.finance_c_deep import (
    FincCashFlowForecast,
    FincInvoiceFinancing,
)
from app.schemas.finance_c_deep import (
    FincCashFlowForecastCreate, FincCashFlowForecastUpdate, FincCashFlowForecastOut,
    FincInvoiceFinancingCreate, FincInvoiceFinancingUpdate, FincInvoiceFinancingOut,
)

router = APIRouter(tags=["finance-ohada (expansion)"])


# ─── Helpers generiques ──────────────────────────────────────────────────────

def _get_or_404(db: Session, model, ident: int, label: str):
    row = db.query(model).filter(model.id == ident).first()
    if not row:
        raise HTTPException(status_code=404, detail=f"{label} introuvable (id={ident})")
    return row


def _check_unique(db: Session, model, field: str, value, label: str, company_id: int, exclude_id=None):
    if value is None:
        return
    q = db.query(model).filter(getattr(model, field) == value, model.company_id == company_id)
    if exclude_id is not None:
        q = q.filter(model.id != exclude_id)
    if q.first():
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=f"{label} « {value} » existe deja dans votre organisation.",
        )


def _scoped_list(db, model, company_id, filters=None):
    q = db.query(model).filter(model.company_id == company_id)
    if hasattr(model, 'is_active'):
        q = q.filter(model.is_active.is_(True))
    if filters:
        for key, val in filters.items():
            if val is not None and hasattr(model, key):
                q = q.filter(getattr(model, key) == val)
    return q.order_by(model.id.desc()).all()


def _apply(payload: dict, obj):
    for key, value in payload.items():
        setattr(obj, key, value)


def _company_id(user: User) -> int:
    if not user.company_id:
        raise HTTPException(status_code=400, detail="Votre compte n'est rattache a aucune organisation.")
    return user.company_id


# ─── Nomenclatures ───────────────────────────────────────────────────────────

@router.get("/nomenclatures", summary="Vocabulaire metier finance-ohada")
def nomenclatures(user: User = Depends(require_perm("tresorerie.nomenclature.read"))):
    from app.models import finance_c_deep as _md
    import enum as _pyenum
    out = {}
    for name in dir(_md):
        obj = getattr(_md, name)
        if isinstance(obj, type) and issubclass(obj, _pyenum.Enum) and obj is not _pyenum.Enum:
            out[name.lower()] = [{"code": m.name, "valeur": m.value} for m in obj]
    return out


# ─── Previsions de tresorerie ─────────────────────────────────────────────────

@router.get("/finc-cash-flow-forecasts", response_model=List[FincCashFlowForecastOut])
def list_cash_flow_forecast(statut: Optional[str] = None, db: Session = Depends(get_db),
    user: User = Depends(require_perm("tresorerie.cash_flow_forecast.read")),
):
    cid = _company_id(user)
    return _scoped_list(db, FincCashFlowForecast, cid, {"statut": statut})


@router.post("/finc-cash-flow-forecasts", response_model=FincCashFlowForecastOut, status_code=201)
def create_cash_flow_forecast(
    payload: FincCashFlowForecastCreate,
    db: Session = Depends(get_db),
    user: User = Depends(require_perm("tresorerie.cash_flow_forecast.create")),
):
    cid = _company_id(user)
    data = payload.model_dump(exclude_unset=True)
    _check_unique(db, FincCashFlowForecast, "reference", data.get("reference"), "reference", cid)
    obj = FincCashFlowForecast(company_id=cid)
    _apply(data, obj)
    db.add(obj)
    db.commit()
    db.refresh(obj)
    return obj


@router.put("/finc-cash-flow-forecasts/{ident}", response_model=FincCashFlowForecastOut)
def update_cash_flow_forecast(
    ident: int,
    payload: FincCashFlowForecastUpdate,
    db: Session = Depends(get_db),
    user: User = Depends(require_perm("tresorerie.cash_flow_forecast.modify")),
):
    cid = _company_id(user)
    obj = _get_or_404(db, FincCashFlowForecast, ident, "Previsions de tresorerie")
    if obj.company_id != cid:
        raise HTTPException(403, "Acces refuse.")
    _apply(payload.model_dump(exclude_unset=True), obj)
    db.commit()
    db.refresh(obj)
    return obj


@router.delete("/finc-cash-flow-forecasts/{ident}", response_model=FincCashFlowForecastOut)
def delete_cash_flow_forecast(
    ident: int,
    db: Session = Depends(get_db),
    user: User = Depends(require_perm("tresorerie.cash_flow_forecast.modify")),
):
    cid = _company_id(user)
    obj = _get_or_404(db, FincCashFlowForecast, ident, "Previsions de tresorerie")
    if obj.company_id != cid:
        raise HTTPException(403, "Acces refuse.")
    obj.is_active = False
    db.commit()
    db.refresh(obj)
    return obj


# ─── Affacturage / escompte de factures ─────────────────────────────────────────────────

@router.get("/finc-invoice-financings", response_model=List[FincInvoiceFinancingOut])
def list_invoice_financing(statut: Optional[str] = None, db: Session = Depends(get_db),
    user: User = Depends(require_perm("tresorerie.invoice_financing.read")),
):
    cid = _company_id(user)
    return _scoped_list(db, FincInvoiceFinancing, cid, {"statut": statut})


@router.post("/finc-invoice-financings", response_model=FincInvoiceFinancingOut, status_code=201)
def create_invoice_financing(
    payload: FincInvoiceFinancingCreate,
    db: Session = Depends(get_db),
    user: User = Depends(require_perm("tresorerie.invoice_financing.create")),
):
    cid = _company_id(user)
    data = payload.model_dump(exclude_unset=True)
    _check_unique(db, FincInvoiceFinancing, "reference", data.get("reference"), "reference", cid)
    obj = FincInvoiceFinancing(company_id=cid)
    _apply(data, obj)
    db.add(obj)
    db.commit()
    db.refresh(obj)
    return obj


@router.put("/finc-invoice-financings/{ident}", response_model=FincInvoiceFinancingOut)
def update_invoice_financing(
    ident: int,
    payload: FincInvoiceFinancingUpdate,
    db: Session = Depends(get_db),
    user: User = Depends(require_perm("tresorerie.invoice_financing.modify")),
):
    cid = _company_id(user)
    obj = _get_or_404(db, FincInvoiceFinancing, ident, "Affacturage / escompte de factures")
    if obj.company_id != cid:
        raise HTTPException(403, "Acces refuse.")
    _apply(payload.model_dump(exclude_unset=True), obj)
    db.commit()
    db.refresh(obj)
    return obj


@router.delete("/finc-invoice-financings/{ident}", response_model=FincInvoiceFinancingOut)
def delete_invoice_financing(
    ident: int,
    db: Session = Depends(get_db),
    user: User = Depends(require_perm("tresorerie.invoice_financing.modify")),
):
    cid = _company_id(user)
    obj = _get_or_404(db, FincInvoiceFinancing, ident, "Affacturage / escompte de factures")
    if obj.company_id != cid:
        raise HTTPException(403, "Acces refuse.")
    obj.is_active = False
    db.commit()
    db.refresh(obj)
    return obj

