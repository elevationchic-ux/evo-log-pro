"""Batch 16 — Bon de sortie / circuit de signature (P2 #10).

Valide le durcissement de app/routers/v1/removal_slip.py :
  * création : références existantes exigées (FK SQLite non appliquées),
    numérotation BE-YYYYMMDD-NNNN sans collision ;
  * validation : stock décrémenté RÉELLEMENT, tout-ou-rien (rupture = 400
    détaillé, aucun décript), registre MouvementStock alimenté ligne à ligne ;
  * refus : motif obligatoire, aucun mouvement, non revalidable ;
  * immuabilité : PUT statut rejeté, document signé intouchable ;
  * PDF : 200 réel ou 501 honnête (jamais un faux PDF).

Conforme au contrat conftest : fixture `client` (faux superuser id=1) + `db`
pour les seeds (même session partagée).
"""
import pytest
from datetime import datetime

from app.models.magasin import Stock, Entrepot, MouvementStock, MouvementType
from app.models.magasin_avance import BonSortie, LigneBonSortie
from app.models.tiers import Client

BASE = "/api/v1/magasin/removal-slips"


# --------------------------------------------------------------------------- #
# Seeds
# --------------------------------------------------------------------------- #

def _seed_client(db, code="CLI-B16", name="Societe Nouvelle du Mfoundi"):
    c = Client(code=code, name=name, city="Douala")
    db.add(c)
    db.commit()
    return c


def _seed_entrepot(db, code="ENT-B16", nom="Magasin Bonaberi"):
    e = Entrepot(code=code, nom=nom)
    db.add(e)
    db.commit()
    return e


def _seed_stock(db, code_article, designation, dispo, entrepot_id=None):
    s = Stock(code_article=code_article, designation=designation,
              quantite_disponible=dispo, unite_mesure="SAC",
              entrepot_id=entrepot_id)
    db.add(s)
    db.commit()
    return s


def _create_bon(client, client_id, entrepot_id, lignes):
    return client.post(BASE + "/", json={
        "client_id": client_id,
        "entrepot_id": entrepot_id,
        "type_sortie": "enlevement",
        "notes": "bon de test",
        "lignes": lignes,
    })


# --------------------------------------------------------------------------- #
# Création : validations d'existence et numérotation
# --------------------------------------------------------------------------- #

def test_create_rejecte_references_inexistantes(client, db):
    cli = _seed_client(db)
    ent = _seed_entrepot(db)
    stock = _seed_stock(db, "ART-A", "Ciment", 100, ent.id)
    ligne = [{"stock_id": stock.id, "quantite_sortie": 10}]

    # client inexistant
    r = _create_bon(client, 999999, ent.id, ligne)
    assert r.status_code == 400 and "Client" in r.json()["detail"]
    # entrepot inexistant
    r = _create_bon(client, cli.id, 999999, ligne)
    assert r.status_code == 400 and "Entrepot" in r.json()["detail"]
    # stock inexistant
    r = _create_bon(client, cli.id, ent.id,
                    [{"stock_id": 999999, "quantite_sortie": 10}])
    assert r.status_code == 400 and "Stock" in r.json()["detail"]
    # quantité <= 0
    r = _create_bon(client, cli.id, ent.id,
                    [{"stock_id": stock.id, "quantite_sortie": 0}])
    assert r.status_code == 400 and "Quantite" in r.json()["detail"]
    # rien n'a été créé
    assert client.get(BASE + "/").json()["total"] == 0


def test_numeration_unique_et_sequencee(client, db):
    cli = _seed_client(db)
    ent = _seed_entrepot(db)
    stock = _seed_stock(db, "ART-A", "Ciment", 500, ent.id)
    numeros = []
    for _ in range(3):
        r = _create_bon(client, cli.id, ent.id,
                        [{"stock_id": stock.id, "quantite_sortie": 5}])
        assert r.status_code == 201
        numeros.append(r.json()["numero_bon"])
    assert len(set(numeros)) == 3
    today = datetime.now().strftime("%Y%m%d")
    assert all(n.startswith(f"BE-{today}-") for n in numeros)


# --------------------------------------------------------------------------- #
# Validation : décrémentation réelle + registre MouvementStock
# --------------------------------------------------------------------------- #

def test_valide_decrete_stock_et_ecrit_registre(client, db):
    cli = _seed_client(db)
    ent = _seed_entrepot(db)
    s1 = _seed_stock(db, "ART-1", "Ciment CP 50kg", 100, ent.id)
    s2 = _seed_stock(db, "ART-2", "Farine 25kg", 40, ent.id)
    created = _create_bon(client, cli.id, ent.id, [
        {"stock_id": s1.id, "quantite_sortie": 30, "prix_unitaire": 4500},
        {"stock_id": s2.id, "quantite_sortie": 10, "numero_lot": "LOT-9"},
    ])
    assert created.status_code == 201
    bon_id = created.json()["id"]
    numero = created.json()["numero_bon"]

    r = client.post(f"{BASE}/{bon_id}/validate")
    assert r.status_code == 200
    body = r.json()
    assert body["statut"] == "valide"
    assert body["mouvements_enregistres"] == 2

    db.expire_all()
    assert float(s1.quantite_disponible) == 70.0
    assert float(s2.quantite_disponible) == 30.0

    mvts = (db.query(MouvementStock)
              .filter(MouvementStock.document_reference == numero)
              .order_by(MouvementStock.id).all())
    assert len(mvts) == 2
    m1, m2 = mvts
    assert m1.type_mouvement == MouvementType.SORTIE
    assert float(m1.quantite) == 30.0
    assert float(m1.quantite_avant) == 100.0
    assert float(m1.quantite_apres) == 70.0
    assert m1.operateur_id == 1  # faux superuser de la fixture client
    assert float(m2.quantite_avant) == 40.0
    assert float(m2.quantite_apres) == 30.0

    bon = db.query(BonSortie).get(bon_id)
    assert bon.statut == "valide"
    assert bon.validateur == 1
    assert bon.date_validation is not None


def test_rupture_tout_ou_rien_sans_aucun_decript(client, db):
    cli = _seed_client(db)
    ent = _seed_entrepot(db)
    ok = _seed_stock(db, "ART-OK", "Produit disponible", 50, ent.id)
    short = _seed_stock(db, "ART-HS", "Produit en rupture", 5, ent.id)
    created = _create_bon(client, cli.id, ent.id, [
        {"stock_id": ok.id, "quantite_sortie": 10},
        {"stock_id": short.id, "quantite_sortie": 50},
    ])
    bon_id = created.json()["id"]

    r = client.post(f"{BASE}/{bon_id}/validate")
    assert r.status_code == 400
    detail = r.json()["detail"]
    # detail structuré : message + lignes en rupture (pas un simple string)
    assert "Rupture" in detail["message"]
    assert len(detail["lignes_en_rupture"]) == 1
    rupture = detail["lignes_en_rupture"][0]
    assert rupture["stock_id"] == short.id
    assert rupture["quantite_demandee"] == 50.0
    assert rupture["quantite_disponible"] == 5.0

    db.expire_all()
    # AUCUN décript, même sur la ligne qui passait (tout-ou-rien) :
    # l'ancien max(0, ...) et le decrement partiel sont morts.
    assert float(ok.quantite_disponible) == 50.0
    assert float(short.quantite_disponible) == 5.0
    assert db.query(MouvementStock).count() == 0
    assert db.query(BonSortie).get(bon_id).statut == "en_attente"


def test_valide_interdits(client, db):
    cli = _seed_client(db)
    ent = _seed_entrepot(db)
    stock = _seed_stock(db, "ART-A", "Ciment", 100, ent.id)

    # bon sans ligne : rien à sortir
    vide = _create_bon(client, cli.id, ent.id, [])
    assert vide.status_code == 201
    r = client.post(f"{BASE}/{vide.json()['id']}/validate")
    assert r.status_code == 400 and "sans ligne" in r.json()["detail"]

    # double validation
    bon = _create_bon(client, cli.id, ent.id,
                      [{"stock_id": stock.id, "quantite_sortie": 10}])
    bon_id = bon.json()["id"]
    assert client.post(f"{BASE}/{bon_id}/validate").status_code == 200
    r = client.post(f"{BASE}/{bon_id}/validate")
    assert r.status_code == 400 and "déjà validé" in r.json()["detail"]


# --------------------------------------------------------------------------- #
# Refus motivé
# --------------------------------------------------------------------------- #

def test_refus_motive_sans_mouvement_puis_non_revalidable(client, db):
    cli = _seed_client(db)
    ent = _seed_entrepot(db)
    stock = _seed_stock(db, "ART-A", "Ciment", 100, ent.id)
    created = _create_bon(client, cli.id, ent.id,
                          [{"stock_id": stock.id, "quantite_sortie": 10}])
    bon_id = created.json()["id"]

    # motif vide refusé
    r = client.post(f"{BASE}/{bon_id}/refuse", json={"motif": "   "})
    assert r.status_code == 400 and "motif" in r.json()["detail"]

    r = client.post(f"{BASE}/{bon_id}/refuse",
                    json={"motif": "Article périmé au contrôle visuel"})
    assert r.status_code == 200
    assert r.json()["statut"] == "refuse"

    db.expire_all()
    bon = db.query(BonSortie).get(bon_id)
    assert bon.statut == "refuse"
    assert "Article périmé" in bon.notes
    assert float(stock.quantite_disponible) == 100.0  # aucun décript
    assert db.query(MouvementStock).count() == 0      # aucun mouvement

    # un refus est une signature : non revalidable, non modifiable, non double-refuse
    assert client.post(f"{BASE}/{bon_id}/validate").status_code == 400
    assert client.post(f"{BASE}/{bon_id}/refuse",
                       json={"motif": "encore"}).status_code == 400
    r = client.put(f"{BASE}/{bon_id}", json={"notes": "retouche"})
    assert r.status_code == 400 and "immuable" in r.json()["detail"]


# --------------------------------------------------------------------------- #
# Circuit de signature : PUT ne peut pas falsifier un statut
# --------------------------------------------------------------------------- #

def test_put_ne_peut_pas_falsifier_statut(client, db):
    cli = _seed_client(db)
    ent = _seed_entrepot(db)
    stock = _seed_stock(db, "ART-A", "Ciment", 100, ent.id)
    created = _create_bon(client, cli.id, ent.id,
                          [{"stock_id": stock.id, "quantite_sortie": 10}])
    bon_id = created.json()["id"]

    # tentative de mise en "valide" par PUT → 400 explicite, aucun décript
    r = client.put(f"{BASE}/{bon_id}", json={"statut": "valide"})
    assert r.status_code == 400
    assert "/validate" in r.json()["detail"]
    db.expire_all()
    assert db.query(BonSortie).get(bon_id).statut == "en_attente"
    assert float(stock.quantite_disponible) == 100.0

    # champs légitimes toujours modifiables avant signature
    r = client.put(f"{BASE}/{bon_id}", json={"notes": "urgence client"})
    assert r.status_code == 200

    # après signature : document verrouillé
    assert client.post(f"{BASE}/{bon_id}/validate").status_code == 200
    r = client.put(f"{BASE}/{bon_id}", json={"notes": "retouche apres signature"})
    assert r.status_code == 400 and "immuable" in r.json()["detail"]


def test_delete_garde_document_signe(client, db):
    cli = _seed_client(db)
    ent = _seed_entrepot(db)
    stock = _seed_stock(db, "ART-A", "Ciment", 100, ent.id)
    created = _create_bon(client, cli.id, ent.id,
                          [{"stock_id": stock.id, "quantite_sortie": 10}])
    bon_id = created.json()["id"]

    # brouillon supprimable
    brouillon = _create_bon(client, cli.id, ent.id, [])
    assert client.delete(f"{BASE}/{brouillon.json()['id']}").status_code == 200

    # signé → supprimable ? Non : un bon validé a une valeur probante
    assert client.post(f"{BASE}/{bon_id}/validate").status_code == 200
    r = client.delete(f"{BASE}/{bon_id}")
    assert r.status_code == 400 and "validé" in r.json()["detail"]


# --------------------------------------------------------------------------- #
# Édition PDF (200 réel ou 501 honnête — jamais de faux PDF)
# --------------------------------------------------------------------------- #

def test_pdf_bon_sortie_statut_honnete(client, db):
    cli = _seed_client(db)
    ent = _seed_entrepot(db)
    stock = _seed_stock(db, "ART-A", "Ciment CP 50kg", 100, ent.id)
    created = _create_bon(client, cli.id, ent.id,
                          [{"stock_id": stock.id, "quantite_sortie": 10,
                            "prix_unitaire": 4500}])
    bon_id = created.json()["id"]

    r = client.get(f"{BASE}/{bon_id}/pdf")
    if r.status_code == 501:
        # Environnement sans WeasyPrint/Pango : 501 explicite, acceptable.
        assert "PDF" in r.json()["detail"]
    else:
        assert r.status_code == 200
        assert r.headers["content-type"] == "application/pdf"
        assert r.content[:5] == b"%PDF-"
        assert "content-disposition" in r.headers
    # 404 sur bon inexistant dans les deux cas
    assert client.get(f"{BASE}/999999/pdf").status_code == 404
