"""
Acconage models for port operations and stevedoring management
"""
from sqlalchemy import Column, Integer, String, Text, DateTime, Boolean, Float, ForeignKey, Enum, Date, Numeric, UniqueConstraint
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
import enum
from app.core.database import Base


class Navire(Base):
    """Ship/Vessel model"""
    __tablename__ = "navires"
    __table_args__ = (
        UniqueConstraint('company_id', 'imo', name='uix_navire_company_imo'),
    )
    
    id = Column(Integer, primary_key=True, index=True)
    company_id = Column(Integer, ForeignKey('companies.id'), nullable=True, index=True)
    nom = Column(String(100), nullable=False)
    imo = Column(String(20))
    pavillon = Column(String(50))
    type_navire = Column(String(50))  # e.g., "porte-conteneurs", "vraquier", "pétrolier"
    longueur = Column(Numeric)
    largeur = Column(Numeric)
    tirant_eau = Column(Numeric)
    port_en_lourd = Column(Numeric)
    deadweight = Column(Numeric)
    annee_construction = Column(Integer)
    proprietaire = Column(String(100))
    armateur = Column(String(100))
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relationships
    escales = relationship("Escale", back_populates="navire")
    conteneurs = relationship("Conteneur", back_populates="navire")


class EscaleStatus(str, enum.Enum):
    """Enumeration for port call status"""
    PROGRAMMEE = "programmee"
    ARRIVEE = "arrivee"
    A_QUAI = "a_quai"
    EN_OPERATION = "en_operation"
    DEPART = "depart"
    ANNULEE = "annulee"


class Escale(Base):
    """Port call/berth model"""
    __tablename__ = "escales"
    __table_args__ = (
        UniqueConstraint('company_id', 'numero_escale', name='uix_escale_company_numero'),
    )
    
    id = Column(Integer, primary_key=True, index=True)
    company_id = Column(Integer, ForeignKey('companies.id'), nullable=True, index=True)
    numero_escale = Column(String(50), nullable=False, index=True)
    navire_id = Column(Integer, ForeignKey('navires.id'))
    port_id = Column(Integer, ForeignKey('agencies.id'))  # Using agency as port reference
    poste_quai = Column(String(50))
    date_arrivee_prevue = Column(DateTime(timezone=True))
    date_arrivee_reelle = Column(DateTime(timezone=True))
    date_depart_prevue = Column(DateTime(timezone=True))
    date_depart_reelle = Column(DateTime(timezone=True))
    statut = Column(Enum(EscaleStatus), default=EscaleStatus.PROGRAMMEE)
    marchandise = Column(Text)
    tonnage = Column(Numeric)
    nombre_conteneurs = Column(Integer)
    agent = Column(String(100))
    notes = Column(Text)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relationships
    navire = relationship("Navire", back_populates="escales")
    operations = relationship("OperationAcconage", back_populates="escale")
    amarages = relationship("Amarage", back_populates="escale")
    manifestes = relationship("Manifeste", back_populates="escale")
    surestaries = relationship("Surestarie", back_populates="escale")


class StowagePlan(Base):
    """Stowage plan - Container positioning on ship"""
    __tablename__ = "stowage_plans"
    
    id = Column(Integer, primary_key=True, index=True)
    navire_id = Column(Integer, ForeignKey('navires.id'))
    voyage_id = Column(String(50))
    plan_pdf = Column(String(255))  # Path to PDF file
    date_creation = Column(DateTime(timezone=True), server_default=func.now())
    valide = Column(Boolean, default=False)
    valide_par = Column(Integer, ForeignKey('users.id'))
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # Relationships
    navire = relationship("Navire")
    positions = relationship("PositionConteneur", back_populates="stowage_plan")


class PositionConteneur(Base):
    """Container position in stowage plan"""
    __tablename__ = "positions_conteneur"
    
    id = Column(Integer, primary_key=True, index=True)
    stowage_plan_id = Column(Integer, ForeignKey('stowage_plans.id'))
    conteneur_id = Column(Integer, ForeignKey('conteneurs.id'))
    bay = Column(Integer)  # Position longitudinale
    row = Column(Integer)  # Position transversale
    tier = Column(Integer)  # Position verticale
    poids = Column(Numeric)
    type_marchandise = Column(String(50))
    port_dechargement = Column(String(50))
    dangereux = Column(Boolean, default=False)
    classe_imdg = Column(String(10))  # Classe IMDG si dangereux
    reefer = Column(Boolean, default=False)
    temperature = Column(Numeric)  # Pour reefer
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # Relationships
    stowage_plan = relationship("StowagePlan", back_populates="positions")
    conteneur = relationship("Conteneur")


class Grue(Base):
    """Crane/Handling equipment"""
    __tablename__ = "grues"
    
    id = Column(Integer, primary_key=True, index=True)
    code = Column(String(50), unique=True, nullable=False)
    type_grue = Column(String(50))  # "portique", "mobile", "roulant"
    capacite_tonnes = Column(Numeric)
    portee_metres = Column(Numeric)
    hauteur_metres = Column(Numeric)
    poste_quai = Column(String(50))
    statut = Column(String(20), default="disponible")  # disponible, en_maintenance, hors_service
    date_maintenance = Column(Date)
    prochaine_maintenance = Column(Date)
    operator_id = Column(Integer, ForeignKey('users.id'))
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relationships
    reservations = relationship("ReservationGrue", back_populates="grue")


class ReservationGrue(Base):
    """Crane reservation for operations"""
    __tablename__ = "reservations_grue"
    
    id = Column(Integer, primary_key=True, index=True)
    grue_id = Column(Integer, ForeignKey('grues.id'))
    operation_id = Column(Integer, ForeignKey('operations_acconage.id'))
    date_debut = Column(DateTime(timezone=True))
    date_fin = Column(DateTime(timezone=True))
    statut = Column(String(20), default="reserve")
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # Relationships
    grue = relationship("Grue", back_populates="reservations")


class Remorqueur(Base):
    """Tugboat for berthing operations"""
    __tablename__ = "remorqueurs"
    
    id = Column(Integer, primary_key=True, index=True)
    nom = Column(String(100), nullable=False)
    puissance_cv = Column(Integer)
    longueur = Column(Numeric)
    port_id = Column(Integer, ForeignKey('agencies.id'))
    statut = Column(String(20), default="disponible")
    capitaine_id = Column(Integer, ForeignKey('users.id'))
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relationships
    amarages = relationship("Amarage", back_populates="remorqueur")


class Amarage(Base):
    """Berthing operations - tugboat assistance"""
    __tablename__ = "amarages"
    
    id = Column(Integer, primary_key=True, index=True)
    escale_id = Column(Integer, ForeignKey('escales.id'))
    remorqueur_id = Column(Integer, ForeignKey('remorqueurs.id'))
    type_amarage = Column(String(50))  # "arrivee", "depart", "deplacement"
    date_debut = Column(DateTime(timezone=True))
    date_fin = Column(DateTime(timezone=True))
    duree_heures = Column(Numeric)
    cout = Column(Numeric)
    notes = Column(Text)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # Relationships
    escale = relationship("Escale", back_populates="amarages")
    remorqueur = relationship("Remorqueur", back_populates="amarages")


class Conteneur(Base):
    """Container model"""
    __tablename__ = "conteneurs"
    
    id = Column(Integer, primary_key=True, index=True)
    numero = Column(String(20), unique=True, nullable=False, index=True)
    type_conteneur = Column(String(20))  # "20' Dry", "40' Dry", "40' Reefer", "Tank", etc.
    statut = Column(String(20))  # "full", "empty", "damage"
    tare_weight = Column(Numeric)  # Poids à vide
    gross_weight = Column(Numeric)  # Poids brut
    net_weight = Column(Numeric)  # Poids net
    navire_id = Column(Integer, ForeignKey('navires.id'))
    proprietaire = Column(String(100))
    scelle = Column(String(50))
    date_scelle = Column(Date)
    inspection_phasanitaire = Column(Boolean, default=False)
    date_inspection = Column(Date)
    certificat_origine = Column(String(255))
    notes = Column(Text)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relationships
    navire = relationship("Navire", back_populates="conteneurs")
    connaissements = relationship("Connaissement", back_populates="conteneur")
    packing_lists = relationship("PackingList", back_populates="conteneur")


class Connaissement(Base):
    """Bill of Lading (B/L)"""
    __tablename__ = "connaissements"
    
    id = Column(Integer, primary_key=True, index=True)
    numero_bl = Column(String(50), unique=True, nullable=False, index=True)
    conteneur_id = Column(Integer, ForeignKey('conteneurs.id'))
    type_bl = Column(String(20))  # "direct", "order", "surrender"
    chargeur = Column(String(100))
    destinataire = Column(String(100))
    port_embarquement = Column(String(50))
    port_dechargement = Column(String(50))
    date_emission = Column(Date)
    montant_freight = Column(Numeric(15, 2))
    devise = Column(String(3), default="XAF")
    signe_par = Column(String(100))
    statut = Column(String(20), default="emis")  # emis, annule, transfere
    escale_id = Column(Integer, ForeignKey('escales.id'))
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relationships
    conteneur = relationship("Conteneur", back_populates="connaissements")
    escale = relationship("Escale")


class PackingList(Base):
    """Packing List - Detailed cargo description"""
    __tablename__ = "packing_lists"
    
    id = Column(Integer, primary_key=True, index=True)
    numero_pl = Column(String(50), unique=True, nullable=False)
    conteneur_id = Column(Integer, ForeignKey('conteneurs.id'))
    connaissement_id = Column(Integer, ForeignKey('connaissements.id'))
    marchandise = Column(String(200))
    description = Column(Text)
    nombre_colis = Column(Integer)
    type_colis = Column(String(50))  # "carton", "palette", "caisse"
    poids_net = Column(Numeric)
    poids_brut = Column(Numeric)
    volume_m3 = Column(Numeric)
    marque = Column(String(100))
    numero_serie = Column(String(100))
    pays_origine = Column(String(50))
    date_emission = Column(Date)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # Relationships
    conteneur = relationship("Conteneur", back_populates="packing_lists")


class Manifeste(Base):
    """Cargo Manifest - Declaration of all cargo on ship"""
    __tablename__ = "manifestes"
    
    id = Column(Integer, primary_key=True, index=True)
    numero_manifeste = Column(String(50), unique=True, nullable=False)
    escale_id = Column(Integer, ForeignKey('escales.id'))
    type_manifeste = Column(String(20))  # "import", "export"
    navire = Column(String(100))
    voyage = Column(String(50))
    port_provenance = Column(String(50))
    port_destination = Column(String(50))
    date_depart = Column(Date)
    nombre_conteneurs = Column(Integer)
    tonnage_total = Column(Numeric)
    valeur_marchandise = Column(Numeric(15, 2))
    devise = Column(String(3), default="XAF")
    signe_par = Column(String(100))
    date_signature = Column(Date)
    conforme = Column(Boolean, default=False)
    controle_par = Column(Integer, ForeignKey('users.id'))
    date_controle = Column(DateTime(timezone=True))
    observations = Column(Text)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relationships
    escale = relationship("Escale", back_populates="manifestes")
    marchandises_dangereuses = relationship("MarchandiseDangereuse", back_populates="manifeste")


class MarchandiseDangereuse(Base):
    """Dangerous goods declaration (IMDG)"""
    __tablename__ = "marchandises_dangereuses"
    
    id = Column(Integer, primary_key=True, index=True)
    manifeste_id = Column(Integer, ForeignKey('manifestes.id'))
    conteneur_id = Column(Integer, ForeignKey('conteneurs.id'))
    classe_imdg = Column(String(10))  # Classe IMDG 1-9
    numero_onu = Column(String(10))  # Number UN
    designation = Column(String(200))
    groupe_emballage = Column(String(10))
    etiquette = Column(String(50))
    quantite = Column(Numeric)
    unite = Column(String(20))
    emplacement = Column(String(50))  # "on deck", "under deck"
    mesures_speciales = Column(Text)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # Relationships
    manifeste = relationship("Manifeste", back_populates="marchandises_dangereuses")


class Surestarie(Base):
    """Demurrage charges - Penalties for port stay"""
    __tablename__ = "surestaries"
    
    id = Column(Integer, primary_key=True, index=True)
    escale_id = Column(Integer, ForeignKey('escales.id'))
    conteneur_id = Column(Integer, ForeignKey('conteneurs.id'))
    connaissement_id = Column(Integer, ForeignKey('connaissements.id'))
    date_debut = Column(Date)
    date_fin = Column(Date)
    nombre_jours = Column(Integer)
    taux_journalier = Column(Numeric(15, 2))
    montant_total = Column(Numeric(15, 2))
    devise = Column(String(3), default="XAF")
    statut = Column(String(20), default="encours")  # encours, paye, annule
    reference_facture = Column(String(50))
    date_paiement = Column(Date)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relationships
    escale = relationship("Escale", back_populates="surestaries")


class TerminalHandlingCharge(Base):
    """Terminal Handling Charges (THC)"""
    __tablename__ = "thc"
    
    id = Column(Integer, primary_key=True, index=True)
    conteneur_id = Column(Integer, ForeignKey('conteneurs.id'))
    type_operation = Column(String(20))  # "import", "export", "transit"
    type_conteneur = Column(String(20))  # "20'", "40'", "reefer"
    montant = Column(Numeric(15, 2))
    devise = Column(String(3), default="XAF")
    date_application = Column(Date)
    facture_reference = Column(String(50))
    statut = Column(String(20), default="facture")
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())


class NettoyageCale(Base):
    """Hold cleaning after discharge"""
    __tablename__ = "nettoyage_cales"
    
    id = Column(Integer, primary_key=True, index=True)
    navire_id = Column(Integer, ForeignKey('navires.id'))
    escale_id = Column(Integer, ForeignKey('escales.id'))
    cale_numero = Column(String(20))
    type_nettoyage = Column(String(50))  # "dry", "wash", "chemical"
    date_debut = Column(DateTime(timezone=True))
    date_fin = Column(DateTime(timezone=True))
    equipe = Column(String(100))
    equipement = Column(String(100))
    conforme = Column(Boolean, default=False)
    inspection_par = Column(Integer, ForeignKey('users.id'))
    date_inspection = Column(DateTime(timezone=True))
    observations = Column(Text)
    created_at = Column(DateTime(timezone=True), server_default=func.now())


class OperationAcconage(Base):
    """Stevedoring operation model"""
    __tablename__ = "operations_acconage"
    
    id = Column(Integer, primary_key=True, index=True)
    reference = Column(String(50), unique=True, nullable=False, index=True)
    escale_id = Column(Integer, ForeignKey('escales.id'))
    type_operation = Column(String(50))  # e.g., "chargement", "dechargement", "transbordement"
    date_debut = Column(DateTime(timezone=True))
    date_fin = Column(DateTime(timezone=True))
    marchandise = Column(String(100))
    quantite = Column(Numeric)
    unite = Column(String(20))
    taux = Column(Numeric)
    montant = Column(Numeric)
    equipe = Column(String(100))
    equipement = Column(String(100))
    statut = Column(String(20), default="planifie")
    notes = Column(Text)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    created_by = Column(Integer, ForeignKey('users.id'))

    # Relationships
    escale = relationship("Escale", back_populates="operations")


class DockerTemporaire(Base):
    """Temporary external docker/stevedore assigned to a specific escale (ship unloading).
    Status auto-expires when parent escale is closed (statut=TERMINE).
    Lifecycle: ACTIF → EXPIRE (auto) or ABSENT (manual).
    Visible across: QHSE (EPI & briefings), RH/Chef du Personnel (vacation pointage),
    Sécurité (badge port). Access strictly limited to the escale's active duration."""
    __tablename__ = "dockers_temporaires"

    id = Column(Integer, primary_key=True, index=True)
    escale_id = Column(Integer, ForeignKey('escales.id'), nullable=False, index=True)

    # Identity
    nom = Column(String(100), nullable=False)
    prenom = Column(String(100), nullable=False)
    telephone = Column(String(30))
    numero_badge = Column(String(50))  # Badge port temporaire (PAD/PAK)
    employeur_externe = Column(String(150))  # Société de main d'œuvre prestataire

    # Shift assignment
    shift = Column(String(20), default='SHIFT_1')
    # SHIFT_1 = 06h00-14h00, SHIFT_2 = 14h00-22h00, SHIFT_3 = 22h00-06h00

    # Compensation
    taux_journalier = Column(Float, default=15000.0)  # FCFA / vacation
    nb_vacations = Column(Integer, default=0)  # Cumulative vacation count
    montant_total = Column(Float, default=0.0)   # Calculated: taux * nb_vacations

    # Compliance (QHSE)
    epi_fourni = Column(Boolean, default=False)
    briefing_securite_fait = Column(Boolean, default=False)
    date_briefing = Column(DateTime(timezone=True))

    # Lifecycle
    statut = Column(String(20), default='ACTIF')
    # ACTIF: during escale / EXPIRE: escale closed / ABSENT: marked absent
    observations = Column(Text)

    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    created_by = Column(Integer, ForeignKey('users.id'))

    # Relationships
    escale = relationship("Escale", foreign_keys=[escale_id])