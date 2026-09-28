"""Etat reel des colonnes a enum des tables RH : valeurs stockees + cotes
des codes Python qui les écrivent. Decide si le modele doit stocker le NOM
ou la VALEUR de l'Enum SQLAlchemy.
"""
import collections
import sqlite3
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
COLONNES = [
    ("conges", "statut"), ("conges", "type_conge"), ("absences", "type_absence"),
    ("salaires", "statut"), ("salaires", "date_paiement"), ("contrats_travail", "statut"),
    ("contrats_travail", "type_contrat"), ("primes", "type_prime"),
    ("participations_formation", "statut"), ("temps_travail", "statut"),
    ("absences", "date_debut"),
]

for nom in ("_replay.db", "kamlog_erp.db"):
    db = ROOT / nom
    if not db.exists():
        print("## %s : absente" % nom)
        continue
    con = sqlite3.connect(str(db))
    print("## %s" % nom)
    for table, col in COLONNES:
        presentes = {r[1] for r in con.execute("PRAGMA table_info(%s)" % table)}
        if not presentes:
            print("   %-26s : TABLE ABSENTE" % table)
            continue
        if col not in presentes:
            print("   %-26s : pas de colonne %s" % (table, col))
            continue
        vals = collections.Counter(
            r[0] for r in con.execute('select "%s" from "%s"' % (col, table)))
        print("   %-26s : %s" % ("%s.%s" % (table, col), dict(vals.most_common(6))))
    con.close()

print()
print("## ecritures Python (extrait)")
for motif in ("StatutConge.", "TypeConge.", 'statut="', "statut='", 'type_conge='):
    r = subprocess.run(
        ["git", "grep", "-n", "--", motif, "app", "scripts"],
        cwd=str(ROOT), capture_output=True, text=True)
    lignes = [l for l in r.stdout.splitlines() if "models/rh.py" not in l]
    print("--- %s  (%d lignes)" % (motif, len(lignes)))
    for l in lignes[:25]:
        print("   " + l[:160])
