# Diagnostic one-shot (batch 15) : recherche de residus de tests dans la base de dev.
# Lit une COPIE (jamais le fichier actif). Aucune ecriture.
# Usage: python scripts/scratch_dev_db_residue.py [db_path]
import re
import sqlite3
import sys

DB = sys.argv[1] if len(sys.argv) > 1 else "kamlog_erp.db.bak-pre-b15"

# Signatures issues des suites pytest (vues dans tests/ et conftest) :
# emails/usernames/codes inventes par les fixtures, jamais par seed_data.py.
PATTERNS = [
    r"@test\.local$",
    r"@example\.com$",
    r"@test\.",
    r"^sonde",           # sonde-admin, Sonde SARL, code SONDE
    r"^sahttp",
    r"\bacme\b",
    r"^tenant?-?test",
    r"^test[-_]",
    r"[-_]test$",
    r"^fake",
    r"^demo[-_]",
    r"pas@pas",
]
RE = re.compile("|".join(PATTERNS), re.IGNORECASE)


def main() -> int:
    con = sqlite3.connect(f"file:{DB}?mode=ro", uri=True)
    con.row_factory = sqlite3.Row
    tables = [r[0] for r in con.execute(
        "SELECT name FROM sqlite_master WHERE type='table' AND name NOT LIKE 'sqlite_%' ORDER BY name")]
    total_hits = 0
    empty_tables = []
    for t in tables:
        try:
            n = con.execute(f"SELECT COUNT(*) FROM [{t}]").fetchone()[0]
        except sqlite3.Error as e:
            print(f"!! {t}: {e}")
            continue
        if n == 0:
            empty_tables.append(t)
            continue
        cols = [r[1] for r in con.execute(f"PRAGMA table_info([{t}])")]
        text_cols = [c for c in cols]
        hits = []
        for row in con.execute(f"SELECT rowid, * FROM [{t}] LIMIT 20000"):
            for c in text_cols:
                v = row[c]
                if isinstance(v, str) and RE.search(v):
                    hits.append((row[0], c, v[:60]))
                    break
        if hits:
            total_hits += len(hits)
            print(f"== {t} ({n} rows): {len(hits)} suspicion(s)")
            for rowid, c, v in hits[:12]:
                print(f"   rowid={rowid} {c}={v!r}")
            if len(hits) > 12:
                print(f"   ... +{len(hits) - 12} autres")
    print(f"\nTOTAL suspicions: {total_hits}")
    print(f"Tables vides: {len(empty_tables)}/{len(tables)}")
    nonzero = [(t, con.execute(f'SELECT COUNT(*) FROM [{t}]').fetchone()[0])
               for t in tables if t not in empty_tables]
    print("Tables non vides:", ", ".join(f"{t}={n}" for t, n in nonzero))
    return 0


if __name__ == "__main__":
    sys.exit(main())
