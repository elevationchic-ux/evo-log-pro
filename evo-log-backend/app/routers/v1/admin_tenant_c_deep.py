"""Routeur CRUD genere pour admin-tenant (expansion)."""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import Optional, List

from app.core.database import get_db
from app.core.permissions import require_perm
from app.models.user import User
from app.models.admin_tenant_c_deep import (
    AdmtDomainConfig,
    AdmtDnsRecord,
    AdmtDataResidency,
    AdmtFeatureEntitlement,
    AdmtUsageQuota,
    AdmtImpersonationLog,
    AdmtOnboardingStep,
    AdmtWhiteLabelConfig,
    AdmtTenantBackup,
    AdmtIntegrationWebhook,
)
from app.schemas.admin_tenant_c_deep import (
    AdmtDomainConfigCreate, AdmtDomainConfigUpdate, AdmtDomainConfigOut,
    AdmtDnsRecordCreate, AdmtDnsRecordUpdate, AdmtDnsRecordOut,
    AdmtDataResidencyCreate, AdmtDataResidencyUpdate, AdmtDataResidencyOut,
    AdmtFeatureEntitlementCreate, AdmtFeatureEntitlementUpdate, AdmtFeatureEntitlementOut,
    AdmtUsageQuotaCreate, AdmtUsageQuotaUpdate, AdmtUsageQuotaOut,
    AdmtImpersonationLogCreate, AdmtImpersonationLogUpdate, AdmtImpersonationLogOut,
    AdmtOnboardingStepCreate, AdmtOnboardingStepUpdate, AdmtOnboardingStepOut,
    AdmtWhiteLabelConfigCreate, AdmtWhiteLabelConfigUpdate, AdmtWhiteLabelConfigOut,
    AdmtTenantBackupCreate, AdmtTenantBackupUpdate, AdmtTenantBackupOut,
    AdmtIntegrationWebhookCreate, AdmtIntegrationWebhookUpdate, AdmtIntegrationWebhookOut,
)

router = APIRouter(tags=["admin-tenant (expansion)"])


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

@router.get("/nomenclatures", summary="Vocabulaire metier admin-tenant")
def nomenclatures(user: User = Depends(require_perm("admin.nomenclature.read"))):
    from app.models import admin_tenant_c_deep as _md
    import enum as _pyenum
    out = {}
    for name in dir(_md):
        obj = getattr(_md, name)
        if isinstance(obj, type) and issubclass(obj, _pyenum.Enum) and obj is not _pyenum.Enum:
            out[name.lower()] = [{"code": m.name, "valeur": m.value} for m in obj]
    return out


# ─── Configurations de domaine ─────────────────────────────────────────────────

@router.get("/admtd-domain-configs", response_model=List[AdmtDomainConfigOut])
def list_domain_config(statut: Optional[str] = None, db: Session = Depends(get_db),
    user: User = Depends(require_perm("admin.domain_config.read")),
):
    cid = _company_id(user)
    return _scoped_list(db, AdmtDomainConfig, cid, {"statut": statut})


@router.post("/admtd-domain-configs", response_model=AdmtDomainConfigOut, status_code=201)
def create_domain_config(
    payload: AdmtDomainConfigCreate,
    db: Session = Depends(get_db),
    user: User = Depends(require_perm("admin.domain_config.create")),
):
    cid = _company_id(user)
    data = payload.model_dump(exclude_unset=True)
    _check_unique(db, AdmtDomainConfig, "reference", data.get("reference"), "reference", cid)
    obj = AdmtDomainConfig(company_id=cid)
    _apply(data, obj)
    db.add(obj)
    db.commit()
    db.refresh(obj)
    return obj


@router.put("/admtd-domain-configs/{ident}", response_model=AdmtDomainConfigOut)
def update_domain_config(
    ident: int,
    payload: AdmtDomainConfigUpdate,
    db: Session = Depends(get_db),
    user: User = Depends(require_perm("admin.domain_config.modify")),
):
    cid = _company_id(user)
    obj = _get_or_404(db, AdmtDomainConfig, ident, "Configurations de domaine")
    if obj.company_id != cid:
        raise HTTPException(403, "Acces refuse.")
    _apply(payload.model_dump(exclude_unset=True), obj)
    db.commit()
    db.refresh(obj)
    return obj


@router.delete("/admtd-domain-configs/{ident}", response_model=AdmtDomainConfigOut)
def delete_domain_config(
    ident: int,
    db: Session = Depends(get_db),
    user: User = Depends(require_perm("admin.domain_config.modify")),
):
    cid = _company_id(user)
    obj = _get_or_404(db, AdmtDomainConfig, ident, "Configurations de domaine")
    if obj.company_id != cid:
        raise HTTPException(403, "Acces refuse.")
    obj.is_active = False
    db.commit()
    db.refresh(obj)
    return obj


# ─── Enregistrements DNS ─────────────────────────────────────────────────

@router.get("/admtd-dns-records", response_model=List[AdmtDnsRecordOut])
def list_dns_record(statut: Optional[str] = None, db: Session = Depends(get_db),
    user: User = Depends(require_perm("admin.dns_record.read")),
):
    cid = _company_id(user)
    return _scoped_list(db, AdmtDnsRecord, cid, {"statut": statut})


@router.post("/admtd-dns-records", response_model=AdmtDnsRecordOut, status_code=201)
def create_dns_record(
    payload: AdmtDnsRecordCreate,
    db: Session = Depends(get_db),
    user: User = Depends(require_perm("admin.dns_record.create")),
):
    cid = _company_id(user)
    data = payload.model_dump(exclude_unset=True)
    _check_unique(db, AdmtDnsRecord, "reference", data.get("reference"), "reference", cid)
    obj = AdmtDnsRecord(company_id=cid)
    _apply(data, obj)
    db.add(obj)
    db.commit()
    db.refresh(obj)
    return obj


@router.put("/admtd-dns-records/{ident}", response_model=AdmtDnsRecordOut)
def update_dns_record(
    ident: int,
    payload: AdmtDnsRecordUpdate,
    db: Session = Depends(get_db),
    user: User = Depends(require_perm("admin.dns_record.modify")),
):
    cid = _company_id(user)
    obj = _get_or_404(db, AdmtDnsRecord, ident, "Enregistrements DNS")
    if obj.company_id != cid:
        raise HTTPException(403, "Acces refuse.")
    _apply(payload.model_dump(exclude_unset=True), obj)
    db.commit()
    db.refresh(obj)
    return obj


@router.delete("/admtd-dns-records/{ident}", response_model=AdmtDnsRecordOut)
def delete_dns_record(
    ident: int,
    db: Session = Depends(get_db),
    user: User = Depends(require_perm("admin.dns_record.modify")),
):
    cid = _company_id(user)
    obj = _get_or_404(db, AdmtDnsRecord, ident, "Enregistrements DNS")
    if obj.company_id != cid:
        raise HTTPException(403, "Acces refuse.")
    obj.is_active = False
    db.commit()
    db.refresh(obj)
    return obj


# ─── Souverainete des donnees ─────────────────────────────────────────────────

@router.get("/admtd-data-residency", response_model=List[AdmtDataResidencyOut])
def list_data_residency(statut: Optional[str] = None, db: Session = Depends(get_db),
    user: User = Depends(require_perm("admin.data_residency.read")),
):
    cid = _company_id(user)
    return _scoped_list(db, AdmtDataResidency, cid, {"statut": statut})


@router.post("/admtd-data-residency", response_model=AdmtDataResidencyOut, status_code=201)
def create_data_residency(
    payload: AdmtDataResidencyCreate,
    db: Session = Depends(get_db),
    user: User = Depends(require_perm("admin.data_residency.create")),
):
    cid = _company_id(user)
    data = payload.model_dump(exclude_unset=True)
    _check_unique(db, AdmtDataResidency, "reference", data.get("reference"), "reference", cid)
    obj = AdmtDataResidency(company_id=cid)
    _apply(data, obj)
    db.add(obj)
    db.commit()
    db.refresh(obj)
    return obj


@router.put("/admtd-data-residency/{ident}", response_model=AdmtDataResidencyOut)
def update_data_residency(
    ident: int,
    payload: AdmtDataResidencyUpdate,
    db: Session = Depends(get_db),
    user: User = Depends(require_perm("admin.data_residency.modify")),
):
    cid = _company_id(user)
    obj = _get_or_404(db, AdmtDataResidency, ident, "Souverainete des donnees")
    if obj.company_id != cid:
        raise HTTPException(403, "Acces refuse.")
    _apply(payload.model_dump(exclude_unset=True), obj)
    db.commit()
    db.refresh(obj)
    return obj


@router.delete("/admtd-data-residency/{ident}", response_model=AdmtDataResidencyOut)
def delete_data_residency(
    ident: int,
    db: Session = Depends(get_db),
    user: User = Depends(require_perm("admin.data_residency.modify")),
):
    cid = _company_id(user)
    obj = _get_or_404(db, AdmtDataResidency, ident, "Souverainete des donnees")
    if obj.company_id != cid:
        raise HTTPException(403, "Acces refuse.")
    obj.is_active = False
    db.commit()
    db.refresh(obj)
    return obj


# ─── Droits fonctionnels ─────────────────────────────────────────────────

@router.get("/admtd-feature-entitlements", response_model=List[AdmtFeatureEntitlementOut])
def list_feature_entitlement(statut: Optional[str] = None, db: Session = Depends(get_db),
    user: User = Depends(require_perm("admin.feature_entitlement.read")),
):
    cid = _company_id(user)
    return _scoped_list(db, AdmtFeatureEntitlement, cid, {"statut": statut})


@router.post("/admtd-feature-entitlements", response_model=AdmtFeatureEntitlementOut, status_code=201)
def create_feature_entitlement(
    payload: AdmtFeatureEntitlementCreate,
    db: Session = Depends(get_db),
    user: User = Depends(require_perm("admin.feature_entitlement.create")),
):
    cid = _company_id(user)
    data = payload.model_dump(exclude_unset=True)
    _check_unique(db, AdmtFeatureEntitlement, "reference", data.get("reference"), "reference", cid)
    obj = AdmtFeatureEntitlement(company_id=cid)
    _apply(data, obj)
    db.add(obj)
    db.commit()
    db.refresh(obj)
    return obj


@router.put("/admtd-feature-entitlements/{ident}", response_model=AdmtFeatureEntitlementOut)
def update_feature_entitlement(
    ident: int,
    payload: AdmtFeatureEntitlementUpdate,
    db: Session = Depends(get_db),
    user: User = Depends(require_perm("admin.feature_entitlement.modify")),
):
    cid = _company_id(user)
    obj = _get_or_404(db, AdmtFeatureEntitlement, ident, "Droits fonctionnels")
    if obj.company_id != cid:
        raise HTTPException(403, "Acces refuse.")
    _apply(payload.model_dump(exclude_unset=True), obj)
    db.commit()
    db.refresh(obj)
    return obj


@router.delete("/admtd-feature-entitlements/{ident}", response_model=AdmtFeatureEntitlementOut)
def delete_feature_entitlement(
    ident: int,
    db: Session = Depends(get_db),
    user: User = Depends(require_perm("admin.feature_entitlement.modify")),
):
    cid = _company_id(user)
    obj = _get_or_404(db, AdmtFeatureEntitlement, ident, "Droits fonctionnels")
    if obj.company_id != cid:
        raise HTTPException(403, "Acces refuse.")
    obj.is_active = False
    db.commit()
    db.refresh(obj)
    return obj


# ─── Quotas d' usage ─────────────────────────────────────────────────

@router.get("/admtd-usage-quotas", response_model=List[AdmtUsageQuotaOut])
def list_usage_quota(statut: Optional[str] = None, db: Session = Depends(get_db),
    user: User = Depends(require_perm("admin.usage_quota.read")),
):
    cid = _company_id(user)
    return _scoped_list(db, AdmtUsageQuota, cid, {"statut": statut})


@router.post("/admtd-usage-quotas", response_model=AdmtUsageQuotaOut, status_code=201)
def create_usage_quota(
    payload: AdmtUsageQuotaCreate,
    db: Session = Depends(get_db),
    user: User = Depends(require_perm("admin.usage_quota.create")),
):
    cid = _company_id(user)
    data = payload.model_dump(exclude_unset=True)
    _check_unique(db, AdmtUsageQuota, "reference", data.get("reference"), "reference", cid)
    obj = AdmtUsageQuota(company_id=cid)
    _apply(data, obj)
    db.add(obj)
    db.commit()
    db.refresh(obj)
    return obj


@router.put("/admtd-usage-quotas/{ident}", response_model=AdmtUsageQuotaOut)
def update_usage_quota(
    ident: int,
    payload: AdmtUsageQuotaUpdate,
    db: Session = Depends(get_db),
    user: User = Depends(require_perm("admin.usage_quota.modify")),
):
    cid = _company_id(user)
    obj = _get_or_404(db, AdmtUsageQuota, ident, "Quotas d' usage")
    if obj.company_id != cid:
        raise HTTPException(403, "Acces refuse.")
    _apply(payload.model_dump(exclude_unset=True), obj)
    db.commit()
    db.refresh(obj)
    return obj


@router.delete("/admtd-usage-quotas/{ident}", response_model=AdmtUsageQuotaOut)
def delete_usage_quota(
    ident: int,
    db: Session = Depends(get_db),
    user: User = Depends(require_perm("admin.usage_quota.modify")),
):
    cid = _company_id(user)
    obj = _get_or_404(db, AdmtUsageQuota, ident, "Quotas d' usage")
    if obj.company_id != cid:
        raise HTTPException(403, "Acces refuse.")
    obj.is_active = False
    db.commit()
    db.refresh(obj)
    return obj


# ─── Journaux d' impersonation ─────────────────────────────────────────────────

@router.get("/admtd-impersonation-logs", response_model=List[AdmtImpersonationLogOut])
def list_impersonation_log(statut: Optional[str] = None, db: Session = Depends(get_db),
    user: User = Depends(require_perm("admin.impersonation_log.read")),
):
    cid = _company_id(user)
    return _scoped_list(db, AdmtImpersonationLog, cid, {"statut": statut})


@router.post("/admtd-impersonation-logs", response_model=AdmtImpersonationLogOut, status_code=201)
def create_impersonation_log(
    payload: AdmtImpersonationLogCreate,
    db: Session = Depends(get_db),
    user: User = Depends(require_perm("admin.impersonation_log.create")),
):
    cid = _company_id(user)
    data = payload.model_dump(exclude_unset=True)
    _check_unique(db, AdmtImpersonationLog, "reference", data.get("reference"), "reference", cid)
    obj = AdmtImpersonationLog(company_id=cid)
    _apply(data, obj)
    db.add(obj)
    db.commit()
    db.refresh(obj)
    return obj


@router.put("/admtd-impersonation-logs/{ident}", response_model=AdmtImpersonationLogOut)
def update_impersonation_log(
    ident: int,
    payload: AdmtImpersonationLogUpdate,
    db: Session = Depends(get_db),
    user: User = Depends(require_perm("admin.impersonation_log.modify")),
):
    cid = _company_id(user)
    obj = _get_or_404(db, AdmtImpersonationLog, ident, "Journaux d' impersonation")
    if obj.company_id != cid:
        raise HTTPException(403, "Acces refuse.")
    _apply(payload.model_dump(exclude_unset=True), obj)
    db.commit()
    db.refresh(obj)
    return obj


@router.delete("/admtd-impersonation-logs/{ident}", response_model=AdmtImpersonationLogOut)
def delete_impersonation_log(
    ident: int,
    db: Session = Depends(get_db),
    user: User = Depends(require_perm("admin.impersonation_log.modify")),
):
    cid = _company_id(user)
    obj = _get_or_404(db, AdmtImpersonationLog, ident, "Journaux d' impersonation")
    if obj.company_id != cid:
        raise HTTPException(403, "Acces refuse.")
    obj.is_active = False
    db.commit()
    db.refresh(obj)
    return obj


# ─── Etapes d' onboarding ─────────────────────────────────────────────────

@router.get("/admtd-onboarding-steps", response_model=List[AdmtOnboardingStepOut])
def list_onboarding_step(statut: Optional[str] = None, db: Session = Depends(get_db),
    user: User = Depends(require_perm("admin.onboarding_step.read")),
):
    cid = _company_id(user)
    return _scoped_list(db, AdmtOnboardingStep, cid, {"statut": statut})


@router.post("/admtd-onboarding-steps", response_model=AdmtOnboardingStepOut, status_code=201)
def create_onboarding_step(
    payload: AdmtOnboardingStepCreate,
    db: Session = Depends(get_db),
    user: User = Depends(require_perm("admin.onboarding_step.create")),
):
    cid = _company_id(user)
    data = payload.model_dump(exclude_unset=True)
    _check_unique(db, AdmtOnboardingStep, "reference", data.get("reference"), "reference", cid)
    obj = AdmtOnboardingStep(company_id=cid)
    _apply(data, obj)
    db.add(obj)
    db.commit()
    db.refresh(obj)
    return obj


@router.put("/admtd-onboarding-steps/{ident}", response_model=AdmtOnboardingStepOut)
def update_onboarding_step(
    ident: int,
    payload: AdmtOnboardingStepUpdate,
    db: Session = Depends(get_db),
    user: User = Depends(require_perm("admin.onboarding_step.modify")),
):
    cid = _company_id(user)
    obj = _get_or_404(db, AdmtOnboardingStep, ident, "Etapes d' onboarding")
    if obj.company_id != cid:
        raise HTTPException(403, "Acces refuse.")
    _apply(payload.model_dump(exclude_unset=True), obj)
    db.commit()
    db.refresh(obj)
    return obj


@router.delete("/admtd-onboarding-steps/{ident}", response_model=AdmtOnboardingStepOut)
def delete_onboarding_step(
    ident: int,
    db: Session = Depends(get_db),
    user: User = Depends(require_perm("admin.onboarding_step.modify")),
):
    cid = _company_id(user)
    obj = _get_or_404(db, AdmtOnboardingStep, ident, "Etapes d' onboarding")
    if obj.company_id != cid:
        raise HTTPException(403, "Acces refuse.")
    obj.is_active = False
    db.commit()
    db.refresh(obj)
    return obj


# ─── Configurations marque blanche ─────────────────────────────────────────────────

@router.get("/admtd-white-label-configs", response_model=List[AdmtWhiteLabelConfigOut])
def list_white_label_config(statut: Optional[str] = None, db: Session = Depends(get_db),
    user: User = Depends(require_perm("admin.white_label_config.read")),
):
    cid = _company_id(user)
    return _scoped_list(db, AdmtWhiteLabelConfig, cid, {"statut": statut})


@router.post("/admtd-white-label-configs", response_model=AdmtWhiteLabelConfigOut, status_code=201)
def create_white_label_config(
    payload: AdmtWhiteLabelConfigCreate,
    db: Session = Depends(get_db),
    user: User = Depends(require_perm("admin.white_label_config.create")),
):
    cid = _company_id(user)
    data = payload.model_dump(exclude_unset=True)
    _check_unique(db, AdmtWhiteLabelConfig, "reference", data.get("reference"), "reference", cid)
    obj = AdmtWhiteLabelConfig(company_id=cid)
    _apply(data, obj)
    db.add(obj)
    db.commit()
    db.refresh(obj)
    return obj


@router.put("/admtd-white-label-configs/{ident}", response_model=AdmtWhiteLabelConfigOut)
def update_white_label_config(
    ident: int,
    payload: AdmtWhiteLabelConfigUpdate,
    db: Session = Depends(get_db),
    user: User = Depends(require_perm("admin.white_label_config.modify")),
):
    cid = _company_id(user)
    obj = _get_or_404(db, AdmtWhiteLabelConfig, ident, "Configurations marque blanche")
    if obj.company_id != cid:
        raise HTTPException(403, "Acces refuse.")
    _apply(payload.model_dump(exclude_unset=True), obj)
    db.commit()
    db.refresh(obj)
    return obj


@router.delete("/admtd-white-label-configs/{ident}", response_model=AdmtWhiteLabelConfigOut)
def delete_white_label_config(
    ident: int,
    db: Session = Depends(get_db),
    user: User = Depends(require_perm("admin.white_label_config.modify")),
):
    cid = _company_id(user)
    obj = _get_or_404(db, AdmtWhiteLabelConfig, ident, "Configurations marque blanche")
    if obj.company_id != cid:
        raise HTTPException(403, "Acces refuse.")
    obj.is_active = False
    db.commit()
    db.refresh(obj)
    return obj


# ─── Sauvegardes tenant ─────────────────────────────────────────────────

@router.get("/admtd-tenant-backups", response_model=List[AdmtTenantBackupOut])
def list_tenant_backup(statut: Optional[str] = None, db: Session = Depends(get_db),
    user: User = Depends(require_perm("admin.tenant_backup.read")),
):
    cid = _company_id(user)
    return _scoped_list(db, AdmtTenantBackup, cid, {"statut": statut})


@router.post("/admtd-tenant-backups", response_model=AdmtTenantBackupOut, status_code=201)
def create_tenant_backup(
    payload: AdmtTenantBackupCreate,
    db: Session = Depends(get_db),
    user: User = Depends(require_perm("admin.tenant_backup.create")),
):
    cid = _company_id(user)
    data = payload.model_dump(exclude_unset=True)
    _check_unique(db, AdmtTenantBackup, "reference", data.get("reference"), "reference", cid)
    obj = AdmtTenantBackup(company_id=cid)
    _apply(data, obj)
    db.add(obj)
    db.commit()
    db.refresh(obj)
    return obj


@router.put("/admtd-tenant-backups/{ident}", response_model=AdmtTenantBackupOut)
def update_tenant_backup(
    ident: int,
    payload: AdmtTenantBackupUpdate,
    db: Session = Depends(get_db),
    user: User = Depends(require_perm("admin.tenant_backup.modify")),
):
    cid = _company_id(user)
    obj = _get_or_404(db, AdmtTenantBackup, ident, "Sauvegardes tenant")
    if obj.company_id != cid:
        raise HTTPException(403, "Acces refuse.")
    _apply(payload.model_dump(exclude_unset=True), obj)
    db.commit()
    db.refresh(obj)
    return obj


@router.delete("/admtd-tenant-backups/{ident}", response_model=AdmtTenantBackupOut)
def delete_tenant_backup(
    ident: int,
    db: Session = Depends(get_db),
    user: User = Depends(require_perm("admin.tenant_backup.modify")),
):
    cid = _company_id(user)
    obj = _get_or_404(db, AdmtTenantBackup, ident, "Sauvegardes tenant")
    if obj.company_id != cid:
        raise HTTPException(403, "Acces refuse.")
    obj.is_active = False
    db.commit()
    db.refresh(obj)
    return obj


# ─── Webhooks d' integration ─────────────────────────────────────────────────

@router.get("/admtd-integration-webhooks", response_model=List[AdmtIntegrationWebhookOut])
def list_integration_webhook(statut: Optional[str] = None, db: Session = Depends(get_db),
    user: User = Depends(require_perm("admin.integration_webhook.read")),
):
    cid = _company_id(user)
    return _scoped_list(db, AdmtIntegrationWebhook, cid, {"statut": statut})


@router.post("/admtd-integration-webhooks", response_model=AdmtIntegrationWebhookOut, status_code=201)
def create_integration_webhook(
    payload: AdmtIntegrationWebhookCreate,
    db: Session = Depends(get_db),
    user: User = Depends(require_perm("admin.integration_webhook.create")),
):
    cid = _company_id(user)
    data = payload.model_dump(exclude_unset=True)
    _check_unique(db, AdmtIntegrationWebhook, "reference", data.get("reference"), "reference", cid)
    obj = AdmtIntegrationWebhook(company_id=cid)
    _apply(data, obj)
    db.add(obj)
    db.commit()
    db.refresh(obj)
    return obj


@router.put("/admtd-integration-webhooks/{ident}", response_model=AdmtIntegrationWebhookOut)
def update_integration_webhook(
    ident: int,
    payload: AdmtIntegrationWebhookUpdate,
    db: Session = Depends(get_db),
    user: User = Depends(require_perm("admin.integration_webhook.modify")),
):
    cid = _company_id(user)
    obj = _get_or_404(db, AdmtIntegrationWebhook, ident, "Webhooks d' integration")
    if obj.company_id != cid:
        raise HTTPException(403, "Acces refuse.")
    _apply(payload.model_dump(exclude_unset=True), obj)
    db.commit()
    db.refresh(obj)
    return obj


@router.delete("/admtd-integration-webhooks/{ident}", response_model=AdmtIntegrationWebhookOut)
def delete_integration_webhook(
    ident: int,
    db: Session = Depends(get_db),
    user: User = Depends(require_perm("admin.integration_webhook.modify")),
):
    cid = _company_id(user)
    obj = _get_or_404(db, AdmtIntegrationWebhook, ident, "Webhooks d' integration")
    if obj.company_id != cid:
        raise HTTPException(403, "Acces refuse.")
    obj.is_active = False
    db.commit()
    db.refresh(obj)
    return obj

