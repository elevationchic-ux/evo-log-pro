"""Routeur CRUD genere pour parc-vehicules (expansion)."""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import Optional, List

from app.core.database import get_db
from app.core.permissions import require_perm
from app.models.user import User
from app.models.parc_deep import (
    VehicleInventory,
    TyreRecord,
    SparePart,
    WorkshopAppointment,
    InsuranceClaim,
    RegistrationRecord,
    TechnicalVisit,
    FuelConsumption,
    VehicleLifecycle,
    CostAnalysis,
)
from app.schemas.parc_deep import (
    VehicleInventoryCreate, VehicleInventoryUpdate, VehicleInventoryOut,
    TyreRecordCreate, TyreRecordUpdate, TyreRecordOut,
    SparePartCreate, SparePartUpdate, SparePartOut,
    WorkshopAppointmentCreate, WorkshopAppointmentUpdate, WorkshopAppointmentOut,
    InsuranceClaimCreate, InsuranceClaimUpdate, InsuranceClaimOut,
    RegistrationRecordCreate, RegistrationRecordUpdate, RegistrationRecordOut,
    TechnicalVisitCreate, TechnicalVisitUpdate, TechnicalVisitOut,
    FuelConsumptionCreate, FuelConsumptionUpdate, FuelConsumptionOut,
    VehicleLifecycleCreate, VehicleLifecycleUpdate, VehicleLifecycleOut,
    CostAnalysisCreate, CostAnalysisUpdate, CostAnalysisOut,
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
    from app.models import parc_deep as _md
    import enum as _pyenum
    out = {}
    for name in dir(_md):
        obj = getattr(_md, name)
        if isinstance(obj, type) and issubclass(obj, _pyenum.Enum) and obj is not _pyenum.Enum:
            out[name.lower()] = [{"code": m.name, "valeur": m.value} for m in obj]
    return out


# ─── Inventaire complet du parc ─────────────────────────────────────────────────

@router.get("/vehicle-inventories", response_model=List[VehicleInventoryOut])
def list_vehicle_inventory(db: Session = Depends(get_db),
    user: User = Depends(require_perm("parc.vehicle_inventory.read")),
):
    cid = _company_id(user)
    return _scoped_list(db, VehicleInventory, cid)


@router.post("/vehicle-inventories", response_model=VehicleInventoryOut, status_code=201)
def create_vehicle_inventory(
    payload: VehicleInventoryCreate,
    db: Session = Depends(get_db),
    user: User = Depends(require_perm("parc.vehicle_inventory.create")),
):
    cid = _company_id(user)
    data = payload.model_dump(exclude_unset=True)
    _check_unique(db, VehicleInventory, "numero_serie", data.get("numero_serie"), "numero_serie", cid)
    obj = VehicleInventory(company_id=cid)
    _apply(data, obj)
    db.add(obj)
    db.commit()
    db.refresh(obj)
    return obj


@router.put("/vehicle-inventories/{ident}", response_model=VehicleInventoryOut)
def update_vehicle_inventory(
    ident: int,
    payload: VehicleInventoryUpdate,
    db: Session = Depends(get_db),
    user: User = Depends(require_perm("parc.vehicle_inventory.modify")),
):
    cid = _company_id(user)
    obj = _get_or_404(db, VehicleInventory, ident, "Inventaire complet du parc")
    if obj.company_id != cid:
        raise HTTPException(403, "Acces refuse.")
    _apply(payload.model_dump(exclude_unset=True), obj)
    db.commit()
    db.refresh(obj)
    return obj


@router.delete("/vehicle-inventories/{ident}", response_model=VehicleInventoryOut)
def delete_vehicle_inventory(
    ident: int,
    db: Session = Depends(get_db),
    user: User = Depends(require_perm("parc.vehicle_inventory.modify")),
):
    cid = _company_id(user)
    obj = _get_or_404(db, VehicleInventory, ident, "Inventaire complet du parc")
    if obj.company_id != cid:
        raise HTTPException(403, "Acces refuse.")
    obj.is_active = False
    db.commit()
    db.refresh(obj)
    return obj


# ─── Gestion pneumatiques ─────────────────────────────────────────────────

@router.get("/tyre-records", response_model=List[TyreRecordOut])
def list_tyre_management(statut: Optional[str] = None, db: Session = Depends(get_db),
    user: User = Depends(require_perm("parc.tyre_management.read")),
):
    cid = _company_id(user)
    return _scoped_list(db, TyreRecord, cid, {"statut": statut})


@router.post("/tyre-records", response_model=TyreRecordOut, status_code=201)
def create_tyre_management(
    payload: TyreRecordCreate,
    db: Session = Depends(get_db),
    user: User = Depends(require_perm("parc.tyre_management.create")),
):
    cid = _company_id(user)
    data = payload.model_dump(exclude_unset=True)
    _check_unique(db, TyreRecord, "numero_gomme", data.get("numero_gomme"), "numero_gomme", cid)
    obj = TyreRecord(company_id=cid)
    _apply(data, obj)
    db.add(obj)
    db.commit()
    db.refresh(obj)
    return obj


@router.put("/tyre-records/{ident}", response_model=TyreRecordOut)
def update_tyre_management(
    ident: int,
    payload: TyreRecordUpdate,
    db: Session = Depends(get_db),
    user: User = Depends(require_perm("parc.tyre_management.modify")),
):
    cid = _company_id(user)
    obj = _get_or_404(db, TyreRecord, ident, "Gestion pneumatiques")
    if obj.company_id != cid:
        raise HTTPException(403, "Acces refuse.")
    _apply(payload.model_dump(exclude_unset=True), obj)
    db.commit()
    db.refresh(obj)
    return obj


@router.delete("/tyre-records/{ident}", response_model=TyreRecordOut)
def delete_tyre_management(
    ident: int,
    db: Session = Depends(get_db),
    user: User = Depends(require_perm("parc.tyre_management.modify")),
):
    cid = _company_id(user)
    obj = _get_or_404(db, TyreRecord, ident, "Gestion pneumatiques")
    if obj.company_id != cid:
        raise HTTPException(403, "Acces refuse.")
    obj.is_active = False
    db.commit()
    db.refresh(obj)
    return obj


# ─── Pieces detachees / stock atelier ─────────────────────────────────────────────────

@router.get("/spare-parts", response_model=List[SparePartOut])
def list_spare_part(db: Session = Depends(get_db),
    user: User = Depends(require_perm("parc.spare_part.read")),
):
    cid = _company_id(user)
    return _scoped_list(db, SparePart, cid)


@router.post("/spare-parts", response_model=SparePartOut, status_code=201)
def create_spare_part(
    payload: SparePartCreate,
    db: Session = Depends(get_db),
    user: User = Depends(require_perm("parc.spare_part.create")),
):
    cid = _company_id(user)
    data = payload.model_dump(exclude_unset=True)
    _check_unique(db, SparePart, "code_piece", data.get("code_piece"), "code_piece", cid)
    obj = SparePart(company_id=cid)
    _apply(data, obj)
    db.add(obj)
    db.commit()
    db.refresh(obj)
    return obj


@router.put("/spare-parts/{ident}", response_model=SparePartOut)
def update_spare_part(
    ident: int,
    payload: SparePartUpdate,
    db: Session = Depends(get_db),
    user: User = Depends(require_perm("parc.spare_part.modify")),
):
    cid = _company_id(user)
    obj = _get_or_404(db, SparePart, ident, "Pieces detachees / stock atelier")
    if obj.company_id != cid:
        raise HTTPException(403, "Acces refuse.")
    _apply(payload.model_dump(exclude_unset=True), obj)
    db.commit()
    db.refresh(obj)
    return obj


@router.delete("/spare-parts/{ident}", response_model=SparePartOut)
def delete_spare_part(
    ident: int,
    db: Session = Depends(get_db),
    user: User = Depends(require_perm("parc.spare_part.modify")),
):
    cid = _company_id(user)
    obj = _get_or_404(db, SparePart, ident, "Pieces detachees / stock atelier")
    if obj.company_id != cid:
        raise HTTPException(403, "Acces refuse.")
    obj.is_active = False
    db.commit()
    db.refresh(obj)
    return obj


# ─── Planification atelier ─────────────────────────────────────────────────

@router.get("/workshop-appointments", response_model=List[WorkshopAppointmentOut])
def list_workshop_scheduling(statut: Optional[str] = None, db: Session = Depends(get_db),
    user: User = Depends(require_perm("parc.workshop_scheduling.read")),
):
    cid = _company_id(user)
    return _scoped_list(db, WorkshopAppointment, cid, {"statut": statut})


@router.post("/workshop-appointments", response_model=WorkshopAppointmentOut, status_code=201)
def create_workshop_scheduling(
    payload: WorkshopAppointmentCreate,
    db: Session = Depends(get_db),
    user: User = Depends(require_perm("parc.workshop_scheduling.create")),
):
    cid = _company_id(user)
    data = payload.model_dump(exclude_unset=True)
    _check_unique(db, WorkshopAppointment, "reference", data.get("reference"), "reference", cid)
    obj = WorkshopAppointment(company_id=cid)
    _apply(data, obj)
    db.add(obj)
    db.commit()
    db.refresh(obj)
    return obj


@router.put("/workshop-appointments/{ident}", response_model=WorkshopAppointmentOut)
def update_workshop_scheduling(
    ident: int,
    payload: WorkshopAppointmentUpdate,
    db: Session = Depends(get_db),
    user: User = Depends(require_perm("parc.workshop_scheduling.modify")),
):
    cid = _company_id(user)
    obj = _get_or_404(db, WorkshopAppointment, ident, "Planification atelier")
    if obj.company_id != cid:
        raise HTTPException(403, "Acces refuse.")
    _apply(payload.model_dump(exclude_unset=True), obj)
    db.commit()
    db.refresh(obj)
    return obj


@router.delete("/workshop-appointments/{ident}", response_model=WorkshopAppointmentOut)
def delete_workshop_scheduling(
    ident: int,
    db: Session = Depends(get_db),
    user: User = Depends(require_perm("parc.workshop_scheduling.modify")),
):
    cid = _company_id(user)
    obj = _get_or_404(db, WorkshopAppointment, ident, "Planification atelier")
    if obj.company_id != cid:
        raise HTTPException(403, "Acces refuse.")
    obj.is_active = False
    db.commit()
    db.refresh(obj)
    return obj


# ─── Sinistres et assurances ─────────────────────────────────────────────────

@router.get("/insurance-claims", response_model=List[InsuranceClaimOut])
def list_insurance_claim(statut: Optional[str] = None, db: Session = Depends(get_db),
    user: User = Depends(require_perm("parc.insurance_claim.read")),
):
    cid = _company_id(user)
    return _scoped_list(db, InsuranceClaim, cid, {"statut": statut})


@router.post("/insurance-claims", response_model=InsuranceClaimOut, status_code=201)
def create_insurance_claim(
    payload: InsuranceClaimCreate,
    db: Session = Depends(get_db),
    user: User = Depends(require_perm("parc.insurance_claim.create")),
):
    cid = _company_id(user)
    data = payload.model_dump(exclude_unset=True)
    _check_unique(db, InsuranceClaim, "numero_sinistre", data.get("numero_sinistre"), "numero_sinistre", cid)
    obj = InsuranceClaim(company_id=cid)
    _apply(data, obj)
    db.add(obj)
    db.commit()
    db.refresh(obj)
    return obj


@router.put("/insurance-claims/{ident}", response_model=InsuranceClaimOut)
def update_insurance_claim(
    ident: int,
    payload: InsuranceClaimUpdate,
    db: Session = Depends(get_db),
    user: User = Depends(require_perm("parc.insurance_claim.modify")),
):
    cid = _company_id(user)
    obj = _get_or_404(db, InsuranceClaim, ident, "Sinistres et assurances")
    if obj.company_id != cid:
        raise HTTPException(403, "Acces refuse.")
    _apply(payload.model_dump(exclude_unset=True), obj)
    db.commit()
    db.refresh(obj)
    return obj


@router.delete("/insurance-claims/{ident}", response_model=InsuranceClaimOut)
def delete_insurance_claim(
    ident: int,
    db: Session = Depends(get_db),
    user: User = Depends(require_perm("parc.insurance_claim.modify")),
):
    cid = _company_id(user)
    obj = _get_or_404(db, InsuranceClaim, ident, "Sinistres et assurances")
    if obj.company_id != cid:
        raise HTTPException(403, "Acces refuse.")
    obj.is_active = False
    db.commit()
    db.refresh(obj)
    return obj


# ─── Suivi immatriculation ─────────────────────────────────────────────────

@router.get("/registration-records", response_model=List[RegistrationRecordOut])
def list_registration_tracking(statut: Optional[str] = None, db: Session = Depends(get_db),
    user: User = Depends(require_perm("parc.registration_tracking.read")),
):
    cid = _company_id(user)
    return _scoped_list(db, RegistrationRecord, cid, {"statut": statut})


@router.post("/registration-records", response_model=RegistrationRecordOut, status_code=201)
def create_registration_tracking(
    payload: RegistrationRecordCreate,
    db: Session = Depends(get_db),
    user: User = Depends(require_perm("parc.registration_tracking.create")),
):
    cid = _company_id(user)
    data = payload.model_dump(exclude_unset=True)
    _check_unique(db, RegistrationRecord, "numero_immatriculation", data.get("numero_immatriculation"), "numero_immatriculation", cid)
    obj = RegistrationRecord(company_id=cid)
    _apply(data, obj)
    db.add(obj)
    db.commit()
    db.refresh(obj)
    return obj


@router.put("/registration-records/{ident}", response_model=RegistrationRecordOut)
def update_registration_tracking(
    ident: int,
    payload: RegistrationRecordUpdate,
    db: Session = Depends(get_db),
    user: User = Depends(require_perm("parc.registration_tracking.modify")),
):
    cid = _company_id(user)
    obj = _get_or_404(db, RegistrationRecord, ident, "Suivi immatriculation")
    if obj.company_id != cid:
        raise HTTPException(403, "Acces refuse.")
    _apply(payload.model_dump(exclude_unset=True), obj)
    db.commit()
    db.refresh(obj)
    return obj


@router.delete("/registration-records/{ident}", response_model=RegistrationRecordOut)
def delete_registration_tracking(
    ident: int,
    db: Session = Depends(get_db),
    user: User = Depends(require_perm("parc.registration_tracking.modify")),
):
    cid = _company_id(user)
    obj = _get_or_404(db, RegistrationRecord, ident, "Suivi immatriculation")
    if obj.company_id != cid:
        raise HTTPException(403, "Acces refuse.")
    obj.is_active = False
    db.commit()
    db.refresh(obj)
    return obj


# ─── Visites techniques periodiques ─────────────────────────────────────────────────

@router.get("/technical-visits", response_model=List[TechnicalVisitOut])
def list_technical_visit(statut: Optional[str] = None, db: Session = Depends(get_db),
    user: User = Depends(require_perm("parc.technical_visit.read")),
):
    cid = _company_id(user)
    return _scoped_list(db, TechnicalVisit, cid, {"statut": statut})


@router.post("/technical-visits", response_model=TechnicalVisitOut, status_code=201)
def create_technical_visit(
    payload: TechnicalVisitCreate,
    db: Session = Depends(get_db),
    user: User = Depends(require_perm("parc.technical_visit.create")),
):
    cid = _company_id(user)
    data = payload.model_dump(exclude_unset=True)
    _check_unique(db, TechnicalVisit, "numero_pv", data.get("numero_pv"), "numero_pv", cid)
    obj = TechnicalVisit(company_id=cid)
    _apply(data, obj)
    db.add(obj)
    db.commit()
    db.refresh(obj)
    return obj


@router.put("/technical-visits/{ident}", response_model=TechnicalVisitOut)
def update_technical_visit(
    ident: int,
    payload: TechnicalVisitUpdate,
    db: Session = Depends(get_db),
    user: User = Depends(require_perm("parc.technical_visit.modify")),
):
    cid = _company_id(user)
    obj = _get_or_404(db, TechnicalVisit, ident, "Visites techniques periodiques")
    if obj.company_id != cid:
        raise HTTPException(403, "Acces refuse.")
    _apply(payload.model_dump(exclude_unset=True), obj)
    db.commit()
    db.refresh(obj)
    return obj


@router.delete("/technical-visits/{ident}", response_model=TechnicalVisitOut)
def delete_technical_visit(
    ident: int,
    db: Session = Depends(get_db),
    user: User = Depends(require_perm("parc.technical_visit.modify")),
):
    cid = _company_id(user)
    obj = _get_or_404(db, TechnicalVisit, ident, "Visites techniques periodiques")
    if obj.company_id != cid:
        raise HTTPException(403, "Acces refuse.")
    obj.is_active = False
    db.commit()
    db.refresh(obj)
    return obj


# ─── Consommation par vehicule ─────────────────────────────────────────────────

@router.get("/fuel-consumptions", response_model=List[FuelConsumptionOut])
def list_fuel_consumption(db: Session = Depends(get_db),
    user: User = Depends(require_perm("parc.fuel_consumption.read")),
):
    cid = _company_id(user)
    return _scoped_list(db, FuelConsumption, cid)


@router.post("/fuel-consumptions", response_model=FuelConsumptionOut, status_code=201)
def create_fuel_consumption(
    payload: FuelConsumptionCreate,
    db: Session = Depends(get_db),
    user: User = Depends(require_perm("parc.fuel_consumption.create")),
):
    cid = _company_id(user)
    data = payload.model_dump(exclude_unset=True)
    _check_unique(db, FuelConsumption, "reference", data.get("reference"), "reference", cid)
    obj = FuelConsumption(company_id=cid)
    _apply(data, obj)
    db.add(obj)
    db.commit()
    db.refresh(obj)
    return obj


@router.put("/fuel-consumptions/{ident}", response_model=FuelConsumptionOut)
def update_fuel_consumption(
    ident: int,
    payload: FuelConsumptionUpdate,
    db: Session = Depends(get_db),
    user: User = Depends(require_perm("parc.fuel_consumption.modify")),
):
    cid = _company_id(user)
    obj = _get_or_404(db, FuelConsumption, ident, "Consommation par vehicule")
    if obj.company_id != cid:
        raise HTTPException(403, "Acces refuse.")
    _apply(payload.model_dump(exclude_unset=True), obj)
    db.commit()
    db.refresh(obj)
    return obj


@router.delete("/fuel-consumptions/{ident}", response_model=FuelConsumptionOut)
def delete_fuel_consumption(
    ident: int,
    db: Session = Depends(get_db),
    user: User = Depends(require_perm("parc.fuel_consumption.modify")),
):
    cid = _company_id(user)
    obj = _get_or_404(db, FuelConsumption, ident, "Consommation par vehicule")
    if obj.company_id != cid:
        raise HTTPException(403, "Acces refuse.")
    obj.is_active = False
    db.commit()
    db.refresh(obj)
    return obj


# ─── Cycle de vie / reforme ─────────────────────────────────────────────────

@router.get("/vehicle-lifecycles", response_model=List[VehicleLifecycleOut])
def list_vehicle_lifecycle(db: Session = Depends(get_db),
    user: User = Depends(require_perm("parc.vehicle_lifecycle.read")),
):
    cid = _company_id(user)
    return _scoped_list(db, VehicleLifecycle, cid)


@router.post("/vehicle-lifecycles", response_model=VehicleLifecycleOut, status_code=201)
def create_vehicle_lifecycle(
    payload: VehicleLifecycleCreate,
    db: Session = Depends(get_db),
    user: User = Depends(require_perm("parc.vehicle_lifecycle.create")),
):
    cid = _company_id(user)
    data = payload.model_dump(exclude_unset=True)
    _check_unique(db, VehicleLifecycle, "reference", data.get("reference"), "reference", cid)
    obj = VehicleLifecycle(company_id=cid)
    _apply(data, obj)
    db.add(obj)
    db.commit()
    db.refresh(obj)
    return obj


@router.put("/vehicle-lifecycles/{ident}", response_model=VehicleLifecycleOut)
def update_vehicle_lifecycle(
    ident: int,
    payload: VehicleLifecycleUpdate,
    db: Session = Depends(get_db),
    user: User = Depends(require_perm("parc.vehicle_lifecycle.modify")),
):
    cid = _company_id(user)
    obj = _get_or_404(db, VehicleLifecycle, ident, "Cycle de vie / reforme")
    if obj.company_id != cid:
        raise HTTPException(403, "Acces refuse.")
    _apply(payload.model_dump(exclude_unset=True), obj)
    db.commit()
    db.refresh(obj)
    return obj


@router.delete("/vehicle-lifecycles/{ident}", response_model=VehicleLifecycleOut)
def delete_vehicle_lifecycle(
    ident: int,
    db: Session = Depends(get_db),
    user: User = Depends(require_perm("parc.vehicle_lifecycle.modify")),
):
    cid = _company_id(user)
    obj = _get_or_404(db, VehicleLifecycle, ident, "Cycle de vie / reforme")
    if obj.company_id != cid:
        raise HTTPException(403, "Acces refuse.")
    obj.is_active = False
    db.commit()
    db.refresh(obj)
    return obj


# ─── Analyse couts par vehicule ─────────────────────────────────────────────────

@router.get("/cost-analyses", response_model=List[CostAnalysisOut])
def list_cost_analysis(db: Session = Depends(get_db),
    user: User = Depends(require_perm("parc.cost_analysis.read")),
):
    cid = _company_id(user)
    return _scoped_list(db, CostAnalysis, cid)


@router.post("/cost-analyses", response_model=CostAnalysisOut, status_code=201)
def create_cost_analysis(
    payload: CostAnalysisCreate,
    db: Session = Depends(get_db),
    user: User = Depends(require_perm("parc.cost_analysis.create")),
):
    cid = _company_id(user)
    data = payload.model_dump(exclude_unset=True)
    _check_unique(db, CostAnalysis, "reference", data.get("reference"), "reference", cid)
    obj = CostAnalysis(company_id=cid)
    _apply(data, obj)
    db.add(obj)
    db.commit()
    db.refresh(obj)
    return obj


@router.put("/cost-analyses/{ident}", response_model=CostAnalysisOut)
def update_cost_analysis(
    ident: int,
    payload: CostAnalysisUpdate,
    db: Session = Depends(get_db),
    user: User = Depends(require_perm("parc.cost_analysis.modify")),
):
    cid = _company_id(user)
    obj = _get_or_404(db, CostAnalysis, ident, "Analyse couts par vehicule")
    if obj.company_id != cid:
        raise HTTPException(403, "Acces refuse.")
    _apply(payload.model_dump(exclude_unset=True), obj)
    db.commit()
    db.refresh(obj)
    return obj


@router.delete("/cost-analyses/{ident}", response_model=CostAnalysisOut)
def delete_cost_analysis(
    ident: int,
    db: Session = Depends(get_db),
    user: User = Depends(require_perm("parc.cost_analysis.modify")),
):
    cid = _company_id(user)
    obj = _get_or_404(db, CostAnalysis, ident, "Analyse couts par vehicule")
    if obj.company_id != cid:
        raise HTTPException(403, "Acces refuse.")
    obj.is_active = False
    db.commit()
    db.refresh(obj)
    return obj

