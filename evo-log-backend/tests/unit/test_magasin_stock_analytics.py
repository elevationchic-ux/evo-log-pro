"""Tests unitaires Tranche D-A  magasin : exploitation des stocks, imports/exports
CSV, analytics et rapports.

Verifie que les routes repondent sur des donnees reelles (pending=False) et non
via le fallback pending-modules, et que les calculs (rotation, stock de securite,
projection, anomalies, valorisation) sont exacts sur un jeu de donnees maitrise.
"""
from datetime import datetime, timedelta

import pytest

from app.models.magasin import (
    Article,
    BandeLivraison,
    Commande,
    CommandeStatut,
    Entrepot,
    MouvementStock,
    MouvementType,
    Stock,
)
from app.models.tiers import Client, TiersType


# --------------------------------------------------------------------------- #
# Helpers de fixture
# --------------------------------------------------------------------------- #

def _entrepot(db, code="DEP-01", nom="Depot Douala", capacite=1000.0):
    row = Entrepot(code=code, nom=nom, ville="Douala", capacite=capacite, superficie=500)
    db.add(row)
    db.commit()
    db.refresh(row)
    return row


def _stock(db, code, dispo, mini=None, maxi=None, prix=1000.0, categorie="divers",
           entrepot=None, reservee=0.0, active=True):
    row = Stock(
        code_article=code,
        designation=f"Article {code}",
        categorie=categorie,
        unite_mesure="U",
        quantite_disponible=dispo,
        quantite_reservee=reservee,
        quantite_minimum=mini,
        quantite_maximum=maxi,
        prix_unitaire=prix,
        emplacement="A-01",
        entrepot_id=entrepot.id if entrepot else None,
        is_active=active,
    )
    db.add(row)
    db.commit()
    db.refresh(row)
    return row


def _mouvement(db, stock, type_mvt, quantite, jours_avant=0, avant=None, apres=None,
               piece=None, prix=1000.0, operateur_id=None):
    row = MouvementStock(
        reference=f"MVT-{stock.code_article}-{stock.id}-{db.query(MouvementStock).count() + 1}",
        stock_id=stock.id,
        type_mouvement=type_mvt,
        quantite=quantite,
        quantite_avant=avant,
        quantite_apres=apres,
        prix_unitaire=prix,
        valeur_totale=float(quantite) * float(prix),
        raison="test",
        document_reference=piece,
        destination="client",
        operateur_id=operateur_id,
        date_mouvement=datetime.utcnow() - timedelta(days=jours_avant),
    )
    db.add(row)
    db.commit()
    return row


# --------------------------------------------------------------------------- #
# Magasins (entrepots)
# --------------------------------------------------------------------------- #

def test_magasin_crud_complet(client, db):
    ent = _entrepot(db)

    lst = client.get("/api/v1/magasin/magasins").json()
    assert lst["pending"] is False
    assert lst["total"] == 1

    detail = client.get(f"/api/v1/magasin/magasins/{ent.id}")
    assert detail.status_code == 200
    assert detail.json()["code"] == "DEP-01"

    upd = client.put(f"/api/v1/magasin/magasins/{ent.id}", json={"ville": "Yaounde"})
    assert upd.status_code == 200
    assert upd.json()["ville"] == "Yaounde"

    assert client.delete(f"/api/v1/magasin/magasins/{ent.id}").status_code == 204
    db.expire_all()
    assert db.get(Entrepot, ent.id).is_active is False


def test_magasin_creation_via_api_et_code_unique(client):
    cree = client.post("/api/v1/magasin/magasins", json={
        "code": "DEP-02", "nom": "Depot Kribi", "ville": "Kribi", "capacite": 250,
    })
    assert cree.status_code == 201
    assert cree.json()["code"] == "DEP-02"

    dup = client.post("/api/v1/magasin/magasins", json={"code": "DEP-02", "nom": "Autre"})
    assert dup.status_code == 400

    assert client.get("/api/v1/magasin/magasins/999999").status_code == 404


def test_magasin_stocks_par_entrepot(client, db):
    ent = _entrepot(db)
    _stock(db, "ART-A", 10, entrepot=ent, prix=500)
    _stock(db, "ART-B", 4, entrepot=ent, prix=250)
    _stock(db, "ART-C", 99)  # autres magasins

    res = client.get(f"/api/v1/magasin/magasins/{ent.id}/stocks").json()
    assert res["pending"] is False
    assert {i["code_article"] for i in res["items"]} == {"ART-A", "ART-B"}
    assert res["valeur_totale"] == pytest.approx(10 * 500 + 4 * 250)


# --------------------------------------------------------------------------- #
# Recherche de stocks et statuts derives
# --------------------------------------------------------------------------- #

def test_stocks_search_statuts_derives(client, db):
    ent = _entrepot(db)
    _stock(db, "RUPT", 0, mini=5, entrepot=ent, prix=100)
    _stock(db, "BAS", 3, mini=5, entrepot=ent, prix=100)
    _stock(db, "NORMAL", 20, mini=5, maxi=50, entrepot=ent, prix=100)
    _stock(db, "SURPLUS", 80, mini=5, maxi=50, entrepot=ent, prix=100)
    _stock(db, "INACTIF", 10, active=False)

    tous = client.get("/api/v1/magasin/stocks/search").json()
    assert tous["total"] == 4  # l'inactif est exclus
    statuts = {i["code_article"]: i["statut"] for i in tous["items"]}
    assert statuts == {"RUPT": "rupture", "BAS": "stock_bas",
                       "NORMAL": "normal", "SURPLUS": "excedent"}

    par_q = client.get("/api/v1/magasin/stocks/search", params={"q": "surp"}).json()
    assert [i["code_article"] for i in par_q["items"]] == ["SURPLUS"]

    rupture = client.get("/api/v1/magasin/stocks/search", params={"statut": "rupture"}).json()
    assert [i["code_article"] for i in rupture["items"]] == ["RUPT"]

    bas = client.get("/api/v1/magasin/stocks/search", params={"statut": "stock_bas"}).json()
    assert [i["code_article"] for i in bas["items"]] == ["BAS"]

    faible = client.get("/api/v1/magasin/stocks/search", params={"stock_faible": True}).json()
    assert {i["code_article"] for i in faible["items"]} == {"RUPT", "BAS"}

    par_entrepot = client.get("/api/v1/magasin/stocks/search",
                              params={"entrepot_id": ent.id}).json()
    assert par_entrepot["total"] == 4
    assert all(i["entrepot_code"] == "DEP-01" for i in par_entrepot["items"])

    vide = client.get("/api/v1/magasin/stocks/search", params={"q": "inexistant"}).json()
    assert vide["total"] == 0 and vide["items"] == []


def test_stock_statuses_repartitions(client, db):
    _stock(db, "S1", 0, mini=2, prix=10)
    _stock(db, "S2", 1, mini=2, prix=20)
    _stock(db, "S3", 10, mini=2, prix=30)
    buckets = {b["statut"]: b for b in client.get("/api/v1/magasin/stock-statuses").json()["statuses"]}
    assert buckets["rupture"]["nb_articles"] == 1
    assert buckets["stock_bas"]["nb_articles"] == 1
    assert buckets["normal"]["nb_articles"] == 1
    assert buckets["normal"]["valeur"] == pytest.approx(300)


def test_stock_inconnu_ne_invente_rien(client, db):
    res = client.get("/api/v1/magasin/stocks/search", params={"q": "ABC"}).json()
    assert res["pending"] is False and res["total"] == 0


# --------------------------------------------------------------------------- #
# Grand livre des mouvements
# --------------------------------------------------------------------------- #

def test_history_et_transactions(client, db):
    st = _stock(db, "MVT-1", 50, prix=10)
    _mouvement(db, st, MouvementType.ENTREE, 30, jours_avant=3, avant=20, apres=50, piece="BL-1")
    _mouvement(db, st, MouvementType.SORTIE, 10, jours_avant=1, avant=50, apres=40, piece="BL-2")

    for url in ("/api/v1/magasin/history", "/api/v1/magasin/transactions"):
        res = client.get(url).json()
        assert res["pending"] is False, url
        assert res["total"] == 2, url
        assert res["entrees"] == 30 and res["sorties"] == 10, url
        # tri chronologique decroissant
        assert [i["reference"] for i in res["items"]][0].endswith("2"), url

    filtres = client.get("/api/v1/magasin/history", params={"type_mouvement": "sortie"}).json()
    assert filtres["total"] == 1 and filtres["entrees"] == 0 and filtres["sorties"] == 10

    vide = client.get("/api/v1/magasin/history", params={"q": "PIECE-INCONNUE"}).json()
    assert vide["total"] == 0

    assert client.get("/api/v1/magasin/history", params={"type_mouvement": "nimporte"}).status_code == 400


# --------------------------------------------------------------------------- #
# Export / import CSV
# --------------------------------------------------------------------------- #

def test_export_csv_articles_et_magasins(client, db):
    _entrepot(db)
    db.add(Article(code="EX-1", designation="Fer a beton", categorie="materiaux",
                   prix_unitaire=12500, unite_mesure="BARRE"))
    db.commit()

    resp = client.get("/api/v1/magasin/export/articles/csv")
    assert resp.status_code == 200
    assert "text/csv" in resp.headers["content-type"]
    assert "attachment" in resp.headers["content-disposition"]
    lignes = resp.content.decode("utf-8-sig").strip().splitlines()
    assert lignes[0].split(";")[0] == "code"
    assert any("EX-1" in l for l in lignes)

    magaz = client.get("/api/v1/magasin/export/magasins/csv")
    assert magaz.status_code == 200
    assert "DEP-01" in magaz.content.decode("utf-8-sig")

    stocks = client.get("/api/v1/magasin/export/stocks/csv")
    assert stocks.status_code == 200

    clients_csv = client.get("/api/v1/magasin/export/clients/csv")
    assert clients_csv.status_code == 200

    inconnu = client.get("/api/v1/magasin/export/cocktails/csv")
    assert inconnu.status_code == 404


def _upload(text):
    return {"file": ("data.csv", text.encode("utf-8"), "text/csv")}


def test_import_articles_csv_creer_et_mettre_a_jour(client, db):
    db.add(Article(code="IMP-1", designation="Ancien nom", prix_unitaire=100))
    db.commit()

    csv_text = (
        "code;designation;categorie;prix_unitaire\n"
        "IMP-1;Nouveau nom;materiaux;4500,50\n"
        "IMP-2;Cable cuivre;electricite;1 200\n"
        ";ligne invalide;x;10\n"
    )
    res = client.post("/api/v1/magasin/import/articles", files=_upload(csv_text))
    assert res.status_code == 200, res.text
    corps = res.json()
    assert corps["cree"] == 1 and corps["mis_a_jour"] == 1
    assert corps["erreurs"][0]["ligne"] == 4
    assert corps["pending"] is False

    db.expire_all()
    art = db.query(Article).filter(Article.code == "IMP-1").first()
    assert art.designation == "Nouveau nom"
    assert float(art.prix_unitaire) == pytest.approx(4500.5)
    assert db.query(Article).filter(Article.code == "IMP-2").first() is not None


def test_import_dry_run_necrit_rien(client):
    csv_text = "code;designation\nDRY-1;Test dry run\n"
    res = client.post("/api/v1/magasin/import/articles", files=_upload(csv_text),
                      params={"dry_run": True})
    corps = res.json()
    assert corps["dry_run"] is True and corps["cree"] == 1
    lst = client.get("/api/v1/magasin/articles", params={"search": "DRY-1"}).json()
    assert lst["total"] == 0


def test_import_magasins_et_clients_csv(client, db):
    res = client.post("/api/v1/magasin/import/magasins", files=_upload(
        "code;nom;ville;capacite\nDEP-X;Depat X;Douala;120\n"
    ))
    assert res.status_code == 200 and res.json()["cree"] == 1

    db.add(Client(code="CLI-9", name="Client existant"))
    db.commit()
    res2 = client.post("/api/v1/magasin/import/clients", files=_upload(
        "code;nom;email;limite_credit\nCLI-9;Client renomme;c@x.cm;500000\nCLI-10;Nouveau;n@x.cm;\n"
    ))
    assert res2.status_code == 200, res2.text
    assert res2.json()["mis_a_jour"] == 1 and res2.json()["cree"] == 1


def test_import_ressource_inconnue(client):
    assert client.post("/api/v1/magasin/import/cocktails", files=_upload("code\nx\n")).status_code == 404


def test_modele_import_telechargeable(client):
    res = client.get("/api/v1/magasin/import/articles/template")
    assert res.status_code == 200
    assert res.content.decode("utf-8-sig").startswith("code;designation")


# --------------------------------------------------------------------------- #
# Analytics
# --------------------------------------------------------------------------- #

def test_analytics_rotation(client, db):
    # Fenetre : ouverture 80, deux sorties (20 puis 40), entree de 20  solde 40.
    st = _stock(db, "ROT-1", 40, prix=500)
    _mouvement(db, st, MouvementType.SORTIE, 20, jours_avant=20, avant=80, apres=60, prix=500)
    _mouvement(db, st, MouvementType.SORTIE, 40, jours_avant=15, avant=60, apres=20, prix=500)
    _mouvement(db, st, MouvementType.ENTREE, 20, jours_avant=5, avant=20, apres=40, prix=500)

    res = client.get("/api/v1/magasin/analytics/stock-turnover", params={"jours": 30}).json()
    assert res["pending"] is False
    ligne = next(l for l in res["items"] if l["code_article"] == "ROT-1")
    assert ligne["quantite_sortie"] == 60
    assert ligne["stock_actuel"] == 40
    assert ligne["stock_moyen"] == pytest.approx(60.0)     # (ouverture 80 + cloture 40) / 2
    assert ligne["taux_rotation"] == pytest.approx(1.0)
    assert ligne["jours_couverture"] == pytest.approx(20.0)  # 40 / (60/30)
    assert ligne["valeur_sortie"] == pytest.approx(30000)

    posts = client.post("/api/v1/magasin/analytics/stock-turnover", json={"jours": 30}).json()
    assert posts["nb_articles"] == res["nb_articles"]


def test_analytics_safety_stock(client, db):
    st = _stock(db, "SS-1", 12, prix=100)
    for jour in (1, 3, 5, 7, 9):
        _mouvement(db, st, MouvementType.SORTIE, 4, jours_avant=jour, piece="BL")
    res = client.get("/api/v1/magasin/analytics/safety-stock",
                     params={"jours": 30, "delai_approvisionnement_jours": 4}).json()
    assert res["pending"] is False
    ligne = next(l for l in res["items"] if l["code_article"] == "SS-1")
    # 20 units sur 30 jours observs
    assert ligne["conso_moyenne_jour"] == pytest.approx(round(20 / 30, 3), abs=0.01)
    assert ligne["stock_securs"] > 0
    assert ligne["seuil_reappro"] > ligne["stock_securs"]
    assert res["facteur_securite_z"] == pytest.approx(1.645, abs=0.01)


def test_analytics_forecast(client, db):
    st = _stock(db, "FC-1", 100, prix=100)
    # demande croissante : 150 jours avant = 10/unites, hier = 60/unites
    for mois in range(0, 6):
        _mouvement(db, st, MouvementType.SORTIE, 10 * (mois + 1),
                   jours_avant=30 * (5 - mois) + 1, piece="BL")
    res = client.get("/api/v1/magasin/analytics/demand-forecast",
                     params={"jours": 365, "horizon": 2}).json()
    assert res["pending"] is False
    ligne = next(l for l in res["items"] if l["code_article"] == "FC-1")
    assert ligne["pente_mensuelle"] > 0
    assert len(ligne["projections"]) == 2
    assert all(p["quantite_prevue"] >= 0 for p in ligne["projections"])
    assert res["methode"].startswith("moindres carres")


def test_analytics_anomalies(client, db):
    negatif = _stock(db, "AN-NEG", -5, prix=10)
    _stock(db, "AN-RUPT", 0, mini=3, prix=10)
    _stock(db, "AN-SURRES", 5, mini=1, prix=10, reservee=9)
    incoherent = _stock(db, "AN-INCO", 30, prix=10)
    _mouvement(db, incoherent, MouvementType.ENTREE, 10, jours_avant=2, avant=20, apres=45)
    _mouvement(db, negatif, MouvementType.SORTIE, 3, jours_avant=1)  # sans piece

    res = client.get("/api/v1/magasin/analytics/anomaly-detection", params={"jours": 30}).json()
    types = {(a["type_anomalie"], a.get("code_article")) for a in res["items"]}
    assert ("stock_negatif", "AN-NEG") in types
    assert ("rupture", "AN-RUPT") in types
    assert ("sur_reservation", "AN-SURRES") in types
    assert ("solde_incoherent", "AN-INCO") in types
    assert ("sans_justificatif", "AN-NEG") in types
    assert res["pending"] is False
    assert res["analysed_movements"] == 2
    critiques = [a for a in res["items"] if a["niveau"] == "critique"]
    assert critiques and res["items"].index(critiques[0]) == 0


def test_analytics_vide_sans_donnees(client):
    assert client.get("/api/v1/magasin/analytics/stock-turnover").json()["items"] == []
    assert client.get("/api/v1/magasin/analytics/safety-stock").json()["items"] == []
    assert client.get("/api/v1/magasin/analytics/demand-forecast").json()["items"] == []


# --------------------------------------------------------------------------- #
# Rapports
# --------------------------------------------------------------------------- #

def test_rapport_valorisation(client, db):
    ent = _entrepot(db)
    _stock(db, "VA-1", 10, prix=100, categorie="a", entrepot=ent)
    _stock(db, "VA-2", 5, prix=200, categorie="b", entrepot=ent)
    rap = client.get("/api/v1/magasin/reports/stock-valuation", params={"group_by": "categorie"}).json()
    assert rap["pending"] is False
    assert rap["totaux"]["valeur_totale"] == pytest.approx(2000)
    assert {l["axe"] for l in rap["lignes"]} == {"a", "b"}
    assert rap["lignes"][0]["poids_valeur_pct"] == pytest.approx(50.0)

    par_entrepot = client.post("/api/v1/magasin/reports/stock-valuation",
                               json={"group_by": "entrepot"}).json()
    assert par_entrepot["lignes"][0]["axe"] == "Depot Douala"

    inconnu = client.post("/api/v1/magasin/reports/stock-valuation",
                          json={"group_by": "nimporte"}).json()
    assert inconnu["totaux"]["axe_analyse"] == "categorie"


def test_rapport_mouvements(client, db):
    st = _stock(db, "MO-1", 20, prix=50)
    _mouvement(db, st, MouvementType.ENTREE, 20, jours_avant=4, piece="BL")
    _mouvement(db, st, MouvementType.SORTIE, 5, jours_avant=2)
    rap = client.get("/api/v1/magasin/reports/mouvement-analysis",
                     params={"jours": 30, "group_by": "type"}).json()
    axes = {l["axe"] for l in rap["lignes"]}
    assert axes == {"entree", "sortie"}
    assert rap["totaux"]["nb_mouvements"] == 2
    assert rap["totaux"]["quantite_totale"] == pytest.approx(25)

    par_jour = client.post("/api/v1/magasin/reports/mouvement-analysis",
                           json={"jours": 30, "group_by": "jour"}).json()
    assert par_jour["total_lignes"] == 2


def test_rapport_performance_client(client, db):
    cli = Client(code="CLI-P", name="Client Performant")
    db.add(cli)
    db.commit()
    # le discriminant polymorphe est deduit de la classe : pas de type manuel
    assert cli.type == TiersType.CLIENT
    for statut in (CommandeStatut.LIVREE, CommandeStatut.LIVREE, CommandeStatut.ANNULEE,
                   CommandeStatut.EN_PREPARATION):
        db.add(Commande(reference=f"CMD-{statut.value}", client_id=cli.id, statut=statut,
                        montant_total=100000, date_commande=datetime.utcnow() - timedelta(days=2)))
    db.add(BandeLivraison(reference="BL-P", client_id=cli.id, statut="livre",
                          date_preparation=datetime.utcnow() - timedelta(days=2),
                          date_livraison=datetime.utcnow() - timedelta(days=1, hours=12),
                          nb_colis=3))
    db.commit()

    rap = client.get("/api/v1/magasin/reports/client-performance", params={"jours": 30}).json()
    ligne = next(l for l in rap["lignes"] if l["client_id"] == cli.id)
    assert ligne["nb_commandes"] == 4
    assert ligne["taux_service_pct"] == pytest.approx(66.7, abs=0.1)
    assert ligne["delai_moyen_heures"] == pytest.approx(12.0, abs=0.1)  # 2j -> 1,5j
    assert rap["totaux"]["montant_total"] == pytest.approx(400000)


def test_export_rapport_csv_et_json(client, db):
    _stock(db, "EX-1", 3, prix=1500)
    csv_resp = client.post("/api/v1/magasin/reports/export/csv",
                           json={"rapport": "stock-valuation", "group_by": "categorie"})
    assert csv_resp.status_code == 200
    texte = csv_resp.content.decode("utf-8-sig")
    assert "valeur" in texte.splitlines()[0]
    assert "TOTAUX" in texte

    json_resp = client.post("/api/v1/magasin/reports/export/json",
                            json={"rapport": "client-performance"})
    assert json_resp.status_code == 200
    import json as _json
    data = _json.loads(json_resp.content.decode("utf-8"))
    assert data["rapport"] == "client-performance"

    # rapport inconnu : retour explicite sur le rapport par defaut, jamais un 200 vide
    fallback = client.post("/api/v1/magasin/reports/export/csv", json={"rapport": "inconnu"})
    assert fallback.status_code == 200
    assert b"stock-valuation" not in fallback.content
    assert "rapport_stock-valuation.csv" in fallback.headers["content-disposition"]
