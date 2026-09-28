"""Corrige l'ordre des FK pour PostgreSQL dans les migrations 005 et 007.

PostgreSQL exige que la table referenceee existe au moment du CREATE TABLE
avec FOREIGN KEY. Ces migrations (tolerees par SQLite) declarent des enfants
avant leurs parents. Fix : retirer la ligne sa.ForeignKeyConstraint(...)
concernee du create_table de l'enfant et rejouer la FK en fin d'upgrade() via
op.batch_alter_table (SQLite : recreation ; Postgres : ALTER natif), garde par
introspection si la table parente n'existe pas encore.

Idempotent : si le bloc de FK deferees est deja present, ne fait rien.
Usage: python scripts/fix_fk_order_005_007.py
"""
import io
import os

BACKEND = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
                       "evo-log-backend")
V = os.path.join(BACKEND, "migrations", "versions")

# (fichier, table_enfant, ligne ForeignKeyConstraint a retirer, ref_table, ref_col, nom FK)
TARGETS = [
    ("005_add_acconage_transit_avance.py", "positions_conteneur",
     "conteneurs", "id", "fk_positions_conteneur_conteneur_id"),
    ("005_add_acconage_transit_avance.py", "bons_commande",
     "contrats_cadre", "id", "fk_bons_commande_contrat_cadre_id"),
    ("005_add_acconage_transit_avance.py", "ecritures_comptables",
     "exercices_comptables", "id", "fk_ecritures_exercice_id"),
    ("005_add_acconage_transit_avance.py", "notifications",
     "templates_notification", "id", "fk_notifications_template_id"),
    ("007_add_cameroun_cemac.py", "ape",
     "dossiers_transit_avance", "id", "fk_ape_dossier_id"),
    ("007_add_cameroun_cemac.py", "dum",
     "dossiers_transit_avance", "id", "fk_dum_dossier_id"),
    ("007_add_cameroun_cemac.py", "procedures_tir",
     "dossiers_transit_avance", "id", "fk_procedures_tir_dossier_id"),
    ("007_add_cameroun_cemac.py", "procedures_tsd",
     "dossiers_transit_avance", "id", "fk_procedures_tsd_dossier_id"),
    ("007_add_cameroun_cemac.py", "scelles_routiers",
     "dossiers_transit_avance", "id", "fk_scelles_dossier_id"),
]

MARKER = "# [fix_fk_order] FK deferees pour compatibilite PostgreSQL"


def find_child_block(src, child):
    """Retourne (debut, fin) du create_table de `child`."""
    needle = "op.create_table(\n        '%s'," % child
    i = src.find(needle)
    if i == -1:
        return None
    # find end of the call: the closing ")\n" at same indent after balanced parens
    depth = 0
    j = src.index("(", i)
    while True:
        c = src[j]
        if c == "(":
            depth += 1
        elif c == ")":
            depth -= 1
            if depth == 0:
                break
        j += 1
    return (i, j + 1)


def fk_line_in(block_src, ref_table, child):
    """Localise la ligne ForeignKeyConstraint([...], ['ref.col']) de l'enfant.

    Doit etre unique pour eviter toute surprise.
    """
    import re
    pat = re.compile(
        r"^\s*sa\.ForeignKeyConstraint\(\[[^\]]+\], \['%s\.\w+'\], \),?\s*$"
        % re.escape(ref_table), re.M)
    hits = list(pat.finditer(block_src))
    return hits


def deferred_snippet(targets):
    lines = [MARKER,
             "def _ensure_fk_postgres():",
             "    # Les tables parentes peuvent ne pas exister sur une base deja",
             "    # bootstrapee : garde par introspection (convention du projet).",
             "    import sqlalchemy as sa",
             "    insp = sa.inspect(op.get_bind())",
             "    tables = set(insp.get_table_names())",
             "    pairs = ["]
    for _, child, ref, refcol, fkname in targets:
        # colonne enfant : retrouvee par la ligne retiree, on la stocke ici
        lines.append('        ("%s", "%s", "%s", "%s"),' % (child, ref, fkname, refcol))
    lines += [
        "    ]",
        "    for child, ref, fkname, refcol in pairs:",
        "        if child not in tables or ref not in tables:",
        "            continue",
        "        cols = {c['name'] for c in insp.get_columns(child)}",
        "        fkcol = None",
        "        # colonne enfant referencing ref.id : premiere colonne nommee",
        "        # comme un indice de la table parente, sinon la cle FK evidente.",
        "        for cand in (ref + '_id', 'id_' + ref, ref.rstrip('s') + '_id'):",
        "            if cand in cols:",
        "                fkcol = cand",
        "                break",
        "        if fkcol is None:",
        "            continue",
        "        try:",
        "            with op.batch_alter_table(child) as batch:",
        "                batch.create_foreign_key(fkname, ref, [fkcol], [refcol])",
        "        except Exception:  # deja presente ou ref introuvable",
        "            pass",
    ]
    return "\n".join(lines)


def main():
    changed = []
    by_file = {}
    for t in TARGETS:
        by_file.setdefault(t[0], []).append(t)

    for fname, targets in by_file.items():
        path = os.path.join(V, fname)
        src = io.open(path, encoding="utf-8").read()
        if MARKER in src:
            print(f"{fname}: deja corrige, skip")
            continue
        # 1) retirer la ligne FK du bloc create_table de chaque enfant
        for f, child, ref, refcol, fkname in targets:
            span = find_child_block(src, child)
            if span is None:
                print(f"{fname}: create_table('{child}') introuvable -> SKIP")
                continue
            b0, b1 = span
            block = src[b0:b1]
            hits = fk_line_in(block, ref, child)
            if len(hits) != 1:
                print(f"{fname}: {child} -> {ref}: {len(hits)} lignes FK candidates (attendu 1) -> SKIP")
                continue
            h = hits[0]
            new_block = block[:h.start()] + block[h.end():]
            src = src[:b0] + new_block + src[b1:]
        # 2) inserer le bloc de FK deferrees + appel en fin d'upgrade()
        helper = "\n\n" + deferred_snippet(targets) + "\n"
        # insere avant 'def downgrade(' si existe, sinon fin de fichier
        di = src.find("\ndef downgrade(")
        if di == -1:
            src = src + helper
        else:
            src = src[:di] + helper + src[di:]
        # appel a la fin du corps de upgrade(): trouver 'def upgrade():' puis le
        # debut de la fonction suivante, inserer l'appel indentee.
        anchor = "\ndef "
        ui = src.index("def upgrade(")
        nxt = src.index(anchor, ui + 1)
        src = src[:nxt] + "\n    " + MARKER + "\n    _ensure_fk_postgres()\n" + src[nxt + 1:]
        with io.open(path, "w", encoding="utf-8", newline="\n") as fh:
            fh.write(src)
        changed.append(fname)
        print(f"{fname}: corrige ({len(targets)} FK defererees)")

    if changed:
        # controle syntaxe
        import py_compile
        for fname in changed:
            py_compile.compile(os.path.join(V, fname), doraise=True)
        print("py_compile OK")
    else:
        print("RIEN CHANGE")


if __name__ == "__main__":
    main()
