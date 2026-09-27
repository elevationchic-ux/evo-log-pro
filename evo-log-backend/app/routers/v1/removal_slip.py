"""
Removal Slip (Bon d'Enlèvement / Bon de Sortie Magasin) router
Gestion complète des bons d'enlèvement magasin, déstockage et contrôle des sorties
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
from app.models.magasin_avance import BonSortie, LigneBonSortie
from app.models.magasin import Stock, Entrepot, MouvementStock, MouvementType
from app.models.tiers import Client

router = APIRouter()


class LigneRemovalCreate(BaseModel):
    stock_id: int
    quantite_sortie: float
    prix_unitaire: Optional[float] = 0.0
    numero_lot: Optional[str] = None
    date_peremption: Optional[date] = None
    commentaires: Optional[str] = None


class RemovalSlipCreate(BaseModel):
    client_id: int
    entrepot_id: int
    date_sortie: Optional[date] = None
    type_sortie: Optional[str] = "enlevement"  # enlevement, vente, consommation, transfert
    commande_reference: Optional[str] = None
    notes: Optional[str] = None
    lignes: List[LigneRemovalCreate] = []


class RemovalSlipUpdate(BaseModel):
    client_id: Optional[int] = None
    entrepot_id: Optional[int] = None
    statut: Optional[str] = None
    notes: Optional[str] = None


@router.get("/")
async def get_removal_slips(
    statut: Optional[str] = Query(None, description="Filtrer par statut (en_attente, valide, refuse)"),
    entrepot_id: Optional[int] = Query(None),
    client_id: Optional[int] = Query(None),
    search: Optional[str] = Query(None, description="Recherche par numéro de bon ou référence"),
    skip: int = 0,
    limit: int = 50,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Liste des bons d'enlèvement magasin avec pagination"""
    query = db.query(BonSortie)

    if statut:
        query = query.filter(BonSortie.statut == statut)
    if entrepot_id:
        query = query.filter(BonSortie.entrepot_id == entrepot_id)
    if client_id:
        query = query.filter(BonSortie.client_id == client_id)
    if search:
        query = query.filter(
            or_(
                BonSortie.numero_bon.ilike(f"%{search}%"),
                BonSortie.commande_reference.ilike(f"%{search}%"),
                BonSortie.notes.ilike(f"%{search}%")
            )
        )

    total = query.count()
    items = query.order_by(desc(BonSortie.date_sortie), desc(BonSortie.id)).offset(skip).limit(limit).all()

    return {
        "total": total,
        "skip": skip,
        "limit": limit,
        "items": [
            {
                "id": b.id,
                "numero_bon": b.numero_bon,
                "client_id": b.client_id,
                "entrepot_id": b.entrepot_id,
                "entrepot_nom": b.entrepot.nom if b.entrepot else None,
                "date_sortie": b.date_sortie.isoformat() if b.date_sortie else None,
                "statut": b.statut,
                "type_sortie": b.type_sortie,
                "commande_reference": b.commande_reference,
                "nombre_lignes": len(b.lignes_bon) if b.lignes_bon else 0,
                "created_at": b.created_at.isoformat() if b.created_at else None
            }
            for b in items
        ]
    }


@router.get("/stats")
async def get_removal_slips_stats(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Statistiques d'enlèvement magasin et sorties de stock"""
    total = db.query(func.count(BonSortie.id)).scalar() or 0
    en_attente = db.query(func.count(BonSortie.id)).filter(BonSortie.statut == "en_attente").scalar() or 0
    valides = db.query(func.count(BonSortie.id)).filter(BonSortie.statut == "valide").scalar() or 0
    refuses = db.query(func.count(BonSortie.id)).filter(BonSortie.statut == "refuse").scalar() or 0

    quantite_totale = db.query(func.sum(LigneBonSortie.quantite_sortie)).scalar() or 0

    return {
        "total_bons_enlevement": total,
        "en_attente": en_attente,
        "valides": valides,
        "refuses": refuses,
        "quantite_totale_enlevee": float(quantite_totale)
    }


@router.post("/", status_code=status.HTTP_201_CREATED)
async def create_removal_slip(
    payload: RemovalSlipCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Crée un nouveau bon d'enlèvement avec ses lignes d'articles.

    Batch 16 : validations d'existence explicites (client, entrepot, stocks) —
    SQLite n'impose PAS les FK par defaut, sans controle un bon pointerait sur
    des ids inexistants. Numeration provisoire `BE-YYYYMMDD-NNNN` : sequence
    par jour, boucle anti-collision (les suppressions de brouillons laissent
    des trous ; UNIQUE sur numero_bon ne doit jamais exploiter en 500).
    """
    client = db.query(Client).filter(Client.id == payload.client_id).first()
    if not client:
        raise HTTPException(status_code=400,
                            detail=f"Client {payload.client_id} inexistant")
    entrepot = db.query(Entrepot).filter(Entrepot.id == payload.entrepot_id).first()
    if not entrepot:
        raise HTTPException(status_code=400,
                            detail=f"Entrepot {payload.entrepot_id} inexistant")

    stocks = {}
    for item in payload.lignes:
        if item.quantite_sortie is None or float(item.quantite_sortie) <= 0:
            raise HTTPException(status_code=400,
                                detail=f"Quantite invalide pour la ligne stock {item.stock_id}")
        stock = db.query(Stock).filter(Stock.id == item.stock_id).first()
        if not stock:
            raise HTTPException(status_code=400,
                                detail=f"Stock {item.stock_id} inexistant")
        stocks[stock.id] = stock

    today_str = datetime.now().strftime("%Y%m%d")
    seq = (db.query(func.count(BonSortie.id))
             .filter(BonSortie.numero_bon.like(f"BE-{today_str}-%")).scalar() or 0) + 1
    numero_bon = f"BE-{today_str}-{seq:04d}"
    while db.query(BonSortie.id).filter(BonSortie.numero_bon == numero_bon).first() is not None:
        seq += 1
        numero_bon = f"BE-{today_str}-{seq:04d}"

    bon = BonSortie(
        numero_bon=numero_bon,
        client_id=payload.client_id,
        entrepot_id=payload.entrepot_id,
        date_sortie=payload.date_sortie or date.today(),
        operateur=current_user.id,
        statut="en_attente",
        type_sortie=payload.type_sortie or "enlevement",
        commande_reference=payload.commande_reference,
        notes=payload.notes
    )
    db.add(bon)
    db.flush()

    for item in payload.lignes:
        ligne = LigneBonSortie(
            bon_sortie_id=bon.id,
            stock_id=item.stock_id,
            quantite_sortie=item.quantite_sortie,
            prix_unitaire=item.prix_unitaire or 0.0,
            numero_lot=item.numero_lot,
            date_peremption=item.date_peremption,
            commentaires=item.commentaires,
            statut="conforme"
        )
        db.add(ligne)

    db.commit()
    db.refresh(bon)

    return {
        "message": "Bon d'enlèvement créé avec succès",
        "id": bon.id,
        "numero_bon": bon.numero_bon,
        "statut": bon.statut
    }


@router.get("/{id}")
async def get_removal_slip_detail(
    id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Détail d'un bon d'enlèvement avec ses articles et informations de déstockage"""
    bon = db.query(BonSortie).filter(BonSortie.id == id).first()
    if not bon:
        raise HTTPException(status_code=404, detail=f"Bon d'enlèvement #{id} non trouvé")

    return {
        "id": bon.id,
        "numero_bon": bon.numero_bon,
        "client_id": bon.client_id,
        "entrepot_id": bon.entrepot_id,
        "entrepot_nom": bon.entrepot.nom if bon.entrepot else None,
        "date_sortie": bon.date_sortie.isoformat() if bon.date_sortie else None,
        "date_validation": bon.date_validation.isoformat() if bon.date_validation else None,
        "operateur": bon.operateur,
        "validateur": bon.validateur,
        "statut": bon.statut,
        "type_sortie": bon.type_sortie,
        "commande_reference": bon.commande_reference,
        "notes": bon.notes,
        "created_at": bon.created_at.isoformat() if bon.created_at else None,
        "lignes": [
            {
                "id": ligne.id,
                "stock_id": ligne.stock_id,
                "designation": ligne.stock.designation if ligne.stock else None,
                "code_article": ligne.stock.code_article if ligne.stock else None,
                "quantite_sortie": float(ligne.quantite_sortie),
                "prix_unitaire": float(ligne.prix_unitaire) if ligne.prix_unitaire else None,
                "numero_lot": ligne.numero_lot,
                "statut": ligne.statut,
                "commentaires": ligne.commentaires
            }
            for ligne in (bon.lignes_bon or [])
        ]
    }


@router.put("/{id}")
async def update_removal_slip(
    id: int,
    payload: RemovalSlipUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Met a jour l'en-tete d'un bon d'enlevement NON signe.

    Batch 16 — circuit de signature :
    - `statut` n'est PLUS modifiable ici : passez par /validate (signature =
      decrement reel du stock) ou /refuse. Le PUT allowait jadis de poser
      statut='valide' sans aucun decript — faux document signe.
    - un bon valide ou refuse est IMMUABLE (le magasinier ne peut que valider,
      pas corriger a posteriori un document signe).
    - les LIGNES ne sont jamais modifiables par cette voie (aucun endpoint de
      modification de ligne n'existe, et n'existera pas apres signature).
    """
    bon = db.query(BonSortie).filter(BonSortie.id == id).first()
    if not bon:
        raise HTTPException(status_code=404, detail=f"Bon d'enlèvement #{id} non trouvé")

    data = payload.dict(exclude_unset=True)
    if "statut" in data:
        raise HTTPException(
            status_code=400,
            detail="Le statut ne se modifie pas par PUT : utilisez /validate ou /refuse "
                   "(circuit de signature).",
        )
    if bon.statut in ("valide", "refuse"):
        raise HTTPException(
            status_code=400,
            detail=f"Bon #{bon.numero_bon} deja signe ({bon.statut}) : document immuable.",
        )

    for field, value in data.items():
        setattr(bon, field, value)

    db.commit()
    db.refresh(bon)
    return {"message": "Bon d'enlèvement mis à jour", "id": bon.id}


@router.post("/{id}/validate")
async def validate_removal_slip(
    id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Valide l'enlèvement et déduit automatiquement les quantités des stocks de l'entrepôt"""
    bon = db.query(BonSortie).filter(BonSortie.id == id).first()
    if not bon:
        raise HTTPException(status_code=404, detail=f"Bon d'enlèvement #{id} non trouvé")

    if bon.statut == "valide":
        raise HTTPException(status_code=400, detail="Ce bon d'enlèvement est déjà validé")

    # Déduire les stocks
    for ligne in (bon.lignes_bon or []):
        stock = db.query(Stock).filter(Stock.id == ligne.stock_id).first()
        if stock:
            qte = float(ligne.quantite_sortie or 0)
            dispo = float(stock.quantite_disponible or 0)
            stock.quantite_disponible = max(0, dispo - qte)
            stock.date_derniere_sortie = datetime.utcnow()

    bon.statut = "valide"
    bon.validateur = current_user.id
    bon.date_validation = date.today()

    db.commit()
    return {
        "message": "Bon d'enlèvement validé et stock décrémenté avec succès",
        "id": bon.id,
        "statut": bon.statut
    }


@router.delete("/{id}")
async def delete_removal_slip(
    id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Supprime un bon d'enlèvement non validé"""
    bon = db.query(BonSortie).filter(BonSortie.id == id).first()
    if not bon:
        raise HTTPException(status_code=404, detail=f"Bon d'enlèvement #{id} non trouvé")

    if bon.statut == "valide":
        raise HTTPException(status_code=400, detail="Impossible de supprimer un bon validé")

    # Supprimer les lignes
    db.query(LigneBonSortie).filter(LigneBonSortie.bon_sortie_id == bon.id).delete()
    db.delete(bon)
    db.commit()

    return {"message": f"Bon d'enlèvement #{id} supprimé"}