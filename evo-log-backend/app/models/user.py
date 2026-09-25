"""
User and authentication models
"""
from sqlalchemy import Column, Integer, String, Boolean, DateTime, ForeignKey, Table, Text
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.core.database import Base

# Many-to-many relationship between users and roles
user_roles = Table(
    'user_roles',
    Base.metadata,
    Column('user_id', Integer, ForeignKey('users.id'), primary_key=True),
    Column('role_id', Integer, ForeignKey('roles.id'), primary_key=True)
)

# Many-to-many relationship between roles and permissions
role_permissions = Table(
    'role_permissions',
    Base.metadata,
    Column('role_id', Integer, ForeignKey('roles.id'), primary_key=True),
    Column('permission_id', Integer, ForeignKey('permissions.id'), primary_key=True)
)


class User(Base):
    """User model for authentication and authorization"""
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True, index=True)
    username = Column(String(50), unique=True, index=True, nullable=False)
    email = Column(String(100), unique=True, index=True, nullable=False)
    hashed_password = Column(String(255), nullable=False)
    full_name = Column(String(100))
    is_active = Column(Boolean, default=True)
    is_superuser = Column(Boolean, default=False)
    agency_id = Column(Integer, ForeignKey('agencies.id'))
    phone = Column(String(20))
    must_change_password = Column(Boolean, default=True)
    password_changed_at = Column(DateTime(timezone=True))
    
    # Multi-tenant fields
    company_id = Column(Integer, ForeignKey('companies.id'))
    organization_id = Column(Integer, ForeignKey('organizations.id'), nullable=True)
    department_id = Column(Integer, ForeignKey('departments.id'))
    role_level = Column(Integer, default=3)  # 0=SuperAdmin, 1=AdminEntreprise, 2=ChefDept, 3=User
    is_b2b = Column(Boolean, default=False)  # B2B portal user
    b2b_portal_id = Column(Integer, ForeignKey('b2b_portals.id'))
    
    # Profile
    avatar_url = Column(String(255))
    bio = Column(Text)
    language = Column(String(10), default="fr")
    timezone = Column(String(50), default="Africa/Douala")
    
    # Security
    last_login = Column(DateTime(timezone=True))
    failed_login_attempts = Column(Integer, default=0)
    locked_until = Column(DateTime(timezone=True))
    # Authentification a deux facteurs (TOTP / RFC 6238)
    two_factor_enabled = Column(Boolean, default=False, nullable=False)
    two_factor_secret = Column(String(64))  # secret base32, jamais expose en clair
    two_factor_confirmed_at = Column(DateTime(timezone=True))
    
    # Metadata
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    created_by = Column(Integer)  # User who created this user
    
    # Relationships
    roles = relationship("Role", secondary=user_roles, back_populates="users")
    company = relationship("Company", back_populates="users")
    department = relationship("Department", back_populates="users", foreign_keys=[department_id])
    b2b_portal = relationship("B2BPortal")
    agency = relationship("Agency", back_populates="users")
    organization = relationship("Organization", back_populates="users")
    accreditations = relationship(
        "Accreditation",
        foreign_keys="Accreditation.user_id",
        back_populates="user",
        cascade="all, delete-orphan",
    )
    # audit_logs = relationship("AuditLog", back_populates="user")


class Role(Base):
    """Role model for RBAC"""
    __tablename__ = "roles"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(50), unique=True, nullable=False)
    description = Column(Text)
    level = Column(Integer, default=3)  # 0=SuperAdmin, 1=AdminEntreprise, 2=ChefDept, 3=User
    company_id = Column(Integer, ForeignKey('companies.id'))  # NULL for system-wide roles
    modules_allowed = Column(Text)  # JSON string of allowed modules
    is_active = Column(Boolean, default=True)
    is_system = Column(Boolean, default=False)  # System roles cannot be deleted
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relationships
    users = relationship("User", secondary=user_roles, back_populates="roles")
    permissions = relationship("Permission", secondary=role_permissions, back_populates="roles")


class Permission(Base):
    """Permission atomique : ``module.sous_module.action``.

    ``code`` est la representation canonique exploitee par le moteur
    d'autorisation :mod:`app.core.permissions`. Exemples :

        "comptabilite.journal.read"   action lecture sur le sous-module journal
        "comptabilite.*.read"         lecture de tous les sous-modules du module
        "*"                           wildcard total (reserve SuperAdmin)

    Les colonnes ``domaine`` / ``module`` / ``sub_module`` / ``action`` sont
    derivees du ``code`` pour construire l'arborescence du catalogue cote UI.
    ``resource`` est conserve par compatibilite historique (= ``sub_module``).
    """
    __tablename__ = "permissions"

    id = Column(Integer, primary_key=True, index=True)
    code = Column(String(150), unique=True, index=True, nullable=False)
    name = Column(String(150), unique=True, nullable=False)  # = code (retro-compat)
    description = Column(Text)
    domaine = Column(String(50), index=True)     # ex: "finance"
    module = Column(String(50), index=True)       # ex: "comptabilite"
    sub_module = Column(String(80))               # ex: "journal" ou "*"
    action = Column(String(50))                   # ex: "read" / "create" / "*"
    resource = Column(String(50))                 # alias legacy de sub_module
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    # Relationships
    roles = relationship("Role", secondary=role_permissions, back_populates="permissions")

    @staticmethod
    def parse_code(code: str):
        """Decompose un ``code`` en (domaine=None, module, sub_module, action).

        Le domaine n'est pas portee par le code ; il est resolve par le
        catalogue. Retourne (module, sub_module, action) avec tolerances pour
        les codes partiels de type ``module`` ou ``module.*``.
        """
        parts = (code or "").split(".")
        module = parts[0] if len(parts) > 0 else "*"
        sub_module = parts[1] if len(parts) > 1 else "*"
        action = parts[2] if len(parts) > 2 else "*"
        return module, sub_module, action


# Backward compatibility aliases for Kamlog modules
RoleModel = Role
PermissionModel = Permission