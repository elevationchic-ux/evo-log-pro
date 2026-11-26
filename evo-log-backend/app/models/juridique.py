"""Domaine juridique : contrats a valeur documentaire et contentieux.

Un contrat resilie ou un contentieux cloture est conserve, jamais efface :
ces pieces font foi devant une juridiction ou une administration CEMAC."""
from datetime import datetime

from sqlalchemy import (
    Boolean, Column, Date, DateTime, ForeignKey, Integer, Numeric,
    String, Text)
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from app.core.database import Base


class ContratJuridique(Base):
    """Contrat ou convention : bail, prestation, partenariat, concession."""
    __tablename__ = "juridique_contrats"

    id = Column(Integer, primary_key=True, index=True)
    company_id = Column(Integer, ForeignKey("companies.id"), nullable=False, index=True)
    reference = Column(String(60), nullable=False, index=True)
    type_contrat = Column(String(40), nullable=False, index=True)
 # bail / prestation / partenariat / concession / fourniture / autre
    objet = Column(Text, nullable=False)
    partie_adverse = Column(String(300), nullable=True)   # bailleur, client, prestataire...
    montant = Column(Numeric(18, 2), nullable=True)
    devise = Column(String(3), default="XAF")
    date_debut = Column(Date, nullable=False)
    date_fin = Column(Date, nullable=True)
    reconduction = Column(String(20), default="non")  # non / tacite / automatique
    preavis_jours = Column(Integer, default=0)
    statut = Column(String(20), default="actif", index=True)
 # brouillon / actif / resilie / expire / contentieux
    document_url = Column(String(500), nullable=True)
    document_hash = Column(String(128), nullable=True)  # empreinte tracabilite
    notes = Column(Text, nullable=True)
    is_active = Column(Boolean, default=True, nullable=True, index=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

 # Relationships
    contentieux = relationship("ContentieuxJuridique", back_populates="contrat")


class ContentieuxJuridique(Base):
    """Litige ou recouvrement rattache a un contrat (ou autonome)."""
    __tablename__ = "juridique_contentieux"

    id = Column(Integer, primary_key=True, index=True)
    company_id = Column(Integer, ForeignKey("companies.id"), nullable=False, index=True)
    reference = Column(String(60), nullable=False, index=True)
    contrat_id = Column(Integer, ForeignKey("juridique_contrats.id"), nullable=True, index=True)
    type_contentieux = Column(String(40), nullable=False, index=True)
 # recouvrement / litige_fournisseur / litige_client / sanction / autre
    description = Column(Text, nullable=False)
    montant_reclame = Column(Numeric(18, 2), nullable=True)
    montant_obtenu = Column(Numeric(18, 2), nullable=True)
    date_declaration = Column(Date, nullable=False)
    date_echeance = Column(Date, nullable=True)
    juridiction = Column(String(200), nullable=True)  # tribunal competent
    statut = Column(String(20), default="ouvert", index=True)
 # ouvert / en_cours / transaction / gagne / perdu / abandonne
    date_cloture = Column(Date, nullable=True)
    notes = Column(Text, nullable=True)
    is_active = Column(Boolean, default=True, nullable=True, index=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

 # Relationships
    contrat = relationship("ContratJuridique", back_populates="contentieux")
