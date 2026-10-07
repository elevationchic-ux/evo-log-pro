"""Routeur CRUD genere pour chat (expansion)."""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import Optional, List

from app.core.database import get_db
from app.core.permissions import require_perm
from app.models.user import User
from app.models.chat_d5_deep import (
    ChtAnnouncement,
    ChtChannel,
    ChtContentReport,
)
from app.schemas.chat_d5_deep import (
    ChtAnnouncementCreate, ChtAnnouncementUpdate, ChtAnnouncementOut,
    ChtChannelCreate, ChtChannelUpdate, ChtChannelOut,
    ChtContentReportCreate, ChtContentReportUpdate, ChtContentReportOut,
)

router = APIRouter(tags=["chat (expansion)"])


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

@router.get("/nomenclatures", summary="Vocabulaire metier chat")
def nomenclatures(user: User = Depends(require_perm("communication.nomenclature.read"))):
    from app.models import chat_d5_deep as _md
    import enum as _pyenum
    out = {}
    for name in dir(_md):
        obj = getattr(_md, name)
        if isinstance(obj, type) and issubclass(obj, _pyenum.Enum) and obj is not _pyenum.Enum:
            out[name.lower()] = [{"code": m.name, "valeur": m.value} for m in obj]
    return out


# ─── Communiques officiels ─────────────────────────────────────────────────

@router.get("/cht-announcements", response_model=List[ChtAnnouncementOut])
def list_announcement(statut: Optional[str] = None, db: Session = Depends(get_db),
    user: User = Depends(require_perm("communication.announcement.read")),
):
    cid = _company_id(user)
    return _scoped_list(db, ChtAnnouncement, cid, {"statut": statut})


@router.post("/cht-announcements", response_model=ChtAnnouncementOut, status_code=201)
def create_announcement(
    payload: ChtAnnouncementCreate,
    db: Session = Depends(get_db),
    user: User = Depends(require_perm("communication.announcement.create")),
):
    cid = _company_id(user)
    data = payload.model_dump(exclude_unset=True)
    _check_unique(db, ChtAnnouncement, "reference", data.get("reference"), "reference", cid)
    obj = ChtAnnouncement(company_id=cid)
    _apply(data, obj)
    db.add(obj)
    db.commit()
    db.refresh(obj)
    return obj


@router.put("/cht-announcements/{ident}", response_model=ChtAnnouncementOut)
def update_announcement(
    ident: int,
    payload: ChtAnnouncementUpdate,
    db: Session = Depends(get_db),
    user: User = Depends(require_perm("communication.announcement.modify")),
):
    cid = _company_id(user)
    obj = _get_or_404(db, ChtAnnouncement, ident, "Communiques officiels")
    if obj.company_id != cid:
        raise HTTPException(403, "Acces refuse.")
    _apply(payload.model_dump(exclude_unset=True), obj)
    db.commit()
    db.refresh(obj)
    return obj


@router.delete("/cht-announcements/{ident}", response_model=ChtAnnouncementOut)
def delete_announcement(
    ident: int,
    db: Session = Depends(get_db),
    user: User = Depends(require_perm("communication.announcement.modify")),
):
    cid = _company_id(user)
    obj = _get_or_404(db, ChtAnnouncement, ident, "Communiques officiels")
    if obj.company_id != cid:
        raise HTTPException(403, "Acces refuse.")
    obj.is_active = False
    db.commit()
    db.refresh(obj)
    return obj


# ─── Canaux thematiques ─────────────────────────────────────────────────

@router.get("/cht-channels", response_model=List[ChtChannelOut])
def list_channel(statut: Optional[str] = None, db: Session = Depends(get_db),
    user: User = Depends(require_perm("communication.channel.read")),
):
    cid = _company_id(user)
    return _scoped_list(db, ChtChannel, cid, {"statut": statut})


@router.post("/cht-channels", response_model=ChtChannelOut, status_code=201)
def create_channel(
    payload: ChtChannelCreate,
    db: Session = Depends(get_db),
    user: User = Depends(require_perm("communication.channel.create")),
):
    cid = _company_id(user)
    data = payload.model_dump(exclude_unset=True)
    _check_unique(db, ChtChannel, "reference", data.get("reference"), "reference", cid)
    obj = ChtChannel(company_id=cid)
    _apply(data, obj)
    db.add(obj)
    db.commit()
    db.refresh(obj)
    return obj


@router.put("/cht-channels/{ident}", response_model=ChtChannelOut)
def update_channel(
    ident: int,
    payload: ChtChannelUpdate,
    db: Session = Depends(get_db),
    user: User = Depends(require_perm("communication.channel.modify")),
):
    cid = _company_id(user)
    obj = _get_or_404(db, ChtChannel, ident, "Canaux thematiques")
    if obj.company_id != cid:
        raise HTTPException(403, "Acces refuse.")
    _apply(payload.model_dump(exclude_unset=True), obj)
    db.commit()
    db.refresh(obj)
    return obj


@router.delete("/cht-channels/{ident}", response_model=ChtChannelOut)
def delete_channel(
    ident: int,
    db: Session = Depends(get_db),
    user: User = Depends(require_perm("communication.channel.modify")),
):
    cid = _company_id(user)
    obj = _get_or_404(db, ChtChannel, ident, "Canaux thematiques")
    if obj.company_id != cid:
        raise HTTPException(403, "Acces refuse.")
    obj.is_active = False
    db.commit()
    db.refresh(obj)
    return obj


# ─── Signalements de contenu ─────────────────────────────────────────────────

@router.get("/cht-content-reports", response_model=List[ChtContentReportOut])
def list_content_report(statut: Optional[str] = None, db: Session = Depends(get_db),
    user: User = Depends(require_perm("communication.content_report.read")),
):
    cid = _company_id(user)
    return _scoped_list(db, ChtContentReport, cid, {"statut": statut})


@router.post("/cht-content-reports", response_model=ChtContentReportOut, status_code=201)
def create_content_report(
    payload: ChtContentReportCreate,
    db: Session = Depends(get_db),
    user: User = Depends(require_perm("communication.content_report.create")),
):
    cid = _company_id(user)
    data = payload.model_dump(exclude_unset=True)
    _check_unique(db, ChtContentReport, "reference", data.get("reference"), "reference", cid)
    obj = ChtContentReport(company_id=cid)
    _apply(data, obj)
    db.add(obj)
    db.commit()
    db.refresh(obj)
    return obj


@router.put("/cht-content-reports/{ident}", response_model=ChtContentReportOut)
def update_content_report(
    ident: int,
    payload: ChtContentReportUpdate,
    db: Session = Depends(get_db),
    user: User = Depends(require_perm("communication.content_report.modify")),
):
    cid = _company_id(user)
    obj = _get_or_404(db, ChtContentReport, ident, "Signalements de contenu")
    if obj.company_id != cid:
        raise HTTPException(403, "Acces refuse.")
    _apply(payload.model_dump(exclude_unset=True), obj)
    db.commit()
    db.refresh(obj)
    return obj


@router.delete("/cht-content-reports/{ident}", response_model=ChtContentReportOut)
def delete_content_report(
    ident: int,
    db: Session = Depends(get_db),
    user: User = Depends(require_perm("communication.content_report.modify")),
):
    cid = _company_id(user)
    obj = _get_or_404(db, ChtContentReport, ident, "Signalements de contenu")
    if obj.company_id != cid:
        raise HTTPException(403, "Acces refuse.")
    obj.is_active = False
    db.commit()
    db.refresh(obj)
    return obj

