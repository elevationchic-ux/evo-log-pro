# -*- coding: utf-8 -*-
"""Verif rapide batch 24 : import du routeur + compteurs."""
import io

import app.routers.v1.qhse as m

src = io.open("app/routers/v1/qhse.py", encoding="utf-8").read()
print("routes monte:", len(m.router.routes))
print("restes get_current_user:", src.count("get_current_user"))
print("Depends(require_perm(:", src.count("Depends(require_perm("))
