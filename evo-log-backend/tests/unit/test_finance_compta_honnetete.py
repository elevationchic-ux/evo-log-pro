"""Contrat d'honnetete des endpoints finance/Comptabilite OHADA consommes par
les tableaux de bord (finance-ohada/dashboard, comptabilite-ohada/dashboard).

Ces ecrans affichent desormais des valeurs reellement agregees (plus aucun KPI
ni facture code en dur). Les tests verrouillent la source :

  * /finance/kpis renvoie des zeros honnetes quand la base est vide (jamais de
    faux "847M" invente),
  * /finance/factures et /comptabilite-avance/ecritures renvoient [] sur base vide,
  * une ecriture semee est restituee fidelement (libelle, debit, credit, journal,
    statut de validation reel), sans en inventer.
"""
from datetime import date

URL_KPIS = "/api/v1/finance/kpis"
URL_FACTURES = "/api/v1/finance/factures"
URL_ECRITURES = "/api/v1/comptabilite-avance/ecritures"


def test_kpis_zeros_honnetes_base_vide(client):
    r = client.get(URL_KPIS)
    assert r.status_code == 200, r.text
    k = r.json()
    for cle in (
        "chiffre_affaires", "total_factures", "total_encaisse",
        "montant_impaye", "taux_recouvrement", "creances_douteuses",
        "tresorerie_disponible",
    ):
        assert cle in k
    # Base VIDE -> tout a 0, aucun chiffre invente.
    assert k["chiffre_affaires"] == 0
    assert k["total_factures"] == 0
    assert k["total_encaisse"] == 0
    assert k["taux_recouvrement"] == 0.0


def test_factures_liste_vide_sans_facture(client):
    r = client.get(URL_FACTURES)
    assert r.status_code == 200, r.text
    assert r.json() == []


def test_ecritures_liste_vide(client):
    r = client.get(URL_ECRITURES)
    assert r.status_code == 200, r.text
    assert r.json() == []


def test_ecriture_semee_restituee_fidelement(client, db):
    from app.models.finance_ohada import EcritureComptableNew

    e = EcritureComptableNew(
        numero_ecriture="ECR-TEST-0001",
        date_ecriture=date(2026, 3, 10),
        numero_piece="FAC-TEST-1",
        libelle="Prestation transit",
        debit=1000000,
        credit=0,
        devise="XAF",
        journal="VENTES",
        periode="2026-03",
        valider=False,
    )
    db.add(e)
    db.commit()

    r = client.get(URL_ECRITURES)
    assert r.status_code == 200, r.text
    items = r.json()
    assert len(items) == 1
    d = items[0]
    assert d["numero_ecriture"] == "ECR-TEST-0001"
    assert d["libelle"] == "Prestation transit"
    assert d["journal"] == "VENTES"
    assert float(d["debit"]) == 1000000.0
    assert float(d["credit"]) == 0.0
    # statut reellement non valide -> pas un faux "Validé"
    assert d["valider"] is False
