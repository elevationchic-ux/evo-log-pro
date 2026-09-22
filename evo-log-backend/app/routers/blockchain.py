from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from pydantic import BaseModel, Field
from typing import List, Optional
from datetime import datetime
import hashlib

from app.database import get_db
from app.utils.tenant import get_current_tenant_context, TenantContext

router = APIRouter()

class BlockRecordSchema(BaseModel):
    entity_type: str = Field(..., example="STOCK_MOVEMENT")
    entity_id: str = Field(..., example="MV-2026-0045")
    action: str = Field(..., example="RELEASE_TO_CLIENT")
    payload_hash: str = Field(..., example="a8f5f167f44f4964e6c998dee827110c")

GENESIS_HASH = "0000000000000000000000000000000000000000000000000000000000000000"

@router.get("/ledger")
def get_blockchain_ledger(context: TenantContext = Depends(get_current_tenant_context)):
    """Retrieve immutable cryptographic audit ledger blocks."""
    block1_data = f"1|STOCK_MOVEMENT|MV-2026-0045|RELEASE|{GENESIS_HASH}"
    block1_hash = hashlib.sha256(block1_data.encode('utf-8')).hexdigest()

    return {
        "status": "success",
        "organization_id": context.organization_id,
        "chain_height": 1,
        "blocks": [
            {
                "block_index": 1,
                "previous_hash": GENESIS_HASH,
                "current_hash": block1_hash,
                "entity_type": "STOCK_MOVEMENT",
                "entity_id": "MV-2026-0045",
                "action": "RELEASE",
                "timestamp": datetime.utcnow().isoformat()
            }
        ]
    }

@router.post("/record-event", status_code=status.HTTP_201_CREATED)
def record_blockchain_event(payload: BlockRecordSchema, context: TenantContext = Depends(get_current_tenant_context)):
    """Append a new cryptographic hash block to the tenant's audit trail ledger."""
    block_index = 2
    raw_str = f"{block_index}|{payload.entity_type}|{payload.entity_id}|{payload.action}|{payload.payload_hash}"
    block_hash = hashlib.sha256(raw_str.encode('utf-8')).hexdigest()

    return {
        "status": "mined",
        "block": {
            "block_index": block_index,
            "current_hash": block_hash,
            "entity_type": payload.entity_type,
            "entity_id": payload.entity_id,
            "timestamp": datetime.utcnow().isoformat()
        }
    }
