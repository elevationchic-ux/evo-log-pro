# -*- coding: utf-8 -*-
"""Smoke test wave 5 : 42 endpoints expansion (pipeline/courier/coldchain/heavylift).

Pour chaque route :
  GET /list -> attend 200 (vide ou pas)
  POST /create avec unique-field -> attend 201
  PUT /{id} avec champ non-unique -> attend 200
  DELETE /{id} -> attend 200 (soft delete via is_active)

Exerce egalement /nomenclatures par module.
"""
import json
import sys
import urllib.request
import urllib.error

BASE = "http://127.0.0.1:8000"
try:
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
except Exception:
    pass


def login():
    body = json.dumps({"username": "admin@evolog.cm", "password": "admin123"}).encode()
    req = urllib.request.Request(BASE + "/api/v1/auth/login", data=body,
                                 headers={"Content-Type": "application/json"}, method="POST")
    with urllib.request.urlopen(req, timeout=45) as r:
        data = json.loads(r.read().decode())
    return data.get("access_token") or data.get("token")


def call(method, path, token, body=None):
    url = BASE + path
    data = json.dumps(body).encode() if body is not None else None
    headers = {"Content-Type": "application/json"}
    if token:
        headers["Authorization"] = "Bearer " + token
    req = urllib.request.Request(url, data=data, headers=headers, method=method)
    try:
        with urllib.request.urlopen(req, timeout=60) as r:
            return r.status, r.read().decode()[:220]
    except urllib.error.HTTPError as e:
        return e.code, e.read().decode()[:220]
    except Exception as e:
        return "ERR", str(e)[:220]


# (module_prefix, sub_path, unique_field, seed_value)
SUBMODULES = [
    # Pipeline /api/v1/pipeline-oleoduc
    ("/api/v1/pipeline-oleoduc", "sections", "code_section", "PIP-SMOKE-S1"),
    ("/api/v1/pipeline-oleoduc", "pump-stations", "code_station", "PS-SMOKE-1"),
    ("/api/v1/pipeline-oleoduc", "storage-tanks", "code_cuve", "CT-SMOKE-1"),
    ("/api/v1/pipeline-oleoduc", "metering-points", "code_point", "MP-SMOKE-1"),
    ("/api/v1/pipeline-oleoduc", "product-batches", "numero_lot", "LOT-SMOKE-1"),
    ("/api/v1/pipeline-oleoduc", "pressure-readings", "reference", "PR-SMOKE-1"),
    ("/api/v1/pipeline-oleoduc", "leak-detections", "reference", "LD-SMOKE-1"),
    ("/api/v1/pipeline-oleoduc", "maintenance-works", "reference", "PW-SMOKE-1"),
    ("/api/v1/pipeline-oleoduc", "injection-campaigns", "reference", "IC-SMOKE-1"),
    ("/api/v1/pipeline-oleoduc", "ship-nominations", "reference", "SN-SMOKE-1"),
    # Courier /api/v1/courier-express
    ("/api/v1/courier-express", "parcels", "numero_colis", "PK-SMOKE-1"),
    ("/api/v1/courier-express", "waybills", "numero_lse", "LSE-SMOKE-1"),
    ("/api/v1/courier-express", "hubs", "code_hub", "HUB-SMOKE-1"),
    ("/api/v1/courier-express", "delivery-zones", "code_zone", "DZ-SMOKE-1"),
    ("/api/v1/courier-express", "routes", "code_tournee", "RT-SMOKE-1"),
    ("/api/v1/courier-express", "couriers", "code_coursier", "CR-SMOKE-1"),
    ("/api/v1/courier-express", "pods", "reference_pod", "POD-SMOKE-1"),
    ("/api/v1/courier-express", "slas", "code_sla", "SLA-SMOKE-1"),
    ("/api/v1/courier-express", "lockers", "code_locker", "LK-SMOKE-1"),
    ("/api/v1/courier-express", "vehicules", "plaque", "PLQ-SMOKE-1"),
    ("/api/v1/courier-express", "tarifs", "code_tarif", "TRF-SMOKE-1"),
    ("/api/v1/courier-express", "exceptions", "reference", "EX-SMOKE-1"),
    # Cold chain /api/v1/chaine-froid
    ("/api/v1/chaine-froid", "chambers", "code_chambre", "CC-SMOKE-1"),
    ("/api/v1/chaine-froid", "reefers", "numero_reefer", "RF-SMOKE-1"),
    ("/api/v1/chaine-froid", "loggers", "numero_logger", "LG-SMOKE-1"),
    ("/api/v1/chaine-froid", "products", "code_sku", "SKU-SMOKE-1"),
    ("/api/v1/chaine-froid", "excursions", "reference", "EXC-SMOKE-1"),
    ("/api/v1/chaine-froid", "vaccin-batches", "numero_lot", "VB-SMOKE-1"),
    ("/api/v1/chaine-froid", "haccp-records", "reference", "HCC-SMOKE-1"),
    ("/api/v1/chaine-froid", "defrost-cycles", "reference", "DFC-SMOKE-1"),
    ("/api/v1/chaine-froid", "energy-meters", "code_compteur", "EM-SMOKE-1"),
    ("/api/v1/chaine-froid", "transport-legs", "reference", "LGT-SMOKE-1"),
    # Heavy lift /api/v1/convoi-exceptionnel
    ("/api/v1/convoi-exceptionnel", "projects", "code_projet", "HL-SMOKE-1"),
    ("/api/v1/convoi-exceptionnel", "cranes", "numero_grue", "GRU-SMOKE-1"),
    ("/api/v1/convoi-exceptionnel", "modular-trailers", "plaque", "MT-SMOKE-1"),
    ("/api/v1/convoi-exceptionnel", "route-surveys", "reference", "RS-SMOKE-1"),
    ("/api/v1/convoi-exceptionnel", "lift-plans", "reference", "LP-SMOKE-1"),
    ("/api/v1/convoi-exceptionnel", "permits", "numero_permis", "PM-SMOKE-1"),
    ("/api/v1/convoi-exceptionnel", "escorts", "reference", "ES-SMOKE-1"),
    ("/api/v1/convoi-exceptionnel", "lashings", "reference", "LSH-SMOKE-1"),
    ("/api/v1/convoi-exceptionnel", "ballasts", "code_ballast", "BL-SMOKE-1"),
    ("/api/v1/convoi-exceptionnel", "rigging-methods", "code_methode", "RM-SMOKE-1"),
]

MODULES = [
    "/api/v1/pipeline-oleoduc",
    "/api/v1/courier-express",
    "/api/v1/chaine-froid",
    "/api/v1/convoi-exceptionnel",
]


def main():
    tok = login()
    print("token:", "OK" if tok else "ABSENT")
    if not tok:
        return 2
    results = []

    # nomenclatures par module (doit etre 200)
    for m in MODULES:
        results.append((f"GET {m}/nomenclatures", *call("GET", m + "/nomenclatures", tok)))

    for prefix, subpath, ufield, uval in SUBMODULES:
        path = f"{prefix}/{subpath}"
        # LIST
        results.append((f"GET {path}", *call("GET", path, tok)))
        # CREATE
        code, body = call("POST", path, tok, {ufield: uval})
        results.append((f"POST {path}", code, body))
        new_id = None
        try:
            new_id = json.loads(body).get("id")
        except Exception:
            pass
        # UPDATE
        if new_id is not None:
            results.append((f"PUT  {path}/{new_id}", *call("PUT", f"{path}/{new_id}", tok, {ufield: uval})))
            # DELETE
            results.append((f"DEL  {path}/{new_id}", *call("DELETE", f"{path}/{new_id}", tok)))

    print("\n================ SMOKE WAVE 5 RESULTS ================")
    bad = 0
    for name, code, body_txt in results:
        ok = code in (200, 201)
        if not ok:
            bad += 1
            print(f"{code}  {name}")
            print(f"       body: {body_txt[:180]}")
    total = len(results)
    print(f"\nDONE: {total - bad}/{total} endpoints OK, {bad} problems")
    return 0 if bad == 0 else 1


if __name__ == "__main__":
    raise SystemExit(main())
