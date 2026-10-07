# -*- coding: utf-8 -*-
"""Sonde rapide : état de la base dev + latence des endpoints vocabulaires."""
import os
import sqlite3
import sys
import time
import json
import urllib.request
import urllib.error

HERE = os.path.dirname(os.path.abspath(__file__))
DB = os.path.join(HERE, "kamlog_erp.db")

c = sqlite3.connect(DB, timeout=5)
cur = c.cursor()
cur.execute("select name from sqlite_master where type='table'")
tables = {r[0] for r in cur.fetchall()}
print("total tables:", len(tables))
tpl = sorted(t for t in tables if t.startswith("tpl"))
print("tpl tables:", tpl)
if "tpl_crossdocks" in tables:
    cur.execute("select count(*) from tpl_crossdocks")
    print("tpl_crossdocks rows:", cur.fetchone()[0])
# expansion tables manquantes vs ORM
cur.execute("select name from sqlite_master where type='table' and name like '%s'" % "alembic%")
print("alembic:", cur.fetchall())
try:
    cur.execute("select version_num from alembic_version")
    print("alembic versions:", cur.fetchall())
except Exception as e:
    print("alembic_version err:", e)
c.close()

print("wal size:", os.path.getsize(DB + "-wal") if os.path.exists(DB + "-wal") else 0)

BASE = "http://localhost:8000"


def req(path, token=None):
    url = BASE + path
    r = urllib.request.Request(url)
    if token:
        r.add_header("Authorization", "Bearer " + token)
    t0 = time.time()
    try:
        resp = urllib.request.urlopen(r, timeout=30)
        body = resp.read()[:120]
        return resp.status, round(time.time() - t0, 2), body
    except urllib.error.HTTPError as e:
        return e.code, round(time.time() - t0, 2), e.read()[:200]
    except Exception as e:
        return "ERR", round(time.time() - t0, 2), repr(e)[:160]


# login
for creds in [{"username": "admin@kamlog.cm", "password": "Admin@2024"},
              {"username": "admin", "password": "admin123"},
              {"username": "superadmin", "password": "Super@2024"}]:
    st, dt, body = req("/api/v1/auth/login")  # placeholder GET to measure
    break

t0 = time.time()
r = urllib.request.Request(BASE + "/api/v1/auth/login")
r.add_header("Content-Type", "application/json")
token = None
used = None
for creds in [{"username": "admin@kamlog.cm", "password": "Admin@2024"},
              {"username": "admin", "password": "Admin@2024"},
              {"username": "admin", "password": "admin123"}]:
    try:
        rr = urllib.request.urlopen(urllib.request.Request(BASE + "/api/v1/auth/login",
                data=json.dumps(creds).encode(), headers={"Content-Type": "application/json"}), timeout=30)
        d = json.loads(rr.read())
        token = d.get("access_token") or (d.get("data") or {}).get("access_token")
        used = creds["username"]
        print("login OK", creds, round(time.time() - t0, 2), "s")
        break
    except Exception as e:
        print("login fail", creds["username"], repr(e)[:100])
if not token:
    print("NO TOKEN")
    sys.exit(1)

paths = [
    "/health",
    "/api/v1/logistique-3pl/nomenclatures",
    "/api/v1/logistique-3pl/tpl-crossdocks",
    "/api/v1/logistique-3pl/tpl-contracts",
]
for p in paths:
    print(p, req(p, token))
