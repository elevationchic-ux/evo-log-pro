"""RH service - Complete HR management for Cameroon/CEMAC compliance"""
from datetime import datetime, date, time, timedelta
from typing import List, Optional, Dict, Any, Union
from sqlalchemy.orm import Session
from sqlalchemy import and_, or_, func, case
from app.models.rh import (
    Conge, Absence, TempsTravail, Formation, ParticipationFormation,
    EvaluationPerformance, ContratTravail, Salaire, Prime, DocumentEmploye,
    Organigramme, Competence, CompetenceEmploye, TypeConge, StatutConge
)
from app.models.user import User
from app.models.agency import Agency

# Droit a conge annuel : 24 jours ouvrables par annee revolue (Code du travail
# camerounais, art. 33). La regle est de valeur legale, pas une donnee locale :
# elle vit ici, unique, pour que l'acces portail et le service ne puissent plus
# se contredire (l'acces annoncait 24 jours, le service 2,5 jours par mois, soit
# 30 -- deux droits differents pour un meme salarie).
DROIT_CONGE_ANNUEL_JOURS_OUVRABLES = 24


def compter_jours_ouvrables(debut: date, fin: date) -> int:
    """Jours ouvrables entre deux dates, dimanche exclu (sens du Code du travail).

    Les fetes chomees ne sont pas retranchees : l'application ne possede aucun
    calendrier national en base. C'est une limite affichee, pas une valeur
    inventee pour faire juste -- un conge compte leger superieur, jamais
    inferieur au reel, ce qui protege le salarie comme la paye.
    """
    if fin < debut:
        raise ValueError("date_fin anterieure a date_debut")
    total = 0
    courant = debut
    while courant <= fin:
        if courant.weekday() != 6:  # 6 = dimanche
            total += 1
        courant += timedelta(days=1)
    return total


def _valeur_enum(valeur):
    """Membre d'enum ou chaine : la forme stockee en base (la valeur)."""
    return valeur.value if hasattr(valeur, "value") else valeur


def _normaliser_heure(valeur: Union[datetime, time, str, None]) -> str:
    """Heure de saisie au format "HH:MM", seule forme lisible par la base.

    Trois formes se presentent selon l'appelant : l'heure HTML d'un champ
    ``<input type="time">`` ("08:30"), un ``time``, ou un ``datetime`` herite
    d'un ancien appel d'API. Elles se ramenent toutes ici, au lieu d'ecrire en
    base une valeur que plus aucune lecture ne saurait reformater. Une saisie
    illegible est refusee : une heure par defaut inventee par l'application
    deviendrait une duree de travail fausse, donc une paye fausse.
    """
    if valeur is None:
        raise ValueError("heure de pointage absente")
    if isinstance(valeur, (datetime, time)):
        return "%02d:%02d" % (valeur.hour, valeur.minute)
    texte = str(valeur).strip()
    for format_ in ("%H:%M", "%H:%M:%S"):
        try:
            parsed = datetime.strptime(texte, format_)
        except ValueError:
            continue
        return "%02d:%02d" % (parsed.hour, parsed.minute)
    raise ValueError(
        f"heure invalide : {texte} (format attendu HH:MM)")


def _minutes(heure: str) -> int:
    """Minutes ecoulees depuis minuit pour une heure "HH:MM"."""
    heures, minutes = heure.split(":")[:2]
    return int(heures) * 60 + int(minutes)


def _date_embauche(db: Session, employe_id: int) -> Optional[date]:
    """Date d'entree en service : le contrat, a defaut la creation du compte.

    `User.date_creation` etait utilisee par l'ancien code -- l'attribut n'existe
    pas, ce qui faisait echouer tout calcul de solde. Le contrat de travail est
    le seul document qui etablit la date d'embauche.
    """
    contrat = db.query(ContratTravail).filter(
        ContratTravail.employe_id == employe_id
    ).order_by(ContratTravail.date_debut.asc()).first()
    if contrat:
        return contrat.date_debut
    employe = db.query(User).filter(User.id == employe_id).first()
    if employe and getattr(employe, "created_at", None):
        return employe.created_at.date() if isinstance(
            employe.created_at, datetime) else employe.created_at
    return None


def _mois_revolus(debut: date, fin: date) -> int:
    """Mois entiers ecoules entre deux dates (base du prorata du droit a conge).

    Un mois ne compte que s'il est reellement accompli : le 11e mois d'un salarie
    entre le 15 ne s'acquiert que le 15 du mois suivant. Arrondi au mois plein,
    jamais au mois entame -- un droit compte leger en faveur du salarie se
    rattrape le mois suivant, un droit surcompte se paie en conges indus.
    """
    if fin < debut:
        return 0
    mois = (fin.year - debut.year) * 12 + (fin.month - debut.month)
    if fin.day < debut.day:
        mois -= 1
    return max(0, mois)


class CongeService:
    """Leave management service - Cameroon labor law compliant"""
    
    @staticmethod
    def calculer_solde_conge(db: Session, employe_id: int, annee: int) -> Dict[str, Any]:
        """Calculate leave balance - Cameroon: 24 working days per full year"""
        conges_pris = db.query(func.sum(Conge.nombre_jours)).filter(
            and_(
                Conge.employe_id == employe_id,
                Conge.type_conge == TypeConge.CONGE_ANNUEL,
                Conge.date_debut.between(date(annee, 1, 1), date(annee, 12, 31)),
                # Un conge en cours ou termine a consomme son droit au meme titre
                # qu'un conge approuve : ne compter que "approuve" laisserait un
                # salarie parti demander un second conge sur le meme solde.
                Conge.statut.in_([
                    StatutConge.APPROUVE,
                    StatutConge.EN_COURS,
                    StatutConge.TERMINE,
                ]),
            )
        ).scalar() or 0

        # Le droit se prorata sur les mois reellement travailles dans l'annee
        # consideree : une entree en service en septembre ne donne pas droit aux
        # douze mois. L'ancienne regle (2,5 jours par mois, soit 30 jours par an)
        # contredisait les 24 jours que l'application annonce par ailleurs.
        droit = CongeService.droit_conge(db, employe_id, annee)

        return {
            "solde": droit,
            "utilise": float(conges_pris),
            "reste": round(droit - float(conges_pris), 1),
            "annee": annee
        }

    @staticmethod
    def droit_conge(db: Session, employe_id: int, annee: int) -> float:
        """Jours ouvrables acquis sur l'annee : 24 pour douze mois revolus."""
        if annee > date.today().year:
            # Une annee future n'a pas encore ete travaille : rien n'est du.
            return 0.0
        entree = _date_embauche(db, employe_id)
        borne = min(date(annee, 12, 31), date.today())
        if entree and entree > borne:
            return 0.0
        # Une entree anterieure a l'annee consideree ne prorata rien : les douze
        # mois de cette annee-la sont dus dans leur integralite.
        debut_ref = max(entree, date(annee, 1, 1)) if entree else date(annee, 1, 1)
        mois = min(12, _mois_revolus(debut_ref, borne))
        return round(DROIT_CONGE_ANNUEL_JOURS_OUVRABLES * mois / 12, 1)
    
    @staticmethod
    def demander_conge(
        db: Session,
        employe_id: int,
        type_conge: str,
        date_debut: date,
        date_fin: date,
        motif: Optional[str] = None,
        approbateur_id: Optional[int] = None
    ) -> Conge:
        """Submit leave request with automatic workflow"""
        if date_fin < date_debut:
            raise ValueError("date_fin anterieure a date_debut")
        try:
            type_retenu = TypeConge(type_conge)
        except ValueError:
            # Une valeur hors enum ne part pas en base : la colonne est contrainte
            # et l'ecran n'a aucun libelle a afficher pour un type invente.
            raise ValueError(
                "type de conge inconnu : "
                + ", ".join(t.value for t in TypeConge))

        nombre_jours = compter_jours_ouvrables(date_debut, date_fin)

        # Check leave balance for annual leave
        if type_retenu == TypeConge.CONGE_ANNUEL:
            solde = CongeService.calculer_solde_conge(db, employe_id, date_debut.year)
            if solde["reste"] < nombre_jours:
                raise ValueError(
                    f"Solde insuffisant: {solde['reste']} jours ouvrables "
                    f"disponibles sur {date_debut.year}")
        
        conge = Conge(
            employe_id=employe_id,
            type_conge=type_retenu,
            date_debut=date_debut,
            date_fin=date_fin,
            nombre_jours=nombre_jours,
            motif=(motif or "").strip() or None,
            approbateur_id=approbateur_id,
            statut=StatutConge.EN_ATTENTE,
            date_demande=datetime.now()
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
        
        conge.statut = StatutConge.APPROUVE
        conge.approbateur_id = approbateur_id
        conge.date_approbation = datetime.now()
        conge.commentaire_approbation = (commentaire or "").strip() or None
        # Une approbation n'efface pas le motif d'un refus anterieur : la colonne
        # garde la trace de la decision precedente tant qu'elle n'est pas vide.
        conge.motif_refus = None
        
        db.commit()
        db.refresh(conge)
        return conge
    
    @staticmethod
    def rejeter_conge(db: Session, conge_id: int, approbateur_id: int, motif_refus: str) -> Conge:
        """Reject leave request"""
        conge = db.query(Conge).filter(Conge.id == conge_id).first()
        if not conge:
            raise ValueError("Congé non trouvé")
        
        conge.statut = StatutConge.REFUSE
        conge.approbateur_id = approbateur_id
        conge.date_approbation = datetime.now()
        # Un refus sans motif saisi reste SANS motif : le decideur peut refuser,
        # l'application n'invente pas la raison qu'il n'a pas donnee.
        conge.motif_refus = (motif_refus or "").strip() or None
        
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
        motif: Optional[str] = None,
        justifie: bool = False
    ) -> Absence:
        """Record absence with justification tracking

        La duree s'appuie sur le calendrier, jamais sur une saisie libre : une
        absence du 3 au 5 dure trois jours, quel que soit ce qu'a tape l'agent.
        Le caractere justifie reste une declaration de l'agent ou du superviseur,
        pas une déduction de l'application.
        """
        if date_fin < date_debut:
            raise ValueError("date_fin anterieure a date_debut")
        if not type_absence:
            # NOT NULL en base : une absence sans type connu n'est pas requalifiee
            # d'office pour satisfaire la contrainte.
            raise ValueError("type_absence est requis")
        nombre_jours = (date_fin - date_debut).days + 1
        
        absence = Absence(
            employe_id=employe_id,
            type_absence=type_absence,
            date_debut=date_debut,
            date_fin=date_fin,
            nombre_jours=nombre_jours,
            motif=(motif or "").strip() or None,
            justifie=justifie,
            date_enregistrement=datetime.now()
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
    """Working time management service - Cameroon labor law compliant

    L'heure de pointage est une heure de saisie ("08:30"), pas un horodatage :
    la colonne `temps_travail.heure_arrivee` est un VARCHAR(5) en base. L'ancien
    code y ecrivait un `datetime` complet, que plus aucune lecture ne savait
    reformater, et calculait les heures par soustraction de deux datetime --
    operation impossible sur des chaines, donc fausse des le premier releve.
    """

    @staticmethod
    def pointer_arrivee(db: Session, employe_id: int, date_pointage: date, heure_arrivee: Union[datetime, time, str]) -> TempsTravail:
        """Clock in - attendance tracking"""
        heure = _normaliser_heure(heure_arrivee)
        existant = db.query(TempsTravail).filter(
            and_(
                TempsTravail.employe_id == employe_id,
                TempsTravail.date == date_pointage,
            )
        ).first()
        if existant:
            # Deux arrivees le meme jour rendraient le depart ambigu (lequel
            # solder ?) et le cumul d'heures faux : le releve existant doit etre
            # corrige, pas double.
            raise ValueError(
                f"Un pointage existe deja pour le {date_pointage.isoformat()} "
                "(arrivee " + str(existant.heure_arrivee) + ")")

        pointage = TempsTravail(
            employe_id=employe_id,
            date=date_pointage,
            heure_arrivee=heure,
            # "en_attente" = releve incomplet, aucune duree ne peut en etre tiree.
            # La presence ne se deduit pas d'un statut invente : elle se lit sur
            # l'existence de la ligne.
            statut="en_attente"
        )
        db.add(pointage)
        db.commit()
        db.refresh(pointage)
        return pointage
    
    @staticmethod
    def pointer_depart(db: Session, employe_id: int, date_pointage: date, heure_depart: Union[datetime, time, str]) -> TempsTravail:
        """Clock out - calculate hours worked"""
        depart = _normaliser_heure(heure_depart)
        pointage = db.query(TempsTravail).filter(
            and_(
                TempsTravail.employe_id == employe_id,
                TempsTravail.date == date_pointage,
                TempsTravail.heure_depart.is_(None)
            )
        ).first()
        
        if not pointage:
            raise ValueError("Pas de pointage d'arrivée trouvé")

        minutes = _minutes(depart) - _minutes(pointage.heure_arrivee)
        if minutes < 0:
            # Un depart avant l'arrivee n'est pas une duree negative en paye :
            # c'est une saisie erronee, et elle doit rester visible comme telle.
            raise ValueError(
                f"Heure de depart ({depart}) anterieure a l'arrivee "
                f"({pointage.heure_arrivee})")
        heures = minutes / 60.0

        pointage.heure_depart = depart
        pointage.heures_travaillees = round(heures, 2)
        pointage.statut = "valide"
        
        # Calculate overtime if > 8 hours (Cameroon standard)
        if heures > 8:
            pointage.heures_sup = round(heures - 8, 2)
        
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
            # Les sommes sortent en Decimal de la base : le schema repond en
            # float, et un Decimal non converti serait refuse a la validation.
            "heures_travaillees": round(float(result.total or 0), 2),
            "heures_sup": round(float(result.sup or 0), 2),
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
            # Vocabulaire du modele : "planifiee". Les deux orthographes auraient
            # fait deux etats differents pour une meme realite dans les requetes.
            statut="planifiee"
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
            date_inscription=datetime.now(),
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
            date_evaluation=datetime.now()
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
        contrat.date_dernier_renouvellement = datetime.now()
        
        db.commit()
        db.refresh(contrat)
        return contrat


class PaieService:
    """Payroll service - Cameroon specific with configuration-driven rules

    Les taux ne sont pas redéfinis ici : CNPS et barème IRGM viennent de
    PaieOHADAService, source unique du backend. Ce que cette classe ajoute est
    la structure du bulletin (brut, cotisations, net), pas une deuxieme table de
    taux qui pourrait contredire la première.
    """

    # Base de conversion mensuelle : la duree légale camerounaise ramenée en
    # heures par mois (2 080 h/an / 12). Un contrat portant un horaire explicite
    # (35h, 38h, 40h par semaine) prend neanmoins la priorité : c'est la durée
    # réellement convenue, pas la valeur par défaut du code du travail.
    HEURES_MENSUELLES_FORFAIT = 173.33

    @staticmethod
    def heures_mensuelles_contrat(db: Session, employe_id: int) -> float:
        """Heures mensuelles de référence : l'horaire du contrat, sinon le forfait."""
        contrat = db.query(ContratTravail).filter(
            and_(
                ContratTravail.employe_id == employe_id,
                ContratTravail.statut == "actif",
            )
        ).order_by(ContratTravail.date_debut.desc()).first()
        horaire = (contrat.horaire_travail if contrat else None) or ""
        chiffre = "".join(c for c in str(horaire) if (c.isdigit() or c == "."))
        if chiffre:
            try:
                hebdo = float(chiffre)
                if 0 < hebdo <= 80:
                    return round(hebdo * 52 / 12, 2)
            except ValueError:
                pass
        return PaieService.HEURES_MENSUELLES_FORFAIT

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
        Prepare payroll bulletin - Cameroon/CEMAC, rates from PaieOHADAService
        """
        primes = primes or []
        deductions = deductions or []
        
        # Base salary
        salaire_brut = salaire_base
        
        # Overtime pay (Cameroon: +25% for first 8h, +50% beyond)
        taux_heures_sup = 1.25 if heures_sup <= 8 else 1.5
        heures_ref = PaieService.heures_mensuelles_contrat(db, employe_id)
        taux_horaire = salaire_base / heures_ref
        indemnite_heures_sup = heures_sup * taux_horaire * taux_heures_sup
        salaire_brut += indemnite_heures_sup
        
        # Add bonuses
        total_primes = sum(p["montant"] for p in primes)
        salaire_brut += total_primes
        
        # CNPS: source unique = PaieOHADAService (plus de taux 7% divergent ici).
        from app.services.rh_avance_service import PaieOHADAService
        taux_cnps = PaieOHADAService.TAUX_CNPS_PENSION + PaieOHADAService.TAUX_CNPS_ACCIDENTS
        cotisation_cnps = salaire_brut * taux_cnps
        
        # Tax on salary  barème progressif unique du backend (IRGM Cameroun),
        # assiette = brut - cotisations salariales. L'ancien « 2% plat sur le
        # brut » (placeholder) est supprimé : il sous-imposait tout le monde.
        base_imposable = salaire_brut - cotisation_cnps
        impot_revenu = PaieOHADAService.calculer_irmg(base_imposable)
        
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
            "heures_mensuelles_reference": heures_ref,
            "taux_horaire": round(taux_horaire, 2),
            "taux_majoration_heures_sup": taux_heures_sup,
            "indemnite_heures_sup": round(indemnite_heures_sup, 2),
            "primes": primes,
            "total_primes": total_primes,
            "salaire_brut": round(salaire_brut, 2),
            "cotisations": {
                "cnps": round(cotisation_cnps, 2),
                "taux_cnps": taux_cnps
            },
            "base_imposable": round(base_imposable, 2),
            "impot_revenu": round(impot_revenu, 2),
            "deductions": deductions,
            "total_deductions": round(total_deductions, 2),
            "salaire_net": round(salaire_net, 2),
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
            date_ajout=datetime.now()
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
            org.date_mise_a_jour = datetime.now()
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
