"""Generateur de boilerplate pour l'expansion ERP (Wave 1-3).

Produit pour chaque module :
  - app/models/{module_key}_deep.py : SQLAlchemy models
  - app/schemas/{module_key}_deep.py : Pydantic schemas
  - app/routers/v1/{module_key}_deep.py : FastAPI CRUD router
  - migrations/versions/{rev}_{module_key}_deep.py : Alembic migration
  - src/components/{module_key}/registres.ts : ConfigRegistre objects
  - src/app/(app)/{module_key}/{slug}/page.tsx : thin page wrappers

Usage : python scripts/generate_module.py <manifest.py> [--apply]

Le manifest est un module Python exposant une dict MANIFEST :
  MANIFEST = {
    "module_key": "transit",           # prefix backend (snake_case)
    "module_slug": "transit-douane",   # prefix frontend (kebab-case)
    "module_path": "transit-douane",   # /api/v1/{module_path}/...
    "perm_module": "transit",          # require_perm("{perm_module}.{sub}.{action}")
    "revision": "048",                 # next migration number
    "down_revision": "047_port_ops_deep",
    "entities": [
      {
        "slug": "hs-classification",       # URL path segment
        "table": "hs_classifications",     # DB table name
        "class_name": "HsClassification",  # Python class
        "entite": "hs_classifications",    # plural path segment
        "perm": "hs_classification",       # {perm_module}.{perm}.{action}
        "titre": "Classification SH",
        "titreEn": "HS Classification",
        "description": "...",
        "descriptionEn": "...",
        "aide": "...",
        "aideEn": "...",
        "icon": "BookOpen",                # Lucide icon name
        "unicite": "code_hs",              # column with (company_id, unicite) unique
        "fields": [
          {"name": "code_hs", "type": "str", "required": True, "label": "Code SH", "search": True},
          {"name": "designation", "type": "text", "label": "Designation"},
          {"name": "section", "type": "str", "label": "Section du SH"},
          {"name": "taux_droit", "type": "num", "label": "Taux droit %"},
          ...
        ],
        "enums": [
          {"name": "statut", "values": ["PROVISOIRE", "VALIDE", "CONTESTE"], "default": "PROVISOIRE"}
        ],
      },
      ...
    ]
  }

Type codes: str (VARCHAR), text (TEXT), num (NUMERIC), int (INTEGER),
            date (DATE), datetime (DATETIME), bool (BOOLEAN),
            enum:<name> (VARCHAR backed by a Python enum).
"""
from __future__ import annotations
import importlib.util
import os
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent
BACKEND = ROOT / "evo-log-backend"
FRONTEND = ROOT / "evo-log-frontend"

SQLA_TYPE = {
    "str": "String", "text": "Text", "num": "Numeric", "int": "Integer",
    "date": "Date", "datetime": "DateTime(timezone=True)", "bool": "Boolean",
}

PY_TYPE = {
    "str": "str", "text": "str", "num": "float", "int": "int",
    "date": "date", "datetime": "datetime", "bool": "bool",
}

TS_TYPE = {
    "str": "string", "text": "string", "num": "number", "int": "number",
    "date": "string", "datetime": "string", "bool": "boolean",
}

FIELD_WIDTH = {
    "str": "(150)", "text": "(2000)", "num": "", "int": "", "date": "",
    "datetime": "", "bool": "",
}


def _sqla_type_str(ftype: str) -> str:
    if ftype == "enum" or ftype.startswith("enum:"):
        return "String(50)"
    return SQLA_TYPE[ftype] + FIELD_WIDTH.get(ftype, "")


def load_manifest(path: Path) -> dict:
    spec = importlib.util.spec_from_file_location("manifest_mod", str(path))
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod.MANIFEST


# ─── Backend model file ──────────────────────────────────────────────────────

def gen_model_file(m: dict) -> str:
    lines = [
        f'"""Modeles {m["module_slug"]} (expansion approfondie generee).',
        '',
        f'{len(m["entities"])} entites de gestion, chacune scoped par company_id.',
        'Convention d\'honnetete : aucune valeur par defaut, NULL = "non enregistre".',
        '"""',
        'from sqlalchemy import (',
        '    Column, Integer, String, Text, DateTime, Boolean, Float,',
        '    ForeignKey, Date, Numeric, UniqueConstraint, Enum as SAEnum,',
        ')',
        'from sqlalchemy.sql import func',
        'import enum',
        '',
        'from app.core.database import Base',
        '',
        '',
        'def _enum(cls):',
        '    return SAEnum(cls, native_enum=False, create_constraint=False,',
        '                  values_callable=lambda x: [e.value for e in x])',
        '',
        '',
    ]

    # Collect all enums globally
    enum_registry = {}
    for ent in m["entities"]:
        for en in ent.get("enums", []):
            enum_registry[f"{ent['class_name']}_{en['name']}"] = en

    if enum_registry:
        lines.append("# ─── Enums ────────────────────────────────────────────────────────────────────")
        lines.append("")
        for key, en in enum_registry.items():
            cname = key
            lines.append(f"class {cname}(str, enum.Enum):")
            for v in en["values"]:
                lines.append(f"    {v} = \"{v.lower()}\"")
            lines.append("")
            lines.append("")

    lines.append("# ─── Modeles ──────────────────────────────────────────────────────────────────")
    lines.append("")

    for ent in m["entities"]:
        lines.append(f"class {ent['class_name']}(Base):")
        lines.append(f'    """{ent["titre"]}."""')
        lines.append(f'    __tablename__ = "{ent["table"]}"')
        uniq = ent.get("unicite")
        if uniq:
            lines.append(f'    __table_args__ = (')
            lines.append(f'        UniqueConstraint(\'company_id\', \'{uniq}\', name=\'uix_{ent["table"][:20]}_company_{uniq[:15]}\'),')
            lines.append(f'    )')
        lines.append(f'    id = Column(Integer, primary_key=True, index=True)')
        lines.append(f"    company_id = Column(Integer, ForeignKey('companies.id'), nullable=False, index=True)")
        for f in ent["fields"]:
            col_kwargs = []
            if f.get("required"):
                col_kwargs.append("nullable=False")
            if f.get("search"):
                col_kwargs.append("index=True")
            if f["type"] == "enum" or f["type"].startswith("enum:"):
                enum_name = f"{ent['class_name']}_{f['name']}"
                default = None
                for en in ent.get("enums", []):
                    if en["name"] == f["name"] and "default" in en:
                        default = en["default"]
                args = [f"_enum({enum_name})"]
                if default:
                    args.append(f"default={enum_name}.{default}")
                if col_kwargs:
                    args.extend(col_kwargs)
                lines.append(f"    {f['name']} = Column({', '.join(args)})")
                continue
            sa = SQLA_TYPE[f["type"]]
            width = FIELD_WIDTH.get(f["type"], "")
            col_kwargs.insert(0, f"{sa}{width}")
            if not any("nullable=" in k for k in col_kwargs):
                col_kwargs.append("nullable=True")
            lines.append(f"    {f['name']} = Column({', '.join(col_kwargs)})")
        lines.append(f"    is_active = Column(Boolean, default=True)")
        lines.append(f"    created_at = Column(DateTime(timezone=True), server_default=func.now())")
        lines.append(f"    updated_at = Column(DateTime(timezone=True), onupdate=func.now())")
        lines.append("")
        lines.append("")

    return "\n".join(lines)


# ─── Backend schema file ─────────────────────────────────────────────────────

def gen_schema_file(m: dict) -> str:
    lines = [
        f'"""Schemas Pydantic pour {m["module_slug"]} (genere)."""',
        'from pydantic import BaseModel',
        'from typing import Optional',
        'from datetime import datetime, date',
        '',
        '',
    ]
    for ent in m["entities"]:
        cn = ent["class_name"]
        # Create schema
        lines.append(f"class {cn}Create(BaseModel):")
        any_field = False
        for f in ent["fields"]:
            pt = "str" if f["type"] == "enum" or f["type"].startswith("enum:") else PY_TYPE[f["type"]]
            req = f.get("required", False)
            if req:
                lines.append(f"    {f['name']}: {pt}")
            else:
                lines.append(f"    {f['name']}: Optional[{pt}] = None")
            any_field = True
        if not any_field:
            lines.append("    pass")
        lines.append("")
        lines.append("")
        # Update
        lines.append(f"class {cn}Update(BaseModel):")
        for f in ent["fields"]:
            pt = "str" if f["type"] == "enum" or f["type"].startswith("enum:") else PY_TYPE[f["type"]]
            lines.append(f"    {f['name']}: Optional[{pt}] = None")
        lines.append("    is_active: Optional[bool] = None")
        lines.append("")
        lines.append("")
        # Out
        lines.append(f"class {cn}Out(BaseModel):")
        lines.append(f"    id: int")
        lines.append(f"    company_id: int")
        for f in ent["fields"]:
            pt = "str" if f["type"] == "enum" or f["type"].startswith("enum:") else PY_TYPE[f["type"]]
            if f.get("required"):
                lines.append(f"    {f['name']}: {pt}")
            else:
                lines.append(f"    {f['name']}: Optional[{pt}] = None")
        lines.append(f"    is_active: Optional[bool] = None")
        lines.append(f"    created_at: Optional[datetime] = None")
        lines.append(f"    updated_at: Optional[datetime] = None")
        lines.append(f'    model_config = {{"from_attributes": True}}')
        lines.append("")
        lines.append("")
    return "\n".join(lines)


# ─── Backend router file ─────────────────────────────────────────────────────

def gen_router_file(m: dict) -> str:
    mod_key = m["module_key"]
    perm = m["perm_module"]
    lines = [
        f'"""Routeur CRUD genere pour {m["module_slug"]} (expansion)."""',
        'from fastapi import APIRouter, Depends, HTTPException, status',
        'from sqlalchemy.orm import Session',
        'from typing import Optional, List',
        '',
        'from app.core.database import get_db',
        'from app.core.permissions import require_perm',
        'from app.models.user import User',
        f'from app.models.{mod_key}_deep import (',
    ]
    for ent in m["entities"]:
        lines.append(f'    {ent["class_name"]},')
    lines.append(')')
    lines.append(f'from app.schemas.{mod_key}_deep import (')
    for ent in m["entities"]:
        cn = ent["class_name"]
        lines.append(f'    {cn}Create, {cn}Update, {cn}Out,')
    lines.append(')')
    lines.append('')
    lines.append(f'router = APIRouter(tags=["{m["module_slug"]} (expansion)"])')
    lines.append('')
    lines.append('')
    lines.append('# ─── Helpers generiques ──────────────────────────────────────────────────────')
    lines.append('')
    lines.append('''
def _get_or_404(db: Session, model, ident: int, label: str):
    row = db.query(model).filter(model.id == ident).first()
    if not row:
        raise HTTPException(status_code=404, detail=f"{label} introuvable (id={ident})")
    return row


def _check_unique(db: Session, model, field: str, value, label: str, company_id: int, exclude_id=None):
    if value is None:
        return
    q = db.query(model).filter(getattr(model, field) == value, model.company_id == company_id)
    if exclude_id is not None:
        q = q.filter(model.id != exclude_id)
    if q.first():
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=f"{label} « {value} » existe deja dans votre organisation.",
        )


def _scoped_list(db, model, company_id, filters=None):
    q = db.query(model).filter(model.company_id == company_id)
    if hasattr(model, 'is_active'):
        q = q.filter(model.is_active.is_(True))
    if filters:
        for key, val in filters.items():
            if val is not None and hasattr(model, key):
                q = q.filter(getattr(model, key) == val)
    return q.order_by(model.id.desc()).all()


def _apply(payload: dict, obj):
    for key, value in payload.items():
        setattr(obj, key, value)


def _company_id(user: User) -> int:
    if not user.company_id:
        raise HTTPException(status_code=400, detail="Votre compte n'est rattache a aucune organisation.")
    return user.company_id


'''.strip('\n'))
    lines.append('')
    lines.append('')

    # Nomenclatures stub (returns empty by default; submodules can add enums)
    lines.append('# ─── Nomenclatures ───────────────────────────────────────────────────────────')
    lines.append('')
    lines.append(f'@router.get("/nomenclatures", summary="Vocabulaire metier {m["module_slug"]}")')
    lines.append(f'def nomenclatures(user: User = Depends(require_perm("{perm}.nomenclature.read"))):')
    lines.append('    from app.models import ' + f'{mod_key}_deep as _md')
    lines.append('    import enum as _pyenum')
    lines.append('    out = {}')
    lines.append('    for name in dir(_md):')
    lines.append('        obj = getattr(_md, name)')
    lines.append('        if isinstance(obj, type) and issubclass(obj, _pyenum.Enum) and obj is not _pyenum.Enum:')
    lines.append('            out[name.lower()] = [{"code": m.name, "valeur": m.value} for m in obj]')
    lines.append('    return out')
    lines.append('')
    lines.append('')

    for ent in m["entities"]:
        cn = ent["class_name"]
        path = ent["entite"]
        p = f'{perm}.{ent["perm"]}'
        label = ent["titre"]
        uniq = ent.get("unicite")
        # List
        lines.append(f'# ─── {label} ─────────────────────────────────────────────────')
        lines.append('')
        lines.append(f'@router.get("/{path}", response_model=List[{cn}Out])')
        # Simpler: add a statut filter if the field exists
        statut_field = next((f for f in ent["fields"] if f["name"] == "statut"), None)
        if statut_field:
            lines.append(f'def list_{ent["perm"]}(statut: Optional[str] = None, db: Session = Depends(get_db),')
        else:
            lines.append(f'def list_{ent["perm"]}(db: Session = Depends(get_db),')
        lines.append(f'    user: User = Depends(require_perm("{p}.read")),')
        lines.append('):')
        lines.append('    cid = _company_id(user)')
        if statut_field:
            lines.append(f'    return _scoped_list(db, {cn}, cid, {{"statut": statut}})')
        else:
            lines.append(f'    return _scoped_list(db, {cn}, cid)')
        lines.append('')
        lines.append('')
        # Create
        lines.append(f'@router.post("/{path}", response_model={cn}Out, status_code=201)')
        lines.append(f'def create_{ent["perm"]}(')
        lines.append(f'    payload: {cn}Create,')
        lines.append(f'    db: Session = Depends(get_db),')
        lines.append(f'    user: User = Depends(require_perm("{p}.create")),')
        lines.append('):')
        lines.append('    cid = _company_id(user)')
        lines.append('    data = payload.model_dump(exclude_unset=True)')
        if uniq:
            lines.append(f'    _check_unique(db, {cn}, "{uniq}", data.get("{uniq}"), "{uniq}", cid)')
        lines.append(f'    obj = {cn}(company_id=cid)')
        lines.append('    _apply(data, obj)')
        lines.append('    db.add(obj)')
        lines.append('    db.commit()')
        lines.append('    db.refresh(obj)')
        lines.append('    return obj')
        lines.append('')
        lines.append('')
        # Update
        lines.append(f'@router.put("/{path}/{{ident}}", response_model={cn}Out)')
        lines.append(f'def update_{ent["perm"]}(')
        lines.append(f'    ident: int,')
        lines.append(f'    payload: {cn}Update,')
        lines.append(f'    db: Session = Depends(get_db),')
        lines.append(f'    user: User = Depends(require_perm("{p}.modify")),')
        lines.append('):')
        lines.append('    cid = _company_id(user)')
        lines.append(f'    obj = _get_or_404(db, {cn}, ident, "{label}")')
        lines.append('    if obj.company_id != cid:')
        lines.append('        raise HTTPException(403, "Acces refuse.")')
        lines.append('    _apply(payload.model_dump(exclude_unset=True), obj)')
        lines.append('    db.commit()')
        lines.append('    db.refresh(obj)')
        lines.append('    return obj')
        lines.append('')
        lines.append('')
        # Delete (soft)
        lines.append(f'@router.delete("/{path}/{{ident}}", response_model={cn}Out)')
        lines.append(f'def delete_{ent["perm"]}(')
        lines.append(f'    ident: int,')
        lines.append(f'    db: Session = Depends(get_db),')
        lines.append(f'    user: User = Depends(require_perm("{p}.modify")),')
        lines.append('):')
        lines.append('    cid = _company_id(user)')
        lines.append(f'    obj = _get_or_404(db, {cn}, ident, "{label}")')
        lines.append('    if obj.company_id != cid:')
        lines.append('        raise HTTPException(403, "Acces refuse.")')
        lines.append('    obj.is_active = False')
        lines.append('    db.commit()')
        lines.append('    db.refresh(obj)')
        lines.append('    return obj')
        lines.append('')
        lines.append('')

    return "\n".join(lines)


# ─── Migration file ──────────────────────────────────────────────────────────

def gen_migration(m: dict) -> str:
    rev = m["revision"]
    down = m["down_revision"]
    lines = [
        f'"""{rev} : tables expansion {m["module_slug"]} (genere)."""',
        'from alembic import op',
        'import sqlalchemy as sa',
        '',
        '',
        f'revision = "{rev}_{m["module_key"]}_deep"',
        f'down_revision = "{down}"',
        'branch_labels = None',
        'depends_on = None',
        '',
        '',
        f'TABLES = [',
    ]
    for ent in m["entities"]:
        lines.append(f'    "{ent["table"]}",')
    lines.append(']')
    lines.append('')
    lines.append('')
    lines.append('def _has(name):')
    lines.append('    insp = sa.inspect(op.get_bind())')
    lines.append('    return name in set(insp.get_table_names())')
    lines.append('')
    lines.append('')
    lines.append('def upgrade():')
    for ent in m["entities"]:
        lines.append(f'    if not _has("{ent["table"]}"):')
        lines.append(f'        op.create_table(')
        lines.append(f'            "{ent["table"]}",')
        lines.append(f'            sa.Column("id", sa.Integer, primary_key=True, index=True),')
        lines.append(f'            sa.Column("company_id", sa.Integer, nullable=False, index=True),')
        for f in ent["fields"]:
            t = f["type"]
            if t == "str":
                sa_t = 'sa.String(200)'
            elif t == "text":
                sa_t = 'sa.Text'
            elif t == "num":
                sa_t = 'sa.Numeric'
            elif t == "int":
                sa_t = 'sa.Integer'
            elif t == "date":
                sa_t = 'sa.Date'
            elif t == "datetime":
                sa_t = 'sa.DateTime(timezone=True)'
            elif t == "bool":
                sa_t = 'sa.Boolean'
            else:  # enum
                sa_t = 'sa.String(50)'
            null = 'nullable=False' if f.get("required") else 'nullable=True'
            idx = ', index=True' if f.get("search") else ''
            lines.append(f'            sa.Column("{f["name"]}", {sa_t}, {null}{idx}),')
        lines.append(f'            sa.Column("is_active", sa.Boolean, nullable=True),')
        lines.append(f'            sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),')
        lines.append(f'            sa.Column("updated_at", sa.DateTime(timezone=True), nullable=True),')
        if ent.get("unicite"):
            lines.append(f'            sa.UniqueConstraint("company_id", "{ent["unicite"]}", name="uix_{ent["table"][:30]}_uniq"),')
        lines.append(f'        )')
        lines.append('')
    lines.append('')
    lines.append('def downgrade():')
    lines.append('    for t in reversed(TABLES):')
    lines.append('        if _has(t):')
    lines.append('            op.drop_table(t)')
    lines.append('')
    return "\n".join(lines)


# ─── Frontend registre.ts ────────────────────────────────────────────────────

def gen_frontend_registres(m: dict) -> str:
    mod_slug = m["module_slug"]
    perm = m["perm_module"]
    lines = [
        f'/**',
        f' * Configs Registre pour {mod_slug} (expansion generee).',
        f' *',
        f' * Chaque ConfigRegistre est passe en prop au composant generique',
        f' * <RegistreGenerique /> pour rendre table, filtres, formulaire.',
        f' */',
        f'"use client";',
        f'',
        f"import * as Icons from 'lucide-react';",
        "import type { ConfigRegistre, ColonneRegistre, ChampRegistre, FiltreRegistre } from '@/components/registre-generique/typesRegistre';",
        "import { registreAPI } from '@/lib/api-client';",
        f'',
        f'const api = registreAPI("{mod_slug}");',
        f'',
        "function col(name: string, label: string, labelEn: string, opts: Partial<ColonneRegistre> = {}): ColonneRegistre {",
        "  return { name, label, labelEn, ...opts } as ColonneRegistre;",
        "}",
        "",
        "function txt(name: string, label: string, labelEn: string, opts: Partial<ChampRegistre> = {}): ChampRegistre {",
        '  return { name, label, labelEn, type: "texte", ...opts } as ChampRegistre;',
        "}",
        "",
        "function num(name: string, label: string, labelEn: string, opts: Partial<ChampRegistre> = {}): ChampRegistre {",
        '  return { name, label, labelEn, type: "nombre", ...opts } as ChampRegistre;',
        "}",
        "",
        "function dt(name: string, label: string, labelEn: string): ChampRegistre {",
        '  return { name, label, labelEn, type: "date" } as ChampRegistre;',
        "}",
        "",
        "function dtx(name: string, label: string, labelEn: string): ChampRegistre {",
        '  return { name, label, labelEn, type: "date" } as ChampRegistre;',
        "}",
        "",
        "function area(name: string, label: string, labelEn: string): ChampRegistre {",
        '  return { name, label, labelEn, type: "zone" } as ChampRegistre;',
        "}",
        "",
        "function chk(name: string, label: string, labelEn: string): ChampRegistre {",
        '  return { name, label, labelEn, type: "booleen" } as ChampRegistre;',
        "}",
        "",
        "function sel(name: string, label: string, labelEn: string, nomKey: string): ChampRegistre {",
        '  return { name, label, labelEn, type: "select", nomenclature: nomKey } as ChampRegistre;',
        "}",
        "",
        "function filtreSel(name: string, label: string, labelEn: string, nomKey: string): FiltreRegistre {",
        '  return { name, label, labelEn, type: "select", nomenclature: nomKey } as FiltreRegistre;',
        "}",
        "",
    ]

    for ent in m["entities"]:
        varname = f'registre{ent["class_name"]}'
        cols_lines = []
        champs_lines = []
        for f in ent["fields"]:
            label_fr = f.get("label", f["name"])
            label_en = f.get("labelEn", label_fr)
            t = f["type"]
            if f.get("search"):
                cols_lines.append(f'    col("{f["name"]}", "{label_fr}", "{label_en}"),')
            else:
                cols_lines.append(f'    col("{f["name"]}", "{label_fr}", "{label_en}"),')
            if t in ("str", "text"):
                if f.get("required"):
                    champs_lines.append(f'    txt("{f["name"]}", "{label_fr}", "{label_en}", {{ requisCreation: true }}),')
                else:
                    champs_lines.append(f'    txt("{f["name"]}", "{label_fr}", "{label_en}"),')
            elif t == "num":
                champs_lines.append(f'    num("{f["name"]}", "{label_fr}", "{label_en}"),')
            elif t == "int":
                champs_lines.append(f'    num("{f["name"]}", "{label_fr}", "{label_en}"),')
            elif t == "date":
                champs_lines.append(f'    dt("{f["name"]}", "{label_fr}", "{label_en}"),')
            elif t == "datetime":
                champs_lines.append(f'    dtx("{f["name"]}", "{label_fr}", "{label_en}"),')
            elif t == "bool":
                champs_lines.append(f'    chk("{f["name"]}", "{label_fr}", "{label_en}"),')
            elif t == "enum" or t.startswith("enum:"):
                # Reference to nomenclature - use key of nomenclature (name without prefix)
                nomkey = f["name"]
                champs_lines.append(f'    sel("{f["name"]}", "{label_fr}", "{label_en}", "{nomkey}"),')

        lines.append(f'export const {varname}: ConfigRegistre = ' + '{')
        lines.append(f'  permModule: "{perm}",')
        lines.append(f'  permSousModule: "{ent["perm"]}",')
        lines.append(f'  tcode: "registre-{ent["slug"]}",')
        lines.append(f'  icon: Icons.{ent["icon"]},')
        lines.append(f'  titre: "{ent["titre"]}",')
        lines.append(f'  titreEn: "{ent["titreEn"]}",')
        lines.append(f'  description: "{ent["description"]}",')
        lines.append(f'  descriptionEn: "{ent["descriptionEn"]}",')
        lines.append(f'  aide: "{ent["aide"]}",')
        lines.append(f'  aideEn: "{ent["aideEn"]}",')
        lines.append(f'  lister: (params) => api.lister("{ent["entite"]}", params),')
        lines.append(f'  creer: (data) => api.creer("{ent["entite"]}", data),')
        lines.append(f'  modifier: (id, data) => api.modifier("{ent["entite"]}", id, data),')
        lines.append(f'  unicite: "{ent.get("unicite") or ""}",')
        lines.append(f'  fetchNomenclatures: () => api.getNomenclatures(),')
        lines.append(f'  colonnes: [')
        lines.extend(cols_lines)
        lines.append(f'  ],')
        lines.append(f'  champs: [')
        lines.extend(champs_lines)
        lines.append(f'  ],')
        lines.append(f'}};')
        lines.append('')
        lines.append('')

    return "\n".join(lines)


# ─── Page wrappers ───────────────────────────────────────────────────────────

def gen_page_wrapper(ent: dict, module_slug: str, registre_filename: str = "registres") -> str:
    cn = ent["class_name"]
    return (
        f"'use client';\n"
        f"import RegistreGenerique from '@/components/registre-generique/RegistreGenerique';\n"
        f"import {{ registre{cn} }} from '@/components/{module_slug}/{registre_filename}';\n"
        f"\n"
        f"export default function Page{cn}() {{\n"
        f"  return <RegistreGenerique config={{registre{cn}}} />;\n"
        f"}}\n"
    )


# ─── Navigation entries ──────────────────────────────────────────────────────

def gen_nav_entries(m: dict) -> str:
    lines = []
    for ent in m["entities"]:
        lines.append(f'  {{')
        lines.append(f'    href: "/{m["module_slug"]}/{ent["slug"]}",')
        lines.append(f'    labelFr: "{ent["titre"]}",')
        lines.append(f'    labelEn: "{ent["titreEn"]}",')
        lines.append(f'    icon: "{ent["icon"]}",')
        lines.append(f'    sousModule: "{ent["slug"]}",')
        lines.append(f'    perm: "{m["perm_module"]}.{ent["perm"]}.read",')
        lines.append(f'  }},')
    return "\n".join(lines)


# ─── Main entrypoint ─────────────────────────────────────────────────────────

def write_file(path: Path, content: str):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")
    print(f"WROTE {path}")


def generate(manifest_path: Path, apply: bool = True):
    m = load_manifest(manifest_path)
    generate_from_dict(m, apply=apply)


def generate_from_dict(m: dict, apply: bool = True):
    if not apply:
        print("DRY RUN: manifest loaded, files not written")
        return
    mod_key = m["module_key"]
    mod_slug = m["module_slug"]
    registre_filename = m.get("registre_filename", "registres")

    write_file(BACKEND / "app" / "models" / f"{mod_key}_deep.py", gen_model_file(m))
    write_file(BACKEND / "app" / "schemas" / f"{mod_key}_deep.py", gen_schema_file(m))
    write_file(BACKEND / "app" / "routers" / "v1" / f"{mod_key}_deep.py", gen_router_file(m))
    write_file(BACKEND / "migrations" / "versions" / f"{m['revision']}_{mod_key}_deep.py", gen_migration(m))
    write_file(FRONTEND / "src" / "components" / mod_slug / f"{registre_filename}.ts", gen_frontend_registres(m))
    for ent in m["entities"]:
        page_path = FRONTEND / "src" / "app" / "(app)" / mod_slug / ent["slug"] / "page.tsx"
        write_file(page_path, gen_page_wrapper(ent, mod_slug, registre_filename))

    print("\n--- Navigation entries (paste into navigationRegistry.ts) ---\n")
    print(f'// Module: {mod_slug}')
    print(gen_nav_entries(m))
    print("\n--- Model __init__.py patch ---")
    imports = "\n".join([f'    {ent["class_name"]},' for ent in m["entities"]])
    names = ", ".join([f'"{ent["class_name"]}"' for ent in m["entities"]])
    print(f'from app.models.{mod_key}_deep import (\n{imports}\n)')
    print(f'__all__.extend([{names}])')
    print("\n--- main.py router include ---")
    print(f'from app.routers.v1 import {mod_key}_deep')
    print(f'safe_include_router({mod_key}_deep.router, prefix="/api/v1/{mod_slug}", tags=["{mod_slug} (expansion)"])')


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print(__doc__)
        sys.exit(1)
    manifest = Path(sys.argv[1])
    apply = "--apply" in sys.argv
    generate(manifest, apply=apply)
