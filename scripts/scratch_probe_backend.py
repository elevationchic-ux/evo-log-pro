# -*- coding: utf-8 -*-
"""Probe backend: login then GET key list endpoints, print shape."""
import json
import urllib.request

BASE = "http://127.0.0.1:8000"


def call(path, token=None, method="GET"):
    req = urllib.request.Request(BASE + path, method=method)
    if token:
        req.add_header("Authorization", f"Bearer {token}")
    try:
        with urllib.request.urlopen(req, timeout=15) as r:
            data = json.loads(r.read().decode())
            if isinstance(data, dict):
                keys = list(data.keys())[:8]
                n = data.get("total", data.get("count"))
                items = data.get("items")
                extra = f" keys={keys} total={n}"
                if isinstance(items, list):
                    extra += f" items=list({len(items)})"
                return f"dict {extra}"
            return f"list len={len(data)}"
    except Exception as e:
        return f"ERR {e}"


body = json.dumps({"username": "admin@evolog.cm", "password": "admin123"}).encode()
req = urllib.request.Request(BASE + "/api/v1/auth/login", data=body, method="POST")
req.add_header("Content-Type", "application/json")
with urllib.request.urlopen(req, timeout=15) as r:
    token = json.loads(r.read().decode())["access_token"]

for p in [
    "/api/v1/tiers",
    "/api/v1/master-data/tiers",
    "/api/v1/magasin/articles",
    "/api/v1/rh/employes",
    "/api/v1/finance/kpis",
    "/api/v1/magasin/kpis",
    "/api/v1/notifications?limit=10",
    "/api/v1/notifications/stats",
    "/api/v1/magasin/magasins",
    "/api/v1/magasin/ordres-transfert",
    "/api/v1/magasin-douane/declarations",
    "/api/v1/transport/chauffeurs",
    "/api/v1/transport/missions",
]:
    print(f"{p:45s} -> {call(p, token)}")
