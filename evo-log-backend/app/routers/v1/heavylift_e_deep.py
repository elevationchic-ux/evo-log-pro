"""Routeur CRUD genere pour convoi-exceptionnel (expansion)."""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import Optional, List

from app.core.database import get_db
from app.core.permissions import require_perm
from app.models.user import User
from app.models.heavylift_e_deep import (
    Heavy2LiftPlan,
    Heavy2RouteSurvey,
    Heavy2EscortSchedule,
    Heavy2LoadMomentCalc,
    Heavy2CraneSetupRecord,
    Heavy2PermitObtention,
    Heavy2LashingRig,
    Heavy2AxleLoadReading,
    Heavy2ConvoyStagingReport,
)
from app.schemas.heavylift_e_deep import (
    Heavy2LiftPlanCreate, Heavy2LiftPlanUpdate, Heavy2LiftPlanOut,
    Heavy2RouteSurveyCreate, Heavy2RouteSurveyUpdate, Heavy2RouteSurveyOut,
    Heavy2EscortScheduleCreate, Heavy2EscortScheduleUpdate, Heavy2EscortScheduleOut,
    Heavy2LoadMomentCalcCreate, Heavy2LoadMomentCalcUpdate, Heavy2LoadMomentCalcOut,
    Heavy2CraneSetupRecordCreate, Heavy2CraneSetupRecordUpdate, Heavy2CraneSetupRecordOut,
    Heavy2PermitObtentionCreate, Heavy2PermitObtentionUpdate, Heavy2PermitObtentionOut,
    Heavy2LashingRigCreate, Heavy2LashingRigUpdate, Heavy2LashingRigOut,
    Heavy2AxleLoadReadingCreate, Heavy2AxleLoadReadingUpdate, Heavy2AxleLoadReadingOut,
    Heavy2ConvoyStagingReportCreate, Heavy2ConvoyStagingReportUpdate, Heavy2ConvoyStagingReportOut,
)

router = APIRouter(tags=["convoi-exceptionnel (expansion)"])


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

@router.get("/nomenclatures", summary="Vocabulaire metier convoi-exceptionnel")
def nomenclatures(user: User = Depends(require_perm("heavylift.nomenclature.read"))):
    from app.models import heavylift_e_deep as _md
    import enum as _pyenum
    out = {}
    for name in dir(_md):
        obj = getattr(_md, name)
        if isinstance(obj, type) and issubclass(obj, _pyenum.Enum) and obj is not _pyenum.Enum:
            out[name.lower()] = [{"code": m.name, "valeur": m.value} for m in obj]
    return out


# ─── Plans de levage ─────────────────────────────────────────────────

@router.get("/heavy2-lift-plans", response_model=List[Heavy2LiftPlanOut])
def list_lift_plan(statut: Optional[str] = None, db: Session = Depends(get_db),
    user: User = Depends(require_perm("heavylift.lift_plan.read")),
):
    cid = _company_id(user)
    return _scoped_list(db, Heavy2LiftPlan, cid, {"statut": statut})


@router.post("/heavy2-lift-plans", response_model=Heavy2LiftPlanOut, status_code=201)
def create_lift_plan(
    payload: Heavy2LiftPlanCreate,
    db: Session = Depends(get_db),
    user: User = Depends(require_perm("heavylift.lift_plan.create")),
):
    cid = _company_id(user)
    data = payload.model_dump(exclude_unset=True)
    _check_unique(db, Heavy2LiftPlan, "reference", data.get("reference"), "reference", cid)
    obj = Heavy2LiftPlan(company_id=cid)
    _apply(data, obj)
    db.add(obj)
    db.commit()
    db.refresh(obj)
    return obj


@router.put("/heavy2-lift-plans/{ident}", response_model=Heavy2LiftPlanOut)
def update_lift_plan(
    ident: int,
    payload: Heavy2LiftPlanUpdate,
    db: Session = Depends(get_db),
    user: User = Depends(require_perm("heavylift.lift_plan.modify")),
):
    cid = _company_id(user)
    obj = _get_or_404(db, Heavy2LiftPlan, ident, "Plans de levage")
    if obj.company_id != cid:
        raise HTTPException(403, "Acces refuse.")
    _apply(payload.model_dump(exclude_unset=True), obj)
    db.commit()
    db.refresh(obj)
    return obj


@router.delete("/heavy2-lift-plans/{ident}", response_model=Heavy2LiftPlanOut)
def delete_lift_plan(
    ident: int,
    db: Session = Depends(get_db),
    user: User = Depends(require_perm("heavylift.lift_plan.modify")),
):
    cid = _company_id(user)
    obj = _get_or_404(db, Heavy2LiftPlan, ident, "Plans de levage")
    if obj.company_id != cid:
        raise HTTPException(403, "Acces refuse.")
    obj.is_active = False
    db.commit()
    db.refresh(obj)
    return obj


# ─── Reconnaissances d' itineraire ─────────────────────────────────────────────────

@router.get("/heavy2-route-surveys", response_model=List[Heavy2RouteSurveyOut])
def list_route_survey(statut: Optional[str] = None, db: Session = Depends(get_db),
    user: User = Depends(require_perm("heavylift.route_survey.read")),
):
    cid = _company_id(user)
    return _scoped_list(db, Heavy2RouteSurvey, cid, {"statut": statut})


@router.post("/heavy2-route-surveys", response_model=Heavy2RouteSurveyOut, status_code=201)
def create_route_survey(
    payload: Heavy2RouteSurveyCreate,
    db: Session = Depends(get_db),
    user: User = Depends(require_perm("heavylift.route_survey.create")),
):
    cid = _company_id(user)
    data = payload.model_dump(exclude_unset=True)
    _check_unique(db, Heavy2RouteSurvey, "reference", data.get("reference"), "reference", cid)
    obj = Heavy2RouteSurvey(company_id=cid)
    _apply(data, obj)
    db.add(obj)
    db.commit()
    db.refresh(obj)
    return obj


@router.put("/heavy2-route-surveys/{ident}", response_model=Heavy2RouteSurveyOut)
def update_route_survey(
    ident: int,
    payload: Heavy2RouteSurveyUpdate,
    db: Session = Depends(get_db),
    user: User = Depends(require_perm("heavylift.route_survey.modify")),
):
    cid = _company_id(user)
    obj = _get_or_404(db, Heavy2RouteSurvey, ident, "Reconnaissances d' itineraire")
    if obj.company_id != cid:
        raise HTTPException(403, "Acces refuse.")
    _apply(payload.model_dump(exclude_unset=True), obj)
    db.commit()
    db.refresh(obj)
    return obj


@router.delete("/heavy2-route-surveys/{ident}", response_model=Heavy2RouteSurveyOut)
def delete_route_survey(
    ident: int,
    db: Session = Depends(get_db),
    user: User = Depends(require_perm("heavylift.route_survey.modify")),
):
    cid = _company_id(user)
    obj = _get_or_404(db, Heavy2RouteSurvey, ident, "Reconnaissances d' itineraire")
    if obj.company_id != cid:
        raise HTTPException(403, "Acces refuse.")
    obj.is_active = False
    db.commit()
    db.refresh(obj)
    return obj


# ─── Planning d' escortes ─────────────────────────────────────────────────

@router.get("/heavy2-escort-schedules", response_model=List[Heavy2EscortScheduleOut])
def list_escort_schedule(statut: Optional[str] = None, db: Session = Depends(get_db),
    user: User = Depends(require_perm("heavylift.escort_schedule.read")),
):
    cid = _company_id(user)
    return _scoped_list(db, Heavy2EscortSchedule, cid, {"statut": statut})


@router.post("/heavy2-escort-schedules", response_model=Heavy2EscortScheduleOut, status_code=201)
def create_escort_schedule(
    payload: Heavy2EscortScheduleCreate,
    db: Session = Depends(get_db),
    user: User = Depends(require_perm("heavylift.escort_schedule.create")),
):
    cid = _company_id(user)
    data = payload.model_dump(exclude_unset=True)
    _check_unique(db, Heavy2EscortSchedule, "reference", data.get("reference"), "reference", cid)
    obj = Heavy2EscortSchedule(company_id=cid)
    _apply(data, obj)
    db.add(obj)
    db.commit()
    db.refresh(obj)
    return obj


@router.put("/heavy2-escort-schedules/{ident}", response_model=Heavy2EscortScheduleOut)
def update_escort_schedule(
    ident: int,
    payload: Heavy2EscortScheduleUpdate,
    db: Session = Depends(get_db),
    user: User = Depends(require_perm("heavylift.escort_schedule.modify")),
):
    cid = _company_id(user)
    obj = _get_or_404(db, Heavy2EscortSchedule, ident, "Planning d' escortes")
    if obj.company_id != cid:
        raise HTTPException(403, "Acces refuse.")
    _apply(payload.model_dump(exclude_unset=True), obj)
    db.commit()
    db.refresh(obj)
    return obj


@router.delete("/heavy2-escort-schedules/{ident}", response_model=Heavy2EscortScheduleOut)
def delete_escort_schedule(
    ident: int,
    db: Session = Depends(get_db),
    user: User = Depends(require_perm("heavylift.escort_schedule.modify")),
):
    cid = _company_id(user)
    obj = _get_or_404(db, Heavy2EscortSchedule, ident, "Planning d' escortes")
    if obj.company_id != cid:
        raise HTTPException(403, "Acces refuse.")
    obj.is_active = False
    db.commit()
    db.refresh(obj)
    return obj


# ─── Calculs de moment de charge ─────────────────────────────────────────────────

@router.get("/heavy2-load-moment-calcs", response_model=List[Heavy2LoadMomentCalcOut])
def list_load_moment_calc(statut: Optional[str] = None, db: Session = Depends(get_db),
    user: User = Depends(require_perm("heavylift.load_moment_calc.read")),
):
    cid = _company_id(user)
    return _scoped_list(db, Heavy2LoadMomentCalc, cid, {"statut": statut})


@router.post("/heavy2-load-moment-calcs", response_model=Heavy2LoadMomentCalcOut, status_code=201)
def create_load_moment_calc(
    payload: Heavy2LoadMomentCalcCreate,
    db: Session = Depends(get_db),
    user: User = Depends(require_perm("heavylift.load_moment_calc.create")),
):
    cid = _company_id(user)
    data = payload.model_dump(exclude_unset=True)
    _check_unique(db, Heavy2LoadMomentCalc, "reference", data.get("reference"), "reference", cid)
    obj = Heavy2LoadMomentCalc(company_id=cid)
    _apply(data, obj)
    db.add(obj)
    db.commit()
    db.refresh(obj)
    return obj


@router.put("/heavy2-load-moment-calcs/{ident}", response_model=Heavy2LoadMomentCalcOut)
def update_load_moment_calc(
    ident: int,
    payload: Heavy2LoadMomentCalcUpdate,
    db: Session = Depends(get_db),
    user: User = Depends(require_perm("heavylift.load_moment_calc.modify")),
):
    cid = _company_id(user)
    obj = _get_or_404(db, Heavy2LoadMomentCalc, ident, "Calculs de moment de charge")
    if obj.company_id != cid:
        raise HTTPException(403, "Acces refuse.")
    _apply(payload.model_dump(exclude_unset=True), obj)
    db.commit()
    db.refresh(obj)
    return obj


@router.delete("/heavy2-load-moment-calcs/{ident}", response_model=Heavy2LoadMomentCalcOut)
def delete_load_moment_calc(
    ident: int,
    db: Session = Depends(get_db),
    user: User = Depends(require_perm("heavylift.load_moment_calc.modify")),
):
    cid = _company_id(user)
    obj = _get_or_404(db, Heavy2LoadMomentCalc, ident, "Calculs de moment de charge")
    if obj.company_id != cid:
        raise HTTPException(403, "Acces refuse.")
    obj.is_active = False
    db.commit()
    db.refresh(obj)
    return obj


# ─── Montages de grue ─────────────────────────────────────────────────

@router.get("/heavy2-crane-setup-records", response_model=List[Heavy2CraneSetupRecordOut])
def list_crane_setup_record(statut: Optional[str] = None, db: Session = Depends(get_db),
    user: User = Depends(require_perm("heavylift.crane_setup_record.read")),
):
    cid = _company_id(user)
    return _scoped_list(db, Heavy2CraneSetupRecord, cid, {"statut": statut})


@router.post("/heavy2-crane-setup-records", response_model=Heavy2CraneSetupRecordOut, status_code=201)
def create_crane_setup_record(
    payload: Heavy2CraneSetupRecordCreate,
    db: Session = Depends(get_db),
    user: User = Depends(require_perm("heavylift.crane_setup_record.create")),
):
    cid = _company_id(user)
    data = payload.model_dump(exclude_unset=True)
    _check_unique(db, Heavy2CraneSetupRecord, "reference", data.get("reference"), "reference", cid)
    obj = Heavy2CraneSetupRecord(company_id=cid)
    _apply(data, obj)
    db.add(obj)
    db.commit()
    db.refresh(obj)
    return obj


@router.put("/heavy2-crane-setup-records/{ident}", response_model=Heavy2CraneSetupRecordOut)
def update_crane_setup_record(
    ident: int,
    payload: Heavy2CraneSetupRecordUpdate,
    db: Session = Depends(get_db),
    user: User = Depends(require_perm("heavylift.crane_setup_record.modify")),
):
    cid = _company_id(user)
    obj = _get_or_404(db, Heavy2CraneSetupRecord, ident, "Montages de grue")
    if obj.company_id != cid:
        raise HTTPException(403, "Acces refuse.")
    _apply(payload.model_dump(exclude_unset=True), obj)
    db.commit()
    db.refresh(obj)
    return obj


@router.delete("/heavy2-crane-setup-records/{ident}", response_model=Heavy2CraneSetupRecordOut)
def delete_crane_setup_record(
    ident: int,
    db: Session = Depends(get_db),
    user: User = Depends(require_perm("heavylift.crane_setup_record.modify")),
):
    cid = _company_id(user)
    obj = _get_or_404(db, Heavy2CraneSetupRecord, ident, "Montages de grue")
    if obj.company_id != cid:
        raise HTTPException(403, "Acces refuse.")
    obj.is_active = False
    db.commit()
    db.refresh(obj)
    return obj


# ─── Obtentions d' autorisation ─────────────────────────────────────────────────

@router.get("/heavy2-permit-obtentions", response_model=List[Heavy2PermitObtentionOut])
def list_permit_obtention(statut: Optional[str] = None, db: Session = Depends(get_db),
    user: User = Depends(require_perm("heavylift.permit_obtention.read")),
):
    cid = _company_id(user)
    return _scoped_list(db, Heavy2PermitObtention, cid, {"statut": statut})


@router.post("/heavy2-permit-obtentions", response_model=Heavy2PermitObtentionOut, status_code=201)
def create_permit_obtention(
    payload: Heavy2PermitObtentionCreate,
    db: Session = Depends(get_db),
    user: User = Depends(require_perm("heavylift.permit_obtention.create")),
):
    cid = _company_id(user)
    data = payload.model_dump(exclude_unset=True)
    _check_unique(db, Heavy2PermitObtention, "reference", data.get("reference"), "reference", cid)
    obj = Heavy2PermitObtention(company_id=cid)
    _apply(data, obj)
    db.add(obj)
    db.commit()
    db.refresh(obj)
    return obj


@router.put("/heavy2-permit-obtentions/{ident}", response_model=Heavy2PermitObtentionOut)
def update_permit_obtention(
    ident: int,
    payload: Heavy2PermitObtentionUpdate,
    db: Session = Depends(get_db),
    user: User = Depends(require_perm("heavylift.permit_obtention.modify")),
):
    cid = _company_id(user)
    obj = _get_or_404(db, Heavy2PermitObtention, ident, "Obtentions d' autorisation")
    if obj.company_id != cid:
        raise HTTPException(403, "Acces refuse.")
    _apply(payload.model_dump(exclude_unset=True), obj)
    db.commit()
    db.refresh(obj)
    return obj


@router.delete("/heavy2-permit-obtentions/{ident}", response_model=Heavy2PermitObtentionOut)
def delete_permit_obtention(
    ident: int,
    db: Session = Depends(get_db),
    user: User = Depends(require_perm("heavylift.permit_obtention.modify")),
):
    cid = _company_id(user)
    obj = _get_or_404(db, Heavy2PermitObtention, ident, "Obtentions d' autorisation")
    if obj.company_id != cid:
        raise HTTPException(403, "Acces refuse.")
    obj.is_active = False
    db.commit()
    db.refresh(obj)
    return obj


# ─── Dispositifs d' arrimage ─────────────────────────────────────────────────

@router.get("/heavy2-lashing-rigs", response_model=List[Heavy2LashingRigOut])
def list_lashing_rig(statut: Optional[str] = None, db: Session = Depends(get_db),
    user: User = Depends(require_perm("heavylift.lashing_rig.read")),
):
    cid = _company_id(user)
    return _scoped_list(db, Heavy2LashingRig, cid, {"statut": statut})


@router.post("/heavy2-lashing-rigs", response_model=Heavy2LashingRigOut, status_code=201)
def create_lashing_rig(
    payload: Heavy2LashingRigCreate,
    db: Session = Depends(get_db),
    user: User = Depends(require_perm("heavylift.lashing_rig.create")),
):
    cid = _company_id(user)
    data = payload.model_dump(exclude_unset=True)
    _check_unique(db, Heavy2LashingRig, "reference", data.get("reference"), "reference", cid)
    obj = Heavy2LashingRig(company_id=cid)
    _apply(data, obj)
    db.add(obj)
    db.commit()
    db.refresh(obj)
    return obj


@router.put("/heavy2-lashing-rigs/{ident}", response_model=Heavy2LashingRigOut)
def update_lashing_rig(
    ident: int,
    payload: Heavy2LashingRigUpdate,
    db: Session = Depends(get_db),
    user: User = Depends(require_perm("heavylift.lashing_rig.modify")),
):
    cid = _company_id(user)
    obj = _get_or_404(db, Heavy2LashingRig, ident, "Dispositifs d' arrimage")
    if obj.company_id != cid:
        raise HTTPException(403, "Acces refuse.")
    _apply(payload.model_dump(exclude_unset=True), obj)
    db.commit()
    db.refresh(obj)
    return obj


@router.delete("/heavy2-lashing-rigs/{ident}", response_model=Heavy2LashingRigOut)
def delete_lashing_rig(
    ident: int,
    db: Session = Depends(get_db),
    user: User = Depends(require_perm("heavylift.lashing_rig.modify")),
):
    cid = _company_id(user)
    obj = _get_or_404(db, Heavy2LashingRig, ident, "Dispositifs d' arrimage")
    if obj.company_id != cid:
        raise HTTPException(403, "Acces refuse.")
    obj.is_active = False
    db.commit()
    db.refresh(obj)
    return obj


# ─── Releves de charge par essieu ─────────────────────────────────────────────────

@router.get("/heavy2-axle-load-readings", response_model=List[Heavy2AxleLoadReadingOut])
def list_axle_load_reading(statut: Optional[str] = None, db: Session = Depends(get_db),
    user: User = Depends(require_perm("heavylift.axle_load_reading.read")),
):
    cid = _company_id(user)
    return _scoped_list(db, Heavy2AxleLoadReading, cid, {"statut": statut})


@router.post("/heavy2-axle-load-readings", response_model=Heavy2AxleLoadReadingOut, status_code=201)
def create_axle_load_reading(
    payload: Heavy2AxleLoadReadingCreate,
    db: Session = Depends(get_db),
    user: User = Depends(require_perm("heavylift.axle_load_reading.create")),
):
    cid = _company_id(user)
    data = payload.model_dump(exclude_unset=True)
    _check_unique(db, Heavy2AxleLoadReading, "reference", data.get("reference"), "reference", cid)
    obj = Heavy2AxleLoadReading(company_id=cid)
    _apply(data, obj)
    db.add(obj)
    db.commit()
    db.refresh(obj)
    return obj


@router.put("/heavy2-axle-load-readings/{ident}", response_model=Heavy2AxleLoadReadingOut)
def update_axle_load_reading(
    ident: int,
    payload: Heavy2AxleLoadReadingUpdate,
    db: Session = Depends(get_db),
    user: User = Depends(require_perm("heavylift.axle_load_reading.modify")),
):
    cid = _company_id(user)
    obj = _get_or_404(db, Heavy2AxleLoadReading, ident, "Releves de charge par essieu")
    if obj.company_id != cid:
        raise HTTPException(403, "Acces refuse.")
    _apply(payload.model_dump(exclude_unset=True), obj)
    db.commit()
    db.refresh(obj)
    return obj


@router.delete("/heavy2-axle-load-readings/{ident}", response_model=Heavy2AxleLoadReadingOut)
def delete_axle_load_reading(
    ident: int,
    db: Session = Depends(get_db),
    user: User = Depends(require_perm("heavylift.axle_load_reading.modify")),
):
    cid = _company_id(user)
    obj = _get_or_404(db, Heavy2AxleLoadReading, ident, "Releves de charge par essieu")
    if obj.company_id != cid:
        raise HTTPException(403, "Acces refuse.")
    obj.is_active = False
    db.commit()
    db.refresh(obj)
    return obj


# ─── Comptes-rendus de rassemblement ─────────────────────────────────────────────────

@router.get("/heavy2-convoy-staging-reports", response_model=List[Heavy2ConvoyStagingReportOut])
def list_convoy_staging_report(statut: Optional[str] = None, db: Session = Depends(get_db),
    user: User = Depends(require_perm("heavylift.convoy_staging_report.read")),
):
    cid = _company_id(user)
    return _scoped_list(db, Heavy2ConvoyStagingReport, cid, {"statut": statut})


@router.post("/heavy2-convoy-staging-reports", response_model=Heavy2ConvoyStagingReportOut, status_code=201)
def create_convoy_staging_report(
    payload: Heavy2ConvoyStagingReportCreate,
    db: Session = Depends(get_db),
    user: User = Depends(require_perm("heavylift.convoy_staging_report.create")),
):
    cid = _company_id(user)
    data = payload.model_dump(exclude_unset=True)
    _check_unique(db, Heavy2ConvoyStagingReport, "reference", data.get("reference"), "reference", cid)
    obj = Heavy2ConvoyStagingReport(company_id=cid)
    _apply(data, obj)
    db.add(obj)
    db.commit()
    db.refresh(obj)
    return obj


@router.put("/heavy2-convoy-staging-reports/{ident}", response_model=Heavy2ConvoyStagingReportOut)
def update_convoy_staging_report(
    ident: int,
    payload: Heavy2ConvoyStagingReportUpdate,
    db: Session = Depends(get_db),
    user: User = Depends(require_perm("heavylift.convoy_staging_report.modify")),
):
    cid = _company_id(user)
    obj = _get_or_404(db, Heavy2ConvoyStagingReport, ident, "Comptes-rendus de rassemblement")
    if obj.company_id != cid:
        raise HTTPException(403, "Acces refuse.")
    _apply(payload.model_dump(exclude_unset=True), obj)
    db.commit()
    db.refresh(obj)
    return obj


@router.delete("/heavy2-convoy-staging-reports/{ident}", response_model=Heavy2ConvoyStagingReportOut)
def delete_convoy_staging_report(
    ident: int,
    db: Session = Depends(get_db),
    user: User = Depends(require_perm("heavylift.convoy_staging_report.modify")),
):
    cid = _company_id(user)
    obj = _get_or_404(db, Heavy2ConvoyStagingReport, ident, "Comptes-rendus de rassemblement")
    if obj.company_id != cid:
        raise HTTPException(403, "Acces refuse.")
    obj.is_active = False
    db.commit()
    db.refresh(obj)
    return obj

