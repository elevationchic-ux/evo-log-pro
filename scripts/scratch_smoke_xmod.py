# -*- coding: utf-8 -*-
"""Smoke test authentifie des endpoints ajoutes (fix_audit + xmod).

Prove que chaque route repond (pas de 404/405 « methode non declaree ») et que
la couche chaine cross-module lit la hierarchie sans lever d'erreur 500.

Les tables de dev etant vides, le harness insere d'abord un jeu de seeds
minimalistes via les modeles SQLAlchemy (data reels, jamais fabriques par le
routeur) puis exerce chaque endpoint sur ces ids.
"""
import json
import sys
import urllib.request
import urllib.error

BASE = "http://127.0.0.1:8000"
BACKEND = r"c:\Users\chris\Documents\Projet\Documents\evo-log pro\evo-log-backend"
sys.path.insert(0, BACKEND)


def login():
    body = json.dumps({"username": "admin@evolog.cm", "password": "admin123"}).encode()
    req = urllib.request.Request(BASE + "/api/v1/auth/login", data=body,
                                 headers={"Content-Type": "application/json"}, method="POST")
    with urllib.request.urlopen(req, timeout=15) as r:
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
        with urllib.request.urlopen(req, timeout=25) as r:
            return r.status, r.read().decode()[:220]
    except urllib.error.HTTPError as e:
        return e.code, e.read().decode()[:220]
    except Exception as e:
        return "ERR", str(e)[:220]


def seed():
    """Insere le strict necessaire via les modeles, idempotent. Retourne les ids."""
    from datetime import date, datetime
    from app.core.database import SessionLocal
    from app.models.tiers import Client, Fournisseur, TiersType
    from app.models.prestataire import Prestataire
    from app.models.transport import Mission
    from app.models.magasin import Commande
    from app.models.finance_ohada import FactureNew

    db = SessionLocal()
    out = {}
    try:
        client = db.query(Client).first()
        if not client:
            client = Client(code="CLI-SMOKE-1", type=TiersType.CLIENT,
                            name="Client Smoke", email="smoke@evolog.cm")
            db.add(client); db.flush()
        out["client_id"] = client.id

        fournisseur = db.query(Fournisseur).first()
        if not fournisseur:
            fournisseur = Fournisseur(code="FRS-SMOKE-1", type=TiersType.FOURNISSEUR,
                                      name="Fournisseur Smoke", email="frs@evolog.cm")
            db.add(fournisseur); db.flush()
        out["fournisseur_id"] = fournisseur.id

        # Dette d'achat ouverte rattachee au fournisseur (client_id = tiers paye)
        dette = db.query(FactureNew).filter(
            FactureNew.type_facture == "achat",
            FactureNew.statut.in_(["emise", "payee_partiel"]),
            FactureNew.solde_restant > 0,
        ).first()
        if not dette:
            dette = FactureNew(
                numero_facture="FAC-ACH-SMOKE-1", client_id=fournisseur.id,
                type_facture="achat", date_emission=date.today(),
                date_echeance=date.today(), montant_ht=100000, montant_tva=19250,
                montant_ttc=119250, statut="emise", solde_restant=119250,
            )
            db.add(dette); db.flush()
        out["dette_id"] = dette.id

        prestataire = db.query(Prestataire).first()
        if not prestataire:
            prestataire = Prestataire(
                code="PRE-SMOKE-1", raison_sociale="Prestataire Smoke",
                specialite="MANUTENTION_PORTUAIRE", contact_telephone="+237600000000",
            )
            db.add(prestataire); db.flush()
        out["supplier_id"] = prestataire.id

        mission = db.query(Mission).first()
        if not mission:
            mission = Mission(
                reference="MIS-SMOKE-1", client_id=client.id,
                type_mission="livraison", numero_bl="B/L-SMOKE-1",
                point_depart="Douala Port", point_arrivee="Yaounde",
                date_debut_prevue=datetime.utcnow(),
            )
            db.add(mission); db.flush()
        out["mission_id"] = mission.id

        commande = db.query(Commande).first()
        if not commande:
            commande = Commande(reference="CMD-SMOKE-1", client_id=client.id,
                                type_commande="sortie", montant_total=50000)
            db.add(commande); db.flush()
        out["commande_id"] = commande.id

        db.commit()
        return out
    except Exception as e:
        db.rollback()
        print("SEED ECHEC:", repr(e)[:300])
        # retomber sur les ids existants s'ils ont ete comites partiellement
        return out
    finally:
        db.close()


def main():
    tok = login()
    print("token:", "OK" if tok else "ABSENT")
    ids = seed()
    print("seed ids:", ids)

    results = []

    # --- xmod : couche chaine ---
    results.append(("GET /chaine/graphe", *call("GET", "/api/v1/chaine/graphe", tok)))
    if ids.get("mission_id"):
        results.append(("GET /chaine/mission/%d" % ids["mission_id"],
                        *call("GET", "/api/v1/chaine/mission/%d" % ids["mission_id"], tok)))
    results.append(("POST /chaine/propager(bad)", *call(
        "POST", "/api/v1/chaine/propager", tok, {"event_type": "inconnu", "data": {}})))
    results.append(("POST /chaine/propager(ok)", *call(
        "POST", "/api/v1/chaine/propager", tok,
        {"event_type": "magasin.stock_alerte",
         "data": {"stock_id": 0, "code_article": "SMOKE", "quantite_actuelle": 1, "quantite_minimum": 5}})))

    # --- fix_audit : methodes precedemment manquantes ---
    results.append(("GET /magasin-avance/reservations", *call("GET", "/api/v1/magasin-avance/reservations", tok)))
    results.append(("POST /auto-invoicing/generate(bad client)", *call(
        "POST", "/api/v1/auto-invoicing/generate", tok,
        {"client_id": 999999, "reference_source": "SMOKE-BAD", "montant_ht": 100000})))
    results.append(("POST /auto-invoicing/generate(ok)", *call(
        "POST", "/api/v1/auto-invoicing/generate", tok,
        {"client_id": ids.get("client_id"), "reference_source": "SMOKE-MISS-1", "montant_ht": 100000})))
    results.append(("POST /container-lifecycle/gate-in", *call(
        "POST", "/api/v1/container-lifecycle/gate-in", tok,
        {"numero_conteneur": "SMK1234568", "type_conteneur": "DRY", "taille": "40",
         "port": "PAD Douala", "emplacement": "TP-A1", "navire": "SMOKE"})))
    if ids.get("fournisseur_id"):
        results.append(("POST /finance-avance/dettes/regler", *call(
            "POST", "/api/v1/finance-avance/dettes/regler", tok,
            {"fournisseur_id": ids["fournisseur_id"], "montant": 50000, "mode_paiement": "virement"})))
    if ids.get("mission_id"):
        results.append(("POST /documents/bl", *call("POST", "/api/v1/documents/bl", tok, {"mission_id": ids["mission_id"]})))
    if ids.get("commande_id"):
        results.append(("PUT /magasin/commandes/%d" % ids["commande_id"], *call(
            "PUT", "/api/v1/magasin/commandes/%d" % ids["commande_id"], tok, {"notes": "smoke update"})))
    if ids.get("supplier_id"):
        results.append(("DELETE /suppliers/%d" % ids["supplier_id"], *call("DELETE", "/api/v1/suppliers/%d" % ids["supplier_id"], tok)))

    # --- endpoints deja valides mais exerces avec data ---
    results.append(("GET /finance-avance/dettes/balance-agee", *call("GET", "/api/v1/finance-avance/dettes/balance-agee?date_reference=2026-10-01", tok)))
    results.append(("GET /finance-avance/dettes/dpo", *call("GET", "/api/v1/finance-avance/dettes/dpo?periode=2026-09", tok)))
    if ids.get("client_id"):
        results.append(("GET /finance-avance/creances/scoring/%d" % ids["client_id"], *call("GET", "/api/v1/finance-avance/creances/scoring/%d" % ids["client_id"], tok)))

    print("\n================ SMOKE RESULTS ================")
    bad = 0
    for name, code, body_txt in results:
        # /bl attend 201; generate(bad client) attend 400; propager(bad) attend 400
        expect_ok = code in (200, 201) or ("bad" in name and code == 400)
        flag = "" if expect_ok else "  <-- PROBLEME"
        if not expect_ok:
            bad += 1
        print("%-42s %s%s" % (name, code, flag))
        print("     %s" % body_txt)
    print("\n%d problemes / %d appels" % (bad, len(results)))
    sys.exit(1 if bad else 0)


if __name__ == "__main__":
    main()
