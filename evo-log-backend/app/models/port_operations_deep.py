"""Modeles approfondis des operations portuaires (Wave 1A expansion).

Ce fichier complete le module acconage.py existant (Navire, Escale, Conteneur,
StowagePlan, Surestarie, Manifeste, Amarage, OperationAcconage) en ajoutant
12 entites de gestion operationnelle portuaire qui couvrent chaque facette du
metier d'un port camerounais (Douala, Kribi, Limbe) :

  1. DraftSurvey       - Constats de tirant d'eau et avaries coque
  2. StevedoringCrew   - Equipes de manutention (gangs) et affectations
  3. CargoHandlingPlan - Plans dechargement/chargement par cale
  4. QuayEquipment     - Inventaire équipements de quai (portiques, reach stackers)
  5. PilotageSession   - Sessions de pilotage maritime
  6. TowageOperation   - Operations de remorquage
  7. BunkeringOrder    - Ordres de ravitaillement (soute)
  8. VesselWasteReceipt - Reception dechets navire MARPOL
  9. TallySheet        - Feuilles de comptage contradictoire
  10. DemurrageCase    - Dossiers de surestaries (complement Surestarie)
  11. GatePass         - Bons de sortie (laisser-passer camion/conteneur)
  12. YardOperation    - Mouvements au parc a conteneurs (CY)

Convention d'honnetete : aucune valeur n'est injectee par defaut, NULL reste
"non enregistre". company_id est present car ces donnees sont specifiques a
chaque operateur portuaire (contrairement au referentiel national des ports).
"""
from sqlalchemy import (
    Column, Integer, String, Text, DateTime, Boolean, Float,
    ForeignKey, Enum, Date, Numeric, UniqueConstraint,
)
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
import enum

from app.core.database import Base


def _enum(cls):
    """Nomenclature Python stockee en VARCHAR, sans type natif."""
    return Enum(cls, native_enum=False, create_constraint=False, values_callable=lambda x: [e.value for e in x])


# ─── Enums ────────────────────────────────────────────────────────────────────

class TypeAvarie(str, enum.Enum):
    CORRELAGE = "correlage"
    FROTTAGE = "frottage"
    IMPACT = "impact"
    CORROSION = "corrosion"
    ENFONCEMENT = "enfoncement"
    AUTRE = "autre"


class GraviteAvarie(str, enum.Enum):
    LEGERE = "legere"
    MOYENNE = "moyenne"
    SERIEUSE = "serieuse"
    CRITIQUE = "critique"


class StatutConstat(str, enum.Enum):
    EN_ATTENTE = "en_attente"
    CONSTATE = "constate"
    SIGNE = "signe"
    CONTESTE = "conteste"
    CLOTURE = "cloture"


class TypeEquipage(str, enum.Enum):
    ACCONAGE = "acconage"
    DEMANUTENTION = "demanutention"
    HARNAIS = "harnais"
    CALAGE = "calage"
    GENERAL = "general"


class StatutGang(str, enum.Enum):
    DISPO = "dispo"
    AFFECTE = "affecte"
    REPOS = "repos"
    CONGE = "conge"


class TypeOperationQuai(str, enum.Enum):
    DECHARGEMENT = "dechargement"
    CHARGEMENT = "chargement"
    TRANSBORD = "transbord"
    RECEPTION = "reception"
    LIVRAISON = "livraison"


class StatutPlanManutention(str, enum.Enum):
    PLANIFIE = "planifie"
    EN_COURS = "en_cours"
    TERMINE = "termine"
    ANNULE = "annule"


class TypeEquipement(str, enum.Enum):
    PORTIQUE = "portique"
    REACH_STACKER = "reach_stacker"
    RETRACK = "retrack"
    CHERIOT_ELEVATEUR = "chariot_elevateur"
    GRUE_CABINE = "grue_cabine"
    CONVOYEUR = "convoyeur"
    TRACTEUR_PORT = "tracteur_port"
    AUTRE = "autre"


class EtatEquipement(str, enum.Enum):
    OPERATIONNEL = "operationnel"
    EN_MAINTENANCE = "en_maintenance"
    HORS_SERVICE = "hors_service"
    EN_ATTENTE_PIECE = "en_attente_piece"


class StatutPilotage(str, enum.Enum):
    DEMANDE = "demande"
    EN_COURS = "en_cours"
    TERMINE = "termine"
    ANNULE = "annule"


class TypeSoute(str, enum.Enum):
    MGO = "mgo"
    HFO = "hfo"
    VLSFO = "vlsfo"
    LNG = "lng"
    METHANOL = "methanol"


class TypeDechet(str, enum.Enum):
    ORDURE_MENAGERE = "ordure_menagere"
    EAU_BALLAST = "eau_ballast"
    HYDROCARBURE = "hydrocarbure"
    BOUE = "boue"
    DECHET_DANGEREUX = "dechet_dangereux"
    RECYCLABLE = "recyclable"


class StatutGatePass(str, enum.Enum):
    EMIS = "emis"
    EN_ATTENTE = "en_attente"
    PASSE = "passe"
    REFUSE = "refuse"
    EXPIRE = "expire"


class TypeMouvementYard(str, enum.Enum):
    DEPOSE = "depose"
    RELEVE = "releve"
    TRANSFERT = "transfert"
    REPOSISION = "reposision"
    LIVRAISON = "livraison"
    RECEPVATION = "reception"


# ─── Modeles ──────────────────────────────────────────────────────────────────

class DraftSurvey(Base):
    """Constat de tirant d'eau et avaries coque."""
    __tablename__ = "draft_surveys"
    __table_args__ = (
        UniqueConstraint('company_id', 'numero_constat', name='uix_draft_survey_company_num'),
    )
    id = Column(Integer, primary_key=True, index=True)
    company_id = Column(Integer, ForeignKey('companies.id'), nullable=False, index=True)
    numero_constat = Column(String(50), nullable=False, index=True)
    navire_id = Column(Integer, ForeignKey('navires.id'))
    escale_id = Column(Integer, ForeignKey('escales.id'))
    date_constat = Column(Date)
    lieu_constat = Column(String(100))
    tirant_eau_avant = Column(Numeric)
    tirant_eau_arriere = Column(Numeric)
    type_avarie = Column(_enum(TypeAvarie))
    gravite = Column(_enum(GraviteAvarie))
    description = Column(Text)
    photos_jointes = Column(Text)
    statut = Column(_enum(StatutConstat), default=StatutConstat.EN_ATTENTE)
    inspecteur = Column(String(100))
    capitaine_signataire = Column(String(100))
    notes = Column(Text)
    source_reference = Column(String(200))
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())


class StevedoringCrew(Base):
    """Equipe de manutention (gang)."""
    __tablename__ = "stevedoring_crews"
    __table_args__ = (
        UniqueConstraint('company_id', 'code_gang', name='uix_crew_company_code'),
    )
    id = Column(Integer, primary_key=True, index=True)
    company_id = Column(Integer, ForeignKey('companies.id'), nullable=False, index=True)
    code_gang = Column(String(30), nullable=False, index=True)
    nom_gang = Column(String(100))
    type_equipe = Column(_enum(TypeEquipage))
    statut = Column(_enum(StatutGang), default=StatutGang.DISPO)
    chef_gang = Column(String(100))
    nombre_membres = Column(Integer)
    specialites = Column(Text)
    certification = Column(String(100))
    date_expiration_certification = Column(Date)
    telephone_chef = Column(String(30))
    notes = Column(Text)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())


class CargoHandlingPlan(Base):
    """Plan de manutention par cale."""
    __tablename__ = "cargo_handling_plans"
    __table_args__ = (
        UniqueConstraint('company_id', 'reference_plan', name='uix_cargo_plan_company_ref'),
    )
    id = Column(Integer, primary_key=True, index=True)
    company_id = Column(Integer, ForeignKey('companies.id'), nullable=False, index=True)
    reference_plan = Column(String(50), nullable=False, index=True)
    escale_id = Column(Integer, ForeignKey('escales.id'))
    navire_id = Column(Integer, ForeignKey('navires.id'))
    type_operation = Column(_enum(TypeOperationQuai))
    statut = Column(_enum(StatutPlanManutention), default=StatutPlanManutention.PLANIFIE)
    numero_cale = Column(String(20))
    poids_total_tonnes = Column(Numeric)
    nombre_colis = Column(Integer)
    nombre_conteneurs = Column(Integer)
    date_debut_prevue = Column(DateTime(timezone=True))
    date_fin_prevue = Column(DateTime(timezone=True))
    date_debut_reelle = Column(DateTime(timezone=True))
    date_fin_reelle = Column(DateTime(timezone=True))
    cadence_prevue_t_h = Column(Numeric)
    cadence_reelle_t_h = Column(Numeric)
    gang_id = Column(Integer, ForeignKey('stevedoring_crews.id'))
    equipement_id = Column(Integer, ForeignKey('quay_equipments.id'))
    charge_a_bord_port = Column(String(100))
    decharge_a_quai_port = Column(String(100))
    notes = Column(Text)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())


class QuayEquipment(Base):
    """Equipement de quai."""
    __tablename__ = "quay_equipments"
    __table_args__ = (
        UniqueConstraint('company_id', 'code_equipement', name='uix_equip_company_code'),
    )
    id = Column(Integer, primary_key=True, index=True)
    company_id = Column(Integer, ForeignKey('companies.id'), nullable=False, index=True)
    code_equipement = Column(String(50), nullable=False, index=True)
    designation = Column(String(200), nullable=False)
    type_equipement = Column(_enum(TypeEquipement))
    etat = Column(_enum(EtatEquipement), default=EtatEquipement.OPERATIONNEL)
    marque = Column(String(100))
    modele = Column(String(100))
    capacite_max_tonnes = Column(Numeric)
    portee_max_m = Column(Numeric)
    hauteur_sous_flèche_m = Column(Numeric)
    annee_mise_service = Column(Integer)
    fournisseur = Column(String(200))
    numero_serial = Column(String(100))
    prochaine_maintenance_date = Column(Date)
    prochaine_maintenance_km = Column(Numeric)
    heures_service_cumulees = Column(Numeric)
    poste_quai_assigne = Column(String(50))
    cout_acquisition_xaf = Column(Numeric)
    notes = Column(Text)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())


class PilotageSession(Base):
    """Session de pilotage maritime."""
    __tablename__ = "pilotage_sessions"
    __table_args__ = (
        UniqueConstraint('company_id', 'reference', name='uix_pilotage_company_ref'),
    )
    id = Column(Integer, primary_key=True, index=True)
    company_id = Column(Integer, ForeignKey('companies.id'), nullable=False, index=True)
    reference = Column(String(50), nullable=False, index=True)
    navire_id = Column(Integer, ForeignKey('navires.id'))
    escale_id = Column(Integer, ForeignKey('escales.id'))
    pilote_nom = Column(String(100))
    pilote_matricule = Column(String(50))
    statut = Column(_enum(StatutPilotage), default=StatutPilotage.DEMANDE)
    type_mouvement = Column(String(30))  # entree, sortie, deplacement
    date_demande = Column(DateTime(timezone=True))
    date_debut_reelle = Column(DateTime(timezone=True))
    date_fin_reelle = Column(DateTime(timezone=True))
    duree_heures = Column(Numeric)
    zone_pilotage = Column(String(100))
    distance_nautique_mq = Column(Numeric)
    conditions_meteo = Column(String(200))
    vitesse_navire_noeuds = Column(Numeric)
    tirant_eau_navire_m = Column(Numeric)
    tarif_pilotage_xaf = Column(Numeric)
    notes = Column(Text)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())


class TowageOperation(Base):
    """Operation de remorquage."""
    __tablename__ = "towage_operations"
    __table_args__ = (
        UniqueConstraint('company_id', 'reference', name='uix_towage_company_ref'),
    )
    id = Column(Integer, primary_key=True, index=True)
    company_id = Column(Integer, ForeignKey('companies.id'), nullable=False, index=True)
    reference = Column(String(50), nullable=False, index=True)
    navire_id = Column(Integer, ForeignKey('navires.id'))
    escale_id = Column(Integer, ForeignKey('escales.id'))
    remorqueur_nom = Column(String(100))
    remorqueur_immatriculation = Column(String(50))
    nombre_remorqueurs = Column(Integer)
    type_prestation = Column(String(50))
    statut = Column(_enum(StatutPilotage), default=StatutPilotage.DEMANDE)
    date_debut_reelle = Column(DateTime(timezone=True))
    date_fin_reelle = Column(DateTime(timezone=True))
    duree_heures = Column(Numeric)
    puissance_bollard_t = Column(Numeric)
    zone_operation = Column(String(100))
    tarif_xaf = Column(Numeric)
    operateur = Column(String(200))
    conditions_meteo = Column(String(200))
    notes = Column(Text)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())


class BunkeringOrder(Base):
    """Ordre de ravitaillement (soute)."""
    __tablename__ = "bunkering_orders"
    __table_args__ = (
        UniqueConstraint('company_id', 'reference', name='uix_bunker_company_ref'),
    )
    id = Column(Integer, primary_key=True, index=True)
    company_id = Column(Integer, ForeignKey('companies.id'), nullable=False, index=True)
    reference = Column(String(50), nullable=False, index=True)
    navire_id = Column(Integer, ForeignKey('navires.id'))
    escale_id = Column(Integer, ForeignKey('escales.id'))
    type_carburant = Column(_enum(TypeSoute))
    quantite_tonnes = Column(Numeric)
    densite = Column(Numeric)
    soufre_pct = Column(Numeric)
    prix_tonne_xaf = Column(Numeric)
    montant_total_xaf = Column(Numeric)
    fournisseur = Column(String(200))
    barge_nom = Column(String(100))
    date_operation = Column(DateTime(timezone=True))
    heure_debut = Column(String(10))
    heure_fin = Column(String(10))
    debit_t_h = Column(Numeric)
    statut = Column(String(30), default='demande')
    bon_livraison_ref = Column(String(100))
    quantitemesuree_t = Column(Numeric)
    ecart_quantite_t = Column(Numeric)
    capitaine_signataire = Column(String(100))
    notes = Column(Text)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())


class VesselWasteReceipt(Base):
    """Reception dechets navire (MARPOL)."""
    __tablename__ = "vessel_waste_receipts"
    __table_args__ = (
        UniqueConstraint('company_id', 'reference', name='uix_waste_company_ref'),
    )
    id = Column(Integer, primary_key=True, index=True)
    company_id = Column(Integer, ForeignKey('companies.id'), nullable=False, index=True)
    reference = Column(String(50), nullable=False, index=True)
    navire_id = Column(Integer, ForeignKey('navires.id'))
    escale_id = Column(Integer, ForeignKey('escales.id'))
    type_dechet = Column(_enum(TypeDechet))
    quantite = Column(Numeric)
    unite = Column(String(20))
    date_reception = Column(DateTime(timezone=True))
    lieu_depot = Column(String(200))
    operateur_collecte = Column(String(200))
    fichier_destinataire = Column(String(200))
    cout_collecte_xaf = Column(Integer)
    numero_manifeste_dechet = Column(String(100))
    marpol_annexe = Column(String(10))
    capitaine_declare = Column(String(100))
    recu_par = Column(String(100))
    conforme = Column(Boolean)
    notes = Column(Text)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())


class TallySheet(Base):
    """Feuille de comptage contradictoire."""
    __tablename__ = "tally_sheets"
    __table_args__ = (
        UniqueConstraint('company_id', 'reference', name='uix_tally_company_ref'),
    )
    id = Column(Integer, primary_key=True, index=True)
    company_id = Column(Integer, ForeignKey('companies.id'), nullable=False, index=True)
    reference = Column(String(50), nullable=False, index=True)
    escale_id = Column(Integer, ForeignKey('escales.id'))
    navire_id = Column(Integer, ForeignKey('navires.id'))
    operation_id = Column(Integer, ForeignKey('cargo_handling_plans.id'))
    type_operation = Column(_enum(TypeOperationQuai))
    date_tally = Column(Date)
    poste_quai = Column(String(50))
    numero_cale = Column(String(20))
    poids_manifeste_t = Column(Numeric)
    poids_tally_t = Column(Numeric)
    colis_manifeste = Column(Integer)
    colis_tally = Column(Integer)
    ecart_poids_t = Column(Numeric)
    ecart_colis = Column(Integer)
    nombre_avaries = Column(Integer)
    tallyeur = Column(String(100))
    contre_tallyeur = Column(String(100))
    valide = Column(Boolean)
    date_validation = Column(DateTime(timezone=True))
    notes = Column(Text)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())


class DemurrageCase(Base):
    """Dossier de surestarie complementaire."""
    __tablename__ = "demurrage_cases"
    __table_args__ = (
        UniqueConstraint('company_id', 'reference', name='uix_demurrage_company_ref'),
    )
    id = Column(Integer, primary_key=True, index=True)
    company_id = Column(Integer, ForeignKey('companies.id'), nullable=False, index=True)
    reference = Column(String(50), nullable=False, index=True)
    escale_id = Column(Integer, ForeignKey('escales.id'))
    navire_id = Column(Integer, ForeignKey('navires.id'))
    conteneur_id = Column(Integer, ForeignKey('conteneurs.id'))
    client_id = Column(Integer, ForeignKey('clients.id'))
    date_debut_franchise = Column(Date)
    date_fin_franchise = Column(Date)
    date_retrait_reelle = Column(Date)
    nb_jours_facturables = Column(Integer)
    tarif_journalier_xaf = Column(Numeric)
    montant_total_xaf = Column(Numeric)
    statut = Column(String(30), default='ouvert')
    facture_id = Column(Integer)
    litige_declare = Column(Boolean)
    motif_litige = Column(Text)
    notes = Column(Text)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())


class GatePass(Base):
    """Bon de sortie (laisser-passer)."""
    __tablename__ = "gate_passes"
    __table_args__ = (
        UniqueConstraint('company_id', 'numero_gate', name='uix_gate_company_num'),
    )
    id = Column(Integer, primary_key=True, index=True)
    company_id = Column(Integer, ForeignKey('companies.id'), nullable=False, index=True)
    numero_gate = Column(String(50), nullable=False, index=True)
    type_sortie = Column(String(30))
    conteneur_id = Column(Integer, ForeignKey('conteneurs.id'))
    camion_immatriculation = Column(String(30))
    chauffeur_nom = Column(String(100))
    chauffeur_telephone = Column(String(30))
    statut = Column(_enum(StatutGatePass), default=StatutGatePass.EMIS)
    date_emission = Column(DateTime(timezone=True), server_default=func.now())
    date_passage = Column(DateTime(timezone=True))
    poste_controle = Column(String(50))
    agent_poste = Column(String(100))
    poids_camion_kg = Column(Numeric)
    poids_charge_kg = Column(Numeric)
    bl_reference = Column(String(50))
    livraison_client = Column(String(200))
    valide_par = Column(String(100))
    notes = Column(Text)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())


class YardOperation(Base):
    """Mouvement au parc a conteneurs (CY)."""
    __tablename__ = "yard_operations"
    __table_args__ = (
        UniqueConstraint('company_id', 'reference', name='uix_yardop_company_ref'),
    )
    id = Column(Integer, primary_key=True, index=True)
    company_id = Column(Integer, ForeignKey('companies.id'), nullable=False, index=True)
    reference = Column(String(50), nullable=False, index=True)
    conteneur_id = Column(Integer, ForeignKey('conteneurs.id'))
    type_mouvement = Column(_enum(TypeMouvementYard))
    emplacement_source = Column(String(50))
    emplacement_destination = Column(String(50))
    zone_yard = Column(String(50))
    date_operation = Column(DateTime(timezone=True))
    equipment_id = Column(Integer, ForeignKey('quay_equipments.id'))
    operateur_equipment = Column(String(100))
    poids_conteneur_t = Column(Numeric)
    statut = Column(String(30), default='planifie')
    reference_gate_pass = Column(String(50))
    reference_escale = Column(String(50))
    notes = Column(Text)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
