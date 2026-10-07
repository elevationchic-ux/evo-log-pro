"""Routeur CRUD genere pour admin-saas (expansion)."""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import Optional, List

from app.core.database import get_db
from app.core.permissions import require_perm
from app.models.user import User
from app.models.admin_deep import (
    FeatureFlag,
    ApiQuota,
    WhiteLabel,
    TenantOnboarding,
    SaasApiKey,
    TenantWebhook,
    DataMigration,
    PlatformTicket,
    BillingEntry,
    UsageAnalytics,
    UptimeRecord,
)
from app.schemas.admin_deep import (
    FeatureFlagCreate, FeatureFlagUpdate, FeatureFlagOut,
    ApiQuotaCreate, ApiQuotaUpdate, ApiQuotaOut,
    WhiteLabelCreate, WhiteLabelUpdate, WhiteLabelOut,
    TenantOnboardingCreate, TenantOnboardingUpdate, TenantOnboardingOut,
    SaasApiKeyCreate, SaasApiKeyUpdate, SaasApiKeyOut,
    TenantWebhookCreate, TenantWebhookUpdate, TenantWebhookOut,
    DataMigrationCreate, DataMigrationUpdate, DataMigrationOut,
    PlatformTicketCreate, PlatformTicketUpdate, PlatformTicketOut,
    BillingEntryCreate, BillingEntryUpdate, BillingEntryOut,
    UsageAnalyticsCreate, UsageAnalyticsUpdate, UsageAnalyticsOut,
    UptimeRecordCreate, UptimeRecordUpdate, UptimeRecordOut,
)

router = APIRouter(tags=["admin-saas (expansion)"])


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

@router.get("/nomenclatures", summary="Vocabulaire metier admin-saas")
def nomenclatures(user: User = Depends(require_perm("admin.nomenclature.read"))):
    from app.models import admin_deep as _md
    import enum as _pyenum
    out = {}
    for name in dir(_md):
        obj = getattr(_md, name)
        if isinstance(obj, type) and issubclass(obj, _pyenum.Enum) and obj is not _pyenum.Enum:
            out[name.lower()] = [{"code": m.name, "valeur": m.value} for m in obj]
    return out


# ─── Gestion fonctionnalites par tenant ─────────────────────────────────────────────────

@router.get("/feature-flags", response_model=List[FeatureFlagOut])
def list_feature_flag(statut: Optional[str] = None, db: Session = Depends(get_db),
    user: User = Depends(require_perm("admin.feature_flag.read")),
):
    cid = _company_id(user)
    return _scoped_list(db, FeatureFlag, cid, {"statut": statut})


@router.post("/feature-flags", response_model=FeatureFlagOut, status_code=201)
def create_feature_flag(
    payload: FeatureFlagCreate,
    db: Session = Depends(get_db),
    user: User = Depends(require_perm("admin.feature_flag.create")),
):
    cid = _company_id(user)
    data = payload.model_dump(exclude_unset=True)
    _check_unique(db, FeatureFlag, "code_flag", data.get("code_flag"), "code_flag", cid)
    obj = FeatureFlag(company_id=cid)
    _apply(data, obj)
    db.add(obj)
    db.commit()
    db.refresh(obj)
    return obj


@router.put("/feature-flags/{ident}", response_model=FeatureFlagOut)
def update_feature_flag(
    ident: int,
    payload: FeatureFlagUpdate,
    db: Session = Depends(get_db),
    user: User = Depends(require_perm("admin.feature_flag.modify")),
):
    cid = _company_id(user)
    obj = _get_or_404(db, FeatureFlag, ident, "Gestion fonctionnalites par tenant")
    if obj.company_id != cid:
        raise HTTPException(403, "Acces refuse.")
    _apply(payload.model_dump(exclude_unset=True), obj)
    db.commit()
    db.refresh(obj)
    return obj


@router.delete("/feature-flags/{ident}", response_model=FeatureFlagOut)
def delete_feature_flag(
    ident: int,
    db: Session = Depends(get_db),
    user: User = Depends(require_perm("admin.feature_flag.modify")),
):
    cid = _company_id(user)
    obj = _get_or_404(db, FeatureFlag, ident, "Gestion fonctionnalites par tenant")
    if obj.company_id != cid:
        raise HTTPException(403, "Acces refuse.")
    obj.is_active = False
    db.commit()
    db.refresh(obj)
    return obj


# ─── Quotas API et limitations ─────────────────────────────────────────────────

@router.get("/api-quotas", response_model=List[ApiQuotaOut])
def list_rate_limit(statut: Optional[str] = None, db: Session = Depends(get_db),
    user: User = Depends(require_perm("admin.rate_limit.read")),
):
    cid = _company_id(user)
    return _scoped_list(db, ApiQuota, cid, {"statut": statut})


@router.post("/api-quotas", response_model=ApiQuotaOut, status_code=201)
def create_rate_limit(
    payload: ApiQuotaCreate,
    db: Session = Depends(get_db),
    user: User = Depends(require_perm("admin.rate_limit.create")),
):
    cid = _company_id(user)
    data = payload.model_dump(exclude_unset=True)
    _check_unique(db, ApiQuota, "reference", data.get("reference"), "reference", cid)
    obj = ApiQuota(company_id=cid)
    _apply(data, obj)
    db.add(obj)
    db.commit()
    db.refresh(obj)
    return obj


@router.put("/api-quotas/{ident}", response_model=ApiQuotaOut)
def update_rate_limit(
    ident: int,
    payload: ApiQuotaUpdate,
    db: Session = Depends(get_db),
    user: User = Depends(require_perm("admin.rate_limit.modify")),
):
    cid = _company_id(user)
    obj = _get_or_404(db, ApiQuota, ident, "Quotas API et limitations")
    if obj.company_id != cid:
        raise HTTPException(403, "Acces refuse.")
    _apply(payload.model_dump(exclude_unset=True), obj)
    db.commit()
    db.refresh(obj)
    return obj


@router.delete("/api-quotas/{ident}", response_model=ApiQuotaOut)
def delete_rate_limit(
    ident: int,
    db: Session = Depends(get_db),
    user: User = Depends(require_perm("admin.rate_limit.modify")),
):
    cid = _company_id(user)
    obj = _get_or_404(db, ApiQuota, ident, "Quotas API et limitations")
    if obj.company_id != cid:
        raise HTTPException(403, "Acces refuse.")
    obj.is_active = False
    db.commit()
    db.refresh(obj)
    return obj


# ─── Personnalisation marque ─────────────────────────────────────────────────

@router.get("/white-labels", response_model=List[WhiteLabelOut])
def list_white_label(db: Session = Depends(get_db),
    user: User = Depends(require_perm("admin.white_label.read")),
):
    cid = _company_id(user)
    return _scoped_list(db, WhiteLabel, cid)


@router.post("/white-labels", response_model=WhiteLabelOut, status_code=201)
def create_white_label(
    payload: WhiteLabelCreate,
    db: Session = Depends(get_db),
    user: User = Depends(require_perm("admin.white_label.create")),
):
    cid = _company_id(user)
    data = payload.model_dump(exclude_unset=True)
    _check_unique(db, WhiteLabel, "reference", data.get("reference"), "reference", cid)
    obj = WhiteLabel(company_id=cid)
    _apply(data, obj)
    db.add(obj)
    db.commit()
    db.refresh(obj)
    return obj


@router.put("/white-labels/{ident}", response_model=WhiteLabelOut)
def update_white_label(
    ident: int,
    payload: WhiteLabelUpdate,
    db: Session = Depends(get_db),
    user: User = Depends(require_perm("admin.white_label.modify")),
):
    cid = _company_id(user)
    obj = _get_or_404(db, WhiteLabel, ident, "Personnalisation marque")
    if obj.company_id != cid:
        raise HTTPException(403, "Acces refuse.")
    _apply(payload.model_dump(exclude_unset=True), obj)
    db.commit()
    db.refresh(obj)
    return obj


@router.delete("/white-labels/{ident}", response_model=WhiteLabelOut)
def delete_white_label(
    ident: int,
    db: Session = Depends(get_db),
    user: User = Depends(require_perm("admin.white_label.modify")),
):
    cid = _company_id(user)
    obj = _get_or_404(db, WhiteLabel, ident, "Personnalisation marque")
    if obj.company_id != cid:
        raise HTTPException(403, "Acces refuse.")
    obj.is_active = False
    db.commit()
    db.refresh(obj)
    return obj


# ─── Parcours onboarding nouveau tenant ─────────────────────────────────────────────────

@router.get("/tenant-onboardings", response_model=List[TenantOnboardingOut])
def list_onboarding_wizard(statut: Optional[str] = None, db: Session = Depends(get_db),
    user: User = Depends(require_perm("admin.onboarding_wizard.read")),
):
    cid = _company_id(user)
    return _scoped_list(db, TenantOnboarding, cid, {"statut": statut})


@router.post("/tenant-onboardings", response_model=TenantOnboardingOut, status_code=201)
def create_onboarding_wizard(
    payload: TenantOnboardingCreate,
    db: Session = Depends(get_db),
    user: User = Depends(require_perm("admin.onboarding_wizard.create")),
):
    cid = _company_id(user)
    data = payload.model_dump(exclude_unset=True)
    _check_unique(db, TenantOnboarding, "reference", data.get("reference"), "reference", cid)
    obj = TenantOnboarding(company_id=cid)
    _apply(data, obj)
    db.add(obj)
    db.commit()
    db.refresh(obj)
    return obj


@router.put("/tenant-onboardings/{ident}", response_model=TenantOnboardingOut)
def update_onboarding_wizard(
    ident: int,
    payload: TenantOnboardingUpdate,
    db: Session = Depends(get_db),
    user: User = Depends(require_perm("admin.onboarding_wizard.modify")),
):
    cid = _company_id(user)
    obj = _get_or_404(db, TenantOnboarding, ident, "Parcours onboarding nouveau tenant")
    if obj.company_id != cid:
        raise HTTPException(403, "Acces refuse.")
    _apply(payload.model_dump(exclude_unset=True), obj)
    db.commit()
    db.refresh(obj)
    return obj


@router.delete("/tenant-onboardings/{ident}", response_model=TenantOnboardingOut)
def delete_onboarding_wizard(
    ident: int,
    db: Session = Depends(get_db),
    user: User = Depends(require_perm("admin.onboarding_wizard.modify")),
):
    cid = _company_id(user)
    obj = _get_or_404(db, TenantOnboarding, ident, "Parcours onboarding nouveau tenant")
    if obj.company_id != cid:
        raise HTTPException(403, "Acces refuse.")
    obj.is_active = False
    db.commit()
    db.refresh(obj)
    return obj


# ─── Cles API tierces par tenant ─────────────────────────────────────────────────

@router.get("/saas-api-keys", response_model=List[SaasApiKeyOut])
def list_api_key(statut: Optional[str] = None, db: Session = Depends(get_db),
    user: User = Depends(require_perm("admin.api_key.read")),
):
    cid = _company_id(user)
    return _scoped_list(db, SaasApiKey, cid, {"statut": statut})


@router.post("/saas-api-keys", response_model=SaasApiKeyOut, status_code=201)
def create_api_key(
    payload: SaasApiKeyCreate,
    db: Session = Depends(get_db),
    user: User = Depends(require_perm("admin.api_key.create")),
):
    cid = _company_id(user)
    data = payload.model_dump(exclude_unset=True)
    _check_unique(db, SaasApiKey, "reference", data.get("reference"), "reference", cid)
    obj = SaasApiKey(company_id=cid)
    _apply(data, obj)
    db.add(obj)
    db.commit()
    db.refresh(obj)
    return obj


@router.put("/saas-api-keys/{ident}", response_model=SaasApiKeyOut)
def update_api_key(
    ident: int,
    payload: SaasApiKeyUpdate,
    db: Session = Depends(get_db),
    user: User = Depends(require_perm("admin.api_key.modify")),
):
    cid = _company_id(user)
    obj = _get_or_404(db, SaasApiKey, ident, "Cles API tierces par tenant")
    if obj.company_id != cid:
        raise HTTPException(403, "Acces refuse.")
    _apply(payload.model_dump(exclude_unset=True), obj)
    db.commit()
    db.refresh(obj)
    return obj


@router.delete("/saas-api-keys/{ident}", response_model=SaasApiKeyOut)
def delete_api_key(
    ident: int,
    db: Session = Depends(get_db),
    user: User = Depends(require_perm("admin.api_key.modify")),
):
    cid = _company_id(user)
    obj = _get_or_404(db, SaasApiKey, ident, "Cles API tierces par tenant")
    if obj.company_id != cid:
        raise HTTPException(403, "Acces refuse.")
    obj.is_active = False
    db.commit()
    db.refresh(obj)
    return obj


# ─── Integration evenements sortants ─────────────────────────────────────────────────

@router.get("/tenant-webhooks", response_model=List[TenantWebhookOut])
def list_webhook(statut: Optional[str] = None, db: Session = Depends(get_db),
    user: User = Depends(require_perm("admin.webhook.read")),
):
    cid = _company_id(user)
    return _scoped_list(db, TenantWebhook, cid, {"statut": statut})


@router.post("/tenant-webhooks", response_model=TenantWebhookOut, status_code=201)
def create_webhook(
    payload: TenantWebhookCreate,
    db: Session = Depends(get_db),
    user: User = Depends(require_perm("admin.webhook.create")),
):
    cid = _company_id(user)
    data = payload.model_dump(exclude_unset=True)
    _check_unique(db, TenantWebhook, "reference", data.get("reference"), "reference", cid)
    obj = TenantWebhook(company_id=cid)
    _apply(data, obj)
    db.add(obj)
    db.commit()
    db.refresh(obj)
    return obj


@router.put("/tenant-webhooks/{ident}", response_model=TenantWebhookOut)
def update_webhook(
    ident: int,
    payload: TenantWebhookUpdate,
    db: Session = Depends(get_db),
    user: User = Depends(require_perm("admin.webhook.modify")),
):
    cid = _company_id(user)
    obj = _get_or_404(db, TenantWebhook, ident, "Integration evenements sortants")
    if obj.company_id != cid:
        raise HTTPException(403, "Acces refuse.")
    _apply(payload.model_dump(exclude_unset=True), obj)
    db.commit()
    db.refresh(obj)
    return obj


@router.delete("/tenant-webhooks/{ident}", response_model=TenantWebhookOut)
def delete_webhook(
    ident: int,
    db: Session = Depends(get_db),
    user: User = Depends(require_perm("admin.webhook.modify")),
):
    cid = _company_id(user)
    obj = _get_or_404(db, TenantWebhook, ident, "Integration evenements sortants")
    if obj.company_id != cid:
        raise HTTPException(403, "Acces refuse.")
    obj.is_active = False
    db.commit()
    db.refresh(obj)
    return obj


# ─── Import / migration donnees ─────────────────────────────────────────────────

@router.get("/data-migrations", response_model=List[DataMigrationOut])
def list_data_migration(statut: Optional[str] = None, db: Session = Depends(get_db),
    user: User = Depends(require_perm("admin.data_migration.read")),
):
    cid = _company_id(user)
    return _scoped_list(db, DataMigration, cid, {"statut": statut})


@router.post("/data-migrations", response_model=DataMigrationOut, status_code=201)
def create_data_migration(
    payload: DataMigrationCreate,
    db: Session = Depends(get_db),
    user: User = Depends(require_perm("admin.data_migration.create")),
):
    cid = _company_id(user)
    data = payload.model_dump(exclude_unset=True)
    _check_unique(db, DataMigration, "reference", data.get("reference"), "reference", cid)
    obj = DataMigration(company_id=cid)
    _apply(data, obj)
    db.add(obj)
    db.commit()
    db.refresh(obj)
    return obj


@router.put("/data-migrations/{ident}", response_model=DataMigrationOut)
def update_data_migration(
    ident: int,
    payload: DataMigrationUpdate,
    db: Session = Depends(get_db),
    user: User = Depends(require_perm("admin.data_migration.modify")),
):
    cid = _company_id(user)
    obj = _get_or_404(db, DataMigration, ident, "Import / migration donnees")
    if obj.company_id != cid:
        raise HTTPException(403, "Acces refuse.")
    _apply(payload.model_dump(exclude_unset=True), obj)
    db.commit()
    db.refresh(obj)
    return obj


@router.delete("/data-migrations/{ident}", response_model=DataMigrationOut)
def delete_data_migration(
    ident: int,
    db: Session = Depends(get_db),
    user: User = Depends(require_perm("admin.data_migration.modify")),
):
    cid = _company_id(user)
    obj = _get_or_404(db, DataMigration, ident, "Import / migration donnees")
    if obj.company_id != cid:
        raise HTTPException(403, "Acces refuse.")
    obj.is_active = False
    db.commit()
    db.refresh(obj)
    return obj


# ─── Tickets support plateforme ─────────────────────────────────────────────────

@router.get("/platform-tickets", response_model=List[PlatformTicketOut])
def list_support_ticket(statut: Optional[str] = None, db: Session = Depends(get_db),
    user: User = Depends(require_perm("admin.support_ticket.read")),
):
    cid = _company_id(user)
    return _scoped_list(db, PlatformTicket, cid, {"statut": statut})


@router.post("/platform-tickets", response_model=PlatformTicketOut, status_code=201)
def create_support_ticket(
    payload: PlatformTicketCreate,
    db: Session = Depends(get_db),
    user: User = Depends(require_perm("admin.support_ticket.create")),
):
    cid = _company_id(user)
    data = payload.model_dump(exclude_unset=True)
    _check_unique(db, PlatformTicket, "reference", data.get("reference"), "reference", cid)
    obj = PlatformTicket(company_id=cid)
    _apply(data, obj)
    db.add(obj)
    db.commit()
    db.refresh(obj)
    return obj


@router.put("/platform-tickets/{ident}", response_model=PlatformTicketOut)
def update_support_ticket(
    ident: int,
    payload: PlatformTicketUpdate,
    db: Session = Depends(get_db),
    user: User = Depends(require_perm("admin.support_ticket.modify")),
):
    cid = _company_id(user)
    obj = _get_or_404(db, PlatformTicket, ident, "Tickets support plateforme")
    if obj.company_id != cid:
        raise HTTPException(403, "Acces refuse.")
    _apply(payload.model_dump(exclude_unset=True), obj)
    db.commit()
    db.refresh(obj)
    return obj


@router.delete("/platform-tickets/{ident}", response_model=PlatformTicketOut)
def delete_support_ticket(
    ident: int,
    db: Session = Depends(get_db),
    user: User = Depends(require_perm("admin.support_ticket.modify")),
):
    cid = _company_id(user)
    obj = _get_or_404(db, PlatformTicket, ident, "Tickets support plateforme")
    if obj.company_id != cid:
        raise HTTPException(403, "Acces refuse.")
    obj.is_active = False
    db.commit()
    db.refresh(obj)
    return obj


# ─── Moteur de facturation SaaS ─────────────────────────────────────────────────

@router.get("/billing-entries", response_model=List[BillingEntryOut])
def list_billing_engine(statut: Optional[str] = None, db: Session = Depends(get_db),
    user: User = Depends(require_perm("admin.billing_engine.read")),
):
    cid = _company_id(user)
    return _scoped_list(db, BillingEntry, cid, {"statut": statut})


@router.post("/billing-entries", response_model=BillingEntryOut, status_code=201)
def create_billing_engine(
    payload: BillingEntryCreate,
    db: Session = Depends(get_db),
    user: User = Depends(require_perm("admin.billing_engine.create")),
):
    cid = _company_id(user)
    data = payload.model_dump(exclude_unset=True)
    _check_unique(db, BillingEntry, "reference", data.get("reference"), "reference", cid)
    obj = BillingEntry(company_id=cid)
    _apply(data, obj)
    db.add(obj)
    db.commit()
    db.refresh(obj)
    return obj


@router.put("/billing-entries/{ident}", response_model=BillingEntryOut)
def update_billing_engine(
    ident: int,
    payload: BillingEntryUpdate,
    db: Session = Depends(get_db),
    user: User = Depends(require_perm("admin.billing_engine.modify")),
):
    cid = _company_id(user)
    obj = _get_or_404(db, BillingEntry, ident, "Moteur de facturation SaaS")
    if obj.company_id != cid:
        raise HTTPException(403, "Acces refuse.")
    _apply(payload.model_dump(exclude_unset=True), obj)
    db.commit()
    db.refresh(obj)
    return obj


@router.delete("/billing-entries/{ident}", response_model=BillingEntryOut)
def delete_billing_engine(
    ident: int,
    db: Session = Depends(get_db),
    user: User = Depends(require_perm("admin.billing_engine.modify")),
):
    cid = _company_id(user)
    obj = _get_or_404(db, BillingEntry, ident, "Moteur de facturation SaaS")
    if obj.company_id != cid:
        raise HTTPException(403, "Acces refuse.")
    obj.is_active = False
    db.commit()
    db.refresh(obj)
    return obj


# ─── Analytique d'usage par tenant ─────────────────────────────────────────────────

@router.get("/usage-analytics", response_model=List[UsageAnalyticsOut])
def list_usage_analytics(db: Session = Depends(get_db),
    user: User = Depends(require_perm("admin.usage_analytics.read")),
):
    cid = _company_id(user)
    return _scoped_list(db, UsageAnalytics, cid)


@router.post("/usage-analytics", response_model=UsageAnalyticsOut, status_code=201)
def create_usage_analytics(
    payload: UsageAnalyticsCreate,
    db: Session = Depends(get_db),
    user: User = Depends(require_perm("admin.usage_analytics.create")),
):
    cid = _company_id(user)
    data = payload.model_dump(exclude_unset=True)
    _check_unique(db, UsageAnalytics, "reference", data.get("reference"), "reference", cid)
    obj = UsageAnalytics(company_id=cid)
    _apply(data, obj)
    db.add(obj)
    db.commit()
    db.refresh(obj)
    return obj


@router.put("/usage-analytics/{ident}", response_model=UsageAnalyticsOut)
def update_usage_analytics(
    ident: int,
    payload: UsageAnalyticsUpdate,
    db: Session = Depends(get_db),
    user: User = Depends(require_perm("admin.usage_analytics.modify")),
):
    cid = _company_id(user)
    obj = _get_or_404(db, UsageAnalytics, ident, "Analytique d'usage par tenant")
    if obj.company_id != cid:
        raise HTTPException(403, "Acces refuse.")
    _apply(payload.model_dump(exclude_unset=True), obj)
    db.commit()
    db.refresh(obj)
    return obj


@router.delete("/usage-analytics/{ident}", response_model=UsageAnalyticsOut)
def delete_usage_analytics(
    ident: int,
    db: Session = Depends(get_db),
    user: User = Depends(require_perm("admin.usage_analytics.modify")),
):
    cid = _company_id(user)
    obj = _get_or_404(db, UsageAnalytics, ident, "Analytique d'usage par tenant")
    if obj.company_id != cid:
        raise HTTPException(403, "Acces refuse.")
    obj.is_active = False
    db.commit()
    db.refresh(obj)
    return obj


# ─── Monitoring disponibilite / SLA ─────────────────────────────────────────────────

@router.get("/uptime-records", response_model=List[UptimeRecordOut])
def list_uptime_monitoring(statut: Optional[str] = None, db: Session = Depends(get_db),
    user: User = Depends(require_perm("admin.uptime_monitoring.read")),
):
    cid = _company_id(user)
    return _scoped_list(db, UptimeRecord, cid, {"statut": statut})


@router.post("/uptime-records", response_model=UptimeRecordOut, status_code=201)
def create_uptime_monitoring(
    payload: UptimeRecordCreate,
    db: Session = Depends(get_db),
    user: User = Depends(require_perm("admin.uptime_monitoring.create")),
):
    cid = _company_id(user)
    data = payload.model_dump(exclude_unset=True)
    _check_unique(db, UptimeRecord, "reference", data.get("reference"), "reference", cid)
    obj = UptimeRecord(company_id=cid)
    _apply(data, obj)
    db.add(obj)
    db.commit()
    db.refresh(obj)
    return obj


@router.put("/uptime-records/{ident}", response_model=UptimeRecordOut)
def update_uptime_monitoring(
    ident: int,
    payload: UptimeRecordUpdate,
    db: Session = Depends(get_db),
    user: User = Depends(require_perm("admin.uptime_monitoring.modify")),
):
    cid = _company_id(user)
    obj = _get_or_404(db, UptimeRecord, ident, "Monitoring disponibilite / SLA")
    if obj.company_id != cid:
        raise HTTPException(403, "Acces refuse.")
    _apply(payload.model_dump(exclude_unset=True), obj)
    db.commit()
    db.refresh(obj)
    return obj


@router.delete("/uptime-records/{ident}", response_model=UptimeRecordOut)
def delete_uptime_monitoring(
    ident: int,
    db: Session = Depends(get_db),
    user: User = Depends(require_perm("admin.uptime_monitoring.modify")),
):
    cid = _company_id(user)
    obj = _get_or_404(db, UptimeRecord, ident, "Monitoring disponibilite / SLA")
    if obj.company_id != cid:
        raise HTTPException(403, "Acces refuse.")
    obj.is_active = False
    db.commit()
    db.refresh(obj)
    return obj

