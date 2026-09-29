"""Portail salarié : le type de congé déposé doit être celui qui est enregistré.

Le routeur acceptait le ``type_conge`` par rapprochement de sous-chaînes
(« maladie », « maternite », « sans »…). L'écran envoie désormais les valeurs
d'enum exactes rendues par l'API, et ``absence_autorisee`` ne contient aucune de
ces sous-chaînes : la demande tombait silencieusement dans la branche par défaut
et le salarié voyait un congé annuel enregistré à la place de son absence
autorisée — sur un document social, ce n'est pas un détail d'affichage.

Couvre aussi le contrat de l'écran : les statuts doivent remonter dans leur
valeur brute (``en_attente``) et non au nom de leur membre (``EN_ATTENTE``),
faute de quoi aucun badge de l'historique ne se déclenche.
"""
from contextlib import contextmanager
from datetime import date, timedelta

import pytest

from app.core.security import get_current_user, get_password_hash
from app.main import app
from app.models.rh import Conge, StatutConge, TypeConge
from app.models.tenant import Company
from app.models.user import User

URL_PORTAIL_CONGES = "/api/v1/rh/portail/conges"


@contextmanager
def _identite(user):
    """Surcharge d'identité qui rend la précédente (contrat de la fixture client)."""
    saved = app.dependency_overrides.get(get_current_user)
    app.dependency_overrides[get_current_user] = lambda: user
    try:
        yield
    finally:
        if saved is not None:
            app.dependency_overrides[get_current_user] = saved


@pytest.fixture
def company(db):
    c = Company(code="PORT", nom="Port Douala SA", is_active=True, modules_actives='["rh"]')
    db.add(c)
    db.commit()
    db.refresh(c)
    return c


@pytest.fixture
def salarie(db, company):
    """Salarie ordinaire : le portail self-service lui est ouvert sans casquette RH."""
    u = User(
        username="salarie-port", email="salarie@port.example",
        hashed_password=get_password_hash("Po12345678"),
        full_name="Kamga Paul", is_active=True, is_superuser=False,
        role_level=4, company_id=company.id, must_change_password=False,
    )
    db.add(u)
    db.commit()
    db.refresh(u)
    return u


def _demander(client, salarie, valeur_type, debut=None, fin=None):
    debut = debut or date.today() + timedelta(days=10)
    fin = fin or debut + timedelta(days=4)
    with _identite(salarie):
        return client.post(URL_PORTAIL_CONGES, json={
            "type_conge": valeur_type,
            "date_debut": debut.isoformat(),
            "date_fin": fin.isoformat(),
            "motif": "",
        })


@pytest.mark.parametrize("valeur", [e.value for e in TypeConge])
def test_chaque_valeur_enum_est_honoree(client, db, salarie, valeur):
    """Une valeur d'enum envoyée telle quelle doit être la valeur stockée."""
    reponse = _demander(client, salarie, valeur)
    assert reponse.status_code == 201, reponse.text
    assert reponse.json()["type_conge"] == valeur

    enregistre = db.query(Conge).filter(Conge.id == reponse.json()["id"]).first()
    assert enregistre is not None
    assert enregistre.type_conge.value == valeur


def test_absence_autorisee_ne_devient_pas_conge_annuel(client, db, salarie):
    """Régression : la seule valeur sans sous-clé de repli était mal routée."""
    reponse = _demander(client, salarie, "absence_autorisee")
    assert reponse.status_code == 201, reponse.text

    enregistre = db.query(Conge).filter(Conge.id == reponse.json()["id"]).first()
    assert enregistre.type_conge == TypeConge.ABSENCE_AUTORISEE
    assert enregistre.type_conge != TypeConge.CONGE_ANNUEL


def test_le_motif_vide_reste_vide(client, db, salarie):
    """Aucune phrase de remplissage n'est rédigée à la place du salarié."""
    reponse = _demander(client, salarie, "conge_annuel")
    enregistre = db.query(Conge).filter(Conge.id == reponse.json()["id"]).first()
    assert enregistre.motif is None


def test_statut_rendu_en_valeur_brute(client, db, salarie):
    """L'écran compare des valeurs minuscules : 'EN_ATTENTE' ne matcherait jamais."""
    assert _demander(client, salarie, "conge_annuel").status_code == 201
    with _identite(salarie):
        liste = client.get(URL_PORTAIL_CONGES).json()
    assert len(liste) == 1
    assert liste[0]["statut"] == StatutConge.EN_ATTENTE.value
    assert liste[0]["type_conge"] == TypeConge.CONGE_ANNUEL.value


def test_date_fin_anterieure_refusee(client, salarie):
    debut = date.today() + timedelta(days=20)
    fin = debut - timedelta(days=3)
    with _identite(salarie):
        reponse = client.post(URL_PORTAIL_CONGES, json={
            "type_conge": "conge_annuel",
            "date_debut": debut.isoformat(),
            "date_fin": fin.isoformat(),
            "motif": "Voyage",
        })
    assert reponse.status_code == 400
    assert "antérieure" in reponse.json()["detail"]
