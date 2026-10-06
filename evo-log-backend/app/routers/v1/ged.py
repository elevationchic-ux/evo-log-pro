import hashlib
import uuid
from datetime import datetime

from fastapi import APIRouter, Depends, UploadFile, File, Form, HTTPException, status
from sqlalchemy.orm import Session
from typing import Optional

from app.database import get_db
from app.utils.tenant import get_current_tenant_context, TenantContext, require_module_access
from app.models.documents import (
    Document, SignatureDocument, SceauNumerique, HistoriqueDocument, ArchivageLegal,
    AnalyseOCR, TypeDocument, StatutDocument,
)
from app.services.documents_service import HistoriqueDocumentService

router = APIRouter()


def _scope_documents(context: TenantContext, query):
    """Un user normal ne voit que ses documents ; un superadmin voit le coffre entier."""
    if getattr(context.user, "is_superadmin", False):
        return query
    return query.filter(Document.proprietaire_id == context.user.id)


def _resolve_type(category: Optional[str]):
    if not category:
        return None
    try:
        return TypeDocument[category.upper()]
    except KeyError:
        try:
            return TypeDocument(category.lower())
        except ValueError:
            return TypeDocument.AUTRE


@router.get("/documents", dependencies=[Depends(require_module_access("documents"))])
def list_ged_documents(
    category: Optional[str] = None,
    context: TenantContext = Depends(get_current_tenant_context),
    db: Session = Depends(get_db),
):
    """Coffre GED reel : lecture de la table Document, filtre par tenant (proprietaire)."""
    query = _scope_documents(context, db.query(Document))
    doc_type = _resolve_type(category)
    if doc_type is not None:
        query = query.filter(Document.type_document == doc_type)
    rows = query.order_by(Document.created_at.desc()).all()
    return [
        {
            "id": d.id,
            "numero_document": d.numero_document,
            "titre": d.titre,
            "type_document": d.type_document.value if d.type_document else None,
            "statut": d.statut.value if d.statut else None,
            "nom_fichier": d.nom_fichier,
            "type_mime": d.type_mime,
            "taille_octets": d.taille_octets,
            "checksum": d.checksum,
            "version": d.version,
            "confidentiel": d.confidentiel,
            "date_creation": d.date_creation.isoformat() if d.date_creation else None,
        }
        for d in rows
    ]


@router.post("/upload", status_code=status.HTTP_201_CREATED,
             dependencies=[Depends(require_module_access("documents"))])
async def upload_ged_document(
    title: str = Form(...),
    category: str = Form("GENERAL"),
    file: UploadFile = File(...),
    context: TenantContext = Depends(get_current_tenant_context),
    db: Session = Depends(get_db),
):
    """Telechargement reel : octets persistes + empreinte SHA-256 calculee + fiche Document."""
    content = await file.read()
    if not content:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Fichier vide")
    checksum = hashlib.sha256(content).hexdigest()
    doc = Document(
        numero_document=f"GED-{uuid.uuid4().hex[:12].upper()}",
        type_document=_resolve_type(category) or TypeDocument.AUTRE,
        titre=title,
        proprietaire_id=context.user.id,
        fichier=content,
        nom_fichier=file.filename,
        type_mime=file.content_type,
        taille_octets=len(content),
        emplacement_stockage="db",
        checksum=checksum,
        statut=StatutDocument.BROUILLON,
        version=1,
        version_active=True,
        cree_par=str(context.user.id),
    )
    db.add(doc)
    db.commit()
    db.refresh(doc)
    HistoriqueDocumentService.enregistrer_action(
        db, document_id=doc.id, action="creation", utilisateur_id=context.user.id,
        details=f"Depot {file.filename} ({len(content)} octets)",
    )
    return {
        "id": doc.id,
        "numero_document": doc.numero_document,
        "titre": doc.titre,
        "nom_fichier": doc.nom_fichier,
        "taille_octets": doc.taille_octets,
        "checksum": doc.checksum,
        "persiste": True,
    }


@router.post("/signature-electronique/certifier",
             dependencies=[Depends(require_module_access("documents"))])
def certifier_document_numerique(
    payload: dict,
    context: TenantContext = Depends(get_current_tenant_context),
    db: Session = Depends(get_db),
):
    """SCELLAGE cryptographique reel : empreinte SHA-256 calculee sur les octets
    archives, SignatureDocument + SceauNumerique persistes.

    Portee honnete : c'est un sceau d'integrite infalsifiable (empreinte reelle du
    contenu + horodatage serveur), PAS une signature electronique qualifiee having
    valeur legale vis-a-vis d'un tiers (cela exigerait une autorite de certification
    externe, configuree separement)."""
    document_id = payload.get("document_id")
    doc = _scope_documents(context, db.query(Document)).filter(Document.id == document_id).first()
    if not doc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Document introuvable")
    if not doc.fichier:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Aucun contenu binaire a sceller")
    empreinte = hashlib.sha256(doc.fichier).hexdigest()
    # cohérence : l'empreinte doit correspondre au checksum enregistre
    if doc.checksum and doc.checksum != empreinte:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT,
                            detail="Empreinte differente du checksum archive (contenu altéré)")
    now = datetime.utcnow()
    signature = SignatureDocument(
        document_id=doc.id,
        signataire_id=context.user.id,
        type_signature="numerique",
        date_signature=now,
        empreinte=empreinte,
        raison=payload.get("raison", "certification d'integrite"),
        statut="valide",
    )
    db.add(signature)
    numero_sceau = f"SC-{uuid.uuid4().hex[:16].upper()}"
    sceau = SceauNumerique(
        document_id=doc.id,
        numero_sceau=numero_sceau,
        type_sceau="permanent",
        createur_id=context.user.id,
        date_creation=now,
        contenu_sceau=empreinte,
        statut="actif",
    )
    db.add(sceau)
    db.commit()
    return {
        "document_id": doc.id,
        "empreinte_sha256": empreinte,
        "numero_sceau": numero_sceau,
        "horodatage": now.isoformat(),
        "type": "sceau_integrite_local",
        "valeur_legale": "signature qualifiee non applicable (aucune AC externe configuree)",
    }


@router.post("/ocr/extraire-texte", dependencies=[Depends(require_module_access("documents"))])
def extraire_metadonnees_ocr(
    payload: dict,
    context: TenantContext = Depends(get_current_tenant_context),
    db: Session = Depends(get_db),
):
    """OCR reel selon le support :

    - contenu textuel (mime text/*) : extraction reelle des octets decodees.
    - image/PDF : moteur Tesseract si disponible ; sinon 503 explicite (aucune
      donnee n'est inventee)."""
    document_id = payload.get("document_id")
    doc = _scope_documents(context, db.query(Document)).filter(Document.id == document_id).first()
    if not doc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Document introuvable")
    mime = (doc.type_mime or "").lower()
    texte = None
    if mime.startswith("text/") or mime == "application/csv":
        try:
            texte = doc.fichier.decode("utf-8") if doc.fichier else ""
        except UnicodeDecodeError:
            texte = doc.fichier.decode("latin-1", errors="replace") if doc.fichier else ""
        confiance = 1.0
    else:
        try:
            import pytesseract  # noqa: F401
            from PIL import Image  # noqa: F401
            import io
            image = Image.open(io.BytesIO(doc.fichier))
            texte = pytesseract.image_to_string(image, lang=payload.get("langue", "fra"))
            confiance = None
        except Exception:
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail=(
                    "Moteur OCR indisponible pour ce format. Installer pytesseract + "
                    "Tesseract et fournir une image ; aucun texte n'est invente."
                ),
            )
    analyse = AnalyseOCR(
        document_id=doc.id,
        langue=payload.get("langue", "fra"),
        texte_extrait=texte,
        confidence=confiance,
        statut="succes",
    )
    db.add(analyse)
    db.commit()
    db.refresh(analyse)
    return {
        "analyse_id": analyse.id,
        "document_id": doc.id,
        "texte_extrait": texte,
        "longueur": len(texte or ""),
        "reel": True,
    }


@router.get("/coffre-fort/audit-log/{document_id}",
            dependencies=[Depends(require_module_access("documents"))])
def consulter_coffre_fort_audit(
    document_id: str,
    context: TenantContext = Depends(get_current_tenant_context),
    db: Session = Depends(get_db),
):
    """Journal d'audit reel : HistoriqueDocument + ArchivageLegal lus en base."""
    doc = _scope_documents(context, db.query(Document)).filter(Document.id == document_id).first()
    if not doc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Document introuvable")
    actions = db.query(HistoriqueDocument).filter(
        HistoriqueDocument.document_id == doc.id
    ).order_by(HistoriqueDocument.date_action.asc()).all()
    archivages = db.query(ArchivageLegal).filter(ArchivageLegal.document_id == doc.id).all()
    return {
        "document_id": doc.id,
        "numero_document": doc.numero_document,
        "empreinte_actuelle": doc.checksum,
        "evenements": [
            {
                "date": h.date_action.isoformat() if h.date_action else None,
                "action": h.action,
                "utilisateur_id": h.utilisateur_id,
                "details": h.details,
                "ip": h.adresse_ip,
            }
            for h in actions
        ],
        "archivages_legal": [
            {
                "numero_archivage": a.numero_archivage,
                "type": a.type_archivage,
                "duree_conservation_mois": a.duree_conservation,
                "date_expiration": a.date_expiration.isoformat() if a.date_expiration else None,
                "conformite": a.conformite,
                "statut": a.statut,
            }
            for a in archivages
        ],
    }
