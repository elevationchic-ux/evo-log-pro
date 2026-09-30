"""Regression portail B2B : resolution du numero de conteneur des dossiers.

``Mission`` n'a AUCUNE relation ORM vers les conteneurs : la cle etrangere
s'appelle ``conteneur_id`` et cible la table ``conteneurs`` (parc acconage).
L'ancien code de ``get_dossiers`` faisait ``joinedload(Mission.conteneur)`` puis
``getattr(m.conteneur, "numero")`` : la relation n'existant pas, la route
levait une erreur. Elle resout desormais la table en une requete, et le numero
reste ``None`` quand aucun conteneur n'est rattache (jamais invente).
"""
from __future__ import annotations

import time

from app.models.acconage import Conteneur
from app.models.tiers import Client
from app.models.transport import Mission, MissionStatus


def _ts() -> int:
    return int(time.time() * 1_000_000) % 100_000_000


def _mission_item(body: dict, reference: str) -> dict:
    for d in body.get("dossiers", []):
        if d.get("origine") == "TRANSPORT" and d.get("reference") == reference:
            return d
    raise AssertionError(f"mission {reference} absente des dossiers")


def test_dossier_remonte_numero_conteneur_rattache(client, db):
    """Un conteneur rattache via conteneur_id remonte son vrai numero."""
    uid = _ts()
    c = Client(code=f"CLI-{uid}", name=f"Client B2B {uid}", city="Douala")
    conteneur = Conteneur(numero=f"MSKU{uid}", type_conteneur="40'HC", statut="full")
    db.add_all([c, conteneur])
    db.commit()

    m = Mission(
        reference=f"BKG-{uid}",
        client_id=c.id,
        conteneur_id=conteneur.id,
        type_mission="enlevement",
        statut=MissionStatus.PLANIFIEE,
        point_depart="Port de Douala",
        point_arrivee="Yaounde",
    )
    db.add(m)
    db.commit()

    resp = client.get("/api/v1/b2b-portal/dossiers", params={"client_id": c.id})
    assert resp.status_code == 200, resp.text
    item = _mission_item(resp.json(), m.reference)
    assert item["conteneur"] == conteneur.numero


def test_dossier_sans_conteneur_n_invente_aucun_numero(client, db):
    """Sans rattachement, le champ conteneur reste null : aucun numero fabrique."""
    uid = _ts() + 7
    c = Client(code=f"CLI-{uid}", name=f"Client B2B vide {uid}", city="Douala")
    db.add(c)
    db.commit()

    m = Mission(
        reference=f"BKG-{uid}",
        client_id=c.id,
        type_mission="livraison",
        statut=MissionStatus.PLANIFIEE,
    )
    db.add(m)
    db.commit()

    resp = client.get("/api/v1/b2b-portal/dossiers", params={"client_id": c.id})
    assert resp.status_code == 200, resp.text
    item = _mission_item(resp.json(), m.reference)
    assert item["conteneur"] is None
