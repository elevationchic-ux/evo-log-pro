"""Batch 19  Réceptions (bons + lignes + validation) et Colis.

Les six endpoints de app/routers/v1/magasin_avance.py (sections Réceptions /
Colis) étaient morts du syndrome « champs fantômes » :
BonReception(commande_id=…) et LigneBonReception(bon_id, article_id,
emplacement_id=…) → TypeError 500 garanti ; valider lisait
LigneBonReception.bon_id et Stock.article_id (AttributError) et écrivait
stock.quantite (colonne inexistante → tout l'apport en stock perdu en
silence) ; ColisService inventait reference_colis/date_creation (TypeError),
code_barres/palette_id/date_palettisation (écriture silencieuse, jamais
persistée).

Ces tests verrouillent le comportement NEUF, sur colonnes réelles :
* réception : numérotation BR-, FK fournisseur/entrepot vérifiées, lignes sur
  stock_id, statut de conformité CALCULÉ (jamais saisi librement) ;
* validation : stock réellement augmenté (quantite_disponible) ET journalisé
  (MouvementStock type entree, avant/apres)  aucun 200 menteux ; decision
  unique ; refuse exige un motif ecrit ; bon vide refuse la validation ;
* liaison commande : lignes de commande mise à jour (quantite_recue, statut
  recu) puis commande « livree » quand tout est reçu ;
* colis : numero CO-, type/poids validés, etiquette date réellement
  (date_etiquetage, colonne Date) et decision unique, palettisation tracee
  dans emplacement (aucune colonne palette inventee).
"""
from datetime import date

from app.models.magasin import Stock, Entrepot, MouvementStock
from app.models.magasin_avance import (
    BonReception, LigneBonReception, BonSortie, Colis,
    CommandeFournisseur, LigneCommandeFournisseur,
)
from app.models.tiers import Client, Fournisseur

BASE = "/api/v1/magasin-avance"


# --------------------------------------------------------------------------- #
# Seeds
# --------------------------------------------------------------------------- #

def _seed_entrepot(db, code="ENT-B19"):
    ent = Entrepot(code=code, nom="Magasin B19")
    db.add(ent)
    db.commit()
    return ent


def _seed_fournisseur(db, code="FRS-B19"):
    f = Fournisseur(code=code, name="Import Distribution SARL")
    db.add(f)
    db.commit()
    return f


def _seed_client(db, code="CLI-B19"):
    c = Client(code=code, name="Client Colis SA")
    db.add(c)
    db.commit()
    return c


def _seed_stock(db, ent, code_article, dispo=0):
    s = Stock(code_article=code_article, designation=f"Article {code_article}",
              quantite_disponible=dispo, entrepot_id=ent.id)
    db.add(s)
    db.commit()
    return s


def _seed_bon_reception_statut(db, ent, frs, statut, numero):
    # Bon deja decide, seede en direct (la route refuserait ces statuts)
    b = BonReception(numero_bon=numero, fournisseur_id=frs.id,
                     entrepot_id=ent.id, date_reception=date.today(),
                     statut=statut)
    db.add(b)
    db.commit()
    return b


def _creer_bon(client, db, ent, frs):
    r = client.post(BASE + "/receptions", json={
        "fournisseur_id": frs.id, "entrepot_id": ent.id})
    assert r.status_code == 201, r.text
    return r.json()


# --------------------------------------------------------------------------- #
# Réceptions : création + validations
# --------------------------------------------------------------------------- #

def test_reception_creation_validations_et_numerotation(client, db):
    ent = _seed_entrepot(db)
    frs = _seed_fournisseur(db)

    # fournisseur inconnu → 400 (FK SQLite non contrôlée : vérification explicite)
    r = client.post(BASE + "/receptions", json={
        "fournisseur_id": 999999, "entrepot_id": ent.id})
    assert r.status_code == 400 and "Fournisseur" in r.json()["detail"]

    # entrepôt inconnu → 400
    r = client.post(BASE + "/receptions", json={
        "fournisseur_id": frs.id, "entrepot_id": 999999})
    assert r.status_code == 400 and "Entrepot" in r.json()["detail"]

    # commande liée inexistante → 400
    r = client.post(BASE + "/receptions", json={
        "fournisseur_id": frs.id, "entrepot_id": ent.id,
        "commande_fournisseur_id": 999999})
    assert r.status_code == 400

    # creation reussie : numero BR-, statut initial en_attente (workflow reel),
    # date du jour par defaut, operateur = utilisateur authentifie
    r = client.post(BASE + "/receptions", json={
        "fournisseur_id": frs.id, "entrepot_id": ent.id})
    assert r.status_code == 201
    data = r.json()
    assert data["numero_bon"].startswith("BR-")
    assert data["statut"] == "en_attente"
    assert data["date_reception"] == date.today().isoformat()
    assert data["operateur"] == 1
    assert data["validateur"] is None and data["date_validation"] is None

    # liste + filtres reels
    r = client.get(BASE + "/receptions", params={"statut": "en_attente",
                                                 "fournisseur_id": frs.id})
    assert r.status_code == 200
    assert any(b["id"] == data["id"] for b in r.json())


def test_reception_lignes_conformite_calculee_et_gardes(client, db):
    ent = _seed_entrepot(db)
    frs = _seed_fournisseur(db)
    bon = _creer_bon(client, db, ent, frs)
    stock = _seed_stock(db, ent, "ART-B19-1", dispo=10)

    # stock inconnu → 404
    r = client.post(f"{BASE}/receptions/{bon['id']}/lignes",
                    json={"stock_id": 999999, "quantite_recue": 5})
    assert r.status_code == 404

    # quantite <= 0 → 400
    r = client.post(f"{BASE}/receptions/{bon['id']}/lignes",
                    json={"stock_id": stock.id, "quantite_recue": 0})
    assert r.status_code == 400

    # ligne conforme : recue == commandee → statut calcule "conforme"
    r = client.post(f"{BASE}/receptions/{bon['id']}/lignes", json={
        "stock_id": stock.id, "quantite_recue": 40,
        "quantite_commandee": 40, "numero_lot": "LOT-9",
        "emplacement": "A-01-A"})
    assert r.status_code == 201
    data = r.json()
    assert data["bon_reception_id"] == bon["id"]     # colonne réelle, pas bon_id
    assert data["stock_id"] == stock.id              # pas article_id
    assert data["statut"] == "conforme"
    assert data["numero_lot"] == "LOT-9"

    # unicite stock/bon : pas de fusion silencieuse
    r = client.post(f"{BASE}/receptions/{bon['id']}/lignes",
                    json={"stock_id": stock.id, "quantite_recue": 5})
    assert r.status_code == 400 and "deja" in r.json()["detail"]

    # deuxieme stock, recu != commande → statut calcule "ecart"
    stock2 = _seed_stock(db, ent, "ART-B19-2", dispo=0)
    r = client.post(f"{BASE}/receptions/{bon['id']}/lignes", json={
        "stock_id": stock2.id, "quantite_recue": 8, "quantite_commandee": 10})
    assert r.status_code == 201 and r.json()["statut"] == "ecart"

    # PATCH du bon avant decision : autorise (correction fournisseur)
    r = client.patch(f"{BASE}/receptions/{bon['id']}",
                     json={"notes": "arrivee partielle"})
    assert r.status_code == 200 and "arrivee partielle" in r.json()["notes"]


# --------------------------------------------------------------------------- #
# Réceptions : validation = stock réel + journal, decision unique
# --------------------------------------------------------------------------- #

def test_reception_valider_adjuste_et_journalise_reelement(client, db):
    ent = _seed_entrepot(db, code="ENT-B19V")
    frs = _seed_fournisseur(db, code="FRS-B19V")
    bon = _creer_bon(client, db, ent, frs)
    stock = _seed_stock(db, ent, "ART-B19-V1", dispo=100)
    stock2 = _seed_stock(db, ent, "ART-B19-V2", dispo=10)

    # bon vide : rien a valider → 400 (pas de 200 menteux)
    r = client.put(f"{BASE}/receptions/{bon['id']}/valider")
    assert r.status_code == 400 and "Aucune ligne" in r.json()["detail"]

    for sid, qty in ((stock.id, 50), (stock2.id, 5)):
        r = client.post(f"{BASE}/receptions/{bon['id']}/lignes",
                        json={"stock_id": sid, "quantite_recue": qty})
        assert r.status_code == 201

    r = client.put(f"{BASE}/receptions/{bon['id']}/valider")
    assert r.status_code == 200, r.text
    data = r.json()
    assert data["statut"] == "valide"
    assert data["validateur"] == 1
    assert data["date_validation"] == date.today().isoformat()  # colonne Date
    assert "[VALIDE" in data["notes"]

    # stock reellement ajuste (quantite_disponible  pas la colonne fantome
    # stock.quantite de l'ancienne version, qui perdait tout en silence)
    db.expire_all()
    assert float(db.query(Stock).get(stock.id).quantite_disponible) == 150.0
    assert float(db.query(Stock).get(stock2.id).quantite_disponible) == 15.0

    # journalisation : un mouvement entree par ligne, avant/apres reels
    mvs = db.query(MouvementStock).filter(
        MouvementStock.document_reference == data["numero_bon"]).all()
    assert len(mvs) == 2
    m = next(m for m in mvs if m.stock_id == stock.id)
    assert str(m.type_mouvement) in ("MouvementType.ENTREE", "entree")
    assert float(m.quantite) == 50.0
    assert float(m.quantite_avant) == 100.0
    assert float(m.quantite_apres) == 150.0

    # decision unique
    r = client.put(f"{BASE}/receptions/{bon['id']}/valider")
    assert r.status_code == 400 and "decision unique" in r.json()["detail"]

    # bon valide immuable : ni PATCH, ni nouvelle ligne
    r = client.patch(f"{BASE}/receptions/{bon['id']}", json={"notes": "x"})
    assert r.status_code == 400 and "immuable" in r.json()["detail"]
    r = client.post(f"{BASE}/receptions/{bon['id']}/lignes",
                    json={"stock_id": stock.id, "quantite_recue": 1})
    assert r.status_code == 400


def test_reception_valider_avec_commande_met_jour_le_registre(client, db):
    ent = _seed_entrepot(db, code="ENT-B19C")
    frs = _seed_fournisseur(db, code="FRS-B19C")
    stock = _seed_stock(db, ent, "ART-B19-C1", dispo=0)

    cmd = CommandeFournisseur(numero_commande="CMD-TEST-B19",
                              fournisseur_id=frs.id, statut="en_cours")
    db.add(cmd)
    db.commit()
    lc = LigneCommandeFournisseur(commande_id=cmd.id, stock_id=stock.id,
                                  quantite_commandee=20, prix_unitaire=1500,
                                  quantite_recue=0, statut="en_attente")
    db.add(lc)
    db.commit()

    r = client.post(BASE + "/receptions", json={
        "fournisseur_id": frs.id, "entrepot_id": ent.id,
        "commande_fournisseur_id": cmd.id})
    assert r.status_code == 201
    bon = r.json()

    r = client.post(f"{BASE}/receptions/{bon['id']}/lignes", json={
        "stock_id": stock.id, "quantite_recue": 20, "quantite_commandee": 20})
    assert r.status_code == 201

    r = client.put(f"{BASE}/receptions/{bon['id']}/valider")
    assert r.status_code == 200

    db.expire_all()
    lc = db.query(LigneCommandeFournisseur).get(lc.id)
    assert float(lc.quantite_recue) == 20.0
    assert lc.statut == "recu"
    assert lc.date_reception == date.today()
    cmd = db.query(CommandeFournisseur).get(cmd.id)
    assert cmd.statut == "livree"                    # statut réel du workflow
    assert cmd.date_livraison_reelle == date.today()


def test_reception_refus_exige_motif_et_ne_bouge_pas_le_stock(client, db):
    ent = _seed_entrepot(db, code="ENT-B19R")
    frs = _seed_fournisseur(db, code="FRS-B19R")
    bon = _creer_bon(client, db, ent, frs)
    stock = _seed_stock(db, ent, "ART-B19-R1", dispo=7)
    r = client.post(f"{BASE}/receptions/{bon['id']}/lignes",
                    json={"stock_id": stock.id, "quantite_recue": 7})
    assert r.status_code == 201

    # motif vide → 400 (une decision opposable sans motif n'existe pas)
    r = client.put(f"{BASE}/receptions/{bon['id']}/refuser", json={"motif": "   "})
    assert r.status_code == 400 and "motif" in r.json()["detail"]

    r = client.put(f"{BASE}/receptions/{bon['id']}/refuser",
                   json={"motif": "marchandise endommagee"})
    assert r.status_code == 200
    data = r.json()
    assert data["statut"] == "refuse" and "[REFUSE" in data["notes"]

    # aucun stock ne bouge : la marchandise refusee n'est pas entree
    db.expire_all()
    assert float(db.query(Stock).get(stock.id).quantite_disponible) == 7.0
    assert db.query(MouvementStock).filter(
        MouvementStock.document_reference == data["numero_bon"]).count() == 0

    # decision unique : refuser/valider un bon deja refuse → 400
    r = client.put(f"{BASE}/receptions/{bon['id']}/refuser", json={"motif": "encore"})
    assert r.status_code == 400 and "decision deja prise" in r.json()["detail"]
    r = client.put(f"{BASE}/receptions/{bon['id']}/valider")
    assert r.status_code == 400 and "reouverture impossible" in r.json()["detail"]


# --------------------------------------------------------------------------- #
# Colis : création, étiquetage réel, palettisation tracée
# --------------------------------------------------------------------------- #

def test_colis_creation_validations_et_numerotation(client, db):
    cli = _seed_client(db)
    ent = _seed_entrepot(db, code="ENT-B19CL")
    bs = BonSortie(numero_bon="BE-TEST-B19CL", client_id=cli.id,
                   entrepot_id=ent.id, date_sortie=date.today(),
                   statut="valide")
    db.add(bs)
    db.commit()

    # bon de sortie lie inexistant → 400
    r = client.post(BASE + "/colis", json={"bon_sortie_id": 999999})
    assert r.status_code == 400 and "Bon de sortie" in r.json()["detail"]

    # type hors liste metier → 400
    r = client.post(BASE + "/colis", json={"type_colis": "valise"})
    assert r.status_code == 400 and "type_colis" in r.json()["detail"]

    # poids negatif → 400
    r = client.post(BASE + "/colis", json={"poids": -3})
    assert r.status_code == 400

    # creation reussie : numero CO-, operateur authentifie, poids/volume reels
    r = client.post(BASE + "/colis", json={
        "type_colis": "carton", "poids": 12.5, "volume": 0.08,
        "dimensions": "40x30x20", "contenu": "pieces detachees",
        "fragile": True, "bon_sortie_id": bs.id})
    assert r.status_code == 201
    data = r.json()
    assert data["numero_colis"].startswith("CO-")
    assert data["operateur"] == 1
    assert data["fragile"] is True
    assert data["date_etiquetage"] is None
    assert float(data["poids"]) == 12.5

    # les colonnes fantomes de l'ancien service ne sont pas revenues
    for champ in ("code_barres", "palette_id", "date_palettisation",
                  "reference_colis", "date_creation"):
        assert champ not in data

    # filtres de liste sur colonnes reelles
    r = client.get(BASE + "/colis", params={"bon_sortie_id": bs.id,
                                            "type_colis": "carton"})
    assert r.status_code == 200 and len(r.json()) == 1


def test_colis_etiquetage_decision_unique(client, db):
    r = client.post(BASE + "/colis", json={"type_colis": "caisse"})
    assert r.status_code == 201
    cid = r.json()["id"]

    inconnu = client.put(f"{BASE}/colis/999999/etiqueter")
    assert inconnu.status_code == 404

    r = client.put(f"{BASE}/colis/{cid}/etiqueter")
    assert r.status_code == 200
    data = r.json()
    assert data["date_etiquetage"] == date.today().isoformat()  # colonne Date reelle

    # etiquette unique : date/operateur traces a la premiere etiquette
    r = client.put(f"{BASE}/colis/{cid}/etiqueter")
    assert r.status_code == 400 and "deja etiquete" in r.json()["detail"]


def test_colis_palettisation_tracee_dans_emplacement(client, db):
    r = client.post(BASE + "/colis", json={"type_colis": "sac"})
    cid = r.json()["id"]

    # reference obligatoire (min_length=1 → 422 FastAPI si absente)
    r = client.put(f"{BASE}/colis/{cid}/palettiser", params={"palette": "PAL-01"})
    assert r.status_code == 200
    assert r.json()["emplacement"] == "palette:PAL-01"

    # 404 colis inconnu
    r = client.put(f"{BASE}/colis/999999/palettiser", params={"palette": "PAL-02"})
    assert r.status_code == 404

    # PATCH : caractéristiques physiques modifiables, type invalide rejeté
    r = client.patch(f"{BASE}/colis/{cid}", json={"poids": 4, "type_colis": "chariot"})
    assert r.status_code == 400
    r = client.patch(f"{BASE}/colis/{cid}", json={"poids": 4})
    assert r.status_code == 200 and float(r.json()["poids"]) == 4.0
    assert r.json()["emplacement"] == "palette:PAL-01"  # conserve


def test_service_fantome_purge(client, db):
    # Batch 19 : plus aucune reference aux classes fantomes du service.
    import app.services.magasin_avance_service as svc
    import app.routers.v1.magasin_avance as routeur
    for nom in ("ColisService", "ReceptionService", "SortieService",
                "RetourService", "KPIStockService"):
        assert not hasattr(svc, nom), nom
        assert not hasattr(routeur, nom), nom
