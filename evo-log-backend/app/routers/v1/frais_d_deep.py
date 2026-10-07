"""Routeur CRUD genere pour portail-frais (expansion)."""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import Optional, List

from app.core.database import get_db
from app.core.permissions import require_perm
from app.models.user import User
from app.models.frais_d_deep import (
    FraExpenseReport,
    FraExpenseReceipt,
    FraExpenseAdvance,
    FraPerDiemClaim,
    FraMileageClaim,
    FraMealExpense,
    FraTravelBooking,
    FraHotelStay,
    FraTransportExpense,
    FraClientEntertainment,
    FraConferenceFee,
    FraOfficeSupply,
    FraCardTransaction,
    FraCurrencyConversion,
    FraExpenseApproval,
    FraExpenseDispute,
    FraVatRecovery,
    FraExpenseBudgetTracking,
    FraExpenseCategory,
)
from app.schemas.frais_d_deep import (
    FraExpenseReportCreate, FraExpenseReportUpdate, FraExpenseReportOut,
    FraExpenseReceiptCreate, FraExpenseReceiptUpdate, FraExpenseReceiptOut,
    FraExpenseAdvanceCreate, FraExpenseAdvanceUpdate, FraExpenseAdvanceOut,
    FraPerDiemClaimCreate, FraPerDiemClaimUpdate, FraPerDiemClaimOut,
    FraMileageClaimCreate, FraMileageClaimUpdate, FraMileageClaimOut,
    FraMealExpenseCreate, FraMealExpenseUpdate, FraMealExpenseOut,
    FraTravelBookingCreate, FraTravelBookingUpdate, FraTravelBookingOut,
    FraHotelStayCreate, FraHotelStayUpdate, FraHotelStayOut,
    FraTransportExpenseCreate, FraTransportExpenseUpdate, FraTransportExpenseOut,
    FraClientEntertainmentCreate, FraClientEntertainmentUpdate, FraClientEntertainmentOut,
    FraConferenceFeeCreate, FraConferenceFeeUpdate, FraConferenceFeeOut,
    FraOfficeSupplyCreate, FraOfficeSupplyUpdate, FraOfficeSupplyOut,
    FraCardTransactionCreate, FraCardTransactionUpdate, FraCardTransactionOut,
    FraCurrencyConversionCreate, FraCurrencyConversionUpdate, FraCurrencyConversionOut,
    FraExpenseApprovalCreate, FraExpenseApprovalUpdate, FraExpenseApprovalOut,
    FraExpenseDisputeCreate, FraExpenseDisputeUpdate, FraExpenseDisputeOut,
    FraVatRecoveryCreate, FraVatRecoveryUpdate, FraVatRecoveryOut,
    FraExpenseBudgetTrackingCreate, FraExpenseBudgetTrackingUpdate, FraExpenseBudgetTrackingOut,
    FraExpenseCategoryCreate, FraExpenseCategoryUpdate, FraExpenseCategoryOut,
)

router = APIRouter(tags=["portail-frais (expansion)"])


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

@router.get("/nomenclatures", summary="Vocabulaire metier portail-frais")
def nomenclatures(user: User = Depends(require_perm("tresorerie.nomenclature.read"))):
    from app.models import frais_d_deep as _md
    import enum as _pyenum
    out = {}
    for name in dir(_md):
        obj = getattr(_md, name)
        if isinstance(obj, type) and issubclass(obj, _pyenum.Enum) and obj is not _pyenum.Enum:
            out[name.lower()] = [{"code": m.name, "valeur": m.value} for m in obj]
    return out


# ─── Notes de frais ─────────────────────────────────────────────────

@router.get("/fra-expense-reports", response_model=List[FraExpenseReportOut])
def list_expense_report(statut: Optional[str] = None, db: Session = Depends(get_db),
    user: User = Depends(require_perm("tresorerie.expense_report.read")),
):
    cid = _company_id(user)
    return _scoped_list(db, FraExpenseReport, cid, {"statut": statut})


@router.post("/fra-expense-reports", response_model=FraExpenseReportOut, status_code=201)
def create_expense_report(
    payload: FraExpenseReportCreate,
    db: Session = Depends(get_db),
    user: User = Depends(require_perm("tresorerie.expense_report.create")),
):
    cid = _company_id(user)
    data = payload.model_dump(exclude_unset=True)
    _check_unique(db, FraExpenseReport, "reference", data.get("reference"), "reference", cid)
    obj = FraExpenseReport(company_id=cid)
    _apply(data, obj)
    db.add(obj)
    db.commit()
    db.refresh(obj)
    return obj


@router.put("/fra-expense-reports/{ident}", response_model=FraExpenseReportOut)
def update_expense_report(
    ident: int,
    payload: FraExpenseReportUpdate,
    db: Session = Depends(get_db),
    user: User = Depends(require_perm("tresorerie.expense_report.modify")),
):
    cid = _company_id(user)
    obj = _get_or_404(db, FraExpenseReport, ident, "Notes de frais")
    if obj.company_id != cid:
        raise HTTPException(403, "Acces refuse.")
    _apply(payload.model_dump(exclude_unset=True), obj)
    db.commit()
    db.refresh(obj)
    return obj


@router.delete("/fra-expense-reports/{ident}", response_model=FraExpenseReportOut)
def delete_expense_report(
    ident: int,
    db: Session = Depends(get_db),
    user: User = Depends(require_perm("tresorerie.expense_report.modify")),
):
    cid = _company_id(user)
    obj = _get_or_404(db, FraExpenseReport, ident, "Notes de frais")
    if obj.company_id != cid:
        raise HTTPException(403, "Acces refuse.")
    obj.is_active = False
    db.commit()
    db.refresh(obj)
    return obj


# ─── Justificatifs de frais ─────────────────────────────────────────────────

@router.get("/fra-expense-receipts", response_model=List[FraExpenseReceiptOut])
def list_expense_receipt(statut: Optional[str] = None, db: Session = Depends(get_db),
    user: User = Depends(require_perm("tresorerie.expense_receipt.read")),
):
    cid = _company_id(user)
    return _scoped_list(db, FraExpenseReceipt, cid, {"statut": statut})


@router.post("/fra-expense-receipts", response_model=FraExpenseReceiptOut, status_code=201)
def create_expense_receipt(
    payload: FraExpenseReceiptCreate,
    db: Session = Depends(get_db),
    user: User = Depends(require_perm("tresorerie.expense_receipt.create")),
):
    cid = _company_id(user)
    data = payload.model_dump(exclude_unset=True)
    _check_unique(db, FraExpenseReceipt, "reference", data.get("reference"), "reference", cid)
    obj = FraExpenseReceipt(company_id=cid)
    _apply(data, obj)
    db.add(obj)
    db.commit()
    db.refresh(obj)
    return obj


@router.put("/fra-expense-receipts/{ident}", response_model=FraExpenseReceiptOut)
def update_expense_receipt(
    ident: int,
    payload: FraExpenseReceiptUpdate,
    db: Session = Depends(get_db),
    user: User = Depends(require_perm("tresorerie.expense_receipt.modify")),
):
    cid = _company_id(user)
    obj = _get_or_404(db, FraExpenseReceipt, ident, "Justificatifs de frais")
    if obj.company_id != cid:
        raise HTTPException(403, "Acces refuse.")
    _apply(payload.model_dump(exclude_unset=True), obj)
    db.commit()
    db.refresh(obj)
    return obj


@router.delete("/fra-expense-receipts/{ident}", response_model=FraExpenseReceiptOut)
def delete_expense_receipt(
    ident: int,
    db: Session = Depends(get_db),
    user: User = Depends(require_perm("tresorerie.expense_receipt.modify")),
):
    cid = _company_id(user)
    obj = _get_or_404(db, FraExpenseReceipt, ident, "Justificatifs de frais")
    if obj.company_id != cid:
        raise HTTPException(403, "Acces refuse.")
    obj.is_active = False
    db.commit()
    db.refresh(obj)
    return obj


# ─── Avances de frais ─────────────────────────────────────────────────

@router.get("/fra-expense-advances", response_model=List[FraExpenseAdvanceOut])
def list_expense_advance(statut: Optional[str] = None, db: Session = Depends(get_db),
    user: User = Depends(require_perm("tresorerie.expense_advance.read")),
):
    cid = _company_id(user)
    return _scoped_list(db, FraExpenseAdvance, cid, {"statut": statut})


@router.post("/fra-expense-advances", response_model=FraExpenseAdvanceOut, status_code=201)
def create_expense_advance(
    payload: FraExpenseAdvanceCreate,
    db: Session = Depends(get_db),
    user: User = Depends(require_perm("tresorerie.expense_advance.create")),
):
    cid = _company_id(user)
    data = payload.model_dump(exclude_unset=True)
    _check_unique(db, FraExpenseAdvance, "reference", data.get("reference"), "reference", cid)
    obj = FraExpenseAdvance(company_id=cid)
    _apply(data, obj)
    db.add(obj)
    db.commit()
    db.refresh(obj)
    return obj


@router.put("/fra-expense-advances/{ident}", response_model=FraExpenseAdvanceOut)
def update_expense_advance(
    ident: int,
    payload: FraExpenseAdvanceUpdate,
    db: Session = Depends(get_db),
    user: User = Depends(require_perm("tresorerie.expense_advance.modify")),
):
    cid = _company_id(user)
    obj = _get_or_404(db, FraExpenseAdvance, ident, "Avances de frais")
    if obj.company_id != cid:
        raise HTTPException(403, "Acces refuse.")
    _apply(payload.model_dump(exclude_unset=True), obj)
    db.commit()
    db.refresh(obj)
    return obj


@router.delete("/fra-expense-advances/{ident}", response_model=FraExpenseAdvanceOut)
def delete_expense_advance(
    ident: int,
    db: Session = Depends(get_db),
    user: User = Depends(require_perm("tresorerie.expense_advance.modify")),
):
    cid = _company_id(user)
    obj = _get_or_404(db, FraExpenseAdvance, ident, "Avances de frais")
    if obj.company_id != cid:
        raise HTTPException(403, "Acces refuse.")
    obj.is_active = False
    db.commit()
    db.refresh(obj)
    return obj


# ─── Indemnites forfaitaires ─────────────────────────────────────────────────

@router.get("/fra-per-diem-claims", response_model=List[FraPerDiemClaimOut])
def list_per_diem_claim(statut: Optional[str] = None, db: Session = Depends(get_db),
    user: User = Depends(require_perm("tresorerie.per_diem_claim.read")),
):
    cid = _company_id(user)
    return _scoped_list(db, FraPerDiemClaim, cid, {"statut": statut})


@router.post("/fra-per-diem-claims", response_model=FraPerDiemClaimOut, status_code=201)
def create_per_diem_claim(
    payload: FraPerDiemClaimCreate,
    db: Session = Depends(get_db),
    user: User = Depends(require_perm("tresorerie.per_diem_claim.create")),
):
    cid = _company_id(user)
    data = payload.model_dump(exclude_unset=True)
    _check_unique(db, FraPerDiemClaim, "reference", data.get("reference"), "reference", cid)
    obj = FraPerDiemClaim(company_id=cid)
    _apply(data, obj)
    db.add(obj)
    db.commit()
    db.refresh(obj)
    return obj


@router.put("/fra-per-diem-claims/{ident}", response_model=FraPerDiemClaimOut)
def update_per_diem_claim(
    ident: int,
    payload: FraPerDiemClaimUpdate,
    db: Session = Depends(get_db),
    user: User = Depends(require_perm("tresorerie.per_diem_claim.modify")),
):
    cid = _company_id(user)
    obj = _get_or_404(db, FraPerDiemClaim, ident, "Indemnites forfaitaires")
    if obj.company_id != cid:
        raise HTTPException(403, "Acces refuse.")
    _apply(payload.model_dump(exclude_unset=True), obj)
    db.commit()
    db.refresh(obj)
    return obj


@router.delete("/fra-per-diem-claims/{ident}", response_model=FraPerDiemClaimOut)
def delete_per_diem_claim(
    ident: int,
    db: Session = Depends(get_db),
    user: User = Depends(require_perm("tresorerie.per_diem_claim.modify")),
):
    cid = _company_id(user)
    obj = _get_or_404(db, FraPerDiemClaim, ident, "Indemnites forfaitaires")
    if obj.company_id != cid:
        raise HTTPException(403, "Acces refuse.")
    obj.is_active = False
    db.commit()
    db.refresh(obj)
    return obj


# ─── Frais kilometriques ─────────────────────────────────────────────────

@router.get("/fra-mileage-claims", response_model=List[FraMileageClaimOut])
def list_mileage_claim(statut: Optional[str] = None, db: Session = Depends(get_db),
    user: User = Depends(require_perm("tresorerie.mileage_claim.read")),
):
    cid = _company_id(user)
    return _scoped_list(db, FraMileageClaim, cid, {"statut": statut})


@router.post("/fra-mileage-claims", response_model=FraMileageClaimOut, status_code=201)
def create_mileage_claim(
    payload: FraMileageClaimCreate,
    db: Session = Depends(get_db),
    user: User = Depends(require_perm("tresorerie.mileage_claim.create")),
):
    cid = _company_id(user)
    data = payload.model_dump(exclude_unset=True)
    _check_unique(db, FraMileageClaim, "reference", data.get("reference"), "reference", cid)
    obj = FraMileageClaim(company_id=cid)
    _apply(data, obj)
    db.add(obj)
    db.commit()
    db.refresh(obj)
    return obj


@router.put("/fra-mileage-claims/{ident}", response_model=FraMileageClaimOut)
def update_mileage_claim(
    ident: int,
    payload: FraMileageClaimUpdate,
    db: Session = Depends(get_db),
    user: User = Depends(require_perm("tresorerie.mileage_claim.modify")),
):
    cid = _company_id(user)
    obj = _get_or_404(db, FraMileageClaim, ident, "Frais kilometriques")
    if obj.company_id != cid:
        raise HTTPException(403, "Acces refuse.")
    _apply(payload.model_dump(exclude_unset=True), obj)
    db.commit()
    db.refresh(obj)
    return obj


@router.delete("/fra-mileage-claims/{ident}", response_model=FraMileageClaimOut)
def delete_mileage_claim(
    ident: int,
    db: Session = Depends(get_db),
    user: User = Depends(require_perm("tresorerie.mileage_claim.modify")),
):
    cid = _company_id(user)
    obj = _get_or_404(db, FraMileageClaim, ident, "Frais kilometriques")
    if obj.company_id != cid:
        raise HTTPException(403, "Acces refuse.")
    obj.is_active = False
    db.commit()
    db.refresh(obj)
    return obj


# ─── Frais de restauration ─────────────────────────────────────────────────

@router.get("/fra-meal-expenses", response_model=List[FraMealExpenseOut])
def list_meal_expense(statut: Optional[str] = None, db: Session = Depends(get_db),
    user: User = Depends(require_perm("tresorerie.meal_expense.read")),
):
    cid = _company_id(user)
    return _scoped_list(db, FraMealExpense, cid, {"statut": statut})


@router.post("/fra-meal-expenses", response_model=FraMealExpenseOut, status_code=201)
def create_meal_expense(
    payload: FraMealExpenseCreate,
    db: Session = Depends(get_db),
    user: User = Depends(require_perm("tresorerie.meal_expense.create")),
):
    cid = _company_id(user)
    data = payload.model_dump(exclude_unset=True)
    _check_unique(db, FraMealExpense, "reference", data.get("reference"), "reference", cid)
    obj = FraMealExpense(company_id=cid)
    _apply(data, obj)
    db.add(obj)
    db.commit()
    db.refresh(obj)
    return obj


@router.put("/fra-meal-expenses/{ident}", response_model=FraMealExpenseOut)
def update_meal_expense(
    ident: int,
    payload: FraMealExpenseUpdate,
    db: Session = Depends(get_db),
    user: User = Depends(require_perm("tresorerie.meal_expense.modify")),
):
    cid = _company_id(user)
    obj = _get_or_404(db, FraMealExpense, ident, "Frais de restauration")
    if obj.company_id != cid:
        raise HTTPException(403, "Acces refuse.")
    _apply(payload.model_dump(exclude_unset=True), obj)
    db.commit()
    db.refresh(obj)
    return obj


@router.delete("/fra-meal-expenses/{ident}", response_model=FraMealExpenseOut)
def delete_meal_expense(
    ident: int,
    db: Session = Depends(get_db),
    user: User = Depends(require_perm("tresorerie.meal_expense.modify")),
):
    cid = _company_id(user)
    obj = _get_or_404(db, FraMealExpense, ident, "Frais de restauration")
    if obj.company_id != cid:
        raise HTTPException(403, "Acces refuse.")
    obj.is_active = False
    db.commit()
    db.refresh(obj)
    return obj


# ─── Reservations de deplacement ─────────────────────────────────────────────────

@router.get("/fra-travel-bookings", response_model=List[FraTravelBookingOut])
def list_travel_booking(statut: Optional[str] = None, db: Session = Depends(get_db),
    user: User = Depends(require_perm("tresorerie.travel_booking.read")),
):
    cid = _company_id(user)
    return _scoped_list(db, FraTravelBooking, cid, {"statut": statut})


@router.post("/fra-travel-bookings", response_model=FraTravelBookingOut, status_code=201)
def create_travel_booking(
    payload: FraTravelBookingCreate,
    db: Session = Depends(get_db),
    user: User = Depends(require_perm("tresorerie.travel_booking.create")),
):
    cid = _company_id(user)
    data = payload.model_dump(exclude_unset=True)
    _check_unique(db, FraTravelBooking, "reference", data.get("reference"), "reference", cid)
    obj = FraTravelBooking(company_id=cid)
    _apply(data, obj)
    db.add(obj)
    db.commit()
    db.refresh(obj)
    return obj


@router.put("/fra-travel-bookings/{ident}", response_model=FraTravelBookingOut)
def update_travel_booking(
    ident: int,
    payload: FraTravelBookingUpdate,
    db: Session = Depends(get_db),
    user: User = Depends(require_perm("tresorerie.travel_booking.modify")),
):
    cid = _company_id(user)
    obj = _get_or_404(db, FraTravelBooking, ident, "Reservations de deplacement")
    if obj.company_id != cid:
        raise HTTPException(403, "Acces refuse.")
    _apply(payload.model_dump(exclude_unset=True), obj)
    db.commit()
    db.refresh(obj)
    return obj


@router.delete("/fra-travel-bookings/{ident}", response_model=FraTravelBookingOut)
def delete_travel_booking(
    ident: int,
    db: Session = Depends(get_db),
    user: User = Depends(require_perm("tresorerie.travel_booking.modify")),
):
    cid = _company_id(user)
    obj = _get_or_404(db, FraTravelBooking, ident, "Reservations de deplacement")
    if obj.company_id != cid:
        raise HTTPException(403, "Acces refuse.")
    obj.is_active = False
    db.commit()
    db.refresh(obj)
    return obj


# ─── Nuits d' hotel ─────────────────────────────────────────────────

@router.get("/fra-hotel-stays", response_model=List[FraHotelStayOut])
def list_hotel_stay(statut: Optional[str] = None, db: Session = Depends(get_db),
    user: User = Depends(require_perm("tresorerie.hotel_stay.read")),
):
    cid = _company_id(user)
    return _scoped_list(db, FraHotelStay, cid, {"statut": statut})


@router.post("/fra-hotel-stays", response_model=FraHotelStayOut, status_code=201)
def create_hotel_stay(
    payload: FraHotelStayCreate,
    db: Session = Depends(get_db),
    user: User = Depends(require_perm("tresorerie.hotel_stay.create")),
):
    cid = _company_id(user)
    data = payload.model_dump(exclude_unset=True)
    _check_unique(db, FraHotelStay, "reference", data.get("reference"), "reference", cid)
    obj = FraHotelStay(company_id=cid)
    _apply(data, obj)
    db.add(obj)
    db.commit()
    db.refresh(obj)
    return obj


@router.put("/fra-hotel-stays/{ident}", response_model=FraHotelStayOut)
def update_hotel_stay(
    ident: int,
    payload: FraHotelStayUpdate,
    db: Session = Depends(get_db),
    user: User = Depends(require_perm("tresorerie.hotel_stay.modify")),
):
    cid = _company_id(user)
    obj = _get_or_404(db, FraHotelStay, ident, "Nuits d' hotel")
    if obj.company_id != cid:
        raise HTTPException(403, "Acces refuse.")
    _apply(payload.model_dump(exclude_unset=True), obj)
    db.commit()
    db.refresh(obj)
    return obj


@router.delete("/fra-hotel-stays/{ident}", response_model=FraHotelStayOut)
def delete_hotel_stay(
    ident: int,
    db: Session = Depends(get_db),
    user: User = Depends(require_perm("tresorerie.hotel_stay.modify")),
):
    cid = _company_id(user)
    obj = _get_or_404(db, FraHotelStay, ident, "Nuits d' hotel")
    if obj.company_id != cid:
        raise HTTPException(403, "Acces refuse.")
    obj.is_active = False
    db.commit()
    db.refresh(obj)
    return obj


# ─── Frais de transport local ─────────────────────────────────────────────────

@router.get("/fra-transport-expenses", response_model=List[FraTransportExpenseOut])
def list_transport_expense(statut: Optional[str] = None, db: Session = Depends(get_db),
    user: User = Depends(require_perm("tresorerie.transport_expense.read")),
):
    cid = _company_id(user)
    return _scoped_list(db, FraTransportExpense, cid, {"statut": statut})


@router.post("/fra-transport-expenses", response_model=FraTransportExpenseOut, status_code=201)
def create_transport_expense(
    payload: FraTransportExpenseCreate,
    db: Session = Depends(get_db),
    user: User = Depends(require_perm("tresorerie.transport_expense.create")),
):
    cid = _company_id(user)
    data = payload.model_dump(exclude_unset=True)
    _check_unique(db, FraTransportExpense, "reference", data.get("reference"), "reference", cid)
    obj = FraTransportExpense(company_id=cid)
    _apply(data, obj)
    db.add(obj)
    db.commit()
    db.refresh(obj)
    return obj


@router.put("/fra-transport-expenses/{ident}", response_model=FraTransportExpenseOut)
def update_transport_expense(
    ident: int,
    payload: FraTransportExpenseUpdate,
    db: Session = Depends(get_db),
    user: User = Depends(require_perm("tresorerie.transport_expense.modify")),
):
    cid = _company_id(user)
    obj = _get_or_404(db, FraTransportExpense, ident, "Frais de transport local")
    if obj.company_id != cid:
        raise HTTPException(403, "Acces refuse.")
    _apply(payload.model_dump(exclude_unset=True), obj)
    db.commit()
    db.refresh(obj)
    return obj


@router.delete("/fra-transport-expenses/{ident}", response_model=FraTransportExpenseOut)
def delete_transport_expense(
    ident: int,
    db: Session = Depends(get_db),
    user: User = Depends(require_perm("tresorerie.transport_expense.modify")),
):
    cid = _company_id(user)
    obj = _get_or_404(db, FraTransportExpense, ident, "Frais de transport local")
    if obj.company_id != cid:
        raise HTTPException(403, "Acces refuse.")
    obj.is_active = False
    db.commit()
    db.refresh(obj)
    return obj


# ─── Frais de representation client ─────────────────────────────────────────────────

@router.get("/fra-client-entertainment", response_model=List[FraClientEntertainmentOut])
def list_client_entertainment(statut: Optional[str] = None, db: Session = Depends(get_db),
    user: User = Depends(require_perm("tresorerie.client_entertainment.read")),
):
    cid = _company_id(user)
    return _scoped_list(db, FraClientEntertainment, cid, {"statut": statut})


@router.post("/fra-client-entertainment", response_model=FraClientEntertainmentOut, status_code=201)
def create_client_entertainment(
    payload: FraClientEntertainmentCreate,
    db: Session = Depends(get_db),
    user: User = Depends(require_perm("tresorerie.client_entertainment.create")),
):
    cid = _company_id(user)
    data = payload.model_dump(exclude_unset=True)
    _check_unique(db, FraClientEntertainment, "reference", data.get("reference"), "reference", cid)
    obj = FraClientEntertainment(company_id=cid)
    _apply(data, obj)
    db.add(obj)
    db.commit()
    db.refresh(obj)
    return obj


@router.put("/fra-client-entertainment/{ident}", response_model=FraClientEntertainmentOut)
def update_client_entertainment(
    ident: int,
    payload: FraClientEntertainmentUpdate,
    db: Session = Depends(get_db),
    user: User = Depends(require_perm("tresorerie.client_entertainment.modify")),
):
    cid = _company_id(user)
    obj = _get_or_404(db, FraClientEntertainment, ident, "Frais de representation client")
    if obj.company_id != cid:
        raise HTTPException(403, "Acces refuse.")
    _apply(payload.model_dump(exclude_unset=True), obj)
    db.commit()
    db.refresh(obj)
    return obj


@router.delete("/fra-client-entertainment/{ident}", response_model=FraClientEntertainmentOut)
def delete_client_entertainment(
    ident: int,
    db: Session = Depends(get_db),
    user: User = Depends(require_perm("tresorerie.client_entertainment.modify")),
):
    cid = _company_id(user)
    obj = _get_or_404(db, FraClientEntertainment, ident, "Frais de representation client")
    if obj.company_id != cid:
        raise HTTPException(403, "Acces refuse.")
    obj.is_active = False
    db.commit()
    db.refresh(obj)
    return obj


# ─── Frais de salon et conference ─────────────────────────────────────────────────

@router.get("/fra-conference-fees", response_model=List[FraConferenceFeeOut])
def list_conference_fee(statut: Optional[str] = None, db: Session = Depends(get_db),
    user: User = Depends(require_perm("tresorerie.conference_fee.read")),
):
    cid = _company_id(user)
    return _scoped_list(db, FraConferenceFee, cid, {"statut": statut})


@router.post("/fra-conference-fees", response_model=FraConferenceFeeOut, status_code=201)
def create_conference_fee(
    payload: FraConferenceFeeCreate,
    db: Session = Depends(get_db),
    user: User = Depends(require_perm("tresorerie.conference_fee.create")),
):
    cid = _company_id(user)
    data = payload.model_dump(exclude_unset=True)
    _check_unique(db, FraConferenceFee, "reference", data.get("reference"), "reference", cid)
    obj = FraConferenceFee(company_id=cid)
    _apply(data, obj)
    db.add(obj)
    db.commit()
    db.refresh(obj)
    return obj


@router.put("/fra-conference-fees/{ident}", response_model=FraConferenceFeeOut)
def update_conference_fee(
    ident: int,
    payload: FraConferenceFeeUpdate,
    db: Session = Depends(get_db),
    user: User = Depends(require_perm("tresorerie.conference_fee.modify")),
):
    cid = _company_id(user)
    obj = _get_or_404(db, FraConferenceFee, ident, "Frais de salon et conference")
    if obj.company_id != cid:
        raise HTTPException(403, "Acces refuse.")
    _apply(payload.model_dump(exclude_unset=True), obj)
    db.commit()
    db.refresh(obj)
    return obj


@router.delete("/fra-conference-fees/{ident}", response_model=FraConferenceFeeOut)
def delete_conference_fee(
    ident: int,
    db: Session = Depends(get_db),
    user: User = Depends(require_perm("tresorerie.conference_fee.modify")),
):
    cid = _company_id(user)
    obj = _get_or_404(db, FraConferenceFee, ident, "Frais de salon et conference")
    if obj.company_id != cid:
        raise HTTPException(403, "Acces refuse.")
    obj.is_active = False
    db.commit()
    db.refresh(obj)
    return obj


# ─── Achats de fournitures ─────────────────────────────────────────────────

@router.get("/fra-office-supplies", response_model=List[FraOfficeSupplyOut])
def list_office_supply(statut: Optional[str] = None, db: Session = Depends(get_db),
    user: User = Depends(require_perm("tresorerie.office_supply.read")),
):
    cid = _company_id(user)
    return _scoped_list(db, FraOfficeSupply, cid, {"statut": statut})


@router.post("/fra-office-supplies", response_model=FraOfficeSupplyOut, status_code=201)
def create_office_supply(
    payload: FraOfficeSupplyCreate,
    db: Session = Depends(get_db),
    user: User = Depends(require_perm("tresorerie.office_supply.create")),
):
    cid = _company_id(user)
    data = payload.model_dump(exclude_unset=True)
    _check_unique(db, FraOfficeSupply, "reference", data.get("reference"), "reference", cid)
    obj = FraOfficeSupply(company_id=cid)
    _apply(data, obj)
    db.add(obj)
    db.commit()
    db.refresh(obj)
    return obj


@router.put("/fra-office-supplies/{ident}", response_model=FraOfficeSupplyOut)
def update_office_supply(
    ident: int,
    payload: FraOfficeSupplyUpdate,
    db: Session = Depends(get_db),
    user: User = Depends(require_perm("tresorerie.office_supply.modify")),
):
    cid = _company_id(user)
    obj = _get_or_404(db, FraOfficeSupply, ident, "Achats de fournitures")
    if obj.company_id != cid:
        raise HTTPException(403, "Acces refuse.")
    _apply(payload.model_dump(exclude_unset=True), obj)
    db.commit()
    db.refresh(obj)
    return obj


@router.delete("/fra-office-supplies/{ident}", response_model=FraOfficeSupplyOut)
def delete_office_supply(
    ident: int,
    db: Session = Depends(get_db),
    user: User = Depends(require_perm("tresorerie.office_supply.modify")),
):
    cid = _company_id(user)
    obj = _get_or_404(db, FraOfficeSupply, ident, "Achats de fournitures")
    if obj.company_id != cid:
        raise HTTPException(403, "Acces refuse.")
    obj.is_active = False
    db.commit()
    db.refresh(obj)
    return obj


# ─── Transactions carte entreprise ─────────────────────────────────────────────────

@router.get("/fra-card-transactions", response_model=List[FraCardTransactionOut])
def list_card_transaction(statut: Optional[str] = None, db: Session = Depends(get_db),
    user: User = Depends(require_perm("tresorerie.card_transaction.read")),
):
    cid = _company_id(user)
    return _scoped_list(db, FraCardTransaction, cid, {"statut": statut})


@router.post("/fra-card-transactions", response_model=FraCardTransactionOut, status_code=201)
def create_card_transaction(
    payload: FraCardTransactionCreate,
    db: Session = Depends(get_db),
    user: User = Depends(require_perm("tresorerie.card_transaction.create")),
):
    cid = _company_id(user)
    data = payload.model_dump(exclude_unset=True)
    _check_unique(db, FraCardTransaction, "reference", data.get("reference"), "reference", cid)
    obj = FraCardTransaction(company_id=cid)
    _apply(data, obj)
    db.add(obj)
    db.commit()
    db.refresh(obj)
    return obj


@router.put("/fra-card-transactions/{ident}", response_model=FraCardTransactionOut)
def update_card_transaction(
    ident: int,
    payload: FraCardTransactionUpdate,
    db: Session = Depends(get_db),
    user: User = Depends(require_perm("tresorerie.card_transaction.modify")),
):
    cid = _company_id(user)
    obj = _get_or_404(db, FraCardTransaction, ident, "Transactions carte entreprise")
    if obj.company_id != cid:
        raise HTTPException(403, "Acces refuse.")
    _apply(payload.model_dump(exclude_unset=True), obj)
    db.commit()
    db.refresh(obj)
    return obj


@router.delete("/fra-card-transactions/{ident}", response_model=FraCardTransactionOut)
def delete_card_transaction(
    ident: int,
    db: Session = Depends(get_db),
    user: User = Depends(require_perm("tresorerie.card_transaction.modify")),
):
    cid = _company_id(user)
    obj = _get_or_404(db, FraCardTransaction, ident, "Transactions carte entreprise")
    if obj.company_id != cid:
        raise HTTPException(403, "Acces refuse.")
    obj.is_active = False
    db.commit()
    db.refresh(obj)
    return obj


# ─── Conversions de devise ─────────────────────────────────────────────────

@router.get("/fra-currency-conversions", response_model=List[FraCurrencyConversionOut])
def list_currency_conversion(statut: Optional[str] = None, db: Session = Depends(get_db),
    user: User = Depends(require_perm("tresorerie.currency_conversion.read")),
):
    cid = _company_id(user)
    return _scoped_list(db, FraCurrencyConversion, cid, {"statut": statut})


@router.post("/fra-currency-conversions", response_model=FraCurrencyConversionOut, status_code=201)
def create_currency_conversion(
    payload: FraCurrencyConversionCreate,
    db: Session = Depends(get_db),
    user: User = Depends(require_perm("tresorerie.currency_conversion.create")),
):
    cid = _company_id(user)
    data = payload.model_dump(exclude_unset=True)
    _check_unique(db, FraCurrencyConversion, "reference", data.get("reference"), "reference", cid)
    obj = FraCurrencyConversion(company_id=cid)
    _apply(data, obj)
    db.add(obj)
    db.commit()
    db.refresh(obj)
    return obj


@router.put("/fra-currency-conversions/{ident}", response_model=FraCurrencyConversionOut)
def update_currency_conversion(
    ident: int,
    payload: FraCurrencyConversionUpdate,
    db: Session = Depends(get_db),
    user: User = Depends(require_perm("tresorerie.currency_conversion.modify")),
):
    cid = _company_id(user)
    obj = _get_or_404(db, FraCurrencyConversion, ident, "Conversions de devise")
    if obj.company_id != cid:
        raise HTTPException(403, "Acces refuse.")
    _apply(payload.model_dump(exclude_unset=True), obj)
    db.commit()
    db.refresh(obj)
    return obj


@router.delete("/fra-currency-conversions/{ident}", response_model=FraCurrencyConversionOut)
def delete_currency_conversion(
    ident: int,
    db: Session = Depends(get_db),
    user: User = Depends(require_perm("tresorerie.currency_conversion.modify")),
):
    cid = _company_id(user)
    obj = _get_or_404(db, FraCurrencyConversion, ident, "Conversions de devise")
    if obj.company_id != cid:
        raise HTTPException(403, "Acces refuse.")
    obj.is_active = False
    db.commit()
    db.refresh(obj)
    return obj


# ─── Validations de frais ─────────────────────────────────────────────────

@router.get("/fra-expense-approvals", response_model=List[FraExpenseApprovalOut])
def list_expense_approval(statut: Optional[str] = None, db: Session = Depends(get_db),
    user: User = Depends(require_perm("tresorerie.expense_approval.read")),
):
    cid = _company_id(user)
    return _scoped_list(db, FraExpenseApproval, cid, {"statut": statut})


@router.post("/fra-expense-approvals", response_model=FraExpenseApprovalOut, status_code=201)
def create_expense_approval(
    payload: FraExpenseApprovalCreate,
    db: Session = Depends(get_db),
    user: User = Depends(require_perm("tresorerie.expense_approval.create")),
):
    cid = _company_id(user)
    data = payload.model_dump(exclude_unset=True)
    _check_unique(db, FraExpenseApproval, "reference", data.get("reference"), "reference", cid)
    obj = FraExpenseApproval(company_id=cid)
    _apply(data, obj)
    db.add(obj)
    db.commit()
    db.refresh(obj)
    return obj


@router.put("/fra-expense-approvals/{ident}", response_model=FraExpenseApprovalOut)
def update_expense_approval(
    ident: int,
    payload: FraExpenseApprovalUpdate,
    db: Session = Depends(get_db),
    user: User = Depends(require_perm("tresorerie.expense_approval.modify")),
):
    cid = _company_id(user)
    obj = _get_or_404(db, FraExpenseApproval, ident, "Validations de frais")
    if obj.company_id != cid:
        raise HTTPException(403, "Acces refuse.")
    _apply(payload.model_dump(exclude_unset=True), obj)
    db.commit()
    db.refresh(obj)
    return obj


@router.delete("/fra-expense-approvals/{ident}", response_model=FraExpenseApprovalOut)
def delete_expense_approval(
    ident: int,
    db: Session = Depends(get_db),
    user: User = Depends(require_perm("tresorerie.expense_approval.modify")),
):
    cid = _company_id(user)
    obj = _get_or_404(db, FraExpenseApproval, ident, "Validations de frais")
    if obj.company_id != cid:
        raise HTTPException(403, "Acces refuse.")
    obj.is_active = False
    db.commit()
    db.refresh(obj)
    return obj


# ─── Litiges de frais ─────────────────────────────────────────────────

@router.get("/fra-expense-disputes", response_model=List[FraExpenseDisputeOut])
def list_expense_dispute(statut: Optional[str] = None, db: Session = Depends(get_db),
    user: User = Depends(require_perm("tresorerie.expense_dispute.read")),
):
    cid = _company_id(user)
    return _scoped_list(db, FraExpenseDispute, cid, {"statut": statut})


@router.post("/fra-expense-disputes", response_model=FraExpenseDisputeOut, status_code=201)
def create_expense_dispute(
    payload: FraExpenseDisputeCreate,
    db: Session = Depends(get_db),
    user: User = Depends(require_perm("tresorerie.expense_dispute.create")),
):
    cid = _company_id(user)
    data = payload.model_dump(exclude_unset=True)
    _check_unique(db, FraExpenseDispute, "reference", data.get("reference"), "reference", cid)
    obj = FraExpenseDispute(company_id=cid)
    _apply(data, obj)
    db.add(obj)
    db.commit()
    db.refresh(obj)
    return obj


@router.put("/fra-expense-disputes/{ident}", response_model=FraExpenseDisputeOut)
def update_expense_dispute(
    ident: int,
    payload: FraExpenseDisputeUpdate,
    db: Session = Depends(get_db),
    user: User = Depends(require_perm("tresorerie.expense_dispute.modify")),
):
    cid = _company_id(user)
    obj = _get_or_404(db, FraExpenseDispute, ident, "Litiges de frais")
    if obj.company_id != cid:
        raise HTTPException(403, "Acces refuse.")
    _apply(payload.model_dump(exclude_unset=True), obj)
    db.commit()
    db.refresh(obj)
    return obj


@router.delete("/fra-expense-disputes/{ident}", response_model=FraExpenseDisputeOut)
def delete_expense_dispute(
    ident: int,
    db: Session = Depends(get_db),
    user: User = Depends(require_perm("tresorerie.expense_dispute.modify")),
):
    cid = _company_id(user)
    obj = _get_or_404(db, FraExpenseDispute, ident, "Litiges de frais")
    if obj.company_id != cid:
        raise HTTPException(403, "Acces refuse.")
    obj.is_active = False
    db.commit()
    db.refresh(obj)
    return obj


# ─── Recuperation TVA sur frais ─────────────────────────────────────────────────

@router.get("/fra-vat-recovery", response_model=List[FraVatRecoveryOut])
def list_vat_recovery(statut: Optional[str] = None, db: Session = Depends(get_db),
    user: User = Depends(require_perm("tresorerie.vat_recovery.read")),
):
    cid = _company_id(user)
    return _scoped_list(db, FraVatRecovery, cid, {"statut": statut})


@router.post("/fra-vat-recovery", response_model=FraVatRecoveryOut, status_code=201)
def create_vat_recovery(
    payload: FraVatRecoveryCreate,
    db: Session = Depends(get_db),
    user: User = Depends(require_perm("tresorerie.vat_recovery.create")),
):
    cid = _company_id(user)
    data = payload.model_dump(exclude_unset=True)
    _check_unique(db, FraVatRecovery, "reference", data.get("reference"), "reference", cid)
    obj = FraVatRecovery(company_id=cid)
    _apply(data, obj)
    db.add(obj)
    db.commit()
    db.refresh(obj)
    return obj


@router.put("/fra-vat-recovery/{ident}", response_model=FraVatRecoveryOut)
def update_vat_recovery(
    ident: int,
    payload: FraVatRecoveryUpdate,
    db: Session = Depends(get_db),
    user: User = Depends(require_perm("tresorerie.vat_recovery.modify")),
):
    cid = _company_id(user)
    obj = _get_or_404(db, FraVatRecovery, ident, "Recuperation TVA sur frais")
    if obj.company_id != cid:
        raise HTTPException(403, "Acces refuse.")
    _apply(payload.model_dump(exclude_unset=True), obj)
    db.commit()
    db.refresh(obj)
    return obj


@router.delete("/fra-vat-recovery/{ident}", response_model=FraVatRecoveryOut)
def delete_vat_recovery(
    ident: int,
    db: Session = Depends(get_db),
    user: User = Depends(require_perm("tresorerie.vat_recovery.modify")),
):
    cid = _company_id(user)
    obj = _get_or_404(db, FraVatRecovery, ident, "Recuperation TVA sur frais")
    if obj.company_id != cid:
        raise HTTPException(403, "Acces refuse.")
    obj.is_active = False
    db.commit()
    db.refresh(obj)
    return obj


# ─── Suivi budget de frais ─────────────────────────────────────────────────

@router.get("/fra-expense-budget-tracking", response_model=List[FraExpenseBudgetTrackingOut])
def list_expense_budget_tracking(statut: Optional[str] = None, db: Session = Depends(get_db),
    user: User = Depends(require_perm("tresorerie.expense_budget_tracking.read")),
):
    cid = _company_id(user)
    return _scoped_list(db, FraExpenseBudgetTracking, cid, {"statut": statut})


@router.post("/fra-expense-budget-tracking", response_model=FraExpenseBudgetTrackingOut, status_code=201)
def create_expense_budget_tracking(
    payload: FraExpenseBudgetTrackingCreate,
    db: Session = Depends(get_db),
    user: User = Depends(require_perm("tresorerie.expense_budget_tracking.create")),
):
    cid = _company_id(user)
    data = payload.model_dump(exclude_unset=True)
    _check_unique(db, FraExpenseBudgetTracking, "reference", data.get("reference"), "reference", cid)
    obj = FraExpenseBudgetTracking(company_id=cid)
    _apply(data, obj)
    db.add(obj)
    db.commit()
    db.refresh(obj)
    return obj


@router.put("/fra-expense-budget-tracking/{ident}", response_model=FraExpenseBudgetTrackingOut)
def update_expense_budget_tracking(
    ident: int,
    payload: FraExpenseBudgetTrackingUpdate,
    db: Session = Depends(get_db),
    user: User = Depends(require_perm("tresorerie.expense_budget_tracking.modify")),
):
    cid = _company_id(user)
    obj = _get_or_404(db, FraExpenseBudgetTracking, ident, "Suivi budget de frais")
    if obj.company_id != cid:
        raise HTTPException(403, "Acces refuse.")
    _apply(payload.model_dump(exclude_unset=True), obj)
    db.commit()
    db.refresh(obj)
    return obj


@router.delete("/fra-expense-budget-tracking/{ident}", response_model=FraExpenseBudgetTrackingOut)
def delete_expense_budget_tracking(
    ident: int,
    db: Session = Depends(get_db),
    user: User = Depends(require_perm("tresorerie.expense_budget_tracking.modify")),
):
    cid = _company_id(user)
    obj = _get_or_404(db, FraExpenseBudgetTracking, ident, "Suivi budget de frais")
    if obj.company_id != cid:
        raise HTTPException(403, "Acces refuse.")
    obj.is_active = False
    db.commit()
    db.refresh(obj)
    return obj


# ─── Categories de frais ─────────────────────────────────────────────────

@router.get("/fra-expense-categories", response_model=List[FraExpenseCategoryOut])
def list_expense_category(statut: Optional[str] = None, db: Session = Depends(get_db),
    user: User = Depends(require_perm("tresorerie.expense_category.read")),
):
    cid = _company_id(user)
    return _scoped_list(db, FraExpenseCategory, cid, {"statut": statut})


@router.post("/fra-expense-categories", response_model=FraExpenseCategoryOut, status_code=201)
def create_expense_category(
    payload: FraExpenseCategoryCreate,
    db: Session = Depends(get_db),
    user: User = Depends(require_perm("tresorerie.expense_category.create")),
):
    cid = _company_id(user)
    data = payload.model_dump(exclude_unset=True)
    _check_unique(db, FraExpenseCategory, "reference", data.get("reference"), "reference", cid)
    obj = FraExpenseCategory(company_id=cid)
    _apply(data, obj)
    db.add(obj)
    db.commit()
    db.refresh(obj)
    return obj


@router.put("/fra-expense-categories/{ident}", response_model=FraExpenseCategoryOut)
def update_expense_category(
    ident: int,
    payload: FraExpenseCategoryUpdate,
    db: Session = Depends(get_db),
    user: User = Depends(require_perm("tresorerie.expense_category.modify")),
):
    cid = _company_id(user)
    obj = _get_or_404(db, FraExpenseCategory, ident, "Categories de frais")
    if obj.company_id != cid:
        raise HTTPException(403, "Acces refuse.")
    _apply(payload.model_dump(exclude_unset=True), obj)
    db.commit()
    db.refresh(obj)
    return obj


@router.delete("/fra-expense-categories/{ident}", response_model=FraExpenseCategoryOut)
def delete_expense_category(
    ident: int,
    db: Session = Depends(get_db),
    user: User = Depends(require_perm("tresorerie.expense_category.modify")),
):
    cid = _company_id(user)
    obj = _get_or_404(db, FraExpenseCategory, ident, "Categories de frais")
    if obj.company_id != cid:
        raise HTTPException(403, "Acces refuse.")
    obj.is_active = False
    db.commit()
    db.refresh(obj)
    return obj

