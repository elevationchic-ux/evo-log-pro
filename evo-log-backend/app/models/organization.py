from sqlalchemy import Column, Integer, String, Boolean, DateTime, JSON, Text
from sqlalchemy.orm import relationship
from datetime import datetime
from app.models.base import Base

class Organization(Base):
    __tablename__ = "organizations"

    id = Column(Integer, primary_key=True, index=True)
    code = Column(String(50), unique=True, index=True, nullable=False)
    name = Column(String(150), nullable=False)
    slug = Column(String(100), unique=True, index=True, nullable=False)
    plan = Column(String(50), default="FREE_TRIAL", nullable=False)  # FREE_TRIAL, STARTER, BUSINESS, ENTERPRISE
    status = Column(String(50), default="ACTIVE", nullable=False)   # ACTIVE, SUSPENDED, EXPIRED, PENDING
    subscription_expires_at = Column(DateTime, nullable=True)
    max_users = Column(Integer, default=10, nullable=False)
    allowed_modules = Column(JSON, nullable=True, default=[
        "transport", "magasin", "finance", "parc", "master-data", "qhse", 
        "documents", "acconage", "maintenance", "fuelguard", "cotations", 
        "douane", "rh", "procurement", "bi", "collaboration", "sectoral"
    ])
    tenant_config = Column(JSON, nullable=True, default={
        "warehouse_management_mode": "ZONES",  # SIMPLE, ZONES, RACK_LEVEL_BIN
        "document_numbering_prefix": "EVO-INV-",
        "logo_url": None,
        "primary_color": "#4f46e5",
        "legal_name": None,
        "tax_id": None,
        "address": None,
        "city": "Douala",
        "country": "Cameroun",
        "currency": "XAF",
        "payment_terms_days": 30,
        "allow_offline_mode": True
    })
    is_active = Column(Boolean, default=True, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    agencies = relationship("Agency", back_populates="organization", cascade="all, delete-orphan")
    users = relationship("User", back_populates="organization", cascade="all, delete-orphan")
