from sqlalchemy import Column, Integer, String, Float, DateTime, ForeignKey, Text, Boolean, JSON
from sqlalchemy.orm import relationship
from datetime import datetime
from app.models.base import Base

class CotationDevis(Base):
    __tablename__ = "cotations_devis"

    id = Column(Integer, primary_key=True, autoincrement=True, index=True)
    reference = Column(String(50), unique=True, index=True, nullable=False)
    client_nom = Column(String(150), nullable=False)
    origine = Column(String(100), nullable=False)
    destination = Column(String(100), nullable=False)
    nature_fret = Column(String(100), nullable=False)
    montant_estime_xaf = Column(Float, nullable=False)
    marge_nette_pct = Column(Float, default=15.0)
    statut = Column(String(50), default="SOUMIS") # SOUMIS, ACCEPTE, REJETE
    created_at = Column(DateTime, default=datetime.utcnow)

class ElectronicPOD(Base):
    __tablename__ = "electronic_pods"

    id = Column(Integer, primary_key=True, index=True)
    reference_mission = Column(String(50), index=True, nullable=False)
    nom_destinataire = Column(String(150), nullable=False)
    signature_url = Column(String(255), nullable=True)
    photo_livraison_url = Column(String(255), nullable=True)
    longitude = Column(Float, nullable=True)
    latitude = Column(Float, nullable=True)
    statut = Column(String(50), default="LIVRE_AVEC_SIGNATURE")
    timestamp = Column(DateTime, default=datetime.utcnow)

class FuelTankSensor(Base):
    __tablename__ = "fuel_tank_sensors"

    id = Column(Integer, primary_key=True, index=True)
    immatriculation_camion = Column(String(50), index=True, nullable=False)
    niveau_actuel_litres = Column(Float, nullable=False)
    capacite_totale_litres = Column(Float, default=400.0)
    alerte_vol_detectee = Column(Boolean, default=False)
    derniere_station = Column(String(100), default="TotalEnergies Douala Port")
    updated_at = Column(DateTime, default=datetime.utcnow)

class PurchaseOrder(Base):
    __tablename__ = "procurement_purchase_orders"

    id = Column(Integer, primary_key=True, index=True)
    numero_po = Column(String(50), unique=True, index=True, nullable=False)
    fournisseur = Column(String(150), nullable=False)
    description = Column(Text, nullable=False)
    montant_total_xaf = Column(Float, nullable=False)
    match_3_voies = Column(Boolean, default=True)
    statut = Column(String(50), default="APPROUVE") # EN_ATTENTE, APPROUVE, RECEPTIONNE
    created_at = Column(DateTime, default=datetime.utcnow)

class ComplianceAudit(Base):
    __tablename__ = "compliance_audits"

    id = Column(Integer, primary_key=True, index=True)
    dossier_reference = Column(String(50), index=True, nullable=False)
    type_reglementation = Column(String(100), default="ZLECAF / CEMAC")
    score_conformite_pct = Column(Float, default=98.5)
    exemption_valide = Column(Boolean, default=True)
    statut = Column(String(50), default="VALIDE")
    created_at = Column(DateTime, default=datetime.utcnow)
