"""Role management service - Hierarchical RBAC for multi-tenant SAAS"""
from datetime import datetime
from typing import List, Optional
from sqlalchemy.orm import Session
from app.models.user import Role
from app.models.tenant import Company


class RoleService:
    """Role management service"""
    
    @staticmethod
    def creer_role(
        db: Session,
        name: str,
        description: str,
        level: int,
        company_id: Optional[int],
        modules_allowed: List[str]
    ) -> Role:
        """Create a role"""
        import json
        
        role = Role(
            name=name,
            description=description,
            level=level,
            company_id=company_id,
            modules_allowed=json.dumps(modules_allowed),
            is_active=True,
            is_system=False
        )
        db.add(role)
        db.commit()
        db.refresh(role)
        return role
    
    @staticmethod
    def creer_role_systeme(
        db: Session,
        name: str,
        description: str,
        level: int,
        modules_allowed: List[str]
    ) -> Role:
        """Create a system role (cannot be deleted)"""
        import json
        
        role = Role(
            name=name,
            description=description,
            level=level,
            company_id=None,  # System roles are not company-specific
            modules_allowed=json.dumps(modules_allowed),
            is_active=True,
            is_system=True
        )
        db.add(role)
        db.commit()
        db.refresh(role)
        return role
    
    @staticmethod
    def initialiser_roles_systeme(db: Session):
        """Initialize system-wide predefined roles"""
        # Super Admin - Level 0
        RoleService.creer_role_systeme(
            db=db,
            name="SUPER_ADMIN",
            description="Super Administrateur de la plateforme - Accès complet",
            level=0,
            modules_allowed=[
                "admin", "companies", "subscriptions", "users", "roles",
                "acconage", "transit", "magasin", "transport", "acquisition",
                "finance", "qhse", "documents", "maintenance", "integration",
                "notifications", "reporting", "tenant"
            ]
        )
        
        # Admin Entreprise - Level 1
        RoleService.creer_role_systeme(
            db=db,
            name="ADMIN_ENTREPRISE",
            description="Administrateur d'entreprise - Gère son entreprise",
            level=1,
            modules_allowed=[
                "users", "departments", "roles", "company_settings",
                "acconage", "transit", "magasin", "transport", "acquisition",
                "finance", "qhse", "documents", "maintenance", "integration",
                "notifications", "reporting"
            ]
        )
        
        # Chef Département - Level 2
        RoleService.creer_role_systeme(
            db=db,
            name="CHEF_DEPARTEMENT",
            description="Chef de département - Gère son département",
            level=2,
            modules_allowed=[
                "users", "department_users", "kpis"
            ]
        )
        
        # User Standard - Level 3
        RoleService.creer_role_systeme(
            db=db,
            name="USER_STANDARD",
            description="Utilisateur standard - Accès aux modules autorisés",
            level=3,
            modules_allowed=[]
        )
        
        # Existing role names (mapped to system roles)
        existing_roles = [
            ("ADMIN", "Administrateur système", 0),
            ("MAGASINIER", "Opérateur magasin", 3),
            ("DISPATCHER", "Dispatcher transport", 3),
            ("QHSE", "Officier QHSE", 3),
            ("FINANCIER", "Comptable", 3),
            ("DOUANE", "Agent douane", 3),
            ("PARC", "Gestionnaire parc", 3),
            ("AUDITOR", "Auditeur", 3)
        ]
        
        for role_name, description, level in existing_roles:
            existing = db.query(Role).filter(Role.name == role_name).first()
            if not existing:
                RoleService.creer_role_systeme(
                    db=db,
                    name=role_name,
                    description=description,
                    level=level,
                    modules_allowed=[]
                )
    
    @staticmethod
    def creer_role_entreprise(
        db: Session,
        company_id: int,
        name: str,
        description: str,
        level: int,
        modules_allowed: List[str]
    ) -> Role:
        """Create a company-specific role"""
        import json
        
        role = Role(
            name=name,
            description=description,
            level=level,
            company_id=company_id,
            modules_allowed=json.dumps(modules_allowed),
            is_active=True,
            is_system=False
        )
        db.add(role)
        db.commit()
        db.refresh(role)
        return role
    
    @staticmethod
    def assigner_role_user(db: Session, user_id: int, role_id: int):
        """Assign role to user"""
        from app.models.user import user_roles
        
        # Check if already assigned
        existing = db.query(user_roles).filter(
            user_roles.c.user_id == user_id,
            user_roles.c.role_id == role_id
        ).first()
        
        if not existing:
            db.execute(
                user_roles.insert().values(user_id=user_id, role_id=role_id)
            )
            db.commit()
    
    @staticmethod
    def retirer_role_user(db: Session, user_id: int, role_id: int):
        """Remove role from user"""
        from app.models.user import user_roles
        
        db.execute(
            user_roles.delete().where(
                (user_roles.c.user_id == user_id) &
                (user_roles.c.role_id == role_id)
            )
        )
        db.commit()
    
    @staticmethod
    def mettre_a_jour_modules_role(db: Session, role_id: int, modules_allowed: List[str]):
        """Update allowed modules for a role"""
        import json
        
        role = db.query(Role).filter(Role.id == role_id).first()
        if not role:
            raise ValueError("Role non trouvé")
        
        role.modules_allowed = json.dumps(modules_allowed)
        db.commit()
        db.refresh(role)
        return role
