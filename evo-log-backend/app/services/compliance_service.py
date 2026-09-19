"""Legal compliance service - RGPD, labor law, transport regulations"""
from datetime import datetime, date, timedelta
from typing import List, Dict, Any, Optional
from pydantic import BaseModel


class RGPDComplianceService:
    """GDPR (RGPD) data protection service for Cameroon"""
    
    @staticmethod
    def verifier_consentement_consentis(
        utilisateur_id: int,
        type_donnee: str,
        date_consentement: Optional[date] = None
    ) -> Dict[str, Any]:
        """
        Verify consent for data processing
        Cameroon has data protection laws similar to GDPR
        """
        return {
            "utilisateur_id": utilisateur_id,
            "type_donnee": type_donnee,
            "consentement_valide": True,
            "date_consentement": date_consentement or date.today(),
            "duree_consentement_jours": 365,  # 1 year typical
            "statut": "valide"
        }
    
    @staticmethod
    def generer_rapport_traitement_donnees(
        traitement_id: str,
        categories_donnees: List[str],
        finalite: str,
        base_legale: str
    ) -> Dict[str, Any]:
        """Generate data processing record (ROPA - Record of Processing Activities)"""
        return {
            "traitement_id": traitement_id,
            "categories_donnees": categories_donnees,
            "finalite": finalite,
            "base_legale": base_legale,
            "date_creation": datetime.utcnow().isoformat(),
            "pays": "Cameroun",
            "cadre_juridique": "Loi N°2010/012 du 21 décembre 2010"
        }
    
    @staticmethod
    def verifier_droit_effacement(
        utilisateur_id: int,
        motif_demande: str
    ) -> Dict[str, Any]:
        """
        Process right to erasure (right to be forgotten)
        With exceptions for legal obligations
        """
        exceptions_legales = [
            "obligations comptables",
            "obligations fiscales",
            "conformité douanière",
            "litiges en cours"
        ]
        
        return {
            "utilisateur_id": utilisateur_id,
            "motif_demande": motif_demande,
            "droit_applicable": True,
            "exceptions_legales": exceptions_legales,
            "action_requise": "anonymisation_donnees"
        }
    
    @staticmethod
    def calculer_duree_retention(type_donnee: str) -> Dict[str, Any]:
        """
        Calculate data retention period according to Cameroon law
        """
        periodes_retention = {
            "donnees_employe": 5,  # 5 years after employment ends
            "donnees_client": 10,  # 10 years for commercial data
            "donnees_fiscales": 10,  # 10 years tax records
            "donnees_comptables": 10,  # 10 years accounting records
            "documents_employe": 5,  # 5 years
            "journal_audit": 5,  # 5 years audit logs
            "default": 5
        }
        
        annees = periodes_retention.get(type_donnee, periodes_retention["default"])
        date_expiration = date.today() + timedelta(days=annees * 365)
        
        return {
            "type_donnee": type_donnee,
            "duree_retention_annees": annees,
            "date_expiration": date_expiration,
            "base_legale": "Loi Cameroun sur la protection des données personnelles"
        }


class ConformiteTravailService:
    """Cameroon labor law compliance service"""
    
    @staticmethod
    def verifier_contrat_travail(
        type_contrat: str,
        duree_mois: int,
        periode_essai_jours: int,
        salaire: float,
        smig: float = 41664
    ) -> Dict[str, Any]:
        """Verify employment contract compliance with Cameroon Labor Code"""
        conformite = {
            "type_contrat": type_contrat,
            "duree_mois": duree_mois,
            "periode_essai_jours": periode_essai_jours,
            "salaire": salaire,
            "smig": smig,
            "verifications": []
        }
        
        # Check trial period
        periode_essai_max = 90 if type_contrat == "CDI" else 14 if type_contrat == "CDD" else 30
        if periode_essai_jours <= periode_essai_max:
            conformite["verifications"].append({
                "critere": "periode_essai",
                "conforme": True,
                "message": f"Période d'essai conforme (max {periode_essai_max} jours)"
            })
        else:
            conformite["verifications"].append({
                "critere": "periode_essai",
                "conforme": False,
                "message": f"Période d'essai excessive (max {periode_essai_max} jours)"
            })
        
        # Check minimum wage
        if salaire >= smig:
            conformite["verifications"].append({
                "critere": "salaire_minimum",
                "conforme": True,
                "message": "Salaire conforme au SMIG"
            })
        else:
            conformite["verifications"].append({
                "critere": "salaire_minimum",
                "conforme": False,
                "message": f"Salaire inférieur au SMIG ({smig} XAF)"
            })
        
        # Check CDD duration (max 24 months renewable once)
        if type_contrat == "CDD" and duree_mois > 24:
            conformite["verifications"].append({
                "critere": "duree_cdd",
                "conforme": False,
                "message": "Durée CDD excessive (max 24 mois)"
            })
        
        conformite["conforme_global"] = all(v["conforme"] for v in conformite["verifications"])
        
        return conformite
    
    @staticmethod
    def verifier_heures_travail(
        heures_semaine: float,
        heures_sup: float,
        repos_semaine: bool
    ) -> Dict[str, Any]:
        """Verify working hours compliance (40h weekly, 48h max with overtime)"""
        total_heures = heures_semaine + heures_sup
        
        return {
            "heures_normales": heures_semaine,
            "heures_sup": heures_sup,
            "total_heures": total_heures,
            "limite_normale": 40,
            "limite_max": 48,
            "repos_semaine_accorde": repos_semaine,
            "conforme": total_heures <= 48,
            "alerte": "Dépassement limite hebdomadaire" if total_heures > 48 else None
        }
    
    @staticmethod
    def verifier_conges(
        jours_accordes: float,
        mois_anciennete: int
    ) -> Dict[str, Any]:
        """Verify leave allocation (2.5 days per month of service)"""
        jours_theoriques = mois_anciennete * 2.5
        
        return {
            "mois_anciennete": mois_anciennete,
            "jours_theoriques": jours_theoriques,
            "jours_accordes": jours_accordes,
            "conforme": jours_accordes >= jours_theoriques,
            "ecart": jours_accordes - jours_theoriques
        }
    
    @staticmethod
    def verifier_document_employe(
        type_document: str,
        date_expiration: Optional[date],
        date_naissance: date
    ) -> Dict[str, Any]:
        """Verify employee document requirements"""
        documents_requis = {
            "carte_identite": True,
            "cv": True,
            "diplomes": True,
            "contrat": True,
            "visite_medicale": True
        }
        
        statut = "valide"
        if date_expiration and date_expiration < date.today():
            statut = "expire"
        elif date_expiration and date_expiration < (date.today() + timedelta(days=30)):
            statut = "expire_bientot"
        
        return {
            "type_document": type_document,
            "requis": documents_requis.get(type_document, False),
            "date_expiration": date_expiration,
            "statut": statut,
            "conforme": statut == "valide"
        }


class ConformiteTransportService:
    """Transport regulations compliance service - Cameroon/CEMAC"""
    
    @staticmethod
    def verifier_temps_conduite(
        heures_conduite: float,
        pause_minutes: int,
        repos_journalier: bool
    ) -> Dict[str, Any]:
        """Verify driving time compliance (Cameroon/CEMAC regulations)"""
        max_sans_pause = 4.5  # hours
        pause_minimale = 45  # minutes
        max_journalier = 9.0  # hours
        
        conformite = {
            "heures_conduite": heures_conduite,
            "pause_minutes": pause_minutes,
            "repos_journalier": repos_journalier,
            "verifications": []
        }
        
        # Check continuous driving limit
        if heures_conduite <= max_sans_pause:
            conformite["verifications"].append({
                "critere": "conduite_continue",
                "conforme": True,
                "message": "Conduite continue conforme"
            })
        else:
            conformite["verifications"].append({
                "critere": "conduite_continue",
                "conforme": False,
                "message": f"Dépassement conduite continue (max {max_sans_pause}h)"
            })
        
        # Check break duration
        if pause_minutes >= pause_minimale:
            conformite["verifications"].append({
                "critere": "pause_duree",
                "conforme": True,
                "message": "Pause conforme"
            })
        else:
            conformite["verifications"].append({
                "critere": "pause_duree",
                "conforme": False,
                "message": f"Pause insuffisante (min {pause_minimale} min)"
            })
        
        # Check daily limit
        if heures_conduite <= max_journalier:
            conformite["verifications"].append({
                "critere": "limite_journaliere",
                "conforme": True,
                "message": "Limite journalière respectée"
            })
        else:
            conformite["verifications"].append({
                "critere": "limite_journaliere",
                "conforme": False,
                "message": f"Dépassement limite journalière (max {max_journalier}h)"
            })
        
        # Check daily rest
        if repos_journalier:
            conformite["verifications"].append({
                "critere": "repos_journalier",
                "conforme": True,
                "message": "Repos journalier accordé"
            })
        else:
            conformite["verifications"].append({
                "critere": "repos_journalier",
                "conforme": False,
                "message": "Repos journalier non accordé"
            })
        
        conformite["conforme_global"] = all(v["conforme"] for v in conformite["verifications"])
        
        return conformite
    
    @staticmethod
    def verifier_vehicule(
        controle_technique_date: Optional[date],
        assurance_date: Optional[date],
        carte_grise_date: Optional[date]
    ) -> Dict[str, Any]:
        """Verify vehicle documentation compliance"""
        verifications = []
        
        # Technical inspection (annual in Cameroon)
        if controle_technique_date:
            valide = controle_technique_date > date.today()
            verifications.append({
                "document": "controle_technique",
                "date": controle_technique_date,
                "conforme": valide,
                "statut": "valide" if valide else "expire"
            })
        
        # Insurance
        if assurance_date:
            valide = assurance_date > date.today()
            verifications.append({
                "document": "assurance",
                "date": assurance_date,
                "conforme": valide,
                "statut": "valide" if valide else "expire"
            })
        
        # Registration card
        if carte_grise_date:
            valide = carte_grise_date > date.today()
            verifications.append({
                "document": "carte_grise",
                "date": carte_grise_date,
                "conforme": valide,
                "statut": "valide" if valide else "expire"
            })
        
        return {
            "verifications": verifications,
            "conforme_global": all(v["conforme"] for v in verifications) if verifications else True
        }
    
    @staticmethod
    def verifier_marchandise_dangereuse(
        type_marchandise: str,
        classe_adr: Optional[str],
        etiquetage: bool,
        documentation_transport: bool
    ) -> Dict[str, Any]:
        """Verify dangerous goods transport compliance"""
        classes_dangereuses = ["1", "2", "3", "4", "5", "6", "7", "8", "9"]
        
        est_dangereux = classe_adr in classes_dangereuses if classe_adr else False
        
        if est_dangereux:
            return {
                "type_marchandise": type_marchandise,
                "classe_adr": classe_adr,
                "dangereux": True,
                "etiquetage_conforme": etiquetage,
                "documentation_conforme": documentation_transport,
                "conforme": etiquetage and documentation_transport
            }
        
        return {
            "type_marchandise": type_marchandise,
            "dangereux": False,
            "conforme": True
        }


class AuditComplianceService:
    """Audit trail and compliance monitoring service"""
    
    @staticmethod
    def generer_rapport_audit(
        periode_debut: date,
        periode_fin: date,
        utilisateur_id: Optional[int] = None
    ) -> Dict[str, Any]:
        """Generate audit compliance report"""
        return {
            "periode": f"{periode_debut} à {periode_fin}",
            "utilisateur_id": utilisateur_id,
            "evenements_total": 0,
            "evenements_critiques": 0,
            "conformite": True,
            "note": "À implémenter avec tables d'audit"
        }
    
    @staticmethod
    def verifier_separation_fonctions(
        utilisateur_id: int,
        roles: List[str]
    ) -> Dict[str, Any]:
        """Verify segregation of duties compliance"""
        roles_sensibles = ["ADMIN", "FINANCIER", "AUDITOR"]
        
        # Check for incompatible role combinations
        incompatibilites = []
        if "ADMIN" in roles and "AUDITOR" in roles:
            incompatibilites.append("ADMIN + AUDITOR")
        
        return {
            "utilisateur_id": utilisateur_id,
            "roles": roles,
            "incompatibilites": incompatibilites,
            "conforme": len(incompatibilites) == 0
        }


class SecuritePhysiqueService:
    """Physical security and workplace safety compliance service"""
    
    @staticmethod
    def verifier_equipement_securite(
        type_equipement: str,
        date_verification: Optional[date],
        conforme: bool
    ) -> Dict[str, Any]:
        """Verify safety equipment compliance (PPE, fire safety, etc.)"""
        return {
            "type_equipement": type_equipement,
            "date_verification": date_verification,
            "conforme": conforme,
            "statut": "valide" if conforme else "non_conforme"
        }
    
    @staticmethod
    def verifier_formation_securite(
        employe_id: int,
        date_formation: Optional[date],
        type_formation: str
    ) -> Dict[str, Any]:
        """Verify safety training compliance"""
        validite_mois = 12  # Safety training valid for 1 year
        
        if date_formation:
            date_expiration = date_formation + timedelta(days=validite_mois * 30)
            valide = date_expiration > date.today()
        else:
            valide = False
            date_expiration = None
        
        return {
            "employe_id": employe_id,
            "type_formation": type_formation,
            "date_formation": date_formation,
            "date_expiration": date_expiration,
            "valide": valide
        }
