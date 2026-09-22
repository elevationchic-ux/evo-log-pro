"""
Models ORM SQLAlchemy pour le système RBAC multi-tenant EVO-LOG SaaS.
Hiérarchie : SuperAdmin → Admin → Manager → Superviseur → Opérateur → Chauffeur
"""
from sqlalchemy import Column, Integer, String, Boolean, DateTime, ForeignKey, Text, Enum as SAEnum
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.core.database import Base
import enum


class TenantPlan(str, enum.Enum):
    STARTER = "STARTER"
    PROFESSIONNEL = "PROFESSIONNEL"
    ENTERPRISE = "ENTERPRISE"
    CUSTOM = "CUSTOM"


class UserRoleLevel(str, enum.Enum):
    SUPER_ADMIN = "SUPER_ADMIN"       # Accès total multi-tenant (EVO-LOG interne)
    ADMIN = "ADMIN"                   # Accès total à son tenant
    MANAGER = "MANAGER"               # Accès à ses modules assignés + reporting
    SUPERVISEUR = "SUPERVISEUR"       # Validation des opérations
    OPERATEUR = "OPERATEUR"           # Saisie et consultation
    CHAUFFEUR = "CHAUFFEUR"           # Mobile uniquement : missions, e-POD
    CLIENT_B2B = "CLIENT_B2B"         # Portail B2B : lecture seule suivi dossier


class Tenant(Base):
    """Organisation cliente du SaaS EVO-LOG"""
    __tablename__ = "tenants"

    id = Column(Integer, primary_key=True, index=True)
    code = Column(String(20), unique=True, nullable=False, index=True)
    nom_entreprise = Column(String(200), nullable=False)
    pays = Column(String(100), default="Cameroun")
    ville = Column(String(100))
    telephone = Column(String(50))
    email_contact = Column(String(200))
    plan = Column(SAEnum(TenantPlan), default=TenantPlan.PROFESSIONNEL)
    modules_actives = Column(Text, default="transport,magasin,finance,comptabilite")
    nb_utilisateurs_max = Column(Integer, default=20)
    date_debut_abonnement = Column(DateTime, server_default=func.now())
    date_fin_abonnement = Column(DateTime)
    actif = Column(Boolean, default=True)
    created_at = Column(DateTime, server_default=func.now())

    users = relationship("User", back_populates="tenant")
    roles = relationship("Role", back_populates="tenant")


class Permission(Base):
    """Permission atomique : module + action"""
    __tablename__ = "permissions"
    __table_args__ = {'extend_existing': True}

    id = Column(Integer, primary_key=True, index=True)
    code = Column(String(100), unique=True, nullable=False)  # ex: "transport.mission.create"
    module = Column(String(50), nullable=False)              # ex: "transport"
    action = Column(String(50), nullable=False)              # ex: "create", "read", "update", "delete", "validate"
    description = Column(String(300))


class Role(Base):
    """Rôle personnalisé au niveau tenant"""
    __tablename__ = "roles"
    __table_args__ = {'extend_existing': True}

    id = Column(Integer, primary_key=True, index=True)

    tenant_id = Column(Integer, ForeignKey("tenants.id"), nullable=True)
    nom = Column(String(100), nullable=False)
    niveau = Column(SAEnum(UserRoleLevel), default=UserRoleLevel.OPERATEUR)
    description = Column(String(300))
    permissions_json = Column(Text, default="[]")  # JSON liste des codes permission
    actif = Column(Boolean, default=True)

    tenant = relationship("Tenant", back_populates="roles")


class UserRoleAssignment(Base):
    """Assignation utilisateur → rôle dans un tenant"""
    __tablename__ = "user_role_assignments"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    role_id = Column(Integer, ForeignKey("roles.id"), nullable=False)
    tenant_id = Column(Integer, ForeignKey("tenants.id"), nullable=False)
    modules_restreints = Column(Text, default="[]")  # Modules supplémentaires restreints pour cet user
    actif = Column(Boolean, default=True)
    assigned_at = Column(DateTime, server_default=func.now())
    assigned_by = Column(Integer, ForeignKey("users.id"), nullable=True)
