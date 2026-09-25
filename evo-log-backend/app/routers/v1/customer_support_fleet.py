"""
Tranche C router : fleet (/api/v1/fleet), customers CRM
(/api/v1/customers) et support (/api/v1/support).

- fleet/vehicles est un proxy sur le modele Vehicule existant (parc.py) :
  meme donnee, deux fenetres metier (parc technique vs flotte operationnelle).
- customers : fiches CRM dediees (crm_customers) + contrats.
- support : tickets et incidents (tables dediees, differentes des incidents
  QHSE/transport deja modeles).

Enveloppes {items,total,pending:False} conformes au protocole pending-modules ;
montes avant le catch-all dans main.py, donc prioritaires.
"""
from __future__ import annotations

import random
import string
from datetime import datetime
from typing import Optional

from fastapi import APIRouter, Depends, File, Form, HTTPException, Query, UploadFile
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.models.customer_support import (
    Customer, ContractCustomer, SupportTicket, SupportIncident, FleetDocument,
)
from app.models.parc import CarburantRecord, Vehicule, VehiculeStatus
from app.schemas.customer_support import (
    FleetVehicleCreate,
    FleetVehicleUpdate,
    FleetVehicleResponse,
    FuelRecordCreate,
    FuelRecordResponse,
    CustomerCreate,
    CustomerUpdate,
    CustomerResponse,
    ContractCreate,
    ContractResponse,
    TicketCreate,
    TicketResponse,
    IncidentCreate,
    IncidentUpdate,
    IncidentResponse,
    FleetDocumentResponse,
)


def _ref(prefix: str) -> str:
    return f"{prefix}-{datetime.now().strftime('%Y%m%d')}-{''.join(random.choices(string.ascii_uppercase + string.digits, k=5))}"


def _envelope(rows, schema) -> dict:
    return {
        "items": [schema.model_validate(r).model_dump() for r in rows],
        "total": len(rows),
        "pending": False,
    }


def _get_or_404(model, db: Session, ident: int, label: str):
    row = db.get(model, ident)
    if not row:
        raise HTTPException(status_code=404, detail=f"{label} introuvable")
    return row


# ─── FLEET ────────────────────────────────────────────────────────────────────
fleet_router = APIRouter()


@fleet_router.get("/vehicles", response_model=dict)
async def list_vehicles(
    skip: int = 0,
    limit: int = Query(100, le=500),
    search: Optional[str] = None,
    db: Session = Depends(get_db),
):
    q = db.query(Vehicule).filter(Vehicule.is_active.is_(True))
    if search:
        q = q.filter(Vehicule.immatriculation.ilike(f"%{search}%"))
    return _envelope(q.offset(skip).limit(limit).all(), FleetVehicleResponse)


@fleet_router.post("/vehicles", response_model=FleetVehicleResponse, status_code=201)
async def create_vehicle(payload: FleetVehicleCreate, db: Session = Depends(get_db)):
    if db.query(Vehicule).filter(Vehicule.immatriculation == payload.immatriculation).first():
        raise HTTPException(status_code=400, detail="Un vehicule avec cette immatriculation existe deja")
    data = payload.model_dump()
    status = data.pop("status", None) or VehiculeStatus.DISPONIBLE.value
    row = Vehicule(status=status, **data)
    db.add(row)
    db.commit()
    db.refresh(row)
    return row


@fleet_router.get("/vehicles/{vehicle_id}", response_model=FleetVehicleResponse)
async def get_vehicle(vehicle_id: int, db: Session = Depends(get_db)):
    return _get_or_404(Vehicule, db, vehicle_id, "Vehicule")


@fleet_router.put("/vehicles/{vehicle_id}", response_model=FleetVehicleResponse)
async def update_vehicle(vehicle_id: int, payload: FleetVehicleUpdate, db: Session = Depends(get_db)):
    row = _get_or_404(Vehicule, db, vehicle_id, "Vehicule")
    for k, v in payload.model_dump(exclude_unset=True).items():
        setattr(row, k, v)
    db.commit()
    db.refresh(row)
    return row


@fleet_router.delete("/vehicles/{vehicle_id}", status_code=204)
async def delete_vehicle(vehicle_id: int, db: Session = Depends(get_db)):
    row = _get_or_404(Vehicule, db, vehicle_id, "Vehicule")
    row.is_active = False
    db.commit()
    return None


@fleet_router.get("/fuel-records", response_model=dict)
async def list_fuel_records(
    skip: int = 0,
    limit: int = Query(100, le=500),
    vehicule_id: Optional[int] = None,
    db: Session = Depends(get_db),
):
    q = db.query(CarburantRecord)
    if vehicule_id:
        q = q.filter(CarburantRecord.vehicule_id == vehicule_id)
    rows = q.order_by(CarburantRecord.id.desc()).offset(skip).limit(limit).all()
    return _envelope(rows, FuelRecordResponse)


@fleet_router.post("/fuel-records", response_model=FuelRecordResponse, status_code=201)
async def create_fuel_record(payload: FuelRecordCreate, db: Session = Depends(get_db)):
    data = payload.model_dump()
    if data.get("vehicule_id") and not data.get("immatriculation"):
        veh = db.get(Vehicule, data["vehicule_id"])
        if not veh:
            raise HTTPException(status_code=400, detail="Vehicule inconnu")
        data["immatriculation"] = veh.immatriculation
    row = CarburantRecord(**data)
    db.add(row)
    db.commit()
    db.refresh(row)
    return row


@fleet_router.get("/documents", response_model=dict)
async def list_fleet_documents(
    vehicle_id: Optional[int] = None,
    db: Session = Depends(get_db),
):
    q = db.query(FleetDocument)
    if vehicle_id:
        q = q.filter(FleetDocument.vehicule_id == vehicle_id)
    return _envelope(q.order_by(FleetDocument.id.desc()).all(), FleetDocumentResponse)


@fleet_router.post("/documents", response_model=FleetDocumentResponse, status_code=201)
async def upload_fleet_document(
    vehicule_id: Optional[int] = Form(None),
    file: Optional[UploadFile] = File(None),
    type_document: Optional[str] = Form(None),
    date_expiration: Optional[str] = Form(None),
    url: Optional[str] = Form(None),
    db: Session = Depends(get_db),
):
    """Accepte le FormData frontend (fichier + champs). Le binaire n'est pas
    persiste ici (GED dedicatee hors perimetre) : seules les metadonnees sont
    enregistrees, avec le nom du fichier recu."""
    exp = None
    if date_expiration:
        try:
            exp = datetime.fromisoformat(date_expiration)
        except ValueError:
            pass
    row = FleetDocument(
        vehicule_id=vehicule_id,
        type_document=type_document,
        nom_fichier=file.filename if file else None,
        url=url,
        date_expiration=exp,
    )
    db.add(row)
    db.commit()
    db.refresh(row)
    return row


# ─── CUSTOMERS (CRM) ──────────────────────────────────────────────────────────
customer_router = APIRouter()


@customer_router.get("", response_model=dict)
@customer_router.get("/", response_model=dict, include_in_schema=False)
async def list_customers(
    skip: int = 0,
    limit: int = Query(100, le=500),
    search: Optional[str] = None,
    db: Session = Depends(get_db),
):
    q = db.query(Customer).filter(Customer.is_active.is_(True))
    if search:
        like = f"%{search}%"
        q = q.filter((Customer.name.ilike(like)) | (Customer.code.ilike(like)))
    return _envelope(q.offset(skip).limit(limit).all(), CustomerResponse)


@customer_router.post("", response_model=CustomerResponse, status_code=201)
@customer_router.post("/", response_model=CustomerResponse, status_code=201, include_in_schema=False)
async def create_customer(payload: CustomerCreate, db: Session = Depends(get_db)):
    data = payload.model_dump()
    row = Customer(code=data.pop("code", None) or _ref("CUS"), **data)
    db.add(row)
    db.commit()
    db.refresh(row)
    return row


# Attention : /contracts declare AVANT /{customer_id} (sinon "contracts"
# serait capture comme un id et renverrait 422).
@customer_router.get("/contracts", response_model=dict)
async def list_contracts(
    customer_id: Optional[int] = None,
    db: Session = Depends(get_db),
):
    q = db.query(ContractCustomer)
    if customer_id:
        q = q.filter(ContractCustomer.customer_id == customer_id)
    return _envelope(q.order_by(ContractCustomer.id.desc()).all(), ContractResponse)


@customer_router.post("/contracts", response_model=ContractResponse, status_code=201)
async def create_contract(payload: ContractCreate, db: Session = Depends(get_db)):
    data = payload.model_dump()
    if data.get("customer_id") and not db.get(Customer, data["customer_id"]):
        raise HTTPException(status_code=400, detail="Client rattache inexistant")
    row = ContractCustomer(reference=data.pop("reference", None) or _ref("CTR"), **data)
    db.add(row)
    db.commit()
    db.refresh(row)
    return row


@customer_router.get("/{customer_id}", response_model=CustomerResponse)
async def get_customer(customer_id: int, db: Session = Depends(get_db)):
    return _get_or_404(Customer, db, customer_id, "Client")


@customer_router.put("/{customer_id}", response_model=CustomerResponse)
async def update_customer(customer_id: int, payload: CustomerUpdate, db: Session = Depends(get_db)):
    row = _get_or_404(Customer, db, customer_id, "Client")
    for k, v in payload.model_dump(exclude_unset=True).items():
        setattr(row, k, v)
    db.commit()
    db.refresh(row)
    return row


@customer_router.delete("/{customer_id}", status_code=204)
async def delete_customer(customer_id: int, db: Session = Depends(get_db)):
    row = _get_or_404(Customer, db, customer_id, "Client")
    row.is_active = False
    db.commit()
    return None


# ─── SUPPORT ──────────────────────────────────────────────────────────────────
support_router = APIRouter()


@support_router.get("/tickets", response_model=dict)
async def list_tickets(
    skip: int = 0,
    limit: int = Query(100, le=500),
    statut: Optional[str] = None,
    db: Session = Depends(get_db),
):
    q = db.query(SupportTicket).filter(SupportTicket.is_active.is_(True))
    if statut:
        q = q.filter(SupportTicket.statut == statut)
    rows = q.order_by(SupportTicket.id.desc()).offset(skip).limit(limit).all()
    return _envelope(rows, TicketResponse)


@support_router.post("/tickets", response_model=TicketResponse, status_code=201)
async def create_ticket(payload: TicketCreate, db: Session = Depends(get_db)):
    row = SupportTicket(reference=_ref("TKT"), **payload.model_dump())
    db.add(row)
    db.commit()
    db.refresh(row)
    return row


@support_router.get("/incidents", response_model=dict)
async def list_incidents(
    skip: int = 0,
    limit: int = Query(100, le=500),
    statut: Optional[str] = None,
    db: Session = Depends(get_db),
):
    q = db.query(SupportIncident).filter(SupportIncident.is_active.is_(True))
    if statut:
        q = q.filter(SupportIncident.statut == statut)
    rows = q.order_by(SupportIncident.id.desc()).offset(skip).limit(limit).all()
    return _envelope(rows, IncidentResponse)


@support_router.post("/incidents", response_model=IncidentResponse, status_code=201)
async def create_incident(payload: IncidentCreate, db: Session = Depends(get_db)):
    row = SupportIncident(reference=_ref("INC"), **payload.model_dump())
    db.add(row)
    db.commit()
    db.refresh(row)
    return row


@support_router.put("/incidents/{incident_id}", response_model=IncidentResponse)
async def update_incident(incident_id: int, payload: IncidentUpdate, db: Session = Depends(get_db)):
    row = _get_or_404(SupportIncident, db, incident_id, "Incident")
    data = payload.model_dump(exclude_unset=True)
    for k, v in data.items():
        setattr(row, k, v)
    if data.get("statut") in ("resolu", "ferme") and not row.resolved_at:
        row.resolved_at = datetime.now()
    db.commit()
    db.refresh(row)
    return row
