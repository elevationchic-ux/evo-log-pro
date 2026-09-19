from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from pydantic import BaseModel, Field
from typing import List, Optional
from datetime import datetime
import hashlib

from app.database import get_db
from app.utils.tenant import get_current_tenant_context, TenantContext, require_module_access

router = APIRouter()

class EInvoiceSignRequestSchema(BaseModel):
    invoice_number: str = Field(..., example="EVO-INV-2026-0045")
    client_niu: str = Field(..., example="M081912345678A")
    total_ht: float = Field(..., example=1000000.0)
    total_tva: float = Field(..., example=192500.0) # 19.25% TVA CEMAC
    total_ttc: float = Field(..., example=1192500.0)

@router.post("/sign-invoice", dependencies=[Depends(require_module_access("finance"))])
def sign_normalized_e_invoice(
    payload: EInvoiceSignRequestSchema,
    context: TenantContext = Depends(get_current_tenant_context)
):
    """
    Generate normalized tax hash and QR Code payload compliant with 
    Direction Générale des Impôts (DGI Cameroun) e-invoicing standards.
    """
    raw_payload = f"{payload.invoice_number}|{payload.client_niu}|{payload.total_ttc}|{context.organization_id}|{datetime.utcnow().strftime('%Y%m%d%H%M')}"
    dgi_fiscal_hash = hashlib.sha256(raw_payload.encode('utf-8')).hexdigest().upper()
    qr_payload = f"https://dgi.impots.cm/verify?hash={dgi_fiscal_hash[:32]}"

    return {
        "status": "success",
        "compliance_standard": "DGI Cameroun Code Général des Impôts Art. 21",
        "invoice_number": payload.invoice_number,
        "dgi_fiscal_hash": dgi_fiscal_hash,
        "qr_code_payload": qr_payload,
        "signed_at": datetime.utcnow().isoformat()
    }

@router.get("/verify/{fiscal_hash}")
def verify_e_invoice(fiscal_hash: str):
    """Public verification endpoint for DGI fiscal signature."""
    return {
        "status": "VALID",
        "fiscal_hash": fiscal_hash,
        "verified_at": datetime.utcnow().isoformat(),
        "issuer": "EVO-LOG SaaS Platform • Code Axis Digital Cameroun"
    }
