"""Routeur CRUD genere pour superadmin-cadc (expansion)."""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import Optional, List

from app.core.database import get_db
from app.core.permissions import require_perm
from app.models.user import User
from app.models.superadmin_deep import (
    PlatformAudit,
    ComplianceDashboard,
    RetentionPolicy,
    PlatformIncident,
    AccessReview,
    SoftwareLicense,
    TechnologyPartner,
    SaasRevenueRecord,
    GlobalConfigSetting,
    DrPlan,
)
from app.schemas.superadmin_deep import (
    PlatformAuditCreate, PlatformAuditUpdate, PlatformAuditOut,
    ComplianceDashboardCreate, ComplianceDashboardUpdate, ComplianceDashboardOut,
    RetentionPolicyCreate, RetentionPolicyUpdate, RetentionPolicyOut,
    PlatformIncidentCreate, PlatformIncidentUpdate, PlatformIncidentOut,
    AccessReviewCreate, AccessReviewUpdate, AccessReviewOut,
    SoftwareLicenseCreate, SoftwareLicenseUpdate, SoftwareLicenseOut,
    TechnologyPartnerCreate, TechnologyPartnerUpdate, TechnologyPartnerOut,
    SaasRevenueRecordCreate, SaasRevenueRecordUpdate, SaasRevenueRecordOut,
    GlobalConfigSettingCreate, GlobalConfigSettingUpdate, GlobalConfigSettingOut,
    DrPlanCreate, DrPlanUpdate, DrPlanOut,
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
    from app.models import superadmin_deep as _md
    import enum as _pyenum
    out = {}
    for name in dir(_md):
        obj = getattr(_md, name)
        if isinstance(obj, type) and issubclass(obj, _pyenum.Enum) and obj is not _pyenum.Enum:
            out[name.lower()] = [{"code": m.name, "valeur": m.value} for m in obj]
    return out


# ─── Audit global plateforme multi-tenant ─────────────────────────────────────────────────

@router.get("/platform-audits", response_model=List[PlatformAuditOut])
def list_platform_audit(statut: Optional[str] = None, db: Session = Depends(get_db),
    user: User = Depends(require_perm("superadmin.platform_audit.read")),
):
    cid = _company_id(user)
    return _scoped_list(db, PlatformAudit, cid, {"statut": statut})


@router.post("/platform-audits", response_model=PlatformAuditOut, status_code=201)
def create_platform_audit(
    payload: PlatformAuditCreate,
    db: Session = Depends(get_db),
    user: User = Depends(require_perm("superadmin.platform_audit.create")),
):
    cid = _company_id(user)
    data = payload.model_dump(exclude_unset=True)
    _check_unique(db, PlatformAudit, "reference", data.get("reference"), "reference", cid)
    obj = PlatformAudit(company_id=cid)
    _apply(data, obj)
    db.add(obj)
    db.commit()
    db.refresh(obj)
    return obj


@router.put("/platform-audits/{ident}", response_model=PlatformAuditOut)
def update_platform_audit(
    ident: int,
    payload: PlatformAuditUpdate,
    db: Session = Depends(get_db),
    user: User = Depends(require_perm("superadmin.platform_audit.modify")),
):
    cid = _company_id(user)
    obj = _get_or_404(db, PlatformAudit, ident, "Audit global plateforme multi-tenant")
    if obj.company_id != cid:
        raise HTTPException(403, "Acces refuse.")
    _apply(payload.model_dump(exclude_unset=True), obj)
    db.commit()
    db.refresh(obj)
    return obj


@router.delete("/platform-audits/{ident}", response_model=PlatformAuditOut)
def delete_platform_audit(
    ident: int,
    db: Session = Depends(get_db),
    user: User = Depends(require_perm("superadmin.platform_audit.modify")),
):
    cid = _company_id(user)
    obj = _get_or_404(db, PlatformAudit, ident, "Audit global plateforme multi-tenant")
    if obj.company_id != cid:
        raise HTTPException(403, "Acces refuse.")
    obj.is_active = False
    db.commit()
    db.refresh(obj)
    return obj


# ─── Tableaux conformite globale ─────────────────────────────────────────────────

@router.get("/compliance-dashboards", response_model=List[ComplianceDashboardOut])
def list_compliance_dashboards(db: Session = Depends(get_db),
    user: User = Depends(require_perm("superadmin.compliance_dashboards.read")),
):
    cid = _company_id(user)
    return _scoped_list(db, ComplianceDashboard, cid)


@router.post("/compliance-dashboards", response_model=ComplianceDashboardOut, status_code=201)
def create_compliance_dashboards(
    payload: ComplianceDashboardCreate,
    db: Session = Depends(get_db),
    user: User = Depends(require_perm("superadmin.compliance_dashboards.create")),
):
    cid = _company_id(user)
    data = payload.model_dump(exclude_unset=True)
    _check_unique(db, ComplianceDashboard, "reference", data.get("reference"), "reference", cid)
    obj = ComplianceDashboard(company_id=cid)
    _apply(data, obj)
    db.add(obj)
    db.commit()
    db.refresh(obj)
    return obj


@router.put("/compliance-dashboards/{ident}", response_model=ComplianceDashboardOut)
def update_compliance_dashboards(
    ident: int,
    payload: ComplianceDashboardUpdate,
    db: Session = Depends(get_db),
    user: User = Depends(require_perm("superadmin.compliance_dashboards.modify")),
):
    cid = _company_id(user)
    obj = _get_or_404(db, ComplianceDashboard, ident, "Tableaux conformite globale")
    if obj.company_id != cid:
        raise HTTPException(403, "Acces refuse.")
    _apply(payload.model_dump(exclude_unset=True), obj)
    db.commit()
    db.refresh(obj)
    return obj


@router.delete("/compliance-dashboards/{ident}", response_model=ComplianceDashboardOut)
def delete_compliance_dashboards(
    ident: int,
    db: Session = Depends(get_db),
    user: User = Depends(require_perm("superadmin.compliance_dashboards.modify")),
):
    cid = _company_id(user)
    obj = _get_or_404(db, ComplianceDashboard, ident, "Tableaux conformite globale")
    if obj.company_id != cid:
        raise HTTPException(403, "Acces refuse.")
    obj.is_active = False
    db.commit()
    db.refresh(obj)
    return obj


# ─── Politique retention / purge ─────────────────────────────────────────────────

@router.get("/retention-policies", response_model=List[RetentionPolicyOut])
def list_data_retention(db: Session = Depends(get_db),
    user: User = Depends(require_perm("superadmin.data_retention.read")),
):
    cid = _company_id(user)
    return _scoped_list(db, RetentionPolicy, cid)


@router.post("/retention-policies", response_model=RetentionPolicyOut, status_code=201)
def create_data_retention(
    payload: RetentionPolicyCreate,
    db: Session = Depends(get_db),
    user: User = Depends(require_perm("superadmin.data_retention.create")),
):
    cid = _company_id(user)
    data = payload.model_dump(exclude_unset=True)
    _check_unique(db, RetentionPolicy, "reference", data.get("reference"), "reference", cid)
    obj = RetentionPolicy(company_id=cid)
    _apply(data, obj)
    db.add(obj)
    db.commit()
    db.refresh(obj)
    return obj


@router.put("/retention-policies/{ident}", response_model=RetentionPolicyOut)
def update_data_retention(
    ident: int,
    payload: RetentionPolicyUpdate,
    db: Session = Depends(get_db),
    user: User = Depends(require_perm("superadmin.data_retention.modify")),
):
    cid = _company_id(user)
    obj = _get_or_404(db, RetentionPolicy, ident, "Politique retention / purge")
    if obj.company_id != cid:
        raise HTTPException(403, "Acces refuse.")
    _apply(payload.model_dump(exclude_unset=True), obj)
    db.commit()
    db.refresh(obj)
    return obj


@router.delete("/retention-policies/{ident}", response_model=RetentionPolicyOut)
def delete_data_retention(
    ident: int,
    db: Session = Depends(get_db),
    user: User = Depends(require_perm("superadmin.data_retention.modify")),
):
    cid = _company_id(user)
    obj = _get_or_404(db, RetentionPolicy, ident, "Politique retention / purge")
    if obj.company_id != cid:
        raise HTTPException(403, "Acces refuse.")
    obj.is_active = False
    db.commit()
    db.refresh(obj)
    return obj


# ─── Reponse incidents plateforme ─────────────────────────────────────────────────

@router.get("/platform-incidents", response_model=List[PlatformIncidentOut])
def list_incident_response(statut: Optional[str] = None, db: Session = Depends(get_db),
    user: User = Depends(require_perm("superadmin.incident_response.read")),
):
    cid = _company_id(user)
    return _scoped_list(db, PlatformIncident, cid, {"statut": statut})


@router.post("/platform-incidents", response_model=PlatformIncidentOut, status_code=201)
def create_incident_response(
    payload: PlatformIncidentCreate,
    db: Session = Depends(get_db),
    user: User = Depends(require_perm("superadmin.incident_response.create")),
):
    cid = _company_id(user)
    data = payload.model_dump(exclude_unset=True)
    _check_unique(db, PlatformIncident, "reference", data.get("reference"), "reference", cid)
    obj = PlatformIncident(company_id=cid)
    _apply(data, obj)
    db.add(obj)
    db.commit()
    db.refresh(obj)
    return obj


@router.put("/platform-incidents/{ident}", response_model=PlatformIncidentOut)
def update_incident_response(
    ident: int,
    payload: PlatformIncidentUpdate,
    db: Session = Depends(get_db),
    user: User = Depends(require_perm("superadmin.incident_response.modify")),
):
    cid = _company_id(user)
    obj = _get_or_404(db, PlatformIncident, ident, "Reponse incidents plateforme")
    if obj.company_id != cid:
        raise HTTPException(403, "Acces refuse.")
    _apply(payload.model_dump(exclude_unset=True), obj)
    db.commit()
    db.refresh(obj)
    return obj


@router.delete("/platform-incidents/{ident}", response_model=PlatformIncidentOut)
def delete_incident_response(
    ident: int,
    db: Session = Depends(get_db),
    user: User = Depends(require_perm("superadmin.incident_response.modify")),
):
    cid = _company_id(user)
    obj = _get_or_404(db, PlatformIncident, ident, "Reponse incidents plateforme")
    if obj.company_id != cid:
        raise HTTPException(403, "Acces refuse.")
    obj.is_active = False
    db.commit()
    db.refresh(obj)
    return obj


# ─── Revue periodique des acces ─────────────────────────────────────────────────

@router.get("/access-reviews", response_model=List[AccessReviewOut])
def list_access_review(statut: Optional[str] = None, db: Session = Depends(get_db),
    user: User = Depends(require_perm("superadmin.access_review.read")),
):
    cid = _company_id(user)
    return _scoped_list(db, AccessReview, cid, {"statut": statut})


@router.post("/access-reviews", response_model=AccessReviewOut, status_code=201)
def create_access_review(
    payload: AccessReviewCreate,
    db: Session = Depends(get_db),
    user: User = Depends(require_perm("superadmin.access_review.create")),
):
    cid = _company_id(user)
    data = payload.model_dump(exclude_unset=True)
    _check_unique(db, AccessReview, "reference", data.get("reference"), "reference", cid)
    obj = AccessReview(company_id=cid)
    _apply(data, obj)
    db.add(obj)
    db.commit()
    db.refresh(obj)
    return obj


@router.put("/access-reviews/{ident}", response_model=AccessReviewOut)
def update_access_review(
    ident: int,
    payload: AccessReviewUpdate,
    db: Session = Depends(get_db),
    user: User = Depends(require_perm("superadmin.access_review.modify")),
):
    cid = _company_id(user)
    obj = _get_or_404(db, AccessReview, ident, "Revue periodique des acces")
    if obj.company_id != cid:
        raise HTTPException(403, "Acces refuse.")
    _apply(payload.model_dump(exclude_unset=True), obj)
    db.commit()
    db.refresh(obj)
    return obj


@router.delete("/access-reviews/{ident}", response_model=AccessReviewOut)
def delete_access_review(
    ident: int,
    db: Session = Depends(get_db),
    user: User = Depends(require_perm("superadmin.access_review.modify")),
):
    cid = _company_id(user)
    obj = _get_or_404(db, AccessReview, ident, "Revue periodique des acces")
    if obj.company_id != cid:
        raise HTTPException(403, "Acces refuse.")
    obj.is_active = False
    db.commit()
    db.refresh(obj)
    return obj


# ─── Gestion licences et modules ─────────────────────────────────────────────────

@router.get("/software-licenses", response_model=List[SoftwareLicenseOut])
def list_license_management(statut: Optional[str] = None, db: Session = Depends(get_db),
    user: User = Depends(require_perm("superadmin.license_management.read")),
):
    cid = _company_id(user)
    return _scoped_list(db, SoftwareLicense, cid, {"statut": statut})


@router.post("/software-licenses", response_model=SoftwareLicenseOut, status_code=201)
def create_license_management(
    payload: SoftwareLicenseCreate,
    db: Session = Depends(get_db),
    user: User = Depends(require_perm("superadmin.license_management.create")),
):
    cid = _company_id(user)
    data = payload.model_dump(exclude_unset=True)
    _check_unique(db, SoftwareLicense, "reference", data.get("reference"), "reference", cid)
    obj = SoftwareLicense(company_id=cid)
    _apply(data, obj)
    db.add(obj)
    db.commit()
    db.refresh(obj)
    return obj


@router.put("/software-licenses/{ident}", response_model=SoftwareLicenseOut)
def update_license_management(
    ident: int,
    payload: SoftwareLicenseUpdate,
    db: Session = Depends(get_db),
    user: User = Depends(require_perm("superadmin.license_management.modify")),
):
    cid = _company_id(user)
    obj = _get_or_404(db, SoftwareLicense, ident, "Gestion licences et modules")
    if obj.company_id != cid:
        raise HTTPException(403, "Acces refuse.")
    _apply(payload.model_dump(exclude_unset=True), obj)
    db.commit()
    db.refresh(obj)
    return obj


@router.delete("/software-licenses/{ident}", response_model=SoftwareLicenseOut)
def delete_license_management(
    ident: int,
    db: Session = Depends(get_db),
    user: User = Depends(require_perm("superadmin.license_management.modify")),
):
    cid = _company_id(user)
    obj = _get_or_404(db, SoftwareLicense, ident, "Gestion licences et modules")
    if obj.company_id != cid:
        raise HTTPException(403, "Acces refuse.")
    obj.is_active = False
    db.commit()
    db.refresh(obj)
    return obj


# ─── Reseau partenaires technologiques ─────────────────────────────────────────────────

@router.get("/technology-partners", response_model=List[TechnologyPartnerOut])
def list_partner_network(statut: Optional[str] = None, db: Session = Depends(get_db),
    user: User = Depends(require_perm("superadmin.partner_network.read")),
):
    cid = _company_id(user)
    return _scoped_list(db, TechnologyPartner, cid, {"statut": statut})


@router.post("/technology-partners", response_model=TechnologyPartnerOut, status_code=201)
def create_partner_network(
    payload: TechnologyPartnerCreate,
    db: Session = Depends(get_db),
    user: User = Depends(require_perm("superadmin.partner_network.create")),
):
    cid = _company_id(user)
    data = payload.model_dump(exclude_unset=True)
    _check_unique(db, TechnologyPartner, "reference", data.get("reference"), "reference", cid)
    obj = TechnologyPartner(company_id=cid)
    _apply(data, obj)
    db.add(obj)
    db.commit()
    db.refresh(obj)
    return obj


@router.put("/technology-partners/{ident}", response_model=TechnologyPartnerOut)
def update_partner_network(
    ident: int,
    payload: TechnologyPartnerUpdate,
    db: Session = Depends(get_db),
    user: User = Depends(require_perm("superadmin.partner_network.modify")),
):
    cid = _company_id(user)
    obj = _get_or_404(db, TechnologyPartner, ident, "Reseau partenaires technologiques")
    if obj.company_id != cid:
        raise HTTPException(403, "Acces refuse.")
    _apply(payload.model_dump(exclude_unset=True), obj)
    db.commit()
    db.refresh(obj)
    return obj


@router.delete("/technology-partners/{ident}", response_model=TechnologyPartnerOut)
def delete_partner_network(
    ident: int,
    db: Session = Depends(get_db),
    user: User = Depends(require_perm("superadmin.partner_network.modify")),
):
    cid = _company_id(user)
    obj = _get_or_404(db, TechnologyPartner, ident, "Reseau partenaires technologiques")
    if obj.company_id != cid:
        raise HTTPException(403, "Acces refuse.")
    obj.is_active = False
    db.commit()
    db.refresh(obj)
    return obj


# ─── Analytique revenus SaaS / MRR ─────────────────────────────────────────────────

@router.get("/saas-revenue-records", response_model=List[SaasRevenueRecordOut])
def list_revenue_analytics(db: Session = Depends(get_db),
    user: User = Depends(require_perm("superadmin.revenue_analytics.read")),
):
    cid = _company_id(user)
    return _scoped_list(db, SaasRevenueRecord, cid)


@router.post("/saas-revenue-records", response_model=SaasRevenueRecordOut, status_code=201)
def create_revenue_analytics(
    payload: SaasRevenueRecordCreate,
    db: Session = Depends(get_db),
    user: User = Depends(require_perm("superadmin.revenue_analytics.create")),
):
    cid = _company_id(user)
    data = payload.model_dump(exclude_unset=True)
    _check_unique(db, SaasRevenueRecord, "reference", data.get("reference"), "reference", cid)
    obj = SaasRevenueRecord(company_id=cid)
    _apply(data, obj)
    db.add(obj)
    db.commit()
    db.refresh(obj)
    return obj


@router.put("/saas-revenue-records/{ident}", response_model=SaasRevenueRecordOut)
def update_revenue_analytics(
    ident: int,
    payload: SaasRevenueRecordUpdate,
    db: Session = Depends(get_db),
    user: User = Depends(require_perm("superadmin.revenue_analytics.modify")),
):
    cid = _company_id(user)
    obj = _get_or_404(db, SaasRevenueRecord, ident, "Analytique revenus SaaS / MRR")
    if obj.company_id != cid:
        raise HTTPException(403, "Acces refuse.")
    _apply(payload.model_dump(exclude_unset=True), obj)
    db.commit()
    db.refresh(obj)
    return obj


@router.delete("/saas-revenue-records/{ident}", response_model=SaasRevenueRecordOut)
def delete_revenue_analytics(
    ident: int,
    db: Session = Depends(get_db),
    user: User = Depends(require_perm("superadmin.revenue_analytics.modify")),
):
    cid = _company_id(user)
    obj = _get_or_404(db, SaasRevenueRecord, ident, "Analytique revenus SaaS / MRR")
    if obj.company_id != cid:
        raise HTTPException(403, "Acces refuse.")
    obj.is_active = False
    db.commit()
    db.refresh(obj)
    return obj


# ─── Configuration systeme globale ─────────────────────────────────────────────────

@router.get("/global-config-settings", response_model=List[GlobalConfigSettingOut])
def list_system_config(statut: Optional[str] = None, db: Session = Depends(get_db),
    user: User = Depends(require_perm("superadmin.system_config.read")),
):
    cid = _company_id(user)
    return _scoped_list(db, GlobalConfigSetting, cid, {"statut": statut})


@router.post("/global-config-settings", response_model=GlobalConfigSettingOut, status_code=201)
def create_system_config(
    payload: GlobalConfigSettingCreate,
    db: Session = Depends(get_db),
    user: User = Depends(require_perm("superadmin.system_config.create")),
):
    cid = _company_id(user)
    data = payload.model_dump(exclude_unset=True)
    _check_unique(db, GlobalConfigSetting, "code_setting", data.get("code_setting"), "code_setting", cid)
    obj = GlobalConfigSetting(company_id=cid)
    _apply(data, obj)
    db.add(obj)
    db.commit()
    db.refresh(obj)
    return obj


@router.put("/global-config-settings/{ident}", response_model=GlobalConfigSettingOut)
def update_system_config(
    ident: int,
    payload: GlobalConfigSettingUpdate,
    db: Session = Depends(get_db),
    user: User = Depends(require_perm("superadmin.system_config.modify")),
):
    cid = _company_id(user)
    obj = _get_or_404(db, GlobalConfigSetting, ident, "Configuration systeme globale")
    if obj.company_id != cid:
        raise HTTPException(403, "Acces refuse.")
    _apply(payload.model_dump(exclude_unset=True), obj)
    db.commit()
    db.refresh(obj)
    return obj


@router.delete("/global-config-settings/{ident}", response_model=GlobalConfigSettingOut)
def delete_system_config(
    ident: int,
    db: Session = Depends(get_db),
    user: User = Depends(require_perm("superadmin.system_config.modify")),
):
    cid = _company_id(user)
    obj = _get_or_404(db, GlobalConfigSetting, ident, "Configuration systeme globale")
    if obj.company_id != cid:
        raise HTTPException(403, "Acces refuse.")
    obj.is_active = False
    db.commit()
    db.refresh(obj)
    return obj


# ─── Plan reprise activite ─────────────────────────────────────────────────

@router.get("/dr-plans", response_model=List[DrPlanOut])
def list_disaster_recovery(db: Session = Depends(get_db),
    user: User = Depends(require_perm("superadmin.disaster_recovery.read")),
):
    cid = _company_id(user)
    return _scoped_list(db, DrPlan, cid)


@router.post("/dr-plans", response_model=DrPlanOut, status_code=201)
def create_disaster_recovery(
    payload: DrPlanCreate,
    db: Session = Depends(get_db),
    user: User = Depends(require_perm("superadmin.disaster_recovery.create")),
):
    cid = _company_id(user)
    data = payload.model_dump(exclude_unset=True)
    _check_unique(db, DrPlan, "reference", data.get("reference"), "reference", cid)
    obj = DrPlan(company_id=cid)
    _apply(data, obj)
    db.add(obj)
    db.commit()
    db.refresh(obj)
    return obj


@router.put("/dr-plans/{ident}", response_model=DrPlanOut)
def update_disaster_recovery(
    ident: int,
    payload: DrPlanUpdate,
    db: Session = Depends(get_db),
    user: User = Depends(require_perm("superadmin.disaster_recovery.modify")),
):
    cid = _company_id(user)
    obj = _get_or_404(db, DrPlan, ident, "Plan reprise activite")
    if obj.company_id != cid:
        raise HTTPException(403, "Acces refuse.")
    _apply(payload.model_dump(exclude_unset=True), obj)
    db.commit()
    db.refresh(obj)
    return obj


@router.delete("/dr-plans/{ident}", response_model=DrPlanOut)
def delete_disaster_recovery(
    ident: int,
    db: Session = Depends(get_db),
    user: User = Depends(require_perm("superadmin.disaster_recovery.modify")),
):
    cid = _company_id(user)
    obj = _get_or_404(db, DrPlan, ident, "Plan reprise activite")
    if obj.company_id != cid:
        raise HTTPException(403, "Acces refuse.")
    obj.is_active = False
    db.commit()
    db.refresh(obj)
    return obj

