# -*- coding: utf-8 -*-
"""Repro: une Mission inseree via ORM survit-elle au commit ?"""
import sys
from datetime import datetime
sys.path.insert(0, ".")

import app.models
import app.models.acconage  # noqa
from app.core.database import SessionLocal
from app.models.transport import Mission
from app.models.tiers import Client

db = SessionLocal()
m = db.query(Mission).filter(Mission.reference == "MIS-SMOKE-1").first()
print("avant:", m)
if not m:
    client = db.query(Client).first()
    m = Mission(reference="MIS-SMOKE-1", client_id=client.id if client else None,
                type_mission="livraison", numero_bl="B/L-SMOKE-1",
                point_depart="Douala Port", point_arrivee="Yaounde",
                date_debut_prevue=datetime.utcnow(), company_id=1)
    db.add(m)
    db.commit()
    print("id apres commit:", m.id)
else:
    print("existe deja, company_id =", m.company_id)
db.close()

# relecture fraiche
db2 = SessionLocal()
print("relecture ORM:", db2.query(Mission).filter(Mission.reference == "MIS-SMOKE-1").first())
db2.close()

import sqlite3
con = sqlite3.connect("kamlog_erp.db")
print("relecture brute:", con.execute("select id,reference,company_id from missions").fetchall())
con.close()
