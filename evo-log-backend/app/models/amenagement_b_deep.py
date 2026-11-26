"""Modeles amenagement-portuaire (expansion approfondie generee).

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

class AmgtbDredgingProject_statut(str, enum.Enum):
    ETUDE = "etude"
    APPEL_OFFRES = "appel_offres"
    EN_COURS = "en_cours"
    ACHEVE = "acheve"
    SUSPENDU = "suspendu"


class AmgtbConcessionPlot_statut(str, enum.Enum):
    LIBRE = "libre"
    CONCEDE = "concede"
    RENOUVELABLE = "renouvelable"
    RESILIE = "resilie"


# ─── Modeles ──────────────────────────────────────────────────────────────────

class AmgtbDredgingProject(Base):
    """Projets de dragage."""
    __tablename__ = "amgtb_dredging_projects"
    __table_args__ = (
        UniqueConstraint('company_id', 'reference', name='uix_amgtb_dredging_proje_company_reference'),
    )
    id = Column(Integer, primary_key=True, index=True)
    company_id = Column(Integer, ForeignKey('companies.id'), nullable=False, index=True)
    reference = Column(String(150), nullable=False, index=True)
    zone = Column(String(150), nullable=True)
    objectif_tirant_eau_m = Column(Integer, nullable=True)
    volume_a_draguer_m3 = Column(Integer, nullable=True)
    volume_rejete_m3 = Column(Integer, nullable=True)
    entreprise = Column(String(150), nullable=True)
    date_debut = Column(Date, nullable=True)
    date_fin = Column(Date, nullable=True)
    statut = Column(String(150), nullable=True)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())


class AmgtbConcessionPlot(Base):
    """Parcelles sous concession."""
    __tablename__ = "amgtb_concession_plots"
    __table_args__ = (
        UniqueConstraint('company_id', 'reference', name='uix_amgtb_concession_plo_company_reference'),
    )
    id = Column(Integer, primary_key=True, index=True)
    company_id = Column(Integer, ForeignKey('companies.id'), nullable=False, index=True)
    reference = Column(String(150), nullable=False, index=True)
    designation = Column(String(150), nullable=True)
    superficie_m2 = Column(Integer, nullable=True)
    concessionnaire = Column(String(150), nullable=True)
    date_debut = Column(Date, nullable=True)
    date_echeance = Column(Date, nullable=True)
    redevance_annuelle = Column(Numeric, nullable=True)
    statut = Column(String(150), nullable=True)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

