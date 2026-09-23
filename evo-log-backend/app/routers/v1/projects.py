from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from pydantic import BaseModel, Field
from typing import List, Optional
from datetime import datetime

from app.database import get_db
from app.utils.tenant import get_current_tenant_context, TenantContext, require_module_access
from app.core.not_implemented import not_implemented

router = APIRouter()

class ProjectSchema(BaseModel):
    title: str = Field(..., example="Extension Entrepôt Zone Industrielle Bonabéri")
    code: str = Field(..., example="PRJ-BNB-01")
    budget_xaf: float = Field(..., example=120000000.0)
    start_date: str = Field(..., example="2026-08-15")
    end_date: str = Field(..., example="2026-12-31")
    manager_name: str = Field(..., example="Ing. Thomas Eboa")

@router.get("/", dependencies=[Depends(require_module_access("transport"))])
def list_projects(context: TenantContext = Depends(get_current_tenant_context)):
    """Projets logistiques : 501 (projet invente, aucune table de projet)."""
    not_implemented(
        "Listage des projets d'infrastructure/logistique",
        "une table de projets persistante avec budget/depuis/agrege reel "
        "(le projet retourne etait fabrique)",
    )

@router.post("/", status_code=status.HTTP_201_CREATED, dependencies=[Depends(require_module_access("transport"))])
def create_project(payload: ProjectSchema, context: TenantContext = Depends(get_current_tenant_context)):
    """Creation de projet : 501 (ne persistait rien, faux succes)."""
    not_implemented(
        "Creation d'un projet",
        "un modele/une table de projet pour reellement enregistrer la fiche "
        "(l'ID retourne etait un simple horodatage)",
    )
