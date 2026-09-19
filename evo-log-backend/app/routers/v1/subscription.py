from fastapi import APIRouter, Depends, HTTPException, status, Request
from sqlalchemy.orm import Session
from pydantic import BaseModel, Field
from typing import Optional, Dict, Any, List
from datetime import datetime, timedelta

from app.database import get_db
from app.models.organization import Organization
from app.models.user import User
from app.utils.tenant import get_current_tenant_context, TenantContext

router = APIRouter()

PLANS_CATALOG = {
    "FREE_TRIAL": {
        "name": "Essai Gratuit 14 Jours",
        "price_xaf_monthly": 0,
        "max_users": 5,
        "features": ["Transport", "WMS Magasin", "Finance de base", "Support Email"],
        "allowed_modules": ["transport", "magasin", "finance", "master-data", "qhse"]
    },
    "STARTER": {
        "name": "Formule Starter PME",
        "price_xaf_monthly": 150000,
        "max_users": 15,
        "features": ["Transport Complete", "WMS Magasin", "Finance & Facturation", "Acconage & Douane", "Support prioritaire 5/7"],
        "allowed_modules": ["transport", "magasin", "finance", "master-data", "qhse", "documents", "acconage", "cotations", "douane", "rh"]
    },
    "BUSINESS": {
        "name": "Formule Business Enterprise",
        "price_xaf_monthly": 450000,
        "max_users": 50,
        "features": ["Tout le Cœur ERP", "GED complète", "Offline-first PWA", "IA prédictive & FuelGuard", "Support 24/7"],
        "allowed_modules": ["transport", "magasin", "finance", "parc", "master-data", "qhse", "documents", "acconage", "maintenance", "fuelguard", "cotations", "douane", "rh", "procurement", "bi", "collaboration", "sectoral"]
    },
    "ENTERPRISE": {
        "name": "Formule Sur-Mesure",
        "price_xaf_monthly": 950000,
        "max_users": 500,
        "features": ["Accès Illimité", "IoT & Télématique", "Bourse de Fret & Blockchain", "SLA 99.9% garanti", "Account Manager Dédié"],
        "allowed_modules": ["*"]
    }
}

class UpgradePlanSchema(BaseModel):
    target_plan: str = Field(..., example="BUSINESS")
    billing_cycle: str = Field("MONTHLY", example="MONTHLY") # MONTHLY, ANNUAL
    payment_method: str = Field("MOBILE_MONEY", example="MOBILE_MONEY") # STRIPE, ORANGE_MONEY, MTN_MOMO

@router.get("/plans")
def get_plans_catalog():
    """Retrieve available SaaS subscription plan tiers and pricing."""
    return {"status": "success", "plans": PLANS_CATALOG}

@router.get("/current")
def get_current_subscription(
    context: TenantContext = Depends(get_current_tenant_context),
    db: Session = Depends(get_db)
):
    """Retrieve active tenant's subscription status, metrics, and plan limits."""
    org = context.organization
    if not org:
        raise HTTPException(status_code=400, detail="No active Organization tenant context.")

    user_count = db.query(User).filter(User.organization_id == org.id).count()
    plan_info = PLANS_CATALOG.get(org.plan, PLANS_CATALOG["STARTER"])

    return {
        "organization_id": org.id,
        "organization_name": org.name,
        "plan": org.plan,
        "plan_details": plan_info,
        "status": org.status,
        "is_active": org.is_active,
        "max_users": org.max_users,
        "active_users": user_count,
        "subscription_expires_at": org.subscription_expires_at,
        "allowed_modules": org.allowed_modules
    }

@router.post("/upgrade")
def upgrade_subscription(
    payload: UpgradePlanSchema,
    context: TenantContext = Depends(get_current_tenant_context),
    db: Session = Depends(get_db)
):
    """Self-service upgrade or renewal of SaaS subscription plan."""
    org = context.organization
    if not org:
        raise HTTPException(status_code=400, detail="No active Organization tenant context.")

    if payload.target_plan not in PLANS_CATALOG:
        raise HTTPException(status_code=400, detail=f"Invalid target plan '{payload.target_plan}'")

    target_details = PLANS_CATALOG[payload.target_plan]
    
    # Update organization plan and expiration date
    org.plan = payload.target_plan
    org.status = "ACTIVE"
    org.max_users = target_details["max_users"]
    org.allowed_modules = target_details["allowed_modules"]
    
    days_to_add = 365 if payload.billing_cycle == "ANNUAL" else 30
    org.subscription_expires_at = datetime.utcnow() + timedelta(days=days_to_add)
    
    db.commit()
    db.refresh(org)

    return {
        "status": "success",
        "message": f"Successfully updated subscription to {payload.target_plan}.",
        "plan": org.plan,
        "expires_at": org.subscription_expires_at
    }

@router.post("/webhook/mobile-money")
async def mobile_money_webhook(request: Request, db: Session = Depends(get_db)):
    """Webhook listener for Orange Money & MTN Mobile Money payment confirmations."""
    data = await request.json()
    # Process payment notification and activate organization subscription
    status_payment = data.get("status", "SUCCESS")
    org_code = data.get("org_code")
    
    if status_payment == "SUCCESS" and org_code:
        org = db.query(Organization).filter(Organization.code == org_code).first()
        if org:
            org.status = "ACTIVE"
            org.subscription_expires_at = datetime.utcnow() + timedelta(days=30)
            db.commit()
            return {"status": "ok", "processed": True}

    return {"status": "received", "processed": False}
