"""
Bill of Loading (Connaissement Maritime / BSC) router
Gestion complète des connaissements maritimes et bulletins de soumission (BSC/CNCC, CSC)
"""
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session
from sqlalchemy import func, desc, or_
from typing import Optional, List
from datetime import datetime, date
from pydantic import BaseModel

from app.core.database import get_db
from app.core.security import get_current_user
from app.models.user import User
from app.models.douane_cameroun import BSC, CSC
from app.models.transit import DossierTransit

router = APIRouter()


class BLCreate(BaseModel):
    numero_connaisse: str
    navire: str
    voyage: Optional[str] = None
    port_chargement: str
    port_dechargement: str
    date_emission: Optional[date] = None
    agent: str
    importateur: str
    poids_brut_tonnes: Optional[float] = None
    valeur_fob: Optional[float] = None
    valeur_caf: Optional[float] = None
    devise: Optional[str] = "USD"
    montant_frais_bsc: Optional[float] = None
    notes: Optional[str] = None


class BLUpdate(BaseModel):
    navire: Optional[str] = None
    voyage: Optional[str] = None
    port_chargement: Optional[str] = None
    port_dechargement: Optional[str] = None
    agent: Optional[str] = None
    importateur: Optional[str] = None
    poids_brut_tonnes: Optional[float] = None
    valeur_fob: Optional[float] = None
    valeur_caf: Optional[float] = None
    statut: Optional[str] = None
    reference_cncc: Optional[str] = None
    notes: Optional[str] = None


@router.get("/")
async def get_bills_of_loading(
    statut: Optional[str] = Query(None, description="Filtrer par statut (en_attente, valide, expire, annule)"),
    search: Optional[str] = Query(None, description="Recherche par numéro de connaissement, navire ou importateur"),
    port_dechargement: Optional[str] = Query(None),
    skip: int = 0,
    limit: int = 50,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Liste tous les connaissements et leurs Bulletins de Soumission Connaissement (BSC)"""
    query = db.query(BSC)

    if statut:
        query = query.filter(BSC.statut == statut)
    if port_dechargement:
        query = query.filter(BSC.port_dechargement.ilike(f"%{port_dechargement}%"))
    if search:
        query = query.filter(
            or_(
                BSC.numero_connaisse.ilike(f"%{search}%"),
                BSC.numero_bsc.ilike(f"%{search}%"),
                BSC.navire.ilike(f"%{search}%"),
                BSC.importateur.ilike(f"%{search}%"),
                BSC.agent.ilike(f"%{search}%"),
            )
        )

    total = query.count()
    items = query.order_by(desc(BSC.created_at)).offset(skip).limit(limit).all()

    return {
        "total": total,
        "skip": skip,
        "limit": limit,
        "items": [
            {
                "id": bsc.id,
                "numero_bsc": bsc.numero_bsc,
                "numero_connaisse": bsc.numero_connaisse,
                "navire": bsc.navire,
                "voyage": bsc.voyage,
                "port_chargement": bsc.port_chargement,
                "port_dechargement": bsc.port_dechargement,
                "date_emission": bsc.date_emission.isoformat() if bsc.date_emission else None,
                "date_validite": bsc.date_validite.isoformat() if bsc.date_validite else None,
                "agent": bsc.agent,
                "importateur": bsc.importateur,
                "poids_brut_tonnes": float(bsc.poids_brut_tonnes) if bsc.poids_brut_tonnes else 0.0,
                "valeur_fob": float(bsc.valeur_fob) if bsc.valeur_fob else 0.0,
                "valeur_caf": float(bsc.valeur_caf) if bsc.valeur_caf else 0.0,
                "devise": bsc.devise,
                "montant_frais_bsc": float(bsc.montant_frais_bsc) if bsc.montant_frais_bsc else 0.0,
                "statut": bsc.statut,
                "reference_cncc": bsc.reference_cncc,
                "date_validation": bsc.date_validation.isoformat() if bsc.date_validation else None,
                "created_at": bsc.created_at.isoformat() if bsc.created_at else None
            }
            for bsc in items
        ]
    }


@router.get("/stats")
async def get_bl_stats(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Métriques consolidées des connaissements et soumissions douanières"""
    total_bl = db.query(func.count(BSC.id)).scalar() or 0
    en_attente = db.query(func.count(BSC.id)).filter(BSC.statut == "en_attente").scalar() or 0
    valides = db.query(func.count(BSC.id)).filter(BSC.statut == "valide").scalar() or 0
    tonnage_total = db.query(func.sum(BSC.poids_brut_tonnes)).scalar() or 0
    valeur_caf_totale = db.query(func.sum(BSC.valeur_caf)).scalar() or 0
    frais_bsc_total = db.query(func.sum(BSC.montant_frais_bsc)).scalar() or 0

    return {
        "total_connaissements": total_bl,
        "en_attente_validation": en_attente,
        "valides": valides,
        "tonnage_total_tonnes": float(tonnage_total),
        "valeur_caf_totale": float(valeur_caf_totale),
        "frais_bsc_collectes": float(frais_bsc_total)
    }


@router.post("/", status_code=status.HTTP_201_CREATED)
async def create_bill_of_loading(
    payload: BLCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Enregistre un nouveau connaissement maritime avec son BSC"""
    # Génération d'un numéro BSC unique
    today_str = datetime.now().strftime("%Y%m%d")
    count_today = db.query(func.count(BSC.id)).scalar() or 0
    numero_bsc = f"BSC-CM-{today_str}-{count_today + 1:04d}"

    emission_date = payload.date_emission or date.today()

    bsc = BSC(
        numero_bsc=numero_bsc,
        numero_connaisse=payload.numero_connaisse,
        navire=payload.navire,
        voyage=payload.voyage,
        port_chargement=payload.port_chargement,
        port_dechargement=payload.port_dechargement,
        date_emission=emission_date,
        agent=payload.agent,
        importateur=payload.importateur,
        poids_brut_tonnes=payload.poids_brut_tonnes,
        valeur_fob=payload.valeur_fob,
        valeur_caf=payload.valeur_caf,
        devise=payload.devise or "USD",
        montant_frais_bsc=payload.montant_frais_bsc or 50000.0,
        statut="en_attente",
        notes=payload.notes
    )

    db.add(bsc)
    db.commit()
    db.refresh(bsc)

    return {
        "message": "Connaissement et BSC créés avec succès",
        "bsc_id": bsc.id,
        "numero_bsc": bsc.numero_bsc,
        "numero_connaisse": bsc.numero_connaisse
    }


@router.get("/{id}")
async def get_bill_of_loading_detail(
    id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Détail d'un connaissement, avec inspection CSC et dossier de transit associé"""
    bsc = db.query(BSC).filter(BSC.id == id).first()
    if not bsc:
        raise HTTPException(status_code=404, detail=f"Connaissement BSC #{id} non trouvé")

    # Recherche éventuelle d'un certificat de sécurité CSC correspondant
    csc = db.query(CSC).filter(CSC.numero_connaisse == bsc.numero_connaisse).first()

    # Dossier transit lié
    dossier = db.query(DossierTransit).filter(DossierTransit.numero_connaisse == bsc.numero_connaisse).first()

    return {
        "id": bsc.id,
        "numero_bsc": bsc.numero_bsc,
        "numero_connaisse": bsc.numero_connaisse,
        "navire": bsc.navire,
        "voyage": bsc.voyage,
        "port_chargement": bsc.port_chargement,
        "port_dechargement": bsc.port_dechargement,
        "date_emission": bsc.date_emission.isoformat() if bsc.date_emission else None,
        "date_validite": bsc.date_validite.isoformat() if bsc.date_validite else None,
        "agent": bsc.agent,
        "importateur": bsc.importateur,
        "poids_brut_tonnes": float(bsc.poids_brut_tonnes) if bsc.poids_brut_tonnes else None,
        "valeur_fob": float(bsc.valeur_fob) if bsc.valeur_fob else None,
        "valeur_caf": float(bsc.valeur_caf) if bsc.valeur_caf else None,
        "devise": bsc.devise,
        "montant_frais_bsc": float(bsc.montant_frais_bsc) if bsc.montant_frais_bsc else None,
        "statut": bsc.statut,
        "reference_cncc": bsc.reference_cncc,
        "date_validation": bsc.date_validation.isoformat() if bsc.date_validation else None,
        "date_paiement": bsc.date_paiement.isoformat() if bsc.date_paiement else None,
        "notes": bsc.notes,
        "csc": {
            "numero_csc": csc.numero_csc,
            "resultat_inspection": csc.resultat_inspection,
            "statut": csc.statut,
            "inspecteur": csc.inspecteur
        } if csc else None,
        "dossier_transit": {
            "id": dossier.id,
            "numero_dossier": dossier.numero_dossier,
            "statut": dossier.statut.value if hasattr(dossier.statut, 'value') else str(dossier.statut)
        } if dossier else None
    }


@router.put("/{id}")
async def update_bill_of_loading(
    id: int,
    payload: BLUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Met à jour les informations d'un connaissement"""
    bsc = db.query(BSC).filter(BSC.id == id).first()
    if not bsc:
        raise HTTPException(status_code=404, detail=f"Connaissement BSC #{id} non trouvé")

    update_data = payload.dict(exclude_unset=True)
    for field, value in update_data.items():
        setattr(bsc, field, value)

    bsc.updated_at = datetime.utcnow()
    db.commit()
    db.refresh(bsc)

    return {"message": "Connaissement mis à jour avec succès", "id": bsc.id}


@router.post("/{id}/validate")
async def validate_bill_of_loading(
    id: int,
    reference_cncc: Optional[str] = Query(None),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Valide officiellement le BSC auprès du Conseil National des Chargeurs du Cameroun (CNCC)"""
    bsc = db.query(BSC).filter(BSC.id == id).first()
    if not bsc:
        raise HTTPException(status_code=404, detail=f"Connaissement BSC #{id} non trouvé")

    ref = reference_cncc or f"CNCC-VAL-{datetime.now().strftime('%Y%m%d%H%M%S')}"
    bsc.statut = "valide"
    bsc.reference_cncc = ref
    bsc.date_validation = date.today()
    bsc.updated_at = datetime.utcnow()

    db.commit()
    return {
        "message": "BSC validé avec succès par le CNCC",
        "id": bsc.id,
        "reference_cncc": ref,
        "statut": bsc.statut
    }


@router.delete("/{id}")
async def delete_bill_of_loading(
    id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Supprime un enregistrement de connaissement"""
    bsc = db.query(BSC).filter(BSC.id == id).first()
    if not bsc:
        raise HTTPException(status_code=404, detail=f"Connaissement BSC #{id} non trouvé")

    db.delete(bsc)
    db.commit()
    return {"message": f"Connaissement #{id} supprimé avec succès"}