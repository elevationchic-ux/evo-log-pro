"""Reporting router - Executive dashboard and multi-dimensional reporting for Cameroon/CEMAC"""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from datetime import datetime, date

from app.core.database import get_db
from app.core.security import get_current_user
from app.models.user import User
from app.schemas.reporting import (
    DashboardExecutifCreate, DashboardExecutifUpdate, DashboardExecutifResponse,
    KPICreate, KPIUpdate, KPIResponse,
    RapportCreate, RapportUpdate, RapportResponse,
    ExportCreate, ExportUpdate, ExportResponse,
    WidgetCreate, WidgetUpdate, WidgetResponse,
    TableauBordOperationnelCreate, TableauBordOperationnelUpdate, TableauBordOperationnelResponse,
    IndicateurFinancierCreate, IndicateurFinancierUpdate, IndicateurFinancierResponse,
    IndicateurDouanierCreate, IndicateurDouanierUpdate, IndicateurDouanierResponse,
    RapportExecutifResponse, RapportFinancierResponse, RapportDouanierResponse
)
from app.services.reporting_service import (
    DashboardExecutifService, KPIService, RapportService, ExportService,
    TableauBordOperationnelService, ReportingReportingService
)
from app.models.reporting import DashboardExecutif, KPI, Rapport, Export, TableauBordOperationnel

router = APIRouter(tags=["Reporting"])


# ============ LECTURE (list) ============
@router.get("/rapports", response_model=List[RapportResponse])
def lister_rapports(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Lister les modèles de rapports réellement enregistrés."""
    return db.query(Rapport).order_by(Rapport.id.desc()).offset(skip).limit(limit).all()


@router.get("/dashboards", response_model=List[DashboardExecutifResponse])
def lister_dashboards(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Lister les dashboards réellement enregistrés."""
    return db.query(DashboardExecutif).order_by(DashboardExecutif.id.desc()).offset(skip).limit(limit).all()


@router.get("/kpis", response_model=List[KPIResponse])
def lister_kpis(
    skip: int = 0,
    limit: int = 200,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Lister les KPI réellement enregistrés."""
    return db.query(KPI).order_by(KPI.id.desc()).offset(skip).limit(limit).all()


@router.get("/exports", response_model=List[ExportResponse])
def lister_exports(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Lister les exports réellement enregistrés."""
    return db.query(Export).order_by(Export.id.desc()).offset(skip).limit(limit).all()


@router.get("/tableaux-bord", response_model=List[TableauBordOperationnelResponse])
def lister_tableaux_bord(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Lister les tableaux de bord opérationnels réellement enregistrés."""
    return db.query(TableauBordOperationnel).order_by(TableauBordOperationnel.id.desc()).offset(skip).limit(limit).all()


# ============ DASHBOARDS EXECUTIFS ============
@router.post("/dashboards", response_model=DashboardExecutifResponse, status_code=status.HTTP_201_CREATED)
def creer_dashboard(
    dashboard: DashboardExecutifCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Create executive dashboard"""
    return DashboardExecutifService.creer_dashboard(
        db, dashboard.code, dashboard.nom, dashboard.layout,
        dashboard.widgets, dashboard.filtres
    )


@router.put("/dashboards/{dashboard_id}", response_model=DashboardExecutifResponse)
def mettre_a_jour_dashboard(
    dashboard_id: int,
    dashboard: DashboardExecutifUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Update executive dashboard"""
    d = db.query(DashboardExecutif).filter(DashboardExecutif.id == dashboard_id).first()
    if not d:
        raise HTTPException(status_code=404, detail="Dashboard non trouvé")
    
    for field, value in dashboard.model_dump(exclude_unset=True).items():
        setattr(d, field, value)
    
    db.commit()
    db.refresh(d)
    return d


# ============ KPIs ============
@router.post("/kpis", response_model=KPIResponse, status_code=status.HTTP_201_CREATED)
def creer_kpi(
    kpi: KPICreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Create KPI"""
    return KPIService.creer_kpi(
        db, kpi.code, kpi.nom, kpi.type_rapport, kpi.categorie,
        kpi.formule, kpi.unite, kpi.objectif
    )


@router.put("/kpis/{kpi_id}/valeur", response_model=KPIResponse)
def mettre_a_jour_valeur_kpi(
    kpi_id: int,
    derniere_valeur: float,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Update KPI value"""
    return KPIService.mettre_a_jour_valeur(db, kpi_id, derniere_valeur)


@router.put("/kpis/{kpi_id}", response_model=KPIResponse)
def mettre_a_jour_kpi(
    kpi_id: int,
    kpi: KPIUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Update KPI"""
    k = db.query(KPI).filter(KPI.id == kpi_id).first()
    if not k:
        raise HTTPException(status_code=404, detail="KPI non trouvé")
    
    for field, value in kpi.model_dump(exclude_unset=True).items():
        setattr(k, field, value)
    
    db.commit()
    db.refresh(k)
    return k


# ============ RAPPORTS ============
@router.post("/rapports", response_model=RapportResponse, status_code=status.HTTP_201_CREATED)
def creer_rapport(
    rapport: RapportCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Create report"""
    return RapportService.creer_rapport(
        db, rapport.numero_rapport, rapport.titre, rapport.type_rapport,
        rapport.frequence, rapport.requetes, rapport.colonnes
    )


@router.put("/rapports/{rapport_id}/generer", response_model=RapportResponse)
def generer_rapport(
    rapport_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Generate report"""
    return RapportService.generer_rapport(db, rapport_id)


@router.put("/rapports/{rapport_id}", response_model=RapportResponse)
def mettre_a_jour_rapport(
    rapport_id: int,
    rapport: RapportUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Update report"""
    r = db.query(Rapport).filter(Rapport.id == rapport_id).first()
    if not r:
        raise HTTPException(status_code=404, detail="Rapport non trouvé")
    
    for field, value in rapport.model_dump(exclude_unset=True).items():
        setattr(r, field, value)
    
    db.commit()
    db.refresh(r)
    return r


# ============ EXPORTS ============
@router.post("/exports", response_model=ExportResponse, status_code=status.HTTP_201_CREATED)
def creer_export(
    export: ExportCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Create export"""
    return ExportService.creer_export(
        db, export.numero_export, export.rapport_id, export.type_rapport,
        export.format_export, export.parametres
    )


@router.put("/exports/{export_id}", response_model=ExportResponse)
def mettre_a_jour_export(
    export_id: int,
    export: ExportUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Update export"""
    e = db.query(Export).filter(Export.id == export_id).first()
    if not e:
        raise HTTPException(status_code=404, detail="Export non trouvé")
    
    for field, value in export.model_dump(exclude_unset=True).items():
        setattr(e, field, value)
    
    db.commit()
    db.refresh(e)
    return e


# ============ TABLEAUX BORD OPERATIONNELS ============
@router.post("/tableaux-bord", response_model=TableauBordOperationnelResponse, status_code=status.HTTP_201_CREATED)
def creer_tableau_bord(
    tableau: TableauBordOperationnelCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Create operational dashboard"""
    return TableauBordOperationnelService.creer_tableau_bord(
        db, tableau.code, tableau.nom, tableau.module,
        tableau.metriques, tableau.graphiques
    )


@router.put("/tableaux-bord/{tableau_id}/actualiser", response_model=TableauBordOperationnelResponse)
def actualiser_tableau_bord(
    tableau_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Update operational dashboard data"""
    return TableauBordOperationnelService.actualiser_donnees(db, tableau_id)


@router.put("/tableaux-bord/{tableau_id}", response_model=TableauBordOperationnelResponse)
def mettre_a_jour_tableau_bord(
    tableau_id: int,
    tableau: TableauBordOperationnelUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Update operational dashboard"""
    t = db.query(TableauBordOperationnel).filter(TableauBordOperationnel.id == tableau_id).first()
    if not t:
        raise HTTPException(status_code=404, detail="Tableau de bord non trouvé")
    
    for field, value in tableau.model_dump(exclude_unset=True).items():
        setattr(t, field, value)
    
    db.commit()
    db.refresh(t)
    return t


# ============ RAPPORTS CONSOLIDÉS ============
@router.get("/rapports/executif", response_model=RapportExecutifResponse)
def rapport_executif(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Generate executive report"""
    return ReportingReportingService.rapport_executif(db)


@router.get("/rapports/financier/{periode}", response_model=RapportFinancierResponse)
def rapport_financier(
    periode: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Generate financial report"""
    return ReportingReportingService.rapport_financier(db, periode)


@router.get("/rapports/douanier/{periode}", response_model=RapportDouanierResponse)
def rapport_douanier(
    periode: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Generate customs report"""
    return ReportingReportingService.rapport_douanier(db, periode)


# ============ RAPPORT UNITE (lecture / suppression) ============
# Enregistre apres les routes statiques (/rapports/executif etc.) pour eviter
# que {rapport_id} n'intercepte les chemins fixes.
@router.get("/rapports/{rapport_id}", response_model=RapportResponse)
def recuperer_rapport(
    rapport_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    r = db.query(Rapport).filter(Rapport.id == rapport_id).first()
    if not r:
        raise HTTPException(status_code=404, detail="Rapport non trouvé")
    return r


@router.delete("/rapports/{rapport_id}", status_code=status.HTTP_200_OK)
def supprimer_rapport(
    rapport_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Supprimer un modèle de rapport enregistré."""
    r = db.query(Rapport).filter(Rapport.id == rapport_id).first()
    if not r:
        raise HTTPException(status_code=404, detail="Rapport non trouvé")
    db.delete(r)
    db.commit()
    return {"message": "Rapport supprimé", "id": rapport_id}
