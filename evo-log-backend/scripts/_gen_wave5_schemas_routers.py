# -*- coding: utf-8 -*-
"""Generateur de schemas + routeurs Pydantic/FastAPI pour modules expansion wave 5.

Lit les modeles SQLAlchemy, puis emet pour chaque module :
  - app/schemas/<slug>_deep.py  : <Entity>Create/Update/Out
  - app/routers/v1/<slug>_deep.py : 4 CRUD par entite + /nomenclatures

Pattern aligne sur ferroviaire_deep.
"""
import sys
import inspect
from pathlib import Path

sys.path.insert(0, ".")

from sqlalchemy import String, Integer, BigInteger, Boolean, Date, DateTime, Text, Float, Numeric  # noqa: E402

from app.models import courier_deep as cou  # noqa: E402
from app.models import coldchain_deep as cold  # noqa: E402
from app.models import heavylift_deep as heavy  # noqa: E402


MODULES = [
    # slug, perm_module, label, api_prefix_tag, models, entity_paths
    ("courier", "courier", "courier-express", "courier-express",
     [cou.CourierParcel, cou.CourierWaybill, cou.CourierHub, cou.CourierDeliveryZone,
      cou.CourierRoute, cou.CourierCourier, cou.CourierPod, cou.CourierSla,
      cou.CourierLocker, cou.CourierVehicule, cou.CourierTarif, cou.CourierException],
     {cou.CourierParcel: ("parcels", "Colis"),
      cou.CourierWaybill: ("waybills", "Lettre voiture express"),
      cou.CourierHub: ("hubs", "Hub"),
      cou.CourierDeliveryZone: ("delivery-zones", "Zone de livraison"),
      cou.CourierRoute: ("routes", "Tournee"),
      cou.CourierCourier: ("couriers", "Coursier"),
      cou.CourierPod: ("pods", "POD"),
      cou.CourierSla: ("slas", "SLA"),
      cou.CourierLocker: ("lockers", "Consigne"),
      cou.CourierVehicule: ("vehicules", "Vehicule"),
      cou.CourierTarif: ("tarifs", "Tarif"),
      cou.CourierException: ("exceptions", "Exception")}),
    ("coldchain", "coldchain", "chaine-froid", "chaine-froid",
     [cold.ColdChainChamber, cold.ColdChainReefer, cold.ColdChainLogger, cold.ColdChainProduct,
      cold.ColdChainExcursion, cold.ColdChainVaccinBatch, cold.ColdChainHaccpRecord,
      cold.ColdChainDefrostCycle, cold.ColdChainEnergyMeter, cold.ColdChainTransportLeg],
     {cold.ColdChainChamber: ("chambers", "Chambre froide"),
      cold.ColdChainReefer: ("reefers", "Reefer"),
      cold.ColdChainLogger: ("loggers", "Logger temperature"),
      cold.ColdChainProduct: ("products", "Produit"),
      cold.ColdChainExcursion: ("excursions", "Excursion"),
      cold.ColdChainVaccinBatch: ("vaccin-batches", "Lot vaccin"),
      cold.ColdChainHaccpRecord: ("haccp-records", "Enregistrement HACCP"),
      cold.ColdChainDefrostCycle: ("defrost-cycles", "Cycle degivrage"),
      cold.ColdChainEnergyMeter: ("energy-meters", "Compteur energie"),
      cold.ColdChainTransportLeg: ("transport-legs", "Leg transport")}),
    ("heavylift", "heavylift", "convoi-exceptionnel", "convoi-exceptionnel",
     [heavy.HeavyLiftProject, heavy.HeavyLiftCrane, heavy.HeavyLiftModularTrailer,
      heavy.HeavyLiftRouteSurvey, heavy.HeavyLiftLiftPlan, heavy.HeavyLiftPermit,
      heavy.HeavyLiftEscort, heavy.HeavyLiftLashing, heavy.HeavyLiftBallast,
      heavy.HeavyLiftRiggingMethod],
     {heavy.HeavyLiftProject: ("projects", "Projet heavy-lift"),
      heavy.HeavyLiftCrane: ("cranes", "Grue"),
      heavy.HeavyLiftModularTrailer: ("modular-trailers", "Remorque modulaire"),
      heavy.HeavyLiftRouteSurvey: ("route-surveys", "Etude itineraire"),
      heavy.HeavyLiftLiftPlan: ("lift-plans", "Plan de levage"),
      heavy.HeavyLiftPermit: ("permits", "Permis"),
      heavy.HeavyLiftEscort: ("escorts", "Escorte"),
      heavy.HeavyLiftLashing: ("lashings", "Amarrage"),
      heavy.HeavyLiftBallast: ("ballasts", "Ballast"),
      heavy.HeavyLiftRiggingMethod: ("rigging-methods", "Methode de greage")}),
]


def _pyd_type(col_type):
    if isinstance(col_type, String) or isinstance(col_type, Text):
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


def _unique_field(model):
    for constr in model.__table__.constraints:
        from sqlalchemy import UniqueConstraint as UC
        if isinstance(constr, UC):
            cols = [c.name for c in constr.columns]
            if "company_id" in cols:
                others = [x for x in cols if x != "company_id"]
                if others:
                    return others[0]
    return None


def gen_schema_file(models) -> str:
    lines = [
        '"""Schemas Pydantic auto- genere (expansion wave 5)."""',
        "from pydantic import BaseModel",
        "from typing import Optional",
        "from datetime import datetime, date",
        "",
        "",
    ]
    for m in models:
        name = m.__name__
        table = m.__table__
        cols = [c for c in table.columns if c.name not in ("id", "company_id", "created_at", "updated_at", "is_active")]
        # Create
        lines.append(f"class {name}Create(BaseModel):")
        for c in cols:
            t = _pyd_type(c.type)
            if c.nullable:
                lines.append(f"    {c.name}: Optional[{t}] = None")
            else:
                lines.append(f"    {c.name}: {t}")
        lines.append("")
        lines.append("")
        # Update (all optional + is_active)
        lines.append(f"class {name}Update(BaseModel):")
        for c in cols:
            t = _pyd_type(c.type)
            lines.append(f"    {c.name}: Optional[{t}] = None")
        lines.append("    is_active: Optional[bool] = None")
        lines.append("")
        lines.append("")
        # Out (all fields + audit)
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
    lines.append(f'"""Routeur CRUD genere pour {tag_label} (expansion wave 5)."""')
    lines.append("from fastapi import APIRouter, Depends, HTTPException, status")
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
    # helpers
    lines.extend([
        "# ─── Helpers generiques ──────────────────────────────────────────────────────",
        "",
        "def _get_or_404(db: Session, model, ident: int, label: str):",
        "    row = db.query(model).filter(model.id == ident).first()",
        "    if not row:",
        '        raise HTTPException(status_code=404, detail=f"{label} introuvable (id={ident})")',
        "    return row",
        "",
        "",
        "def _check_unique(db: Session, model, field: str, value, label: str, company_id: int, exclude_id=None):",
        "    if value is None:",
        "        return",
        "    q = db.query(model).filter(getattr(model, field) == value, model.company_id == company_id)",
        "    if exclude_id is not None:",
        "        q = q.filter(model.id != exclude_id)",
        "    if q.first():",
        "        raise HTTPException(",
        "            status_code=status.HTTP_409_CONFLICT,",
        '            detail=f"{label} « {value} » existe deja dans votre organisation.",',
        "        )",
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
        "# ─── Nomenclatures ───────────────────────────────────────────────────────────",
        "",
        '@router.get("/nomenclatures", summary=f"Vocabulaire metier {tag_label}")',
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
        unique_field = _unique_field(m)
        lines.append(f"# ─── {label} ─────────────────────────────────────────────")
        lines.append("")
        lines.append(f'@router.get("/{path}", response_model=List[{n}Out])')
        if unique_field and unique_field != "reference":
            lines.append(f"def list_{subperm.replace('-','_')}(statut: Optional[str] = None, db: Session = Depends(get_db),")
            lines.append(f'    user: User = Depends(require_perm("{perm_module}.{subperm}.read")),')
            lines.append("):")
            lines.append("    cid = _company_id(user)")
            lines.append(f"    return _scoped_list(db, {n}, cid, {{'statut': statut}})")
        else:
            lines.append(f"def list_{subperm.replace('-','_')}(db: Session = Depends(get_db),")
            lines.append(f'    user: User = Depends(require_perm("{perm_module}.{subperm}.read")),')
            lines.append("):")
            lines.append("    cid = _company_id(user)")
            lines.append(f"    return _scoped_list(db, {n}, cid)")
        lines.append("")
        lines.append("")
        lines.append(f'@router.post("/{path}", response_model={n}Out, status_code=201)')
        lines.append(f"def create_{subperm.replace('-','_')}(")
        lines.append(f"    payload: {n}Create,")
        lines.append("    db: Session = Depends(get_db),")
        lines.append(f'    user: User = Depends(require_perm("{perm_module}.{subperm}.create")),')
        lines.append("):")
        lines.append("    cid = _company_id(user)")
        lines.append("    data = payload.model_dump(exclude_unset=True)")
        if unique_field:
            lines.append(f'    _check_unique(db, {n}, "{unique_field}", data.get("{unique_field}"), "{unique_field}", cid)')
        lines.append(f"    obj = {n}(company_id=cid)")
        lines.append("    _apply(data, obj)")
        lines.append("    db.add(obj)")
        lines.append("    db.commit()")
        lines.append("    db.refresh(obj)")
        lines.append("    return obj")
        lines.append("")
        lines.append("")
        lines.append(f'@router.put("/{path}/{{ident}}", response_model={n}Out)')
        lines.append(f"def update_{subperm.replace('-','_')}(")
        lines.append("    ident: int,")
        lines.append(f"    payload: {n}Update,")
        lines.append("    db: Session = Depends(get_db),")
        lines.append(f'    user: User = Depends(require_perm("{perm_module}.{subperm}.modify")),')
        lines.append("):")
        lines.append("    cid = _company_id(user)")
        lines.append(f'    obj = _get_or_404(db, {n}, ident, "{label}")')
        lines.append("    if obj.company_id != cid:")
        lines.append('        raise HTTPException(403, "Acces refuse.")')
        lines.append("    _apply(payload.model_dump(exclude_unset=True), obj)")
        lines.append("    db.commit()")
        lines.append("    db.refresh(obj)")
        lines.append("    return obj")
        lines.append("")
        lines.append("")
        lines.append(f'@router.delete("/{path}/{{ident}}", response_model={n}Out)')
        lines.append(f"def delete_{subperm.replace('-','_')}(")
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
    for slug, perm_module, label, tag_label, models, paths_map in MODULES:
        spath = sch_dir / f"{slug}_deep.py"
        spath.write_text(gen_schema_file(models), encoding="utf-8")
        rpath = rt_dir / f"{slug}_deep.py"
        rpath.write_text(gen_router_file(slug, perm_module, tag_label, models, paths_map), encoding="utf-8")
        print("OK", slug, "->", spath.name, rpath.name)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
