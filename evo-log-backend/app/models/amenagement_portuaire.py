"""Aménagement portuaire — département autonome (Douala, Kribi, Limbé).

Ce module ne décrit PAS l'exploitation du quai (acconage, escales, tarifs) : il
décrit la maîtrise d'ouvrage, c'est-à-dire tout ce qui précède et accompagne
la mise en service d'une infrastructure. Le découpage reprend le circuit
réellement en vigueur au Cameroun :

  1. la politique portuaire est conduite par le ministère en charge des Ports
     (MINMIVT), avec l'Autorité Portuaire Nationale (APN) comme organe
     technique — c'est elle qui élabore le schéma directeur portuaire national
     et les schémas directeurs d'aménagement des places portuaires ;
  2. le domaine portuaire est délimité, concédé et géré par l'autorité
     portuaire de la place (Port Autonome de Douala, Port Autonome de Kribi,
     Port Autonome de Limbé) — loi n° 2012/021 portant sûreté et sécurité
     dans le domaine maritime, portuaire et des pêches maritimes ;
  3. les travaux et extensions sont financés sur budget de l'autorité
     portuaire, sur subventions, ou en partenariat public-privé (loi
     n° 2023/008 du 25 juillet 2023 fixant le régime général des PPP : modes
     concessifs CET/BOT et autorisations d'occupation du domaine public) ;
  4. la passation obéit au régime des marchés publics camerounais (COLIFE /
     CIP pour la place de Douala) et la conformité environnementale à la loi
     n° 96/012 du 5 août 1996 (EIES, audit IEMU).

PHILOSOPHIE DES DONNÉES — aucune donnée n'est inventée ici.
  * Les tables portent des COLONNES de provenance (source_reference,
    date_verification, autorite_emettrice) : une valeur n'existe que si un
    agent l'a saisie depuis un document réel (schéma directeur approuvé, DTO
    visé, arrêté, rapport de bathymétrie).
  * NULL veut dire « non renseigné », jamais « 0 » ni « moyenne de marché ».
  * Le module ne simule aucune téléprocédure : ce qui dépend d'un tiers
    institutionnel (APN, COLIFE, MINMIVT, MINEPF) répond 501 côté routeur.

Modèle domanial : comme ``ports_cameroun`` et ``terminaux_portuaires`` (données
de référence nationales), ces tables ne portent PAS de ``company_id`` — elles
décrivent l'infrastructure publique du pays, pas le fonds de commerce d'un
tenant. ``app/core/tenant_enforcement.py`` ne les filtre donc pas, ce qui est
le comportement voulu (même raisonnement que pour les incoterms et le plan
comptable COMPTABLE global).
"""
from sqlalchemy import (
    Column, Integer, String, Text, DateTime, Boolean, Date, Numeric,
    ForeignKey, Enum, UniqueConstraint,
)
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
import enum

from app.core.database import Base


# ─── Nomenclatures ───────────────────────────────────────────────────────────

class TypeSchema(str, enum.Enum):
    """Nature du document d'orientation domaniale."""
    SCHEMA_DIRECTEUR = "schema_directeur"          # schéma directeur d'aménagement d'une place
    PLAN_DIRECTEUR = "plan_directeur"              # plan directeur urbain/interne du port
    ETUDE_PROSPECTIVE = "etude_prospective"        # horizon 10-30 ans, scénarios de trafic
    PLAN_MASSE = "plan_masse"                      # plan masse des installations
    PDA = "pda"                                    # plan directeur d'aménagement (ville portuaire)
    REVISION = "revision"                          # révision d'un document existant


class StatutSchema(str, enum.Enum):
    ELABORATION = "elaboration"
    CONSULTATION = "consultation"                  # CCO / communautés portuaires
    DEPOSE = "depose"                              # déposé pour visa ministériel
    APPROUVE = "approuve"
    EN_COURS = "en_cours"                          # en cours d'exécution
    REVISE = "revise"
    ABROGE = "abroge"


class TypeProjet(str, enum.Enum):
    """Famille d'ouvrage du génie portuaire."""
    QUAI = "quai"
    POSTE_QUAI = "poste_quai"
    DRAGAGE = "dragage"                            # approfondissement / accès
    DIGUE = "digue"
    HORS_EMISSION = "hors_emission"                # breakwater
    CHENEAU = "cheneau"                            # chenal d'accès
    AIRE_DEPOT_CONTENEURS = "aire_depot"
    MAGASIN = "magasin"
    TERMINAL = "terminal"                          # création d'un terminal
    ZONE_FRANCHE = "zone_franche"                  # extension de zone franche
    ROUTE_INTERNE = "route_interne"
    VOIE_FERREE = "voie_ferree"                    # raccordement ferroviaire
    RACCORDEMENT = "raccordement"                  # route nationale / corridor
    ENERGIE = "energie"                            # poste HTA, branchement ENEO
    ADDUCTION = "adduction"                        # eau, assainissement
    TELECOM = "telecom"
    ISPS = "isps"                                  # clôture, PC sécurité, contrôle d'accès
    BATIMENT = "batiment"
    AUTRE = "autre"


class StatutProjet(str, enum.Enum):
    IDENTIFIE = "identifie"
    ETUDIE = "etudie"                              # faisabilité bouclée
    INSCRIT_DTO = "inscrit_dto"                    # porté au Document Technique Outil
    NOTIFIE_MINEPF = "notifie_minepf"              # notification de l'engagement (Art. 57)
    EN_ATTRIBUTION = "en_attribution"              # DAO en cours (COLIFE / CIP)
    ATTRIBUE = "attribue"
    EN_CONSTRUCTION = "en_construction"
    RECEPTIONNE = "receptionne"
    EN_SERVICE = "en_service"
    ABANDONNE = "abandonne"


class OrigineFinancement(str, enum.Enum):
    BUDGET_AUTORITE_PORTUAIRE = "budget_autorite_portuaire"
    SUBVENTION_ETAT = "subvention_etat"
    Pret_BAILLEUR = "pret_bailleur"                # BEI, AFD, BAD, JICA, Exim…
    PPP = "ppp"                                    # loi 2023/008
    CONCESSIONNAIRE = "concessionnaire"            # investissement privé amorti sur redevance
    AUTOFINANCEMENT = "autofinancement"
    MIXTE = "mixte"


class TypeMarche(str, enum.Enum):
    TRAVAUX = "travaux"
    FOURNITURES = "fournitures"
    SERVICES = "services"
    ETUDES = "etudes"
    CONTROLE_SURVEILLANCE = "controle_surveillance"
    CONCESSION = "concession"                       # marché de type concessif (PPP)


class CodeMarche(str, enum.Enum):
    AO_RESTREINT = "ao_restreint"
    AO_OUVERT = "ao_ouvert"
    DEMANDE_COTES = "demande_cotes"
    GRE_A_GRE = "gre_a_gre"
    CONTRAT_CADRE = "contrat_cadre"


class StatutMarche(str, enum.Enum):
    PREVU = "prevu"
    PUBLIE = "publie"
    EN_COURS_EVALUATION = "en_cours_evaluation"
    ATTRIBUE = "attribue"
    NOTIFIE = "notifie"
    EN_EXECUTION = "en_execution"
    RECEPTIONNE = "receptionne"
    RESILIE = "resilie"
    ANNULE = "annule"


class TypeTitreDomanial(str, enum.Enum):
    """Occupation / attribution du domaine portuaire."""
    AUTORISATION_OCCUPATION_TEMPORAIRE = "autorisation_temporaire"
    CONVENTION_OCCUPATION = "convention_occupation"
    ATTRIBUTION_DOMAINE_PORTUAIRE = "attribution_domaine"
    PERMIS_DE_TRANCHEE = "permis_tranchee"          # travaux dans une tranchee existante
    AUTORISATION_POLICE_PORTUAIRE = "police_portuaire"
    DECLARATION_PREALABLE = "declaration_preable"
    ARRETE_DELIMITATION = "arrete_delimitation"     # extension du périmètre
    CESSION_REDEVANCE = "cession_redevance"


class TypeContratExploitation(str, enum.Enum):
    """Modèle de transfert d'exploitation du domaine concédé."""
    AFFERMAGE = "affermage"
    CONCESSION_SERVICE = "concession_service"
    BOT = "bot"                                     # Build-Operate-Transfer
    CET = "cet"                                     # Construction-Exploitation-Transfert
    AOT = "aot"                                     # Autorisation d'Occupation Temporaire
    LOTISSEMENT_PORTUAIRE = "lotissement"
    REGIE_DIRECTE = "regie_directe"                 # exploité en régie par l'autorité portuaire


class StatutContrat(str, enum.Enum):
    NEGOCIATION = "negociation"
    APPROUVE = "approuve"
    EN_VIGUEUR = "en_vigueur"
    PROLONGE = "prolonge"
    RESILIE = "resilie"
    ECHEU = "echeu"
    TRANSFERE = "transfere"                         # retour du patrimoine à l'autorité portuaire


class TypeInfrastructure(str, enum.Enum):
    OUVRAGE = "ouvrage"                             # quai, digue, forme, cale
    AIRE = "aire"                                   # terre-plein, revêtement
    BATIMENT = "batiment"
    RESEAU = "reseau"                               # énergie, eau, assainissement, télécom
    EQUIEMENT_QUAI = "equipement_quai"              # portique, convenor, duc-d-albe
    FERROVIAIRE = "ferroviaire"
    ZONE = "zone"


class EtatInfrastructure(str, enum.Enum):
    PROJETEE = "projete"
    EN_CONSTRUCTION = "en_construction"
    OPERATIONNELLE = "operationnelle"
    SOUS_UTILISEE = "sous_utilisee"
    DEGRADEE = "degradee"
    HORS_SERVICE = "hors_service"
    DEMOLIE = "demolie"


class TypeDragage(str, enum.Enum):
    CONSTRUCTION = "construction"                   # approfondissement initial
    ENTRETIEN = "entretien"                         # maintenance de profondeur
    DAPPRECIATION = "appreciation"
    REMBLAIEMENT = "remblaiement"
    DECOMMISSIONNEMENT = "decommissionnement"


class TypeAutorisationTravaux(str, enum.Enum):
    EIES = "eies"                                   # étude d'impact (loi 96/012)
    CE = "certificat_conformite_environnementale"
    IEMU = "iemu"                                   # audit environnemental periodique
    AUTORISATION_DRAGAGE = "autorisation_dragage"
    DEVERSEMENT = "deversement"                     # exutoire/ disposal pour drague
    PERMIS_BATIR = "permis_batir"
    VISITE_CONFORMITE = "visite_conformite"
    AUTRE = "autre"


class StatutAutorisation(str, enum.Enum):
    EN_PREPARATION = "en_preparation"
    DEPOSEE = "deposee"
    COMPLEMENT_REQUIS = "complement_requis"
    ACCORDEE = "accordee"
    REFUSEE = "refusee"
    EXPIREE = "expirée".replace("é", "e")
    RENOUVELEE = "renouvelee"


# ─── 1. Orientation domaniale : schémas directeurs ───────────────────────────

class SchemaDirecteur(Base):
    """Schéma directeur / plan d'aménagement d'une place portuaire.

    Pièce maîtresse du département : c'est le document qui decide ou l'on
    étend le domaine portuaire, quels terminaux sont créés, et a quel
    horizon. Il est élabore par l'APN (national) ou par l'autorité portuaire
    de la place, puis approuve par le gouvernement.
    """
    __tablename__ = "schemas_directeurs_amgt"

    id = Column(Integer, primary_key=True, index=True)
    code = Column(String(40), unique=True, nullable=False, index=True)
    libelle = Column(String(200), nullable=False)
    port_id = Column(Integer, ForeignKey("ports_cameroun.id"), nullable=True, index=True)
    type_schema = Column(Enum(TypeSchema), nullable=False, default=TypeSchema.SCHEMA_DIRECTEUR)
    perimetre = Column(Text)                       # description textuelle du périmètre couvert
    horizon_debut = Column(Integer)                # année, jamais déduite
    horizon_fin = Column(Integer)
    statut = Column(Enum(StatutSchema), nullable=False, default=StatutSchema.ELABORATION, index=True)
    autorite_elaboratrice = Column(String(160))    # APN, PAD, PAK, PAL...
    reference_approbatrice = Column(String(120))   # numéro de décret / arrêté réel
    date_approbation = Column(Date)
    date_depot = Column(Date)
    date_echeance_revision = Column(Date)          # obligation de révision périodique
    cout_elaboration_xaf = Column(Numeric(18, 2))  # NULL tant que non facturé
    budget_alloue_travaux_xaf = Column(Numeric(18, 2))
    superficie_totale_ha = Column(Numeric(14, 3))  # emprise visée par le document
    surface_eau_ha = Column(Numeric(14, 3))
    zones_prevues = Column(Text)                   # JSON [{nom, type_zone, superficie_ha}] saisi
    lignes_directrices = Column(Text)              # JSON [str] : axes structurants décidés
    documents_sources = Column(Text)               # JSON [str] : références des pièces jointes
    source_reference = Column(String(200))         # provenance : journal officiel, arrêté, dossier
    date_verification = Column(Date)               # dernier contrôle humain de la donnée
    auteur_saisie = Column(String(120))
    notes = Column(Text)
    est_actif = Column(Boolean, default=True, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    port = relationship("PortCameroun")
    projets = relationship("ProjetAmenagement", back_populates="schema")


# ─── 2. Programmation : projets d'investissement ─────────────────────────────

class ProjetAmenagement(Base):
    """Opération d'aménagement inscrite à la programmation d'une place.

    Le pilotage camerounais est documenté : un projet n'existe juridiquement
    qu'à partir du moment où il est porté au DTO (Document Technique Outil,
    loi de finances) et notifié au MINMIVT au titre de l'engagement des
    crédits. Ces deux dates sont donc des champs saisis, jamais déduits.
    """
    __tablename__ = "projets_amenagement"

    id = Column(Integer, primary_key=True, index=True)
    code_projet = Column(String(40), unique=True, nullable=False, index=True)
    libelle = Column(String(200), nullable=False)
    description = Column(Text)
    port_id = Column(Integer, ForeignKey("ports_cameroun.id"), nullable=True, index=True)
    terminal_id = Column(Integer, ForeignKey("terminaux_portuaires.id"), nullable=True)
    schema_id = Column(Integer, ForeignKey("schemas_directeurs_amgt.id"), nullable=True, index=True)
    type_ouvrage = Column(Enum(TypeProjet), nullable=False, default=TypeProjet.AUTRE, index=True)
    statut = Column(Enum(StatutProjet), nullable=False, default=StatutProjet.IDENTIFIE, index=True)
    priorite = Column(String(20))                  # P1/P2/P3 : gradation saisie, pas calculée
    origines_financement = Column(Text)            # JSON [str] (plusieurs sources possibles)
    cout_previsionnel_xaf = Column(Numeric(18, 2))
    cout_reel_xaf = Column(Numeric(18, 2))
    devise = Column(String(6), default="XAF")
    financement_public_xaf = Column(Numeric(18, 2))
    financement_prive_xaf = Column(Numeric(18, 2))
    date_debut_prevue = Column(Date)
    date_fin_prevue = Column(Date)
    date_reelle_demarrage = Column(Date)
    date_reelle_achevement = Column(Date)
    avancement_physique_pct = Column(Numeric(5, 2))  # % relevé sur chantier, NULL si jamais relevé
    avancement_financier_pct = Column(Numeric(5, 2))
    maitre_ouvrage = Column(String(160))           # PAD / PAK / APN / MINMIVT
    maitre_doeuvre = Column(String(160))
    bureau_controle = Column(String(160))
    entreprise_attributaire = Column(String(200))
    marche_id = Column(Integer, ForeignKey("marches_amenagement.id"), nullable=True)
    dto_reference = Column(String(120))            # ligne DTO réelle (« DTO-2026-… »)
    date_notification_minepf = Column(Date)        # engagement visé par le contrôle financier
    eies_obligatoire = Column(Boolean)             # classification loi 96/012, saisie
    superficie_impactee_ha = Column(Numeric(14, 3))
    capacite_additionnelle = Column(String(120))   # ex. « 300 000 EVP/an », texte saisi
    justificatif_utilite = Column(Text)            # argument du schéma directeur
    risques = Column(Text)                         # JSON [str]
    source_reference = Column(String(200))
    date_verification = Column(Date)
    auteur_saisie = Column(String(120))
    notes = Column(Text)
    est_actif = Column(Boolean, default=True, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    port = relationship("PortCameroun")
    terminal = relationship("TerminalPortuaire")
    schema = relationship("SchemaDirecteur", back_populates="projets")
    marches = relationship("MarcheAmenagement", back_populates="projet")
    autorisations = relationship("AutorisationTravaux", back_populates="projet")
    infrastructures = relationship("InfrastructurePortuaire", back_populates="projet")


# ─── 3. Programmation budgétaire : DTO ───────────────────────────────────────

class RegistreDTO(Base):
    """Document Technique Outil — support légal de tout projet d'investissement.

    Au Cameroun, la loi de finances exige un DTO visé par le contrôle
    financier pour tout projet : sans lui, la passation du marché ne peut pas
    être régularisée. Cette table en tient le registre, avec les visas réels.
    """
    __tablename__ = "registres_dto_amgt"

    id = Column(Integer, primary_key=True, index=True)
    reference_dto = Column(String(80), unique=True, nullable=False, index=True)
    exercice = Column(Integer, nullable=False, index=True)
    projet_id = Column(Integer, ForeignKey("projets_amenagement.id"), nullable=True, index=True)
    port_id = Column(Integer, ForeignKey("ports_cameroun.id"), nullable=True)
    objet = Column(String(300), nullable=False)
    montant_inscrit_xaf = Column(Numeric(18, 2))
    montant_paye_xaf = Column(Numeric(18, 2))
    source_financement = Column(Enum(OrigineFinancement), nullable=True)
    chapitre = Column(String(120))                 # chapitre budgétaire déclaré
    statut = Column(String(30), default="PREPARATION", index=True)
    date_presentation = Column(Date)
    date_visa_controle_financier = Column(Date)
    autorite_visa = Column(String(160))
    numero_engagement = Column(String(80))
    date_notification_minepf = Column(Date)
    source_reference = Column(String(200))
    date_verification = Column(Date)
    auteur_saisie = Column(String(120))
    notes = Column(Text)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    projet = relationship("ProjetAmenagement")


# ─── 4. Passation : marchés publics & contrats PPP ───────────────────────────

class MarcheAmenagement(Base):
    """Marché ou contrat de PPP lié à un projet d'aménagement.

    Le régime camerounais (code des marchés publics + loi 2023/008 sur les
    PPP) impose des jalons précis : publication, COLIFE/CIP pour le contrôle
    d'éligibilité, attribution, notification, avance de démarrage, décomptes
    provisoires et définitifs, réception. Les montants et dates sont saisis
    depuis les pièces réelles ; le module ne produit aucun numéro de marché.
    """
    __tablename__ = "marches_amenagement"

    id = Column(Integer, primary_key=True, index=True)
    reference = Column(String(80), unique=True, nullable=False, index=True)
    designations = Column(String(300), nullable=False)
    projet_id = Column(Integer, ForeignKey("projets_amenagement.id"), nullable=True, index=True)
    port_id = Column(Integer, ForeignKey("ports_cameroun.id"), nullable=True)
    type_marche = Column(Enum(TypeMarche), nullable=False, default=TypeMarche.TRAVAUX)
    code_marche = Column(Enum(CodeMarche), nullable=True)
    statut = Column(Enum(StatutMarche), nullable=False, default=StatutMarche.PREVU, index=True)
    procedure_controle = Column(String(60))        # COLIFE, CIP, marché propre à l'autorité
    dossier_appel_offre = Column(String(120))      # référence DAO déposée
    date_publication_dao = Column(Date)
    date_remise_offres = Column(Date)
    date_colife = Column(Date)                     # passage en commission
    avis_colife = Column(String(40))               # ELIGIBLE / SUSPENSION / INELIGIBLE
    date_attribution = Column(Date)
    attributaire = Column(String(200))
    montant_attribue_xaf = Column(Numeric(18, 2))
    montant_initial_xaf = Column(Numeric(18, 2))
    montant_final_xaf = Column(Numeric(18, 2))
    devise = Column(String(6), default="XAF")
    part_pmp_pct = Column(Numeric(5, 2))           # part réservée PME (décret en vigueur)
    avance_demarrage_xaf = Column(Numeric(18, 2))
    retenue_garantie_pct = Column(Numeric(5, 2))
    caution_banque = Column(String(160))
    delai_execution_mois = Column(Integer)
    date_notification = Column(Date)
    date_ouverture_chantier = Column(Date)
    date_reception_provisoire = Column(Date)
    date_reception_definitive = Column(Date)
    garant_result_annees = Column(Integer)         # garantie de parfait achèvement
    nrd_max_jours = Column(Integer)                # nantissement / règlement définitif
    source_reference = Column(String(200))
    date_verification = Column(Date)
    auteur_saisie = Column(String(120))
    notes = Column(Text)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    projet = relationship("ProjetAmenagement", back_populates="marches")