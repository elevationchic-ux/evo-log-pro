# -*- coding: utf-8 -*-
"""Repro seed double : la Mission survit-elle a un second seed ?"""
import sys
sys.path.insert(0, ".")
sys.path.insert(0, r"..\scripts")

import sqlite3
from scratch_smoke_xmod import seed

def raw(label):
    con = sqlite3.connect("kamlog_erp.db")
    print(label,
          "missions=", con.execute("select id,reference,company_id from missions").fetchall(),
          "commandes=", con.execute("select id,reference,company_id from commandes").fetchall())
    con.close()

raw("run0:")
ids1 = seed()
raw("apres seed1:")
print("ids1:", ids1)
ids2 = seed()
raw("apres seed2:")
print("ids2:", ids2)
