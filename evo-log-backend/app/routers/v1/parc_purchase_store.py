"""
Tranche B router : parc (zones / emplacements / gate in-out) + purchase
(requisitions d'achat avec workflow d'approbation).

Monte sur /api/v1/parc et /api/v1/purchase (chemins disjoints des routeurs
existants). Les endpoints GET liste repondent l'enveloppe {items,total,
pending:False} conforme au protocole pending-modules. Le montage precede le
catch-all, donc ces routes reelles gagnent la priorite.
"""
from __future__ import annotations

import random
import string
from datetime import datetime
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.security import get_current_user
from app.models.parc import ZoneParc, EmplacementParc, MouvementParc
from app.models.purchase import Requisition, RequisitionStatut
from app.models.user import User
from app.schemas.parc_purchase import (
    ZoneParcCreate,
    ZoneParcUpdate,
    ZoneParcResponse,
    EmplacementParcCreate,
    EmplacementParcUpdate,
    EmplacementParcResponse,
    GateMovementCreate,
    MouvementParcResponse,
    RequisitionCreate,
    RequisitionUpdate,
    RequisitionDecision,
    RequisitionResponse,
)


def _ref(prefix: str) -> str:
    return f"{prefix}-{datetime.now().strftime('%Y%m%d')}-{''.join(random.choices(string.ascii_uppercase + string.digits, k=5))}"


def _envelope(rows, schema) -> dict:
    return {
        "items": [schema.model_validate(r).model_dump() for r in rows],
        "total": len(rows),
        "pending": False,
    }


# ─── PARC : zones & emplacements & gate ─────────────────────────────────────
parc_router = APIRouter()


@parc_router.get("/zones", response_model=dict)
async def list_zones(
    skip: int = 0,
    limit: int = Query(100, le=500),
    search: Optional[str] = None,
    db: Session = Depends(get_db),
):
    q = db.query(ZoneParc).filter(ZoneParc.is_active.is_(True))
    if search:
        like = f"%{search}%"
        q = q.filter((ZoneParc.nom.ilike(like)) | (ZoneParc.code.ilike(like)))
    return _envelope(q.offset(skip).limit(limit).all(), ZoneParcResponse)


@parc_router.post("/zones", response_model=ZoneParcResponse, status_code=201)
async def create_zone(payload: ZoneParcCreate, db: Session = Depends(get_db)):
    row = ZoneParc(**payload.model_dump())
    db.add(row)
    db.commit()
    db.refresh(row)
    return row


@parc_router.get("/zones/{zone_id}", response_model=ZoneParcResponse)
async def get_zone(zone_id: int, db: Session = Depends(get_db)):
    row = db.get(ZoneParc, zone_id)
    if not row:
        raise HTTPException(status_code=404, detail="Zone introuvable")
    return row


@parc_router.put("/zones/{zone_id}", response_model=ZoneParcResponse)
async def update_zone(zone_id: int, payload: ZoneParcUpdate, db: Session = Depends(get_db)):
    row = db.get(ZoneParc, zone_id)
    if not row:
        raise HTTPException(status_code=404, detail="Zone introuvable")
    for k, v in payload.model_dump(exclude_unset=True).items():
        setattr(row, k, v)
    db.commit()
    db.refresh(row)
    return row


@parc_router.delete("/zones/{zone_id}", status_code=204)
async def delete_zone(zone_id: int, db: Session = Depends(get_db)):
    row = db.get(ZoneParc, zone_id)
    if not row:
        raise HTTPException(status_code=404, detail="Zone introuvable")
    row.is_active = False
    db.commit()
    return None


@parc_router.get("/emplacements", response_model=dict)
async def list_emplacements(
    skip: int = 0,
    limit: int = Query(100, le=500),
    zone_id: Optional[int] = None,
    statut: Optional[str] = None,
    db: Session = Depends(get_db),
):
    q = db.query(EmplacementParc).filter(EmplacementParc.is_active.is_(True))
    if zone_id:
        q = q.filter(EmplacementParc.zone_id == zone_id)
    if statut:
        q = q.filter(EmplacementParc.statut == statut)
    return _envelope(q.offset(skip).limit(limit).all(), EmplacementParcResponse)


@parc_router.post("/emplacements", response_model=EmplacementParcResponse, status_code=201)
async def create_emplacement(payload: EmplacementParcCreate, db: Session = Depends(get_db)):
    if payload.zone_id and not db.get(ZoneParc, payload.zone_id):
        raise HTTPException(status_code=400, detail="Zone rattachee inexistante")
    row = EmplacementParc(**payload.model_dump())
    db.add(row)
    db.commit()
    db.refresh(row)
    return row


@parc_router.get("/emplacements/{empl_id}", response_model=EmplacementParcResponse)
async def get_emplacement(empl_id: int, db: Session = Depends(get_db)):
    row = db.get(EmplacementParc, empl_id)
    if not row:
        raise HTTPException(status_code=404, detail="Emplacement introuvable")
    return row


@parc_router.put("/emplacements/{empl_id}", response_model=EmplacementParcResponse)
async def update_emplacement(empl_id: int, payload: EmplacementParcUpdate, db: Session = Depends(get_db)):
    row = db.get(EmplacementParc, empl_id)
    if not row:
        raise HTTPException(status_code=404, detail="Emplacement introuvable")
    for k, v in payload.model_dump(exclude_unset=True).items():
        setattr(row, k, v)
    db.commit()
    db.refresh(row)
    return row


@parc_router.delete("/emplacements/{empl_id}", status_code=204)
async def delete_emplacement(empl_id: int, db: Session = Depends(get_db)):
    row = db.get(EmplacementParc, empl_id)
    if not row:
        raise HTTPException(status_code=404, detail="Emplacement introuvable")
    row.is_active = False
    db.commit()
    return None


def _gate(db: Session, sens: str, payload: GateMovementCreate):
    if payload.emplacement_id:
        empl = db.get(EmplacementParc, payload.emplacement_id)
        if not empl:
            raise HTTPException(status_code=400, detail="Emplacement inconnu")
        empl.statut = "occupe" if sens == "entree" else "libre"
        if sens == "sortie":
            empl.contenu = None
    row = MouvementParc(sens=sens, **payload.model_dump())
    db.add(row)
    db.commit()
    db.refresh(row)
    return row


@parc_router.post("/gate-in", response_model=MouvementParcResponse, status_code=201)
async def gate_in(payload: GateMovementCreate, db: Session = Depends(get_db)):
    """Entree conteneur/vehicule au parc : marque l'emplacement occupe."""
    return _gate(db, "entree", payload)


@parc_router.post("/gate-out", response_model=MouvementParcResponse, status_code=201)
async def gate_out(payload: GateMovementCreate, db: Session = Depends(get_db)):
    """Sortie du parc : libere l'emplacement."""
    return _gate(db, "sortie", payload)


@parc_router.get("/mouvements", response_model=dict)
async def list_mouvements(
    skip: int = 0,
    limit: int = Query(100, le=500),
    sens: Optional[str] = None,
    db: Session = Depends(get_db),
):
    q = db.query(MouvementParc)
    if sens:
        q = q.filter(MouvementParc.sens == sens)
    rows = q.order_by(MouvementParc.id.desc()).offset(skip).limit(limit).all()
    return _envelope(rows, MouvementParcResponse)


# ─── PURCHASE : requisitions (workflow) ──────────────────────────────────────
# Cohérent avec le routeur purchase existant : endpoints protégés get_current_user.
requisition_router = APIRouter(dependencies=[Depends(get_current_user)])


@requisition_router.get("/requisitions", response_model=dict)
@requisition_router.get("/requisitions/", response_model=dict, include_in_schema=False)
async def list_requisitions(
    skip: int = 0,
    limit: int = Query(100, le=500),
    statut: Optional[str] = None,
    db: Session = Depends(get_db),
):
    q = db.query(Requisition).filter(Requisition.is_active.is_(True))
    if statut:
        q = q.filter(Requisition.statut == statut)
    return _envelope(q.order_by(Requisition.id.desc()).offset(skip).limit(limit).all(), RequisitionResponse)


@requisition_router.post("/requisitions", response_model=RequisitionResponse, status_code=201)
@requisition_router.post("/requisitions/", response_model=RequisitionResponse, status_code=201, include_in_schema=False)
async def create_requisition(
    payload: RequisitionCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    data = payload.model_dump()
    demandeur = data.pop("demandeur", None) or (
        getattr(current_user, "full_name", None) or current_user.username
    )
    row = Requisition(
        reference=data.pop("reference", None) or _ref("DA"),
        demandeur=demandeur,
        **data,
    )
    db.add(row)
    db.commit()
    db.refresh(row)
    return row


@requisition_router.get("/requisitions/{req_id}", response_model=RequisitionResponse)
async def get_requisition(req_id: int, db: Session = Depends(get_db)):
    row = db.get(Requisition, req_id)
    if not row:
        raise HTTPException(status_code=404, detail="Requisition introuvable")
    return row


@requisition_router.put("/requisitions/{req_id}", response_model=RequisitionResponse)
async def update_requisition(req_id: int, payload: RequisitionUpdate, db: Session = Depends(get_db)):
    row = db.get(Requisition, req_id)
    if not row:
        raise HTTPException(status_code=404, detail="Requisition introuvable")
    if row.statut != RequisitionStatut.BROUILLON:
        raise HTTPException(status_code=400, detail="Seule une requisition en brouillon est modifiable")
    for k, v in payload.model_dump(exclude_unset=True).items():
        setattr(row, k, v)
    db.commit()
    db.refresh(row)
    return row


@requisition_router.delete("/requisitions/{req_id}", status_code=204)
async def delete_requisition(req_id: int, db: Session = Depends(get_db)):
    row = db.get(Requisition, req_id)
    if not row:
        raise HTTPException(status_code=404, detail="Requisition introuvable")
    if row.statut not in (RequisitionStatut.BROUILLON, RequisitionStatut.REJETEE):
        raise HTTPException(status_code=400, detail="Impossible de supprimer une requisition engagee")
    row.is_active = False
    db.commit()
    return None


@requisition_router.post("/requisitions/{req_id}/submit", response_model=RequisitionResponse)
async def submit_requisition(req_id: int, db: Session = Depends(get_db)):
    row = db.get(Requisition, req_id)
    if not row:
        raise HTTPException(status_code=404, detail="Requisition introuvable")
    if row.statut != RequisitionStatut.BROUILLON:
        raise HTTPException(status_code=400, detail="Seule une requisition en brouillon peut etre soumise")
    row.statut = RequisitionStatut.SOUMISE
    row.date_soumission = datetime.now()
    db.commit()
    db.refresh(row)
    return row


def _decide(req_id: int, db: Session, target: RequisitionStatut, payload: Optional[RequisitionDecision], user: User):
    row = db.get(Requisition, req_id)
    if not row:
        raise HTTPException(status_code=404, detail="Requisition introuvable")
    if row.statut != RequisitionStatut.SOUMISE:
        raise HTTPException(status_code=400, detail="Seule une requisition soumise peut recevoir une decision")
    row.statut = target
    row.date_decision = datetime.now()
    row.approuve_par = user.id
    if payload and payload.notes_approbation:
        row.notes_approbation = payload.notes_approbation
    db.commit()
    db.refresh(row)
    return row


@requisition_router.post("/requisitions/{req_id}/approve", response_model=RequisitionResponse)
async def approve_requisition(
    req_id: int,
    payload: Optional[RequisitionDecision] = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return _decide(req_id, db, RequisitionStatut.APPROUVEE, payload, current_user)


@requisition_router.post("/requisitions/{req_id}/reject", response_model=RequisitionResponse)
async def reject_requisition(
    req_id: int,
    payload: Optional[RequisitionDecision] = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return _decide(req_id, db, RequisitionStatut.REJETEE, payload, current_user)
