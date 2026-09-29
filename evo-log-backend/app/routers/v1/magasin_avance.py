"""Advanced warehouse router - FEFO, reservations, transfers, cycle counting"""
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session
from sqlalchemy import and_, func
from typing import List, Optional
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
    BonReceptionCreate, BonReceptionUpdate, BonReceptionResponse,
    LigneBonReceptionCreate, LigneBonReceptionResponse, RefusBonReception,
    RetourClientCreate, RetourClientUpdate, RetourClientTraitement, RetourClientResponse,
    LitigeTransporteurCreate, LitigeTransporteurUpdate, LitigeTransporteurResolution, LitigeTransporteurResponse,
    ColisCreate, ColisUpdate, ColisResponse,
    RotationStockResponse, PrecisionInventaireResponse, PerformanceFournisseurResponse,
    ReapproAutomatiqueResponse
)

# ColisService IMPORTÉ PUIS SUPPRIMÉ (Batch 19) : ses trois methodes
# ecrivaient des colonnes fantomes (reference_colis, code_barres, palette_id,
# date_creation, date_palettisation). Les routes /colis sont reconstruites
# en direct sur le modele reel plus haut dans ce fichier.

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
    """Ouvre un inventaire tournant (Batch 18, modèle réel InventaireTournant).

    L'ancienne version construisait InventaireTournant(date_inventaire=...) :
    TypeError 500 garanti (colonne réelle : date_debut/date_fin/responsable).
    numero_inventaire, unique NOT NULL, est généré ici (INV-YYYYMMDD-NNNN).
    """
    from app.models.magasin_avance import InventaireTournant
    from app.models.magasin import Entrepot

    if not db.query(Entrepot).filter(Entrepot.id == inventaire.entrepot_id).first():
        raise HTTPException(status_code=404, detail="Entrepot inexistant")
    if inventaire.date_fin and inventaire.date_fin < inventaire.date_debut:
        raise HTTPException(status_code=400, detail="date_fin antérieure à date_debut")

    i = InventaireTournant(
        numero_inventaire=_prochaine_rotation_numero(
            db, InventaireTournant, "numero_inventaire", "INV"),
        entrepot_id=inventaire.entrepot_id,
        date_debut=inventaire.date_debut,
        date_fin=inventaire.date_fin,
        type_inventaire=inventaire.type_inventaire,
        statut="en_cours",
        responsable=current_user.id,
        notes=inventaire.notes,
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
    """Enregistre un comptage physique (Batch 18).

    Théorique = Stock.quantite_disponible (colonne réelle ; l'ancien code
    lisait stock.quantite → AttributeError 500). compteur_id (fantôme) →
    operateur (réel). Un seul comptage par stock et par inventaire : le
    second est refusé, pas fusionné en silence.
    """
    from app.models.magasin_avance import InventaireTournant, LigneInventaire
    from app.models.magasin import Stock

    inventaire = db.query(InventaireTournant).filter(InventaireTournant.id == inventaire_id).first()
    if not inventaire:
        raise HTTPException(status_code=404, detail="Inventaire non trouvé")
    if inventaire.statut not in ("planifie", "en_cours"):
        raise HTTPException(
            status_code=400,
            detail=f"Inventaire {inventaire.statut} : plus aucun comptage possible")
    stock = db.query(Stock).filter(Stock.id == ligne.stock_id).first()
    if not stock:
        raise HTTPException(status_code=404, detail="Stock non trouvé")
    quantite_comptee = float(ligne.quantite_comptee)
    if quantite_comptee < 0:
        raise HTTPException(status_code=400, detail="quantite_comptee ne peut pas être négative")
    if db.query(LigneInventaire).filter(
            LigneInventaire.inventaire_id == inventaire_id,
            LigneInventaire.stock_id == ligne.stock_id).first():
        raise HTTPException(
            status_code=400, detail="Ce stock a déjà été compté dans cet inventaire")

    theorique = float(stock.quantite_disponible or 0)
    l = LigneInventaire(
        inventaire_id=inventaire_id,
        stock_id=ligne.stock_id,
        quantite_theorique=theorique,
        quantite_comptee=quantite_comptee,
        ecart=quantite_comptee - theorique,
        statut="compte",
        operateur=ligne.operateur or current_user.id,
        date_comptage=date.today(),
        commentaires=ligne.commentaires,
    )
    db.add(l)
    db.commit()
    db.refresh(l)
    return l


@router.put("/inventaires/{inventaire_id}/valider", response_model=InventaireTournantResponse)
def valider_inventaire(
    inventaire_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Valide l'inventaire et ajuste réellement le stock (Batch 18).

    Anciens fantômes : stock.quantite (perte silencieuse — l'ajustement
    n'était jamais persisté sur la bonne colonne), validateur_id /
    date_validation (colonnes inexistantes) et statut "valide" hors du
    workflow réel planifie/en_cours/termine/annule. Ici : l'ajustement porte
    sur quantite_disponible ET chaque écart corrigé est tracé dans le registre
    MouvementStock (type inventaire) — aucune correction invisible.
    Le validateur est l'utilisateur authentifié (plus de query param
    validateur_id non vérifié).
    """
    from app.models.magasin_avance import InventaireTournant, LigneInventaire
    from app.models.magasin import Stock, MouvementStock, MouvementType

    inventaire = db.query(InventaireTournant).filter(InventaireTournant.id == inventaire_id).first()
    if not inventaire:
        raise HTTPException(status_code=404, detail="Inventaire non trouvé")
    if inventaire.statut == "termine":
        raise HTTPException(status_code=400, detail="Inventaire déjà validé (décision unique)")
    if inventaire.statut == "annule":
        raise HTTPException(status_code=400, detail="Inventaire annulé : validation impossible")
    lignes = db.query(LigneInventaire).filter(LigneInventaire.inventaire_id == inventaire_id).all()
    if not lignes:
        raise HTTPException(status_code=400, detail="Aucune ligne comptée : rien à valider")

    ajustees = 0
    for ligne in lignes:
        if ligne.quantite_comptee is None or float(ligne.ecart or 0) == 0:
            continue
        stock = db.query(Stock).filter(Stock.id == ligne.stock_id).first()
        if not stock:
            continue
        dispo_avant = float(stock.quantite_disponible or 0)
        dispo_apres = float(ligne.quantite_comptee)
        db.add(MouvementStock(
            company_id=stock.company_id,
            reference=f"{inventaire.numero_inventaire}/L{ligne.id}",
            stock_id=stock.id,
            type_mouvement=MouvementType.INVENTAIRE,
            quantite=abs(dispo_apres - dispo_avant),
            quantite_avant=dispo_avant,
            quantite_apres=dispo_apres,
            raison=f"Correction inventaire {inventaire.numero_inventaire} "
                   f"(ecart {dispo_apres - dispo_avant:+.2f})",
            document_reference=inventaire.numero_inventaire,
            operateur_id=current_user.id,
        ))
        stock.quantite_disponible = dispo_apres
        ajustees += 1

    inventaire.statut = "termine"
    inventaire.date_fin = date.today()
    trace = (f"[VALIDE {date.today().isoformat()} par utilisateur {current_user.id}] "
             f"{ajustees} ligne(s) ajustée(s)")
    inventaire.notes = f"{inventaire.notes}\n{trace}" if inventaire.notes else trace

    db.commit()
    db.refresh(inventaire)
    return inventaire


@router.get("/inventaires/{inventaire_id}/precision", response_model=PrecisionInventaireResponse)
def calculer_precision_inventaire(
    inventaire_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Taux de précision d'un inventaire (Batch 18).

    Sans ligne comptée : precision = None + message « non mesurée » — un
    inventaire jamais compté n'est pas un inventaire à 0 % (l'ancien code
    rendait un faux 0.0 mensonger).
    """
    from app.models.magasin_avance import InventaireTournant, LigneInventaire

    if not db.query(InventaireTournant).filter(InventaireTournant.id == inventaire_id).first():
        raise HTTPException(status_code=404, detail="Inventaire non trouvé")
    lignes = db.query(LigneInventaire).filter(LigneInventaire.inventaire_id == inventaire_id).all()
    if not lignes:
        return {"inventaire_id": inventaire_id, "precision": None,
                "message": "aucune ligne comptée — précision non mesurée"}
    lignes_correctes = sum(1 for l in lignes if float(l.ecart or 0) == 0)
    return {
        "inventaire_id": inventaire_id,
        "lignes_total": len(lignes),
        "lignes_correctes": lignes_correctes,
        "precision": round(lignes_correctes / len(lignes) * 100, 2),
    }


# ============ FOURNISSEURS ============
@router.post("/fournisseurs-stock", response_model=FournisseurStockResponse, status_code=status.HTTP_201_CREATED)
def creer_fournisseur_stock(
    evaluation: FournisseurStockCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Enregistre une évaluation fournisseur (Batch 18, modèle réel).

    L'ancien code construisait FournisseurStock(delai_livraison_jours=...,
    qualite=..., fiabilite=...) : aucune de ces colonnes n'existe →
    TypeError 500 garanti. note_globale : calculée sur les notes 1-10
    réellement fournies, jamais inventée.
    """
    from app.models.magasin_avance import FournisseurStock
    from app.models.tiers import Fournisseur

    if not db.query(Fournisseur).filter(Fournisseur.id == evaluation.fournisseur_id).first():
        raise HTTPException(status_code=404, detail="Fournisseur inexistant")
    for champ in ("qualite_produit", "prix_competitif", "service_client"):
        note = getattr(evaluation, champ)
        if note is not None and not (1 <= float(note) <= 10):
            raise HTTPException(status_code=400,
                                detail=f"{champ} doit être une note entre 1 et 10")
    if evaluation.taux_livraison_ponctuelle is not None and not (
            0 <= float(evaluation.taux_livraison_ponctuelle) <= 100):
        raise HTTPException(status_code=400,
                            detail="taux_livraison_ponctuelle doit être un pourcentage 0-100")
    if evaluation.delai_moyen_livraison is not None and evaluation.delai_moyen_livraison < 0:
        raise HTTPException(status_code=400,
                            detail="delai_moyen_livraison ne peut pas être négatif")

    note_globale = evaluation.note_globale
    if note_globale is None:
        notes_fournies = [float(v) for v in (evaluation.qualite_produit,
                                             evaluation.prix_competitif,
                                             evaluation.service_client) if v is not None]
        note_globale = (round(sum(notes_fournies) / len(notes_fournies), 2)
                        if notes_fournies else None)

    fs = FournisseurStock(
        fournisseur_id=evaluation.fournisseur_id,
        delai_moyen_livraison=evaluation.delai_moyen_livraison,
        taux_livraison_ponctuelle=evaluation.taux_livraison_ponctuelle,
        qualite_produit=evaluation.qualite_produit,
        prix_competitif=evaluation.prix_competitif,
        service_client=evaluation.service_client,
        note_globale=note_globale,
        date_evaluation=date.today(),
        evaluateur=current_user.id,
        commentaires=evaluation.commentaires,
        statut="actif",
    )
    db.add(fs)
    db.commit()
    db.refresh(fs)
    return fs


@router.get("/fournisseurs/{fournisseur_id}/performance",
            response_model=PerformanceFournisseurResponse)
def evaluer_performance_fournisseur(
    fournisseur_id: int,
    debut_periode: date,
    fin_periode: date,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Performance réelle d'après les commandes fournisseur (Batch 18).

    Anciens fantômes : cmd.date_livraison / cmd.date_prevue (réel :
    date_livraison_reelle / date_livraison_prevue → AttributeError 500) et
    statut "recu" (réel : "livree" → le compteur ne matchait jamais). Sans
    commande sur la période : note/taux/délai = None + message, plus le faux
    0/100 qui transformait l'absence de mesure en mauvaise note.
    """
    from app.models.magasin_avance import CommandeFournisseur
    from app.models.tiers import Fournisseur

    if debut_periode > fin_periode:
        raise HTTPException(status_code=400, detail="debut_periode postérieure à fin_periode")
    if not db.query(Fournisseur).filter(Fournisseur.id == fournisseur_id).first():
        raise HTTPException(status_code=404, detail="Fournisseur inexistant")

    commandes = db.query(CommandeFournisseur).filter(
        and_(
            CommandeFournisseur.fournisseur_id == fournisseur_id,
            CommandeFournisseur.date_commande >= debut_periode,
            CommandeFournisseur.date_commande <= fin_periode
        )
    ).all()

    if not commandes:
        return {"fournisseur_id": fournisseur_id, "commandes": 0,
                "note": None, "taux_livraison": None, "delai_moyen_jours": None,
                "message": "aucune commande sur la période — performance non évaluée"}

    total = len(commandes)
    livrees = sum(1 for c in commandes if c.statut == "livree")
    taux = round(livrees / total * 100, 2)

    delais = [(c.date_livraison_reelle - c.date_livraison_prevue).days
              for c in commandes
              if c.date_livraison_reelle and c.date_livraison_prevue]
    if delais:
        delai_moyen = round(sum(delais) / len(delais), 2)
        note = round(min(100, taux * 0.7 + max(0, 100 - abs(delai_moyen)) * 0.3), 2)
    else:
        # Retard jamais mesurable : note = taux de livraison brut, sans
        # composante délai inventée.
        delai_moyen = None
        note = taux

    return {"fournisseur_id": fournisseur_id, "commandes": total,
            "commandes_livrees": livrees, "taux_livraison": taux,
            "delai_moyen_jours": delai_moyen, "note": round(note, 2)}


# ============ RÉAPPROVISIONNEMENT ============
@router.post("/reapprovisionnement/automatique/{fournisseur_id}",
             response_model=ReapproAutomatiqueResponse)
def generer_commande_automatique(
    fournisseur_id: int,
    seuil_alerte: float = 10.0,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Génère UNE commande groupée pour les stocks sous le seuil (Batch 18).

    Anciens fantômes : CommandeFournisseur(reference=..., date_prevue=...)
    et LigneCommandeFournisseur(article_id=stock.article_id) — reference,
    date_prevue et article_id n'existent pas, et Stock n'a pas d'article_id
    (lien réel : stock_id / code_article) → TypeError avant le premier
    commit. prix_unitaire est NOT NULL sur le modèle : un stock sans prix
    sur sa fiche est IGNORE et déclaré dans « ignorees », jamais price a 0.0
    invente (Zero-Mock).
    """
    from app.models.magasin_avance import CommandeFournisseur, LigneCommandeFournisseur
    from app.models.magasin import Stock
    from app.models.tiers import Fournisseur

    if seuil_alerte <= 0:
        raise HTTPException(status_code=400, detail="seuil_alerte doit être positif")
    if not db.query(Fournisseur).filter(Fournisseur.id == fournisseur_id).first():
        raise HTTPException(status_code=404, detail="Fournisseur inexistant")

    stocks_bas = db.query(Stock).filter(Stock.quantite_disponible < seuil_alerte).all()
    a_commander = [s for s in stocks_bas if s.prix_unitaire is not None]
    ignorees = [{"stock_id": s.id, "code_article": s.code_article,
                 "raison": "prix_unitaire absent de la fiche stock — aucun prix inventé"}
                for s in stocks_bas if s.prix_unitaire is None]
    if not a_commander:
        raise HTTPException(
            status_code=400,
            detail=f"Aucun stock commandable sous le seuil {seuil_alerte} "
                   f"({len(stocks_bas)} sous le seuil, {len(ignorees)} ignorés faute de prix)")

    numero = _prochaine_rotation_numero(db, CommandeFournisseur, "numero_commande", "CMD")
    quantite = seuil_alerte * 2
    commande = CommandeFournisseur(
        numero_commande=numero,
        fournisseur_id=fournisseur_id,
        date_commande=date.today(),
        date_livraison_prevue=date.today() + timedelta(days=7),
        statut="en_cours",
        devise="XAF",
        createur=current_user.id,
        notes=f"Générée automatiquement — seuil {seuil_alerte}",
    )
    db.add(commande)
    db.flush()

    lignes_infos = []
    montant_total = 0.0
    for stock in a_commander:
        prix = float(stock.prix_unitaire)
        total_ligne = round(quantite * prix, 2)
        montant_total += total_ligne
        db.add(LigneCommandeFournisseur(
            commande_id=commande.id,
            stock_id=stock.id,
            quantite_commandee=quantite,
            prix_unitaire=prix,
            quantite_recue=0,
            prix_total=total_ligne,
            statut="en_attente",
        ))
        lignes_infos.append({"stock_id": stock.id, "code_article": stock.code_article,
                             "designation": stock.designation,
                             "quantite_commandee": quantite,
                             "prix_unitaire": prix, "prix_total": total_ligne})
    commande.montant_total = round(montant_total, 2)
    db.commit()
    return {"commande_id": commande.id, "numero_commande": numero,
            "lignes": lignes_infos, "ignorees": ignorees}


# ============ RÉCEPTIONS ============
# Batch 19 : reconstruit sur les modeles REELS BonReception /
# LigneBonReception. L'ancienne version inventait commande_id (reel :
# commande_fournisseur_id), bon_id (reel : bon_reception_id), article_id /
# emplacement_id (reels : stock_id / emplacement String), oubliait
# numero_bon (unique NOT NULL) et ecrivait stock.quantite (reel :
# quantite_disponible) → TypeError 500 garanti ou succes menteux.
# Le numero BR-YYYYMMDD-NNNN est genere cote route ; un bon recoit
# obligatoirement un fournisseur ET un entrepot reels (FK SQLite non
# verifiees → controles explicites).


@router.get("/receptions", response_model=List[BonReceptionResponse])
def lister_receptions(
    statut: Optional[str] = Query(None),
    fournisseur_id: Optional[int] = Query(None),
    entrepot_id: Optional[int] = Query(None),
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=500),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Liste des bons de reception (filtres reels, aucune donnee inventee)."""
    from app.models.magasin_avance import BonReception

    q = db.query(BonReception)
    if statut:
        q = q.filter(BonReception.statut == statut)
    if fournisseur_id:
        q = q.filter(BonReception.fournisseur_id == fournisseur_id)
    if entrepot_id:
        q = q.filter(BonReception.entrepot_id == entrepot_id)
    return q.order_by(BonReception.id.desc()).offset(skip).limit(limit).all()


@router.post("/receptions", response_model=BonReceptionResponse, status_code=status.HTTP_201_CREATED)
def creer_bon_reception(
    bon: BonReceptionCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Ouvre un bon de reception (statut initial `en_attente`).

    Fournisseur, entrepot et commande liee sont verifies existants avant
    toute ecriture ; la date est celle du jour si elle n'est pas fournie.
    """
    from app.models.magasin_avance import BonReception
    from app.models.magasin import Entrepot
    from app.models.tiers import Fournisseur

    if not db.query(Fournisseur).filter(Fournisseur.id == bon.fournisseur_id).first():
        raise HTTPException(status_code=400,
                            detail=f"Fournisseur {bon.fournisseur_id} inexistant")
    if not db.query(Entrepot).filter(Entrepot.id == bon.entrepot_id).first():
        raise HTTPException(status_code=400,
                            detail=f"Entrepot {bon.entrepot_id} inexistant")
    if bon.commande_fournisseur_id is not None:
        from app.models.magasin_avance import CommandeFournisseur
        if not db.query(CommandeFournisseur).filter(
                CommandeFournisseur.id == bon.commande_fournisseur_id).first():
            raise HTTPException(
                status_code=400,
                detail=f"Commande {bon.commande_fournisseur_id} inexistante")

    b = BonReception(
        numero_bon=_prochaine_rotation_numero(db, BonReception, "numero_bon", "BR"),
        commande_fournisseur_id=bon.commande_fournisseur_id,
        fournisseur_id=bon.fournisseur_id,
        entrepot_id=bon.entrepot_id,
        date_reception=bon.date_reception or date.today(),
        statut="en_attente",
        operateur=current_user.id,
        notes=bon.notes,
    )
    db.add(b)
    db.commit()
    db.refresh(b)
    return b


@router.patch("/receptions/{bon_id}", response_model=BonReceptionResponse)
def modifier_bon_reception(
    bon_id: int,
    data: BonReceptionUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Corrige un bon EN ATTENTE uniquement. Un bon valide ou refuse est
    immuable (decision unique) — passage par /valider ou /refuser."""
    from app.models.magasin_avance import BonReception
    from app.models.magasin import Entrepot
    from app.models.tiers import Fournisseur

    b = db.query(BonReception).filter(BonReception.id == bon_id).first()
    if not b:
        raise HTTPException(status_code=404, detail="Bon de réception non trouvé")
    if b.statut != "en_attente":
        raise HTTPException(
            status_code=400,
            detail=f"Bon {b.statut} : immuable, decision deja prise")

    if data.fournisseur_id is not None:
        if not db.query(Fournisseur).filter(Fournisseur.id == data.fournisseur_id).first():
            raise HTTPException(status_code=400,
                                detail=f"Fournisseur {data.fournisseur_id} inexistant")
        b.fournisseur_id = data.fournisseur_id
    if data.entrepot_id is not None:
        if not db.query(Entrepot).filter(Entrepot.id == data.entrepot_id).first():
            raise HTTPException(status_code=400,
                                detail=f"Entrepot {data.entrepot_id} inexistant")
        b.entrepot_id = data.entrepot_id
    if data.date_reception is not None:
        b.date_reception = data.date_reception
    if data.notes is not None:
        b.notes = data.notes

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
    """Ajoute un article recu a un bon en attente (colonnes reelles).

    stock_id (Fantome : article_id) ; emplacement est une chaine (Fantome :
    emplacement_id). Un bon deja valide ou refuse n'accepte plus de ligne.
    Le statut de conformite est CALCULE (conforme si quantite commandee
    fournie et egale, sinon ecart) — jamais laisse a une saisie libre.
    """
    from app.models.magasin_avance import BonReception, LigneBonReception
    from app.models.magasin import Stock

    b = db.query(BonReception).filter(BonReception.id == bon_id).first()
    if not b:
        raise HTTPException(status_code=404, detail="Bon de réception non trouvé")
    if b.statut != "en_attente":
        raise HTTPException(
            status_code=400,
            detail=f"Bon {b.statut} : plus aucune ligne possible")
    stock = db.query(Stock).filter(Stock.id == ligne.stock_id).first()
    if not stock:
        raise HTTPException(status_code=404, detail="Stock non trouvé")
    quantite_recue = float(ligne.quantite_recue)
    if quantite_recue <= 0:
        raise HTTPException(status_code=400,
                            detail="quantite_recue doit etre positive")
    if ligne.quantite_commandee is not None and float(ligne.quantite_commandee) < 0:
        raise HTTPException(status_code=400,
                            detail="quantite_commandee ne peut pas etre negative")
    if db.query(LigneBonReception).filter(
            LigneBonReception.bon_reception_id == bon_id,
            LigneBonReception.stock_id == ligne.stock_id).first():
        raise HTTPException(
            status_code=400,
            detail="Ce stock figure deja sur ce bon : corrigez la ligne existante")

    statut_ligne = "conforme"
    if (ligne.quantite_commandee is not None
            and quantite_recue != float(ligne.quantite_commandee)):
        statut_ligne = "ecart"

    l = LigneBonReception(
        bon_reception_id=bon_id,
        stock_id=ligne.stock_id,
        quantite_recue=quantite_recue,
        quantite_commandee=ligne.quantite_commandee,
        prix_unitaire=ligne.prix_unitaire,
        emplacement=ligne.emplacement,
        numero_lot=ligne.numero_lot,
        date_peremption=ligne.date_peremption,
        statut=statut_ligne,
        commentaires=ligne.commentaires,
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
    """Valide la reception : stock reellement augmente ET journalise.

    Ancienne version : lisait LigneBonReception.bon_id et Stock.article_id
    (AttributError), ecrivait stock.quantite (colonne fantome → perte
    silencieuse de tout l'apport), inventait un Stock(...article_id=...)
    et signait date_validation=utcnow() sur une colonne Date. Ici :
    augmentation de quantite_disponible sur les lignes reellement comptees,
    un mouvement MouvementStock (type entree) par ligne — aucun apport
    invisible — decision unique, validateur = utilisateur authentifie.
    """
    from app.models.magasin_avance import (
        BonReception, LigneBonReception, CommandeFournisseur,
        LigneCommandeFournisseur)
    from app.models.magasin import Stock, MouvementStock, MouvementType

    b = db.query(BonReception).filter(BonReception.id == bon_id).first()
    if not b:
        raise HTTPException(status_code=404, detail="Bon de réception non trouvé")
    if b.statut == "valide":
        raise HTTPException(status_code=400,
                            detail="Bon deja valide : decision unique")
    if b.statut == "refuse":
        raise HTTPException(status_code=400,
                            detail="Bon refuse : reouverture impossible")
    lignes = db.query(LigneBonReception).filter(
        LigneBonReception.bon_reception_id == bon_id).all()
    if not lignes:
        raise HTTPException(status_code=400,
                            detail="Aucune ligne recue : rien a valider")

    for ligne in lignes:
        stock = db.query(Stock).filter(Stock.id == ligne.stock_id).first()
        if not stock:
            raise HTTPException(
                status_code=400,
                detail=f"Ligne {ligne.id} : stock {ligne.stock_id} introuvable")
        avant = float(stock.quantite_disponible or 0)
        delta = float(ligne.quantite_recue)
        db.add(MouvementStock(
            company_id=stock.company_id,
            reference=f"{b.numero_bon}/L{ligne.id}",
            stock_id=stock.id,
            type_mouvement=MouvementType.ENTREE,
            quantite=delta,
            quantite_avant=avant,
            quantite_apres=avant + delta,
            prix_unitaire=ligne.prix_unitaire,
            raison=f"Reception {b.numero_bon}",
            document_reference=b.numero_bon,
            operateur_id=current_user.id,
        ))
        stock.quantite_disponible = avant + delta
        # Le registre des lignes de commande porte quantite_recue : on le
        # met a jour quand le bon est rattache a une commande (sinon la
        # commande resterait eternellement « en cours »).
        if b.commande_fournisseur_id is not None:
            lc = db.query(LigneCommandeFournisseur).filter(
                LigneCommandeFournisseur.commande_id == b.commande_fournisseur_id,
                LigneCommandeFournisseur.stock_id == ligne.stock_id).first()
            if lc:
                lc.quantite_recue = float(lc.quantite_recue or 0) + delta
                lc.date_reception = date.today()
                if lc.quantite_recue >= float(lc.quantite_commandee or 0):
                    lc.statut = "recu"

    b.statut = "valide"
    b.validateur = current_user.id
    b.date_validation = date.today()
    trace = (f"[VALIDE {date.today().isoformat()} par utilisateur "
             f"{current_user.id}] {len(lignes)} ligne(s) en stock")
    b.notes = f"{b.notes}\n{trace}" if b.notes else trace

    if b.commande_fournisseur_id is not None:
        cmd = db.query(CommandeFournisseur).filter(
            CommandeFournisseur.id == b.commande_fournisseur_id).first()
        if cmd:
            toutes_reçues = db.query(LigneCommandeFournisseur).filter(
                LigneCommandeFournisseur.commande_id == cmd.id,
                LigneCommandeFournisseur.statut != "recu").count() == 0
            if toutes_reçues:
                cmd.statut = "livree"
                cmd.date_livraison_reelle = date.today()

    db.commit()
    db.refresh(b)
    return b


@router.put("/receptions/{bon_id}/refuser", response_model=BonReceptionResponse)
def refuser_reception(
    bon_id: int,
    data: RefusBonReception,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Refuse une reception avec motif ecrit OBLIGATOIRE ( Batch 16 :
    une decision opposable sans motif trace n'existe pas). Aucun stock ne
    bouge : la marchandise refusee n'est pas entree."""
    from app.models.magasin_avance import BonReception

    b = db.query(BonReception).filter(BonReception.id == bon_id).first()
    if not b:
        raise HTTPException(status_code=404, detail="Bon de réception non trouvé")
    if b.statut != "en_attente":
        raise HTTPException(status_code=400,
                            detail=f"Bon {b.statut} : decision deja prise")
    motif = (data.motif or "").strip()
    if not motif:
        raise HTTPException(status_code=400,
                            detail="Un refus exige un motif ecrit non vide")

    b.statut = "refuse"
    b.validateur = current_user.id
    b.date_validation = date.today()
    trace = (f"[REFUSE {date.today().isoformat()} par utilisateur "
             f"{current_user.id}] {motif}")
    b.notes = f"{b.notes}\n{trace}" if b.notes else trace

    db.commit()
    db.refresh(b)
    return b


# ============ SORTIES ============
# SUPPRIMÉ (Batch 16) : l'ancien trio POST /sorties, POST /sorties/{id}/lignes,
# PUT /sorties/{id}/valider était du code mort — il construisait
# BonSortie(destinataire_id=...), LigneBonSortie(bon_id=..., quantite=...) et
# lisait stock.quantite, champs qui n'existent pas sur les modèles
# (TypeError systématique → 500). Le vrai circuit de bon de sortie (numérotation,
# stock tout-ou-rien, registre MouvementStock, refus motivé, PDF signé) vit dans
# app/routers/v1/removal_slip.py, monté sous /api/v1/magasin/removal-slips
# et connecté au frontend (portail magasinier).


# ============ RETOURS CLIENTS ============
# Batch 17 : reconstruit sur le modele REEL RetourClient. L'ancienne version
# inventait article_id/etat a la creation (TypeError 500 systematique) et
# ecrivait action_effectuee/date_traitement — colonnes inexistantes, donc
# perte silencieuse. Attention : le modele ne porte PAS de stock_id — la
# reintegration physique en stock n'est pas modelisee ; aucun mouvement de
# stock n'est ici INVENTE (Zero-Mock).


def _prochaine_rotation_numero(db, modele, champ, prefix):
    """Numerotation ROTATEUR-safe : seq du jour + boucle anti-collision."""
    today_str = datetime.now().strftime("%Y%m%d")
    seq = (db.query(func.count(modele.id))
             .filter(getattr(modele, champ).like(f"{prefix}-{today_str}-%"))
             .scalar() or 0) + 1
    numero = f"{prefix}-{today_str}-{seq:04d}"
    while db.query(getattr(modele, modele.id.name)).filter(
            getattr(modele, champ) == numero).first() is not None:
        seq += 1
        numero = f"{prefix}-{today_str}-{seq:04d}"
    return numero


@router.get("/retours", response_model=List[RetourClientResponse])
def lister_retours(
    statut: Optional[str] = Query(None),
    client_id: Optional[int] = Query(None),
    skip: int = Query(0),
    limit: int = Query(50),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Liste des retours clients (filtres statut/client, pagination)."""
    from app.models.magasin_avance import RetourClient
    q = db.query(RetourClient)
    if statut:
        q = q.filter(RetourClient.statut == statut)
    if client_id:
        q = q.filter(RetourClient.client_id == client_id)
    return q.order_by(RetourClient.id.desc()).offset(skip).limit(min(limit, 200)).all()


@router.post("/retours", response_model=RetourClientResponse, status_code=status.HTTP_201_CREATED)
def enregistrer_retour(
    retour: RetourClientCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Enregistre un retour client (statut initial `en_attente`).

    Validations reelles : client existant, bon de sortie existant si lie,
    motif non vide, quantite > 0 si precisee, type dans la liste metier.
    """
    from app.models.magasin_avance import RetourClient, BonSortie
    from app.models.tiers import Client

    TYPES_RETOUR = ("defectif", "mauvais_quantite", "refus", "erreur_livraison")

    if not db.query(Client).filter(Client.id == retour.client_id).first():
        raise HTTPException(status_code=400,
                            detail=f"Client {retour.client_id} inexistant")
    if retour.bon_sortie_id is not None:
        if not db.query(BonSortie).filter(BonSortie.id == retour.bon_sortie_id).first():
            raise HTTPException(
                status_code=400,
                detail=f"Bon de sortie {retour.bon_sortie_id} inexistant")
    motif = (retour.motif or "").strip()
    if not motif:
        raise HTTPException(status_code=400, detail="Un retour exige un motif non vide")
    if retour.quantite is not None and float(retour.quantite) <= 0:
        raise HTTPException(status_code=400,
                            detail=f"Quantite invalide ({retour.quantite})")
    if retour.type_retour and retour.type_retour not in TYPES_RETOUR:
        raise HTTPException(status_code=400,
                            detail=f"type_retour doit etre l'un de {list(TYPES_RETOUR)}")

    r = RetourClient(
        numero_retour=_prochaine_rotation_numero(db, RetourClient, "numero_retour", "RT"),
        client_id=retour.client_id,
        bon_sortie_id=retour.bon_sortie_id,
        date_retour=date.today(),
        type_retour=retour.type_retour,
        motif=motif,
        quantite=retour.quantite,
        statut="en_attente",
        notes=retour.notes,
        operateur=current_user.id,
    )
    db.add(r)
    db.commit()
    db.refresh(r)
    return r


@router.patch("/retours/{retour_id}", response_model=RetourClientResponse)
def modifier_retour(
    retour_id: int,
    retour: RetourClientUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Corrige un retour NON ENCORE TRAITE. Un retour accepte/refuse est
    une decision signee : document immuable (circulaire du batch 16)."""
    from app.models.magasin_avance import RetourClient
    r = db.query(RetourClient).filter(RetourClient.id == retour_id).first()
    if not r:
        raise HTTPException(status_code=404, detail="Retour non trouvé")
    if r.statut != "en_attente":
        raise HTTPException(
            status_code=400,
            detail=f"Retour {r.numero_retour} deja traite ({r.statut}) : document immuable.")
    data = retour.dict(exclude_unset=True)
    if "motif" in data and not (data["motif"] or "").strip():
        raise HTTPException(status_code=400, detail="Un retour exige un motif non vide")
    for field, value in data.items():
        setattr(r, field, value)
    db.commit()
    db.refresh(r)
    return r


@router.put("/retours/{retour_id}/traiter", response_model=RetourClientResponse)
def traiter_retour(
    retour_id: int,
    payload: RetourClientTraitement,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Prend la decision finale sur un retour : `accepte` (avec action parmi
    remplacement/remboursement/destruction) ou `refuse`.

    La date de traitement est TRACEE dans notes (le modele n'a pas de colonne
    date_traitement) — rien n'est ecrit dans des colonnes inventees. Aucun
    mouvement de stock : la reintegration physique n'est pas modelisee sur
    RetourClient (pas de stock_id) et ne sera pas inventee.
    """
    from app.models.magasin_avance import RetourClient
    ACTIONS = ("remplacement", "remboursement", "destruction")

    r = db.query(RetourClient).filter(RetourClient.id == retour_id).first()
    if not r:
        raise HTTPException(status_code=404, detail="Retour non trouvé")
    if r.statut != "en_attente":
        raise HTTPException(
            status_code=400,
            detail=f"Retour {r.numero_retour} deja traite ({r.statut}) : decision unique.")

    decision = (payload.decision or "").strip()
    if decision not in ("accepte", "refuse"):
        raise HTTPException(status_code=400,
                            detail="decision doit etre 'accepte' ou 'refuse'")
    if decision == "accepte":
        if payload.action not in ACTIONS:
            raise HTTPException(
                status_code=400,
                detail=f"Un retour accepte exige une action parmi {list(ACTIONS)}")
    elif payload.action:
        raise HTTPException(status_code=400,
                            detail="Un retour refuse ne porte pas d'action")
    if payload.cout_traitement is not None and float(payload.cout_traitement) < 0:
        raise HTTPException(status_code=400, detail="cout_traitement ne peut pas etre negatif")

    r.statut = decision
    r.action = payload.action if decision == "accepte" else None
    r.cout_traitement = payload.cout_traitement
    trace = (f"[TRAITE {date.today().isoformat()} par utilisateur {current_user.id}] "
             f"{decision}" + (f" ({r.action})" if r.action else ""))
    if payload.notes:
        trace += f" — {payload.notes}"
    r.notes = f"{r.notes + chr(10) if r.notes else ''}{trace}"
    db.commit()
    db.refresh(r)
    return r


# ============ LITIGES TRANSPORTEURS ============
# Batch 17 : reconstruit sur le modele reel LitigeTransporteur (l'ancien
# creer_litige passait date_litige=, colonne inexistante → TypeError 500).


@router.get("/litiges", response_model=List[LitigeTransporteurResponse])
def lister_litiges(
    statut: Optional[str] = Query(None),
    transporteur_id: Optional[int] = Query(None),
    skip: int = Query(0),
    limit: int = Query(50),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Liste des litiges transporteur (filtres statut/transporteur)."""
    from app.models.magasin_avance import LitigeTransporteur
    q = db.query(LitigeTransporteur)
    if statut:
        q = q.filter(LitigeTransporteur.statut == statut)
    if transporteur_id:
        q = q.filter(LitigeTransporteur.transporteur_id == transporteur_id)
    return q.order_by(LitigeTransporteur.id.desc()).offset(skip).limit(min(limit, 200)).all()


@router.post("/litiges", response_model=LitigeTransporteurResponse, status_code=status.HTTP_201_CREATED)
def creer_litige(
    litige: LitigeTransporteurCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Ouvre un litige transporteur (statut initial `en_cours`).

    Transporteur = fournisseur existant (FK fournisseurs.id) ; description
    obligatoire ; montant >= 0 ; type dans la liste metier.
    """
    from app.models.magasin_avance import LitigeTransporteur
    from app.models.tiers import Fournisseur

    TYPES_LITIGE = ("retard", "avarie", "perte", "erreur_livraison")

    if not db.query(Fournisseur).filter(Fournisseur.id == litige.transporteur_id).first():
        raise HTTPException(
            status_code=400,
            detail=f"Transporteur/fournisseur {litige.transporteur_id} inexistant")
    description = (litige.description or "").strip()
    if not description:
        raise HTTPException(status_code=400, detail="Un litige exige une description non vide")
    if litige.type_litige not in TYPES_LITIGE:
        raise HTTPException(status_code=400,
                            detail=f"type_litige doit etre l'un de {list(TYPES_LITIGE)}")
    if litige.montant_reclame is not None and float(litige.montant_reclame) < 0:
        raise HTTPException(status_code=400, detail="montant_reclame ne peut pas etre negatif")

    l = LitigeTransporteur(
        numero_litige=_prochaine_rotation_numero(db, LitigeTransporteur, "numero_litige", "LI"),
        transporteur_id=litige.transporteur_id,
        mission_id=litige.mission_id,
        date_incident=date.today(),
        type_litige=litige.type_litige,
        description=description,
        montant_reclame=litige.montant_reclame,
        statut="en_cours",
        assureur=litige.assureur,
        numero_police=litige.numero_police,
    )
    db.add(l)
    db.commit()
    db.refresh(l)
    return l


@router.patch("/litiges/{litige_id}", response_model=LitigeTransporteurResponse)
def modifier_litige(
    litige_id: int,
    litige: LitigeTransporteurUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Corrige un litige EN COURS seulement (cloture = decision immuable)."""
    from app.models.magasin_avance import LitigeTransporteur
    l = db.query(LitigeTransporteur).filter(LitigeTransporteur.id == litige_id).first()
    if not l:
        raise HTTPException(status_code=404, detail="Litige non trouvé")
    if l.statut != "en_cours":
        raise HTTPException(
            status_code=400,
            detail=f"Litige {l.numero_litige} deja cloture ({l.statut}) : document immuable.")
    data = litige.dict(exclude_unset=True)
    if "description" in data and not (data["description"] or "").strip():
        raise HTTPException(status_code=400, detail="Un litige exige une description non vide")
    for field, value in data.items():
        setattr(l, field, value)
    db.commit()
    db.refresh(l)
    return l


@router.put("/litiges/{litige_id}/resoudre", response_model=LitigeTransporteurResponse)
def resoudre_litige(
    litige_id: int,
    payload: LitigeTransporteurResolution,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Clot un litige : `resolu`, `refuse` ou transmis en `justice`.

    La resolution ecrite est obligatoire et datee (date_resolution, colonne
    reelle). `montant_indemnise` (optionnel, cloture `resolu` uniquement)
    majore la trace de l'accord en remplacant montant_reclame par le montant
    convenu — le modele n'a pas de colonne d'indemnite separee, c'est le seul
    rendu honest possible sans migration.
    """
    from app.models.magasin_avance import LitigeTransporteur
    l = db.query(LitigeTransporteur).filter(LitigeTransporteur.id == litige_id).first()
    if not l:
        raise HTTPException(status_code=404, detail="Litige non trouvé")
    if l.statut != "en_cours":
        raise HTTPException(
            status_code=400,
            detail=f"Litige {l.numero_litige} deja cloture ({l.statut}).")

    nouveau_statut = (payload.statut or "").strip()
    if nouveau_statut not in ("resolu", "refuse", "justice"):
        raise HTTPException(
            status_code=400,
            detail="statut de cloture doit etre 'resolu', 'refuse' ou 'justice'")
    resolution = (payload.resolution or "").strip()
    if not resolution:
        raise HTTPException(status_code=400,
                            detail="Une cloture exige une resolution ecrite non vide")
    if payload.montant_indemnise is not None:
        if nouveau_statut != "resolu":
            raise HTTPException(
                status_code=400,
                detail="montant_indemnise reserve aux litiges resolus")
        if float(payload.montant_indemnise) < 0:
            raise HTTPException(status_code=400,
                                detail="montant_indemnise ne peut pas etre negatif")
        l.montant_reclame = payload.montant_indemnise

    l.statut = nouveau_statut
    l.resolution = resolution
    l.date_resolution = date.today()
    db.commit()
    db.refresh(l)
    return l


# ============ COLIS ============
# Batch 19 : reconstruit sur le modele REEL Colis (numero_colis, type_colis,
# poids, dimensions, volume, contenu, fragile, empilable, emplacement,
# date_etiquetage Date, operateur). L'ancien ColisService inventait
# reference_colis / date_creation (TypeError a la creation), code_barres et
# palette_id/date_palettisation (ecriture silencieuse sur objets Python sans
# colonne → perte pure et simple). La palette n'ayant AUCUNE colonne, la
# palettisation est tracee dans `emplacement` (seule localisation reelle) et
# l'etiquetage date reellement (date_etiquetage) — rien de plus.


@router.get("/colis", response_model=List[ColisResponse])
def lister_colis(
    bon_sortie_id: Optional[int] = Query(None),
    type_colis: Optional[str] = Query(None),
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=500),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Liste des colis (filtres sur colonnes reelles)."""
    from app.models.magasin_avance import Colis

    q = db.query(Colis)
    if bon_sortie_id:
        q = q.filter(Colis.bon_sortie_id == bon_sortie_id)
    if type_colis:
        q = q.filter(Colis.type_colis == type_colis)
    return q.order_by(Colis.id.desc()).offset(skip).limit(limit).all()


@router.post("/colis", response_model=ColisResponse, status_code=status.HTTP_201_CREATED)
def creer_colis(
    colis: ColisCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Enregistre un colis (numero CO-YYYYMMDD-NNNN genere ici).

    Poids/volume non negatifs, type dans la liste metier si fourni,
    bon_sortie lie verifie existant (FK SQLite non contrôlée).
    """
    from app.models.magasin_avance import Colis, BonSortie

    TYPES_COLIS = ("carton", "palette", "caisse", "sac")
    if colis.type_colis is not None and colis.type_colis not in TYPES_COLIS:
        raise HTTPException(status_code=400,
                            detail=f"type_colis doit etre l'un de {list(TYPES_COLIS)}")
    if colis.poids is not None and float(colis.poids) < 0:
        raise HTTPException(status_code=400, detail="poids ne peut pas etre negatif")
    if colis.volume is not None and float(colis.volume) < 0:
        raise HTTPException(status_code=400, detail="volume ne peut pas etre negatif")
    if colis.bon_sortie_id is not None:
        if not db.query(BonSortie).filter(BonSortie.id == colis.bon_sortie_id).first():
            raise HTTPException(
                status_code=400,
                detail=f"Bon de sortie {colis.bon_sortie_id} inexistant")

    c = Colis(
        numero_colis=_prochaine_rotation_numero(db, Colis, "numero_colis", "CO"),
        bon_sortie_id=colis.bon_sortie_id,
        type_colis=colis.type_colis,
        poids=colis.poids,
        dimensions=colis.dimensions,
        volume=colis.volume,
        contenu=colis.contenu,
        fragile=colis.fragile,
        empilable=colis.empilable,
        operateur=current_user.id,
    )
    db.add(c)
    db.commit()
    db.refresh(c)
    return c


@router.patch("/colis/{colis_id}", response_model=ColisResponse)
def modifier_colis(
    colis_id: int,
    data: ColisUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Met a jour les caracteres physiques d'un colis (numero immuable)."""
    from app.models.magasin_avance import Colis

    TYPES_COLIS = ("carton", "palette", "caisse", "sac")
    c = db.query(Colis).filter(Colis.id == colis_id).first()
    if not c:
        raise HTTPException(status_code=404, detail="Colis non trouvé")
    if data.type_colis is not None:
        if data.type_colis not in TYPES_COLIS:
            raise HTTPException(status_code=400,
                                detail=f"type_colis doit etre l'un de {list(TYPES_COLIS)}")
        c.type_colis = data.type_colis
    if data.poids is not None:
        if float(data.poids) < 0:
            raise HTTPException(status_code=400,
                                detail="poids ne peut pas etre negatif")
        c.poids = data.poids
    if data.volume is not None:
        if float(data.volume) < 0:
            raise HTTPException(status_code=400,
                                detail="volume ne peut pas etre negatif")
        c.volume = data.volume
    for champ in ("dimensions", "contenu", "fragile", "empilable", "emplacement"):
        valeur = getattr(data, champ)
        if valeur is not None:
            setattr(c, champ, valeur)

    db.commit()
    db.refresh(c)
    return c


@router.put("/colis/{colis_id}/etiqueter", response_model=ColisResponse)
def etiqueter_colis(
    colis_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Étiquette un colis : date_etiquetage (colonne Date reelle) = aujourdhui.

    L'ancien service ecrivait code_barres — colonne inexistante → perte
    silencieuse. Un colis deja etiquete ne repond pas deux fois : et
    operateur traces a la premiere etiquette.
    """
    from app.models.magasin_avance import Colis

    c = db.query(Colis).filter(Colis.id == colis_id).first()
    if not c:
        raise HTTPException(status_code=404, detail="Colis non trouvé")
    if c.date_etiquetage is not None:
        raise HTTPException(
            status_code=400,
            detail=f"Colis deja etiquete le {c.date_etiquetage.isoformat()}")

    c.date_etiquetage = date.today()
    c.operateur = current_user.id
    db.commit()
    db.refresh(c)
    return c


@router.put("/colis/{colis_id}/palettiser", response_model=ColisResponse)
def palettiser_colis(
    colis_id: int,
    palette: str = Query(..., min_length=1,
                         description="Reference palette (ex: PAL-2026-014)"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Affecte le colis a une palette, tracee dans `emplacement`.

    Pas de colonne palette_id/date_palettisation dans le modele : au lieu
    d'inventer une donnee perduee en silence, la reference palette est
    ecrite dans l'unique colonne de localisation reelle du modele.
    """
    from app.models.magasin_avance import Colis

    c = db.query(Colis).filter(Colis.id == colis_id).first()
    if not c:
        raise HTTPException(status_code=404, detail="Colis non trouvé")
    ref = (palette or "").strip()
    if not ref:
        raise HTTPException(status_code=400,
                            detail="Reference palette non vide obligatoire")

    c.emplacement = f"palette:{ref}"
    db.commit()
    db.refresh(c)
    return c


# ============ KPIs ============
@router.get("/kpi/rotation/{article_id}", response_model=RotationStockResponse)
def calculer_rotation_stock(
    article_id: int,
    jours: int = 90,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Taux de rotation annualise d'une fiche article.

    Batch 17 : reecrit sur les COLONNES REELLES. L'ancien code filtrait sur
    MouvementStock.article_id, Stock.quantite et Stock.article_id — trois
    colonnes qui n'existent pas (AttributeError 500 systematique). Les
    sorties sont desormais comptees dans le registre MouvementStock (via
    stock_id), le stock actuel sur Stock.quantite_disponible, et le resultat
    expose ses composantes (sorties, stock_actuel) au lieu d'un nombre nu.
    """
    from app.models.magasin import Stock, MouvementStock, MouvementType, Article

    article = db.query(Article).filter(Article.id == article_id).first()
    if not article:
        raise HTTPException(status_code=404, detail=f"Article {article_id} inexistant")
    if jours <= 0:
        raise HTTPException(status_code=400, detail="jours doit etre positif")

    stock_ids = [row[0] for row in
                 db.query(Stock.id).filter(Stock.code_article == article.code).all()]
    if not stock_ids:
        return {"article_id": article_id, "jours": jours,
                "sorties": 0.0, "stock_actuel": 0.0, "rotation": None}

    date_debut = datetime.utcnow() - timedelta(days=jours)
    sorties = db.query(func.coalesce(func.sum(MouvementStock.quantite), 0)).filter(
        and_(
            MouvementStock.stock_id.in_(stock_ids),
            MouvementStock.type_mouvement == MouvementType.SORTIE,
            MouvementStock.date_mouvement >= date_debut,
        )
    ).scalar() or 0

    stock_actuel = db.query(func.coalesce(func.sum(Stock.quantite_disponible), 0)).filter(
        Stock.id.in_(stock_ids)
    ).scalar() or 0

    sorties = float(sorties)
    stock_actuel = float(stock_actuel)
    # Rotation indefinie si le stock est a zero : None, pas un 0.0 mensonger.
    rotation = None if stock_actuel <= 0 else round(sorties / stock_actuel * (365 / jours), 2)
    return {"article_id": article_id, "jours": jours,
            "sorties": sorties, "stock_actuel": stock_actuel, "rotation": rotation}


@router.get("/kpi/precision/{entrepot_id}")
def calculer_precision_stock(
    entrepot_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Exactitude du dernier inventaire TOURNE (statut `termine`) d'un entrepot.

    Batch 17 : l'ancien code triait sur `date_inventaire` (colonne inexistante
    → AttributeError 500) et cherchait le statut `valide` qui n'existe pas
    dans ce workflow (planifie/en_cours/termine/annule) — il n'aurait donc
    jamais rien trouve. Sans inventaire termine, reponse explicite : la
    precision est `None` (« non mesuree »), pas un 0.0 invente.
    """
    from app.models.magasin_avance import InventaireTournant, LigneInventaire

    dernier = db.query(InventaireTournant).filter(
        and_(
            InventaireTournant.entrepot_id == entrepot_id,
            InventaireTournant.statut == "termine"
        )
    ).order_by(InventaireTournant.date_debut.desc()).first()

    if not dernier:
        return {"entrepot_id": entrepot_id, "inventaire_id": None, "precision": None,
                "message": "Aucun inventaire termine pour cet entrepot : precision non mesuree"}

    lignes = db.query(LigneInventaire).filter(
        LigneInventaire.inventaire_id == dernier.id
    ).all()

    if not lignes:
        return {"entrepot_id": entrepot_id, "inventaire_id": dernier.id,
                "precision": None,
                "message": "Inventaire termine sans ligne comptee : precision non mesuree"}

    lignes_correctes = sum(1 for l in lignes if float(l.ecart or 0) == 0)
    precision = (lignes_correctes / len(lignes)) * 100

    return {"entrepot_id": entrepot_id, "inventaire_id": dernier.id,
            "lignes_total": len(lignes), "lignes_correctes": lignes_correctes,
            "precision": round(precision, 2)}
