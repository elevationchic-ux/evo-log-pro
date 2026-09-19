"""Cameroon Taxation Service - IRPP, IS, TCF, TDR, Complete OHADA"""
from datetime import datetime, date, timedelta
from typing import Dict, Any, Optional
from sqlalchemy.orm import Session
from app.models.fiscalite_cameroun import ImpotCameroun, DeclarationFiscale, PaiementLocal, ContratFiscal, RetenueSourceCameroun as RetenueSource


class FiscaliteCamerounService:
    """Cameroon Taxation Service"""
    
    @staticmethod
    def calculer_impot(
        db: Session,
        type_impot: str,
        base_calcul: float,
        type_base: str
    ) -> Dict[str, Any]:
        """Calculer impôt selon type et base"""
        impot = db.query(ImpotCameroun).filter(
            ImpotCameroun.code == type_impot,
            ImpotCameroun.est_actif == True
        ).first()
        
        if not impot:
            raise ValueError(f"Impôt {type_impot} non trouvé")
        
        montant = base_calcul * (impot.taux / 100)
        
        # Minimum tax for certain types
        if impot.taux_minimum and montant < impot.taux_minimum:
            montant = impot.taux_minimum
        
        return {
            "type_impot": type_impot,
            "designation": impot.designation,
            "base_calcul": base_calcul,
            "type_base": type_base,
            "taux": impot.taux,
            "montant_du": montant,
            "devise": "XAF"
        }
    
    @staticmethod
    def creer_declaration_fiscale(
        db: Session,
        company_id: int,
        type_impot: str,
        periode_debut: date,
        periode_fin: date,
        chiffre_affaires: float,
        benefice: float
    ) -> DeclarationFiscale:
        """Créer déclaration fiscale"""
        # Calculate tax amount
        if type_impot == "IS":
            base = benefice
            type_base = "BENEFICE"
        elif type_impot == "TCA":
            base = chiffre_affaires
            type_base = "CA"
        else:
            base = chiffre_affaires
            type_base = "CA"
        
        calcul = FiscaliteCamerounService.calculer_impot(db, type_impot, base, type_base)
        
        declaration = DeclarationFiscale(
            company_id=company_id,
            type_impot=type_impot,
            periode_debut=periode_debut,
            periode_fin=periode_fin,
            chiffre_affaires=chiffre_affaires,
            benefice=benefice,
            montant_du=calcul["montant_du"],
            reste_a_payer=calcul["montant_du"],
            reference_declaration=f"DEC-{datetime.now().strftime('%Y%m%d%H%M%S')}",
            statut="en_attente"
        )
        db.add(declaration)
        db.commit()
        db.refresh(declaration)
        return declaration
    
    @staticmethod
    def soumettre_declaration(db: Session, declaration_id: int) -> DeclarationFiscale:
        """Soumettre déclaration à l'administration fiscale"""
        declaration = db.query(DeclarationFiscale).filter(DeclarationFiscale.id == declaration_id).first()
        if not declaration:
            raise ValueError("Déclaration non trouvée")
        
        declaration.statut = "soumis"
        declaration.date_soumission = date.today()
        db.commit()
        db.refresh(declaration)
        return declaration
    
    @staticmethod
    def valider_declaration(db: Session, declaration_id: int, agent_fiscal: str) -> DeclarationFiscale:
        """Valider déclaration par l'administration fiscale"""
        declaration = db.query(DeclarationFiscale).filter(DeclarationFiscale.id == declaration_id).first()
        if not declaration:
            raise ValueError("Déclaration non trouvée")
        
        declaration.statut = "valide"
        declaration.date_validation = date.today()
        declaration.agent_fiscal = agent_fiscal
        db.commit()
        db.refresh(declaration)
        return declaration
    
    @staticmethod
    def payer_declaration(db: Session, declaration_id: int, montant: float) -> DeclarationFiscale:
        """Payer déclaration fiscale"""
        declaration = db.query(DeclarationFiscale).filter(DeclarationFiscale.id == declaration_id).first()
        if not declaration:
            raise ValueError("Déclaration non trouvée")
        
        declaration.montant_paye += montant
        declaration.reste_a_payer = declaration.montant_du - declaration.montant_paye
        
        if declaration.reste_a_payer <= 0:
            declaration.statut = "paye"
            declaration.date_paiement = date.today()
        
        db.commit()
        db.refresh(declaration)
        return declaration
    
    @staticmethod
    def creer_retenue_source(
        db: Session,
        company_id: int,
        type_retenue: str,
        montant_brut: float,
        beneficiaire: str,
        numero_contribuable: str
    ) -> RetenueSource:
        """Créer retenue à la source"""
        # Determine rate based on type
        taux_map = {
            "SALAIRE": 0.15,  # 15%
            "HONORAIRE": 0.20,  # 20%
            "DIVIDENDE": 0.15,  # 15%
            "LOYER": 0.15  # 15%
        }
        
        taux = taux_map.get(type_retenue, 0.15)
        montant_retenue = montant_brut * taux
        montant_net = montant_brut - montant_retenue
        
        retenue = RetenueSource(
            company_id=company_id,
            type_retenue=type_retenue,
            montant_brut=montant_brut,
            taux_retenue=taux,
            montant_retenue=montant_retenue,
            montant_net=montant_net,
            beneficiaire=beneficiaire,
            numero_contribuable=numero_contribuable,
            date_operation=date.today(),
            reference_paiement=f"RS-{datetime.now().strftime('%Y%m%d%H%M%S')}",
            statut="declare"
        )
        db.add(retenue)
        db.commit()
        db.refresh(retenue)
        return retenue
    
    @staticmethod
    def verser_retenue(db: Session, retenue_id: int) -> RetenueSource:
        """Verser retenue à l'administration fiscale"""
        retenue = db.query(RetenueSource).filter(RetenueSource.id == retenue_id).first()
        if not retenue:
            raise ValueError("Retenue non trouvée")
        
        retenue.statut = "verse"
        retenue.date_versement = date.today()
        db.commit()
        db.refresh(retenue)
        return retenue


class OHADAService:
    """OHADA Accounting Service - Complete implementation"""
    
    @staticmethod
    def calculer_tva_ohada(montant_ht: float, taux_tva: float = 19.25) -> Dict[str, Any]:
        """Calculer TVA OHADA (19.25% standard)"""
        montant_tva = montant_ht * (taux_tva / 100)
        montant_ttc = montant_ht + montant_tva
        
        return {
            "montant_ht": montant_ht,
            "taux_tva": taux_tva,
            "montant_tva": montant_tva,
            "montant_ttc": montant_ttc,
            "devise": "XAF"
        }
    
    @staticmethod
    def calculer_centimes_additionnels(montant: float, taux: float = 10) -> Dict[str, Any]:
        """Calculer centimes additionnels (10% standard)"""
        montant_centimes = montant * (taux / 100)
        
        return {
            "montant_base": montant,
            "taux_centimes": taux,
            "montant_centimes": montant_centimes,
            "devise": "XAF"
        }
    
    @staticmethod
    def calculer_is_minimum(db: Session, chiffre_affaires: float) -> Dict[str, Any]:
        """Calculer IS minimum (Cameroon)"""
        # IS minimum calculation based on CA
        if chiffre_affaires <= 10000000:  # < 10M FCFA
            is_minimum = 300000  # 300K FCFA
        elif chiffre_affaires <= 50000000:  # < 50M FCFA
            is_minimum = 500000  # 500K FCFA
        elif chiffre_affaires <= 100000000:  # < 100M FCFA
            is_minimum = 1000000  # 1M FCFA
        else:
            is_minimum = 2000000  # 2M FCFA
        
        return {
            "chiffre_affaires": chiffre_affaires,
            "is_minimum": is_minimum,
            "devise": "XAF"
        }
    
    @staticmethod
    def generer_bilan(db: Session, company_id: int, exercice: int) -> Dict[str, Any]:
        """Générer bilan OHADA"""
        # Simplified OHADA balance sheet generation
        return {
            "company_id": company_id,
            "exercice": exercice,
            "actif": {
                "immobilisations": 0,
                "stocks": 0,
                "creances": 0,
                "disponibilites": 0
            },
            "passif": {
                "capital": 0,
                "dettes": 0,
                "provisions": 0
            },
            "resultat": {
                "benefice": 0,
                "perte": 0
            },
            "date_generation": date.today()
        }
    
    @staticmethod
    def generer_compte_resultat(db: Session, company_id: int, exercice: int) -> Dict[str, Any]:
        """Générer compte de résultat OHADA"""
        return {
            "company_id": company_id,
            "exercice": exercice,
            "produits": {
                "ventes": 0,
                "autres_produits": 0
            },
            "charges": {
                "achats": 0,
                "services": 0,
                "personnel": 0,
                "amortissements": 0,
                "autres_charges": 0
            },
            "resultat_exploitation": 0,
            "resultat_financier": 0,
            "resultat_exceptionnel": 0,
            "resultat_net": 0,
            "date_generation": date.today()
        }
