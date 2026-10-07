"""Routeur CRUD genere pour portail-technicien (expansion)."""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import Optional, List

from app.core.database import get_db
from app.core.permissions import require_perm
from app.models.user import User
from app.models.technicien_d_deep import (
    TechWorkOrder,
    TechInterventionSheet,
    TechDiagnosis,
    TechPartConsumption,
    TechPreventivePlan,
    TechBreakdownTicket,
    TechRepairReport,
    TechCalibrationRecord,
    TechEquipmentChecklist,
    TechToolLoan,
    TechSafetyLockout,
    TechWarrantyClaim,
    TechServiceAppointment,
    TechLaborTimesheet,
    TechUpgradeRequest,
    TechFailureAnalysis,
    TechSpareRequest,
    TechInspectionRecord,
    TechWorkOrderCost,
)
from app.schemas.technicien_d_deep import (
    TechWorkOrderCreate, TechWorkOrderUpdate, TechWorkOrderOut,
    TechInterventionSheetCreate, TechInterventionSheetUpdate, TechInterventionSheetOut,
    TechDiagnosisCreate, TechDiagnosisUpdate, TechDiagnosisOut,
    TechPartConsumptionCreate, TechPartConsumptionUpdate, TechPartConsumptionOut,
    TechPreventivePlanCreate, TechPreventivePlanUpdate, TechPreventivePlanOut,
    TechBreakdownTicketCreate, TechBreakdownTicketUpdate, TechBreakdownTicketOut,
    TechRepairReportCreate, TechRepairReportUpdate, TechRepairReportOut,
    TechCalibrationRecordCreate, TechCalibrationRecordUpdate, TechCalibrationRecordOut,
    TechEquipmentChecklistCreate, TechEquipmentChecklistUpdate, TechEquipmentChecklistOut,
    TechToolLoanCreate, TechToolLoanUpdate, TechToolLoanOut,
    TechSafetyLockoutCreate, TechSafetyLockoutUpdate, TechSafetyLockoutOut,
    TechWarrantyClaimCreate, TechWarrantyClaimUpdate, TechWarrantyClaimOut,
    TechServiceAppointmentCreate, TechServiceAppointmentUpdate, TechServiceAppointmentOut,
    TechLaborTimesheetCreate, TechLaborTimesheetUpdate, TechLaborTimesheetOut,
    TechUpgradeRequestCreate, TechUpgradeRequestUpdate, TechUpgradeRequestOut,
    TechFailureAnalysisCreate, TechFailureAnalysisUpdate, TechFailureAnalysisOut,
    TechSpareRequestCreate, TechSpareRequestUpdate, TechSpareRequestOut,
    TechInspectionRecordCreate, TechInspectionRecordUpdate, TechInspectionRecordOut,
    TechWorkOrderCostCreate, TechWorkOrderCostUpdate, TechWorkOrderCostOut,
)

router = APIRouter(tags=["portail-technicien (expansion)"])


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

@router.get("/nomenclatures", summary="Vocabulaire metier portail-technicien")
def nomenclatures(user: User = Depends(require_perm("parc.nomenclature.read"))):
    from app.models import technicien_d_deep as _md
    import enum as _pyenum
    out = {}
    for name in dir(_md):
        obj = getattr(_md, name)
        if isinstance(obj, type) and issubclass(obj, _pyenum.Enum) and obj is not _pyenum.Enum:
            out[name.lower()] = [{"code": m.name, "valeur": m.value} for m in obj]
    return out


# ─── Ordres de travail ─────────────────────────────────────────────────

@router.get("/tech-work-orders", response_model=List[TechWorkOrderOut])
def list_work_order(statut: Optional[str] = None, db: Session = Depends(get_db),
    user: User = Depends(require_perm("parc.work_order.read")),
):
    cid = _company_id(user)
    return _scoped_list(db, TechWorkOrder, cid, {"statut": statut})


@router.post("/tech-work-orders", response_model=TechWorkOrderOut, status_code=201)
def create_work_order(
    payload: TechWorkOrderCreate,
    db: Session = Depends(get_db),
    user: User = Depends(require_perm("parc.work_order.create")),
):
    cid = _company_id(user)
    data = payload.model_dump(exclude_unset=True)
    _check_unique(db, TechWorkOrder, "reference", data.get("reference"), "reference", cid)
    obj = TechWorkOrder(company_id=cid)
    _apply(data, obj)
    db.add(obj)
    db.commit()
    db.refresh(obj)
    return obj


@router.put("/tech-work-orders/{ident}", response_model=TechWorkOrderOut)
def update_work_order(
    ident: int,
    payload: TechWorkOrderUpdate,
    db: Session = Depends(get_db),
    user: User = Depends(require_perm("parc.work_order.modify")),
):
    cid = _company_id(user)
    obj = _get_or_404(db, TechWorkOrder, ident, "Ordres de travail")
    if obj.company_id != cid:
        raise HTTPException(403, "Acces refuse.")
    _apply(payload.model_dump(exclude_unset=True), obj)
    db.commit()
    db.refresh(obj)
    return obj


@router.delete("/tech-work-orders/{ident}", response_model=TechWorkOrderOut)
def delete_work_order(
    ident: int,
    db: Session = Depends(get_db),
    user: User = Depends(require_perm("parc.work_order.modify")),
):
    cid = _company_id(user)
    obj = _get_or_404(db, TechWorkOrder, ident, "Ordres de travail")
    if obj.company_id != cid:
        raise HTTPException(403, "Acces refuse.")
    obj.is_active = False
    db.commit()
    db.refresh(obj)
    return obj


# ─── Fiches d' intervention ─────────────────────────────────────────────────

@router.get("/tech-intervention-sheets", response_model=List[TechInterventionSheetOut])
def list_intervention_sheet(statut: Optional[str] = None, db: Session = Depends(get_db),
    user: User = Depends(require_perm("parc.intervention_sheet.read")),
):
    cid = _company_id(user)
    return _scoped_list(db, TechInterventionSheet, cid, {"statut": statut})


@router.post("/tech-intervention-sheets", response_model=TechInterventionSheetOut, status_code=201)
def create_intervention_sheet(
    payload: TechInterventionSheetCreate,
    db: Session = Depends(get_db),
    user: User = Depends(require_perm("parc.intervention_sheet.create")),
):
    cid = _company_id(user)
    data = payload.model_dump(exclude_unset=True)
    _check_unique(db, TechInterventionSheet, "reference", data.get("reference"), "reference", cid)
    obj = TechInterventionSheet(company_id=cid)
    _apply(data, obj)
    db.add(obj)
    db.commit()
    db.refresh(obj)
    return obj


@router.put("/tech-intervention-sheets/{ident}", response_model=TechInterventionSheetOut)
def update_intervention_sheet(
    ident: int,
    payload: TechInterventionSheetUpdate,
    db: Session = Depends(get_db),
    user: User = Depends(require_perm("parc.intervention_sheet.modify")),
):
    cid = _company_id(user)
    obj = _get_or_404(db, TechInterventionSheet, ident, "Fiches d' intervention")
    if obj.company_id != cid:
        raise HTTPException(403, "Acces refuse.")
    _apply(payload.model_dump(exclude_unset=True), obj)
    db.commit()
    db.refresh(obj)
    return obj


@router.delete("/tech-intervention-sheets/{ident}", response_model=TechInterventionSheetOut)
def delete_intervention_sheet(
    ident: int,
    db: Session = Depends(get_db),
    user: User = Depends(require_perm("parc.intervention_sheet.modify")),
):
    cid = _company_id(user)
    obj = _get_or_404(db, TechInterventionSheet, ident, "Fiches d' intervention")
    if obj.company_id != cid:
        raise HTTPException(403, "Acces refuse.")
    obj.is_active = False
    db.commit()
    db.refresh(obj)
    return obj


# ─── Diagnostics ─────────────────────────────────────────────────

@router.get("/tech-diagnoses", response_model=List[TechDiagnosisOut])
def list_diagnosis(statut: Optional[str] = None, db: Session = Depends(get_db),
    user: User = Depends(require_perm("parc.diagnosis.read")),
):
    cid = _company_id(user)
    return _scoped_list(db, TechDiagnosis, cid, {"statut": statut})


@router.post("/tech-diagnoses", response_model=TechDiagnosisOut, status_code=201)
def create_diagnosis(
    payload: TechDiagnosisCreate,
    db: Session = Depends(get_db),
    user: User = Depends(require_perm("parc.diagnosis.create")),
):
    cid = _company_id(user)
    data = payload.model_dump(exclude_unset=True)
    _check_unique(db, TechDiagnosis, "reference", data.get("reference"), "reference", cid)
    obj = TechDiagnosis(company_id=cid)
    _apply(data, obj)
    db.add(obj)
    db.commit()
    db.refresh(obj)
    return obj


@router.put("/tech-diagnoses/{ident}", response_model=TechDiagnosisOut)
def update_diagnosis(
    ident: int,
    payload: TechDiagnosisUpdate,
    db: Session = Depends(get_db),
    user: User = Depends(require_perm("parc.diagnosis.modify")),
):
    cid = _company_id(user)
    obj = _get_or_404(db, TechDiagnosis, ident, "Diagnostics")
    if obj.company_id != cid:
        raise HTTPException(403, "Acces refuse.")
    _apply(payload.model_dump(exclude_unset=True), obj)
    db.commit()
    db.refresh(obj)
    return obj


@router.delete("/tech-diagnoses/{ident}", response_model=TechDiagnosisOut)
def delete_diagnosis(
    ident: int,
    db: Session = Depends(get_db),
    user: User = Depends(require_perm("parc.diagnosis.modify")),
):
    cid = _company_id(user)
    obj = _get_or_404(db, TechDiagnosis, ident, "Diagnostics")
    if obj.company_id != cid:
        raise HTTPException(403, "Acces refuse.")
    obj.is_active = False
    db.commit()
    db.refresh(obj)
    return obj


# ─── Consommation de pieces ─────────────────────────────────────────────────

@router.get("/tech-parts-consumption", response_model=List[TechPartConsumptionOut])
def list_part_consumption(statut: Optional[str] = None, db: Session = Depends(get_db),
    user: User = Depends(require_perm("parc.part_consumption.read")),
):
    cid = _company_id(user)
    return _scoped_list(db, TechPartConsumption, cid, {"statut": statut})


@router.post("/tech-parts-consumption", response_model=TechPartConsumptionOut, status_code=201)
def create_part_consumption(
    payload: TechPartConsumptionCreate,
    db: Session = Depends(get_db),
    user: User = Depends(require_perm("parc.part_consumption.create")),
):
    cid = _company_id(user)
    data = payload.model_dump(exclude_unset=True)
    _check_unique(db, TechPartConsumption, "reference", data.get("reference"), "reference", cid)
    obj = TechPartConsumption(company_id=cid)
    _apply(data, obj)
    db.add(obj)
    db.commit()
    db.refresh(obj)
    return obj


@router.put("/tech-parts-consumption/{ident}", response_model=TechPartConsumptionOut)
def update_part_consumption(
    ident: int,
    payload: TechPartConsumptionUpdate,
    db: Session = Depends(get_db),
    user: User = Depends(require_perm("parc.part_consumption.modify")),
):
    cid = _company_id(user)
    obj = _get_or_404(db, TechPartConsumption, ident, "Consommation de pieces")
    if obj.company_id != cid:
        raise HTTPException(403, "Acces refuse.")
    _apply(payload.model_dump(exclude_unset=True), obj)
    db.commit()
    db.refresh(obj)
    return obj


@router.delete("/tech-parts-consumption/{ident}", response_model=TechPartConsumptionOut)
def delete_part_consumption(
    ident: int,
    db: Session = Depends(get_db),
    user: User = Depends(require_perm("parc.part_consumption.modify")),
):
    cid = _company_id(user)
    obj = _get_or_404(db, TechPartConsumption, ident, "Consommation de pieces")
    if obj.company_id != cid:
        raise HTTPException(403, "Acces refuse.")
    obj.is_active = False
    db.commit()
    db.refresh(obj)
    return obj


# ─── Plans d' entretien preventif ─────────────────────────────────────────────────

@router.get("/tech-preventive-plans", response_model=List[TechPreventivePlanOut])
def list_preventive_plan(statut: Optional[str] = None, db: Session = Depends(get_db),
    user: User = Depends(require_perm("parc.preventive_plan.read")),
):
    cid = _company_id(user)
    return _scoped_list(db, TechPreventivePlan, cid, {"statut": statut})


@router.post("/tech-preventive-plans", response_model=TechPreventivePlanOut, status_code=201)
def create_preventive_plan(
    payload: TechPreventivePlanCreate,
    db: Session = Depends(get_db),
    user: User = Depends(require_perm("parc.preventive_plan.create")),
):
    cid = _company_id(user)
    data = payload.model_dump(exclude_unset=True)
    _check_unique(db, TechPreventivePlan, "reference", data.get("reference"), "reference", cid)
    obj = TechPreventivePlan(company_id=cid)
    _apply(data, obj)
    db.add(obj)
    db.commit()
    db.refresh(obj)
    return obj


@router.put("/tech-preventive-plans/{ident}", response_model=TechPreventivePlanOut)
def update_preventive_plan(
    ident: int,
    payload: TechPreventivePlanUpdate,
    db: Session = Depends(get_db),
    user: User = Depends(require_perm("parc.preventive_plan.modify")),
):
    cid = _company_id(user)
    obj = _get_or_404(db, TechPreventivePlan, ident, "Plans d' entretien preventif")
    if obj.company_id != cid:
        raise HTTPException(403, "Acces refuse.")
    _apply(payload.model_dump(exclude_unset=True), obj)
    db.commit()
    db.refresh(obj)
    return obj


@router.delete("/tech-preventive-plans/{ident}", response_model=TechPreventivePlanOut)
def delete_preventive_plan(
    ident: int,
    db: Session = Depends(get_db),
    user: User = Depends(require_perm("parc.preventive_plan.modify")),
):
    cid = _company_id(user)
    obj = _get_or_404(db, TechPreventivePlan, ident, "Plans d' entretien preventif")
    if obj.company_id != cid:
        raise HTTPException(403, "Acces refuse.")
    obj.is_active = False
    db.commit()
    db.refresh(obj)
    return obj


# ─── Billets de panne ─────────────────────────────────────────────────

@router.get("/tech-breakdown-tickets", response_model=List[TechBreakdownTicketOut])
def list_breakdown_ticket(statut: Optional[str] = None, db: Session = Depends(get_db),
    user: User = Depends(require_perm("parc.breakdown_ticket.read")),
):
    cid = _company_id(user)
    return _scoped_list(db, TechBreakdownTicket, cid, {"statut": statut})


@router.post("/tech-breakdown-tickets", response_model=TechBreakdownTicketOut, status_code=201)
def create_breakdown_ticket(
    payload: TechBreakdownTicketCreate,
    db: Session = Depends(get_db),
    user: User = Depends(require_perm("parc.breakdown_ticket.create")),
):
    cid = _company_id(user)
    data = payload.model_dump(exclude_unset=True)
    _check_unique(db, TechBreakdownTicket, "reference", data.get("reference"), "reference", cid)
    obj = TechBreakdownTicket(company_id=cid)
    _apply(data, obj)
    db.add(obj)
    db.commit()
    db.refresh(obj)
    return obj


@router.put("/tech-breakdown-tickets/{ident}", response_model=TechBreakdownTicketOut)
def update_breakdown_ticket(
    ident: int,
    payload: TechBreakdownTicketUpdate,
    db: Session = Depends(get_db),
    user: User = Depends(require_perm("parc.breakdown_ticket.modify")),
):
    cid = _company_id(user)
    obj = _get_or_404(db, TechBreakdownTicket, ident, "Billets de panne")
    if obj.company_id != cid:
        raise HTTPException(403, "Acces refuse.")
    _apply(payload.model_dump(exclude_unset=True), obj)
    db.commit()
    db.refresh(obj)
    return obj


@router.delete("/tech-breakdown-tickets/{ident}", response_model=TechBreakdownTicketOut)
def delete_breakdown_ticket(
    ident: int,
    db: Session = Depends(get_db),
    user: User = Depends(require_perm("parc.breakdown_ticket.modify")),
):
    cid = _company_id(user)
    obj = _get_or_404(db, TechBreakdownTicket, ident, "Billets de panne")
    if obj.company_id != cid:
        raise HTTPException(403, "Acces refuse.")
    obj.is_active = False
    db.commit()
    db.refresh(obj)
    return obj


# ─── Rapports de reparation ─────────────────────────────────────────────────

@router.get("/tech-repair-reports", response_model=List[TechRepairReportOut])
def list_repair_report(statut: Optional[str] = None, db: Session = Depends(get_db),
    user: User = Depends(require_perm("parc.repair_report.read")),
):
    cid = _company_id(user)
    return _scoped_list(db, TechRepairReport, cid, {"statut": statut})


@router.post("/tech-repair-reports", response_model=TechRepairReportOut, status_code=201)
def create_repair_report(
    payload: TechRepairReportCreate,
    db: Session = Depends(get_db),
    user: User = Depends(require_perm("parc.repair_report.create")),
):
    cid = _company_id(user)
    data = payload.model_dump(exclude_unset=True)
    _check_unique(db, TechRepairReport, "reference", data.get("reference"), "reference", cid)
    obj = TechRepairReport(company_id=cid)
    _apply(data, obj)
    db.add(obj)
    db.commit()
    db.refresh(obj)
    return obj


@router.put("/tech-repair-reports/{ident}", response_model=TechRepairReportOut)
def update_repair_report(
    ident: int,
    payload: TechRepairReportUpdate,
    db: Session = Depends(get_db),
    user: User = Depends(require_perm("parc.repair_report.modify")),
):
    cid = _company_id(user)
    obj = _get_or_404(db, TechRepairReport, ident, "Rapports de reparation")
    if obj.company_id != cid:
        raise HTTPException(403, "Acces refuse.")
    _apply(payload.model_dump(exclude_unset=True), obj)
    db.commit()
    db.refresh(obj)
    return obj


@router.delete("/tech-repair-reports/{ident}", response_model=TechRepairReportOut)
def delete_repair_report(
    ident: int,
    db: Session = Depends(get_db),
    user: User = Depends(require_perm("parc.repair_report.modify")),
):
    cid = _company_id(user)
    obj = _get_or_404(db, TechRepairReport, ident, "Rapports de reparation")
    if obj.company_id != cid:
        raise HTTPException(403, "Acces refuse.")
    obj.is_active = False
    db.commit()
    db.refresh(obj)
    return obj


# ─── Fiches d' etalonnage ─────────────────────────────────────────────────

@router.get("/tech-calibration-records", response_model=List[TechCalibrationRecordOut])
def list_calibration_record(statut: Optional[str] = None, db: Session = Depends(get_db),
    user: User = Depends(require_perm("parc.calibration_record.read")),
):
    cid = _company_id(user)
    return _scoped_list(db, TechCalibrationRecord, cid, {"statut": statut})


@router.post("/tech-calibration-records", response_model=TechCalibrationRecordOut, status_code=201)
def create_calibration_record(
    payload: TechCalibrationRecordCreate,
    db: Session = Depends(get_db),
    user: User = Depends(require_perm("parc.calibration_record.create")),
):
    cid = _company_id(user)
    data = payload.model_dump(exclude_unset=True)
    _check_unique(db, TechCalibrationRecord, "reference", data.get("reference"), "reference", cid)
    obj = TechCalibrationRecord(company_id=cid)
    _apply(data, obj)
    db.add(obj)
    db.commit()
    db.refresh(obj)
    return obj


@router.put("/tech-calibration-records/{ident}", response_model=TechCalibrationRecordOut)
def update_calibration_record(
    ident: int,
    payload: TechCalibrationRecordUpdate,
    db: Session = Depends(get_db),
    user: User = Depends(require_perm("parc.calibration_record.modify")),
):
    cid = _company_id(user)
    obj = _get_or_404(db, TechCalibrationRecord, ident, "Fiches d' etalonnage")
    if obj.company_id != cid:
        raise HTTPException(403, "Acces refuse.")
    _apply(payload.model_dump(exclude_unset=True), obj)
    db.commit()
    db.refresh(obj)
    return obj


@router.delete("/tech-calibration-records/{ident}", response_model=TechCalibrationRecordOut)
def delete_calibration_record(
    ident: int,
    db: Session = Depends(get_db),
    user: User = Depends(require_perm("parc.calibration_record.modify")),
):
    cid = _company_id(user)
    obj = _get_or_404(db, TechCalibrationRecord, ident, "Fiches d' etalonnage")
    if obj.company_id != cid:
        raise HTTPException(403, "Acces refuse.")
    obj.is_active = False
    db.commit()
    db.refresh(obj)
    return obj


# ─── Controles d' equipement atelier ─────────────────────────────────────────────────

@router.get("/tech-equipment-checklists", response_model=List[TechEquipmentChecklistOut])
def list_equipment_checklist(statut: Optional[str] = None, db: Session = Depends(get_db),
    user: User = Depends(require_perm("parc.equipment_checklist.read")),
):
    cid = _company_id(user)
    return _scoped_list(db, TechEquipmentChecklist, cid, {"statut": statut})


@router.post("/tech-equipment-checklists", response_model=TechEquipmentChecklistOut, status_code=201)
def create_equipment_checklist(
    payload: TechEquipmentChecklistCreate,
    db: Session = Depends(get_db),
    user: User = Depends(require_perm("parc.equipment_checklist.create")),
):
    cid = _company_id(user)
    data = payload.model_dump(exclude_unset=True)
    _check_unique(db, TechEquipmentChecklist, "reference", data.get("reference"), "reference", cid)
    obj = TechEquipmentChecklist(company_id=cid)
    _apply(data, obj)
    db.add(obj)
    db.commit()
    db.refresh(obj)
    return obj


@router.put("/tech-equipment-checklists/{ident}", response_model=TechEquipmentChecklistOut)
def update_equipment_checklist(
    ident: int,
    payload: TechEquipmentChecklistUpdate,
    db: Session = Depends(get_db),
    user: User = Depends(require_perm("parc.equipment_checklist.modify")),
):
    cid = _company_id(user)
    obj = _get_or_404(db, TechEquipmentChecklist, ident, "Controles d' equipement atelier")
    if obj.company_id != cid:
        raise HTTPException(403, "Acces refuse.")
    _apply(payload.model_dump(exclude_unset=True), obj)
    db.commit()
    db.refresh(obj)
    return obj


@router.delete("/tech-equipment-checklists/{ident}", response_model=TechEquipmentChecklistOut)
def delete_equipment_checklist(
    ident: int,
    db: Session = Depends(get_db),
    user: User = Depends(require_perm("parc.equipment_checklist.modify")),
):
    cid = _company_id(user)
    obj = _get_or_404(db, TechEquipmentChecklist, ident, "Controles d' equipement atelier")
    if obj.company_id != cid:
        raise HTTPException(403, "Acces refuse.")
    obj.is_active = False
    db.commit()
    db.refresh(obj)
    return obj


# ─── Prets d' outillage ─────────────────────────────────────────────────

@router.get("/tech-tool-loans", response_model=List[TechToolLoanOut])
def list_tool_loan(statut: Optional[str] = None, db: Session = Depends(get_db),
    user: User = Depends(require_perm("parc.tool_loan.read")),
):
    cid = _company_id(user)
    return _scoped_list(db, TechToolLoan, cid, {"statut": statut})


@router.post("/tech-tool-loans", response_model=TechToolLoanOut, status_code=201)
def create_tool_loan(
    payload: TechToolLoanCreate,
    db: Session = Depends(get_db),
    user: User = Depends(require_perm("parc.tool_loan.create")),
):
    cid = _company_id(user)
    data = payload.model_dump(exclude_unset=True)
    _check_unique(db, TechToolLoan, "reference", data.get("reference"), "reference", cid)
    obj = TechToolLoan(company_id=cid)
    _apply(data, obj)
    db.add(obj)
    db.commit()
    db.refresh(obj)
    return obj


@router.put("/tech-tool-loans/{ident}", response_model=TechToolLoanOut)
def update_tool_loan(
    ident: int,
    payload: TechToolLoanUpdate,
    db: Session = Depends(get_db),
    user: User = Depends(require_perm("parc.tool_loan.modify")),
):
    cid = _company_id(user)
    obj = _get_or_404(db, TechToolLoan, ident, "Prets d' outillage")
    if obj.company_id != cid:
        raise HTTPException(403, "Acces refuse.")
    _apply(payload.model_dump(exclude_unset=True), obj)
    db.commit()
    db.refresh(obj)
    return obj


@router.delete("/tech-tool-loans/{ident}", response_model=TechToolLoanOut)
def delete_tool_loan(
    ident: int,
    db: Session = Depends(get_db),
    user: User = Depends(require_perm("parc.tool_loan.modify")),
):
    cid = _company_id(user)
    obj = _get_or_404(db, TechToolLoan, ident, "Prets d' outillage")
    if obj.company_id != cid:
        raise HTTPException(403, "Acces refuse.")
    obj.is_active = False
    db.commit()
    db.refresh(obj)
    return obj


# ─── Consignations de securite ─────────────────────────────────────────────────

@router.get("/tech-safety-lockouts", response_model=List[TechSafetyLockoutOut])
def list_safety_lockout(statut: Optional[str] = None, db: Session = Depends(get_db),
    user: User = Depends(require_perm("parc.safety_lockout.read")),
):
    cid = _company_id(user)
    return _scoped_list(db, TechSafetyLockout, cid, {"statut": statut})


@router.post("/tech-safety-lockouts", response_model=TechSafetyLockoutOut, status_code=201)
def create_safety_lockout(
    payload: TechSafetyLockoutCreate,
    db: Session = Depends(get_db),
    user: User = Depends(require_perm("parc.safety_lockout.create")),
):
    cid = _company_id(user)
    data = payload.model_dump(exclude_unset=True)
    _check_unique(db, TechSafetyLockout, "reference", data.get("reference"), "reference", cid)
    obj = TechSafetyLockout(company_id=cid)
    _apply(data, obj)
    db.add(obj)
    db.commit()
    db.refresh(obj)
    return obj


@router.put("/tech-safety-lockouts/{ident}", response_model=TechSafetyLockoutOut)
def update_safety_lockout(
    ident: int,
    payload: TechSafetyLockoutUpdate,
    db: Session = Depends(get_db),
    user: User = Depends(require_perm("parc.safety_lockout.modify")),
):
    cid = _company_id(user)
    obj = _get_or_404(db, TechSafetyLockout, ident, "Consignations de securite")
    if obj.company_id != cid:
        raise HTTPException(403, "Acces refuse.")
    _apply(payload.model_dump(exclude_unset=True), obj)
    db.commit()
    db.refresh(obj)
    return obj


@router.delete("/tech-safety-lockouts/{ident}", response_model=TechSafetyLockoutOut)
def delete_safety_lockout(
    ident: int,
    db: Session = Depends(get_db),
    user: User = Depends(require_perm("parc.safety_lockout.modify")),
):
    cid = _company_id(user)
    obj = _get_or_404(db, TechSafetyLockout, ident, "Consignations de securite")
    if obj.company_id != cid:
        raise HTTPException(403, "Acces refuse.")
    obj.is_active = False
    db.commit()
    db.refresh(obj)
    return obj


# ─── Reclamations de garantie ─────────────────────────────────────────────────

@router.get("/tech-warranty-claims", response_model=List[TechWarrantyClaimOut])
def list_warranty_claim(statut: Optional[str] = None, db: Session = Depends(get_db),
    user: User = Depends(require_perm("parc.warranty_claim.read")),
):
    cid = _company_id(user)
    return _scoped_list(db, TechWarrantyClaim, cid, {"statut": statut})


@router.post("/tech-warranty-claims", response_model=TechWarrantyClaimOut, status_code=201)
def create_warranty_claim(
    payload: TechWarrantyClaimCreate,
    db: Session = Depends(get_db),
    user: User = Depends(require_perm("parc.warranty_claim.create")),
):
    cid = _company_id(user)
    data = payload.model_dump(exclude_unset=True)
    _check_unique(db, TechWarrantyClaim, "reference", data.get("reference"), "reference", cid)
    obj = TechWarrantyClaim(company_id=cid)
    _apply(data, obj)
    db.add(obj)
    db.commit()
    db.refresh(obj)
    return obj


@router.put("/tech-warranty-claims/{ident}", response_model=TechWarrantyClaimOut)
def update_warranty_claim(
    ident: int,
    payload: TechWarrantyClaimUpdate,
    db: Session = Depends(get_db),
    user: User = Depends(require_perm("parc.warranty_claim.modify")),
):
    cid = _company_id(user)
    obj = _get_or_404(db, TechWarrantyClaim, ident, "Reclamations de garantie")
    if obj.company_id != cid:
        raise HTTPException(403, "Acces refuse.")
    _apply(payload.model_dump(exclude_unset=True), obj)
    db.commit()
    db.refresh(obj)
    return obj


@router.delete("/tech-warranty-claims/{ident}", response_model=TechWarrantyClaimOut)
def delete_warranty_claim(
    ident: int,
    db: Session = Depends(get_db),
    user: User = Depends(require_perm("parc.warranty_claim.modify")),
):
    cid = _company_id(user)
    obj = _get_or_404(db, TechWarrantyClaim, ident, "Reclamations de garantie")
    if obj.company_id != cid:
        raise HTTPException(403, "Acces refuse.")
    obj.is_active = False
    db.commit()
    db.refresh(obj)
    return obj


# ─── RDV d' atelier ─────────────────────────────────────────────────

@router.get("/tech-service-appointments", response_model=List[TechServiceAppointmentOut])
def list_service_appointment(statut: Optional[str] = None, db: Session = Depends(get_db),
    user: User = Depends(require_perm("parc.service_appointment.read")),
):
    cid = _company_id(user)
    return _scoped_list(db, TechServiceAppointment, cid, {"statut": statut})


@router.post("/tech-service-appointments", response_model=TechServiceAppointmentOut, status_code=201)
def create_service_appointment(
    payload: TechServiceAppointmentCreate,
    db: Session = Depends(get_db),
    user: User = Depends(require_perm("parc.service_appointment.create")),
):
    cid = _company_id(user)
    data = payload.model_dump(exclude_unset=True)
    _check_unique(db, TechServiceAppointment, "reference", data.get("reference"), "reference", cid)
    obj = TechServiceAppointment(company_id=cid)
    _apply(data, obj)
    db.add(obj)
    db.commit()
    db.refresh(obj)
    return obj


@router.put("/tech-service-appointments/{ident}", response_model=TechServiceAppointmentOut)
def update_service_appointment(
    ident: int,
    payload: TechServiceAppointmentUpdate,
    db: Session = Depends(get_db),
    user: User = Depends(require_perm("parc.service_appointment.modify")),
):
    cid = _company_id(user)
    obj = _get_or_404(db, TechServiceAppointment, ident, "RDV d' atelier")
    if obj.company_id != cid:
        raise HTTPException(403, "Acces refuse.")
    _apply(payload.model_dump(exclude_unset=True), obj)
    db.commit()
    db.refresh(obj)
    return obj


@router.delete("/tech-service-appointments/{ident}", response_model=TechServiceAppointmentOut)
def delete_service_appointment(
    ident: int,
    db: Session = Depends(get_db),
    user: User = Depends(require_perm("parc.service_appointment.modify")),
):
    cid = _company_id(user)
    obj = _get_or_404(db, TechServiceAppointment, ident, "RDV d' atelier")
    if obj.company_id != cid:
        raise HTTPException(403, "Acces refuse.")
    obj.is_active = False
    db.commit()
    db.refresh(obj)
    return obj


# ─── Feuilles de temps main d' oeuvre ─────────────────────────────────────────────────

@router.get("/tech-labor-timesheets", response_model=List[TechLaborTimesheetOut])
def list_labor_timesheet(statut: Optional[str] = None, db: Session = Depends(get_db),
    user: User = Depends(require_perm("parc.labor_timesheet.read")),
):
    cid = _company_id(user)
    return _scoped_list(db, TechLaborTimesheet, cid, {"statut": statut})


@router.post("/tech-labor-timesheets", response_model=TechLaborTimesheetOut, status_code=201)
def create_labor_timesheet(
    payload: TechLaborTimesheetCreate,
    db: Session = Depends(get_db),
    user: User = Depends(require_perm("parc.labor_timesheet.create")),
):
    cid = _company_id(user)
    data = payload.model_dump(exclude_unset=True)
    _check_unique(db, TechLaborTimesheet, "reference", data.get("reference"), "reference", cid)
    obj = TechLaborTimesheet(company_id=cid)
    _apply(data, obj)
    db.add(obj)
    db.commit()
    db.refresh(obj)
    return obj


@router.put("/tech-labor-timesheets/{ident}", response_model=TechLaborTimesheetOut)
def update_labor_timesheet(
    ident: int,
    payload: TechLaborTimesheetUpdate,
    db: Session = Depends(get_db),
    user: User = Depends(require_perm("parc.labor_timesheet.modify")),
):
    cid = _company_id(user)
    obj = _get_or_404(db, TechLaborTimesheet, ident, "Feuilles de temps main d' oeuvre")
    if obj.company_id != cid:
        raise HTTPException(403, "Acces refuse.")
    _apply(payload.model_dump(exclude_unset=True), obj)
    db.commit()
    db.refresh(obj)
    return obj


@router.delete("/tech-labor-timesheets/{ident}", response_model=TechLaborTimesheetOut)
def delete_labor_timesheet(
    ident: int,
    db: Session = Depends(get_db),
    user: User = Depends(require_perm("parc.labor_timesheet.modify")),
):
    cid = _company_id(user)
    obj = _get_or_404(db, TechLaborTimesheet, ident, "Feuilles de temps main d' oeuvre")
    if obj.company_id != cid:
        raise HTTPException(403, "Acces refuse.")
    obj.is_active = False
    db.commit()
    db.refresh(obj)
    return obj


# ─── Demandes d' amlioration ─────────────────────────────────────────────────

@router.get("/tech-upgrade-requests", response_model=List[TechUpgradeRequestOut])
def list_upgrade_request(statut: Optional[str] = None, db: Session = Depends(get_db),
    user: User = Depends(require_perm("parc.upgrade_request.read")),
):
    cid = _company_id(user)
    return _scoped_list(db, TechUpgradeRequest, cid, {"statut": statut})


@router.post("/tech-upgrade-requests", response_model=TechUpgradeRequestOut, status_code=201)
def create_upgrade_request(
    payload: TechUpgradeRequestCreate,
    db: Session = Depends(get_db),
    user: User = Depends(require_perm("parc.upgrade_request.create")),
):
    cid = _company_id(user)
    data = payload.model_dump(exclude_unset=True)
    _check_unique(db, TechUpgradeRequest, "reference", data.get("reference"), "reference", cid)
    obj = TechUpgradeRequest(company_id=cid)
    _apply(data, obj)
    db.add(obj)
    db.commit()
    db.refresh(obj)
    return obj


@router.put("/tech-upgrade-requests/{ident}", response_model=TechUpgradeRequestOut)
def update_upgrade_request(
    ident: int,
    payload: TechUpgradeRequestUpdate,
    db: Session = Depends(get_db),
    user: User = Depends(require_perm("parc.upgrade_request.modify")),
):
    cid = _company_id(user)
    obj = _get_or_404(db, TechUpgradeRequest, ident, "Demandes d' amlioration")
    if obj.company_id != cid:
        raise HTTPException(403, "Acces refuse.")
    _apply(payload.model_dump(exclude_unset=True), obj)
    db.commit()
    db.refresh(obj)
    return obj


@router.delete("/tech-upgrade-requests/{ident}", response_model=TechUpgradeRequestOut)
def delete_upgrade_request(
    ident: int,
    db: Session = Depends(get_db),
    user: User = Depends(require_perm("parc.upgrade_request.modify")),
):
    cid = _company_id(user)
    obj = _get_or_404(db, TechUpgradeRequest, ident, "Demandes d' amlioration")
    if obj.company_id != cid:
        raise HTTPException(403, "Acces refuse.")
    obj.is_active = False
    db.commit()
    db.refresh(obj)
    return obj


# ─── Analyses de panne ─────────────────────────────────────────────────

@router.get("/tech-failure-analyses", response_model=List[TechFailureAnalysisOut])
def list_failure_analysis(statut: Optional[str] = None, db: Session = Depends(get_db),
    user: User = Depends(require_perm("parc.failure_analysis.read")),
):
    cid = _company_id(user)
    return _scoped_list(db, TechFailureAnalysis, cid, {"statut": statut})


@router.post("/tech-failure-analyses", response_model=TechFailureAnalysisOut, status_code=201)
def create_failure_analysis(
    payload: TechFailureAnalysisCreate,
    db: Session = Depends(get_db),
    user: User = Depends(require_perm("parc.failure_analysis.create")),
):
    cid = _company_id(user)
    data = payload.model_dump(exclude_unset=True)
    _check_unique(db, TechFailureAnalysis, "reference", data.get("reference"), "reference", cid)
    obj = TechFailureAnalysis(company_id=cid)
    _apply(data, obj)
    db.add(obj)
    db.commit()
    db.refresh(obj)
    return obj


@router.put("/tech-failure-analyses/{ident}", response_model=TechFailureAnalysisOut)
def update_failure_analysis(
    ident: int,
    payload: TechFailureAnalysisUpdate,
    db: Session = Depends(get_db),
    user: User = Depends(require_perm("parc.failure_analysis.modify")),
):
    cid = _company_id(user)
    obj = _get_or_404(db, TechFailureAnalysis, ident, "Analyses de panne")
    if obj.company_id != cid:
        raise HTTPException(403, "Acces refuse.")
    _apply(payload.model_dump(exclude_unset=True), obj)
    db.commit()
    db.refresh(obj)
    return obj


@router.delete("/tech-failure-analyses/{ident}", response_model=TechFailureAnalysisOut)
def delete_failure_analysis(
    ident: int,
    db: Session = Depends(get_db),
    user: User = Depends(require_perm("parc.failure_analysis.modify")),
):
    cid = _company_id(user)
    obj = _get_or_404(db, TechFailureAnalysis, ident, "Analyses de panne")
    if obj.company_id != cid:
        raise HTTPException(403, "Acces refuse.")
    obj.is_active = False
    db.commit()
    db.refresh(obj)
    return obj


# ─── Demandes de pieces ─────────────────────────────────────────────────

@router.get("/tech-spare-requests", response_model=List[TechSpareRequestOut])
def list_spare_request(statut: Optional[str] = None, db: Session = Depends(get_db),
    user: User = Depends(require_perm("parc.spare_request.read")),
):
    cid = _company_id(user)
    return _scoped_list(db, TechSpareRequest, cid, {"statut": statut})


@router.post("/tech-spare-requests", response_model=TechSpareRequestOut, status_code=201)
def create_spare_request(
    payload: TechSpareRequestCreate,
    db: Session = Depends(get_db),
    user: User = Depends(require_perm("parc.spare_request.create")),
):
    cid = _company_id(user)
    data = payload.model_dump(exclude_unset=True)
    _check_unique(db, TechSpareRequest, "reference", data.get("reference"), "reference", cid)
    obj = TechSpareRequest(company_id=cid)
    _apply(data, obj)
    db.add(obj)
    db.commit()
    db.refresh(obj)
    return obj


@router.put("/tech-spare-requests/{ident}", response_model=TechSpareRequestOut)
def update_spare_request(
    ident: int,
    payload: TechSpareRequestUpdate,
    db: Session = Depends(get_db),
    user: User = Depends(require_perm("parc.spare_request.modify")),
):
    cid = _company_id(user)
    obj = _get_or_404(db, TechSpareRequest, ident, "Demandes de pieces")
    if obj.company_id != cid:
        raise HTTPException(403, "Acces refuse.")
    _apply(payload.model_dump(exclude_unset=True), obj)
    db.commit()
    db.refresh(obj)
    return obj


@router.delete("/tech-spare-requests/{ident}", response_model=TechSpareRequestOut)
def delete_spare_request(
    ident: int,
    db: Session = Depends(get_db),
    user: User = Depends(require_perm("parc.spare_request.modify")),
):
    cid = _company_id(user)
    obj = _get_or_404(db, TechSpareRequest, ident, "Demandes de pieces")
    if obj.company_id != cid:
        raise HTTPException(403, "Acces refuse.")
    obj.is_active = False
    db.commit()
    db.refresh(obj)
    return obj


# ─── Fiches de controle technique ─────────────────────────────────────────────────

@router.get("/tech-inspection-records", response_model=List[TechInspectionRecordOut])
def list_inspection_record(statut: Optional[str] = None, db: Session = Depends(get_db),
    user: User = Depends(require_perm("parc.inspection_record.read")),
):
    cid = _company_id(user)
    return _scoped_list(db, TechInspectionRecord, cid, {"statut": statut})


@router.post("/tech-inspection-records", response_model=TechInspectionRecordOut, status_code=201)
def create_inspection_record(
    payload: TechInspectionRecordCreate,
    db: Session = Depends(get_db),
    user: User = Depends(require_perm("parc.inspection_record.create")),
):
    cid = _company_id(user)
    data = payload.model_dump(exclude_unset=True)
    _check_unique(db, TechInspectionRecord, "reference", data.get("reference"), "reference", cid)
    obj = TechInspectionRecord(company_id=cid)
    _apply(data, obj)
    db.add(obj)
    db.commit()
    db.refresh(obj)
    return obj


@router.put("/tech-inspection-records/{ident}", response_model=TechInspectionRecordOut)
def update_inspection_record(
    ident: int,
    payload: TechInspectionRecordUpdate,
    db: Session = Depends(get_db),
    user: User = Depends(require_perm("parc.inspection_record.modify")),
):
    cid = _company_id(user)
    obj = _get_or_404(db, TechInspectionRecord, ident, "Fiches de controle technique")
    if obj.company_id != cid:
        raise HTTPException(403, "Acces refuse.")
    _apply(payload.model_dump(exclude_unset=True), obj)
    db.commit()
    db.refresh(obj)
    return obj


@router.delete("/tech-inspection-records/{ident}", response_model=TechInspectionRecordOut)
def delete_inspection_record(
    ident: int,
    db: Session = Depends(get_db),
    user: User = Depends(require_perm("parc.inspection_record.modify")),
):
    cid = _company_id(user)
    obj = _get_or_404(db, TechInspectionRecord, ident, "Fiches de controle technique")
    if obj.company_id != cid:
        raise HTTPException(403, "Acces refuse.")
    obj.is_active = False
    db.commit()
    db.refresh(obj)
    return obj


# ─── Couts d' ordre de travail ─────────────────────────────────────────────────

@router.get("/tech-work-order-costs", response_model=List[TechWorkOrderCostOut])
def list_work_order_cost(statut: Optional[str] = None, db: Session = Depends(get_db),
    user: User = Depends(require_perm("parc.work_order_cost.read")),
):
    cid = _company_id(user)
    return _scoped_list(db, TechWorkOrderCost, cid, {"statut": statut})


@router.post("/tech-work-order-costs", response_model=TechWorkOrderCostOut, status_code=201)
def create_work_order_cost(
    payload: TechWorkOrderCostCreate,
    db: Session = Depends(get_db),
    user: User = Depends(require_perm("parc.work_order_cost.create")),
):
    cid = _company_id(user)
    data = payload.model_dump(exclude_unset=True)
    _check_unique(db, TechWorkOrderCost, "reference", data.get("reference"), "reference", cid)
    obj = TechWorkOrderCost(company_id=cid)
    _apply(data, obj)
    db.add(obj)
    db.commit()
    db.refresh(obj)
    return obj


@router.put("/tech-work-order-costs/{ident}", response_model=TechWorkOrderCostOut)
def update_work_order_cost(
    ident: int,
    payload: TechWorkOrderCostUpdate,
    db: Session = Depends(get_db),
    user: User = Depends(require_perm("parc.work_order_cost.modify")),
):
    cid = _company_id(user)
    obj = _get_or_404(db, TechWorkOrderCost, ident, "Couts d' ordre de travail")
    if obj.company_id != cid:
        raise HTTPException(403, "Acces refuse.")
    _apply(payload.model_dump(exclude_unset=True), obj)
    db.commit()
    db.refresh(obj)
    return obj


@router.delete("/tech-work-order-costs/{ident}", response_model=TechWorkOrderCostOut)
def delete_work_order_cost(
    ident: int,
    db: Session = Depends(get_db),
    user: User = Depends(require_perm("parc.work_order_cost.modify")),
):
    cid = _company_id(user)
    obj = _get_or_404(db, TechWorkOrderCost, ident, "Couts d' ordre de travail")
    if obj.company_id != cid:
        raise HTTPException(403, "Acces refuse.")
    obj.is_active = False
    db.commit()
    db.refresh(obj)
    return obj

