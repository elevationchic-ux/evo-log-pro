"""Liste les tables RH presentes en base et les noms proches, pour verifier
les __tablename__ des modeles (ex: participations_formations vs participations_formation).
"""
import sqlite3
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DB = ROOT / (sys.argv[1] if len(sys.argv) > 1 else "_replay.db")
conn = sqlite3.connect(str(DB))
rows = [r[0] for r in conn.execute(
    "SELECT name FROM sqlite_master WHERE type='table' ORDER BY name")]
for frag in ("formation", "competence", "organigramme", "evaluation", "prime",
             "salaire", "conge", "absence", "contrat", "document_employe", "temps"):
    print("%-18s -> %s" % (frag, [t for t in rows if frag in t]))
conn.close()
