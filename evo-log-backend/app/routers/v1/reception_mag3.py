"""
Reception Magasin 3 (MAG3 Portuaire / Entrepôt Sous Douane) router
Gestion complète des réceptions de fret, dépotage conteneurs et mise en stock magasin portuaire
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
from app.models.magasin_avance import BonReception, LigneBonReception
from app.models.magasin import Stock, Entrepot

router = APIRouter()


class LigneReceptionCreate(BaseModel):
    stock_id: int
    quantite_recue: float
    quantite_commandee: Optional[float] = None
    prix_unitaire: Optional[float] = 0.0
    emplacement: Optional[str] = "MAG3-QUAI-A"
    numero_lot: Optional[str] = None
    date_peremption: Optional[date] = None
    statut: Optional[str] = "conforme"  # conforme, ecart, refuse
    commentaires: Optional[str] = None


class ReceptionMag3Create(BaseModel):
    fournisseur_id: int
    entrepot_id: int
    commande_fournisseur_id: Optional[int] = None
    date_reception: Optional[date] = None
    notes: Optional[str] = None
    lignes: List[LigneReceptionCreate] = []


class ReceptionMag3Update(BaseModel):
    statut: Optional[str] = None
    notes: Optional[str] = None


@router.get("/")
async def get_receptions_mag3(
    statut: Optional[str] = Query(None, description="Filtrer par statut (en_attente, valide, refuse)"),
    entrepot_id: Optional[int] = Query(None),
    fournisseur_id: Optional[int] = Query(None),
    search: Optional[str] = Query(None, description="Recherche par numéro de bon ou notes"),
    skip: int = 0,
    limit: int = 50,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Liste des réceptions de fret au Magasin 3 avec pagination"""
    query = db.query(BonReception)

    if statut:
        query = query.filter(BonReception.statut == statut)
    if entrepot_id:
        query = query.filter(BonReception.entrepot_id == entrepot_id)
    if fournisseur_id:
        query = query.filter(BonReception.fournisseur_id == fournisseur_id)
    if search:
        query = query.filter(
            or_(
                BonReception.numero_bon.ilike(f"%{search}%"),
                BonReception.notes.ilike(f"%{search}%")
            )
        )

    total = query.count()
    items = query.order_by(desc(BonReception.date_reception), desc(BonReception.id)).offset(skip).limit(limit).all()

    return {
        "total": total,
        "skip": skip,
        "limit": limit,
        "items": [
            {
                "id": r.id,
                "numero_bon": r.numero_bon,
                "fournisseur_id": r.fournisseur_id,
                "entrepot_id": r.entrepot_id,
                "entrepot_nom": r.entrepot.nom if r.entrepot else None,
                "date_reception": r.date_reception.isoformat() if r.date_reception else None,
                "statut": r.statut,
                "nombre_lignes": len(r.lignes_bon) if r.lignes_bon else 0,
                "notes": r.notes,
                "created_at": r.created_at.isoformat() if r.created_at else None
            }
            for r in items
        ]
    }


@router.get("/stats")
async def get_reception_mag3_stats(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Statistiques d'exploitation et de cadencement du Magasin 3"""
    total = db.query(func.count(BonReception.id)).scalar() or 0
    en_attente = db.query(func.count(BonReception.id)).filter(BonReception.statut == "en_attente").scalar() or 0
    valides = db.query(func.count(BonReception.id)).filter(BonReception.statut == "valide").scalar() or 0
    refuses = db.query(func.count(BonReception.id)).filter(BonReception.statut == "refuse").scalar() or 0

    quantite_recue_totale = db.query(func.sum(LigneBonReception.quantite_recue)).scalar() or 0

    return {
        "total_receptions_mag3": total,
        "en_cours_controle": en_attente,
        "validees": valides,
        "refusees": refuses,
        "volume_total_receptionne": float(quantite_recue_totale)
    }


@router.post("/", status_code=status.HTTP_201_CREATED)
async def create_reception_mag3(
    payload: ReceptionMag3Create,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Enregistre une nouvelle entrée / réception de marchandise au Magasin 3"""
    today_str = datetime.now().strftime("%Y%m%d")
    count_today = db.query(func.count(BonReception.id)).scalar() or 0
    numero_bon = f"REC-MAG3-{today_str}-{count_today + 1:04d}"

    bon = BonReception(
        numero_bon=numero_bon,
        commande_fournisseur_id=payload.commande_fournisseur_id,
        fournisseur_id=payload.fournisseur_id,
        entrepot_id=payload.entrepot_id,
        date_reception=payload.date_reception or date.today(),
        operateur=current_user.id,
        statut="en_attente",
        notes=payload.notes
    )
    db.add(bon)
    db.flush()

    for item in payload.lignes:
        ligne = LigneBonReception(
            bon_reception_id=bon.id,
            stock_id=item.stock_id,
            quantite_recue=item.quantite_recue,
            quantite_commandee=item.quantite_commandee,
            prix_unitaire=item.prix_unitaire or 0.0,
            emplacement=item.emplacement or "MAG3-ENTREE",
            numero_lot=item.numero_lot,
            date_peremption=item.date_peremption,
            statut=item.statut or "conforme",
            commentaires=item.commentaires
        )
        db.add(ligne)

    db.commit()
    db.refresh(bon)

    return {
        "message": "Réception Magasin 3 enregistrée avec succès",
        "id": bon.id,
        "numero_bon": bon.numero_bon,
        "statut": bon.statut
    }


@router.get("/{id}")
async def get_reception_mag3_detail(
    id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Détail d'une réception Magasin 3 avec lignes d'inspection"""
    bon = db.query(BonReception).filter(BonReception.id == id).first()
    if not bon:
        raise HTTPException(status_code=404, detail=f"Réception Magasin 3 #{id} non trouvée")

    return {
        "id": bon.id,
        "numero_bon": bon.numero_bon,
        "fournisseur_id": bon.fournisseur_id,
        "entrepot_id": bon.entrepot_id,
        "entrepot_nom": bon.entrepot.nom if bon.entrepot else None,
        "date_reception": bon.date_reception.isoformat() if bon.date_reception else None,
        "date_validation": bon.date_validation.isoformat() if bon.date_validation else None,
        "operateur": bon.operateur,
        "validateur": bon.validateur,
        "statut": bon.statut,
        "notes": bon.notes,
        "created_at": bon.created_at.isoformat() if bon.created_at else None,
        "lignes": [
            {
                "id": ligne.id,
                "stock_id": ligne.stock_id,
                "designation": ligne.stock.designation if ligne.stock else None,
                "code_article": ligne.stock.code_article if ligne.stock else None,
                "quantite_recue": float(ligne.quantite_recue),
                "quantite_commandee": float(ligne.quantite_commandee) if ligne.quantite_commandee else None,
                "emplacement": ligne.emplacement,
                "numero_lot": ligne.numero_lot,
                "statut": ligne.statut,
                "commentaires": ligne.commentaires
            }
            for ligne in (bon.lignes_bon or [])
        ]
    }


@router.put("/{id}")
async def update_reception_mag3(
    id: int,
    payload: ReceptionMag3Update,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Met à jour les informations d'une réception"""
    bon = db.query(BonReception).filter(BonReception.id == id).first()
    if not bon:
        raise HTTPException(status_code=404, detail=f"Réception #{id} non trouvée")

    data = payload.dict(exclude_unset=True)
    for field, value in data.items():
        setattr(bon, field, value)

    db.commit()
    db.refresh(bon)
    return {"message": "Réception mise à jour avec succès", "id": bon.id}


@router.post("/{id}/validate")
async def validate_reception_mag3(
    id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Valide la réception au Magasin 3 et incrémente automatiquement les stocks disponibles"""
    bon = db.query(BonReception).filter(BonReception.id == id).first()
    if not bon:
        raise HTTPException(status_code=404, detail=f"Réception #{id} non trouvée")

    if bon.statut == "valide":
        raise HTTPException(status_code=400, detail="Cette réception est déjà validée")

    # Incrémenter les stocks
    for ligne in (bon.lignes_bon or []):
        stock = db.query(Stock).filter(Stock.id == ligne.stock_id).first()
        if stock:
            qte = float(ligne.quantite_recue or 0)
            dispo = float(stock.quantite_disponible or 0)
            stock.quantite_disponible = dispo + qte
            stock.date_derniere_entree = datetime.utcnow()
            if ligne.emplacement:
                stock.emplacement = ligne.emplacement

    bon.statut = "valide"
    bon.validateur = current_user.id
    bon.date_validation = date.today()

    db.commit()
    return {
        "message": "Réception Magasin 3 validée et stocks incrémentés avec succès",
        "id": bon.id,
        "statut": bon.statut
    }


@router.delete("/{id}")
async def delete_reception_mag3(
    id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Supprime une réception Magasin 3 non validée"""
    bon = db.query(BonReception).filter(BonReception.id == id).first()
    if not bon:
        raise HTTPException(status_code=404, detail=f"Réception #{id} non trouvée")

    if bon.statut == "valide":
        raise HTTPException(status_code=400, detail="Impossible de supprimer une réception validée")

    db.query(LigneBonReception).filter(LigneBonReception.bon_reception_id == bon.id).delete()
    db.delete(bon)
    db.commit()

    return {"message": f"Réception #{id} supprimée"}