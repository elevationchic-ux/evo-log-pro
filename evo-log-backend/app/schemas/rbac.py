"""Schemas Pydantic pour le système RBAC multi-tenant EVO-LOG SaaS"""
from pydantic import BaseModel, Field, EmailStr
from typing import List, Optional
from datetime import datetime
from enum import Enum


class TenantPlanEnum(str, Enum):
    STARTER = "STARTER"
    PROFESSIONNEL = "PROFESSIONNEL"
    ENTERPRISE = "ENTERPRISE"
    CUSTOM = "CUSTOM"


class UserRoleLevelEnum(str, Enum):
    SUPER_ADMIN = "SUPER_ADMIN"
    ADMIN = "ADMIN"
    MANAGER = "MANAGER"
    SUPERVISEUR = "SUPERVISEUR"
    OPERATEUR = "OPERATEUR"
    CHAUFFEUR = "CHAUFFEUR"
    CLIENT_B2B = "CLIENT_B2B"


# ── Tenant ───────────────────────────────────────────────────────────────────
class TenantCreate(BaseModel):
    code: str = Field(..., min_length=3, max_length=20, description="Code unique du tenant ex: EVOLOGS-CI")
    nom_entreprise: str
    pays: str = "Cameroun"
    ville: Optional[str] = None
    telephone: Optional[str] = None
    email_contact: Optional[str] = None
    plan: TenantPlanEnum = TenantPlanEnum.PROFESSIONNEL
    modules_actives: str = "transport,magasin,finance,comptabilite"
    nb_utilisateurs_max: int = 20


class TenantResponse(BaseModel):
    id: int
    code: str
    nom_entreprise: str
    pays: str
    plan: TenantPlanEnum
    modules_actives: str
    nb_utilisateurs_max: int
    actif: bool
    created_at: datetime

    class Config:
        from_attributes = True


# ── Permission ────────────────────────────────────────────────────────────────
class PermissionResponse(BaseModel):
    id: int
    code: str
    module: str
    action: str
    description: Optional[str] = None

    class Config:
        from_attributes = True


# ── Rôle ─────────────────────────────────────────────────────────────────────
class RoleCreate(BaseModel):
    nom: str
    niveau: UserRoleLevelEnum
    description: Optional[str] = None
    permissions_json: str = "[]"


class RoleResponse(BaseModel):
    id: int
    nom: str
    niveau: UserRoleLevelEnum
    description: Optional[str] = None
    permissions_json: str
    actif: bool

    class Config:
        from_attributes = True


# ── Assignation utilisateur ───────────────────────────────────────────────────
class UserRoleAssignRequest(BaseModel):
    user_id: int
    role_id: int
    tenant_id: int
    modules_restreints: str = "[]"


class UserRoleAssignResponse(BaseModel):
    id: int
    user_id: int
    role_id: int
    tenant_id: int
    actif: bool
    assigned_at: datetime

    class Config:
        from_attributes = True


# ── Permission check ──────────────────────────────────────────────────────────
class PermissionCheckRequest(BaseModel):
    user_id: int
    tenant_id: int
    permission_code: str = Field(..., description="Ex: transport.mission.create")


class PermissionCheckResponse(BaseModel):
    user_id: int
    permission_code: str
    autorise: bool
    niveau_role: Optional[str] = None
    raison: str
