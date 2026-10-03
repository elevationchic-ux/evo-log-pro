"""Contrat d'honnetete RH/paie (lane RH & Paie OHADA).

Les ecrans /rh/dashboard, /rh/paie et /rh-personnel/* affichent des chiffres
sensibles (salaires, cotisations, effectifs). Ce test epingle la promesse
cote backend sur laquelle ils s'appuient :

1. listes vides honnetes : aucun bulletin, conge ou employe fictif n'est
   injecte quand la base est vide ;
2. le bulletin renvoyé restitue FIDELEMENT les valeurs frappees en base
   (CNPS/IRGM reellement retenus, statut en minuscules) ;
3. POST /rh/paie/bulletin PERSISTE la fiche (une seule fois par periode :
   409 sinon) et refuse un statut inconnu (400) ;
4. le registre de pointage chef-personnel est vide, pas fabrique.
"""
from datetime import date, datetime

import pytest

from app.models.rh import Conge, Salaire, StatutConge, TypeConge
from app.models.user import User

URL_EMPLOYES = "/api/v1/rh/employes"
URL_PAIE = "/api/v1/rh/paie/bulletin"
URL_CONGES = "/api/v1/rh/conges"
URL_POINTAGES = "/api/v1/chef-personnel/pointages"


def _employe(db, username="salarie.test"):
    u = User(
        username=username,
        email=f"{username}@rh.test",
        hashed_password="x",
        full_name="Collaborateur Test",
        is_active=True,
        is_superuser=False,
        role_level=4,
        company_id=None,
        matricule="MAT-RH-001",
    )
    db.add(u)
    db.commit()
    db.refresh(u)
    return u


def _salaire(db, employe_id):
    s = Salaire(
        employe_id=employe_id,
        mois=3,
        annee=2026,
        salaire_brut=500_000,
        heures_sup=0,
        primes=0,
        deductions=85_000,
        periode_debut=date(2026, 3, 1),
        periode_fin=date(2026, 3, 31),
        salaire_base=480_000,
        heures_supplementaires=0,
        taux_horaire_sup=0,
        prime_transport=20_000,
        deductions_cnps=21_000,
        deductions_impot=54_000,
        deductions_avances=0,
        autres_deductions=10_000,
        salaire_net=415_000,
        devise="XAF",
        statut="en_attente",
    )
    db.add(s)
    db.commit()
    db.refresh(s)
    return s


# --------------------------------------------------------------------------- #
# 1. Listes vides honnetes
# --------------------------------------------------------------------------- #
def test_annuaire_employes_vide_honnete(client):
    r = client.get(URL_EMPLOYES)
    assert r.status_code == 200, r.text
    body = r.json()
    # Contrat front-end : {items, total} -- pas une liste nue, pas de fiction.
    assert body["items"] == []
    assert body["total"] == 0


def test_paie_liste_vide_sans_bulletin_fictif(client):
    r = client.get(URL_PAIE)
    assert r.status_code == 200, r.text
    assert r.json() == []


def test_conges_liste_vide(client):
    r = client.get(URL_CONGES)
    assert r.status_code == 200, r.text
    assert r.json() == []


def test_pointages_registre_vide(client, db):
    # Le module chef-personnel exige une habilitation : on autentifie un vrai
    # User superuser (resolve_current_user le passe tel quel depuis le fix).
    from app.core.security import get_current_user
    from app.main import app

    chef = User(
        username="chef.rh", email="chef.rh@rh.test", hashed_password="x",
        full_name="Chef du Personnel", is_active=True, is_superuser=True,
        role_level=0, company_id=None,
    )
    db.add(chef)
    db.commit()
    db.refresh(chef)

    saved = app.dependency_overrides.get(get_current_user)
    app.dependency_overrides[get_current_user] = lambda: chef
    try:
        r = client.get(URL_POINTAGES)
        assert r.status_code == 200, r.text
        assert r.json() == []
    finally:
        if saved is not None:
            app.dependency_overrides[get_current_user] = saved


# --------------------------------------------------------------------------- #
# 2. Restitution fidele des valeurs frappees
# --------------------------------------------------------------------------- #
def test_bulletin_restitue_les_valeurs_reelles(client, db):
    emp = _employe(db)
    _salaire(db, emp.id)

    r = client.get(URL_PAIE)
    assert r.status_code == 200, r.text
    fiches = r.json()
    assert len(fiches) == 1
    f = fiches[0]
    # CNPS/IRGM = ce qui a ete retenu, pas un taux de marche re-applique.
    assert float(f["cotisations_cnps"]) == 21_000.0
    assert float(f["retenues_fiscales"]) == 54_000.0
    assert float(f["net_a_payer"]) == 415_000.0
    assert f["periode"] == "2026-03"
    # Le statut remonte dans sa valeur d'enum, en minuscules.
    assert f["statut"] == "en_attente"


def test_annuaire_employes_matricule_reel(client, db):
    emp = _employe(db)
    r = client.get(URL_EMPLOYES)
    body = r.json()
    assert body["total"] == 1
    item = body["items"][0]
    assert item["matricule"] == "MAT-RH-001"
    assert item["full_name"] == "Collaborateur Test"
    # Sans contrat porte, le salaire de base reste null : rien n'est devine.
    assert item["salaire_base"] is None
    assert item["type_contrat"] is None


# --------------------------------------------------------------------------- #
# 3. La fiche calculee par le serveur est bien persistee
# --------------------------------------------------------------------------- #
def test_fiche_paie_persistee_puis_pas_de_duplicate(client, db):
    emp = _employe(db)
    payload = {
        "employe_id": emp.id,
        "mois": 5,
        "annee": 2026,
        "salaire_base": 300_000,
        "heures_supplementaires": 0,
        "primes": [],
        "deductions": [],
        "statut": "en_attente",
    }
    r = client.post(URL_PAIE, json=payload)
    assert r.status_code == 201, r.text
    bulletin = r.json()
    # Le net provient du calcul serveur, pas d'une saisine ecran.
    assert float(bulletin["net_a_payer"]) > 0
    assert float(bulletin["salaire_brut"]) == 300_000.0

    # La liste la voit desormais : elle n'etait pas que repondue, elle est en base.
    lst = client.get(URL_PAIE).json()
    assert any(f["id"] == bulletin["id"] for f in lst)

    # Meme employe + meme periode -> 409, jamais un doublon silencieux.
    r2 = client.post(URL_PAIE, json=payload)
    assert r2.status_code == 409
    assert "existe deja" in r2.json()["detail"]


def test_fiche_paie_statut_inconnu_refuse(client, db):
    emp = _employe(db)
    r = client.post(URL_PAIE, json={
        "employe_id": emp.id,
        "mois": 6,
        "annee": 2026,
        "salaire_base": 250_000,
        "statut": "VALIDEE_PAR_ECRAN",
    })
    assert r.status_code == 400
    assert "Statut de paie inconnu" in r.json()["detail"]


# --------------------------------------------------------------------------- #
# 4. Conges : la demande enregistree est restituee telle quelle
# --------------------------------------------------------------------------- #
def test_conge_enregistre_restitue(client, db):
    emp = _employe(db, username="conge.test")
    db.add(Conge(
        employe_id=emp.id,
        type_conge=TypeConge.CONGE_ANNUEL,
        date_debut=date(2026, 8, 1),
        date_fin=date(2026, 8, 10),
        nombre_jours=10,
        statut=StatutConge.EN_ATTENTE,
        motif=None,
        date_demande=datetime(2026, 7, 1, 9, 0),
    ))
    db.commit()

    r = client.get(URL_CONGES)
    assert r.status_code == 200, r.text
    conges = r.json()
    assert len(conges) == 1
    c = conges[0]
    assert c["statut"] == "en_attente"
    assert c["type_conge"] == "conge_annuel"
    assert c["employe_nom"] == "Collaborateur Test"
    # Un motif absent reste absent : jamais de phrase de remplissage.
    assert c["motif"] is None
