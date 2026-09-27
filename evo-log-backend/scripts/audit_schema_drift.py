"""Audit de parite entre les modeles SQLAlchemy et le schema reellement en base.

Pourquoi cet outil existe : une route peut repondre 200 et une page s'afficher
avec un squelette correct, puis mourir a la premiere ligne lue ou ecrite. Les
modeles et la base peuvent diverger sur QUATRE axes, et un seul se voit en
developpement :

  1. colonne reclamee par le modele et absente de la base
     -> "no such column: ..." a la premiere SELECT (lecture).
  2. colonne NOT NULL en base, nullable dans le modele, sans defaut
     -> "NOT NULL constraint failed" a l'INSERT : le modele ne l'alimente pas.
  3. valeur par defaut en base sans equivalent dans le modele
     -> SQLAlchemy relit la colonne apres INSERT ; si le defaut est
        CURRENT_TIMESTAMP (date+heure) et la colonne declaree Date dans le
        modele, la relecture leve "Invalid isoformat string".
  4. type Date cote modele contre DATETIME cote base (et l'inverse)
     -> meme cause, meme effet, selon le sens de la conversion.

Les derives de sens inverse (colonnes en surplus dans la base) sont enumerees
mais ne sont pas des defauts : elles gene seulement quand elles sont NOT NULL
sans defaut, ce que leve le point 2.

Reference : il faut comparer au schema produit par la chaine Alembic complete,
pas a la base de developpement. Celle-ci est bootstrappee par create_all() puis
bricolee a la main : elle presente l'UNION des formes et masque donc tout.

Usage :
    python scripts/audit_schema_drift.py [chemin/vers/base.db]
    python scripts/audit_schema_drift.py --replay     # rejoue 001..head dans une base temporaire
"""
from __future__ import annotations

import os
import sqlite3
import subprocess
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

import sqlalchemy as sa  # noqa: E402
from app.core.database import Base  # noqa: E402
import app.models  # noqa: F401,E402  (enregistre toutes les tables)
import app.models.acconage  # noqa: F401,E402  (navires, escales, conteneurs)


FAMILLE_DATE = {"DATE"}
FAMILLE_DATETIME = {"DATETIME", "TIMESTAMP"}


def details_base(cur, table: str):
    """nom de colonne -> (type SQL, notnull, defaut SQL)."""
    donnees = {}
    for ligne in cur.execute("PRAGMA table_info('{}')".format(table)):
        donnees[ligne[1]] = (ligne[2].upper(), ligne[3], ligne[4])
    return donnees


def table_presente(cur, table: str) -> bool:
    return cur.execute(
        "SELECT name FROM sqlite_master WHERE type='table' AND name=?", (table,)
    ).fetchone() is not None


def famille(type_sql: str):
    base = type_sql.split("(")[0].strip()
    if base in FAMILLE_DATE:
        return "Date"
    if base in FAMILLE_DATETIME:
        return "DateTime"
    return None


def famille_modele(colonne):
    type_ = colonne.type
    if isinstance(type_, sa.Date):
        return "Date"
    if isinstance(type_, sa.DateTime):
        return "DateTime"
    return None


def analyser(db: str):
    con = sqlite3.connect(db)
    cur = con.cursor()

    absentes, colonnes_manquantes = [], []
    notnull_imposes, defauts_orphelins, conflits_type = [], [], []
    surplus_inoffensifs = []

    for nom, table in sorted(Base.metadata.tables.items()):
        if not table_presente(cur, nom):
            absentes.append((nom, sorted(c.name for c in table.columns)))
            continue
        base = details_base(cur, nom)
        model_colonnes = {c.name: c for c in table.columns}

        manque = sorted(set(model_colonnes) - set(base))
        if manque:
            colonnes_manquantes.append((nom, manque))

        for nom_col in sorted(set(base) - set(model_colonnes)):
            type_sql, notnull, dflt = base[nom_col]
            if notnull and dflt is None:
                notnull_imposes.append((nom, nom_col, type_sql, "absente du modele"))
            else:
                surplus_inoffensifs.append((nom, nom_col))

        for nom_col, colonne in sorted(model_colonnes.items()):
            if nom_col not in base:
                continue
            type_sql, notnull, dflt = base[nom_col]
            a_un_defaut = colonne.server_default is not None
            if notnull and colonne.nullable and dflt is None and not a_un_defaut:
                notnull_imposes.append((nom, nom_col, type_sql, "nullable dans le modele"))
            if dflt is not None and not a_un_defaut:
                fm, fb = famille_modele(colonne), famille(type_sql)
                horodate = "TIME" in type_sql or "TIMESTAMP" in type_sql
                if fm == "Date" and horodate:
                    defauts_orphelins.append(
                        (nom, nom_col, dflt, "Date vs defaut horodate"))
                elif fb and fm and fb != fm:
                    conflits_type.append((nom, nom_col, fm, f"{fb} (defaut {dflt})"))
            else:
                fm, fb = famille_modele(colonne), famille(type_sql)
                if fb and fm and fb != fm:
                    conflits_type.append((nom, nom_col, fm, fb))

    con.close()
    return {
        "db": db,
        "absentes": absentes,
        "colonnes_manquantes": colonnes_manquantes,
        "notnull_imposes": notnull_imposes,
        "defauts_orphelins": defauts_orphelins,
        "conflits_type": conflits_type,
        "surplus_inoffensifs": surplus_inoffensifs,
    }


def _section(titre, elements, ligne):
    print("=" * 74)
    print(f"{titre} ({len(elements)})")
    print("=" * 74)
    for element in elements:
        print("   " + ligne(element))
    print()


def afficher(r):
    print(f"base analysee : {r['db']}")
    print(f"tables declarees par les modeles : {len(Base.metadata.tables)}")
    print()
    _section("1. TABLES ABSENTES DE LA BASE", r["absentes"],
             lambda e: f"{e[0]}  ({len(e[1])} colonnes attendues)")
    _section("2. COLONNES DU MODELE ABSENTES DE LA BASE (erreur SQL garantie)",
             r["colonnes_manquantes"],
             lambda e: f"{e[0]} : {' '.join(e[1])}")
    _section("3. NOT NULL IMPOSEES PAR LA BASE, NON ALIMENTEES PAR LE MODELE "
             "(INSERT impossible)", r["notnull_imposes"],
             lambda e: f"{e[0]}.{e[1]} [{e[2]}] - {e[3]}")
    _section("4. DEFAULTS EN BASE SANS EQUIVALENT DANS LE MODELE "
             "(relecture de la valeur apres INSERT)", r["defauts_orphelins"],
             lambda e: f"{e[0]}.{e[1]} defaut={e[2]} - {e[3]}")
    _section("5. DESACCORDS DE TYPE Date / DateTime", r["conflits_type"],
             lambda e: f"{e[0]}.{e[1]} : modele={e[2]} base={e[3]}")
    _section("6. COLONNES EN SURPLUS DANS LA BASE (inoffensives)",
             r["surplus_inoffensifs"], lambda e: f"{e[0]}.{e[1]}")

    critiques = (len(r["absentes"]) + len(r["colonnes_manquantes"])
                 + len(r["notnull_imposes"]) + len(r["defauts_orphelins"])
                 + len(r["conflits_type"]))
    print("VERDICT : " + (
        f"{critiques} divergence(s) bloquante(s) : ces tables font echouer une "
        "lecture, une ecriture ou une relecture."
        if critiques else
        "parite complete : aucun modele ne reclame une colonne absente, aucune "
        "contrainte NOT NULL n'entrave une ecriture, aucun defaut ne heurte un "
        "type."
    ))


def rejouer_chaine() -> str:
    """Reconstruit une base sqlite vierge en rejouant toute la chaine Alembic.

    C'est la seule facon de voir le schema que la production possede vraiment :
    en production create_all() est desactive (app/main.py), le schema vient
    EXCLUSIVEMENT des migrations.
    """
    chemin = Path(tempfile.gettempdir()) / "kamlog_replay.db"
    if chemin.exists():
        chemin.unlink()
    import os
    environ = dict(os.environ, DATABASE_URL=f"sqlite:///{chemin}")
    subprocess.run([sys.executable, "-m", "alembic", "upgrade", "head"],
                   cwd=str(ROOT), env=environ, check=True,
                   stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    return str(chemin)


if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == "--replay":
        cible = rejouer_chaine()
    elif len(sys.argv) > 1:
        cible = sys.argv[1]
    else:
        cible = str(ROOT / "kamlog_erp.db")
    afficher(analyser(cible))
