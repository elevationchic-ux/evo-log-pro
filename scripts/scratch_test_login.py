# -*- coding: utf-8 -*-
import json
import urllib.request

body = json.dumps({"username": "admin@evolog.cm", "password": "admin123"}).encode()
req = urllib.request.Request(
    "http://127.0.0.1:8000/api/v1/auth/login",
    data=body,
    headers={"Content-Type": "application/json"},
    method="POST",
)
try:
    with urllib.request.urlopen(req, timeout=15) as r:
        print("HTTP", r.status)
        print(r.read().decode()[:400])
except Exception as e:
    print("ERR", e)
    try:
        print(e.read().decode()[:600])
    except Exception:
        pass
