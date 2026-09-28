"""
RH models - Complete HR management for Cameroon/CEMAC compliance

Forme des tables : la reference est le schema produit par la chaine Alembic
complete (scripts/audit_schema_drift.py --replay), pas la base de developpement.
Celle-ci est bootstrappee par create_all() puis bricolee a la main : elle presente
l'union des formes et ne revele donc aucune divergence, alors qu'en production
create_all() est desactive et que la premiere lecture d'une colonne inventee leve
"no such column" en 500. Chaque classe ci-dessous declare donc :

  - les colonnes REELLEMENT en base, sous leur nom et leur type de base (un
    horodatage en base est un DateTime ici : declare Date, le processeur de
    resultat refuse "2026-09-25 08:30:00" et la ligne devient illisible) ;
  - les colonnes que le code utilise vraiment et que la migration 028 ajoute ;
  - rien d'autre. Les champs "de modelisation" sans colonne et sans lecteur
  (solde_conge, preavis, convention_collective, nombre_places, sous_ordinates...)
  ont ete retires : une colonne que personne n'ecrit ni ne lit est une promesse
  que l'application ne tient pas.

Statuts et types : Enum(..., native_enum=False) avec values_callable, c'est-a-
dire la VALEUR ("en_attente") stockee, pas le NOM ("APPROUVE"). Les schemas
Pydantic, les filtres HTTP et les donnees heritees manipulent tous la valeur ;
stocker le nom rendrait toute relecture ulterieurement incoherente. Un statut
hors liste echoue a l'ecriture plutot que de s'installer silencieusement.
"""
from sqlalchemy import (
    Column, Integer, String, Text, DateTime, Boolean, Float, ForeignKey, Enum,
    Date, Numeric, event
)
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
import enum
from app.core.database import Base


class TypeConge(str, enum.Enum):
    """Leave types compliant with Cameroon labor law"""
    CONGE_ANNUEL = "conge_annuel"
    CONGE_MALADIE = "conge_maladie"
    CONGE_MATERNITE = "conge_maternite"
    CONGE_PATERNITE = "conge_paternite"
    CONGE_EXCEPTIONNEL = "conge_exceptionnel"
    CONGE_SANS_SOLDE = "conge_sans_solde"
    ABSENCE_AUTORISEE = "absence_autorisee"


class StatutConge(str, enum.Enum):
    """Leave status"""
    EN_ATTENTE = "en_attente"
    APPROUVE = "approuve"
    REFUSE = "refuse"
    EN_COURS = "en_cours"
    TERMINE = "termine"
    ANNULE = "annule"


def _enum(type_enum, longueur=30):
    """Colonne a valeurs limitees, stockee en VARCHAR sous sa VALEUR.

    native_enum=False : Postgres comme SQLite recoivent un VARCHAR simple, la
    chaine Alembic n'a pas a creer de type composite. values_callable : on ecrit
    "conge_annuel" et non "CONGE_ANNUEL", soit exactement ce que renvoie l'API et
    ce que les schemas Pydantic attendent.
    """
    return Enum(type_enum, native_enum=False, length=longueur,
                values_callable=lambda e: [m.value for m in e])


class Conge(Base):
    """Leave management model - Cameroon labor law compliant"""
    __tablename__ = "conges"

    id = Column(Integer, primary_key=True, index=True)
    employe_id = Column(Integer, ForeignKey('users.id'), nullable=False)
    type_conge = Column(_enum(TypeConge), nullable=False)
    date_debut = Column(Date, nullable=False)
    date_fin = Column(Date, nullable=False)
    nombre_jours = Column(Integer, nullable=False)
    statut = Column(_enum(StatutConge), nullable=False,
                    default=StatutConge.EN_ATTENTE)
    # NULLable ici, NOT NULL en base : la migration 028 leve la contrainte. Une
    # raison forcee n'est pas une raison -- mieux vaut une demande sans motif
    # qu'un motif invente par l'application pour satisfaire la contrainte.
    motif = Column(Text)
    # Herite : la base stocke un horodatage complet, date de depot a la seconde.
    date_demande = Column(DateTime, nullable=False, server_default=func.now())
    date_approbation = Column(DateTime)
    approbateur_id = Column(Integer, ForeignKey('users.id'))
    commentaire_approbation = Column(Text)
    motif_refus = Column(Text)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    # Relationships
    employe = relationship("User", foreign_keys=[employe_id])
    approbateur = relationship("User", foreign_keys=[approbateur_id])


class Absence(Base):
    """Absence tracking model

    La base raisonnera toujours enperiode (`date_debut`/`date_fin`,
    `nombre_jours`), pas en jour unique : le modele herite declare `date` et
    `justifiee`, deux colonnes qui n'existent nulle part, ce qui fit echouer
    chaque lecture d'absences. Les releves d'horaires (arrivee/departee)
    restent porteurs, mais sur des colonnes que 028 cree.
    """
    __tablename__ = "absences"

    id = Column(Integer, primary_key=True, index=True)
    employe_id = Column(Integer, ForeignKey('users.id'), nullable=False)
    type_absence = Column(String(50), nullable=False)  # maladie, famille, personnelle
    date_debut = Column(Date, nullable=False)
    date_fin = Column(Date, nullable=False)
    nombre_jours = Column(Integer, nullable=False)
    motif = Column(Text)
    justifie = Column(Boolean, nullable=False, default=False)
    date_enregistrement = Column(DateTime, nullable=False,
                                 server_default=func.now())
    # Demi-journees : saisie horaire sur une absence d'une partie de journee.
    heure_debut = Column(String(5))
    heure_fin = Column(String(5))
    nombre_heures = Column(Numeric)

    # Relationships
    employe = relationship("User", foreign_keys=[employe_id])


class TempsTravail(Base):
    """Work time tracking model - Timesheets

    heure_arrivee/heure_depart etaient DATETIME en base alors que tout le code
    (chef_personnel, rh_service, shift_planning) les manipule en "HH:MM". Le
    type est ramene a une heure de saisie dans 028 : un pointage n'est pas un
    horodatage, et la valeur heritee etait de toute facon illegible.
    """
    __tablename__ = "temps_travail"

    id = Column(Integer, primary_key=True, index=True)
    employe_id = Column(Integer, ForeignKey('users.id'), nullable=False)
    date = Column(Date, nullable=False)
    heure_arrivee = Column(String(5), nullable=False)
    heure_depart = Column(String(5))
    heures_travaillees = Column(Numeric)
    heures_sup = Column(Numeric)
    statut = Column(String(20), nullable=False, default="valide")  # valide, en_attente, refuse
    tache = Column(String(200))

    # Relationships
    employe = relationship("User", foreign_keys=[employe_id])


class Formation(Base):
    """Training management model"""
    __tablename__ = "formations"

    id = Column(Integer, primary_key=True, index=True)
    titre = Column(String(200), nullable=False)
    description = Column(Text)
    date_debut = Column(Date, nullable=False)
    date_fin = Column(Date, nullable=False)
    duree_heures = Column(Integer, nullable=False)
    cout = Column(Numeric, nullable=False, default=0)
    formateur = Column(String(100))
    lieu = Column(String(100))
    agency_id = Column(Integer, ForeignKey('agencies.id'))
    statut = Column(String(20), nullable=False, default="planifiee")
    # CEMAC : certaines habilitations (conduite, produits dangereux) perissent.
    certificat_valide_jusque = Column(Date)

    # Relationships
    agency = relationship("Agency", foreign_keys=[agency_id])
    participations = relationship("ParticipationFormation",
                                  back_populates="formation")


class ParticipationFormation(Base):
    """Training participation model

    Nom de table reel : `participations_formation` (singulier). Le modele
    declarait `participations_formations` : creation ORM jamais migratee,
    lectures en "no such table".
    """
    __tablename__ = "participations_formation"

    id = Column(Integer, primary_key=True, index=True)
    formation_id = Column(Integer, ForeignKey('formations.id'), nullable=False)
    employe_id = Column(Integer, ForeignKey('users.id'), nullable=False)
    date_inscription = Column(DateTime, nullable=False,
                              server_default=func.now())
    present = Column(Boolean)
    certificat_obtenu = Column(Boolean)
    commentaire = Column(Text)
    statut = Column(String(20), nullable=False, default="inscrit")

    # Relationships
    formation = relationship("Formation", back_populates="participations")
    employe = relationship("User", foreign_keys=[employe_id])


class EvaluationPerformance(Base):
    """Performance evaluation model

    objectifs_atteints/objectifs_total sont des compteurs en base (INTEGER), pas
    du texte : le rapport de notation calcule un taux, ce qui exige des nombres.
    """
    __tablename__ = "evaluations_performance"

    id = Column(Integer, primary_key=True, index=True)
    employe_id = Column(Integer, ForeignKey('users.id'), nullable=False)
    evaluateur_id = Column(Integer, ForeignKey('users.id'), nullable=False)
    periode_debut = Column(Date, nullable=False)
    periode_fin = Column(Date, nullable=False)
    note_globale = Column(Float, nullable=False)
    objectifs_atteints = Column(Integer, nullable=False, default=0)
    objectifs_total = Column(Integer, nullable=False, default=0)
    commentaires = Column(Text)
    date_evaluation = Column(DateTime, nullable=False,
                             server_default=func.now())

    # Relationships
    employe = relationship("User", foreign_keys=[employe_id])
    evaluateur = relationship("User", foreign_keys=[evaluateur_id])


class ContratTravail(Base):
    """Employment contract model - Cameroon labor law compliant"""
    __tablename__ = "contrats_travail"

    id = Column(Integer, primary_key=True, index=True)
    employe_id = Column(Integer, ForeignKey('users.id'), nullable=False)
    type_contrat = Column(String(50), nullable=False)  # CDI, CDD, STAGE, APPRENTISSAGE
    date_debut = Column(Date, nullable=False)
    date_fin = Column(Date)
    poste = Column(String(100), nullable=False)
    salaire_base = Column(Numeric, nullable=False)
    # Convention collective camerounaise : le coefficient et la classification
    # determinent la grille salariale, d'ou leur presence en base.
    coefficient = Column(Integer)
    classification = Column(String(50))
    periode_essai_jours = Column(Integer, nullable=False, default=90)  # Cameroun : 90 jours pour un CDI
    statut = Column(String(20), nullable=False, default="actif")  # actif, expire, resilie, suspendu
    nombre_renouvellements = Column(Integer, default=0)
    date_dernier_renouvellement = Column(DateTime)
    # Trois colonnes que l'attestation de travail et la fiche salarie exigent.
    departement = Column(String(100))
    horaire_travail = Column(String(50))  # 35h, 40h, etc.
    lieu_travail = Column(String(200))

    # Relationships
    employe = relationship("User", foreign_keys=[employe_id])


class Salaire(Base):
    """Salary management model - CEMAC compliant

    Deux generations cohabitent dans la meme table. L'heritee (mois, annee,
    salaire_brut, heures_sup, primes, deductions) est NOT NULL et filtree par
    d'anciens services ; la generation détaillée (CNPS, IRGM, primes par
    categorie) est celle que la loi camerounaise rend controlee. Le modele
    conserve les deux et les tient coherentles : _synchroniser_herite() recopie
    le detail vers l'herite a chaque ecriture, un seul endroit sachant ce
    qu'est un brut.
    """
    __tablename__ = "salaires"

    id = Column(Integer, primary_key=True, index=True)
    employe_id = Column(Integer, ForeignKey('users.id'), nullable=False)

    # --- generation heritee : contrainte NOT NULL en base, lisible par l'app ---
    mois = Column(Integer, nullable=False)
    annee = Column(Integer, nullable=False)
    salaire_brut = Column(Numeric, nullable=False, default=0)
    heures_sup = Column(Numeric, nullable=False, default=0)
    primes = Column(Numeric, nullable=False, default=0)
    deductions = Column(Numeric, nullable=False, default=0)

    # --- generation detaillee (ajoutee par 028) ---
    periode_debut = Column(Date, nullable=False)
    periode_fin = Column(Date, nullable=False)
    salaire_base = Column(Numeric, nullable=False)
    heures_supplementaires = Column(Numeric, default=0)
    taux_horaire_sup = Column(Numeric, default=0)
    prime_anciennete = Column(Numeric, default=0)
    prime_performance = Column(Numeric, default=0)
    prime_responsabilite = Column(Numeric, default=0)
    prime_logement = Column(Numeric, default=0)
    prime_transport = Column(Numeric, default=0)
    prime_autre = Column(Numeric, default=0)
    deductions_cnps = Column(Numeric, default=0)  # CEMAC social security
    deductions_impot = Column(Numeric, default=0)
    deductions_avances = Column(Numeric, default=0)
    autres_deductions = Column(Numeric, default=0)

    salaire_net = Column(Numeric, nullable=False)
    devise = Column(String(10), default="XAF")
    date_paiement = Column(DateTime)
    statut = Column(String(20), default="en_attente")  # en_attente, paye, annule
    nombre_heures_travaillees = Column(Numeric, default=0)
    taux_imposition = Column(Numeric, default=0)  # Cameroon tax rate
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    # Relationships
    employe = relationship("User", foreign_keys=[employe_id])


def _somme(fiche, noms):
    return sum(float(getattr(fiche, n) or 0) for n in noms)


def _synchroniser_herite(mapper, connection, target):
    """Aligne les colonnes heritees de `salaires` sur la fiche detaillee.

    Une seule source de verite : le detail. Sans ce recopiage, deux colonnes
    NOT NULL obligatoires resteraient a 0 pendant que le net est calcule sur le
    detail -- tout rapport ancien lisant `salaire_brut` afficherait un faux
    montant, et c'est precisement le genre de donnee inventee que la regle du
    projet interdit.
    """
    if target.periode_debut is not None:
        target.mois = target.periode_debut.month
        target.annee = target.periode_debut.year
    primes = _somme(target, ("prime_anciennete", "prime_performance",
                             "prime_responsabilite", "prime_logement",
                             "prime_transport", "prime_autre"))
    retenues = _somme(target, ("deductions_cnps", "deductions_impot",
                               "deductions_avances", "autres_deductions"))
    target.primes = primes
    target.deductions = retenues
    target.heures_sup = target.heures_supplementaires or 0
    target.salaire_brut = (float(target.salaire_base or 0)
                           + float(target.heures_supplementaires or 0) + primes)
    if not target.salaire_net:
        target.salaire_net = target.salaire_brut - retenues


event.listen(Salaire, "before_insert", _synchroniser_herite)
event.listen(Salaire, "before_update", _synchroniser_herite)


class Prime(Base):
    """Bonus management model"""
    __tablename__ = "primes"

    id = Column(Integer, primary_key=True, index=True)
    employe_id = Column(Integer, ForeignKey('users.id'), nullable=False)
    type_prime = Column(String(50), nullable=False)  # performance, exceptionnelle, projet, logement
    montant = Column(Numeric, nullable=False)
    motif = Column(Text)
    date_prime = Column(Date, nullable=False, server_default=func.current_date())
    # Colonne d'appui des services RH (rh_avance_service) : periodisation YYYY-MM
    # et circuit d'approbation, ajoutees par 028.
    periode = Column(String(20))
    statut = Column(String(20), default="en_attente")
    approuve_par = Column(Integer, ForeignKey('users.id'))

    # Relationships
    employe = relationship("User", foreign_keys=[employe_id])
    valideur = relationship("User", foreign_keys=[approuve_par])


class DocumentEmploye(Base):
    """Employee document management model

    La base ne connait qu'un `chemin_fichier` : le nom affiche et l'URL de
    telechargement s'en derivent, ils n'ont pas a etre stockes une seconde fois
    (et donc a pouvoir contredire le chemin).
    """
    __tablename__ = "documents_employe"

    id = Column(Integer, primary_key=True, index=True)
    employe_id = Column(Integer, ForeignKey('users.id'), nullable=False)
    type_document = Column(String(50), nullable=False)  # cv, diplome, contrat, casier, certificat
    chemin_fichier = Column(String(500), nullable=False)
    date_emission = Column(Date)
    date_expiration = Column(Date)
    date_ajout = Column(DateTime, nullable=False, server_default=func.now())

    # Relationships
    employe = relationship("User", foreign_keys=[employe_id])

    @property
    def nom_fichier(self):
        """Nom affiche : derniere portion du chemin stocke."""
        return (self.chemin_fichier or "").replace("\\", "/").rstrip("/").split("/")[-1]


class Organigramme(Base):
    """Organization chart model"""
    __tablename__ = "organigramme"

    id = Column(Integer, primary_key=True, index=True)
    employe_id = Column(Integer, ForeignKey('users.id'), nullable=False)
    manager_id = Column(Integer, ForeignKey('users.id'))
    departement = Column(String(100), nullable=False)
    poste = Column(String(100), nullable=False)
    date_creation = Column(DateTime, server_default=func.now())
    date_mise_a_jour = Column(DateTime, onupdate=func.now())

    # Relationships
    employe = relationship("User", foreign_keys=[employe_id])
    manager = relationship("User", foreign_keys=[manager_id])


class Competence(Base):
    """Skills/Competencies model"""
    __tablename__ = "competences"

    id = Column(Integer, primary_key=True, index=True)
    nom = Column(String(100), nullable=False)
    categorie = Column(String(50), nullable=False)  # technique, comportementale, linguistique
    description = Column(Text)
    niveau_requis = Column(String(20), nullable=False)  # debutant, intermediaire, avance, expert


class CompetenceEmploye(Base):
    """Employee skills model"""
    __tablename__ = "competences_employe"

    id = Column(Integer, primary_key=True, index=True)
    employe_id = Column(Integer, ForeignKey('users.id'), nullable=False)
    competence_id = Column(Integer, ForeignKey('competences.id'), nullable=False)
    niveau = Column(String(20), nullable=False)
    date_evaluation = Column(Date)

    # Relationships
    employe = relationship("User", foreign_keys=[employe_id])
    competence = relationship("Competence", foreign_keys=[competence_id])
