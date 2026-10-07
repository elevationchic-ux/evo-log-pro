"""Routeur CRUD genere pour amenagement-portuaire (expansion)."""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import Optional, List

from app.core.database import get_db
from app.core.permissions import require_perm
from app.models.user import User
from app.models.amenagement_extra_deep import (
    ConstructionProgress,
    InfrastructureMaintenance,
    IspsRecord,
    PortPerception,
    AnnualActivityReport,
    SigLayer,
    DomainArchive,
    AmenagementKpi,
)
from app.schemas.amenagement_extra_deep import (
    ConstructionProgressCreate, ConstructionProgressUpdate, ConstructionProgressOut,
    InfrastructureMaintenanceCreate, InfrastructureMaintenanceUpdate, InfrastructureMaintenanceOut,
    IspsRecordCreate, IspsRecordUpdate, IspsRecordOut,
    PortPerceptionCreate, PortPerceptionUpdate, PortPerceptionOut,
    AnnualActivityReportCreate, AnnualActivityReportUpdate, AnnualActivityReportOut,
    SigLayerCreate, SigLayerUpdate, SigLayerOut,
    DomainArchiveCreate, DomainArchiveUpdate, DomainArchiveOut,
    AmenagementKpiCreate, AmenagementKpiUpdate, AmenagementKpiOut,
)

router = APIRouter(tags=["amenagement-portuaire (expansion)"])


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

@router.get("/nomenclatures", summary="Vocabulaire metier amenagement-portuaire")
def nomenclatures(user: User = Depends(require_perm("amenagement.nomenclature.read"))):
    from app.models import amenagement_extra_deep as _md
    import enum as _pyenum
    out = {}
    for name in dir(_md):
        obj = getattr(_md, name)
        if isinstance(obj, type) and issubclass(obj, _pyenum.Enum) and obj is not _pyenum.Enum:
            out[name.lower()] = [{"code": m.name, "valeur": m.value} for m in obj]
    return out


# ─── Suivi avancement physique travaux ─────────────────────────────────────────────────

@router.get("/construction-progresses", response_model=List[ConstructionProgressOut])
def list_construction_tracking(db: Session = Depends(get_db),
    user: User = Depends(require_perm("amenagement.construction_tracking.read")),
):
    cid = _company_id(user)
    return _scoped_list(db, ConstructionProgress, cid)


@router.post("/construction-progresses", response_model=ConstructionProgressOut, status_code=201)
def create_construction_tracking(
    payload: ConstructionProgressCreate,
    db: Session = Depends(get_db),
    user: User = Depends(require_perm("amenagement.construction_tracking.create")),
):
    cid = _company_id(user)
    data = payload.model_dump(exclude_unset=True)
    _check_unique(db, ConstructionProgress, "reference", data.get("reference"), "reference", cid)
    obj = ConstructionProgress(company_id=cid)
    _apply(data, obj)
    db.add(obj)
    db.commit()
    db.refresh(obj)
    return obj


@router.put("/construction-progresses/{ident}", response_model=ConstructionProgressOut)
def update_construction_tracking(
    ident: int,
    payload: ConstructionProgressUpdate,
    db: Session = Depends(get_db),
    user: User = Depends(require_perm("amenagement.construction_tracking.modify")),
):
    cid = _company_id(user)
    obj = _get_or_404(db, ConstructionProgress, ident, "Suivi avancement physique travaux")
    if obj.company_id != cid:
        raise HTTPException(403, "Acces refuse.")
    _apply(payload.model_dump(exclude_unset=True), obj)
    db.commit()
    db.refresh(obj)
    return obj


@router.delete("/construction-progresses/{ident}", response_model=ConstructionProgressOut)
def delete_construction_tracking(
    ident: int,
    db: Session = Depends(get_db),
    user: User = Depends(require_perm("amenagement.construction_tracking.modify")),
):
    cid = _company_id(user)
    obj = _get_or_404(db, ConstructionProgress, ident, "Suivi avancement physique travaux")
    if obj.company_id != cid:
        raise HTTPException(403, "Acces refuse.")
    obj.is_active = False
    db.commit()
    db.refresh(obj)
    return obj


# ─── Maintenance preventive ouvrages ─────────────────────────────────────────────────

@router.get("/infrastructure-maintenances", response_model=List[InfrastructureMaintenanceOut])
def list_infrastructure_maintenance(statut: Optional[str] = None, db: Session = Depends(get_db),
    user: User = Depends(require_perm("amenagement.infrastructure_maintenance.read")),
):
    cid = _company_id(user)
    return _scoped_list(db, InfrastructureMaintenance, cid, {"statut": statut})


@router.post("/infrastructure-maintenances", response_model=InfrastructureMaintenanceOut, status_code=201)
def create_infrastructure_maintenance(
    payload: InfrastructureMaintenanceCreate,
    db: Session = Depends(get_db),
    user: User = Depends(require_perm("amenagement.infrastructure_maintenance.create")),
):
    cid = _company_id(user)
    data = payload.model_dump(exclude_unset=True)
    _check_unique(db, InfrastructureMaintenance, "reference", data.get("reference"), "reference", cid)
    obj = InfrastructureMaintenance(company_id=cid)
    _apply(data, obj)
    db.add(obj)
    db.commit()
    db.refresh(obj)
    return obj


@router.put("/infrastructure-maintenances/{ident}", response_model=InfrastructureMaintenanceOut)
def update_infrastructure_maintenance(
    ident: int,
    payload: InfrastructureMaintenanceUpdate,
    db: Session = Depends(get_db),
    user: User = Depends(require_perm("amenagement.infrastructure_maintenance.modify")),
):
    cid = _company_id(user)
    obj = _get_or_404(db, InfrastructureMaintenance, ident, "Maintenance preventive ouvrages")
    if obj.company_id != cid:
        raise HTTPException(403, "Acces refuse.")
    _apply(payload.model_dump(exclude_unset=True), obj)
    db.commit()
    db.refresh(obj)
    return obj


@router.delete("/infrastructure-maintenances/{ident}", response_model=InfrastructureMaintenanceOut)
def delete_infrastructure_maintenance(
    ident: int,
    db: Session = Depends(get_db),
    user: User = Depends(require_perm("amenagement.infrastructure_maintenance.modify")),
):
    cid = _company_id(user)
    obj = _get_or_404(db, InfrastructureMaintenance, ident, "Maintenance preventive ouvrages")
    if obj.company_id != cid:
        raise HTTPException(403, "Acces refuse.")
    obj.is_active = False
    db.commit()
    db.refresh(obj)
    return obj


# ─── Surete ISPS (distinct QHSE) ─────────────────────────────────────────────────

@router.get("/isps-records", response_model=List[IspsRecordOut])
def list_port_security_isps(db: Session = Depends(get_db),
    user: User = Depends(require_perm("amenagement.port_security_isps.read")),
):
    cid = _company_id(user)
    return _scoped_list(db, IspsRecord, cid)


@router.post("/isps-records", response_model=IspsRecordOut, status_code=201)
def create_port_security_isps(
    payload: IspsRecordCreate,
    db: Session = Depends(get_db),
    user: User = Depends(require_perm("amenagement.port_security_isps.create")),
):
    cid = _company_id(user)
    data = payload.model_dump(exclude_unset=True)
    _check_unique(db, IspsRecord, "reference", data.get("reference"), "reference", cid)
    obj = IspsRecord(company_id=cid)
    _apply(data, obj)
    db.add(obj)
    db.commit()
    db.refresh(obj)
    return obj


@router.put("/isps-records/{ident}", response_model=IspsRecordOut)
def update_port_security_isps(
    ident: int,
    payload: IspsRecordUpdate,
    db: Session = Depends(get_db),
    user: User = Depends(require_perm("amenagement.port_security_isps.modify")),
):
    cid = _company_id(user)
    obj = _get_or_404(db, IspsRecord, ident, "Surete ISPS (distinct QHSE)")
    if obj.company_id != cid:
        raise HTTPException(403, "Acces refuse.")
    _apply(payload.model_dump(exclude_unset=True), obj)
    db.commit()
    db.refresh(obj)
    return obj


@router.delete("/isps-records/{ident}", response_model=IspsRecordOut)
def delete_port_security_isps(
    ident: int,
    db: Session = Depends(get_db),
    user: User = Depends(require_perm("amenagement.port_security_isps.modify")),
):
    cid = _company_id(user)
    obj = _get_or_404(db, IspsRecord, ident, "Surete ISPS (distinct QHSE)")
    if obj.company_id != cid:
        raise HTTPException(403, "Acces refuse.")
    obj.is_active = False
    db.commit()
    db.refresh(obj)
    return obj


# ─── Redevances et perceptions portuaires ─────────────────────────────────────────────────

@router.get("/port-perceptions", response_model=List[PortPerceptionOut])
def list_port_pricing(db: Session = Depends(get_db),
    user: User = Depends(require_perm("amenagement.port_pricing.read")),
):
    cid = _company_id(user)
    return _scoped_list(db, PortPerception, cid)


@router.post("/port-perceptions", response_model=PortPerceptionOut, status_code=201)
def create_port_pricing(
    payload: PortPerceptionCreate,
    db: Session = Depends(get_db),
    user: User = Depends(require_perm("amenagement.port_pricing.create")),
):
    cid = _company_id(user)
    data = payload.model_dump(exclude_unset=True)
    _check_unique(db, PortPerception, "code_perception", data.get("code_perception"), "code_perception", cid)
    obj = PortPerception(company_id=cid)
    _apply(data, obj)
    db.add(obj)
    db.commit()
    db.refresh(obj)
    return obj


@router.put("/port-perceptions/{ident}", response_model=PortPerceptionOut)
def update_port_pricing(
    ident: int,
    payload: PortPerceptionUpdate,
    db: Session = Depends(get_db),
    user: User = Depends(require_perm("amenagement.port_pricing.modify")),
):
    cid = _company_id(user)
    obj = _get_or_404(db, PortPerception, ident, "Redevances et perceptions portuaires")
    if obj.company_id != cid:
        raise HTTPException(403, "Acces refuse.")
    _apply(payload.model_dump(exclude_unset=True), obj)
    db.commit()
    db.refresh(obj)
    return obj


@router.delete("/port-perceptions/{ident}", response_model=PortPerceptionOut)
def delete_port_pricing(
    ident: int,
    db: Session = Depends(get_db),
    user: User = Depends(require_perm("amenagement.port_pricing.modify")),
):
    cid = _company_id(user)
    obj = _get_or_404(db, PortPerception, ident, "Redevances et perceptions portuaires")
    if obj.company_id != cid:
        raise HTTPException(403, "Acces refuse.")
    obj.is_active = False
    db.commit()
    db.refresh(obj)
    return obj


# ─── Rapport d'activite annuel ─────────────────────────────────────────────────

@router.get("/annual-activity-reports", response_model=List[AnnualActivityReportOut])
def list_activity_report(statut: Optional[str] = None, db: Session = Depends(get_db),
    user: User = Depends(require_perm("amenagement.activity_report.read")),
):
    cid = _company_id(user)
    return _scoped_list(db, AnnualActivityReport, cid, {"statut": statut})


@router.post("/annual-activity-reports", response_model=AnnualActivityReportOut, status_code=201)
def create_activity_report(
    payload: AnnualActivityReportCreate,
    db: Session = Depends(get_db),
    user: User = Depends(require_perm("amenagement.activity_report.create")),
):
    cid = _company_id(user)
    data = payload.model_dump(exclude_unset=True)
    _check_unique(db, AnnualActivityReport, "reference", data.get("reference"), "reference", cid)
    obj = AnnualActivityReport(company_id=cid)
    _apply(data, obj)
    db.add(obj)
    db.commit()
    db.refresh(obj)
    return obj


@router.put("/annual-activity-reports/{ident}", response_model=AnnualActivityReportOut)
def update_activity_report(
    ident: int,
    payload: AnnualActivityReportUpdate,
    db: Session = Depends(get_db),
    user: User = Depends(require_perm("amenagement.activity_report.modify")),
):
    cid = _company_id(user)
    obj = _get_or_404(db, AnnualActivityReport, ident, "Rapport d'activite annuel")
    if obj.company_id != cid:
        raise HTTPException(403, "Acces refuse.")
    _apply(payload.model_dump(exclude_unset=True), obj)
    db.commit()
    db.refresh(obj)
    return obj


@router.delete("/annual-activity-reports/{ident}", response_model=AnnualActivityReportOut)
def delete_activity_report(
    ident: int,
    db: Session = Depends(get_db),
    user: User = Depends(require_perm("amenagement.activity_report.modify")),
):
    cid = _company_id(user)
    obj = _get_or_404(db, AnnualActivityReport, ident, "Rapport d'activite annuel")
    if obj.company_id != cid:
        raise HTTPException(403, "Acces refuse.")
    obj.is_active = False
    db.commit()
    db.refresh(obj)
    return obj


# ─── SIG / cartographie domaine ─────────────────────────────────────────────────

@router.get("/sig-layers", response_model=List[SigLayerOut])
def list_domain_cartography(db: Session = Depends(get_db),
    user: User = Depends(require_perm("amenagement.domain_cartography.read")),
):
    cid = _company_id(user)
    return _scoped_list(db, SigLayer, cid)


@router.post("/sig-layers", response_model=SigLayerOut, status_code=201)
def create_domain_cartography(
    payload: SigLayerCreate,
    db: Session = Depends(get_db),
    user: User = Depends(require_perm("amenagement.domain_cartography.create")),
):
    cid = _company_id(user)
    data = payload.model_dump(exclude_unset=True)
    _check_unique(db, SigLayer, "code_couche", data.get("code_couche"), "code_couche", cid)
    obj = SigLayer(company_id=cid)
    _apply(data, obj)
    db.add(obj)
    db.commit()
    db.refresh(obj)
    return obj


@router.put("/sig-layers/{ident}", response_model=SigLayerOut)
def update_domain_cartography(
    ident: int,
    payload: SigLayerUpdate,
    db: Session = Depends(get_db),
    user: User = Depends(require_perm("amenagement.domain_cartography.modify")),
):
    cid = _company_id(user)
    obj = _get_or_404(db, SigLayer, ident, "SIG / cartographie domaine")
    if obj.company_id != cid:
        raise HTTPException(403, "Acces refuse.")
    _apply(payload.model_dump(exclude_unset=True), obj)
    db.commit()
    db.refresh(obj)
    return obj


@router.delete("/sig-layers/{ident}", response_model=SigLayerOut)
def delete_domain_cartography(
    ident: int,
    db: Session = Depends(get_db),
    user: User = Depends(require_perm("amenagement.domain_cartography.modify")),
):
    cid = _company_id(user)
    obj = _get_or_404(db, SigLayer, ident, "SIG / cartographie domaine")
    if obj.company_id != cid:
        raise HTTPException(403, "Acces refuse.")
    obj.is_active = False
    db.commit()
    db.refresh(obj)
    return obj


# ─── Archivage pieces domaniales ─────────────────────────────────────────────────

@router.get("/domain-archives", response_model=List[DomainArchiveOut])
def list_archive_management(statut: Optional[str] = None, db: Session = Depends(get_db),
    user: User = Depends(require_perm("amenagement.archive_management.read")),
):
    cid = _company_id(user)
    return _scoped_list(db, DomainArchive, cid, {"statut": statut})


@router.post("/domain-archives", response_model=DomainArchiveOut, status_code=201)
def create_archive_management(
    payload: DomainArchiveCreate,
    db: Session = Depends(get_db),
    user: User = Depends(require_perm("amenagement.archive_management.create")),
):
    cid = _company_id(user)
    data = payload.model_dump(exclude_unset=True)
    _check_unique(db, DomainArchive, "cote_archive", data.get("cote_archive"), "cote_archive", cid)
    obj = DomainArchive(company_id=cid)
    _apply(data, obj)
    db.add(obj)
    db.commit()
    db.refresh(obj)
    return obj


@router.put("/domain-archives/{ident}", response_model=DomainArchiveOut)
def update_archive_management(
    ident: int,
    payload: DomainArchiveUpdate,
    db: Session = Depends(get_db),
    user: User = Depends(require_perm("amenagement.archive_management.modify")),
):
    cid = _company_id(user)
    obj = _get_or_404(db, DomainArchive, ident, "Archivage pieces domaniales")
    if obj.company_id != cid:
        raise HTTPException(403, "Acces refuse.")
    _apply(payload.model_dump(exclude_unset=True), obj)
    db.commit()
    db.refresh(obj)
    return obj


@router.delete("/domain-archives/{ident}", response_model=DomainArchiveOut)
def delete_archive_management(
    ident: int,
    db: Session = Depends(get_db),
    user: User = Depends(require_perm("amenagement.archive_management.modify")),
):
    cid = _company_id(user)
    obj = _get_or_404(db, DomainArchive, ident, "Archivage pieces domaniales")
    if obj.company_id != cid:
        raise HTTPException(403, "Acces refuse.")
    obj.is_active = False
    db.commit()
    db.refresh(obj)
    return obj


# ─── Tableau bord indicateurs amenagement ─────────────────────────────────────────────────

@router.get("/amenagement-kpis", response_model=List[AmenagementKpiOut])
def list_development_kpi(statut: Optional[str] = None, db: Session = Depends(get_db),
    user: User = Depends(require_perm("amenagement.development_kpi.read")),
):
    cid = _company_id(user)
    return _scoped_list(db, AmenagementKpi, cid, {"statut": statut})


@router.post("/amenagement-kpis", response_model=AmenagementKpiOut, status_code=201)
def create_development_kpi(
    payload: AmenagementKpiCreate,
    db: Session = Depends(get_db),
    user: User = Depends(require_perm("amenagement.development_kpi.create")),
):
    cid = _company_id(user)
    data = payload.model_dump(exclude_unset=True)
    _check_unique(db, AmenagementKpi, "code_kpi", data.get("code_kpi"), "code_kpi", cid)
    obj = AmenagementKpi(company_id=cid)
    _apply(data, obj)
    db.add(obj)
    db.commit()
    db.refresh(obj)
    return obj


@router.put("/amenagement-kpis/{ident}", response_model=AmenagementKpiOut)
def update_development_kpi(
    ident: int,
    payload: AmenagementKpiUpdate,
    db: Session = Depends(get_db),
    user: User = Depends(require_perm("amenagement.development_kpi.modify")),
):
    cid = _company_id(user)
    obj = _get_or_404(db, AmenagementKpi, ident, "Tableau bord indicateurs amenagement")
    if obj.company_id != cid:
        raise HTTPException(403, "Acces refuse.")
    _apply(payload.model_dump(exclude_unset=True), obj)
    db.commit()
    db.refresh(obj)
    return obj


@router.delete("/amenagement-kpis/{ident}", response_model=AmenagementKpiOut)
def delete_development_kpi(
    ident: int,
    db: Session = Depends(get_db),
    user: User = Depends(require_perm("amenagement.development_kpi.modify")),
):
    cid = _company_id(user)
    obj = _get_or_404(db, AmenagementKpi, ident, "Tableau bord indicateurs amenagement")
    if obj.company_id != cid:
        raise HTTPException(403, "Acces refuse.")
    obj.is_active = False
    db.commit()
    db.refresh(obj)
    return obj

