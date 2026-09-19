from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from pydantic import BaseModel, EmailStr, Field
from typing import Optional
from datetime import datetime, timedelta
import re

from app.database import get_db
from app.models.organization import Organization
from app.models.user import User, RoleModel
from app.models.agency import Agency
from app.utils.rbac import get_password_hash

router = APIRouter()

class OnboardingRegisterSchema(BaseModel):
    company_name: str = Field(..., example="Transports Cameroun Express")
    company_code: str = Field(..., example="TCE-LOG")
    admin_email: EmailStr = Field(..., example="admin@tce-logistics.cm")
    admin_password: str = Field(..., min_length=6, example="Secret123!")
    admin_full_name: str = Field(..., example="Jean Dupont")
    admin_telephone: Optional[str] = Field(None, example="+237699001122")
    city: str = Field("Douala", example="Douala")
    country: str = Field("Cameroun", example="Cameroun")

@router.post("/register", status_code=status.HTTP_201_CREATED)
def register_organization_onboarding(
    payload: OnboardingRegisterSchema,
    db: Session = Depends(get_db)
):
    """
    Self-service signup: Automates creation of Organization, Primary Agency, 
    and Admin Account with a 14-day free trial.
    """
    clean_code = payload.company_code.upper().strip()
    slug = re.sub(r'[^a-z0-9]+', '-', payload.company_name.lower()).strip('-')

    # Check for existing email or company code
    existing_user = db.query(User).filter(User.email == payload.admin_email.lower()).first()
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="An account with this email already exists."
        )

    existing_org = db.query(Organization).filter(
        (Organization.code == clean_code) | (Organization.slug == slug)
    ).first()
    if existing_org:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="A company with this code or name is already registered."
        )

    # 1. Create Organization tenant with 14-day trial
    org = Organization(
        code=clean_code,
        name=payload.company_name,
        slug=slug,
        plan="FREE_TRIAL",
        status="ACTIVE",
        subscription_expires_at=datetime.utcnow() + timedelta(days=14),
        max_users=5,
        allowed_modules=[
            "transport", "magasin", "finance", "parc", "master-data", "qhse", 
            "documents", "acconage", "maintenance", "fuelguard", "cotations", 
            "douane", "rh", "procurement", "bi", "collaboration", "sectoral"
        ],
        tenant_config={
            "warehouse_management_mode": "ZONES",
            "document_numbering_prefix": f"EVO-{clean_code[:4]}-",
            "logo_url": None,
            "primary_color": "#4f46e5",
            "legal_name": payload.company_name,
            "city": payload.city,
            "country": payload.country,
            "currency": "XAF",
            "payment_terms_days": 30,
            "allow_offline_mode": True
        },
        is_active=True
    )
    db.add(org)
    db.commit()
    db.refresh(org)

    # 2. Create default Primary Agency
    agency = Agency(
        organization_id=org.id,
        code=f"AG-{clean_code}-01",
        nom=f"Siège Principal - {payload.company_name}",
        ville=payload.city,
        pays=payload.country,
        is_active=True
    )
    db.add(agency)
    db.commit()
    db.refresh(agency)

    # 3. Create Admin User
    hashed_pwd = get_password_hash(payload.admin_password)
    admin_role = db.query(RoleModel).filter(RoleModel.code == "ADMIN").first()
    
    user = User(
        organization_id=org.id,
        agency_id=agency.id,
        email=payload.admin_email.lower(),
        username=payload.admin_email.lower().split('@')[0],
        hashed_password=hashed_pwd,
        full_name=payload.admin_full_name,
        telephone=payload.admin_telephone,
        departement="DIRECTION",
        modules_allowed=["*"],
        is_active=True,
        must_change_password=False
    )
    if admin_role:
        user.roles.append(admin_role)

    db.add(user)
    db.commit()
    db.refresh(user)

    return {
        "status": "success",
        "message": "Organization self-service onboarding completed successfully! 14-day free trial activated.",
        "organization": {
            "id": org.id,
            "code": org.code,
            "name": org.name,
            "plan": org.plan,
            "expires_at": org.subscription_expires_at
        },
        "admin_user": {
            "id": user.id,
            "email": user.email,
            "full_name": user.full_name
        }
    }
