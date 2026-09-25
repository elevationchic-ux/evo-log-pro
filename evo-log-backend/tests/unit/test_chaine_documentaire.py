"""Tests du batch 8 - fermeture de la chaine documentaire (migration 024).

Verrouille trois choses :
  • la migration 024 est IDEMPOTENTE dans les deux sens (re-execution sure),
    et la chaine complete reste montante/descendante sur base vierge ;
  • le dossier marchandise ne montre aux etapes aval QUE les enregistrements
    explicitement rattaches (FK conteneur_id / escale_id / numero_bl saisis) ;
  • les API qui creent ces enregistrements acceptent desormais les liens
    (mission via schema, facture via payload), sans jamais les deviner.

Aucune donnee n'est inventee ici : un lien absent reste absent.
"""
import os
from datetime import date

import pytest
from alembic import command
from alembic.config import Config
from sqlalchemy import create_engine, inspect
from sqlalchemy.orm import Session

from app.models.acconage import Connaissement, Conteneur, Escale, Navire
from app.models.finance_ohada import FactureNew
from app.models.transport import Mission
from app.services.dossier_marchandise import consigner_dossier_marchandise

BACKEND_ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
ALEMBIC_INI = os.path.join(BACKEND_ROOT, "alembic.ini")
SCRIPT_LOCATION = os.path.join(BACKEND_ROOT, "migrations")

REV_023 = "023_add_tarif_cemac_provenance"
REV_024 = "024_add_chaine_documentaire_links"

TABLES_COLONNES = {
    "declarations_douaniere_avance": ("conteneur_id", "escale_id", "numero_bl"),
    "factures_ohada": ("conteneur_id", "escale_id"),
    "missions": ("conteneur_id", "numero_bl"),
}


def _cfg() -> Config:
    cfg = Config(str(ALEMBIC_INI))
    cfg.set_main_option("script_location", str(SCRIPT_LOCATION))
    return cfg


def _colonnes(url: str, table: str):
    insp = inspect(create_engine(url))
    if table not in set(insp.get_table_names()):
        return set()
    return {c["name"] for c in insp.get_columns(table)}


# --------------------------------------------------------------------------- #
# 1. Migration : montee idempotente, descente propre, remontee stable
# --------------------------------------------------------------------------- #
def test_024_montee_idempotente_et_reversible(tmp_path, monkeypatch):
    db_file = tmp_path / "cha024.db"
    url = f"sqlite:///{db_file.as_posix()}"
    monkeypatch.setenv("DATABASE_URL", url)
    cfg = _cfg()

    # On monte la chaine jusqu'a l'avant-derniere revision, puis 024 DEUX FOIS
    # (re-execution forcee) : la garde d'inspection doit rendre le 2e passage
    # inoffensif.
    command.upgrade(cfg, REV_023)
    command.upgrade(cfg, REV_024)
    first = {t: _colonnes(url, t) for t in TABLES_COLONNES}
    command.stamp(cfg, REV_023)
    command.upgrade(cfg, REV_024)
    second = {t: _colonnes(url, t) for t in TABLES_COLONNES}
    for table, cols in TABLES_COLONNES.items():
        if not first[table]:
            continue  # table creee hors chaine sur ce profil : rien a verifier
        for col in cols:
            assert col in second[table], f"{table}.{col} absente apres re-upgrade"

    # Descente vers 023 : les colonnes disparaissent proprement (round-trip).
    command.downgrade(cfg, REV_023)
    for table, cols in TABLES_COLONNES.items():
        if not first[table]:
            continue
        after = _colonnes(url, table)
        for col in cols:
            if col in first[table]:
                assert col not in after, f"{table}.{col} survit au downgrade"

    command.upgrade(cfg, REV_024)
    # Aprues round-trip complet, la tete est revenue a 024 et le schéma est
    # identique au premier passage (aucune dérive).
    for table, cols in TABLES_COLONNES.items():
        if not first[table]:
            continue
        final = _colonnes(url, table)
        assert final == first[table] | set(cols) or final == first[table]


# --------------------------------------------------------------------------- #
# 2. Dossier : seuls les liens saisis explicitement remontent
# --------------------------------------------------------------------------- #
def _ancre(db: Session):
    navire = Navire(nom="CMA CGM Mont Louis", imo="9396237", armateur="CMA CGM")
    db.add(navire)
    db.flush()
    escale = Escale(numero_escale="ESC-024", navire_id=navire.id, statut="arrivee")
    db.add(escale)
    db.flush()
    conteneur = Conteneur(numero="CMAU1234567", type_conteneur="40'HC",
                          statut="full", navire_id=navire.id)
    db.add(conteneur)
    db.flush()
    db.add(Connaissement(numero_bl="CMAUBLGH024", conteneur_id=conteneur.id,
                         escale_id=escale.id, statut="emis"))
    db.commit()
    return conteneur, escale


def _etape(dossier, cle):
    return next(e for e in dossier["etapes"] if e["cle"] == cle)


def test_facture_rattachee_par_escale_rembousse_dans_le_dossier(db: Session):
    conteneur, escale = _ancre(db)
    db.add(FactureNew(
        numero_facture="FAC-024-A", type_facture="prestation",
        date_emission=date(2026, 2, 1), montant_ht=100_000, montant_ttc=119_250,
        escale_id=escale.id,
    ))
    db.add(FactureNew(
        numero_facture="FAC-024-B", type_facture="vente",
        date_emission=date(2026, 2, 1), montant_ht=50_000, montant_ttc=59_625,
        # aucune FK : ne doit PAS apparaitre dans le dossier
    ))
    db.commit()

    d = consigner_dossier_marchandise(db, numero_conteneur="CMAU1234567")
    fac = _etape(d, "facture")
    numeros = {r["numero_facture"] for r in fac["enregistrements"]}
    assert numeros == {"FAC-024-A"}  # jamais la facture sans lien
    assert fac["etat"] == "reel"


def test_mission_saisie_par_numero_bl_rembousse(db: Session):
    conteneur, escale = _ancre(db)
    db.add(Mission(reference="MIS-024-BL", type_mission="livraison",
                   numero_bl="CMAUBLGH024"))
    db.add(Mission(reference="MIS-024-VIDE", type_mission="livraison"))
    db.commit()
    d = consigner_dossier_marchandise(db, numero_bl="CMAUBLGH024")
    refs = {r["reference"] for r in _etape(d, "livraison")["enregistrements"]}
    assert refs == {"MIS-024-BL"}


# --------------------------------------------------------------------------- #
# 3. API : les liens sont acceptes a la creation, pas devines
# --------------------------------------------------------------------------- #
def test_api_mission_accepte_conteneur_id(db: Session, client):
    conteneur, escale = _ancre(db)
    r = client.post("/api/v1/transport/missions", json={
        "reference": "MIS-API-024",
        "type_mission": "livraison",
        "conteneur_id": conteneur.id,
        "numero_bl": "CMAUBLGH024",
    })
    assert r.status_code in (200, 201), r.text
    body = r.json()
    assert body["conteneur_id"] == conteneur.id
    assert body["numero_bl"] == "CMAUBLGH024"
    # Verification en base, pas seulement dans la reponse.
    m = db.query(Mission).filter(Mission.reference == "MIS-API-024").first()
    db.expire_all()
    assert m is not None and m.conteneur_id == conteneur.id


def test_api_facture_accepte_escale_id(db: Session, client):
    from app.core.security import get_current_user, get_password_hash
    from app.main import app
    from app.models.user import User

    conteneur, escale = _ancre(db)
    agent = User(
        username="fact024", email="fact024@test.cm",
        hashed_password=get_password_hash("Admin12345"),
        is_active=True, is_superuser=False, role_level=2, company_id=None,
    )
    db.add(agent)
    db.commit()
    app.dependency_overrides[get_current_user] = lambda: agent
    try:
        r = client.post("/api/v1/auto-invoicing/", json={
            "type_facture": "prestation",
            "montant_ht": 250_000,
            "date_emission": "2026-02-03",
            "escale_id": escale.id,
            "conteneur_id": conteneur.id,
        })
        assert r.status_code == 200, r.text
        fac = db.query(FactureNew).filter(
            FactureNew.id == r.json()["id"]).first()
        db.refresh(fac)
        assert fac.escale_id == escale.id
        assert fac.conteneur_id == conteneur.id
    finally:
        app.dependency_overrides.clear()
