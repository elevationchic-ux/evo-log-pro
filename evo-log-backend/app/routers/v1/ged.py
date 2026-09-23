from fastapi import APIRouter, Depends, UploadFile, File, Form
from typing import Optional

from app.utils.tenant import get_current_tenant_context, TenantContext, require_module_access
from app.core.not_implemented import not_implemented

router = APIRouter()


# La GED (Gestion Electronique de Documents) complete reste a brancher : depot
# binaire reel (S3/Disque), enregistrement en base (modele Document existe mais
# n'est pas exploite ici), PKI/horodatage qualifie RFC3161 et moteur OCR reel.
# Plutot que de renvoyer de faux succes (documents inventes, hashes/QR simules,
# OCR a valeurs codees en dur), chaque route repond explicitement 501.

@router.get("/documents", dependencies=[Depends(require_module_access("documents"))])
def list_ged_documents(
    category: Optional[str] = None,
    context: TenantContext = Depends(get_current_tenant_context)
):
    """Documents GED : 501 (liste fabricquee, aucune lecture du coffre reel)."""
    not_implemented(
        "Listage du coffre de documents GED",
        "une lecture reelle de la table Document par tenant (les 2 documents "
        "retournes etaient inventes)",
    )


@router.post("/upload", status_code=201, dependencies=[Depends(require_module_access("documents"))])
async def upload_ged_document(
    title: str = Form(...),
    category: str = Form("GENERAL"),
    file: UploadFile = File(...),
    context: TenantContext = Depends(get_current_tenant_context)
):
    """Upload GED : 501 (ne stockait ni le fichier ni l'enregistrement)."""
    not_implemented(
        "Telechargement/archivage d'un document dans la GED",
        "un stockage binaire reel (disque/S3) et l'ecriture de la fiche "
        "Document associee (le succes etait fabrique sans aucune persistance)",
    )


# ============ SIGNATURE ÉLECTRONIQUE AVANCÉE & CACHET SERVEUR ============
@router.post("/signature-electronique/certifier", dependencies=[Depends(require_module_access("documents"))])
def certifier_document_numerique(payload: dict, context: TenantContext = Depends(get_current_tenant_context)):
    """Certification : 501 (SHA-256 local, pas de PKI ni d'horodatage qualifie RFC3161)."""
    not_implemented(
        "Certification par signature electronique qualifiee et horodatage RFC3161",
        "une autorite de certification / PKI et un service d'horodatage qualifie "
        "reels (l'empreinte et le QR Retourne n'ont aucune valeur probante)",
    )


# ============ RECONNAISSANCE OPTIQUE DE CARACTÈRES (OCR) ============
@router.post("/ocr/extraire-texte", dependencies=[Depends(require_module_access("documents"))])
def extraire_metadonnees_ocr(payload: dict, context: TenantContext = Depends(get_current_tenant_context)):
    """OCR : 501 (donnees extraites codees en dur, aucun moteur OCR branche)."""
    not_implemented(
        "Extraction OCR de documents scannes",
        "un veritable moteur OCR (Tesseract/LayoutLM) ; les champs retournes "
        "etaient des donnees TOTAL CAMEROUN codees en dur",
    )


# ============ COFFRE-FORT NUMÉRIQUE ARCHIVAGE LÉGAL 10 ANS ============
@router.get("/coffre-fort/audit-log/{document_id}", dependencies=[Depends(require_module_access("documents"))])
def consulter_coffre_fort_audit(document_id: str, context: TenantContext = Depends(get_current_tenant_context)):
    """Coffre-fort legal : 501 (journal d'audit immuable invente, sans backend)."""
    not_implemented(
        "Consultation du journal d'archivage legal infalsifiable",
        "un coffre-fort numerique audite (journal append-only + preuves de chainage) "
        "conforme NF Z42-013 (les evenements retournes etaient fabriques)",
    )
