"""Routeur CRUD genere pour reports-bi (expansion)."""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import Optional, List

from app.core.database import get_db
from app.core.permissions import require_perm
from app.models.user import User
from app.models.reports_deep import (
    WarehouseTable,
    Scorecard,
    IndustryBenchmark,
    PredictiveModel,
    CustomDashboard,
    ReportExport,
    KpiDefinition,
    DrillPath,
    CohortAnalysis,
    AnomalyRecord,
    RegulatoryReport,
)
from app.schemas.reports_deep import (
    WarehouseTableCreate, WarehouseTableUpdate, WarehouseTableOut,
    ScorecardCreate, ScorecardUpdate, ScorecardOut,
    IndustryBenchmarkCreate, IndustryBenchmarkUpdate, IndustryBenchmarkOut,
    PredictiveModelCreate, PredictiveModelUpdate, PredictiveModelOut,
    CustomDashboardCreate, CustomDashboardUpdate, CustomDashboardOut,
    ReportExportCreate, ReportExportUpdate, ReportExportOut,
    KpiDefinitionCreate, KpiDefinitionUpdate, KpiDefinitionOut,
    DrillPathCreate, DrillPathUpdate, DrillPathOut,
    CohortAnalysisCreate, CohortAnalysisUpdate, CohortAnalysisOut,
    AnomalyRecordCreate, AnomalyRecordUpdate, AnomalyRecordOut,
    RegulatoryReportCreate, RegulatoryReportUpdate, RegulatoryReportOut,
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
    from app.models import reports_deep as _md
    import enum as _pyenum
    out = {}
    for name in dir(_md):
        obj = getattr(_md, name)
        if isinstance(obj, type) and issubclass(obj, _pyenum.Enum) and obj is not _pyenum.Enum:
            out[name.lower()] = [{"code": m.name, "valeur": m.value} for m in obj]
    return out


# ─── Entrepot de donnees ─────────────────────────────────────────────────

@router.get("/warehouse-tables", response_model=List[WarehouseTableOut])
def list_data_warehouse(statut: Optional[str] = None, db: Session = Depends(get_db),
    user: User = Depends(require_perm("reports.data_warehouse.read")),
):
    cid = _company_id(user)
    return _scoped_list(db, WarehouseTable, cid, {"statut": statut})


@router.post("/warehouse-tables", response_model=WarehouseTableOut, status_code=201)
def create_data_warehouse(
    payload: WarehouseTableCreate,
    db: Session = Depends(get_db),
    user: User = Depends(require_perm("reports.data_warehouse.create")),
):
    cid = _company_id(user)
    data = payload.model_dump(exclude_unset=True)
    _check_unique(db, WarehouseTable, "code_table", data.get("code_table"), "code_table", cid)
    obj = WarehouseTable(company_id=cid)
    _apply(data, obj)
    db.add(obj)
    db.commit()
    db.refresh(obj)
    return obj


@router.put("/warehouse-tables/{ident}", response_model=WarehouseTableOut)
def update_data_warehouse(
    ident: int,
    payload: WarehouseTableUpdate,
    db: Session = Depends(get_db),
    user: User = Depends(require_perm("reports.data_warehouse.modify")),
):
    cid = _company_id(user)
    obj = _get_or_404(db, WarehouseTable, ident, "Entrepot de donnees")
    if obj.company_id != cid:
        raise HTTPException(403, "Acces refuse.")
    _apply(payload.model_dump(exclude_unset=True), obj)
    db.commit()
    db.refresh(obj)
    return obj


@router.delete("/warehouse-tables/{ident}", response_model=WarehouseTableOut)
def delete_data_warehouse(
    ident: int,
    db: Session = Depends(get_db),
    user: User = Depends(require_perm("reports.data_warehouse.modify")),
):
    cid = _company_id(user)
    obj = _get_or_404(db, WarehouseTable, ident, "Entrepot de donnees")
    if obj.company_id != cid:
        raise HTTPException(403, "Acces refuse.")
    obj.is_active = False
    db.commit()
    db.refresh(obj)
    return obj


# ─── Tableaux de score par pole ─────────────────────────────────────────────────

@router.get("/scorecards", response_model=List[ScorecardOut])
def list_scorecard(db: Session = Depends(get_db),
    user: User = Depends(require_perm("reports.scorecard.read")),
):
    cid = _company_id(user)
    return _scoped_list(db, Scorecard, cid)


@router.post("/scorecards", response_model=ScorecardOut, status_code=201)
def create_scorecard(
    payload: ScorecardCreate,
    db: Session = Depends(get_db),
    user: User = Depends(require_perm("reports.scorecard.create")),
):
    cid = _company_id(user)
    data = payload.model_dump(exclude_unset=True)
    _check_unique(db, Scorecard, "reference", data.get("reference"), "reference", cid)
    obj = Scorecard(company_id=cid)
    _apply(data, obj)
    db.add(obj)
    db.commit()
    db.refresh(obj)
    return obj


@router.put("/scorecards/{ident}", response_model=ScorecardOut)
def update_scorecard(
    ident: int,
    payload: ScorecardUpdate,
    db: Session = Depends(get_db),
    user: User = Depends(require_perm("reports.scorecard.modify")),
):
    cid = _company_id(user)
    obj = _get_or_404(db, Scorecard, ident, "Tableaux de score par pole")
    if obj.company_id != cid:
        raise HTTPException(403, "Acces refuse.")
    _apply(payload.model_dump(exclude_unset=True), obj)
    db.commit()
    db.refresh(obj)
    return obj


@router.delete("/scorecards/{ident}", response_model=ScorecardOut)
def delete_scorecard(
    ident: int,
    db: Session = Depends(get_db),
    user: User = Depends(require_perm("reports.scorecard.modify")),
):
    cid = _company_id(user)
    obj = _get_or_404(db, Scorecard, ident, "Tableaux de score par pole")
    if obj.company_id != cid:
        raise HTTPException(403, "Acces refuse.")
    obj.is_active = False
    db.commit()
    db.refresh(obj)
    return obj


# ─── Comparaison sectorielle ports CEMAC ─────────────────────────────────────────────────

@router.get("/industry-benchmarks", response_model=List[IndustryBenchmarkOut])
def list_benchmark(db: Session = Depends(get_db),
    user: User = Depends(require_perm("reports.benchmark.read")),
):
    cid = _company_id(user)
    return _scoped_list(db, IndustryBenchmark, cid)


@router.post("/industry-benchmarks", response_model=IndustryBenchmarkOut, status_code=201)
def create_benchmark(
    payload: IndustryBenchmarkCreate,
    db: Session = Depends(get_db),
    user: User = Depends(require_perm("reports.benchmark.create")),
):
    cid = _company_id(user)
    data = payload.model_dump(exclude_unset=True)
    _check_unique(db, IndustryBenchmark, "reference", data.get("reference"), "reference", cid)
    obj = IndustryBenchmark(company_id=cid)
    _apply(data, obj)
    db.add(obj)
    db.commit()
    db.refresh(obj)
    return obj


@router.put("/industry-benchmarks/{ident}", response_model=IndustryBenchmarkOut)
def update_benchmark(
    ident: int,
    payload: IndustryBenchmarkUpdate,
    db: Session = Depends(get_db),
    user: User = Depends(require_perm("reports.benchmark.modify")),
):
    cid = _company_id(user)
    obj = _get_or_404(db, IndustryBenchmark, ident, "Comparaison sectorielle ports CEMAC")
    if obj.company_id != cid:
        raise HTTPException(403, "Acces refuse.")
    _apply(payload.model_dump(exclude_unset=True), obj)
    db.commit()
    db.refresh(obj)
    return obj


@router.delete("/industry-benchmarks/{ident}", response_model=IndustryBenchmarkOut)
def delete_benchmark(
    ident: int,
    db: Session = Depends(get_db),
    user: User = Depends(require_perm("reports.benchmark.modify")),
):
    cid = _company_id(user)
    obj = _get_or_404(db, IndustryBenchmark, ident, "Comparaison sectorielle ports CEMAC")
    if obj.company_id != cid:
        raise HTTPException(403, "Acces refuse.")
    obj.is_active = False
    db.commit()
    db.refresh(obj)
    return obj


# ─── Analyses predictives ─────────────────────────────────────────────────

@router.get("/predictive-models", response_model=List[PredictiveModelOut])
def list_predictive_analytics(statut: Optional[str] = None, db: Session = Depends(get_db),
    user: User = Depends(require_perm("reports.predictive_analytics.read")),
):
    cid = _company_id(user)
    return _scoped_list(db, PredictiveModel, cid, {"statut": statut})


@router.post("/predictive-models", response_model=PredictiveModelOut, status_code=201)
def create_predictive_analytics(
    payload: PredictiveModelCreate,
    db: Session = Depends(get_db),
    user: User = Depends(require_perm("reports.predictive_analytics.create")),
):
    cid = _company_id(user)
    data = payload.model_dump(exclude_unset=True)
    _check_unique(db, PredictiveModel, "reference", data.get("reference"), "reference", cid)
    obj = PredictiveModel(company_id=cid)
    _apply(data, obj)
    db.add(obj)
    db.commit()
    db.refresh(obj)
    return obj


@router.put("/predictive-models/{ident}", response_model=PredictiveModelOut)
def update_predictive_analytics(
    ident: int,
    payload: PredictiveModelUpdate,
    db: Session = Depends(get_db),
    user: User = Depends(require_perm("reports.predictive_analytics.modify")),
):
    cid = _company_id(user)
    obj = _get_or_404(db, PredictiveModel, ident, "Analyses predictives")
    if obj.company_id != cid:
        raise HTTPException(403, "Acces refuse.")
    _apply(payload.model_dump(exclude_unset=True), obj)
    db.commit()
    db.refresh(obj)
    return obj


@router.delete("/predictive-models/{ident}", response_model=PredictiveModelOut)
def delete_predictive_analytics(
    ident: int,
    db: Session = Depends(get_db),
    user: User = Depends(require_perm("reports.predictive_analytics.modify")),
):
    cid = _company_id(user)
    obj = _get_or_404(db, PredictiveModel, ident, "Analyses predictives")
    if obj.company_id != cid:
        raise HTTPException(403, "Acces refuse.")
    obj.is_active = False
    db.commit()
    db.refresh(obj)
    return obj


# ─── Tableaux de bord personnalises ─────────────────────────────────────────────────

@router.get("/custom-dashboards", response_model=List[CustomDashboardOut])
def list_custom_dashboard(db: Session = Depends(get_db),
    user: User = Depends(require_perm("reports.custom_dashboard.read")),
):
    cid = _company_id(user)
    return _scoped_list(db, CustomDashboard, cid)


@router.post("/custom-dashboards", response_model=CustomDashboardOut, status_code=201)
def create_custom_dashboard(
    payload: CustomDashboardCreate,
    db: Session = Depends(get_db),
    user: User = Depends(require_perm("reports.custom_dashboard.create")),
):
    cid = _company_id(user)
    data = payload.model_dump(exclude_unset=True)
    _check_unique(db, CustomDashboard, "reference", data.get("reference"), "reference", cid)
    obj = CustomDashboard(company_id=cid)
    _apply(data, obj)
    db.add(obj)
    db.commit()
    db.refresh(obj)
    return obj


@router.put("/custom-dashboards/{ident}", response_model=CustomDashboardOut)
def update_custom_dashboard(
    ident: int,
    payload: CustomDashboardUpdate,
    db: Session = Depends(get_db),
    user: User = Depends(require_perm("reports.custom_dashboard.modify")),
):
    cid = _company_id(user)
    obj = _get_or_404(db, CustomDashboard, ident, "Tableaux de bord personnalises")
    if obj.company_id != cid:
        raise HTTPException(403, "Acces refuse.")
    _apply(payload.model_dump(exclude_unset=True), obj)
    db.commit()
    db.refresh(obj)
    return obj


@router.delete("/custom-dashboards/{ident}", response_model=CustomDashboardOut)
def delete_custom_dashboard(
    ident: int,
    db: Session = Depends(get_db),
    user: User = Depends(require_perm("reports.custom_dashboard.modify")),
):
    cid = _company_id(user)
    obj = _get_or_404(db, CustomDashboard, ident, "Tableaux de bord personnalises")
    if obj.company_id != cid:
        raise HTTPException(403, "Acces refuse.")
    obj.is_active = False
    db.commit()
    db.refresh(obj)
    return obj


# ─── Exports planifies / abonnes ─────────────────────────────────────────────────

@router.get("/report-exports", response_model=List[ReportExportOut])
def list_export_reports(statut: Optional[str] = None, db: Session = Depends(get_db),
    user: User = Depends(require_perm("reports.export_reports.read")),
):
    cid = _company_id(user)
    return _scoped_list(db, ReportExport, cid, {"statut": statut})


@router.post("/report-exports", response_model=ReportExportOut, status_code=201)
def create_export_reports(
    payload: ReportExportCreate,
    db: Session = Depends(get_db),
    user: User = Depends(require_perm("reports.export_reports.create")),
):
    cid = _company_id(user)
    data = payload.model_dump(exclude_unset=True)
    _check_unique(db, ReportExport, "reference", data.get("reference"), "reference", cid)
    obj = ReportExport(company_id=cid)
    _apply(data, obj)
    db.add(obj)
    db.commit()
    db.refresh(obj)
    return obj


@router.put("/report-exports/{ident}", response_model=ReportExportOut)
def update_export_reports(
    ident: int,
    payload: ReportExportUpdate,
    db: Session = Depends(get_db),
    user: User = Depends(require_perm("reports.export_reports.modify")),
):
    cid = _company_id(user)
    obj = _get_or_404(db, ReportExport, ident, "Exports planifies / abonnes")
    if obj.company_id != cid:
        raise HTTPException(403, "Acces refuse.")
    _apply(payload.model_dump(exclude_unset=True), obj)
    db.commit()
    db.refresh(obj)
    return obj


@router.delete("/report-exports/{ident}", response_model=ReportExportOut)
def delete_export_reports(
    ident: int,
    db: Session = Depends(get_db),
    user: User = Depends(require_perm("reports.export_reports.modify")),
):
    cid = _company_id(user)
    obj = _get_or_404(db, ReportExport, ident, "Exports planifies / abonnes")
    if obj.company_id != cid:
        raise HTTPException(403, "Acces refuse.")
    obj.is_active = False
    db.commit()
    db.refresh(obj)
    return obj


# ─── Catalogue et definitions KPI ─────────────────────────────────────────────────

@router.get("/kpi-definitions", response_model=List[KpiDefinitionOut])
def list_kpi_definition(db: Session = Depends(get_db),
    user: User = Depends(require_perm("reports.kpi_definition.read")),
):
    cid = _company_id(user)
    return _scoped_list(db, KpiDefinition, cid)


@router.post("/kpi-definitions", response_model=KpiDefinitionOut, status_code=201)
def create_kpi_definition(
    payload: KpiDefinitionCreate,
    db: Session = Depends(get_db),
    user: User = Depends(require_perm("reports.kpi_definition.create")),
):
    cid = _company_id(user)
    data = payload.model_dump(exclude_unset=True)
    _check_unique(db, KpiDefinition, "code_kpi", data.get("code_kpi"), "code_kpi", cid)
    obj = KpiDefinition(company_id=cid)
    _apply(data, obj)
    db.add(obj)
    db.commit()
    db.refresh(obj)
    return obj


@router.put("/kpi-definitions/{ident}", response_model=KpiDefinitionOut)
def update_kpi_definition(
    ident: int,
    payload: KpiDefinitionUpdate,
    db: Session = Depends(get_db),
    user: User = Depends(require_perm("reports.kpi_definition.modify")),
):
    cid = _company_id(user)
    obj = _get_or_404(db, KpiDefinition, ident, "Catalogue et definitions KPI")
    if obj.company_id != cid:
        raise HTTPException(403, "Acces refuse.")
    _apply(payload.model_dump(exclude_unset=True), obj)
    db.commit()
    db.refresh(obj)
    return obj


@router.delete("/kpi-definitions/{ident}", response_model=KpiDefinitionOut)
def delete_kpi_definition(
    ident: int,
    db: Session = Depends(get_db),
    user: User = Depends(require_perm("reports.kpi_definition.modify")),
):
    cid = _company_id(user)
    obj = _get_or_404(db, KpiDefinition, ident, "Catalogue et definitions KPI")
    if obj.company_id != cid:
        raise HTTPException(403, "Acces refuse.")
    obj.is_active = False
    db.commit()
    db.refresh(obj)
    return obj


# ─── Explorations en cascade ─────────────────────────────────────────────────

@router.get("/drill-paths", response_model=List[DrillPathOut])
def list_drill_down(db: Session = Depends(get_db),
    user: User = Depends(require_perm("reports.drill_down.read")),
):
    cid = _company_id(user)
    return _scoped_list(db, DrillPath, cid)


@router.post("/drill-paths", response_model=DrillPathOut, status_code=201)
def create_drill_down(
    payload: DrillPathCreate,
    db: Session = Depends(get_db),
    user: User = Depends(require_perm("reports.drill_down.create")),
):
    cid = _company_id(user)
    data = payload.model_dump(exclude_unset=True)
    _check_unique(db, DrillPath, "reference", data.get("reference"), "reference", cid)
    obj = DrillPath(company_id=cid)
    _apply(data, obj)
    db.add(obj)
    db.commit()
    db.refresh(obj)
    return obj


@router.put("/drill-paths/{ident}", response_model=DrillPathOut)
def update_drill_down(
    ident: int,
    payload: DrillPathUpdate,
    db: Session = Depends(get_db),
    user: User = Depends(require_perm("reports.drill_down.modify")),
):
    cid = _company_id(user)
    obj = _get_or_404(db, DrillPath, ident, "Explorations en cascade")
    if obj.company_id != cid:
        raise HTTPException(403, "Acces refuse.")
    _apply(payload.model_dump(exclude_unset=True), obj)
    db.commit()
    db.refresh(obj)
    return obj


@router.delete("/drill-paths/{ident}", response_model=DrillPathOut)
def delete_drill_down(
    ident: int,
    db: Session = Depends(get_db),
    user: User = Depends(require_perm("reports.drill_down.modify")),
):
    cid = _company_id(user)
    obj = _get_or_404(db, DrillPath, ident, "Explorations en cascade")
    if obj.company_id != cid:
        raise HTTPException(403, "Acces refuse.")
    obj.is_active = False
    db.commit()
    db.refresh(obj)
    return obj


# ─── Analyse de cohortes ─────────────────────────────────────────────────

@router.get("/cohort-analyses", response_model=List[CohortAnalysisOut])
def list_cohort_analysis(db: Session = Depends(get_db),
    user: User = Depends(require_perm("reports.cohort_analysis.read")),
):
    cid = _company_id(user)
    return _scoped_list(db, CohortAnalysis, cid)


@router.post("/cohort-analyses", response_model=CohortAnalysisOut, status_code=201)
def create_cohort_analysis(
    payload: CohortAnalysisCreate,
    db: Session = Depends(get_db),
    user: User = Depends(require_perm("reports.cohort_analysis.create")),
):
    cid = _company_id(user)
    data = payload.model_dump(exclude_unset=True)
    _check_unique(db, CohortAnalysis, "reference", data.get("reference"), "reference", cid)
    obj = CohortAnalysis(company_id=cid)
    _apply(data, obj)
    db.add(obj)
    db.commit()
    db.refresh(obj)
    return obj


@router.put("/cohort-analyses/{ident}", response_model=CohortAnalysisOut)
def update_cohort_analysis(
    ident: int,
    payload: CohortAnalysisUpdate,
    db: Session = Depends(get_db),
    user: User = Depends(require_perm("reports.cohort_analysis.modify")),
):
    cid = _company_id(user)
    obj = _get_or_404(db, CohortAnalysis, ident, "Analyse de cohortes")
    if obj.company_id != cid:
        raise HTTPException(403, "Acces refuse.")
    _apply(payload.model_dump(exclude_unset=True), obj)
    db.commit()
    db.refresh(obj)
    return obj


@router.delete("/cohort-analyses/{ident}", response_model=CohortAnalysisOut)
def delete_cohort_analysis(
    ident: int,
    db: Session = Depends(get_db),
    user: User = Depends(require_perm("reports.cohort_analysis.modify")),
):
    cid = _company_id(user)
    obj = _get_or_404(db, CohortAnalysis, ident, "Analyse de cohortes")
    if obj.company_id != cid:
        raise HTTPException(403, "Acces refuse.")
    obj.is_active = False
    db.commit()
    db.refresh(obj)
    return obj


# ─── Detection anomalies / seuils ─────────────────────────────────────────────────

@router.get("/anomaly-records", response_model=List[AnomalyRecordOut])
def list_anomaly_detection(statut: Optional[str] = None, db: Session = Depends(get_db),
    user: User = Depends(require_perm("reports.anomaly_detection.read")),
):
    cid = _company_id(user)
    return _scoped_list(db, AnomalyRecord, cid, {"statut": statut})


@router.post("/anomaly-records", response_model=AnomalyRecordOut, status_code=201)
def create_anomaly_detection(
    payload: AnomalyRecordCreate,
    db: Session = Depends(get_db),
    user: User = Depends(require_perm("reports.anomaly_detection.create")),
):
    cid = _company_id(user)
    data = payload.model_dump(exclude_unset=True)
    _check_unique(db, AnomalyRecord, "reference", data.get("reference"), "reference", cid)
    obj = AnomalyRecord(company_id=cid)
    _apply(data, obj)
    db.add(obj)
    db.commit()
    db.refresh(obj)
    return obj


@router.put("/anomaly-records/{ident}", response_model=AnomalyRecordOut)
def update_anomaly_detection(
    ident: int,
    payload: AnomalyRecordUpdate,
    db: Session = Depends(get_db),
    user: User = Depends(require_perm("reports.anomaly_detection.modify")),
):
    cid = _company_id(user)
    obj = _get_or_404(db, AnomalyRecord, ident, "Detection anomalies / seuils")
    if obj.company_id != cid:
        raise HTTPException(403, "Acces refuse.")
    _apply(payload.model_dump(exclude_unset=True), obj)
    db.commit()
    db.refresh(obj)
    return obj


@router.delete("/anomaly-records/{ident}", response_model=AnomalyRecordOut)
def delete_anomaly_detection(
    ident: int,
    db: Session = Depends(get_db),
    user: User = Depends(require_perm("reports.anomaly_detection.modify")),
):
    cid = _company_id(user)
    obj = _get_or_404(db, AnomalyRecord, ident, "Detection anomalies / seuils")
    if obj.company_id != cid:
        raise HTTPException(403, "Acces refuse.")
    obj.is_active = False
    db.commit()
    db.refresh(obj)
    return obj


# ─── Rapports reglementaires (APN, douane) ─────────────────────────────────────────────────

@router.get("/regulatory-reports", response_model=List[RegulatoryReportOut])
def list_regulatory_report(statut: Optional[str] = None, db: Session = Depends(get_db),
    user: User = Depends(require_perm("reports.regulatory_report.read")),
):
    cid = _company_id(user)
    return _scoped_list(db, RegulatoryReport, cid, {"statut": statut})


@router.post("/regulatory-reports", response_model=RegulatoryReportOut, status_code=201)
def create_regulatory_report(
    payload: RegulatoryReportCreate,
    db: Session = Depends(get_db),
    user: User = Depends(require_perm("reports.regulatory_report.create")),
):
    cid = _company_id(user)
    data = payload.model_dump(exclude_unset=True)
    _check_unique(db, RegulatoryReport, "reference", data.get("reference"), "reference", cid)
    obj = RegulatoryReport(company_id=cid)
    _apply(data, obj)
    db.add(obj)
    db.commit()
    db.refresh(obj)
    return obj


@router.put("/regulatory-reports/{ident}", response_model=RegulatoryReportOut)
def update_regulatory_report(
    ident: int,
    payload: RegulatoryReportUpdate,
    db: Session = Depends(get_db),
    user: User = Depends(require_perm("reports.regulatory_report.modify")),
):
    cid = _company_id(user)
    obj = _get_or_404(db, RegulatoryReport, ident, "Rapports reglementaires (APN, douane)")
    if obj.company_id != cid:
        raise HTTPException(403, "Acces refuse.")
    _apply(payload.model_dump(exclude_unset=True), obj)
    db.commit()
    db.refresh(obj)
    return obj


@router.delete("/regulatory-reports/{ident}", response_model=RegulatoryReportOut)
def delete_regulatory_report(
    ident: int,
    db: Session = Depends(get_db),
    user: User = Depends(require_perm("reports.regulatory_report.modify")),
):
    cid = _company_id(user)
    obj = _get_or_404(db, RegulatoryReport, ident, "Rapports reglementaires (APN, douane)")
    if obj.company_id != cid:
        raise HTTPException(403, "Acces refuse.")
    obj.is_active = False
    db.commit()
    db.refresh(obj)
    return obj

