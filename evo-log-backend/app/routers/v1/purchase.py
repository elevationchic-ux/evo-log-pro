"""
Purchase router - manages purchasing operations (bons de commande, factures fournisseurs)
"""
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from sqlalchemy import func, desc, or_
from typing import Optional
from datetime import datetime, date
from app.core.database import get_db
from app.core.security import get_current_user
from app.models.user import User
from app.models.finance import Facture, Paiement
from app.models.finance_ohada import EcritureComptableNew

router = APIRouter()


@router.get("/")
async def get_purchases(
    statut: Optional[str] = Query(None),
    date_debut: Optional[str] = Query(None),
    date_fin: Optional[str] = Query(None),
    skip: int = 0,
    limit: int = 50,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Récupère les factures fournisseurs (achats)"""
    # Les achats sont identifiés par les écritures du journal ACHATS
    query = db.query(EcritureComptableNew).filter(
        EcritureComptableNew.journal == "ACHATS"
    )

    if date_debut:
        try:
            d = datetime.strptime(date_debut, "%Y-%m-%d").date()
            query = query.filter(EcritureComptableNew.date_ecriture >= d)
        except ValueError:
            pass

    if date_fin:
        try:
            d = datetime.strptime(date_fin, "%Y-%m-%d").date()
            query = query.filter(EcritureComptableNew.date_ecriture <= d)
        except ValueError:
            pass

    total = query.count()
    purchases = query.order_by(desc(EcritureComptableNew.date_ecriture)).offset(skip).limit(limit).all()

    return {
        "total": total,
        "skip": skip,
        "limit": limit,
        "data": [
            {
                "id": p.id,
                "numero_ecriture": p.numero_ecriture,
                "date_ecriture": p.date_ecriture.isoformat() if p.date_ecriture else None,
                "numero_piece": p.numero_piece,
                "libelle": p.libelle,
                "debit": float(p.debit) if p.debit else 0.0,
                "credit": float(p.credit) if p.credit else 0.0,
                "devise": p.devise,
                "reference_document": p.reference_document,
                "type_document": p.type_document,
                "periode": p.periode,
                "journal": p.journal,
                "valider": p.valider,
                "created_at": p.created_at.isoformat() if p.created_at else None,
            }
            for p in purchases
        ]
    }


@router.get("/stats")
async def get_purchase_stats(
    periode: Optional[str] = Query(None, description="Format: YYYY-MM"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Statistiques des achats"""
    query = db.query(EcritureComptableNew).filter(
        EcritureComptableNew.journal == "ACHATS"
    )

    if periode:
        query = query.filter(EcritureComptableNew.periode == periode)

    total_achats = query.with_entities(func.sum(EcritureComptableNew.debit)).scalar() or 0.0
    total_credits = query.with_entities(func.sum(EcritureComptableNew.credit)).scalar() or 0.0
    nb_factures = query.with_entities(func.count(EcritureComptableNew.id)).scalar() or 0

    # Factures globales non payées
    factures_impayees = db.query(func.count(Facture.id)).filter(
        Facture.statut.in_(["emise", "retard", "payee_partiellement"])
    ).scalar() or 0

    montant_impaye = db.query(func.sum(Facture.montant_ttc)).filter(
        Facture.statut.in_(["emise", "retard"])
    ).scalar() or 0.0

    return {
        "periode": periode or "Toutes périodes",
        "total_achats_debit": float(total_achats),
        "total_credits": float(total_credits),
        "nb_ecritures_achat": nb_factures,
        "factures_impayees": factures_impayees,
        "montant_impaye": float(montant_impaye),
    }


@router.get("/factures")
async def get_purchase_invoices(
    statut: Optional[str] = Query(None),
    skip: int = 0,
    limit: int = 50,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Récupère les factures avec leurs statuts de paiement"""
    query = db.query(Facture)
    if statut:
        query = query.filter(Facture.statut == statut)

    total = query.count()
    factures = query.order_by(desc(Facture.date_emission)).offset(skip).limit(limit).all()

    return {
        "total": total,
        "skip": skip,
        "limit": limit,
        "data": [
            {
                "id": f.id,
                "numero_facture": f.numero_facture,
                "date_emission": f.date_emission.isoformat() if f.date_emission else None,
                "date_echeance": f.date_echeance.isoformat() if f.date_echeance else None,
                "montant_ht": float(f.montant_ht) if f.montant_ht else 0.0,
                "montant_tva": float(f.montant_tva) if f.montant_tva else 0.0,
                "montant_ttc": float(f.montant_ttc) if f.montant_ttc else 0.0,
                "devise": f.devise,
                "statut": f.statut.value if hasattr(f.statut, "value") else str(f.statut),
                "notes": f.notes,
                "created_at": f.created_at.isoformat() if f.created_at else None,
            }
            for f in factures
        ]
    }


@router.get("/factures/{facture_id}/paiements")
async def get_invoice_payments(
    facture_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Récupère les paiements d'une facture"""
    facture = db.query(Facture).filter(Facture.id == facture_id).first()
    if not facture:
        raise HTTPException(status_code=404, detail="Facture introuvable")

    paiements = db.query(Paiement).filter(Paiement.facture_id == facture_id).all()

    total_paye = sum(float(p.montant) for p in paiements)
    reste_a_payer = float(facture.montant_ttc) - total_paye

    return {
        "facture_id": facture_id,
        "numero_facture": facture.numero_facture,
        "montant_ttc": float(facture.montant_ttc),
        "total_paye": total_paye,
        "reste_a_payer": max(reste_a_payer, 0),
        "statut": facture.statut.value if hasattr(facture.statut, "value") else str(facture.statut),
        "paiements": [
            {
                "id": p.id,
                "montant": float(p.montant),
                "date_paiement": p.date_paiement.isoformat() if p.date_paiement else None,
                "mode_paiement": p.mode_paiement,
                "reference": p.reference,
                "statut": p.statut.value if hasattr(p.statut, "value") else str(p.statut),
            }
            for p in paiements
        ]
    }