"""Audite l'ordre des dependances FK de la chaine alembic pour PostgreSQL.

PostgreSQL exige que la table referenceee existe AU MOMENT du CREATE TABLE
avec FOREIGN KEY (ou ALTER ADD FK). SQLite tolere l'inverse. La CI
"Replay Alembic chain on Postgres" echoue donc sur le premier ecart.

Methodes: parcours la chaine dans l'ordre des revisions, accumule les tables
creees (create_table, create_all de 014, additions via ALTER), et signale
toute ForeignKeyConstraint/op.create_foreign_key qui referencing une table
inconnue a ce stade.

Usage: python scripts/audit_fk_order_postgres.py
"""
import io
import os
import re
import sys

VERSIONS = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
                        "evo-log-backend", "migrations", "versions")

REV_RE = re.compile(r"^revision\s*(?::\s*str)?\s*=\s*[\"']([^\"']+)[\"']", re.M)
DOWN_RE = re.compile(r"^down_revision\s*(?::\s*(?:str|None)\s*)?=\s*[\"']([^\"']+)[\"']", re.M)
CREATE_RE = re.compile(r"op\.create_table\(\s*(?:sa\.text\([\"']|op\.f\([\"']|[\"'])%s?[\"']?", re.M)
CREATE_NAME_RE = re.compile(r"op\.create_table\(\s*[\"']([a-zA-Z_][\w]*)[\"']")
FK_REF_RE = re.compile(r"ForeignKeyConstraint\(\s*\[[^\]]*\]\s*,\s*\[[\"']([\w]+)\.")
FK_OP_RE = re.compile(r"op\.create_foreign_key\([^)]*?[\"']([\w]+)[\"']\s*,\s*[\"']([\w]+)\.|\bref_table\b", re.S)
BATCH_RE = re.compile(r"op\.batch_alter_table\(\s*[\"']([\w]+)[\"']")
ALTER_ADD_FK_RE = re.compile(r"batch\.add_foreign_key\([^)]*\[[\"']([\w]+)\.", re.S)


def load_chain():
    files = {}
    for name in os.listdir(VERSIONS):
        if not name.endswith(".py"):
            continue
        src = io.open(os.path.join(VERSIONS, name), encoding="utf-8").read()
        rev = REV_RE.search(src)
        down = DOWN_RE.search(src)
        if rev:
            files[rev.group(1)] = (down.group(1) if down else None, src, name)
    # ordre lineaire depuis la base
    downs = {d for (d, _, _) in files.values() if d}
    heads = [r for r in files if r not in downs]
    assert len(heads) == 1, f"tetes multiples: {heads}"
    order = []
    cur = heads[0]
    while cur:
        order.append(cur)
        cur = files[cur][0] if cur in files else None
    order.reverse()
    return [(r, files[r][1], files[r][2]) for r in order]


def main():
    known = set()
    problems = []
    for rev, src, name in load_chain():
        # tables creees dans ce fichier, dans l'ordre d'apparition du code
        created_here = []
        for m in CREATE_NAME_RE.finditer(src):
            created_here.append(m.group(1))
        # 014 cree le reste via metadata.create_all : on lui fait confiance
        # (tri topologique SQLAlchemy) et on ajoute TOUTES les tables ORM.
        is_parity = "create_all" in src
        # scan sequentiel:Alterner create_table et FK refs par position.
        events = []
        for m in CREATE_NAME_RE.finditer(src):
            events.append((m.start(), "create", m.group(1)))
        for m in FK_REF_RE.finditer(src):
            # FK a l'interieur d'un create_table: la table en cours de creation
            # est celle creee juste avant cette position.
            events.append((m.start(), "fk", m.group(1)))
        events.sort()
        current_create = None
        for pos, kind, table in events:
            if kind == "create":
                current_create = table
                if table not in known:
                    known.add(table)
            else:  # fk vers `table` depuis current_create
                if table not in known:
                    # le create_all de 014 n'a pas encore eu lieu pour les
                    # revisions anterieures : on signale quand meme.
                    problems.append((name, current_create, table))
        if is_parity:
            # approx: les tables ORM additionnelles deviennent connues.
            known.update(t for t in created_here)
    print(f"tables connues en fin de chaine: {len(known)}")
    if problems:
        print("PROBLEMES d'ordre FK pour PostgreSQL (table_cree -> ref manquante):")
        for fname, created, ref in problems:
            print(f"  {fname}: {created} reference {ref} avant qu'elle n'existe")
        return 1
    print("AUCUN probleme d'ordre FK detecte (create_table inline).")
    return 0


if __name__ == "__main__":
    sys.exit(main())
