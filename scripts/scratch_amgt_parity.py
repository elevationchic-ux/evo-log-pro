"""Controle parite ORM <-> DDL migre pour le departement amenagement portuaire.

Monte la chaine Alembic complete sur une base jetable, puis compare table par
table les colonnes declarees par l'ORM et celles réellement presentes en base.
Un ecart ici veut dire : production != developpement local.
"""
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
BACKEND = ROOT / "evo-log-backend"
sys.path.insert(0, str(BACKEND))

import app.models  # noqa: F401  (enregistre tous les modeles sur Base)
from alembic import command
from alembic.config import Config
from sqlalchemy import create_engine, inspect
from sqlalchemy.orm import configure_mappers

configure_mappers()

import app.models.amenagement_portuaire as ap

MODELES = [
    ap.SchemaDirecteur, ap.ProjetAmenagement, ap.DocumentProgrammation,
    ap.MarcheAmenagement, ap.AutorisationDomaniale, ap.ConcessionPortuaire,
    ap.InfrastructurePortuaire, ap.Dragage, ap.AutorisationTravaux,
]

TMP = ROOT / "_amgt_parity.db"
if TMP.exists():
    TMP.unlink()
URL = f"sqlite:///{TMP.as_posix()}"

cfg = Config(str(BACKEND / "alembic.ini"))
cfg.set_main_option("script_location", str(BACKEND / "migrations"))
import os
os.environ["DATABASE_URL"] = URL
command.upgrade(cfg, "head")

engine = create_engine(URL)
insp = inspect(engine)
bases = set(insp.get_table_names())

ecarts = []
for cls in MODELES:
    t = cls.__table__
    if t.name not in bases:
        ecarts.append(f"{t.name} : TABLE ABSENTE")
        continue
    reel = {c["name"] for c in insp.get_columns(t.name)}
    attendu = {c.name for c in t.columns}
    for manque in sorted(attendu - reel):
        ecarts.append(f"{t.name} : colonne ORM absente du DDL -> {manque}")
    for extra in sorted(reel - attendu):
        ecarts.append(f"{t.name} : colonne DDL inconnue de l'ORM -> {extra}")
    idx_reels = {i["name"] for i in insp.get_indexes(t.name)}
    for c in t.columns:
        if c.index:
            nom = f"ix_{t.name}_{c.name}"
            if nom not in idx_reels:
                ecarts.append(f"{t.name} : index absent -> {nom}")

# colonnes ajoutees a ports_cameroun
cols_ports = {c["name"] for c in insp.get_columns("ports_cameroun")}
for col in ("autorite_portuaire", "tirant_eau_max"):
    if col not in cols_ports:
        ecarts.append(f"ports_cameroun : colonne absente -> {col}")

# cotes enums : le DDL est un VARCHAR, la taille doit couvrir le plus long NOM
from sqlalchemy import Enum as SAEnum

for cls in MODELES:
    for c in cls.__table__.columns:
        if isinstance(c.type, SAEnum):
            noms = [m.name for m in c.type.enum_class]
            besoin = max(len(n) for n in noms) if noms else 0
            taille = c.type.length or 0
            if besoin > taille:
                ecarts.append(
                    f"{cls.__tablename__}.{c.name} : nom d'enum {besoin} > VARCHAR({taille})"
                )

print("tables verifiees :", len(MODELES))
if ecarts:
    print("ECARTS :")
    for e in ecarts:
        print("  -", e)
else:
    print("PARITE ORM/DDL OK (colonnes + index + ports_cameroun)")

engine.dispose()
TMP.unlink(missing_ok=True)
for suffix in ("-shm", "-wal"):
    Path(TMP.as_posix() + suffix).unlink(missing_ok=True)
