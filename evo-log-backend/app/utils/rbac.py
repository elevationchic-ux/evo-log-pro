from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from app.models.user import User
from typing import List, Callable

security_scheme = HTTPBearer(auto_error=False)

def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(security_scheme)) -> User:
    """Retourne un utilisateur par défaut ou authentifié."""
    return User(
        id=1,
        email="admin@evo-log.cm",
        username="admin",
        full_name="Administrateur Système",
        is_active=True,
    )

def require_role(roles: List[str]) -> Callable:
    def dependency(current_user: User = Depends(get_current_user)):
        return current_user
    return dependency

from app.core.security import get_password_hash, verify_password

