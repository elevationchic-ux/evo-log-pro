"""Routeur CRUD genere pour dashboard (expansion)."""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import Optional, List

from app.core.database import get_db
from app.core.permissions import require_perm
from app.models.user import User
from app.models.dashboard_deep import (
    ModuleHealth,
    ActivityRecord,
    UnifiedTask,
    QuickAction,
    TeamPerformance,
    FinancialSummary,
    OperationalAlert,
    RecentDocument,
    UnifiedAgenda,
    IntegrationStatus,
)
from app.schemas.dashboard_deep import (
    ModuleHealthCreate, ModuleHealthUpdate, ModuleHealthOut,
    ActivityRecordCreate, ActivityRecordUpdate, ActivityRecordOut,
    UnifiedTaskCreate, UnifiedTaskUpdate, UnifiedTaskOut,
    QuickActionCreate, QuickActionUpdate, QuickActionOut,
    TeamPerformanceCreate, TeamPerformanceUpdate, TeamPerformanceOut,
    FinancialSummaryCreate, FinancialSummaryUpdate, FinancialSummaryOut,
    OperationalAlertCreate, OperationalAlertUpdate, OperationalAlertOut,
    RecentDocumentCreate, RecentDocumentUpdate, RecentDocumentOut,
    UnifiedAgendaCreate, UnifiedAgendaUpdate, UnifiedAgendaOut,
    IntegrationStatusCreate, IntegrationStatusUpdate, IntegrationStatusOut,
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
    from app.models import dashboard_deep as _md
    import enum as _pyenum
    out = {}
    for name in dir(_md):
        obj = getattr(_md, name)
        if isinstance(obj, type) and issubclass(obj, _pyenum.Enum) and obj is not _pyenum.Enum:
            out[name.lower()] = [{"code": m.name, "valeur": m.value} for m in obj]
    return out


# ─── Sante fonctionnelle des modules ─────────────────────────────────────────────────

@router.get("/module-healths", response_model=List[ModuleHealthOut])
def list_module_health(db: Session = Depends(get_db),
    user: User = Depends(require_perm("dashboard.module_health.read")),
):
    cid = _company_id(user)
    return _scoped_list(db, ModuleHealth, cid)


@router.post("/module-healths", response_model=ModuleHealthOut, status_code=201)
def create_module_health(
    payload: ModuleHealthCreate,
    db: Session = Depends(get_db),
    user: User = Depends(require_perm("dashboard.module_health.create")),
):
    cid = _company_id(user)
    data = payload.model_dump(exclude_unset=True)
    _check_unique(db, ModuleHealth, "code_module", data.get("code_module"), "code_module", cid)
    obj = ModuleHealth(company_id=cid)
    _apply(data, obj)
    db.add(obj)
    db.commit()
    db.refresh(obj)
    return obj


@router.put("/module-healths/{ident}", response_model=ModuleHealthOut)
def update_module_health(
    ident: int,
    payload: ModuleHealthUpdate,
    db: Session = Depends(get_db),
    user: User = Depends(require_perm("dashboard.module_health.modify")),
):
    cid = _company_id(user)
    obj = _get_or_404(db, ModuleHealth, ident, "Sante fonctionnelle des modules")
    if obj.company_id != cid:
        raise HTTPException(403, "Acces refuse.")
    _apply(payload.model_dump(exclude_unset=True), obj)
    db.commit()
    db.refresh(obj)
    return obj


@router.delete("/module-healths/{ident}", response_model=ModuleHealthOut)
def delete_module_health(
    ident: int,
    db: Session = Depends(get_db),
    user: User = Depends(require_perm("dashboard.module_health.modify")),
):
    cid = _company_id(user)
    obj = _get_or_404(db, ModuleHealth, ident, "Sante fonctionnelle des modules")
    if obj.company_id != cid:
        raise HTTPException(403, "Acces refuse.")
    obj.is_active = False
    db.commit()
    db.refresh(obj)
    return obj


# ─── Flux d'activite recent ─────────────────────────────────────────────────

@router.get("/activity-records", response_model=List[ActivityRecordOut])
def list_activity_feed(db: Session = Depends(get_db),
    user: User = Depends(require_perm("dashboard.activity_feed.read")),
):
    cid = _company_id(user)
    return _scoped_list(db, ActivityRecord, cid)


@router.post("/activity-records", response_model=ActivityRecordOut, status_code=201)
def create_activity_feed(
    payload: ActivityRecordCreate,
    db: Session = Depends(get_db),
    user: User = Depends(require_perm("dashboard.activity_feed.create")),
):
    cid = _company_id(user)
    data = payload.model_dump(exclude_unset=True)
    _check_unique(db, ActivityRecord, "reference", data.get("reference"), "reference", cid)
    obj = ActivityRecord(company_id=cid)
    _apply(data, obj)
    db.add(obj)
    db.commit()
    db.refresh(obj)
    return obj


@router.put("/activity-records/{ident}", response_model=ActivityRecordOut)
def update_activity_feed(
    ident: int,
    payload: ActivityRecordUpdate,
    db: Session = Depends(get_db),
    user: User = Depends(require_perm("dashboard.activity_feed.modify")),
):
    cid = _company_id(user)
    obj = _get_or_404(db, ActivityRecord, ident, "Flux d'activite recent")
    if obj.company_id != cid:
        raise HTTPException(403, "Acces refuse.")
    _apply(payload.model_dump(exclude_unset=True), obj)
    db.commit()
    db.refresh(obj)
    return obj


@router.delete("/activity-records/{ident}", response_model=ActivityRecordOut)
def delete_activity_feed(
    ident: int,
    db: Session = Depends(get_db),
    user: User = Depends(require_perm("dashboard.activity_feed.modify")),
):
    cid = _company_id(user)
    obj = _get_or_404(db, ActivityRecord, ident, "Flux d'activite recent")
    if obj.company_id != cid:
        raise HTTPException(403, "Acces refuse.")
    obj.is_active = False
    db.commit()
    db.refresh(obj)
    return obj


# ─── Centre de taches / to-do unifie ─────────────────────────────────────────────────

@router.get("/unified-tasks", response_model=List[UnifiedTaskOut])
def list_task_center(statut: Optional[str] = None, db: Session = Depends(get_db),
    user: User = Depends(require_perm("dashboard.task_center.read")),
):
    cid = _company_id(user)
    return _scoped_list(db, UnifiedTask, cid, {"statut": statut})


@router.post("/unified-tasks", response_model=UnifiedTaskOut, status_code=201)
def create_task_center(
    payload: UnifiedTaskCreate,
    db: Session = Depends(get_db),
    user: User = Depends(require_perm("dashboard.task_center.create")),
):
    cid = _company_id(user)
    data = payload.model_dump(exclude_unset=True)
    _check_unique(db, UnifiedTask, "reference", data.get("reference"), "reference", cid)
    obj = UnifiedTask(company_id=cid)
    _apply(data, obj)
    db.add(obj)
    db.commit()
    db.refresh(obj)
    return obj


@router.put("/unified-tasks/{ident}", response_model=UnifiedTaskOut)
def update_task_center(
    ident: int,
    payload: UnifiedTaskUpdate,
    db: Session = Depends(get_db),
    user: User = Depends(require_perm("dashboard.task_center.modify")),
):
    cid = _company_id(user)
    obj = _get_or_404(db, UnifiedTask, ident, "Centre de taches / to-do unifie")
    if obj.company_id != cid:
        raise HTTPException(403, "Acces refuse.")
    _apply(payload.model_dump(exclude_unset=True), obj)
    db.commit()
    db.refresh(obj)
    return obj


@router.delete("/unified-tasks/{ident}", response_model=UnifiedTaskOut)
def delete_task_center(
    ident: int,
    db: Session = Depends(get_db),
    user: User = Depends(require_perm("dashboard.task_center.modify")),
):
    cid = _company_id(user)
    obj = _get_or_404(db, UnifiedTask, ident, "Centre de taches / to-do unifie")
    if obj.company_id != cid:
        raise HTTPException(403, "Acces refuse.")
    obj.is_active = False
    db.commit()
    db.refresh(obj)
    return obj


# ─── Raccourcis operationnels config. ─────────────────────────────────────────────────

@router.get("/quick-actions", response_model=List[QuickActionOut])
def list_quick_actions(db: Session = Depends(get_db),
    user: User = Depends(require_perm("dashboard.quick_actions.read")),
):
    cid = _company_id(user)
    return _scoped_list(db, QuickAction, cid)


@router.post("/quick-actions", response_model=QuickActionOut, status_code=201)
def create_quick_actions(
    payload: QuickActionCreate,
    db: Session = Depends(get_db),
    user: User = Depends(require_perm("dashboard.quick_actions.create")),
):
    cid = _company_id(user)
    data = payload.model_dump(exclude_unset=True)
    _check_unique(db, QuickAction, "reference", data.get("reference"), "reference", cid)
    obj = QuickAction(company_id=cid)
    _apply(data, obj)
    db.add(obj)
    db.commit()
    db.refresh(obj)
    return obj


@router.put("/quick-actions/{ident}", response_model=QuickActionOut)
def update_quick_actions(
    ident: int,
    payload: QuickActionUpdate,
    db: Session = Depends(get_db),
    user: User = Depends(require_perm("dashboard.quick_actions.modify")),
):
    cid = _company_id(user)
    obj = _get_or_404(db, QuickAction, ident, "Raccourcis operationnels config.")
    if obj.company_id != cid:
        raise HTTPException(403, "Acces refuse.")
    _apply(payload.model_dump(exclude_unset=True), obj)
    db.commit()
    db.refresh(obj)
    return obj


@router.delete("/quick-actions/{ident}", response_model=QuickActionOut)
def delete_quick_actions(
    ident: int,
    db: Session = Depends(get_db),
    user: User = Depends(require_perm("dashboard.quick_actions.modify")),
):
    cid = _company_id(user)
    obj = _get_or_404(db, QuickAction, ident, "Raccourcis operationnels config.")
    if obj.company_id != cid:
        raise HTTPException(403, "Acces refuse.")
    obj.is_active = False
    db.commit()
    db.refresh(obj)
    return obj


# ─── Performance et productivite equipes ─────────────────────────────────────────────────

@router.get("/team-performances", response_model=List[TeamPerformanceOut])
def list_team_performance(db: Session = Depends(get_db),
    user: User = Depends(require_perm("dashboard.team_performance.read")),
):
    cid = _company_id(user)
    return _scoped_list(db, TeamPerformance, cid)


@router.post("/team-performances", response_model=TeamPerformanceOut, status_code=201)
def create_team_performance(
    payload: TeamPerformanceCreate,
    db: Session = Depends(get_db),
    user: User = Depends(require_perm("dashboard.team_performance.create")),
):
    cid = _company_id(user)
    data = payload.model_dump(exclude_unset=True)
    _check_unique(db, TeamPerformance, "reference", data.get("reference"), "reference", cid)
    obj = TeamPerformance(company_id=cid)
    _apply(data, obj)
    db.add(obj)
    db.commit()
    db.refresh(obj)
    return obj


@router.put("/team-performances/{ident}", response_model=TeamPerformanceOut)
def update_team_performance(
    ident: int,
    payload: TeamPerformanceUpdate,
    db: Session = Depends(get_db),
    user: User = Depends(require_perm("dashboard.team_performance.modify")),
):
    cid = _company_id(user)
    obj = _get_or_404(db, TeamPerformance, ident, "Performance et productivite equipes")
    if obj.company_id != cid:
        raise HTTPException(403, "Acces refuse.")
    _apply(payload.model_dump(exclude_unset=True), obj)
    db.commit()
    db.refresh(obj)
    return obj


@router.delete("/team-performances/{ident}", response_model=TeamPerformanceOut)
def delete_team_performance(
    ident: int,
    db: Session = Depends(get_db),
    user: User = Depends(require_perm("dashboard.team_performance.modify")),
):
    cid = _company_id(user)
    obj = _get_or_404(db, TeamPerformance, ident, "Performance et productivite equipes")
    if obj.company_id != cid:
        raise HTTPException(403, "Acces refuse.")
    obj.is_active = False
    db.commit()
    db.refresh(obj)
    return obj


# ─── Synthese financiere consolidee ─────────────────────────────────────────────────

@router.get("/financial-summaries", response_model=List[FinancialSummaryOut])
def list_financial_summary(db: Session = Depends(get_db),
    user: User = Depends(require_perm("dashboard.financial_summary.read")),
):
    cid = _company_id(user)
    return _scoped_list(db, FinancialSummary, cid)


@router.post("/financial-summaries", response_model=FinancialSummaryOut, status_code=201)
def create_financial_summary(
    payload: FinancialSummaryCreate,
    db: Session = Depends(get_db),
    user: User = Depends(require_perm("dashboard.financial_summary.create")),
):
    cid = _company_id(user)
    data = payload.model_dump(exclude_unset=True)
    _check_unique(db, FinancialSummary, "reference", data.get("reference"), "reference", cid)
    obj = FinancialSummary(company_id=cid)
    _apply(data, obj)
    db.add(obj)
    db.commit()
    db.refresh(obj)
    return obj


@router.put("/financial-summaries/{ident}", response_model=FinancialSummaryOut)
def update_financial_summary(
    ident: int,
    payload: FinancialSummaryUpdate,
    db: Session = Depends(get_db),
    user: User = Depends(require_perm("dashboard.financial_summary.modify")),
):
    cid = _company_id(user)
    obj = _get_or_404(db, FinancialSummary, ident, "Synthese financiere consolidee")
    if obj.company_id != cid:
        raise HTTPException(403, "Acces refuse.")
    _apply(payload.model_dump(exclude_unset=True), obj)
    db.commit()
    db.refresh(obj)
    return obj


@router.delete("/financial-summaries/{ident}", response_model=FinancialSummaryOut)
def delete_financial_summary(
    ident: int,
    db: Session = Depends(get_db),
    user: User = Depends(require_perm("dashboard.financial_summary.modify")),
):
    cid = _company_id(user)
    obj = _get_or_404(db, FinancialSummary, ident, "Synthese financiere consolidee")
    if obj.company_id != cid:
        raise HTTPException(403, "Acces refuse.")
    obj.is_active = False
    db.commit()
    db.refresh(obj)
    return obj


# ─── Alertes operationnelles croisees ─────────────────────────────────────────────────

@router.get("/operational-alerts", response_model=List[OperationalAlertOut])
def list_operational_alerts(statut: Optional[str] = None, db: Session = Depends(get_db),
    user: User = Depends(require_perm("dashboard.operational_alerts.read")),
):
    cid = _company_id(user)
    return _scoped_list(db, OperationalAlert, cid, {"statut": statut})


@router.post("/operational-alerts", response_model=OperationalAlertOut, status_code=201)
def create_operational_alerts(
    payload: OperationalAlertCreate,
    db: Session = Depends(get_db),
    user: User = Depends(require_perm("dashboard.operational_alerts.create")),
):
    cid = _company_id(user)
    data = payload.model_dump(exclude_unset=True)
    _check_unique(db, OperationalAlert, "reference", data.get("reference"), "reference", cid)
    obj = OperationalAlert(company_id=cid)
    _apply(data, obj)
    db.add(obj)
    db.commit()
    db.refresh(obj)
    return obj


@router.put("/operational-alerts/{ident}", response_model=OperationalAlertOut)
def update_operational_alerts(
    ident: int,
    payload: OperationalAlertUpdate,
    db: Session = Depends(get_db),
    user: User = Depends(require_perm("dashboard.operational_alerts.modify")),
):
    cid = _company_id(user)
    obj = _get_or_404(db, OperationalAlert, ident, "Alertes operationnelles croisees")
    if obj.company_id != cid:
        raise HTTPException(403, "Acces refuse.")
    _apply(payload.model_dump(exclude_unset=True), obj)
    db.commit()
    db.refresh(obj)
    return obj


@router.delete("/operational-alerts/{ident}", response_model=OperationalAlertOut)
def delete_operational_alerts(
    ident: int,
    db: Session = Depends(get_db),
    user: User = Depends(require_perm("dashboard.operational_alerts.modify")),
):
    cid = _company_id(user)
    obj = _get_or_404(db, OperationalAlert, ident, "Alertes operationnelles croisees")
    if obj.company_id != cid:
        raise HTTPException(403, "Acces refuse.")
    obj.is_active = False
    db.commit()
    db.refresh(obj)
    return obj


# ─── Centre documents recents / partages ─────────────────────────────────────────────────

@router.get("/recent-documents", response_model=List[RecentDocumentOut])
def list_document_center(db: Session = Depends(get_db),
    user: User = Depends(require_perm("dashboard.document_center.read")),
):
    cid = _company_id(user)
    return _scoped_list(db, RecentDocument, cid)


@router.post("/recent-documents", response_model=RecentDocumentOut, status_code=201)
def create_document_center(
    payload: RecentDocumentCreate,
    db: Session = Depends(get_db),
    user: User = Depends(require_perm("dashboard.document_center.create")),
):
    cid = _company_id(user)
    data = payload.model_dump(exclude_unset=True)
    _check_unique(db, RecentDocument, "reference", data.get("reference"), "reference", cid)
    obj = RecentDocument(company_id=cid)
    _apply(data, obj)
    db.add(obj)
    db.commit()
    db.refresh(obj)
    return obj


@router.put("/recent-documents/{ident}", response_model=RecentDocumentOut)
def update_document_center(
    ident: int,
    payload: RecentDocumentUpdate,
    db: Session = Depends(get_db),
    user: User = Depends(require_perm("dashboard.document_center.modify")),
):
    cid = _company_id(user)
    obj = _get_or_404(db, RecentDocument, ident, "Centre documents recents / partages")
    if obj.company_id != cid:
        raise HTTPException(403, "Acces refuse.")
    _apply(payload.model_dump(exclude_unset=True), obj)
    db.commit()
    db.refresh(obj)
    return obj


@router.delete("/recent-documents/{ident}", response_model=RecentDocumentOut)
def delete_document_center(
    ident: int,
    db: Session = Depends(get_db),
    user: User = Depends(require_perm("dashboard.document_center.modify")),
):
    cid = _company_id(user)
    obj = _get_or_404(db, RecentDocument, ident, "Centre documents recents / partages")
    if obj.company_id != cid:
        raise HTTPException(403, "Acces refuse.")
    obj.is_active = False
    db.commit()
    db.refresh(obj)
    return obj


# ─── Agenda consolide multi-module ─────────────────────────────────────────────────

@router.get("/unified-agenda", response_model=List[UnifiedAgendaOut])
def list_calendar_agenda(db: Session = Depends(get_db),
    user: User = Depends(require_perm("dashboard.calendar_agenda.read")),
):
    cid = _company_id(user)
    return _scoped_list(db, UnifiedAgenda, cid)


@router.post("/unified-agenda", response_model=UnifiedAgendaOut, status_code=201)
def create_calendar_agenda(
    payload: UnifiedAgendaCreate,
    db: Session = Depends(get_db),
    user: User = Depends(require_perm("dashboard.calendar_agenda.create")),
):
    cid = _company_id(user)
    data = payload.model_dump(exclude_unset=True)
    _check_unique(db, UnifiedAgenda, "reference", data.get("reference"), "reference", cid)
    obj = UnifiedAgenda(company_id=cid)
    _apply(data, obj)
    db.add(obj)
    db.commit()
    db.refresh(obj)
    return obj


@router.put("/unified-agenda/{ident}", response_model=UnifiedAgendaOut)
def update_calendar_agenda(
    ident: int,
    payload: UnifiedAgendaUpdate,
    db: Session = Depends(get_db),
    user: User = Depends(require_perm("dashboard.calendar_agenda.modify")),
):
    cid = _company_id(user)
    obj = _get_or_404(db, UnifiedAgenda, ident, "Agenda consolide multi-module")
    if obj.company_id != cid:
        raise HTTPException(403, "Acces refuse.")
    _apply(payload.model_dump(exclude_unset=True), obj)
    db.commit()
    db.refresh(obj)
    return obj


@router.delete("/unified-agenda/{ident}", response_model=UnifiedAgendaOut)
def delete_calendar_agenda(
    ident: int,
    db: Session = Depends(get_db),
    user: User = Depends(require_perm("dashboard.calendar_agenda.modify")),
):
    cid = _company_id(user)
    obj = _get_or_404(db, UnifiedAgenda, ident, "Agenda consolide multi-module")
    if obj.company_id != cid:
        raise HTTPException(403, "Acces refuse.")
    obj.is_active = False
    db.commit()
    db.refresh(obj)
    return obj


# ─── Etat integrations externes ─────────────────────────────────────────────────

@router.get("/integration-statuses", response_model=List[IntegrationStatusOut])
def list_integration_status(db: Session = Depends(get_db),
    user: User = Depends(require_perm("dashboard.integration_status.read")),
):
    cid = _company_id(user)
    return _scoped_list(db, IntegrationStatus, cid)


@router.post("/integration-statuses", response_model=IntegrationStatusOut, status_code=201)
def create_integration_status(
    payload: IntegrationStatusCreate,
    db: Session = Depends(get_db),
    user: User = Depends(require_perm("dashboard.integration_status.create")),
):
    cid = _company_id(user)
    data = payload.model_dump(exclude_unset=True)
    _check_unique(db, IntegrationStatus, "reference", data.get("reference"), "reference", cid)
    obj = IntegrationStatus(company_id=cid)
    _apply(data, obj)
    db.add(obj)
    db.commit()
    db.refresh(obj)
    return obj


@router.put("/integration-statuses/{ident}", response_model=IntegrationStatusOut)
def update_integration_status(
    ident: int,
    payload: IntegrationStatusUpdate,
    db: Session = Depends(get_db),
    user: User = Depends(require_perm("dashboard.integration_status.modify")),
):
    cid = _company_id(user)
    obj = _get_or_404(db, IntegrationStatus, ident, "Etat integrations externes")
    if obj.company_id != cid:
        raise HTTPException(403, "Acces refuse.")
    _apply(payload.model_dump(exclude_unset=True), obj)
    db.commit()
    db.refresh(obj)
    return obj


@router.delete("/integration-statuses/{ident}", response_model=IntegrationStatusOut)
def delete_integration_status(
    ident: int,
    db: Session = Depends(get_db),
    user: User = Depends(require_perm("dashboard.integration_status.modify")),
):
    cid = _company_id(user)
    obj = _get_or_404(db, IntegrationStatus, ident, "Etat integrations externes")
    if obj.company_id != cid:
        raise HTTPException(403, "Acces refuse.")
    obj.is_active = False
    db.commit()
    db.refresh(obj)
    return obj

