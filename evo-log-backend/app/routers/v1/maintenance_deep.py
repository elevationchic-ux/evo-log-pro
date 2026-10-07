"""Routeur CRUD genere pour maintenance-industrielle (expansion wave 6)."""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session
from typing import Optional, List

from app.core.database import get_db
from app.core.permissions import require_perm
from app.models.user import User
from app.models.maintenance_deep import (
    TechnicalAsset,
    AssetComponent,
    SparePartCatalog,
    BillOfMaterial,
    SerializedPart,
    PartInventory,
    PartMovement,
    FailureMode,
    MaintenancePlan,
    MaintenanceTask,
    WorkOrder,
    AssetFailure,
    WorkOrderPart,
    WorkOrderLabour,
    WorkOrderTool,
    RootCauseAnalysis,
    OverhaulCampaign,
    LubricationSchedule,
    ConditionReading,
    Sensor,
    PredictiveModel,
    ReliabilityKpi,
    RegulatoryInspection,
    MaintenanceBudget,
    MaintenanceVendor,
)
from app.schemas.maintenance_deep import (
    TechnicalAssetCreate, TechnicalAssetUpdate, TechnicalAssetOut,
    AssetComponentCreate, AssetComponentUpdate, AssetComponentOut,
    SparePartCatalogCreate, SparePartCatalogUpdate, SparePartCatalogOut,
    BillOfMaterialCreate, BillOfMaterialUpdate, BillOfMaterialOut,
    SerializedPartCreate, SerializedPartUpdate, SerializedPartOut,
    PartInventoryCreate, PartInventoryUpdate, PartInventoryOut,
    PartMovementCreate, PartMovementUpdate, PartMovementOut,
    FailureModeCreate, FailureModeUpdate, FailureModeOut,
    MaintenancePlanCreate, MaintenancePlanUpdate, MaintenancePlanOut,
    MaintenanceTaskCreate, MaintenanceTaskUpdate, MaintenanceTaskOut,
    WorkOrderCreate, WorkOrderUpdate, WorkOrderOut,
    AssetFailureCreate, AssetFailureUpdate, AssetFailureOut,
    WorkOrderPartCreate, WorkOrderPartUpdate, WorkOrderPartOut,
    WorkOrderLabourCreate, WorkOrderLabourUpdate, WorkOrderLabourOut,
    WorkOrderToolCreate, WorkOrderToolUpdate, WorkOrderToolOut,
    RootCauseAnalysisCreate, RootCauseAnalysisUpdate, RootCauseAnalysisOut,
    OverhaulCampaignCreate, OverhaulCampaignUpdate, OverhaulCampaignOut,
    LubricationScheduleCreate, LubricationScheduleUpdate, LubricationScheduleOut,
    ConditionReadingCreate, ConditionReadingUpdate, ConditionReadingOut,
    SensorCreate, SensorUpdate, SensorOut,
    PredictiveModelCreate, PredictiveModelUpdate, PredictiveModelOut,
    ReliabilityKpiCreate, ReliabilityKpiUpdate, ReliabilityKpiOut,
    RegulatoryInspectionCreate, RegulatoryInspectionUpdate, RegulatoryInspectionOut,
    MaintenanceBudgetCreate, MaintenanceBudgetUpdate, MaintenanceBudgetOut,
    MaintenanceVendorCreate, MaintenanceVendorUpdate, MaintenanceVendorOut,
)

router = APIRouter(tags=["maintenance-industrielle (expansion)"])


# --- Helpers generiques ---------------------------------------------------

def _get_or_404(db: Session, model, ident: int, label: str):
    row = db.query(model).filter(model.id == ident).first()
    if not row:
        raise HTTPException(status_code=404, detail=f"{label} introuvable (id={ident})")
    return row


def _check_unique(db: Session, model, fields, data: dict, label: str, company_id: int, exclude_id=None):
    if not fields:
        return
    if any(data.get(f) is None for f in fields):
        return
    q = db.query(model).filter(model.company_id == company_id)
    for f in fields:
        q = q.filter(getattr(model, f) == data.get(f))
    if exclude_id is not None:
        q = q.filter(model.id != exclude_id)
    if q.first():
        human = ' / '.join(str(data.get(f)) for f in fields)
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=f"{label} '{human}' existe deja dans votre organisation.",
        )


def _commit(db: Session, obj, label: str):
    db.add(obj)
    try:
        db.commit()
    except IntegrityError as exc:
        db.rollback()
        msg = str(getattr(exc, 'orig', exc))
        if 'FOREIGN KEY' in msg.upper() or 'foreign key' in msg:
            raise HTTPException(422, detail=f"References invalides : un enregistrement lie ({label}) n'existe pas ou appartient a une autre organisation.")
        raise HTTPException(409, detail=f"Conflit d'integrite lors de l'enregistrement de {label}.")
    db.refresh(obj)
    return obj


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


# --- Nomenclatures ---------------------------------------------------------

@router.get("/nomenclatures", summary="Vocabulaire metier maintenance-industrielle")
def nomenclatures(user: User = Depends(require_perm("maintindustrielle.nomenclature.read"))):
    from app.models import maintenance_deep as _md
    import enum as _pyenum
    out = {}
    for name in dir(_md):
        obj = getattr(_md, name)
        if isinstance(obj, type) and issubclass(obj, _pyenum.Enum) and obj is not _pyenum.Enum:
            out[name.lower()] = [{"code": m.name, "valeur": m.value} for m in obj]
    return out


# --- Actif technique ---------------------------------------------------------

@router.get("/assets", response_model=List[TechnicalAssetOut])
def list_assets(statut: Optional[str] = None, db: Session = Depends(get_db),
    user: User = Depends(require_perm("maintindustrielle.assets.read")),
):
    cid = _company_id(user)
    return _scoped_list(db, TechnicalAsset, cid, {'statut': statut})


@router.post("/assets", response_model=TechnicalAssetOut, status_code=201)
def create_assets(
    payload: TechnicalAssetCreate,
    db: Session = Depends(get_db),
    user: User = Depends(require_perm("maintindustrielle.assets.create")),
):
    cid = _company_id(user)
    data = payload.model_dump(exclude_unset=True)
    _check_unique(db, TechnicalAsset, ['tag_actif'], data, "Actif technique", cid)
    obj = TechnicalAsset(company_id=cid)
    _apply(data, obj)
    return _commit(db, obj, "Actif technique")


@router.put("/assets/{ident}", response_model=TechnicalAssetOut)
def update_assets(
    ident: int,
    payload: TechnicalAssetUpdate,
    db: Session = Depends(get_db),
    user: User = Depends(require_perm("maintindustrielle.assets.modify")),
):
    cid = _company_id(user)
    obj = _get_or_404(db, TechnicalAsset, ident, "Actif technique")
    if obj.company_id != cid:
        raise HTTPException(403, "Acces refuse.")
    upd = payload.model_dump(exclude_unset=True)
    _chk = {f: upd.get(f, getattr(obj, f)) for f in ['tag_actif']}
    _check_unique(db, TechnicalAsset, ['tag_actif'], _chk, "Actif technique", cid, exclude_id=ident)
    _apply(upd, obj)
    try:
        db.commit()
    except IntegrityError as exc:
        db.rollback()
        raise HTTPException(422, detail="Reference invalide ou conflit d'integrite.")
    db.refresh(obj)
    return obj


@router.delete("/assets/{ident}", response_model=TechnicalAssetOut)
def delete_assets(
    ident: int,
    db: Session = Depends(get_db),
    user: User = Depends(require_perm("maintindustrielle.assets.modify")),
):
    cid = _company_id(user)
    obj = _get_or_404(db, TechnicalAsset, ident, "Actif technique")
    if obj.company_id != cid:
        raise HTTPException(403, "Acces refuse.")
    obj.is_active = False
    db.commit()
    db.refresh(obj)
    return obj


# --- Composant ---------------------------------------------------------

@router.get("/components", response_model=List[AssetComponentOut])
def list_components(statut: Optional[str] = None, db: Session = Depends(get_db),
    user: User = Depends(require_perm("maintindustrielle.components.read")),
):
    cid = _company_id(user)
    return _scoped_list(db, AssetComponent, cid, {'statut': statut})


@router.post("/components", response_model=AssetComponentOut, status_code=201)
def create_components(
    payload: AssetComponentCreate,
    db: Session = Depends(get_db),
    user: User = Depends(require_perm("maintindustrielle.components.create")),
):
    cid = _company_id(user)
    data = payload.model_dump(exclude_unset=True)
    _check_unique(db, AssetComponent, ['code_composant'], data, "Composant", cid)
    obj = AssetComponent(company_id=cid)
    _apply(data, obj)
    return _commit(db, obj, "Composant")


@router.put("/components/{ident}", response_model=AssetComponentOut)
def update_components(
    ident: int,
    payload: AssetComponentUpdate,
    db: Session = Depends(get_db),
    user: User = Depends(require_perm("maintindustrielle.components.modify")),
):
    cid = _company_id(user)
    obj = _get_or_404(db, AssetComponent, ident, "Composant")
    if obj.company_id != cid:
        raise HTTPException(403, "Acces refuse.")
    upd = payload.model_dump(exclude_unset=True)
    _chk = {f: upd.get(f, getattr(obj, f)) for f in ['code_composant']}
    _check_unique(db, AssetComponent, ['code_composant'], _chk, "Composant", cid, exclude_id=ident)
    _apply(upd, obj)
    try:
        db.commit()
    except IntegrityError as exc:
        db.rollback()
        raise HTTPException(422, detail="Reference invalide ou conflit d'integrite.")
    db.refresh(obj)
    return obj


@router.delete("/components/{ident}", response_model=AssetComponentOut)
def delete_components(
    ident: int,
    db: Session = Depends(get_db),
    user: User = Depends(require_perm("maintindustrielle.components.modify")),
):
    cid = _company_id(user)
    obj = _get_or_404(db, AssetComponent, ident, "Composant")
    if obj.company_id != cid:
        raise HTTPException(403, "Acces refuse.")
    obj.is_active = False
    db.commit()
    db.refresh(obj)
    return obj


# --- Piece de rechange ---------------------------------------------------------

@router.get("/spare-parts", response_model=List[SparePartCatalogOut])
def list_spare_parts(db: Session = Depends(get_db),
    user: User = Depends(require_perm("maintindustrielle.spare_parts.read")),
):
    cid = _company_id(user)
    return _scoped_list(db, SparePartCatalog, cid)


@router.post("/spare-parts", response_model=SparePartCatalogOut, status_code=201)
def create_spare_parts(
    payload: SparePartCatalogCreate,
    db: Session = Depends(get_db),
    user: User = Depends(require_perm("maintindustrielle.spare_parts.create")),
):
    cid = _company_id(user)
    data = payload.model_dump(exclude_unset=True)
    _check_unique(db, SparePartCatalog, ['reference_interne'], data, "Piece de rechange", cid)
    obj = SparePartCatalog(company_id=cid)
    _apply(data, obj)
    return _commit(db, obj, "Piece de rechange")


@router.put("/spare-parts/{ident}", response_model=SparePartCatalogOut)
def update_spare_parts(
    ident: int,
    payload: SparePartCatalogUpdate,
    db: Session = Depends(get_db),
    user: User = Depends(require_perm("maintindustrielle.spare_parts.modify")),
):
    cid = _company_id(user)
    obj = _get_or_404(db, SparePartCatalog, ident, "Piece de rechange")
    if obj.company_id != cid:
        raise HTTPException(403, "Acces refuse.")
    upd = payload.model_dump(exclude_unset=True)
    _chk = {f: upd.get(f, getattr(obj, f)) for f in ['reference_interne']}
    _check_unique(db, SparePartCatalog, ['reference_interne'], _chk, "Piece de rechange", cid, exclude_id=ident)
    _apply(upd, obj)
    try:
        db.commit()
    except IntegrityError as exc:
        db.rollback()
        raise HTTPException(422, detail="Reference invalide ou conflit d'integrite.")
    db.refresh(obj)
    return obj


@router.delete("/spare-parts/{ident}", response_model=SparePartCatalogOut)
def delete_spare_parts(
    ident: int,
    db: Session = Depends(get_db),
    user: User = Depends(require_perm("maintindustrielle.spare_parts.modify")),
):
    cid = _company_id(user)
    obj = _get_or_404(db, SparePartCatalog, ident, "Piece de rechange")
    if obj.company_id != cid:
        raise HTTPException(403, "Acces refuse.")
    obj.is_active = False
    db.commit()
    db.refresh(obj)
    return obj


# --- Nomenclature BOM ---------------------------------------------------------

@router.get("/bill-of-material", response_model=List[BillOfMaterialOut])
def list_bill_of_material(db: Session = Depends(get_db),
    user: User = Depends(require_perm("maintindustrielle.bill_of_material.read")),
):
    cid = _company_id(user)
    return _scoped_list(db, BillOfMaterial, cid)


@router.post("/bill-of-material", response_model=BillOfMaterialOut, status_code=201)
def create_bill_of_material(
    payload: BillOfMaterialCreate,
    db: Session = Depends(get_db),
    user: User = Depends(require_perm("maintindustrielle.bill_of_material.create")),
):
    cid = _company_id(user)
    data = payload.model_dump(exclude_unset=True)
    _check_unique(db, BillOfMaterial, ['position_index'], data, "Nomenclature BOM", cid)
    obj = BillOfMaterial(company_id=cid)
    _apply(data, obj)
    return _commit(db, obj, "Nomenclature BOM")


@router.put("/bill-of-material/{ident}", response_model=BillOfMaterialOut)
def update_bill_of_material(
    ident: int,
    payload: BillOfMaterialUpdate,
    db: Session = Depends(get_db),
    user: User = Depends(require_perm("maintindustrielle.bill_of_material.modify")),
):
    cid = _company_id(user)
    obj = _get_or_404(db, BillOfMaterial, ident, "Nomenclature BOM")
    if obj.company_id != cid:
        raise HTTPException(403, "Acces refuse.")
    upd = payload.model_dump(exclude_unset=True)
    _chk = {f: upd.get(f, getattr(obj, f)) for f in ['position_index']}
    _check_unique(db, BillOfMaterial, ['position_index'], _chk, "Nomenclature BOM", cid, exclude_id=ident)
    _apply(upd, obj)
    try:
        db.commit()
    except IntegrityError as exc:
        db.rollback()
        raise HTTPException(422, detail="Reference invalide ou conflit d'integrite.")
    db.refresh(obj)
    return obj


@router.delete("/bill-of-material/{ident}", response_model=BillOfMaterialOut)
def delete_bill_of_material(
    ident: int,
    db: Session = Depends(get_db),
    user: User = Depends(require_perm("maintindustrielle.bill_of_material.modify")),
):
    cid = _company_id(user)
    obj = _get_or_404(db, BillOfMaterial, ident, "Nomenclature BOM")
    if obj.company_id != cid:
        raise HTTPException(403, "Acces refuse.")
    obj.is_active = False
    db.commit()
    db.refresh(obj)
    return obj


# --- Piece serialisee (singleton) ---------------------------------------------------------

@router.get("/serialized-parts", response_model=List[SerializedPartOut])
def list_serialized_parts(statut: Optional[str] = None, db: Session = Depends(get_db),
    user: User = Depends(require_perm("maintindustrielle.serialized_parts.read")),
):
    cid = _company_id(user)
    return _scoped_list(db, SerializedPart, cid, {'statut': statut})


@router.post("/serialized-parts", response_model=SerializedPartOut, status_code=201)
def create_serialized_parts(
    payload: SerializedPartCreate,
    db: Session = Depends(get_db),
    user: User = Depends(require_perm("maintindustrielle.serialized_parts.create")),
):
    cid = _company_id(user)
    data = payload.model_dump(exclude_unset=True)
    _check_unique(db, SerializedPart, ['numero_serial'], data, "Piece serialisee (singleton)", cid)
    obj = SerializedPart(company_id=cid)
    _apply(data, obj)
    return _commit(db, obj, "Piece serialisee (singleton)")


@router.put("/serialized-parts/{ident}", response_model=SerializedPartOut)
def update_serialized_parts(
    ident: int,
    payload: SerializedPartUpdate,
    db: Session = Depends(get_db),
    user: User = Depends(require_perm("maintindustrielle.serialized_parts.modify")),
):
    cid = _company_id(user)
    obj = _get_or_404(db, SerializedPart, ident, "Piece serialisee (singleton)")
    if obj.company_id != cid:
        raise HTTPException(403, "Acces refuse.")
    upd = payload.model_dump(exclude_unset=True)
    _chk = {f: upd.get(f, getattr(obj, f)) for f in ['numero_serial']}
    _check_unique(db, SerializedPart, ['numero_serial'], _chk, "Piece serialisee (singleton)", cid, exclude_id=ident)
    _apply(upd, obj)
    try:
        db.commit()
    except IntegrityError as exc:
        db.rollback()
        raise HTTPException(422, detail="Reference invalide ou conflit d'integrite.")
    db.refresh(obj)
    return obj


@router.delete("/serialized-parts/{ident}", response_model=SerializedPartOut)
def delete_serialized_parts(
    ident: int,
    db: Session = Depends(get_db),
    user: User = Depends(require_perm("maintindustrielle.serialized_parts.modify")),
):
    cid = _company_id(user)
    obj = _get_or_404(db, SerializedPart, ident, "Piece serialisee (singleton)")
    if obj.company_id != cid:
        raise HTTPException(403, "Acces refuse.")
    obj.is_active = False
    db.commit()
    db.refresh(obj)
    return obj


# --- Stock piece ---------------------------------------------------------

@router.get("/inventory", response_model=List[PartInventoryOut])
def list_inventory(db: Session = Depends(get_db),
    user: User = Depends(require_perm("maintindustrielle.inventory.read")),
):
    cid = _company_id(user)
    return _scoped_list(db, PartInventory, cid)


@router.post("/inventory", response_model=PartInventoryOut, status_code=201)
def create_inventory(
    payload: PartInventoryCreate,
    db: Session = Depends(get_db),
    user: User = Depends(require_perm("maintindustrielle.inventory.create")),
):
    cid = _company_id(user)
    data = payload.model_dump(exclude_unset=True)
    _check_unique(db, PartInventory, ['part_id'], data, "Stock piece", cid)
    obj = PartInventory(company_id=cid)
    _apply(data, obj)
    return _commit(db, obj, "Stock piece")


@router.put("/inventory/{ident}", response_model=PartInventoryOut)
def update_inventory(
    ident: int,
    payload: PartInventoryUpdate,
    db: Session = Depends(get_db),
    user: User = Depends(require_perm("maintindustrielle.inventory.modify")),
):
    cid = _company_id(user)
    obj = _get_or_404(db, PartInventory, ident, "Stock piece")
    if obj.company_id != cid:
        raise HTTPException(403, "Acces refuse.")
    upd = payload.model_dump(exclude_unset=True)
    _chk = {f: upd.get(f, getattr(obj, f)) for f in ['part_id']}
    _check_unique(db, PartInventory, ['part_id'], _chk, "Stock piece", cid, exclude_id=ident)
    _apply(upd, obj)
    try:
        db.commit()
    except IntegrityError as exc:
        db.rollback()
        raise HTTPException(422, detail="Reference invalide ou conflit d'integrite.")
    db.refresh(obj)
    return obj


@router.delete("/inventory/{ident}", response_model=PartInventoryOut)
def delete_inventory(
    ident: int,
    db: Session = Depends(get_db),
    user: User = Depends(require_perm("maintindustrielle.inventory.modify")),
):
    cid = _company_id(user)
    obj = _get_or_404(db, PartInventory, ident, "Stock piece")
    if obj.company_id != cid:
        raise HTTPException(403, "Acces refuse.")
    obj.is_active = False
    db.commit()
    db.refresh(obj)
    return obj


# --- Mouvement piece ---------------------------------------------------------

@router.get("/movements", response_model=List[PartMovementOut])
def list_movements(db: Session = Depends(get_db),
    user: User = Depends(require_perm("maintindustrielle.movements.read")),
):
    cid = _company_id(user)
    return _scoped_list(db, PartMovement, cid)


@router.post("/movements", response_model=PartMovementOut, status_code=201)
def create_movements(
    payload: PartMovementCreate,
    db: Session = Depends(get_db),
    user: User = Depends(require_perm("maintindustrielle.movements.create")),
):
    cid = _company_id(user)
    data = payload.model_dump(exclude_unset=True)
    _check_unique(db, PartMovement, ['reference_mouvement'], data, "Mouvement piece", cid)
    obj = PartMovement(company_id=cid)
    _apply(data, obj)
    return _commit(db, obj, "Mouvement piece")


@router.put("/movements/{ident}", response_model=PartMovementOut)
def update_movements(
    ident: int,
    payload: PartMovementUpdate,
    db: Session = Depends(get_db),
    user: User = Depends(require_perm("maintindustrielle.movements.modify")),
):
    cid = _company_id(user)
    obj = _get_or_404(db, PartMovement, ident, "Mouvement piece")
    if obj.company_id != cid:
        raise HTTPException(403, "Acces refuse.")
    upd = payload.model_dump(exclude_unset=True)
    _chk = {f: upd.get(f, getattr(obj, f)) for f in ['reference_mouvement']}
    _check_unique(db, PartMovement, ['reference_mouvement'], _chk, "Mouvement piece", cid, exclude_id=ident)
    _apply(upd, obj)
    try:
        db.commit()
    except IntegrityError as exc:
        db.rollback()
        raise HTTPException(422, detail="Reference invalide ou conflit d'integrite.")
    db.refresh(obj)
    return obj


@router.delete("/movements/{ident}", response_model=PartMovementOut)
def delete_movements(
    ident: int,
    db: Session = Depends(get_db),
    user: User = Depends(require_perm("maintindustrielle.movements.modify")),
):
    cid = _company_id(user)
    obj = _get_or_404(db, PartMovement, ident, "Mouvement piece")
    if obj.company_id != cid:
        raise HTTPException(403, "Acces refuse.")
    obj.is_active = False
    db.commit()
    db.refresh(obj)
    return obj


# --- Mode de defaillance (FMEA) ---------------------------------------------------------

@router.get("/failure-modes", response_model=List[FailureModeOut])
def list_failure_modes(statut: Optional[str] = None, db: Session = Depends(get_db),
    user: User = Depends(require_perm("maintindustrielle.failure_modes.read")),
):
    cid = _company_id(user)
    return _scoped_list(db, FailureMode, cid, {'statut': statut})


@router.post("/failure-modes", response_model=FailureModeOut, status_code=201)
def create_failure_modes(
    payload: FailureModeCreate,
    db: Session = Depends(get_db),
    user: User = Depends(require_perm("maintindustrielle.failure_modes.create")),
):
    cid = _company_id(user)
    data = payload.model_dump(exclude_unset=True)
    _check_unique(db, FailureMode, ['code_fmea'], data, "Mode de defaillance (FMEA)", cid)
    obj = FailureMode(company_id=cid)
    _apply(data, obj)
    return _commit(db, obj, "Mode de defaillance (FMEA)")


@router.put("/failure-modes/{ident}", response_model=FailureModeOut)
def update_failure_modes(
    ident: int,
    payload: FailureModeUpdate,
    db: Session = Depends(get_db),
    user: User = Depends(require_perm("maintindustrielle.failure_modes.modify")),
):
    cid = _company_id(user)
    obj = _get_or_404(db, FailureMode, ident, "Mode de defaillance (FMEA)")
    if obj.company_id != cid:
        raise HTTPException(403, "Acces refuse.")
    upd = payload.model_dump(exclude_unset=True)
    _chk = {f: upd.get(f, getattr(obj, f)) for f in ['code_fmea']}
    _check_unique(db, FailureMode, ['code_fmea'], _chk, "Mode de defaillance (FMEA)", cid, exclude_id=ident)
    _apply(upd, obj)
    try:
        db.commit()
    except IntegrityError as exc:
        db.rollback()
        raise HTTPException(422, detail="Reference invalide ou conflit d'integrite.")
    db.refresh(obj)
    return obj


@router.delete("/failure-modes/{ident}", response_model=FailureModeOut)
def delete_failure_modes(
    ident: int,
    db: Session = Depends(get_db),
    user: User = Depends(require_perm("maintindustrielle.failure_modes.modify")),
):
    cid = _company_id(user)
    obj = _get_or_404(db, FailureMode, ident, "Mode de defaillance (FMEA)")
    if obj.company_id != cid:
        raise HTTPException(403, "Acces refuse.")
    obj.is_active = False
    db.commit()
    db.refresh(obj)
    return obj


# --- Plan de maintenance ---------------------------------------------------------

@router.get("/plans", response_model=List[MaintenancePlanOut])
def list_plans(statut: Optional[str] = None, db: Session = Depends(get_db),
    user: User = Depends(require_perm("maintindustrielle.plans.read")),
):
    cid = _company_id(user)
    return _scoped_list(db, MaintenancePlan, cid, {'statut': statut})


@router.post("/plans", response_model=MaintenancePlanOut, status_code=201)
def create_plans(
    payload: MaintenancePlanCreate,
    db: Session = Depends(get_db),
    user: User = Depends(require_perm("maintindustrielle.plans.create")),
):
    cid = _company_id(user)
    data = payload.model_dump(exclude_unset=True)
    _check_unique(db, MaintenancePlan, ['code_plan'], data, "Plan de maintenance", cid)
    obj = MaintenancePlan(company_id=cid)
    _apply(data, obj)
    return _commit(db, obj, "Plan de maintenance")


@router.put("/plans/{ident}", response_model=MaintenancePlanOut)
def update_plans(
    ident: int,
    payload: MaintenancePlanUpdate,
    db: Session = Depends(get_db),
    user: User = Depends(require_perm("maintindustrielle.plans.modify")),
):
    cid = _company_id(user)
    obj = _get_or_404(db, MaintenancePlan, ident, "Plan de maintenance")
    if obj.company_id != cid:
        raise HTTPException(403, "Acces refuse.")
    upd = payload.model_dump(exclude_unset=True)
    _chk = {f: upd.get(f, getattr(obj, f)) for f in ['code_plan']}
    _check_unique(db, MaintenancePlan, ['code_plan'], _chk, "Plan de maintenance", cid, exclude_id=ident)
    _apply(upd, obj)
    try:
        db.commit()
    except IntegrityError as exc:
        db.rollback()
        raise HTTPException(422, detail="Reference invalide ou conflit d'integrite.")
    db.refresh(obj)
    return obj


@router.delete("/plans/{ident}", response_model=MaintenancePlanOut)
def delete_plans(
    ident: int,
    db: Session = Depends(get_db),
    user: User = Depends(require_perm("maintindustrielle.plans.modify")),
):
    cid = _company_id(user)
    obj = _get_or_404(db, MaintenancePlan, ident, "Plan de maintenance")
    if obj.company_id != cid:
        raise HTTPException(403, "Acces refuse.")
    obj.is_active = False
    db.commit()
    db.refresh(obj)
    return obj


# --- Tache de maintenance ---------------------------------------------------------

@router.get("/tasks", response_model=List[MaintenanceTaskOut])
def list_tasks(db: Session = Depends(get_db),
    user: User = Depends(require_perm("maintindustrielle.tasks.read")),
):
    cid = _company_id(user)
    return _scoped_list(db, MaintenanceTask, cid)


@router.post("/tasks", response_model=MaintenanceTaskOut, status_code=201)
def create_tasks(
    payload: MaintenanceTaskCreate,
    db: Session = Depends(get_db),
    user: User = Depends(require_perm("maintindustrielle.tasks.create")),
):
    cid = _company_id(user)
    data = payload.model_dump(exclude_unset=True)
    _check_unique(db, MaintenanceTask, ['code_tache'], data, "Tache de maintenance", cid)
    obj = MaintenanceTask(company_id=cid)
    _apply(data, obj)
    return _commit(db, obj, "Tache de maintenance")


@router.put("/tasks/{ident}", response_model=MaintenanceTaskOut)
def update_tasks(
    ident: int,
    payload: MaintenanceTaskUpdate,
    db: Session = Depends(get_db),
    user: User = Depends(require_perm("maintindustrielle.tasks.modify")),
):
    cid = _company_id(user)
    obj = _get_or_404(db, MaintenanceTask, ident, "Tache de maintenance")
    if obj.company_id != cid:
        raise HTTPException(403, "Acces refuse.")
    upd = payload.model_dump(exclude_unset=True)
    _chk = {f: upd.get(f, getattr(obj, f)) for f in ['code_tache']}
    _check_unique(db, MaintenanceTask, ['code_tache'], _chk, "Tache de maintenance", cid, exclude_id=ident)
    _apply(upd, obj)
    try:
        db.commit()
    except IntegrityError as exc:
        db.rollback()
        raise HTTPException(422, detail="Reference invalide ou conflit d'integrite.")
    db.refresh(obj)
    return obj


@router.delete("/tasks/{ident}", response_model=MaintenanceTaskOut)
def delete_tasks(
    ident: int,
    db: Session = Depends(get_db),
    user: User = Depends(require_perm("maintindustrielle.tasks.modify")),
):
    cid = _company_id(user)
    obj = _get_or_404(db, MaintenanceTask, ident, "Tache de maintenance")
    if obj.company_id != cid:
        raise HTTPException(403, "Acces refuse.")
    obj.is_active = False
    db.commit()
    db.refresh(obj)
    return obj


# --- Ordre de travail ---------------------------------------------------------

@router.get("/work-orders", response_model=List[WorkOrderOut])
def list_work_orders(statut: Optional[str] = None, db: Session = Depends(get_db),
    user: User = Depends(require_perm("maintindustrielle.work_orders.read")),
):
    cid = _company_id(user)
    return _scoped_list(db, WorkOrder, cid, {'statut': statut})


@router.post("/work-orders", response_model=WorkOrderOut, status_code=201)
def create_work_orders(
    payload: WorkOrderCreate,
    db: Session = Depends(get_db),
    user: User = Depends(require_perm("maintindustrielle.work_orders.create")),
):
    cid = _company_id(user)
    data = payload.model_dump(exclude_unset=True)
    _check_unique(db, WorkOrder, ['numero_ot'], data, "Ordre de travail", cid)
    obj = WorkOrder(company_id=cid)
    _apply(data, obj)
    return _commit(db, obj, "Ordre de travail")


@router.put("/work-orders/{ident}", response_model=WorkOrderOut)
def update_work_orders(
    ident: int,
    payload: WorkOrderUpdate,
    db: Session = Depends(get_db),
    user: User = Depends(require_perm("maintindustrielle.work_orders.modify")),
):
    cid = _company_id(user)
    obj = _get_or_404(db, WorkOrder, ident, "Ordre de travail")
    if obj.company_id != cid:
        raise HTTPException(403, "Acces refuse.")
    upd = payload.model_dump(exclude_unset=True)
    _chk = {f: upd.get(f, getattr(obj, f)) for f in ['numero_ot']}
    _check_unique(db, WorkOrder, ['numero_ot'], _chk, "Ordre de travail", cid, exclude_id=ident)
    _apply(upd, obj)
    try:
        db.commit()
    except IntegrityError as exc:
        db.rollback()
        raise HTTPException(422, detail="Reference invalide ou conflit d'integrite.")
    db.refresh(obj)
    return obj


@router.delete("/work-orders/{ident}", response_model=WorkOrderOut)
def delete_work_orders(
    ident: int,
    db: Session = Depends(get_db),
    user: User = Depends(require_perm("maintindustrielle.work_orders.modify")),
):
    cid = _company_id(user)
    obj = _get_or_404(db, WorkOrder, ident, "Ordre de travail")
    if obj.company_id != cid:
        raise HTTPException(403, "Acces refuse.")
    obj.is_active = False
    db.commit()
    db.refresh(obj)
    return obj


# --- Panne actif ---------------------------------------------------------

@router.get("/asset-failures", response_model=List[AssetFailureOut])
def list_asset_failures(statut: Optional[str] = None, db: Session = Depends(get_db),
    user: User = Depends(require_perm("maintindustrielle.asset_failures.read")),
):
    cid = _company_id(user)
    return _scoped_list(db, AssetFailure, cid, {'statut': statut})


@router.post("/asset-failures", response_model=AssetFailureOut, status_code=201)
def create_asset_failures(
    payload: AssetFailureCreate,
    db: Session = Depends(get_db),
    user: User = Depends(require_perm("maintindustrielle.asset_failures.create")),
):
    cid = _company_id(user)
    data = payload.model_dump(exclude_unset=True)
    _check_unique(db, AssetFailure, ['reference_defaillance'], data, "Panne actif", cid)
    obj = AssetFailure(company_id=cid)
    _apply(data, obj)
    return _commit(db, obj, "Panne actif")


@router.put("/asset-failures/{ident}", response_model=AssetFailureOut)
def update_asset_failures(
    ident: int,
    payload: AssetFailureUpdate,
    db: Session = Depends(get_db),
    user: User = Depends(require_perm("maintindustrielle.asset_failures.modify")),
):
    cid = _company_id(user)
    obj = _get_or_404(db, AssetFailure, ident, "Panne actif")
    if obj.company_id != cid:
        raise HTTPException(403, "Acces refuse.")
    upd = payload.model_dump(exclude_unset=True)
    _chk = {f: upd.get(f, getattr(obj, f)) for f in ['reference_defaillance']}
    _check_unique(db, AssetFailure, ['reference_defaillance'], _chk, "Panne actif", cid, exclude_id=ident)
    _apply(upd, obj)
    try:
        db.commit()
    except IntegrityError as exc:
        db.rollback()
        raise HTTPException(422, detail="Reference invalide ou conflit d'integrite.")
    db.refresh(obj)
    return obj


@router.delete("/asset-failures/{ident}", response_model=AssetFailureOut)
def delete_asset_failures(
    ident: int,
    db: Session = Depends(get_db),
    user: User = Depends(require_perm("maintindustrielle.asset_failures.modify")),
):
    cid = _company_id(user)
    obj = _get_or_404(db, AssetFailure, ident, "Panne actif")
    if obj.company_id != cid:
        raise HTTPException(403, "Acces refuse.")
    obj.is_active = False
    db.commit()
    db.refresh(obj)
    return obj


# --- OT - pieces ---------------------------------------------------------

@router.get("/wo-parts", response_model=List[WorkOrderPartOut])
def list_wo_parts(db: Session = Depends(get_db),
    user: User = Depends(require_perm("maintindustrielle.wo_parts.read")),
):
    cid = _company_id(user)
    return _scoped_list(db, WorkOrderPart, cid)


@router.post("/wo-parts", response_model=WorkOrderPartOut, status_code=201)
def create_wo_parts(
    payload: WorkOrderPartCreate,
    db: Session = Depends(get_db),
    user: User = Depends(require_perm("maintindustrielle.wo_parts.create")),
):
    cid = _company_id(user)
    data = payload.model_dump(exclude_unset=True)
    _check_unique(db, WorkOrderPart, ['work_order_id', 'part_id'], data, "OT - pieces", cid)
    obj = WorkOrderPart(company_id=cid)
    _apply(data, obj)
    return _commit(db, obj, "OT - pieces")


@router.put("/wo-parts/{ident}", response_model=WorkOrderPartOut)
def update_wo_parts(
    ident: int,
    payload: WorkOrderPartUpdate,
    db: Session = Depends(get_db),
    user: User = Depends(require_perm("maintindustrielle.wo_parts.modify")),
):
    cid = _company_id(user)
    obj = _get_or_404(db, WorkOrderPart, ident, "OT - pieces")
    if obj.company_id != cid:
        raise HTTPException(403, "Acces refuse.")
    upd = payload.model_dump(exclude_unset=True)
    _chk = {f: upd.get(f, getattr(obj, f)) for f in ['work_order_id', 'part_id']}
    _check_unique(db, WorkOrderPart, ['work_order_id', 'part_id'], _chk, "OT - pieces", cid, exclude_id=ident)
    _apply(upd, obj)
    try:
        db.commit()
    except IntegrityError as exc:
        db.rollback()
        raise HTTPException(422, detail="Reference invalide ou conflit d'integrite.")
    db.refresh(obj)
    return obj


@router.delete("/wo-parts/{ident}", response_model=WorkOrderPartOut)
def delete_wo_parts(
    ident: int,
    db: Session = Depends(get_db),
    user: User = Depends(require_perm("maintindustrielle.wo_parts.modify")),
):
    cid = _company_id(user)
    obj = _get_or_404(db, WorkOrderPart, ident, "OT - pieces")
    if obj.company_id != cid:
        raise HTTPException(403, "Acces refuse.")
    obj.is_active = False
    db.commit()
    db.refresh(obj)
    return obj


# --- OT - main d'oeuvre ---------------------------------------------------------

@router.get("/wo-labours", response_model=List[WorkOrderLabourOut])
def list_wo_labours(statut: Optional[str] = None, db: Session = Depends(get_db),
    user: User = Depends(require_perm("maintindustrielle.wo_labours.read")),
):
    cid = _company_id(user)
    return _scoped_list(db, WorkOrderLabour, cid, {'statut': statut})


@router.post("/wo-labours", response_model=WorkOrderLabourOut, status_code=201)
def create_wo_labours(
    payload: WorkOrderLabourCreate,
    db: Session = Depends(get_db),
    user: User = Depends(require_perm("maintindustrielle.wo_labours.create")),
):
    cid = _company_id(user)
    data = payload.model_dump(exclude_unset=True)
    _check_unique(db, WorkOrderLabour, ['date_travail'], data, "OT - main d'oeuvre", cid)
    obj = WorkOrderLabour(company_id=cid)
    _apply(data, obj)
    return _commit(db, obj, "OT - main d'oeuvre")


@router.put("/wo-labours/{ident}", response_model=WorkOrderLabourOut)
def update_wo_labours(
    ident: int,
    payload: WorkOrderLabourUpdate,
    db: Session = Depends(get_db),
    user: User = Depends(require_perm("maintindustrielle.wo_labours.modify")),
):
    cid = _company_id(user)
    obj = _get_or_404(db, WorkOrderLabour, ident, "OT - main d'oeuvre")
    if obj.company_id != cid:
        raise HTTPException(403, "Acces refuse.")
    upd = payload.model_dump(exclude_unset=True)
    _chk = {f: upd.get(f, getattr(obj, f)) for f in ['date_travail']}
    _check_unique(db, WorkOrderLabour, ['date_travail'], _chk, "OT - main d'oeuvre", cid, exclude_id=ident)
    _apply(upd, obj)
    try:
        db.commit()
    except IntegrityError as exc:
        db.rollback()
        raise HTTPException(422, detail="Reference invalide ou conflit d'integrite.")
    db.refresh(obj)
    return obj


@router.delete("/wo-labours/{ident}", response_model=WorkOrderLabourOut)
def delete_wo_labours(
    ident: int,
    db: Session = Depends(get_db),
    user: User = Depends(require_perm("maintindustrielle.wo_labours.modify")),
):
    cid = _company_id(user)
    obj = _get_or_404(db, WorkOrderLabour, ident, "OT - main d'oeuvre")
    if obj.company_id != cid:
        raise HTTPException(403, "Acces refuse.")
    obj.is_active = False
    db.commit()
    db.refresh(obj)
    return obj


# --- OT - outillage ---------------------------------------------------------

@router.get("/wo-tools", response_model=List[WorkOrderToolOut])
def list_wo_tools(statut: Optional[str] = None, db: Session = Depends(get_db),
    user: User = Depends(require_perm("maintindustrielle.wo_tools.read")),
):
    cid = _company_id(user)
    return _scoped_list(db, WorkOrderTool, cid, {'statut': statut})


@router.post("/wo-tools", response_model=WorkOrderToolOut, status_code=201)
def create_wo_tools(
    payload: WorkOrderToolCreate,
    db: Session = Depends(get_db),
    user: User = Depends(require_perm("maintindustrielle.wo_tools.create")),
):
    cid = _company_id(user)
    data = payload.model_dump(exclude_unset=True)
    _check_unique(db, WorkOrderTool, ['reference_outillage'], data, "OT - outillage", cid)
    obj = WorkOrderTool(company_id=cid)
    _apply(data, obj)
    return _commit(db, obj, "OT - outillage")


@router.put("/wo-tools/{ident}", response_model=WorkOrderToolOut)
def update_wo_tools(
    ident: int,
    payload: WorkOrderToolUpdate,
    db: Session = Depends(get_db),
    user: User = Depends(require_perm("maintindustrielle.wo_tools.modify")),
):
    cid = _company_id(user)
    obj = _get_or_404(db, WorkOrderTool, ident, "OT - outillage")
    if obj.company_id != cid:
        raise HTTPException(403, "Acces refuse.")
    upd = payload.model_dump(exclude_unset=True)
    _chk = {f: upd.get(f, getattr(obj, f)) for f in ['reference_outillage']}
    _check_unique(db, WorkOrderTool, ['reference_outillage'], _chk, "OT - outillage", cid, exclude_id=ident)
    _apply(upd, obj)
    try:
        db.commit()
    except IntegrityError as exc:
        db.rollback()
        raise HTTPException(422, detail="Reference invalide ou conflit d'integrite.")
    db.refresh(obj)
    return obj


@router.delete("/wo-tools/{ident}", response_model=WorkOrderToolOut)
def delete_wo_tools(
    ident: int,
    db: Session = Depends(get_db),
    user: User = Depends(require_perm("maintindustrielle.wo_tools.modify")),
):
    cid = _company_id(user)
    obj = _get_or_404(db, WorkOrderTool, ident, "OT - outillage")
    if obj.company_id != cid:
        raise HTTPException(403, "Acces refuse.")
    obj.is_active = False
    db.commit()
    db.refresh(obj)
    return obj


# --- Analyse cause racine ---------------------------------------------------------

@router.get("/root-causes", response_model=List[RootCauseAnalysisOut])
def list_root_causes(statut: Optional[str] = None, db: Session = Depends(get_db),
    user: User = Depends(require_perm("maintindustrielle.root_causes.read")),
):
    cid = _company_id(user)
    return _scoped_list(db, RootCauseAnalysis, cid, {'statut': statut})


@router.post("/root-causes", response_model=RootCauseAnalysisOut, status_code=201)
def create_root_causes(
    payload: RootCauseAnalysisCreate,
    db: Session = Depends(get_db),
    user: User = Depends(require_perm("maintindustrielle.root_causes.create")),
):
    cid = _company_id(user)
    data = payload.model_dump(exclude_unset=True)
    _check_unique(db, RootCauseAnalysis, ['reference_rca'], data, "Analyse cause racine", cid)
    obj = RootCauseAnalysis(company_id=cid)
    _apply(data, obj)
    return _commit(db, obj, "Analyse cause racine")


@router.put("/root-causes/{ident}", response_model=RootCauseAnalysisOut)
def update_root_causes(
    ident: int,
    payload: RootCauseAnalysisUpdate,
    db: Session = Depends(get_db),
    user: User = Depends(require_perm("maintindustrielle.root_causes.modify")),
):
    cid = _company_id(user)
    obj = _get_or_404(db, RootCauseAnalysis, ident, "Analyse cause racine")
    if obj.company_id != cid:
        raise HTTPException(403, "Acces refuse.")
    upd = payload.model_dump(exclude_unset=True)
    _chk = {f: upd.get(f, getattr(obj, f)) for f in ['reference_rca']}
    _check_unique(db, RootCauseAnalysis, ['reference_rca'], _chk, "Analyse cause racine", cid, exclude_id=ident)
    _apply(upd, obj)
    try:
        db.commit()
    except IntegrityError as exc:
        db.rollback()
        raise HTTPException(422, detail="Reference invalide ou conflit d'integrite.")
    db.refresh(obj)
    return obj


@router.delete("/root-causes/{ident}", response_model=RootCauseAnalysisOut)
def delete_root_causes(
    ident: int,
    db: Session = Depends(get_db),
    user: User = Depends(require_perm("maintindustrielle.root_causes.modify")),
):
    cid = _company_id(user)
    obj = _get_or_404(db, RootCauseAnalysis, ident, "Analyse cause racine")
    if obj.company_id != cid:
        raise HTTPException(403, "Acces refuse.")
    obj.is_active = False
    db.commit()
    db.refresh(obj)
    return obj


# --- Campagne revision ---------------------------------------------------------

@router.get("/overhauls", response_model=List[OverhaulCampaignOut])
def list_overhauls(statut: Optional[str] = None, db: Session = Depends(get_db),
    user: User = Depends(require_perm("maintindustrielle.overhauls.read")),
):
    cid = _company_id(user)
    return _scoped_list(db, OverhaulCampaign, cid, {'statut': statut})


@router.post("/overhauls", response_model=OverhaulCampaignOut, status_code=201)
def create_overhauls(
    payload: OverhaulCampaignCreate,
    db: Session = Depends(get_db),
    user: User = Depends(require_perm("maintindustrielle.overhauls.create")),
):
    cid = _company_id(user)
    data = payload.model_dump(exclude_unset=True)
    _check_unique(db, OverhaulCampaign, ['code_overhaul'], data, "Campagne revision", cid)
    obj = OverhaulCampaign(company_id=cid)
    _apply(data, obj)
    return _commit(db, obj, "Campagne revision")


@router.put("/overhauls/{ident}", response_model=OverhaulCampaignOut)
def update_overhauls(
    ident: int,
    payload: OverhaulCampaignUpdate,
    db: Session = Depends(get_db),
    user: User = Depends(require_perm("maintindustrielle.overhauls.modify")),
):
    cid = _company_id(user)
    obj = _get_or_404(db, OverhaulCampaign, ident, "Campagne revision")
    if obj.company_id != cid:
        raise HTTPException(403, "Acces refuse.")
    upd = payload.model_dump(exclude_unset=True)
    _chk = {f: upd.get(f, getattr(obj, f)) for f in ['code_overhaul']}
    _check_unique(db, OverhaulCampaign, ['code_overhaul'], _chk, "Campagne revision", cid, exclude_id=ident)
    _apply(upd, obj)
    try:
        db.commit()
    except IntegrityError as exc:
        db.rollback()
        raise HTTPException(422, detail="Reference invalide ou conflit d'integrite.")
    db.refresh(obj)
    return obj


@router.delete("/overhauls/{ident}", response_model=OverhaulCampaignOut)
def delete_overhauls(
    ident: int,
    db: Session = Depends(get_db),
    user: User = Depends(require_perm("maintindustrielle.overhauls.modify")),
):
    cid = _company_id(user)
    obj = _get_or_404(db, OverhaulCampaign, ident, "Campagne revision")
    if obj.company_id != cid:
        raise HTTPException(403, "Acces refuse.")
    obj.is_active = False
    db.commit()
    db.refresh(obj)
    return obj


# --- Plainte graissage ---------------------------------------------------------

@router.get("/lubrication", response_model=List[LubricationScheduleOut])
def list_lubrication(statut: Optional[str] = None, db: Session = Depends(get_db),
    user: User = Depends(require_perm("maintindustrielle.lubrication.read")),
):
    cid = _company_id(user)
    return _scoped_list(db, LubricationSchedule, cid, {'statut': statut})


@router.post("/lubrication", response_model=LubricationScheduleOut, status_code=201)
def create_lubrication(
    payload: LubricationScheduleCreate,
    db: Session = Depends(get_db),
    user: User = Depends(require_perm("maintindustrielle.lubrication.create")),
):
    cid = _company_id(user)
    data = payload.model_dump(exclude_unset=True)
    _check_unique(db, LubricationSchedule, ['point_lubrifiant'], data, "Plainte graissage", cid)
    obj = LubricationSchedule(company_id=cid)
    _apply(data, obj)
    return _commit(db, obj, "Plainte graissage")


@router.put("/lubrication/{ident}", response_model=LubricationScheduleOut)
def update_lubrication(
    ident: int,
    payload: LubricationScheduleUpdate,
    db: Session = Depends(get_db),
    user: User = Depends(require_perm("maintindustrielle.lubrication.modify")),
):
    cid = _company_id(user)
    obj = _get_or_404(db, LubricationSchedule, ident, "Plainte graissage")
    if obj.company_id != cid:
        raise HTTPException(403, "Acces refuse.")
    upd = payload.model_dump(exclude_unset=True)
    _chk = {f: upd.get(f, getattr(obj, f)) for f in ['point_lubrifiant']}
    _check_unique(db, LubricationSchedule, ['point_lubrifiant'], _chk, "Plainte graissage", cid, exclude_id=ident)
    _apply(upd, obj)
    try:
        db.commit()
    except IntegrityError as exc:
        db.rollback()
        raise HTTPException(422, detail="Reference invalide ou conflit d'integrite.")
    db.refresh(obj)
    return obj


@router.delete("/lubrication/{ident}", response_model=LubricationScheduleOut)
def delete_lubrication(
    ident: int,
    db: Session = Depends(get_db),
    user: User = Depends(require_perm("maintindustrielle.lubrication.modify")),
):
    cid = _company_id(user)
    obj = _get_or_404(db, LubricationSchedule, ident, "Plainte graissage")
    if obj.company_id != cid:
        raise HTTPException(403, "Acces refuse.")
    obj.is_active = False
    db.commit()
    db.refresh(obj)
    return obj


# --- Releu condition ---------------------------------------------------------

@router.get("/condition-readings", response_model=List[ConditionReadingOut])
def list_condition_readings(db: Session = Depends(get_db),
    user: User = Depends(require_perm("maintindustrielle.condition_readings.read")),
):
    cid = _company_id(user)
    return _scoped_list(db, ConditionReading, cid)


@router.post("/condition-readings", response_model=ConditionReadingOut, status_code=201)
def create_condition_readings(
    payload: ConditionReadingCreate,
    db: Session = Depends(get_db),
    user: User = Depends(require_perm("maintindustrielle.condition_readings.create")),
):
    cid = _company_id(user)
    data = payload.model_dump(exclude_unset=True)
    _check_unique(db, ConditionReading, ['reference_lecture'], data, "Releu condition", cid)
    obj = ConditionReading(company_id=cid)
    _apply(data, obj)
    return _commit(db, obj, "Releu condition")


@router.put("/condition-readings/{ident}", response_model=ConditionReadingOut)
def update_condition_readings(
    ident: int,
    payload: ConditionReadingUpdate,
    db: Session = Depends(get_db),
    user: User = Depends(require_perm("maintindustrielle.condition_readings.modify")),
):
    cid = _company_id(user)
    obj = _get_or_404(db, ConditionReading, ident, "Releu condition")
    if obj.company_id != cid:
        raise HTTPException(403, "Acces refuse.")
    upd = payload.model_dump(exclude_unset=True)
    _chk = {f: upd.get(f, getattr(obj, f)) for f in ['reference_lecture']}
    _check_unique(db, ConditionReading, ['reference_lecture'], _chk, "Releu condition", cid, exclude_id=ident)
    _apply(upd, obj)
    try:
        db.commit()
    except IntegrityError as exc:
        db.rollback()
        raise HTTPException(422, detail="Reference invalide ou conflit d'integrite.")
    db.refresh(obj)
    return obj


@router.delete("/condition-readings/{ident}", response_model=ConditionReadingOut)
def delete_condition_readings(
    ident: int,
    db: Session = Depends(get_db),
    user: User = Depends(require_perm("maintindustrielle.condition_readings.modify")),
):
    cid = _company_id(user)
    obj = _get_or_404(db, ConditionReading, ident, "Releu condition")
    if obj.company_id != cid:
        raise HTTPException(403, "Acces refuse.")
    obj.is_active = False
    db.commit()
    db.refresh(obj)
    return obj


# --- Capteur IoT ---------------------------------------------------------

@router.get("/sensors", response_model=List[SensorOut])
def list_sensors(statut: Optional[str] = None, db: Session = Depends(get_db),
    user: User = Depends(require_perm("maintindustrielle.sensors.read")),
):
    cid = _company_id(user)
    return _scoped_list(db, Sensor, cid, {'statut': statut})


@router.post("/sensors", response_model=SensorOut, status_code=201)
def create_sensors(
    payload: SensorCreate,
    db: Session = Depends(get_db),
    user: User = Depends(require_perm("maintindustrielle.sensors.create")),
):
    cid = _company_id(user)
    data = payload.model_dump(exclude_unset=True)
    _check_unique(db, Sensor, ['code_capteur'], data, "Capteur IoT", cid)
    obj = Sensor(company_id=cid)
    _apply(data, obj)
    return _commit(db, obj, "Capteur IoT")


@router.put("/sensors/{ident}", response_model=SensorOut)
def update_sensors(
    ident: int,
    payload: SensorUpdate,
    db: Session = Depends(get_db),
    user: User = Depends(require_perm("maintindustrielle.sensors.modify")),
):
    cid = _company_id(user)
    obj = _get_or_404(db, Sensor, ident, "Capteur IoT")
    if obj.company_id != cid:
        raise HTTPException(403, "Acces refuse.")
    upd = payload.model_dump(exclude_unset=True)
    _chk = {f: upd.get(f, getattr(obj, f)) for f in ['code_capteur']}
    _check_unique(db, Sensor, ['code_capteur'], _chk, "Capteur IoT", cid, exclude_id=ident)
    _apply(upd, obj)
    try:
        db.commit()
    except IntegrityError as exc:
        db.rollback()
        raise HTTPException(422, detail="Reference invalide ou conflit d'integrite.")
    db.refresh(obj)
    return obj


@router.delete("/sensors/{ident}", response_model=SensorOut)
def delete_sensors(
    ident: int,
    db: Session = Depends(get_db),
    user: User = Depends(require_perm("maintindustrielle.sensors.modify")),
):
    cid = _company_id(user)
    obj = _get_or_404(db, Sensor, ident, "Capteur IoT")
    if obj.company_id != cid:
        raise HTTPException(403, "Acces refuse.")
    obj.is_active = False
    db.commit()
    db.refresh(obj)
    return obj


# --- Modele predictif ---------------------------------------------------------

@router.get("/predictive-models", response_model=List[PredictiveModelOut])
def list_predictive_models(statut: Optional[str] = None, db: Session = Depends(get_db),
    user: User = Depends(require_perm("maintindustrielle.predictive_models.read")),
):
    cid = _company_id(user)
    return _scoped_list(db, PredictiveModel, cid, {'statut': statut})


@router.post("/predictive-models", response_model=PredictiveModelOut, status_code=201)
def create_predictive_models(
    payload: PredictiveModelCreate,
    db: Session = Depends(get_db),
    user: User = Depends(require_perm("maintindustrielle.predictive_models.create")),
):
    cid = _company_id(user)
    data = payload.model_dump(exclude_unset=True)
    _check_unique(db, PredictiveModel, ['code_modele'], data, "Modele predictif", cid)
    obj = PredictiveModel(company_id=cid)
    _apply(data, obj)
    return _commit(db, obj, "Modele predictif")


@router.put("/predictive-models/{ident}", response_model=PredictiveModelOut)
def update_predictive_models(
    ident: int,
    payload: PredictiveModelUpdate,
    db: Session = Depends(get_db),
    user: User = Depends(require_perm("maintindustrielle.predictive_models.modify")),
):
    cid = _company_id(user)
    obj = _get_or_404(db, PredictiveModel, ident, "Modele predictif")
    if obj.company_id != cid:
        raise HTTPException(403, "Acces refuse.")
    upd = payload.model_dump(exclude_unset=True)
    _chk = {f: upd.get(f, getattr(obj, f)) for f in ['code_modele']}
    _check_unique(db, PredictiveModel, ['code_modele'], _chk, "Modele predictif", cid, exclude_id=ident)
    _apply(upd, obj)
    try:
        db.commit()
    except IntegrityError as exc:
        db.rollback()
        raise HTTPException(422, detail="Reference invalide ou conflit d'integrite.")
    db.refresh(obj)
    return obj


@router.delete("/predictive-models/{ident}", response_model=PredictiveModelOut)
def delete_predictive_models(
    ident: int,
    db: Session = Depends(get_db),
    user: User = Depends(require_perm("maintindustrielle.predictive_models.modify")),
):
    cid = _company_id(user)
    obj = _get_or_404(db, PredictiveModel, ident, "Modele predictif")
    if obj.company_id != cid:
        raise HTTPException(403, "Acces refuse.")
    obj.is_active = False
    db.commit()
    db.refresh(obj)
    return obj


# --- KPI fiabilite ---------------------------------------------------------

@router.get("/reliability-kpis", response_model=List[ReliabilityKpiOut])
def list_reliability_kpis(db: Session = Depends(get_db),
    user: User = Depends(require_perm("maintindustrielle.reliability_kpis.read")),
):
    cid = _company_id(user)
    return _scoped_list(db, ReliabilityKpi, cid)


@router.post("/reliability-kpis", response_model=ReliabilityKpiOut, status_code=201)
def create_reliability_kpis(
    payload: ReliabilityKpiCreate,
    db: Session = Depends(get_db),
    user: User = Depends(require_perm("maintindustrielle.reliability_kpis.create")),
):
    cid = _company_id(user)
    data = payload.model_dump(exclude_unset=True)
    _check_unique(db, ReliabilityKpi, ['periode'], data, "KPI fiabilite", cid)
    obj = ReliabilityKpi(company_id=cid)
    _apply(data, obj)
    return _commit(db, obj, "KPI fiabilite")


@router.put("/reliability-kpis/{ident}", response_model=ReliabilityKpiOut)
def update_reliability_kpis(
    ident: int,
    payload: ReliabilityKpiUpdate,
    db: Session = Depends(get_db),
    user: User = Depends(require_perm("maintindustrielle.reliability_kpis.modify")),
):
    cid = _company_id(user)
    obj = _get_or_404(db, ReliabilityKpi, ident, "KPI fiabilite")
    if obj.company_id != cid:
        raise HTTPException(403, "Acces refuse.")
    upd = payload.model_dump(exclude_unset=True)
    _chk = {f: upd.get(f, getattr(obj, f)) for f in ['periode']}
    _check_unique(db, ReliabilityKpi, ['periode'], _chk, "KPI fiabilite", cid, exclude_id=ident)
    _apply(upd, obj)
    try:
        db.commit()
    except IntegrityError as exc:
        db.rollback()
        raise HTTPException(422, detail="Reference invalide ou conflit d'integrite.")
    db.refresh(obj)
    return obj


@router.delete("/reliability-kpis/{ident}", response_model=ReliabilityKpiOut)
def delete_reliability_kpis(
    ident: int,
    db: Session = Depends(get_db),
    user: User = Depends(require_perm("maintindustrielle.reliability_kpis.modify")),
):
    cid = _company_id(user)
    obj = _get_or_404(db, ReliabilityKpi, ident, "KPI fiabilite")
    if obj.company_id != cid:
        raise HTTPException(403, "Acces refuse.")
    obj.is_active = False
    db.commit()
    db.refresh(obj)
    return obj


# --- Inspection reglementaire ---------------------------------------------------------

@router.get("/inspections", response_model=List[RegulatoryInspectionOut])
def list_inspections(statut: Optional[str] = None, db: Session = Depends(get_db),
    user: User = Depends(require_perm("maintindustrielle.inspections.read")),
):
    cid = _company_id(user)
    return _scoped_list(db, RegulatoryInspection, cid, {'statut': statut})


@router.post("/inspections", response_model=RegulatoryInspectionOut, status_code=201)
def create_inspections(
    payload: RegulatoryInspectionCreate,
    db: Session = Depends(get_db),
    user: User = Depends(require_perm("maintindustrielle.inspections.create")),
):
    cid = _company_id(user)
    data = payload.model_dump(exclude_unset=True)
    _check_unique(db, RegulatoryInspection, ['numero_pv'], data, "Inspection reglementaire", cid)
    obj = RegulatoryInspection(company_id=cid)
    _apply(data, obj)
    return _commit(db, obj, "Inspection reglementaire")


@router.put("/inspections/{ident}", response_model=RegulatoryInspectionOut)
def update_inspections(
    ident: int,
    payload: RegulatoryInspectionUpdate,
    db: Session = Depends(get_db),
    user: User = Depends(require_perm("maintindustrielle.inspections.modify")),
):
    cid = _company_id(user)
    obj = _get_or_404(db, RegulatoryInspection, ident, "Inspection reglementaire")
    if obj.company_id != cid:
        raise HTTPException(403, "Acces refuse.")
    upd = payload.model_dump(exclude_unset=True)
    _chk = {f: upd.get(f, getattr(obj, f)) for f in ['numero_pv']}
    _check_unique(db, RegulatoryInspection, ['numero_pv'], _chk, "Inspection reglementaire", cid, exclude_id=ident)
    _apply(upd, obj)
    try:
        db.commit()
    except IntegrityError as exc:
        db.rollback()
        raise HTTPException(422, detail="Reference invalide ou conflit d'integrite.")
    db.refresh(obj)
    return obj


@router.delete("/inspections/{ident}", response_model=RegulatoryInspectionOut)
def delete_inspections(
    ident: int,
    db: Session = Depends(get_db),
    user: User = Depends(require_perm("maintindustrielle.inspections.modify")),
):
    cid = _company_id(user)
    obj = _get_or_404(db, RegulatoryInspection, ident, "Inspection reglementaire")
    if obj.company_id != cid:
        raise HTTPException(403, "Acces refuse.")
    obj.is_active = False
    db.commit()
    db.refresh(obj)
    return obj


# --- Budget maintenance ---------------------------------------------------------

@router.get("/budgets", response_model=List[MaintenanceBudgetOut])
def list_budgets(statut: Optional[str] = None, db: Session = Depends(get_db),
    user: User = Depends(require_perm("maintindustrielle.budgets.read")),
):
    cid = _company_id(user)
    return _scoped_list(db, MaintenanceBudget, cid, {'statut': statut})


@router.post("/budgets", response_model=MaintenanceBudgetOut, status_code=201)
def create_budgets(
    payload: MaintenanceBudgetCreate,
    db: Session = Depends(get_db),
    user: User = Depends(require_perm("maintindustrielle.budgets.create")),
):
    cid = _company_id(user)
    data = payload.model_dump(exclude_unset=True)
    _check_unique(db, MaintenanceBudget, ['exercice'], data, "Budget maintenance", cid)
    obj = MaintenanceBudget(company_id=cid)
    _apply(data, obj)
    return _commit(db, obj, "Budget maintenance")


@router.put("/budgets/{ident}", response_model=MaintenanceBudgetOut)
def update_budgets(
    ident: int,
    payload: MaintenanceBudgetUpdate,
    db: Session = Depends(get_db),
    user: User = Depends(require_perm("maintindustrielle.budgets.modify")),
):
    cid = _company_id(user)
    obj = _get_or_404(db, MaintenanceBudget, ident, "Budget maintenance")
    if obj.company_id != cid:
        raise HTTPException(403, "Acces refuse.")
    upd = payload.model_dump(exclude_unset=True)
    _chk = {f: upd.get(f, getattr(obj, f)) for f in ['exercice']}
    _check_unique(db, MaintenanceBudget, ['exercice'], _chk, "Budget maintenance", cid, exclude_id=ident)
    _apply(upd, obj)
    try:
        db.commit()
    except IntegrityError as exc:
        db.rollback()
        raise HTTPException(422, detail="Reference invalide ou conflit d'integrite.")
    db.refresh(obj)
    return obj


@router.delete("/budgets/{ident}", response_model=MaintenanceBudgetOut)
def delete_budgets(
    ident: int,
    db: Session = Depends(get_db),
    user: User = Depends(require_perm("maintindustrielle.budgets.modify")),
):
    cid = _company_id(user)
    obj = _get_or_404(db, MaintenanceBudget, ident, "Budget maintenance")
    if obj.company_id != cid:
        raise HTTPException(403, "Acces refuse.")
    obj.is_active = False
    db.commit()
    db.refresh(obj)
    return obj


# --- Prestataire maintenance ---------------------------------------------------------

@router.get("/vendors", response_model=List[MaintenanceVendorOut])
def list_vendors(statut: Optional[str] = None, db: Session = Depends(get_db),
    user: User = Depends(require_perm("maintindustrielle.vendors.read")),
):
    cid = _company_id(user)
    return _scoped_list(db, MaintenanceVendor, cid, {'statut': statut})


@router.post("/vendors", response_model=MaintenanceVendorOut, status_code=201)
def create_vendors(
    payload: MaintenanceVendorCreate,
    db: Session = Depends(get_db),
    user: User = Depends(require_perm("maintindustrielle.vendors.create")),
):
    cid = _company_id(user)
    data = payload.model_dump(exclude_unset=True)
    _check_unique(db, MaintenanceVendor, ['code_prestataire'], data, "Prestataire maintenance", cid)
    obj = MaintenanceVendor(company_id=cid)
    _apply(data, obj)
    return _commit(db, obj, "Prestataire maintenance")


@router.put("/vendors/{ident}", response_model=MaintenanceVendorOut)
def update_vendors(
    ident: int,
    payload: MaintenanceVendorUpdate,
    db: Session = Depends(get_db),
    user: User = Depends(require_perm("maintindustrielle.vendors.modify")),
):
    cid = _company_id(user)
    obj = _get_or_404(db, MaintenanceVendor, ident, "Prestataire maintenance")
    if obj.company_id != cid:
        raise HTTPException(403, "Acces refuse.")
    upd = payload.model_dump(exclude_unset=True)
    _chk = {f: upd.get(f, getattr(obj, f)) for f in ['code_prestataire']}
    _check_unique(db, MaintenanceVendor, ['code_prestataire'], _chk, "Prestataire maintenance", cid, exclude_id=ident)
    _apply(upd, obj)
    try:
        db.commit()
    except IntegrityError as exc:
        db.rollback()
        raise HTTPException(422, detail="Reference invalide ou conflit d'integrite.")
    db.refresh(obj)
    return obj


@router.delete("/vendors/{ident}", response_model=MaintenanceVendorOut)
def delete_vendors(
    ident: int,
    db: Session = Depends(get_db),
    user: User = Depends(require_perm("maintindustrielle.vendors.modify")),
):
    cid = _company_id(user)
    obj = _get_or_404(db, MaintenanceVendor, ident, "Prestataire maintenance")
    if obj.company_id != cid:
        raise HTTPException(403, "Acces refuse.")
    obj.is_active = False
    db.commit()
    db.refresh(obj)
    return obj

