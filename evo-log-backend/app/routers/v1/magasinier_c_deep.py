"""Routeur CRUD genere pour portail-magasinier (expansion)."""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import Optional, List

from app.core.database import get_db
from app.core.permissions import require_perm
from app.models.user import User
from app.models.magasinier_c_deep import (
    MagcPickingTask,
    MagcPackingSlip,
    MagcPutawayTask,
    MagcCycleCount,
    MagcInternalMove,
    MagcGoodsIssue,
    MagcReturnProcessing,
    MagcLabelPrint,
    MagcPalletBuild,
    MagcEquipmentCheck,
    MagcSafetyInspection,
    MagcSpillCleanup,
    MagcLoadingCheck,
    MagcReceivingCheck,
    MagcPutawayException,
    MagcOrderStaging,
    MagcColdChainCheck,
    MagcHazmatHandling,
    MagcDockAssignment,
)
from app.schemas.magasinier_c_deep import (
    MagcPickingTaskCreate, MagcPickingTaskUpdate, MagcPickingTaskOut,
    MagcPackingSlipCreate, MagcPackingSlipUpdate, MagcPackingSlipOut,
    MagcPutawayTaskCreate, MagcPutawayTaskUpdate, MagcPutawayTaskOut,
    MagcCycleCountCreate, MagcCycleCountUpdate, MagcCycleCountOut,
    MagcInternalMoveCreate, MagcInternalMoveUpdate, MagcInternalMoveOut,
    MagcGoodsIssueCreate, MagcGoodsIssueUpdate, MagcGoodsIssueOut,
    MagcReturnProcessingCreate, MagcReturnProcessingUpdate, MagcReturnProcessingOut,
    MagcLabelPrintCreate, MagcLabelPrintUpdate, MagcLabelPrintOut,
    MagcPalletBuildCreate, MagcPalletBuildUpdate, MagcPalletBuildOut,
    MagcEquipmentCheckCreate, MagcEquipmentCheckUpdate, MagcEquipmentCheckOut,
    MagcSafetyInspectionCreate, MagcSafetyInspectionUpdate, MagcSafetyInspectionOut,
    MagcSpillCleanupCreate, MagcSpillCleanupUpdate, MagcSpillCleanupOut,
    MagcLoadingCheckCreate, MagcLoadingCheckUpdate, MagcLoadingCheckOut,
    MagcReceivingCheckCreate, MagcReceivingCheckUpdate, MagcReceivingCheckOut,
    MagcPutawayExceptionCreate, MagcPutawayExceptionUpdate, MagcPutawayExceptionOut,
    MagcOrderStagingCreate, MagcOrderStagingUpdate, MagcOrderStagingOut,
    MagcColdChainCheckCreate, MagcColdChainCheckUpdate, MagcColdChainCheckOut,
    MagcHazmatHandlingCreate, MagcHazmatHandlingUpdate, MagcHazmatHandlingOut,
    MagcDockAssignmentCreate, MagcDockAssignmentUpdate, MagcDockAssignmentOut,
)

router = APIRouter(tags=["portail-magasinier (expansion)"])


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

@router.get("/nomenclatures", summary="Vocabulaire metier portail-magasinier")
def nomenclatures(user: User = Depends(require_perm("magasin.nomenclature.read"))):
    from app.models import magasinier_c_deep as _md
    import enum as _pyenum
    out = {}
    for name in dir(_md):
        obj = getattr(_md, name)
        if isinstance(obj, type) and issubclass(obj, _pyenum.Enum) and obj is not _pyenum.Enum:
            out[name.lower()] = [{"code": m.name, "valeur": m.value} for m in obj]
    return out


# ─── Taches de preparation ─────────────────────────────────────────────────

@router.get("/magc-picking-tasks", response_model=List[MagcPickingTaskOut])
def list_picking_task(statut: Optional[str] = None, db: Session = Depends(get_db),
    user: User = Depends(require_perm("magasin.picking_task.read")),
):
    cid = _company_id(user)
    return _scoped_list(db, MagcPickingTask, cid, {"statut": statut})


@router.post("/magc-picking-tasks", response_model=MagcPickingTaskOut, status_code=201)
def create_picking_task(
    payload: MagcPickingTaskCreate,
    db: Session = Depends(get_db),
    user: User = Depends(require_perm("magasin.picking_task.create")),
):
    cid = _company_id(user)
    data = payload.model_dump(exclude_unset=True)
    _check_unique(db, MagcPickingTask, "reference", data.get("reference"), "reference", cid)
    obj = MagcPickingTask(company_id=cid)
    _apply(data, obj)
    db.add(obj)
    db.commit()
    db.refresh(obj)
    return obj


@router.put("/magc-picking-tasks/{ident}", response_model=MagcPickingTaskOut)
def update_picking_task(
    ident: int,
    payload: MagcPickingTaskUpdate,
    db: Session = Depends(get_db),
    user: User = Depends(require_perm("magasin.picking_task.modify")),
):
    cid = _company_id(user)
    obj = _get_or_404(db, MagcPickingTask, ident, "Taches de preparation")
    if obj.company_id != cid:
        raise HTTPException(403, "Acces refuse.")
    _apply(payload.model_dump(exclude_unset=True), obj)
    db.commit()
    db.refresh(obj)
    return obj


@router.delete("/magc-picking-tasks/{ident}", response_model=MagcPickingTaskOut)
def delete_picking_task(
    ident: int,
    db: Session = Depends(get_db),
    user: User = Depends(require_perm("magasin.picking_task.modify")),
):
    cid = _company_id(user)
    obj = _get_or_404(db, MagcPickingTask, ident, "Taches de preparation")
    if obj.company_id != cid:
        raise HTTPException(403, "Acces refuse.")
    obj.is_active = False
    db.commit()
    db.refresh(obj)
    return obj


# ─── Bons de colisage ─────────────────────────────────────────────────

@router.get("/magc-packing-slips", response_model=List[MagcPackingSlipOut])
def list_packing_slip(statut: Optional[str] = None, db: Session = Depends(get_db),
    user: User = Depends(require_perm("magasin.packing_slip.read")),
):
    cid = _company_id(user)
    return _scoped_list(db, MagcPackingSlip, cid, {"statut": statut})


@router.post("/magc-packing-slips", response_model=MagcPackingSlipOut, status_code=201)
def create_packing_slip(
    payload: MagcPackingSlipCreate,
    db: Session = Depends(get_db),
    user: User = Depends(require_perm("magasin.packing_slip.create")),
):
    cid = _company_id(user)
    data = payload.model_dump(exclude_unset=True)
    _check_unique(db, MagcPackingSlip, "reference", data.get("reference"), "reference", cid)
    obj = MagcPackingSlip(company_id=cid)
    _apply(data, obj)
    db.add(obj)
    db.commit()
    db.refresh(obj)
    return obj


@router.put("/magc-packing-slips/{ident}", response_model=MagcPackingSlipOut)
def update_packing_slip(
    ident: int,
    payload: MagcPackingSlipUpdate,
    db: Session = Depends(get_db),
    user: User = Depends(require_perm("magasin.packing_slip.modify")),
):
    cid = _company_id(user)
    obj = _get_or_404(db, MagcPackingSlip, ident, "Bons de colisage")
    if obj.company_id != cid:
        raise HTTPException(403, "Acces refuse.")
    _apply(payload.model_dump(exclude_unset=True), obj)
    db.commit()
    db.refresh(obj)
    return obj


@router.delete("/magc-packing-slips/{ident}", response_model=MagcPackingSlipOut)
def delete_packing_slip(
    ident: int,
    db: Session = Depends(get_db),
    user: User = Depends(require_perm("magasin.packing_slip.modify")),
):
    cid = _company_id(user)
    obj = _get_or_404(db, MagcPackingSlip, ident, "Bons de colisage")
    if obj.company_id != cid:
        raise HTTPException(403, "Acces refuse.")
    obj.is_active = False
    db.commit()
    db.refresh(obj)
    return obj


# ─── Taches de mise en place ─────────────────────────────────────────────────

@router.get("/magc-put-away-tasks", response_model=List[MagcPutawayTaskOut])
def list_putaway_task(statut: Optional[str] = None, db: Session = Depends(get_db),
    user: User = Depends(require_perm("magasin.putaway_task.read")),
):
    cid = _company_id(user)
    return _scoped_list(db, MagcPutawayTask, cid, {"statut": statut})


@router.post("/magc-put-away-tasks", response_model=MagcPutawayTaskOut, status_code=201)
def create_putaway_task(
    payload: MagcPutawayTaskCreate,
    db: Session = Depends(get_db),
    user: User = Depends(require_perm("magasin.putaway_task.create")),
):
    cid = _company_id(user)
    data = payload.model_dump(exclude_unset=True)
    _check_unique(db, MagcPutawayTask, "reference", data.get("reference"), "reference", cid)
    obj = MagcPutawayTask(company_id=cid)
    _apply(data, obj)
    db.add(obj)
    db.commit()
    db.refresh(obj)
    return obj


@router.put("/magc-put-away-tasks/{ident}", response_model=MagcPutawayTaskOut)
def update_putaway_task(
    ident: int,
    payload: MagcPutawayTaskUpdate,
    db: Session = Depends(get_db),
    user: User = Depends(require_perm("magasin.putaway_task.modify")),
):
    cid = _company_id(user)
    obj = _get_or_404(db, MagcPutawayTask, ident, "Taches de mise en place")
    if obj.company_id != cid:
        raise HTTPException(403, "Acces refuse.")
    _apply(payload.model_dump(exclude_unset=True), obj)
    db.commit()
    db.refresh(obj)
    return obj


@router.delete("/magc-put-away-tasks/{ident}", response_model=MagcPutawayTaskOut)
def delete_putaway_task(
    ident: int,
    db: Session = Depends(get_db),
    user: User = Depends(require_perm("magasin.putaway_task.modify")),
):
    cid = _company_id(user)
    obj = _get_or_404(db, MagcPutawayTask, ident, "Taches de mise en place")
    if obj.company_id != cid:
        raise HTTPException(403, "Acces refuse.")
    obj.is_active = False
    db.commit()
    db.refresh(obj)
    return obj


# ─── Inventaires tournants ─────────────────────────────────────────────────

@router.get("/magc-cycle-counts", response_model=List[MagcCycleCountOut])
def list_cycle_count(statut: Optional[str] = None, db: Session = Depends(get_db),
    user: User = Depends(require_perm("magasin.cycle_count.read")),
):
    cid = _company_id(user)
    return _scoped_list(db, MagcCycleCount, cid, {"statut": statut})


@router.post("/magc-cycle-counts", response_model=MagcCycleCountOut, status_code=201)
def create_cycle_count(
    payload: MagcCycleCountCreate,
    db: Session = Depends(get_db),
    user: User = Depends(require_perm("magasin.cycle_count.create")),
):
    cid = _company_id(user)
    data = payload.model_dump(exclude_unset=True)
    _check_unique(db, MagcCycleCount, "reference", data.get("reference"), "reference", cid)
    obj = MagcCycleCount(company_id=cid)
    _apply(data, obj)
    db.add(obj)
    db.commit()
    db.refresh(obj)
    return obj


@router.put("/magc-cycle-counts/{ident}", response_model=MagcCycleCountOut)
def update_cycle_count(
    ident: int,
    payload: MagcCycleCountUpdate,
    db: Session = Depends(get_db),
    user: User = Depends(require_perm("magasin.cycle_count.modify")),
):
    cid = _company_id(user)
    obj = _get_or_404(db, MagcCycleCount, ident, "Inventaires tournants")
    if obj.company_id != cid:
        raise HTTPException(403, "Acces refuse.")
    _apply(payload.model_dump(exclude_unset=True), obj)
    db.commit()
    db.refresh(obj)
    return obj


@router.delete("/magc-cycle-counts/{ident}", response_model=MagcCycleCountOut)
def delete_cycle_count(
    ident: int,
    db: Session = Depends(get_db),
    user: User = Depends(require_perm("magasin.cycle_count.modify")),
):
    cid = _company_id(user)
    obj = _get_or_404(db, MagcCycleCount, ident, "Inventaires tournants")
    if obj.company_id != cid:
        raise HTTPException(403, "Acces refuse.")
    obj.is_active = False
    db.commit()
    db.refresh(obj)
    return obj


# ─── Transferts internes ─────────────────────────────────────────────────

@router.get("/magc-internal-moves", response_model=List[MagcInternalMoveOut])
def list_internal_move(statut: Optional[str] = None, db: Session = Depends(get_db),
    user: User = Depends(require_perm("magasin.internal_move.read")),
):
    cid = _company_id(user)
    return _scoped_list(db, MagcInternalMove, cid, {"statut": statut})


@router.post("/magc-internal-moves", response_model=MagcInternalMoveOut, status_code=201)
def create_internal_move(
    payload: MagcInternalMoveCreate,
    db: Session = Depends(get_db),
    user: User = Depends(require_perm("magasin.internal_move.create")),
):
    cid = _company_id(user)
    data = payload.model_dump(exclude_unset=True)
    _check_unique(db, MagcInternalMove, "reference", data.get("reference"), "reference", cid)
    obj = MagcInternalMove(company_id=cid)
    _apply(data, obj)
    db.add(obj)
    db.commit()
    db.refresh(obj)
    return obj


@router.put("/magc-internal-moves/{ident}", response_model=MagcInternalMoveOut)
def update_internal_move(
    ident: int,
    payload: MagcInternalMoveUpdate,
    db: Session = Depends(get_db),
    user: User = Depends(require_perm("magasin.internal_move.modify")),
):
    cid = _company_id(user)
    obj = _get_or_404(db, MagcInternalMove, ident, "Transferts internes")
    if obj.company_id != cid:
        raise HTTPException(403, "Acces refuse.")
    _apply(payload.model_dump(exclude_unset=True), obj)
    db.commit()
    db.refresh(obj)
    return obj


@router.delete("/magc-internal-moves/{ident}", response_model=MagcInternalMoveOut)
def delete_internal_move(
    ident: int,
    db: Session = Depends(get_db),
    user: User = Depends(require_perm("magasin.internal_move.modify")),
):
    cid = _company_id(user)
    obj = _get_or_404(db, MagcInternalMove, ident, "Transferts internes")
    if obj.company_id != cid:
        raise HTTPException(403, "Acces refuse.")
    obj.is_active = False
    db.commit()
    db.refresh(obj)
    return obj


# ─── Sorties de magasin ─────────────────────────────────────────────────

@router.get("/magc-goods-issues", response_model=List[MagcGoodsIssueOut])
def list_goods_issue(statut: Optional[str] = None, db: Session = Depends(get_db),
    user: User = Depends(require_perm("magasin.goods_issue.read")),
):
    cid = _company_id(user)
    return _scoped_list(db, MagcGoodsIssue, cid, {"statut": statut})


@router.post("/magc-goods-issues", response_model=MagcGoodsIssueOut, status_code=201)
def create_goods_issue(
    payload: MagcGoodsIssueCreate,
    db: Session = Depends(get_db),
    user: User = Depends(require_perm("magasin.goods_issue.create")),
):
    cid = _company_id(user)
    data = payload.model_dump(exclude_unset=True)
    _check_unique(db, MagcGoodsIssue, "reference", data.get("reference"), "reference", cid)
    obj = MagcGoodsIssue(company_id=cid)
    _apply(data, obj)
    db.add(obj)
    db.commit()
    db.refresh(obj)
    return obj


@router.put("/magc-goods-issues/{ident}", response_model=MagcGoodsIssueOut)
def update_goods_issue(
    ident: int,
    payload: MagcGoodsIssueUpdate,
    db: Session = Depends(get_db),
    user: User = Depends(require_perm("magasin.goods_issue.modify")),
):
    cid = _company_id(user)
    obj = _get_or_404(db, MagcGoodsIssue, ident, "Sorties de magasin")
    if obj.company_id != cid:
        raise HTTPException(403, "Acces refuse.")
    _apply(payload.model_dump(exclude_unset=True), obj)
    db.commit()
    db.refresh(obj)
    return obj


@router.delete("/magc-goods-issues/{ident}", response_model=MagcGoodsIssueOut)
def delete_goods_issue(
    ident: int,
    db: Session = Depends(get_db),
    user: User = Depends(require_perm("magasin.goods_issue.modify")),
):
    cid = _company_id(user)
    obj = _get_or_404(db, MagcGoodsIssue, ident, "Sorties de magasin")
    if obj.company_id != cid:
        raise HTTPException(403, "Acces refuse.")
    obj.is_active = False
    db.commit()
    db.refresh(obj)
    return obj


# ─── Traitement des retours ─────────────────────────────────────────────────

@router.get("/magc-returns-processing", response_model=List[MagcReturnProcessingOut])
def list_return_processing(statut: Optional[str] = None, db: Session = Depends(get_db),
    user: User = Depends(require_perm("magasin.return_processing.read")),
):
    cid = _company_id(user)
    return _scoped_list(db, MagcReturnProcessing, cid, {"statut": statut})


@router.post("/magc-returns-processing", response_model=MagcReturnProcessingOut, status_code=201)
def create_return_processing(
    payload: MagcReturnProcessingCreate,
    db: Session = Depends(get_db),
    user: User = Depends(require_perm("magasin.return_processing.create")),
):
    cid = _company_id(user)
    data = payload.model_dump(exclude_unset=True)
    _check_unique(db, MagcReturnProcessing, "reference", data.get("reference"), "reference", cid)
    obj = MagcReturnProcessing(company_id=cid)
    _apply(data, obj)
    db.add(obj)
    db.commit()
    db.refresh(obj)
    return obj


@router.put("/magc-returns-processing/{ident}", response_model=MagcReturnProcessingOut)
def update_return_processing(
    ident: int,
    payload: MagcReturnProcessingUpdate,
    db: Session = Depends(get_db),
    user: User = Depends(require_perm("magasin.return_processing.modify")),
):
    cid = _company_id(user)
    obj = _get_or_404(db, MagcReturnProcessing, ident, "Traitement des retours")
    if obj.company_id != cid:
        raise HTTPException(403, "Acces refuse.")
    _apply(payload.model_dump(exclude_unset=True), obj)
    db.commit()
    db.refresh(obj)
    return obj


@router.delete("/magc-returns-processing/{ident}", response_model=MagcReturnProcessingOut)
def delete_return_processing(
    ident: int,
    db: Session = Depends(get_db),
    user: User = Depends(require_perm("magasin.return_processing.modify")),
):
    cid = _company_id(user)
    obj = _get_or_404(db, MagcReturnProcessing, ident, "Traitement des retours")
    if obj.company_id != cid:
        raise HTTPException(403, "Acces refuse.")
    obj.is_active = False
    db.commit()
    db.refresh(obj)
    return obj


# ─── Edition d' etiquettes ─────────────────────────────────────────────────

@router.get("/magc-label-printing", response_model=List[MagcLabelPrintOut])
def list_label_print(statut: Optional[str] = None, db: Session = Depends(get_db),
    user: User = Depends(require_perm("magasin.label_print.read")),
):
    cid = _company_id(user)
    return _scoped_list(db, MagcLabelPrint, cid, {"statut": statut})


@router.post("/magc-label-printing", response_model=MagcLabelPrintOut, status_code=201)
def create_label_print(
    payload: MagcLabelPrintCreate,
    db: Session = Depends(get_db),
    user: User = Depends(require_perm("magasin.label_print.create")),
):
    cid = _company_id(user)
    data = payload.model_dump(exclude_unset=True)
    _check_unique(db, MagcLabelPrint, "reference", data.get("reference"), "reference", cid)
    obj = MagcLabelPrint(company_id=cid)
    _apply(data, obj)
    db.add(obj)
    db.commit()
    db.refresh(obj)
    return obj


@router.put("/magc-label-printing/{ident}", response_model=MagcLabelPrintOut)
def update_label_print(
    ident: int,
    payload: MagcLabelPrintUpdate,
    db: Session = Depends(get_db),
    user: User = Depends(require_perm("magasin.label_print.modify")),
):
    cid = _company_id(user)
    obj = _get_or_404(db, MagcLabelPrint, ident, "Edition d' etiquettes")
    if obj.company_id != cid:
        raise HTTPException(403, "Acces refuse.")
    _apply(payload.model_dump(exclude_unset=True), obj)
    db.commit()
    db.refresh(obj)
    return obj


@router.delete("/magc-label-printing/{ident}", response_model=MagcLabelPrintOut)
def delete_label_print(
    ident: int,
    db: Session = Depends(get_db),
    user: User = Depends(require_perm("magasin.label_print.modify")),
):
    cid = _company_id(user)
    obj = _get_or_404(db, MagcLabelPrint, ident, "Edition d' etiquettes")
    if obj.company_id != cid:
        raise HTTPException(403, "Acces refuse.")
    obj.is_active = False
    db.commit()
    db.refresh(obj)
    return obj


# ─── Constitution de palettes ─────────────────────────────────────────────────

@router.get("/magc-pallet-building", response_model=List[MagcPalletBuildOut])
def list_pallet_build(statut: Optional[str] = None, db: Session = Depends(get_db),
    user: User = Depends(require_perm("magasin.pallet_build.read")),
):
    cid = _company_id(user)
    return _scoped_list(db, MagcPalletBuild, cid, {"statut": statut})


@router.post("/magc-pallet-building", response_model=MagcPalletBuildOut, status_code=201)
def create_pallet_build(
    payload: MagcPalletBuildCreate,
    db: Session = Depends(get_db),
    user: User = Depends(require_perm("magasin.pallet_build.create")),
):
    cid = _company_id(user)
    data = payload.model_dump(exclude_unset=True)
    _check_unique(db, MagcPalletBuild, "reference", data.get("reference"), "reference", cid)
    obj = MagcPalletBuild(company_id=cid)
    _apply(data, obj)
    db.add(obj)
    db.commit()
    db.refresh(obj)
    return obj


@router.put("/magc-pallet-building/{ident}", response_model=MagcPalletBuildOut)
def update_pallet_build(
    ident: int,
    payload: MagcPalletBuildUpdate,
    db: Session = Depends(get_db),
    user: User = Depends(require_perm("magasin.pallet_build.modify")),
):
    cid = _company_id(user)
    obj = _get_or_404(db, MagcPalletBuild, ident, "Constitution de palettes")
    if obj.company_id != cid:
        raise HTTPException(403, "Acces refuse.")
    _apply(payload.model_dump(exclude_unset=True), obj)
    db.commit()
    db.refresh(obj)
    return obj


@router.delete("/magc-pallet-building/{ident}", response_model=MagcPalletBuildOut)
def delete_pallet_build(
    ident: int,
    db: Session = Depends(get_db),
    user: User = Depends(require_perm("magasin.pallet_build.modify")),
):
    cid = _company_id(user)
    obj = _get_or_404(db, MagcPalletBuild, ident, "Constitution de palettes")
    if obj.company_id != cid:
        raise HTTPException(403, "Acces refuse.")
    obj.is_active = False
    db.commit()
    db.refresh(obj)
    return obj


# ─── Controles engins ─────────────────────────────────────────────────

@router.get("/magc-equipment-checks", response_model=List[MagcEquipmentCheckOut])
def list_equipment_check(statut: Optional[str] = None, db: Session = Depends(get_db),
    user: User = Depends(require_perm("magasin.equipment_check.read")),
):
    cid = _company_id(user)
    return _scoped_list(db, MagcEquipmentCheck, cid, {"statut": statut})


@router.post("/magc-equipment-checks", response_model=MagcEquipmentCheckOut, status_code=201)
def create_equipment_check(
    payload: MagcEquipmentCheckCreate,
    db: Session = Depends(get_db),
    user: User = Depends(require_perm("magasin.equipment_check.create")),
):
    cid = _company_id(user)
    data = payload.model_dump(exclude_unset=True)
    _check_unique(db, MagcEquipmentCheck, "reference", data.get("reference"), "reference", cid)
    obj = MagcEquipmentCheck(company_id=cid)
    _apply(data, obj)
    db.add(obj)
    db.commit()
    db.refresh(obj)
    return obj


@router.put("/magc-equipment-checks/{ident}", response_model=MagcEquipmentCheckOut)
def update_equipment_check(
    ident: int,
    payload: MagcEquipmentCheckUpdate,
    db: Session = Depends(get_db),
    user: User = Depends(require_perm("magasin.equipment_check.modify")),
):
    cid = _company_id(user)
    obj = _get_or_404(db, MagcEquipmentCheck, ident, "Controles engins")
    if obj.company_id != cid:
        raise HTTPException(403, "Acces refuse.")
    _apply(payload.model_dump(exclude_unset=True), obj)
    db.commit()
    db.refresh(obj)
    return obj


@router.delete("/magc-equipment-checks/{ident}", response_model=MagcEquipmentCheckOut)
def delete_equipment_check(
    ident: int,
    db: Session = Depends(get_db),
    user: User = Depends(require_perm("magasin.equipment_check.modify")),
):
    cid = _company_id(user)
    obj = _get_or_404(db, MagcEquipmentCheck, ident, "Controles engins")
    if obj.company_id != cid:
        raise HTTPException(403, "Acces refuse.")
    obj.is_active = False
    db.commit()
    db.refresh(obj)
    return obj


# ─── Rondes de securite ─────────────────────────────────────────────────

@router.get("/magc-safety-inspections", response_model=List[MagcSafetyInspectionOut])
def list_safety_inspection(statut: Optional[str] = None, db: Session = Depends(get_db),
    user: User = Depends(require_perm("magasin.safety_inspection.read")),
):
    cid = _company_id(user)
    return _scoped_list(db, MagcSafetyInspection, cid, {"statut": statut})


@router.post("/magc-safety-inspections", response_model=MagcSafetyInspectionOut, status_code=201)
def create_safety_inspection(
    payload: MagcSafetyInspectionCreate,
    db: Session = Depends(get_db),
    user: User = Depends(require_perm("magasin.safety_inspection.create")),
):
    cid = _company_id(user)
    data = payload.model_dump(exclude_unset=True)
    _check_unique(db, MagcSafetyInspection, "reference", data.get("reference"), "reference", cid)
    obj = MagcSafetyInspection(company_id=cid)
    _apply(data, obj)
    db.add(obj)
    db.commit()
    db.refresh(obj)
    return obj


@router.put("/magc-safety-inspections/{ident}", response_model=MagcSafetyInspectionOut)
def update_safety_inspection(
    ident: int,
    payload: MagcSafetyInspectionUpdate,
    db: Session = Depends(get_db),
    user: User = Depends(require_perm("magasin.safety_inspection.modify")),
):
    cid = _company_id(user)
    obj = _get_or_404(db, MagcSafetyInspection, ident, "Rondes de securite")
    if obj.company_id != cid:
        raise HTTPException(403, "Acces refuse.")
    _apply(payload.model_dump(exclude_unset=True), obj)
    db.commit()
    db.refresh(obj)
    return obj


@router.delete("/magc-safety-inspections/{ident}", response_model=MagcSafetyInspectionOut)
def delete_safety_inspection(
    ident: int,
    db: Session = Depends(get_db),
    user: User = Depends(require_perm("magasin.safety_inspection.modify")),
):
    cid = _company_id(user)
    obj = _get_or_404(db, MagcSafetyInspection, ident, "Rondes de securite")
    if obj.company_id != cid:
        raise HTTPException(403, "Acces refuse.")
    obj.is_active = False
    db.commit()
    db.refresh(obj)
    return obj


# ─── Nettoyages de deversement ─────────────────────────────────────────────────

@router.get("/magc-spill-cleanups", response_model=List[MagcSpillCleanupOut])
def list_spill_cleanup(statut: Optional[str] = None, db: Session = Depends(get_db),
    user: User = Depends(require_perm("magasin.spill_cleanup.read")),
):
    cid = _company_id(user)
    return _scoped_list(db, MagcSpillCleanup, cid, {"statut": statut})


@router.post("/magc-spill-cleanups", response_model=MagcSpillCleanupOut, status_code=201)
def create_spill_cleanup(
    payload: MagcSpillCleanupCreate,
    db: Session = Depends(get_db),
    user: User = Depends(require_perm("magasin.spill_cleanup.create")),
):
    cid = _company_id(user)
    data = payload.model_dump(exclude_unset=True)
    _check_unique(db, MagcSpillCleanup, "reference", data.get("reference"), "reference", cid)
    obj = MagcSpillCleanup(company_id=cid)
    _apply(data, obj)
    db.add(obj)
    db.commit()
    db.refresh(obj)
    return obj


@router.put("/magc-spill-cleanups/{ident}", response_model=MagcSpillCleanupOut)
def update_spill_cleanup(
    ident: int,
    payload: MagcSpillCleanupUpdate,
    db: Session = Depends(get_db),
    user: User = Depends(require_perm("magasin.spill_cleanup.modify")),
):
    cid = _company_id(user)
    obj = _get_or_404(db, MagcSpillCleanup, ident, "Nettoyages de deversement")
    if obj.company_id != cid:
        raise HTTPException(403, "Acces refuse.")
    _apply(payload.model_dump(exclude_unset=True), obj)
    db.commit()
    db.refresh(obj)
    return obj


@router.delete("/magc-spill-cleanups/{ident}", response_model=MagcSpillCleanupOut)
def delete_spill_cleanup(
    ident: int,
    db: Session = Depends(get_db),
    user: User = Depends(require_perm("magasin.spill_cleanup.modify")),
):
    cid = _company_id(user)
    obj = _get_or_404(db, MagcSpillCleanup, ident, "Nettoyages de deversement")
    if obj.company_id != cid:
        raise HTTPException(403, "Acces refuse.")
    obj.is_active = False
    db.commit()
    db.refresh(obj)
    return obj


# ─── Controles de chargement ─────────────────────────────────────────────────

@router.get("/magc-loading-checks", response_model=List[MagcLoadingCheckOut])
def list_loading_check(statut: Optional[str] = None, db: Session = Depends(get_db),
    user: User = Depends(require_perm("magasin.loading_check.read")),
):
    cid = _company_id(user)
    return _scoped_list(db, MagcLoadingCheck, cid, {"statut": statut})


@router.post("/magc-loading-checks", response_model=MagcLoadingCheckOut, status_code=201)
def create_loading_check(
    payload: MagcLoadingCheckCreate,
    db: Session = Depends(get_db),
    user: User = Depends(require_perm("magasin.loading_check.create")),
):
    cid = _company_id(user)
    data = payload.model_dump(exclude_unset=True)
    _check_unique(db, MagcLoadingCheck, "reference", data.get("reference"), "reference", cid)
    obj = MagcLoadingCheck(company_id=cid)
    _apply(data, obj)
    db.add(obj)
    db.commit()
    db.refresh(obj)
    return obj


@router.put("/magc-loading-checks/{ident}", response_model=MagcLoadingCheckOut)
def update_loading_check(
    ident: int,
    payload: MagcLoadingCheckUpdate,
    db: Session = Depends(get_db),
    user: User = Depends(require_perm("magasin.loading_check.modify")),
):
    cid = _company_id(user)
    obj = _get_or_404(db, MagcLoadingCheck, ident, "Controles de chargement")
    if obj.company_id != cid:
        raise HTTPException(403, "Acces refuse.")
    _apply(payload.model_dump(exclude_unset=True), obj)
    db.commit()
    db.refresh(obj)
    return obj


@router.delete("/magc-loading-checks/{ident}", response_model=MagcLoadingCheckOut)
def delete_loading_check(
    ident: int,
    db: Session = Depends(get_db),
    user: User = Depends(require_perm("magasin.loading_check.modify")),
):
    cid = _company_id(user)
    obj = _get_or_404(db, MagcLoadingCheck, ident, "Controles de chargement")
    if obj.company_id != cid:
        raise HTTPException(403, "Acces refuse.")
    obj.is_active = False
    db.commit()
    db.refresh(obj)
    return obj


# ─── Controles de reception ─────────────────────────────────────────────────

@router.get("/magc-receiving-checks", response_model=List[MagcReceivingCheckOut])
def list_receiving_check(statut: Optional[str] = None, db: Session = Depends(get_db),
    user: User = Depends(require_perm("magasin.receiving_check.read")),
):
    cid = _company_id(user)
    return _scoped_list(db, MagcReceivingCheck, cid, {"statut": statut})


@router.post("/magc-receiving-checks", response_model=MagcReceivingCheckOut, status_code=201)
def create_receiving_check(
    payload: MagcReceivingCheckCreate,
    db: Session = Depends(get_db),
    user: User = Depends(require_perm("magasin.receiving_check.create")),
):
    cid = _company_id(user)
    data = payload.model_dump(exclude_unset=True)
    _check_unique(db, MagcReceivingCheck, "reference", data.get("reference"), "reference", cid)
    obj = MagcReceivingCheck(company_id=cid)
    _apply(data, obj)
    db.add(obj)
    db.commit()
    db.refresh(obj)
    return obj


@router.put("/magc-receiving-checks/{ident}", response_model=MagcReceivingCheckOut)
def update_receiving_check(
    ident: int,
    payload: MagcReceivingCheckUpdate,
    db: Session = Depends(get_db),
    user: User = Depends(require_perm("magasin.receiving_check.modify")),
):
    cid = _company_id(user)
    obj = _get_or_404(db, MagcReceivingCheck, ident, "Controles de reception")
    if obj.company_id != cid:
        raise HTTPException(403, "Acces refuse.")
    _apply(payload.model_dump(exclude_unset=True), obj)
    db.commit()
    db.refresh(obj)
    return obj


@router.delete("/magc-receiving-checks/{ident}", response_model=MagcReceivingCheckOut)
def delete_receiving_check(
    ident: int,
    db: Session = Depends(get_db),
    user: User = Depends(require_perm("magasin.receiving_check.modify")),
):
    cid = _company_id(user)
    obj = _get_or_404(db, MagcReceivingCheck, ident, "Controles de reception")
    if obj.company_id != cid:
        raise HTTPException(403, "Acces refuse.")
    obj.is_active = False
    db.commit()
    db.refresh(obj)
    return obj


# ─── Exceptions de rangement ─────────────────────────────────────────────────

@router.get("/magc-putaway-exceptions", response_model=List[MagcPutawayExceptionOut])
def list_putaway_exception(statut: Optional[str] = None, db: Session = Depends(get_db),
    user: User = Depends(require_perm("magasin.putaway_exception.read")),
):
    cid = _company_id(user)
    return _scoped_list(db, MagcPutawayException, cid, {"statut": statut})


@router.post("/magc-putaway-exceptions", response_model=MagcPutawayExceptionOut, status_code=201)
def create_putaway_exception(
    payload: MagcPutawayExceptionCreate,
    db: Session = Depends(get_db),
    user: User = Depends(require_perm("magasin.putaway_exception.create")),
):
    cid = _company_id(user)
    data = payload.model_dump(exclude_unset=True)
    _check_unique(db, MagcPutawayException, "reference", data.get("reference"), "reference", cid)
    obj = MagcPutawayException(company_id=cid)
    _apply(data, obj)
    db.add(obj)
    db.commit()
    db.refresh(obj)
    return obj


@router.put("/magc-putaway-exceptions/{ident}", response_model=MagcPutawayExceptionOut)
def update_putaway_exception(
    ident: int,
    payload: MagcPutawayExceptionUpdate,
    db: Session = Depends(get_db),
    user: User = Depends(require_perm("magasin.putaway_exception.modify")),
):
    cid = _company_id(user)
    obj = _get_or_404(db, MagcPutawayException, ident, "Exceptions de rangement")
    if obj.company_id != cid:
        raise HTTPException(403, "Acces refuse.")
    _apply(payload.model_dump(exclude_unset=True), obj)
    db.commit()
    db.refresh(obj)
    return obj


@router.delete("/magc-putaway-exceptions/{ident}", response_model=MagcPutawayExceptionOut)
def delete_putaway_exception(
    ident: int,
    db: Session = Depends(get_db),
    user: User = Depends(require_perm("magasin.putaway_exception.modify")),
):
    cid = _company_id(user)
    obj = _get_or_404(db, MagcPutawayException, ident, "Exceptions de rangement")
    if obj.company_id != cid:
        raise HTTPException(403, "Acces refuse.")
    obj.is_active = False
    db.commit()
    db.refresh(obj)
    return obj


# ─── Zone de pre-expedition ─────────────────────────────────────────────────

@router.get("/magc-order-staging", response_model=List[MagcOrderStagingOut])
def list_order_staging(statut: Optional[str] = None, db: Session = Depends(get_db),
    user: User = Depends(require_perm("magasin.order_staging.read")),
):
    cid = _company_id(user)
    return _scoped_list(db, MagcOrderStaging, cid, {"statut": statut})


@router.post("/magc-order-staging", response_model=MagcOrderStagingOut, status_code=201)
def create_order_staging(
    payload: MagcOrderStagingCreate,
    db: Session = Depends(get_db),
    user: User = Depends(require_perm("magasin.order_staging.create")),
):
    cid = _company_id(user)
    data = payload.model_dump(exclude_unset=True)
    _check_unique(db, MagcOrderStaging, "reference", data.get("reference"), "reference", cid)
    obj = MagcOrderStaging(company_id=cid)
    _apply(data, obj)
    db.add(obj)
    db.commit()
    db.refresh(obj)
    return obj


@router.put("/magc-order-staging/{ident}", response_model=MagcOrderStagingOut)
def update_order_staging(
    ident: int,
    payload: MagcOrderStagingUpdate,
    db: Session = Depends(get_db),
    user: User = Depends(require_perm("magasin.order_staging.modify")),
):
    cid = _company_id(user)
    obj = _get_or_404(db, MagcOrderStaging, ident, "Zone de pre-expedition")
    if obj.company_id != cid:
        raise HTTPException(403, "Acces refuse.")
    _apply(payload.model_dump(exclude_unset=True), obj)
    db.commit()
    db.refresh(obj)
    return obj


@router.delete("/magc-order-staging/{ident}", response_model=MagcOrderStagingOut)
def delete_order_staging(
    ident: int,
    db: Session = Depends(get_db),
    user: User = Depends(require_perm("magasin.order_staging.modify")),
):
    cid = _company_id(user)
    obj = _get_or_404(db, MagcOrderStaging, ident, "Zone de pre-expedition")
    if obj.company_id != cid:
        raise HTTPException(403, "Acces refuse.")
    obj.is_active = False
    db.commit()
    db.refresh(obj)
    return obj


# ─── Controles chaine du froid ─────────────────────────────────────────────────

@router.get("/magc-cold-chain-checks", response_model=List[MagcColdChainCheckOut])
def list_cold_chain_check(statut: Optional[str] = None, db: Session = Depends(get_db),
    user: User = Depends(require_perm("magasin.cold_chain_check.read")),
):
    cid = _company_id(user)
    return _scoped_list(db, MagcColdChainCheck, cid, {"statut": statut})


@router.post("/magc-cold-chain-checks", response_model=MagcColdChainCheckOut, status_code=201)
def create_cold_chain_check(
    payload: MagcColdChainCheckCreate,
    db: Session = Depends(get_db),
    user: User = Depends(require_perm("magasin.cold_chain_check.create")),
):
    cid = _company_id(user)
    data = payload.model_dump(exclude_unset=True)
    _check_unique(db, MagcColdChainCheck, "reference", data.get("reference"), "reference", cid)
    obj = MagcColdChainCheck(company_id=cid)
    _apply(data, obj)
    db.add(obj)
    db.commit()
    db.refresh(obj)
    return obj


@router.put("/magc-cold-chain-checks/{ident}", response_model=MagcColdChainCheckOut)
def update_cold_chain_check(
    ident: int,
    payload: MagcColdChainCheckUpdate,
    db: Session = Depends(get_db),
    user: User = Depends(require_perm("magasin.cold_chain_check.modify")),
):
    cid = _company_id(user)
    obj = _get_or_404(db, MagcColdChainCheck, ident, "Controles chaine du froid")
    if obj.company_id != cid:
        raise HTTPException(403, "Acces refuse.")
    _apply(payload.model_dump(exclude_unset=True), obj)
    db.commit()
    db.refresh(obj)
    return obj


@router.delete("/magc-cold-chain-checks/{ident}", response_model=MagcColdChainCheckOut)
def delete_cold_chain_check(
    ident: int,
    db: Session = Depends(get_db),
    user: User = Depends(require_perm("magasin.cold_chain_check.modify")),
):
    cid = _company_id(user)
    obj = _get_or_404(db, MagcColdChainCheck, ident, "Controles chaine du froid")
    if obj.company_id != cid:
        raise HTTPException(403, "Acces refuse.")
    obj.is_active = False
    db.commit()
    db.refresh(obj)
    return obj


# ─── Manutention matieres dangereuses ─────────────────────────────────────────────────

@router.get("/magc-hazmat-handling", response_model=List[MagcHazmatHandlingOut])
def list_hazmat_handling(statut: Optional[str] = None, db: Session = Depends(get_db),
    user: User = Depends(require_perm("magasin.hazmat_handling.read")),
):
    cid = _company_id(user)
    return _scoped_list(db, MagcHazmatHandling, cid, {"statut": statut})


@router.post("/magc-hazmat-handling", response_model=MagcHazmatHandlingOut, status_code=201)
def create_hazmat_handling(
    payload: MagcHazmatHandlingCreate,
    db: Session = Depends(get_db),
    user: User = Depends(require_perm("magasin.hazmat_handling.create")),
):
    cid = _company_id(user)
    data = payload.model_dump(exclude_unset=True)
    _check_unique(db, MagcHazmatHandling, "reference", data.get("reference"), "reference", cid)
    obj = MagcHazmatHandling(company_id=cid)
    _apply(data, obj)
    db.add(obj)
    db.commit()
    db.refresh(obj)
    return obj


@router.put("/magc-hazmat-handling/{ident}", response_model=MagcHazmatHandlingOut)
def update_hazmat_handling(
    ident: int,
    payload: MagcHazmatHandlingUpdate,
    db: Session = Depends(get_db),
    user: User = Depends(require_perm("magasin.hazmat_handling.modify")),
):
    cid = _company_id(user)
    obj = _get_or_404(db, MagcHazmatHandling, ident, "Manutention matieres dangereuses")
    if obj.company_id != cid:
        raise HTTPException(403, "Acces refuse.")
    _apply(payload.model_dump(exclude_unset=True), obj)
    db.commit()
    db.refresh(obj)
    return obj


@router.delete("/magc-hazmat-handling/{ident}", response_model=MagcHazmatHandlingOut)
def delete_hazmat_handling(
    ident: int,
    db: Session = Depends(get_db),
    user: User = Depends(require_perm("magasin.hazmat_handling.modify")),
):
    cid = _company_id(user)
    obj = _get_or_404(db, MagcHazmatHandling, ident, "Manutention matieres dangereuses")
    if obj.company_id != cid:
        raise HTTPException(403, "Acces refuse.")
    obj.is_active = False
    db.commit()
    db.refresh(obj)
    return obj


# ─── Affectations de quai ─────────────────────────────────────────────────

@router.get("/magc-dock-assignments", response_model=List[MagcDockAssignmentOut])
def list_dock_assignment(statut: Optional[str] = None, db: Session = Depends(get_db),
    user: User = Depends(require_perm("magasin.dock_assignment.read")),
):
    cid = _company_id(user)
    return _scoped_list(db, MagcDockAssignment, cid, {"statut": statut})


@router.post("/magc-dock-assignments", response_model=MagcDockAssignmentOut, status_code=201)
def create_dock_assignment(
    payload: MagcDockAssignmentCreate,
    db: Session = Depends(get_db),
    user: User = Depends(require_perm("magasin.dock_assignment.create")),
):
    cid = _company_id(user)
    data = payload.model_dump(exclude_unset=True)
    _check_unique(db, MagcDockAssignment, "reference", data.get("reference"), "reference", cid)
    obj = MagcDockAssignment(company_id=cid)
    _apply(data, obj)
    db.add(obj)
    db.commit()
    db.refresh(obj)
    return obj


@router.put("/magc-dock-assignments/{ident}", response_model=MagcDockAssignmentOut)
def update_dock_assignment(
    ident: int,
    payload: MagcDockAssignmentUpdate,
    db: Session = Depends(get_db),
    user: User = Depends(require_perm("magasin.dock_assignment.modify")),
):
    cid = _company_id(user)
    obj = _get_or_404(db, MagcDockAssignment, ident, "Affectations de quai")
    if obj.company_id != cid:
        raise HTTPException(403, "Acces refuse.")
    _apply(payload.model_dump(exclude_unset=True), obj)
    db.commit()
    db.refresh(obj)
    return obj


@router.delete("/magc-dock-assignments/{ident}", response_model=MagcDockAssignmentOut)
def delete_dock_assignment(
    ident: int,
    db: Session = Depends(get_db),
    user: User = Depends(require_perm("magasin.dock_assignment.modify")),
):
    cid = _company_id(user)
    obj = _get_or_404(db, MagcDockAssignment, ident, "Affectations de quai")
    if obj.company_id != cid:
        raise HTTPException(403, "Acces refuse.")
    obj.is_active = False
    db.commit()
    db.refresh(obj)
    return obj

