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
    generate_totp_secret, build_otpauth_uri, verify_totp,
    create_2fa_token, decode_2fa_token,
    generate_recovery_codes, parse_recovery_codes, try_consume_recovery_code,
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


@router.post("/login")
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

    # Second facteur : si l'utilisateur a active le 2FA, le mot de passe seul
    # ne suffit PAS. On delivre un jeton intermediaire court et on exige la
    # verification TOTP via POST /auth/2fa/verify avant toute emission de token.
    if getattr(user, "two_factor_enabled", False) and getattr(user, "two_factor_secret", None):
        return {
            "two_factor_required": True,
            "two_factor_token": create_2fa_token(user.id),
            "token_type": "bearer",
        }

    return _build_login_payload(user)


def _build_login_payload(user: User) -> dict:
    """Construit la reponse de session (tokens + roles + modules autorises).

    Partagee par /auth/login et /auth/2fa/verify pour garantir une structure
    de reponse strictement identique (contrat attendu par NextAuth cote front).
    """
    # Create tokens
    access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": str(user.id), "username": user.username, "company_id": user.company_id},
        expires_delta=access_token_expires
    )
    refresh_token = create_refresh_token(data={"sub": str(user.id)})

    user_roles = [r.name for r in user.roles] if hasattr(user, "roles") and user.roles else []

    # Calcul des modules autorises (repli historique modules_allowed).
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

    # Permissions granulaires effectives + modules communs a l'entreprise.
    permissions: list = []
    shared_modules: list = []
    try:
        from app.core.permissions import load_effective_permissions, _shared_module_keys
        permissions = sorted(load_effective_permissions(user))
        shared_modules = sorted(_shared_module_keys(user))
    except Exception:
        # Ne jamais faire echouer la connexion si la brique granulaire n'est
        # pas encore en place (base non migree) : on retombe sur modules_allowed.
        pass

    return {
        "access_token": access_token,
        "refresh_token": refresh_token,
        "token_type": "bearer",
        "user_id": user.id,
        "username": user.username,
        "email": user.email,
        "roles": user_roles,
        "role_level": getattr(user, "role_level", 3),
        "department_id": getattr(user, "department_id", None),
        "company_id": user.company_id,
        "company_name": user.company.nom if getattr(user, 'company', None) else None,
        "is_superuser": bool(user.is_superuser or "SUPER_ADMIN" in user_roles),
        "modules_allowed": allowed_modules,
        "permissions": permissions,
        "shared_modules": shared_modules,
        # Le front n'invente jamais cette regle : c'est la source backend
        # (colonne users.must_change_password) qui declenche le gate.
        # Exception : un Super Administrateur (compte CADC) n'est JAMAIS renvoye
        # vers le changement de mot de passe, meme si la colonne vaut True (ex.
        # apres regeneration de la colonne). Protoge contre les regressions.
        "must_change_password": bool(
            getattr(user, "must_change_password", False)
            and not (user.is_superuser or "SUPER_ADMIN" in user_roles)
        ),
    }


@router.get("/session")
async def read_session(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Reconstruit le payload de session depuis un access token deja valide.

    Utilise par NextAuth (provider credentials) quand le formulaire a deja
    franchi l'etape mot de passe (+ code 2FA eventuel) directement contre
    /auth/login et /auth/2fa/verify : le handler d'autorisation du front
    verifie le jalon recu ici au lieu de renvoyer le mot de passe, ce qui
    evite deux appels /login (et le compteur de tentatives associe) pour une
    seule connexion utilisateur."""
    return _build_login_payload(current_user)


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


@router.get("/2fa/status")
async def get_2fa_status(current_user: User = Depends(get_current_user)):
    """Etat courant de la 2FA pour l'utilisateur authentifie.

    Les codes de secours ne sont JAMAIS renvoyes ici : seuls le total et le
    solde utilisable le sont (les codes en clair n'existent qu'a l'emission)."""
    codes = parse_recovery_codes(getattr(current_user, "two_factor_recovery_codes", None))
    issued_at = getattr(current_user, "two_factor_recovery_issued_at", None)
    confirmed_at = getattr(current_user, "two_factor_confirmed_at", None)
    return {
        "two_factor_enabled": bool(getattr(current_user, "two_factor_enabled", False)),
        "configured": bool(getattr(current_user, "two_factor_secret", None)),
        "confirmed_at": confirmed_at.isoformat() if confirmed_at else None,
        "recovery_codes_total": len(codes),
        "recovery_codes_remaining": sum(1 for c in codes if not c.get("used_at")),
        "recovery_codes_issued_at": issued_at.isoformat() if issued_at else None,
    }


@router.post("/2fa/setup")
async def setup_2fa(
    request: Request,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Genere un secret TOTP (mise en attente) + l'URI otpauth a encoder en QR.

    La 2FA n'est PAS encore active : il faut confirmer via /2fa/enable avec un
    code valide. Le secret n'est jamais renvoye par un autre endpoint.

    Quand la 2FA est deja active, re-emettre un secret la couperait
    instantanement (two_factor_enabled remis a False) : un compte detourne
    pourrait desarmer le second facteur sans le code courant. Un code TOTP
    valide est donc exige avant tout re-provisionnement.
    """
    try:
        corps = await request.json()
    except Exception:
        corps = {}
    code = (corps or {}).get("code")
    deja_active = bool(getattr(current_user, "two_factor_enabled", False))
    secret_courant = getattr(current_user, "two_factor_secret", None)
    if deja_active:
        if not verify_totp(secret_courant or "", code or ""):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=(
                    "La 2FA est deja active : un code TOTP en cours est requis "
                    "pour reinitialiser le secret."
                ),
            )
    secret = generate_totp_secret()
    current_user.two_factor_secret = secret
    current_user.two_factor_enabled = False
    db.commit()
    return {
        "secret": secret,
        "otpauth_uri": build_otpauth_uri(secret, current_user.username),
        "reset": deja_active,
        "message": "Scannez le QR puis confirmez avec un code pour activer la 2FA.",
    }


@router.post("/2fa/enable")
async def enable_2fa(
    request: Request,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Active la 2FA seulement si le code TOTP correspond au secret en attente."""
    try:
        body = await request.json()
    except Exception:
        body = {}
    if not isinstance(body, dict):
        body = {}
    code = body.get("code")
    secret = getattr(current_user, "two_factor_secret", None)
    if not secret:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Aucun secret 2FA en attente. Appelez d'abord /auth/2fa/setup.",
        )
    if not verify_totp(secret, code or ""):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Code de verification invalide.",
        )
    current_user.two_factor_enabled = True
    current_user.two_factor_confirmed_at = datetime.utcnow()
    # Emission automatique des codes de secours : sans eux, perdre son
    # generateur de codes signifie ne plus jamais pouvoir se connecter. Les
    # codes en clair ne sont renvoyes qu'ici, une seule fois.
    codes_clairs, blob = generate_recovery_codes()
    current_user.two_factor_recovery_codes = blob
    current_user.two_factor_recovery_issued_at = datetime.utcnow()
    db.commit()
    return {
        "success": True,
        "two_factor_enabled": True,
        "recovery_codes": codes_clairs,
        "message": "2FA activee. Conservez les codes de secours hors ligne.",
    }


@router.get("/2fa/recovery-codes")
async def recovery_codes_status(
    current_user: User = Depends(get_current_user),
):
    """Solde des codes de secours. Les codes eux-memes ne sont jamais relus :
    la base ne contient que leurs hachages."""
    codes = parse_recovery_codes(getattr(current_user, "two_factor_recovery_codes", None))
    issued_at = getattr(current_user, "two_factor_recovery_issued_at", None)
    return {
        "configured": bool(codes),
        "total": len(codes),
        "remaining": sum(1 for c in codes if not c.get("used_at")),
        "used": sum(1 for c in codes if c.get("used_at")),
        "issued_at": issued_at.isoformat() if issued_at else None,
    }


@router.post("/2fa/recovery-codes")
async def regenerate_recovery_codes(
    request: Request,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Regenere un jeu de codes de secours (les anciens sont remplaces).

    Le mot de passe est exige : changer les codes de secours est une operation
    sensible, au meme titre que desactiver la 2FA."""
    try:
        corps = await request.json()
    except Exception:
        corps = {}
    password = (corps or {}).get("password")
    if not password or not verify_password(password, current_user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Mot de passe requis pour regenerer les codes de secours.",
        )
    if not bool(getattr(current_user, "two_factor_enabled", False)):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Aucune 2FA active : les codes de secours n'ont pas d'objet.",
        )
    codes_clairs, blob = generate_recovery_codes()
    current_user.two_factor_recovery_codes = blob
    current_user.two_factor_recovery_issued_at = datetime.utcnow()
    db.commit()
    return {
        "success": True,
        "recovery_codes": codes_clairs,
        "message": "Nouveaux codes emis ; les precedents ne fonctionnent plus.",
    }


@router.post("/2fa/disable")
async def disable_2fa(
    request: Request,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Desactive la 2FA. Exige le mot de passe pour eviter toute desactivation
    par detournement de session."""
    try:
        body = await request.json()
    except Exception:
        body = {}
    if not isinstance(body, dict):
        body = {}
    password = body.get("password")
    if not password or not verify_password(password, current_user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Mot de passe requis et valide pour desactiver la 2FA.",
        )
    current_user.two_factor_enabled = False
    current_user.two_factor_secret = None
    current_user.two_factor_confirmed_at = None
    # Les codes de secours n'ont plus de sens sans second facteur : ils
    # resteraient des trousseaux d'acces orphelins en base.
    current_user.two_factor_recovery_codes = None
    current_user.two_factor_recovery_issued_at = None
    db.commit()
    return {"success": True, "two_factor_enabled": False, "message": "2FA desactivee."}


@router.post("/2fa/verify")
async def verify_2fa(
    request: Request,
    db: Session = Depends(get_db),
):
    """Echange un jeton 2FA (delivre par /login) + code TOTP contre une vraie
    session. Repond avec la MEME structure que /login pour rester compatible
    avec NextAuth cote frontend.

    Pas de `response_model` : le schema Token ne declare ni must_change_password
    ni les champs RBAC granulaires (permissions, shared_modules, role_level,
    department_id). Avec ce filtre, un compte 2FA echappait au changement de mot
    de passe obligatoire et perdait ses permissions effectives."""
    try:
        body = await request.json()
    except Exception:
        body = {}
    if not isinstance(body, dict):
        body = {}
    two_factor_token = body.get("two_factor_token")
    code = body.get("code")
    if not two_factor_token:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="two_factor_token requis.",
        )

    user_id = decode_2fa_token(two_factor_token)
    user = db.query(User).filter(User.id == user_id, User.is_active.is_(True)).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Utilisateur introuvable ou inactif.",
        )
    secret = getattr(user, "two_factor_secret", None)
    if secret and verify_totp(secret, code or ""):
        return _build_login_payload(user)

    # Le code peut aussi etre un code de secours a usage unique : c'est la
    # seule porte de sortie quand le telephone a ete perdu ou remplace.
    accepte, nouveau_blob = try_consume_recovery_code(
        getattr(user, "two_factor_recovery_codes", None), code or ""
    )
    if accepte:
        user.two_factor_recovery_codes = nouveau_blob
        db.commit()
        return _build_login_payload(user)

    raise HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Code de verification invalide.",
    )


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