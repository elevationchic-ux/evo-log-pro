"""Routeur CRUD genere pour qhse-securite (expansion)."""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import Optional, List

from app.core.database import get_db
from app.core.permissions import require_perm
from app.models.user import User
from app.models.qhse_deep import (
    EnvironmentalMeasurement,
    WasteRecord,
    SafetyDataSheet,
    EmergencyPlan,
    PpeItem,
    HealthVisit,
    RiskAssessment,
    CorrectiveAction,
    ManagementReview,
    ComplianceRecord,
    QualityAudit,
)
from app.schemas.qhse_deep import (
    EnvironmentalMeasurementCreate, EnvironmentalMeasurementUpdate, EnvironmentalMeasurementOut,
    WasteRecordCreate, WasteRecordUpdate, WasteRecordOut,
    SafetyDataSheetCreate, SafetyDataSheetUpdate, SafetyDataSheetOut,
    EmergencyPlanCreate, EmergencyPlanUpdate, EmergencyPlanOut,
    PpeItemCreate, PpeItemUpdate, PpeItemOut,
    HealthVisitCreate, HealthVisitUpdate, HealthVisitOut,
    RiskAssessmentCreate, RiskAssessmentUpdate, RiskAssessmentOut,
    CorrectiveActionCreate, CorrectiveActionUpdate, CorrectiveActionOut,
    ManagementReviewCreate, ManagementReviewUpdate, ManagementReviewOut,
    ComplianceRecordCreate, ComplianceRecordUpdate, ComplianceRecordOut,
    QualityAuditCreate, QualityAuditUpdate, QualityAuditOut,
)

router = APIRouter(tags=["qhse-securite (expansion)"])


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

@router.get("/nomenclatures", summary="Vocabulaire metier qhse-securite")
def nomenclatures(user: User = Depends(require_perm("qhse.nomenclature.read"))):
    from app.models import qhse_deep as _md
    import enum as _pyenum
    out = {}
    for name in dir(_md):
        obj = getattr(_md, name)
        if isinstance(obj, type) and issubclass(obj, _pyenum.Enum) and obj is not _pyenum.Enum:
            out[name.lower()] = [{"code": m.name, "valeur": m.value} for m in obj]
    return out


# ─── Suivi environnemental ─────────────────────────────────────────────────

@router.get("/environmental-measurements", response_model=List[EnvironmentalMeasurementOut])
def list_environmental(db: Session = Depends(get_db),
    user: User = Depends(require_perm("qhse.environmental.read")),
):
    cid = _company_id(user)
    return _scoped_list(db, EnvironmentalMeasurement, cid)


@router.post("/environmental-measurements", response_model=EnvironmentalMeasurementOut, status_code=201)
def create_environmental(
    payload: EnvironmentalMeasurementCreate,
    db: Session = Depends(get_db),
    user: User = Depends(require_perm("qhse.environmental.create")),
):
    cid = _company_id(user)
    data = payload.model_dump(exclude_unset=True)
    _check_unique(db, EnvironmentalMeasurement, "reference", data.get("reference"), "reference", cid)
    obj = EnvironmentalMeasurement(company_id=cid)
    _apply(data, obj)
    db.add(obj)
    db.commit()
    db.refresh(obj)
    return obj


@router.put("/environmental-measurements/{ident}", response_model=EnvironmentalMeasurementOut)
def update_environmental(
    ident: int,
    payload: EnvironmentalMeasurementUpdate,
    db: Session = Depends(get_db),
    user: User = Depends(require_perm("qhse.environmental.modify")),
):
    cid = _company_id(user)
    obj = _get_or_404(db, EnvironmentalMeasurement, ident, "Suivi environnemental")
    if obj.company_id != cid:
        raise HTTPException(403, "Acces refuse.")
    _apply(payload.model_dump(exclude_unset=True), obj)
    db.commit()
    db.refresh(obj)
    return obj


@router.delete("/environmental-measurements/{ident}", response_model=EnvironmentalMeasurementOut)
def delete_environmental(
    ident: int,
    db: Session = Depends(get_db),
    user: User = Depends(require_perm("qhse.environmental.modify")),
):
    cid = _company_id(user)
    obj = _get_or_404(db, EnvironmentalMeasurement, ident, "Suivi environnemental")
    if obj.company_id != cid:
        raise HTTPException(403, "Acces refuse.")
    obj.is_active = False
    db.commit()
    db.refresh(obj)
    return obj


# ─── Gestion dechets / BSD ─────────────────────────────────────────────────

@router.get("/waste-records", response_model=List[WasteRecordOut])
def list_waste_management(statut: Optional[str] = None, db: Session = Depends(get_db),
    user: User = Depends(require_perm("qhse.waste_management.read")),
):
    cid = _company_id(user)
    return _scoped_list(db, WasteRecord, cid, {"statut": statut})


@router.post("/waste-records", response_model=WasteRecordOut, status_code=201)
def create_waste_management(
    payload: WasteRecordCreate,
    db: Session = Depends(get_db),
    user: User = Depends(require_perm("qhse.waste_management.create")),
):
    cid = _company_id(user)
    data = payload.model_dump(exclude_unset=True)
    _check_unique(db, WasteRecord, "numero_bsd", data.get("numero_bsd"), "numero_bsd", cid)
    obj = WasteRecord(company_id=cid)
    _apply(data, obj)
    db.add(obj)
    db.commit()
    db.refresh(obj)
    return obj


@router.put("/waste-records/{ident}", response_model=WasteRecordOut)
def update_waste_management(
    ident: int,
    payload: WasteRecordUpdate,
    db: Session = Depends(get_db),
    user: User = Depends(require_perm("qhse.waste_management.modify")),
):
    cid = _company_id(user)
    obj = _get_or_404(db, WasteRecord, ident, "Gestion dechets / BSD")
    if obj.company_id != cid:
        raise HTTPException(403, "Acces refuse.")
    _apply(payload.model_dump(exclude_unset=True), obj)
    db.commit()
    db.refresh(obj)
    return obj


@router.delete("/waste-records/{ident}", response_model=WasteRecordOut)
def delete_waste_management(
    ident: int,
    db: Session = Depends(get_db),
    user: User = Depends(require_perm("qhse.waste_management.modify")),
):
    cid = _company_id(user)
    obj = _get_or_404(db, WasteRecord, ident, "Gestion dechets / BSD")
    if obj.company_id != cid:
        raise HTTPException(403, "Acces refuse.")
    obj.is_active = False
    db.commit()
    db.refresh(obj)
    return obj


# ─── FDS et produits chimiques ─────────────────────────────────────────────────

@router.get("/safety-data-sheets", response_model=List[SafetyDataSheetOut])
def list_chemical_safety(db: Session = Depends(get_db),
    user: User = Depends(require_perm("qhse.chemical_safety.read")),
):
    cid = _company_id(user)
    return _scoped_list(db, SafetyDataSheet, cid)


@router.post("/safety-data-sheets", response_model=SafetyDataSheetOut, status_code=201)
def create_chemical_safety(
    payload: SafetyDataSheetCreate,
    db: Session = Depends(get_db),
    user: User = Depends(require_perm("qhse.chemical_safety.create")),
):
    cid = _company_id(user)
    data = payload.model_dump(exclude_unset=True)
    _check_unique(db, SafetyDataSheet, "reference", data.get("reference"), "reference", cid)
    obj = SafetyDataSheet(company_id=cid)
    _apply(data, obj)
    db.add(obj)
    db.commit()
    db.refresh(obj)
    return obj


@router.put("/safety-data-sheets/{ident}", response_model=SafetyDataSheetOut)
def update_chemical_safety(
    ident: int,
    payload: SafetyDataSheetUpdate,
    db: Session = Depends(get_db),
    user: User = Depends(require_perm("qhse.chemical_safety.modify")),
):
    cid = _company_id(user)
    obj = _get_or_404(db, SafetyDataSheet, ident, "FDS et produits chimiques")
    if obj.company_id != cid:
        raise HTTPException(403, "Acces refuse.")
    _apply(payload.model_dump(exclude_unset=True), obj)
    db.commit()
    db.refresh(obj)
    return obj


@router.delete("/safety-data-sheets/{ident}", response_model=SafetyDataSheetOut)
def delete_chemical_safety(
    ident: int,
    db: Session = Depends(get_db),
    user: User = Depends(require_perm("qhse.chemical_safety.modify")),
):
    cid = _company_id(user)
    obj = _get_or_404(db, SafetyDataSheet, ident, "FDS et produits chimiques")
    if obj.company_id != cid:
        raise HTTPException(403, "Acces refuse.")
    obj.is_active = False
    db.commit()
    db.refresh(obj)
    return obj


# ─── Plans d'urgence / exercices ─────────────────────────────────────────────────

@router.get("/emergency-plans", response_model=List[EmergencyPlanOut])
def list_emergency_plan(db: Session = Depends(get_db),
    user: User = Depends(require_perm("qhse.emergency_plan.read")),
):
    cid = _company_id(user)
    return _scoped_list(db, EmergencyPlan, cid)


@router.post("/emergency-plans", response_model=EmergencyPlanOut, status_code=201)
def create_emergency_plan(
    payload: EmergencyPlanCreate,
    db: Session = Depends(get_db),
    user: User = Depends(require_perm("qhse.emergency_plan.create")),
):
    cid = _company_id(user)
    data = payload.model_dump(exclude_unset=True)
    _check_unique(db, EmergencyPlan, "reference", data.get("reference"), "reference", cid)
    obj = EmergencyPlan(company_id=cid)
    _apply(data, obj)
    db.add(obj)
    db.commit()
    db.refresh(obj)
    return obj


@router.put("/emergency-plans/{ident}", response_model=EmergencyPlanOut)
def update_emergency_plan(
    ident: int,
    payload: EmergencyPlanUpdate,
    db: Session = Depends(get_db),
    user: User = Depends(require_perm("qhse.emergency_plan.modify")),
):
    cid = _company_id(user)
    obj = _get_or_404(db, EmergencyPlan, ident, "Plans d'urgence / exercices")
    if obj.company_id != cid:
        raise HTTPException(403, "Acces refuse.")
    _apply(payload.model_dump(exclude_unset=True), obj)
    db.commit()
    db.refresh(obj)
    return obj


@router.delete("/emergency-plans/{ident}", response_model=EmergencyPlanOut)
def delete_emergency_plan(
    ident: int,
    db: Session = Depends(get_db),
    user: User = Depends(require_perm("qhse.emergency_plan.modify")),
):
    cid = _company_id(user)
    obj = _get_or_404(db, EmergencyPlan, ident, "Plans d'urgence / exercices")
    if obj.company_id != cid:
        raise HTTPException(403, "Acces refuse.")
    obj.is_active = False
    db.commit()
    db.refresh(obj)
    return obj


# ─── EPI equipements protection ─────────────────────────────────────────────────

@router.get("/ppe-items", response_model=List[PpeItemOut])
def list_ppe_tracking(statut: Optional[str] = None, db: Session = Depends(get_db),
    user: User = Depends(require_perm("qhse.ppe_tracking.read")),
):
    cid = _company_id(user)
    return _scoped_list(db, PpeItem, cid, {"statut": statut})


@router.post("/ppe-items", response_model=PpeItemOut, status_code=201)
def create_ppe_tracking(
    payload: PpeItemCreate,
    db: Session = Depends(get_db),
    user: User = Depends(require_perm("qhse.ppe_tracking.create")),
):
    cid = _company_id(user)
    data = payload.model_dump(exclude_unset=True)
    _check_unique(db, PpeItem, "reference", data.get("reference"), "reference", cid)
    obj = PpeItem(company_id=cid)
    _apply(data, obj)
    db.add(obj)
    db.commit()
    db.refresh(obj)
    return obj


@router.put("/ppe-items/{ident}", response_model=PpeItemOut)
def update_ppe_tracking(
    ident: int,
    payload: PpeItemUpdate,
    db: Session = Depends(get_db),
    user: User = Depends(require_perm("qhse.ppe_tracking.modify")),
):
    cid = _company_id(user)
    obj = _get_or_404(db, PpeItem, ident, "EPI equipements protection")
    if obj.company_id != cid:
        raise HTTPException(403, "Acces refuse.")
    _apply(payload.model_dump(exclude_unset=True), obj)
    db.commit()
    db.refresh(obj)
    return obj


@router.delete("/ppe-items/{ident}", response_model=PpeItemOut)
def delete_ppe_tracking(
    ident: int,
    db: Session = Depends(get_db),
    user: User = Depends(require_perm("qhse.ppe_tracking.modify")),
):
    cid = _company_id(user)
    obj = _get_or_404(db, PpeItem, ident, "EPI equipements protection")
    if obj.company_id != cid:
        raise HTTPException(403, "Acces refuse.")
    obj.is_active = False
    db.commit()
    db.refresh(obj)
    return obj


# ─── Medecine du travail ─────────────────────────────────────────────────

@router.get("/health-visits", response_model=List[HealthVisitOut])
def list_occupational_health(db: Session = Depends(get_db),
    user: User = Depends(require_perm("qhse.occupational_health.read")),
):
    cid = _company_id(user)
    return _scoped_list(db, HealthVisit, cid)


@router.post("/health-visits", response_model=HealthVisitOut, status_code=201)
def create_occupational_health(
    payload: HealthVisitCreate,
    db: Session = Depends(get_db),
    user: User = Depends(require_perm("qhse.occupational_health.create")),
):
    cid = _company_id(user)
    data = payload.model_dump(exclude_unset=True)
    _check_unique(db, HealthVisit, "reference", data.get("reference"), "reference", cid)
    obj = HealthVisit(company_id=cid)
    _apply(data, obj)
    db.add(obj)
    db.commit()
    db.refresh(obj)
    return obj


@router.put("/health-visits/{ident}", response_model=HealthVisitOut)
def update_occupational_health(
    ident: int,
    payload: HealthVisitUpdate,
    db: Session = Depends(get_db),
    user: User = Depends(require_perm("qhse.occupational_health.modify")),
):
    cid = _company_id(user)
    obj = _get_or_404(db, HealthVisit, ident, "Medecine du travail")
    if obj.company_id != cid:
        raise HTTPException(403, "Acces refuse.")
    _apply(payload.model_dump(exclude_unset=True), obj)
    db.commit()
    db.refresh(obj)
    return obj


@router.delete("/health-visits/{ident}", response_model=HealthVisitOut)
def delete_occupational_health(
    ident: int,
    db: Session = Depends(get_db),
    user: User = Depends(require_perm("qhse.occupational_health.modify")),
):
    cid = _company_id(user)
    obj = _get_or_404(db, HealthVisit, ident, "Medecine du travail")
    if obj.company_id != cid:
        raise HTTPException(403, "Acces refuse.")
    obj.is_active = False
    db.commit()
    db.refresh(obj)
    return obj


# ─── Evaluation des risques (DUER) ─────────────────────────────────────────────────

@router.get("/risk-assessments", response_model=List[RiskAssessmentOut])
def list_risk_assessment(db: Session = Depends(get_db),
    user: User = Depends(require_perm("qhse.risk_assessment.read")),
):
    cid = _company_id(user)
    return _scoped_list(db, RiskAssessment, cid)


@router.post("/risk-assessments", response_model=RiskAssessmentOut, status_code=201)
def create_risk_assessment(
    payload: RiskAssessmentCreate,
    db: Session = Depends(get_db),
    user: User = Depends(require_perm("qhse.risk_assessment.create")),
):
    cid = _company_id(user)
    data = payload.model_dump(exclude_unset=True)
    _check_unique(db, RiskAssessment, "reference", data.get("reference"), "reference", cid)
    obj = RiskAssessment(company_id=cid)
    _apply(data, obj)
    db.add(obj)
    db.commit()
    db.refresh(obj)
    return obj


@router.put("/risk-assessments/{ident}", response_model=RiskAssessmentOut)
def update_risk_assessment(
    ident: int,
    payload: RiskAssessmentUpdate,
    db: Session = Depends(get_db),
    user: User = Depends(require_perm("qhse.risk_assessment.modify")),
):
    cid = _company_id(user)
    obj = _get_or_404(db, RiskAssessment, ident, "Evaluation des risques (DUER)")
    if obj.company_id != cid:
        raise HTTPException(403, "Acces refuse.")
    _apply(payload.model_dump(exclude_unset=True), obj)
    db.commit()
    db.refresh(obj)
    return obj


@router.delete("/risk-assessments/{ident}", response_model=RiskAssessmentOut)
def delete_risk_assessment(
    ident: int,
    db: Session = Depends(get_db),
    user: User = Depends(require_perm("qhse.risk_assessment.modify")),
):
    cid = _company_id(user)
    obj = _get_or_404(db, RiskAssessment, ident, "Evaluation des risques (DUER)")
    if obj.company_id != cid:
        raise HTTPException(403, "Acces refuse.")
    obj.is_active = False
    db.commit()
    db.refresh(obj)
    return obj


# ─── Actions correctives / 8D ─────────────────────────────────────────────────

@router.get("/corrective-actions", response_model=List[CorrectiveActionOut])
def list_corrective_action(statut: Optional[str] = None, db: Session = Depends(get_db),
    user: User = Depends(require_perm("qhse.corrective_action.read")),
):
    cid = _company_id(user)
    return _scoped_list(db, CorrectiveAction, cid, {"statut": statut})


@router.post("/corrective-actions", response_model=CorrectiveActionOut, status_code=201)
def create_corrective_action(
    payload: CorrectiveActionCreate,
    db: Session = Depends(get_db),
    user: User = Depends(require_perm("qhse.corrective_action.create")),
):
    cid = _company_id(user)
    data = payload.model_dump(exclude_unset=True)
    _check_unique(db, CorrectiveAction, "reference", data.get("reference"), "reference", cid)
    obj = CorrectiveAction(company_id=cid)
    _apply(data, obj)
    db.add(obj)
    db.commit()
    db.refresh(obj)
    return obj


@router.put("/corrective-actions/{ident}", response_model=CorrectiveActionOut)
def update_corrective_action(
    ident: int,
    payload: CorrectiveActionUpdate,
    db: Session = Depends(get_db),
    user: User = Depends(require_perm("qhse.corrective_action.modify")),
):
    cid = _company_id(user)
    obj = _get_or_404(db, CorrectiveAction, ident, "Actions correctives / 8D")
    if obj.company_id != cid:
        raise HTTPException(403, "Acces refuse.")
    _apply(payload.model_dump(exclude_unset=True), obj)
    db.commit()
    db.refresh(obj)
    return obj


@router.delete("/corrective-actions/{ident}", response_model=CorrectiveActionOut)
def delete_corrective_action(
    ident: int,
    db: Session = Depends(get_db),
    user: User = Depends(require_perm("qhse.corrective_action.modify")),
):
    cid = _company_id(user)
    obj = _get_or_404(db, CorrectiveAction, ident, "Actions correctives / 8D")
    if obj.company_id != cid:
        raise HTTPException(403, "Acces refuse.")
    obj.is_active = False
    db.commit()
    db.refresh(obj)
    return obj


# ─── Revues de direction ─────────────────────────────────────────────────

@router.get("/management-reviews", response_model=List[ManagementReviewOut])
def list_management_review(statut: Optional[str] = None, db: Session = Depends(get_db),
    user: User = Depends(require_perm("qhse.management_review.read")),
):
    cid = _company_id(user)
    return _scoped_list(db, ManagementReview, cid, {"statut": statut})


@router.post("/management-reviews", response_model=ManagementReviewOut, status_code=201)
def create_management_review(
    payload: ManagementReviewCreate,
    db: Session = Depends(get_db),
    user: User = Depends(require_perm("qhse.management_review.create")),
):
    cid = _company_id(user)
    data = payload.model_dump(exclude_unset=True)
    _check_unique(db, ManagementReview, "reference", data.get("reference"), "reference", cid)
    obj = ManagementReview(company_id=cid)
    _apply(data, obj)
    db.add(obj)
    db.commit()
    db.refresh(obj)
    return obj


@router.put("/management-reviews/{ident}", response_model=ManagementReviewOut)
def update_management_review(
    ident: int,
    payload: ManagementReviewUpdate,
    db: Session = Depends(get_db),
    user: User = Depends(require_perm("qhse.management_review.modify")),
):
    cid = _company_id(user)
    obj = _get_or_404(db, ManagementReview, ident, "Revues de direction")
    if obj.company_id != cid:
        raise HTTPException(403, "Acces refuse.")
    _apply(payload.model_dump(exclude_unset=True), obj)
    db.commit()
    db.refresh(obj)
    return obj


@router.delete("/management-reviews/{ident}", response_model=ManagementReviewOut)
def delete_management_review(
    ident: int,
    db: Session = Depends(get_db),
    user: User = Depends(require_perm("qhse.management_review.modify")),
):
    cid = _company_id(user)
    obj = _get_or_404(db, ManagementReview, ident, "Revues de direction")
    if obj.company_id != cid:
        raise HTTPException(403, "Acces refuse.")
    obj.is_active = False
    db.commit()
    db.refresh(obj)
    return obj


# ─── Conformite reglementaire ─────────────────────────────────────────────────

@router.get("/compliance-records", response_model=List[ComplianceRecordOut])
def list_regulatory_compliance(statut: Optional[str] = None, db: Session = Depends(get_db),
    user: User = Depends(require_perm("qhse.regulatory_compliance.read")),
):
    cid = _company_id(user)
    return _scoped_list(db, ComplianceRecord, cid, {"statut": statut})


@router.post("/compliance-records", response_model=ComplianceRecordOut, status_code=201)
def create_regulatory_compliance(
    payload: ComplianceRecordCreate,
    db: Session = Depends(get_db),
    user: User = Depends(require_perm("qhse.regulatory_compliance.create")),
):
    cid = _company_id(user)
    data = payload.model_dump(exclude_unset=True)
    _check_unique(db, ComplianceRecord, "reference", data.get("reference"), "reference", cid)
    obj = ComplianceRecord(company_id=cid)
    _apply(data, obj)
    db.add(obj)
    db.commit()
    db.refresh(obj)
    return obj


@router.put("/compliance-records/{ident}", response_model=ComplianceRecordOut)
def update_regulatory_compliance(
    ident: int,
    payload: ComplianceRecordUpdate,
    db: Session = Depends(get_db),
    user: User = Depends(require_perm("qhse.regulatory_compliance.modify")),
):
    cid = _company_id(user)
    obj = _get_or_404(db, ComplianceRecord, ident, "Conformite reglementaire")
    if obj.company_id != cid:
        raise HTTPException(403, "Acces refuse.")
    _apply(payload.model_dump(exclude_unset=True), obj)
    db.commit()
    db.refresh(obj)
    return obj


@router.delete("/compliance-records/{ident}", response_model=ComplianceRecordOut)
def delete_regulatory_compliance(
    ident: int,
    db: Session = Depends(get_db),
    user: User = Depends(require_perm("qhse.regulatory_compliance.modify")),
):
    cid = _company_id(user)
    obj = _get_or_404(db, ComplianceRecord, ident, "Conformite reglementaire")
    if obj.company_id != cid:
        raise HTTPException(403, "Acces refuse.")
    obj.is_active = False
    db.commit()
    db.refresh(obj)
    return obj


# ─── Audits internes qualite ─────────────────────────────────────────────────

@router.get("/quality-audits", response_model=List[QualityAuditOut])
def list_quality_audit(statut: Optional[str] = None, db: Session = Depends(get_db),
    user: User = Depends(require_perm("qhse.quality_audit.read")),
):
    cid = _company_id(user)
    return _scoped_list(db, QualityAudit, cid, {"statut": statut})


@router.post("/quality-audits", response_model=QualityAuditOut, status_code=201)
def create_quality_audit(
    payload: QualityAuditCreate,
    db: Session = Depends(get_db),
    user: User = Depends(require_perm("qhse.quality_audit.create")),
):
    cid = _company_id(user)
    data = payload.model_dump(exclude_unset=True)
    _check_unique(db, QualityAudit, "reference", data.get("reference"), "reference", cid)
    obj = QualityAudit(company_id=cid)
    _apply(data, obj)
    db.add(obj)
    db.commit()
    db.refresh(obj)
    return obj


@router.put("/quality-audits/{ident}", response_model=QualityAuditOut)
def update_quality_audit(
    ident: int,
    payload: QualityAuditUpdate,
    db: Session = Depends(get_db),
    user: User = Depends(require_perm("qhse.quality_audit.modify")),
):
    cid = _company_id(user)
    obj = _get_or_404(db, QualityAudit, ident, "Audits internes qualite")
    if obj.company_id != cid:
        raise HTTPException(403, "Acces refuse.")
    _apply(payload.model_dump(exclude_unset=True), obj)
    db.commit()
    db.refresh(obj)
    return obj


@router.delete("/quality-audits/{ident}", response_model=QualityAuditOut)
def delete_quality_audit(
    ident: int,
    db: Session = Depends(get_db),
    user: User = Depends(require_perm("qhse.quality_audit.modify")),
):
    cid = _company_id(user)
    obj = _get_or_404(db, QualityAudit, ident, "Audits internes qualite")
    if obj.company_id != cid:
        raise HTTPException(403, "Acces refuse.")
    obj.is_active = False
    db.commit()
    db.refresh(obj)
    return obj

