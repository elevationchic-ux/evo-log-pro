"""Pydantic schemas pour les accréditations et les acces partages."""
from datetime import datetime, date
from typing import List, Optional
from pydantic import BaseModel, Field


# ── Accreditation ─────────────────────────────────────────────────────────────
class AccreditationBase(BaseModel):
    libelle: str = Field(..., max_length=150)
    type: str = Field("permission", description="permission | scope")
    permission_code: Optional[str] = None
    perimetre_utilisateurs: List[int] = []
    module: Optional[str] = None
    date_debut: Optional[date] = None
    date_fin: Optional[date] = None
    motif: Optional[str] = None


class AccreditationCreate(AccreditationBase):
    user_id: int
    code: Optional[str] = None
    statut: str = "actif"


class AccreditationUpdate(BaseModel):
    libelle: Optional[str] = None
    permission_code: Optional[str] = None
    perimetre_utilisateurs: Optional[List[int]] = None
    module: Optional[str] = None
    date_debut: Optional[date] = None
    date_fin: Optional[date] = None
    statut: Optional[str] = None
    motif: Optional[str] = None


class AccreditationResponse(AccreditationBase):
    id: int
    user_id: int
    company_id: Optional[int] = None
    code: Optional[str] = None
    statut: str
    octroye_par: Optional[int] = None
    created_at: Optional[datetime] = None

    class Config:
        from_attributes = True


# ── SharedAccess (modules communs par entreprise) ─────────────────────────────
class SharedAccessCreate(BaseModel):
    module_key: str
    libelle: Optional[str] = None
    autorise_tous_utilisateurs: bool = True


class SharedAccessResponse(BaseModel):
    id: int
    company_id: int
    module_key: str
    libelle: Optional[str] = None
    autorise_tous_utilisateurs: bool

    class Config:
        from_attributes = True
