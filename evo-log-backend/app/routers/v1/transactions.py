"""
Transactions router - manages commercial and financial transactions
Système complet de suivi des règlements, encaissements et transactions financières
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
from app.models.finance import Facture, Paiement, PaiementStatus, Compte, EcritureComptable

router = APIRouter()


class TransactionCreate(BaseModel):
    facture_id: int
    montant: float
    mode_paiement: str  # virement, espece, cheque, mobile_money, orange_money, mtn_momo
    reference: Optional[str] = None
    date_paiement: Optional[date] = None
    notes: Optional[str] = None


class TransactionUpdate(BaseModel):
    montant: Optional[float] = None
    mode_paiement: Optional[str] = None
    reference: Optional[str] = None
    statut: Optional[str] = None
    notes: Optional[str] = None


@router.get("/")
async def get_transactions(
    mode_paiement: Optional[str] = Query(None, description="Filtrer par mode de paiement"),
    statut: Optional[str] = Query(None, description="Filtrer par statut"),
    facture_id: Optional[int] = Query(None),
    search: Optional[str] = Query(None, description="Recherche par référence ou notes"),
    skip: int = 0,
    limit: int = 50,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Liste des transactions et règlements financiers avec pagination"""
    query = db.query(Paiement).join(Facture, Paiement.facture_id == Facture.id)
    if not current_user.is_superuser:
        query = query.filter(
            Paiement.company_id == current_user.company_id,
            Facture.company_id == current_user.company_id,
        )

    if mode_paiement:
        query = query.filter(Paiement.mode_paiement.ilike(f"%{mode_paiement}%"))
    if statut:
        try:
            enum_val = PaiementStatus(statut)
            query = query.filter(Paiement.statut == enum_val)
        except ValueError:
            pass
    if facture_id:
        query = query.filter(Paiement.facture_id == facture_id)
    if search:
        query = query.filter(
            or_(
                Paiement.reference.ilike(f"%{search}%"),
                Paiement.notes.ilike(f"%{search}%")
            )
        )

    total = query.count()
    items = query.order_by(desc(Paiement.date_paiement), desc(Paiement.id)).offset(skip).limit(limit).all()

    return {
        "total": total,
        "skip": skip,
        "limit": limit,
        "items": [
            {
                "id": p.id,
                "facture_id": p.facture_id,
                "facture_numero": p.facture.numero_facture if p.facture else None,
                "client_id": p.facture.client_id if p.facture else None,
                "montant": float(p.montant),
                "date_paiement": p.date_paiement.isoformat() if p.date_paiement else None,
                "mode_paiement": p.mode_paiement,
                "reference": p.reference,
                "statut": p.statut.value if hasattr(p.statut, 'value') else str(p.statut),
                "notes": p.notes,
                "created_at": p.created_at.isoformat() if p.created_at else None
            }
            for p in items
        ]
    }


@router.get("/stats")
async def get_transaction_stats(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Statistiques financières globales des encaissements"""
    query = db.query(Paiement)
    if not current_user.is_superuser:
        query = query.filter(Paiement.company_id == current_user.company_id)
    total_tx = query.with_entities(func.count(Paiement.id)).scalar() or 0
    total_encaisse = query.with_entities(func.sum(Paiement.montant)).filter(
        Paiement.statut == PaiementStatus.CONFIRME
    ).scalar() or 0
    en_attente = query.with_entities(func.sum(Paiement.montant)).filter(
        Paiement.statut == PaiementStatus.EN_ATTENTE
    ).scalar() or 0

    # Répartition par mode de paiement
    modes_query = query.with_entities(
        Paiement.mode_paiement,
        func.count(Paiement.id),
        func.sum(Paiement.montant)
    ).group_by(Paiement.mode_paiement).all()
    modes = modes_query

    repartition_modes = [
        {
            "mode": mode or "Non spécifié",
            "count": count,
            "volume": float(total or 0)
        }
        for mode, count, total in modes
    ]

    return {
        "nombre_total_transactions": total_tx,
        "volume_encaisse_xaf": float(total_encaisse),
        "volume_en_attente_xaf": float(en_attente),
        "repartition_modes": repartition_modes
    }


@router.post("/", status_code=status.HTTP_201_CREATED)
async def create_transaction(
    payload: TransactionCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Enregistre un nouveau paiement ou règlement pour une facture"""
    facture_query = db.query(Facture).filter(Facture.id == payload.facture_id)
    if not current_user.is_superuser:
        facture_query = facture_query.filter(Facture.company_id == current_user.company_id)
    facture = facture_query.first()
    if not facture:
        raise HTTPException(status_code=404, detail=f"Facture #{payload.facture_id} non trouvée")

    paiement = Paiement(
        facture_id=payload.facture_id,
        company_id=facture.company_id or current_user.company_id,
        montant=payload.montant,
        date_paiement=payload.date_paiement or date.today(),
        mode_paiement=payload.mode_paiement,
        reference=payload.reference or f"TX-{datetime.now().strftime('%Y%m%d%H%M%S')}",
        statut=PaiementStatus.EN_ATTENTE,
        notes=payload.notes
    )

    db.add(paiement)
    db.commit()
    db.refresh(paiement)

    return {
        "message": "Transaction enregistrée avec succès",
        "id": paiement.id,
        "reference": paiement.reference,
        "montant": float(paiement.montant),
        "facture_id": paiement.facture_id
    }


@router.get("/{id}")
async def get_transaction(
    id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Détail d'une transaction financière avec informations de facture"""
    query = db.query(Paiement).filter(Paiement.id == id)
    if not current_user.is_superuser:
        query = query.filter(Paiement.company_id == current_user.company_id)
    p = query.first()
    if not p:
        raise HTTPException(status_code=404, detail=f"Transaction #{id} non trouvée")

    return {
        "id": p.id,
        "facture_id": p.facture_id,
        "facture_numero": p.facture.numero_facture if p.facture else None,
        "facture_montant_ttc": float(p.facture.montant_ttc) if p.facture else None,
        "montant": float(p.montant),
        "date_paiement": p.date_paiement.isoformat() if p.date_paiement else None,
        "mode_paiement": p.mode_paiement,
        "reference": p.reference,
        "statut": p.statut.value if hasattr(p.statut, 'value') else str(p.statut),
        "notes": p.notes,
        "created_at": p.created_at.isoformat() if p.created_at else None
    }


@router.put("/{id}")
async def update_transaction(
    id: int,
    payload: TransactionUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Met à jour les informations ou statut d'une transaction"""
    p = db.query(Paiement).filter(Paiement.id == id).first()
    if not p:
        raise HTTPException(status_code=404, detail=f"Transaction #{id} non trouvée")

    if payload.montant is not None:
        p.montant = payload.montant
    if payload.mode_paiement is not None:
        p.mode_paiement = payload.mode_paiement
    if payload.reference is not None:
        p.reference = payload.reference
    if payload.notes is not None:
        p.notes = payload.notes
    if payload.statut is not None:
        try:
            p.statut = PaiementStatus(payload.statut)
        except ValueError:
            raise HTTPException(status_code=400, detail=f"Statut invalide: {payload.statut}")

    db.commit()
    db.refresh(p)

    return {"message": "Transaction mise à jour avec succès", "id": p.id}


@router.post("/{id}/reconcile")
async def reconcile_transaction(
    id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Rapproche une transaction bancaire et crée l'écriture comptable correspondante"""
    p = db.query(Paiement).filter(Paiement.id == id).first()
    if not p:
        raise HTTPException(status_code=404, detail=f"Transaction #{id} non trouvée")

    p.statut = PaiementStatus.VALIDE

    # Génération d'une écriture comptable
    ecriture = EcritureComptable(
        date_ecriture=date.today(),
        reference=f"RECON-{p.reference}",
        libelle=f"Règlement Facture {p.facture.numero_facture if p.facture else id} via {p.mode_paiement}",
        montant_debit=p.montant,
        montant_credit=p.montant
    )
    db.add(ecriture)
    db.commit()

    return {
        "message": "Transaction rapprochée et écriture comptable générée",
        "transaction_id": p.id,
        "statut": p.statut.value if hasattr(p.statut, 'value') else str(p.statut),
        "ecriture_id": ecriture.id
    }


@router.delete("/{id}")
async def delete_transaction(
    id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Supprime un enregistrement de transaction"""
    p = db.query(Paiement).filter(Paiement.id == id).first()
    if not p:
        raise HTTPException(status_code=404, detail=f"Transaction #{id} non trouvée")

    db.delete(p)
    db.commit()
    return {"message": f"Transaction #{id} supprimée"}