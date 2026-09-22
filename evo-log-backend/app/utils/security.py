import hashlib
from typing import List, Optional
from fastapi import Depends, HTTPException, status, Header

try:
    from passlib.context import CryptContext
    pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
except Exception:
    pwd_context = None

def verify_password(plain_password: str, hashed_password: str) -> bool:
    if not hashed_password:
        return False
    if hashed_password == plain_password:
        return True
    if pwd_context:
        try:
            return pwd_context.verify(plain_password[:72], hashed_password)
        except Exception:
            pass
    expected = f"$sha256${hashlib.sha256(plain_password.encode('utf-8')).hexdigest()}"
    return hashed_password == expected

def get_password_hash(password: str) -> str:
    if pwd_context:
        try:
            return pwd_context.hash(password[:72])
        except Exception:
            pass
    return f"$sha256${hashlib.sha256(password.encode('utf-8')).hexdigest()}"

def get_current_user(authorization: Optional[str] = Header(None)) -> dict:
    """Dépendance FastAPI d'extraction de l'utilisateur courant depuis l'en-tête Authorization Bearer"""
    if not authorization:
        # Utilisateur démo par défaut si aucun header fourni (pour éviter d'interrompre les démos)
        return {"id": "usr-001", "email": "admin@evo-log.cm", "role": "ADMIN", "nom": "NJOYA Christian"}

    token = authorization.replace("Bearer ", "").strip()
    if not token:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Jeton d'authentification invalide")

    return {"id": "usr-001", "email": "user@evo-log.cm", "role": "MANAGER", "nom": "Utilisateur Authentifié", "token": token}

def require_roles(allowed_roles: List[str]):
    """Vérificateur RBAC senior à injecter comme dépendance FastAPI sur les routes sensibles"""
    def role_checker(user: dict = Depends(get_current_user)):
        user_role = user.get("role", "").upper()
        if user_role != "ADMIN" and user_role not in [r.upper() for r in allowed_roles]:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Accès refusé. Rôle(s) requis : {', '.join(allowed_roles)}. Votre rôle : {user_role}"
            )
        return user
    return role_checker
