# -*- coding: utf-8 -*-
"""Expeience honnete batch 24 : etat reel des liens role QHSE avant/apres 036."""
import os
import tempfile

from alembic import command
from alembic.config import Config
from pathlib import Path

BACKEND = Path(__file__).resolve().parents[1]
tmp = tempfile.mkdtemp()
url = f"sqlite:///{os.path.join(tmp, 'mig.db')}"
os.environ["DATABASE_URL"] = url

cfg = Config(str(BACKEND / "alembic.ini"))
cfg.set_main_option("script_location", str(BACKEND / "migrations"))

import sqlalchemy as sa

command.upgrade(cfg, "035_rbac_acconage_grants")
eng = sa.create_engine(url)
with eng.connect() as c:
    rid = c.exec_driver_sql("SELECT id FROM roles WHERE name='QHSE'").first()
    print("role QHSE apres 035 :", rid)
    if rid:
        rows = c.exec_driver_sql(
            "SELECT p.code FROM role_permissions rp JOIN permissions p ON p.id=rp.permission_id "
            "WHERE rp.role_id=%d AND p.code LIKE 'qhse%%'" % rid[0]).fetchall()
        print("  liens qhse:", len(rows), [r[0] for r in rows][:6])

command.upgrade(cfg, "head")
with eng.connect() as c:
    rid = c.exec_driver_sql("SELECT id FROM roles WHERE name='QHSE'").first()
    rows = c.exec_driver_sql(
        "SELECT p.code FROM role_permissions rp JOIN permissions p ON p.id=rp.permission_id "
        "WHERE rp.role_id=%d AND p.code LIKE 'qhse%%'" % rid[0]).fetchall()
    codes = sorted(r[0] for r in rows)
    print("role QHSE apres 036 : liens qhse =", len(codes))
    print("  ", codes[:8], "...")
    n_all = c.exec_driver_sql(
        "SELECT COUNT(*) FROM role_permissions WHERE role_id=%d" % rid[0]).scalar()
    print("  liens totaux:", n_all)
    aud = c.exec_driver_sql("SELECT id FROM roles WHERE name='AUDITEUR'").first()
    if aud:
        n_a = c.exec_driver_sql(
            "SELECT COUNT(*) FROM role_permissions rp JOIN permissions p ON p.id=rp.permission_id "
            "WHERE rp.role_id=%d AND p.code LIKE 'qhse%%'" % aud[0]).scalar()
        print("  AUDITEUR liens qhse:", n_a)
eng.dispose()
print("OK tmp:", tmp)
