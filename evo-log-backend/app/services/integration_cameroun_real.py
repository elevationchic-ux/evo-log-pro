"""
Integration Cameroun Services - Real API Implementation
"""
import os
import requests
import logging
from typing import Dict, Any, Optional
from datetime import datetime, date, timedelta
from sqlalchemy.orm import Session

logger = logging.getLogger(__name__)

class CameroonIntegrationConfig:
    """Configuration for Cameroon official integrations"""
    
    # CNCC API Configuration
    CNCC_API_URL = os.getenv("CNCC_API_URL", "https://api.cncc.cm")
    CNCC_API_KEY = os.getenv("CNCC_API_KEY", "")
    
    # INS API Configuration  
    INS_API_URL = os.getenv("INS_API_URL", "https://api.ins.cm")
    INS_API_KEY = os.getenv("INS_API_KEY", "")
    
    # SYGED Customs API Configuration
    SYGED_API_URL = os.getenv("SYGED_API_URL", "https://api.syged.cm")
    SYGED_API_KEY = os.getenv("SYGED_API_KEY", "")
    
    # BEAC API Configuration
    BEAC_API_URL = os.getenv("BEAC_API_URL", "https://api.beac.int")
    BEAC_API_KEY = os.getenv("BEAC_API_KEY", "")


class RealBSCService:
    """Real BSC Service - CNCC Integration"""
    
    @staticmethod
    def generer_bsc_real(
        db: Session,
        numero_connaisse: str,
        navire: str,
        port_chargement: str,
        port_dechargement: str,
        agent: str,
        importateur: str,
        poids_brut_tonnes: float,
        valeur_fob: float
    ) -> Dict[str, Any]:
        """Generate BSC via real CNCC API"""
        try:
            # Call CNCC API
            headers = {
                "Authorization": f"Bearer {CameroonIntegrationConfig.CNCC_API_KEY}",
                "Content-Type": "application/json"
            }
            
            payload = {
                "numero_connaisse": numero_connaisse,
                "navire": navire,
                "port_chargement": port_chargement,
                "port_dechargement": port_dechargement,
                "agent": agent,
                "importateur": importateur,
                "poids_brut_tonnes": poids_brut_tonnes,
                "valeur_fob": valeur_fob
            }
            
            response = requests.post(
                f"{CameroonIntegrationConfig.CNCC_API_URL}/api/v1/bsc",
                json=payload,
                headers=headers,
                timeout=30
            )
            
            if response.status_code == 200:
                bsc_data = response.json()
                logger.info(f"BSC generated successfully: {bsc_data.get('numero_bsc')}")
                return {
                    "success": True,
                    "data": bsc_data,
                    "message": "BSC généré avec succès via CNCC"
                }
            else:
                logger.error(f"CNCC API error: {response.status_code} - {response.text}")
                return {
                    "success": False,
                    "error": f"Erreur API CNCC: {response.status_code}",
                    "message": response.text
                }
                
        except requests.exceptions.RequestException as e:
            logger.error(f"CNCC API connection error: {e}")
            return {
                "success": False,
                "error": "Erreur de connexion à l'API CNCC",
                "message": str(e)
            }


class RealCSCService:
    """Real CSC Service - INS Integration"""
    
    @staticmethod
    def demander_csc_real(
        db: Session,
        numero_bsc: str,
        numero_declaration: str,
        declarant: str
    ) -> Dict[str, Any]:
        """Request CSC via real INS API"""
        try:
            headers = {
                "Authorization": f"Bearer {CameroonIntegrationConfig.INS_API_KEY}",
                "Content-Type": "application/json"
            }
            
            payload = {
                "numero_bsc": numero_bsc,
                "numero_declaration": numero_declaration,
                "declarant": declarant
            }
            
            response = requests.post(
                f"{CameroonIntegrationConfig.INS_API_URL}/api/v1/csc",
                json=payload,
                headers=headers,
                timeout=30
            )
            
            if response.status_code == 200:
                csc_data = response.json()
                logger.info(f"CSC requested successfully: {csc_data.get('numero_csc')}")
                return {
                    "success": True,
                    "data": csc_data,
                    "message": "CSC demandé avec succès via INS"
                }
            else:
                logger.error(f"INS API error: {response.status_code} - {response.text}")
                return {
                    "success": False,
                    "error": f"Erreur API INS: {response.status_code}",
                    "message": response.text
                }
                
        except requests.exceptions.RequestException as e:
            logger.error(f"INS API connection error: {e}")
            return {
                "success": False,
                "error": "Erreur de connexion à l'API INS",
                "message": str(e)
            }


class RealSYGEDService:
    """Real SYGED Service - Customs Integration"""
    
    @staticmethod
    def soumettre_declaration_customs(
        db: Session,
        type_declaration: str,
        donnees_declaration: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Submit customs declaration via SYGED API"""
        try:
            headers = {
                "Authorization": f"Bearer {CameroonIntegrationConfig.SYGED_API_KEY}",
                "Content-Type": "application/json"
            }
            
            payload = {
                "type_declaration": type_declaration,
                "donnees": donnees_declaration
            }
            
            response = requests.post(
                f"{CameroonIntegrationConfig.SYGED_API_URL}/api/v1/declarations",
                json=payload,
                headers=headers,
                timeout=30
            )
            
            if response.status_code == 200:
                customs_data = response.json()
                logger.info(f"Customs declaration submitted: {customs_data.get('numero_declaration')}")
                return {
                    "success": True,
                    "data": customs_data,
                    "message": "Déclaration soumise avec succès via SYGED"
                }
            else:
                logger.error(f"SYGED API error: {response.status_code} - {response.text}")
                return {
                    "success": False,
                    "error": f"Erreur API SYGED: {response.status_code}",
                    "message": response.text
                }
                
        except requests.exceptions.RequestException as e:
            logger.error(f"SYGED API connection error: {e}")
            return {
                "success": False,
                "error": "Erreur de connexion à l'API SYGED",
                "message": str(e)
            }


class RealBEACService:
    """Real BEAC Service - Exchange Rate Integration"""
    
    @staticmethod
    def obtenir_taux_reference_beac(
        devise: str = "XAF"
    ) -> Dict[str, Any]:
        """Get reference exchange rates from BEAC"""
        try:
            headers = {
                "Authorization": f"Bearer {CameroonIntegrationConfig.BEAC_API_KEY}",
                "Content-Type": "application/json"
            }
            
            response = requests.get(
                f"{CameroonIntegrationConfig.BEAC_API_URL}/api/v1/taux/{devise}",
                headers=headers,
                timeout=30
            )
            
            if response.status_code == 200:
                taux_data = response.json()
                logger.info(f"BEAC rates retrieved for {devise}")
                return {
                    "success": True,
                    "data": taux_data,
                    "message": "Taux BEAC obtenus avec succès"
                }
            else:
                logger.error(f"BEAC API error: {response.status_code} - {response.text}")
                return {
                    "success": False,
                    "error": f"Erreur API BEAC: {response.status_code}",
                    "message": response.text
                }
                
        except requests.exceptions.RequestException as e:
            logger.error(f"BEAC API connection error: {e}")
            return {
                "success": False,
                "error": "Erreur de connexion à l'API BEAC",
                "message": str(e)
            }


class CameroonIntegrationService:
    """Main Cameroon Integration Service"""
    
    def __init__(self):
        self.bsc_service = RealBSCService()
        self.csc_service = RealCSCService()
        self.syged_service = RealSYGEDService()
        self.beac_service = RealBEACService()
    
    def generer_bsc(self, db: Session, **kwargs) -> Dict[str, Any]:
        """Generate BSC with real CNCC integration"""
        return self.bsc_service.generer_bsc_real(db, **kwargs)
    
    def demander_csc(self, db: Session, **kwargs) -> Dict[str, Any]:
        """Request CSC with real INS integration"""
        return self.csc_service.demander_csc_real(db, **kwargs)
    
    def soumettre_declaration(self, db: Session, **kwargs) -> Dict[str, Any]:
        """Submit customs declaration with real SYGED integration"""
        return self.syged_service.soumettre_declaration_customs(db, **kwargs)
    
    def obtenir_taux_beac(self, devise: str = "XAF") -> Dict[str, Any]:
        """Get BEAC reference rates"""
        return self.beac_service.obtenir_taux_reference_beac(devise)
