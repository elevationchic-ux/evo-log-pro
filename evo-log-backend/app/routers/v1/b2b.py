"""B2B router - B2B Portal endpoints for multi-tenant SAAS"""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List

from app.core.database import get_db
from app.core.security import get_current_user
from app.models.user import User
from app.services.b2b_service import (
    B2BService, DevisService, ChatSupportService, B2BAPIService, B2BReportingService
)
from app.middleware.tenant import TenantSecurity


router = APIRouter(prefix="/b2b", tags=["B2B Portal"])


@router.get("/portal/{company_id}")
def get_b2b_portal(
    company_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get B2B portal data for a company"""
    TenantSecurity.check_company_access(current_user, company_id)
    
    return B2BService.get_client_data(db, company_id)


@router.get("/portal/{company_id}/invoices")
def get_b2b_invoices(
    company_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get invoices for B2B portal (isolated by company)"""
    TenantSecurity.check_company_access(current_user, company_id)
    
    return B2BService.get_client_invoices(db, company_id)


@router.get("/portal/{company_id}/shipments")
def get_b2b_shipments(
    company_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get shipments for B2B portal (isolated by company)"""
    TenantSecurity.check_company_access(current_user, company_id)
    
    return B2BService.get_client_shipments(db, company_id)


@router.get("/portal/{company_id}/stats")
def get_b2b_stats(
    company_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get statistics for B2B portal (isolated by company)"""
    TenantSecurity.check_company_access(current_user, company_id)
    
    return B2BService.get_client_stats(db, company_id)


@router.post("/portal/{company_id}/quotes")
def create_quote(
    company_id: int,
    numero_devis: str,
    client_id: int,
    montant_estime: float,
    date_validite: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Create a quote for B2B"""
    from datetime import datetime
    TenantSecurity.check_company_access(current_user, company_id)
    
    return DevisService.creer_devis(
        db, company_id, numero_devis, client_id, montant_estime,
        datetime.strptime(date_validite, "%Y-%m-%d").date()
    )


@router.post("/portal/{company_id}/chat")
def send_chat_message(
    company_id: int,
    message: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Send chat message for B2B support"""
    TenantSecurity.check_company_access(current_user, company_id)
    
    return ChatSupportService.envoyer_message(db, company_id, current_user.id, message)


@router.post("/portal/{company_id}/api-key")
def generate_api_key(
    company_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Generate API key for B2B access"""
    TenantSecurity.check_company_access(current_user, company_id)
    
    return B2BAPIService.generer_api_key(db, company_id)


@router.get("/portal/{company_id}/reports/{type_rapport}")
def get_b2b_report(
    company_id: int,
    type_rapport: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get personalized report for B2B portal"""
    TenantSecurity.check_company_access(current_user, company_id)
    
    return B2BReportingService.rapport_personnalise(db, company_id, type_rapport)
