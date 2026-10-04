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
    DAPPRECIATION = "appréciation".replace("é", "e")
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
    autorite_approbatrice = Column(String(160))    # MINMIVT, Premier ministre...
    reference_approba