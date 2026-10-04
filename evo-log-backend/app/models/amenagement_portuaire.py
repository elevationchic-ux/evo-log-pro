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
     avant tout engagement de crédit, le projet passe le circuit de
     programmation des investissements publics : fiche / dossier technique,
     visa de maturité (décret n° 2018/0492), inscription au PIP-CDMT, visa du
     contrôle financier ;
  4. la passation obéit au régime des marchés publics camerounais (COLIFE /
     CIP pour la place de Douala) et la conformité environnementale à la loi
     n° 96/012 du 5 août 1996 (EIES, audit IEMU).

PHILOSOPHIE DES DONNÉES — aucune donnée n'est inventée ici.
  * Les tables portent des COLONNES de provenance (source_reference,
    date_verification, autorite_emettrice) : une valeur n'existe que si un
    agent l'a saisie depuis un document réel (schéma directeur approuvé, visa
    de maturité, arrêté, rapport de bathymétrie).
  * NULL veut dire « non renseigné », jamais « 0 » ni « moyenne de marché ».
  * Le module ne simule aucune téléprocédure : ce qui dépend d'un tiers
    institutionnel (APN, COLIFE, MINMIVT, MINEPAT, MINFI) répond 501 côté
    routeur.

Modèle domanial : comme ``ports_cameroun`` et ``terminaux_portuaires`` (données
de référence nationales), ces tables ne portent PAS de ``company_id`` — elles
décrivent l'infrastructure publique du pays, pas le fonds de commerce d'un
tenant. ``app/core/tenant_enforcement.py`` ne les filtre donc pas, ce qui est
le comportement voulu (même raisonnement que pour les incoterms et le plan
comptable COMPTABLE global).
"""
from sqlalchemy import (
    Column, Integer, String, Text, DateTime, Boolean, Date, Numeric,
    ForeignKey, Enum,
)
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
import enum

from app.core.database import Base


def _enum(cls):
    """Nomenclature Python stockee en VARCHAR, sans type natif ni CHECK.

    Double raison :
      * le DDL devient identique sur SQLite (dev/tests) et PostgreSQL
        (production) — une migration ``sa.String(...)`` et le modele restent
        strictement en parite, convention des migrations 014/028 ;
      * la nomenclature est deja garantie a l'entree par les schemas Pydantic
        (un code hors enum est refuse en 422) : un CHECK de plus n'apporte
        rien et rendrait toute evolution de vocabulaire cooperative.
    """
    return Enum(cls, native_enum=False, create_constraint=False)


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
    INSCRIT_PIP = "inscrit_pip"                    # porté au PIP / CDMT après le visa de maturité
    NOTIFIE_MINFI = "notifie_minfi"                # credits inscrits au budget, engagement vise
    EN_ATTRIBUTION = "en_attribution"              # DAO en cours (COLIFE / CIP)
    ATTRIBUE = "attribue"
    EN_CONSTRUCTION = "en_construction"
    RECEPTIONNE = "receptionne"
    EN_SERVICE = "en_service"
    ABANDONNE = "abandonne"


class OrigineFinancement(str, enum.Enum):
    BUDGET_AUTORITE_PORTUAIRE = "budget_autorite_portuaire"
    SUBVENTION_ETAT = "subvention_etat"
    PRET_BAILLEUR = "pret_bailleur"                # BEI, AFD, BAD, JICA, Exim…
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
    EXPIREE = "expiree"
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
    type_schema = Column(_enum(TypeSchema), nullable=False, default=TypeSchema.SCHEMA_DIRECTEUR)
    perimetre = Column(Text)                       # description textuelle du périmètre couvert
    horizon_debut = Column(Integer)                # année, jamais déduite
    horizon_fin = Column(Integer)
    statut = Column(_enum(StatutSchema), nullable=False, default=StatutSchema.ELABORATION, index=True)
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

    Le pilotage camerounais est documenté : un projet d'investissement n'existe
    juridiquement qu'après les étapes suivies par le MINEPAT (DGPIP) — fiche /
    dossier technique, visa de maturité (décret n° 2018/0492 du Premier
    Ministre), inscription au PIP-CDMT puis à la loi de finances, et engagement
    des crédits visé par le contrôle financier du MINFI. Ces références et ces
    dates sont donc des champs saisis depuis les actes réels, jamais déduits.
    """
    __tablename__ = "projets_amenagement"

    id = Column(Integer, primary_key=True, index=True)
    code_projet = Column(String(40), unique=True, nullable=False, index=True)
    libelle = Column(String(200), nullable=False)
    description = Column(Text)
    port_id = Column(Integer, ForeignKey("ports_cameroun.id"), nullable=True, index=True)
    terminal_id = Column(Integer, ForeignKey("terminaux_portuaires.id"), nullable=True)
    schema_id = Column(Integer, ForeignKey("schemas_directeurs_amgt.id"), nullable=True, index=True)
    type_ouvrage = Column(_enum(TypeProjet), nullable=False, default=TypeProjet.AUTRE, index=True)
    statut = Column(_enum(StatutProjet), nullable=False, default=StatutProjet.IDENTIFIE, index=True)
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
    reference_fiche_technique = Column(String(120))  # fiche/dossier technique déposé (« FT-2026-… »)
    date_notification_minfi = Column(Date)         # engagement visé par le contrôle financier
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
    marches = relationship(
        "MarcheAmenagement",
        back_populates="projet",
        cascade="all, delete-orphan",
    )
    autorisations = relationship("AutorisationTravaux", back_populates="projet")
    infrastructures = relationship("InfrastructurePortuaire", back_populates="projet")


# ─── 3. Programmation budgétaire : fiche technique & visas ───────────────────

class DocumentProgrammation(Base):
    """Chaîne de programmation d'un projet : fiche technique, maturité, PIP, visas.

    Circuit réel camerounais (décret n° 2018/0492 fixant les modalités de
    préparation des projets d'investissement public, manuel MINEPAT de
    sélection des projets) : la fiche / le dossier technique est déposé devant
    la commission technique, qui débouche sur un **visa de maturité** ; le
    projet inscrit au PIP / cadre à moyen terme (CDMT) devient une ligne de loi
    de finances ; l'engagement des crédits exige le **visa du contrôle
    financier** (MINFI). Chaque référence et chaque date de cette table est
    saisie depuis l'acte correspondant : le module ne produit aucun numéro et
    ne valide rien à la place des commissions.
    """
    __tablename__ = "documents_programmation_amgt"

    id = Column(Integer, primary_key=True, index=True)
    reference_fiche_technique = Column(String(80), unique=True, nullable=False, index=True)
    exercice = Column(Integer, nullable=False, index=True)
    projet_id = Column(Integer, ForeignKey("projets_amenagement.id"), nullable=True, index=True)
    port_id = Column(Integer, ForeignKey("ports_cameroun.id"), nullable=True)
    objet = Column(String(300), nullable=False)
    montant_inscrit_xaf = Column(Numeric(18, 2))
    montant_paye_xaf = Column(Numeric(18, 2))
    source_financement = Column(_enum(OrigineFinancement), nullable=True)
    chapitre = Column(String(120))                 # chapitre budgétaire déclaré
    # PREPARATION / MATURITE_VISEE / INSCRIT_PIP / VISE / NOTIFIE / ANNULE :
    # statut saisi, jamais dérivé automatiquement d'une date.
    statut = Column(String(30), default="PREPARATION", index=True)
    date_presentation = Column(Date)               # dépôt devant la commission technique
    # ── visa de maturité (décret 2018/0492) ──
    numero_visa_maturite = Column(String(80))
    date_visa_maturite = Column(Date)
    autorite_visa_maturite = Column(String(160))   # commission / DGPIP émettrice
    # ── inscription à la programmation pluriannuelle ──
    reference_pip_cdmt = Column(String(120))       # ligne PIP ou CDMT telle que publiée
    # ── engagement des crédits ──
    date_visa_controle_financier = Column(Date)
    autorite_visa = Column(String(160))
    numero_engagement = Column(String(80))
    date_notification_minfi = Column(Date)
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
    type_marche = Column(_enum(TypeMarche), nullable=False, default=TypeMarche.TRAVAUX)
    code_marche = Column(_enum(CodeMarche), nullable=True)
    statut = Column(_enum(StatutMarche), nullable=False, default=StatutMarche.PREVU, index=True)
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


# ─── 5. Domanialité : titres d'occupation du domaine portuaire ───────────────

class AutorisationDomaniale(Base):
    """Titre d'occupation ou d'attribution dans le domaine portuaire.

    Avant toute construction, l'opérateur doit obtenir un titre : autorisation
    d'occupation temporaire, convention d'occupation (régime des AOT de la loi
    2023/008), attribution du domaine portuaire par l'autorité, arrêté de
    délimitation pour une extension. C'est le registre qui permet de répondre
    à la question « qui est censé occuper cette parcelle, et à quel titre ? ».
    """
    __tablename__ = "autorisations_domaniales_amgt"

    id = Column(Integer, primary_key=True, index=True)
    numero_piece = Column(String(80), unique=True, nullable=False, index=True)
    type_titre = Column(_enum(TypeTitreDomanial), nullable=False, index=True)
    port_id = Column(Integer, ForeignKey("ports_cameroun.id"), nullable=True, index=True)
    terminal_id = Column(Integer, ForeignKey("terminaux_portuaires.id"), nullable=True)
    zone_id = Column(Integer, ForeignKey("zones_portuaires.id"), nullable=True)
    beneficiaire = Column(String(200), nullable=False)   # raison sociale réelle
    objet = Column(String(300))
    assiette = Column(Text)                        # localisation / repères de la parcelle
    superficie_m2 = Column(Numeric(14, 3))
    destination = Column(String(120))              # stockage, exploitation, bâtiment, annexe
    redevance_annuelle_xaf = Column(Numeric(18, 2))
    taux_redevance = Column(String(60))            # barème applicable, saisi depuis la grille
    date_demande = Column(Date)
    date_signature = Column(Date)
    date_effet = Column(Date)
    date_expiration = Column(Date, index=True)
    renouvelable = Column(Boolean)
    delai_renouvellement_mois = Column(Integer)
    autorite_emettrice = Column(String(160))       # direction domainiale de l'autorité portuaire
    reference_deliberation = Column(String(120))
    piece_jointe = Column(String(300))
    statut = Column(String(30), default="DEMANDEE", index=True)
    motif_refus = Column(Text)
    source_reference = Column(String(200))
    date_verification = Column(Date)
    auteur_saisie = Column(String(120))
    notes = Column(Text)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    port = relationship("PortCameroun")
    terminal = relationship("TerminalPortuaire")


# ─── 6. Transfert d'exploitation : concessions, affermage, BOT ───────────────

class ConcessionPortuaire(Base):
    """Contrat de transfert (concession, affermage, BOT/CET, AOT).

    Le port de Douala comme celui de Kribi sont exploités par des opérateurs
    sous contrat avec l'autorité portuaire. Le suivi de l'aménagement exige de
    connaître le périmètre concédé, la durée, les investissements promis
    (obligations du concessionnaire) et l'état de leur réalisation : c'est
    exactement ce qui détermine si un terminal peut être étendu ou repris.
    """
    __tablename__ = "concessions_amenagement"

    id = Column(Integer, primary_key=True, index=True)
    code_contrat = Column(String(60), unique=True, nullable=False, index=True)
    nom_contrat = Column(String(200), nullable=False)
    port_id = Column(Integer, ForeignKey("ports_cameroun.id"), nullable=False, index=True)
    terminal_id = Column(Integer, ForeignKey("terminaux_portuaires.id"), nullable=True)
    type_contrat = Column(_enum(TypeContratExploitation), nullable=False, index=True)
    statut = Column(_enum(StatutContrat), nullable=False, default=StatutContrat.NEGOCIATION, index=True)
    autorite_concedante = Column(String(160), nullable=False)
    concessionnaire = Column(String(200), nullable=False)
    groupe_final = Column(String(160))             # actionnariat / maison mère, si connu
    objet = Column(Text)
    perimetre = Column(Text)                       # terminaux, postes, parcelles concernés
    superficie_concedee_ha = Column(Numeric(14, 3))
    longueur_quai_ml = Column(Numeric(12, 2))
    capacite_contractuelle = Column(String(120))   # ex. « 150 000 EVP/an » inscrit au contrat
    date_effet = Column(Date)
    date_echeance = Column(Date, index=True)
    duree_mois = Column(Integer)
    prolongations = Column(Text)                   # JSON [{date, duree_mois, motif, reference}]
    investissement_promis_xaf = Column(Numeric(18, 2))
    investissement_realise_xaf = Column(Numeric(18, 2))
    redevance_concession_xaf = Column(Numeric(18, 2))
    redevance_par_unite = Column(Numeric(18, 2))
    unite_redevance = Column(String(40))           # EVP, tonne, m2, jour
    clauses_revolution = Column(Text)              # 5e/10e/15e année : taux, montant, référence
    sanctions_contractuelles = Column(Text)
    biens_reversibles = Column(Text)               # patrimoine remis à l'autorité en fin de contrat
    reference_approbation = Column(String(120))    # décret/arrêté d'approbation réel
    date_approbation = Column(Date)
    arret_travail = Column(Boolean)                # mise à l'arrêt / redressement déclaratif
    source_reference = Column(String(200))
    date_verification = Column(Date)
    auteur_saisie = Column(String(120))
    notes = Column(Text)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    port = relationship("PortCameroun")
    terminal = relationship("TerminalPortuaire")


# ─── 7. Patrimoine bâti : inventaire des installations ───────────────────────

class InfrastructurePortuaire(Base):
    """Ouvrage, aire ou réseau livré et à maintenir.

    C'est la mémoire technique du domaine : un quai n'est pas seulement une
    ligne du schéma directeur, c'est une longueur, un tirant d'eau, un état
    structural et une date de visite. Les mesures (état, bathymétrie) sont
    issues de rapports réels ; aucune valeur n'est estimée par le logiciel.
    """
    __tablename__ = "infrastructures_amenagees"

    id = Column(Integer, primary_key=True, index=True)
    code = Column(String(60), unique=True, nullable=False, index=True)
    designation = Column(String(200), nullable=False)
    type_infrastructure = Column(_enum(TypeInfrastructure), nullable=False, index=True)
    port_id = Column(Integer, ForeignKey("ports_cameroun.id"), nullable=False, index=True)
    terminal_id = Column(Integer, ForeignKey("terminaux_portuaires.id"), nullable=True)
    projet_id = Column(Integer, ForeignKey("projets_amenagement.id"), nullable=True, index=True)
    zone_id = Column(Integer, ForeignKey("zones_portuaires.id"), nullable=True)
    emplacement = Column(String(200))
    statut = Column(_enum(EtatInfrastructure), nullable=False, default=EtatInfrastructure.PROJETEE, index=True)
    longueur_ml = Column(Numeric(12, 2))
    largeur_m = Column(Numeric(10, 2))
    superficie_m2 = Column(Numeric(14, 3))
    profondeur_utile_m = Column(Numeric(8, 2))     # le long de l'ouvrage
    hauteur_parement_m = Column(Integer)
    portance_tonnes_m2 = Column(Numeric(8, 2))     # capacité de surcharge du terre-plein
    capacite_teus = Column(Integer)
    date_mise_service = Column(Date)
    date_derniere_inspection = Column(Date)
    periodicite_inspection_mois = Column(Integer)
    prochaine_inspection = Column(Date)
    etat_structural = Column(String(30))           # BON / A_SURVEILLER / DEGRADE / CRITIQUE (relevé)
    note_genie_civil = Column(Numeric(5, 2))       # issue d'une expertise, jamais calculée ici
    travaux_renovation_prevus = Column(Boolean)
    estimation_renovation_xaf = Column(Numeric(18, 2))
    valeur_patrimoniale_xaf = Column(Numeric(18, 2))
    date_entree_patrimoine = Column(Date)
    regime_fiscal = Column(String(60))             # domaine public / domaine privé de l'autorité
    reversable = Column(Boolean)                   # réversible à l'État en fin de concession
    operateur_entretien = Column(String(160))
    sources_documents = Column(Text)               # JSON [str] : Plans, PV de réception, rapports
    source_reference = Column(String(200))
    date_verification = Column(Date)
    auteur_saisie = Column(String(120))
    notes = Column(Text)
    est_actif = Column(Boolean, default=True, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    port = relationship("PortCameroun")
    terminal = relationship("TerminalPortuaire")
    projet = relationship("ProjetAmenagement", back_populates="infrastructures")


# ─── 8. Dragage & chenal ─────────────────────────────────────────────────────

class Dragage(Base):
    """Campagne de dragage (construction, entretien, appréciation).

    C'est l'acte d'aménagement le plus récurrent d'un port camerounais : la
    vase du Wouri et le banc du chenal de Kribi imposent des campagnes
    répétées, chacune encadrée par une autorisation, un volume mesuré et un
    exutoire de rejet. Tous ces éléments proviennent de rapports de l'entreprise
    et de l'administration — ils sont saisis, jamais devinés.
    """
    __tablename__ = "campagnes_dragage"

    id = Column(Integer, primary_key=True, index=True)
    code_campagne = Column(String(60), unique=True, nullable=False, index=True)
    libelle = Column(String(200), nullable=False)
    port_id = Column(Integer, ForeignKey("ports_cameroun.id"), nullable=False, index=True)
    projet_id = Column(Integer, ForeignKey("projets_amenagement.id"), nullable=True, index=True)
    type_dragage = Column(_enum(TypeDragage), nullable=False, default=TypeDragage.ENTRETIEN, index=True)
    zone_traitee = Column(String(200))             # chenal, avant-quai, bassin, tourne à quai
    superficie_draguee_m2 = Column(Numeric(14, 3))
    volume_mesure_m3 = Column(Numeric(18, 2))      # cubage relevé (levé bathymétrique)
    volume_facture_m3 = Column(Numeric(18, 2))     # cubage contractuel payé
    profondeur_avant_m = Column(Numeric(8, 2))
    profondeur_visee_m = Column(Numeric(8, 2))
    profondeur_obtenue_m = Column(Numeric(8, 2))
    nature_sediment = Column(String(120))          # sable, vase, argile… (carottage)
    exutoire_rejet = Column(String(200))           # disposal offshore / remblai précis
    autorisation_rejet_reference = Column(String(120))
    entreprise = Column(String(200))
    type_drague = Column(String(80))               # drague à cutter, aspiratrice, preloader
    cout_xaf = Column(Numeric(18, 2))
    devise = Column(String(6), default="XAF")
    date_debut = Column(Date)
    date_fin = Column(Date)
    jours_arret = Column(Integer)                  # intempéries, pannes : faits relevés
    statut = Column(String(30), default="PLANIFIEE", index=True)
    leve_bathymetrique_apres = Column(Boolean)
    date_releve = Column(Date)
    autorisation_administrative = Column(String(200))
    impact_environnemental = Column(Text)
    source_reference = Column(String(200))
    date_verification = Column(Date)
    auteur_saisie = Column(String(120))
    notes = Column(Text)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    port = relationship("PortCameroun")
    projet = relationship("ProjetAmenagement")


# ─── 9. Conformité : autorisations administratives & EIES ────────────────────

class AutorisationTravaux(Base):
    """Enregistrement d'une autorisation ou d'un visa administratif.

    Le module n'adresse RIEN à l'administration : il tient le registre de ce
    qui a été déposé et de ce qui a été notifié, avec les dates réelles. Un
    champ NULL signifie « pas encore notifié ». C'est la seule façon honnête
    de piloter un chantier sans simuler une réponse du MINEPPT ou du MINMIVT.
    """
    __tablename__ = "autorisations_travaux_amgt"

    id = Column(Integer, primary_key=True, index=True)
    reference = Column(String(80), unique=True, nullable=False, index=True)
    type_autorisation = Column(_enum(TypeAutorisationTravaux), nullable=False, index=True)
    projet_id = Column(Integer, ForeignKey("projets_amenagement.id"), nullable=True, index=True)
    port_id = Column(Integer, ForeignKey("ports_cameroun.id"), nullable=True)
    administration = Column(String(160))           # MINEPPT, MINMIVT, PAD, PAK, délégation régionale
    categorie_projet = Column(String(40))          # classification loi 96/012 (1re/2e/3e catégorie)
    objet = Column(String(300))
    statut = Column(_enum(StatutAutorisation), nullable=False, default=StatutAutorisation.EN_PREPARATION, index=True)
    date_depot = Column(Date)
    date_accord = Column(Date)
    date_expiration = Column(Date)
    numero_arrete = Column(String(120))
    conditions_particulieres = Column(Text)        # mesures d'atténuation prescrites
    charges_enviro_xaf = Column(Numeric(18, 2))    # coût des mesures compensatoires chiffrées
    audit_date_prochaine = Column(Date)            # échéance IEMU périodique
    piece_jointe = Column(String(300))
    source_reference = Column(String(200))
    date_verification = Column(Date)
    auteur_saisie = Column(String(120))
    notes = Column(Text)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    projet = relationship("ProjetAmenagement", back_populates="autorisations")
