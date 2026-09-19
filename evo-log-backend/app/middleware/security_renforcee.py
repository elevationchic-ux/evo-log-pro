"""Enhanced Security Middlewares - 2FA, IP Whitelist, Encryption"""
from fastapi import Request, HTTPException, status
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.responses import JSONResponse
from typing import Optional
from datetime import datetime
import pyotp
import hashlib
from cryptography.fernet import Fernet


class TwoFactorAuthMiddleware(BaseHTTPMiddleware):
    """Two-Factor Authentication middleware"""
    
    async def dispatch(self, request: Request, call_next):
        # Skip 2FA for health checks and public endpoints
        if request.url.path in ["/health", "/docs", "/openapi.json"]:
            return await call_next(request)
        
        # Check if 2FA is required
        user = getattr(request.state, "user", None)
        if user and getattr(user, "two_factor_enabled", False):
            two_factor_token = request.headers.get("X-2FA-Token")
            if not two_factor_token:
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail="Two-factor authentication required"
                )
            
            # Verify 2FA token
            if not self.verify_2fa_token(user, two_factor_token):
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Invalid two-factor authentication token"
                )
        
        response = await call_next(request)
        return response
    
    @staticmethod
    def verify_2fa_token(user, token: str) -> bool:
        """Verify 2FA token"""
        # In production, use user's secret key
        totp = pyotp.TOTP("JBSWY3DPEHPK3PXP")  # Demo secret
        return totp.verify(token, valid_window=1)


class IPWhitelistMiddleware(BaseHTTPMiddleware):
    """IP Whitelist middleware for tenant isolation"""
    
    async def dispatch(self, request: Request, call_next):
        # Get client IP
        client_ip = request.client.host if request.client else "unknown"
        
        # Get tenant context
        tenant_id = getattr(request.state, "tenant_id", None)
        
        if tenant_id:
            # Check if IP is whitelisted for this tenant
            if not self.is_ip_whitelisted(tenant_id, client_ip):
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail=f"IP {client_ip} not whitelisted for tenant {tenant_id}"
                )
        
        response = await call_next(request)
        return response
    
    @staticmethod
    def is_ip_whitelisted(tenant_id: str, ip: str) -> bool:
        """Check if IP is whitelisted for tenant"""
        # In production, check database for IP whitelist
        # For now, allow all IPs in development
        return True


class EncryptionMiddleware(BaseHTTPMiddleware):
    """Encryption middleware for sensitive data"""
    
    def __init__(self, app, encryption_key: str):
        super().__init__(app)
        self.cipher = Fernet(encryption_key.encode() if isinstance(encryption_key, str) else encryption_key)
    
    async def dispatch(self, request: Request, call_next):
        # Encrypt sensitive data in request body if needed
        if request.method in ["POST", "PUT", "PATCH"]:
            # Process and encrypt sensitive fields
            pass
        
        response = await call_next(request)
        
        # Decrypt sensitive data in response if needed
        return response
    
    def encrypt_data(self, data: str) -> str:
        """Encrypt data"""
        return self.cipher.encrypt(data.encode()).decode()
    
    def decrypt_data(self, encrypted_data: str) -> str:
        """Decrypt data"""
        return self.cipher.decrypt(encrypted_data.encode()).decode()


class TenantRateLimitMiddleware(BaseHTTPMiddleware):
    """Rate limiting per tenant"""
    
    def __init__(self, app, default_limit: int = 1000):
        super().__init__(app)
        self.default_limit = default_limit
        self.request_counts = {}  # tenant_id -> count
    
    async def dispatch(self, request: Request, call_next):
        tenant_id = getattr(request.state, "tenant_id", None)
        
        if tenant_id:
            # Get tenant-specific limit
            limit = self.get_tenant_limit(tenant_id)
            
            # Check rate limit
            current_count = self.request_counts.get(tenant_id, 0)
            if current_count >= limit:
                raise HTTPException(
                    status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                    detail=f"Rate limit exceeded for tenant {tenant_id}"
                )
            
            # Increment counter
            self.request_counts[tenant_id] = current_count + 1
        
        response = await call_next(request)
        return response
    
    def get_tenant_limit(self, tenant_id: str) -> int:
        """Get tenant-specific rate limit"""
        # In production, check tenant subscription plan
        return self.default_limit


class AuditLogMiddleware(BaseHTTPMiddleware):
    """Enhanced audit logging middleware"""
    
    async def dispatch(self, request: Request, call_next):
        # Log request details
        user = getattr(request.state, "user", None)
        tenant_id = getattr(request.state, "tenant_id", None)
        
        audit_data = {
            "timestamp": datetime.utcnow().isoformat(),
            "method": request.method,
            "path": request.url.path,
            "query_params": str(request.query_params),
            "user_id": getattr(user, "id", None) if user else None,
            "tenant_id": tenant_id,
            "client_ip": request.client.host if request.client else "unknown",
            "user_agent": request.headers.get("user-agent"),
        }
        
        # Store audit log (in production, write to database or log file)
        self.log_audit(audit_data)
        
        response = await call_next(request)
        
        # Log response
        audit_data["status_code"] = response.status_code
        self.log_audit(audit_data)
        
        return response
    
    @staticmethod
    def log_audit(data: dict):
        """Log audit data"""
        # In production, write to database or structured log file
        import logging
        logger = logging.getLogger("audit")
        logger.info(f"AUDIT: {data}")
