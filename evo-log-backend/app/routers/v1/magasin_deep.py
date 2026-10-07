"""Routeur CRUD genere pour magasin-stock (expansion)."""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import Optional, List

from app.core.database import get_db
from app.core.permissions import require_perm
from app.models.user import User
from app.models.magasin_deep import (
    ArticleCatalog,
    SupplierArticle,
    PurchaseOrderDeep,
    QualityInspection,
    StockAlert,
    ExpiryRecord,
    SerialNumber,
    PackingUnit,
    StockReturn,
    ConsignmentStock,
    StockValuation,
    WmsKpi,
)
from app.schemas.magasin_deep import (
    ArticleCatalogCreate, ArticleCatalogUpdate, ArticleCatalogOut,
    SupplierArticleCreate, SupplierArticleUpdate, SupplierArticleOut,
    PurchaseOrderDeepCreate, PurchaseOrderDeepUpdate, PurchaseOrderDeepOut,
    QualityInspectionCreate, QualityInspectionUpdate, QualityInspectionOut,
    StockAlertCreate, StockAlertUpdate, StockAlertOut,
    ExpiryRecordCreate, ExpiryRecordUpdate, ExpiryRecordOut,
    SerialNumberCreate, SerialNumberUpdate, SerialNumberOut,
    PackingUnitCreate, PackingUnitUpdate, PackingUnitOut,
    StockReturnCreate, StockReturnUpdate, StockReturnOut,
    ConsignmentStockCreate, ConsignmentStockUpdate, ConsignmentStockOut,
    StockValuationCreate, StockValuationUpdate, StockValuationOut,
    WmsKpiCreate, WmsKpiUpdate, WmsKpiOut,
)

router = APIRouter(tags=["magasin-stock (expansion)"])


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

@router.get("/nomenclatures", summary="Vocabulaire metier magasin-stock")
def nomenclatures(user: User = Depends(require_perm("magasin.nomenclature.read"))):
    from app.models import magasin_deep as _md
    import enum as _pyenum
    out = {}
    for name in dir(_md):
        obj = getattr(_md, name)
        if isinstance(obj, type) and issubclass(obj, _pyenum.Enum) and obj is not _pyenum.Enum:
            out[name.lower()] = [{"code": m.name, "valeur": m.value} for m in obj]
    return out


# ─── Referentiel articles / SKU ─────────────────────────────────────────────────

@router.get("/article-catalogs", response_model=List[ArticleCatalogOut])
def list_article_catalog(statut: Optional[str] = None, db: Session = Depends(get_db),
    user: User = Depends(require_perm("magasin.article_catalog.read")),
):
    cid = _company_id(user)
    return _scoped_list(db, ArticleCatalog, cid, {"statut": statut})


@router.post("/article-catalogs", response_model=ArticleCatalogOut, status_code=201)
def create_article_catalog(
    payload: ArticleCatalogCreate,
    db: Session = Depends(get_db),
    user: User = Depends(require_perm("magasin.article_catalog.create")),
):
    cid = _company_id(user)
    data = payload.model_dump(exclude_unset=True)
    _check_unique(db, ArticleCatalog, "code_sku", data.get("code_sku"), "code_sku", cid)
    obj = ArticleCatalog(company_id=cid)
    _apply(data, obj)
    db.add(obj)
    db.commit()
    db.refresh(obj)
    return obj


@router.put("/article-catalogs/{ident}", response_model=ArticleCatalogOut)
def update_article_catalog(
    ident: int,
    payload: ArticleCatalogUpdate,
    db: Session = Depends(get_db),
    user: User = Depends(require_perm("magasin.article_catalog.modify")),
):
    cid = _company_id(user)
    obj = _get_or_404(db, ArticleCatalog, ident, "Referentiel articles / SKU")
    if obj.company_id != cid:
        raise HTTPException(403, "Acces refuse.")
    _apply(payload.model_dump(exclude_unset=True), obj)
    db.commit()
    db.refresh(obj)
    return obj


@router.delete("/article-catalogs/{ident}", response_model=ArticleCatalogOut)
def delete_article_catalog(
    ident: int,
    db: Session = Depends(get_db),
    user: User = Depends(require_perm("magasin.article_catalog.modify")),
):
    cid = _company_id(user)
    obj = _get_or_404(db, ArticleCatalog, ident, "Referentiel articles / SKU")
    if obj.company_id != cid:
        raise HTTPException(403, "Acces refuse.")
    obj.is_active = False
    db.commit()
    db.refresh(obj)
    return obj


# ─── Fournisseurs par article ─────────────────────────────────────────────────

@router.get("/supplier-articles", response_model=List[SupplierArticleOut])
def list_supplier_catalog(db: Session = Depends(get_db),
    user: User = Depends(require_perm("magasin.supplier_catalog.read")),
):
    cid = _company_id(user)
    return _scoped_list(db, SupplierArticle, cid)


@router.post("/supplier-articles", response_model=SupplierArticleOut, status_code=201)
def create_supplier_catalog(
    payload: SupplierArticleCreate,
    db: Session = Depends(get_db),
    user: User = Depends(require_perm("magasin.supplier_catalog.create")),
):
    cid = _company_id(user)
    data = payload.model_dump(exclude_unset=True)
    _check_unique(db, SupplierArticle, "reference", data.get("reference"), "reference", cid)
    obj = SupplierArticle(company_id=cid)
    _apply(data, obj)
    db.add(obj)
    db.commit()
    db.refresh(obj)
    return obj


@router.put("/supplier-articles/{ident}", response_model=SupplierArticleOut)
def update_supplier_catalog(
    ident: int,
    payload: SupplierArticleUpdate,
    db: Session = Depends(get_db),
    user: User = Depends(require_perm("magasin.supplier_catalog.modify")),
):
    cid = _company_id(user)
    obj = _get_or_404(db, SupplierArticle, ident, "Fournisseurs par article")
    if obj.company_id != cid:
        raise HTTPException(403, "Acces refuse.")
    _apply(payload.model_dump(exclude_unset=True), obj)
    db.commit()
    db.refresh(obj)
    return obj


@router.delete("/supplier-articles/{ident}", response_model=SupplierArticleOut)
def delete_supplier_catalog(
    ident: int,
    db: Session = Depends(get_db),
    user: User = Depends(require_perm("magasin.supplier_catalog.modify")),
):
    cid = _company_id(user)
    obj = _get_or_404(db, SupplierArticle, ident, "Fournisseurs par article")
    if obj.company_id != cid:
        raise HTTPException(403, "Acces refuse.")
    obj.is_active = False
    db.commit()
    db.refresh(obj)
    return obj


# ─── Commandes d'achat ─────────────────────────────────────────────────

@router.get("/purchase-orders", response_model=List[PurchaseOrderDeepOut])
def list_purchase_order(statut: Optional[str] = None, db: Session = Depends(get_db),
    user: User = Depends(require_perm("magasin.purchase_order.read")),
):
    cid = _company_id(user)
    return _scoped_list(db, PurchaseOrderDeep, cid, {"statut": statut})


@router.post("/purchase-orders", response_model=PurchaseOrderDeepOut, status_code=201)
def create_purchase_order(
    payload: PurchaseOrderDeepCreate,
    db: Session = Depends(get_db),
    user: User = Depends(require_perm("magasin.purchase_order.create")),
):
    cid = _company_id(user)
    data = payload.model_dump(exclude_unset=True)
    _check_unique(db, PurchaseOrderDeep, "numero_commande", data.get("numero_commande"), "numero_commande", cid)
    obj = PurchaseOrderDeep(company_id=cid)
    _apply(data, obj)
    db.add(obj)
    db.commit()
    db.refresh(obj)
    return obj


@router.put("/purchase-orders/{ident}", response_model=PurchaseOrderDeepOut)
def update_purchase_order(
    ident: int,
    payload: PurchaseOrderDeepUpdate,
    db: Session = Depends(get_db),
    user: User = Depends(require_perm("magasin.purchase_order.modify")),
):
    cid = _company_id(user)
    obj = _get_or_404(db, PurchaseOrderDeep, ident, "Commandes d'achat")
    if obj.company_id != cid:
        raise HTTPException(403, "Acces refuse.")
    _apply(payload.model_dump(exclude_unset=True), obj)
    db.commit()
    db.refresh(obj)
    return obj


@router.delete("/purchase-orders/{ident}", response_model=PurchaseOrderDeepOut)
def delete_purchase_order(
    ident: int,
    db: Session = Depends(get_db),
    user: User = Depends(require_perm("magasin.purchase_order.modify")),
):
    cid = _company_id(user)
    obj = _get_or_404(db, PurchaseOrderDeep, ident, "Commandes d'achat")
    if obj.company_id != cid:
        raise HTTPException(403, "Acces refuse.")
    obj.is_active = False
    db.commit()
    db.refresh(obj)
    return obj


# ─── Controle qualite a reception ─────────────────────────────────────────────────

@router.get("/quality-inspections", response_model=List[QualityInspectionOut])
def list_quality_control(db: Session = Depends(get_db),
    user: User = Depends(require_perm("magasin.quality_control.read")),
):
    cid = _company_id(user)
    return _scoped_list(db, QualityInspection, cid)


@router.post("/quality-inspections", response_model=QualityInspectionOut, status_code=201)
def create_quality_control(
    payload: QualityInspectionCreate,
    db: Session = Depends(get_db),
    user: User = Depends(require_perm("magasin.quality_control.create")),
):
    cid = _company_id(user)
    data = payload.model_dump(exclude_unset=True)
    _check_unique(db, QualityInspection, "numero_controle", data.get("numero_controle"), "numero_controle", cid)
    obj = QualityInspection(company_id=cid)
    _apply(data, obj)
    db.add(obj)
    db.commit()
    db.refresh(obj)
    return obj


@router.put("/quality-inspections/{ident}", response_model=QualityInspectionOut)
def update_quality_control(
    ident: int,
    payload: QualityInspectionUpdate,
    db: Session = Depends(get_db),
    user: User = Depends(require_perm("magasin.quality_control.modify")),
):
    cid = _company_id(user)
    obj = _get_or_404(db, QualityInspection, ident, "Controle qualite a reception")
    if obj.company_id != cid:
        raise HTTPException(403, "Acces refuse.")
    _apply(payload.model_dump(exclude_unset=True), obj)
    db.commit()
    db.refresh(obj)
    return obj


@router.delete("/quality-inspections/{ident}", response_model=QualityInspectionOut)
def delete_quality_control(
    ident: int,
    db: Session = Depends(get_db),
    user: User = Depends(require_perm("magasin.quality_control.modify")),
):
    cid = _company_id(user)
    obj = _get_or_404(db, QualityInspection, ident, "Controle qualite a reception")
    if obj.company_id != cid:
        raise HTTPException(403, "Acces refuse.")
    obj.is_active = False
    db.commit()
    db.refresh(obj)
    return obj


# ─── Seuils et alertes rupture ─────────────────────────────────────────────────

@router.get("/stock-alerts", response_model=List[StockAlertOut])
def list_stock_alert(statut: Optional[str] = None, db: Session = Depends(get_db),
    user: User = Depends(require_perm("magasin.stock_alert.read")),
):
    cid = _company_id(user)
    return _scoped_list(db, StockAlert, cid, {"statut": statut})


@router.post("/stock-alerts", response_model=StockAlertOut, status_code=201)
def create_stock_alert(
    payload: StockAlertCreate,
    db: Session = Depends(get_db),
    user: User = Depends(require_perm("magasin.stock_alert.create")),
):
    cid = _company_id(user)
    data = payload.model_dump(exclude_unset=True)
    _check_unique(db, StockAlert, "code_alerte", data.get("code_alerte"), "code_alerte", cid)
    obj = StockAlert(company_id=cid)
    _apply(data, obj)
    db.add(obj)
    db.commit()
    db.refresh(obj)
    return obj


@router.put("/stock-alerts/{ident}", response_model=StockAlertOut)
def update_stock_alert(
    ident: int,
    payload: StockAlertUpdate,
    db: Session = Depends(get_db),
    user: User = Depends(require_perm("magasin.stock_alert.modify")),
):
    cid = _company_id(user)
    obj = _get_or_404(db, StockAlert, ident, "Seuils et alertes rupture")
    if obj.company_id != cid:
        raise HTTPException(403, "Acces refuse.")
    _apply(payload.model_dump(exclude_unset=True), obj)
    db.commit()
    db.refresh(obj)
    return obj


@router.delete("/stock-alerts/{ident}", response_model=StockAlertOut)
def delete_stock_alert(
    ident: int,
    db: Session = Depends(get_db),
    user: User = Depends(require_perm("magasin.stock_alert.modify")),
):
    cid = _company_id(user)
    obj = _get_or_404(db, StockAlert, ident, "Seuils et alertes rupture")
    if obj.company_id != cid:
        raise HTTPException(403, "Acces refuse.")
    obj.is_active = False
    db.commit()
    db.refresh(obj)
    return obj


# ─── Peremption / FEFO ─────────────────────────────────────────────────

@router.get("/expiry-records", response_model=List[ExpiryRecordOut])
def list_expiry_tracking(statut: Optional[str] = None, db: Session = Depends(get_db),
    user: User = Depends(require_perm("magasin.expiry_tracking.read")),
):
    cid = _company_id(user)
    return _scoped_list(db, ExpiryRecord, cid, {"statut": statut})


@router.post("/expiry-records", response_model=ExpiryRecordOut, status_code=201)
def create_expiry_tracking(
    payload: ExpiryRecordCreate,
    db: Session = Depends(get_db),
    user: User = Depends(require_perm("magasin.expiry_tracking.create")),
):
    cid = _company_id(user)
    data = payload.model_dump(exclude_unset=True)
    _check_unique(db, ExpiryRecord, "numero_lot", data.get("numero_lot"), "numero_lot", cid)
    obj = ExpiryRecord(company_id=cid)
    _apply(data, obj)
    db.add(obj)
    db.commit()
    db.refresh(obj)
    return obj


@router.put("/expiry-records/{ident}", response_model=ExpiryRecordOut)
def update_expiry_tracking(
    ident: int,
    payload: ExpiryRecordUpdate,
    db: Session = Depends(get_db),
    user: User = Depends(require_perm("magasin.expiry_tracking.modify")),
):
    cid = _company_id(user)
    obj = _get_or_404(db, ExpiryRecord, ident, "Peremption / FEFO")
    if obj.company_id != cid:
        raise HTTPException(403, "Acces refuse.")
    _apply(payload.model_dump(exclude_unset=True), obj)
    db.commit()
    db.refresh(obj)
    return obj


@router.delete("/expiry-records/{ident}", response_model=ExpiryRecordOut)
def delete_expiry_tracking(
    ident: int,
    db: Session = Depends(get_db),
    user: User = Depends(require_perm("magasin.expiry_tracking.modify")),
):
    cid = _company_id(user)
    obj = _get_or_404(db, ExpiryRecord, ident, "Peremption / FEFO")
    if obj.company_id != cid:
        raise HTTPException(403, "Acces refuse.")
    obj.is_active = False
    db.commit()
    db.refresh(obj)
    return obj


# ─── Tracabilite numeros serie ─────────────────────────────────────────────────

@router.get("/serial-numbers", response_model=List[SerialNumberOut])
def list_serial_tracking(statut: Optional[str] = None, db: Session = Depends(get_db),
    user: User = Depends(require_perm("magasin.serial_tracking.read")),
):
    cid = _company_id(user)
    return _scoped_list(db, SerialNumber, cid, {"statut": statut})


@router.post("/serial-numbers", response_model=SerialNumberOut, status_code=201)
def create_serial_tracking(
    payload: SerialNumberCreate,
    db: Session = Depends(get_db),
    user: User = Depends(require_perm("magasin.serial_tracking.create")),
):
    cid = _company_id(user)
    data = payload.model_dump(exclude_unset=True)
    _check_unique(db, SerialNumber, "numero_serial", data.get("numero_serial"), "numero_serial", cid)
    obj = SerialNumber(company_id=cid)
    _apply(data, obj)
    db.add(obj)
    db.commit()
    db.refresh(obj)
    return obj


@router.put("/serial-numbers/{ident}", response_model=SerialNumberOut)
def update_serial_tracking(
    ident: int,
    payload: SerialNumberUpdate,
    db: Session = Depends(get_db),
    user: User = Depends(require_perm("magasin.serial_tracking.modify")),
):
    cid = _company_id(user)
    obj = _get_or_404(db, SerialNumber, ident, "Tracabilite numeros serie")
    if obj.company_id != cid:
        raise HTTPException(403, "Acces refuse.")
    _apply(payload.model_dump(exclude_unset=True), obj)
    db.commit()
    db.refresh(obj)
    return obj


@router.delete("/serial-numbers/{ident}", response_model=SerialNumberOut)
def delete_serial_tracking(
    ident: int,
    db: Session = Depends(get_db),
    user: User = Depends(require_perm("magasin.serial_tracking.modify")),
):
    cid = _company_id(user)
    obj = _get_or_404(db, SerialNumber, ident, "Tracabilite numeros serie")
    if obj.company_id != cid:
        raise HTTPException(403, "Acces refuse.")
    obj.is_active = False
    db.commit()
    db.refresh(obj)
    return obj


# ─── Unites de conditionnement ─────────────────────────────────────────────────

@router.get("/packing-units", response_model=List[PackingUnitOut])
def list_packing_unit(db: Session = Depends(get_db),
    user: User = Depends(require_perm("magasin.packing_unit.read")),
):
    cid = _company_id(user)
    return _scoped_list(db, PackingUnit, cid)


@router.post("/packing-units", response_model=PackingUnitOut, status_code=201)
def create_packing_unit(
    payload: PackingUnitCreate,
    db: Session = Depends(get_db),
    user: User = Depends(require_perm("magasin.packing_unit.create")),
):
    cid = _company_id(user)
    data = payload.model_dump(exclude_unset=True)
    _check_unique(db, PackingUnit, "code_uc", data.get("code_uc"), "code_uc", cid)
    obj = PackingUnit(company_id=cid)
    _apply(data, obj)
    db.add(obj)
    db.commit()
    db.refresh(obj)
    return obj


@router.put("/packing-units/{ident}", response_model=PackingUnitOut)
def update_packing_unit(
    ident: int,
    payload: PackingUnitUpdate,
    db: Session = Depends(get_db),
    user: User = Depends(require_perm("magasin.packing_unit.modify")),
):
    cid = _company_id(user)
    obj = _get_or_404(db, PackingUnit, ident, "Unites de conditionnement")
    if obj.company_id != cid:
        raise HTTPException(403, "Acces refuse.")
    _apply(payload.model_dump(exclude_unset=True), obj)
    db.commit()
    db.refresh(obj)
    return obj


@router.delete("/packing-units/{ident}", response_model=PackingUnitOut)
def delete_packing_unit(
    ident: int,
    db: Session = Depends(get_db),
    user: User = Depends(require_perm("magasin.packing_unit.modify")),
):
    cid = _company_id(user)
    obj = _get_or_404(db, PackingUnit, ident, "Unites de conditionnement")
    if obj.company_id != cid:
        raise HTTPException(403, "Acces refuse.")
    obj.is_active = False
    db.commit()
    db.refresh(obj)
    return obj


# ─── Retours et avoirs stock ─────────────────────────────────────────────────

@router.get("/stock-returns", response_model=List[StockReturnOut])
def list_returns_management(statut: Optional[str] = None, db: Session = Depends(get_db),
    user: User = Depends(require_perm("magasin.returns_management.read")),
):
    cid = _company_id(user)
    return _scoped_list(db, StockReturn, cid, {"statut": statut})


@router.post("/stock-returns", response_model=StockReturnOut, status_code=201)
def create_returns_management(
    payload: StockReturnCreate,
    db: Session = Depends(get_db),
    user: User = Depends(require_perm("magasin.returns_management.create")),
):
    cid = _company_id(user)
    data = payload.model_dump(exclude_unset=True)
    _check_unique(db, StockReturn, "numero_retour", data.get("numero_retour"), "numero_retour", cid)
    obj = StockReturn(company_id=cid)
    _apply(data, obj)
    db.add(obj)
    db.commit()
    db.refresh(obj)
    return obj


@router.put("/stock-returns/{ident}", response_model=StockReturnOut)
def update_returns_management(
    ident: int,
    payload: StockReturnUpdate,
    db: Session = Depends(get_db),
    user: User = Depends(require_perm("magasin.returns_management.modify")),
):
    cid = _company_id(user)
    obj = _get_or_404(db, StockReturn, ident, "Retours et avoirs stock")
    if obj.company_id != cid:
        raise HTTPException(403, "Acces refuse.")
    _apply(payload.model_dump(exclude_unset=True), obj)
    db.commit()
    db.refresh(obj)
    return obj


@router.delete("/stock-returns/{ident}", response_model=StockReturnOut)
def delete_returns_management(
    ident: int,
    db: Session = Depends(get_db),
    user: User = Depends(require_perm("magasin.returns_management.modify")),
):
    cid = _company_id(user)
    obj = _get_or_404(db, StockReturn, ident, "Retours et avoirs stock")
    if obj.company_id != cid:
        raise HTTPException(403, "Acces refuse.")
    obj.is_active = False
    db.commit()
    db.refresh(obj)
    return obj


# ─── Stock en consignation ─────────────────────────────────────────────────

@router.get("/consignment-stocks", response_model=List[ConsignmentStockOut])
def list_consignment_stock(statut: Optional[str] = None, db: Session = Depends(get_db),
    user: User = Depends(require_perm("magasin.consignment_stock.read")),
):
    cid = _company_id(user)
    return _scoped_list(db, ConsignmentStock, cid, {"statut": statut})


@router.post("/consignment-stocks", response_model=ConsignmentStockOut, status_code=201)
def create_consignment_stock(
    payload: ConsignmentStockCreate,
    db: Session = Depends(get_db),
    user: User = Depends(require_perm("magasin.consignment_stock.create")),
):
    cid = _company_id(user)
    data = payload.model_dump(exclude_unset=True)
    _check_unique(db, ConsignmentStock, "reference", data.get("reference"), "reference", cid)
    obj = ConsignmentStock(company_id=cid)
    _apply(data, obj)
    db.add(obj)
    db.commit()
    db.refresh(obj)
    return obj


@router.put("/consignment-stocks/{ident}", response_model=ConsignmentStockOut)
def update_consignment_stock(
    ident: int,
    payload: ConsignmentStockUpdate,
    db: Session = Depends(get_db),
    user: User = Depends(require_perm("magasin.consignment_stock.modify")),
):
    cid = _company_id(user)
    obj = _get_or_404(db, ConsignmentStock, ident, "Stock en consignation")
    if obj.company_id != cid:
        raise HTTPException(403, "Acces refuse.")
    _apply(payload.model_dump(exclude_unset=True), obj)
    db.commit()
    db.refresh(obj)
    return obj


@router.delete("/consignment-stocks/{ident}", response_model=ConsignmentStockOut)
def delete_consignment_stock(
    ident: int,
    db: Session = Depends(get_db),
    user: User = Depends(require_perm("magasin.consignment_stock.modify")),
):
    cid = _company_id(user)
    obj = _get_or_404(db, ConsignmentStock, ident, "Stock en consignation")
    if obj.company_id != cid:
        raise HTTPException(403, "Acces refuse.")
    obj.is_active = False
    db.commit()
    db.refresh(obj)
    return obj


# ─── Valorisation du stock ─────────────────────────────────────────────────

@router.get("/stock-valuations", response_model=List[StockValuationOut])
def list_stock_valuation(db: Session = Depends(get_db),
    user: User = Depends(require_perm("magasin.stock_valuation.read")),
):
    cid = _company_id(user)
    return _scoped_list(db, StockValuation, cid)


@router.post("/stock-valuations", response_model=StockValuationOut, status_code=201)
def create_stock_valuation(
    payload: StockValuationCreate,
    db: Session = Depends(get_db),
    user: User = Depends(require_perm("magasin.stock_valuation.create")),
):
    cid = _company_id(user)
    data = payload.model_dump(exclude_unset=True)
    _check_unique(db, StockValuation, "reference", data.get("reference"), "reference", cid)
    obj = StockValuation(company_id=cid)
    _apply(data, obj)
    db.add(obj)
    db.commit()
    db.refresh(obj)
    return obj


@router.put("/stock-valuations/{ident}", response_model=StockValuationOut)
def update_stock_valuation(
    ident: int,
    payload: StockValuationUpdate,
    db: Session = Depends(get_db),
    user: User = Depends(require_perm("magasin.stock_valuation.modify")),
):
    cid = _company_id(user)
    obj = _get_or_404(db, StockValuation, ident, "Valorisation du stock")
    if obj.company_id != cid:
        raise HTTPException(403, "Acces refuse.")
    _apply(payload.model_dump(exclude_unset=True), obj)
    db.commit()
    db.refresh(obj)
    return obj


@router.delete("/stock-valuations/{ident}", response_model=StockValuationOut)
def delete_stock_valuation(
    ident: int,
    db: Session = Depends(get_db),
    user: User = Depends(require_perm("magasin.stock_valuation.modify")),
):
    cid = _company_id(user)
    obj = _get_or_404(db, StockValuation, ident, "Valorisation du stock")
    if obj.company_id != cid:
        raise HTTPException(403, "Acces refuse.")
    obj.is_active = False
    db.commit()
    db.refresh(obj)
    return obj


# ─── KPIs magasin ─────────────────────────────────────────────────

@router.get("/wms-kpis", response_model=List[WmsKpiOut])
def list_wms_analytics(db: Session = Depends(get_db),
    user: User = Depends(require_perm("magasin.wms_analytics.read")),
):
    cid = _company_id(user)
    return _scoped_list(db, WmsKpi, cid)


@router.post("/wms-kpis", response_model=WmsKpiOut, status_code=201)
def create_wms_analytics(
    payload: WmsKpiCreate,
    db: Session = Depends(get_db),
    user: User = Depends(require_perm("magasin.wms_analytics.create")),
):
    cid = _company_id(user)
    data = payload.model_dump(exclude_unset=True)
    _check_unique(db, WmsKpi, "reference", data.get("reference"), "reference", cid)
    obj = WmsKpi(company_id=cid)
    _apply(data, obj)
    db.add(obj)
    db.commit()
    db.refresh(obj)
    return obj


@router.put("/wms-kpis/{ident}", response_model=WmsKpiOut)
def update_wms_analytics(
    ident: int,
    payload: WmsKpiUpdate,
    db: Session = Depends(get_db),
    user: User = Depends(require_perm("magasin.wms_analytics.modify")),
):
    cid = _company_id(user)
    obj = _get_or_404(db, WmsKpi, ident, "KPIs magasin")
    if obj.company_id != cid:
        raise HTTPException(403, "Acces refuse.")
    _apply(payload.model_dump(exclude_unset=True), obj)
    db.commit()
    db.refresh(obj)
    return obj


@router.delete("/wms-kpis/{ident}", response_model=WmsKpiOut)
def delete_wms_analytics(
    ident: int,
    db: Session = Depends(get_db),
    user: User = Depends(require_perm("magasin.wms_analytics.modify")),
):
    cid = _company_id(user)
    obj = _get_or_404(db, WmsKpi, ident, "KPIs magasin")
    if obj.company_id != cid:
        raise HTTPException(403, "Acces refuse.")
    obj.is_active = False
    db.commit()
    db.refresh(obj)
    return obj

