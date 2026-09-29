"""Pytest configuration and fixtures for the EVO-LOG backend.

CONTRAT DE LA FIXTURE `client` (a lire avant d'ecrire un test d'auth) :
- `client` authentifie TOUT par defaut : elle surcharge `get_current_user` avec
  un faux super-utilisateur. Un test qui verifie un refus anonyme (401/403)
  doit utiliser la fixture `unauthenticated` ci-dessous.
- NE JAMAIS appeler `app.dependency_overrides.clear()` en cours de test : cela
  supprime aussi l'override `get_db` et les requetes suivantes partent sur
  l'engine reel de l'application. Le garde-fou `DATABASE_URL` en tete de fichier
  transforme ce scenario en echec bruyant ("no such table") au lieu d'une
  ecriture silencieuse dans la base de dev.

PERFORMANCE NOTES :
- TestClient lifespan is SESSION-SCOPED (starts once ~0.5 s, not per test).
- DB isolation uses outer-transaction + rollback (0.8 ms/test) instead of
  DELETE-all-318-tables (70 ms/test). Total saving: ~330 s for 589 tests.
"""
import os

# Guard Zero-Pollution : le defaut de Settings est sqlite:///./kamlog_erp.db,
# la VRAIE base de developpement. Sans ce setdefault, toute requise emise hors
# override get_db (ex. dependency_overrides.clear() en milieu de test) lit et
# ECrit dans ce fichier reel. On force une base memoire ephemeraite pour la
# session de test ; setdefault respecte une DATABASE_URL exportee explicitement
# (CI Postgres, debug local volontaire).
os.environ.setdefault("DATABASE_URL", "sqlite:///:memory:")
# Redis : "disabled" fait skipper la connexion completement (0 s vs 2-4 s de timeout
# TCP par test). L'event_service tourne en mode in-process uniquement.
os.environ.setdefault("REDIS_URL", "disabled")

import types

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from app.core.database import Base, get_db

SQLALCHEMY_DATABASE_URL = "sqlite:///:memory:"
engine = create_engine(
    SQLALCHEMY_DATABASE_URL,
    connect_args={"check_same_thread": False},
    # StaticPool : une seule connexion partagee entre tous les threads. Sans
    # cela, chaque thread (celui du TestClient/portal asynchrone) ouvrirait sa
    # propre base memoire :memory: vide -> "no such table" sur les endpoints
    # appeles apres le premier.
    poolclass=StaticPool,
)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Tables are created ONCE per pytest session (expensive with 318 tables);
# per-test isolation uses outer transaction + rollback.
_tables_created = False


def _ensure_tables():
    global _tables_created
    if _tables_created:
        return
    # Importer l'application complete enregistre TOUS les modeles SQLAlchemy
    # (les routers importent des modeles qui ne sont pas tous exposes via
    # app.models.__init__, ex. 'navires' via le module acconage). Sans cela,
    # Base.metadata.create_all() echoue sur des cles etrangeres non resolvees.
    import app.main  # noqa: F401
    Base.metadata.create_all(bind=engine)
    _tables_created = True


# ---------------------------------------------------------------------------
# Session-scoped fixtures: expensive setup done ONCE
# ---------------------------------------------------------------------------

@pytest.fixture(scope="session")
def _session_client():
    """TestClient whose lifespan runs exactly once per pytest session.

    This avoids re-triggering the ~0.5 s startup/shutdown for every test.
    Individual tests receive a per-test DB session via dependency_overrides.
    """
    _ensure_tables()
    from app.main import app
    # Ensure tables exist on the *app* engine too (lifespan calls create_all
    # but it's idempotent).
    with TestClient(app) as test_client:
        yield test_client


# ---------------------------------------------------------------------------
# Function-scoped fixtures: per-test isolation
# ---------------------------------------------------------------------------

@pytest.fixture(scope="function")
def db():
    """Per-test transaction isolation via outer-transaction rollback.

    Creates a connection, begins a transaction, and binds a session to it.
    All ORM operations within the test (and via the overridden get_db) run
    inside this transaction. On teardown, rollback reverts EVERYTHING —
    including committed data within savepoints — in ~0.8 ms vs 70 ms for
    DELETE-all-318-tables.
    """
    _ensure_tables()
    connection = engine.connect()
    transaction = connection.begin()
    session = TestingSessionLocal(bind=connection)
    try:
        yield session
    finally:
        session.close()
        transaction.rollback()
        connection.close()


@pytest.fixture(scope="function")
def client(db, _session_client):
    """Provide a FastAPI client bound to the test database with superuser auth.

    Reuses the session-scoped _session_client (lifespan already started) but
    swaps dependency_overrides to point get_db at the current test's isolated
    session.
    """
    from app.main import app
    from app.core.security import get_current_user

    # Fake superuser that bypasses all permission checks
    _fake_user = types.SimpleNamespace(
        id=1, email="admin@test.local", is_active=True,
        is_superuser=True, company_id=None, role_level=0,
    )

    def override_get_db():
        try:
            yield db
        finally:
            pass

    def override_get_current_user():
        return _fake_user

    app.dependency_overrides[get_db] = override_get_db
    app.dependency_overrides[get_current_user] = override_get_current_user
    yield _session_client
    # Restore overrides to a clean state for the next test (do NOT clear all —
    # see docstring contract; just remove ours).
    app.dependency_overrides.pop(get_db, None)
    app.dependency_overrides.pop(get_current_user, None)


@pytest.fixture(scope="function")
def unauthenticated(client, db):
    """Meme client que la fixture `client`, mais SANS identite surcharge :
    les routes Protegees repondent 401/403, ce qui permet d'auditer le vrai
    comportement anonyme.

    On ne fait PAS `dependency_overrides.clear()` : cela emporterait aussi
    l'override get_db et les requetes suivantes toucheraient l'engine reel.
    On ne retire que get_current_user, et on le remet ensuite.
    """
    from app.main import app
    from app.core.security import get_current_user

    saved = app.dependency_overrides.pop(get_current_user, None)
    try:
        yield client
    finally:
        if saved is not None:
            app.dependency_overrides[get_current_user] = saved


@pytest.fixture
def taux_cameroun():
    return {
        "tva": 0.1925,
        "cnps_salarial": 0.028,
        "cnps_patronal": 0.172,
        "cnps_plafond": 750_000,
        "tec_cat0": 0.00,
        "tec_cat1": 0.05,
        "tec_cat2": 0.10,
        "tec_cat3": 0.20,
        "redevance_informatique": 0.0035,
        "taxe_communautaire": 0.01,
    }
