"""Modeles rh-personnel (expansion approfondie generee).

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

class RhCTrainingPlan_categorie(str, enum.Enum):
    TECHNIQUE = "technique"
    SECURITE = "securite"
    MANAGEMENT = "management"
    REGLEMENTAIRE = "reglementaire"


class RhCTrainingPlan_statut(str, enum.Enum):
    PLANIFIE = "planifie"
    EN_COURS = "en_cours"
    TERMINE = "termine"
    ABANDONNE = "abandonne"


class RhCDisciplinaryRecord_type_sanction(str, enum.Enum):
    AVERTISSEMENT = "avertissement"
    BLAME = "blame"
    MISE_PIED = "mise_pied"
    SUSPENSION = "suspension"
    LICENCIEMENT = "licenciement"


class RhCDisciplinaryRecord_statut(str, enum.Enum):
    OUVERT = "ouvert"
    INSTRUIT = "instruit"
    APPLIQUEE = "appliquee"
    LEVEE = "levee"
    CONTESTEE = "contestee"


# ─── Modeles ──────────────────────────────────────────────────────────────────

class RhCTrainingPlan(Base):
    """Plans de formation."""
    __tablename__ = "rhc_training_plans"
    __table_args__ = (
        UniqueConstraint('company_id', 'reference', name='uix_rhc_training_plans_company_reference'),
    )
    id = Column(Integer, primary_key=True, index=True)
    company_id = Column(Integer, ForeignKey('companies.id'), nullable=False, index=True)
    reference = Column(String(150), nullable=False, index=True)
    intitule = Column(String(150), nullable=True)
    categorie = Column(String(150), nullable=True)
    collaborateur = Column(String(150), nullable=True)
    organisme = Column(String(150), nullable=True)
    heures_financees = Column(Integer, nullable=True)
    heures_realisees = Column(Integer, nullable=True)
    date_debut = Column(Date, nullable=True)
    statut = Column(String(150), nullable=True)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())


class RhCDisciplinaryRecord(Base):
    """Registre disciplinaire."""
    __tablename__ = "rhc_disciplinary_records"
    __table_args__ = (
        UniqueConstraint('company_id', 'reference', name='uix_rhc_disciplinary_rec_company_reference'),
    )
    id = Column(Integer, primary_key=True, index=True)
    company_id = Column(Integer, ForeignKey('companies.id'), nullable=False, index=True)
    reference = Column(String(150), nullable=False, index=True)
    collaborateur = Column(String(150), nullable=True)
    type_sanction = Column(String(150), nullable=True)
    motif = Column(Text, nullable=True)
    date_effet = Column(Date, nullable=True)
    date_fin_effet = Column(Date, nullable=True)
    decideur = Column(String(150), nullable=True)
    statut = Column(String(150), nullable=True)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

