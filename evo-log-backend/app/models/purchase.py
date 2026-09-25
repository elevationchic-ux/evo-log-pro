"""
Purchase models - demandes d'achat (requisitions) en amont du bon de commande.

Workflow : brouillon -> soumise -> approuvee / rejetee.
"""
from sqlalchemy import Column, Integer, String, Text, DateTime, Boolean, ForeignKey, Enum, Numeric
from sqlalchemy.sql import func
import enum

from app.core.database import Base


class RequisitionStatut(str, enum.Enum):
    BROUILLON = "brouillon"
    SOUMISE = "soumise"
    APPROUVEE = "approuvee"
    REJETEE = "rejetee"


class Requisition(Base):
    """Demande d'achat interne, soumise a approbation avant engagement."""
    __tablename__ = "purchase_requisitions"

    id = Column(Integer, primary_key=True, index=True)
    company_id = Column(Integer, ForeignKey('companies.id'), nullable=True, index=True)
    reference = Column(String(50), nullable=False, index=True)
    designation = Column(String(200), nullable=False)
    description = Column(Text)
    article_id = Column(Integer, ForeignKey('articles.id'), nullable=True)
    quantite = Column(Numeric, default=0)
    prix_estime = Column(Numeric)
    devise = Column(String(10), default="XAF")
    demandeur = Column(String(100))
    service = Column(String(100))
    urgence = Column(String(20), default="normale")  # normale / haute / critique
    statut = Column(Enum(RequisitionStatut), default=RequisitionStatut.BROUILLON)
    date_soumission = Column(DateTime(timezone=True))
    date_decision = Column(DateTime(timezone=True))
    approuve_par = Column(Integer, ForeignKey('users.id'))
    notes_approbation = Column(Text)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
