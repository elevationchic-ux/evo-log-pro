from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from pydantic import BaseModel, Field
from typing import List, Optional
from datetime import datetime
import hashlib

from app.database import get_db
from app.utils.tenant import get_current_tenant_context, TenantContext
from app.core.not_implemented import not_implemented

router = APIRouter()

class BlockRecordSchema(BaseModel):
    entity_type: str = Field(..., example="STOCK_MOVEMENT")
    entity_id: str = Field(..., example="MV-2026-0045")
    action: str = Field(..., example="RELEASE_TO_CLIENT")
    payload_hash: str = Field(..., example="a8f5f167f44f4964e6c998dee827110c")

GENESIS_HASH = "0000000000000000000000000000000000000000000000000000000000000000"

@router.get("/ledger")
def get_blockchain_ledger(context: TenantContext = Depends(get_current_tenant_context)):
    """Registre blockchain immuable : aucune chaine persistante n'est branchée."""
    not_implemented(
        "Ledger blockchain (lecture des blocs)",
        "un backend de registre append-only persistant (table blocks + chainage "
        "SHA-256 réél), inexistant a ce jour",
    )

@router.post("/record-event", status_code=status.HTTP_201_CREATED)
def record_blockchain_event(payload: BlockRecordSchema, context: TenantContext = Depends(get_current_tenant_context)):
    """Ajout d'un bloc : non implémenté (pas de persistance de chaine réelle)."""
    not_implemented(
        "Enregistrement d'un evenement blockchain",
        "un service de minage/chainage persistant et un stockage des blocs, "
        "inexistants a ce jour",
    )
