"""Contrat des endpoints DUM consommes par /finance-ohada/taxes-cemac.

La page affiche desormais les droits & taxes reellement enregistres (plus aucun
KPI codé en dur). Ces tests verrouillent l'honnetete de la source de donnees :

  * une DUM recemment creee est une ESTIMATION locale : statut "en_attente" et
    reference_sydonia NULL (jamais presentee comme acquittee aupres de SYDONIA),
  * les statistiques agregent bien les lignes reellement en base,
  * la liquidation reste une estimation transparentement documentee.
"""
import random

URL_LIST = "/api/v1/transport/goods-declarations"
URL_STATS = "/api/v1/transport/goods-declarations/stats"


def _create(client, nomenclature):
    return client.post(URL_LIST, json={
        "declarant": "Transitaire Test",
        "importateur": "Importateur Test",
        "marchandise": "Bobines d'acier",
        "nomenclature": nomenclature,
        "valeur_fob": 1000,
        "devise": "USD",
        "taux_change": 600,   # fourni explicitement : pas de taux BEAC invente
    })


def test_dum_creee_restimation_non_acquittee(client):
    """201 + estimation : la DUM n'est ni teletransmise ni acquittee aupres SYDONIA."""
    resp = _create(client, "SH-TEST-0001")
    assert resp.status_code == 201, resp.text
    body = resp.json()
    assert body["estimation"] is True
    # val_caf = 1000 * 1.15 = 1150 ; valeur douane = 1150 * 600 = 690 000
    assert body["valeur_douane_xaf"] == 690_000.0
    # droits 20% (138000) + CAC 10% des droits (13800) + TVA 19.25% assiette
    # (828000*0.1925=159390) + timbre 5000 = 316 190
    assert body["montant_total_taxes"] == 316_190.0


def test_liste_statut_en_attente_et_reference_sydonia_nulle(client):
    nomen = f"SH-TEST-{random.randint(1000, 9999)}"
    assert _create(client, nomen).status_code == 201

    resp = client.get(URL_LIST, params={"search": nomen})
    assert resp.status_code == 200, resp.text
    items = resp.json()["items"]
    assert items, "la DUM creee doit apparaitre dans la liste"
    item = items[0]
    # Honnetete : jamais presentee comme payee/ acquittee aupres de SYDONIA.
    assert item["statut"] == "en_attente"
    assert item["reference_sydonia"] is None
    assert item["droits_douane"] == 138_000.0


def test_stats_agregent_les_lignes_reelles(client):
    assert _create(client, "SH-TEST-STATS").status_code == 201
    resp = client.get(URL_STATS)
    assert resp.status_code == 200, resp.text
    stats = resp.json()
    assert stats["total_declarations"] >= 1
    assert stats["droits_douane_total_xaf"] >= 138_000.0
    # Le contrat de la cle utilisee par la page doit rester stable.
    for cle in ("en_attente", "validees", "liquidees",
                "valeur_douane_totale_xaf", "recettes_fiscales_totales_xaf"):
        assert cle in stats
