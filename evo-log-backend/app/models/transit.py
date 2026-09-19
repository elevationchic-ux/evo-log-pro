"""
Transit models for customs and transit operations
"""
from sqlalchemy import Column, Integer, String, Text, DateTime, Boolean, Float, ForeignKey, Enum, Numeric
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
import enum
from app.core.database import Base


class DossierTransitStatus(str, enum.Enum):
    """Enumeration for transit dossier status"""
    OUVERT = "ouvert"
    EN_COURS = "en_cours"
    EN_DOUANE = "en_douane"
    DELIVRE = "delivre"
    CLOTURE = "cloture"
    ANNULE = "annule"


class DossierTransit(Base):
    """Transit dossier model"""
    __tablename__ = "dossiers_transit"
    
    id = Column(Integer, primary_key=True, index=True)
    numero_dossier = Column(String(50), unique=True, nullable=False, index=True)
    client_id = Column(Integer, ForeignKey('clients.id'))
    transitaire_id = Column(Integer, ForeignKey('partenaires.id'))
    type_transit = Column(String(50))  # e.g., "import", "export", "transit"
    statut = Column(Enum(DossierTransitStatus), default=DossierTransitStatus.OUVERT)
    date_ouverture = Column(DateTime(timezone=True), server_default=func.now())
    date_cloture = Column(DateTime(timezone=True))
    marchandise = Column(Text)
    valeur_marchandise = Column(Numeric)
    poids_brut = Column(Numeric)
    poids_net = Column(Numeric)
    nombre_colis = Column(Integer)
    origine = Column(String(100))
    destination = Column(String(100))
    moyen_transport = Column(String(50))
    numero_connaisse = Column(String(50))
    taux_change = Column(Numeric, default=1.0)
    montant_frais = Column(Numeric)
    montant_droits = Column(Numeric)
    montant_tva = Column(Numeric)
    montant_total = Column(Numeric)
    notes = Column(Text)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relationships
    declarations = relationship("DeclarationDouaniere", back_populates="dossier")


class DeclarationDouaniere(Base):
    """Customs declaration model - SYDONIA+ integration"""
    __tablename__ = "declarations_douanieres"
    
    id = Column(Integer, primary_key=True, index=True)
    numero_declaration = Column(String(50), unique=True, nullable=False, index=True)
    dossier_transit_id = Column(Integer, ForeignKey('dossiers_transit.id'))
    regime_douanier = Column(String(50))  # e.g., "TIR", "TSD", "MISE A LA CONSOMMATION"
    bureau_douane = Column(String(100))
    date_enregistrement = Column(DateTime(timezone=True))
    date_validation = Column(DateTime(timezone=True))
    date_acquittement = Column(DateTime(timezone=True))
    valeur_declaree = Column(Numeric)
    poids_declare = Column(Numeric)
    taux_droit = Column(Numeric)
    montant_droit = Column(Numeric)
    taux_tva = Column(Numeric)
    montant_tva = Column(Numeric)
    autres_taxes = Column(Numeric)
    total_taxes = Column(Numeric)
    numero_b7 = Column(String(50))
    numero_quitus = Column(String(50))
    statut = Column(String(20), default="brouillon")
    notes = Column(Text)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relationships
    dossier = relationship("DossierTransit", back_populates="declarations")