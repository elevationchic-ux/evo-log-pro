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

router = APIRouter()


@router.get("/navires", response_model=List[NavireResponse])
async def get_all_navires(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    """Get all ships"""
    navires = db.query(Navire).offset(skip).limit(limit).all()
    return navires


@router.post("/navires", response_model=NavireResponse, status_code=status.HTTP_201_CREATED)
async def create_navire(navire_data: NavireCreate, db: Session = Depends(get_db)):
    """Create a new ship"""
    db_navire = Navire(**navire_data.model_dump())
    db.add(db_navire)
    db.commit()
    db.refresh(db_navire)
    return db_navire


@router.get("/escales", response_model=List[EscaleResponse])
async def get_all_escales(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    """Get all port calls"""
    escales = db.query(Escale).offset(skip).limit(limit).all()
    return escales


@router.post("/escales", response_model=EscaleResponse, status_code=status.HTTP_201_CREATED)
async def create_escale(escale_data: EscaleCreate, db: Session = Depends(get_db)):
    """Create a new port call"""
    import random
    import string
    
    data = escale_data.model_dump()
    numero_escale = data.pop("numero_escale", None) or (
        f"ESC-{datetime.now().strftime('%Y%m%d')}-{''.join(random.choices(string.ascii_uppercase + string.digits, k=6))}"
    )
    
    db_escale = Escale(numero_escale=numero_escale, **data)
    db.add(db_escale)
    db.commit()
    db.refresh(db_escale)
    return db_escale


@router.get("", response_model=List[OperationAcconageResponse])
@router.get("/", response_model=List[OperationAcconageResponse])
async def list_operations(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    """List all stevedoring operations"""
    return db.query(OperationAcconage).offset(skip).limit(limit).all()


@router.post("", response_model=OperationAcconageResponse, status_code=status.HTTP_201_CREATED)
@router.post("/", response_model=OperationAcconageResponse, status_code=status.HTTP_201_CREATED)
async def create_operation_root(operation_data: OperationAcconageCreate, db: Session = Depends(get_db)):
    """Create a new stevedoring operation from root endpoint"""
    return await create_operation_acconage(operation_data, db)


@router.post("/operations", response_model=OperationAcconageResponse, status_code=status.HTTP_201_CREATED)
async def create_operation_acconage(operation_data: OperationAcconageCreate, db: Session = Depends(get_db)):
    """Create a new stevedoring operation"""
    import random
    import string
    
    reference = f"OPA-{datetime.now().strftime('%Y%m%d')}-{''.join(random.choices(string.ascii_uppercase + string.digits, k=6))}"
    
    db_operation = OperationAcconage(reference=reference, **operation_data.model_dump())
    db.add(db_operation)
    db.commit()
    db.refresh(db_operation)
    return db_operation


# ============ DOSSIER UNIQUE DE MARCHANDISE (vue consolidee honnete) ============
@router.get("/dossier-marchandise")
async def dossier_marchandise(
    numero_conteneur: str = None,
    numero_bl: str = None,
    db: Session = Depends(get_db),
):
    """Fiche consolidee d'une marchandise le long de la chaine portuaire.

    Cle d'entree : un numero de conteneur OU un numero de connaissement (B/L).
    Retourne, pour chaque etape, UNIQUEMENT ce qui est reellement relie (cle
    etrangere ou numero physique). Les etapes que le schema ne relie pas au
    conteneur sont signalees 'non_liciable_en_base' : rien n'est invente.
    """
    from app.services.dossier_marchandise import consigner_dossier_marchandise

    return consigner_dossier_marchandise(
        db, numero_conteneur=numero_conteneur, numero_bl=numero_bl
    )


# ============ BAPLIE EDI & TOS STOWAGE 3D ============
@router.post("/baplie/import")
async def importer_plan_baplie(payload: dict, db: Session = Depends(get_db)):
    """Import and validate BAPLIE EDIFACT message with IMDG segregation check"""
    from app.services.acconage_service import PortAdvancedTOSService
    edi_text = payload.get("edi_content", "")
    escale_id = int(payload.get("escale_id", 1))
    return PortAdvancedTOSService.parse_baplie_edi(edi_text, escale_id)


@router.get("/baplie/export/{escale_id}")
async def exporter_plan_baplie(escale_id: int, db: Session = Depends(get_db)):
    """Export vessel stowage plan into SMDG BAPLIE 2.2 EDIFACT format"""
    from app.services.acconage_service import PortAdvancedTOSService
    edi_content = PortAdvancedTOSService.generate_baplie_edi(escale_id, db)
    return {"escale_id": escale_id, "baplie_edi": edi_content, "standard": "SMDG BAPLIE 2.2"}


# ============ YARD MANAGEMENT TERRE-PLEIN ============
@router.get("/yard/positions")
@router.get("/yard/state")
async def obtenir_etat_terre_plein():
    """Get container yard state and blocks occupancy (PAD / PAK)"""
    from app.services.acconage_service import PortAdvancedTOSService
    return PortAdvancedTOSService.get_yard_state()


@router.post("/yard/assign")
async def assigner_emplacement_terre_plein(payload: dict):
    """Dynamically assign container slot minimizing re-handling"""
    from app.services.acconage_service import PortAdvancedTOSService
    return PortAdvancedTOSService.assign_yard_slot(payload)


# ============ FACTURATION DROITS DE QUAI PAD / PAK ============
@router.get("/facturation-quai/{escale_id}")
async def calculer_redevances_quai(
    escale_id: int, port_code: str = "PAD", db: Session = Depends(get_db)
):
    """Estimation des redevances portuaires PAD/PAK d'une escale relle.

    Quantities are derived from the actual port call and prices from the official
    TarifPortuaire table. If the official tariffs are not loaded, the service
    answers 501 rather than inventing rates. Nothing is certified here.
    """
    from app.services.acconage_service import PortAdvancedTOSService
    return PortAdvancedTOSService.calculate_port_dues_cemac(db, escale_id, port_code)


@router.post("/facturation-quai/{escale_id}/generer-facture")
async def generer_facture_quai(escale_id: int, payload: dict = None, db: Session = Depends(get_db)):
    """Prepare a DRAFT port-dues invoice for an armateur (no fake certification).

    Honesty fix: the previous version stamped statut_facturation='GENEREE_VALIDEE'
    on an invoice computed from hardcoded rates and fabricated container counts.
    It now returns the honest estimation draft only; certification/validation must
    come from a real, signed emission step, never simulated here.
    """
    from app.services.acconage_service import PortAdvancedTOSService
    port_code = (payload or {}).get("port_code", "PAD")
    facture = PortAdvancedTOSService.calculate_port_dues_cemac(db, escale_id, port_code)
    facture["note"] = (
        "Brouillon d'estimation. Non certifie : aucune emission signee n'a eu lieu."
    )
    return facture