"""B2B router - B2B Portal endpoints for multi-tenant SAAS"""
from fastapi import APIRouter, Body, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List

from app.core.database import get_db
from app.core.security import get_current_user
from app.models.user import User
from app.models.tenant import B2BPortal, Company
from app.models.chat import EnterpriseChatMessage
from app.models.new_k_modules import CotationDevis
from app.services.b2b_service import (
    B2BService, DevisService, ChatSupportService, B2BAPIService, B2BReportingService
)
from app.middleware.tenant import TenantSecurity


router = APIRouter(prefix="/b2b", tags=["B2B Portal"])


def _company_or_404(db: Session, company_id: int):
    company = db.query(Company).filter(Company.id == company_id).first()
    if company is None:
        raise HTTPException(status_code=404, detail="Société introuvable")
    return company


@router.get("/portal/{company_id}")
def get_b2b_portal(
    company_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get B2B portal data for a company"""
    TenantSecurity.check_company_access(current_user, company_id)
    _company_or_404(db, company_id)
    
    return B2BService.get_client_data(db, company_id)


@router.get("/portal/{company_id}/quotes")
def get_quotes(
    company_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    TenantSecurity.check_company_access(current_user, company_id)
    _company_or_404(db, company_id)
    return db.query(CotationDevis).filter(
        CotationDevis.company_id == company_id
    ).order_by(CotationDevis.created_at.desc(), CotationDevis.id.desc()).all()


@router.post("/portal/{company_id}/quotes", status_code=status.HTTP_201_CREATED)
def create_quote(
    company_id: int,
    payload: dict = Body(...),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    TenantSecurity.check_company_access(current_user, company_id)
    _company_or_404(db, company_id)
    required = ("reference", "client_nom", "origine", "destination", "nature_fret", "montant_estime_xaf")
    missing = [field for field in required if payload.get(field) in (None, "")]
    if missing:
        raise HTTPException(status_code=422, detail=f"Champs requis: {', '.join(missing)}")
    quote = CotationDevis(
        company_id=company_id,
        reference=payload["reference"],
        client_nom=payload["client_nom"],
        origine=payload["origine"],
        destination=payload["destination"],
        nature_fret=payload["nature_fret"],
        montant_estime_xaf=payload["montant_estime_xaf"],
    )
    db.add(quote)
    db.commit()
    db.refresh(quote)
    return quote


@router.get("/portal/{company_id}/chat")
def get_chat_messages(
    company_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    TenantSecurity.check_company_access(current_user, company_id)
    _company_or_404(db, company_id)
    return db.query(EnterpriseChatMessage).filter(
        EnterpriseChatMessage.company_id == company_id,
        EnterpriseChatMessage.channel_type == "b2b_support",
    ).order_by(EnterpriseChatMessage.created_at.asc(), EnterpriseChatMessage.id.asc()).all()


@router.post("/portal/{company_id}/chat", status_code=status.HTTP_201_CREATED)
def send_chat_message(
    company_id: int,
    payload: dict = Body(...),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    TenantSecurity.check_company_access(current_user, company_id)
    _company_or_404(db, company_id)
    content = str(payload.get("content", "")).strip()
    if not content:
        raise HTTPException(status_code=422, detail="Le message est requis")
    message = EnterpriseChatMessage(
        company_id=company_id,
        sender_id=current_user.id,
        channel_type="b2b_support",
        content=content,
        sender_name_snapshot=current_user.full_name or current_user.username,
    )
    db.add(message)
    db.commit()
    db.refresh(message)
    return message


@router.put("/portal/{company_id}")
def update_b2b_portal(
    company_id: int,
    payload: dict = Body(...),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    TenantSecurity.check_company_access(current_user, company_id)
    portal = db.query(B2BPortal).filter(B2BPortal.company_id == company_id).first()
    if portal is None:
        raise HTTPException(status_code=404, detail="Portail B2B introuvable")
    allowed = {
        "subdomain", "custom_domain", "primary_color", "secondary_color",
        "accent_color", "background_color", "text_color", "logo_url",
        "banner_url", "favicon_url", "enable_chat", "enable_quotes",
        "enable_tracking", "enable_api",
    }
    for key, value in payload.items():
        if key in allowed:
            setattr(portal, key, value)
    db.commit()
    db.refresh(portal)
    return portal


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
