"""Modeles finance-ohada (expansion approfondie generee).

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

class FincCashFlowForecast_statut(str, enum.Enum):
    BROUILLON = "brouillon"
    SOUMIS = "soumis"
    VALIDE = "valide"
    REVISION = "revision"


class FincInvoiceFinancing_statut(str, enum.Enum):
    SOUMISE = "soumise"
    ACCEPTEE = "acceptee"
    AVANCEE = "avancee"
    RECOUVREE = "recouvree"
    REJETEE = "rejetee"


# ─── Modeles ──────────────────────────────────────────────────────────────────

class FincCashFlowForecast(Base):
    """Previsions de tresorerie."""
    __tablename__ = "finc_cash_flow_forecasts"
    __table_args__ = (
        UniqueConstraint('company_id', 'reference', name='uix_finc_cash_flow_forec_company_reference'),
    )
    id = Column(Integer, primary_key=True, index=True)
    company_id = Column(Integer, ForeignKey('companies.id'), nullable=False, index=True)
    reference = Column(String(150), nullable=False, index=True)
    periode = Column(String(150), nullable=True)
    solde_debut = Column(Numeric, nullable=True)
    entrees_prevues = Column(Numeric, nullable=True)
    sorties_prevues = Column(Numeric, nullable=True)
    position_finale = Column(Numeric, nullable=True)
    horizon_jours = Column(Integer, nullable=True)
    statut = Column(String(150), nullable=True)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())


class FincInvoiceFinancing(Base):
    """Affacturage / escompte de factures."""
    __tablename__ = "finc_invoice_financings"
    __table_args__ = (
        UniqueConstraint('company_id', 'reference', name='uix_finc_invoice_financi_company_reference'),
    )
    id = Column(Integer, primary_key=True, index=True)
    company_id = Column(Integer, ForeignKey('companies.id'), nullable=False, index=True)
    reference = Column(String(150), nullable=False, index=True)
    affacteur = Column(String(150), nullable=True)
    facture = Column(String(150), nullable=True)
    montant_facture = Column(Numeric, nullable=True)
    avance_pct = Column(Integer, nullable=True)
    commission = Column(Numeric, nullable=True)
    date_echeance = Column(Date, nullable=True)
    statut = Column(String(150), nullable=True)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

