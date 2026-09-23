from fastapi import APIRouter, Depends, status, UploadFile, File
from pydantic import BaseModel, Field
from typing import Optional

from app.utils.tenant import get_current_tenant_context, TenantContext, require_module_access
from app.core.not_implemented import not_implemented

router = APIRouter()

# Ce routeur "features sectorielles" melait calculs legitimes et donnees
# fabricquees. On garde les calculs/reference reels (balance pont-bascule,
# parite fixe EUR/XAF) et on renvoie 501 partout ou le resultat etait invente
# (alertes cold-chain, FDS, certificats, signatures qualifiees, OCR, consignations).


# ─── N29: Batch / Lot & Serial Tracking ───
class BatchTrackSchema(BaseModel):
    batch_number: str = Field(..., example="LOT-CACAO-2026-08A")
    serial_number: Optional[str] = Field(None, example="SN-MOTOR-9912")
    article_code: str = Field(..., example="ART-FEVE-CACAO")
    expiry_date: Optional[str] = Field(None, example="2027-12-31")
    humidity_rate_percentage: Optional[float] = Field(None, example=7.2)


@router.post("/batch-track", dependencies=[Depends(require_module_access("magasin"))])
def register_batch_item(payload: BatchTrackSchema, context: TenantContext = Depends(get_current_tenant_context)):
    """N29 tracabilite lot : 501 (ne persistait rien, succes fabrique)."""
    not_implemented(
        "Enregistrement d'un lot/numero de serie pour tracabilite",
        "une table de lots/series portee par le tenant (l'ID retourne etait un "
        "simple horodatage, rien n'etait ecrit)",
    )


# ─── N30: Weighbridge / Pont-Bascule ───
class WeighbridgeTicketSchema(BaseModel):
    ticket_number: str = Field(..., example="PONT-2026-045")
    vehicle_immat: str = Field(..., example="LT-123-XY")
    gross_weight_kg: float = Field(..., example=42500.0)  # Poids Brut
    tare_weight_kg: float = Field(..., example=14200.0)   # Poids Taré (Véhicule à vide)
    commodity: str = Field("CIMENT_VRAC", example="CIMENT_VRAC")


@router.post("/weighbridge", dependencies=[Depends(require_module_access("transport"))])
def record_weighbridge_ticket(payload: WeighbridgeTicketSchema, context: TenantContext = Depends(get_current_tenant_context)):
    """N30: Calcule le poids net a partir du ticket saisi (calcul determinant, legitime)."""
    net_weight_kg = payload.gross_weight_kg - payload.tare_weight_kg
    net_weight_tons = net_weight_kg / 1000.0
    return {
        "status": "success",
        "ticket_number": payload.ticket_number,
        "gross_weight_kg": payload.gross_weight_kg,
        "tare_weight_kg": payload.tare_weight_kg,
        "net_weight_kg": net_weight_kg,
        "net_weight_tons": net_weight_tons,
        "variance_status": "WITHIN_TOLERANCE" if net_weight_kg > 0 else "INVALID_WEIGHT",
    }


# ─── N31: Cold Chain Temperature Alarm ───
@router.get("/cold-chain-alerts", dependencies=[Depends(require_module_access("magasin"))])
def get_cold_chain_alerts(context: TenantContext = Depends(get_current_tenant_context)):
    """Alertes chaine du froid : 501 (alerte inventee, aucun capteur branche)."""
    not_implemented(
        "Alertes de rupture de la chaine du froid",
        "un flux de capteurs IoT/sonde de temperature reel par conteneur "
        "(l'alerte retournee etait fabriquee)",
    )


# ─── N32: Hazmat & Extended HSE ───
@router.get("/hazmat-fds/{article_code}", dependencies=[Depends(require_module_access("qhse"))])
def get_hazmat_safety_data_sheet(article_code: str):
    """FDS matieres dangereuses : 501 (retournait la meme fiche UN-1203 pour tout code)."""
    not_implemented(
        "Fiche de Donnees de Securite (FDS) matieres dangereuses",
        "une base reglementaire reellement indexee par code article/ONU "
        "(la fiche retournee etait une constante independante de l'article)",
    )


# ─── N33: Qualified E-Signature ───
class QualifiedSignatureSchema(BaseModel):
    pod_id: str = Field(..., example="EPOD-2026-0099")
    signer_name: str = Field(..., example="M. Paul Nsonga (Chef de Dépôt)")
    signature_base64: str = Field(..., example="data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAA...")


@router.post("/qualified-signature", dependencies=[Depends(require_module_access("transport"))])
def sign_epod_qualified(payload: QualifiedSignatureSchema, context: TenantContext = Depends(get_current_tenant_context)):
    """Signature qualifiee : 501 (SHA-256 local, aucune valeur probante/PKI)."""
    not_implemented(
        "Apposition d'une signature electronique qualifiee horodatee",
        "un prestataire de signature qualifiee / PKI et un horodatage RFC3161 "
        "reels (le hash SHA-256 local n'est pas une preuve opposable)",
    )


# ─── N34: OCR Archive Ingestion ───
@router.post("/ocr-ingest", dependencies=[Depends(require_module_access("documents"))])
async def process_ocr_paper_document(file: UploadFile = File(...)):
    """OCR archivage : 501 (champs extraits codes en dur, aucun moteur OCR)."""
    not_implemented(
        "Numerisation/OCR d'archives papier",
        "un veritable moteur OCR (Tesseract/LayoutLM) ; les champs retournes "
        "etaient une facture codee en dur",
    )


# ─── N35: Export Customs & Specific Certificates ───
@router.get("/export-certificates/{dossier_id}", dependencies=[Depends(require_module_access("douane"))])
def get_export_certificates(dossier_id: str):
    """Certificats export : 501 (certificats inventes, identiques pour tout dossier)."""
    not_implemented(
        "Certificats d'export (origine CEMAC, phytosanitaire)",
        "une source reelle (issued by Chambre de Commerce / MINADER) rattachee "
        "au dossier (les certificats retournes etaient fabriques)",
    )


# ─── N36: Multi-Currency FX Engine ───
@router.get("/forex-rates")
def get_forex_rates():
    """N36: Parite officielle EUR/XAF (fixe, 655.957) + taux indicatif USD.

    Reference statique documentee ; le taux EUR/XAF est une parite fixe legale.
    Pour des taux flottants a jour, brancher un feed banque (BEAC/EC) (todo).
    """
    return {
        "status": "success",
        "base_currency": "XAF",
        "rates": {
            "XAF": 1.0,
            "EUR": 655.957,  # Parité fixe Franc CFA / Euro (ancrage legal)
            "USD": 605.20,   # indicatif, a remplacer par un feed banque temps reel
        },
        "note": "EUR/XAF = parite fixe garantie. USD = indicatif, non temps reel.",
    }


# ─── N37: Pallet & Container Consignment ───
@router.get("/consignment-balance", dependencies=[Depends(require_module_access("magasin"))])
def get_consignment_balance(context: TenantContext = Depends(get_current_tenant_context)):
    """Solde consignations : 501 (consignations inventees, aucune table)."""
    not_implemented(
        "Suivi des palettes/conteneurs consignes",
        "des agrements reels depuis les tables de consignation par tenant "
        "(les montants retournes etaient fabriques)",
    )
