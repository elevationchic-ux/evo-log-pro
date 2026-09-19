from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from pydantic import BaseModel, Field
from typing import List, Optional
from datetime import datetime

from app.database import get_db
from app.utils.tenant import get_current_tenant_context, TenantContext, require_module_access

router = APIRouter()

class ProjectSchema(BaseModel):
    title: str = Field(..., example="Extension Entrepôt Zone Industrielle Bonabéri")
    code: str = Field(..., example="PRJ-BNB-01")
    budget_xaf: float = Field(..., example=120000000.0)
    start_date: str = Field(..., example="2026-08-15")
    end_date: str = Field(..., example="2026-12-31")
    manager_name: str = Field(..., example="Ing. Thomas Eboa")

@router.get("/projects", dependencies=[Depends(require_module_access("transport"))])
def list_projects(context: TenantContext = Depends(get_current_tenant_context)):
    """List non-transport logistics and infrastructure projects."""
    return {
        "status": "success",
        "projects": [
            {
                "id": "PRJ-001",
                "code": "PRJ-BNB-01",
                "title": "Extension Entrepôt Zone Industrielle Bonabéri",
                "budget_xaf": 120000000.0,
                "spent_xaf": 35000000.0,
                "progress_percentage": 30,
                "status": "IN_PROGRESS",
                "manager_name": "Ing. Thomas Eboa"
            }
        ]
    }

@router.post("/projects", status_code=status.HTTP_201_CREATED, dependencies=[Depends(require_module_access("transport"))])
def create_project(payload: ProjectSchema, context: TenantContext = Depends(get_current_tenant_context)):
    return {
        "status": "success",
        "message": "Project initialized successfully!",
        "project": {
            "id": f"PRJ-00{datetime.utcnow().strftime('%S')}",
            "organization_id": context.organization_id,
            **payload.dict(),
            "spent_xaf": 0.0,
            "progress_percentage": 0,
            "status": "PLANNED"
        }
    }
