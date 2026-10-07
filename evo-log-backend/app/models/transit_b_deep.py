"""Modeles transit-douane (expansion approfondie generee).

2 entites de gestion, chacune scoped par company_id.
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

class TransitbIncoterm_categorie(str, enum.Enum):
    E = "e"
    F = "f"
    C = "c"
    D = "d"


class TransitbIncoterm_version(str, enum.Enum):
    V_2010 = "2010"
    V_2020 = "2020"


class TransitbIncoterm_statut(str, enum.Enum):
    ACTIF = "actif"
    OBSOLETE = "obsolete"


class TransitbInspectionRecord_type_visite(str, enum.Enum):
    DOCUMENTAIRE = "documentaire"
    PHYSIQUE = "physique"
    RADIOGRAPHIE = "radiographie"


class TransitbInspectionRecord_statut(str, enum.Enum):
    CONFORME = "conforme"
    NON_CONFORME = "non_conforme"
    LITIGE = "litige"
    EN_ATTENTE = "en_attente"


# ─── Modeles ──────────────────────────────────────────────────────────────────

class TransitbIncoterm(Base):
    """Incoterms applicables."""
    __tablename__ = "transitb_incoterms"
    __table_args__ = (
        UniqueConstraint('company_id', 'code', name='uix_transitb_incoterms_company_code'),
    )
    id = Column(Integer, primary_key=True, index=True)
    company_id = Column(Integer, ForeignKey('companies.id'), nullable=False, index=True)
    code = Column(String(150), nullable=False, index=True)
    libelle = Column(String(150), nullable=True)
    categorie = Column(String(150), nullable=True)
    transfert_risque_lieu = Column(String(150), nullable=True)
    transport_principal = Column(String(150), nullable=True)
    version = Column(String(150), nullable=True)
    statut = Column(String(150), nullable=True)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())


class TransitbInspectionRecord(Base):
    """Proces-verbaux de visite douaniere."""
    __tablename__ = "transitb_inspections"
    __table_args__ = (
        UniqueConstraint('company_id', 'reference', name='uix_transitb_inspections_company_reference'),
    )
    id = Column(Integer, primary_key=True, index=True)
    company_id = Column(Integer, ForeignKey('companies.id'), nullable=False, index=True)
    reference = Column(String(150), nullable=False, index=True)
    declaration = Column(String(150), nullable=True)
    type_visite = Column(String(150), nullable=True)
    agent = Column(String(150), nullable=True)
    bureau = Column(String(150), nullable=True)
    date_inspection = Column(DateTime(timezone=True), nullable=True)
    observation = Column(Text(2000), nullable=True)
    conformite = Column(Boolean, nullable=True)
    statut = Column(String(150), nullable=True)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

