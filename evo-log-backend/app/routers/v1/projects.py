from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session
from pydantic import BaseModel, Field
from typing import List, Optional

from app.database import get_db
from app.utils.tenant import get_current_tenant_context, TenantContext, require_module_access
from app.models.advanced_crud import Project

router = APIRouter()


class ProjectSchema(BaseModel):
    title: str = Field(..., example="Extension Entrepôt Zone Industrielle Bonabéri")
    code: str = Field(..., example="PRJ-BNB-01")
    budget_xaf: float = Field(..., example=120000000.0)
    start_date: str = Field(..., example="2026-08-15")
    end_date: str = Field(..., example="2026-12-31")
    manager_name: str = Field(..., example="Ing. Thomas Eboa")
    status: str = Field("PLANIFIE", example="EN_COURS")


class ProjectOut(BaseModel):
    id: int
    code: str
    title: str
    budget_xaf: float
    spent_xaf: float
    start_date: Optional[str]
    end_date: Optional[str]
    manager_name: Optional[str]
    status: str

    class Config:
        from_attributes = True


def _scope(context: TenantContext, query):
    if context.organization_id is not None:
        return query.filter(Project.organization_id == context.organization_id)
    return query


@router.get("/", response_model=List[ProjectOut], dependencies=[Depends(require_module_access("transport"))])
def list_projects(
    context: TenantContext = Depends(get_current_tenant_context),
    db: Session = Depends(get_db),
):
    """Projets logistiques reellement persistes, budget engage agregre depuis la base."""
    return _scope(context, db.query(Project)).order_by(Project.created_at.desc()).all()


@router.post("/", response_model=ProjectOut, status_code=status.HTTP_201_CREATED,
             dependencies=[Depends(require_module_access("transport"))])
def create_project(
    payload: ProjectSchema,
    context: TenantContext = Depends(get_current_tenant_context),
    db: Session = Depends(get_db),
):
    """Creation de projet : la fiche est reellement enregistree en base."""
    project = Project(organization_id=context.organization_id, **payload.model_dump())
    db.add(project)
    db.commit()
    db.refresh(project)
    return project
