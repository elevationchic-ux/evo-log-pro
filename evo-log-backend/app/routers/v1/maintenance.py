"""
Maintenance router - manages equipment, vehicle maintenance, spare parts, and telematics
"""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import datetime

from app.core.database import get_db
from app.services.maintenance_gmao_avance_service import (
    MaintenancePreventiveService, AnalyticsMaintenanceService,
    GestionPiecesRechangeService, CarnetEntretienNumeriqueService,
    TelematicsOBD2IoTService
)

router = APIRouter()


@router.get("")
@router.get("/")
async def get_maintenances(skip: int = 0, limit: int = 100):
    """Get active maintenance work orders and summary"""
    return [
        {
            "id": 1,
            "ordre_id": "OT-2026-0042",
            "vehicule": "LT-TR-4021 (Mercedes Actros 6x4)",
            "type_intervention": "PREVENTIF",
            "statut": "EN_COURS",
            "priorite": "HAUTE",
            "technicien": "Chef d'équipe Mbida",
            "date_creation": "2026-03-10T08:30:00",
            "description": "Révision périodique 280 000 km + contrôle freins et filtration",
            "cout_estime_xaf": 385000
        },
        {
            "id": 2,
            "ordre_id": "OT-2026-0043",
            "vehicule": "RS-KALMAR-02 (Reachstacker Quai)",
            "type_intervention": "CURATIF",
            "statut": "ATTENTE_PIECES",
            "priorite": "URGENT_PORTUAIRE",
            "technicien": "Tech. Levage Ewane",
            "date_creation": "2026-03-11T11:15:00",
            "description": "Fuite vérin de levage télescopique droit",
            "cout_estime_xaf": 850000
        },
        {
            "id": 3,
            "ordre_id": "OT-2026-0044",
            "vehicule": "LT-TR-8812 (Plateau 40')",
            "type_intervention": "REGLEMENTAIRE",
            "statut": "TERMINE",
            "priorite": "NORMALE",
            "technicien": "Atelier Central Bassa",
            "date_creation": "2026-03-09T09:00:00",
            "description": "Visite technique annuelle CEMAC et contrôle CPA levage",
            "cout_estime_xaf": 125000
        }
    ]


@router.post("/ordres")
async def creer_ordre_travail(payload: dict):
    """Create a new maintenance work order"""
    ordre_id = f"OT-{datetime.now().strftime('%Y%m%d%H%M')}"
    return {
        "id": 4,
        "ordre_id": ordre_id,
        "vehicule": payload.get("vehicule", "LT-TR-4021"),
        "type_intervention": payload.get("type_intervention", "PREVENTIF"),
        "statut": "PLANIFIE",
        "description": payload.get("description", "Intervention programmée"),
        "date_creation": datetime.now().isoformat()
    }


# ============ GESTION PIECES DE RECHANGE & DESTOCKAGE WMS ============
@router.post("/destockage-pieces")
async def destocker_pieces_intervention(payload: dict):
    """Consume spare parts directly onto work order from WMS warehouse"""
    ordre_id = payload.get("ordre_id", "OT-2026-0042")
    pieces = payload.get("pieces", [
        {"article_code": "PDR-FLTR-GASOIL", "designation": "Filtre Gasoil Actros", "quantite": 2, "prix_unitaire_xaf": 35000},
        {"article_code": "PDR-HUILE-15W40", "designation": "Huile Moteur 15W40 (Bidon 20L)", "quantite": 2, "prix_unitaire_xaf": 65000}
    ])
    return GestionPiecesRechangeService.destocker_pieces_ot(ordre_id, pieces)


# ============ CARNET D'ENTRETIEN NUMERIQUE PASSEPORT ============
@router.get("/carnet-entretien/{vin_chassis}")
async def obtenir_carnet_entretien(vin_chassis: str):
    """Digital maintenance passport and component life history"""
    return CarnetEntretienNumeriqueService.get_carnet_entretien(vin_chassis)


# ============ TÉLÉMATIQUE IOT & CODES DÉFAUTS CAN-BUS OBD2 ============
@router.get("/telematics/obd2/{immatriculation}")
async def diagnostiquer_telematics_obd2(immatriculation: str):
    """Real-time CAN-Bus / OBD2 engine diagnostics and DTC codes"""
    return TelematicsOBD2IoTService.diagnostiquer_defauts_canbus(immatriculation)


# ============ ANALYTICS RELIABILITY MTBF / MTTR & TCO ============
@router.get("/analytics/kpis")
async def obtenir_kpis_maintenance(db: Session = Depends(get_db)):
    """GMAO reliability KPIs: MTBF, MTTR, availability rate"""
    return AnalyticsMaintenanceService.calculer_mtbf_mttr(db, vehicule_id=1, periode_mois=12)