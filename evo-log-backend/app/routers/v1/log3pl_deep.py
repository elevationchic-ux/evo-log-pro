"""Routeur CRUD genere pour logistique-3pl (expansion)."""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import Optional, List

from app.core.database import get_db
from app.core.permissions import require_perm
from app.models.user import User
from app.models.log3pl_deep import (
    TplContract,
    TplWarehouse,
    TplCrossDock,
    TplPickingLine,
    TplSlaKpi,
    TplInvoice,
    TplInventoryValuation,
    TplSubProvider,
    TplReverseOperation,
    TplControlTower,
)
from app.schemas.log3pl_deep import (
    TplContractCreate, TplContractUpdate, TplContractOut,
    TplWarehouseCreate, TplWarehouseUpdate, TplWarehouseOut,
    TplCrossDockCreate, TplCrossDockUpdate, TplCrossDockOut,
    TplPickingLineCreate, TplPickingLineUpdate, TplPickingLineOut,
    TplSlaKpiCreate, TplSlaKpiUpdate, TplSlaKpiOut,
    TplInvoiceCreate, TplInvoiceUpdate, TplInvoiceOut,
    TplInventoryValuationCreate, TplInventoryValuationUpdate, TplInventoryValuationOut,
    TplSubProviderCreate, TplSubProviderUpdate, TplSubProviderOut,
    TplReverseOperationCreate, TplReverseOperationUpdate, TplReverseOperationOut,
    TplControlTowerCreate, TplControlTowerUpdate, TplControlTowerOut,
)

router = APIRouter(tags=["logistique-3pl (expansion)"])


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

@router.get("/nomenclatures", summary="Vocabulaire metier logistique-3pl")
def nomenclatures(user: User = Depends(require_perm("log3pl.nomenclature.read"))):
    from app.models import log3pl_deep as _md
    import enum as _pyenum
    out = {}
    for name in dir(_md):
        obj = getattr(_md, name)
        if isinstance(obj, type) and issubclass(obj, _pyenum.Enum) and obj is not _pyenum.Enum:
            out[name.lower()] = [{"code": m.name, "valeur": m.value} for m in obj]
    return out


# ─── Contrats cadres 3PL ─────────────────────────────────────────────────

@router.get("/tpl-contracts", response_model=List[TplContractOut])
def list_contracts(statut: Optional[str] = None, db: Session = Depends(get_db),
    user: User = Depends(require_perm("log3pl.contracts.read")),
):
    cid = _company_id(user)
    return _scoped_list(db, TplContract, cid, {"statut": statut})


@router.post("/tpl-contracts", response_model=TplContractOut, status_code=201)
def create_contracts(
    payload: TplContractCreate,
    db: Session = Depends(get_db),
    user: User = Depends(require_perm("log3pl.contracts.create")),
):
    cid = _company_id(user)
    data = payload.model_dump(exclude_unset=True)
    _check_unique(db, TplContract, "numero_contrat", data.get("numero_contrat"), "numero_contrat", cid)
    obj = TplContract(company_id=cid)
    _apply(data, obj)
    db.add(obj)
    db.commit()
    db.refresh(obj)
    return obj


@router.put("/tpl-contracts/{ident}", response_model=TplContractOut)
def update_contracts(
    ident: int,
    payload: TplContractUpdate,
    db: Session = Depends(get_db),
    user: User = Depends(require_perm("log3pl.contracts.modify")),
):
    cid = _company_id(user)
    obj = _get_or_404(db, TplContract, ident, "Contrats cadres 3PL")
    if obj.company_id != cid:
        raise HTTPException(403, "Acces refuse.")
    _apply(payload.model_dump(exclude_unset=True), obj)
    db.commit()
    db.refresh(obj)
    return obj


@router.delete("/tpl-contracts/{ident}", response_model=TplContractOut)
def delete_contracts(
    ident: int,
    db: Session = Depends(get_db),
    user: User = Depends(require_perm("log3pl.contracts.modify")),
):
    cid = _company_id(user)
    obj = _get_or_404(db, TplContract, ident, "Contrats cadres 3PL")
    if obj.company_id != cid:
        raise HTTPException(403, "Acces refuse.")
    obj.is_active = False
    db.commit()
    db.refresh(obj)
    return obj


# ─── Entrepots sous contrat ─────────────────────────────────────────────────

@router.get("/tpl-warehouses", response_model=List[TplWarehouseOut])
def list_warehouses(statut: Optional[str] = None, db: Session = Depends(get_db),
    user: User = Depends(require_perm("log3pl.warehouses.read")),
):
    cid = _company_id(user)
    return _scoped_list(db, TplWarehouse, cid, {"statut": statut})


@router.post("/tpl-warehouses", response_model=TplWarehouseOut, status_code=201)
def create_warehouses(
    payload: TplWarehouseCreate,
    db: Session = Depends(get_db),
    user: User = Depends(require_perm("log3pl.warehouses.create")),
):
    cid = _company_id(user)
    data = payload.model_dump(exclude_unset=True)
    _check_unique(db, TplWarehouse, "code_site", data.get("code_site"), "code_site", cid)
    obj = TplWarehouse(company_id=cid)
    _apply(data, obj)
    db.add(obj)
    db.commit()
    db.refresh(obj)
    return obj


@router.put("/tpl-warehouses/{ident}", response_model=TplWarehouseOut)
def update_warehouses(
    ident: int,
    payload: TplWarehouseUpdate,
    db: Session = Depends(get_db),
    user: User = Depends(require_perm("log3pl.warehouses.modify")),
):
    cid = _company_id(user)
    obj = _get_or_404(db, TplWarehouse, ident, "Entrepots sous contrat")
    if obj.company_id != cid:
        raise HTTPException(403, "Acces refuse.")
    _apply(payload.model_dump(exclude_unset=True), obj)
    db.commit()
    db.refresh(obj)
    return obj


@router.delete("/tpl-warehouses/{ident}", response_model=TplWarehouseOut)
def delete_warehouses(
    ident: int,
    db: Session = Depends(get_db),
    user: User = Depends(require_perm("log3pl.warehouses.modify")),
):
    cid = _company_id(user)
    obj = _get_or_404(db, TplWarehouse, ident, "Entrepots sous contrat")
    if obj.company_id != cid:
        raise HTTPException(403, "Acces refuse.")
    obj.is_active = False
    db.commit()
    db.refresh(obj)
    return obj


# ─── Plans cross-dock ─────────────────────────────────────────────────

@router.get("/tpl-crossdocks", response_model=List[TplCrossDockOut])
def list_crossdock(statut: Optional[str] = None, db: Session = Depends(get_db),
    user: User = Depends(require_perm("log3pl.crossdock.read")),
):
    cid = _company_id(user)
    return _scoped_list(db, TplCrossDock, cid, {"statut": statut})


@router.post("/tpl-crossdocks", response_model=TplCrossDockOut, status_code=201)
def create_crossdock(
    payload: TplCrossDockCreate,
    db: Session = Depends(get_db),
    user: User = Depends(require_perm("log3pl.crossdock.create")),
):
    cid = _company_id(user)
    data = payload.model_dump(exclude_unset=True)
    _check_unique(db, TplCrossDock, "reference", data.get("reference"), "reference", cid)
    obj = TplCrossDock(company_id=cid)
    _apply(data, obj)
    db.add(obj)
    db.commit()
    db.refresh(obj)
    return obj


@router.put("/tpl-crossdocks/{ident}", response_model=TplCrossDockOut)
def update_crossdock(
    ident: int,
    payload: TplCrossDockUpdate,
    db: Session = Depends(get_db),
    user: User = Depends(require_perm("log3pl.crossdock.modify")),
):
    cid = _company_id(user)
    obj = _get_or_404(db, TplCrossDock, ident, "Plans cross-dock")
    if obj.company_id != cid:
        raise HTTPException(403, "Acces refuse.")
    _apply(payload.model_dump(exclude_unset=True), obj)
    db.commit()
    db.refresh(obj)
    return obj


@router.delete("/tpl-crossdocks/{ident}", response_model=TplCrossDockOut)
def delete_crossdock(
    ident: int,
    db: Session = Depends(get_db),
    user: User = Depends(require_perm("log3pl.crossdock.modify")),
):
    cid = _company_id(user)
    obj = _get_or_404(db, TplCrossDock, ident, "Plans cross-dock")
    if obj.company_id != cid:
        raise HTTPException(403, "Acces refuse.")
    obj.is_active = False
    db.commit()
    db.refresh(obj)
    return obj


# ─── Lignes de preparation ─────────────────────────────────────────────────

@router.get("/tpl-picking-lines", response_model=List[TplPickingLineOut])
def list_pickpack(statut: Optional[str] = None, db: Session = Depends(get_db),
    user: User = Depends(require_perm("log3pl.pickpack.read")),
):
    cid = _company_id(user)
    return _scoped_list(db, TplPickingLine, cid, {"statut": statut})


@router.post("/tpl-picking-lines", response_model=TplPickingLineOut, status_code=201)
def create_pickpack(
    payload: TplPickingLineCreate,
    db: Session = Depends(get_db),
    user: User = Depends(require_perm("log3pl.pickpack.create")),
):
    cid = _company_id(user)
    data = payload.model_dump(exclude_unset=True)
    _check_unique(db, TplPickingLine, "reference", data.get("reference"), "reference", cid)
    obj = TplPickingLine(company_id=cid)
    _apply(data, obj)
    db.add(obj)
    db.commit()
    db.refresh(obj)
    return obj


@router.put("/tpl-picking-lines/{ident}", response_model=TplPickingLineOut)
def update_pickpack(
    ident: int,
    payload: TplPickingLineUpdate,
    db: Session = Depends(get_db),
    user: User = Depends(require_perm("log3pl.pickpack.modify")),
):
    cid = _company_id(user)
    obj = _get_or_404(db, TplPickingLine, ident, "Lignes de preparation")
    if obj.company_id != cid:
        raise HTTPException(403, "Acces refuse.")
    _apply(payload.model_dump(exclude_unset=True), obj)
    db.commit()
    db.refresh(obj)
    return obj


@router.delete("/tpl-picking-lines/{ident}", response_model=TplPickingLineOut)
def delete_pickpack(
    ident: int,
    db: Session = Depends(get_db),
    user: User = Depends(require_perm("log3pl.pickpack.modify")),
):
    cid = _company_id(user)
    obj = _get_or_404(db, TplPickingLine, ident, "Lignes de preparation")
    if obj.company_id != cid:
        raise HTTPException(403, "Acces refuse.")
    obj.is_active = False
    db.commit()
    db.refresh(obj)
    return obj


# ─── KPI / SLA contractuels ─────────────────────────────────────────────────

@router.get("/tpl-sla-kpis", response_model=List[TplSlaKpiOut])
def list_slakpi(statut: Optional[str] = None, db: Session = Depends(get_db),
    user: User = Depends(require_perm("log3pl.slakpi.read")),
):
    cid = _company_id(user)
    return _scoped_list(db, TplSlaKpi, cid, {"statut": statut})


@router.post("/tpl-sla-kpis", response_model=TplSlaKpiOut, status_code=201)
def create_slakpi(
    payload: TplSlaKpiCreate,
    db: Session = Depends(get_db),
    user: User = Depends(require_perm("log3pl.slakpi.create")),
):
    cid = _company_id(user)
    data = payload.model_dump(exclude_unset=True)
    _check_unique(db, TplSlaKpi, "reference", data.get("reference"), "reference", cid)
    obj = TplSlaKpi(company_id=cid)
    _apply(data, obj)
    db.add(obj)
    db.commit()
    db.refresh(obj)
    return obj


@router.put("/tpl-sla-kpis/{ident}", response_model=TplSlaKpiOut)
def update_slakpi(
    ident: int,
    payload: TplSlaKpiUpdate,
    db: Session = Depends(get_db),
    user: User = Depends(require_perm("log3pl.slakpi.modify")),
):
    cid = _company_id(user)
    obj = _get_or_404(db, TplSlaKpi, ident, "KPI / SLA contractuels")
    if obj.company_id != cid:
        raise HTTPException(403, "Acces refuse.")
    _apply(payload.model_dump(exclude_unset=True), obj)
    db.commit()
    db.refresh(obj)
    return obj


@router.delete("/tpl-sla-kpis/{ident}", response_model=TplSlaKpiOut)
def delete_slakpi(
    ident: int,
    db: Session = Depends(get_db),
    user: User = Depends(require_perm("log3pl.slakpi.modify")),
):
    cid = _company_id(user)
    obj = _get_or_404(db, TplSlaKpi, ident, "KPI / SLA contractuels")
    if obj.company_id != cid:
        raise HTTPException(403, "Acces refuse.")
    obj.is_active = False
    db.commit()
    db.refresh(obj)
    return obj


# ─── Facturation 3PL ─────────────────────────────────────────────────

@router.get("/tpl-invoices", response_model=List[TplInvoiceOut])
def list_billing(statut: Optional[str] = None, db: Session = Depends(get_db),
    user: User = Depends(require_perm("log3pl.billing.read")),
):
    cid = _company_id(user)
    return _scoped_list(db, TplInvoice, cid, {"statut": statut})


@router.post("/tpl-invoices", response_model=TplInvoiceOut, status_code=201)
def create_billing(
    payload: TplInvoiceCreate,
    db: Session = Depends(get_db),
    user: User = Depends(require_perm("log3pl.billing.create")),
):
    cid = _company_id(user)
    data = payload.model_dump(exclude_unset=True)
    _check_unique(db, TplInvoice, "numero_facture", data.get("numero_facture"), "numero_facture", cid)
    obj = TplInvoice(company_id=cid)
    _apply(data, obj)
    db.add(obj)
    db.commit()
    db.refresh(obj)
    return obj


@router.put("/tpl-invoices/{ident}", response_model=TplInvoiceOut)
def update_billing(
    ident: int,
    payload: TplInvoiceUpdate,
    db: Session = Depends(get_db),
    user: User = Depends(require_perm("log3pl.billing.modify")),
):
    cid = _company_id(user)
    obj = _get_or_404(db, TplInvoice, ident, "Facturation 3PL")
    if obj.company_id != cid:
        raise HTTPException(403, "Acces refuse.")
    _apply(payload.model_dump(exclude_unset=True), obj)
    db.commit()
    db.refresh(obj)
    return obj


@router.delete("/tpl-invoices/{ident}", response_model=TplInvoiceOut)
def delete_billing(
    ident: int,
    db: Session = Depends(get_db),
    user: User = Depends(require_perm("log3pl.billing.modify")),
):
    cid = _company_id(user)
    obj = _get_or_404(db, TplInvoice, ident, "Facturation 3PL")
    if obj.company_id != cid:
        raise HTTPException(403, "Acces refuse.")
    obj.is_active = False
    db.commit()
    db.refresh(obj)
    return obj


# ─── Valorisation stock client ─────────────────────────────────────────────────

@router.get("/tpl-inventory-valuations", response_model=List[TplInventoryValuationOut])
def list_valuation(statut: Optional[str] = None, db: Session = Depends(get_db),
    user: User = Depends(require_perm("log3pl.valuation.read")),
):
    cid = _company_id(user)
    return _scoped_list(db, TplInventoryValuation, cid, {"statut": statut})


@router.post("/tpl-inventory-valuations", response_model=TplInventoryValuationOut, status_code=201)
def create_valuation(
    payload: TplInventoryValuationCreate,
    db: Session = Depends(get_db),
    user: User = Depends(require_perm("log3pl.valuation.create")),
):
    cid = _company_id(user)
    data = payload.model_dump(exclude_unset=True)
    _check_unique(db, TplInventoryValuation, "reference", data.get("reference"), "reference", cid)
    obj = TplInventoryValuation(company_id=cid)
    _apply(data, obj)
    db.add(obj)
    db.commit()
    db.refresh(obj)
    return obj


@router.put("/tpl-inventory-valuations/{ident}", response_model=TplInventoryValuationOut)
def update_valuation(
    ident: int,
    payload: TplInventoryValuationUpdate,
    db: Session = Depends(get_db),
    user: User = Depends(require_perm("log3pl.valuation.modify")),
):
    cid = _company_id(user)
    obj = _get_or_404(db, TplInventoryValuation, ident, "Valorisation stock client")
    if obj.company_id != cid:
        raise HTTPException(403, "Acces refuse.")
    _apply(payload.model_dump(exclude_unset=True), obj)
    db.commit()
    db.refresh(obj)
    return obj


@router.delete("/tpl-inventory-valuations/{ident}", response_model=TplInventoryValuationOut)
def delete_valuation(
    ident: int,
    db: Session = Depends(get_db),
    user: User = Depends(require_perm("log3pl.valuation.modify")),
):
    cid = _company_id(user)
    obj = _get_or_404(db, TplInventoryValuation, ident, "Valorisation stock client")
    if obj.company_id != cid:
        raise HTTPException(403, "Acces refuse.")
    obj.is_active = False
    db.commit()
    db.refresh(obj)
    return obj


# ─── Sous-traitants secondaires ─────────────────────────────────────────────────

@router.get("/tpl-sub-providers", response_model=List[TplSubProviderOut])
def list_subcontractors(statut: Optional[str] = None, db: Session = Depends(get_db),
    user: User = Depends(require_perm("log3pl.subcontractors.read")),
):
    cid = _company_id(user)
    return _scoped_list(db, TplSubProvider, cid, {"statut": statut})


@router.post("/tpl-sub-providers", response_model=TplSubProviderOut, status_code=201)
def create_subcontractors(
    payload: TplSubProviderCreate,
    db: Session = Depends(get_db),
    user: User = Depends(require_perm("log3pl.subcontractors.create")),
):
    cid = _company_id(user)
    data = payload.model_dump(exclude_unset=True)
    _check_unique(db, TplSubProvider, "code_fournisseur", data.get("code_fournisseur"), "code_fournisseur", cid)
    obj = TplSubProvider(company_id=cid)
    _apply(data, obj)
    db.add(obj)
    db.commit()
    db.refresh(obj)
    return obj


@router.put("/tpl-sub-providers/{ident}", response_model=TplSubProviderOut)
def update_subcontractors(
    ident: int,
    payload: TplSubProviderUpdate,
    db: Session = Depends(get_db),
    user: User = Depends(require_perm("log3pl.subcontractors.modify")),
):
    cid = _company_id(user)
    obj = _get_or_404(db, TplSubProvider, ident, "Sous-traitants secondaires")
    if obj.company_id != cid:
        raise HTTPException(403, "Acces refuse.")
    _apply(payload.model_dump(exclude_unset=True), obj)
    db.commit()
    db.refresh(obj)
    return obj


@router.delete("/tpl-sub-providers/{ident}", response_model=TplSubProviderOut)
def delete_subcontractors(
    ident: int,
    db: Session = Depends(get_db),
    user: User = Depends(require_perm("log3pl.subcontractors.modify")),
):
    cid = _company_id(user)
    obj = _get_or_404(db, TplSubProvider, ident, "Sous-traitants secondaires")
    if obj.company_id != cid:
        raise HTTPException(403, "Acces refuse.")
    obj.is_active = False
    db.commit()
    db.refresh(obj)
    return obj


# ─── Logistique retour / SAV ─────────────────────────────────────────────────

@router.get("/tpl-reverse-operations", response_model=List[TplReverseOperationOut])
def list_reverse(statut: Optional[str] = None, db: Session = Depends(get_db),
    user: User = Depends(require_perm("log3pl.reverse.read")),
):
    cid = _company_id(user)
    return _scoped_list(db, TplReverseOperation, cid, {"statut": statut})


@router.post("/tpl-reverse-operations", response_model=TplReverseOperationOut, status_code=201)
def create_reverse(
    payload: TplReverseOperationCreate,
    db: Session = Depends(get_db),
    user: User = Depends(require_perm("log3pl.reverse.create")),
):
    cid = _company_id(user)
    data = payload.model_dump(exclude_unset=True)
    _check_unique(db, TplReverseOperation, "reference", data.get("reference"), "reference", cid)
    obj = TplReverseOperation(company_id=cid)
    _apply(data, obj)
    db.add(obj)
    db.commit()
    db.refresh(obj)
    return obj


@router.put("/tpl-reverse-operations/{ident}", response_model=TplReverseOperationOut)
def update_reverse(
    ident: int,
    payload: TplReverseOperationUpdate,
    db: Session = Depends(get_db),
    user: User = Depends(require_perm("log3pl.reverse.modify")),
):
    cid = _company_id(user)
    obj = _get_or_404(db, TplReverseOperation, ident, "Logistique retour / SAV")
    if obj.company_id != cid:
        raise HTTPException(403, "Acces refuse.")
    _apply(payload.model_dump(exclude_unset=True), obj)
    db.commit()
    db.refresh(obj)
    return obj


@router.delete("/tpl-reverse-operations/{ident}", response_model=TplReverseOperationOut)
def delete_reverse(
    ident: int,
    db: Session = Depends(get_db),
    user: User = Depends(require_perm("log3pl.reverse.modify")),
):
    cid = _company_id(user)
    obj = _get_or_404(db, TplReverseOperation, ident, "Logistique retour / SAV")
    if obj.company_id != cid:
        raise HTTPException(403, "Acces refuse.")
    obj.is_active = False
    db.commit()
    db.refresh(obj)
    return obj


# ─── Tour de controle multi-flux ─────────────────────────────────────────────────

@router.get("/tpl-control-towers", response_model=List[TplControlTowerOut])
def list_controltower(statut: Optional[str] = None, db: Session = Depends(get_db),
    user: User = Depends(require_perm("log3pl.controltower.read")),
):
    cid = _company_id(user)
    return _scoped_list(db, TplControlTower, cid, {"statut": statut})


@router.post("/tpl-control-towers", response_model=TplControlTowerOut, status_code=201)
def create_controltower(
    payload: TplControlTowerCreate,
    db: Session = Depends(get_db),
    user: User = Depends(require_perm("log3pl.controltower.create")),
):
    cid = _company_id(user)
    data = payload.model_dump(exclude_unset=True)
    _check_unique(db, TplControlTower, "reference", data.get("reference"), "reference", cid)
    obj = TplControlTower(company_id=cid)
    _apply(data, obj)
    db.add(obj)
    db.commit()
    db.refresh(obj)
    return obj


@router.put("/tpl-control-towers/{ident}", response_model=TplControlTowerOut)
def update_controltower(
    ident: int,
    payload: TplControlTowerUpdate,
    db: Session = Depends(get_db),
    user: User = Depends(require_perm("log3pl.controltower.modify")),
):
    cid = _company_id(user)
    obj = _get_or_404(db, TplControlTower, ident, "Tour de controle multi-flux")
    if obj.company_id != cid:
        raise HTTPException(403, "Acces refuse.")
    _apply(payload.model_dump(exclude_unset=True), obj)
    db.commit()
    db.refresh(obj)
    return obj


@router.delete("/tpl-control-towers/{ident}", response_model=TplControlTowerOut)
def delete_controltower(
    ident: int,
    db: Session = Depends(get_db),
    user: User = Depends(require_perm("log3pl.controltower.modify")),
):
    cid = _company_id(user)
    obj = _get_or_404(db, TplControlTower, ident, "Tour de controle multi-flux")
    if obj.company_id != cid:
        raise HTTPException(403, "Acces refuse.")
    obj.is_active = False
    db.commit()
    db.refresh(obj)
    return obj

