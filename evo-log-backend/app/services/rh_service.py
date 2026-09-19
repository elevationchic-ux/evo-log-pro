"""RH service - Complete HR management for Cameroon/CEMAC compliance"""
from datetime import datetime, date, timedelta
from typing import List, Optional, Dict, Any
from sqlalchemy.orm import Session
from sqlalchemy import and_, or_, func, case
from app.models.rh import (
    Conge, Absence, TempsTravail, Formation, ParticipationFormation,
    EvaluationPerformance, ContratTravail, Salaire, Prime, DocumentEmploye,
    Organigramme, Competence, CompetenceEmploye
)
from app.models.user import User
from app.models.agency import Agency


class CongeService:
    """Leave management service - Cameroon labor law compliant"""
    
    @staticmethod
    def calculer_solde_conge(db: Session, employe_id: int, annee: int) -> Dict[str, Any]:
        """Calculate leave balance - Cameroon: 2.5 days/month of service"""
        # Cameroon law: 2.5 working days per month of service
        conges_accordes = db.query(func.sum(Conge.nombre_jours)).filter(
            and_(
                Conge.employe_id == employe_id,
                Conge.type_conge == "annuel",
                Conge.date_debut.between(date(annee, 1, 1), date(annee, 12, 31)),
                Conge.statut == "approuve"
            )
        ).scalar() or 0
        
        # Get employment start date to calculate accrued days
        employe = db.query(User).filter(User.id == employe_id).first()
        if not employe:
            return {"solde": 0, "utilise": 0, "reste": 0}
        
        # Calculate months of service in current year
        date_entree = employe.date_creation or date(annee, 1, 1)
        mois_service = min(12, max(1, (date(annee, 12, 31) - date_entree).days // 30))
        solde_accorde = mois_service * 2.5  # Cameroon standard
        
        return {
            "solde": solde_accorde,
            "utilise": conges_accordes,
            "reste": solde_accorde - conges_accordes,
            "annee": annee
        }
    
    @staticmethod
    def demander_conge(
        db: Session,
        employe_id: int,
        type_conge: str,
        date_debut: date,
        date_fin: date,
        motif: str,
        approbateur_id: Optional[int] = None
    ) -> Conge:
        """Submit leave request with automatic workflow"""
        nombre_jours = (date_fin - date_debut).days + 1
        
        # Check leave balance for annual leave
        if type_conge == "annuel":
            solde = CongeService.calculer_solde_conge(db, employe_id, date_debut.year)
            if solde["reste"] < nombre_jours:
                raise ValueError(f"Solde insuffisant: {solde['reste']} jours disponibles")
        
        conge = Conge(
            employe_id=employe_id,
            type_conge=type_conge,
            date_debut=date_debut,
            date_fin=date_fin,
            nombre_jours=nombre_jours,
            motif=motif,
            statut="en_attente",
            date_demande=datetime.utcnow()
        )
        
        db.add(conge)
        db.commit()
        db.refresh(conge)
        return conge
    
    @staticmethod
    def approuver_conge(db: Session, conge_id: int, approbateur_id: int, commentaire: str = "") -> Conge:
        """Approve leave request"""
        conge = db.query(Conge).filter(Conge.id == conge_id).first()
        if not conge:
            raise ValueError("Congé non trouvé")
        
        conge.statut = "approuve"
        conge.approbateur_id = approbateur_id
        conge.date_approbation = datetime.utcnow()
        conge.commentaire_approbation = commentaire
        
        db.commit()
        db.refresh(conge)
        return conge
    
    @staticmethod
    def rejeter_conge(db: Session, conge_id: int, approbateur_id: int, motif_refus: str) -> Conge:
        """Reject leave request"""
        conge = db.query(Conge).filter(Conge.id == conge_id).first()
        if not conge:
            raise ValueError("Congé non trouvé")
        
        conge.statut = "refuse"
        conge.approbateur_id = approbateur_id
        conge.date_approbation = datetime.utcnow()
        conge.motif_refus = motif_refus
        
        db.commit()
        db.refresh(conge)
        return conge


class AbsenceService:
    """Absence tracking service"""
    
    @staticmethod
    def enregistrer_absence(
        db: Session,
        employe_id: int,
        type_absence: str,
        date_debut: date,
        date_fin: date,
        motif: str,
        justifie: bool = False
    ) -> Absence:
        """Record absence with justification tracking"""
        nombre_jours = (date_fin - date_debut).days + 1
        
        absence = Absence(
            employe_id=employe_id,
            type_absence=type_absence,
            date_debut=date_debut,
            date_fin=date_fin,
            nombre_jours=nombre_jours,
            motif=motif,
            justifie=justifie,
            date_enregistrement=datetime.utcnow()
        )
        
        db.add(absence)
        db.commit()
        db.refresh(absence)
        return absence
    
    @staticmethod
    def calculer_taux_absenteisme(db: Session, employe_id: int, mois: int, annee: int) -> float:
        """Calculate absenteeism rate for the month"""
        debut_mois = date(annee, mois, 1)
        fin_mois = (date(annee, mois + 1, 1) - timedelta(days=1)) if mois < 12 else date(annee, 12, 31)
        jours_ouvres = 22  # Standard working days per month
        
        absences = db.query(func.sum(Absence.nombre_jours)).filter(
            and_(
                Absence.employe_id == employe_id,
                Absence.date_debut >= debut_mois,
                Absence.date_fin <= fin_mois
            )
        ).scalar() or 0
        
        return (absences / jours_ouvres) * 100 if jours_ouvres > 0 else 0


class TempsTravailService:
    """Working time management service - Cameroon labor law compliant"""
    
    @staticmethod
    def pointer_arrivee(db: Session, employe_id: int, date_pointage: date, heure_arrivee: datetime) -> TempsTravail:
        """Clock in - attendance tracking"""
        pointage = TempsTravail(
            employe_id=employe_id,
            date=date_pointage,
            heure_arrivee=heure_arrivee,
            statut="present"
        )
        db.add(pointage)
        db.commit()
        db.refresh(pointage)
        return pointage
    
    @staticmethod
    def pointer_depart(db: Session, employe_id: int, date_pointage: date, heure_depart: datetime) -> TempsTravail:
        """Clock out - calculate hours worked"""
        pointage = db.query(TempsTravail).filter(
            and_(
                TempsTravail.employe_id == employe_id,
                TempsTravail.date == date_pointage,
                TempsTravail.heure_depart.is_(None)
            )
        ).first()
        
        if not pointage:
            raise ValueError("Pas de pointage d'arrivée trouvé")
        
        pointage.heure_depart = heure_depart
        pointage.heures_travaillees = (heure_depart - pointage.heure_arrivee).total_seconds() / 3600
        
        # Calculate overtime if > 8 hours (Cameroon standard)
        if pointage.heures_travaillees > 8:
            pointage.heures_sup = pointage.heures_travaillees - 8
        
        db.commit()
        db.refresh(pointage)
        return pointage
    
    @staticmethod
    def calculer_heures_mois(db: Session, employe_id: int, mois: int, annee: int) -> Dict[str, float]:
        """Calculate monthly hours and overtime"""
        debut_mois = date(annee, mois, 1)
        fin_mois = (date(annee, mois + 1, 1) - timedelta(days=1)) if mois < 12 else date(annee, 12, 31)
        
        result = db.query(
            func.sum(TempsTravail.heures_travaillees).label("total"),
            func.sum(TempsTravail.heures_sup).label("sup"),
            func.count(TempsTravail.id).label("jours")
        ).filter(
            and_(
                TempsTravail.employe_id == employe_id,
                TempsTravail.date >= debut_mois,
                TempsTravail.date <= fin_mois
            )
        ).first()
        
        return {
            "heures_travaillees": result.total or 0,
            "heures_sup": result.sup or 0,
            "jours_presents": result.jours or 0
        }


class FormationService:
    """Training management service"""
    
    @staticmethod
    def creer_formation(
        db: Session,
        titre: str,
        description: str,
        date_debut: date,
        date_fin: date,
        duree_heures: int,
        cout: float,
        formateur: str,
        lieu: str,
        agency_id: Optional[int] = None
    ) -> Formation:
        """Create training session"""
        formation = Formation(
            titre=titre,
            description=description,
            date_debut=date_debut,
            date_fin=date_fin,
            duree_heures=duree_heures,
            cout=cout,
            formateur=formateur,
            lieu=lieu,
            agency_id=agency_id,
            statut="planifie"
        )
        db.add(formation)
        db.commit()
        db.refresh(formation)
        return formation
    
    @staticmethod
    def inscrire_employe(db: Session, formation_id: int, employe_id: int) -> ParticipationFormation:
        """Enroll employee in training"""
        participation = ParticipationFormation(
            formation_id=formation_id,
            employe_id=employe_id,
            date_inscription=datetime.utcnow(),
            statut="inscrit"
        )
        db.add(participation)
        db.commit()
        db.refresh(participation)
        return participation
    
    @staticmethod
    def valider_participation(
        db: Session,
        participation_id: int,
        present: bool,
        certificat_obtenu: bool = False,
        commentaire: str = ""
    ) -> ParticipationFormation:
        """Validate training participation and certification"""
        participation = db.query(ParticipationFormation).filter(
            ParticipationFormation.id == participation_id
        ).first()
        
        if not participation:
            raise ValueError("Participation non trouvée")
        
        participation.present = present
        participation.certificat_obtenu = certificat_obtenu
        participation.commentaire = commentaire
        participation.statut = "complete" if present else "absent"
        
        db.commit()
        db.refresh(participation)
        return participation
    
    @staticmethod
    def obtenir_formations_expirantes(db: Session, jours_avance: int = 30) -> List[Formation]:
        """Get trainings with expiring certifications"""
        date_limite = date.today() + timedelta(days=jours_avance)
        
        formations = db.query(Formation).filter(
            and_(
                Formation.certificat_valide_jusque.isnot(None),
                Formation.certificat_valide_jusque <= date_limite
            )
        ).all()
        
        return formations


class PerformanceService:
    """Performance evaluation service"""
    
    @staticmethod
    def creer_evaluation(
        db: Session,
        employe_id: int,
        evaluateur_id: int,
        periode_debut: date,
        periode_fin: date,
        note_globale: float,
        commentaires: str,
        objectifs_atteints: int,
        objectifs_total: int
    ) -> EvaluationPerformance:
        """Create performance evaluation"""
        evaluation = EvaluationPerformance(
            employe_id=employe_id,
            evaluateur_id=evaluateur_id,
            periode_debut=periode_debut,
            periode_fin=periode_fin,
            note_globale=note_globale,
            commentaires=commentaires,
            objectifs_atteints=objectifs_atteints,
            objectifs_total=objectifs_total,
            date_evaluation=datetime.utcnow()
        )
        db.add(evaluation)
        db.commit()
        db.refresh(evaluation)
        return evaluation
    
    @staticmethod
    def obtenir_historique_evaluation(db: Session, employe_id: int) -> List[EvaluationPerformance]:
        """Get employee evaluation history"""
        return db.query(EvaluationPerformance).filter(
            EvaluationPerformance.employe_id == employe_id
        ).order_by(EvaluationPerformance.periode_fin.desc()).all()


class ContratService:
    """Employment contract management service - Cameroon labor law compliant"""
    
    @staticmethod
    def creer_contrat(
        db: Session,
        employe_id: int,
        type_contrat: str,  # CDI, CDD, Stage
        date_debut: date,
        date_fin: Optional[date],
        poste: str,
        salaire_base: float,
        coefficient: Optional[int] = None,
        classification: Optional[str] = None,
        periode_essai_jours: int = 90  # Cameroon standard: 3 months for CDI
    ) -> ContratTravail:
        """Create employment contract with Cameroon legal compliance"""
        contrat = ContratTravail(
            employe_id=employe_id,
            type_contrat=type_contrat,
            date_debut=date_debut,
            date_fin=date_fin,
            poste=poste,
            salaire_base=salaire_base,
            coefficient=coefficient,
            classification=classification,
            periode_essai_jours=periode_essai_jours,
            statut="actif"
        )
        db.add(contrat)
        db.commit()
        db.refresh(contrat)
        return contrat
    
    @staticmethod
    def obtenir_contrats_expirants(db: Session, jours_avance: int = 60) -> List[ContratTravail]:
        """Get contracts expiring soon for renewal alerts"""
        date_limite = date.today() + timedelta(days=jours_avance)
        
        contrats = db.query(ContratTravail).filter(
            and_(
                ContratTravail.date_fin.isnot(None),
                ContratTravail.date_fin <= date_limite,
                ContratTravail.statut == "actif"
            )
        ).all()
        
        return contrats
    
    @staticmethod
    def renouveler_contrat(
        db: Session,
        contrat_id: int,
        nouvelle_date_fin: date,
        nouveau_salaire: Optional[float] = None
    ) -> ContratTravail:
        """Renew employment contract"""
        contrat = db.query(ContratTravail).filter(ContratTravail.id == contrat_id).first()
        if not contrat:
            raise ValueError("Contrat non trouvé")
        
        contrat.date_fin = nouvelle_date_fin
        if nouveau_salaire:
            contrat.salaire_base = nouveau_salaire
        contrat.nombre_renouvellements = (contrat.nombre_renouvellements or 0) + 1
        contrat.date_dernier_renouvellement = datetime.utcnow()
        
        db.commit()
        db.refresh(contrat)
        return contrat


class PaieService:
    """Payroll service - Cameroon specific with configuration-driven rules"""
    
    @staticmethod
    def preparer_bulletin(
        db: Session,
        employe_id: int,
        mois: int,
        annee: int,
        salaire_base: float,
        heures_sup: float = 0,
        primes: List[Dict[str, Any]] = None,
        deductions: List[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Prepare payroll bulletin - Configuration-driven for Cameroon
        
        NOTE: Actual tax rates and social contributions must be configured
        and validated against current Cameroon/CEMAC regulations before
        production use. This is a template structure.
        """
        primes = primes or []
        deductions = deductions or []
        
        # Base salary
        salaire_brut = salaire_base
        
        # Overtime pay (Cameroon: +25% for first 8h, +50% beyond)
        taux_heures_sup = 1.25 if heures_sup <= 8 else 1.5
        indemnite_heures_sup = heures_sup * (salaire_base / 173.33) * taux_heures_sup
        salaire_brut += indemnite_heures_sup
        
        # Add bonuses
        total_primes = sum(p["montant"] for p in primes)
        salaire_brut += total_primes
        
        # Social contributions (CONFIGURATION REQUIRED - rates subject to change)
        # CNPS: 7% employee, 11.5% employer (to be configured)
        taux_cnps = 0.07  # Employee portion - MUST BE CONFIGURED
        cotisation_cnps = salaire_brut * taux_cnps
        
        # Tax on salary (CONFIGURATION REQUIRED)
        # Cameroon uses progressive tax brackets - simplified here
        # Actual calculation requires current tax tables
        taux_impot = 0.02  # Placeholder - MUST BE CONFIGURED
        impot_revenu = salaire_brut * taux_impot
        
        # Total deductions
        total_deductions = cotisation_cnps + impot_revenu
        total_deductions += sum(d["montant"] for d in deductions)
        
        # Net salary
        salaire_net = salaire_brut - total_deductions
        
        return {
            "employe_id": employe_id,
            "periode": f"{annee}-{mois:02d}",
            "salaire_base": salaire_base,
            "heures_sup": heures_sup,
            "indemnite_heures_sup": indemnite_heures_sup,
            "primes": primes,
            "total_primes": total_primes,
            "salaire_brut": salaire_brut,
            "cotisations": {
                "cnps": cotisation_cnps,
                "taux_cnps": taux_cnps
            },
            "impot_revenu": impot_revenu,
            "deductions": deductions,
            "total_deductions": total_deductions,
            "salaire_net": salaire_net,
            "note": "Règles fiscales à configurer selon législation Cameroun actuelle"
        }


class DocumentEmployeService:
    """Employee document management service"""
    
    @staticmethod
    def ajouter_document(
        db: Session,
        employe_id: int,
        type_document: str,
        chemin_fichier: str,
        date_emission: Optional[date] = None,
        date_expiration: Optional[date] = None
    ) -> DocumentEmploye:
        """Add employee document with expiry tracking"""
        document = DocumentEmploye(
            employe_id=employe_id,
            type_document=type_document,
            chemin_fichier=chemin_fichier,
            date_emission=date_emission,
            date_expiration=date_expiration,
            date_ajout=datetime.utcnow()
        )
        db.add(document)
        db.commit()
        db.refresh(document)
        return document
    
    @staticmethod
    def obtenir_documents_expirants(db: Session, jours_avance: int = 30) -> List[DocumentEmploye]:
        """Get documents expiring soon"""
        date_limite = date.today() + timedelta(days=jours_avance)
        
        documents = db.query(DocumentEmploye).filter(
            and_(
                DocumentEmploye.date_expiration.isnot(None),
                DocumentEmploye.date_expiration <= date_limite
            )
        ).all()
        
        return documents


class OrganigrammeService:
    """Organization chart service"""
    
    @staticmethod
    def definir_hierarchie(
        db: Session,
        employe_id: int,
        manager_id: Optional[int],
        departement: str,
        poste: str
    ) -> Organigramme:
        """Define employee hierarchy and department"""
        org = db.query(Organigramme).filter(
            Organigramme.employe_id == employe_id
        ).first()
        
        if org:
            org.manager_id = manager_id
            org.departement = departement
            org.poste = poste
            org.date_mise_a_jour = datetime.utcnow()
        else:
            org = Organigramme(
                employe_id=employe_id,
                manager_id=manager_id,
                departement=departement,
                poste=poste
            )
            db.add(org)
        
        db.commit()
        db.refresh(org)
        return org
    
    @staticmethod
    def obtenir_subordonnes(db: Session, manager_id: int) -> List[Organigramme]:
        """Get all direct reports of a manager"""
        return db.query(Organigramme).filter(
            Organigramme.manager_id == manager_id
        ).all()


class CompetenceService:
    """Skills and competency management service"""
    
    @staticmethod
    def creer_competence(
        db: Session,
        nom: str,
        categorie: str,
        description: str,
        niveau_requis: str
    ) -> Competence:
        """Create skill/competency definition"""
        competence = Competence(
            nom=nom,
            categorie=categorie,
            description=description,
            niveau_requis=niveau_requis
        )
        db.add(competence)
        db.commit()
        db.refresh(competence)
        return competence
    
    @staticmethod
    def attribuer_competence(
        db: Session,
        employe_id: int,
        competence_id: int,
        niveau: str,
        date_evaluation: Optional[date] = None
    ) -> CompetenceEmploye:
        """Assign skill to employee with proficiency level"""
        date_eval = date_evaluation or date.today()
        
        competence_emp = CompetenceEmploye(
            employe_id=employe_id,
            competence_id=competence_id,
            niveau=niveau,
            date_evaluation=date_eval
        )
        db.add(competence_emp)
        db.commit()
        db.refresh(competence_emp)
        return competence_emp
    
    @staticmethod
    def obtenir_competences_employe(db: Session, employe_id: int) -> List[CompetenceEmploye]:
        """Get all employee skills"""
        return db.query(CompetenceEmploye).filter(
            CompetenceEmploye.employe_id == employe_id
        ).all()
