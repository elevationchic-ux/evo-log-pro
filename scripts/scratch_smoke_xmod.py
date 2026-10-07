# -*- coding: utf-8 -*-
"""Smoke test authentifie des endpoints ajoutes (fix_audit + xmod).

Prove que chaque route repond (pas de 404/405 « methode non declaree ») et que
la couche chaine cross-module lit la hierarchie sans lever d'erreur 500.
"""
import json
import sqlite3
import urllib.request
import urllib.error

BASE = "http://127.0.0.1:8000"
DB = r"c:\Users\chris\Documents\Projet\Documents\evo-log pro\evo-log-backend\kamlog_erp.db"


def login():
    body = json.dumps({"username": "admin@evolog.cm", "password": "admin123"}).encode()
    req = urllib.request.Request(BASE + "/api/v1/auth/login", data=body,
                                 headers={"Content-Type": "application/json"}, method="POST")
    with urllib.request.urlopen(req, timeout=15) as r:
        data = json.loads(r.read().decode())
    tok = data.get("access_token") or data.get("token")
    return tok


def call(method, path, token, body=None):
    url = BASE + path
    data = json.dumps(body).encode() if body is not None else None
    headers = {"Content-Type": "application/json"}
    if token:
        headers["Authorization"] = "Bearer " + token
    req = urllib.request.Request(url, data=data, headers=headers, method=method)
    try:
        with urllib.request.urlopen(req, timeout=20) as r:
            return r.status, r.read().decode()[:200]
    except urllib.error.HTTPError as e:
        return e.code, e.read().decode()[:200]
    except Exception as e:
        return "ERR", str(e)[:200]


def one(sql):
    try:
        con = sqlite3.connect(DB)
        cur = con.execute(sql)
        row = cur.fetchone()
        con.close()
        return row[0] if row else None
    except Exception:
        return None


def main():
    tok = login()
    print("token:", "OK" if tok else "ABSENT")

    escale_id = one("SELECT id FROM escales LIMIT 1")
    mission_id = one("SELECT id FROM missions LIMIT 1")
    client_id = one("SELECT id FROM clients LIMIT 1") or 1
    fournisseur_id = one("SELECT id FROM fournisseurs LIMIT 1")
    commande_id = one("SELECT id FROM commandes LIMIT 1")
    supplier_id = one("SELECT id FROM prestataires LIMIT 1")
    print("seed ids:", dict(escale=escale_id, mission=mission_id, client=client_id,
                            fournisseur=fournisseur_id, commande=commande_id, supplier=supplier_id))

    results = []

    # --- xmod : couche chaine ---
    results.append(("GET /chaine/graphe", *call("GET", "/api/v1/chaine/graphe", tok)))
    if escale_id:
        results.append(("GET /chaine/escale/%d" % escale_id, *call("GET", "/api/v1/chaine/escale/%d" % escale_id, tok)))
    if mission_id:
        results.append(("GET /chaine/mission/%d" % mission_id, *call("GET", "/api/v1/chaine/mission/%d" % mission_id, tok)))
    results.append(("POST /chaine/propager(bad)", *call("POST", "/api/v1/chaine/propager", tok, {"event_type": "inconnu", "data": {}})))
    results.append(("POST /chaine/propager(ok)", *call("POST", "/api/v1/chaine/propager", tok, {"event_type": "magasin.stock_alerte", "data": {"stock_id": 0, "code_article": "SMOKE", "quantite_actuelle": 1, "quantite_minimum": 5}})))

    # --- fix_audit : methodes precedemment manquantes ---
    results.append(("GET /magasin-avance/reservations", *call("GET", "/api/v1/magasin-avance/reservations", tok)))
    results.append(("POST /auto-invoicing/generate", *call("POST", "/api/v1/auto-invoicing/generate", tok, {"client_id": client_id, "reference_source": "SMOKE-MISS-1", "montant_ht": 100000})))
    results.append(("POST /container-lifecycle/gate-in", *call("POST", "/api/v1/container-lifecycle/gate-in", tok, {"numero_conteneur": "SMK1234567", "type_conteneur": "DRY", "taille": "40", "port": "PAD Douala", "emplacement": "TP-A1", "navire": "SMOKE"})))
    if fournisseur_id:
        results.append(("POST /finance-avance/dettes/regler", *call("POST", "/api/v1/finance-avance/dettes/regler", tok, {"fournisseur_id": fournisseur_id, "montant": 1000, "mode_paiement": "virement"})))
    if mission_id:
        results.append(("POST /documents/bl", *call("POST", "/api/v1/documents/bl", tok, {"mission_id": mission_id})))
    if commande_id:
        results.append(("PUT /magasin/commandes/%d" % commande_id, *call("PUT", "/api/v1/magasin/commandes/%d" % commande_id, tok, {"notes": "smoke update"})))
    if supplier_id:
        results.append(("DELETE /suppliers/%d" % supplier_id, *call("DELETE", "/api/v1/suppliers/%d" % supplier_id, tok)))

    print("\n================ SMOKE RESULTS ================")
    bad = 0
    for line in results:
        name, code = line[0], line[1]
        # 404/405 = route/methode absente -> ECHEC. 400 peut etre legitime (payload).
        flag = ""
        if code in (404, 405) or code == "ERR" or code == 500 or code == 501:
            flag = "  <-- PROBLEME"
            bad += 1
        print("%-40s %s%s" % (name, code, flag))
        print("     %s" % (line[2] if len(line) > 2 else ""))
    print("\n%d/%d problemes" % (bad, len(results)))


if __name__ == "__main__":
    main()
