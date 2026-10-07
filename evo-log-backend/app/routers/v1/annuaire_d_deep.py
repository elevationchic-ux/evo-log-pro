"""Routeur CRUD genere pour annuaire-prestataires (expansion)."""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import Optional, List

from app.core.database import get_db
from app.core.permissions import require_perm
from app.models.user import User
from app.models.annuaire_d_deep import (
    ProvProfile,
    ProvCategory,
    ProvCertification,
    ProvInsuranceAttestation,
    ProvServiceContract,
    ProvEvaluation,
    ProvIncident,
    ProvAvailabilityCalendar,
    ProvPriceList,
    ProvContact,
    ProvOnboarding,
    ProvReview,
    ProvRfqRequest,
    ProvIntervention,
    ProvComplianceDoc,
    ProvBankDetail,
    ProvBlacklist,
)
from app.schemas.annuaire_d_deep import (
    ProvProfileCreate, ProvProfileUpdate, ProvProfileOut,
    ProvCategoryCreate, ProvCategoryUpdate, ProvCategoryOut,
    ProvCertificationCreate, ProvCertificationUpdate, ProvCertificationOut,
    ProvInsuranceAttestationCreate, ProvInsuranceAttestationUpdate, ProvInsuranceAttestationOut,
    ProvServiceContractCreate, ProvServiceContractUpdate, ProvServiceContractOut,
    ProvEvaluationCreate, ProvEvaluationUpdate, ProvEvaluationOut,
    ProvIncidentCreate, ProvIncidentUpdate, ProvIncidentOut,
    ProvAvailabilityCalendarCreate, ProvAvailabilityCalendarUpdate, ProvAvailabilityCalendarOut,
    ProvPriceListCreate, ProvPriceListUpdate, ProvPriceListOut,
    ProvContactCreate, ProvContactUpdate, ProvContactOut,
    ProvOnboardingCreate, ProvOnboardingUpdate, ProvOnboardingOut,
    ProvReviewCreate, ProvReviewUpdate, ProvReviewOut,
    ProvRfqRequestCreate, ProvRfqRequestUpdate, ProvRfqRequestOut,
    ProvInterventionCreate, ProvInterventionUpdate, ProvInterventionOut,
    ProvComplianceDocCreate, ProvComplianceDocUpdate, ProvComplianceDocOut,
    ProvBankDetailCreate, ProvBankDetailUpdate, ProvBankDetailOut,
    ProvBlacklistCreate, ProvBlacklistUpdate, ProvBlacklistOut,
)

router = APIRouter(tags=["annuaire-prestataires (expansion)"])


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

@router.get("/nomenclatures", summary="Vocabulaire metier annuaire-prestataires")
def nomenclatures(user: User = Depends(require_perm("transport.nomenclature.read"))):
    from app.models import annuaire_d_deep as _md
    import enum as _pyenum
    out = {}
    for name in dir(_md):
        obj = getattr(_md, name)
        if isinstance(obj, type) and issubclass(obj, _pyenum.Enum) and obj is not _pyenum.Enum:
            out[name.lower()] = [{"code": m.name, "valeur": m.value} for m in obj]
    return out


# ─── Fiches prestataires ─────────────────────────────────────────────────

@router.get("/prov-provider-profiles", response_model=List[ProvProfileOut])
def list_provider_profile(statut: Optional[str] = None, db: Session = Depends(get_db),
    user: User = Depends(require_perm("transport.provider_profile.read")),
):
    cid = _company_id(user)
    return _scoped_list(db, ProvProfile, cid, {"statut": statut})


@router.post("/prov-provider-profiles", response_model=ProvProfileOut, status_code=201)
def create_provider_profile(
    payload: ProvProfileCreate,
    db: Session = Depends(get_db),
    user: User = Depends(require_perm("transport.provider_profile.create")),
):
    cid = _company_id(user)
    data = payload.model_dump(exclude_unset=True)
    _check_unique(db, ProvProfile, "reference", data.get("reference"), "reference", cid)
    obj = ProvProfile(company_id=cid)
    _apply(data, obj)
    db.add(obj)
    db.commit()
    db.refresh(obj)
    return obj


@router.put("/prov-provider-profiles/{ident}", response_model=ProvProfileOut)
def update_provider_profile(
    ident: int,
    payload: ProvProfileUpdate,
    db: Session = Depends(get_db),
    user: User = Depends(require_perm("transport.provider_profile.modify")),
):
    cid = _company_id(user)
    obj = _get_or_404(db, ProvProfile, ident, "Fiches prestataires")
    if obj.company_id != cid:
        raise HTTPException(403, "Acces refuse.")
    _apply(payload.model_dump(exclude_unset=True), obj)
    db.commit()
    db.refresh(obj)
    return obj


@router.delete("/prov-provider-profiles/{ident}", response_model=ProvProfileOut)
def delete_provider_profile(
    ident: int,
    db: Session = Depends(get_db),
    user: User = Depends(require_perm("transport.provider_profile.modify")),
):
    cid = _company_id(user)
    obj = _get_or_404(db, ProvProfile, ident, "Fiches prestataires")
    if obj.company_id != cid:
        raise HTTPException(403, "Acces refuse.")
    obj.is_active = False
    db.commit()
    db.refresh(obj)
    return obj


# ─── Categories de prestataires ─────────────────────────────────────────────────

@router.get("/prov-provider-categories", response_model=List[ProvCategoryOut])
def list_provider_category(statut: Optional[str] = None, db: Session = Depends(get_db),
    user: User = Depends(require_perm("transport.provider_category.read")),
):
    cid = _company_id(user)
    return _scoped_list(db, ProvCategory, cid, {"statut": statut})


@router.post("/prov-provider-categories", response_model=ProvCategoryOut, status_code=201)
def create_provider_category(
    payload: ProvCategoryCreate,
    db: Session = Depends(get_db),
    user: User = Depends(require_perm("transport.provider_category.create")),
):
    cid = _company_id(user)
    data = payload.model_dump(exclude_unset=True)
    _check_unique(db, ProvCategory, "reference", data.get("reference"), "reference", cid)
    obj = ProvCategory(company_id=cid)
    _apply(data, obj)
    db.add(obj)
    db.commit()
    db.refresh(obj)
    return obj


@router.put("/prov-provider-categories/{ident}", response_model=ProvCategoryOut)
def update_provider_category(
    ident: int,
    payload: ProvCategoryUpdate,
    db: Session = Depends(get_db),
    user: User = Depends(require_perm("transport.provider_category.modify")),
):
    cid = _company_id(user)
    obj = _get_or_404(db, ProvCategory, ident, "Categories de prestataires")
    if obj.company_id != cid:
        raise HTTPException(403, "Acces refuse.")
    _apply(payload.model_dump(exclude_unset=True), obj)
    db.commit()
    db.refresh(obj)
    return obj


@router.delete("/prov-provider-categories/{ident}", response_model=ProvCategoryOut)
def delete_provider_category(
    ident: int,
    db: Session = Depends(get_db),
    user: User = Depends(require_perm("transport.provider_category.modify")),
):
    cid = _company_id(user)
    obj = _get_or_404(db, ProvCategory, ident, "Categories de prestataires")
    if obj.company_id != cid:
        raise HTTPException(403, "Acces refuse.")
    obj.is_active = False
    db.commit()
    db.refresh(obj)
    return obj


# ─── Certifications prestataires ─────────────────────────────────────────────────

@router.get("/prov-provider-certifications", response_model=List[ProvCertificationOut])
def list_provider_certification(statut: Optional[str] = None, db: Session = Depends(get_db),
    user: User = Depends(require_perm("transport.provider_certification.read")),
):
    cid = _company_id(user)
    return _scoped_list(db, ProvCertification, cid, {"statut": statut})


@router.post("/prov-provider-certifications", response_model=ProvCertificationOut, status_code=201)
def create_provider_certification(
    payload: ProvCertificationCreate,
    db: Session = Depends(get_db),
    user: User = Depends(require_perm("transport.provider_certification.create")),
):
    cid = _company_id(user)
    data = payload.model_dump(exclude_unset=True)
    _check_unique(db, ProvCertification, "reference", data.get("reference"), "reference", cid)
    obj = ProvCertification(company_id=cid)
    _apply(data, obj)
    db.add(obj)
    db.commit()
    db.refresh(obj)
    return obj


@router.put("/prov-provider-certifications/{ident}", response_model=ProvCertificationOut)
def update_provider_certification(
    ident: int,
    payload: ProvCertificationUpdate,
    db: Session = Depends(get_db),
    user: User = Depends(require_perm("transport.provider_certification.modify")),
):
    cid = _company_id(user)
    obj = _get_or_404(db, ProvCertification, ident, "Certifications prestataires")
    if obj.company_id != cid:
        raise HTTPException(403, "Acces refuse.")
    _apply(payload.model_dump(exclude_unset=True), obj)
    db.commit()
    db.refresh(obj)
    return obj


@router.delete("/prov-provider-certifications/{ident}", response_model=ProvCertificationOut)
def delete_provider_certification(
    ident: int,
    db: Session = Depends(get_db),
    user: User = Depends(require_perm("transport.provider_certification.modify")),
):
    cid = _company_id(user)
    obj = _get_or_404(db, ProvCertification, ident, "Certifications prestataires")
    if obj.company_id != cid:
        raise HTTPException(403, "Acces refuse.")
    obj.is_active = False
    db.commit()
    db.refresh(obj)
    return obj


# ─── Attestations d' assurance ─────────────────────────────────────────────────

@router.get("/prov-insurance-attestations", response_model=List[ProvInsuranceAttestationOut])
def list_insurance_attestation(statut: Optional[str] = None, db: Session = Depends(get_db),
    user: User = Depends(require_perm("transport.insurance_attestation.read")),
):
    cid = _company_id(user)
    return _scoped_list(db, ProvInsuranceAttestation, cid, {"statut": statut})


@router.post("/prov-insurance-attestations", response_model=ProvInsuranceAttestationOut, status_code=201)
def create_insurance_attestation(
    payload: ProvInsuranceAttestationCreate,
    db: Session = Depends(get_db),
    user: User = Depends(require_perm("transport.insurance_attestation.create")),
):
    cid = _company_id(user)
    data = payload.model_dump(exclude_unset=True)
    _check_unique(db, ProvInsuranceAttestation, "reference", data.get("reference"), "reference", cid)
    obj = ProvInsuranceAttestation(company_id=cid)
    _apply(data, obj)
    db.add(obj)
    db.commit()
    db.refresh(obj)
    return obj


@router.put("/prov-insurance-attestations/{ident}", response_model=ProvInsuranceAttestationOut)
def update_insurance_attestation(
    ident: int,
    payload: ProvInsuranceAttestationUpdate,
    db: Session = Depends(get_db),
    user: User = Depends(require_perm("transport.insurance_attestation.modify")),
):
    cid = _company_id(user)
    obj = _get_or_404(db, ProvInsuranceAttestation, ident, "Attestations d' assurance")
    if obj.company_id != cid:
        raise HTTPException(403, "Acces refuse.")
    _apply(payload.model_dump(exclude_unset=True), obj)
    db.commit()
    db.refresh(obj)
    return obj


@router.delete("/prov-insurance-attestations/{ident}", response_model=ProvInsuranceAttestationOut)
def delete_insurance_attestation(
    ident: int,
    db: Session = Depends(get_db),
    user: User = Depends(require_perm("transport.insurance_attestation.modify")),
):
    cid = _company_id(user)
    obj = _get_or_404(db, ProvInsuranceAttestation, ident, "Attestations d' assurance")
    if obj.company_id != cid:
        raise HTTPException(403, "Acces refuse.")
    obj.is_active = False
    db.commit()
    db.refresh(obj)
    return obj


# ─── Contrats de prestation ─────────────────────────────────────────────────

@router.get("/prov-service-contracts", response_model=List[ProvServiceContractOut])
def list_service_contract(statut: Optional[str] = None, db: Session = Depends(get_db),
    user: User = Depends(require_perm("transport.service_contract.read")),
):
    cid = _company_id(user)
    return _scoped_list(db, ProvServiceContract, cid, {"statut": statut})


@router.post("/prov-service-contracts", response_model=ProvServiceContractOut, status_code=201)
def create_service_contract(
    payload: ProvServiceContractCreate,
    db: Session = Depends(get_db),
    user: User = Depends(require_perm("transport.service_contract.create")),
):
    cid = _company_id(user)
    data = payload.model_dump(exclude_unset=True)
    _check_unique(db, ProvServiceContract, "reference", data.get("reference"), "reference", cid)
    obj = ProvServiceContract(company_id=cid)
    _apply(data, obj)
    db.add(obj)
    db.commit()
    db.refresh(obj)
    return obj


@router.put("/prov-service-contracts/{ident}", response_model=ProvServiceContractOut)
def update_service_contract(
    ident: int,
    payload: ProvServiceContractUpdate,
    db: Session = Depends(get_db),
    user: User = Depends(require_perm("transport.service_contract.modify")),
):
    cid = _company_id(user)
    obj = _get_or_404(db, ProvServiceContract, ident, "Contrats de prestation")
    if obj.company_id != cid:
        raise HTTPException(403, "Acces refuse.")
    _apply(payload.model_dump(exclude_unset=True), obj)
    db.commit()
    db.refresh(obj)
    return obj


@router.delete("/prov-service-contracts/{ident}", response_model=ProvServiceContractOut)
def delete_service_contract(
    ident: int,
    db: Session = Depends(get_db),
    user: User = Depends(require_perm("transport.service_contract.modify")),
):
    cid = _company_id(user)
    obj = _get_or_404(db, ProvServiceContract, ident, "Contrats de prestation")
    if obj.company_id != cid:
        raise HTTPException(403, "Acces refuse.")
    obj.is_active = False
    db.commit()
    db.refresh(obj)
    return obj


# ─── Evaluations de prestataires ─────────────────────────────────────────────────

@router.get("/prov-provider-evaluations", response_model=List[ProvEvaluationOut])
def list_provider_evaluation(statut: Optional[str] = None, db: Session = Depends(get_db),
    user: User = Depends(require_perm("transport.provider_evaluation.read")),
):
    cid = _company_id(user)
    return _scoped_list(db, ProvEvaluation, cid, {"statut": statut})


@router.post("/prov-provider-evaluations", response_model=ProvEvaluationOut, status_code=201)
def create_provider_evaluation(
    payload: ProvEvaluationCreate,
    db: Session = Depends(get_db),
    user: User = Depends(require_perm("transport.provider_evaluation.create")),
):
    cid = _company_id(user)
    data = payload.model_dump(exclude_unset=True)
    _check_unique(db, ProvEvaluation, "reference", data.get("reference"), "reference", cid)
    obj = ProvEvaluation(company_id=cid)
    _apply(data, obj)
    db.add(obj)
    db.commit()
    db.refresh(obj)
    return obj


@router.put("/prov-provider-evaluations/{ident}", response_model=ProvEvaluationOut)
def update_provider_evaluation(
    ident: int,
    payload: ProvEvaluationUpdate,
    db: Session = Depends(get_db),
    user: User = Depends(require_perm("transport.provider_evaluation.modify")),
):
    cid = _company_id(user)
    obj = _get_or_404(db, ProvEvaluation, ident, "Evaluations de prestataires")
    if obj.company_id != cid:
        raise HTTPException(403, "Acces refuse.")
    _apply(payload.model_dump(exclude_unset=True), obj)
    db.commit()
    db.refresh(obj)
    return obj


@router.delete("/prov-provider-evaluations/{ident}", response_model=ProvEvaluationOut)
def delete_provider_evaluation(
    ident: int,
    db: Session = Depends(get_db),
    user: User = Depends(require_perm("transport.provider_evaluation.modify")),
):
    cid = _company_id(user)
    obj = _get_or_404(db, ProvEvaluation, ident, "Evaluations de prestataires")
    if obj.company_id != cid:
        raise HTTPException(403, "Acces refuse.")
    obj.is_active = False
    db.commit()
    db.refresh(obj)
    return obj


# ─── Incidents prestataires ─────────────────────────────────────────────────

@router.get("/prov-provider-incidents", response_model=List[ProvIncidentOut])
def list_provider_incident(statut: Optional[str] = None, db: Session = Depends(get_db),
    user: User = Depends(require_perm("transport.provider_incident.read")),
):
    cid = _company_id(user)
    return _scoped_list(db, ProvIncident, cid, {"statut": statut})


@router.post("/prov-provider-incidents", response_model=ProvIncidentOut, status_code=201)
def create_provider_incident(
    payload: ProvIncidentCreate,
    db: Session = Depends(get_db),
    user: User = Depends(require_perm("transport.provider_incident.create")),
):
    cid = _company_id(user)
    data = payload.model_dump(exclude_unset=True)
    _check_unique(db, ProvIncident, "reference", data.get("reference"), "reference", cid)
    obj = ProvIncident(company_id=cid)
    _apply(data, obj)
    db.add(obj)
    db.commit()
    db.refresh(obj)
    return obj


@router.put("/prov-provider-incidents/{ident}", response_model=ProvIncidentOut)
def update_provider_incident(
    ident: int,
    payload: ProvIncidentUpdate,
    db: Session = Depends(get_db),
    user: User = Depends(require_perm("transport.provider_incident.modify")),
):
    cid = _company_id(user)
    obj = _get_or_404(db, ProvIncident, ident, "Incidents prestataires")
    if obj.company_id != cid:
        raise HTTPException(403, "Acces refuse.")
    _apply(payload.model_dump(exclude_unset=True), obj)
    db.commit()
    db.refresh(obj)
    return obj


@router.delete("/prov-provider-incidents/{ident}", response_model=ProvIncidentOut)
def delete_provider_incident(
    ident: int,
    db: Session = Depends(get_db),
    user: User = Depends(require_perm("transport.provider_incident.modify")),
):
    cid = _company_id(user)
    obj = _get_or_404(db, ProvIncident, ident, "Incidents prestataires")
    if obj.company_id != cid:
        raise HTTPException(403, "Acces refuse.")
    obj.is_active = False
    db.commit()
    db.refresh(obj)
    return obj


# ─── Calendriers de disponibilite ─────────────────────────────────────────────────

@router.get("/prov-availability-calendars", response_model=List[ProvAvailabilityCalendarOut])
def list_availability_calendar(statut: Optional[str] = None, db: Session = Depends(get_db),
    user: User = Depends(require_perm("transport.availability_calendar.read")),
):
    cid = _company_id(user)
    return _scoped_list(db, ProvAvailabilityCalendar, cid, {"statut": statut})


@router.post("/prov-availability-calendars", response_model=ProvAvailabilityCalendarOut, status_code=201)
def create_availability_calendar(
    payload: ProvAvailabilityCalendarCreate,
    db: Session = Depends(get_db),
    user: User = Depends(require_perm("transport.availability_calendar.create")),
):
    cid = _company_id(user)
    data = payload.model_dump(exclude_unset=True)
    _check_unique(db, ProvAvailabilityCalendar, "reference", data.get("reference"), "reference", cid)
    obj = ProvAvailabilityCalendar(company_id=cid)
    _apply(data, obj)
    db.add(obj)
    db.commit()
    db.refresh(obj)
    return obj


@router.put("/prov-availability-calendars/{ident}", response_model=ProvAvailabilityCalendarOut)
def update_availability_calendar(
    ident: int,
    payload: ProvAvailabilityCalendarUpdate,
    db: Session = Depends(get_db),
    user: User = Depends(require_perm("transport.availability_calendar.modify")),
):
    cid = _company_id(user)
    obj = _get_or_404(db, ProvAvailabilityCalendar, ident, "Calendriers de disponibilite")
    if obj.company_id != cid:
        raise HTTPException(403, "Acces refuse.")
    _apply(payload.model_dump(exclude_unset=True), obj)
    db.commit()
    db.refresh(obj)
    return obj


@router.delete("/prov-availability-calendars/{ident}", response_model=ProvAvailabilityCalendarOut)
def delete_availability_calendar(
    ident: int,
    db: Session = Depends(get_db),
    user: User = Depends(require_perm("transport.availability_calendar.modify")),
):
    cid = _company_id(user)
    obj = _get_or_404(db, ProvAvailabilityCalendar, ident, "Calendriers de disponibilite")
    if obj.company_id != cid:
        raise HTTPException(403, "Acces refuse.")
    obj.is_active = False
    db.commit()
    db.refresh(obj)
    return obj


# ─── Grilles tarifaires prestataires ─────────────────────────────────────────────────

@router.get("/prov-price-lists", response_model=List[ProvPriceListOut])
def list_price_list(statut: Optional[str] = None, db: Session = Depends(get_db),
    user: User = Depends(require_perm("transport.price_list.read")),
):
    cid = _company_id(user)
    return _scoped_list(db, ProvPriceList, cid, {"statut": statut})


@router.post("/prov-price-lists", response_model=ProvPriceListOut, status_code=201)
def create_price_list(
    payload: ProvPriceListCreate,
    db: Session = Depends(get_db),
    user: User = Depends(require_perm("transport.price_list.create")),
):
    cid = _company_id(user)
    data = payload.model_dump(exclude_unset=True)
    _check_unique(db, ProvPriceList, "reference", data.get("reference"), "reference", cid)
    obj = ProvPriceList(company_id=cid)
    _apply(data, obj)
    db.add(obj)
    db.commit()
    db.refresh(obj)
    return obj


@router.put("/prov-price-lists/{ident}", response_model=ProvPriceListOut)
def update_price_list(
    ident: int,
    payload: ProvPriceListUpdate,
    db: Session = Depends(get_db),
    user: User = Depends(require_perm("transport.price_list.modify")),
):
    cid = _company_id(user)
    obj = _get_or_404(db, ProvPriceList, ident, "Grilles tarifaires prestataires")
    if obj.company_id != cid:
        raise HTTPException(403, "Acces refuse.")
    _apply(payload.model_dump(exclude_unset=True), obj)
    db.commit()
    db.refresh(obj)
    return obj


@router.delete("/prov-price-lists/{ident}", response_model=ProvPriceListOut)
def delete_price_list(
    ident: int,
    db: Session = Depends(get_db),
    user: User = Depends(require_perm("transport.price_list.modify")),
):
    cid = _company_id(user)
    obj = _get_or_404(db, ProvPriceList, ident, "Grilles tarifaires prestataires")
    if obj.company_id != cid:
        raise HTTPException(403, "Acces refuse.")
    obj.is_active = False
    db.commit()
    db.refresh(obj)
    return obj


# ─── Contacts prestataires ─────────────────────────────────────────────────

@router.get("/prov-provider-contacts", response_model=List[ProvContactOut])
def list_provider_contact(statut: Optional[str] = None, db: Session = Depends(get_db),
    user: User = Depends(require_perm("transport.provider_contact.read")),
):
    cid = _company_id(user)
    return _scoped_list(db, ProvContact, cid, {"statut": statut})


@router.post("/prov-provider-contacts", response_model=ProvContactOut, status_code=201)
def create_provider_contact(
    payload: ProvContactCreate,
    db: Session = Depends(get_db),
    user: User = Depends(require_perm("transport.provider_contact.create")),
):
    cid = _company_id(user)
    data = payload.model_dump(exclude_unset=True)
    _check_unique(db, ProvContact, "reference", data.get("reference"), "reference", cid)
    obj = ProvContact(company_id=cid)
    _apply(data, obj)
    db.add(obj)
    db.commit()
    db.refresh(obj)
    return obj


@router.put("/prov-provider-contacts/{ident}", response_model=ProvContactOut)
def update_provider_contact(
    ident: int,
    payload: ProvContactUpdate,
    db: Session = Depends(get_db),
    user: User = Depends(require_perm("transport.provider_contact.modify")),
):
    cid = _company_id(user)
    obj = _get_or_404(db, ProvContact, ident, "Contacts prestataires")
    if obj.company_id != cid:
        raise HTTPException(403, "Acces refuse.")
    _apply(payload.model_dump(exclude_unset=True), obj)
    db.commit()
    db.refresh(obj)
    return obj


@router.delete("/prov-provider-contacts/{ident}", response_model=ProvContactOut)
def delete_provider_contact(
    ident: int,
    db: Session = Depends(get_db),
    user: User = Depends(require_perm("transport.provider_contact.modify")),
):
    cid = _company_id(user)
    obj = _get_or_404(db, ProvContact, ident, "Contacts prestataires")
    if obj.company_id != cid:
        raise HTTPException(403, "Acces refuse.")
    obj.is_active = False
    db.commit()
    db.refresh(obj)
    return obj


# ─── Onboarding prestataires ─────────────────────────────────────────────────

@router.get("/prov-provider-onboarding", response_model=List[ProvOnboardingOut])
def list_provider_onboarding(statut: Optional[str] = None, db: Session = Depends(get_db),
    user: User = Depends(require_perm("transport.provider_onboarding.read")),
):
    cid = _company_id(user)
    return _scoped_list(db, ProvOnboarding, cid, {"statut": statut})


@router.post("/prov-provider-onboarding", response_model=ProvOnboardingOut, status_code=201)
def create_provider_onboarding(
    payload: ProvOnboardingCreate,
    db: Session = Depends(get_db),
    user: User = Depends(require_perm("transport.provider_onboarding.create")),
):
    cid = _company_id(user)
    data = payload.model_dump(exclude_unset=True)
    _check_unique(db, ProvOnboarding, "reference", data.get("reference"), "reference", cid)
    obj = ProvOnboarding(company_id=cid)
    _apply(data, obj)
    db.add(obj)
    db.commit()
    db.refresh(obj)
    return obj


@router.put("/prov-provider-onboarding/{ident}", response_model=ProvOnboardingOut)
def update_provider_onboarding(
    ident: int,
    payload: ProvOnboardingUpdate,
    db: Session = Depends(get_db),
    user: User = Depends(require_perm("transport.provider_onboarding.modify")),
):
    cid = _company_id(user)
    obj = _get_or_404(db, ProvOnboarding, ident, "Onboarding prestataires")
    if obj.company_id != cid:
        raise HTTPException(403, "Acces refuse.")
    _apply(payload.model_dump(exclude_unset=True), obj)
    db.commit()
    db.refresh(obj)
    return obj


@router.delete("/prov-provider-onboarding/{ident}", response_model=ProvOnboardingOut)
def delete_provider_onboarding(
    ident: int,
    db: Session = Depends(get_db),
    user: User = Depends(require_perm("transport.provider_onboarding.modify")),
):
    cid = _company_id(user)
    obj = _get_or_404(db, ProvOnboarding, ident, "Onboarding prestataires")
    if obj.company_id != cid:
        raise HTTPException(403, "Acces refuse.")
    obj.is_active = False
    db.commit()
    db.refresh(obj)
    return obj


# ─── Avis sur prestataires ─────────────────────────────────────────────────

@router.get("/prov-provider-reviews", response_model=List[ProvReviewOut])
def list_provider_review(statut: Optional[str] = None, db: Session = Depends(get_db),
    user: User = Depends(require_perm("transport.provider_review.read")),
):
    cid = _company_id(user)
    return _scoped_list(db, ProvReview, cid, {"statut": statut})


@router.post("/prov-provider-reviews", response_model=ProvReviewOut, status_code=201)
def create_provider_review(
    payload: ProvReviewCreate,
    db: Session = Depends(get_db),
    user: User = Depends(require_perm("transport.provider_review.create")),
):
    cid = _company_id(user)
    data = payload.model_dump(exclude_unset=True)
    _check_unique(db, ProvReview, "reference", data.get("reference"), "reference", cid)
    obj = ProvReview(company_id=cid)
    _apply(data, obj)
    db.add(obj)
    db.commit()
    db.refresh(obj)
    return obj


@router.put("/prov-provider-reviews/{ident}", response_model=ProvReviewOut)
def update_provider_review(
    ident: int,
    payload: ProvReviewUpdate,
    db: Session = Depends(get_db),
    user: User = Depends(require_perm("transport.provider_review.modify")),
):
    cid = _company_id(user)
    obj = _get_or_404(db, ProvReview, ident, "Avis sur prestataires")
    if obj.company_id != cid:
        raise HTTPException(403, "Acces refuse.")
    _apply(payload.model_dump(exclude_unset=True), obj)
    db.commit()
    db.refresh(obj)
    return obj


@router.delete("/prov-provider-reviews/{ident}", response_model=ProvReviewOut)
def delete_provider_review(
    ident: int,
    db: Session = Depends(get_db),
    user: User = Depends(require_perm("transport.provider_review.modify")),
):
    cid = _company_id(user)
    obj = _get_or_404(db, ProvReview, ident, "Avis sur prestataires")
    if obj.company_id != cid:
        raise HTTPException(403, "Acces refuse.")
    obj.is_active = False
    db.commit()
    db.refresh(obj)
    return obj


# ─── Demandes de devis ─────────────────────────────────────────────────

@router.get("/prov-rfq-requests", response_model=List[ProvRfqRequestOut])
def list_rfq_request(statut: Optional[str] = None, db: Session = Depends(get_db),
    user: User = Depends(require_perm("transport.rfq_request.read")),
):
    cid = _company_id(user)
    return _scoped_list(db, ProvRfqRequest, cid, {"statut": statut})


@router.post("/prov-rfq-requests", response_model=ProvRfqRequestOut, status_code=201)
def create_rfq_request(
    payload: ProvRfqRequestCreate,
    db: Session = Depends(get_db),
    user: User = Depends(require_perm("transport.rfq_request.create")),
):
    cid = _company_id(user)
    data = payload.model_dump(exclude_unset=True)
    _check_unique(db, ProvRfqRequest, "reference", data.get("reference"), "reference", cid)
    obj = ProvRfqRequest(company_id=cid)
    _apply(data, obj)
    db.add(obj)
    db.commit()
    db.refresh(obj)
    return obj


@router.put("/prov-rfq-requests/{ident}", response_model=ProvRfqRequestOut)
def update_rfq_request(
    ident: int,
    payload: ProvRfqRequestUpdate,
    db: Session = Depends(get_db),
    user: User = Depends(require_perm("transport.rfq_request.modify")),
):
    cid = _company_id(user)
    obj = _get_or_404(db, ProvRfqRequest, ident, "Demandes de devis")
    if obj.company_id != cid:
        raise HTTPException(403, "Acces refuse.")
    _apply(payload.model_dump(exclude_unset=True), obj)
    db.commit()
    db.refresh(obj)
    return obj


@router.delete("/prov-rfq-requests/{ident}", response_model=ProvRfqRequestOut)
def delete_rfq_request(
    ident: int,
    db: Session = Depends(get_db),
    user: User = Depends(require_perm("transport.rfq_request.modify")),
):
    cid = _company_id(user)
    obj = _get_or_404(db, ProvRfqRequest, ident, "Demandes de devis")
    if obj.company_id != cid:
        raise HTTPException(403, "Acces refuse.")
    obj.is_active = False
    db.commit()
    db.refresh(obj)
    return obj


# ─── Interventions prestataires ─────────────────────────────────────────────────

@router.get("/prov-provider-interventions", response_model=List[ProvInterventionOut])
def list_provider_intervention(statut: Optional[str] = None, db: Session = Depends(get_db),
    user: User = Depends(require_perm("transport.provider_intervention.read")),
):
    cid = _company_id(user)
    return _scoped_list(db, ProvIntervention, cid, {"statut": statut})


@router.post("/prov-provider-interventions", response_model=ProvInterventionOut, status_code=201)
def create_provider_intervention(
    payload: ProvInterventionCreate,
    db: Session = Depends(get_db),
    user: User = Depends(require_perm("transport.provider_intervention.create")),
):
    cid = _company_id(user)
    data = payload.model_dump(exclude_unset=True)
    _check_unique(db, ProvIntervention, "reference", data.get("reference"), "reference", cid)
    obj = ProvIntervention(company_id=cid)
    _apply(data, obj)
    db.add(obj)
    db.commit()
    db.refresh(obj)
    return obj


@router.put("/prov-provider-interventions/{ident}", response_model=ProvInterventionOut)
def update_provider_intervention(
    ident: int,
    payload: ProvInterventionUpdate,
    db: Session = Depends(get_db),
    user: User = Depends(require_perm("transport.provider_intervention.modify")),
):
    cid = _company_id(user)
    obj = _get_or_404(db, ProvIntervention, ident, "Interventions prestataires")
    if obj.company_id != cid:
        raise HTTPException(403, "Acces refuse.")
    _apply(payload.model_dump(exclude_unset=True), obj)
    db.commit()
    db.refresh(obj)
    return obj


@router.delete("/prov-provider-interventions/{ident}", response_model=ProvInterventionOut)
def delete_provider_intervention(
    ident: int,
    db: Session = Depends(get_db),
    user: User = Depends(require_perm("transport.provider_intervention.modify")),
):
    cid = _company_id(user)
    obj = _get_or_404(db, ProvIntervention, ident, "Interventions prestataires")
    if obj.company_id != cid:
        raise HTTPException(403, "Acces refuse.")
    obj.is_active = False
    db.commit()
    db.refresh(obj)
    return obj


# ─── Documents de conformite ─────────────────────────────────────────────────

@router.get("/prov-compliance-documents", response_model=List[ProvComplianceDocOut])
def list_compliance_document(statut: Optional[str] = None, db: Session = Depends(get_db),
    user: User = Depends(require_perm("transport.compliance_document.read")),
):
    cid = _company_id(user)
    return _scoped_list(db, ProvComplianceDoc, cid, {"statut": statut})


@router.post("/prov-compliance-documents", response_model=ProvComplianceDocOut, status_code=201)
def create_compliance_document(
    payload: ProvComplianceDocCreate,
    db: Session = Depends(get_db),
    user: User = Depends(require_perm("transport.compliance_document.create")),
):
    cid = _company_id(user)
    data = payload.model_dump(exclude_unset=True)
    _check_unique(db, ProvComplianceDoc, "reference", data.get("reference"), "reference", cid)
    obj = ProvComplianceDoc(company_id=cid)
    _apply(data, obj)
    db.add(obj)
    db.commit()
    db.refresh(obj)
    return obj


@router.put("/prov-compliance-documents/{ident}", response_model=ProvComplianceDocOut)
def update_compliance_document(
    ident: int,
    payload: ProvComplianceDocUpdate,
    db: Session = Depends(get_db),
    user: User = Depends(require_perm("transport.compliance_document.modify")),
):
    cid = _company_id(user)
    obj = _get_or_404(db, ProvComplianceDoc, ident, "Documents de conformite")
    if obj.company_id != cid:
        raise HTTPException(403, "Acces refuse.")
    _apply(payload.model_dump(exclude_unset=True), obj)
    db.commit()
    db.refresh(obj)
    return obj


@router.delete("/prov-compliance-documents/{ident}", response_model=ProvComplianceDocOut)
def delete_compliance_document(
    ident: int,
    db: Session = Depends(get_db),
    user: User = Depends(require_perm("transport.compliance_document.modify")),
):
    cid = _company_id(user)
    obj = _get_or_404(db, ProvComplianceDoc, ident, "Documents de conformite")
    if obj.company_id != cid:
        raise HTTPException(403, "Acces refuse.")
    obj.is_active = False
    db.commit()
    db.refresh(obj)
    return obj


# ─── Coordonnees bancaires prestataires ─────────────────────────────────────────────────

@router.get("/prov-provider-bank-details", response_model=List[ProvBankDetailOut])
def list_provider_bank_detail(statut: Optional[str] = None, db: Session = Depends(get_db),
    user: User = Depends(require_perm("transport.provider_bank_detail.read")),
):
    cid = _company_id(user)
    return _scoped_list(db, ProvBankDetail, cid, {"statut": statut})


@router.post("/prov-provider-bank-details", response_model=ProvBankDetailOut, status_code=201)
def create_provider_bank_detail(
    payload: ProvBankDetailCreate,
    db: Session = Depends(get_db),
    user: User = Depends(require_perm("transport.provider_bank_detail.create")),
):
    cid = _company_id(user)
    data = payload.model_dump(exclude_unset=True)
    _check_unique(db, ProvBankDetail, "reference", data.get("reference"), "reference", cid)
    obj = ProvBankDetail(company_id=cid)
    _apply(data, obj)
    db.add(obj)
    db.commit()
    db.refresh(obj)
    return obj


@router.put("/prov-provider-bank-details/{ident}", response_model=ProvBankDetailOut)
def update_provider_bank_detail(
    ident: int,
    payload: ProvBankDetailUpdate,
    db: Session = Depends(get_db),
    user: User = Depends(require_perm("transport.provider_bank_detail.modify")),
):
    cid = _company_id(user)
    obj = _get_or_404(db, ProvBankDetail, ident, "Coordonnees bancaires prestataires")
    if obj.company_id != cid:
        raise HTTPException(403, "Acces refuse.")
    _apply(payload.model_dump(exclude_unset=True), obj)
    db.commit()
    db.refresh(obj)
    return obj


@router.delete("/prov-provider-bank-details/{ident}", response_model=ProvBankDetailOut)
def delete_provider_bank_detail(
    ident: int,
    db: Session = Depends(get_db),
    user: User = Depends(require_perm("transport.provider_bank_detail.modify")),
):
    cid = _company_id(user)
    obj = _get_or_404(db, ProvBankDetail, ident, "Coordonnees bancaires prestataires")
    if obj.company_id != cid:
        raise HTTPException(403, "Acces refuse.")
    obj.is_active = False
    db.commit()
    db.refresh(obj)
    return obj


# ─── Exclusions de prestataires ─────────────────────────────────────────────────

@router.get("/prov-provider-blacklist", response_model=List[ProvBlacklistOut])
def list_provider_blacklist(statut: Optional[str] = None, db: Session = Depends(get_db),
    user: User = Depends(require_perm("transport.provider_blacklist.read")),
):
    cid = _company_id(user)
    return _scoped_list(db, ProvBlacklist, cid, {"statut": statut})


@router.post("/prov-provider-blacklist", response_model=ProvBlacklistOut, status_code=201)
def create_provider_blacklist(
    payload: ProvBlacklistCreate,
    db: Session = Depends(get_db),
    user: User = Depends(require_perm("transport.provider_blacklist.create")),
):
    cid = _company_id(user)
    data = payload.model_dump(exclude_unset=True)
    _check_unique(db, ProvBlacklist, "reference", data.get("reference"), "reference", cid)
    obj = ProvBlacklist(company_id=cid)
    _apply(data, obj)
    db.add(obj)
    db.commit()
    db.refresh(obj)
    return obj


@router.put("/prov-provider-blacklist/{ident}", response_model=ProvBlacklistOut)
def update_provider_blacklist(
    ident: int,
    payload: ProvBlacklistUpdate,
    db: Session = Depends(get_db),
    user: User = Depends(require_perm("transport.provider_blacklist.modify")),
):
    cid = _company_id(user)
    obj = _get_or_404(db, ProvBlacklist, ident, "Exclusions de prestataires")
    if obj.company_id != cid:
        raise HTTPException(403, "Acces refuse.")
    _apply(payload.model_dump(exclude_unset=True), obj)
    db.commit()
    db.refresh(obj)
    return obj


@router.delete("/prov-provider-blacklist/{ident}", response_model=ProvBlacklistOut)
def delete_provider_blacklist(
    ident: int,
    db: Session = Depends(get_db),
    user: User = Depends(require_perm("transport.provider_blacklist.modify")),
):
    cid = _company_id(user)
    obj = _get_or_404(db, ProvBlacklist, ident, "Exclusions de prestataires")
    if obj.company_id != cid:
        raise HTTPException(403, "Acces refuse.")
    obj.is_active = False
    db.commit()
    db.refresh(obj)
    return obj

