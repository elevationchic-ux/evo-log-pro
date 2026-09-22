"""Unit tests for Reporting module - Executive dashboard and multi-dimensional reporting"""
import pytest
from datetime import datetime, date
from sqlalchemy.orm import Session
from app.models.reporting import (
    DashboardExecutif, KPI, Rapport, Export, TableauBordOperationnel,
    IndicateurFinancier, IndicateurDouanier
)
from app.services.reporting_service import (
    DashboardExecutifService, KPIService, RapportService, ExportService,
    TableauBordOperationnelService, ReportingReportingService
)


class TestDashboardExecutifService:
    """Test Dashboard Executif service"""
    
    def test_creer_dashboard(self, db: Session):
        """Test creating executive dashboard"""
        dashboard = DashboardExecutifService.creer_dashboard(
            db=db,
            code="DASH-EXEC-001",
            nom="Dashboard Direction",
            layout={"colonnes": 12, "rangees": 8},
            widgets={"kpi": ["CA", "Marge"]},
            filtres={"periode": "mensuel"}
        )
        assert dashboard.code == "DASH-EXEC-001"
        assert dashboard.nom == "Dashboard Direction"
        assert dashboard.actif is True


class TestKPIService:
    """Test KPI service"""
    
    def test_creer_kpi(self, db: Session):
        """Test creating KPI"""
        kpi = KPIService.creer_kpi(
            db=db,
            code="KPI-CA",
            nom="Chiffre d'Affaires",
            type_rapport="financier",
            categorie="rentabilite",
            formule="SUM(factures.montant_ttc)",
            unite="XAF",
            objectif=500000000.0
        )
        assert kpi.code == "KPI-CA"
        assert kpi.type_rapport == "financier"
        assert kpi.objectif == 500000000.0
    
    def test_mettre_a_jour_valeur(self, db: Session):
        """Test updating KPI value"""
        kpi = KPIService.creer_kpi(
            db=db,
            code="KPI-CA",
            nom="Chiffre d'Affaires",
            type_rapport="financier",
            categorie="rentabilite",
            formule="SUM(factures.montant_ttc)",
            unite="XAF",
            objectif=500000000.0
        )
        
        kpi_maj = KPIService.mettre_a_jour_valeur(
            db=db,
            kpi_id=kpi.id,
            derniere_valeur=450000000.0
        )
        assert kpi_maj.derniere_valeur == 450000000.0
        assert kpi_maj.tendance == "baisse"


class TestRapportService:
    """Test Rapport service"""
    
    def test_creer_rapport(self, db: Session):
        """Test creating report"""
        rapport = RapportService.creer_rapport(
            db=db,
            numero_rapport="RPT-2026-001",
            titre="Rapport Mensuel Janvier",
            type_rapport="financier",
            frequence="mensuel",
            requetes={"sql": "SELECT * FROM factures"},
            colonnes=["id", "numero", "montant"]
        )
        assert rapport.numero_rapport == "RPT-2026-001"
        assert rapport.type_rapport == "financier"
        assert rapport.statut == "en_preparation"
    
    def test_generer_rapport(self, db: Session):
        """Test generating report"""
        rapport = RapportService.creer_rapport(
            db=db,
            numero_rapport="RPT-2026-001",
            titre="Rapport Mensuel Janvier",
            type_rapport="financier",
            frequence="mensuel",
            requetes={"sql": "SELECT * FROM factures"},
            colonnes=["id", "numero", "montant"]
        )
        
        rapport_genere = RapportService.generer_rapport(
            db=db,
            rapport_id=rapport.id
        )
        assert rapport_genere.statut == "disponible"
        assert rapport_genere.date_generation is not None


class TestExportService:
    """Test Export service"""
    
    def test_creer_export(self, db: Session):
        """Test creating export"""
        export = ExportService.creer_export(
            db=db,
            numero_export="EXP-2026-001",
            rapport_id=1,
            type_rapport="financier",
            format_export="excel",
            parametres={"periode": "2026-01"}
        )
        assert export.numero_export == "EXP-2026-001"
        assert export.format_export == "excel"
        assert export.statut == "en_attente"


class TestTableauBordOperationnelService:
    """Test Tableau Bord Operationnel service"""
    
    def test_creer_tableau_bord(self, db: Session):
        """Test creating operational dashboard"""
        tableau = TableauBordOperationnelService.creer_tableau_bord(
            db=db,
            code="TB-ACCONAGE-001",
            nom="Tableau Acconage",
            module="acconage",
            metriques={"navires": 15, "conteneurs": 1200},
            graphiques={"types": ["bar", "line"]}
        )
        assert tableau.code == "TB-ACCONAGE-001"
        assert tableau.module == "acconage"
        assert tableau.actif is True
    
    def test_actualiser_donnees(self, db: Session):
        """Test updating dashboard data"""
        tableau = TableauBordOperationnelService.creer_tableau_bord(
            db=db,
            code="TB-ACCONAGE-001",
            nom="Tableau Acconage",
            module="acconage",
            metriques={"navires": 15, "conteneurs": 1200},
            graphiques={"types": ["bar", "line"]}
        )
        
        tableau_maj = TableauBordOperationnelService.actualiser_donnees(
            db=db,
            tableau_id=tableau.id
        )
        assert tableau_maj.derniere_actualisation is not None


class TestReportingReportingService:
    """Test Reporting aggregation service"""
    
    def test_rapport_executif(self, db: Session):
        """Test generating executive report"""
        kpi = KPIService.creer_kpi(
            db=db,
            code="KPI-CA",
            nom="Chiffre d'Affaires",
            type_rapport="financier",
            categorie="rentabilite",
            formule="SUM(factures.montant_ttc)",
            unite="XAF",
            objectif=500000000.0
        )
        
        rapport = ReportingReportingService.rapport_executif(db)
        assert "kpis" in rapport
        assert "nombre_kpis" in rapport
        assert rapport["nombre_kpis"] >= 1
    
    def test_rapport_financier(self, db: Session):
        """Test generating financial report"""
        rapport = ReportingReportingService.rapport_financier(db, "mensuel")
        assert "periode" in rapport
        assert rapport["periode"] == "mensuel"
        assert "indicateurs" in rapport
    
    def test_rapport_douanier(self, db: Session):
        """Test generating customs report"""
        rapport = ReportingReportingService.rapport_douanier(db, "mensuel")
        assert "periode" in rapport
        assert rapport["periode"] == "mensuel"
        assert "indicateurs" in rapport
