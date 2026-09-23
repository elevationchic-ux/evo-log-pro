"""
Security utilities and authentication
"""
from passlib.context import CryptContext
from jose import JWTError, jwt
from datetime import datetime, timedelta
from fastapi import Depends, HTTPException, WebSocket, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from slowapi import Limiter
from slowapi.util import get_remote_address
from app.core.config import settings
from app.core.database import get_db
from app.models.user import User
from sqlalchemy.orm import Session

import bcrypt

security = HTTPBearer(auto_error=True)
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# Rate limiter
limiter = Limiter(key_func=get_remote_address)

# JWT Bearer
security = HTTPBearer()


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verify a password against a hash"""
    try:
        if isinstance(hashed_password, str):
            hashed_bytes = hashed_password.encode('utf-8')
        else:
            hashed_bytes = hashed_password
        plain_bytes = plain_password.encode('utf-8')[:72]
        return bcrypt.checkpw(plain_bytes, hashed_bytes)
    except Exception:
        try:
            return pwd_context.verify(plain_password, hashed_password)
        except Exception:
            return False


def get_password_hash(password: str) -> str:
    """Hash a password"""
    plain_bytes = password.encode('utf-8')[:72]
    salt = bcrypt.gensalt()
    return bcrypt.hashpw(plain_bytes, salt).decode('utf-8')


# Liste courte de mots de passe bannis (les plus frequents / evidents).
_COMMON_PASSWORDS = {
    "password", "motdepasse", "12345678", "123456789", "azertyuiop",
    "admin123", "supadmin123", "qwer1234", "11111111", "iloveyou",
}


def validate_password_strength(password: str, username: str | None = None) -> None:
    """Verifie la robustesse minimale d'un mot de passe.

    Leve une ``ValueError`` (message pret a afficher) si la politique n'est
    pas satisfaite. Politique volontairement raisonnable pour ne pas bloquer
    les utilisateurs legitimes :
      - au moins 8 caracteres ;
      - au moins une lettre et au moins un chiffre ;
      - ne doit pas figurer dans la liste des mots de passe les plus courants ;
      - ne doit pas egaliser le nom d'utilisateur.
    """
    if not password or len(password) < 8:
        raise ValueError("Le mot de passe doit contenir au moins 8 caracteres.")
    if not any(c.isdigit() for c in password):
        raise ValueError("Le mot de passe doit contenir au moins un chiffre.")
    if not any(c.isalpha() for c in password):
        raise ValueError("Le mot de passe doit contenir au moins une lettre.")
    lowered = password.lower()
    if lowered in _COMMON_PASSWORDS:
        raise ValueError("Ce mot de passe est trop courant, choisissez-en un autre.")
    if username and lowered == username.lower():
        raise ValueError("Le mot de passe ne peut pas etre identique au nom d'utilisateur.")



def create_access_token(data: dict, expires_delta: timedelta = None) -> str:
    """Create JWT access token"""
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM)
    return encoded_jwt


def create_refresh_token(data: dict) -> str:
    """Create JWT refresh token"""
    to_encode = data.copy()
    expire = datetime.utcnow() + timedelta(days=settings.REFRESH_TOKEN_EXPIRE_DAYS)
    to_encode.update({"exp": expire, "type": "refresh"})
    encoded_jwt = jwt.encode(to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM)
    return encoded_jwt


def decode_token(token: str) -> dict:
    """Decode and validate JWT token"""
    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
        return payload
    except JWTError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )


def get_token_payload(
    credentials: HTTPAuthorizationCredentials = Depends(security),
) -> dict:
    """Validate an access token and return its claims."""
    payload = decode_token(credentials.credentials)
    if payload.get("type") == "refresh":
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Refresh token cannot be used for access",
        )
    return payload


def get_current_user_id(
    credentials: HTTPAuthorizationCredentials = Depends(security),
) -> int:
    """Return the authenticated numeric user id from an access token."""
    payload = get_token_payload(credentials)
    user_id = payload.get("sub")
    if not str(user_id).isdigit():
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authentication credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )
    return int(user_id)


def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: Session = Depends(get_db),
) -> User:
    """Return the authenticated active user from the database."""
    user_id = get_current_user_id(credentials)
    user = db.query(User).filter(User.id == user_id, User.is_active.is_(True)).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User account is inactive or does not exist",
        )
    return user


def authenticate_websocket(websocket: WebSocket, db: Session) -> User:
    authorization = websocket.headers.get("authorization")
    token = websocket.query_params.get("token")
    if authorization and authorization.lower().startswith("bearer "):
        token = authorization[7:].strip()
    if not token:
        raise HTTPException(status_code=401, detail="WebSocket authentication required")
    payload = get_token_payload(
        HTTPAuthorizationCredentials(scheme="Bearer", credentials=token)
    )
    try:
        user = db.query(User).filter(User.id == int(payload.get("sub"))).first()
    except (TypeError, ValueError):
        user = None
    if user is None or not user.is_active:
        raise HTTPException(status_code=401, detail="Invalid WebSocket credentials")
    return user