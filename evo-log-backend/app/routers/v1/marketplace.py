import hashlib
import secrets

from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session
from pydantic import BaseModel, Field
from typing import List, Optional

from app.database import get_db
from app.utils.tenant import get_current_tenant_context, TenantContext
from app.models.advanced_crud import TenantAPIKey

router = APIRouter()


class APIKeyCreateSchema(BaseModel):
    key_name: str = Field(..., example="Intégration Odoo / SAP B2B")
    allowed_ips: Optional[List[str]] = Field(None, example=["197.239.12.4"])


class APIKeyMeta(BaseModel):
    id: int
    key_name: str
    key_prefix: str
    allowed_ips: Optional[List[str]]
    active: bool

    class Config:
        from_attributes = True


class APIKeyCreated(APIKeyMeta):
    cle_secrete: str = Field(..., description="Cle complete retournee UNE SEULE FOIS, jamais stockee en clair.")


def _scope(context: TenantContext, query):
    if context.organization_id is not None:
        return query.filter(TenantAPIKey.organization_id == context.organization_id)
    return query


@router.get("/api-keys", response_model=List[APIKeyMeta])
def list_tenant_api_keys(
    context: TenantContext = Depends(get_current_tenant_context),
    db: Session = Depends(get_db),
):
    """Cles API du tenant : on expose prefixe + etat, jamais le hash ni la cle claire."""
    return _scope(context, db.query(TenantAPIKey)).order_by(TenantAPIKey.created_at.desc()).all()


@router.post("/api-keys", response_model=APIKeyCreated, status_code=status.HTTP_201_CREATED)
def create_tenant_api_key(
    payload: APIKeyCreateSchema,
    context: TenantContext = Depends(get_current_tenant_context),
    db: Session = Depends(get_db),
):
    """Generation cryptographique reelle (secrets) ; seul le SHA-256 est persiste.

    La cle complete n'est retournee qu'ici, a la creation. Toute verification
    ulterieure se fait en rehashant la cle fournie par le client.
    """
    raw = secrets.token_urlsafe(32)
    prefix = raw[:16]
    key_hash = hashlib.sha256(raw.encode("utf-8")).hexdigest()
    record = TenantAPIKey(
        organization_id=context.organization_id,
        created_by=getattr(context.user, "id", None),
        key_name=payload.key_name,
        key_prefix=prefix,
        key_hash=key_hash,
        allowed_ips=payload.allowed_ips,
        active=True,
    )
    db.add(record)
    db.commit()
    db.refresh(record)
    return APIKeyCreated(
        id=record.id,
        key_name=record.key_name,
        key_prefix=record.key_prefix,
        allowed_ips=record.allowed_ips,
        active=record.active,
        cle_secrete=raw,
    )
