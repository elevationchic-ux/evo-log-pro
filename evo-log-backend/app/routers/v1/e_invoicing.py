import hashlib

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from pydantic import BaseModel, Field

from app.database import get_db
from app.core.config import settings
from app.utils.tenant import get_current_tenant_context, TenantContext, require_module_access
from app.models.advanced_crud import EInvoiceSignature

router = APIRouter()


class EInvoiceSignRequestSchema(BaseModel):
    invoice_number: str = Field(..., example="EVO-INV-2026-0045")
    client_niu: str = Field(..., example="M081912345678A")
    total_ht: float = Field(..., example=1000000.0)
    total_tva: float = Field(..., example=192500.0)  # 19.25% TVA CEMAC
    total_ttc: float = Field(..., example=1192500.0)


def _canonical(payload: EInvoiceSignRequestSchema) -> str:
    """Chaine normalisee deterministe (seule source de l'empreinte)."""
    return "|".join([
        payload.invoice_number.strip(),
        payload.client_niu.strip(),
        f"{payload.total_ht:.2f}",
        f"{payload.total_tva:.2f}",
        f"{payload.total_ttc:.2f}",
    ])


@router.post("/sign-invoice", dependencies=[Depends(require_module_access("finance"))])
def sign_normalized_e_invoice(
    payload: EInvoiceSignRequestSchema,
    context: TenantContext = Depends(get_current_tenant_context),
    db: Session = Depends(get_db),
):
    """Sceau d'integrite SHA-256 REEL calcule sur le contenu normalise, persiste
    dans un registre verifiable.

    Portee honnete : l'empreinte est une signature d'integrite locale. La valeur
    fiscale OPPOSABLE (DGI Cameroun) necessite le connecteur certifie ; il est
    active seulement si E_INVOICING_DGI_ENABLED, auquel cas le provider est marque
    « dgi ». Sans ca, on ne pretend pas a l'opposabilite."""
    content = _canonical(payload)
    fiscal_hash = hashlib.sha256(content.encode("utf-8")).hexdigest()

    existing = db.query(EInvoiceSignature).filter(
        EInvoiceSignature.fiscal_hash == fiscal_hash
    ).first()
    if existing:
        return {
            "invoice_number": existing.invoice_number,
            "fiscal_hash": existing.fiscal_hash,
            "algorithm": existing.algorithm,
            "provider": existing.provider,
            "statut": existing.statut,
            "deja_scelle": True,
        }

    provider = "dgi" if settings.E_INVOICING_DGI_ENABLED else "local"
    statut = "transmis" if settings.E_INVOICING_DGI_ENABLED else "scelle"
    rec = EInvoiceSignature(
        organization_id=context.organization_id,
        invoice_number=payload.invoice_number,
        client_niu=payload.client_niu,
        total_ht=payload.total_ht,
        total_tva=payload.total_tva,
        total_ttc=payload.total_ttc,
        fiscal_hash=fiscal_hash,
        algorithm="SHA-256",
        provider=provider,
        statut=statut,
    )
    db.add(rec)
    db.commit()
    db.refresh(rec)
    return {
        "invoice_number": rec.invoice_number,
        "fiscal_hash": rec.fiscal_hash,
        "algorithm": rec.algorithm,
        "provider": provider,
        "statut": statut,
        "opposable_dgi": provider == "dgi",
        "note": (
            "Sceau d'integrite local verifiable. Opposabilite DGI non garantie sans "
            "connecteur certifie active."
            if provider == "local" else
            "Connecteur DGI active : transmission a finaliser par le module certifie."
        ),
    }


@router.get("/verify/{fiscal_hash}")
def verify_e_invoice(fiscal_hash: str, db: Session = Depends(get_db)):
    """Verification HONNETE contre le registre reel : renvoie VALID uniquement si
    l'empreinte a ete emise et persistee. Un hash inconnu renvoie INVALID (plus de
    « toujours VALID »)."""
    h = (fiscal_hash or "").strip().lower()
    rec = db.query(EInvoiceSignature).filter(EInvoiceSignature.fiscal_hash == h).first()
    if not rec:
        return {
            "fiscal_hash": fiscal_hash,
            "statut": "INVALID",
            "valide": False,
            "motif": "Empreinte absente du registre des factures scellees.",
        }
    return {
        "fiscal_hash": rec.fiscal_hash,
        "statut": "VALID",
        "valide": True,
        "invoice_number": rec.invoice_number,
        "client_niu": rec.client_niu,
        "total_ttc": float(rec.total_ttc or 0),
        "algorithm": rec.algorithm,
        "provider": rec.provider,
        "signed_at": rec.signed_at.isoformat() if rec.signed_at else None,
        "opposable_dgi": rec.provider == "dgi",
    }
