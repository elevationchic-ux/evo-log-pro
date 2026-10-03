"""Peremption.numero_serie + ComposantKit.stock_id : colonnes reelles.

Deux sites « champ fantome » du module magasinavance qui plantaient avant
d'etre couverts par un test passant :

* ``POST /magasin-avance/peremptions`` construisait
  ``Peremption(numero_serie=…)`` alors que la table ``peremptions`` n'avait
  JAMAIS eu cette colonne (le schema ``PeremptionCreate``, le service
  ``enregistrer_peremption`` et le routeur la reference pourtant tous).
  -> ``TypeError`` systematique a la moindre inscription de peremption.
  Correction additive idempotente (migration 036) : colonne nullable
  String(100). Aucun numero invente pour les lignes existantes (NULL).

* ``POST /magasin-avance/kits/{id}/composants`` construisait
  ``ComposantKit(article_composant_id=…)`` ; la colonne reelle de
  ``ComposantKit`` est ``stock_id`` (FK stocks.id). Le schema exposait
  donc un champ fantome, et le ``response_model=ComposantKitResponse``
  (from_attributes) n'aurait rien pu relire sur l'objet ORM.
  Correction fidele : ``article_composant_id`` -> ``stock_id`` (schema +
  routeur), sans inventer de semantique.

Ces tests verrouillent le aller/retour REEL des colonnes CORRIGEES. La
fabrication des kits (KitArticle.article_kit_id) et les transferts
multi-entrepots (UniqueConstraint company_id+code_article) restent des
lacunes de modelisation NON resolues ici (decision produit requise) : elles
ne sont donc volontairement pas testees comme si elles fonctionnaient.
"""
from datetime import date, timedelta

from app.models.magasin import Stock, Entrepot
from app.models.magasin_avance import Peremption, KitArticle, ComposantKit

BASE = "/api/v1/magasin-avance"


def _seed_stock(db, code="ART-PER-1"):
    ent = Entrepot(code=f"ENT-{code}", nom="Magasin test")
    db.add(ent)
    db.commit()
    s = Stock(code_article=code, designation=f"Article {code}",
              quantite_disponible=50, entrepot_id=ent.id)
    db.add(s)
    db.commit()
    return s


# --------------------------------------------------------------------------- #
# Peremption.numero_serie (colonne ajoutee par la migration 036)
# --------------------------------------------------------------------------- #

def test_peremption_numero_serie_roundtrip(client, db):
    stock = _seed_stock(db)
    expiry = (date.today() + timedelta(days=30)).isoformat()

    r = client.post(BASE + "/peremptions", json={
        "stock_id": stock.id,
        "date_peremption": expiry,
        "lot_numero": "LOT-A1",
        "quantite": 12,
        "numero_serie": "SN-0001",
    })
    assert r.status_code == 201, r.text
    data = r.json()
    assert data["stock_id"] == stock.id
    assert data["lot_numero"] == "LOT-A1"
    assert float(data["quantite"]) == 12.0
    # le numero de serie traverse reellement la base (pas un champ fantome)
    assert data["numero_serie"] == "SN-0001"

    persisted = db.query(Peremption).filter(Peremption.id == data["id"]).first()
    assert persisted is not None
    assert persisted.numero_serie == "SN-0001"


def test_peremption_sans_numero_serie_est_nullable(client, db):
    stock = _seed_stock(db, code="ART-PER-2")
    expiry = (date.today() + timedelta(days=10)).isoformat()

    r = client.post(BASE + "/peremptions", json={
        "stock_id": stock.id,
        "date_peremption": expiry,
        "lot_numero": "LOT-B2",
        "quantite": 7,
    })
    assert r.status_code == 201, r.text
    data = r.json()
    # champ optionnel : absent -> None, jamais une valeur inventee
    assert data["numero_serie"] is None
    persisted = db.query(Peremption).filter(Peremption.id == data["id"]).first()
    assert persisted.numero_serie is None


# --------------------------------------------------------------------------- #
# ComposantKit.stock_id (colonne reelle, ex-« article_composant_id » fantome)
# --------------------------------------------------------------------------- #

def test_ajouter_composant_utilise_stock_id(client, db):
    kit = KitArticle(code_kit="KIT-TEST-1", nom_kit="Kit de test",
                     description="kit unitaire")
    db.add(kit)
    db.commit()
    stock = _seed_stock(db, code="ART-COMP-1")

    r = client.post(BASE + f"/kits/{kit.id}/composants", json={
        "kit_id": kit.id,
        "stock_id": stock.id,
        "quantite": 3,
    })
    assert r.status_code == 201, r.text
    data = r.json()
    assert data["stock_id"] == stock.id
    assert data["kit_id"] == kit.id
    assert float(data["quantite"]) == 3.0

    persisted = db.query(ComposantKit).filter(ComposantKit.id == data["id"]).first()
    assert persisted is not None
    assert persisted.stock_id == stock.id
