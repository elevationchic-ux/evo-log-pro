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
def ingest_iot_telemetry(payload: TelemetryPayloadSchema, db: Session = Depends(get_db)):
    """Ingest IoT sensor telemetry for fuel, GPS position, and cold-chain temperature."""
    return {
        "status": "ingested",
        "device_id": payload.device_id,
        "timestamp": datetime.utcnow().isoformat(),
        "alerts_triggered": []
    }

@router.get("/live-fleet-map", dependencies=[Depends(require_module_access("parc"))])
def get_live_fleet_telemetry(context: TenantContext = Depends(get_current_tenant_context)):
    """Retrieve live GPS coordinates and telemetry status for active fleet."""
    return {
        "status": "success",
        "organization_id": context.organization_id,
        "active_devices": [
            {
                "device_id": "IOT-GPS-4589",
                "vehicle_immat": "LT-456-XY",
                "driver_name": "Nguema Joseph",
                "latitude": 4.051056,
                "longitude": 9.767869,
                "location_label": "Port Autonome de Douala - Quai 12",
                "fuel_level_liters": 340.5,
                "temperature_celsius": 4.2,
                "speed_kmh": 0.0,
                "engine_status": "IDLING",
                "last_seen": datetime.utcnow().isoformat()
            },
            {
                "device_id": "IOT-GPS-9912",
                "vehicle_immat": "LT-789-BZ",
                "driver_name": "Kamga Pierre",
                "latitude": 3.866667,
                "longitude": 11.516667,
                "location_label": "Entrée Douane Yaoundé-Nsam",
                "fuel_level_liters": 180.0,
                "temperature_celsius": None,
                "speed_kmh": 45.0,
                "engine_status": "MOVING",
                "last_seen": datetime.utcnow().isoformat()
            }
        ]
    }
