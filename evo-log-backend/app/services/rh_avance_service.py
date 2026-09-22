"""RH avancée service - Paie OHADA Cameroon, Recrutement, Formations"""
from datetime import datetime, date, timedelta
from typing import List, Optional, Dict, Any
from sqlalchemy.orm import Session
from sqlalchemy import and_, func
from app.models.rh import Conge, Absence, TempsTravail
from app.models.user import User


class PaieOHADAService:
    """Service de paie OHADA Cameroon"""
    
    @staticmethod
    def bulletin_paie_complet(
        db: Session,
        employe_id: int,
        periode: str
    ) -> Dict[str, Any]:
        """Générer un bulletin de paie complet OHADA"""
        employe = db.query(User).filter(User.id == employe_id).first()
        if not employe:
            raise ValueError("Employé non trouvé")
        
        # Salaire de base
        salaire_base = 500000  # Placeholder - devrait venir de la fiche employé
        
        # Heures supplémentaires
        heures_sup = db.query(func.sum(TempsTravail.heures_sup)).filter(
            and_(
                TempsTravail.employe_id == employe_id,
                TempsTravail.periode == periode
            )
        ).scalar() or 0
        
        taux_horaire_sup = salaire_base / 160  # 160h par mois
        montant_heures_sup = heures_sup * taux_horaire_sup * 1.25  # +25%
        
        # Primes diverses
        primes = 50000  # Placeholder
        
        # Salaire brut
        salaire_brut = salaire_base + montant_heures_sup + primes
        
        # Charges salariales employé
        cnps_retraites = salaire_brut * 0.042  # 4.2%
        cnps_accidents = salaire_brut * 0.005  # 0.5%
        total_cnps = cnps_retraites + cnps_accidents
        
        # IRGM (Impôt sur revenus)
        # Barème progressif Cameroun
        base_imposable = salaire_brut - total_cnps
        irgm = PaieOHADAService.calculer_irmg(base_imposable)
        
        # Net à payer
        net_a_payer = salaire_brut - total_cnps - irgm
        
        return {
            "employe_id": employe_id,
            "employe_nom": employe.full_name,
            "periode": periode,
            "salaire_base": salaire_base,
            "heures_supplementaires": heures_sup,
            "montant_heures_sup": montant_heures_sup,
            "primes": primes,
            "salaire_brut": salaire_brut,
            "cnps_retraites": cnps_retraites,
            "cnps_accidents": cnps_accidents,
            "total_cnps": total_cnps,
            "irmg": irgm,
            "net_a_payer": net_a_payer,
            "devise": "XAF"
        }
    
    @staticmethod
    def calculer_irmg(base_imposable: float) -> float:
        """Calculer l'IRGM selon barème Cameroun"""
        # Barème simplifié Cameroun 2026
        if base_imposable <= 50000:
            return 0
        elif base_imposable <= 100000:
            return (base_imposable - 50000) * 0.10
        elif base_imposable <= 200000:
            return 5000 + (base_imposable - 100000) * 0.15
        elif base_imposable <= 500000:
            return 20000 + (base_imposable - 200000) * 0.20
        elif base_imposable <= 1000000:
            return 80000 + (base_imposable - 500000) * 0.25
        else:
            return 205000 + (base_imposable - 1000000) * 0.30
    
    @staticmethod
    def charges_sociales(
        db: Session,
        employe_id: int,
        periode: str
    ) -> Dict[str, Any]:
        """Calculer les charges sociales OHADA"""
        # Récupérer le salaire brut
        salaire_brut = 500000  # Placeholder
        
        # CNPS
        cnps_retraites = salaire_brut * 0.042
        cnps_accidents = salaire_brut * 0.005
        cnps_total = cnps_retraites + cnps_accidents
        
        # Taxe apprentissage
        taxe_apprentissage = salaire_brut * 0.0025
        
        # Fonds de promotion
        fonds_promotion = salaire_brut * 0.001
        
        total_charges = cnps_total + taxe_apprentissage + fonds_promotion
        
        return {
            "employe_id": employe_id,
            "periode": periode,
            "salaire_brut": salaire_brut,
            "cnps_retraites": cnps_retraites,
            "cnps_accidents": cnps_accidents,
            "cnps_total": cnps_total,
            "taxe_apprentissage": taxe_apprentissage,
            "fonds_promotion": fonds_promotion,
            "total_charges": total_charges,
            "devise": "XAF"
        }
    
    @staticmethod
    def declaration_cnps(
        db: Session,
        periode: str
    ) -> Dict[str, Any]:
        """Déclaration CNPS mensuelle"""
        # Récupérer tous les employés
        employes = db.query(User).filter(User.is_active == True).all()
        
        total_salaires = 0
        total_cnps = 0
        
        for employe in employes:
            salaire_brut = 500000  # Placeholder
            total_salaires += salaire_brut
            total_cnps += salaire_brut * 0.047  # 4.2% + 0.5%
        
        return {
            "periode": periode,
            "nombre_employes": len(employes),
            "total_salaires": total_salaires,
            "total_cnps": total_cnps,
            "date_declaration": date.today(),
            "statut": "a_deposer"
        }
    
    @staticmethod
    def dipe_declaration(
        db: Session,
        periode: str
    ) -> Dict[str, Any]:
        """DIPE - Déclaration Employeur"""
        return {
            "periode": periode,
            "nombre_employes": 0,
            "masse_salariale": 0,
            "charges_sociales": 0,
            "statut": "a_deposer"
        }


class RecrutementService:
    """Service de recrutement"""
    
    @staticmethod
    def creer_offre_emploi(
        db: Session,
        titre: str,
        description: str,
        departement: str,
        profil_requis: str,
        date_limite: date
    ) -> Dict[str, Any]:
        """Créer une offre d'emploi"""
        # Placeholder - modèle OffreEmploi à créer
        return {
            "titre": titre,
            "description": description,
            "departement": departement,
            "profil_requis": profil_requis,
            "date_limite": date_limite,
            "statut": "active",
            "date_creation": date.today()
        }
    
    @staticmethod
    def traiter_candidature(
        db: Session,
        candidature_id: int,
        decision: str,
        notes: Optional[str] = None
    ) -> Dict[str, Any]:
        """Traiter une candidature"""
        return {
            "candidature_id": candidature_id,
            "decision": decision,
            "notes": notes,
            "date_decision": date.today()
        }


class FormationService:
    """Service de formation"""
    
    @staticmethod
    def plan_formation_annuel(
        db: Session,
        exercice_id: int
    ) -> Dict[str, Any]:
        """Plan de formation annuel"""
        return {
            "exercice_id": exercice_id,
            "budget_formation": 5000000,
            "nombre_formations": 10,
            "statut": "en_cours"
        }
    
    @staticmethod
    def inscrire_formation(
        db: Session,
        employe_id: int,
        formation_id: int
    ) -> Dict[str, Any]:
        """Inscrire un employé à une formation"""
        return {
            "employe_id": employe_id,
            "formation_id": formation_id,
            "date_inscription": date.today(),
            "statut": "inscrit"
        }