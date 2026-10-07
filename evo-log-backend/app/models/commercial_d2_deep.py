"""Modeles portail-commercial (expansion approfondie generee).

1 entites de gestion, chacune scoped par company_id.
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

class CommCompetitorNote_statut(str, enum.Enum):
    SAISIE = "saisie"
    VERIFIEE = "verifiee"
    PARTAGEE = "partagee"
    CLASSE = "classe"


# ─── Modeles ──────────────────────────────────────────────────────────────────

class CommCompetitorNote(Base):
    """Notes de veille concurrence."""
    __tablename__ = "comm_competitor_notes"
    __table_args__ = (
        UniqueConstraint('company_id', 'reference', name='uix_comm_competitor_note_company_reference'),
    )
    id = Column(Integer, primary_key=True, index=True)
    company_id = Column(Integer, ForeignKey('companies.id'), nullable=False, index=True)
    reference = Column(String(150), nullable=False, index=True)
    concurrent = Column(String(150), nullable=True)
    fait_observe = Column(Text, nullable=True)
    marche = Column(String(150), nullable=True)
    date = Column(Date, nullable=True)
    statut = Column(String(150), nullable=True)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

