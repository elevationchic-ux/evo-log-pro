"""Routeur CRUD genere pour parc-vehicules (expansion)."""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import Optional, List

from app.core.database import get_db
from app.core.permissions import require_perm
from app.models.user import User
from app.models.parc_b_deep import (
    ParcDriverAssignment,
    ParcGeofenceZone,
    ParcInspectionChecklist,
    ParcLeaseContract,
    ParcTollPass,
)
from app.schemas.parc_b_deep import (
    ParcDriverAssignmentCreate, ParcDriverAssignmentUpdate, ParcDriverAssignmentOut,
    ParcGeofenceZoneCreate, ParcGeofenceZoneUpdate, ParcGeofenceZoneOut,
    ParcInspectionChecklistCreate, ParcInspectionChecklistUpdate, ParcInspectionChecklistOut,
    ParcLeaseContractCreate, ParcLeaseContractUpdate, ParcLeaseContractOut,
    ParcTollPassCreate, ParcTollPassUpdate, ParcTollPassOut,
)

router = APIRouter(tags=["parc-vehicules (expansion)"])


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

@router.get("/nomenclatures", summary="Vocabulaire metier parc-vehicules")
def nomenclatures(user: User = Depends(require_perm("parc.nomenclature.read"))):
    from app.models import parc_b_deep as _md
    import enum as _pyenum
    out = {}
    for name in dir(_md):
        obj = getattr(_md, name)
        if isinstance(obj, type) and issubclass(obj, _pyenum.Enum) and obj is not _pyenum.Enum:
            out[name.lower()] = [{"code": m.name, "valeur": m.value} for m in obj]
    return out


# ─── Affectation chauffeurs ─────────────────────────────────────────────────

@router.get("/parcb-driver-assignments", response_model=List[ParcDriverAssignmentOut])
def list_driver_assignment(statut: Optional[str] = None, db: Session = Depends(get_db),
    user: User = Depends(require_perm("parc.driver_assignment.read")),
):
    cid = _company_id(user)
    return _scoped_list(db, ParcDriverAssignment, cid, {"statut": statut})


@router.post("/parcb-driver-assignments", response_model=ParcDriverAssignmentOut, status_code=201)
def create_driver_assignment(
    payload: ParcDriverAssignmentCreate,
    db: Session = Depends(get_db),
    user: User = Depends(require_perm("parc.driver_assignment.create")),
):
    cid = _company_id(user)
    data = payload.model_dump(exclude_unset=True)
    _check_unique(db, ParcDriverAssignment, "reference", data.get("reference"), "reference", cid)
    obj = ParcDriverAssignment(company_id=cid)
    _apply(data, obj)
    db.add(obj)
    db.commit()
    db.refresh(obj)
    return obj


@router.put("/parcb-driver-assignments/{ident}", response_model=ParcDriverAssignmentOut)
def update_driver_assignment(
    ident: int,
    payload: ParcDriverAssignmentUpdate,
    db: Session = Depends(get_db),
    user: User = Depends(require_perm("parc.driver_assignment.modify")),
):
    cid = _company_id(user)
    obj = _get_or_404(db, ParcDriverAssignment, ident, "Affectation chauffeurs")
    if obj.company_id != cid:
        raise HTTPException(403, "Acces refuse.")
    _apply(payload.model_dump(exclude_unset=True), obj)
    db.commit()
    db.refresh(obj)
    return obj


@router.delete("/parcb-driver-assignments/{ident}", response_model=ParcDriverAssignmentOut)
def delete_driver_assignment(
    ident: int,
    db: Session = Depends(get_db),
    user: User = Depends(require_perm("parc.driver_assignment.modify")),
):
    cid = _company_id(user)
    obj = _get_or_404(db, ParcDriverAssignment, ident, "Affectation chauffeurs")
    if obj.company_id != cid:
        raise HTTPException(403, "Acces refuse.")
    obj.is_active = False
    db.commit()
    db.refresh(obj)
    return obj


# ─── Zones geoclotees ─────────────────────────────────────────────────

@router.get("/parcb-geofence-zones", response_model=List[ParcGeofenceZoneOut])
def list_geofence_zone(statut: Optional[str] = None, db: Session = Depends(get_db),
    user: User = Depends(require_perm("parc.geofence_zone.read")),
):
    cid = _company_id(user)
    return _scoped_list(db, ParcGeofenceZone, cid, {"statut": statut})


@router.post("/parcb-geofence-zones", response_model=ParcGeofenceZoneOut, status_code=201)
def create_geofence_zone(
    payload: ParcGeofenceZoneCreate,
    db: Session = Depends(get_db),
    user: User = Depends(require_perm("parc.geofence_zone.create")),
):
    cid = _company_id(user)
    data = payload.model_dump(exclude_unset=True)
    _check_unique(db, ParcGeofenceZone, "code_zone", data.get("code_zone"), "code_zone", cid)
    obj = ParcGeofenceZone(company_id=cid)
    _apply(data, obj)
    db.add(obj)
    db.commit()
    db.refresh(obj)
    return obj


@router.put("/parcb-geofence-zones/{ident}", response_model=ParcGeofenceZoneOut)
def update_geofence_zone(
    ident: int,
    payload: ParcGeofenceZoneUpdate,
    db: Session = Depends(get_db),
    user: User = Depends(require_perm("parc.geofence_zone.modify")),
):
    cid = _company_id(user)
    obj = _get_or_404(db, ParcGeofenceZone, ident, "Zones geoclotees")
    if obj.company_id != cid:
        raise HTTPException(403, "Acces refuse.")
    _apply(payload.model_dump(exclude_unset=True), obj)
    db.commit()
    db.refresh(obj)
    return obj


@router.delete("/parcb-geofence-zones/{ident}", response_model=ParcGeofenceZoneOut)
def delete_geofence_zone(
    ident: int,
    db: Session = Depends(get_db),
    user: User = Depends(require_perm("parc.geofence_zone.modify")),
):
    cid = _company_id(user)
    obj = _get_or_404(db, ParcGeofenceZone, ident, "Zones geoclotees")
    if obj.company_id != cid:
        raise HTTPException(403, "Acces refuse.")
    obj.is_active = False
    db.commit()
    db.refresh(obj)
    return obj


# ─── Checklists de controle ─────────────────────────────────────────────────

@router.get("/parcb-inspection-checklists", response_model=List[ParcInspectionChecklistOut])
def list_inspection_checklist(statut: Optional[str] = None, db: Session = Depends(get_db),
    user: User = Depends(require_perm("parc.inspection_checklist.read")),
):
    cid = _company_id(user)
    return _scoped_list(db, ParcInspectionChecklist, cid, {"statut": statut})


@router.post("/parcb-inspection-checklists", response_model=ParcInspectionChecklistOut, status_code=201)
def create_inspection_checklist(
    payload: ParcInspectionChecklistCreate,
    db: Session = Depends(get_db),
    user: User = Depends(require_perm("parc.inspection_checklist.create")),
):
    cid = _company_id(user)
    data = payload.model_dump(exclude_unset=True)
    _check_unique(db, ParcInspectionChecklist, "reference", data.get("reference"), "reference", cid)
    obj = ParcInspectionChecklist(company_id=cid)
    _apply(data, obj)
    db.add(obj)
    db.commit()
    db.refresh(obj)
    return obj


@router.put("/parcb-inspection-checklists/{ident}", response_model=ParcInspectionChecklistOut)
def update_inspection_checklist(
    ident: int,
    payload: ParcInspectionChecklistUpdate,
    db: Session = Depends(get_db),
    user: User = Depends(require_perm("parc.inspection_checklist.modify")),
):
    cid = _company_id(user)
    obj = _get_or_404(db, ParcInspectionChecklist, ident, "Checklists de controle")
    if obj.company_id != cid:
        raise HTTPException(403, "Acces refuse.")
    _apply(payload.model_dump(exclude_unset=True), obj)
    db.commit()
    db.refresh(obj)
    return obj


@router.delete("/parcb-inspection-checklists/{ident}", response_model=ParcInspectionChecklistOut)
def delete_inspection_checklist(
    ident: int,
    db: Session = Depends(get_db),
    user: User = Depends(require_perm("parc.inspection_checklist.modify")),
):
    cid = _company_id(user)
    obj = _get_or_404(db, ParcInspectionChecklist, ident, "Checklists de controle")
    if obj.company_id != cid:
        raise HTTPException(403, "Acces refuse.")
    obj.is_active = False
    db.commit()
    db.refresh(obj)
    return obj


# ─── Contrats de location / leasing ─────────────────────────────────────────────────

@router.get("/parcb-lease-contracts", response_model=List[ParcLeaseContractOut])
def list_lease_contract(statut: Optional[str] = None, db: Session = Depends(get_db),
    user: User = Depends(require_perm("parc.lease_contract.read")),
):
    cid = _company_id(user)
    return _scoped_list(db, ParcLeaseContract, cid, {"statut": statut})


@router.post("/parcb-lease-contracts", response_model=ParcLeaseContractOut, status_code=201)
def create_lease_contract(
    payload: ParcLeaseContractCreate,
    db: Session = Depends(get_db),
    user: User = Depends(require_perm("parc.lease_contract.create")),
):
    cid = _company_id(user)
    data = payload.model_dump(exclude_unset=True)
    _check_unique(db, ParcLeaseContract, "numero_contrat", data.get("numero_contrat"), "numero_contrat", cid)
    obj = ParcLeaseContract(company_id=cid)
    _apply(data, obj)
    db.add(obj)
    db.commit()
    db.refresh(obj)
    return obj


@router.put("/parcb-lease-contracts/{ident}", response_model=ParcLeaseContractOut)
def update_lease_contract(
    ident: int,
    payload: ParcLeaseContractUpdate,
    db: Session = Depends(get_db),
    user: User = Depends(require_perm("parc.lease_contract.modify")),
):
    cid = _company_id(user)
    obj = _get_or_404(db, ParcLeaseContract, ident, "Contrats de location / leasing")
    if obj.company_id != cid:
        raise HTTPException(403, "Acces refuse.")
    _apply(payload.model_dump(exclude_unset=True), obj)
    db.commit()
    db.refresh(obj)
    return obj


@router.delete("/parcb-lease-contracts/{ident}", response_model=ParcLeaseContractOut)
def delete_lease_contract(
    ident: int,
    db: Session = Depends(get_db),
    user: User = Depends(require_perm("parc.lease_contract.modify")),
):
    cid = _company_id(user)
    obj = _get_or_404(db, ParcLeaseContract, ident, "Contrats de location / leasing")
    if obj.company_id != cid:
        raise HTTPException(403, "Acces refuse.")
    obj.is_active = False
    db.commit()
    db.refresh(obj)
    return obj


# ─── Badges de peage / telepeage ─────────────────────────────────────────────────

@router.get("/parcb-toll-passes", response_model=List[ParcTollPassOut])
def list_toll_pass(statut: Optional[str] = None, db: Session = Depends(get_db),
    user: User = Depends(require_perm("parc.toll_pass.read")),
):
    cid = _company_id(user)
    return _scoped_list(db, ParcTollPass, cid, {"statut": statut})


@router.post("/parcb-toll-passes", response_model=ParcTollPassOut, status_code=201)
def create_toll_pass(
    payload: ParcTollPassCreate,
    db: Session = Depends(get_db),
    user: User = Depends(require_perm("parc.toll_pass.create")),
):
    cid = _company_id(user)
    data = payload.model_dump(exclude_unset=True)
    _check_unique(db, ParcTollPass, "numero_badge", data.get("numero_badge"), "numero_badge", cid)
    obj = ParcTollPass(company_id=cid)
    _apply(data, obj)
    db.add(obj)
    db.commit()
    db.refresh(obj)
    return obj


@router.put("/parcb-toll-passes/{ident}", response_model=ParcTollPassOut)
def update_toll_pass(
    ident: int,
    payload: ParcTollPassUpdate,
    db: Session = Depends(get_db),
    user: User = Depends(require_perm("parc.toll_pass.modify")),
):
    cid = _company_id(user)
    obj = _get_or_404(db, ParcTollPass, ident, "Badges de peage / telepeage")
    if obj.company_id != cid:
        raise HTTPException(403, "Acces refuse.")
    _apply(payload.model_dump(exclude_unset=True), obj)
    db.commit()
    db.refresh(obj)
    return obj


@router.delete("/parcb-toll-passes/{ident}", response_model=ParcTollPassOut)
def delete_toll_pass(
    ident: int,
    db: Session = Depends(get_db),
    user: User = Depends(require_perm("parc.toll_pass.modify")),
):
    cid = _company_id(user)
    obj = _get_or_404(db, ParcTollPass, ident, "Badges de peage / telepeage")
    if obj.company_id != cid:
        raise HTTPException(403, "Acces refuse.")
    obj.is_active = False
    db.commit()
    db.refresh(obj)
    return obj

