"""Modeles comptabilite-ohada (expansion approfondie generee).

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

class CmptcJournalReversal_statut(str, enum.Enum):
    PROPOSEE = "proposee"
    VALIDEE = "validee"
    COMPTABILISEE = "comptabilisee"
    REJETEE = "rejetee"


class CmptcBankReconciliation_statut(str, enum.Enum):
    EN_COURS = "en_cours"
    EQUILIBRE = "equilibre"
    ECART_CONSTATE = "ecart_constate"
    VALIDE = "valide"


# ─── Modeles ──────────────────────────────────────────────────────────────────

class CmptcJournalReversal(Base):
    """Contre-passations d'ecritures."""
    __tablename__ = "cmptc_journal_reversals"
    __table_args__ = (
        UniqueConstraint('company_id', 'reference', name='uix_cmptc_journal_revers_company_reference'),
    )
    id = Column(Integer, primary_key=True, index=True)
    company_id = Column(Integer, ForeignKey('companies.id'), nullable=False, index=True)
    reference = Column(String(150), nullable=False, index=True)
    ecriture_origine = Column(String(150), nullable=True)
    date_reversal = Column(Date, nullable=True)
    compte_debit = Column(String(150), nullable=True)
    compte_credit = Column(String(150), nullable=True)
    montant = Column(Numeric, nullable=True)
    motif = Column(Text, nullable=True)
    statut = Column(String(150), nullable=True)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())


class CmptcBankReconciliation(Base):
    """Rapprochements bancaires."""
    __tablename__ = "cmptc_bank_reconciliations"
    __table_args__ = (
        UniqueConstraint('company_id', 'reference', name='uix_cmptc_bank_reconcili_company_reference'),
    )
    id = Column(Integer, primary_key=True, index=True)
    company_id = Column(Integer, ForeignKey('companies.id'), nullable=False, index=True)
    reference = Column(String(150), nullable=False, index=True)
    compte_banque = Column(String(150), nullable=True)
    date_releve = Column(Date, nullable=True)
    solde_comptable = Column(Numeric, nullable=True)
    solde_bancaire = Column(Numeric, nullable=True)
    ecart = Column(Numeric, nullable=True)
    date_rapprochement = Column(Date, nullable=True)
    statut = Column(String(150), nullable=True)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

