"""Batch 18 — Inventaires tournants, évaluations/performance fournisseur, réappro.

Les sept endpoints de app/routers/v1/magasin_avance.py (sections Inventaires /
Fournisseurs / Réapprovisionnement) étaient morts du syndrome « champs
fantômes » : InventaireTournant(date_inventaire=…), stock.quantite (inexistant
→ AttributeError), FournisseurStock(delai_livraison_jours/qualite/fiabilite=…),
cmd.date_livraison/date_prevue, CommandeFournisseur(reference=…),
LigneCommandeFournisseur(article_id=stock.article_id…) — et le statut
inventaire "valide" hors du workflow réel planifie/en_cours/termine/annule.

Ces tests verrouillent le comportement NEUF, sur colonnes réelles :
* inventaire : numérotation INV-, comptage théorique = quantite_disponible,
  unicité du comptage, validation → statut `termine` + ajustement RÉELLEMENT
  persisté + journal MouvementStock (aucune correction invisible) ;
* précision : sans ligne comptée → None + « non mesurée », jamais un faux 0 % ;
* évaluation fournisseur : notes 1-10 validées, note_globale calculée ou None ;
* performance : aucune commande → note None (pas 0/100) ; statut réel « livree » ;
* réappro : UNE commande groupée, prix réels de la fiche stock, stocks sans
  prix IGNORES et déclarés — jamais de prix 0.0 inventé.
"""
from datetime import date

from app.models.magasin import Stock, Entrepot, MouvementStock
from app.models.magasin_avance import (
    InventaireTournant, LigneInventaire, CommandeFournisseur, FournisseurStock,
)
from app.models.tiers import Fournisseur

BASE = "/api/v1/magasin-avance"


# --------------------------------------------------------------------------- #
# Seeds
# --------------------------------------------------------------------------- #

def _seed_entrepot(db, code="ENT-B18"):
    ent = Entrepot(code=code, nom="Magasin B18")
    db.add(ent)
    db.commit()
    return ent


def _seed_stock(db, ent, code_article, dispo, prix=None):
    s = Stock(code_article=code_article, designation=f"Article {code_article}",
              quantite_disponible=dispo, prix_unitaire=prix, entrepot_id=ent.id)
    db.add(s)
    db.commit()
    return s


def _seed_fournisseur(db, code="FRS-B18"):
    f = Fournisseur(code=code, name="Import Distribution SARL")
    db.add(f)
    db.commit()
    return f


def _seed_inventaire(db, ent, statut="en_cours"):
    i = InventaireTournant(numero_inventaire=f"INV-TEST-{ent.id}-{statut}",
                           entrepot_id=ent.id, date_debut=date.today(),
                           statut=statut)
    db.add(i)
    db.commit()
    return i


# --------------------------------------------------------------------------- #
# Inventaires : création + comptage
# --------------------------------------------------------------------------- #

def test_inventaire_creation_et_validations(client, db):
    ent = _seed_entrepot(db)

    r = client.post(BASE + "/inventaires", json={
        "entrepot_id": 999999, "date_debut": date.today().isoformat()})
    assert r.status_code == 404

    r = client.post(BASE + "/inventaires", json={
        "entrepot_id": ent.id, "date_debut": "2026-05-10", "date_fin": "2026-05-01"})
    assert r.status_code == 400 and "date_fin" in r.json()["detail"]

    r = client.post(BASE + "/inventaires", json={
        "entrepot_id": ent.id, "date_debut": "2026-05-01", "type_inventaire": "cyclique"})
    assert r.status_code == 201
    data = r.json()
    assert data["numero_inventaire"].startswith("INV-")
    assert data["statut"] == "en_cours"
    assert data["responsable"] == 1  # utilisateur authentifié du harnais


def test_ligne_inventaire_theorique_ecart_et_unicite(client, db):
    ent = _seed_entrepot(db)
    inv = _seed_inventaire(db, ent)
    stock = _seed_stock(db, ent, "ART-B18-1", dispo=50)

    r = client.post(f"{BASE}/inventaires/{inv.id}/lignes",
                    json={"stock_id": 999999, "quantite_comptee": 10})
    assert r.status_code == 404

    r = client.post(f"{BASE}/inventaires/{inv.id}/lignes",
                    json={"stock_id": stock.id, "quantite_comptee": -5})
    assert r.status_code == 400

    r = client.post(f"{BASE}/inventaires/{inv.id}/lignes",
                    json={"stock_id": stock.id, "quantite_comptee": 48})
    assert r.status_code == 201
    data = r.json()
    assert data["quantite_theorique"] == 50.0      # colonne réelle, pas stock.quantite
    assert data["ecart"] == -2.0
    assert data["statut"] == "compte"
    assert data["operateur"] == 1                   # compteur_id fantôme → operateur réel

    # Deuxième comptage du même stock : refusé, pas fusionné en silence
    r = client.post(f"{BASE}/inventaires/{inv.id}/lignes",
                    json={"stock_id": stock.id, "quantite_comptee": 47})
    assert r.status_code == 400 and "déjà été compté" in r.json()["detail"]

    # Inventaire terminé : plus aucun comptage
    inv.statut = "termine"
    db.commit()
    stock2 = _seed_stock(db, ent, "ART-B18-2", dispo=5)
    r = client.post(f"{BASE}/inventaires/{inv.id}/lignes",
                    json={"stock_id": stock2.id, "quantite_comptee": 5})
    assert r.status_code == 400


def test_valider_inventaire_ajuste_stock_et_journalise(client, db):
    ent = _seed_entrepot(db)
    inv = _seed_inventaire(db, ent)
    stock_ecart = _seed_stock(db, ent, "ART-B18-E", dispo=50)
    stock_conforme = _seed_stock(db, ent, "ART-B18-C", dispo=10)

    for s, comptee in ((stock_ecart, 46), (stock_conforme, 10)):
        r = client.post(f"{BASE}/inventaires/{inv.id}/lignes",
                        json={"stock_id": s.id, "quantite_comptee": comptee})
        assert r.status_code == 201

    r = client.put(f"{BASE}/inventaires/{inv.id}/valider")
    assert r.status_code == 200
    data = r.json()
    assert data["statut"] == "termine"  # workflow RÉEL, plus de "valide" fantôme
    assert "[VALIDE" in (data["notes"] or "")

    db.expire_all()
    # Ajustement réellement persisté sur la colonne réelle
    assert float(stock_ecart.quantite_disponible) == 46.0
    assert float(stock_conforme.quantite_disponible) == 10.0

    # … et journalisé : UN seul mouvement (le conforme n'a pas d'écart)
    mvts = db.query(MouvementStock).filter(
        MouvementStock.document_reference == inv.numero_inventaire).all()
    assert len(mvts) == 1
    assert str(mvts[0].type_mouvement).endswith("inventaire")
    assert float(mvts[0].quantite_avant) == 50.0
    assert float(mvts[0].quantite_apres) == 46.0

    # Décision unique
    r = client.put(f"{BASE}/inventaires/{inv.id}/valider")
    assert r.status_code == 400 and "déjà validé" in r.json()["detail"]


def test_valider_inventaire_vide_refuse(client, db):
    ent = _seed_entrepot(db)
    inv = _seed_inventaire(db, ent)
    r = client.put(f"{BASE}/inventaires/{inv.id}/valider")
    assert r.status_code == 400 and "Aucune ligne" in r.json()["detail"]


# --------------------------------------------------------------------------- #
# Précision : pas de faux 0 %
# --------------------------------------------------------------------------- #

def test_precision_inventaire_honnete(client, db):
    ent = _seed_entrepot(db)
    inv = _seed_inventaire(db, ent)

    r = client.get(f"{BASE}/inventaires/999999/precision")
    assert r.status_code == 404

    # Aucun comptage → non mesurée, pas 0.0
    r = client.get(f"{BASE}/inventaires/{inv.id}/precision")
    assert r.status_code == 200
    data = r.json()
    assert data["precision"] is None
    assert "non mesurée" in data["message"]

    # 4 lignes dont 3 sans écart → 75 %
    for n, (theo, comptee) in enumerate(
            ((10, 10), (20, 20), (30, 30), (40, 35))):
        db.add(LigneInventaire(inventaire_id=inv.id, stock_id=n + 1,
                               quantite_theorique=float(theo),
                               quantite_comptee=float(comptee),
                               ecart=float(comptee) - theo, statut="compte"))
    db.commit()
    r = client.get(f"{BASE}/inventaires/{inv.id}/precision")
    data = r.json()
    assert data["lignes_total"] == 4
    assert data["lignes_correctes"] == 3
    assert data["precision"] == 75.0


# --------------------------------------------------------------------------- #
# Évaluation + performance fournisseur
# --------------------------------------------------------------------------- #

def test_evaluation_fournisseur_validee_note_calculee(client, db):
    f = _seed_fournisseur(db)

    r = client.post(BASE + "/fournisseurs-stock", json={"fournisseur_id": 999999})
    assert r.status_code == 404

    r = client.post(BASE + "/fournisseurs-stock", json={
        "fournisseur_id": f.id, "qualite_produit": 15})
    assert r.status_code == 400 and "entre 1 et 10" in r.json()["detail"]

    r = client.post(BASE + "/fournisseurs-stock", json={
        "fournisseur_id": f.id, "qualite_produit": 8, "prix_competitif": 9,
        "service_client": 10, "delai_moyen_livraison": 12})
    assert r.status_code == 201
    data = r.json()
    assert data["note_globale"] == 9.0   # moyenne des notes fournies
    assert data["evaluateur"] == 1
    assert data["date_evaluation"] == date.today().isoformat()

    # Aucune note fournie → note_globale None, pas de 0 inventé
    r = client.post(BASE + "/fournisseurs-stock", json={
        "fournisseur_id": f.id, "delai_moyen_livraison": 5})
    assert r.status_code == 201 and r.json()["note_globale"] is None


def test_performance_fournisseur_sans_faux_zero(client, db):
    f = _seed_fournisseur(db)
    debut, fin = "2026-01-01", "2026-12-31"

    r = client.get(f"{BASE}/fournisseurs/999999/performance"
                   f"?debut_periode={debut}&fin_periode={fin}")
    assert r.status_code == 404

    r = client.get(f"{BASE}/fournisseurs/{f.id}/performance"
                   f"?debut_periode={fin}&fin_periode={debut}")
    assert r.status_code == 400

    # Aucune commande → non évaluée (jamais note 0/100)
    r = client.get(f"{BASE}/fournisseurs/{f.id}/performance"
                   f"?debut_periode={debut}&fin_periode={fin}")
    assert r.status_code == 200
    data = r.json()
    assert data["note"] is None and data["commandes"] == 0
    assert "non évaluée" in data["message"]

    # 2 commandes : 1 livrée en retard de +2j (réel : date_livraison_reelle /
    # _prevue, statut "livree"), 1 en cours → taux 50, délai +2
    db.add(CommandeFournisseur(
        numero_commande="CMD-PF-1", fournisseur_id=f.id,
        date_commande=date(2026, 5, 1),
        date_livraison_prevue=date(2026, 5, 10),
        date_livraison_reelle=date(2026, 5, 12), statut="livree"))
    db.add(CommandeFournisseur(
        numero_commande="CMD-PF-2", fournisseur_id=f.id,
        date_commande=date(2026, 6, 1), statut="en_cours"))
    db.commit()

    r = client.get(f"{BASE}/fournisseurs/{f.id}/performance"
                   f"?debut_periode={debut}&fin_periode={fin}")
    data = r.json()
    assert data["commandes"] == 2 and data["commandes_livrees"] == 1
    assert data["taux_livraison"] == 50.0
    assert data["delai_moyen_jours"] == 2.0
    # note = 50*0.7 + (100-2)*0.3 = 64.4
    assert data["note"] == 64.4


# --------------------------------------------------------------------------- #
# Réapprovisionnement automatique
# --------------------------------------------------------------------------- #

def test_reappro_commande_groupee_prix_reels(client, db):
    ent = _seed_entrepot(db)
    f = _seed_fournisseur(db, code="FRS-B18-R")
    ok = _seed_stock(db, ent, "ART-R-1", dispo=5, prix=500)
    sans_prix = _seed_stock(db, ent, "ART-R-2", dispo=2, prix=None)
    _seed_stock(db, ent, "ART-R-3", dispo=200, prix=100)  # au-dessus du seuil

    r = client.post(f"{BASE}/reapprovisionnement/automatique/999999?seuil_alerte=10")
    assert r.status_code == 404

    r = client.post(f"{BASE}/reapprovisionnement/automatique/{f.id}?seuil_alerte=0")
    assert r.status_code == 400

    r = client.post(f"{BASE}/reapprovisionnement/automatique/{f.id}?seuil_alerte=10")
    assert r.status_code == 200, r.json()
    data = r.json()
    assert data["numero_commande"].startswith("CMD-")
    assert len(data["lignes"]) == 1 and data["lignes"][0]["stock_id"] == ok.id
    assert data["lignes"][0]["prix_unitaire"] == 500.0   # prix RÉEL de la fiche
    assert data["lignes"][0]["quantite_commandee"] == 20.0
    assert len(data["ignorees"]) == 1
    assert data["ignorees"][0]["stock_id"] == sans_prix.id
    assert "prix" in data["ignorees"][0]["raison"]

    cmd = db.query(CommandeFournisseur).filter(
        CommandeFournisseur.numero_commande == data["numero_commande"]).first()
    assert cmd is not None
    assert float(cmd.montant_total) == 10000.0  # 20 × 500, pas 0.0 × n
    assert cmd.statut == "en_cours"


def test_reappro_jamais_de_prix_invente(client, db):
    ent = _seed_entrepot(db)
    f = _seed_fournisseur(db, code="FRS-B18-NP")
    _seed_stock(db, ent, "ART-NP-1", dispo=1, prix=None)

    r = client.post(f"{BASE}/reapprovisionnement/automatique/{f.id}?seuil_alerte=10")
    # Seul stock sous seuil sans prix → commande refusée, AUCUNE commande créée
    assert r.status_code == 400
    assert "Aucun stock commandable" in r.json()["detail"]
    assert db.query(CommandeFournisseur).count() == 0
    assert db.query(FournisseurStock).count() == 0
