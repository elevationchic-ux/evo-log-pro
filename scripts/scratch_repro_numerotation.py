# -*- coding: utf-8 -*-
"""Repro lookup numerotation avec tenant actif."""
import sys
sys.path.insert(0, ".")

import app.models
import app.models.acconage  # noqa
from app.core.database import SessionLocal
from app.core import tenant_context
from app.models.numerotation import SequenceNumerotation

tenant_context.set_current_tenant(1)
print("enforcement active:", tenant_context.is_enforcement_active())

db = SessionLocal()
seq = (
    db.query(SequenceNumerotation)
    .filter(
        SequenceNumerotation.company_id == 1,
        SequenceNumerotation.type_document == "REGLEMENT",
        SequenceNumerotation.exercice == 2026,
    )
    .first()
)
print("lookup avec tenant:", seq)

str_sql = str(db.query(SequenceNumerotation).filter(
    SequenceNumerotation.company_id == 1,
    SequenceNumerotation.type_document == "REGLEMENT",
    SequenceNumerotation.exercice == 2026).statement)
print("SQL genere :\n", str_sql)
db.close()
