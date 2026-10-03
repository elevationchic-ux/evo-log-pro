# -*- coding: utf-8 -*-
"""Verif rapide batch 24 : grants des roles concernes + etat pre-036."""
from app.core.permission_catalog import ROLE_GRANTS
from app.core.permissions import has_perm

codes = [
    "qhse.accident.read", "qhse.accident.create", "qhse.accident.modify",
    "qhse.rapport.read", "qhse.imdg.read", "qhse.permis.create",
    "qhse.enregistrement.delete", "qhse.controle.create", "qhse.risque.create",
]
for role in ("QHSE", "CHEF_EXPLOITATION", "AUDITEUR", "DIRECTEUR_GENERAL"):
    grants = next((g for g in ROLE_GRANTS if g[0] == role), None)
    if grants is None:
        print(role, ": ABSENT du catalogue")
        continue
    print(role, "level", grants[1], "nb_codes", len(grants[3]))
    print("   ", {c: has_perm(grants[3], c) for c in codes})
