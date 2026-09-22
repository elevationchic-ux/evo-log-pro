"""Advanced reporting service - RH, Warehouse, Transport KPIs and analytics"""
from datetime import datetime, date, timedelta
from typing import List, Dict, Any, Optional
from sqlalchemy.orm import Session
from sqlalchemy import and_, func, case, desc, asc
from app.models.rh import (
    Conge, Absence, TempsTravail, Formation, ParticipationFormation,
    EvaluationPerformance, ContratTravail, Salaire, DocumentEmploye
)
from app.models.magasin_avance import (
    Peremption, ReservationStock, TransfertStock, InventaireTournant,
    CommandeFournisseur, BonReception, BonSortie, RetourClient
)
from app.models.transport_avance import (
    Tournée, Livraison, TempsConduite, AccidentTransport, MaintenancePreventive,
    PositionGPS, MissionSousTraitant
)
from app.models.magasin import Stock, MouvementStock
from app.models.transport import Mission


class RHReportingService:
    """HR reporting and analytics service"""
    
    @staticmethod
    def rapport_effectif(db: Session, date_rapport: date = None) -> Dict[str, Any]:
        """Generate headcount report"""
        date_rapport = date_rapport or date.today()
        from app.models.user import User
        
        total_employes = db.query(User).filter(User.is_active == True).count()
        
        return {
            "date_rapport": date_rapport,
            "effectif_total": total_employes,
            "note": "Rapport effectif total"
        }
    
    @staticmethod
    def rapport_taux_rotation(db: Session, mois: int, annee: int) -> Dict[str, Any]:
        """Calculate employee turnover rate"""
        debut_mois = date(annee, mois, 1)
        fin_mois = (date(annee, mois + 1, 1) - timedelta(days=1)) if mois < 12 else date(annee, 12, 31)
        
        # This would track hires and departures - simplified for now
        return {
            "mois": mois,
            "annee": annee,
            "taux_rotation": 0.0,
            "entrees": 0,
            "sorties": 0,
            "note": "À implémenter avec tracking historique"
        }
    
    @staticmethod
    def rapport_absenteisme(db: Session, mois: int, annee: int) -> Dict[str, Any]:
        """Generate absenteeism report"""
        debut_mois = date(annee, mois, 1)
        fin_mois = (date(annee, mois + 1, 1) - timedelta(days=1)) if mois < 12 else date(annee, 12, 31)
        
        absences = db.query(Absence).filter(
            and_(
                Absence.date_debut >= debut_mois,
                Absence.date_fin <= fin_mois
            )
        ).all()
        
        total_jours_absence = sum(a.nombre_jours for a in absences)
        absences_justifiees = sum(1 for a in absences if a.justifie)
        taux_justification = (absences_justifiees / len(absences)) * 100 if absences else 0
        
        return {
            "mois": mois,
            "annee": annee,
            "total_absences": len(absences),
            "jours_absence": total_jours_absence,
            "absences_justifiees": absences_justifiees,
            "taux_justification": round(taux_justification, 2)
        }
    
    @staticmethod
    def rapport_conges(db: Session, annee: int) -> Dict[str, Any]:
        """Generate leave consumption report"""
        from app.models.rh import Conge
        from app.models.user import User
        
        conges = db.query(Conge).filter(
            and_(
                Conge.date_debut >= date(annee, 1, 1),
                Conge.date_debut <= date(annee, 12, 31)
            )
        ).all()
        
        conges_pris = sum(c.nombre_jours for c in conges if c.statut == "approuve")
        conges_en_attente = sum(c.nombre_jours for c in conges if c.statut == "en_attente")
        conges_refuses = sum(c.nombre_jours for c in conges if c.statut == "refuse")
        
        return {
            "annee": annee,
            "conges_pris": conges_pris,
            "conges_en_attente": conges_en_attente,
            "conges_refuses": conges_refuses,
            "total_jours": conges_pris + conges_en_attente + conges_refuses
        }
    
    @staticmethod
    def rapport_formation(db: Session, debut: date, fin: date) -> Dict[str, Any]:
        """Generate training compliance report"""
        formations = db.query(Formation).filter(
            and_(
                Formation.date_debut >= debut,
                Formation.date_fin <= fin
            )
        ).all()
        
        participations = db.query(ParticipationFormation).join(Formation).filter(
            and_(
                Formation.date_debut >= debut,
                Formation.date_fin <= fin
            )
        ).all()
        
        total_participants = len(participations)
        certifications_obtenues = sum(1 for p in participations if p.certificat_obtenu)
        taux_certification = (certifications_obtenues / total_participants) * 100 if total_participants > 0 else 0
        
        # Check for expiring certifications
        date_limite = date.today() + timedelta(days=30)
        formations_expirantes = db.query(Formation).filter(
            and_(
                Formation.certificat_valide_jusque.isnot(None),
                Formation.certificat_valide_jusque <= date_limite
            )
        ).count()
        
        return {
            "periode": f"{debut} à {fin}",
            "formations": len(formations),
            "total_participants": total_participants,
            "certifications_obtenues": certifications_obtenues,
            "taux_certification": round(taux_certification, 2),
            "formations_expirantes": formations_expirantes
        }
    
    @staticmethod
    def rapport_paie(db: Session, mois: int, annee: int) -> Dict[str, Any]:
        """Generate payroll summary report"""
        salaires = db.query(Salaire).filter(
            and_(
                Salaire.mois == mois,
                Salaire.annee == annee
            )
        ).all()
        
        total_salaire_brut = sum(s.salaire_brut for s in salaires)
        total_salaire_net = sum(s.salaire_net for s in salaires)
        total_heures_sup = sum(s.heures_sup for s in salaires)
        total_primes = sum(s.primes for s in salaires)
        total_deductions = sum(s.deductions for s in salaires)
        
        return {
            "periode": f"{annee}-{mois:02d}",
            "nombre_employes": len(salaires),
            "total_salaire_brut": round(total_salaire_brut, 2),
            "total_salaire_net": round(total_salaire_net, 2),
            "total_heures_sup": round(total_heures_sup, 2),
            "total_primes": round(total_primes, 2),
            "total_deductions": round(total_deductions, 2)
        }
    
    @staticmethod
    def alertes_expirations(db: Session, jours_critique: int = 30) -> Dict[str, Any]:
        """Get expiring contracts and documents alerts"""
        date_limite = date.today() + timedelta(days=jours_critique)
        
        contrats_expirants = db.query(ContratTravail).filter(
            and_(
                ContratTravail.date_fin.isnot(None),
                ContratTravail.date_fin <= date_limite,
                ContratTravail.statut == "actif"
            )
        ).count()
        
        documents_expirants = db.query(DocumentEmploye).filter(
            and_(
                DocumentEmploye.date_expiration.isnot(None),
                DocumentEmploye.date_expiration <= date_limite
            )
        ).count()
        
        return {
            "jours_critique": jours_critique,
            "contrats_expirants": contrats_expirants,
            "documents_expirants": documents_expirants,
            "date_limite": date_limite
        }


class MagasinReportingService:
    """Warehouse reporting and analytics service"""
    
    @staticmethod
    def rapport_rotation_stock(db: Session, article_id: int, jours: int = 90) -> Dict[str, Any]:
        """Calculate stock turnover rate"""
        date_debut = date.today() - timedelta(days=jours)
        
        sorties = db.query(func.sum(MouvementStock.quantite)).filter(
            and_(
                MouvementStock.article_id == article_id,
                MouvementStock.type_mouvement == "sortie",
                MouvementStock.date_mouvement >= date_debut
            )
        ).scalar() or 0
        
        stock_actuel = db.query(Stock.quantite).filter(
            Stock.article_id == article_id
        ).scalar() or 0
        
        rotation = (sorties / stock_actuel) * (365 / jours) if stock_actuel > 0 else 0
        
        return {
            "article_id": article_id,
            "periode_jours": jours,
            "sorties": sorties,
            "stock_moyen": stock_actuel,
            "rotation": round(rotation, 2)
        }
    
    @staticmethod
    def rapport_ruptures(db: Session, seuil: float = 10.0) -> Dict[str, Any]:
        """Generate stock-out report"""
        stocks_bas = db.query(Stock).filter(
            Stock.quantite_disponible < seuil
        ).all()
        
        return {
            "seuil": seuil,
            "articles_en_rupture": len(stocks_bas),
            "articles": [
                {"article_id": s.article_id, "quantite": s.quantite_disponible}
                for s in stocks_bas
            ]
        }
    
    @staticmethod
    def rapport_precision_inventaire(db: Session, entrepot_id: int) -> Dict[str, Any]:
        """Generate inventory accuracy report"""
        dernier_inventaire = db.query(InventaireTournant).filter(
            and_(
                InventaireTournant.entrepot_id == entrepot_id,
                InventaireTournant.statut == "valide"
            )
        ).order_by(InventaireTournant.date_inventaire.desc()).first()
        
        if not dernier_inventaire:
            return {"entrepot_id": entrepot_id, "precision": 0, "note": "Pas d'inventaire"}
        
        from app.models.magasin_avance import LigneInventaire
        lignes = db.query(LigneInventaire).filter(
            LigneInventaire.inventaire_id == dernier_inventaire.id
        ).all()
        
        lignes_correctes = sum(1 for l in lignes if l.ecart == 0)
        precision = (lignes_correctes / len(lignes)) * 100 if lignes else 0
        
        return {
            "entrepot_id": entrepot_id,
            "date_inventaire": dernier_inventaire.date_inventaire,
            "lignes_total": len(lignes),
            "lignes_correctes": lignes_correctes,
            "precision": round(precision, 2)
        }
    
    @staticmethod
    def rapport_peremptions(db: Session, jours_critique: int = 30) -> Dict[str, Any]:
        """Generate expiration report"""
        date_limite = date.today() + timedelta(days=jours_critique)
        
        peremptions_critiques = db.query(Peremption).join(Stock).filter(
            and_(
                Peremption.date_peremption <= date_limite,
                Peremption.date_peremption >= date.today(),
                Stock.quantite > 0
            )
        ).count()
        
        peremptions_expirees = db.query(Peremption).join(Stock).filter(
            and_(
                Peremption.date_peremption < date.today(),
                Stock.quantite > 0
            )
        ).count()
        
        return {
            "jours_critique": jours_critique,
            "peremptions_critiques": peremptions_critiques,
            "peremptions_expirees": peremptions_expirees
        }
    
    @staticmethod
    def rapport_fournisseurs(db: Session, debut: date, fin: date) -> List[Dict[str, Any]]:
        """Generate supplier performance report"""
        commandes = db.query(CommandeFournisseur).filter(
            and_(
                CommandeFournisseur.date_commande >= debut,
                CommandeFournisseur.date_commande <= fin
            )
        ).all()
        
        fournisseurs = {}
        for cmd in commandes:
            if cmd.fournisseur_id not in fournisseurs:
                fournisseurs[cmd.fournisseur_id] = {
                    "fournisseur_id": cmd.fournisseur_id,
                    "commandes": 0,
                    "livrees": 0
                }
            fournisseurs[cmd.fournisseur_id]["commandes"] += 1
            if cmd.statut == "recu":
                fournisseurs[cmd.fournisseur_id]["livrees"] += 1
        
        for f_id, data in fournisseurs.items():
            taux = (data["livrees"] / data["commandes"]) * 100 if data["commandes"] > 0 else 0
            data["taux_livraison"] = round(taux, 2)
        
        return list(fournisseurs.values())


class TransportReportingService:
    """Transport reporting and analytics service"""
    
    @staticmethod
    def rapport_livraison_ponctuelle(db: Session, debut: date, fin: date) -> Dict[str, Any]:
        """Generate on-time delivery report"""
        livraisons = db.query(Livraison).filter(
            and_(
                Livraison.date_livraison_reelle >= debut,
                Livraison.date_livraison_reelle <= fin
            )
        ).all()
        
        if not livraisons:
            return {"periode": f"{debut} à {fin}", "taux_ponctualite": 0, "total": 0}
        
        ponctuelles = sum(
            1 for l in livraisons 
            if l.date_livraison_reelle and l.date_livraison_reelle <= l.fenetre_horaire_fin
        )
        
        taux = (ponctuelles / len(livraisons)) * 100
        
        return {
            "periode": f"{debut} à {fin}",
            "total_livraisons": len(livraisons),
            "livraisons_ponctuelles": ponctuelles,
            "taux_ponctualite": round(taux, 2)
        }
    
    @staticmethod
    def rapport_cout_mission(db: Session, debut: date, fin: date) -> Dict[str, Any]:
        """Generate cost per mission report"""
        missions = db.query(Mission).filter(
            and_(
                Mission.date_debut >= debut,
                Mission.date_fin <= fin
            )
        ).all()
        
        total_missions = len(missions)
        total_kilometres = sum(m.kilometrage or 0 for m in missions)
        
        return {
            "periode": f"{debut} à {fin}",
            "total_missions": total_missions,
            "total_kilometres": total_kilometres,
            "km_par_mission": round(total_kilometres / total_missions, 2) if total_missions > 0 else 0
        }
    
    @staticmethod
    def rapport_accidents(db: Session, debut: date, fin: date) -> Dict[str, Any]:
        """Generate accident statistics report"""
        accidents = db.query(AccidentTransport).filter(
            and_(
                AccidentTransport.date_accident >= datetime.combine(debut, datetime.min.time()),
                AccidentTransport.date_accident <= datetime.combine(fin, datetime.max.time())
            )
        ).all()
        
        total = len(accidents)
        avec_blessures = sum(1 for a in accidents if a.blessures and a.blessures.lower() != "aucune")
        
        return {
            "periode": f"{debut} à {fin}",
            "total_accidents": total,
            "avec_blessures": avec_blessures,
            "taux_blessures": round((avec_blessures / total) * 100, 2) if total > 0 else 0
        }
    
    @staticmethod
    def rapport_maintenance(db: Session, mois: int, annee: int) -> Dict[str, Any]:
        """Generate preventive maintenance report"""
        maintenances = db.query(MaintenancePreventive).filter(
            and_(
                MaintenancePreventive.date_prevue >= date(annee, mois, 1),
                MaintenancePreventive.date_prevue <= (date(annee, mois + 1, 1) - timedelta(days=1)) if mois < 12 else date(annee, 12, 31)
            )
        ).all()
        
        planifiees = len(maintenances)
        executees = sum(1 for m in maintenances if m.statut == "execute")
        en_retard = sum(1 for m in maintenances if m.statut == "planifie" and m.date_prevue < date.today())
        
        return {
            "periode": f"{annee}-{mois:02d}",
            "maintenances_planifiees": planifiees,
            "maintenances_executees": executees,
            "en_retard": en_retard,
            "taux_execution": round((executees / planifiees) * 100, 2) if planifiees > 0 else 0
        }
    
    @staticmethod
    def rapport_utilisation_vehicules(db: Session, vehicule_id: int, jours: int = 30) -> Dict[str, Any]:
        """Generate vehicle utilization report"""
        date_debut = date.today() - timedelta(days=jours)
        
        temps = db.query(func.sum(TempsConduite.duree_heures)).filter(
            and_(
                TempsConduite.vehicule_id == vehicule_id,
                TempsConduite.debut_conduite >= datetime.combine(date_debut, datetime.min.time())
            )
        ).scalar() or 0
        
        heures_disponibles = jours * 24
        taux = (temps / heures_disponibles) * 100
        
        return {
            "vehicule_id": vehicule_id,
            "periode_jours": jours,
            "heures_utilisation": round(temps, 2),
            "heures_disponibles": heures_disponibles,
            "taux_utilisation": round(taux, 2)
        }


class DashboardReportingService:
    """Dashboard KPI aggregation service"""
    
    @staticmethod
    def tableau_bord_global(db: Session) -> Dict[str, Any]:
        """Generate global dashboard KPIs"""
        from app.models.user import User
        
        # RH KPIs
        effectif = db.query(User).filter(User.is_active == True).count()
        
        # Warehouse KPIs
        total_stock = db.query(func.sum(Stock.quantite)).scalar() or 0
        valeur_stock = total_stock  # Simplified
        
        # Transport KPIs
        missions_activees = db.query(Mission).filter(
            Mission.statut == "en_cours"
        ).count()
        
        return {
            "date": date.today(),
            "rh": {
                "effectif": effectif
            },
            "magasin": {
                "total_stock": total_stock,
                "valeur_estimee": valeur_stock
            },
            "transport": {
                "missions_activees": missions_activees
            }
        }
