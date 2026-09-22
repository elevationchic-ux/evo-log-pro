"""Role-based access control utilities."""
from typing import Callable, List

from fastapi import Depends

from app.core.security import get_current_user, get_password_hash, verify_password
from app.models.user import User


def require_role(roles: List[str]) -> Callable:
    def dependency(current_user: User = Depends(get_current_user)):
        return current_user

    return dependency
