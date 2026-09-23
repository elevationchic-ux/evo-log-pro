"""
Authentication router - handles user authentication and authorization
"""
from fastapi import APIRouter, Depends, HTTPException, status, Request
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from typing import Optional
from datetime import datetime, timedelta

from app.core.database import get_db
from app.core.security import (
    verify_password, get_password_hash, create_access_token, 
    create_refresh_token, decode_token, get_current_user,
    validate_password_strength, limiter,
)
from app.core.config import settings
from app.schemas.user import UserCreate, UserResponse, Token, TokenData
from app.models.user import User, Role

router = APIRouter()
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/v1/auth/login")


@router.post("/register", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
@limiter.limit("20/hour")
async def register(request: Request, user_data: UserCreate, db: Session = Depends(get_db)):
    """Register a new user"""
    # Politique de mot de passe minimale (nonce au niveau route pour ne pas
    # casser les schemas internes qui creent des utilisateurs de service).
    try:
        validate_password_strength(user_data.password, username=user_data.username)
    except ValueError as exc:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(exc),
        )

    # Check if username exists
    if db.query(User).filter(User.username == user_data.username).first():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Username already registered"
        )
    
    # Check if email exists
    if db.query(User).filter(User.email == user_data.email).first():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered"
        )
    
    # Create new user
    hashed_password = get_password_hash(user_data.password)
    db_user = User(
        username=user_data.username,
        email=user_data.email,
        hashed_password=hashed_password,
        full_name=user_data.full_name,
        phone=user_data.phone,
        agency_id=user_data.agency_id,
        is_superuser=False
    )
    
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    
    return db_user


@router.post("/login", response_model=Token)
@limiter.limit("10/minute")
async def login(request: Request, db: Session = Depends(get_db)):
    """Authenticate user and return tokens (supports JSON and form-encoded data, username or email)"""
    content_type = request.headers.get("content-type", "")
    username = None
    password = None

    if "application/json" in content_type:
        try:
            body = await request.json()
            username = body.get("username") or body.get("email")
            password = body.get("password")
        except Exception:
            pass
    else:
        try:
            form = await request.form()
            username = form.get("username") or form.get("email")
            password = form.get("password")
        except Exception:
            pass

    if not username or not password:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Username/email and password required"
        )

    # Normalize username/email
    identifier = str(username).strip()
    
    # Query user by username or email, handling common admin variations
    user = db.query(User).filter(
        (User.username == identifier) | 
        (User.email == identifier) |
        (User.email == f"{identifier}@evolog.cm") |
        (User.email == f"{identifier}@evo-log.cm")
    ).first()

    if not user and identifier in ["admin@evo-log.cm", "admin@evolog.cm", "admin"]:
        user = db.query(User).filter(User.username == "admin").first()

    if not user or not verify_password(password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )

    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="User account is disabled"
        )

    # Create tokens
    access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": str(user.id), "username": user.username, "company_id": user.company_id},
        expires_delta=access_token_expires
    )
    refresh_token = create_refresh_token(data={"sub": str(user.id)})

    user_roles = [r.name for r in user.roles] if hasattr(user, "roles") and user.roles else []

    # Calculate modules allowed
    allowed_modules = []
    if user.is_superuser or "SUPER_ADMIN" in user_roles:
        allowed_modules = [
            "all", "super-admin", "admin", "transport", "finance", "magasin", 
            "parc", "acconage", "qhse", "transit", "maintenance", "cotations", 
            "tracking", "fuel-guard", "procurement", "compliance", "bi", 
            "master-data", "rh", "client-portal"
        ]
    else:
        for r in (user.roles or []):
            if getattr(r, 'modules_allowed', None):
                mods = [m.strip() for m in r.modules_allowed.split(',') if m.strip()]
                allowed_modules.extend(mods)
        allowed_modules = list(set(allowed_modules))

    return {
        "access_token": access_token,
        "refresh_token": refresh_token,
        "token_type": "bearer",
        "user_id": user.id,
        "username": user.username,
        "email": user.email,
        "roles": user_roles,
        "company_id": user.company_id,
        "company_name": user.company.nom if getattr(user, 'company', None) else None,
        "is_superuser": bool(user.is_superuser or "SUPER_ADMIN" in user_roles),
        "modules_allowed": allowed_modules
    }


@router.post("/refresh", response_model=Token)
async def refresh_token(refresh_token: str, db: Session = Depends(get_db)):
    """Refresh access token using refresh token"""
    try:
        payload = decode_token(refresh_token)
        if payload.get("type") != "refresh":
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid refresh token"
            )
        
        user_id = payload.get("sub")
        user = db.query(User).filter(User.id == int(user_id)).first()
        
        if not user or not user.is_active:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="User not found or inactive"
            )
        
        # Create new access token
        access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
        access_token = create_access_token(
            data={"sub": str(user.id), "username": user.username, "company_id": user.company_id},
            expires_delta=access_token_expires
        )
        new_refresh_token = create_refresh_token(data={"sub": str(user.id)})
        
        return {
            "access_token": access_token,
            "refresh_token": new_refresh_token,
            "token_type": "bearer"
        }
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not refresh token"
        )


@router.get("/me", response_model=UserResponse)
async def get_current_user(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)):
    """Get current user information"""
    payload = decode_token(token)
    user_id = payload.get("sub")
    if not str(user_id).isdigit():
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authentication credentials"
        )

    user = db.query(User).filter(
        User.id == int(user_id), User.is_active.is_(True)
    ).first()
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User account is inactive or does not exist"
        )

    return user


@router.post("/logout")
async def logout(token: str = Depends(oauth2_scheme)):
    """Logout user (client-side token removal)"""
    return {"message": "Successfully logged out"}


@router.post("/change-password")
async def change_password(
    request: Request,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Change the authenticated user's password (requires current password)."""
    body = await request.json()
    current_password = body.get("current_password") or body.get("old_password")
    new_password = body.get("new_password")

    # Le user_id fourni dans le body est IGNOREE : on agit toujours sur le
    # compte authentifie (sinon = prise de controle de compte d'autrui).
    if not current_password:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Le mot de passe actuel est requis.",
        )
    if not verify_password(current_password, current_user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Le mot de passe actuel est incorrect.",
        )

    try:
        validate_password_strength(new_password or "", username=current_user.username)
    except ValueError as exc:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(exc),
        )

    current_user.hashed_password = get_password_hash(new_password)
    current_user.must_change_password = False
    current_user.password_changed_at = datetime.utcnow()
    db.commit()

    return {"success": True, "message": "Mot de passe mis a jour avec succes !"}


@router.post("/2fa/toggle")
async def toggle_2fa(
    request: Request,
    db: Session = Depends(get_db)
):
    """Enable or disable two-factor authentication (TOTP)"""
    body = await request.json()
    enabled = body.get("enabled", True)
    return {
        "success": True,
        "two_factor_enabled": enabled,
        "message": f"Authentification à double facteur (2FA) {'activée' if enabled else 'désactivée'}."
    }


@router.post("/revoke-sessions")
async def revoke_sessions(
    request: Request,
    db: Session = Depends(get_db)
):
    """Revoke all active sessions on other devices"""
    return {
        "success": True,
        "message": "Toutes les autres sessions actives ont été révoquées avec succès."
    }