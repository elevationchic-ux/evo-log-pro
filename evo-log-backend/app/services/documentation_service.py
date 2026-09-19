"""Documentation and Training Services - Cameroon/CEMAC"""
from datetime import datetime, date, timedelta
from typing import Dict, Any, List
from sqlalchemy.orm import Session
from app.models.reglementaire import Reglementation, AlerteReglementaire, DocumentUtilisateur, ProcedureOperationnelle, FAQ
from app.models.formation import ModuleFormation, QuizFormation, CertificationUtilisateur, SupportUtilisateur


class DocumentationService:
    """Documentation service for Cameroon/CEMAC"""
    
    @staticmethod
    def creer_document(
        db: Session,
        titre: str,
        type_document: str,
        categorie: str,
        contenu: str,
        langue: str = "fr"
    ) -> DocumentUtilisateur:
        """Créer document utilisateur"""
        doc = DocumentUtilisateur(
            titre=titre,
            type_document=type_document,
            categorie=categorie,
            contenu=contenu,
            langue=langue,
            date_publication=date.today(),
            est_publie=True
        )
        db.add(doc)
        db.commit()
        db.refresh(doc)
        return doc
    
    @staticmethod
    def creer_procedure(
        db: Session,
        code: str,
        titre: str,
        description: str,
        categorie: str,
        etapes: List[Dict[str, Any]]
    ) -> ProcedureOperationnelle:
        """Créer procédure opérationnelle"""
        import json
        
        procedure = ProcedureOperationnelle(
            code=code,
            titre=titre,
            description=description,
            categorie=categorie,
            etapes=json.dumps(etapes),
            duree_estime_minutes=30,
            est_actif=True,
            date_creation=date.today()
        )
        db.add(procedure)
        db.commit()
        db.refresh(procedure)
        return procedure
    
    @staticmethod
    def creer_faq(
        db: Session,
        question: str,
        reponse: str,
        categorie: str
    ) -> FAQ:
        """Créer FAQ"""
        faq = FAQ(
            question=question,
            reponse=reponse,
            categorie=categorie,
            date_creation=date.today(),
            est_publie=True
        )
        db.add(faq)
        db.commit()
        db.refresh(faq)
        return faq
    
    @staticmethod
    def ajouter_reglementation(
        db: Session,
        code: str,
        titre: str,
        type_reglement: str,
        date_promulgation: date,
        description: str
    ) -> Reglementation:
        """Ajouter réglementation"""
        reg = Reglementation(
            code=code,
            titre=titre,
            type_reglement=type_reglement,
            date_promulgation=date_promulgation,
            date_application=date_promulgation,
            description=description,
            est_actif=True
        )
        db.add(reg)
        db.commit()
        db.refresh(reg)
        return reg
    
    @staticmethod
    def creer_alerte_reglementaire(
        db: Session,
        reglementation_id: int,
        type_alerte: str,
        titre: str,
        description: str,
        date_publication: date
    ) -> AlerteReglementaire:
        """Créer alerte réglementaire"""
        alerte = AlerteReglementaire(
            reglementation_id=reglementation_id,
            type_alerte=type_alerte,
            titre=titre,
            description=description,
            date_publication=date_publication,
            est_resolue=False
        )
        db.add(alerte)
        db.commit()
        db.refresh(alerte)
        return alerte


class FormationService:
    """Training service for Cameroon/CEMAC"""
    
    @staticmethod
    def creer_module_formation(
        db: Session,
        titre: str,
        description: str,
        contenu: str,
        categorie: str,
        niveau: str,
        duree_minutes: int
    ) -> ModuleFormation:
        """Créer module de formation"""
        module = ModuleFormation(
            titre=titre,
            description=description,
            contenu=contenu,
            categorie=categorie,
            niveau=niveau,
            duree_minutes=duree_minutes,
            est_publie=True,
            date_publication=date.today()
        )
        db.add(module)
        db.commit()
        db.refresh(module)
        return module
    
    @staticmethod
    def creer_quiz(
        db: Session,
        module_id: int,
        titre: str,
        nombre_questions: int,
        score_reussite: int
    ) -> QuizFormation:
        """Créer quiz pour module"""
        quiz = QuizFormation(
            module_id=module_id,
            titre=titre,
            nombre_questions=nombre_questions,
            score_reussite=score_reussite,
            est_actif=True,
            date_creation=date.today()
        )
        db.add(quiz)
        db.commit()
        db.refresh(quiz)
        return quiz
    
    @staticmethod
    def passer_quiz(
        db: Session,
        quiz_id: int,
        utilisateur_id: int,
        reponses: List[Dict[str, Any]]
    ) -> CertificationUtilisateur:
        """Passer quiz et obtenir certification"""
        from app.models.formation import TentativeQuiz, QuestionQuiz
        
        # Get quiz and questions
        quiz = db.query(QuizFormation).filter(QuizFormation.id == quiz_id).first()
        questions = db.query(QuestionQuiz).filter(QuestionQuiz.quiz_id == quiz_id).all()
        
        # Calculate score
        score = 0
        score_maximum = 0
        for question in questions:
            score_maximum += question.points
            # Check if answer is correct (simplified)
            score += question.points  # Assume all correct for demo
        
        pourcentage = (score / score_maximum) * 100 if score_maximum > 0 else 0
        
        # Record attempt
        tentative = TentativeQuiz(
            quiz_id=quiz_id,
            utilisateur_id=utilisateur_id,
            date_debut=datetime.utcnow(),
            date_fin=datetime.utcnow(),
            score=score,
            score_maximum=score_maximum,
            pourcentage=pourcentage,
            statut="termine",
            reponses=str(reponses)
        )
        db.add(tentative)
        db.commit()
        
        # Create certification if passed
        if pourcentage >= quiz.score_reussite:
            certification = CertificationUtilisateur(
                utilisateur_id=utilisateur_id,
                module_id=quiz.module_id,
                date_passage=datetime.utcnow(),
                score=score,
                score_maximum=score_maximum,
                pourcentage=pourcentage,
                statut="reussi",
                numero_certificat=f"CERT-{datetime.now().strftime('%Y%m%d%H%M%S')}",
                date_expiration=date.today() + timedelta(days=365)
            )
            db.add(certification)
            db.commit()
            db.refresh(certification)
            return certification
        
        return None
    
    @staticmethod
    def creer_ticket_support(
        db: Session,
        utilisateur_id: int,
        titre: str,
        description: str,
        categorie: str,
        priorite: str
    ) -> SupportUtilisateur:
        """Créer ticket de support"""
        ticket = SupportUtilisateur(
            utilisateur_id=utilisateur_id,
            type_support="TICKET",
            titre=titre,
            description=description,
            categorie=categorie,
            priorite=priorite,
            statut="ouvert",
            date_creation=datetime.utcnow()
        )
        db.add(ticket)
        db.commit()
        db.refresh(ticket)
        return ticket
    
    @staticmethod
    def resoudre_ticket(db: Session, ticket_id: int, solution: str) -> SupportUtilisateur:
        """Résoudre ticket de support"""
        ticket = db.query(SupportUtilisateur).filter(SupportUtilisateur.id == ticket_id).first()
        if not ticket:
            raise ValueError("Ticket non trouvé")
        
        ticket.statut = "resolu"
        ticket.solution = solution
        ticket.date_resolution = datetime.utcnow()
        db.commit()
        db.refresh(ticket)
        return ticket


class CameroonContentService:
    """Cameroon-specific content service"""
    
    @staticmethod
    def generer_contenu_initial(db: Session):
        """Générer contenu initial pour Cameroun/CEMAC"""
        # Documentation
        DocumentationService.creer_document(
            db,
            "Guide Import Douala",
            "MANUEL",
            "DOUANE",
            """# Guide Import via Port de Douala

Ce guide explique pas à pas comment importer des marchandises via le Port de Douala (PAD).

## Étape 1: Préparation
- Obtenir numéro de connaissement
- Préparer documents commerciaux
- Vérifier conformité produits

## Étape 2: BSC
- Générer BSC via CNCC
- Payer frais BSC
- Obtenir validation

## Étape 3: CSC
- Demander certificat sécurité
- Inspection par INS
- Obtenir validation

## Étape 4: DUM
- Créer DUM via SYGED
- Déclarer marchandise
- Payer droits de douane
            """,
            "fr"
        )
        
        # FAQ
        DocumentationService.creer_faq(
            db,
            "Comment obtenir un BSC?",
            "Le BSC s'obtient via la Chambre de Commerce (CNCC). Vous devez soumettre le numéro de connaissement et payer les frais applicables.",
            "DOUANE"
        )
        
        # Training module
        FormationService.creer_module_formation(
            db,
            "Introduction à la Douane Camerounaise",
            "Formation sur les procédures douanières au Cameroun",
            """# Module 1: Introduction

Ce module couvre les bases de la douane camerounaise.

## Le Code des Douanes
- Loi n°98/012 du 14 juillet 1998
- Régimes douaniers
- Taux de droits

## Procédures
- Import
- Export
- Transit
            """,
            "DOUANE",
            "DEBUTANT",
            60
        )
        
        # Procedure
        DocumentationService.creer_procedure(
            db,
            "PROC-IMPORT-DOUALA",
            "Procédure Import via Douala",
            "Guide complet pour importer via Port de Douala",
            "IMPORT",
            [
                {"etape": 1, "titre": "Préparation", "description": "Documents et BSC"},
                {"etape": 2, "titre": "Arrivée Navire", "description": "Enregistrement conteneurs"},
                {"etape": 3, "titre": "Déchargement", "description": "Opérations portuaires"},
                {"etape": 4, "titre": "Déclaration", "description": "DUM et SYGED"},
                {"etape": 5, "titre": "Paiement", "description": "Droits et taxes"}
            ]
        )
