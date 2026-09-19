"""Tenant middleware for multi-tenant SAAS - Isolation and tenant context"""
from fastapi import Request, HTTPException, status
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.responses import JSONResponse
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.models.tenant import Company
from app.models.user import User


class TenantMiddleware(BaseHTTPMiddleware):
    """Middleware to inject tenant context into requests"""
    
    async def dispatch(self, request: Request, call_next):
        # Extract tenant from subdomain or header
        tenant_id = None
        
        # Try X-Tenant-ID header first
        tenant_id = request.headers.get("X-Tenant-ID")
        
        # If not in header, try to extract from subdomain
        if not tenant_id:
            host = request.headers.get("host", "")
            if "." in host:
                subdomain = host.split(".")[0]
                # Look up company by subdomain
                try:
                    db = next(get_db())
                    company = db.query(Company).filter(
                        Company.subdomain == subdomain,
                        Company.is_active == True
                    ).first()
                    if company:
                        tenant_id = str(company.id)
                    db.close()
                except Exception:
                    pass
        
        # Inject tenant into request state
        if tenant_id:
            request.state.tenant_id = tenant_id
            request.state.company_id = int(tenant_id)
        else:
            # Super Admin doesn't need tenant context
            request.state.tenant_id = None
            request.state.company_id = None
        
        response = await call_next(request)
        return response


class TenantQueryFilter:
    """Query filter for automatic tenant isolation"""
    
    @staticmethod
    def filter_by_tenant(query, company_id: int):
        """Add company_id filter to query if company_id is provided"""
        if company_id:
            # Check if the model has company_id column
            from sqlalchemy import inspect
            model = query.column_descriptions[0]['type']
            if hasattr(model, 'company_id'):
                query = query.filter_by(company_id=company_id)
        return query


class TenantSecurity:
    """Security checks for tenant operations"""
    
    @staticmethod
    def check_super_admin(user: User):
        """Check if user is Super Admin"""
        if not user.is_superuser:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Super Admin required"
            )
    
    @staticmethod
    def check_company_admin(user: User, company_id: int):
        """Check if user is Admin of the company"""
        if user.role_level > 1:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Admin Entreprise required"
            )
        if user.company_id != company_id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="User does not belong to this company"
            )
    
    @staticmethod
    def check_department_manager(user: User, department_id: int):
        """Check if user is manager of the department"""
        if user.role_level > 2:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Chef Département required"
            )
        if user.department_id != department_id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="User does not belong to this department"
            )
    
    @staticmethod
    def check_company_access(user: User, company_id: int):
        """Check if user has access to the company"""
        if user.is_superuser:
            return True  # Super Admin has access to all companies
        if user.company_id == company_id:
            return True  # User belongs to the company
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access denied to this company"
        )
    
    @staticmethod
    def check_quota(db: Session, company_id: int, quota_type: str):
        """Check if company has exceeded quota"""
        company = db.query(Company).filter(Company.id == company_id).first()
        if not company:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Company not found"
            )
        
        if quota_type == "users":
            if company.current_users >= company.max_users:
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail=f"User quota exceeded ({company.current_users}/{company.max_users})"
                )
        elif quota_type == "storage":
            if company.current_storage_mb >= company.max_storage_mb:
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail=f"Storage quota exceeded ({company.current_storage_mb}/{company.max_storage_mb} MB)"
                )
