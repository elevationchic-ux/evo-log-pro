"""Extract per-entity unique_field + subpath from wave 6 models."""
import sys, json
sys.path.insert(0, ".")
import app.models  # noqa
from app.models import maintenance_deep as mnt
from app.models import tracabilite_deep as trc
from sqlalchemy import UniqueConstraint


SUBPATHS = {
    mnt.TechnicalAsset: "assets",
    mnt.AssetComponent: "components",
    mnt.SparePartCatalog: "spare-parts",
    mnt.BillOfMaterial: "bill-of-material",
    mnt.SerializedPart: "serialized-parts",
    mnt.PartInventory: "inventory",
    mnt.PartMovement: "movements",
    mnt.FailureMode: "failure-modes",
    mnt.MaintenancePlan: "plans",
    mnt.MaintenanceTask: "tasks",
    mnt.WorkOrder: "work-orders",
    mnt.AssetFailure: "asset-failures",
    mnt.WorkOrderPart: "wo-parts",
    mnt.WorkOrderLabour: "wo-labours",
    mnt.WorkOrderTool: "wo-tools",
    mnt.RootCauseAnalysis: "root-causes",
    mnt.OverhaulCampaign: "overhauls",
    mnt.LubricationSchedule: "lubrication",
    mnt.ConditionReading: "condition-readings",
    mnt.Sensor: "sensors",
    mnt.PredictiveModel: "predictive-models",
    mnt.ReliabilityKpi: "reliability-kpis",
    mnt.RegulatoryInspection: "inspections",
    mnt.MaintenanceBudget: "budgets",
    mnt.MaintenanceVendor: "vendors",
    trc.TraceabilityEvent: "events",
    trc.ChainOfCustodyTransfer: "custody-transfers",
    trc.BatchGenealogy: "batch-genealogy",
    trc.SerialGenealogy: "serial-genealogy",
    trc.DocumentHash: "document-hashes",
    trc.GeolocationTrace: "geolocations",
    trc.ColdChainTrace: "cold-chain",
    trc.IncidentChainOfCommand: "incidents",
    trc.RegulatoryTraceExport: "regulatory-exports",
    trc.ImmutableAuditLog: "audit-logs",
    trc.TimestampAuthority: "timestamps",
    trc.WitnessSignature: "signatures",
    trc.IntegrityMerkleProof: "merkle-proofs",
    trc.ContainerSeal: "seals",
    trc.CargoHandoff: "cargo-handoffs",
    trc.AccessSecurityLog: "access-logs",
    trc.ConsentGrant: "consents",
    trc.AntiTamperingEvent: "anti-tampering",
    trc.RetentionPolicy: "retention-policies",
}


def ufield(m):
    for c in m.__table__.constraints:
        if isinstance(c, UniqueConstraint):
            cols = [x.name for x in c.columns]
            if "company_id" in cols:
                others = [x for x in cols if x != "company_id"]
                if others:
                    return others[0]
    return None


rows = []
for m, sp in SUBPATHS.items():
    prefix = "/api/v1/maintenance-industrielle" if m.__module__.endswith("maintenance_deep") else "/api/v1/tracabilite"
    uf = ufield(m)
    rows.append((prefix, sp, uf or "reference", m.__name__))
    print(f"{prefix:35s} {sp:22s} {uf or '(none)':22s} {m.__name__}")

with open("smoke_wave6_targets.json", "w", encoding="utf-8") as f:
    json.dump([list(r) for r in rows], f, indent=2)
