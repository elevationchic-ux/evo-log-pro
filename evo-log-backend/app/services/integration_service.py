"""Integration service - External integrations for Cameroon/CEMAC"""
from datetime import datetime, date, timedelta
from typing import List, Optional, Dict, Any
from sqlalchemy.orm import Session
from sqlalchemy import and_, func
from app.models.integration import (
    Integration, RequeteIntegration, WebhookIntegration, SYDONIAPlus, GuichetUnique, PCS,
    IntegrationBanque, IntegrationAssureur, IntegrationTransitaire, Synchronisation,
    TypeIntegration, StatutIntegration, TypeRequete, StatutRequete
)


class IntegrationService:
    """Integration service"""
    
    @staticmethod
    def creer_integration(
        db: Session,
        code_integration: str,
        type_integration: TypeIntegration,
        nom: str,
        url_api: str,
        api_key: str
    ) -> Integration:
        """Create external integration"""
        integration = Integration(
            code_integration=code_integration,
            type_integration=type_integration,
            nom=nom,
            url_api=url_api,
            api_key=api_key,
            statut=StatutIntegration.ACTIF,
            date_activation=date.today()
        )
        db.add(integration)
        db.commit()
        db.refresh(integration)
        return integration
    
    @staticmethod
    def activer_integration(db: Session, integration_id: int) -> Integration:
        """Activate integration"""
        integration = db.query(Integration).filter(Integration.id == integration_id).first()
        if not integration:
            raise ValueError("Intégration non trouvée")
        
        integration.statut = StatutIntegration.ACTIF
        integration.date_activation = date.today()
        integration.derniere_synchronisation = datetime.utcnow()
        db.commit()
        db.refresh(integration)
        return integration


class RequeteIntegrationService:
    """Integration request service"""
    
    @staticmethod
    def creer_requete(
        db: Session,
        integration_id: int,
        numero_requete: str,
        type_requete: TypeRequete,
        direction: str,
        donnees_envoyees: str
    ) -> RequeteIntegration:
        """Create integration request"""
        requete = RequeteIntegration(
            integration_id=integration_id,
            numero_requete=numero_requete,
            type_requete=type_requete,
            direction=direction,
            donnees_envoyees=donnees_envoyees,
            statut=StatutRequete.EN_ATTENTE
        )
        db.add(requete)
        db.commit()
        db.refresh(requete)
        return requete
    
    @staticmethod
    def mettre_a_jour_reponse(
        db: Session,
        requete_id: int,
        donnees_recues: str,
        code_reponse: int,
        duree_ms: int
    ) -> RequeteIntegration:
        """Update request response"""
        requete = db.query(RequeteIntegration).filter(RequeteIntegration.id == requete_id).first()
        if not requete:
            raise ValueError("Requête non trouvée")
        
        requete.donnees_recues = donnees_recues
        requete.code_reponse = code_reponse
        requete.duree_ms = duree_ms
        requete.date_reponse = datetime.utcnow()
        requete.statut = StatutRequete.SUCCES if code_reponse < 400 else StatutRequete.ECHEC
        db.commit()
        db.refresh(requete)
        return requete


class SYDONIAPlusService:
    """SYDONIA+ service"""
    
    @staticmethod
    def creer_dossier_sydonia(
        db: Session,
        numero_dossier: str,
        bureau_douane: str,
        type_operation: str,
        regime: str
    ) -> SYDONIAPlus:
        """Create SYDONIA+ dossier"""
        dossier = SYDONIAPlus(
            numero_dossier=numero_dossier,
            bureau_douane=bureau_douane,
            type_operation=type_operation,
            regime=regime
        )
        db.add(dossier)
        db.commit()
        db.refresh(dossier)
        return dossier


class GuichetUniqueService:
    """GUICHET UNIQUE service"""
    
    @staticmethod
    def creer_transaction(
        db: Session,
        numero_transaction: str,
        service: str,
        type_service: str,
        utilisateur: str
    ) -> GuichetUnique:
        """Create GUICHET UNIQUE transaction"""
        transaction = GuichetUnique(
            numero_transaction=numero_transaction,
            service=service,
            type_service=type_service,
            utilisateur=utilisateur,
            date_transaction=datetime.utcnow(),
            statut="en_cours"
        )
        db.add(transaction)
        db.commit()
        db.refresh(transaction)
        return transaction


class PCSService:
    """PCS service"""
    
    @staticmethod
    def creer_operation_pcs(
        db: Session,
        reference_pcs: str,
        type_operation: str,
        navire: str,
        port: str
    ) -> PCS:
        """Create PCS operation"""
        operation = PCS(
            reference_pcs=reference_pcs,
            type_operation=type_operation,
            navire=navire,
            port=port,
            date_operation=date.today(),
            statut_pcs="en_cours"
        )
        db.add(operation)
        db.commit()
        db.refresh(operation)
        return operation


class IntegrationBanqueService:
    """Bank integration service"""
    
    @staticmethod
    def creer_integration_banque(
        db: Session,
        banque_id: int,
        code_banque: str,
        nom_banque: str,
        bic: str,
        iban: str
    ) -> IntegrationBanque:
        """Create bank integration"""
        integration = IntegrationBanque(
            banque_id=banque_id,
            code_banque=code_banque,
            nom_banque=nom_banque,
            bic=bic,
            iban=iban,
            statut="actif",
            date_activation=date.today()
        )
        db.add(integration)
        db.commit()
        db.refresh(integration)
        return integration


class IntegrationAssureurService:
    """Insurer integration service"""
    
    @staticmethod
    def creer_integration_assureur(
        db: Session,
        assureur_id: int,
        code_assureur: str,
        nom_assureur: str,
        type_assurance: str
    ) -> IntegrationAssureur:
        """Create insurer integration"""
        integration = IntegrationAssureur(
            assureur_id=assureur_id,
            code_assureur=code_assureur,
            nom_assureur=nom_assureur,
            type_assurance=type_assurance,
            statut="actif"
        )
        db.add(integration)
        db.commit()
        db.refresh(integration)
        return integration


class IntegrationTransitaireService:
    """Forwarder integration service"""
    
    @staticmethod
    def creer_integration_transitaire(
        db: Session,
        transitaire_id: int,
        code_transitaire: str,
        nom_transitaire: str,
        type_service: str
    ) -> IntegrationTransitaire:
        """Create forwarder integration"""
        integration = IntegrationTransitaire(
            transitaire_id=transitaire_id,
            code_transitaire=code_transitaire,
            nom_transitaire=nom_transitaire,
            type_service=type_service,
            statut="actif",
            date_activation=date.today()
        )
        db.add(integration)
        db.commit()
        db.refresh(integration)
        return integration


class SynchronisationService:
    """Synchronization service"""
    
    @staticmethod
    def creer_synchronisation(
        db: Session,
        integration_id: int,
        type_synchronisation: str,
        lance_par: str
    ) -> Synchronisation:
        """Create synchronization record"""
        synchronisation = Synchronisation(
            integration_id=integration_id,
            type_synchronisation=type_synchronisation,
            date_debut=datetime.utcnow(),
            statut="en_cours",
            lance_par=lance_par
        )
        db.add(synchronisation)
        db.commit()
        db.refresh(synchronisation)
        return synchronisation
    
    @staticmethod
    def completer_synchronisation(
        db: Session,
        synchronisation_id: int,
        enregistrements_traites: int,
        enregistrements_echoues: int
    ) -> Synchronisation:
        """Complete synchronization"""
        synchronisation = db.query(Synchronisation).filter(Synchronisation.id == synchronisation_id).first()
        if not synchronisation:
            raise ValueError("Synchronisation non trouvée")
        
        synchronisation.date_fin = datetime.utcnow()
        synchronisation.enregistrements_traites = enregistrements_traites
        synchronisation.enregistrements_echoues = enregistrements_echoues
        synchronisation.duree_secondes = int((synchronisation.date_fin - synchronisation.date_debut).total_seconds())
        synchronisation.statut = "succes" if enregistrements_echoues == 0 else "echec"
        
        # Update integration last sync
        integration = db.query(Integration).filter(Integration.id == synchronisation.integration_id).first()
        if integration:
            integration.derniere_synchronisation = synchronisation.date_fin
        
        db.commit()
        db.refresh(synchronisation)
        return synchronisation


class IntegrationReportingService:
    """Integration reporting service"""
    
    @staticmethod
    def rapport_integration(db: Session, integration_id: int) -> Dict[str, Any]:
        """Generate integration report"""
        integration = db.query(Integration).filter(Integration.id == integration_id).first()
        if not integration:
            raise ValueError("Intégration non trouvée")
        
        requetes = db.query(RequeteIntegration).filter(
            RequeteIntegration.integration_id == integration_id
        ).all()
        
        synchronisations = db.query(Synchronisation).filter(
            Synchronisation.integration_id == integration_id
        ).all()
        
        return {
            "integration": {
                "code": integration.code_integration,
                "type": integration.type_integration.value,
                "nom": integration.nom,
                "statut": integration.statut.value
            },
            "requetes": {
                "total": len(requetes),
                "succes": sum(1 for r in requetes if r.statut == StatutRequete.SUCCES),
                "echec": sum(1 for r in requetes if r.statut == StatutRequete.ECHEC)
            },
            "synchronisations": {
                "total": len(synchronisations),
                "succes": sum(1 for s in synchronisations if s.statut == "succes"),
                "echec": sum(1 for s in synchronisations if s.statut == "echec")
            }
        }
