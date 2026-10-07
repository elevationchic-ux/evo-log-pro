"""Routeur CRUD genere pour dashboard (expansion)."""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import Optional, List

from app.core.database import get_db
from app.core.permissions import require_perm
from app.models.user import User
from app.models.dashboard_b_deep import (
    DashboardbOperationalKpi,
    DashboardbScorecard,
    DashboardbAlertRule,
    DashboardbRefreshJob,
    DashboardbSavedView,
)
from app.schemas.dashboard_b_deep import (
    DashboardbOperationalKpiCreate, DashboardbOperationalKpiUpdate, DashboardbOperationalKpiOut,
    DashboardbScorecardCreate, DashboardbScorecardUpdate, DashboardbScorecardOut,
    DashboardbAlertRuleCreate, DashboardbAlertRuleUpdate, DashboardbAlertRuleOut,
    DashboardbRefreshJobCreate, DashboardbRefreshJobUpdate, DashboardbRefreshJobOut,
    DashboardbSavedViewCreate, DashboardbSavedViewUpdate, DashboardbSavedViewOut,
)

router = APIRouter(tags=["dashboard (expansion)"])


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

@router.get("/nomenclatures", summary="Vocabulaire metier dashboard")
def nomenclatures(user: User = Depends(require_perm("dashboard.nomenclature.read"))):
    from app.models import dashboard_b_deep as _md
    import enum as _pyenum
    out = {}
    for name in dir(_md):
        obj = getattr(_md, name)
        if isinstance(obj, type) and issubclass(obj, _pyenum.Enum) and obj is not _pyenum.Enum:
            out[name.lower()] = [{"code": m.name, "valeur": m.value} for m in obj]
    return out


# ─── Indicateurs de performance operationnelle ─────────────────────────────────────────────────

@router.get("/dashb-operational-kpis", response_model=List[DashboardbOperationalKpiOut])
def list_operational_kpi(statut: Optional[str] = None, db: Session = Depends(get_db),
    user: User = Depends(require_perm("dashboard.operational_kpi.read")),
):
    cid = _company_id(user)
    return _scoped_list(db, DashboardbOperationalKpi, cid, {"statut": statut})


@router.post("/dashb-operational-kpis", response_model=DashboardbOperationalKpiOut, status_code=201)
def create_operational_kpi(
    payload: DashboardbOperationalKpiCreate,
    db: Session = Depends(get_db),
    user: User = Depends(require_perm("dashboard.operational_kpi.create")),
):
    cid = _company_id(user)
    data = payload.model_dump(exclude_unset=True)
    _check_unique(db, DashboardbOperationalKpi, "reference", data.get("reference"), "reference", cid)
    obj = DashboardbOperationalKpi(company_id=cid)
    _apply(data, obj)
    db.add(obj)
    db.commit()
    db.refresh(obj)
    return obj


@router.put("/dashb-operational-kpis/{ident}", response_model=DashboardbOperationalKpiOut)
def update_operational_kpi(
    ident: int,
    payload: DashboardbOperationalKpiUpdate,
    db: Session = Depends(get_db),
    user: User = Depends(require_perm("dashboard.operational_kpi.modify")),
):
    cid = _company_id(user)
    obj = _get_or_404(db, DashboardbOperationalKpi, ident, "Indicateurs de performance operationnelle")
    if obj.company_id != cid:
        raise HTTPException(403, "Acces refuse.")
    _apply(payload.model_dump(exclude_unset=True), obj)
    db.commit()
    db.refresh(obj)
    return obj


@router.delete("/dashb-operational-kpis/{ident}", response_model=DashboardbOperationalKpiOut)
def delete_operational_kpi(
    ident: int,
    db: Session = Depends(get_db),
    user: User = Depends(require_perm("dashboard.operational_kpi.modify")),
):
    cid = _company_id(user)
    obj = _get_or_404(db, DashboardbOperationalKpi, ident, "Indicateurs de performance operationnelle")
    if obj.company_id != cid:
        raise HTTPException(403, "Acces refuse.")
    obj.is_active = False
    db.commit()
    db.refresh(obj)
    return obj


# ─── Tableaux de bord direction ─────────────────────────────────────────────────

@router.get("/dashb-executive-scorecards", response_model=List[DashboardbScorecardOut])
def list_scorecard(statut: Optional[str] = None, db: Session = Depends(get_db),
    user: User = Depends(require_perm("dashboard.scorecard.read")),
):
    cid = _company_id(user)
    return _scoped_list(db, DashboardbScorecard, cid, {"statut": statut})


@router.post("/dashb-executive-scorecards", response_model=DashboardbScorecardOut, status_code=201)
def create_scorecard(
    payload: DashboardbScorecardCreate,
    db: Session = Depends(get_db),
    user: User = Depends(require_perm("dashboard.scorecard.create")),
):
    cid = _company_id(user)
    data = payload.model_dump(exclude_unset=True)
    _check_unique(db, DashboardbScorecard, "reference", data.get("reference"), "reference", cid)
    obj = DashboardbScorecard(company_id=cid)
    _apply(data, obj)
    db.add(obj)
    db.commit()
    db.refresh(obj)
    return obj


@router.put("/dashb-executive-scorecards/{ident}", response_model=DashboardbScorecardOut)
def update_scorecard(
    ident: int,
    payload: DashboardbScorecardUpdate,
    db: Session = Depends(get_db),
    user: User = Depends(require_perm("dashboard.scorecard.modify")),
):
    cid = _company_id(user)
    obj = _get_or_404(db, DashboardbScorecard, ident, "Tableaux de bord direction")
    if obj.company_id != cid:
        raise HTTPException(403, "Acces refuse.")
    _apply(payload.model_dump(exclude_unset=True), obj)
    db.commit()
    db.refresh(obj)
    return obj


@router.delete("/dashb-executive-scorecards/{ident}", response_model=DashboardbScorecardOut)
def delete_scorecard(
    ident: int,
    db: Session = Depends(get_db),
    user: User = Depends(require_perm("dashboard.scorecard.modify")),
):
    cid = _company_id(user)
    obj = _get_or_404(db, DashboardbScorecard, ident, "Tableaux de bord direction")
    if obj.company_id != cid:
        raise HTTPException(403, "Acces refuse.")
    obj.is_active = False
    db.commit()
    db.refresh(obj)
    return obj


# ─── Regles d'alerte ─────────────────────────────────────────────────

@router.get("/dashb-alert-rules", response_model=List[DashboardbAlertRuleOut])
def list_alert_rule(statut: Optional[str] = None, db: Session = Depends(get_db),
    user: User = Depends(require_perm("dashboard.alert_rule.read")),
):
    cid = _company_id(user)
    return _scoped_list(db, DashboardbAlertRule, cid, {"statut": statut})


@router.post("/dashb-alert-rules", response_model=DashboardbAlertRuleOut, status_code=201)
def create_alert_rule(
    payload: DashboardbAlertRuleCreate,
    db: Session = Depends(get_db),
    user: User = Depends(require_perm("dashboard.alert_rule.create")),
):
    cid = _company_id(user)
    data = payload.model_dump(exclude_unset=True)
    _check_unique(db, DashboardbAlertRule, "reference", data.get("reference"), "reference", cid)
    obj = DashboardbAlertRule(company_id=cid)
    _apply(data, obj)
    db.add(obj)
    db.commit()
    db.refresh(obj)
    return obj


@router.put("/dashb-alert-rules/{ident}", response_model=DashboardbAlertRuleOut)
def update_alert_rule(
    ident: int,
    payload: DashboardbAlertRuleUpdate,
    db: Session = Depends(get_db),
    user: User = Depends(require_perm("dashboard.alert_rule.modify")),
):
    cid = _company_id(user)
    obj = _get_or_404(db, DashboardbAlertRule, ident, "Regles d'alerte")
    if obj.company_id != cid:
        raise HTTPException(403, "Acces refuse.")
    _apply(payload.model_dump(exclude_unset=True), obj)
    db.commit()
    db.refresh(obj)
    return obj


@router.delete("/dashb-alert-rules/{ident}", response_model=DashboardbAlertRuleOut)
def delete_alert_rule(
    ident: int,
    db: Session = Depends(get_db),
    user: User = Depends(require_perm("dashboard.alert_rule.modify")),
):
    cid = _company_id(user)
    obj = _get_or_404(db, DashboardbAlertRule, ident, "Regles d'alerte")
    if obj.company_id != cid:
        raise HTTPException(403, "Acces refuse.")
    obj.is_active = False
    db.commit()
    db.refresh(obj)
    return obj


# ─── Taches de rafraichissement ─────────────────────────────────────────────────

@router.get("/dashb-data-refresh-jobs", response_model=List[DashboardbRefreshJobOut])
def list_refresh_job(statut: Optional[str] = None, db: Session = Depends(get_db),
    user: User = Depends(require_perm("dashboard.refresh_job.read")),
):
    cid = _company_id(user)
    return _scoped_list(db, DashboardbRefreshJob, cid, {"statut": statut})


@router.post("/dashb-data-refresh-jobs", response_model=DashboardbRefreshJobOut, status_code=201)
def create_refresh_job(
    payload: DashboardbRefreshJobCreate,
    db: Session = Depends(get_db),
    user: User = Depends(require_perm("dashboard.refresh_job.create")),
):
    cid = _company_id(user)
    data = payload.model_dump(exclude_unset=True)
    _check_unique(db, DashboardbRefreshJob, "reference", data.get("reference"), "reference", cid)
    obj = DashboardbRefreshJob(company_id=cid)
    _apply(data, obj)
    db.add(obj)
    db.commit()
    db.refresh(obj)
    return obj


@router.put("/dashb-data-refresh-jobs/{ident}", response_model=DashboardbRefreshJobOut)
def update_refresh_job(
    ident: int,
    payload: DashboardbRefreshJobUpdate,
    db: Session = Depends(get_db),
    user: User = Depends(require_perm("dashboard.refresh_job.modify")),
):
    cid = _company_id(user)
    obj = _get_or_404(db, DashboardbRefreshJob, ident, "Taches de rafraichissement")
    if obj.company_id != cid:
        raise HTTPException(403, "Acces refuse.")
    _apply(payload.model_dump(exclude_unset=True), obj)
    db.commit()
    db.refresh(obj)
    return obj


@router.delete("/dashb-data-refresh-jobs/{ident}", response_model=DashboardbRefreshJobOut)
def delete_refresh_job(
    ident: int,
    db: Session = Depends(get_db),
    user: User = Depends(require_perm("dashboard.refresh_job.modify")),
):
    cid = _company_id(user)
    obj = _get_or_404(db, DashboardbRefreshJob, ident, "Taches de rafraichissement")
    if obj.company_id != cid:
        raise HTTPException(403, "Acces refuse.")
    obj.is_active = False
    db.commit()
    db.refresh(obj)
    return obj


# ─── Vues enregistrees ─────────────────────────────────────────────────

@router.get("/dashb-saved-views", response_model=List[DashboardbSavedViewOut])
def list_saved_view(statut: Optional[str] = None, db: Session = Depends(get_db),
    user: User = Depends(require_perm("dashboard.saved_view.read")),
):
    cid = _company_id(user)
    return _scoped_list(db, DashboardbSavedView, cid, {"statut": statut})


@router.post("/dashb-saved-views", response_model=DashboardbSavedViewOut, status_code=201)
def create_saved_view(
    payload: DashboardbSavedViewCreate,
    db: Session = Depends(get_db),
    user: User = Depends(require_perm("dashboard.saved_view.create")),
):
    cid = _company_id(user)
    data = payload.model_dump(exclude_unset=True)
    _check_unique(db, DashboardbSavedView, "reference", data.get("reference"), "reference", cid)
    obj = DashboardbSavedView(company_id=cid)
    _apply(data, obj)
    db.add(obj)
    db.commit()
    db.refresh(obj)
    return obj


@router.put("/dashb-saved-views/{ident}", response_model=DashboardbSavedViewOut)
def update_saved_view(
    ident: int,
    payload: DashboardbSavedViewUpdate,
    db: Session = Depends(get_db),
    user: User = Depends(require_perm("dashboard.saved_view.modify")),
):
    cid = _company_id(user)
    obj = _get_or_404(db, DashboardbSavedView, ident, "Vues enregistrees")
    if obj.company_id != cid:
        raise HTTPException(403, "Acces refuse.")
    _apply(payload.model_dump(exclude_unset=True), obj)
    db.commit()
    db.refresh(obj)
    return obj


@router.delete("/dashb-saved-views/{ident}", response_model=DashboardbSavedViewOut)
def delete_saved_view(
    ident: int,
    db: Session = Depends(get_db),
    user: User = Depends(require_perm("dashboard.saved_view.modify")),
):
    cid = _company_id(user)
    obj = _get_or_404(db, DashboardbSavedView, ident, "Vues enregistrees")
    if obj.company_id != cid:
        raise HTTPException(403, "Acces refuse.")
    obj.is_active = False
    db.commit()
    db.refresh(obj)
    return obj

