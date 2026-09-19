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
    """Permission model for fine-grained access control"""
    __tablename__ = "permissions"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), unique=True, nullable=False)
    description = Column(Text)
    resource = Column(String(50))  # e.g., "users", "missions", "factures"
    action = Column(String(50))    # e.g., "create", "read", "update", "delete"
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # Relationships
    roles = relationship("Role", secondary=role_permissions, back_populates="permissions")


# Backward compatibility aliases for Kamlog modules
RoleModel = Role
PermissionModel = Permission