# -*- coding: utf-8 -*-
"""Generateur de migrations Alembic pour les modules expansion deep (wave 5).

Lit les modeles SQLAlchemy (Base.metadata) et emet pour chaque module un
fichier `NNN_<slug>_deep.py` conforme au pattern de 062-070 :
  - tables prefixe = table_name du modele ;
  - colonnes avec types mappes (String/Integer/Date/DateTime/Boolean/Text/Float/Numeric) ;
  - UniqueConstraint (company_id, champ unique) ;
  - garde _has() idempotente ;
  - downgrade() en ordre inverse.

Usage (depuis evo-log-backend/) :
    python scripts/_gen_wave5_migrations.py
"""
import sys
from pathlib import Path

sys.path.insert(0, ".")

from app.core.database import Base  # noqa: E402
from app.models import pipeline_deep as pipe  # noqa: E402
from app.models import courier_deep as cou  # noqa: E402
from app.models import coldchain_deep as cold  # noqa: E402
from app.models import heavylift_deep as heavy  # noqa: E402

import sqlalchemy as sa  # noqa: E402
from sqlalchemy import String, Integer, BigInteger, Boolean, Date, DateTime, Text, Float, Numeric  # noqa: E402


MODULES = [
    # (module_slug, module_label, list_models, down_revision)
    ("pipeline", "pipeline-oleoduc",
     [pipe.PipelineSection, pipe.PipelinePumpStation, pipe.PipelineStorageTank,
      pipe.PipelineMeteringPoint, pipe.PipelineProductBatch, pipe.PipelinePressureReading,
      pipe.PipelineLeakDetection, pipe.PipelineMaintenanceWork,
      pipe.PipelineInjectionCampaign, pipe.PipelineShipNomination],
     "079_pipeline_deep", "078_dashboard_b_deep"),
    ("courier", "courier-express",
     [cou.CourierParcel, cou.CourierWaybill, cou.CourierHub, cou.CourierDeliveryZone,
      cou.CourierRoute, cou.CourierCourier, cou.CourierPod, cou.CourierSla,
      cou.CourierLocker, cou.CourierVehicule, cou.CourierTarif, cou.CourierException],
     "080_courier_deep", "079_pipeline_deep"),
    ("coldchain", "chaine-froid",
     [cold.ColdChainChamber, cold.ColdChainReefer, cold.ColdChainLogger, cold.ColdChainProduct,
      cold.ColdChainExcursion, cold.ColdChainVaccinBatch, cold.ColdChainHaccpRecord,
      cold.ColdChainDefrostCycle, cold.ColdChainEnergyMeter, cold.ColdChainTransportLeg],
     "081_coldchain_deep", "080_courier_deep"),
    ("heavylift", "convoi-exceptionnel",
     [heavy.HeavyLiftProject, heavy.HeavyLiftCrane, heavy.HeavyLiftModularTrailer,
      heavy.HeavyLiftRouteSurvey, heavy.HeavyLiftLiftPlan, heavy.HeavyLiftPermit,
      heavy.HeavyLiftEscort, heavy.HeavyLiftLashing, heavy.HeavyLiftBallast,
      heavy.HeavyLiftRiggingMethod],
     "082_heavylift_deep", "081_coldchain_deep"),
]


def _sa_type(col_type):
    if isinstance(col_type, String):
        n = col_type.length or 200
        return f'sa.String({n})'
    if isinstance(col_type, Integer):
        return "sa.Integer"
    if isinstance(col_type, BigInteger):
        return "sa.BigInteger"
    if isinstance(col_type, Boolean):
        return "sa.Boolean"
    if isinstance(col_type, Date):
        return "sa.Date"
    if isinstance(col_type, DateTime):
        tz = getattr(col_type, "timezone", False)
        return f"sa.DateTime(timezone={'True' if tz else 'False'})"
    if isinstance(col_type, Text):
        return "sa.Text"
    if isinstance(col_type, Float):
        return "sa.Float"
    if isinstance(col_type, Numeric):
        p = getattr(col_type, "precision", None) or 15
        s = getattr(col_type, "scale", None) or 2
        return f"sa.Numeric({p},{s})"
    return "sa.String(200)"


def gen_module(out_dir: Path, slug: str, label: str, models, rev: str, down: str):
    tbls = [m.__tablename__ for m in models]
    body = []
    body.append(f'"""{rev.split("_")[0]} : tables expansion {label} (genere)."""')
    body.append("from alembic import op")
    body.append("import sqlalchemy as sa")
    body.append("")
    body.append("")
    body.append(f'revision = "{rev}"')
    body.append(f'down_revision = "{down}"')
    body.append("branch_labels = None")
    body.append("depends_on = None")
    body.append("")
    body.append("")
    body.append("TABLES = [")
    for t in tbls:
        body.append(f'    "{t}",')
    body.append("]")
    body.append("")
    body.append("")
    body.append("def _has(name):")
    body.append("    insp = sa.inspect(op.get_bind())")
    body.append("    return name in set(insp.get_table_names())")
    body.append("")
    body.append("")
    body.append("def upgrade():")
    for m in models:
        t = m.__tablename__
        body.append(f'    if not _has("{t}"):')
        body.append(f"        op.create_table(")
        body.append(f'            "{t}",')
        # id + company_id first
        table = m.__table__
        seen = set()
        for c in table.columns:
            if c.name in ("id", "company_id"):
                seen.add(c.name)
                if c.name == "id":
                    body.append('            sa.Column("id", sa.Integer, primary_key=True, index=True),')
                else:
                    body.append('            sa.Column("company_id", sa.Integer, nullable=False, index=True),')
        # unique field first (from UniqueConstraint)
        uc_key = None
        for constr in table.constraints:
            if isinstance(constr, sa.UniqueConstraint):
                cols = [cc.name for cc in constr.columns]
                if "company_id" in cols:
                    others = [x for x in cols if x != "company_id"]
                    if others:
                        uc_key = others[0]
                        break
        if uc_key:
            c = table.columns[uc_key]
            body.append(f'            sa.Column("{c.name}", {_sa_type(c.type)}, nullable=False, index=True),')
        # remaining columns
        for c in table.columns:
            if c.name in seen:
                continue
            if uc_key and c.name == uc_key:
                continue
            nullable = "True" if c.nullable else "False"
            body.append(f'            sa.Column("{c.name}", {_sa_type(c.type)}, nullable={nullable}),')
        if uc_key:
            body.append(f'            sa.UniqueConstraint("company_id", "{uc_key}", name="uix_{t}_uniq"),')
        body.append("        )")
        body.append("")
    body.append("")
    body.append("def downgrade():")
    body.append("    for t in reversed(TABLES):")
    body.append("        if _has(t):")
    body.append("            op.drop_table(t)")
    body.append("")
    path = out_dir / f"{rev}.py"
    path.write_text("\n".join(body), encoding="utf-8")
    return path


def main():
    out_dir = Path("migrations/versions")
    if not out_dir.exists():
        print("!! out_dir introuvable :", out_dir.resolve())
        return 1
    for slug, label, models, rev, down in MODULES:
        try:
            p = gen_module(out_dir, slug, label, models, rev, down)
            print("OK", p.name, len(p.read_text(encoding="utf-8").splitlines()), "lignes")
        except Exception as e:
            print("FAIL", slug, repr(e))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
