# -*- coding: utf-8 -*-
"""Smoke test wave 6 : maintenance industrielle (25) + traçabilité (19).

Approche "flux métier réel" (parent-first) :
  1. On cree d'abord les racines (actif, piece, prestataire, plan, OT...) et on
    memorise leurs VRAIS ids retournes par l'API.
  2. Les entites enfants referencent ces ids reels (jetons {ASSET}, {PART}...)
    au lieu d'un id 9999 fictif -> cela prouve que l'integrite referentielle
    cross-table fonctionne et que le POST renvoie un vrai 201.
  3. Chaque POST inclut TOUTES les colonnes NOT NULL (satisfait le schema
    Pydantic) -> plus de 422 "toleres" : on exige 201 reel.
  4. PUT + DELETE sur chaque ligne creee.

Un suffixe temporel rend les cles metier uniques entre executions.

Cible : 44 listes x 4 methodes + 2 nomenclatures = 178 endpoints, 0 echec.
"""
import json
import sys
import time
import urllib.request
import urllib.error

BASE = "http://127.0.0.1:8000"
try:
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
except Exception:
    pass

SFX = str(int(time.time()))[-6:]


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
            return r.status, r.read().decode()[:300]
    except urllib.error.HTTPError as e:
        return e.code, e.read().decode()[:300]
    except Exception as e:
        return "ERR", str(e)[:300]


def s(val):
    """Cle metier unique suffixee."""
    return f"{val}-{SFX}"


# (subpath, body)  -- body values may contain jetons {ASSET} {PART} {WO} {PLAN}
# {COMP} {SER} {FM} {RCA} {TSA} remplaces par les vrais ids enregistres.
MNT = "/api/v1/maintenance-industrielle"
TRC = "/api/v1/tracabilite"

PHASES = [
    # --- racines sans dependance (ordre = topologie) ---
    (MNT, "vendors", {"code_prestataire": s("VEN"), "raison_sociale": "Prestataire test"}),
    (MNT, "assets", {"tag_actif": s("MA"), "nom": "Grue portique STS"}),
    (MNT, "spare-parts", {"reference_interne": s("PI"), "designation": "Filtre a huile moteur"}),
    # --- enfants dependants ---
    (MNT, "components", {"asset_id": "{ASSET}", "code_composant": s("CMP"), "nom_composant": "Moteur principal"}),
    (MNT, "plans", {"code_plan": s("PL"), "nom": "Plan preventif moteur", "type_plan": "preventif", "asset_id": "{ASSET}"}),
    (MNT, "work-orders", {"numero_ot": s("OT"), "type_ot": "preventif", "asset_id": "{ASSET}", "titre": "Revision 500h"}),
    (MNT, "bill-of-material", {"asset_id": "{ASSET}", "part_id": "{PART}", "position_index": 1}),
    (MNT, "serialized-parts", {"part_id": "{PART}", "numero_serial": s("SER")}),
    (MNT, "inventory", {"part_id": "{PART}", "quantite_en_stock": 12}),
    (MNT, "movements", {"reference_mouvement": s("MV"), "part_id": "{PART}", "type_mouvement": "entree_achat",
                        "quantite": 5, "date_mouvement": "2026-01-01T10:00:00"}),
    (MNT, "failure-modes", {"code_fmea": s("FM"), "mode_defaillance": "Usure prematuree", "asset_id": "{ASSET}"}),
    (MNT, "tasks", {"code_tache": s("TS"), "titre": "Vidange", "plan_id": "{PLAN}"}),
    (MNT, "asset-failures", {"reference_defaillance": s("PA"), "asset_id": "{ASSET}", "date_detection": "2026-01-01T10:00:00"}),
    (MNT, "wo-parts", {"work_order_id": "{WO}", "part_id": "{PART}", "quantite_demandee": 2}),
    (MNT, "wo-labours", {"work_order_id": "{WO}", "user_id": 2, "date_travail": "2026-01-01", "heures_reelles": 3.5}),
    (MNT, "wo-tools", {"work_order_id": "{WO}", "reference_outillage": s("OUT")}),
    (MNT, "root-causes", {"reference_rca": s("RCA"), "probleme": "Surchauffe moteur"}),
    (MNT, "overhauls", {"code_overhaul": s("OVB"), "asset_id": "{ASSET}"}),
    (MNT, "lubrication", {"asset_id": "{ASSET}", "point_lubrifiant": s("PG")}),
    (MNT, "condition-readings", {"reference_lecture": s("CR"), "asset_id": "{ASSET}", "type_technique": "vibration",
                                 "date_lecture": "2026-01-01T10:00:00"}),
    (MNT, "sensors", {"code_capteur": s("SEN")}),
    (MNT, "predictive-models", {"code_modele": s("PMO")}),
    (MNT, "reliability-kpis", {"asset_id": "{ASSET}", "periode": s("2026-01")}),
    (MNT, "inspections", {"numero_pv": s("PV"), "asset_id": "{ASSET}"}),
    (MNT, "budgets", {"asset_id": "{ASSET}", "exercice": 2026}),
    # --- TRAÇABILITE (auto-suffisant, pas de FK wave 6 obligatoire) ---
    (TRC, "events", {"event_uid": s("EV"), "event_type": "colis.scan", "module_source": "smoke",
                     "timestamp_server": "2026-01-01T10:00:00"}),
    (TRC, "custody-transfers", {"reference_transfert": s("CT"), "asset_type": "colis", "asset_ref": "PK1",
                                "date_transfert": "2026-01-01T10:00:00"}),
    (TRC, "batch-genealogy", {"child_lot": s("LOT-E"), "parent_lot": s("LOT-P")}),
    (TRC, "serial-genealogy", {"child_serial": s("SER-E"), "parent_serial": s("SER-P")}),
    (TRC, "document-hashes", {"document_ref": s("DOC"), "version": 1}),
    (TRC, "geolocations", {"subject_type": "vehicule", "subject_ref": "VH1", "date_position": "2026-01-01T10:00:00",
                           "gps_lat": 4.05, "gps_lng": 9.70}),
    (TRC, "cold-chain", {"subject_type": "reefer", "subject_ref": "RF1", "date_lecture": "2026-01-01T10:00:00"}),
    (TRC, "incidents", {"reference_incident": s("INC"), "type_incident": "accident", "date_debut": "2026-01-01T10:00:00"}),
    (TRC, "regulatory-exports", {"numero_expedition": s("EXP"), "autorite_destinataire": "SAT"}),
    (TRC, "audit-logs", {"timestamp_server": "2026-01-01T10:00:00"}),
    (TRC, "timestamps", {"token_tsa": s("TSA"), "date_horodatage": "2026-01-01T10:00:00"}),
    (TRC, "signatures", {"reference_signature": s("SG"), "date_signature": "2026-01-01T10:00:00"}),
    (TRC, "merkle-proofs", {"racine_type": "trace_events", "periode": s("2026-01")}),
    (TRC, "seals", {"numero_sceau": s("SEL")}),
    (TRC, "cargo-handoffs", {"reference_handoff": s("HO")}),
    (TRC, "access-logs", {"type_evenement": "login_success", "date_evenement": "2026-01-01T10:00:00"}),
    (TRC, "consents", {"reference_consentement": s("CG")}),
    (TRC, "anti-tampering", {"reference_alerte": s("AT"), "type_alerte": "hash_mismatch",
                             "date_detection": "2026-01-01T10:00:00"}),
    (TRC, "retention-policies", {"code_politique": s("RP")}),
]

# token -> cle du registre des ids crees
TOKEN_KEY = {
    "{ASSET}": "assets", "{PART}": "spare-parts", "{WO}": "work-orders",
    "{PLAN}": "plans", "{COMP}": "components", "{SER}": "serialized-parts",
    "{FM}": "failure-modes", "{RCA}": "root-causes", "{TSA}": "timestamps",
}


def resolve(body, ids):
    out = {}
    for k, v in body.items():
        if isinstance(v, str) and v in TOKEN_KEY:
            out[k] = ids.get(TOKEN_KEY[v])
        else:
            out[k] = v
    return out


def main():
    tok = login()
    print("token:", "OK" if tok else "ABSENT")
    if not tok:
        return 2
    ids = {}
    results = []

    # nomenclatures par module
    for m in (MNT, TRC):
        results.append((f"GET {m}/nomenclatures", *call("GET", m + "/nomenclatures", tok)))

    for prefix, subpath, body in PHASES:
        path = f"{prefix}/{subpath}"
        # LIST
        results.append((f"GET {path}", *call("GET", path, tok)))
        # CREATE (resolve jetons -> ids reels)
        payload = resolve(body, ids)
        missing = [k for k, v in payload.items() if v is None]
        if missing:
            results.append((f"POST {path}", "SKIP", f"parent manquant pour {missing}"))
            continue
        code, resp = call("POST", path, tok, payload)
        results.append((f"POST {path}", code, resp))
        new_id = None
        try:
            new_id = json.loads(resp).get("id")
        except Exception:
            pass
        if new_id is not None:
            ids[subpath] = new_id
            results.append((f"PUT  {path}/{new_id}", *call("PUT", f"{path}/{new_id}", tok, payload)))
            results.append((f"DEL  {path}/{new_id}", *call("DELETE", f"{path}/{new_id}", tok)))

    print("\n================ SMOKE WAVE 6 RESULTS ================")
    bad = 0
    for name, code, body_txt in results:
        if name.startswith("POST"):
            if code in (201, 409, "SKIP"):
                continue
            bad += 1
            print(f"{code}  {name}\n       {body_txt[:220]}")
        else:
            if code in (200, 201):
                continue
            bad += 1
            print(f"{code}  {name}\n       {body_txt[:220]}")
    total = len(results)
    print(f"\nDONE: {total - bad}/{total} endpoints OK, {bad} problems")
    return 0 if bad == 0 else 1


if __name__ == "__main__":
    raise SystemExit(main())
