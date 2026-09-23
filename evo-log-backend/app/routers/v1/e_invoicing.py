from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from pydantic import BaseModel, Field
from typing import List, Optional
from datetime import datetime
import hashlib

from app.database import get_db
from app.utils.tenant import get_current_tenant_context, TenantContext, require_module_access
from app.core.not_implemented import not_implemented

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
    Signature electronique normalisee DGI : 501 (un simple SHA-256 local ne vaut
    pas une signature qualifiee conforme DGI).
    """
    not_implemented(
        "Signature de facture electronique normalisee (DGI Cameroun)",
        "un reel service de signature qualifiee / d'horodatage et l'integration "
        "API DGI (le hash SHA-256 local n'a aucune valeur fiscale opposable)",
    )

@router.get("/verify/{fiscal_hash}")
def verify_e_invoice(fiscal_hash: str):
    """Verification de facture : 501 (renvoyait VALID pour n'importe quel hash)."""
    not_implemented(
        "Verification publique d'une signature fiscale",
        "un registre verifiable des hashes emis (la reponse renvoyait systemati-"
        "quement VALID, ce qui est faux et dangereux)",
    )
