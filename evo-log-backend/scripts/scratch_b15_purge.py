# Scratch batch 15 : purge des lignes audit_logs creees par pytest dans la base de dev.
# Cible exclusive : url LIKE 'http://testserver%' (host fixe de fastapi TestClient).
# Les lignes reelles (127.0.0.1:8000, localhost:8000 = usage dev / load_test.py) sont CONSERVEES.
# Defaut = dry-run ; --apply pour executer. Backup requis: kamlog_erp.db.bak-pre-b15.
import os
import sqlite3
import sys

APPLY = "--apply" in sys.argv
DB = "kamlog_erp.db"
BACKUP = "kamlog_erp.db.bak-pre-b15"
PREDICATE = "url LIKE 'http://testserver%'"

if not os.path.exists(BACKUP):
    print(f"ABORT: backup {BACKUP} manquant  ne pas purger sans filet.")
    sys.exit(2)

con = sqlite3.connect(DB, timeout=15)
total = con.execute("SELECT COUNT(*) FROM audit_logs").fetchone()[0]
doomed = con.execute(f"SELECT COUNT(*) FROM audit_logs WHERE {PREDICATE}").fetchone()[0]
kept = total - doomed
print(f"audit_logs total={total} testserver={doomed} a conserver={kept}")

if not APPLY:
    print("DRY-RUN  rien n'a ete supprime. Relancer avec --apply.")
    sys.exit(0)

con.execute(f"DELETE FROM audit_logs WHERE {PREDICATE}")
con.commit()
after = con.execute("SELECT COUNT(*) FROM audit_logs").fetchone()[0]
assert after == kept, f"invariant viole: {after} != {kept}"
con.execute("VACUUM")
ok = con.execute("PRAGMA integrity_check").fetchone()[0]
con.close()
print(f"PURGE OK: {total} -> {after} lignes, integrity_check={ok}")
