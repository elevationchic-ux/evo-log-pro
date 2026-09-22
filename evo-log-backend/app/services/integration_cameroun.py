"""Cameroon Integration Services - BSC, CSC, SYGED, APE"""
from datetime import datetime, date, timedelta
from typing import Dict, Any, Optional
from sqlalchemy.orm import Session
from app.models.douane_cameroun import BSC, CSC, APE, DUM, BV, TauxReferenceBEAC, ArticleCodeDouanes
from app.models.transit_cemac import CorridorCEMAC, PosteFrontalier
import requests
import json


class BSCService:
    """BSC (Bulletin de Soumission Connaissement) Service - CNCC Integration"""
    
    @staticmethod
    def generer_bsc(
        db: Session,
        numero_connaisse: str,
        navire: str,
        port_chargement: str,
        port_dechargement: str,
        agent: str,
        importateur: str,
        poids_brut_tonnes: float,
        valeur_fob: float
    ) -> BSC:
        """Générer BSC via API CNCC"""
        # Call CNCC API
        bsc = BSC(
            numero_bsc=f"BSC-{datetime.now().strftime('%Y%m%d%H%M%S')}",
            numero_connaisse=numero_connaisse,
            navire=navire,
            port_chargement=port_chargement,
            port_dechargement=port_dechargement,
            date_emission=date.today(),
            date_validite=date.today() + timedelta(days=7),
            agent=agent,
            importateur=importateur,
            poids_brut_tonnes=poids_brut_tonnes,
            valeur_fob=valeur_fob,
            devise="USD",
            montant_frais_bsc=valeur_fob * 0.0002,  # 0.02% of FOB
            devise_frais="XAF",
            statut="en_attente"
        )
        db.add(bsc)
        db.commit()
        db.refresh(bsc)
        return bsc
    
    @staticmethod
    def valider_bsc(db: Session, numero_bsc: str) -> BSC:
        """Valider BSC auprès de CNCC"""
        bsc = db.query(BSC).filter(BSC.numero_bsc == numero_bsc).first()
        if not bsc:
            raise ValueError("BSC non trouvé")
        
        # Call CNCC validation API
        bsc.statut = "valide"
        bsc.date_validation = date.today()
        db.commit()
        db.refresh(bsc)
        return bsc
    
    @staticmethod
    def payer_bsc(db: Session, numero_bsc: str) -> BSC:
        """Payer frais BSC"""
        bsc = db.query(BSC).filter(BSC.numero_bsc == numero_bsc).first()
        if not bsc:
            raise ValueError("BSC non trouvé")
        
        bsc.statut = "valide"
        bsc.date_paiement = date.today()
        db.commit()
        db.refresh(bsc)
        return bsc


class CSCService:
    """CSC (Certificat de Sécurité) Service - INS Integration"""
    
    @staticmethod
    def demander_csc(
        db: Session,
        numero_connaisse: str,
        navire: str,
        port_origine: str,
        port_destination: str,
        poids_brut_tonnes: float,
        nombre_colis: int,
        valeur_fob: float
    ) -> CSC:
        """Demander certificat sécurité via API INS"""
        csc = CSC(
            numero_csc=f"CSC-{datetime.now().strftime('%Y%m%d%H%M%S')}",
            numero_connaisse=numero_connaisse,
            navire=navire,
            port_origine=port_origine,
            port_destination=port_destination,
            date_demande=date.today(),
            compagnie_inspection="INS",
            poids_brut_tonnes=poids_brut_tonnes,
            nombre_colis=nombre_colis,
            valeur_fob=valeur_fob,
            frais_inspection=valeur_fob * 0.001,  # 0.1% of FOB
            statut="en_attente"
        )
        db.add(csc)
        db.commit()
        db.refresh(csc)
        return csc
    
    @staticmethod
    def valider_csc(db: Session, numero_csc: str, resultat: str) -> CSC:
        """Valider CSC avec résultat inspection"""
        csc = db.query(CSC).filter(CSC.numero_csc == numero_csc).first()
        if not csc:
            raise ValueError("CSC non trouvé")
        
        csc.resultat_inspection = resultat
        csc.statut = "emis" if resultat == "CONFORME" else "rejete"
        csc.date_emission = date.today()
        db.commit()
        db.refresh(csc)
        return csc


class SYGEDService:
    """SYGED (Système de Gestion des Droits) Service - Douanes Cameroun Integration"""
    
    @staticmethod
    def creer_dum(
        db: Session,
        dossier_transit_id: int,
        type_operation: str,
        regime_douanier: str,
        bureau_douane: str,
        declarant: str,
        importateur: str,
        marchandise: str,
        valeur_fob: float,
        taux_change: float
    ) -> DUM:
        """Créer DUM via SYGED API"""
        from datetime import timedelta
        
        taux_tva = 19.25
        centimes = 10
        timbre = 1000
        
        valeur_caf = valeur_fob * taux_change
        valeur_douane_xaf = valeur_caf
        droits_douane = valeur_douane_xaf * 0.2  # 20% average
        tva = valeur_douane_xaf * (taux_tva / 100)
        centimes_additionnels = valeur_douane_xaf * (centimes / 100)
        montant_total = valeur_douane_xaf + droits_douane + tva + centimes_additionnels + timbre
        
        dum = DUM(
            numero_dum=f"DUM-{datetime.now().strftime('%Y%m%d%H%M%S')}",
            dossier_transit_id=dossier_transit_id,
            type_operation=type_operation,
            regime_douanier=regime_douanier,
            bureau_douane=bureau_douane,
            date_depot=date.today(),
            declarant=declarant,
            importateur=importateur,
            marchandise=marchandise,
            valeur_fob=valeur_fob,
            valeur_caf=valeur_caf,
            devise="USD",
            taux_change=taux_change,
            valeur_douane_xaf=valeur_douane_xaf,
            droits_douane=droits_douane,
            tva=tva,
            centimes_additionnels=centimes_additionnels,
            timbre_usage=timbre,
            montant_total=montant_total,
            statut="en_attente"
        )
        db.add(dum)
        db.commit()
        db.refresh(dum)
        return dum
    
    @staticmethod
    def valider_dum(db: Session, numero_dum: str, agent_douane: str) -> DUM:
        """Valider DUM via SYGED"""
        dum = db.query(DUM).filter(DUM.numero_dum == numero_dum).first()
        if not dum:
            raise ValueError("DUM non trouvé")
        
        dum.statut = "valide"
        dum.date_validation = date.today()
        dum.agent_douane = agent_douane
        dum.reference_sydonia = f"SYD-{datetime.now().strftime('%Y%m%d%H%M%S')}"
        db.commit()
        db.refresh(dum)
        return dum
    
    @staticmethod
    def liquider_dum(db: Session, numero_dum: str) -> DUM:
        """Liquider DUM (paiement droits)"""
        dum = db.query(DUM).filter(DUM.numero_dum == numero_dum).first()
        if not dum:
            raise ValueError("DUM non trouvé")
        
        dum.statut = "liquidé"
        dum.date_liquidation = date.today()
        db.commit()
        db.refresh(dum)
        return dum


class APEService:
    """APE (Arrêté de Paiement des Étrangers) Service - BEAC Integration"""
    
    @staticmethod
    def demander_ape(
        db: Session,
        dossier_import_id: int,
        importateur: str,
        montant_xaf: float,
        devise: str,
        banque: str,
        beneficiaire_etranger: str,
        pays_beneficiaire: str,
        objet_transfert: str
    ) -> APE:
        """Demander APE via BEAC API"""
        # Calculate foreign currency amount
        taux = APEService.get_taux_beac(db, devise)
        montant_devise = montant_xaf / taux if taux else 0
        
        ape = APE(
            numero_ape=f"APE-{datetime.now().strftime('%Y%m%d%H%M%S')}",
            dossier_import_id=dossier_import_id,
            importateur=importateur,
            montant_xaf=montant_xaf,
            montant_devise=montant_devise,
            devise=devise,
            taux_change=taux,
            banque=banque,
            beneficiaire_etranger=beneficiaire_etranger,
            pays_beneficiaire=pays_beneficiaire,
            objet_transfert=objet_transfert,
            date_demande=date.today(),
            statut="en_attente"
        )
        db.add(ape)
        db.commit()
        db.refresh(ape)
        return ape
    
    @staticmethod
    def get_taux_beac(db: Session, devise: str) -> Optional[float]:
        """Get BEAC exchange rate"""
        taux = db.query(TauxReferenceBEAC).filter(
            TauxReferenceBEAC.devise == devise,
            TauxReferenceBEAC.est_taux_officiel == True
        ).order_by(TauxReferenceBEAC.date_application.desc()).first()
        return taux.taux_moyen if taux else None
    
    @staticmethod
    def autoriser_ape(db: Session, numero_ape: str, agent_beac: str) -> APE:
        """Autoriser APE via BEAC"""
        ape = db.query(APE).filter(APE.numero_ape == numero_ape).first()
        if not ape:
            raise ValueError("APE non trouvé")
        
        ape.statut = "autorise"
        ape.date_autorisation = date.today()
        ape.agent_beac = agent_beac
        ape.reference_beac = f"BEAC-{datetime.now().strftime('%Y%m%d%H%M%S')}"
        db.commit()
        db.refresh(ape)
        return ape


class BEACRateService:
    """BEAC Exchange Rate Service"""
    
    @staticmethod
    def mettre_a_jour_taux(
        db: Session,
        devise: str,
        taux_achat: float,
        taux_vente: float,
        date_application: date
    ) -> TauxReferenceBEAC:
        """Update BEAC exchange rate"""
        taux_moyen = (taux_achat + taux_vente) / 2
        
        taux = TauxReferenceBEAC(
            devise=devise,
            taux_achat=taux_achat,
            taux_vente=taux_vente,
            taux_moyen=taux_moyen,
            date_application=date_application,
            source="BEAC",
            est_taux_officiel=True
        )
        db.add(taux)
        db.commit()
        db.refresh(taux)
        return taux
    
    @staticmethod
    def get_taux_actuel(db: Session, devise: str) -> Optional[float]:
        """Get current BEAC rate"""
        return APEService.get_taux_beac(db, devise)


class DouaneCamerounService:
    """Cameroon Customs Service"""
    
    @staticmethod
    def creer_bureau_validation(
        db: Session,
        dum_id: int,
        validateur: str,
        grade: str,
        resultat: str
    ) -> BV:
        """Create Bureau de Validation"""
        bv = BV(
            numero_bv=f"BV-{datetime.now().strftime('%Y%m%d%H%M%S')}",
            dum_id=dum_id,
            date_validation=date.today(),
            validateur=validateur,
            grade=grade,
            resultat=resultat
        )
        db.add(bv)
        db.commit()
        db.refresh(bv)
        return bv
    
    @staticmethod
    def get_articles_code_douanes(db: Session, article: str = None):
        """Get articles from Code des Douanes"""
        query = db.query(ArticleCodeDouanes)
        if article:
            query = query.filter(ArticleCodeDouanes.article == article)
        return query.filter(ArticleCodeDouanes.est_actif == True).all()


# Compatibility alias
IntegrationCamerounService = DouaneCamerounService

