"""Maintenance GMAO service - CMMS for Cameroon/CEMAC"""
from datetime import datetime, date, timedelta
from typing import List, Optional, Dict, Any
from sqlalchemy.orm import Session
from sqlalchemy import and_, func
from app.models.maintenance_gmao import (
    OrdreMaintenance, EquipementGMAO, PlanMaintenance, PieceRechangeGMAO, PieceUtilisee,
    Calibration, PerformanceEquipement, HistoriqueMaintenance,
    TypeMaintenance, PrioriteMaintenance, StatutMaintenance, TypeEquipement, StatutEquipement
)


class OrdreMaintenanceService:
    """Maintenance work order service"""
    
    @staticmethod
    def creer_ordre(
        db: Session,
        numero_ordre: str,
        equipement_id: int,
        type_maintenance: TypeMaintenance,
        priorite: PrioriteMaintenance,
        description: str,
        date_planifiee: date,
        technicien_id: int
    ) -> OrdreMaintenance:
        """Create maintenance work order"""
        ordre = OrdreMaintenance(
            numero_ordre=numero_ordre,
            equipement_id=equipement_id,
            type_maintenance=type_maintenance,
            priorite=priorite,
            description=description,
            date_planifiee=date_planifiee,
            technicien_id=technicien_id,
            statut=StatutMaintenance.PLANIFIEE,
            devise="XAF"
        )
        db.add(ordre)
        db.commit()
        db.refresh(ordre)
        return ordre
    
    @staticmethod
    def completer_ordre(
        db: Session,
        ordre_id: int,
        date_fin: datetime,
        duree_reelle: int,
        observations: str
    ) -> OrdreMaintenance:
        """Complete maintenance work order"""
        ordre = db.query(OrdreMaintenance).filter(OrdreMaintenance.id == ordre_id).first()
        if not ordre:
            raise ValueError("Ordre de maintenance non trouvé")
        
        ordre.date_fin = date_fin
        ordre.duree_reelle = duree_reelle
        ordre.observations = observations
        ordre.statut = StatutMaintenance.VALIDE
        ordre.date_validation = date.today()
        
        # Calculate total cost
        ordre.cout_total = ordre.cout_pieces + ordre.cout_main_oeuvre
        
        db.commit()
        db.refresh(ordre)
        return ordre


class EquipementGMAOService:
    """Equipment service"""
    
    @staticmethod
    def creer_equipement(
        db: Session,
        numero_serie: str,
        designation: str,
        type_equipement: TypeEquipement,
        marque: str,
        modele: str,
        localisation: str
    ) -> EquipementGMAO:
        """Create equipment"""
        equipement = EquipementGMAO(
            numero_serie=numero_serie,
            designation=designation,
            type_equipement=type_equipement,
            marque=marque,
            modele=modele,
            localisation=localisation,
            statut=StatutEquipement.OPERATIONNEL,
            devise="XAF"
        )
        db.add(equipement)
        db.commit()
        db.refresh(equipement)
        return equipement


class PlanMaintenanceService:
    """Maintenance plan service"""
    
    @staticmethod
    def creer_plan(
        db: Session,
        numero_plan: str,
        equipement_id: int,
        type_maintenance: TypeMaintenance,
        frequence: str,
        intervalle_jours: int,
        date_debut: date
    ) -> PlanMaintenance:
        """Create maintenance plan"""
        plan = PlanMaintenance(
            numero_plan=numero_plan,
            equipement_id=equipement_id,
            type_maintenance=type_maintenance,
            frequence=frequence,
            intervalle_jours=intervalle_jours,
            date_debut=date_debut,
            statut="actif"
        )
        db.add(plan)
        db.commit()
        db.refresh(plan)
        return plan


class PieceRechangeGMAOService:
    """Spare part service"""
    
    @staticmethod
    def creer_piece(
        db: Session,
        reference: str,
        designation: str,
        equipement_id: int,
        categorie: str,
        prix_unitaire: float
    ) -> PieceRechangeGMAO:
        """Create spare part"""
        piece = PieceRechangeGMAO(
            reference=reference,
            designation=designation,
            equipement_id=equipement_id,
            categorie=categorie,
            prix_unitaire=prix_unitaire,
            stock_actuel=0,
            stock_minimum=0,
            devise="XAF",
            statut="disponible"
        )
        db.add(piece)
        db.commit()
        db.refresh(piece)
        return piece


class CalibrationService:
    """Calibration service"""
    
    @staticmethod
    def creer_calibration(
        db: Session,
        numero_calibration: str,
        equipement_id: int,
        instrument: str,
        date_calibration: date,
        intervalle_mois: int
    ) -> Calibration:
        """Create calibration record"""
        date_prochaine = date_calibration + timedelta(days=intervalle_mois * 30)
        
        calibration = Calibration(
            numero_calibration=numero_calibration,
            equipement_id=equipement_id,
            instrument=instrument,
            date_calibration=date_calibration,
            date_prochaine=date_prochaine,
            intervalle_mois=intervalle_mois,
            statut="valide"
        )
        db.add(calibration)
        db.commit()
        db.refresh(calibration)
        return calibration


class PerformanceEquipementService:
    """Equipment performance service"""
    
    @staticmethod
    def enregistrer_performance(
        db: Session,
        equipement_id: int,
        periode: str,
        temps_fonctionnement: float,
        temps_arret: float,
        nombre_pannes: int,
        temps_maintenance: float
    ) -> PerformanceEquipement:
        """Record equipment performance"""
        # Calculate MTBF, MTTR, Availability
        mtbf = temps_fonctionnement / nombre_pannes if nombre_pannes > 0 else 0
        mttr = temps_maintenance / nombre_pannes if nombre_pannes > 0 else 0
        disponibilite = (temps_fonctionnement / (temps_fonctionnement + temps_arret)) * 100 if (temps_fonctionnement + temps_arret) > 0 else 0
        taux_panne = (temps_arret / (temps_fonctionnement + temps_arret)) * 100 if (temps_fonctionnement + temps_arret) > 0 else 0
        
        performance = PerformanceEquipement(
            equipement_id=equipement_id,
            periode=periode,
            date_mesure=date.today(),
            temps_fonctionnement=temps_fonctionnement,
            temps_arret=temps_arret,
            nombre_pannes=nombre_pannes,
            temps_maintenance=temps_maintenance,
            mtbf=mtbf,
            mttr=mttr,
            disponibilite=disponibilite,
            taux_panne=taux_panne,
            devise="XAF"
        )
        db.add(performance)
        db.commit()
        db.refresh(performance)
        return performance


class MaintenanceReportingService:
    """Maintenance reporting service"""
    
    @staticmethod
    def rapport_maintenance(db: Session, equipement_id: int) -> Dict[str, Any]:
        """Generate maintenance report"""
        equipement = db.query(EquipementGMAO).filter(EquipementGMAO.id == equipement_id).first()
        if not equipement:
            raise ValueError("Équipement non trouvé")
        
        ordres = db.query(OrdreMaintenance).filter(
            OrdreMaintenance.equipement_id == equipement_id
        ).all()
        
        return {
            "equipement": {
                "numero_serie": equipement.numero_serie,
                "designation": equipement.designation,
                "statut": equipement.statut.value
            },
            "maintenance": {
                "total_ordres": len(ordres),
                "ordres_termines": sum(1 for o in ordres if o.statut == StatutMaintenance.VALIDE),
                "cout_total": sum(o.cout_total or 0 for o in ordres)
            }
        }
