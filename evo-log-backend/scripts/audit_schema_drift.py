"""Audit du drift entre les modeles SQLAlchemy et les tables reellement en base.

Une classe remaniee sans migration (colonnes renommees, ajoutees, retirees) laisse
le routeur et le service parler le langage de la table : la requete part avec des
colonnes qui n'existent pas et la page meurt en 500 « Internal Server Error » sans
qu'aucun audit frontend/backend ne le voie. Ce script compare, table par table,
les colonnes declarees par les modeles a celles presentes dans la base.

Usage :
    python scripts/audit_schema_drift.py [chemin/vers/base.db]
    (defaut : la valeur d'URLALCHEMY_DATABASE dans app.core.config)
"""
from __future__ import annotations

import sqlite3
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from app.core.database import Base  # noqa: E402
import app.models  # noqa: F401,E402  (enregistre toutes les tables)


def colonnes_base(cur, table: str):
    try:
        return {r[1] for r in cur.execute(f'PRAGMA table_info("{table}")')}
    except sqlite3.Error:
        return None


def main():
    db = sys.argv[1] if len(sys.argv) > 1 else str(ROOT / "kamlog_erp.db")
    con = sqlite3.connect(db)
    cur = con.cursor()

    absentes, derives = [], []
    for table in sorted(Base.metadata.tables):
        modele = Base.metadata.tables[table]
        veut = {c.name for c in modele.columns}
        reel = colonnes_base(cur, table)
        if reel is None:
            absentes.append((table, sorted(veut)))
            continue
        manque = veut - reel
        surplus = reel - veut
        if manque or surplus:
            derives.append((table, sorted(manque), sorted(surplus)))

    print(f"base analysee : {db}")
    print(f"tables declarees par les modeles : {len(Base.metadata.tables)}")
    print()
    print("=" * 72)
    print(f"TABLES ABSENTES DE LA BASE ({len(absentes)})")
    print("=" * 72)
    for table, cols in absentes:
        print(f"   {table}  ({len(cols)} colonnes attendues)")

    print()
    print("=" * 72)
    print(f"DRIFT DE COLONNES ({len(derives)})")
    print("=" * 72)
    for table, manque, surplus in derives:
        print(f"\n   {table}")
        if manque:
            print(f"      modele seulement : {' '.join(manque)}")
        if surplus:
            print(f"      base seulement   : {' '.join(surplus)}")

    con.close()


if __name__ == "__main__":
    main()
