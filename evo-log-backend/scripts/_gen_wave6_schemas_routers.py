# -*- coding: utf-8 -*-
"""Generateur de schemas + routeurs Pydantic/FastAPI pour modules expansion wave 6.

Vague 6 :
  - maintenance-industrielle  (25 entites)  → /api/v1/maintenance-industrielle
  - tracabilite-bout-en-bout  (19 entites)  → /api/v1/tracabilite

NB : les tables trace_events / trace_audit_logs / trace_access_security /
trace_anti_tampering sont logiquement append-only (hash chain Merkle). Le
DELETE emis ici est un soft-delete (is_active=False) qui reste detectable
par le controle d'integrite de chaine.
"""
import sys
from pathlib import Path

sys.path.insert(0, ".")

from sqlalchemy import String, Integer, BigInteger, Boolean, Date, DateTime, Text, Float, Numeric  # noqa: E402
from sqlalchemy import Enum as SAEnum  # noqa: E402

from app.models import maintenance_deep as mnt  # noqa: E402
from app.models import tracabilite_deep as trc  # noqa: E402


MODULES = [
    # slug, perm_module, dir_frontend, tag_label, models, entity_paths
    ("maintenance", "maintindustrielle", "maintenance-industrielle", "maintenance-industrielle",
     [mnt.TechnicalAsset, mnt.AssetComponent, mnt.SparePartCatalog, mnt.BillOfMaterial,
      mnt.SerializedPart, mnt.PartInventory, mnt.PartMovement, mnt.FailureMode,
      mnt.MaintenancePlan, mnt.MaintenanceTask, mnt.WorkOrder, mnt.AssetFailure,
      mnt.WorkOrderPart, mnt.WorkOrderLabour, mnt.WorkOrderTool, mnt.RootCauseAnalysis,
      mnt.OverhaulCampaign, mnt.LubricationSchedule, mnt.ConditionReading, mnt.Sensor,
      mnt.PredictiveModel, mnt.ReliabilityKpi, mnt.RegulatoryInspection,
      mnt.MaintenanceBudget, mnt.MaintenanceVendor],
     {
        mnt.TechnicalAsset:        ("assets", "Actif technique"),
        mnt.AssetComponent:        ("components", "Composant"),
        mnt.SparePartCatalog:      ("spare-parts", "Piece de rechange"),
        mnt.BillOfMaterial:        ("bill-of-material", "Nomenclature BOM"),
        mnt.SerializedPart:        ("serialized-parts", "Piece serialisee (singleton)"),
        mnt.PartInventory:         ("inventory", "Stock piece"),
        mnt.PartMovement:          ("movements", "Mouvement piece"),
        mnt.FailureMode:           ("failure-modes", "Mode de defaillance (FMEA)"),
        mnt.MaintenancePlan:       ("plans", "Plan de maintenance"),
        mnt.MaintenanceTask:       ("tasks", "Tache de maintenance"),
        mnt.WorkOrder:             ("work-orders", "Ordre de travail"),
        mnt.AssetFailure:          ("asset-failures", "Panne actif"),
        mnt.WorkOrderPart:         ("wo-parts", "OT - pieces"),
        mnt.WorkOrderLabour:       ("wo-labours", "OT - main d'oeuvre"),
        mnt.WorkOrderTool:         ("wo-tools", "OT - outillage"),
        mnt.RootCauseAnalysis:     ("root-causes", "Analyse cause racine"),
        mnt.OverhaulCampaign:      ("overhauls", "Campagne revision"),
        mnt.LubricationSchedule:   ("lubrication", "Plainte graissage"),
        mnt.ConditionReading:      ("condition-readings", "Releu condition"),
        mnt.Sensor:                ("sensors", "Capteur IoT"),
        mnt.PredictiveModel:       ("predictive-models", "Modele predictif"),
        mnt.ReliabilityKpi:        ("reliability-kpis", "KPI fiabilite"),
        mnt.RegulatoryInspection:  ("inspections", "Inspection reglementaire"),
        mnt.MaintenanceBudget:     ("budgets", "Budget maintenance"),
        mnt.MaintenanceVendor:     ("vendors", "Prestataire maintenance"),
     }),
    ("tracabilite", "tracabilite", "tracabilite", "tracabilite-bout-en-bout",
     [trc.TraceabilityEvent, trc.ChainOfCustodyTransfer, trc.BatchGenealogy,
      trc.SerialGenealogy, trc.DocumentHash, trc.GeolocationTrace, trc.ColdChainTrace,
      trc.IncidentChainOfCommand, trc.RegulatoryTraceExport, trc.ImmutableAuditLog,
      trc.TimestampAuthority, trc.WitnessSignature, trc.IntegrityMerkleProof,
      trc.ContainerSeal, trc.CargoHandoff, trc.AccessSecurityLog, trc.ConsentGrant,
      trc.AntiTamperingEvent, trc.RetentionPolicy],
     {
        trc.TraceabilityEvent:         ("events", "Evenement tracabilite"),
        trc.ChainOfCustodyTransfer:    ("custody-transfers", "Chaine de custody"),
        trc.BatchGenealogy:            ("batch-genealogy", "Genealogie lot"),
        trc.SerialGenealogy:           ("serial-genealogy", "Genealogie numero serial"),
        trc.DocumentHash:              ("document-hashes", "Empreinte document"),
        trc.GeolocationTrace:          ("geolocations", "Trace geolocalisation"),
        trc.ColdChainTrace:            ("cold-chain", "Chaine du froid"),
        trc.IncidentChainOfCommand:    ("incidents", "Post commandement incident"),
        trc.RegulatoryTraceExport:     ("regulatory-exports", "Export reglementaire"),
        trc.ImmutableAuditLog:         ("audit-logs", "Journal audit inalterable"),
        trc.TimestampAuthority:        ("timestamps", "Horodatage qualifie"),
        trc.WitnessSignature:          ("signatures", "Signature / temoin"),
        trc.IntegrityMerkleProof:      ("merkle-proofs", "Preuve Merkle"),
        trc.ContainerSeal:             ("seals", "Sceau conteneur ISO 17712"),
        trc.CargoHandoff:              ("cargo-handoffs", "Transfert cargo multimodal"),
        trc.AccessSecurityLog:         ("access-logs", "Journal securite acces"),
        trc.ConsentGrant:              ("consents", "Consentement RGPD / loi Cameroun"),
        trc.AntiTamperingEvent:        ("anti-tampering", "Evenement anti-falsification"),
        trc.RetentionPolicy:           ("retention-policies", "Politique conservation"),
     }),
]


def _pyd_type(col_type):
    if isinstance(col_type, SAEnum):
        return "str"
    if isinstance(col_type, (String, Text)):
        return "str"
    if isinstance(col_type, (Integer, BigInteger)):
        return "int"
    if isinstance(col_type, Boolean):
        return "bool"
    if isinstance(col_type, Date):
        return "date"
    if isinstance(col_type, DateTime):
        return "datetime"
    if isinstance(col_type, (Float, Numeric)):
        return "float"
    return "str"


def _fk_columns(model):
    from sqlalchemy import ForeignKeyConstraint
    out = set()
    for fk in model.__table__.foreign_key_constraints:
        for c in fk.columns:
            if c.name != "company_id":
                out.add(c.name)
    return out


def _unique_fields(model):
    """Cle metier unique (hors company_id) utilise pour le controle de doublon.

    Retourne la liste complete des colonnes non-NULL de la contrainte unique
    (minus company_id). On exclut les colonnes FK cross-tables (ancre parente)
    qui ne sont pas verifiables en scope tenant seul quand elles sont alone ;
    mais on les garde dans la cle compositée quand elles coexistent avec une
    colonne non-FK, ce qui evite de choisir un FK nu comme cle unique.
    """
    from sqlalchemy import UniqueConstraint as UC
    fkcols = _fk_columns(model)
    for constr in model.__table__.constraints:
        if isinstance(constr, UC):
            cols = [c for c in constr.columns if c.name != "company_id"]
            nonnull = [c for c in cols if not c.nullable]
            if not nonnull:
                nonnull = cols
            names = [c.name for c in nonnull]
            if not names:
                continue
            # Preferer la cle complete sans FK cross-table si une colonne non-FK existe.
            nonfk = [c.name for c in nonnull if c.name not in fkcols]
            if nonfk:
                return nonfk
            return names
    return []


def gen_schema_file(models) -> str:
    lines = [
        '"""Schemas Pydantic auto-genere (expansion wave 6)."""',
        "from pydantic import BaseModel",
        "from typing import Optional",
        "from datetime import datetime, date",
        "",
        "",
    ]
    for m in models:
        name = m.__name__
        table = m.__table__
        cols = [c for c in table.columns
                if c.name not in ("id", "company_id", "created_at", "updated_at", "is_active")]
        lines.append(f"class {name}Create(BaseModel):")
        for c in cols:
            t = _pyd_type(c.type)
            if c.nullable:
                lines.append(f"    {c.name}: Optional[{t}] = None")
            else:
                lines.append(f"    {c.name}: {t}")
        lines.append("")
        lines.append("")
        lines.append(f"class {name}Update(BaseModel):")
        for c in cols:
            t = _pyd_type(c.type)
            lines.append(f"    {c.name}: Optional[{t}] = None")
        lines.append("    is_active: Optional[bool] = None")
        lines.append("")
        lines.append("")
        lines.append(f"class {name}Out(BaseModel):")
        lines.append("    id: int")
        lines.append("    company_id: int")
        for c in cols:
            t = _pyd_type(c.type)
            if c.nullable:
                lines.append(f"    {c.name}: Optional[{t}] = None")
            else:
                lines.append(f"    {c.name}: {t}")
        lines.append("    is_active: Optional[bool] = None")
        lines.append("    created_at: Optional[datetime] = None")
        lines.append("    updated_at: Optional[datetime] = None")
        lines.append('    model_config = {"from_attributes": True}')
        lines.append("")
        lines.append("")
    return "\n".join(lines)


def gen_router_file(slug: str, perm_module: str, tag_label: str, models, paths_map) -> str:
    lines = []
    lines.append(f'"""Routeur CRUD genere pour {tag_label} (expansion wave 6)."""')
    lines.append("from fastapi import APIRouter, Depends, HTTPException, status")
    lines.append("from sqlalchemy.exc import IntegrityError")
    lines.append("from sqlalchemy.orm import Session")
    lines.append("from typing import Optional, List")
    lines.append("")
    lines.append("from app.core.database import get_db")
    lines.append("from app.core.permissions import require_perm")
    lines.append("from app.models.user import User")
    lines.append(f"from app.models.{slug}_deep import (")
    for m in models:
        lines.append(f"    {m.__name__},")
    lines.append(")")
    lines.append(f"from app.schemas.{slug}_deep import (")
    for m in models:
        n = m.__name__
        lines.append(f"    {n}Create, {n}Update, {n}Out,")
    lines.append(")")
    lines.append("")
    lines.append(f'router = APIRouter(tags=["{tag_label} (expansion)"])')
    lines.append("")
    lines.append("")
    lines.extend([
        "# --- Helpers generiques ---------------------------------------------------",
        "",
        "def _get_or_404(db: Session, model, ident: int, label: str):",
        "    row = db.query(model).filter(model.id == ident).first()",
        "    if not row:",
        '        raise HTTPException(status_code=404, detail=f"{label} introuvable (id={ident})")',
        "    return row",
        "",
        "",
        "def _check_unique(db: Session, model, fields, data: dict, label: str, company_id: int, exclude_id=None):",
        "    if not fields:",
        "        return",
        "    if any(data.get(f) is None for f in fields):",
        "        return",
        "    q = db.query(model).filter(model.company_id == company_id)",
        "    for f in fields:",
        "        q = q.filter(getattr(model, f) == data.get(f))",
        "    if exclude_id is not None:",
        "        q = q.filter(model.id != exclude_id)",
        "    if q.first():",
        "        human = ' / '.join(str(data.get(f)) for f in fields)",
        "        raise HTTPException(",
        "            status_code=status.HTTP_409_CONFLICT,",
        "            detail=f\"{label} '{human}' existe deja dans votre organisation.\",",
        "        )",
        "",
        "",
        "def _commit(db: Session, obj, label: str):",
        "    db.add(obj)",
        "    try:",
        "        db.commit()",
        "    except IntegrityError as exc:",
        "        db.rollback()",
        "        msg = str(getattr(exc, 'orig', exc))",
        "        if 'FOREIGN KEY' in msg.upper() or 'foreign key' in msg:",
        "            raise HTTPException(422, detail=f\"References invalides : un enregistrement lie ({label}) n'existe pas ou appartient a une autre organisation.\")",
        "        raise HTTPException(409, detail=f\"Conflit d'integrite lors de l'enregistrement de {label}.\")",
        "    db.refresh(obj)",
        "    return obj",
        "",
        "",
        "def _scoped_list(db, model, company_id, filters=None):",
        "    q = db.query(model).filter(model.company_id == company_id)",
        "    if hasattr(model, 'is_active'):",
        "        q = q.filter(model.is_active.is_(True))",
        "    if filters:",
        "        for key, val in filters.items():",
        "            if val is not None and hasattr(model, key):",
        "                q = q.filter(getattr(model, key) == val)",
        "    return q.order_by(model.id.desc()).all()",
        "",
        "",
        "def _apply(payload: dict, obj):",
        "    for key, value in payload.items():",
        "        setattr(obj, key, value)",
        "",
        "",
        "def _company_id(user: User) -> int:",
        "    if not user.company_id:",
        '        raise HTTPException(status_code=400, detail="Votre compte n\'est rattache a aucune organisation.")',
        "    return user.company_id",
        "",
        "",
        "# --- Nomenclatures ---------------------------------------------------------",
        "",
        f'@router.get("/nomenclatures", summary="Vocabulaire metier {tag_label}")',
        f'def nomenclatures(user: User = Depends(require_perm("{perm_module}.nomenclature.read"))):',
        f"    from app.models import {slug}_deep as _md",
        "    import enum as _pyenum",
        "    out = {}",
        "    for name in dir(_md):",
        "        obj = getattr(_md, name)",
        "        if isinstance(obj, type) and issubclass(obj, _pyenum.Enum) and obj is not _pyenum.Enum:",
        '            out[name.lower()] = [{"code": m.name, "valeur": m.value} for m in obj]',
        "    return out",
        "",
        "",
    ])
    for m in models:
        n = m.__name__
        path, label = paths_map[m]
        subperm = path.replace("-", "_")
        fn = subperm.replace("-", "_")
        unique_fields = _unique_fields(m)
        lines.append(f"# --- {label} ---------------------------------------------------------")
        lines.append("")
        lines.append(f'@router.get("/{path}", response_model=List[{n}Out])')
        if unique_fields and "statut" in [c.name for c in m.__table__.columns]:
            lines.append(f"def list_{fn}(statut: Optional[str] = None, db: Session = Depends(get_db),")
            lines.append(f'    user: User = Depends(require_perm("{perm_module}.{subperm}.read")),')
            lines.append("):")
            lines.append("    cid = _company_id(user)")
            lines.append(f"    return _scoped_list(db, {n}, cid, {{'statut': statut}})")
        else:
            lines.append(f"def list_{fn}(db: Session = Depends(get_db),")
            lines.append(f'    user: User = Depends(require_perm("{perm_module}.{subperm}.read")),')
            lines.append("):")
            lines.append("    cid = _company_id(user)")
            lines.append(f"    return _scoped_list(db, {n}, cid)")
        lines.append("")
        lines.append("")
        lines.append(f'@router.post("/{path}", response_model={n}Out, status_code=201)')
        lines.append(f"def create_{fn}(")
        lines.append(f"    payload: {n}Create,")
        lines.append("    db: Session = Depends(get_db),")
        lines.append(f'    user: User = Depends(require_perm("{perm_module}.{subperm}.create")),')
        lines.append("):")
        lines.append("    cid = _company_id(user)")
        lines.append("    data = payload.model_dump(exclude_unset=True)")
        if unique_fields:
            lines.append(f'    _check_unique(db, {n}, {unique_fields!r}, data, "{label}", cid)')
        lines.append(f"    obj = {n}(company_id=cid)")
        lines.append("    _apply(data, obj)")
        lines.append(f'    return _commit(db, obj, "{label}")')
        lines.append("")
        lines.append("")
        lines.append(f'@router.put("/{path}/{{ident}}", response_model={n}Out)')
        lines.append(f"def update_{fn}(")
        lines.append("    ident: int,")
        lines.append(f"    payload: {n}Update,")
        lines.append("    db: Session = Depends(get_db),")
        lines.append(f'    user: User = Depends(require_perm("{perm_module}.{subperm}.modify")),')
        lines.append("):")
        lines.append("    cid = _company_id(user)")
        lines.append(f'    obj = _get_or_404(db, {n}, ident, "{label}")')
        lines.append("    if obj.company_id != cid:")
        lines.append('        raise HTTPException(403, "Acces refuse.")')
        lines.append("    upd = payload.model_dump(exclude_unset=True)")
        if unique_fields:
            lines.append(f"    _chk = {{f: upd.get(f, getattr(obj, f)) for f in {unique_fields!r}}}")
            lines.append(f'    _check_unique(db, {n}, {unique_fields!r}, _chk, "{label}", cid, exclude_id=ident)')
        lines.append("    _apply(upd, obj)")
        lines.append("    try:")
        lines.append("        db.commit()")
        lines.append("    except IntegrityError as exc:")
        lines.append("        db.rollback()")
        lines.append('        raise HTTPException(422, detail="Reference invalide ou conflit d\'integrite.")')
        lines.append("    db.refresh(obj)")
        lines.append("    return obj")
        lines.append("")
        lines.append("")
        lines.append(f'@router.delete("/{path}/{{ident}}", response_model={n}Out)')
        lines.append(f"def delete_{fn}(")
        lines.append("    ident: int,")
        lines.append("    db: Session = Depends(get_db),")
        lines.append(f'    user: User = Depends(require_perm("{perm_module}.{subperm}.modify")),')
        lines.append("):")
        lines.append("    cid = _company_id(user)")
        lines.append(f'    obj = _get_or_404(db, {n}, ident, "{label}")')
        lines.append("    if obj.company_id != cid:")
        lines.append('        raise HTTPException(403, "Acces refuse.")')
        lines.append("    obj.is_active = False")
        lines.append("    db.commit()")
        lines.append("    db.refresh(obj)")
        lines.append("    return obj")
        lines.append("")
        lines.append("")
    return "\n".join(lines)


def main():
    sch_dir = Path("app/schemas")
    rt_dir = Path("app/routers/v1")
    for slug, perm_module, dir_label, tag_label, models, paths_map in MODULES:
        spath = sch_dir / f"{slug}_deep.py"
        spath.write_text(gen_schema_file(models), encoding="utf-8")
        rpath = rt_dir / f"{slug}_deep.py"
        rpath.write_text(gen_router_file(slug, perm_module, tag_label, models, paths_map), encoding="utf-8")
        print("OK", slug, "->", spath.name, rpath.name)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
