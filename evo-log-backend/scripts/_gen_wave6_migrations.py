# -*- coding: utf-8 -*-
"""Generateur de migrations Alembic pour wave 6 (maintenance + tracabilite).

Reflechit le metadata SQLAlchemy et emet un fichier de migration par module :
  migrations/versions/105_maintenance_deep.py
  migrations/versions/106_tracabilite_deep.py

Pattern idempotent (_has(t) + if not _has) aligne sur wave 5.
"""
import sys
from pathlib import Path

sys.path.insert(0, ".")

from sqlalchemy import (
    String, Integer, BigInteger, Boolean, Date, DateTime, Text, Float, Numeric,
)
from sqlalchemy import Enum as SAEnum, ForeignKey, UniqueConstraint, Index  # noqa: E402

import app.models  # noqa: F401,E402  (register tables)
from app.models.maintenance_deep import Base  # noqa: E402
from app.models import maintenance_deep as mnt  # noqa: E402
from app.models import tracabilite_deep as trc  # noqa: E402


MODULES = [
    ("105_maintenance_deep", "104_departement_d5_deep", "maintenance", "maint_", mnt),
    ("106_tracabilite_deep", "105_maintenance_deep", "tracabilite", "trace_", trc),
]


def _sa_type(col_type):
    if isinstance(col_type, SAEnum):
        # Enum stored as VARCHAR of max 60 (safety net)
        vals = col_type.enums or [""]
        size = max(60, max(len(v) for v in vals) + 20)
        return f"sa.String({size})"
    if isinstance(col_type, String):
        n = col_type.length or 200
        return f"sa.String({n})"
    if isinstance(col_type, Text):
        return "sa.Text"
    if isinstance(col_type, Integer):
        return "sa.Integer"
    if isinstance(col_type, BigInteger):
        return "sa.BigInteger"
    if isinstance(col_type, Boolean):
        return "sa.Boolean"
    if isinstance(col_type, Date):
        return "sa.Date"
    if isinstance(col_type, DateTime):
        if col_type.timezone:
            return "sa.DateTime(timezone=True)"
        return "sa.DateTime"
    if isinstance(col_type, Numeric):
        if col_type.precision and col_type.scale:
            return f"sa.Numeric({col_type.precision}, {col_type.scale})"
        return "sa.Numeric"
    if isinstance(col_type, Float):
        return "sa.Float"
    return "sa.String(200)"


def _is_fk(col):
    return bool(col.foreign_keys)


def gen_table_block(t):
    """Return list of lines to create one table."""
    lines = []
    lines.append(f'    if not _has("{t.name}"):')
    lines.append(f"        op.create_table(")
    lines.append(f'            "{t.name}",')
    # Columns
    for col in t.columns:
        parts = [f'sa.Column("{col.name}", {_sa_type(col.type)}']
        if col.foreign_keys:
            fk = next(iter(col.foreign_keys))
            target = fk.target_fullname  # e.g. "maint_technical_assets.id"
            parts.append(f', sa.ForeignKey("{target}")')
        if col.primary_key:
            parts.append(", primary_key=True")
            parts.append(", index=True")
        if not col.nullable and not col.primary_key:
            parts.append(", nullable=False")
        elif col.nullable and not col.primary_key:
            parts.append(", nullable=True")
        # index (best-effort via t.indexes)
        if not col.primary_key:
            for idx in t.indexes:
                idx_cols = [c.name for c in idx.columns]
                if col.name in idx_cols and len(idx_cols) == 1:
                    parts.append(", index=True")
                    break
        # default (python-side) not applied at DDL for portability
        parts.append(")")
        lines.append("            " + "".join(parts) + ",")
    # UniqueConstraints
    for constr in t.constraints:
        if isinstance(constr, UniqueConstraint):
            cols = [c.name for c in constr.columns]
            cols_repr = ", ".join(f'"{c}"' for c in cols)
            name = constr.name or f"uix_{t.name}_{'_'.join(cols)}"
            lines.append(f"            sa.UniqueConstraint({cols_repr}, name=\"{name}\"),")
    lines.append("        )")
    lines.append("")
    return lines


def gen_composite_indexes(t):
    lines = []
    for idx in t.indexes:
        cols = list(idx.columns)
        if len(cols) < 2:
            continue
        # Composite index — emit op.create_index
        col_names = ", ".join(f'"{c.name}"' for c in cols)
        idx_name = idx.name or f"ix_{t.name}_{'_'.join(c.name for c in cols)}"
        lines.append(f'    op.create_index("{idx_name}", "{t.name}", [{col_names}], unique={str(idx.unique)})')
    return lines


def gen_migration(revision, down_revision, module_label, prefix, model_mod):
    lines = [
        f'"""{revision} : tables expansion {module_label} (genere wave 6)."""',
        "from alembic import op",
        "import sqlalchemy as sa",
        "",
        "",
        f'revision = "{revision}"',
        f'down_revision = "{down_revision}"',
        "branch_labels = None",
        "depends_on = None",
        "",
        "",
    ]
    tables = [t for t in Base.metadata.tables.values()
              if t.name.startswith(prefix)]
    tables_sorted = sorted(tables, key=lambda t: t.name)
    lines.append("TABLES = [")
    for t in tables_sorted:
        lines.append(f'    "{t.name}",')
    lines.append("]")
    lines.extend([
        "",
        "",
        "def _has(name):",
        "    insp = sa.inspect(op.get_bind())",
        "    return name in set(insp.get_table_names())",
        "",
        "",
        "def upgrade():",
    ])
    for t in tables_sorted:
        lines.extend(gen_table_block(t))
    lines.append("")
    lines.append("")
    lines.append("def downgrade():")
    lines.append("    for name in reversed(TABLES):")
    lines.append("        if _has(name):")
    lines.append("            op.drop_table(name)")
    lines.append("")
    return "\n".join(lines)


def main():
    out_dir = Path("migrations/versions")
    for revision, down_rev, label, prefix, mod in MODULES:
        fpath = out_dir / f"{revision}.py"
        fpath.write_text(gen_migration(revision, down_rev, label, prefix, mod), encoding="utf-8")
        print("OK", revision, "->", fpath)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
