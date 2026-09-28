"""Batch 17 — Retours clients, litiges transporteurs et KPIs magasin.

Les six endpoints de app/routers/v1/magasin_avance.py étaient morts du même
syndrome que le trio /sorties du batch 16 : kwargs/colonnes inventés
(article_id, etat, action_effectuee, date_litige, MouvementStock.article_id,
InventaireTournant.date_inventaire…). Reconstruits sur les modèles réels, ces
tests verrouillent le comportement NEUF :

* retour : création validée (client/bon sortie/motif), décision unique
  accepte(action)/refuse, immuabilité après traitement, et SURTOUT aucun
  mouvement de stock inventé (modèle sans stock_id → pas de réintégration
  fantôme) ;
* litige : transporteur = fournisseur existant, cloture resolu/refuse/justice
  avec résolution écrite datée, décision unique ;
* KPI rotation : colonnes réelles (registre MouvementStock via stock_id),
  rotation None si stock à zéro (pas de 0.0 mensonger) ;
* KPI précision : inventaire `termine` (le `valide` duancien code n'existe
  pas) ; sans mesure → precision None + message, pas un faux 0.0.
"""
from datetime import date, datetime, timedelta

from app.models.magasin import Stock, Entrepot, MouvementStock, MouvementType, Article
from app.models.magasin_avance import (
    BonSortie, RetourClient, LitigeTransporteur, InventaireTournant, LigneInventaire,
)
from app.models.tiers import Client, Fournisseur

BASE = "/api/v1/magasin-avance"


# --------------------------------------------------------------------------- #
# Seeds
# --------------------------------------------------------------------------- #

def _seed_client(db, code="CLI-B17"):
    c = Client(code=code, name="Client Retours SA")
    db.add(c)
    db.commit()
    return c


def _seed_fournisseur(db, code="FRS-B17"):
    f = Fournisseur(code=code, name="Transports Logistique CM")
    db.add(f)
    db.commit()
    return f


def _seed_bon_sortie(db, client_id, code_ent="ENT-B17"):
    ent = Entrepot(code=code_ent, nom="Magasin central")
    db.add(ent)
    db.commit()
    bon = BonSortie(numero_bon=f"BE-TEST-{ent.id}", client_id=client_id,
                    entrepot_id=ent.id, date_sortie=date.today(),
                    statut="valide")
    db.add(bon)
    db.commit()
    return bon, ent


# --------------------------------------------------------------------------- #
# Retours clients
# --------------------------------------------------------------------------- #

def test_retour_creation_et_validations(client, db):
    cli = _seed_client(db)
    bon, _ = _seed_bon_sortie(db, cli.id)

    # client inexistant
    r = client.post(BASE + "/retours", json={"client_id": 999999, "motif": "casse"})
    assert r.status_code == 400 and "Client" in r.json()["detail"]
    # bon de sortie inexistant
    r = client.post(BASE + "/retours", json={
        "client_id": cli.id, "bon_sortie_id": 999999, "motif": "casse"})
    assert r.status_code == 400 and "Bon de sortie" in r.json()["detail"]
    # motif vide
    r = client.post(BASE + "/retours", json={"client_id": cli.id, "motif": "  "})
    assert r.status_code == 400 and "motif" in r.json()["detail"]
    # quantite <= 0
    r = client.post(BASE + "/retours", json={
        "client_id": cli.id, "motif": "casse", "quantite": 0})
    assert r.status_code == 400
    # type hors liste metier
    r = client.post(BASE + "/retours", json={
        "client_id": cli.id, "motif": "casse", "type_retour": "j_ai_change_avis"})
    assert r.status_code == 400 and "type_retour" in r.json()["detail"]

    # création réelle
    r = client.post(BASE + "/retours", json={
        "client_id": cli.id, "bon_sortie_id": bon.id, "motif": "Sac éventré",
        "type_retour": "defectif", "quantite": 4})
    assert r.status_code == 201
    corps = r.json()
    assert corps["numero_retour"].startswith(f"RT-{datetime.now().strftime('%Y%m%d')}-")
    assert corps["statut"] == "en_attente"
    assert corps["bon_sortie_id"] == bon.id
    assert corps["operateur"] == 1  # faux superuser de la fixture client

    # liste filtrée
    lst = client.get(BASE + "/retours", params={"statut": "en_attente"}).json()
    assert len(lst) == 1 and lst[0]["id"] == corps["id"]


def test_retour_traitement_decision_unique_et_sans_stock_invente(client, db):
    cli = _seed_client(db)
    r = client.post(BASE + "/retours", json={"client_id": cli.id, "motif": "périmé"})
    ret_id = r.json()["id"]

    # accepte SANS action → 400 (choix métier obligatoire)
    rep = client.put(f"{BASE}/retours/{ret_id}/traiter", json={"decision": "accepte"})
    assert rep.status_code == 400 and "action" in rep.json()["detail"]
    # décision hors workflow
    assert client.put(f"{BASE}/retours/{ret_id}/traiter",
                      json={"decision": "on_avise"}).status_code == 400
    # action interdite sur un refus
    # (le premier refus consomme la décision → testé après l'acceptation)

    # PATCH avant traitement : autorisé (le retour n'est pas encore signé)
    rep = client.patch(f"{BASE}/retours/{ret_id}", json={"quantite": 2})
    assert rep.status_code == 200 and rep.json()["quantite"] == 2.0

    # accepte avec action → trace réelle dans notes, statut final
    rep = client.put(f"{BASE}/retours/{ret_id}/traiter",
                     json={"decision": "accepte", "action": "remboursement",
                           "cout_traitement": 1500})
    assert rep.status_code == 200
    corps = rep.json()
    assert corps["statut"] == "accepte"
    assert corps["action"] == "remboursement"
    assert corps["cout_traitement"] == 1500.0
    assert "[TRAITE" in corps["notes"] and "accepte (remboursement)" in corps["notes"]

    # decision unique : re-traiter un retour traité → 400
    rep = client.put(f"{BASE}/retours/{ret_id}/traiter",
                     json={"decision": "refuse"})
    assert rep.status_code == 400 and "deja traite" in rep.json()["detail"]
    # document traité immuable (PATCH aussi)
    assert client.patch(f"{BASE}/retours/{ret_id}",
                        json={"motif": "retouche"}).status_code == 400

    # ZÉRO STOCK INVENTÉ : le modèle RetourClient n'a pas de stock_id, donc
    # aucun mouvement de stock ne doit exister après un retour accepté.
    assert db.query(MouvementStock).count() == 0


def test_retour_refus_sans_action(client, db):
    cli = _seed_client(db)
    r = client.post(BASE + "/retours", json={"client_id": cli.id, "motif": "hors delai"})
    ret_id = r.json()["id"]
    rep = client.put(f"{BASE}/retours/{ret_id}/traiter", json={"decision": "refuse"})
    assert rep.status_code == 200
    assert rep.json()["statut"] == "refuse"
    assert rep.json()["action"] is None


# --------------------------------------------------------------------------- #
# Litiges transporteurs
# --------------------------------------------------------------------------- #

def test_litige_creation_validations(client, db):
    frs = _seed_fournisseur(db)

    # transporteur inexistant
    r = client.post(BASE + "/litiges", json={
        "transporteur_id": 999999, "type_litige": "avarie", "description": "palette écrasée"})
    assert r.status_code == 400 and "fournisseur" in r.json()["detail"]
    # type hors liste
    r = client.post(BASE + "/litiges", json={
        "transporteur_id": frs.id, "type_litige": "mauvaise_humeur", "description": "x"})
    assert r.status_code == 400 and "type_litige" in r.json()["detail"]
    # description vide
    r = client.post(BASE + "/litiges", json={
        "transporteur_id": frs.id, "type_litige": "retard", "description": "   "})
    assert r.status_code == 400
    # montant négatif
    r = client.post(BASE + "/litiges", json={
        "transporteur_id": frs.id, "type_litige": "retard",
        "description": "livraison J+9", "montant_reclame": -1})
    assert r.status_code == 400

    r = client.post(BASE + "/litiges", json={
        "transporteur_id": frs.id, "type_litige": "avarie",
        "description": "20 sacs détruits en route", "montant_reclame": 90000,
        "assureur": "ACTUA", "numero_police": "POL-77"})
    assert r.status_code == 201
    corps = r.json()
    assert corps["numero_litige"].startswith(f"LI-{datetime.now().strftime('%Y%m%d')}-")
    assert corps["statut"] == "en_cours"
    assert corps["assureur"] == "ACTUA"
    assert corps["date_incident"] == date.today().isoformat()


def test_litige_cloture_decision_unique(client, db):
    frs = _seed_fournisseur(db, code="FRS-B17B")
    r = client.post(BASE + "/litiges", json={
        "transporteur_id": frs.id, "type_litige": "perte",
        "description": "conteneur introuvable", "montant_reclame": 500000})
    lit_id = r.json()["id"]

    # statut de cloture hors liste
    assert client.put(f"{BASE}/litiges/{lit_id}/resoudre",
                      json={"statut": "oubli", "resolution": "on laisse"}).status_code == 400
    # résolution écrite obligatoire
    assert client.put(f"{BASE}/litiges/{lit_id}/resoudre",
                      json={"statut": "resolu", "resolution": " "}
                      ).status_code == 400
    # montant_indemnise réservé aux litiges résolus
    assert client.put(f"{BASE}/litiges/{lit_id}/resoudre",
                      json={"statut": "justice", "resolution": "assignation",
                            "montant_indemnise": 100}).status_code == 400

    # clôture réelle : resolu avec indemnité convenue
    rep = client.put(f"{BASE}/litiges/{lit_id}/resoudre",
                     json={"statut": "resolu", "resolution": "accord transactionnel 350 000",
                           "montant_indemnise": 350000})
    assert rep.status_code == 200
    corps = rep.json()
    assert corps["statut"] == "resolu"
    assert corps["date_resolution"] == date.today().isoformat()
    assert corps["montant_reclame"] == 350000.0

    # clôture unique + immuabilité
    assert client.put(f"{BASE}/litiges/{lit_id}/resoudre",
                      json={"statut": "refuse", "resolution": "revirement"}).status_code == 400
    assert client.patch(f"{BASE}/litiges/{lit_id}",
                        json={"description": "retouche"}).status_code == 400
    # PATCH avant clôture toujours possible
    r2 = client.post(BASE + "/litiges", json={
        "transporteur_id": frs.id, "type_litige": "retard", "description": "livraison J+5"})
    assert client.patch(f"{BASE}/litiges/{r2.json()['id']}",
                        json={"description": "livraison J+5, pénalité contrat"}).status_code == 200


# --------------------------------------------------------------------------- #
# KPI rotation (colonnes réelles)
# --------------------------------------------------------------------------- #

def test_kpi_rotation_calculee_sur_registre_reel(client, db):
    art = Article(code="ART-KPI", designation="Ciment CP 45")
    db.add(art)
    db.commit()
    st = Stock(code_article=art.code, designation="Ciment CP 45",
               quantite_disponible=70)
    db.add(st)
    db.commit()
    db.add(MouvementStock(reference="TEST-ROT-1", stock_id=st.id,
                          type_mouvement=MouvementType.SORTIE, quantite=30,
                          quantite_avant=100, quantite_apres=70,
                          date_mouvement=datetime.utcnow() - timedelta(days=10)))
    db.commit()

    r = client.get(f"{BASE}/kpi/rotation/{art.id}")
    assert r.status_code == 200
    corps = r.json()
    assert corps["sorties"] == 30.0
    assert corps["stock_actuel"] == 70.0
    # 30/70 * 365/90 = 1.7381 → arrondi 1.74
    assert corps["rotation"] == round(30.0 / 70.0 * (365 / 90), 2)

    # article inexistant → 404 (ancien code : 500 par AttributeError)
    assert client.get(f"{BASE}/kpi/rotation/999999").status_code == 404


def test_kpi_rotation_stock_zero_pas_de_faux_chiffre(client, db):
    art = Article(code="ART-KPI-VIDE", designation="Produit épuisé")
    db.add(art)
    db.commit()
    st = Stock(code_article=art.code, designation="Produit épuisé",
               quantite_disponible=0)
    db.add(st)
    db.commit()
    db.add(MouvementStock(reference="TEST-ROT-2", stock_id=st.id,
                          type_mouvement=MouvementType.SORTIE, quantite=5,
                          date_mouvement=datetime.utcnow()))
    db.commit()
    corps = client.get(f"{BASE}/kpi/rotation/{art.id}").json()
    # rotation INDEFINIE (division par un stock nul) : None, pas 0.0 inventé
    assert corps["rotation"] is None
    assert corps["sorties"] == 5.0


# --------------------------------------------------------------------------- #
# KPI précision d'inventaire
# --------------------------------------------------------------------------- #

def test_kpi_precision_sans_mesure_repond_honnetement(client, db):
    rep = client.get(f"{BASE}/kpi/precision/4242")
    assert rep.status_code == 200
    corps = rep.json()
    assert corps["precision"] is None
    assert "non mesuree" in corps["message"]


def test_kpi_precision_calculee_sur_inventaire_termine(client, db):
    ent = Entrepot(code="ENT-PREC", nom="Depot Kribi")
    db.add(ent)
    db.commit()
    inv = InventaireTournant(numero_inventaire="INV-PREC-1", entrepot_id=ent.id,
                             date_debut=date.today(), statut="termine")
    db.add(inv)
    db.commit()
    stocks = [Stock(code_article=f"ART-P{i}", designation=f"Art {i}",
                    quantite_disponible=10) for i in range(4)]
    db.add_all(stocks)
    db.commit()
    ecarts = [0, 0, 0, 5]  # 3 lignes justes / 4 → 75 %
    for st, ecart in zip(stocks, ecarts):
        db.add(LigneInventaire(inventaire_id=inv.id, stock_id=st.id,
                               quantite_theorique=10, quantite_comptee=10 - ecart,
                               ecart=-ecart if ecart else 0, statut="compte"))
    db.commit()

    corps = client.get(f"{BASE}/kpi/precision/{ent.id}").json()
    assert corps["precision"] == 75.0
    assert corps["lignes_total"] == 4 and corps["lignes_correctes"] == 3
