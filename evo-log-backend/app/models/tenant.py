"""Multi-tenant models for SAAS architecture - Company, Subscription, B2B Portal"""
from sqlalchemy import Column, Integer, String, Text, DateTime, Boolean, ForeignKey, Enum, Date, Float, Numeric
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
import enum
from app.core.database import Base


class SubscriptionPlanType(str, enum.Enum):
    """Subscription plan types"""
    STARTER = "starter"
    PRO = "pro"
    ENTERPRISE = "enterprise"
    CUSTOM = "custom"


class SubscriptionStatus(str, enum.Enum):
    """Subscription status"""
    ACTIVE = "active"
    TRIAL = "trial"
    PAST_DUE = "past_due"
    CANCELLED = "cancelled"
    EXPIRED = "expired"


class Company(Base):
    """Company/Tenant model for multi-tenant SAAS"""
    __tablename__ = "companies"
    
    id = Column(Integer, primary_key=True, index=True)
    code = Column(String(50), unique=True, nullable=False, index=True)
    nom = Column(String(200), nullable=False)
    sigle = Column(String(50))  # Sigle / Abréviation
    legal_form = Column(String(50))  # SARL, SA, SAS, etc.
    capital_social = Column(String(100))  # Ex: "100 000 000 FCFA"
    tax_id = Column(String(50))  # NIF (Numéro d'Identification Fiscale)
    rccm = Column(String(100))  # Registre du Commerce et du Crédit Mobilier
    agrement_douane = Column(String(100))  # Agrément Douane DGD
    agrement_pad = Column(String(100))   # Agrément Port Autonome de Douala
    agrement_pak = Column(String(100))   # Agrément Port Autonome de Kribi
    rib = Column(String(150))  # Relevé d'Identité Bancaire
    adresse = Column(Text)
    ville = Column(String(100))
    pays = Column(String(50), default="Cameroun")
    telephone = Column(String(20))
    email = Column(String(100))
    website = Column(String(255))
    logo_url = Column(String(500))
    is_active = Column(Boolean, default=True)
    is_verified = Column(Boolean, default=False)
    verification_date = Column(DateTime(timezone=True))
    suspension_reason = Column(Text)

    # Subscription
    subscription_plan_id = Column(Integer, ForeignKey('subscription_plans.id'))
    subscription_start = Column(Date)
    subscription_end = Column(Date)

    # Quotas
    max_users = Column(Integer, default=10)
    max_storage_mb = Column(Integer, default=1024)
    max_apis_per_day = Column(Integer, default=1000)
    max_camions = Column(Integer, default=20)  # Max véhicules dans le parc

    # Usage tracking
    current_users = Column(Integer, default=0)
    current_storage_mb = Column(Integer, default=0)
    current_apis_today = Column(Integer, default=0)
    last_api_reset = Column(Date)

    # B2B Portal
    subdomain = Column(String(100), unique=True, nullable=True)
    custom_domain = Column(String(100), unique=True, nullable=True)

    # Branding
    primary_color = Column(String(7), default="#3B82F6")
    secondary_color = Column(String(7), default="#10B981")
    banner_url = Column(String(500))

    # Module feature flags (JSON array stored as Text)
    modules_actives = Column(Text, default='["transport","magasin","finance","qhse"]')

    # Metadata
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    created_by = Column(Integer)  # Super Admin who created
    
    # Relationships
    subscription_plan = relationship("SubscriptionPlan", back_populates="companies")
    users = relationship("User", back_populates="company")
    departments = relationship("Department", back_populates="company")
    b2b_portal = relationship("B2BPortal", back_populates="company", uselist=False)


class SubscriptionPlan(Base):
    """Subscription plan model"""
    __tablename__ = "subscription_plans"
    
    id = Column(Integer, primary_key=True, index=True)
    code = Column(String(50), unique=True, nullable=False, index=True)
    nom = Column(String(100), nullable=False)
    type_plan = Column(Enum(SubscriptionPlanType), nullable=False)
    description = Column(Text)
    
    # Pricing
    prix_mensuel = Column(Numeric, default=0.0)
    prix_annuel = Column(Numeric, default=0.0)
    devise = Column(String(3), default="XAF")
    
    # Features
    features = Column(Text)  # JSON string of features
    modules_inclus = Column(Text)  # JSON array of module names
    
    # Limits
    max_users = Column(Integer, default=10)
    max_storage_mb = Column(Integer, default=1024)
    max_apis_per_day = Column(Integer, default=1000)
    max_companies = Column(Integer, default=1)  # For reseller plans
    
    # Trial
    trial_days = Column(Integer, default=14)
    
    # Metadata
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relationships
    companies = relationship("Company", back_populates="subscription_plan")


class Subscription(Base):
    """Subscription model for tracking company subscriptions"""
    __tablename__ = "subscriptions"
    
    id = Column(Integer, primary_key=True, index=True)
    company_id = Column(Integer, ForeignKey('companies.id'), nullable=False)
    plan_id = Column(Integer, ForeignKey('subscription_plans.id'), nullable=False)
    
    # Dates
    start_date = Column(Date, nullable=False)
    end_date = Column(Date, nullable=False)
    trial_end_date = Column(Date)
    
    # Status
    status = Column(Enum(SubscriptionStatus), default=SubscriptionStatus.TRIAL)
    
    # Payment
    amount = Column(Numeric)
    currency = Column(String(3), default="XAF")
    payment_method = Column(String(50))  # card, bank_transfer, mobile_money
    payment_reference = Column(String(100))
    
    # Auto-renewal
    auto_renew = Column(Boolean, default=True)
    
    # Metadata
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relationships
    company = relationship("Company")
    plan = relationship("SubscriptionPlan")


class Department(Base):
    """Department model for hierarchical organization within companies"""
    __tablename__ = "departments"
    
    id = Column(Integer, primary_key=True, index=True)
    company_id = Column(Integer, ForeignKey('companies.id'), nullable=False)
    code = Column(String(50), nullable=False)
    nom = Column(String(100), nullable=False)
    description = Column(Text)
    
    # Hierarchy
    parent_id = Column(Integer, ForeignKey('departments.id'))
    # use_alter: users.department_id -> departments.id cree un cycle FK
    # users<->departments. Sans ALTER TABLE differe, le tri topologique de
    # create_all est corrompu et la creation en cascade echoue sur Postgres
    # ("relation users does not exist"). La contrainte est ajoutee apres
    # creation des deux tables.
    manager_id = Column(Integer, ForeignKey('users.id', use_alter=True, name='fk_departments_manager_id_users'))
    
    # Modules authorized for this department
    modules_allowed = Column(Text)  # JSON string
    
    # Metadata
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relationships
    company = relationship("Company", back_populates="departments")
    parent = relationship("Department", remote_side=[id])
    manager = relationship("User", foreign_keys=[manager_id])
    users = relationship("User", back_populates="department", foreign_keys="[User.department_id]")
    children = relationship("Department", back_populates="parent")


class B2BPortal(Base):
    """B2B Portal configuration for personalized client portals"""
    __tablename__ = "b2b_portals"
    
    id = Column(Integer, primary_key=True, index=True)
    company_id = Column(Integer, ForeignKey('companies.id'), nullable=False, unique=True)
    
    # Domain configuration
    subdomain = Column(String(100), unique=True, nullable=True)  # ex: client1.evolog.cm
    custom_domain = Column(String(100), unique=True, nullable=True)  # ex: client1.logistics.cm
    
    # Branding
    primary_color = Column(String(7), default="#3B82F6")
    secondary_color = Column(String(7), default="#10B981")
    accent_color = Column(String(7), default="#F59E0B")
    background_color = Column(String(7), default="#FFFFFF")
    text_color = Column(String(7), default="#1F2937")
    
    # Assets
    logo_url = Column(String(255))
    banner_url = Column(String(255))
    favicon_url = Column(String(255))
    
    # Configuration
    custom_css = Column(Text)
    custom_js = Column(Text)
    
    # Features
    enable_chat = Column(Boolean, default=True)
    enable_quotes = Column(Boolean, default=True)
    enable_tracking = Column(Boolean, default=True)
    enable_api = Column(Boolean, default=False)
    
    # Email customization
    email_from_name = Column(String(100))
    email_from_address = Column(String(100))
    email_signature = Column(Text)
    
    # Metadata
    is_active = Column(Boolean, default=True)
    published_at = Column(DateTime(timezone=True))
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relationships
    company = relationship("Company", back_populates="b2b_portal")


class TenantAuditLog(Base):
    """Audit log for tenant-level operations"""
    __tablename__ = "tenant_audit_logs"
    
    id = Column(Integer, primary_key=True, index=True)
    company_id = Column(Integer, ForeignKey('companies.id'))
    user_id = Column(Integer, ForeignKey('users.id'))
    
    action = Column(String(100), nullable=False)  # create_company, add_user, etc.
    entity_type = Column(String(50))  # company, user, subscription
    entity_id = Column(Integer)
    
    old_values = Column(Text)  # JSON string
    new_values = Column(Text)  # JSON string
    
    ip_address = Column(String(50))
    user_agent = Column(String(255))
    
    created_at = Column(DateTime(timezone=True), server_default=func.now())
