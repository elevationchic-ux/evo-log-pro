"""Contrat de l'endpoint liste des dossiers de transit (transit-avance/dossiers).

La page /transit-douane/dossiers-cemac affiche desormais les dossiers reellement
enregistres (plus aucune rangee codee en dur, plus de colonnes "caution/corridor/
escorte" inventees). Ces tests verrouillent l'honnetete de la source :

  * base vide -> liste vide (aucun dossier fabrique),
  * un dossier semé est restitue avec SES PROPRES champs (numero, destination,
    montant, statut "ouvert" par defaut), sans en ajouter ni en gonfler,
  * le filtre `search` ne renvoie que les dossiers reellement correspondants.
"""
from app.models.transit_avance import (
    DossierTransitAvance, TypeTransit, RegimeDouanier,
)

URL = "/api/v1/transit-avance/dossiers"


def _seed(db, numero, destination="Tchad", montant=2500000.0):
    dossier = DossierTransitAvance(
        numero_dossier=numero,
        client_id=1,
        transitaire_id=1,
        type_transit=TypeTransit.ORDINAIRE,
        regime_douanier=RegimeDouanier.TRANSIT_COMMUNAUTAIRE,
        bureau_entree_id=1,
        bureau_sortie_id=1,
        marchandise="Ciment CPJ",
        valeur_marchandise=10000000.0,
        pays_origine_code="CM",
        pays_destination_code="TD",
        destination=destination,
        montant_total=montant,
        statut="ouvert",
    )
    db.add(dossier)
    db.commit()
    return dossier


def test_liste_vide_sans_dossier(client):
    """Aucun dossier en base -> reponse [] (pas de ligne inventee)."""
    r = client.get(URL)
    assert r.status_code == 200, r.text
    assert r.json() == []


def test_dossier_reel_restitue_fidelement(client, db):
    _seed(db, "TRN-CEMAC-0001")

    r = client.get(URL)
    assert r.status_code == 200, r.text
    items = r.json()
    assert len(items) == 1

    d = items[0]
    assert d["numero_dossier"] == "TRN-CEMAC-0001"
    assert d["destination"] == "Tchad"
    assert d["pays_destination_code"] == "TD"
    assert d["regime_douanier"] == "TRANSIT_COMMUNAUTAIRE"
    assert float(d["montant_total"]) == 2500000.0
    assert d["statut"] == "ouvert"


def test_recherche_filtree_reelle(client, db):
    _seed(db, "TRN-CEMAC-0002")
    _seed(db, "TRN-CEMAC-0003")

    r = client.get(URL, params={"search": "0003"})
    assert r.status_code == 200, r.text
    items = r.json()
    assert [x["numero_dossier"] for x in items] == ["TRN-CEMAC-0003"]

    # recherche sans correspondance -> rien, jamais un resultat fabrique
    r2 = client.get(URL, params={"search": "INEXISTANT"})
    assert r2.json() == []
