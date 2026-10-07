"""Routeur CRUD genere pour client-b2b (expansion)."""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import Optional, List

from app.core.database import get_db
from app.core.permissions import require_perm
from app.models.user import User
from app.models.b2b_deep import (
    ClientOnboarding,
    SlaContract,
    B2bContract,
    SatisfactionSurvey,
    ClientCreditLimit,
    B2bDocument,
    ServiceRequest,
    PricingAgreement,
    ShipmentBooking,
    ClientClaim,
    AccountReport,
)
from app.schemas.b2b_deep import (
    ClientOnboardingCreate, ClientOnboardingUpdate, ClientOnboardingOut,
    SlaContractCreate, SlaContractUpdate, SlaContractOut,
    B2bContractCreate, B2bContractUpdate, B2bContractOut,
    SatisfactionSurveyCreate, SatisfactionSurveyUpdate, SatisfactionSurveyOut,
    ClientCreditLimitCreate, ClientCreditLimitUpdate, ClientCreditLimitOut,
    B2bDocumentCreate, B2bDocumentUpdate, B2bDocumentOut,
    ServiceRequestCreate, ServiceRequestUpdate, ServiceRequestOut,
    PricingAgreementCreate, PricingAgreementUpdate, PricingAgreementOut,
    ShipmentBookingCreate, ShipmentBookingUpdate, ShipmentBookingOut,
    ClientClaimCreate, ClientClaimUpdate, ClientClaimOut,
    AccountReportCreate, AccountReportUpdate, AccountReportOut,
)

router = APIRouter(tags=["client-b2b (expansion)"])


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

@router.get("/nomenclatures", summary="Vocabulaire metier client-b2b")
def nomenclatures(user: User = Depends(require_perm("b2b.nomenclature.read"))):
    from app.models import b2b_deep as _md
    import enum as _pyenum
    out = {}
    for name in dir(_md):
        obj = getattr(_md, name)
        if isinstance(obj, type) and issubclass(obj, _pyenum.Enum) and obj is not _pyenum.Enum:
            out[name.lower()] = [{"code": m.name, "valeur": m.value} for m in obj]
    return out


# ─── Admission nouveau client ─────────────────────────────────────────────────

@router.get("/client-onboardings", response_model=List[ClientOnboardingOut])
def list_client_onboarding(statut: Optional[str] = None, db: Session = Depends(get_db),
    user: User = Depends(require_perm("b2b.client_onboarding.read")),
):
    cid = _company_id(user)
    return _scoped_list(db, ClientOnboarding, cid, {"statut": statut})


@router.post("/client-onboardings", response_model=ClientOnboardingOut, status_code=201)
def create_client_onboarding(
    payload: ClientOnboardingCreate,
    db: Session = Depends(get_db),
    user: User = Depends(require_perm("b2b.client_onboarding.create")),
):
    cid = _company_id(user)
    data = payload.model_dump(exclude_unset=True)
    _check_unique(db, ClientOnboarding, "reference", data.get("reference"), "reference", cid)
    obj = ClientOnboarding(company_id=cid)
    _apply(data, obj)
    db.add(obj)
    db.commit()
    db.refresh(obj)
    return obj


@router.put("/client-onboardings/{ident}", response_model=ClientOnboardingOut)
def update_client_onboarding(
    ident: int,
    payload: ClientOnboardingUpdate,
    db: Session = Depends(get_db),
    user: User = Depends(require_perm("b2b.client_onboarding.modify")),
):
    cid = _company_id(user)
    obj = _get_or_404(db, ClientOnboarding, ident, "Admission nouveau client")
    if obj.company_id != cid:
        raise HTTPException(403, "Acces refuse.")
    _apply(payload.model_dump(exclude_unset=True), obj)
    db.commit()
    db.refresh(obj)
    return obj


@router.delete("/client-onboardings/{ident}", response_model=ClientOnboardingOut)
def delete_client_onboarding(
    ident: int,
    db: Session = Depends(get_db),
    user: User = Depends(require_perm("b2b.client_onboarding.modify")),
):
    cid = _company_id(user)
    obj = _get_or_404(db, ClientOnboarding, ident, "Admission nouveau client")
    if obj.company_id != cid:
        raise HTTPException(403, "Acces refuse.")
    obj.is_active = False
    db.commit()
    db.refresh(obj)
    return obj


# ─── Niveau de service / penalisations ─────────────────────────────────────────────────

@router.get("/sla-contracts", response_model=List[SlaContractOut])
def list_sla_management(statut: Optional[str] = None, db: Session = Depends(get_db),
    user: User = Depends(require_perm("b2b.sla_management.read")),
):
    cid = _company_id(user)
    return _scoped_list(db, SlaContract, cid, {"statut": statut})


@router.post("/sla-contracts", response_model=SlaContractOut, status_code=201)
def create_sla_management(
    payload: SlaContractCreate,
    db: Session = Depends(get_db),
    user: User = Depends(require_perm("b2b.sla_management.create")),
):
    cid = _company_id(user)
    data = payload.model_dump(exclude_unset=True)
    _check_unique(db, SlaContract, "reference", data.get("reference"), "reference", cid)
    obj = SlaContract(company_id=cid)
    _apply(data, obj)
    db.add(obj)
    db.commit()
    db.refresh(obj)
    return obj


@router.put("/sla-contracts/{ident}", response_model=SlaContractOut)
def update_sla_management(
    ident: int,
    payload: SlaContractUpdate,
    db: Session = Depends(get_db),
    user: User = Depends(require_perm("b2b.sla_management.modify")),
):
    cid = _company_id(user)
    obj = _get_or_404(db, SlaContract, ident, "Niveau de service / penalisations")
    if obj.company_id != cid:
        raise HTTPException(403, "Acces refuse.")
    _apply(payload.model_dump(exclude_unset=True), obj)
    db.commit()
    db.refresh(obj)
    return obj


@router.delete("/sla-contracts/{ident}", response_model=SlaContractOut)
def delete_sla_management(
    ident: int,
    db: Session = Depends(get_db),
    user: User = Depends(require_perm("b2b.sla_management.modify")),
):
    cid = _company_id(user)
    obj = _get_or_404(db, SlaContract, ident, "Niveau de service / penalisations")
    if obj.company_id != cid:
        raise HTTPException(403, "Acces refuse.")
    obj.is_active = False
    db.commit()
    db.refresh(obj)
    return obj


# ─── Contrats cadres / avenants ─────────────────────────────────────────────────

@router.get("/b2b-contracts", response_model=List[B2bContractOut])
def list_contract_tracking(statut: Optional[str] = None, db: Session = Depends(get_db),
    user: User = Depends(require_perm("b2b.contract_tracking.read")),
):
    cid = _company_id(user)
    return _scoped_list(db, B2bContract, cid, {"statut": statut})


@router.post("/b2b-contracts", response_model=B2bContractOut, status_code=201)
def create_contract_tracking(
    payload: B2bContractCreate,
    db: Session = Depends(get_db),
    user: User = Depends(require_perm("b2b.contract_tracking.create")),
):
    cid = _company_id(user)
    data = payload.model_dump(exclude_unset=True)
    _check_unique(db, B2bContract, "numero_contrat", data.get("numero_contrat"), "numero_contrat", cid)
    obj = B2bContract(company_id=cid)
    _apply(data, obj)
    db.add(obj)
    db.commit()
    db.refresh(obj)
    return obj


@router.put("/b2b-contracts/{ident}", response_model=B2bContractOut)
def update_contract_tracking(
    ident: int,
    payload: B2bContractUpdate,
    db: Session = Depends(get_db),
    user: User = Depends(require_perm("b2b.contract_tracking.modify")),
):
    cid = _company_id(user)
    obj = _get_or_404(db, B2bContract, ident, "Contrats cadres / avenants")
    if obj.company_id != cid:
        raise HTTPException(403, "Acces refuse.")
    _apply(payload.model_dump(exclude_unset=True), obj)
    db.commit()
    db.refresh(obj)
    return obj


@router.delete("/b2b-contracts/{ident}", response_model=B2bContractOut)
def delete_contract_tracking(
    ident: int,
    db: Session = Depends(get_db),
    user: User = Depends(require_perm("b2b.contract_tracking.modify")),
):
    cid = _company_id(user)
    obj = _get_or_404(db, B2bContract, ident, "Contrats cadres / avenants")
    if obj.company_id != cid:
        raise HTTPException(403, "Acces refuse.")
    obj.is_active = False
    db.commit()
    db.refresh(obj)
    return obj


# ─── Enquetes satisfaction NPS ─────────────────────────────────────────────────

@router.get("/satisfaction-surveys", response_model=List[SatisfactionSurveyOut])
def list_satisfaction_survey(db: Session = Depends(get_db),
    user: User = Depends(require_perm("b2b.satisfaction_survey.read")),
):
    cid = _company_id(user)
    return _scoped_list(db, SatisfactionSurvey, cid)


@router.post("/satisfaction-surveys", response_model=SatisfactionSurveyOut, status_code=201)
def create_satisfaction_survey(
    payload: SatisfactionSurveyCreate,
    db: Session = Depends(get_db),
    user: User = Depends(require_perm("b2b.satisfaction_survey.create")),
):
    cid = _company_id(user)
    data = payload.model_dump(exclude_unset=True)
    _check_unique(db, SatisfactionSurvey, "reference", data.get("reference"), "reference", cid)
    obj = SatisfactionSurvey(company_id=cid)
    _apply(data, obj)
    db.add(obj)
    db.commit()
    db.refresh(obj)
    return obj


@router.put("/satisfaction-surveys/{ident}", response_model=SatisfactionSurveyOut)
def update_satisfaction_survey(
    ident: int,
    payload: SatisfactionSurveyUpdate,
    db: Session = Depends(get_db),
    user: User = Depends(require_perm("b2b.satisfaction_survey.modify")),
):
    cid = _company_id(user)
    obj = _get_or_404(db, SatisfactionSurvey, ident, "Enquetes satisfaction NPS")
    if obj.company_id != cid:
        raise HTTPException(403, "Acces refuse.")
    _apply(payload.model_dump(exclude_unset=True), obj)
    db.commit()
    db.refresh(obj)
    return obj


@router.delete("/satisfaction-surveys/{ident}", response_model=SatisfactionSurveyOut)
def delete_satisfaction_survey(
    ident: int,
    db: Session = Depends(get_db),
    user: User = Depends(require_perm("b2b.satisfaction_survey.modify")),
):
    cid = _company_id(user)
    obj = _get_or_404(db, SatisfactionSurvey, ident, "Enquetes satisfaction NPS")
    if obj.company_id != cid:
        raise HTTPException(403, "Acces refuse.")
    obj.is_active = False
    db.commit()
    db.refresh(obj)
    return obj


# ─── Plafonds de credit client ─────────────────────────────────────────────────

@router.get("/client-credit-limits", response_model=List[ClientCreditLimitOut])
def list_credit_limit(statut: Optional[str] = None, db: Session = Depends(get_db),
    user: User = Depends(require_perm("b2b.credit_limit.read")),
):
    cid = _company_id(user)
    return _scoped_list(db, ClientCreditLimit, cid, {"statut": statut})


@router.post("/client-credit-limits", response_model=ClientCreditLimitOut, status_code=201)
def create_credit_limit(
    payload: ClientCreditLimitCreate,
    db: Session = Depends(get_db),
    user: User = Depends(require_perm("b2b.credit_limit.create")),
):
    cid = _company_id(user)
    data = payload.model_dump(exclude_unset=True)
    _check_unique(db, ClientCreditLimit, "reference", data.get("reference"), "reference", cid)
    obj = ClientCreditLimit(company_id=cid)
    _apply(data, obj)
    db.add(obj)
    db.commit()
    db.refresh(obj)
    return obj


@router.put("/client-credit-limits/{ident}", response_model=ClientCreditLimitOut)
def update_credit_limit(
    ident: int,
    payload: ClientCreditLimitUpdate,
    db: Session = Depends(get_db),
    user: User = Depends(require_perm("b2b.credit_limit.modify")),
):
    cid = _company_id(user)
    obj = _get_or_404(db, ClientCreditLimit, ident, "Plafonds de credit client")
    if obj.company_id != cid:
        raise HTTPException(403, "Acces refuse.")
    _apply(payload.model_dump(exclude_unset=True), obj)
    db.commit()
    db.refresh(obj)
    return obj


@router.delete("/client-credit-limits/{ident}", response_model=ClientCreditLimitOut)
def delete_credit_limit(
    ident: int,
    db: Session = Depends(get_db),
    user: User = Depends(require_perm("b2b.credit_limit.modify")),
):
    cid = _company_id(user)
    obj = _get_or_404(db, ClientCreditLimit, ident, "Plafonds de credit client")
    if obj.company_id != cid:
        raise HTTPException(403, "Acces refuse.")
    obj.is_active = False
    db.commit()
    db.refresh(obj)
    return obj


# ─── Echange documents contractuels ─────────────────────────────────────────────────

@router.get("/b2b-documents", response_model=List[B2bDocumentOut])
def list_document_exchange(statut: Optional[str] = None, db: Session = Depends(get_db),
    user: User = Depends(require_perm("b2b.document_exchange.read")),
):
    cid = _company_id(user)
    return _scoped_list(db, B2bDocument, cid, {"statut": statut})


@router.post("/b2b-documents", response_model=B2bDocumentOut, status_code=201)
def create_document_exchange(
    payload: B2bDocumentCreate,
    db: Session = Depends(get_db),
    user: User = Depends(require_perm("b2b.document_exchange.create")),
):
    cid = _company_id(user)
    data = payload.model_dump(exclude_unset=True)
    _check_unique(db, B2bDocument, "reference", data.get("reference"), "reference", cid)
    obj = B2bDocument(company_id=cid)
    _apply(data, obj)
    db.add(obj)
    db.commit()
    db.refresh(obj)
    return obj


@router.put("/b2b-documents/{ident}", response_model=B2bDocumentOut)
def update_document_exchange(
    ident: int,
    payload: B2bDocumentUpdate,
    db: Session = Depends(get_db),
    user: User = Depends(require_perm("b2b.document_exchange.modify")),
):
    cid = _company_id(user)
    obj = _get_or_404(db, B2bDocument, ident, "Echange documents contractuels")
    if obj.company_id != cid:
        raise HTTPException(403, "Acces refuse.")
    _apply(payload.model_dump(exclude_unset=True), obj)
    db.commit()
    db.refresh(obj)
    return obj


@router.delete("/b2b-documents/{ident}", response_model=B2bDocumentOut)
def delete_document_exchange(
    ident: int,
    db: Session = Depends(get_db),
    user: User = Depends(require_perm("b2b.document_exchange.modify")),
):
    cid = _company_id(user)
    obj = _get_or_404(db, B2bDocument, ident, "Echange documents contractuels")
    if obj.company_id != cid:
        raise HTTPException(403, "Acces refuse.")
    obj.is_active = False
    db.commit()
    db.refresh(obj)
    return obj


# ─── Demandes de service client ─────────────────────────────────────────────────

@router.get("/service-requests", response_model=List[ServiceRequestOut])
def list_service_request(statut: Optional[str] = None, db: Session = Depends(get_db),
    user: User = Depends(require_perm("b2b.service_request.read")),
):
    cid = _company_id(user)
    return _scoped_list(db, ServiceRequest, cid, {"statut": statut})


@router.post("/service-requests", response_model=ServiceRequestOut, status_code=201)
def create_service_request(
    payload: ServiceRequestCreate,
    db: Session = Depends(get_db),
    user: User = Depends(require_perm("b2b.service_request.create")),
):
    cid = _company_id(user)
    data = payload.model_dump(exclude_unset=True)
    _check_unique(db, ServiceRequest, "reference", data.get("reference"), "reference", cid)
    obj = ServiceRequest(company_id=cid)
    _apply(data, obj)
    db.add(obj)
    db.commit()
    db.refresh(obj)
    return obj


@router.put("/service-requests/{ident}", response_model=ServiceRequestOut)
def update_service_request(
    ident: int,
    payload: ServiceRequestUpdate,
    db: Session = Depends(get_db),
    user: User = Depends(require_perm("b2b.service_request.modify")),
):
    cid = _company_id(user)
    obj = _get_or_404(db, ServiceRequest, ident, "Demandes de service client")
    if obj.company_id != cid:
        raise HTTPException(403, "Acces refuse.")
    _apply(payload.model_dump(exclude_unset=True), obj)
    db.commit()
    db.refresh(obj)
    return obj


@router.delete("/service-requests/{ident}", response_model=ServiceRequestOut)
def delete_service_request(
    ident: int,
    db: Session = Depends(get_db),
    user: User = Depends(require_perm("b2b.service_request.modify")),
):
    cid = _company_id(user)
    obj = _get_or_404(db, ServiceRequest, ident, "Demandes de service client")
    if obj.company_id != cid:
        raise HTTPException(403, "Acces refuse.")
    obj.is_active = False
    db.commit()
    db.refresh(obj)
    return obj


# ─── Accords tarifaires / remises ─────────────────────────────────────────────────

@router.get("/pricing-agreements", response_model=List[PricingAgreementOut])
def list_pricing_agreement(statut: Optional[str] = None, db: Session = Depends(get_db),
    user: User = Depends(require_perm("b2b.pricing_agreement.read")),
):
    cid = _company_id(user)
    return _scoped_list(db, PricingAgreement, cid, {"statut": statut})


@router.post("/pricing-agreements", response_model=PricingAgreementOut, status_code=201)
def create_pricing_agreement(
    payload: PricingAgreementCreate,
    db: Session = Depends(get_db),
    user: User = Depends(require_perm("b2b.pricing_agreement.create")),
):
    cid = _company_id(user)
    data = payload.model_dump(exclude_unset=True)
    _check_unique(db, PricingAgreement, "reference", data.get("reference"), "reference", cid)
    obj = PricingAgreement(company_id=cid)
    _apply(data, obj)
    db.add(obj)
    db.commit()
    db.refresh(obj)
    return obj


@router.put("/pricing-agreements/{ident}", response_model=PricingAgreementOut)
def update_pricing_agreement(
    ident: int,
    payload: PricingAgreementUpdate,
    db: Session = Depends(get_db),
    user: User = Depends(require_perm("b2b.pricing_agreement.modify")),
):
    cid = _company_id(user)
    obj = _get_or_404(db, PricingAgreement, ident, "Accords tarifaires / remises")
    if obj.company_id != cid:
        raise HTTPException(403, "Acces refuse.")
    _apply(payload.model_dump(exclude_unset=True), obj)
    db.commit()
    db.refresh(obj)
    return obj


@router.delete("/pricing-agreements/{ident}", response_model=PricingAgreementOut)
def delete_pricing_agreement(
    ident: int,
    db: Session = Depends(get_db),
    user: User = Depends(require_perm("b2b.pricing_agreement.modify")),
):
    cid = _company_id(user)
    obj = _get_or_404(db, PricingAgreement, ident, "Accords tarifaires / remises")
    if obj.company_id != cid:
        raise HTTPException(403, "Acces refuse.")
    obj.is_active = False
    db.commit()
    db.refresh(obj)
    return obj


# ─── Reservation expedition client ─────────────────────────────────────────────────

@router.get("/shipment-bookings", response_model=List[ShipmentBookingOut])
def list_shipment_booking(statut: Optional[str] = None, db: Session = Depends(get_db),
    user: User = Depends(require_perm("b2b.shipment_booking.read")),
):
    cid = _company_id(user)
    return _scoped_list(db, ShipmentBooking, cid, {"statut": statut})


@router.post("/shipment-bookings", response_model=ShipmentBookingOut, status_code=201)
def create_shipment_booking(
    payload: ShipmentBookingCreate,
    db: Session = Depends(get_db),
    user: User = Depends(require_perm("b2b.shipment_booking.create")),
):
    cid = _company_id(user)
    data = payload.model_dump(exclude_unset=True)
    _check_unique(db, ShipmentBooking, "reference", data.get("reference"), "reference", cid)
    obj = ShipmentBooking(company_id=cid)
    _apply(data, obj)
    db.add(obj)
    db.commit()
    db.refresh(obj)
    return obj


@router.put("/shipment-bookings/{ident}", response_model=ShipmentBookingOut)
def update_shipment_booking(
    ident: int,
    payload: ShipmentBookingUpdate,
    db: Session = Depends(get_db),
    user: User = Depends(require_perm("b2b.shipment_booking.modify")),
):
    cid = _company_id(user)
    obj = _get_or_404(db, ShipmentBooking, ident, "Reservation expedition client")
    if obj.company_id != cid:
        raise HTTPException(403, "Acces refuse.")
    _apply(payload.model_dump(exclude_unset=True), obj)
    db.commit()
    db.refresh(obj)
    return obj


@router.delete("/shipment-bookings/{ident}", response_model=ShipmentBookingOut)
def delete_shipment_booking(
    ident: int,
    db: Session = Depends(get_db),
    user: User = Depends(require_perm("b2b.shipment_booking.modify")),
):
    cid = _company_id(user)
    obj = _get_or_404(db, ShipmentBooking, ident, "Reservation expedition client")
    if obj.company_id != cid:
        raise HTTPException(403, "Acces refuse.")
    obj.is_active = False
    db.commit()
    db.refresh(obj)
    return obj


# ─── Reclamation / litige client ─────────────────────────────────────────────────

@router.get("/client-claims", response_model=List[ClientClaimOut])
def list_claim_dispute(statut: Optional[str] = None, db: Session = Depends(get_db),
    user: User = Depends(require_perm("b2b.claim_dispute.read")),
):
    cid = _company_id(user)
    return _scoped_list(db, ClientClaim, cid, {"statut": statut})


@router.post("/client-claims", response_model=ClientClaimOut, status_code=201)
def create_claim_dispute(
    payload: ClientClaimCreate,
    db: Session = Depends(get_db),
    user: User = Depends(require_perm("b2b.claim_dispute.create")),
):
    cid = _company_id(user)
    data = payload.model_dump(exclude_unset=True)
    _check_unique(db, ClientClaim, "reference", data.get("reference"), "reference", cid)
    obj = ClientClaim(company_id=cid)
    _apply(data, obj)
    db.add(obj)
    db.commit()
    db.refresh(obj)
    return obj


@router.put("/client-claims/{ident}", response_model=ClientClaimOut)
def update_claim_dispute(
    ident: int,
    payload: ClientClaimUpdate,
    db: Session = Depends(get_db),
    user: User = Depends(require_perm("b2b.claim_dispute.modify")),
):
    cid = _company_id(user)
    obj = _get_or_404(db, ClientClaim, ident, "Reclamation / litige client")
    if obj.company_id != cid:
        raise HTTPException(403, "Acces refuse.")
    _apply(payload.model_dump(exclude_unset=True), obj)
    db.commit()
    db.refresh(obj)
    return obj


@router.delete("/client-claims/{ident}", response_model=ClientClaimOut)
def delete_claim_dispute(
    ident: int,
    db: Session = Depends(get_db),
    user: User = Depends(require_perm("b2b.claim_dispute.modify")),
):
    cid = _company_id(user)
    obj = _get_or_404(db, ClientClaim, ident, "Reclamation / litige client")
    if obj.company_id != cid:
        raise HTTPException(403, "Acces refuse.")
    obj.is_active = False
    db.commit()
    db.refresh(obj)
    return obj


# ─── Releves periodiques compte client ─────────────────────────────────────────────────

@router.get("/account-reports", response_model=List[AccountReportOut])
def list_account_report(db: Session = Depends(get_db),
    user: User = Depends(require_perm("b2b.account_report.read")),
):
    cid = _company_id(user)
    return _scoped_list(db, AccountReport, cid)


@router.post("/account-reports", response_model=AccountReportOut, status_code=201)
def create_account_report(
    payload: AccountReportCreate,
    db: Session = Depends(get_db),
    user: User = Depends(require_perm("b2b.account_report.create")),
):
    cid = _company_id(user)
    data = payload.model_dump(exclude_unset=True)
    _check_unique(db, AccountReport, "reference", data.get("reference"), "reference", cid)
    obj = AccountReport(company_id=cid)
    _apply(data, obj)
    db.add(obj)
    db.commit()
    db.refresh(obj)
    return obj


@router.put("/account-reports/{ident}", response_model=AccountReportOut)
def update_account_report(
    ident: int,
    payload: AccountReportUpdate,
    db: Session = Depends(get_db),
    user: User = Depends(require_perm("b2b.account_report.modify")),
):
    cid = _company_id(user)
    obj = _get_or_404(db, AccountReport, ident, "Releves periodiques compte client")
    if obj.company_id != cid:
        raise HTTPException(403, "Acces refuse.")
    _apply(payload.model_dump(exclude_unset=True), obj)
    db.commit()
    db.refresh(obj)
    return obj


@router.delete("/account-reports/{ident}", response_model=AccountReportOut)
def delete_account_report(
    ident: int,
    db: Session = Depends(get_db),
    user: User = Depends(require_perm("b2b.account_report.modify")),
):
    cid = _company_id(user)
    obj = _get_or_404(db, AccountReport, ident, "Releves periodiques compte client")
    if obj.company_id != cid:
        raise HTTPException(403, "Acces refuse.")
    obj.is_active = False
    db.commit()
    db.refresh(obj)
    return obj

