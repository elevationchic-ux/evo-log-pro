"""Reporting service - Executive dashboard and multi-dimensional reporting for Cameroon/CEMAC"""
from datetime import datetime, date, timedelta
from typing import List, Optional, Dict, Any
from sqlalchemy.orm import Session
from sqlalchemy import and_, func
from app.models.reporting import (
    DashboardExecutif, KPI, Rapport, HistoriqueGeneration, Export,
    Widget, DrillDown, ScheduleReport, TableauBordOperationnel,
    IndicateurFinancier, IndicateurDouanier
)


class DashboardExecutifService:
    """Executive dashboard service"""
    
    @staticmethod
    def creer_dashboard(
        db: Session,
        code: str,
        nom: str,
        layout: dict,
        widgets: dict,
        filtres: dict
    ) -> DashboardExecutif:
        """Create executive dashboard"""
        dashboard = DashboardExecutif(
            code=code,
            nom=nom,
            layout=layout,
            widgets=widgets,
            filtres=filtres,
            actif=True
        )
        db.add(dashboard)
        db.commit()
        db.refresh(dashboard)
        return dashboard


class KPIService:
    """KPI service"""
    
    @staticmethod
    def creer_kpi(
        db: Session,
        code: str,
        nom: str,
        type_rapport: str,
        categorie: str,
        formule: str,
        unite: str,
        objectif: float
    ) -> KPI:
        """Create KPI"""
        kpi = KPI(
            code=code,
            nom=nom,
            type_rapport=type_rapport,
            categorie=categorie,
            formule=formule,
            unite=unite,
            objectif=objectif,
            actif=True
        )
        db.add(kpi)
        db.commit()
        db.refresh(kpi)
        return kpi
    
    @staticmethod
    def mettre_a_jour_valeur(
        db: Session,
        kpi_id: int,
        derniere_valeur: float
    ) -> KPI:
        """Update KPI value"""
        kpi = db.query(KPI).filter(KPI.id == kpi_id).first()
        if not kpi:
            raise ValueError("KPI non trouvé")
        
        # Colonnes Numeric -> Decimal cote SQLAlchemy : sans conversion, la
        # 2e mise a jour d'un KPI plantait (float - Decimal -> TypeError).
        valeur_precedente = float(kpi.derniere_valeur or 0)
        derniere_valeur = float(derniere_valeur)
        variation = ((derniere_valeur - valeur_precedente) / valeur_precedente * 100) if valeur_precedente > 0 else 0
        
        if variation > 0:
            tendance = "hausse"
        elif variation < 0:
            tendance = "baisse"
        else:
            tendance = "stable"
        
        kpi.derniere_valeur = derniere_valeur
        kpi.valeur_precedente = valeur_precedente
        kpi.variation_pourcentage = variation
        kpi.tendance = tendance
        kpi.date_derniere_valeur = datetime.utcnow()
        
        db.commit()
        db.refresh(kpi)
        return kpi


class RapportService:
    """Report service"""
    
    @staticmethod
    def creer_rapport(
        db: Session,
        numero_rapport: str,
        titre: str,
        type_rapport: str,
        frequence: str,
        requetes: dict,
        colonnes: dict
    ) -> Rapport:
        """Create report"""
        rapport = Rapport(
            numero_rapport=numero_rapport,
            titre=titre,
            type_rapport=type_rapport,
            frequence=frequence,
            requetes=requetes,
            colonnes=colonnes,
            statut="en_preparation"
        )
        db.add(rapport)
        db.commit()
        db.refresh(rapport)
        return rapport
    
    @staticmethod
    def generer_rapport(db: Session, rapport_id: int) -> Rapport:
        """Generate report"""
        rapport = db.query(Rapport).filter(Rapport.id == rapport_id).first()
        if not rapport:
            raise ValueError("Rapport non trouvé")
        
        debut = datetime.utcnow()
        rapport.statut = "en_cours"
        rapport.date_generation = debut
        db.commit()
        
        # Simulate report generation
        import time
        time.sleep(1)
        
        fin = datetime.utcnow()
        rapport.statut = "disponible"
        rapport.date_generation = fin
        rapport.duree_generation = int((fin - debut).total_seconds())
        rapport.nombre_lignes = 1000
        
        db.commit()
        db.refresh(rapport)
        return rapport


class ExportService:
    """Export service"""
    
    @staticmethod
    def creer_export(
        db: Session,
        numero_export: str,
        rapport_id: int,
        type_rapport: str,
        format_export: str,
        parametres: dict
    ) -> Export:
        """Create export"""
        export = Export(
            numero_export=numero_export,
            rapport_id=rapport_id,
            type_rapport=type_rapport,
            format_export=format_export,
            parametres=parametres,
            statut="en_attente"
        )
        db.add(export)
        db.commit()
        db.refresh(export)
        return export


class TableauBordOperationnelService:
    """Operational dashboard service"""
    
    @staticmethod
    def creer_tableau_bord(
        db: Session,
        code: str,
        nom: str,
        module: str,
        metriques: dict,
        graphiques: dict
    ) -> TableauBordOperationnel:
        """Create operational dashboard"""
        tableau = TableauBordOperationnel(
            code=code,
            nom=nom,
            module=module,
            metriques=metriques,
            graphiques=graphiques,
            actif=True
        )
        db.add(tableau)
        db.commit()
        db.refresh(tableau)
        return tableau
    
    @staticmethod
    def actualiser_donnees(db: Session, tableau_id: int) -> TableauBordOperationnel:
        """Update dashboard data"""
        tableau = db.query(TableauBordOperationnel).filter(TableauBordOperationnel.id == tableau_id).first()
        if not tableau:
            raise ValueError("Tableau de bord non trouvé")
        
        tableau.derniere_actualisation = datetime.utcnow()
        db.commit()
        db.refresh(tableau)
        return tableau


class ReportingReportingService:
    """Reporting aggregation service"""
    
    @staticmethod
    def rapport_executif(db: Session) -> Dict[str, Any]:
        """Generate executive report.

        100% agrégé depuis la table KPI (filtre tenant via filtre ORM global).
        Aucune valeur inventée : sans KPI enregistré, kpis/poles restent vides
        et l'frontend affiche un état neutre.
        """
        kpis = db.query(KPI).filter(KPI.actif == True).all()

        # Regroupement réel par pôle (type_rapport) : nb d'indicateurs et
        # somme des dernières valeurs, calculés sur les données persistées.
        par_pole: Dict[str, Dict[str, Any]] = {}
        for k in kpis:
            pole = k.type_rapport or "GENERAL"
            bucket = par_pole.setdefault(
                pole, {"pole": pole, "nb_indicateurs": 0, "valeur_cumulee": 0.0}
            )
            bucket["nb_indicateurs"] += 1
            if k.derniere_valeur is not None:
                try:
                    bucket["valeur_cumulee"] += float(k.derniere_valeur)
                except (TypeError, ValueError):
                    pass
        poles = sorted(
            (
                {
                    "pole": v["pole"],
                    "nb_indicateurs": v["nb_indicateurs"],
                    "valeur_cumulee": round(v["valeur_cumulee"], 2),
                }
                for v in par_pole.values()
            ),
            key=lambda p: p["pole"],
        )

        return {
            "kpis": [
                {
                    "code": k.code,
                    "nom": k.nom,
                    "valeur": k.derniere_valeur,
                    "unite": k.unite,
                    "objectif": k.objectif,
                    "categorie": k.categorie,
                    "type_rapport": k.type_rapport,
                    "tendance": k.tendance,
                    "variation": k.variation_pourcentage
                }
                for k in kpis
            ],
            "nombre_kpis": len(kpis),
            "k_par_type": {k.type_rapport: 1 for k in kpis},
            "poles": poles
        }
    
    @staticmethod
    def rapport_financier(db: Session, periode: str) -> Dict[str, Any]:
        """Generate financial report"""
        indicateurs = db.query(IndicateurFinancier).filter(
            IndicateurFinancier.periode == periode
        ).all()
        
        return {
            "periode": periode,
            "indicateurs": [
                {
                    "code": i.code,
                    "nom": i.nom,
                    "valeur": i.valeur_actuelle,
                    "objectif": i.objectif,
                    "variation": i.variation,
                    "tendance": i.tendance
                }
                for i in indicateurs
            ]
        }
    
    @staticmethod
    def rapport_douanier(db: Session, periode: str) -> Dict[str, Any]:
        """Generate customs report"""
        indicateurs = db.query(IndicateurDouanier).filter(
            IndicateurDouanier.periode == periode
        ).all()
        
        return {
            "periode": periode,
            "indicateurs": [
                {
                    "code": i.code,
                    "nom": i.nom,
                    "valeur": i.valeur_actuelle,
                    "objectif": i.objectif,
                    "variation": i.variation,
                    "tendance": i.tendance
                }
                for i in indicateurs
            ]
        }


# Facade service for backward compatibility
class ReportingService:
    """Unified reporting service facade"""
    dashboard = DashboardExecutifService
    kpis = KPIService
    rapports = RapportService
    exports = ExportService
    tableau_bord = TableauBordOperationnelService
    reporting = ReportingReportingService
