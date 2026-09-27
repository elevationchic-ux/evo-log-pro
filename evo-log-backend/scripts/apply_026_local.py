"""Applique localement les colonnes 2FA de la migration 026.

Le schéma de production est piloté par Alembic ; ce fichier ne fait que
reproduire, sur la base de développement sqlite, l'effet idempotent de
migrations/versions/026_add_2fa_recovery_codes.py, dont la chaîne de versions
locale est figée en 004 (le schéma local vient de create_all, pas d'Alembic).
"""
import sqlite3

CONNEXION = "kamlog_erp.db"

CIBLES = [
    ("two_factor_recovery_codes", "TEXT"),
    ("two_factor_recovery_issued_at", "DATETIME"),
]


def colonnes(cur):
    return {r[1] for r in cur.execute("PRAGMA table_info(users)")}


def main():
    con = sqlite3.connect(CONNEXION)
    cur = con.cursor()
    existantes = colonnes(cur)
    for nom, type_sql in CIBLES:
        if nom in existantes:
            print(f"present: {nom}")
            continue
        cur.execute(f"ALTER TABLE users ADD COLUMN {nom} {type_sql}")
        print(f"added: {nom} {type_sql}")
    con.commit()
    print("users 2fa cols:", sorted(x for x in colonnes(cur) if "two_factor" in x))
    con.close()


if __name__ == "__main__":
    main()
