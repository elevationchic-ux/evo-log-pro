"""Pytest configuration and fixtures for the EVO-LOG backend."""
import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
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


@pytest.fixture(scope="function")
def db():
    """Create a fresh in-memory database for each test."""
    # Importer l'application complete enregistre TOUS les modeles SQLAlchemy
    # (les routers importent des modeles qui ne sont pas tous exposes via
    # app.models.__init__, ex. 'navires' via le module acconage). Sans cela,
    # Base.metadata.create_all() echoue sur des cles etrangeres non resolvees.
    import app.main  # noqa: F401
    Base.metadata.create_all(bind=engine)
    session = TestingSessionLocal()
    try:
        yield session
    finally:
        session.close()
        Base.metadata.drop_all(bind=engine)


@pytest.fixture(scope="function")
def client(db):
    """Provide a FastAPI client bound to the test database."""
    from app.main import app

    def override_get_db():
        try:
            yield db
        finally:
            pass

    app.dependency_overrides[get_db] = override_get_db
    with TestClient(app) as test_client:
        yield test_client
    app.dependency_overrides.clear()


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
