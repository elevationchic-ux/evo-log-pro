"""Contrat d'honnetete du calculateur de taxation CEMAC (moteur UNIQUE).

La page /transit-douane/taxation-cameroun ne code plus aucun tarif en dur : elle
delegue a POST /api/v1/transit-douane-avance/taxation/simuler. Ces tests verrouillent
la promesse qui rend cet ecran honnete :

  * tout montant repose sur un taux resolu selon un ordre explicite
    (nomenclature CEMAC -> taux manuel -> categorie TEC -> defaut de simulation),
  * la reponse porte toujours ``source_taux`` + ``simulation`` pour que l'ecran
    affiche la provenance reelle du taux,
  * un taux fantome n'est jamais facture silencieusement,
  * une categorie TEC invalide repond 400 (motif lisible), jamais un 500 muet.
"""
from app.models.transit_avance import NomenclatureCEMAC

URL = "/api/v1/transit-douane-avance/taxation/simuler"


def _post(client, **payload):
    body = {"valeur_cif_xaf": 100_000, "code_sh": payload.pop("code_sh", "0000.00.00")}
    body.update(payload)
    return client.post(URL, json=body)


def test_position_absente_repli_simulation_honnete(client):
    """SH inconnu en base -> taux par defaut 20% MAIS marque simulation."""
    resp = _post(client, code_sh="9999.99.99")
    assert resp.status_code == 200, resp.text
    body = resp.json()
    assert body["source_taux"] == "defaut_simulation"
    assert body["simulation"] is True
    assert body["taux_dd"] == 0.20
    # DD = 20% de l'assiette, jamais un montant invente.
    assert body["droit_douane_dd"] == 20_000.0
    assert "note" in body and body["note"]


def test_categorie_tec_explicite_source_categorie_tec(client):
    resp = _post(client, code_sh="9999.99.99", categorie_tec=1)
    assert resp.status_code == 200, resp.text
    body = resp.json()
    assert body["source_taux"] == "categorie_tec"
    assert body["taux_dd"] == 0.05
    assert body["simulation"] is True
    assert body["droit_douane_dd"] == 5_000.0


def test_taux_manuel_prioritaire_source_manuelle(client):
    """Un taux saisi a la main est prioritaire sur la categorie TEC, mais reste
    signale comme simulation (il ne provient pas de la nomenclature officielle)."""
    resp = _post(client, code_sh="9999.99.99", taux_dd_explicite=10)
    assert resp.status_code == 200, resp.text
    body = resp.json()
    assert body["source_taux"] == "manuel"
    assert body["taux_dd"] == 0.10
    assert body["simulation"] is True
    assert body["droit_douane_dd"] == 10_000.0


def test_categorie_tec_invalide_repond_400_et_non_500(client):
    resp = _post(client, code_sh="1234.56.78", categorie_tec=7)
    assert resp.status_code == 400
    assert "Categorie TEC" in resp.json()["detail"]


def test_nomenclature_reelle_en_base_source_nomenclature(client, db):
    """Quand la position SH existe (statut actif), le taux vient de la base :
    source = nomenclature_cemac et simulation = False."""
    db.add(NomenclatureCEMAC(
        code_hs="8471.30.00",
        description="Machines automatiques de traitement de l'information",
        taux_dd=10.0,   # saisi en pourcentage, normalise en fraction par le moteur
        taux_tva=19.25,
        statut="actif",
        source_reference="TEC CEMAC (test)",
    ))
    db.commit()

    resp = _post(client, code_sh="8471.30.00")
    assert resp.status_code == 200, resp.text
    body = resp.json()
    assert body["source_taux"] == "nomenclature_cemac"
    assert body["simulation"] is False
    assert body["taux_dd"] == 0.10
    assert body["droit_douane_dd"] == 10_000.0


def test_origine_cemac_exonere_le_droit_de_douane(client):
    resp = _post(client, code_sh="9999.99.99", categorie_tec=3, origine="CEMAC")
    assert resp.status_code == 200, resp.text
    body = resp.json()
    assert body["source_taux"] == "exoneration_origine"
    assert body["droit_douane_dd"] == 0.0
    # La TVA reste due a l'importation meme quand le DD est exonere.
    assert body["tva_1925"] > 0


def test_total_coherent_avec_composantes(client):
    body = _post(client, code_sh="9999.99.99").json()
    composantes = (
        body["droit_douane_dd"] + body["redevance_informatique"] + body["cci_cemac"]
        + body["prelevement_ohada"] + body["tva_1925"] + body["precompte_is"]
    )
    assert abs(body["total_a_liquider_xaf"] - composantes) < 1.0
