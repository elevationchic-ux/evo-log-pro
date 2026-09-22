from fastapi import HTTPException, status, Depends, Request
from sqlalchemy.orm import Session
from typing import Optional, List
from app.database import get_db
from app.models.organization import Organization
from app.models.user import User
from app.utils.rbac import get_current_user

class TenantContext:
    def __init__(self, organization: Optional[Organization], user: User):
        self.organization = organization
        self.organization_id = organization.id if organization else None
        self.user = user

async def get_current_tenant_context(
    request: Request,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
) -> TenantContext:
    """
    Extract and validate current tenant organization context.
    Superadmins can override tenant via X-Organization-ID header.
    """
    header_tenant_id = request.headers.get("X-Organization-ID")
    
    if current_user.is_superadmin and header_tenant_id:
        try:
            tenant_id = int(header_tenant_id)
            org = db.query(Organization).filter(Organization.id == tenant_id).first()
            if not org:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail=f"Organization #{tenant_id} not found"
                )
            return TenantContext(organization=org, user=current_user)
        except ValueError:
            pass

    # Standard user: use user's assigned organization
    if not current_user.organization_id:
        if current_user.is_superadmin:
            # Superadmin without explicit organization header context
            return TenantContext(organization=None, user=current_user)
        
        # Fallback to default or first active organization for dev/legacy compatibility
        default_org = db.query(Organization).filter(Organization.is_active == True).first()
        if default_org:
            current_user.organization_id = default_org.id
            db.commit()
            return TenantContext(organization=default_org, user=current_user)

        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="User is not associated with an active Organization tenant."
        )

    org = db.query(Organization).filter(Organization.id == current_user.organization_id).first()
    if not org or not org.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Organization account is suspended or inactive."
        )

    return TenantContext(organization=org, user=current_user)

def require_module_access(module_name: str):
    """
    Dependency verifying double-layer access control:
    Layer 1: Enabled for the Organization tenant by SuperAdmin
    Layer 2: Permitted for the User via RBAC / modules_allowed
    """
    async def _verify(context: TenantContext = Depends(get_current_tenant_context)):
        user = context.user
        org = context.organization

        if user.is_superadmin:
            return context

        # Layer 1 Check (Organization Level)
        if org and org.allowed_modules is not None:
            if module_name not in org.allowed_modules and "*" not in org.allowed_modules:
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail=f"Module '{module_name}' is not enabled for your Organization subscription plan."
                )

        # Layer 2 Check (User RBAC Level)
        user_modules = user.modules_allowed or []
        if "*" in user_modules or module_name in user_modules:
            return context

        # Check user roles
        role_modules = []
        for role in (user.roles or []):
            if role.modules_allowed:
                role_modules.extend(role.modules_allowed)
        
        if "*" in role_modules or module_name in role_modules:
            return context

        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=f"Access denied to module '{module_name}' for current user permissions."
        )

    return _verify
