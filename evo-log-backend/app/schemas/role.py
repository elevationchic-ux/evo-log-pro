"""Pydantic schemas for Role management - Hierarchical RBAC"""
from datetime import datetime
from typing import Optional, List
from pydantic import BaseModel


class RoleBase(BaseModel):
    name: str
    description: str
    level: int
    modules_allowed: List[str]


class RoleCreate(RoleBase):
    company_id: Optional[int] = None


class RoleUpdate(BaseModel):
    description: Optional[str] = None
    modules_allowed: Optional[List[str]] = None
    is_active: Optional[bool] = None


class RoleResponse(RoleBase):
    id: int
    company_id: Optional[int] = None
    is_active: bool
    is_system: bool
    created_at: datetime
    updated_at: Optional[datetime] = None
    
    class Config:
        from_attributes = True


class UserRoleAssignment(BaseModel):
    user_id: int
    role_id: int


class UserWithRoles(BaseModel):
    id: int
    username: str
    email: str
    full_name: Optional[str] = None
    role_level: int
    company_id: Optional[int] = None
    department_id: Optional[int] = None
    roles: List[RoleResponse]
