"""
Authentication service - handles user authentication and authorization logic
"""
from sqlalchemy.orm import Session
from typing import Optional
from datetime import datetime, timedelta

from app.core.security import verify_password, get_password_hash, create_access_token, create_refresh_token
from app.core.config import settings
from app.models.user import User, Role
from app.schemas.user import UserCreate, UserResponse


class AuthService:
    """Service for authentication operations"""
    
    @staticmethod
    def create_user(user_data: UserCreate, db: Session) -> User:
        """Create a new user"""
        # Check if username exists
        if db.query(User).filter(User.username == user_data.username).first():
            raise ValueError("Username already registered")
        
        # Check if email exists
        if db.query(User).filter(User.email == user_data.email).first():
            raise ValueError("Email already registered")
        
        # Create new user
        hashed_password = get_password_hash(user_data.password)
        db_user = User(
            username=user_data.username,
            email=user_data.email,
            hashed_password=hashed_password,
            full_name=user_data.full_name,
            phone=user_data.phone,
            agency_id=user_data.agency_id,
            is_superuser=user_data.is_superuser
        )
        
        db.add(db_user)
        db.commit()
        db.refresh(db_user)
        return db_user
    
    @staticmethod
    def authenticate_user(username: str, password: str, db: Session) -> Optional[User]:
        """Authenticate user with username and password"""
        user = db.query(User).filter(User.username == username).first()
        
        if not user or not verify_password(password, user.hashed_password):
            return None
        
        if not user.is_active:
            return None
        
        return user
    
    @staticmethod
    def create_tokens(user: User) -> dict:
        """Create access and refresh tokens for user"""
        access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
        access_token = create_access_token(
            data={"sub": str(user.id), "username": user.username},
            expires_delta=access_token_expires
        )
        refresh_token = create_refresh_token(data={"sub": str(user.id)})
        
        return {
            "access_token": access_token,
            "refresh_token": refresh_token,
            "token_type": "bearer"
        }
    
    @staticmethod
    def get_user_by_id(user_id: int, db: Session) -> Optional[User]:
        """Get user by ID"""
        return db.query(User).filter(User.id == user_id).first()
    
    @staticmethod
    def update_user_password(user_id: int, new_password: str, db: Session) -> User:
        """Update user password"""
        user = db.query(User).filter(User.id == user_id).first()
        if not user:
            raise ValueError("User not found")
        
        user.hashed_password = get_password_hash(new_password)
        user.must_change_password = False
        user.password_changed_at = datetime.utcnow()
        
        db.commit()
        db.refresh(user)
        return user