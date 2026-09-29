"""Test du heal_schema : simule le bug prod (colonne `users` absente) puis
verifie que ensure_login_railway.py la detecte (--check) et la restaure."""
import shutil
import sqlite3
import subprocess
import sys

SRC = "_ci_replay_clean.db"
DST = "_scratch_heal.db"
DROP_COL = "two_factor_recovery_codes"  # colonne modele ajoutee tard (026)


def cols(db):
    con = sqlite3.connect(db)
    try:
        return [r[1] for r in con.execute("PRAGMA table_info(users)")]
    finally:
        con.close()


def drop_column(db, col):
    con = sqlite3.connect(db)
    try:
        con.execute(f'ALTER TABLE users DROP COLUMN "{col}"')
        con.commit()
    finally:
        con.close()


shutil.copy(SRC, DST)
before = cols(DST)
print(f"colonnes users AVANT : {len(before)} ; {DROP_COL} present = {DROP_COL in before}")
assert DROP_COL in before, "colonne de test absente du replay -- change DROP_COL"

drop_column(DST, DROP_COL)
missing_now = DROP_COL not in cols(DST)
print(f"apres DROP : {DROP_COL} present = {not missing_now} (attendu False)")

import os
env = dict(os.environ, DATABASE_URL=f"sqlite:///./{DST}", SECRET_KEY="testsecret")

print("\n--- ensure_login_railway.py --check ---")
subprocess.run([sys.executable, "-X", "utf8", "scripts/ensure_login_railway.py", "--check"], env=env)

print("\n--- ensure_login_railway.py (write) ---")
subprocess.run([sys.executable, "-X", "utf8", "scripts/ensure_login_railway.py"], env=env)

after = cols(DST)
print(f"\ncolonnes users APRES : {len(after)} ; {DROP_COL} restauree = {DROP_COL in after}")
assert DROP_COL in after, "ECHEC : la colonne n'a pas ete restauree"
print("OK : parite users restauree par le script.")
