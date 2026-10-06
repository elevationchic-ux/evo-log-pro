"""Features sectorielles : la ou le resultat etait invente est desormais REEL.

- Tracabilite lot/serie, releves de temperature et consignations sont persistes
  dans de vraies tables portees par tenant ; les alertes cold-chain sont DERIVEES
  des mesures enregistrees (rien n'est genere sans mesure).
- FDS matieres dangereues : lecture reellement indexee par code ONU/designation
  dans la table marchandises_dangereuses (plus de constante UNIQUE pour tout code).
- Signature electronique QUALIFIEE et certificats d'export : actes externes
  (PKI/AC, Chambre de Commerce/MINADER) -> connecteur pilote par configuration
  (appel reel si gateway fournie, 503 honnete sinon). Jamais de preuve inventee.
- OCR : moteur local reel (Tesseract) si disponible ; contenu textuel decode
  reellement ; sinon 503 (aucun champ code en dur).
- Balance pont-bascule et parite EUR/XAF : calculs deterministes legitimes conserves.
"""
import hashlib

from fastapi import APIRouter, Depends, status, UploadFile, File, HTTPException
from pydantic import BaseModel, Field
from typing import Optional
from sqlalchemy.orm import Session

from app.database import get_db
from app.utils.tenant import get_current_tenant_context, TenantContext, require_module_access
from app.utils.external import call_provider, provider_configured
from app.models.advanced_crud import LotSerial, TemperatureReading, Consignation
from app.models.acconage import MarchandiseDangereuse

router = APIRouter()


def _org(context: TenantContext):
    return getattr(context, "organization_id", None)


# ─── N29: Batch / Lot & Serial Tracking (persistance reelle) ───
class BatchTrackSchema(BaseModel):
    batch_number: str = Field(..., example="LOT-CACAO-2026-08A")
    serial_number: Optional[str] = Field(None, example="SN-MOTOR-9912")
    article_code: str = Field(..., example="ART-FEVE-CACAO")
    expiry_date: Optional[str] = Field(None, example="2027-12-31")
    humidity_rate_percentage: Optional[float] = Field(None, example=7.2)


@router.post("/batch-track", status_code=status.HTTP_201_CREATED,
             dependencies=[Depends(require_module_access("magasin"))])
def register_batch_item(
    payload: BatchTrackSchema,
    context: TenantContext = Depends(get_current_tenant_context),
    db: Session = Depends(get_db),
):
    """N29 tracabilite lot : ecriture REELLE en base (lot_serial_tracks)."""
    row = LotSerial(
        organization_id=_org(context),
        enregistre_par=getattr(context.user, "id", None),
        **payload.model_dump(),
    )
    db.add(row)
    db.commit()
    db.refresh(row)
    return {
        "id": row.id,
        "batch_number": row.batch_number,
        "serial_number": row.serial_number,
        "article_code": row.article_code,
        "expiry_date": row.expiry_date,
        "persiste": True,
    }


@router.get("/batch-track", dependencies=[Depends(require_module_access("magasin"))])
def list_batch_items(
    article_code: Optional[str] = None,
    context: TenantContext = Depends(get_current_tenant_context),
    db: Session = Depends(get_db),
):
    query = db.query(LotSerial)
    if _org(context) is not None:
        query = query.filter(LotSerial.organization_id == _org(context))
    if article_code:
        query = query.filter(LotSerial.article_code == article_code)
    return [
        {
            "id": r.id, "batch_number": r.batch_number, "serial_number": r.serial_number,
            "article_code": r.article_code, "expiry_date": r.expiry_date,
            "humidity_rate_percentage": float(r.humidity_rate_percentage or 0),
        }
        for r in query.order_by(LotSerial.created_at.desc()).limit(500).all()
    ]


# ─── N30: Weighbridge / Pont-Bascule (calcul legitime) ───
class WeighbridgeTicketSchema(BaseModel):
    ticket_number: str = Field(..., example="PONT-2026-045")
    vehicle_immat: str = Field(..., example="LT-123-XY")
    gross_weight_kg: float = Field(..., example=42500.0)
    tare_weight_kg: float = Field(..., example=14200.0)
    commodity: str = Field("CIMENT_VRAC", example="CIMENT_VRAC")


@router.post("/weighbridge", dependencies=[Depends(require_module_access("transport"))])
def record_weighbridge_ticket(payload: WeighbridgeTicketSchema, context: TenantContext = Depends(get_current_tenant_context)):
    """N30: Calcule le poids net a partir du ticket saisi (calcul determinant, legitime)."""
    net_weight_kg = payload.gross_weight_kg - payload.tare_weight_kg
    return {
        "status": "success",
        "ticket_number": payload.ticket_number,
        "gross_weight_kg": payload.gross_weight_kg,
        "tare_weight_kg": payload.tare_weight_kg,
        "net_weight_kg": net_weight_kg,
        "net_weight_tons": net_weight_kg / 1000.0,
        "variance_status": "WITHIN_TOLERANCE" if net_weight_kg > 0 else "INVALID_WEIGHT",
    }


# ─── N31: Cold Chain — mesures saisies + alertes DERIVEES ───
class TemperatureReadingSchema(BaseModel):
    container_ref: str = Field(..., example="TCLU1234567")
    zone: Optional[str] = Field(None, example="Chambre froide 2")
    temperature_c: float = Field(..., example=-18.4)
    seuil_min_c: Optional[float] = Field(-25.0, example=-25.0)
    seuil_max_c: Optional[float] = Field(-15.0, example=-15.0)
    capteur_id: Optional[str] = Field(None, example="SONDE-DHL-07")


@router.post("/cold-chain/readings", status_code=status.HTTP_201_CREATED,
             dependencies=[Depends(require_module_access("magasin"))])
def enregistrer_releve_temperature(
    payload: TemperatureReadingSchema,
    context: TenantContext = Depends(get_current_tenant_context),
    db: Session = Depends(get_db),
):
    """Depot REEL d'une mesure de sonde (manuel ou import). Les alertes sont
    calculees a partir de ces mesures en enregistrees."""
    row = TemperatureReading(organization_id=_org(context), **payload.model_dump())
    db.add(row)
    db.commit()
    db.refresh(row)
    rupture = (
        (row.seuil_max_c is not None and row.temperature_c > row.seuil_max_c)
        or (row.seuil_min_c is not None and row.temperature_c < row.seuil_min_c)
    )
    return {"id": row.id, "container_ref": row.container_ref,
            "temperature_c": float(row.temperature_c), "rupture_chaines": bool(rupture),
            "persiste": True}


@router.get("/cold-chain-alerts", dependencies=[Depends(require_module_access("magasin"))])
def get_cold_chain_alerts(
    context: TenantContext = Depends(get_current_tenant_context),
    db: Session = Depends(get_db),
):
    """Alertes chaine du froid DERIVEES des mesures reellement enregistrees
    (temperature hors seuils). Aucune alerte inventee : si aucune mesure, liste vide."""
    query = db.query(TemperatureReading)
    if _org(context) is not None:
        query = query.filter(TemperatureReading.organization_id == _org(context))
    alerts = []
    for r in query.order_by(TemperatureReading.created_at.desc()).limit(2000).all():
        hors = (
            (r.seuil_max_c is not None and r.temperature_c > r.seuil_max_c)
            or (r.seuil_min_c is not None and r.temperature_c < r.seuil_min_c)
        )
        if hors:
            alerts.append({
                "container_ref": r.container_ref, "zone": r.zone,
                "temperature_c": float(r.temperature_c),
                "seuil_min_c": float(r.seuil_min_c) if r.seuil_min_c is not None else None,
                "seuil_max_c": float(r.seuil_max_c) if r.seuil_max_c is not None else None,
                "capteur_id": r.capteur_id,
                "mesure_le": r.mesure_le.isoformat() if r.mesure_le else None,
            })
    return {
        "alertes": alerts,
        "nombre": len(alerts),
        "source": "temperature_readings (mesures saisies/importees)",
        "note_capteurs": "Sonde IoT non branchee ; alertes basees sur les mesures enregistrees.",
    }


# ─── N32: Hazmat — lecture reellement indexee (plus de constante) ───
@router.get("/hazmat-fds/{article_code}", dependencies=[Depends(require_module_access("qhse"))])
def get_hazmat_safety_data_sheet(article_code: str, db: Session = Depends(get_db)):
    """FDS matieres dangereuses lue dans la table marchandises_dangereuses, indexee
    par numero ONU ou designation. 404 honnete si aucune matiere ne correspond
    (remplace l'ancienne constante UN-1203 retournee pour tout code)."""
    code = (article_code or "").strip()
    row = db.query(MarchandiseDangereuse).filter(
        MarchandiseDangereuse.numero_onu == code
    ).first()
    if row is None:
        row = db.query(MarchandiseDangereuse).filter(
            MarchandiseDangereuse.designation.ilike(f"%{code}%")
        ).first()
    if row is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=(
                f"Aucune matiere dangereuse en base pour '{code}'. La FDS n'est "
                "pas inventee : enregistrer la matiere (numero ONU/designation) d'abord."
            ),
        )
    return {
        "numero_onu": row.numero_onu,
        "classe_imdg": row.classe_imdg,
        "designation": row.designation,
        "groupe_emballage": row.groupe_emballage,
        "etiquette": row.etiquette,
        "mesures_speciales": row.mesures_speciales,
        "source_reelle": True,
    }


# ─── N33: Qualified E-Signature (acte externe, connecteur) ───
class QualifiedSignatureSchema(BaseModel):
    pod_id: str = Field(..., example="EPOD-2026-0099")
    signer_name: str = Field(..., example="M. Paul Nsonga (Chef de Dépôt)")
    signature_base64: str = Field(..., example="data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAA...")


@router.post("/qualified-signature", dependencies=[Depends(require_module_access("transport"))])
def sign_epod_qualified(payload: QualifiedSignatureSchema, context: TenantContext = Depends(get_current_tenant_context)):
    """Signature electronique QUALIFIEE + horodatage RFC3161 via le prestataire PKI
    configure. Non configure => 503 honnete (un hash local n'est pas une preuve
    opposable ; on ne la fait pas passer pour une signature qualifiee)."""
    content = hashlib.sha256(
        f"{payload.pod_id}|{payload.signer_name}".encode("utf-8")
    ).hexdigest()
    result = call_provider(
        "QUALIFIED_SIGN",
        "Apposition d'une signature electronique qualifiee horodatee",
        path="/sign",
        payload={
            "pod_id": payload.pod_id,
            "signer_name": payload.signer_name,
            "content_sha256": content,
        },
    )
    return {"statut": "TRANSMIS_AC", "empreinte_locale_sha256": content, **result}


# ─── N34: OCR Archive Ingestion (moteur local reel) ───
@router.post("/ocr-ingest", dependencies=[Depends(require_module_access("documents"))])
async def process_ocr_paper_document(file: UploadFile = File(...)):
    """OCR reel selon le support : texte decode reelement pour un mime text/* ;
    sinon moteur Tesseract si disponible ; 503 si aucun OCR (aucun champ code en dur)."""
    content = await file.read()
    if not content:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Fichier vide")
    mime = (file.content_type or "").lower()
    if mime.startswith("text/") or mime == "application/csv":
        try:
            texte = content.decode("utf-8")
        except UnicodeDecodeError:
            texte = content.decode("latin-1", errors="replace")
        return {"nom_fichier": file.filename, "texte_extrait": texte,
                "longueur": len(texte), "reel": True}
    try:
        import pytesseract
        from PIL import Image
        import io
        image = Image.open(io.BytesIO(content))
        texte = pytesseract.image_to_string(image, lang="fra")
        return {"nom_fichier": file.filename, "texte_extrait": texte,
                "longueur": len(texte), "moteur": "tesseract", "reel": True}
    except Exception:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=(
                "Moteur OCR indisponible pour ce format. Installer pytesseract + "
                "Tesseract et fournir une image. Aucun champ n'est code en dur."
            ),
        )


# ─── N35: Export Customs & Certificates (acte externe, connecteur) ───
@router.get("/export-certificates/{dossier_id}", dependencies=[Depends(require_module_access("douane"))])
def get_export_certificates(dossier_id: str):
    """Certificats d'export (origine CEMAC, phytosanitaire) delivres par une autorite
    externe (Chambre de Commerce / MINADER). Connecteur pilote par configuration :
    appel reel a la gateway si fournie, 503 sinon. Aucun certificat invente."""
    result = call_provider(
        "GOV",
        "Certificats d'export (origine CEMAC, phytosanitaire)",
        path=f"/certificates/{dossier_id}",
        method="GET",
    )
    return result


# ─── N36: Multi-Currency FX Engine (parite fixe legitime) ───
@router.get("/forex-rates")
def get_forex_rates():
    """Parite officielle EUR/XAF (fixe, 655.957) + taux indicatif USD."""
    return {
        "status": "success",
        "base_currency": "XAF",
        "rates": {
            "XAF": 1.0,
            "EUR": 655.957,  # Parite fixe Franc CFA / Euro (ancrage legal)
            "USD": 605.20,   # indicatif, a remplacer par un feed banque temps reel
        },
        "note": "EUR/XAF = parite fixe garantie. USD = indicatif, non temps reel.",
    }


# ─── N37: Pallet & Container Consignment (agrégation reelle) ───
class ConsignationSchema(BaseModel):
    support_ref: str = Field(..., example="PAL-EURO-1200")
    support_type: str = Field("PALETTE", example="PALETTE")
    client_id: Optional[int] = Field(None, example=42)
    quantite: float = Field(50.0, example=50.0)
    valeur_consignation_xaf: float = Field(25000.0, example=25000.0)


@router.post("/consignments", status_code=status.HTTP_201_CREATED,
             dependencies=[Depends(require_module_access("magasin"))])
def enregistrer_consignation(
    payload: ConsignationSchema,
    context: TenantContext = Depends(get_current_tenant_context),
    db: Session = Depends(get_db),
):
    row = Consignation(organization_id=_org(context), **payload.model_dump())
    db.add(row)
    db.commit()
    db.refresh(row)
    return {"id": row.id, "support_ref": row.support_ref, "quantite": float(row.quantite),
            "statut": row.statut, "persiste": True}


@router.get("/consignment-balance", dependencies=[Depends(require_module_access("magasin"))])
def get_consignment_balance(
    context: TenantContext = Depends(get_current_tenant_context),
    db: Session = Depends(get_db),
):
    """Solde des consignations AGGREGEE depuis la table consignations du tenant.
    Sur base vide => vrai solde nul (plus de montants fabriques)."""
    query = db.query(Consignation)
    if _org(context) is not None:
        query = query.filter(Consignation.organization_id == _org(context))
    rows = query.all()
    par_statut = {}
    valeur_totale = 0.0
    for c in rows:
        par_statut[c.statut] = par_statut.get(c.statut, 0) + float(c.quantite or 0)
        valeur_totale += float(c.valeur_consignation_xaf or 0)
    return {
        "supports": len(rows),
        "quantite_par_statut": par_statut,
        "valeur_consignee_totale_xaf": round(valeur_totale, 2),
        "agrege_depuis_la_base": True,
    }
