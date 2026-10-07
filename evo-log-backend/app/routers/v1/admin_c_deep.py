"""Routeur CRUD genere pour admin-saas (expansion)."""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import Optional, List

from app.core.database import get_db
from app.core.permissions import require_perm
from app.models.user import User
from app.models.admin_c_deep import (
    AdmCSubscriptionPlan,
    AdmCTenantInvite,
    AdmCApiToken,
    AdmCBillingInvoice,
    AdmCUsageMetering,
)
from app.schemas.admin_c_deep import (
    AdmCSubscriptionPlanCreate, AdmCSubscriptionPlanUpdate, AdmCSubscriptionPlanOut,
    AdmCTenantInviteCreate, AdmCTenantInviteUpdate, AdmCTenantInviteOut,
    AdmCApiTokenCreate, AdmCApiTokenUpdate, AdmCApiTokenOut,
    AdmCBillingInvoiceCreate, AdmCBillingInvoiceUpdate, AdmCBillingInvoiceOut,
    AdmCUsageMeteringCreate, AdmCUsageMeteringUpdate, AdmCUsageMeteringOut,
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
    from app.models import admin_c_deep as _md
    import enum as _pyenum
    out = {}
    for name in dir(_md):
        obj = getattr(_md, name)
        if isinstance(obj, type) and issubclass(obj, _pyenum.Enum) and obj is not _pyenum.Enum:
            out[name.lower()] = [{"code": m.name, "valeur": m.value} for m in obj]
    return out


# ─── Plans d' abonnement ─────────────────────────────────────────────────

@router.get("/admc-subscription-plans", response_model=List[AdmCSubscriptionPlanOut])
def list_subscription_plan(statut: Optional[str] = None, db: Session = Depends(get_db),
    user: User = Depends(require_perm("admin.subscription_plan.read")),
):
    cid = _company_id(user)
    return _scoped_list(db, AdmCSubscriptionPlan, cid, {"statut": statut})


@router.post("/admc-subscription-plans", response_model=AdmCSubscriptionPlanOut, status_code=201)
def create_subscription_plan(
    payload: AdmCSubscriptionPlanCreate,
    db: Session = Depends(get_db),
    user: User = Depends(require_perm("admin.subscription_plan.create")),
):
    cid = _company_id(user)
    data = payload.model_dump(exclude_unset=True)
    _check_unique(db, AdmCSubscriptionPlan, "reference", data.get("reference"), "reference", cid)
    obj = AdmCSubscriptionPlan(company_id=cid)
    _apply(data, obj)
    db.add(obj)
    db.commit()
    db.refresh(obj)
    return obj


@router.put("/admc-subscription-plans/{ident}", response_model=AdmCSubscriptionPlanOut)
def update_subscription_plan(
    ident: int,
    payload: AdmCSubscriptionPlanUpdate,
    db: Session = Depends(get_db),
    user: User = Depends(require_perm("admin.subscription_plan.modify")),
):
    cid = _company_id(user)
    obj = _get_or_404(db, AdmCSubscriptionPlan, ident, "Plans d' abonnement")
    if obj.company_id != cid:
        raise HTTPException(403, "Acces refuse.")
    _apply(payload.model_dump(exclude_unset=True), obj)
    db.commit()
    db.refresh(obj)
    return obj


@router.delete("/admc-subscription-plans/{ident}", response_model=AdmCSubscriptionPlanOut)
def delete_subscription_plan(
    ident: int,
    db: Session = Depends(get_db),
    user: User = Depends(require_perm("admin.subscription_plan.modify")),
):
    cid = _company_id(user)
    obj = _get_or_404(db, AdmCSubscriptionPlan, ident, "Plans d' abonnement")
    if obj.company_id != cid:
        raise HTTPException(403, "Acces refuse.")
    obj.is_active = False
    db.commit()
    db.refresh(obj)
    return obj


# ─── Invitations des locataires ─────────────────────────────────────────────────

@router.get("/admc-tenant-invites", response_model=List[AdmCTenantInviteOut])
def list_tenant_invite(statut: Optional[str] = None, db: Session = Depends(get_db),
    user: User = Depends(require_perm("admin.tenant_invite.read")),
):
    cid = _company_id(user)
    return _scoped_list(db, AdmCTenantInvite, cid, {"statut": statut})


@router.post("/admc-tenant-invites", response_model=AdmCTenantInviteOut, status_code=201)
def create_tenant_invite(
    payload: AdmCTenantInviteCreate,
    db: Session = Depends(get_db),
    user: User = Depends(require_perm("admin.tenant_invite.create")),
):
    cid = _company_id(user)
    data = payload.model_dump(exclude_unset=True)
    _check_unique(db, AdmCTenantInvite, "reference", data.get("reference"), "reference", cid)
    obj = AdmCTenantInvite(company_id=cid)
    _apply(data, obj)
    db.add(obj)
    db.commit()
    db.refresh(obj)
    return obj


@router.put("/admc-tenant-invites/{ident}", response_model=AdmCTenantInviteOut)
def update_tenant_invite(
    ident: int,
    payload: AdmCTenantInviteUpdate,
    db: Session = Depends(get_db),
    user: User = Depends(require_perm("admin.tenant_invite.modify")),
):
    cid = _company_id(user)
    obj = _get_or_404(db, AdmCTenantInvite, ident, "Invitations des locataires")
    if obj.company_id != cid:
        raise HTTPException(403, "Acces refuse.")
    _apply(payload.model_dump(exclude_unset=True), obj)
    db.commit()
    db.refresh(obj)
    return obj


@router.delete("/admc-tenant-invites/{ident}", response_model=AdmCTenantInviteOut)
def delete_tenant_invite(
    ident: int,
    db: Session = Depends(get_db),
    user: User = Depends(require_perm("admin.tenant_invite.modify")),
):
    cid = _company_id(user)
    obj = _get_or_404(db, AdmCTenantInvite, ident, "Invitations des locataires")
    if obj.company_id != cid:
        raise HTTPException(403, "Acces refuse.")
    obj.is_active = False
    db.commit()
    db.refresh(obj)
    return obj


# ─── Jeton d' API ─────────────────────────────────────────────────

@router.get("/admc-api-tokens", response_model=List[AdmCApiTokenOut])
def list_api_token(statut: Optional[str] = None, db: Session = Depends(get_db),
    user: User = Depends(require_perm("admin.api_token.read")),
):
    cid = _company_id(user)
    return _scoped_list(db, AdmCApiToken, cid, {"statut": statut})


@router.post("/admc-api-tokens", response_model=AdmCApiTokenOut, status_code=201)
def create_api_token(
    payload: AdmCApiTokenCreate,
    db: Session = Depends(get_db),
    user: User = Depends(require_perm("admin.api_token.create")),
):
    cid = _company_id(user)
    data = payload.model_dump(exclude_unset=True)
    _check_unique(db, AdmCApiToken, "reference", data.get("reference"), "reference", cid)
    obj = AdmCApiToken(company_id=cid)
    _apply(data, obj)
    db.add(obj)
    db.commit()
    db.refresh(obj)
    return obj


@router.put("/admc-api-tokens/{ident}", response_model=AdmCApiTokenOut)
def update_api_token(
    ident: int,
    payload: AdmCApiTokenUpdate,
    db: Session = Depends(get_db),
    user: User = Depends(require_perm("admin.api_token.modify")),
):
    cid = _company_id(user)
    obj = _get_or_404(db, AdmCApiToken, ident, "Jeton d' API")
    if obj.company_id != cid:
        raise HTTPException(403, "Acces refuse.")
    _apply(payload.model_dump(exclude_unset=True), obj)
    db.commit()
    db.refresh(obj)
    return obj


@router.delete("/admc-api-tokens/{ident}", response_model=AdmCApiTokenOut)
def delete_api_token(
    ident: int,
    db: Session = Depends(get_db),
    user: User = Depends(require_perm("admin.api_token.modify")),
):
    cid = _company_id(user)
    obj = _get_or_404(db, AdmCApiToken, ident, "Jeton d' API")
    if obj.company_id != cid:
        raise HTTPException(403, "Acces refuse.")
    obj.is_active = False
    db.commit()
    db.refresh(obj)
    return obj


# ─── Factures d' abonnement ─────────────────────────────────────────────────

@router.get("/admc-billing-invoices", response_model=List[AdmCBillingInvoiceOut])
def list_billing_invoice(statut: Optional[str] = None, db: Session = Depends(get_db),
    user: User = Depends(require_perm("admin.billing_invoice.read")),
):
    cid = _company_id(user)
    return _scoped_list(db, AdmCBillingInvoice, cid, {"statut": statut})


@router.post("/admc-billing-invoices", response_model=AdmCBillingInvoiceOut, status_code=201)
def create_billing_invoice(
    payload: AdmCBillingInvoiceCreate,
    db: Session = Depends(get_db),
    user: User = Depends(require_perm("admin.billing_invoice.create")),
):
    cid = _company_id(user)
    data = payload.model_dump(exclude_unset=True)
    _check_unique(db, AdmCBillingInvoice, "reference", data.get("reference"), "reference", cid)
    obj = AdmCBillingInvoice(company_id=cid)
    _apply(data, obj)
    db.add(obj)
    db.commit()
    db.refresh(obj)
    return obj


@router.put("/admc-billing-invoices/{ident}", response_model=AdmCBillingInvoiceOut)
def update_billing_invoice(
    ident: int,
    payload: AdmCBillingInvoiceUpdate,
    db: Session = Depends(get_db),
    user: User = Depends(require_perm("admin.billing_invoice.modify")),
):
    cid = _company_id(user)
    obj = _get_or_404(db, AdmCBillingInvoice, ident, "Factures d' abonnement")
    if obj.company_id != cid:
        raise HTTPException(403, "Acces refuse.")
    _apply(payload.model_dump(exclude_unset=True), obj)
    db.commit()
    db.refresh(obj)
    return obj


@router.delete("/admc-billing-invoices/{ident}", response_model=AdmCBillingInvoiceOut)
def delete_billing_invoice(
    ident: int,
    db: Session = Depends(get_db),
    user: User = Depends(require_perm("admin.billing_invoice.modify")),
):
    cid = _company_id(user)
    obj = _get_or_404(db, AdmCBillingInvoice, ident, "Factures d' abonnement")
    if obj.company_id != cid:
        raise HTTPException(403, "Acces refuse.")
    obj.is_active = False
    db.commit()
    db.refresh(obj)
    return obj


# ─── Mesure d' usage ─────────────────────────────────────────────────

@router.get("/admc-usage-metering", response_model=List[AdmCUsageMeteringOut])
def list_usage_metering(statut: Optional[str] = None, db: Session = Depends(get_db),
    user: User = Depends(require_perm("admin.usage_metering.read")),
):
    cid = _company_id(user)
    return _scoped_list(db, AdmCUsageMetering, cid, {"statut": statut})


@router.post("/admc-usage-metering", response_model=AdmCUsageMeteringOut, status_code=201)
def create_usage_metering(
    payload: AdmCUsageMeteringCreate,
    db: Session = Depends(get_db),
    user: User = Depends(require_perm("admin.usage_metering.create")),
):
    cid = _company_id(user)
    data = payload.model_dump(exclude_unset=True)
    _check_unique(db, AdmCUsageMetering, "reference", data.get("reference"), "reference", cid)
    obj = AdmCUsageMetering(company_id=cid)
    _apply(data, obj)
    db.add(obj)
    db.commit()
    db.refresh(obj)
    return obj


@router.put("/admc-usage-metering/{ident}", response_model=AdmCUsageMeteringOut)
def update_usage_metering(
    ident: int,
    payload: AdmCUsageMeteringUpdate,
    db: Session = Depends(get_db),
    user: User = Depends(require_perm("admin.usage_metering.modify")),
):
    cid = _company_id(user)
    obj = _get_or_404(db, AdmCUsageMetering, ident, "Mesure d' usage")
    if obj.company_id != cid:
        raise HTTPException(403, "Acces refuse.")
    _apply(payload.model_dump(exclude_unset=True), obj)
    db.commit()
    db.refresh(obj)
    return obj


@router.delete("/admc-usage-metering/{ident}", response_model=AdmCUsageMeteringOut)
def delete_usage_metering(
    ident: int,
    db: Session = Depends(get_db),
    user: User = Depends(require_perm("admin.usage_metering.modify")),
):
    cid = _company_id(user)
    obj = _get_or_404(db, AdmCUsageMetering, ident, "Mesure d' usage")
    if obj.company_id != cid:
        raise HTTPException(403, "Acces refuse.")
    obj.is_active = False
    db.commit()
    db.refresh(obj)
    return obj

