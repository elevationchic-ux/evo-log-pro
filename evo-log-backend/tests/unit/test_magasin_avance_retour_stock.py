"""Batch 20 — Réintégration en stock des retours clients (migration 029).

Le batch 17 avait reconstruit le circuit /retours SANS aucun mouvement de
stock, parce que le modele RetourClient ne portait aucune liaison vers une
ligne de stock — et qu'inventer cette liaison aurait ete du faux. Le rapport
§21 l'avait declare : « une migration ajoutant cette liaison serait le seul
moyen honnete de la rendre reelle ». La migration 029 l'ajoute (stock_id
NULLable), et ces tests verrouillent le comportement NEUF :

* la liaison est optionnelle a la creation, mais VERIFIEE existante si fournie ;
* /traiter reintegre reellement : quantite_disponible augmentee + un
  MouvementStock ENTREE journalise (avant/apres/operateur) quand la ligne est
  precisee, que la decision est `accepte` et que l'action n'est pas
  `destruction` ;
* destruction / refus / absence de liaison : ZERO mouvement ecrit, et la
  raison est tracee dans notes — jamais un mouvement poli mais faux ;
* la migration 029 est idempotente et ne devine aucune donnee (colonne
  NULLable, valeurs existantes laissees a NULL).
"""
from pathlib import Path

from alembic import command
from alembic.config import Config
from sqlalchemy import create_engine, inspect, text

from app.models.magasin import Stock, MouvementStock, MouvementType
from app.models.tiers import Client

BASE = "/api/v1/magasin-avance"


def _seed_client(db, code="CLI-B20"):
    c = Client(code=code, name="Client Reintegration SA")
    db.add(c)
    db.commit()
    return c


def _seed_stock(db, code="ART-B20", quantite=50):
    st = Stock(code_article=code, designation="Sac ciment 45kg",
               quantite_disponible=quantite)
    db.add(st)
    db.commit()
    return st


# --------------------------------------------------------------------------- #
# Creation : la liaison est verifiee, pas devinee
# --------------------------------------------------------------------------- #

def test_retour_creation_valide_lie_stock_existant(client, db):
    cli = _seed_client(db)
    st = _seed_stock(db)

    # ligne de stock inexistante → 400 (FK SQLite non controlee : verification explicite)
    r = client.post(BASE + "/retours", json={
        "client_id": cli.id, "motif": "sac eventre", "stock_id": 999999})
    assert r.status_code == 400 and "stock" in r.json()["detail"].lower()

    # avec une vraie ligne de stock → 201, stock_id echo reel
    r = client.post(BASE + "/retours", json={
        "client_id": cli.id, "motif": "sac eventre", "quantite": 4,
        "stock_id": st.id})
    assert r.status_code == 201
    assert r.json()["stock_id"] == st.id


# --------------------------------------------------------------------------- #
# /traiter : reintegration REELLE quand elle est modelisee
# --------------------------------------------------------------------------- #

def test_retour_accepte_avec_ligne_reintegre_stock_et_journalise(client, db):
    cli = _seed_client(db)
    st = _seed_stock(db, quantite=50)
    r = client.post(BASE + "/retours", json={
        "client_id": cli.id, "motif": "retour livraison", "quantite": 8,
        "stock_id": st.id})
    assert r.status_code == 201
    corps = r.json()

    rep = client.put(f"{BASE}/retours/{corps['id']}/traiter",
                     json={"decision": "accepte", "action": "remplacement"})
    assert rep.status_code == 200

    # Le stock a REELLEMENT bouge (colonne reelle quantite_disponible).
    db.refresh(st)
    assert float(st.quantite_disponible) == 58.0

    # Un seul mouvement, dans le bon sens, avec avant/apres reels.
    mvts = db.query(MouvementStock).filter(
        MouvementStock.stock_id == st.id).all()
    assert len(mvts) == 1
    m = mvts[0]
    assert m.type_mouvement == MouvementType.ENTREE
    assert float(m.quantite) == 8.0
    assert float(m.quantite_avant) == 50.0
    assert float(m.quantite_apres) == 58.0
    assert m.reference == corps["numero_retour"]
    assert m.operateur_id == 1  # faux superuser de la fixture client

    # La reintegration est TRACEE dans notes (decision + fait physique).
    notes = rep.json()["notes"]
    assert "REINTEGRE en stock" in notes and "[TRAITE" in notes


def test_retour_destruction_et_refus_ne_bougent_pas_le_stock(client, db):
    cli = _seed_client(db, code="CLI-B20B")
    st = _seed_stock(db, code="ART-B20B", quantite=30)

    # accepte + destruction : la marchandise est jetee, pas reintegree
    r = client.post(BASE + "/retours", json={
        "client_id": cli.id, "motif": "produit perime", "quantite": 3,
        "stock_id": st.id})
    rid = r.json()["id"]
    rep = client.put(f"{BASE}/retours/{rid}/traiter",
                     json={"decision": "accepte", "action": "destruction"})
    assert rep.status_code == 200
    db.refresh(st)
    assert float(st.quantite_disponible) == 30.0
    assert db.query(MouvementStock).filter(
        MouvementStock.stock_id == st.id).count() == 0

    # refuse : la marchandise repart chez le client, rien n'entre
    r2 = client.post(BASE + "/retours", json={
        "client_id": cli.id, "motif": "hors delai", "quantite": 5,
        "stock_id": st.id})
    rep2 = client.put(f"{BASE}/retours/{r2.json()['id']}/traiter",
                      json={"decision": "refuse"})
    assert rep2.status_code == 200
    db.refresh(st)
    assert float(st.quantite_disponible) == 30.0
    assert db.query(MouvementStock).filter(
        MouvementStock.stock_id == st.id).count() == 0


def test_retour_sans_ligne_accepte_trace_l_absence_de_reintegration(client, db):
    cli = _seed_client(db, code="CLI-B20C")
    # Pas de stock_id : le retour est reel, la decision est prise, mais la
    # reintegration physique est IMPOSSIBLE a ecrire — et cela doit etre
    # declare, pas simule.
    r = client.post(BASE + "/retours", json={
        "client_id": cli.id, "motif": "retour sans ligne designee", "quantite": 2})
    rid = r.json()["id"]
    rep = client.put(f"{BASE}/retours/{rid}/traiter",
                     json={"decision": "accepte", "action": "remboursement"})
    assert rep.status_code == 200
    assert "PAS DE REINTEGRATION STOCK" in rep.json()["notes"]
    assert db.query(MouvementStock).count() == 0
    # NB : stock_id n'est pas modifiable par PATCH (contrat RetourClientUpdate) ;
    # la voie honnete est la creation avec la liaison — verrouillee plus haut.


def test_retour_quantite_absente_refuse_toute_fausse_reintegration(client, db):
    cli = _seed_client(db, code="CLI-B20D")
    st = _seed_stock(db, code="ART-B20D", quantite=10)
    # retour accepte avec ligne mais SANS quantite comptee : impossible de
    # savoir quoi faire entrer → 400 explicite, aucune decision ecrite.
    r = client.post(BASE + "/retours", json={
        "client_id": cli.id, "motif": "colis abime", "stock_id": st.id})
    rid = r.json()["id"]
    rep = client.put(f"{BASE}/retours/{rid}/traiter",
                     json={"decision": "accepte", "action": "remplacement"})
    assert rep.status_code == 400 and "quantite" in rep.json()["detail"].lower()
    corps = client.get(BASE + "/retours").json()
    mine = [x for x in corps if x["id"] == rid][0]
    assert mine["statut"] == "en_attente"  # decision non prise, rien n'est ecrit
    assert db.query(MouvementStock).count() == 0


# --------------------------------------------------------------------------- #
# Migration 029 : idempotence + aucune donnee devinee (base jetable)
# --------------------------------------------------------------------------- #

BACKEND_ROOT = Path(__file__).resolve().parents[2]
ALEMBIC_INI = BACKEND_ROOT / "alembic.ini"
SCRIPT_LOCATION = BACKEND_ROOT / "migrations"


def _make_config() -> Config:
    cfg = Config(str(ALEMBIC_INI))
    cfg.set_main_option("script_location", str(SCRIPT_LOCATION))
    return cfg


def test_migration_029_idempotente_sans_donnee_inventee(tmp_path, monkeypatch):
    db_file = tmp_path / "mig_029.db"
    url = f"sqlite:///{db_file.as_posix()}"
    monkeypatch.setenv("DATABASE_URL", url)
    cfg = _make_config()

    # On simule l'etat PRE-batch 20 : la table existe, sans stock_id.
    engine = create_engine(url)
    with engine.begin() as conn:
        conn.execute(text(
            'CREATE TABLE retours_client ('
            'id INTEGER PRIMARY KEY, numero_retour VARCHAR(50), '
            'client_id INTEGER, motif VARCHAR(200))'
        ))
        conn.execute(text(
            'CREATE TABLE stocks (id INTEGER PRIMARY KEY, code_article VARCHAR(50))'
        ))
        conn.execute(text(
            "INSERT INTO retours_client (id, numero_retour, client_id) "
            "VALUES (1, 'RT-OLD-0001', 7)"
        ))
    engine.dispose()

    command.upgrade(cfg, "029_add_retour_stock_link")

    insp = inspect(create_engine(url))
    colonnes = {c["name"] for c in insp.get_columns("retours_client")}
    assert "stock_id" in colonnes, "la liaison n'a pas ete ajoutee"
    fks = insp.get_foreign_keys("retours_client")
    assert any(fk["referred_table"] == "stocks" for fk in fks), "FK absente"

    # Aucune valeur devinee : l'ancien retour reste NULL (ligne non precisee).
    engine = create_engine(url)
    with engine.connect() as conn:
        valeur = conn.execute(text(
            "SELECT stock_id FROM retours_client WHERE id = 1")).scalar()
    engine.dispose()
    assert valeur is None, "la migration a invente une valeur de liaison"

    # Re-execution sure : remonter la meme revision est un no-op.
    command.upgrade(cfg, "029_add_retour_stock_link")
