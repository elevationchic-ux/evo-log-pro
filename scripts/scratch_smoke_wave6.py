# -*- coding: utf-8 -*-
"""Smoke test wave 6 : maintenance industrielle (25) + tracaabilite (19).

V1 : test de reachabilite route. Pour chaque endpoint :
  GET  /list           -> attend 200 (array vide ok)
  GET  /nomenclatures  -> attend 200 (dico des enums)
  POST /list minimal   -> attend 201 (cree) OU 422 (endpoint cablé, validation
                          Pydantic sur les champs non-null obligatoires) :
                          les deux sont des succes de wiring.
  PUT  /list/{id}      -> si POST a cree : attend 200 ; sinon skip.
  DELETE /list/{id}    -> si POST a cree : attend 200 ; sinon skip.

Cible : 44 listes x 4 methodes + 2 nomenclatures = 178 endpoints.
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


# (module_prefix, sub_path, unique_field, seed_value, extra_body)
SUBMODULES = [
    # --- MAINTENANCE INDUSTRIELLE -----------------------------------------
    ("/api/v1/maintenance-industrielle", "assets",              "tag_actif",              "MA-ASM-1", {"nom": "Grue STS-01", "categorie": "grue"}),
    ("/api/v1/maintenance-industrielle", "components",          "asset_id",               9999,        {"nom_composant": "Moteur principal", "code_composant": "CMP-1"}),
    ("/api/v1/maintenance-industrielle", "spare-parts",         "reference_interne",      "PI-SMOKE-1",{"designation": "Filtre a huile"}),
    ("/api/v1/maintenance-industrielle", "bill-of-material",    "asset_id",               9999,        {"piece_id": 9999, "quantite": 1}),
    ("/api/v1/maintenance-industrielle", "serialized-parts",    "numero_serial",          "SER-SMOKE-1",{"piece_id": 9999}),
    ("/api/v1/maintenance-industrielle", "inventory",           "part_id",                9999,        {"quantite_en_stock": 5}),
    ("/api/v1/maintenance-industrielle", "movements",           "reference_mouvement",    "MV-SMOKE-1",{"piece_id": 9999, "type_mouvement": "entree_achat", "quantite": 1}),
    ("/api/v1/maintenance-industrielle", "failure-modes",       "code_fmea",              "FM-SMOKE-1",{}),
    ("/api/v1/maintenance-industrielle", "plans",               "code_plan",              "PL-SMOKE-1",{"nom_plan": "P1"}),
    ("/api/v1/maintenance-industrielle", "tasks",               "code_tache",             "TS-SMOKE-1",{"libelle": "T1"}),
    ("/api/v1/maintenance-industrielle", "work-orders",         "numero_ot",              "OT-SMOKE-1",{"type_ot": "preventif", "actif_id": 9999}),
    ("/api/v1/maintenance-industrielle", "asset-failures",      "reference_defaillance",  "PA-SMOKE-1",{"actif_id": 9999}),
    ("/api/v1/maintenance-industrielle", "wo-parts",            "work_order_id",          9999,        {"piece_id": 9999}),
    ("/api/v1/maintenance-industrielle", "wo-labours",          "work_order_id",          9999,        {"user_id": 1, "heures_reelles": 1}),
    ("/api/v1/maintenance-industrielle", "wo-tools",            "work_order_id",          9999,        {"nom_outil": "Cle"}),
    ("/api/v1/maintenance-industrielle", "root-causes",         "reference_rca",          "RCA-SMOKE-1",{}),
    ("/api/v1/maintenance-industrielle", "overhauls",           "code_overhaul",          "OVB-SMOKE-1",{}),
    ("/api/v1/maintenance-industrielle", "lubrication",         "asset_id",               9999,        {"point_graissage": "PG1"}),
    ("/api/v1/maintenance-industrielle", "condition-readings",  "reference_lecture",      "CR-SMOKE-1",{"actif_id": 9999, "type_technique": "vibration"}),
    ("/api/v1/maintenance-industrielle", "sensors",             "code_capteur",           "SEN-SMOKE-1",{}),
    ("/api/v1/maintenance-industrielle", "predictive-models",   "code_modele",            "PMO-SMOKE-1",{}),
    ("/api/v1/maintenance-industrielle", "reliability-kpis",    "asset_id",               9999,        {"periode": "2026-01"}),
    ("/api/v1/maintenance-industrielle", "inspections",         "numero_pv",              "PV-SMOKE-1",{}),
    ("/api/v1/maintenance-industrielle", "budgets",             "asset_id",               9999,        {"exercice": 2026}),
    ("/api/v1/maintenance-industrielle", "vendors",             "code_prestataire",       "VEN-SMOKE-1",{"nom": "Presta"}),
    # --- TRAÇABILITE BOUT-EN-BOUT -----------------------------------------
    ("/api/v1/tracabilite", "events",              "event_uid",              "11111111-1111-1111-1111-111111111111",
     {"event_type": "colis.scan", "module_source": "smoke"}),
    ("/api/v1/tracabilite", "custody-transfers",   "reference_transfert",    "CT-SMOKE-1", {"asset_type": "colis", "asset_ref": "PK1", "type_transfert": "remise_physique"}),
    ("/api/v1/tracabilite", "batch-genealogy",     "child_lot",              "LOT-ENF-1",  {"parent_lot": "LOT-PAR-1", "operation": "melange"}),
    ("/api/v1/tracabilite", "serial-genealogy",    "child_serial",           "SER-ENF-1",  {"parent_serial": "SER-PAR-1", "relation_type": "sous_ensemble"}),
    ("/api/v1/tracabilite", "document-hashes",     "document_ref",           "DOC-SMOKE-1",{"version": 1, "hash_algos": "sha256", "hash_valeur": "abc"}),
    ("/api/v1/tracabilite", "geolocations",        "subject_type",           "vehicule",   {"subject_ref": "VH1", "gps_lat": 4.05, "gps_lng": 9.70}),
    ("/api/v1/tracabilite", "cold-chain",          "subject_ref",            "RF-SMOKE-1", {"sonde_id": "S1", "temperature_c": -18.5}),
    ("/api/v1/tracabilite", "incidents",           "reference_incident",     "INC-SMOKE-1",{"type_incident": "accident", "severite": "mineure"}),
    ("/api/v1/tracabilite", "regulatory-exports",  "numero_expedition",      "EXP-SMOKE-1",{"autorite": "SAT", "type_document": "DUM"}),
    ("/api/v1/tracabilite", "audit-logs",          "action",                 "login",     {"user_id_test": 1, "hash_self": "h", "hash_prev": "h"}),
    ("/api/v1/tracabilite", "timestamps",          "token_tsa",              "TSA-SMOKE-1",{"autorite": "CAMPOST", "objet_hash": "abc"}),
    ("/api/v1/tracabilite", "signatures",          "reference_signature",    "SG-SMOKE-1",{"type_signataire": "emetteur", "type_signature": "manuscrite"}),
    ("/api/v1/tracabilite", "merkle-proofs",       "periode",                "2026-01",   {"racine_type": "trace_events", "merkle_root": "r0"}),
    ("/api/v1/tracabilite", "seals",               "numero_sceau",           "SEL-SMOKE-1",{"conteneur_numero": "MSKU123", "type_sceau": "haute_securite"}),
    ("/api/v1/tracabilite", "cargo-handoffs",      "reference_handoff",      "HO-SMOKE-1",{"type_cargo": "container", "mode_precedent": "maritime", "mode_suivant": "routier"}),
    ("/api/v1/tracabilite", "access-logs",         "type_evenement",         "login_success",{"user_id_test": 1}),
    ("/api/v1/tracabilite", "consents",            "reference_consentement", "CG-SMOKE-1",{"finalite": "newsletter", "categorie_donnees": "contact"}),
    ("/api/v1/tracabilite", "anti-tampering",      "reference_evenement",    "AT-SMOKE-1",{"type_attaque": "hash_mismatch"}),
    ("/api/v1/tracabilite", "retention-policies",  "code_politique",         "RP-SMOKE-1",{"type_objet": "facture", "duree_conservation_ans": 10}),
]

MODULES = [
    "/api/v1/maintenance-industrielle",
    "/api/v1/tracabilite",
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

    for prefix, subpath, ufield, uval, extra in SUBMODULES:
        path = f"{prefix}/{subpath}"
        # LIST
        results.append((f"GET {path}", *call("GET", path, tok)))
        # CREATE (payload = champ unique + extras)
        body = dict(extra)
        body[ufield] = uval
        code, resp_body = call("POST", path, tok, body)
        results.append((f"POST {path}", code, resp_body))
        new_id = None
        try:
            new_id = json.loads(resp_body).get("id")
        except Exception:
            pass
        # UPDATE + DELETE si POST a cree
        if new_id is not None:
            results.append((f"PUT  {path}/{new_id}", *call("PUT", f"{path}/{new_id}", tok, {ufield: uval})))
            results.append((f"DEL  {path}/{new_id}", *call("DELETE", f"{path}/{new_id}", tok)))

    print("\n================ SMOKE WAVE 6 RESULTS ================")
    strict_bad = 0
    tolerated = 0
    for name, code, body_txt in results:
        # POST peut retourne 201 (cree) OU 422 (validation attendue) OU 409 (doublon)
        if name.startswith("POST"):
            if code in (201, 422, 409):
                if code != 201:
                    tolerated += 1
                continue
            strict_bad += 1
            print(f"{code}  {name}")
            print(f"       body: {body_txt[:180]}")
        else:
            if code in (200, 201):
                continue
            strict_bad += 1
            print(f"{code}  {name}")
            print(f"       body: {body_txt[:180]}")
    total = len(results)
    print(f"\nDONE: {total - strict_bad}/{total} endpoints OK ({tolerated} POST rejected by schema but wired), {strict_bad} problems")
    return 0 if strict_bad == 0 else 1


if __name__ == "__main__":
    raise SystemExit(main())
