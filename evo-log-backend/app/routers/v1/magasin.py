"""
Magasin router - manages warehouse and inventory
"""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from datetime import datetime

from app.core.database import get_db
from app.schemas.magasin import StockCreate, StockUpdate, StockResponse, MouvementStockCreate, MouvementStockResponse, EntrepotCreate, EntrepotResponse
from app.models.magasin import Stock, MouvementStock, Entrepot

router = APIRouter()


@router.get("/kpis")
async def get_magasin_kpis(db: Session = Depends(get_db)):
    """KPIs magasin agreges depuis la base (filtr tenant via filtre ORM global).

    Valeur stock = somme(quantite_disponible * prix_unitaire). Sans donnees,
    renvoie 0 reel : aucune valeur inventee.
    """
    from sqlalchemy import func

    nb_articles = db.query(func.count(Stock.id)).scalar() or 0
    valeur_stock = float(
        db.query(
            func.sum(Stock.quantite_disponible * Stock.prix_unitaire)
        ).scalar()
        or 0.0
    )
    # Articles sous leur seuil minimum (alerte reappro)
    nb_alertes_min = (
        db.query(func.count(Stock.id))
        .filter(
            Stock.quantite_minimum != None,  # noqa: E711
            Stock.quantite_disponible <= Stock.quantite_minimum,
        )
        .scalar()
        or 0
    )
    nb_entrepots = db.query(func.count(Entrepot.id)).scalar() or 0
    mouvements_jour = (
        db.query(func.count(MouvementStock.id))
        .filter(func.date(MouvementStock.date_mouvement) == datetime.utcnow().date())
        .scalar()
        or 0
    )

    return {
        "nb_articles": nb_articles,
        "valeur_stock": round(valeur_stock, 2),
        "nb_alertes_min": nb_alertes_min,
        "nb_entrepots": nb_entrepots,
        "mouvements_jour": mouvements_jour,
        "source": "stocks/mouvements_stocks",
    }


@router.get("/entrepots/occupation")
async def get_entrepots_occupation(db: Session = Depends(get_db)):
    """Taux d'occupation par entrepot, calcule sur les stockages reels.

    Occupation = surface/utilisation inconnue en base -> on retourne a la place
    le nombre d'articles et la valeur stockee par entrepot (donnees reelles),
    et occupancy=None si aucune capacite n'est enregistree.
    """
    from sqlalchemy import func

    entrepots = db.query(Entrepot).limit(50).all()
    resultats = []
    for ent in entrepots:
        nb = (
            db.query(func.count(Stock.id))
            .filter(Stock.entrepot_id == ent.id)
            .scalar()
            or 0
        )
        valeur = float(
            db.query(func.sum(Stock.quantite_disponible * Stock.prix_unitaire))
            .filter(Stock.entrepot_id == ent.id)
            .scalar()
            or 0.0
        )
        capacite = getattr(ent, "capacite", None)
        occupation = None
        if capacite:
            occupation = round(min(100.0, (valeur / float(capacite)) * 100), 1)
        resultats.append({
            "entrepot_id": ent.id,
            "zone": f"{ent.code} ({ent.nom})",
            "nb_articles": nb,
            "valeur_stockee": round(valeur, 2),
            "occupancy": occupation,
        })
    return {"source": "entrepots/stocks", "zones": resultats}



@router.get("/stocks", response_model=List[StockResponse])
async def get_all_stocks(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    """Get all stock items"""
    stocks = db.query(Stock).offset(skip).limit(limit).all()
    return stocks


@router.post("/stocks", response_model=StockResponse, status_code=status.HTTP_201_CREATED)
async def create_stock(stock_data: StockCreate, db: Session = Depends(get_db)):
    """Create a new stock item"""
    if db.query(Stock).filter(Stock.code_article == stock_data.code_article).first():
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Article code already exists")
    
    db_stock = Stock(**stock_data.model_dump())
    db.add(db_stock)
    db.commit()
    db.refresh(db_stock)
    return db_stock


@router.post("/mouvements", response_model=MouvementStockResponse, status_code=status.HTTP_201_CREATED)
async def create_mouvement_stock(mouvement_data: MouvementStockCreate, db: Session = Depends(get_db)):
    """Create a stock movement"""
    import random
    import string
    
    reference = f"MOV-{datetime.now().strftime('%Y%m%d')}-{''.join(random.choices(string.ascii_uppercase + string.digits, k=6))}"
    
    db_mouvement = MouvementStock(reference=reference, **mouvement_data.model_dump())
    db.add(db_mouvement)
    db.commit()
    db.refresh(db_mouvement)
    return db_mouvement


@router.get("", response_model=List[StockResponse])
@router.get("/", response_model=List[StockResponse])
async def list_stocks_root(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    """List all stock items from root endpoint"""
    return db.query(Stock).offset(skip).limit(limit).all()


@router.get("/entrepots", response_model=List[EntrepotResponse])
async def get_all_entrepots(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    """Get all warehouses"""
    entrepots = db.query(Entrepot).offset(skip).limit(limit).all()
    return entrepots


@router.post("/entrepots", response_model=EntrepotResponse, status_code=status.HTTP_201_CREATED)
async def create_entrepot(entrepot_data: EntrepotCreate, db: Session = Depends(get_db)):
    """Create a new warehouse"""
    if db.query(Entrepot).filter(Entrepot.code == entrepot_data.code).first():
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Warehouse code already exists")
    
    db_entrepot = Entrepot(**entrepot_data.model_dump())
    db.add(db_entrepot)
    db.commit()
    db.refresh(db_entrepot)
    return db_entrepot


# ============ WMS CROSS-DOCKING & RF TERMINAL ============
@router.post("/cross-docking")
async def executer_cross_docking(payload: dict):
    """Execute direct quai-to-truck cross-docking"""
    from app.services.magasin_wms_avance_service import CrossDockingService
    manifeste_ref = payload.get("manifeste_ref", "MAN-2026-001")
    camion_immat = payload.get("camion_immat", "LT-452-BA")
    colis = payload.get("colis", [{"colis_ref": "COLIS-01", "poids_kg": 1200.0}])
    return CrossDockingService.executer_cross_docking(manifeste_ref, camion_immat, colis)


@router.post("/rf-scan")
async def scanner_code_barres_rf(payload: dict):
    """Scan barcode / QR code with RF handheld terminal"""
    from app.services.magasin_wms_avance_service import RadioFrequencePDAService
    code = payload.get("code_scanne", "ART-1002")
    loc = payload.get("emplacement_cible")
    return RadioFrequencePDAService.scanner_code_barres(code, loc)


@router.get("/reapprovisionnement/rop")
async def calculer_seuil_rop(article_code: str = "ART-REF-01"):
    """Calculate safety stock and Reorder Point (Wilson ROP)"""
    from app.services.magasin_wms_avance_service import ReapprovisionnementService
    return ReapprovisionnementService.calculer_rop_et_stocks_securite(article_code)