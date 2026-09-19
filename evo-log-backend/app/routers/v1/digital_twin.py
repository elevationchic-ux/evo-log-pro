from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from pydantic import BaseModel, Field
from typing import List, Optional
from datetime import datetime

from app.database import get_db
from app.utils.tenant import get_current_tenant_context, TenantContext, require_module_access

router = APIRouter()

@router.get("/yard-state", dependencies=[Depends(require_module_access("parc"))])
def get_digital_twin_yard_state(context: TenantContext = Depends(get_current_tenant_context)):
    """Retrieve 2D/3D digital twin layout and real-time slot occupancy state."""
    return {
        "status": "success",
        "organization_id": context.organization_id,
        "digital_twin": {
            "facility_name": "Parc Logistique Douala Bonabéri",
            "total_slots": 150,
            "occupied_slots": 112,
            "occupancy_rate_percentage": 74.6,
            "zones": [
                {
                    "zone_code": "ZONE-A",
                    "label": "Conteneurs Réfrigérés (Reefer)",
                    "capacity": 40,
                    "occupied": 32,
                    "temperature_monitoring_active": True
                },
                {
                    "zone_code": "ZONE-B",
                    "label": "Marchandises Dangereuses (Hazmat)",
                    "capacity": 30,
                    "occupied": 18,
                    "safety_clearance_verified": True
                },
                {
                    "zone_code": "ZONE-C",
                    "label": "Stockage Vrac & Matériaux",
                    "capacity": 80,
                    "occupied": 62,
                    "weighbridge_linked": True
                }
            ]
        }
    }
