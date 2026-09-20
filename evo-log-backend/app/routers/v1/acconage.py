"""
Acconage router - manages port operations and stevedoring
"""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from datetime import datetime

from app.core.database import get_db
from app.schemas.acconage import NavireCreate, NavireResponse, EscaleCreate, EscaleUpdate, EscaleResponse, OperationAcconageCreate, OperationAcconageResponse
from app.models.acconage import Navire, Escale, OperationAcconage
from app.models.user import User
from app.utils.rbac import get_current_user

router = APIRouter()


@router.get("/navires", response_model=List[NavireResponse])
async def get_all_navires(skip: int = 0, limit: int = 100, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    """Get all ships"""
    query = db.query(Navire)
    if not current_user.is_superuser:
        query = query.filter(Navire.company_id == current_user.company_id)
    navires = query.offset(skip).limit(limit).all()
    return navires


@router.post("/navires", response_model=NavireResponse, status_code=status.HTTP_201_CREATED)
async def create_navire(navire_data: NavireCreate, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    """Create a new ship"""
    values = navire_data.model_dump()
    if not current_user.is_superuser:
        values["company_id"] = current_user.company_id
    db_navire = Navire(**values)
    db.add(db_navire)
    db.commit()
    db.refresh(db_navire)
    return db_navire


@router.get("/escales", response_model=List[EscaleResponse])
async def get_all_escales(skip: int = 0, limit: int = 100, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    """Get all port calls"""
    query = db.query(Escale)
    if not current_user.is_superuser:
        query = query.filter(Escale.company_id == current_user.company_id)
    escales = query.offset(skip).limit(limit).all()
    return escales


@router.post("/escales", response_model=EscaleResponse, status_code=status.HTTP_201_CREATED)
async def create_escale(escale_data: EscaleCreate, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    """Create a new port call"""
    import random
    import string
    
    numero_escale = f"ESC-{datetime.now().strftime('%Y%m%d')}-{''.join(random.choices(string.ascii_uppercase + string.digits, k=6))}"
    
    values = escale_data.model_dump()
    if not current_user.is_superuser:
        values["company_id"] = current_user.company_id
    db_escale = Escale(numero_escale=numero_escale, **values)
    db.add(db_escale)
    db.commit()
    db.refresh(db_escale)
    return db_escale


@router.get("", response_model=List[OperationAcconageResponse])
@router.get("/", response_model=List[OperationAcconageResponse])
async def list_operations(skip: int = 0, limit: int = 100, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    """List all stevedoring operations"""
    query = db.query(OperationAcconage).join(Escale, OperationAcconage.escale_id == Escale.id)
    if not current_user.is_superuser:
        query = query.filter(Escale.company_id == current_user.company_id)
    return query.offset(skip).limit(limit).all()


@router.post("", response_model=OperationAcconageResponse, status_code=status.HTTP_201_CREATED)
@router.post("/", response_model=OperationAcconageResponse, status_code=status.HTTP_201_CREATED)
async def create_operation_root(operation_data: OperationAcconageCreate, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    """Create a new stevedoring operation from root endpoint"""
    return await create_operation_acconage(operation_data, db, current_user)


@router.post("/operations", response_model=OperationAcconageResponse, status_code=status.HTTP_201_CREATED)
async def create_operation_acconage(operation_data: OperationAcconageCreate, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    """Create a new stevedoring operation"""
    import random
    import string
    
    reference = f"OPA-{datetime.now().strftime('%Y%m%d')}-{''.join(random.choices(string.ascii_uppercase + string.digits, k=6))}"
    
    values = operation_data.model_dump()
    escale = db.query(Escale).filter(Escale.id == values.get("escale_id")).first()
    if not escale or (not current_user.is_superuser and escale.company_id != current_user.company_id):
        raise HTTPException(status_code=404, detail="Escale non trouvée")
    db_operation = OperationAcconage(reference=reference, created_by=current_user.id, **values)
    db.add(db_operation)
    db.commit()
    db.refresh(db_operation)
    return db_operation


# ============ BAPLIE EDI & TOS STOWAGE 3D ============
@router.post("/baplie/import")
async def importer_plan_baplie(payload: dict, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    """Import and validate BAPLIE EDIFACT message with IMDG segregation check"""
    from app.services.acconage_service import PortAdvancedTOSService
    edi_text = payload.get("edi_content", "")
    escale_id = int(payload.get("escale_id", 1))
    return PortAdvancedTOSService.parse_baplie_edi(edi_text, escale_id)


@router.get("/baplie/export/{escale_id}")
async def exporter_plan_baplie(escale_id: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    """Export vessel stowage plan into SMDG BAPLIE 2.2 EDIFACT format"""
    from app.services.acconage_service import PortAdvancedTOSService
    edi_content = PortAdvancedTOSService.generate_baplie_edi(escale_id, db)
    return {"escale_id": escale_id, "baplie_edi": edi_content, "standard": "SMDG BAPLIE 2.2"}


# ============ YARD MANAGEMENT TERRE-PLEIN ============
@router.get("/yard/positions")
@router.get("/yard/state")
async def obtenir_etat_terre_plein(current_user: User = Depends(get_current_user)):
    """Get container yard state and blocks occupancy (PAD / PAK)"""
    from app.services.acconage_service import PortAdvancedTOSService
    return PortAdvancedTOSService.get_yard_state()


@router.post("/yard/assign")
async def assigner_emplacement_terre_plein(payload: dict, current_user: User = Depends(get_current_user)):
    """Dynamically assign container slot minimizing re-handling"""
    from app.services.acconage_service import PortAdvancedTOSService
    return PortAdvancedTOSService.assign_yard_slot(payload)


# ============ FACTURATION DROITS DE QUAI PAD / PAK ============
@router.get("/facturation-quai/{escale_id}")
async def calculer_redevances_quai(escale_id: int, port_code: str = "PAD", current_user: User = Depends(get_current_user)):
    """Calculate official PAD / PAK port dues, wharfage and stevedoring invoice"""
    from app.services.acconage_service import PortAdvancedTOSService
    return PortAdvancedTOSService.calculate_port_dues_cemac(escale_id, port_code)


@router.post("/facturation-quai/{escale_id}/generer-facture")
async def generer_facture_quai(escale_id: int, payload: dict = None, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    """Issue certified armateur invoice for port dues and berthing fees"""
    from app.services.acconage_service import PortAdvancedTOSService
    port_code = (payload or {}).get("port_code", "PAD")
    facture = PortAdvancedTOSService.calculate_port_dues_cemac(escale_id, port_code)
    facture["statut_facturation"] = "GENEREE_VALIDEE"
    facture["date_validation"] = datetime.utcnow().isoformat()
    return facture