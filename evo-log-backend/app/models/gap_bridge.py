"""
Modeles legers ajoutes pour combler les endpoints reclames par le frontend
mais sans table dediee jusque-la. Aucun donnes factices : ces tables ne sont
remplies que par des ecritures reelles issues des ecrans de parametres.
"""
from sqlalchemy import Column, Integer, String, Numeric, Boolean, DateTime, ForeignKey, JSON, func
from app.core.database import Base


class SystemSetting(Base):
    """Preference cle/valeur par entreprise (profil global, config systeme)."""
    __tablename__ = "system_settings"

    id = Column(Integer, primary_key=True, index=True)
    company_id = Column(Integer, ForeignKey("companies.id"), nullable=True, index=True)
    key = Column(String(100), nullable=False, index=True)
    value = Column(JSON, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())


class Tarif(Base):
    """Grille tarifaire commerciale (finance). Ligne persistante reelle."""
    __tablename__ = "tarifs"

    id = Column(Integer, primary_key=True, index=True)
    company_id = Column(Integer, ForeignKey("companies.id"), nullable=True, index=True)
    code = Column(String(50), nullable=False, index=True)
    designation = Column(String(255), nullable=False)
    categorie = Column(String(100), nullable=True)
    unite = Column(String(30), nullable=True)
    prix = Column(Numeric(15, 2), nullable=False, default=0)
    devise = Column(String(10), default="XAF")
    tva = Column(Numeric(5, 2), default=0)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())


class RegistreEntry(Base):
    """Ligne de registre generique par module (inspections QHSE, bordereaux
    BSDD, fiches ISPS, elements de conformite...). Persiste depuis les formulaires
    reels des ecrans ; aucune donnee inventee."""
    __tablename__ = "registre_entries"

    id = Column(Integer, primary_key=True, index=True)
    company_id = Column(Integer, ForeignKey("companies.id"), nullable=True, index=True)
    registry = Column(String(60), nullable=False, index=True)
    reference = Column(String(60), nullable=True, index=True)
    statut = Column(String(40), nullable=True)
    payload = Column(JSON, nullable=True)
    created_by = Column(String(120), nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
