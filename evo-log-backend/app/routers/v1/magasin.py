"""
Magasin router - manages warehouse and inventory
"""
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from typing import List
from datetime import datetime

from app.core.database import get_db
from app.schemas.magasin import StockCreate, StockUpdate, StockResponse, MouvementStockCreate, MouvementStockResponse, EntrepotCreate, EntrepotResponse
from app.models.magasin import Stock, MouvementStock, Entrepot
from app.models.user import User
from app.core.security import get_current_user

router = APIRouter()


def resolve_magasin_user(identity: str = Depends(get_current_user), db: Session = Depends(get_db)) -> User:
    user = db.query(User).filter(User.id == int(identity)).first() if str(identity).isdigit() else db.query(User).filter(
        (User.username == str(identity)) | (User.email == str(identity))
    ).first()
    if not user or not user.is_active:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Utilisateur non authentifié.")
    return user


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
async def create_mouvement_stock(mouvement_data: MouvementStockCreate, db: Session = Depends(get_db), current_user: User = Depends(resolve_magasin_user)):
    """Create a stock movement"""
    if current_user.company_id is None:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="L'utilisateur n'est rattaché à aucune société.")
    reference = f"MOV-{datetime.now().strftime('%Y%m%d%H%M%S')}-{current_user.id}"

    db_mouvement = MouvementStock(reference=reference, company_id=current_user.company_id, operateur_id=current_user.id, **mouvement_data.model_dump())
    db.add(db_mouvement)
    db.commit()
    db.refresh(db_mouvement)
    return db_mouvement


@router.get("/mouvements", response_model=List[MouvementStockResponse])
async def get_mouvements_stock(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=500),
    db: Session = Depends(get_db),
    current_user: User = Depends(resolve_magasin_user),
):
    query = db.query(MouvementStock)
    if not current_user.is_superuser:
        query = query.filter(MouvementStock.company_id == current_user.company_id)
    return query.order_by(MouvementStock.date_mouvement.desc()).offset(skip).limit(limit).all()


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