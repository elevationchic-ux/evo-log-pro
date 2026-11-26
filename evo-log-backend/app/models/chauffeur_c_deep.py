"""Modeles portail-chauffeur (expansion approfondie generee).

19 entites de gestion, chacune scoped par company_id.
Convention d'honnetete : aucune valeur par defaut, NULL = "non enregistre".
"""
from sqlalchemy import (
    Column, Integer, String, Text, DateTime, Boolean, Float,
    ForeignKey, Date, Numeric, UniqueConstraint, Enum as SAEnum,
)
from sqlalchemy.sql import func
import enum

from app.core.database import Base


def _enum(cls):
    return SAEnum(cls, native_enum=False, create_constraint=False,
                  values_callable=lambda x: [e.value for e in x])


# ─── Enums ────────────────────────────────────────────────────────────────────

class ChfTripSheet_statut(str, enum.Enum):
    EN_COURS = "en_cours"
    TERMINEE = "terminee"
    VALIDEE = "validee"
    ANOMALIE = "anomalie"


class ChfDailyVehicleCheck_statut(str, enum.Enum):
    CONFORME = "conforme"
    ANOMALIE = "anomalie"
    IMMOBILISE = "immobilise"


class ChfFuelLog_statut(str, enum.Enum):
    ENREGISTRE = "enregistre"
    JUSTIFIE = "justifie"
    REMBOURSE = "rembourse"
    REJETE = "rejete"


class ChfDrivingTimeRecord_statut(str, enum.Enum):
    CONDUITE = "conduite"
    DISPO = "dispo"
    REPOS = "repos"
    HORS_REGLE = "hors_regle"


class ChfRestBreak_statut(str, enum.Enum):
    PRISE = "prise"
    INTERROMPU = "interrompu"
    MANQUANT = "manquant"


class ChfTollReceipt_statut(str, enum.Enum):
    ENREGISTRE = "enregistre"
    REMBOURSE = "rembourse"
    REJETE = "rejete"


class ChfParkingSession_statut(str, enum.Enum):
    OUVERTE = "ouverte"
    FERMEE = "fermee"
    REMBOURSEE = "remboursee"


class ChfCargoSeal_statut(str, enum.Enum):
    POSE = "pose"
    CONTROLE = "controle"
    ROMPU = "rompu"
    REMPPLACE = "rempplace"


class ChfRoadsideIncident_gravite(str, enum.Enum):
    MINEUR = "mineur"
    MAJEUR = "majeur"
    CRITIQUE = "critique"


class ChfRoadsideIncident_statut(str, enum.Enum):
    OUVERT = "ouvert"
    SIGNAL = "signal"
    RESOLU = "resolu"
    ASSURANCE = "assurance"


class ChfDeliveryStop_statut(str, enum.Enum):
    A_FAIRE = "a_faire"
    VISITE = "visite"
    ABSENCE = "absence"
    REFUS = "refus"


class ChfMileageLog_statut(str, enum.Enum):
    ENREGISTRE = "enregistre"
    VERIFIE = "verifie"
    ANOMALE = "anomale"


class ChfLoadSecuringCheck_statut(str, enum.Enum):
    CONFORME = "conforme"
    A_CORRIGER = "a_corriger"
    BLOQUE = "bloque"


class ChfBorderCrossing_entree_sortie(str, enum.Enum):
    ENTREE = "entree"
    SORTIE = "sortie"
    TRANSIT = "transit"


class ChfBorderCrossing_statut(str, enum.Enum):
    FRANCHI = "franchi"
    BLOQUE = "bloque"
    EN_ATTENTE = "en_attente"


class ChfDeliveryAppointment_statut(str, enum.Enum):
    CONFIRME = "confirme"
    EN_ATTENTE = "en_attente"
    MANQUE = "manque"
    REPROGRAMME = "reprogramme"


class ChfPpeIssue_etat(str, enum.Enum):
    NEUF = "neuf"
    BON = "bon"
    USE = "use"
    HORS_SERVICE = "hors_service"


class ChfPpeIssue_statut(str, enum.Enum):
    REMIS = "remis"
    A_RENOUVELER = "a_renouveler"
    REFORME = "reforme"


class ChfShiftHandover_statut(str, enum.Enum):
    FAITE = "faite"
    PARTIELLE = "partielle"
    CONTESTEE = "contestee"


class ChfBreakdownReport_statut(str, enum.Enum):
    SIGNAL = "signal"
    PRISE_EN_CHARGE = "prise_en_charge"
    REPOUSSE = "repousse"
    IMMOBILISE = "immobilise"


class ChfTyreCheck_statut(str, enum.Enum):
    CONFORME = "conforme"
    A_SURVEILLER = "a_surveiller"
    A_REMPLACER = "a_remplacer"


class ChfCargoPhoto_statut(str, enum.Enum):
    CHARGEMENT = "chargement"
    LIVRAISON = "livraison"
    LITIGE = "litige"
    ARCHEVEE = "archevee"


# ─── Modeles ──────────────────────────────────────────────────────────────────

class ChfTripSheet(Base):
    """Feuilles de route."""
    __tablename__ = "chf_trip_sheets"
    __table_args__ = (
        UniqueConstraint('company_id', 'reference', name='uix_chf_trip_sheets_company_reference'),
    )
    id = Column(Integer, primary_key=True, index=True)
    company_id = Column(Integer, ForeignKey('companies.id'), nullable=False, index=True)
    reference = Column(String(150), nullable=False, index=True)
    mission = Column(String(150), nullable=True)
    debut = Column(DateTime(timezone=True), nullable=True)
    fin = Column(DateTime(timezone=True), nullable=True)
    km_debut = Column(Integer, nullable=True)
    km_fin = Column(Integer, nullable=True)
    statut = Column(String(150), nullable=True)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())


class ChfDailyVehicleCheck(Base):
    """Controles quotidiens du vehicule."""
    __tablename__ = "chf_daily_vehicle_checks"
    __table_args__ = (
        UniqueConstraint('company_id', 'reference', name='uix_chf_daily_vehicle_ch_company_reference'),
    )
    id = Column(Integer, primary_key=True, index=True)
    company_id = Column(Integer, ForeignKey('companies.id'), nullable=False, index=True)
    reference = Column(String(150), nullable=False, index=True)
    vehicule = Column(String(150), nullable=True)
    date_controle = Column(DateTime(timezone=True), nullable=True)
    points_controles = Column(Integer, nullable=True)
    anomalies = Column(Boolean, nullable=True)
    statut = Column(String(150), nullable=True)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())


class ChfFuelLog(Base):
    """Carnet carburant."""
    __tablename__ = "chf_fuel_logs"
    __table_args__ = (
        UniqueConstraint('company_id', 'reference', name='uix_chf_fuel_logs_company_reference'),
    )
    id = Column(Integer, primary_key=True, index=True)
    company_id = Column(Integer, ForeignKey('companies.id'), nullable=False, index=True)
    reference = Column(String(150), nullable=False, index=True)
    vehicule = Column(String(150), nullable=True)
    litres = Column(Numeric, nullable=True)
    prix = Column(Numeric, nullable=True)
    station = Column(String(150), nullable=True)
    date_plein = Column(DateTime(timezone=True), nullable=True)
    statut = Column(String(150), nullable=True)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())


class ChfDrivingTimeRecord(Base):
    """Temps de conduite."""
    __tablename__ = "chf_driving_times"
    __table_args__ = (
        UniqueConstraint('company_id', 'reference', name='uix_chf_driving_times_company_reference'),
    )
    id = Column(Integer, primary_key=True, index=True)
    company_id = Column(Integer, ForeignKey('companies.id'), nullable=False, index=True)
    reference = Column(String(150), nullable=False, index=True)
    chauffeur = Column(String(150), nullable=True)
    debut = Column(DateTime(timezone=True), nullable=True)
    fin = Column(DateTime(timezone=True), nullable=True)
    minutes_conduite = Column(Integer, nullable=True)
    statut = Column(String(150), nullable=True)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())


class ChfRestBreak(Base):
    """Pauses et repos."""
    __tablename__ = "chf_rest_breaks"
    __table_args__ = (
        UniqueConstraint('company_id', 'reference', name='uix_chf_rest_breaks_company_reference'),
    )
    id = Column(Integer, primary_key=True, index=True)
    company_id = Column(Integer, ForeignKey('companies.id'), nullable=False, index=True)
    reference = Column(String(150), nullable=False, index=True)
    chauffeur = Column(String(150), nullable=True)
    debut = Column(DateTime(timezone=True), nullable=True)
    duree_min = Column(Integer, nullable=True)
    lieu = Column(String(150), nullable=True)
    statut = Column(String(150), nullable=True)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())


class ChfTollReceipt(Base):
    """Recus de peage."""
    __tablename__ = "chf_toll_receipts"
    __table_args__ = (
        UniqueConstraint('company_id', 'reference', name='uix_chf_toll_receipts_company_reference'),
    )
    id = Column(Integer, primary_key=True, index=True)
    company_id = Column(Integer, ForeignKey('companies.id'), nullable=False, index=True)
    reference = Column(String(150), nullable=False, index=True)
    peage = Column(String(150), nullable=True)
    montant = Column(Numeric, nullable=True)
    date_passage = Column(DateTime(timezone=True), nullable=True)
    troncon = Column(String(150), nullable=True)
    statut = Column(String(150), nullable=True)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())


class ChfParkingSession(Base):
    """Sessions de parking."""
    __tablename__ = "chf_parking_sessions"
    __table_args__ = (
        UniqueConstraint('company_id', 'reference', name='uix_chf_parking_sessions_company_reference'),
    )
    id = Column(Integer, primary_key=True, index=True)
    company_id = Column(Integer, ForeignKey('companies.id'), nullable=False, index=True)
    reference = Column(String(150), nullable=False, index=True)
    lieu = Column(String(150), nullable=True)
    entree = Column(DateTime(timezone=True), nullable=True)
    sortie = Column(DateTime(timezone=True), nullable=True)
    frais = Column(Numeric, nullable=True)
    statut = Column(String(150), nullable=True)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())


class ChfCargoSeal(Base):
    """Plombs de cargaison."""
    __tablename__ = "chf_cargo_seals"
    __table_args__ = (
        UniqueConstraint('company_id', 'reference', name='uix_chf_cargo_seals_company_reference'),
    )
    id = Column(Integer, primary_key=True, index=True)
    company_id = Column(Integer, ForeignKey('companies.id'), nullable=False, index=True)
    reference = Column(String(150), nullable=False, index=True)
    unite = Column(String(150), nullable=True)
    numero_plomb = Column(String(150), nullable=True)
    pose_datetime = Column(DateTime(timezone=True), nullable=True)
    retrait_datetime = Column(DateTime(timezone=True), nullable=True)
    intact = Column(Boolean, nullable=True)
    statut = Column(String(150), nullable=True)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())


class ChfRoadsideIncident(Base):
    """Incidents de route."""
    __tablename__ = "chf_roadside_incidents"
    __table_args__ = (
        UniqueConstraint('company_id', 'reference', name='uix_chf_roadside_inciden_company_reference'),
    )
    id = Column(Integer, primary_key=True, index=True)
    company_id = Column(Integer, ForeignKey('companies.id'), nullable=False, index=True)
    reference = Column(String(150), nullable=False, index=True)
    type_incident = Column(String(150), nullable=True)
    localisation = Column(String(150), nullable=True)
    date = Column(DateTime(timezone=True), nullable=True)
    gravite = Column(String(150), nullable=True)
    decrit = Column(Text, nullable=True)
    statut = Column(String(150), nullable=True)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())


class ChfDeliveryStop(Base):
    """Points de livraison."""
    __tablename__ = "chf_delivery_stops"
    __table_args__ = (
        UniqueConstraint('company_id', 'reference', name='uix_chf_delivery_stops_company_reference'),
    )
    id = Column(Integer, primary_key=True, index=True)
    company_id = Column(Integer, ForeignKey('companies.id'), nullable=False, index=True)
    reference = Column(String(150), nullable=False, index=True)
    tournee = Column(String(150), nullable=True)
    adresse = Column(String(150), nullable=True)
    ordre = Column(Integer, nullable=True)
    arrivee = Column(DateTime(timezone=True), nullable=True)
    departure = Column(DateTime(timezone=True), nullable=True)
    statut = Column(String(150), nullable=True)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())


class ChfMileageLog(Base):
    """Releves de kilometrage."""
    __tablename__ = "chf_mileage_logs"
    __table_args__ = (
        UniqueConstraint('company_id', 'reference', name='uix_chf_mileage_logs_company_reference'),
    )
    id = Column(Integer, primary_key=True, index=True)
    company_id = Column(Integer, ForeignKey('companies.id'), nullable=False, index=True)
    reference = Column(String(150), nullable=False, index=True)
    vehicule = Column(String(150), nullable=True)
    date = Column(DateTime(timezone=True), nullable=True)
    km_debut = Column(Integer, nullable=True)
    km_fin = Column(Integer, nullable=True)
    statut = Column(String(150), nullable=True)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())


class ChfLoadSecuringCheck(Base):
    """Controles d' arrimage."""
    __tablename__ = "chf_load_securing"
    __table_args__ = (
        UniqueConstraint('company_id', 'reference', name='uix_chf_load_securing_company_reference'),
    )
    id = Column(Integer, primary_key=True, index=True)
    company_id = Column(Integer, ForeignKey('companies.id'), nullable=False, index=True)
    reference = Column(String(150), nullable=False, index=True)
    unite = Column(String(150), nullable=True)
    sangles_ok = Column(Boolean, nullable=True)
    poids_equilibre = Column(String(150), nullable=True)
    controle_datetime = Column(DateTime(timezone=True), nullable=True)
    statut = Column(String(150), nullable=True)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())


class ChfBorderCrossing(Base):
    """Postes frontiere."""
    __tablename__ = "chf_border_crossings"
    __table_args__ = (
        UniqueConstraint('company_id', 'reference', name='uix_chf_border_crossings_company_reference'),
    )
    id = Column(Integer, primary_key=True, index=True)
    company_id = Column(Integer, ForeignKey('companies.id'), nullable=False, index=True)
    reference = Column(String(150), nullable=False, index=True)
    poste = Column(String(150), nullable=True)
    pays = Column(String(150), nullable=True)
    entree_sortie = Column(String(150), nullable=True)
    horodatage = Column(DateTime(timezone=True), nullable=True)
    documents_ok = Column(Boolean, nullable=True)
    statut = Column(String(150), nullable=True)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())


class ChfDeliveryAppointment(Base):
    """RDV de livraison."""
    __tablename__ = "chf_delivery_appointments"
    __table_args__ = (
        UniqueConstraint('company_id', 'reference', name='uix_chf_delivery_appoint_company_reference'),
    )
    id = Column(Integer, primary_key=True, index=True)
    company_id = Column(Integer, ForeignKey('companies.id'), nullable=False, index=True)
    reference = Column(String(150), nullable=False, index=True)
    client = Column(String(150), nullable=True)
    creneau = Column(DateTime(timezone=True), nullable=True)
    site = Column(String(150), nullable=True)
    contact = Column(String(150), nullable=True)
    statut = Column(String(150), nullable=True)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())


class ChfPpeIssue(Base):
    """Remise d' EPI."""
    __tablename__ = "chf_ppe_issues"
    __table_args__ = (
        UniqueConstraint('company_id', 'reference', name='uix_chf_ppe_issues_company_reference'),
    )
    id = Column(Integer, primary_key=True, index=True)
    company_id = Column(Integer, ForeignKey('companies.id'), nullable=False, index=True)
    reference = Column(String(150), nullable=False, index=True)
    equipement = Column(String(150), nullable=True)
    taille = Column(String(150), nullable=True)
    date_remise = Column(Date, nullable=True)
    etat = Column(String(150), nullable=True)
    statut = Column(String(150), nullable=True)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())


class ChfShiftHandover(Base):
    """Relais de conduite."""
    __tablename__ = "chf_shift_handovers"
    __table_args__ = (
        UniqueConstraint('company_id', 'reference', name='uix_chf_shift_handovers_company_reference'),
    )
    id = Column(Integer, primary_key=True, index=True)
    company_id = Column(Integer, ForeignKey('companies.id'), nullable=False, index=True)
    reference = Column(String(150), nullable=False, index=True)
    sortant = Column(String(150), nullable=True)
    entrant = Column(String(150), nullable=True)
    datetime = Column(DateTime(timezone=True), nullable=True)
    consignes = Column(Text, nullable=True)
    statut = Column(String(150), nullable=True)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())


class ChfBreakdownReport(Base):
    """Signalements de panne."""
    __tablename__ = "chf_breakdown_reports"
    __table_args__ = (
        UniqueConstraint('company_id', 'reference', name='uix_chf_breakdown_report_company_reference'),
    )
    id = Column(Integer, primary_key=True, index=True)
    company_id = Column(Integer, ForeignKey('companies.id'), nullable=False, index=True)
    reference = Column(String(150), nullable=False, index=True)
    vehicule = Column(String(150), nullable=True)
    panne = Column(String(150), nullable=True)
    lieu = Column(String(150), nullable=True)
    date_signalement = Column(DateTime(timezone=True), nullable=True)
    immobilise = Column(Boolean, nullable=True)
    statut = Column(String(150), nullable=True)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())


class ChfTyreCheck(Base):
    """Controles pneumatiques."""
    __tablename__ = "chf_tyre_checks"
    __table_args__ = (
        UniqueConstraint('company_id', 'reference', name='uix_chf_tyre_checks_company_reference'),
    )
    id = Column(Integer, primary_key=True, index=True)
    company_id = Column(Integer, ForeignKey('companies.id'), nullable=False, index=True)
    reference = Column(String(150), nullable=False, index=True)
    vehicule = Column(String(150), nullable=True)
    numero_essieu = Column(Integer, nullable=True)
    pression_bar = Column(Numeric, nullable=True)
    usure_mm = Column(Numeric, nullable=True)
    date_controle = Column(DateTime(timezone=True), nullable=True)
    statut = Column(String(150), nullable=True)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())


class ChfCargoPhoto(Base):
    """Photos de cargaison."""
    __tablename__ = "chf_cargo_photos"
    __table_args__ = (
        UniqueConstraint('company_id', 'reference', name='uix_chf_cargo_photos_company_reference'),
    )
    id = Column(Integer, primary_key=True, index=True)
    company_id = Column(Integer, ForeignKey('companies.id'), nullable=False, index=True)
    reference = Column(String(150), nullable=False, index=True)
    mission = Column(String(150), nullable=True)
    prise = Column(DateTime(timezone=True), nullable=True)
    legende = Column(String(150), nullable=True)
    fichier = Column(String(150), nullable=True)
    statut = Column(String(150), nullable=True)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

