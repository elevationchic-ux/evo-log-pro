"""Routeur CRUD genere pour reports-bi (expansion)."""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import Optional, List

from app.core.database import get_db
from app.core.permissions import require_perm
from app.models.user import User
from app.models.reports_c_deep import (
    RptcScheduledReport,
    RptcReportTemplate,
    RptcDataExport,
    RptcAdHocQuery,
    RptcOlapCube,
)
from app.schemas.reports_c_deep import (
    RptcScheduledReportCreate, RptcScheduledReportUpdate, RptcScheduledReportOut,
    RptcReportTemplateCreate, RptcReportTemplateUpdate, RptcReportTemplateOut,
    RptcDataExportCreate, RptcDataExportUpdate, RptcDataExportOut,
    RptcAdHocQueryCreate, RptcAdHocQueryUpdate, RptcAdHocQueryOut,
    RptcOlapCubeCreate, RptcOlapCubeUpdate, RptcOlapCubeOut,
)

router = APIRouter(tags=["reports-bi (expansion)"])


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

@router.get("/nomenclatures", summary="Vocabulaire metier reports-bi")
def nomenclatures(user: User = Depends(require_perm("reports.nomenclature.read"))):
    from app.models import reports_c_deep as _md
    import enum as _pyenum
    out = {}
    for name in dir(_md):
        obj = getattr(_md, name)
        if isinstance(obj, type) and issubclass(obj, _pyenum.Enum) and obj is not _pyenum.Enum:
            out[name.lower()] = [{"code": m.name, "valeur": m.value} for m in obj]
    return out


# ─── Rapports planifies ─────────────────────────────────────────────────

@router.get("/rptc-scheduled-reports", response_model=List[RptcScheduledReportOut])
def list_scheduled_report(statut: Optional[str] = None, db: Session = Depends(get_db),
    user: User = Depends(require_perm("reports.scheduled_report.read")),
):
    cid = _company_id(user)
    return _scoped_list(db, RptcScheduledReport, cid, {"statut": statut})


@router.post("/rptc-scheduled-reports", response_model=RptcScheduledReportOut, status_code=201)
def create_scheduled_report(
    payload: RptcScheduledReportCreate,
    db: Session = Depends(get_db),
    user: User = Depends(require_perm("reports.scheduled_report.create")),
):
    cid = _company_id(user)
    data = payload.model_dump(exclude_unset=True)
    _check_unique(db, RptcScheduledReport, "reference", data.get("reference"), "reference", cid)
    obj = RptcScheduledReport(company_id=cid)
    _apply(data, obj)
    db.add(obj)
    db.commit()
    db.refresh(obj)
    return obj


@router.put("/rptc-scheduled-reports/{ident}", response_model=RptcScheduledReportOut)
def update_scheduled_report(
    ident: int,
    payload: RptcScheduledReportUpdate,
    db: Session = Depends(get_db),
    user: User = Depends(require_perm("reports.scheduled_report.modify")),
):
    cid = _company_id(user)
    obj = _get_or_404(db, RptcScheduledReport, ident, "Rapports planifies")
    if obj.company_id != cid:
        raise HTTPException(403, "Acces refuse.")
    _apply(payload.model_dump(exclude_unset=True), obj)
    db.commit()
    db.refresh(obj)
    return obj


@router.delete("/rptc-scheduled-reports/{ident}", response_model=RptcScheduledReportOut)
def delete_scheduled_report(
    ident: int,
    db: Session = Depends(get_db),
    user: User = Depends(require_perm("reports.scheduled_report.modify")),
):
    cid = _company_id(user)
    obj = _get_or_404(db, RptcScheduledReport, ident, "Rapports planifies")
    if obj.company_id != cid:
        raise HTTPException(403, "Acces refuse.")
    obj.is_active = False
    db.commit()
    db.refresh(obj)
    return obj


# ─── Modeles de rapport ─────────────────────────────────────────────────

@router.get("/rptc-report-templates", response_model=List[RptcReportTemplateOut])
def list_report_template(statut: Optional[str] = None, db: Session = Depends(get_db),
    user: User = Depends(require_perm("reports.report_template.read")),
):
    cid = _company_id(user)
    return _scoped_list(db, RptcReportTemplate, cid, {"statut": statut})


@router.post("/rptc-report-templates", response_model=RptcReportTemplateOut, status_code=201)
def create_report_template(
    payload: RptcReportTemplateCreate,
    db: Session = Depends(get_db),
    user: User = Depends(require_perm("reports.report_template.create")),
):
    cid = _company_id(user)
    data = payload.model_dump(exclude_unset=True)
    _check_unique(db, RptcReportTemplate, "reference", data.get("reference"), "reference", cid)
    obj = RptcReportTemplate(company_id=cid)
    _apply(data, obj)
    db.add(obj)
    db.commit()
    db.refresh(obj)
    return obj


@router.put("/rptc-report-templates/{ident}", response_model=RptcReportTemplateOut)
def update_report_template(
    ident: int,
    payload: RptcReportTemplateUpdate,
    db: Session = Depends(get_db),
    user: User = Depends(require_perm("reports.report_template.modify")),
):
    cid = _company_id(user)
    obj = _get_or_404(db, RptcReportTemplate, ident, "Modeles de rapport")
    if obj.company_id != cid:
        raise HTTPException(403, "Acces refuse.")
    _apply(payload.model_dump(exclude_unset=True), obj)
    db.commit()
    db.refresh(obj)
    return obj


@router.delete("/rptc-report-templates/{ident}", response_model=RptcReportTemplateOut)
def delete_report_template(
    ident: int,
    db: Session = Depends(get_db),
    user: User = Depends(require_perm("reports.report_template.modify")),
):
    cid = _company_id(user)
    obj = _get_or_404(db, RptcReportTemplate, ident, "Modeles de rapport")
    if obj.company_id != cid:
        raise HTTPException(403, "Acces refuse.")
    obj.is_active = False
    db.commit()
    db.refresh(obj)
    return obj


# ─── Extractions de donnees ─────────────────────────────────────────────────

@router.get("/rptc-data-exports", response_model=List[RptcDataExportOut])
def list_data_export(statut: Optional[str] = None, db: Session = Depends(get_db),
    user: User = Depends(require_perm("reports.data_export.read")),
):
    cid = _company_id(user)
    return _scoped_list(db, RptcDataExport, cid, {"statut": statut})


@router.post("/rptc-data-exports", response_model=RptcDataExportOut, status_code=201)
def create_data_export(
    payload: RptcDataExportCreate,
    db: Session = Depends(get_db),
    user: User = Depends(require_perm("reports.data_export.create")),
):
    cid = _company_id(user)
    data = payload.model_dump(exclude_unset=True)
    _check_unique(db, RptcDataExport, "reference", data.get("reference"), "reference", cid)
    obj = RptcDataExport(company_id=cid)
    _apply(data, obj)
    db.add(obj)
    db.commit()
    db.refresh(obj)
    return obj


@router.put("/rptc-data-exports/{ident}", response_model=RptcDataExportOut)
def update_data_export(
    ident: int,
    payload: RptcDataExportUpdate,
    db: Session = Depends(get_db),
    user: User = Depends(require_perm("reports.data_export.modify")),
):
    cid = _company_id(user)
    obj = _get_or_404(db, RptcDataExport, ident, "Extractions de donnees")
    if obj.company_id != cid:
        raise HTTPException(403, "Acces refuse.")
    _apply(payload.model_dump(exclude_unset=True), obj)
    db.commit()
    db.refresh(obj)
    return obj


@router.delete("/rptc-data-exports/{ident}", response_model=RptcDataExportOut)
def delete_data_export(
    ident: int,
    db: Session = Depends(get_db),
    user: User = Depends(require_perm("reports.data_export.modify")),
):
    cid = _company_id(user)
    obj = _get_or_404(db, RptcDataExport, ident, "Extractions de donnees")
    if obj.company_id != cid:
        raise HTTPException(403, "Acces refuse.")
    obj.is_active = False
    db.commit()
    db.refresh(obj)
    return obj


# ─── Requetes ad hoc ─────────────────────────────────────────────────

@router.get("/rptc-ad-hoc-queries", response_model=List[RptcAdHocQueryOut])
def list_ad_hoc_query(statut: Optional[str] = None, db: Session = Depends(get_db),
    user: User = Depends(require_perm("reports.ad_hoc_query.read")),
):
    cid = _company_id(user)
    return _scoped_list(db, RptcAdHocQuery, cid, {"statut": statut})


@router.post("/rptc-ad-hoc-queries", response_model=RptcAdHocQueryOut, status_code=201)
def create_ad_hoc_query(
    payload: RptcAdHocQueryCreate,
    db: Session = Depends(get_db),
    user: User = Depends(require_perm("reports.ad_hoc_query.create")),
):
    cid = _company_id(user)
    data = payload.model_dump(exclude_unset=True)
    _check_unique(db, RptcAdHocQuery, "reference", data.get("reference"), "reference", cid)
    obj = RptcAdHocQuery(company_id=cid)
    _apply(data, obj)
    db.add(obj)
    db.commit()
    db.refresh(obj)
    return obj


@router.put("/rptc-ad-hoc-queries/{ident}", response_model=RptcAdHocQueryOut)
def update_ad_hoc_query(
    ident: int,
    payload: RptcAdHocQueryUpdate,
    db: Session = Depends(get_db),
    user: User = Depends(require_perm("reports.ad_hoc_query.modify")),
):
    cid = _company_id(user)
    obj = _get_or_404(db, RptcAdHocQuery, ident, "Requetes ad hoc")
    if obj.company_id != cid:
        raise HTTPException(403, "Acces refuse.")
    _apply(payload.model_dump(exclude_unset=True), obj)
    db.commit()
    db.refresh(obj)
    return obj


@router.delete("/rptc-ad-hoc-queries/{ident}", response_model=RptcAdHocQueryOut)
def delete_ad_hoc_query(
    ident: int,
    db: Session = Depends(get_db),
    user: User = Depends(require_perm("reports.ad_hoc_query.modify")),
):
    cid = _company_id(user)
    obj = _get_or_404(db, RptcAdHocQuery, ident, "Requetes ad hoc")
    if obj.company_id != cid:
        raise HTTPException(403, "Acces refuse.")
    obj.is_active = False
    db.commit()
    db.refresh(obj)
    return obj


# ─── Cubes analytiques ─────────────────────────────────────────────────

@router.get("/rptc-olap-cubes", response_model=List[RptcOlapCubeOut])
def list_olap_cube(statut: Optional[str] = None, db: Session = Depends(get_db),
    user: User = Depends(require_perm("reports.olap_cube.read")),
):
    cid = _company_id(user)
    return _scoped_list(db, RptcOlapCube, cid, {"statut": statut})


@router.post("/rptc-olap-cubes", response_model=RptcOlapCubeOut, status_code=201)
def create_olap_cube(
    payload: RptcOlapCubeCreate,
    db: Session = Depends(get_db),
    user: User = Depends(require_perm("reports.olap_cube.create")),
):
    cid = _company_id(user)
    data = payload.model_dump(exclude_unset=True)
    _check_unique(db, RptcOlapCube, "reference", data.get("reference"), "reference", cid)
    obj = RptcOlapCube(company_id=cid)
    _apply(data, obj)
    db.add(obj)
    db.commit()
    db.refresh(obj)
    return obj


@router.put("/rptc-olap-cubes/{ident}", response_model=RptcOlapCubeOut)
def update_olap_cube(
    ident: int,
    payload: RptcOlapCubeUpdate,
    db: Session = Depends(get_db),
    user: User = Depends(require_perm("reports.olap_cube.modify")),
):
    cid = _company_id(user)
    obj = _get_or_404(db, RptcOlapCube, ident, "Cubes analytiques")
    if obj.company_id != cid:
        raise HTTPException(403, "Acces refuse.")
    _apply(payload.model_dump(exclude_unset=True), obj)
    db.commit()
    db.refresh(obj)
    return obj


@router.delete("/rptc-olap-cubes/{ident}", response_model=RptcOlapCubeOut)
def delete_olap_cube(
    ident: int,
    db: Session = Depends(get_db),
    user: User = Depends(require_perm("reports.olap_cube.modify")),
):
    cid = _company_id(user)
    obj = _get_or_404(db, RptcOlapCube, ident, "Cubes analytiques")
    if obj.company_id != cid:
        raise HTTPException(403, "Acces refuse.")
    obj.is_active = False
    db.commit()
    db.refresh(obj)
    return obj

