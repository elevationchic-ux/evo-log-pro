"""Advanced warehouse router - FEFO, reservations, transfers, cycle counting"""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy import and_
from typing import List
from datetime import date, datetime, timedelta

from app.core.database import get_db
from app.core.security import get_current_user
from app.models.user import User
from app.schemas.magasin_avance import (
    PeremptionCreate, PeremptionResponse,
    ReservationStockCreate, ReservationStockResponse,
    KitArticleCreate, KitArticleResponse,
    ComposantKitCreate, ComposantKitResponse,
    EmplacementDetailCreate, EmplacementDetailResponse,
    TransfertStockCreate, TransfertStockResponse,
    InventaireTournantCreate, InventaireTournantResponse,
    LigneInventaireCreate, LigneInventaireResponse,
    FournisseurStockCreate, FournisseurStockResponse,
    CommandeFournisseurCreate, CommandeFournisseurResponse,
    LigneCommandeFournisseurCreate, LigneCommandeFournisseurResponse,
    BonReceptionCreate, BonReceptionResponse,
    LigneBonReceptionCreate, LigneBonReceptionResponse,
    BonSortieCreate, BonSortieResponse,
    LigneBonSortieCreate, LigneBonSortieResponse,
    RetourClientCreate, RetourClientUpdate, RetourClientResponse,
    LitigeTransporteurCreate, LitigeTransporteurUpdate, LitigeTransporteurResponse,
    ColisCreate, ColisUpdate, ColisResponse,
    RotationStockResponse, PrecisionInventaireResponse, PerformanceFournisseurResponse
)
from app.services.magasin_avance_service import (
    ColisService
)

router = APIRouter(tags=["Magasin Avancé"])


# ============ PÉREMPTIONS / FEFO ============
@router.post("/peremptions", response_model=PeremptionResponse, status_code=status.HTTP_201_CREATED)
def enregistrer_peremption(
    peremption: PeremptionCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Register expiration date for lot/serial tracking"""
    from app.models.magasin_avance import Peremption
    p = Peremption(
        stock_id=peremption.stock_id,
        date_peremption=peremption.date_peremption,
        lot_numero=peremption.lot_numero,
        numero_serie=peremption.numero_serie
    )
    db.add(p)
    db.commit()
    db.refresh(p)
    return p


@router.get("/peremptions/fefo/{article_id}/{quantite}")
def obtenir_stock_fefo(
    article_id: int,
    quantite: float,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get stock using FEFO (First Expired, First Out)"""
    from app.models.magasin_avance import Peremption
    from app.models.magasin import Stock
    from sqlalchemy import and_
    
    peremptions = db.query(Peremption).join(Stock).filter(
        and_(
            Stock.article_id == article_id,
            Stock.quantite > 0,
            Peremption.date_peremption >= date.today()
        )
    ).order_by(Peremption.date_peremption.asc()).all()
    
    return peremptions


@router.get("/peremptions/critiques")
def obtenir_peremptions_critiques(
    jours_critique: int = 30,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get stock expiring within critical period"""
    from app.models.magasin_avance import Peremption
    from app.models.magasin import Stock
    from sqlalchemy import and_
    
    date_limite = date.today() + timedelta(days=jours_critique)
    
    peremptions = db.query(Peremption).join(Stock).filter(
        and_(
            Peremption.date_peremption <= date_limite,
            Peremption.date_peremption >= date.today(),
            Stock.quantite > 0
        )
    ).order_by(Peremption.date_peremption.asc()).all()
    
    return peremptions


@router.get("/peremptions/expirees")
def obtenir_peremptions_expirees(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get expired stock for quarantine"""
    from app.models.magasin_avance import Peremption
    from app.models.magasin import Stock
    from sqlalchemy import and_
    
    return db.query(Peremption).join(Stock).filter(
        and_(
            Peremption.date_peremption < date.today(),
            Stock.quantite > 0
        )
    ).all()


# ============ RÉSERVATIONS ============
@router.post("/reservations", response_model=ReservationStockResponse, status_code=status.HTTP_201_CREATED)
def reserver_stock(
    reservation: ReservationStockCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Reserve stock for specific purpose"""
    from app.models.magasin_avance import ReservationStock
    from app.models.magasin import Stock
    
    stock = db.query(Stock).filter(Stock.id == reservation.stock_id).first()
    if not stock:
        raise HTTPException(status_code=404, detail="Stock non trouvé")
    
    if stock.quantite_disponible < reservation.quantite:
        raise HTTPException(status_code=400, detail="Stock insuffisant")
    
    r = ReservationStock(
        stock_id=reservation.stock_id,
        type_reservation=reservation.type_reservation,
        reference_id=reservation.reference_id,
        quantite=reservation.quantite,
        date_reservation=datetime.utcnow(),
        date_expiration=reservation.date_expiration or (date.today() + timedelta(days=7))
    )
    
    stock.quantite_disponible -= reservation.quantite
    stock.quantite_reservee = (stock.quantite_reservee or 0) + reservation.quantite
    
    db.add(r)
    db.commit()
    db.refresh(r)
    return r


@router.put("/reservations/{reservation_id}/liberer", response_model=ReservationStockResponse)
def liberer_reservation(
    reservation_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Release stock reservation"""
    from app.models.magasin_avance import ReservationStock
    from app.models.magasin import Stock
    
    r = db.query(ReservationStock).filter(ReservationStock.id == reservation_id).first()
    if not r:
        raise HTTPException(status_code=404, detail="Réservation non trouvée")
    
    stock = db.query(Stock).filter(Stock.id == r.stock_id).first()
    if stock:
        stock.quantite_disponible += r.quantite
        stock.quantite_reservee = max(0, (stock.quantite_reservee or 0) - r.quantite)
    
    r.statut = "libere"
    r.date_liberation = datetime.utcnow()
    
    db.commit()
    db.refresh(r)
    return r


@router.put("/reservations/{reservation_id}/consommer", response_model=ReservationStockResponse)
def consommer_reservation(
    reservation_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Consume reserved stock"""
    from app.models.magasin_avance import ReservationStock
    from app.models.magasin import Stock
    
    r = db.query(ReservationStock).filter(ReservationStock.id == reservation_id).first()
    if not r:
        raise HTTPException(status_code=404, detail="Réservation non trouvée")
    
    stock = db.query(Stock).filter(Stock.id == r.stock_id).first()
    if stock:
        stock.quantite -= r.quantite
        stock.quantite_reservee = max(0, (stock.quantite_reservee or 0) - r.quantite)
    
    r.statut = "consomme"
    r.date_consommation = datetime.utcnow()
    
    db.commit()
    db.refresh(r)
    return r


@router.post("/reservations/nettoyer")
def nettoyer_reservations_expirees(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Auto-release expired reservations"""
    from app.models.magasin_avance import ReservationStock
    from app.models.magasin import Stock
    
    date_limite = date.today()
    
    reservations = db.query(ReservationStock).filter(
        and_(
            ReservationStock.statut == "active",
            ReservationStock.date_expiration < date_limite
        )
    ).all()
    
    compte = 0
    for r in reservations:
        stock = db.query(Stock).filter(Stock.id == r.stock_id).first()
        if stock:
            stock.quantite_disponible += r.quantite
            stock.quantite_reservee = max(0, (stock.quantite_reservee or 0) - r.quantite)
        
        r.statut = "libere"
        r.date_liberation = datetime.utcnow()
        compte += 1
    
    db.commit()
    return {"reservations_liberees": compte}


# ============ KITS ============
@router.post("/kits", response_model=KitArticleResponse, status_code=status.HTTP_201_CREATED)
def creer_kit(
    kit: KitArticleCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Create kit definition"""
    from app.models.magasin_avance import KitArticle
    k = KitArticle(
        article_kit_id=kit.article_kit_id,
        nom_kit=kit.nom_kit,
        description=kit.description
    )
    db.add(k)
    db.commit()
    db.refresh(k)
    return k


@router.post("/kits/{kit_id}/composants", response_model=ComposantKitResponse, status_code=status.HTTP_201_CREATED)
def ajouter_composant(
    kit_id: int,
    composant: ComposantKitCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Add component to kit"""
    from app.models.magasin_avance import ComposantKit
    c = ComposantKit(
        kit_id=kit_id,
        article_composant_id=composant.article_composant_id,
        quantite=composant.quantite
    )
    db.add(c)
    db.commit()
    db.refresh(c)
    return c


@router.post("/kits/{kit_id}/assembler")
def assembler_kit(
    kit_id: int,
    quantite_kits: float,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Assemble kits from components"""
    from app.models.magasin_avance import KitArticle, ComposantKit
    from app.models.magasin import Stock, Entrepot
    
    kit = db.query(KitArticle).filter(KitArticle.id == kit_id).first()
    if not kit:
        raise HTTPException(status_code=404, detail="Kit non trouvé")
    
    composants = db.query(ComposantKit).filter(ComposantKit.kit_id == kit_id).all()
    
    for comp in composants:
        stock = db.query(Stock).filter(Stock.article_id == comp.article_composant_id).first()
        if not stock or stock.quantite_disponible < (comp.quantite * quantite_kits):
            raise HTTPException(status_code=400, detail="Stock insuffisant pour composant")
    
    for comp in composants:
        stock = db.query(Stock).filter(Stock.article_id == comp.article_composant_id).first()
        stock.quantite -= comp.quantite * quantite_kits
        stock.quantite_disponible -= comp.quantite * quantite_kits
    
    stock_kit = db.query(Stock).filter(Stock.article_id == kit.article_kit_id).first()
    if stock_kit:
        stock_kit.quantite += quantite_kits
        stock_kit.quantite_disponible += quantite_kits
    else:
        entrepot = db.query(Entrepot).first()
        if entrepot:
            nouveau_stock = Stock(
                article_id=kit.article_kit_id,
                entrepot_id=entrepot.id,
                quantite=quantite_kits,
                quantite_disponible=quantite_kits
            )
            db.add(nouveau_stock)
    
    db.commit()
    return {"kit_id": kit_id, "quantite_assemblee": quantite_kits}


# ============ EMPLACEMENTS ============
@router.post("/emplacements", response_model=EmplacementDetailResponse, status_code=status.HTTP_201_CREATED)
def definir_emplacement(
    emplacement: EmplacementDetailCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Define detailed storage location"""
    from app.models.magasin_avance import EmplacementDetail
    e = EmplacementDetail(
        entrepot_id=emplacement.entrepot_id,
        zone=emplacement.zone,
        allee=emplacement.allee,
        rack=emplacement.rack,
        casier=emplacement.casier,
        niveau=emplacement.niveau
    )
    db.add(e)
    db.commit()
    db.refresh(e)
    return e


@router.get("/emplacements/{emplacement_id}/stock")
def obtenir_stock_par_emplacement(
    emplacement_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get all stock at specific location"""
    from app.models.magasin import Stock
    return db.query(Stock).filter(Stock.emplacement_detail_id == emplacement_id).all()


# ============ TRANSFERTS ============
@router.post("/transferts", response_model=TransfertStockResponse, status_code=status.HTTP_201_CREATED)
def creer_transfert(
    transfert: TransfertStockCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Create stock transfer between warehouses"""
    from app.models.magasin_avance import TransfertStock
    t = TransfertStock(
        stock_id=transfert.stock_id,
        entrepot_source_id=transfert.entrepot_source_id,
        entrepot_destination_id=transfert.entrepot_destination_id,
        quantite=transfert.quantite,
        motif=transfert.motif,
        date_transfert=transfert.date_transfert or date.today(),
        statut="en_attente"
    )
    db.add(t)
    db.commit()
    db.refresh(t)
    return t


@router.put("/transferts/{transfert_id}/executer", response_model=TransfertStockResponse)
def executer_transfert(
    transfert_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Execute transfer (move stock)"""
    from app.models.magasin_avance import TransfertStock
    from app.models.magasin import Stock
    
    t = db.query(TransfertStock).filter(TransfertStock.id == transfert_id).first()
    if not t:
        raise HTTPException(status_code=404, detail="Transfert non trouvé")
    
    stock_source = db.query(Stock).filter(
        and_(
            Stock.id == t.stock_id,
            Stock.entrepot_id == t.entrepot_source_id
        )
    ).first()
    
    if not stock_source or stock_source.quantite < t.quantite:
        raise HTTPException(status_code=400, detail="Stock source insuffisant")
    
    stock_source.quantite -= t.quantite
    stock_source.quantite_disponible -= t.quantite
    
    stock_dest = db.query(Stock).filter(
        and_(
            Stock.article_id == stock_source.article_id,
            Stock.entrepot_id == t.entrepot_destination_id
        )
    ).first()
    
    if stock_dest:
        stock_dest.quantite += t.quantite
        stock_dest.quantite_disponible += t.quantite
    else:
        nouveau_stock = Stock(
            article_id=stock_source.article_id,
            entrepot_id=t.entrepot_destination_id,
            quantite=t.quantite,
            quantite_disponible=t.quantite
        )
        db.add(nouveau_stock)
    
    t.statut = "complete"
    t.date_execution = datetime.utcnow()
    
    db.commit()
    db.refresh(t)
    return t


# ============ INVENTAIRE TOURNANT ============
@router.post("/inventaires", response_model=InventaireTournantResponse, status_code=status.HTTP_201_CREATED)
def creer_inventaire(
    inventaire: InventaireTournantCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Create cycle count inventory"""
    from app.models.magasin_avance import InventaireTournant
    i = InventaireTournant(
        entrepot_id=inventaire.entrepot_id,
        date_inventaire=inventaire.date_inventaire,
        type_inventaire=inventaire.type_inventaire,
        statut="en_cours"
    )
    db.add(i)
    db.commit()
    db.refresh(i)
    return i


@router.post("/inventaires/{inventaire_id}/lignes", response_model=LigneInventaireResponse, status_code=status.HTTP_201_CREATED)
def ajouter_ligne_inventaire(
    inventaire_id: int,
    ligne: LigneInventaireCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Add counted item to inventory"""
    from app.models.magasin_avance import LigneInventaire
    from app.models.magasin import Stock
    
    stock = db.query(Stock).filter(Stock.id == ligne.stock_id).first()
    if not stock:
        raise HTTPException(status_code=404, detail="Stock non trouvé")
    
    ecart = ligne.quantite_comptee - stock.quantite
    
    l = LigneInventaire(
        inventaire_id=inventaire_id,
        stock_id=ligne.stock_id,
        quantite_theorique=stock.quantite,
        quantite_comptee=ligne.quantite_comptee,
        ecart=ecart,
        compteur_id=ligne.compteur_id,
        date_comptage=datetime.utcnow()
    )
    db.add(l)
    db.commit()
    db.refresh(l)
    return l


@router.put("/inventaires/{inventaire_id}/valider", response_model=InventaireTournantResponse)
def valider_inventaire(
    inventaire_id: int,
    validateur_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Validate inventory and adjust stock"""
    from app.models.magasin_avance import InventaireTournant, LigneInventaire
    from app.models.magasin import Stock
    
    inventaire = db.query(InventaireTournant).filter(InventaireTournant.id == inventaire_id).first()
    if not inventaire:
        raise HTTPException(status_code=404, detail="Inventaire non trouvé")
    
    lignes = db.query(LigneInventaire).filter(LigneInventaire.inventaire_id == inventaire_id).all()
    
    for ligne in lignes:
        if ligne.ecart != 0:
            stock = db.query(Stock).filter(Stock.id == ligne.stock_id).first()
            if stock:
                stock.quantite = ligne.quantite_comptee
                stock.quantite_disponible = ligne.quantite_comptee - (stock.quantite_reservee or 0)
    
    inventaire.statut = "valide"
    inventaire.validateur_id = validateur_id
    inventaire.date_validation = datetime.utcnow()
    
    db.commit()
    db.refresh(inventaire)
    return inventaire


@router.get("/inventaires/{inventaire_id}/precision", response_model=PrecisionInventaireResponse)
def calculer_precision_inventaire(
    inventaire_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Calculate inventory accuracy percentage"""
    from app.models.magasin_avance import LigneInventaire
    
    lignes = db.query(LigneInventaire).filter(LigneInventaire.inventaire_id == inventaire_id).all()
    
    if not lignes:
        return {"inventaire_id": inventaire_id, "precision": 0.0}
    
    lignes_correctes = sum(1 for l in lignes if l.ecart == 0)
    precision = (lignes_correctes / len(lignes)) * 100
    
    return {"inventaire_id": inventaire_id, "precision": round(precision, 2)}


# ============ FOURNISSEURS ============
@router.post("/fournisseurs-stock", response_model=FournisseurStockResponse, status_code=status.HTTP_201_CREATED)
def creer_fournisseur_stock(
    fournisseur: FournisseurStockCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Create supplier stock record"""
    from app.models.magasin_avance import FournisseurStock
    fs = FournisseurStock(
        fournisseur_id=fournisseur.fournisseur_id,
        delai_livraison_jours=fournisseur.delai_livraison_jours,
        qualite=fournisseur.qualite,
        fiabilite=fournisseur.fiabilite
    )
    db.add(fs)
    db.commit()
    db.refresh(fs)
    return fs


@router.get("/fournisseurs/{fournisseur_id}/performance")
def evaluer_performance_fournisseur(
    fournisseur_id: int,
    debut_periode: date,
    fin_periode: date,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Evaluate supplier performance"""
    from app.models.magasin_avance import CommandeFournisseur, MissionSousTraitant
    from sqlalchemy import func, and_
    
    commandes = db.query(CommandeFournisseur).filter(
        and_(
            CommandeFournisseur.fournisseur_id == fournisseur_id,
            CommandeFournisseur.date_commande >= debut_periode,
            CommandeFournisseur.date_commande <= fin_periode
        )
    ).all()
    
    if not commandes:
        return {"note": 0, "commandes": 0, "taux_livraison": 0}
    
    total_commandes = len(commandes)
    commandes_livrees = sum(1 for c in commandes if c.statut == "recu")
    taux_livraison = (commandes_livrees / total_commandes) * 100
    
    delais = []
    for cmd in commandes:
        if cmd.date_livraison and cmd.date_prevue:
            delai = (cmd.date_livraison - cmd.date_prevue).days
            delais.append(delai)
    
    delai_moyen = sum(delais) / len(delais) if delais else 0
    note = min(100, taux_livraison * 0.7 + max(0, 100 - abs(delai_moyen)) * 0.3)
    
    return {
        "note": round(note, 2),
        "commandes": total_commandes,
        "commandes_livrees": commandes_livrees,
        "taux_livraison": round(taux_livraison, 2),
        "delai_moyen_jours": round(delai_moyen, 2)
    }


# ============ RÉAPPROVISIONNEMENT ============
@router.post("/reapprovisionnement/automatique/{fournisseur_id}")
def generer_commande_automatique(
    fournisseur_id: int,
    seuil_alerte: float = 10.0,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Generate purchase orders for stock below threshold"""
    from app.models.magasin_avance import CommandeFournisseur, LigneCommandeFournisseur
    from app.models.magasin import Stock
    
    stocks_bas = db.query(Stock).filter(
        Stock.quantite_disponible < seuil_alerte
    ).all()
    
    commandes_generees = []
    for stock in stocks_bas:
        quantite_commandee = seuil_alerte * 2
        
        commande = CommandeFournisseur(
            fournisseur_id=fournisseur_id,
            reference=f"CMD-{datetime.utcnow().strftime('%Y%m%d%H%M%S')}",
            date_commande=date.today(),
            date_prevue=date.today() + timedelta(days=7),
            statut="en_attente"
        )
        db.add(commande)
        db.flush()
        
        ligne = LigneCommandeFournisseur(
            commande_id=commande.id,
            article_id=stock.article_id,
            quantite_commandee=quantite_commandee,
            prix_unitaire=0.0
        )
        db.add(ligne)
        
        commandes_generees.append({
            "article_id": stock.article_id,
            "quantite": quantite_commandee,
            "commande_id": commande.id
        })
    
    db.commit()
    return commandes_generees


# ============ RÉCEPTIONS ============
@router.post("/receptions", response_model=BonReceptionResponse, status_code=status.HTTP_201_CREATED)
def creer_bon_reception(
    bon: BonReceptionCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Create goods receipt note"""
    from app.models.magasin_avance import BonReception
    b = BonReception(
        commande_id=bon.commande_id,
        fournisseur_id=bon.fournisseur_id,
        date_reception=bon.date_reception,
        statut="en_cours"
    )
    db.add(b)
    db.commit()
    db.refresh(b)
    return b


@router.post("/receptions/{bon_id}/lignes", response_model=LigneBonReceptionResponse, status_code=status.HTTP_201_CREATED)
def ajouter_ligne_reception(
    bon_id: int,
    ligne: LigneBonReceptionCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Add received item line"""
    from app.models.magasin_avance import LigneBonReception
    l = LigneBonReception(
        bon_id=bon_id,
        article_id=ligne.article_id,
        quantite_recue=ligne.quantite_recue,
        quantite_commandee=ligne.quantite_commandee,
        emplacement_id=ligne.emplacement_id
    )
    db.add(l)
    db.commit()
    db.refresh(l)
    return l


@router.put("/receptions/{bon_id}/valider", response_model=BonReceptionResponse)
def valider_reception(
    bon_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Validate receipt and update stock"""
    from app.models.magasin_avance import BonReception, LigneBonReception
    from app.models.magasin import Stock, Entrepot
    
    bon = db.query(BonReception).filter(BonReception.id == bon_id).first()
    if not bon:
        raise HTTPException(status_code=404, detail="Bon de réception non trouvé")
    
    lignes = db.query(LigneBonReception).filter(LigneBonReception.bon_id == bon_id).all()
    entrepot = db.query(Entrepot).first()
    
    for ligne in lignes:
        stock = db.query(Stock).filter(
            Stock.article_id == ligne.article_id
        ).first()
        
        if stock:
            stock.quantite += ligne.quantite_recue
            stock.quantite_disponible += ligne.quantite_recue
        else:
            nouveau_stock = Stock(
                article_id=ligne.article_id,
                entrepot_id=entrepot.id if entrepot else 1,
                quantite=ligne.quantite_recue,
                quantite_disponible=ligne.quantite_recue,
                emplacement_detail_id=ligne.emplacement_id
            )
            db.add(nouveau_stock)
    
    bon.statut = "valide"
    bon.date_validation = datetime.utcnow()
    
    db.commit()
    db.refresh(bon)
    return bon


# ============ SORTIES ============
@router.post("/sorties", response_model=BonSortieResponse, status_code=status.HTTP_201_CREATED)
def creer_bon_sortie(
    bon: BonSortieCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Create goods issue note"""
    from app.models.magasin_avance import BonSortie
    b = BonSortie(
        destinataire_id=bon.destinataire_id,
        type_sortie=bon.type_sortie,
        date_sortie=bon.date_sortie,
        statut="en_cours"
    )
    db.add(b)
    db.commit()
    db.refresh(b)
    return b


@router.post("/sorties/{bon_id}/lignes", response_model=LigneBonSortieResponse, status_code=status.HTTP_201_CREATED)
def ajouter_ligne_sortie(
    bon_id: int,
    ligne: LigneBonSortieCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Add item to issue note"""
    from app.models.magasin_avance import LigneBonSortie
    from app.models.magasin import Stock
    
    stock = db.query(Stock).filter(Stock.id == ligne.stock_id).first()
    if not stock or stock.quantite_disponible < ligne.quantite:
        raise HTTPException(status_code=400, detail="Stock insuffisant")
    
    l = LigneBonSortie(
        bon_id=bon_id,
        stock_id=ligne.stock_id,
        quantite=ligne.quantite
    )
    db.add(l)
    db.commit()
    db.refresh(l)
    return l


@router.put("/sorties/{bon_id}/valider", response_model=BonSortieResponse)
def valider_sortie(
    bon_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Validate issue and deduct stock"""
    from app.models.magasin_avance import BonSortie, LigneBonSortie
    from app.models.magasin import Stock
    
    bon = db.query(BonSortie).filter(BonSortie.id == bon_id).first()
    if not bon:
        raise HTTPException(status_code=404, detail="Bon de sortie non trouvé")
    
    lignes = db.query(LigneBonSortie).filter(LigneBonSortie.bon_id == bon_id).all()
    
    for ligne in lignes:
        stock = db.query(Stock).filter(Stock.id == ligne.stock_id).first()
        if stock:
            stock.quantite -= ligne.quantite
            stock.quantite_disponible -= ligne.quantite
    
    bon.statut = "valide"
    bon.date_validation = datetime.utcnow()
    
    db.commit()
    db.refresh(bon)
    return bon


# ============ RETOURS CLIENTS ============
@router.post("/retours", response_model=RetourClientResponse, status_code=status.HTTP_201_CREATED)
def enregistrer_retour(
    retour: RetourClientCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Register customer return"""
    from app.models.magasin_avance import RetourClient
    r = RetourClient(
        client_id=retour.client_id,
        article_id=retour.article_id,
        quantite=retour.quantite,
        motif=retour.motif,
        etat=retour.etat,
        date_retour=datetime.utcnow()
    )
    db.add(r)
    db.commit()
    db.refresh(r)
    return r


@router.put("/retours/{retour_id}/traiter", response_model=RetourClientResponse)
def traiter_retour(
    retour_id: int,
    action: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Process return (repair, replace, refund)"""
    from app.models.magasin_avance import RetourClient
    r = db.query(RetourClient).filter(RetourClient.id == retour_id).first()
    if not r:
        raise HTTPException(status_code=404, detail="Retour non trouvé")
    r.action_effectuee = action
    r.date_traitement = datetime.utcnow()
    r.statut = "traite"
    db.commit()
    db.refresh(r)
    return r


# ============ LITIGES TRANSPORTEURS ============
@router.post("/litiges", response_model=LitigeTransporteurResponse, status_code=status.HTTP_201_CREATED)
def creer_litige(
    litige: LitigeTransporteurCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Create carrier dispute"""
    from app.models.magasin_avance import LitigeTransporteur
    l = LitigeTransporteur(
        transporteur_id=litige.transporteur_id,
        type_litige=litige.type_litige,
        description=litige.description,
        montant_reclame=litige.montant_reclame,
        date_litige=datetime.utcnow()
    )
    db.add(l)
    db.commit()
    db.refresh(l)
    return l


@router.put("/litiges/{litige_id}/resoudre", response_model=LitigeTransporteurResponse)
def resoudre_litige(
    litige_id: int,
    resolution: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Resolve carrier dispute"""
    from app.models.magasin_avance import LitigeTransporteur
    l = db.query(LitigeTransporteur).filter(LitigeTransporteur.id == litige_id).first()
    if not l:
        raise HTTPException(status_code=404, detail="Litige non trouvé")
    l.resolution = resolution
    l.statut = "resolu"
    l.date_resolution = datetime.utcnow()
    db.commit()
    db.refresh(l)
    return l


# ============ COLIS ============
@router.post("/colis", response_model=ColisResponse, status_code=status.HTTP_201_CREATED)
def creer_colis(
    colis: ColisCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Create package record"""
    return ColisService.creer_colis(
        db, colis.reference_colis, colis.poids,
        colis.dimensions, colis.contenu
    )


@router.put("/colis/{colis_id}/etiqueter", response_model=ColisResponse)
def etiqueter_colis(
    colis_id: int,
    code_barres: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Label package with barcode"""
    return ColisService.etiqueter_colis(db, colis_id, code_barres)


@router.put("/colis/{colis_id}/palettiser", response_model=ColisResponse)
def palettiser_colis(
    colis_id: int,
    palette_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Palletize package"""
    return ColisService.palettiser_colis(db, colis_id, palette_id)


# ============ KPIs ============
@router.get("/kpi/rotation/{article_id}", response_model=RotationStockResponse)
def calculer_rotation_stock(
    article_id: int,
    jours: int = 90,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Calculate stock turnover rate"""
    from app.models.magasin import MouvementStock
    from sqlalchemy import func, and_
    from datetime import timedelta
    
    date_debut = date.today() - timedelta(days=jours)
    
    sorties = db.query(func.sum(MouvementStock.quantite)).filter(
        and_(
            MouvementStock.article_id == article_id,
            MouvementStock.type_mouvement == "sortie",
            MouvementStock.date_mouvement >= date_debut
        )
    ).scalar() or 0
    
    from app.models.magasin import Stock
    stock_actuel = db.query(Stock.quantite).filter(
        Stock.article_id == article_id
    ).scalar() or 0
    
    if stock_actuel == 0:
        rotation = 0.0
    else:
        rotation = (sorties / stock_actuel) * (365 / jours)
    
    return {"article_id": article_id, "rotation": round(rotation, 2)}


@router.get("/kpi/precision/{entrepot_id}")
def calculer_precision_stock(
    entrepot_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Calculate overall inventory accuracy"""
    from app.models.magasin_avance import InventaireTournant, LigneInventaire
    
    dernier_inventaire = db.query(InventaireTournant).filter(
        and_(
            InventaireTournant.entrepot_id == entrepot_id,
            InventaireTournant.statut == "valide"
        )
    ).order_by(InventaireTournant.date_inventaire.desc()).first()
    
    if not dernier_inventaire:
        return {"entrepot_id": entrepot_id, "precision": 0.0}
    
    lignes = db.query(LigneInventaire).filter(
        LigneInventaire.inventaire_id == dernier_inventaire.id
    ).all()
    
    if not lignes:
        return {"entrepot_id": entrepot_id, "precision": 0.0}
    
    lignes_correctes = sum(1 for l in lignes if l.ecart == 0)
    precision = (lignes_correctes / len(lignes)) * 100
    
    return {"entrepot_id": entrepot_id, "precision": round(precision, 2)}
