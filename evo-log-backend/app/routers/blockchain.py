"""Ledger append-only a chainage SHA-256 REEL (registre d'audit infalsifiable local).

Ce n'est pas une blockchain distribuee ni un service de minage externe : c'est un
registre local ou chaque bloc encastre son empreinte sur le precedent. L'integrite
est VERIFIABLE en relite la chaine et en recalculant les empreintes. Aucune donnee
n'est inventee : les blocs proviennent d'evenements reellement enregistres."""
import hashlib

from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session
from pydantic import BaseModel, Field

from app.database import get_db
from app.utils.tenant import get_current_tenant_context, TenantContext
from app.models.advanced_crud import Block

router = APIRouter()

GENESIS_HASH = "0" * 64


def _block_hash(height: int, entity_type: str, entity_id: str, action: str,
                payload_hash: str, prev_hash: str) -> str:
    canon = f"{height}|{entity_type}|{entity_id}|{action}|{payload_hash}|{prev_hash}"
    return hashlib.sha256(canon.encode("utf-8")).hexdigest()


def _last_block(db: Session, organization_id):
    q = db.query(Block)
    if organization_id is not None:
        q = q.filter(Block.organization_id == organization_id)
    return q.order_by(Block.height.desc()).first()


class BlockRecordSchema(BaseModel):
    entity_type: str = Field(..., example="STOCK_MOVEMENT")
    entity_id: str = Field(..., example="MV-2026-0045")
    action: str = Field(..., example="RELEASE_TO_CLIENT")
    payload_hash: str = Field(..., example="a8f5f167f44f4964e6c998dee827110c")


@router.get("/ledger")
def get_blockchain_ledger(
    context: TenantContext = Depends(get_current_tenant_context),
    db: Session = Depends(get_db),
):
    """Lecture de la chaine + verification d'integrite (recalcul des empreintes)."""
    org = getattr(context, "organization_id", None)
    q = db.query(Block)
    if org is not None:
        q = q.filter(Block.organization_id == org)
    blocks = q.order_by(Block.height.asc()).all()

    expected_prev = GENESIS_HASH
    intact = True
    for b in blocks:
        recomputed = _block_hash(
            b.height, b.entity_type, b.entity_id, b.action, b.payload_hash, b.prev_hash
        )
        if b.prev_hash != expected_prev or b.block_hash != recomputed:
            intact = False
            break
        expected_prev = b.block_hash

    return {
        "nombre_blocs": len(blocks),
        "integrite_verifiee": intact,
        "chainage": "SHA-256 (local, verifiable)",
        "blocs": [
            {
                "height": b.height, "entity_type": b.entity_type, "entity_id": b.entity_id,
                "action": b.action, "payload_hash": b.payload_hash,
                "prev_hash": b.prev_hash, "block_hash": b.block_hash,
                "created_at": b.created_at.isoformat() if b.created_at else None,
            }
            for b in blocks
        ],
    }


@router.post("/record-event", status_code=status.HTTP_201_CREATED)
def record_blockchain_event(
    payload: BlockRecordSchema,
    context: TenantContext = Depends(get_current_tenant_context),
    db: Session = Depends(get_db),
):
    """Ajoute un bloc reellement enchaine (hash du bloc precedent + empreinte calculee)."""
    org = getattr(context, "organization_id", None)
    last = _last_block(db, org)
    height = (last.height + 1) if last else 0
    prev_hash = last.block_hash if last else GENESIS_HASH
    block_hash = _block_hash(
        height, payload.entity_type, payload.entity_id, payload.action,
        payload.payload_hash, prev_hash,
    )
    block = Block(
        organization_id=org, height=height, prev_hash=prev_hash, block_hash=block_hash,
        mined_by=getattr(context.user, "id", None), **payload.model_dump(),
    )
    db.add(block)
    db.commit()
    db.refresh(block)
    return {
        "id": block.id, "height": height, "prev_hash": prev_hash,
        "block_hash": block_hash, "chaine": "locale", "persiste": True,
    }
