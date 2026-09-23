import inspect

import app.services.maintenance_gmao_service as gsvc
import app.services.transport_international_service as tsvc

print("### maintenance_gmao_service")
for cn in ["OrdreMaintenanceService", "EquipementGMAOService", "PlanMaintenanceService", "CalibrationService"]:
    c = getattr(gsvc, cn, None)
    if not c:
        print(cn, "MISSING")
        continue
    print("==", cn)
    for m, f in inspect.getmembers(c, predicate=inspect.isfunction):
        if not m.startswith("_"):
            print("   ", m, inspect.signature(f))

print("### transport_international_service")
for cn in ["OrdreTransportService", "CarnetTIRService", "CMRService", "ScelleRoutierService", "PositionGPSService"]:
    c = getattr(tsvc, cn, None)
    if not c:
        print(cn, "MISSING")
        continue
    print("==", cn)
    for m, f in inspect.getmembers(c, predicate=inspect.isfunction):
        if not m.startswith("_"):
            print("   ", m, inspect.signature(f))

print("### model defaults")
from app.models.maintenance_gmao import OrdreMaintenance, EquipementGMAO, PlanMaintenance, Calibration
for M in (OrdreMaintenance, EquipementGMAO, PlanMaintenance, Calibration):
    print(M.__name__, [(c.name, c.default.arg if c.default and c.default.is_scalar else None) for c in M.__table__.columns if c.name in ("statut", "priorite", "type_maintenance", "actif", "frequence", "resultat", "mtbf", "type_equipement", "code", "code_equipement", "numero_ordre", "numero_calibration", "numero_plan")])
from app.models.transport_international import OrdreTransport, CarnetTIR, CMR, ScelleRoutier, PositionGPS
for M in (OrdreTransport, CarnetTIR, CMR, ScelleRoutier, PositionGPS):
    print(M.__name__, [c.name for c in M.__table__.columns])
