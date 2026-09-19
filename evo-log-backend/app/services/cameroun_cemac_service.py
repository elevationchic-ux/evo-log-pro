"""Cameroon/CEMAC integration service - Configuration-driven for SYDONIA+, GUICHET UNIQUE, OHADA"""
from datetime import datetime, date, timedelta
from typing import Dict, List, Optional, Any
from pydantic import BaseModel
import json


class CamerounConfig(BaseModel):
    """Configuration for Cameroon-specific business rules
    
    NOTE: All rates and rules must be validated against current official
    Cameroon/CEMAC regulations before production use. This provides a
    configuration structure to manage such rules.
    """
    # Currency
    devise: str = "XAF"
    taux_echange_xaf_eur: float = 655.957  # To be updated periodically
    
    # Tax rates (CONFIGURATION REQUIRED - subject to change)
    taux_tva: float = 0.1925  # 19.25% standard VAT
    taux_tva_reduit: float = 0.05  # 5% reduced VAT
    taux_is: float = 0.33  # 33% corporate tax
    taux_irpp: float = 0.35  # 35% personal income tax max rate
    
    # Social contributions (CONFIGURATION REQUIRED - subject to change)
    taux_cnps_employe: float = 0.07  # 7% employee CNPS
    taux_cnps_employeur: float = 0.115  # 11.5% employer CNPS
    
    # Labor law (Cameroon Labor Code)
    conges_annuels_jours: float = 2.5  # 2.5 days per month
    heures_travail_hebdo: int = 40  # 40 hours weekly
    periode_essai_cdi_jours: int = 90  # 3 months for CDI
    salaire_minimum: float = 41664  # SMIG 2024 (XAF)
    
    # Transport regulations
    max_heures_conduite_journalier: float = 9.0
    max_heures_conduite_sans_pause: float = 4.5
    pause_minimale_minutes: int = 45
    
    # Customs/Trade
    code_pays_iso: str = "CM"
    code_devise_iso: str = "XAF"
    code_zone_cefac: str = "CEMAC"
    
    # Integration endpoints (placeholder - to be configured)
    sydonia_plus_url: Optional[str] = None
    guichet_unique_url: Optional[str] = None
    api_key_sydonia: Optional[str] = None
    api_key_guichet: Optional[str] = None


class OHADAComptabiliteService:
    """OHADA accounting structure service - Configuration-driven"""
    
    @staticmethod
    def generer_plan_comptable_ohada() -> Dict[str, Any]:
        """
        Generate OHADA chart of accounts structure
        This is a template - actual account codes must be configured
        according to SYSCOHADA requirements
        """
        return {
            "classe_1": {
                "nom": "Ressources durables",
                "comptes": [
                    "10 - Capital",
                    "12 - Résultat",
                    "16 - Emprunts et dettes",
                    "17 - Dettes rattachées"
                ]
            },
            "classe_2": {
                "nom": "Immobilisations",
                "comptes": [
                    "21 - Immobilisations corporelles",
                    "22 - Immobilisations incorporelles",
                    "23 - Immobilisations en cours"
                ]
            },
            "classe_3": {
                "nom": "Stocks",
                "comptes": [
                    "31 - Marchandises",
                    "32 - Matières premières",
                    "33 - Produits finis"
                ]
            },
            "classe_4": {
                "nom": "Tiers",
                "comptes": [
                    "40 - Fournisseurs",
                    "41 - Clients",
                    "42 - Personnel",
                    "44 - État et collectivités"
                ]
            },
            "classe_5": {
                "nom": "Trésorerie",
                "comptes": [
                    "50 - Valeurs mobilières",
                    "51 - Banques",
                    "57 - Caisse"
                ]
            },
            "classe_6": {
                "nom": "Charges",
                "comptes": [
                    "60 - Achats",
                    "61 - Services extérieurs",
                    "62 - Autres services",
                    "63 - Personnel",
                    "64 - Impôts et taxes",
                    "66 - Charges financières",
                    "68 - Dotations aux amortissements"
                ]
            },
            "classe_7": {
                "nom": "Produits",
                "comptes": [
                    "70 - Ventes",
                    "71 - Production stockée",
                    "72 - Production immobilisée",
                    "75 - Autres produits",
                    "76 - Produits financiers"
                ]
            }
        }
    
    @staticmethod
    def calculer_tva_ohada(montant_ht: float, taux: float, config: CamerounConfig) -> Dict[str, float]:
        """Calculate VAT according to OHADA rules"""
        tva = montant_ht * taux
        montant_ttc = montant_ht + tva
        
        return {
            "montant_ht": montant_ht,
            "taux_tva": taux,
            "tva": round(tva, 2),
            "montant_ttc": round(montant_ttc, 2),
            "devise": config.devise
        }


class SydoniaPlusIntegrationService:
    """SYDONIA+ customs integration service - Cameroon port operations
    
    NOTE: This is a template structure. Actual integration requires:
    - Official SYDONIA+ API documentation
    - Test environment access
    - Certification from Cameroon Customs
    - Production credentials
    """
    
    @staticmethod
    def preparer_declaration_douaniere(
        reference: str,
        type_declaration: str,  # Import, Export, Transit
        regime_douanier: str,
        valeur_marchandise: float,
        poids_net: float,
        poids_brut: float,
        nombre_colis: int,
        code_hs: str,
        origine: str,
        destination: str,
        config: CamerounConfig
    ) -> Dict[str, Any]:
        """
        Prepare customs declaration data for SYDONIA+
        Returns data structure compatible with SYDONIA+ format
        """
        declaration = {
            "reference": reference,
            "type_declaration": type_declaration,
            "regime_douanier": regime_douanier,
            "pays": config.code_pays_iso,
            "devise": config.code_devise_iso,
            "marchandise": {
                "valeur": valeur_marchandise,
                "devise": config.devise,
                "poids_net": poids_net,
                "poids_brut": poids_brut,
                "nombre_colis": nombre_colis,
                "code_hs": code_hs
            },
            "origine": origine,
            "destination": destination,
            "date_declaration": datetime.utcnow().isoformat(),
            "statut": "prepare"
        }
        
        return declaration
    
    @staticmethod
    def calculer_droits_douane(
        valeur_caf: float,
        taux_dd: float,  # Droits de douane (configured per HS code)
        taux_tva: float,
        taux_autres_taxes: float = 0.0,
        config: CamerounConfig = None
    ) -> Dict[str, float]:
        """
        Calculate customs duties according to Cameroon tariff schedule
        Rates must be configured based on official tariff books
        """
        dd = valeur_caf * taux_dd
        tva = (valeur_caf + dd) * taux_tva
        autres_taxes = valeur_caf * taux_autres_taxes
        total = valeur_caf + dd + tva + autres_taxes
        
        return {
            "valeur_caf": valeur_caf,
            "droits_douane": round(dd, 2),
            "taux_dd": taux_dd,
            "tva": round(tva, 2),
            "taux_tva": taux_tva,
            "autres_taxes": round(autres_taxes, 2),
            "total": round(total, 2),
            "devise": config.devise if config else "XAF"
        }


class GuichetUniqueIntegrationService:
    """GUICHET UNIQUE integration service - Cameroon business procedures
    
    NOTE: This is a template structure. Actual integration requires:
    - Official GUICHET UNIQUE API documentation
    - Test environment access
    - Company registration with GUICHET UNIQUE
    - Production credentials
    """
    
    @staticmethod
    def preparer_dossier_import(
        numero_dossier: str,
        importateur_id: str,
        fournisseur_id: str,
        description_marchandise: str,
        valeur_fob: float,
        pays_origine: str,
        port_arrivee: str,
        config: CamerounConfig
    ) -> Dict[str, Any]:
        """Prepare import file for GUICHET UNIQUE"""
        dossier = {
            "numero_dossier": numero_dossier,
            "type_operation": "IMPORT",
            "importateur": {
                "id": importateur_id,
                "pays": config.code_pays_iso
            },
            "fournisseur": {
                "id": fournisseur_id,
                "pays": pays_origine
            },
            "marchandise": {
                "description": description_marchandise,
                "valeur_fob": valeur_fob,
                "devise": config.devise
            },
            "logistique": {
                "port_arrivee": port_arrivee,
                "pays_destination": config.code_pays_iso
            },
            "date_creation": datetime.utcnow().isoformat(),
            "statut": "soumis"
        }
        
        return dossier
    
    @staticmethod
    def preparer_declaration_cemac(
        numero_reference: str,
        type_operation: str,  # Import, Export
        valeur: float,
            pays_origine: str,
        pays_destination: str,
        config: CamerounConfig
    ) -> Dict[str, Any]:
        """Prepare CEMAC regional trade declaration"""
        declaration = {
            "reference": numero_reference,
            "type_operation": type_operation,
            "zone_cefac": config.code_zone_cefac,
            "pays_declarant": config.code_pays_iso,
            "pays_origine": pays_origine,
            "pays_destination": pays_destination,
            "valeur": valeur,
            "devise": config.devise,
            "date_declaration": datetime.utcnow().isoformat()
        }
        
        return declaration


class PaieCamerounService:
    """Cameroon payroll service - Configuration-driven
    
    NOTE: Tax rates and social contributions must be validated against
    current Cameroon regulations before production use.
    """
    
    @staticmethod
    def calculer_cnps(salaire_brut: float, config: CamerounConfig) -> Dict[str, float]:
        """Calculate CNPS contributions (employee and employer portions)"""
        # Apply ceiling if applicable (Cameroon law has thresholds)
        plafond = 750000  # Example ceiling - to be verified
        base_assujettie = min(salaire_brut, plafond)
        
        cnps_employe = base_assujettie * config.taux_cnps_employe
        cnps_employeur = base_assujettie * config.taux_cnps_employeur
        
        return {
            "salaire_brut": salaire_brut,
            "base_assujettie": base_assujettie,
            "cnps_employe": round(cnps_employe, 2),
            "taux_employe": config.taux_cnps_employe,
            "cnps_employeur": round(cnps_employeur, 2),
            "taux_employeur": config.taux_cnps_employeur,
            "total_cnps": round(cnps_employe + cnps_employeur, 2),
            "devise": config.devise
        }
    
    @staticmethod
    def calculer_irpp(salaire_imposable: float, config: CamerounConfig) -> Dict[str, float]:
        """
        Calculate IRPP (Income Tax) using progressive tax brackets
        This is a simplified calculation - actual calculation requires
        current tax tables from Cameroon tax administration
        """
        # Simplified progressive brackets (to be configured with actual rates)
        tranches = [
            {"min": 0, "max": 53000, "taux": 0.10, "fixe": 0},
            {"min": 53001, "max": 150000, "taux": 0.15, "fixe": 5300},
            {"min": 150001, "max": 400000, "taux": 0.25, "fixe": 23000},
            {"min": 400001, "max": None, "taux": 0.35, "fixe": 85500}
        ]
        
        irpp = 0
        base = salaire_imposable
        
        for tranche in tranches:
            if base <= tranche["min"]:
                continue
            
            if tranche["max"] is None or base <= tranche["max"]:
                taxable = base - tranche["min"]
                irpp += (taxable * tranche["taux"]) + tranche["fixe"]
                break
            else:
                taxable = tranche["max"] - tranche["min"]
                irpp += (taxable * tranche["taux"]) + tranche["fixe"]
        
        return {
            "salaire_imposable": salaire_imposable,
            "irpp": round(irpp, 2),
            "devise": config.devise,
            "note": "Barèmes à configurer selon législation Cameroun actuelle"
        }


class CEMACFinanceService:
    """CEMAC financial operations service"""
    
    @staticmethod
    def convertir_devise(
        montant: float,
        devise_source: str,
        devise_cible: str,
        config: CamerounConfig
    ) -> Dict[str, float]:
        """Convert between currencies using configured exchange rates"""
        if devise_source == devise_cible:
            return {"montant": montant, "taux": 1.0}
        
        # Simplified conversion - in production, use live exchange rate API
        taux = 1.0
        
        if devise_source == "XAF" and devise_cible == "EUR":
            taux = 1 / config.taux_echange_xaf_eur
        elif devise_source == "EUR" and devise_cible == "XAF":
            taux = config.taux_echange_xaf_eur
        else:
            # Additional currency pairs to be configured
            taux = 1.0
        
        montant_converti = montant * taux
        
        return {
            "montant_source": montant,
            "devise_source": devise_source,
            "devise_cible": devise_cible,
            "taux": taux,
            "montant_converti": round(montant_converti, 2)
        }
    
    @staticmethod
    def formater_montant_cefac(montant: float, devise: str = "XAF") -> str:
        """Format amount according to CEMAC/CEFAC standards"""
        if devise == "XAF":
            return f"{montant:,.0f} XAF".replace(",", " ")
        return f"{montant:,.2f} {devise}"


class ComplianceCamerounService:
    """Cameroon legal compliance service"""
    
    @staticmethod
    def verifier_conformite_travail(
        heures_travaillees: float,
        heures_sup: float,
        config: CamerounConfig
    ) -> Dict[str, Any]:
        """Verify compliance with Cameroon labor law"""
        heures_hebdo = heures_travaillees + heures_sup
        conforme = heures_hebdo <= config.heures_travail_hebdo
        
        return {
            "heures_travaillees": heures_travaillees,
            "heures_sup": heures_sup,
            "total_heures": heures_hebdo,
            "limite_hebdomadaire": config.heures_travail_hebdo,
            "conforme": conforme,
            "alerte": "Dépassement heures de travail hebdomadaires" if not conforme else None
        }
    
    @staticmethod
    def verifier_conformite_salaire(
        salaire: float,
        config: CamerounConfig
    ) -> Dict[str, Any]:
        """Verify compliance with minimum wage (SMIG)"""
        conforme = salaire >= config.salaire_minimum
        
        return {
            "salaire": salaire,
            "salaire_minimum": config.salaire_minimum,
            "conforme": conforme,
            "devise": config.devise,
            "alerte": "Salaire inférieur au SMIG" if not conforme else None
        }
    
    @staticmethod
    def verifier_expiration_documents(
        documents: List[Dict[str, Any]],
        jours_critique: int = 30
    ) -> List[Dict[str, Any]]:
        """Check for expiring documents (visas, permits, etc.)"""
        date_limite = date.today() + timedelta(days=jours_critique)
        
        documents_expirants = []
        for doc in documents:
            if doc.get("date_expiration") and doc["date_expiration"] <= date_limite:
                documents_expirants.append({
                    "type": doc.get("type"),
                    "date_expiration": doc["date_expiration"],
                    "jours_restants": (doc["date_expiration"] - date.today()).days,
                    "critique": doc["date_expiration"] < date.today()
                })
        
        return documents_expirants


class IntegrationConfigService:
    """Configuration management service for Cameroon/CEMAC integrations"""
    
    @staticmethod
    def charger_config() -> CamerounConfig:
        """Load Cameroon/CEMAC configuration from environment or file"""
        # In production, load from environment variables or config file
        return CamerounConfig()
    
    @staticmethod
    def sauvegarder_config(config: CamerounConfig, chemin_fichier: str) -> bool:
        """Save configuration to file"""
        try:
            with open(chemin_fichier, 'w') as f:
                json.dump(config.model_dump(), f, indent=2)
            return True
        except Exception:
            return False
    
    @staticmethod
    def charger_config_fichier(chemin_fichier: str) -> Optional[CamerounConfig]:
        """Load configuration from file"""
        try:
            with open(chemin_fichier, 'r') as f:
                data = json.load(f)
            return CamerounConfig(**data)
        except Exception:
            return None
