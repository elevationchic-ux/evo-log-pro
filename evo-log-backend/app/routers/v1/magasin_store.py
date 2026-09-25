"""
Magasin store-domain router (Tranche A).

Real, DB-backed CRUD for the warehouse business objects the frontend calls under
/api/v1/magasin/* :
  * articles            (master data fiches articles)
  * clients             (proxy sur le modele Tiers/Client existant)
  * commandes           (+ lignes, valider / preparer / annuler)
  * ordres-transfert    (+ valider / payer / expedier / receptionner / annuler)
  * bandes-livraison    (+ CRUD et derivation depuis un ordre de transfert)

Monte sur /api/v1/magasin (meme prefixe que le routeur magasin existant ; les
chemins sont disjoints). Le filtrage multi-tenant par company_id est assure par
le middleware/ORM global, comme sur les autres routeurs metier.
"""
from __future__ import annotations

import random
import string
from datetime import datetime
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.models.magasin import (
    Article,
    Commande,
    LigneCommande,
    OrdreTransfert,
    BandeLivraison,
    CommandeStatut,
    TransfertStatut,
)
from app.models.tiers import Tiers, Client, TiersType
from app.schemas.magasin_store import (
    ArticleCreate,
    ArticleUpdate,
    ArticleResponse,
    ClientCreate,
    ClientUpdate,
    ClientResponse,
    CommandeCreate,
    CommandeResponse,
    OrdreTransfertCreate,
    OrdreTransfertResponse,
    BandeLivraisonCreate,
    BandeLivraisonUpdate,
    BandeLivraisonResponse,
)

router = APIRouter()


def _ref(prefix: str) -> str:
    return f"{prefix}-{datetime.now().strftime('%Y%m%d')}-{''.join(random.choices(string.ascii_uppercase + string.digits, k=5))}"


def _get_or_404(obj, db: Session, ident: int, label: str):
    row = db.get(obj, ident)
    if not row:
        raise HTTPException(status_code=404, detail=f"{label} introuvable")
    return row


# ─── ARTICLES ────────────────────────────────────────────────────────────────
@router.get("/articles", response_model=dict)
async def list_articles(
    skip: int = 0,
    limit: int = Query(100, le=500),
    search: Optional[str] = None,
    categorie: Optional[str] = None,
    db: Session = Depends(get_db),
):
    q = db.query(Article)
    if search:
        like = f"%{search}%"
        q = q.filter((Article.designation.ilike(like)) | (Article.code.ilike(like)))
    if categorie:
        q = q.filter(Article.categorie == categorie)
    total = q.count()
    items = q.offset(skip).limit(limit).all()
    return {
        "items": [ArticleResponse.model_validate(a).model_dump() for a in items],
        "total": total,
        "pending": False,
    }


@router.post("/articles", response_model=ArticleResponse, status_code=201)
async def create_article(payload: ArticleCreate, db: Session = Depends(get_db)):
    if db.query(Article).filter(Article.code == payload.code).first():
        raise HTTPException(status_code=400, detail="Un article avec ce code existe deja")
    row = Article(**payload.model_dump())
    db.add(row)
    db.commit()
    db.refresh(row)
    return row


@router.get("/articles/by-code/{code}", response_model=ArticleResponse)
async def get_article_by_code(code: str, db: Session = Depends(get_db)):
    row = db.query(Article).filter(Article.code == code).first()
    if not row:
        raise HTTPException(status_code=404, detail="Article introuvable")
    return row


@router.get("/articles/{article_id}", response_model=ArticleResponse)
async def get_article(article_id: int, db: Session = Depends(get_db)):
    return _get_or_404(Article, db, article_id, "Article")


@router.put("/articles/{article_id}", response_model=ArticleResponse)
async def update_article(article_id: int, payload: ArticleUpdate, db: Session = Depends(get_db)):
    row = _get_or_404(Article, db, article_id, "Article")
    for k, v in payload.model_dump(exclude_unset=True).items():
        setattr(row, k, v)
    db.commit()
    db.refresh(row)
    return row


@router.delete("/articles/{article_id}", status_code=204)
async def delete_article(article_id: int, db: Session = Depends(get_db)):
    row = _get_or_404(Article, db, article_id, "Article")
    row.is_active = False
    db.commit()
    return None


# ─── CLIENTS (proxy Tiers/Client) ──────────────────────────────────────────────
@router.get("/clients", response_model=dict)
async def list_clients(
    skip: int = 0,
    limit: int = Query(100, le=500),
    search: Optional[str] = None,
    db: Session = Depends(get_db),
):
    q = db.query(Tiers).filter(Tiers.type == TiersType.CLIENT)
    if search:
        like = f"%{search}%"
        q = q.filter((Tiers.name.ilike(like)) | (Tiers.code.ilike(like)))
    total = q.count()
    items = q.offset(skip).limit(limit).all()
    return {
        "items": [ClientResponse.model_validate(c).model_dump() for c in items],
        "total": total,
        "pending": False,
    }


@router.post("/clients", response_model=ClientResponse, status_code=201)
async def create_client(payload: ClientCreate, db: Session = Depends(get_db)):
    data = payload.model_dump()
    code = data.pop("code", None) or _ref("CLI")
    # Herite polymorphique : instancier Client (pas Tiers + type manuel),
    # sinon l'identite polymorphe est incoherente au flush.
    row = Client(code=code, **data)
    db.add(row)
    db.commit()
    db.refresh(row)
    return row


@router.get("/clients/{client_id}", response_model=ClientResponse)
async def get_client(client_id: int, db: Session = Depends(get_db)):
    row = db.query(Tiers).filter(Tiers.id == client_id).first()
    if not row:
        raise HTTPException(status_code=404, detail="Client introuvable")
    return row


@router.put("/clients/{client_id}", response_model=ClientResponse)
async def update_client(client_id: int, payload: ClientUpdate, db: Session = Depends(get_db)):
    row = db.query(Tiers).filter(Tiers.id == client_id).first()
    if not row:
        raise HTTPException(status_code=404, detail="Client introuvable")
    for k, v in payload.model_dump(exclude_unset=True).items():
        setattr(row, k, v)
    db.commit()
    db.refresh(row)
    return row


@router.delete("/clients/{client_id}", status_code=204)
async def delete_client(client_id: int, db: Session = Depends(get_db)):
    row = db.query(Tiers).filter(Tiers.id == client_id).first()
    if not row:
        raise HTTPException(status_code=404, detail="Client introuvable")
    row.is_active = False
    db.commit()
    return None


# ─── COMMANDES ─────────────────────────────────────────────────────────────────
@router.get("/commandes", response_model=dict)
async def list_commandes(
    skip: int = 0,
    limit: int = Query(100, le=500),
    statut: Optional[str] = None,
    db: Session = Depends(get_db),
):
    q = db.query(Commande)
    if statut:
        q = q.filter(Commande.statut == statut)
    total = q.count()
    items = q.offset(skip).limit(limit).all()
    return {
        "items": [CommandeResponse.model_validate(c).model_dump() for c in items],
        "total": total,
        "pending": False,
    }


@router.post("/commandes", response_model=CommandeResponse, status_code=201)
async def create_commande(payload: CommandeCreate, db: Session = Depends(get_db)):
    data = payload.model_dump()
    lignes = data.pop("lignes", [])
    row = Commande(reference=data.pop("reference", None) or _ref("CMD"), **data)
    db.add(row)
    db.flush()
    for lg in lignes:
        db.add(LigneCommande(commande_id=row.id, **lg))
    db.commit()
    db.refresh(row)
    return row


@router.get("/commandes/{commande_id}", response_model=CommandeResponse)
async def get_commande(commande_id: int, db: Session = Depends(get_db)):
    return _get_or_404(Commande, db, commande_id, "Commande")


def _transition(commande_id: int, db: Session, target: CommandeStatut):
    row = _get_or_404(Commande, db, commande_id, "Commande")
    if row.statut == CommandeStatut.ANNULEE:
        raise HTTPException(status_code=400, detail="Commande annulee : transition impossible")
    row.statut = target
    db.commit()
    db.refresh(row)
    return row


@router.post("/commandes/{commande_id}/valider", response_model=CommandeResponse)
async def valider_commande(commande_id: int, db: Session = Depends(get_db)):
    return _transition(commande_id, db, CommandeStatut.VALIDEE)


@router.post("/commandes/{commande_id}/preparer", response_model=CommandeResponse)
async def preparer_commande(commande_id: int, db: Session = Depends(get_db)):
    return _transition(commande_id, db, CommandeStatut.EN_PREPARATION)


@router.post("/commandes/{commande_id}/valider-paiement", response_model=CommandeResponse)
async def valider_paiement_commande(commande_id: int, db: Session = Depends(get_db)):
    return _transition(commande_id, db, CommandeStatut.PRETE)


@router.post("/commandes/{commande_id}/annuler", response_model=CommandeResponse)
async def annuler_commande(commande_id: int, db: Session = Depends(get_db)):
    return _transition(commande_id, db, CommandeStatut.ANNULEE)


# ─── ORDRES DE TRANSFERT ─────────────────────────────────────────────────────
@router.get("/ordres-transfert", response_model=dict)
async def list_ordres_transfert(
    skip: int = 0,
    limit: int = Query(100, le=500),
    statut: Optional[str] = None,
    db: Session = Depends(get_db),
):
    q = db.query(OrdreTransfert)
    if statut:
        q = q.filter(OrdreTransfert.statut == statut)
    total = q.count()
    items = q.offset(skip).limit(limit).all()
    return {
        "items": [OrdreTransfertResponse.model_validate(o).model_dump() for o in items],
        "total": total,
        "pending": False,
    }


@router.post("/ordres-transfert", response_model=OrdreTransfertResponse, status_code=201)
async def create_ordre_transfert(payload: OrdreTransfertCreate, db: Session = Depends(get_db)):
    data = payload.model_dump()
    row = OrdreTransfert(reference=data.pop("reference", None) or _ref("OT"), **data)
    db.add(row)
    db.commit()
    db.refresh(row)
    return row


@router.get("/ordres-transfert/{ot_id}", response_model=OrdreTransfertResponse)
async def get_ordre_transfert(ot_id: int, db: Session = Depends(get_db)):
    return _get_or_404(OrdreTransfert, db, ot_id, "Ordre de transfert")


def _ot_transition(ot_id: int, db: Session, target: TransfertStatut):
    row = _get_or_404(OrdreTransfert, db, ot_id, "Ordre de transfert")
    if row.statut == TransfertStatut.ANNULE:
        raise HTTPException(status_code=400, detail="Transfert annule : transition impossible")
    row.statut = target
    db.commit()
    db.refresh(row)
    return row


@router.post("/ordres-transfert/{ot_id}/valider", response_model=OrdreTransfertResponse)
async def valider_ot(ot_id: int, db: Session = Depends(get_db)):
    return _ot_transition(ot_id, db, TransfertStatut.VALIDE)


@router.post("/ordres-transfert/{ot_id}/valider-paiement", response_model=OrdreTransfertResponse)
async def valider_paiement_ot(ot_id: int, db: Session = Depends(get_db)):
    return _ot_transition(ot_id, db, TransfertStatut.PAYE)


@router.post("/ordres-transfert/{ot_id}/expedier", response_model=OrdreTransfertResponse)
async def expedier_ot(ot_id: int, db: Session = Depends(get_db)):
    return _ot_transition(ot_id, db, TransfertStatut.EXPEDIE)


@router.post("/ordres-transfert/{ot_id}/receptionner", response_model=OrdreTransfertResponse)
async def receptionner_ot(ot_id: int, db: Session = Depends(get_db)):
    return _ot_transition(ot_id, db, TransfertStatut.RECEPTIONNE)


@router.post("/ordres-transfert/{ot_id}/annuler", response_model=OrdreTransfertResponse)
async def annuler_ot(ot_id: int, db: Session = Depends(get_db)):
    return _ot_transition(ot_id, db, TransfertStatut.ANNULE)


# ─── BANDES DE LIVRAISON ─────────────────────────────────────────────────────
@router.get("/bandes-livraison", response_model=dict)
async def list_bandes(
    skip: int = 0,
    limit: int = Query(100, le=500),
    statut: Optional[str] = None,
    db: Session = Depends(get_db),
):
    q = db.query(BandeLivraison)
    if statut:
        q = q.filter(BandeLivraison.statut == statut)
    total = q.count()
    items = q.offset(skip).limit(limit).all()
    return {
        "items": [BandeLivraisonResponse.model_validate(b).model_dump() for b in items],
        "total": total,
        "pending": False,
    }


@router.post("/bandes-livraison", response_model=BandeLivraisonResponse, status_code=201)
async def create_bande(payload: BandeLivraisonCreate, db: Session = Depends(get_db)):
    data = payload.model_dump()
    row = BandeLivraison(
        reference=data.pop("reference", None) or _ref("BL"),
        date_preparation=datetime.now(),
        **data,
    )
    db.add(row)
    db.commit()
    db.refresh(row)
    return row


@router.get("/bandes-livraison/ordre-transfert/{ot_id}", response_model=list[BandeLivraisonResponse])
async def get_bandes_by_ot(ot_id: int, db: Session = Depends(get_db)):
    return db.query(BandeLivraison).filter(BandeLivraison.ordre_transfert_id == ot_id).all()


@router.post("/bandes-livraison/from-ordre-transfert/{ot_id}", response_model=BandeLivraisonResponse, status_code=201)
async def create_bande_from_ot(ot_id: int, prepare_par: Optional[str] = None, db: Session = Depends(get_db)):
    ot = _get_or_404(OrdreTransfert, db, ot_id, "Ordre de transfert")
    row = BandeLivraison(
        reference=_ref("BL"),
        ordre_transfert_id=ot.id,
        prepare_par=prepare_par,
        poids_total=ot.quantite,
        statut="en_preparation",
        date_preparation=datetime.now(),
    )
    db.add(row)
    db.commit()
    db.refresh(row)
    return row


@router.get("/bandes-livraison/{bande_id}", response_model=BandeLivraisonResponse)
async def get_bande(bande_id: int, db: Session = Depends(get_db)):
    return _get_or_404(BandeLivraison, db, bande_id, "Bande de livraison")


@router.put("/bandes-livraison/{bande_id}", response_model=BandeLivraisonResponse)
async def update_bande(bande_id: int, payload: BandeLivraisonUpdate, db: Session = Depends(get_db)):
    row = _get_or_404(BandeLivraison, db, bande_id, "Bande de livraison")
    for k, v in payload.model_dump(exclude_unset=True).items():
        setattr(row, k, v)
    db.commit()
    db.refresh(row)
    return row
