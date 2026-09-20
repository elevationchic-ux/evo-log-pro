from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from pydantic import BaseModel, Field
from typing import List, Optional
from datetime import datetime

from app.database import get_db
from app.utils.tenant import get_current_tenant_context, TenantContext, require_module_access

router = APIRouter()

class TelemetryPayloadSchema(BaseModel):
    device_id: str = Field(..., example="IOT-GPS-4589")
    vehicle_immat: str = Field(..., example="LT-456-XY")
    latitude: float = Field(..., example=4.051056)
    longitude: float = Field(..., example=9.767869)
    fuel_level_liters: float = Field(..., example=340.5)
    temperature_celsius: Optional[float] = Field(None, example=4.2)
    speed_kmh: float = Field(..., example=62.5)

@router.post("/telemetry", status_code=status.HTTP_201_CREATED)
def ingest_iot_telemetry(payload: TelemetryPayloadSchema, context: TenantContext = Depends(get_current_tenant_context)):
    """Ingest IoT sensor telemetry for fuel, GPS position, and cold-chain temperature."""
    raise HTTPException(
        status_code=status.HTTP_501_NOT_IMPLEMENTED,
        detail="La persistance de télémétrie IoT n'est pas encore configurée pour ce tenant.",
    )

@router.get("/live-fleet-map", dependencies=[Depends(require_module_access("parc"))])
def get_live_fleet_telemetry(context: TenantContext = Depends(get_current_tenant_context)):
    """Retrieve live GPS coordinates and telemetry status for active fleet."""
    return {
        "status": "unavailable",
        "organization_id": context.organization_id,
        "active_devices": [],
        "message": "Aucune télémétrie persistante n'est configurée pour ce tenant.",
    }
