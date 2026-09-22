"""Finance avancée service - Trésorerie, Créances, Dettes, Budget"""
from datetime import datetime, date, timedelta
from typing import List, Optional, Dict, Any
from sqlalchemy.orm import Session
from sqlalchemy import and_, func
from app.models.finance_ohada import Reglement, FactureNew as Facture
from app.models.tiers import Client, Fournisseur


class TrésorerieService:
    """Service de trésorerie - Cash flow management"""
    
    @staticmethod
    def tableau_bord_tresorerie(
        db: Session,
        date_reference: date
    ) -> Dict[str, Any]:
        """Tableau de bord trésorerie"""
        # Encaissements du jour
        encaissements = db.query(func.sum(Reglement.montant)).filter(
            Reglement.date_reglement == date_reference
        ).scalar() or 0
        
        # Décaissements du jour
        decaissements = db.query(func.sum(Reglement.montant)).filter(
            and_(
                Reglement.date_reglement == date_reference,
                Reglement.mode_paiement.in_(["especes", "cheque", "virement"])
            )
        ).scalar() or 0
        
        # Solde de trésorerie
        solde_tresorerie = encaissements - decaissements
        
        # Créances à recevoir
        creances_a_recevoir = db.query(func.sum(Facture.solde_restant)).filter(
            Facture.statut.in_(["emise", "payee_partiel"])
        ).scalar() or 0
        
        # Dettes à payer
        dettes_a_payer = db.query(func.sum(Facture.solde_restant)).filter(
            Facture.type_facture == "achat"
        ).scalar() or 0
        
        return {
            "date": date_reference,
            "encaissements": encaissements,
            "decaissements": decaissements,
            "solde_tresorerie": solde_tresorerie,
            "creances_a_recevoir": creances_a_recevoir,
            "dettes_a_payer": dettes_a_payer,
            "besoin_fdr": creances_a_recevoir - dettes_a_payer
        }
    
    @staticmethod
    def previsions_tresorerie(
        db: Session,
        horizon_jours: int = 30
    ) -> Dict[str, Any]:
        """Prévisions de trésorerie"""
        date_fin = date.today() + timedelta(days=horizon_jours)
        
        # Encaissements prévus (factures à recevoir)
        encaissements_prevus = db.query(func.sum(Facture.solde_restant)).filter(
            and_(
                Facture.statut.in_(["emise", "payee_partiel"]),
                Facture.date_echeance <= date_fin
            )
        ).scalar() or 0
        
        # Décaissements prévus (factures à payer)
        decaissements_prevus = db.query(func.sum(Facture.solde_restant)).filter(
            and_(
                Facture.type_facture == "achat",
                Facture.date_echeance <= date_fin
            )
        ).scalar() or 0
        
        return {
            "horizon_jours": horizon_jours,
            "date_debut": date.today(),
            "date_fin": date_fin,
            "encaissements_prevus": encaissements_prevus,
            "decaissements_prevus": decaissements_prevus,
            "solde_prevu": encaissements_prevus - decaissements_prevus
        }
    
    @staticmethod
    def calcul_bfr(
        db: Session,
        periode: str
    ) -> Dict[str, Any]:
        """Calculer le Besoin en Fonds de Roulement"""
        # Stock moyen
        stock_moyen = 1000000  # Placeholder
        
        # Créances clients
        creances_clients = db.query(func.sum(Facture.solde_restant)).filter(
            Facture.type_facture == "vente"
        ).scalar() or 0
        
        # Dettes fournisseurs
        dettes_fournisseurs = db.query(func.sum(Facture.solde_restant)).filter(
            Facture.type_facture == "achat"
        ).scalar() or 0
        
        bfr = stock_moyen + creances_clients - dettes_fournisseurs
        
        return {
            "periode": periode,
            "stock_moyen": stock_moyen,
            "creances_clients": creances_clients,
            "dettes_fournisseurs": dettes_fournisseurs,
            "bfr": bfr
        }


class GestionCreancesService:
    """Service de gestion des créances"""
    
    @staticmethod
    def balance_agee_clients(
        db: Session,
        date_reference: date
    ) -> List[Dict[str, Any]]:
        """Balance âgée clients"""
        clients = db.query(Client).all()
        
        balance_agee = []
        for client in clients:
            factures = db.query(Facture).filter(
                and_(
                    Facture.client_id == client.id,
                    Facture.statut.in_(["emise", "payee_partiel"])
                )
            ).all()
            
            total_solde = sum(f.solde_restant for f in factures)
            
            if total_solde > 0:
                balance_agee.append({
                    "client_id": client.id,
                    "client_nom": client.nom,
                    "total_solde": total_solde,
                    "nombre_factures": len(factures)
                })
        
        return balance_agee
    
    @staticmethod
    def analyse_dso(
        db: Session,
        periode: str
    ) -> Dict[str, Any]:
        """Analyse DSO (Days Sales Outstanding)"""
        # Simplifié - DSO = (Crances / Ventes moyennes quotidiennes) * 365
        from datetime import datetime, timedelta
        
        periode_fin = datetime.strptime(periode, "%Y-%m").replace(day=1) + timedelta(days=32)
        periode_fin = periode_fin.replace(day=1) - timedelta(days=1)
        
        # Crances à la fin de la période
        creances = db.query(func.sum(Facture.solde_restant)).filter(
            Facture.type_facture == "vente"
        ).scalar() or 0
        
        # Ventes de la période
        ventes = db.query(func.sum(Facture.montant_ttc)).filter(
            and_(
                Facture.type_facture == "vente",
                Facture.date_emission >= periode_fin.replace(day=1),
                Facture.date_emission <= periode_fin
            )
        ).scalar() or 0
        
        jours_periode = (periode_fin - periode_fin.replace(day=1)).days
        ventes_quotidiennes = ventes / jours_periode if jours_periode > 0 else 0
        
        dso = (creances / ventes_quotidiennes) if ventes_quotidiennes > 0 else 0
        
        return {
            "periode": periode,
            "creances": creances,
            "ventes": ventes,
            "jours_periode": jours_periode,
            "ventes_quotidiennes": ventes_quotidiennes,
            "dso": dso
        }
    
    @staticmethod
    def scoring_client(
        db: Session,
        client_id: int
    ) -> Dict[str, Any]:
        """Scoring client"""
        client = db.query(Client).filter(Client.id == client_id).first()
        if not client:
            raise ValueError("Client non trouvé")
        
        factures = db.query(Facture).filter(Facture.client_id == client_id).all()
        
        nombre_factures = len(factures)
        factures_en_retard = sum(1 for f in factures if f.statut == "payee_partiel")
        
        # Calcul du score (0-100)
        taux_paiement = ((nombre_factures - factures_en_retard) / nombre_factaires * 100) if nombre_factires > 0 else 100
        
        score = taux_paiement
        
        return {
            "client_id": client_id,
            "client_nom": client.nom,
            "nombre_factures": nombre_factures,
            "factures_en_retard": factures_en_retard,
            "taux_paiement": taux_paiement,
            "score": score
        }


class GestionDettesService:
    """Service de gestion des dettes"""
    
    @staticmethod
    def balance_agee_fournisseurs(
        db: Session,
        date_reference: date
    ) -> List[Dict[str, Any]]:
        """Balance âgée fournisseurs"""
        fournisseurs = db.query(Fournisseur).all()
        
        balance_agee = []
        for fournisseur in fournisseurs:
            factures = db.query(Facture).filter(
                and_(
                    Facture.fournisseur_id == fournisseur.id,
                    Facture.type_facture == "achat",
                    Facture.statut.in_(["emise", "payee_partiel"])
                )
            ).all()
            
            total_solde = sum(f.solde_restant for f in factures)
            
            if total_solde > 0:
                balance_agee.append({
                    "fournisseur_id": fournisseur.id,
                    "fournisseur_nom": fournisseur.nom,
                    "total_solde": total_solde,
                    "nombre_factures": len(factures)
                })
        
        return balance_agee
    
    @staticmethod
    def analyse_dpo(
        db: Session,
        periode: str
    ) -> Dict[str, Any]:
        """Analyse DPO (Days Payable Outstanding)"""
        from datetime import datetime, timedelta
        
        periode_fin = datetime.strptime(periode, "%Y-%m").replace(day=1) + timedelta(days=32)
        periode_fin = periode_fin.replace(day=1) - timedelta(days=1)
        
        # Dettes à la fin de la période
        dettes = db.query(func.sum(Facture.solde_restant)).filter(
            Facture.type_factire == "achat"
        ).scalar() or 0
        
        # Achats de la période
        achats = db.query(func.sum(Facture.montant_ttc)).filter(
            and_(
                Facture.type_facture == "achat",
                Facture.date_emission >= periode_fin.replace(day=1),
                Facture.date_emission <= periode_fin
            )
        ).scalar() or 0
        
        jours_periode = (periode_fin - periode_fin.replace(day=1)).days
        achats_quotidiens = achats / jours_periode if jours_periode > 0 else 0
        
        dpo = (dettes / achats_quotidiens) if achats_quotidiens > 0 else 0
        
        return {
            "periode": periode,
            "dettes": dettes,
            "achats": achats,
            "jours_periode": jours_periode,
            "achats_quotidiens": achats_quotidiens,
            "dpo": dpo
        }


class BudgetPrevisionsService:
    """Service de budget et prévisions"""
    
    @staticmethod
    def creer_budget_annuel(
        db: Session,
        exercice_id: int,
        budget_data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Créer un budget annuel"""
        # Placeholder - implémentation future avec modèle Budget
        return {
            "exercice_id": exercice_id,
            "budget_total": budget_data.get("total", 0),
            "statut": "actif"
        }
    
    @staticmethod
    def suivi_realise_vs_budget(
        db: Session,
        exercice_id: int,
        periode: str
    ) -> Dict[str, Any]:
        """Suivi réalisé vs budget"""
        # Placeholder - comparaison des dépenses réelles vs budget
        return {
            "exercice_id": exercice_id,
            "periode": periode,
            "budget": 1000000,
            "realise": 750000,
            "ecart": -250000,
            "taux_realisation": 75
        }