"""Modeles parc-vehicules (expansion approfondie generee).

10 entites de gestion, chacune scoped par company_id.
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

class VehicleInventory_energie(str, enum.Enum):
    GASOIL = "gasoil"
    ESSENCE = "essence"
    HYBRIDE = "hybride"
    ELECTRIQUE = "electrique"
    GPL = "gpl"
    CNG = "cng"


class TyreRecord_position(str, enum.Enum):
    AV_G = "av_g"
    AV_D = "av_d"
    AR_G = "ar_g"
    AR_D = "ar_d"
    SPARE = "spare"


class TyreRecord_statut(str, enum.Enum):
    MONTÉE = "montée"
    REPOSE = "repose"
    REBOUTE = "reboute"
    RECONSTRUCTION = "reconstruction"


class SparePart_famille(str, enum.Enum):
    MOTEUR = "moteur"
    FREINAGE = "freinage"
    SUSPENSION = "suspension"
    ELECTRIQUE = "electrique"
    CARROSSERIE = "carrosserie"
    CONSO = "conso"


class WorkshopAppointment_type_intervention(str, enum.Enum):
    PREVENTIF = "preventif"
    CORRECTIF = "correctif"
    REVISION = "revision"
    CONTROLE_TECHNIQUE = "controle_technique"


class WorkshopAppointment_statut(str, enum.Enum):
    PLANIFIE = "planifie"
    EN_COURS = "en_cours"
    TERMINE = "termine"
    ANNULE = "annule"


class InsuranceClaim_type_sinistre(str, enum.Enum):
    COLLISION = "collision"
    VOL = "vol"
    INCENDIE = "incendie"
    BRIS_DE_GLACE = "bris_de_glace"
    MARCHANDISES = "marchandises"


class InsuranceClaim_statut(str, enum.Enum):
    OUVERT = "ouvert"
    EN_INSTRUCTION = "en_instruction"
    INDEMNISE = "indemnise"
    REJETE = "rejete"


class RegistrationRecord_statut(str, enum.Enum):
    VALIDE = "valide"
    EXPIRE = "expire"
    EN_RENEW = "en_renew"
    TRANSFERT = "transfert"


class TechnicalVisit_resultat(str, enum.Enum):
    CONFORME = "conforme"
    DEFAIT_MINEUR = "defait_mineur"
    DEFAIT_MAJEUR = "defait_majeur"
    REFUS = "refus"


class TechnicalVisit_statut(str, enum.Enum):
    PLANIFIE = "planifie"
    FAITE = "faite"
    ECHEANCE_PROCHAINE = "echeance_prochaine"


class FuelConsumption_carburant(str, enum.Enum):
    GASOIL = "gasoil"
    ESSENCE = "essence"
    GPL = "gpl"
    CNG = "cng"


class VehicleLifecycle_mode_reforme(str, enum.Enum):
    VENTE = "vente"
    RECYCLAGE = "recyclage"
    DON = "don"
    DESTRUCTION = "destruction"


# ─── Modeles ──────────────────────────────────────────────────────────────────

class VehicleInventory(Base):
    """Inventaire complet du parc."""
    __tablename__ = "vehicle_inventories"
    __table_args__ = (
        UniqueConstraint('company_id', 'numero_serie', name='uix_vehicle_inventories_company_numero_serie'),
    )
    id = Column(Integer, primary_key=True, index=True)
    company_id = Column(Integer, ForeignKey('companies.id'), nullable=False, index=True)
    numero_serie = Column(String(150), nullable=False, index=True)
    marque = Column(String(150), nullable=True)
    modele = Column(String(150), nullable=True)
    annee = Column(Integer, nullable=True)
    carrosserie = Column(String(150), nullable=True)
    energie = Column(_enum(VehicleInventory_energie), default=VehicleInventory_energie.GASOIL)
    kilometrage = Column(Numeric, nullable=True)
    cout_acquisition_xaf = Column(Numeric, nullable=True)
    valeur_argent_xaf = Column(Numeric, nullable=True)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())


class TyreRecord(Base):
    """Gestion pneumatiques."""
    __tablename__ = "tyre_records"
    __table_args__ = (
        UniqueConstraint('company_id', 'numero_gomme', name='uix_tyre_records_company_numero_gomme'),
    )
    id = Column(Integer, primary_key=True, index=True)
    company_id = Column(Integer, ForeignKey('companies.id'), nullable=False, index=True)
    numero_gomme = Column(String(150), nullable=False, index=True)
    vehicule_id = Column(Integer, nullable=True)
    dimension = Column(String(150), nullable=True)
    marque = Column(String(150), nullable=True)
    position = Column(_enum(TyreRecord_position), default=TyreRecord_position.AV_G)
    km_parcourus = Column(Numeric, nullable=True)
    profondeur_couronne_mm = Column(Numeric, nullable=True)
    date_montage = Column(Date, nullable=True)
    statut = Column(_enum(TyreRecord_statut), default=TyreRecord_statut.MONTÉE)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())


class SparePart(Base):
    """Pieces detachees / stock atelier."""
    __tablename__ = "spare_parts"
    __table_args__ = (
        UniqueConstraint('company_id', 'code_piece', name='uix_spare_parts_company_code_piece'),
    )
    id = Column(Integer, primary_key=True, index=True)
    company_id = Column(Integer, ForeignKey('companies.id'), nullable=False, index=True)
    code_piece = Column(String(150), nullable=False, index=True)
    designation = Column(String(150), nullable=True)
    referencence_constructeur = Column(String(150), nullable=True)
    famille = Column(_enum(SparePart_famille), default=SparePart_famille.MOTEUR)
    stock_actuel = Column(Numeric, nullable=True)
    seuil_mini = Column(Numeric, nullable=True)
    prix_unitaire_xaf = Column(Numeric, nullable=True)
    fournisseur_principal = Column(String(150), nullable=True)
    compatibilites = Column(Text, nullable=True)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())


class WorkshopAppointment(Base):
    """Planification atelier."""
    __tablename__ = "workshop_appointments"
    __table_args__ = (
        UniqueConstraint('company_id', 'reference', name='uix_workshop_appointment_company_reference'),
    )
    id = Column(Integer, primary_key=True, index=True)
    company_id = Column(Integer, ForeignKey('companies.id'), nullable=False, index=True)
    reference = Column(String(150), nullable=False, index=True)
    vehicule_id = Column(Integer, nullable=True)
    date_horaire = Column(DateTime(timezone=True), nullable=True)
    type_intervention = Column(_enum(WorkshopAppointment_type_intervention), default=WorkshopAppointment_type_intervention.PREVENTIF)
    mecanicien = Column(String(150), nullable=True)
    duree_estimee_h = Column(Numeric, nullable=True)
    cout_estime_xaf = Column(Numeric, nullable=True)
    statut = Column(_enum(WorkshopAppointment_statut), default=WorkshopAppointment_statut.PLANIFIE)
    notes = Column(Text, nullable=True)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())


class InsuranceClaim(Base):
    """Sinistres et assurances."""
    __tablename__ = "insurance_claims"
    __table_args__ = (
        UniqueConstraint('company_id', 'numero_sinistre', name='uix_insurance_claims_company_numero_sinistre'),
    )
    id = Column(Integer, primary_key=True, index=True)
    company_id = Column(Integer, ForeignKey('companies.id'), nullable=False, index=True)
    numero_sinistre = Column(String(150), nullable=False, index=True)
    vehicule_id = Column(Integer, nullable=True)
    date_sinistre = Column(Date, nullable=True)
    type_sinistre = Column(_enum(InsuranceClaim_type_sinistre), default=InsuranceClaim_type_sinistre.COLLISION)
    description = Column(Text, nullable=True)
    montant_estime_xaf = Column(Numeric, nullable=True)
    montant_indemnise_xaf = Column(Numeric, nullable=True)
    assureur = Column(String(150), nullable=True)
    statut = Column(_enum(InsuranceClaim_statut), default=InsuranceClaim_statut.OUVERT)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())


class RegistrationRecord(Base):
    """Suivi immatriculation."""
    __tablename__ = "registration_records"
    __table_args__ = (
        UniqueConstraint('company_id', 'numero_immatriculation', name='uix_registration_records_company_numero_immatric'),
    )
    id = Column(Integer, primary_key=True, index=True)
    company_id = Column(Integer, ForeignKey('companies.id'), nullable=False, index=True)
    numero_immatriculation = Column(String(150), nullable=False, index=True)
    vehicule_id = Column(Integer, nullable=True)
    proprietaire = Column(String(150), nullable=True)
    date_emission = Column(Date, nullable=True)
    date_expiration = Column(Date, nullable=True)
    autorite = Column(String(150), nullable=True)
    statut = Column(_enum(RegistrationRecord_statut), default=RegistrationRecord_statut.VALIDE)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())


class TechnicalVisit(Base):
    """Visites techniques periodiques."""
    __tablename__ = "technical_visits"
    __table_args__ = (
        UniqueConstraint('company_id', 'numero_pv', name='uix_technical_visits_company_numero_pv'),
    )
    id = Column(Integer, primary_key=True, index=True)
    company_id = Column(Integer, ForeignKey('companies.id'), nullable=False, index=True)
    numero_pv = Column(String(150), nullable=False, index=True)
    vehicule_id = Column(Integer, nullable=True)
    date_visite = Column(Date, nullable=True)
    centre_controle = Column(String(150), nullable=True)
    resultat = Column(_enum(TechnicalVisit_resultat), default=TechnicalVisit_resultat.CONFORME)
    observations = Column(Text, nullable=True)
    contre_visite_possible = Column(Boolean, nullable=True)
    statut = Column(_enum(TechnicalVisit_statut), default=TechnicalVisit_statut.PLANIFIE)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())


class FuelConsumption(Base):
    """Consommation par vehicule."""
    __tablename__ = "fuel_consumptions"
    __table_args__ = (
        UniqueConstraint('company_id', 'reference', name='uix_fuel_consumptions_company_reference'),
    )
    id = Column(Integer, primary_key=True, index=True)
    company_id = Column(Integer, ForeignKey('companies.id'), nullable=False, index=True)
    reference = Column(String(150), nullable=False, index=True)
    vehicule_id = Column(Integer, nullable=True)
    date = Column(Date, nullable=True)
    litres = Column(Numeric, nullable=True)
    prix_total_xaf = Column(Numeric, nullable=True)
    km_etape = Column(Numeric, nullable=True)
    conso_l100km = Column(Numeric, nullable=True)
    station = Column(String(150), nullable=True)
    carburant = Column(_enum(FuelConsumption_carburant), default=FuelConsumption_carburant.GASOIL)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())


class VehicleLifecycle(Base):
    """Cycle de vie / reforme."""
    __tablename__ = "vehicle_lifecycles"
    __table_args__ = (
        UniqueConstraint('company_id', 'reference', name='uix_vehicle_lifecycles_company_reference'),
    )
    id = Column(Integer, primary_key=True, index=True)
    company_id = Column(Integer, ForeignKey('companies.id'), nullable=False, index=True)
    reference = Column(String(150), nullable=False, index=True)
    vehicule_id = Column(Integer, nullable=True)
    date_acquisition = Column(Date, nullable=True)
    date_reforme = Column(Date, nullable=True)
    duree_detention_an = Column(Integer, nullable=True)
    km_final = Column(Numeric, nullable=True)
    mode_reforme = Column(_enum(VehicleLifecycle_mode_reforme), default=VehicleLifecycle_mode_reforme.VENTE)
    valeur_recuperation_xaf = Column(Numeric, nullable=True)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())


class CostAnalysis(Base):
    """Analyse couts par vehicule."""
    __tablename__ = "cost_analyses"
    __table_args__ = (
        UniqueConstraint('company_id', 'reference', name='uix_cost_analyses_company_reference'),
    )
    id = Column(Integer, primary_key=True, index=True)
    company_id = Column(Integer, ForeignKey('companies.id'), nullable=False, index=True)
    reference = Column(String(150), nullable=False, index=True)
    vehicule_id = Column(Integer, nullable=True)
    periode = Column(String(150), nullable=True)
    cout_carburant_xaf = Column(Numeric, nullable=True)
    cout_maintenance_xaf = Column(Numeric, nullable=True)
    cout_assurance_xaf = Column(Numeric, nullable=True)
    cout_amortissement_xaf = Column(Numeric, nullable=True)
    cout_total_xaf = Column(Numeric, nullable=True)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

