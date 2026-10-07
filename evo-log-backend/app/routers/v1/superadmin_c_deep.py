"""Routeur CRUD genere pour superadmin-cadc (expansion)."""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import Optional, List

from app.core.database import get_db
from app.core.permissions import require_perm
from app.models.user import User
from app.models.superadmin_c_deep import (
    SaCAuditLogReview,
    SaCSystemParameter,
    SaCPlatformAlert,
    SaCMigrationRun,
    SaCLicenseKey,
)
from app.schemas.superadmin_c_deep import (
    SaCAuditLogReviewCreate, SaCAuditLogReviewUpdate, SaCAuditLogReviewOut,
    SaCSystemParameterCreate, SaCSystemParameterUpdate, SaCSystemParameterOut,
    SaCPlatformAlertCreate, SaCPlatformAlertUpdate, SaCPlatformAlertOut,
    SaCMigrationRunCreate, SaCMigrationRunUpdate, SaCMigrationRunOut,
    SaCLicenseKeyCreate, SaCLicenseKeyUpdate, SaCLicenseKeyOut,
)

router = APIRouter(tags=["superadmin-cadc (expansion)"])


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

@router.get("/nomenclatures", summary="Vocabulaire metier superadmin-cadc")
def nomenclatures(user: User = Depends(require_perm("superadmin.nomenclature.read"))):
    from app.models import superadmin_c_deep as _md
    import enum as _pyenum
    out = {}
    for name in dir(_md):
        obj = getattr(_md, name)
        if isinstance(obj, type) and issubclass(obj, _pyenum.Enum) and obj is not _pyenum.Enum:
            out[name.lower()] = [{"code": m.name, "valeur": m.value} for m in obj]
    return out


# ─── Revues des journaux d' audit ─────────────────────────────────────────────────

@router.get("/sac-audit-log-reviews", response_model=List[SaCAuditLogReviewOut])
def list_audit_log_review(statut: Optional[str] = None, db: Session = Depends(get_db),
    user: User = Depends(require_perm("superadmin.audit_log_review.read")),
):
    cid = _company_id(user)
    return _scoped_list(db, SaCAuditLogReview, cid, {"statut": statut})


@router.post("/sac-audit-log-reviews", response_model=SaCAuditLogReviewOut, status_code=201)
def create_audit_log_review(
    payload: SaCAuditLogReviewCreate,
    db: Session = Depends(get_db),
    user: User = Depends(require_perm("superadmin.audit_log_review.create")),
):
    cid = _company_id(user)
    data = payload.model_dump(exclude_unset=True)
    _check_unique(db, SaCAuditLogReview, "reference", data.get("reference"), "reference", cid)
    obj = SaCAuditLogReview(company_id=cid)
    _apply(data, obj)
    db.add(obj)
    db.commit()
    db.refresh(obj)
    return obj


@router.put("/sac-audit-log-reviews/{ident}", response_model=SaCAuditLogReviewOut)
def update_audit_log_review(
    ident: int,
    payload: SaCAuditLogReviewUpdate,
    db: Session = Depends(get_db),
    user: User = Depends(require_perm("superadmin.audit_log_review.modify")),
):
    cid = _company_id(user)
    obj = _get_or_404(db, SaCAuditLogReview, ident, "Revues des journaux d' audit")
    if obj.company_id != cid:
        raise HTTPException(403, "Acces refuse.")
    _apply(payload.model_dump(exclude_unset=True), obj)
    db.commit()
    db.refresh(obj)
    return obj


@router.delete("/sac-audit-log-reviews/{ident}", response_model=SaCAuditLogReviewOut)
def delete_audit_log_review(
    ident: int,
    db: Session = Depends(get_db),
    user: User = Depends(require_perm("superadmin.audit_log_review.modify")),
):
    cid = _company_id(user)
    obj = _get_or_404(db, SaCAuditLogReview, ident, "Revues des journaux d' audit")
    if obj.company_id != cid:
        raise HTTPException(403, "Acces refuse.")
    obj.is_active = False
    db.commit()
    db.refresh(obj)
    return obj


# ─── Parametres systeme ─────────────────────────────────────────────────

@router.get("/sac-system-parameters", response_model=List[SaCSystemParameterOut])
def list_system_parameter(statut: Optional[str] = None, db: Session = Depends(get_db),
    user: User = Depends(require_perm("superadmin.system_parameter.read")),
):
    cid = _company_id(user)
    return _scoped_list(db, SaCSystemParameter, cid, {"statut": statut})


@router.post("/sac-system-parameters", response_model=SaCSystemParameterOut, status_code=201)
def create_system_parameter(
    payload: SaCSystemParameterCreate,
    db: Session = Depends(get_db),
    user: User = Depends(require_perm("superadmin.system_parameter.create")),
):
    cid = _company_id(user)
    data = payload.model_dump(exclude_unset=True)
    _check_unique(db, SaCSystemParameter, "reference", data.get("reference"), "reference", cid)
    obj = SaCSystemParameter(company_id=cid)
    _apply(data, obj)
    db.add(obj)
    db.commit()
    db.refresh(obj)
    return obj


@router.put("/sac-system-parameters/{ident}", response_model=SaCSystemParameterOut)
def update_system_parameter(
    ident: int,
    payload: SaCSystemParameterUpdate,
    db: Session = Depends(get_db),
    user: User = Depends(require_perm("superadmin.system_parameter.modify")),
):
    cid = _company_id(user)
    obj = _get_or_404(db, SaCSystemParameter, ident, "Parametres systeme")
    if obj.company_id != cid:
        raise HTTPException(403, "Acces refuse.")
    _apply(payload.model_dump(exclude_unset=True), obj)
    db.commit()
    db.refresh(obj)
    return obj


@router.delete("/sac-system-parameters/{ident}", response_model=SaCSystemParameterOut)
def delete_system_parameter(
    ident: int,
    db: Session = Depends(get_db),
    user: User = Depends(require_perm("superadmin.system_parameter.modify")),
):
    cid = _company_id(user)
    obj = _get_or_404(db, SaCSystemParameter, ident, "Parametres systeme")
    if obj.company_id != cid:
        raise HTTPException(403, "Acces refuse.")
    obj.is_active = False
    db.commit()
    db.refresh(obj)
    return obj


# ─── Alertes plateforme ─────────────────────────────────────────────────

@router.get("/sac-platform-alerts", response_model=List[SaCPlatformAlertOut])
def list_platform_alert(statut: Optional[str] = None, db: Session = Depends(get_db),
    user: User = Depends(require_perm("superadmin.platform_alert.read")),
):
    cid = _company_id(user)
    return _scoped_list(db, SaCPlatformAlert, cid, {"statut": statut})


@router.post("/sac-platform-alerts", response_model=SaCPlatformAlertOut, status_code=201)
def create_platform_alert(
    payload: SaCPlatformAlertCreate,
    db: Session = Depends(get_db),
    user: User = Depends(require_perm("superadmin.platform_alert.create")),
):
    cid = _company_id(user)
    data = payload.model_dump(exclude_unset=True)
    _check_unique(db, SaCPlatformAlert, "reference", data.get("reference"), "reference", cid)
    obj = SaCPlatformAlert(company_id=cid)
    _apply(data, obj)
    db.add(obj)
    db.commit()
    db.refresh(obj)
    return obj


@router.put("/sac-platform-alerts/{ident}", response_model=SaCPlatformAlertOut)
def update_platform_alert(
    ident: int,
    payload: SaCPlatformAlertUpdate,
    db: Session = Depends(get_db),
    user: User = Depends(require_perm("superadmin.platform_alert.modify")),
):
    cid = _company_id(user)
    obj = _get_or_404(db, SaCPlatformAlert, ident, "Alertes plateforme")
    if obj.company_id != cid:
        raise HTTPException(403, "Acces refuse.")
    _apply(payload.model_dump(exclude_unset=True), obj)
    db.commit()
    db.refresh(obj)
    return obj


@router.delete("/sac-platform-alerts/{ident}", response_model=SaCPlatformAlertOut)
def delete_platform_alert(
    ident: int,
    db: Session = Depends(get_db),
    user: User = Depends(require_perm("superadmin.platform_alert.modify")),
):
    cid = _company_id(user)
    obj = _get_or_404(db, SaCPlatformAlert, ident, "Alertes plateforme")
    if obj.company_id != cid:
        raise HTTPException(403, "Acces refuse.")
    obj.is_active = False
    db.commit()
    db.refresh(obj)
    return obj


# ─── Executions de migration ─────────────────────────────────────────────────

@router.get("/sac-migration-runs", response_model=List[SaCMigrationRunOut])
def list_migration_run(statut: Optional[str] = None, db: Session = Depends(get_db),
    user: User = Depends(require_perm("superadmin.migration_run.read")),
):
    cid = _company_id(user)
    return _scoped_list(db, SaCMigrationRun, cid, {"statut": statut})


@router.post("/sac-migration-runs", response_model=SaCMigrationRunOut, status_code=201)
def create_migration_run(
    payload: SaCMigrationRunCreate,
    db: Session = Depends(get_db),
    user: User = Depends(require_perm("superadmin.migration_run.create")),
):
    cid = _company_id(user)
    data = payload.model_dump(exclude_unset=True)
    _check_unique(db, SaCMigrationRun, "reference", data.get("reference"), "reference", cid)
    obj = SaCMigrationRun(company_id=cid)
    _apply(data, obj)
    db.add(obj)
    db.commit()
    db.refresh(obj)
    return obj


@router.put("/sac-migration-runs/{ident}", response_model=SaCMigrationRunOut)
def update_migration_run(
    ident: int,
    payload: SaCMigrationRunUpdate,
    db: Session = Depends(get_db),
    user: User = Depends(require_perm("superadmin.migration_run.modify")),
):
    cid = _company_id(user)
    obj = _get_or_404(db, SaCMigrationRun, ident, "Executions de migration")
    if obj.company_id != cid:
        raise HTTPException(403, "Acces refuse.")
    _apply(payload.model_dump(exclude_unset=True), obj)
    db.commit()
    db.refresh(obj)
    return obj


@router.delete("/sac-migration-runs/{ident}", response_model=SaCMigrationRunOut)
def delete_migration_run(
    ident: int,
    db: Session = Depends(get_db),
    user: User = Depends(require_perm("superadmin.migration_run.modify")),
):
    cid = _company_id(user)
    obj = _get_or_404(db, SaCMigrationRun, ident, "Executions de migration")
    if obj.company_id != cid:
        raise HTTPException(403, "Acces refuse.")
    obj.is_active = False
    db.commit()
    db.refresh(obj)
    return obj


# ─── Cles de licence ─────────────────────────────────────────────────

@router.get("/sac-license-keys", response_model=List[SaCLicenseKeyOut])
def list_license_key(statut: Optional[str] = None, db: Session = Depends(get_db),
    user: User = Depends(require_perm("superadmin.license_key.read")),
):
    cid = _company_id(user)
    return _scoped_list(db, SaCLicenseKey, cid, {"statut": statut})


@router.post("/sac-license-keys", response_model=SaCLicenseKeyOut, status_code=201)
def create_license_key(
    payload: SaCLicenseKeyCreate,
    db: Session = Depends(get_db),
    user: User = Depends(require_perm("superadmin.license_key.create")),
):
    cid = _company_id(user)
    data = payload.model_dump(exclude_unset=True)
    _check_unique(db, SaCLicenseKey, "reference", data.get("reference"), "reference", cid)
    obj = SaCLicenseKey(company_id=cid)
    _apply(data, obj)
    db.add(obj)
    db.commit()
    db.refresh(obj)
    return obj


@router.put("/sac-license-keys/{ident}", response_model=SaCLicenseKeyOut)
def update_license_key(
    ident: int,
    payload: SaCLicenseKeyUpdate,
    db: Session = Depends(get_db),
    user: User = Depends(require_perm("superadmin.license_key.modify")),
):
    cid = _company_id(user)
    obj = _get_or_404(db, SaCLicenseKey, ident, "Cles de licence")
    if obj.company_id != cid:
        raise HTTPException(403, "Acces refuse.")
    _apply(payload.model_dump(exclude_unset=True), obj)
    db.commit()
    db.refresh(obj)
    return obj


@router.delete("/sac-license-keys/{ident}", response_model=SaCLicenseKeyOut)
def delete_license_key(
    ident: int,
    db: Session = Depends(get_db),
    user: User = Depends(require_perm("superadmin.license_key.modify")),
):
    cid = _company_id(user)
    obj = _get_or_404(db, SaCLicenseKey, ident, "Cles de licence")
    if obj.company_id != cid:
        raise HTTPException(403, "Acces refuse.")
    obj.is_active = False
    db.commit()
    db.refresh(obj)
    return obj

