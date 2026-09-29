"""Verifier que TOUTES les routes de magasin_stock.py exigent une authentification.

Avant la correction d24, les 13 routes etaient publiques (aucun Depends(get_current_user))
et le tenant_enforcement "fail OPEN" exposait les donnees de tous les tenants.

Ce test s'assure qu'aucune de ces routes n'est accessible sans JWT.
"""
from __future__ import annotations

import types

import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from app.core.database import Base, get_db


SQLALCHEMY_DATABASE_URL = "sqlite:///:memory:"
engine = create_engine(
    SQLALCHEMY_DATABASE_URL,
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


@pytest.fixture(scope="module")
def app_no_auth():
    """Application avec get_db override mais SANS override get_current_user.

    Cela simule un appel client sans JWT : la reponse doit etre 401 ou 403.
    """
    import app.main  # noqa: F401  register all models
    Base.metadata.create_all(bind=engine)

    from app.main import app as _app

    def override_get_db():
        db = TestingSessionLocal()
        try:
            yield db
        finally:
            db.close()

    # Override ONLY get_db, not get_current_user
    _app.dependency_overrides = {get_db: override_get_db}
    client = TestClient(_app, raise_server_exceptions=False)
    yield client
    _app.dependency_overrides.clear()
    Base.metadata.drop_all(bind=engine)


# Les 13 routes critiques de magasin_stock.py
UNAUTHENTICATED_ROUTES = [
    ("GET", "/api/v1/magasin/magasins"),
    ("POST", "/api/v1/magasin/magasins"),
    ("GET", "/api/v1/magasin/magasins/1"),
    ("PUT", "/api/v1/magasin/magasins/1"),
    ("DELETE", "/api/v1/magasin/magasins/1"),
    ("GET", "/api/v1/magasin/magasins/1/stocks"),
    ("GET", "/api/v1/magasin/stocks/search"),
    ("GET", "/api/v1/magasin/stock-statuses"),
    ("GET", "/api/v1/magasin/history"),
    ("GET", "/api/v1/magasin/transactions"),
    ("GET", "/api/v1/magasin/export/articles/csv"),
    ("POST", "/api/v1/magasin/import/articles"),
    ("GET", "/api/v1/magasin/import/articles/template"),
]


@pytest.mark.parametrize("method,path", UNAUTHENTICATED_ROUTES)
def test_route_rejete_sans_jwt(app_no_auth, method, path):
    """Aucune route magasin_stock ne doit repondre sans authentification."""
    kwargs = {}
    if method == "POST":
        kwargs["json"] = {}
    elif method == "PUT":
        kwargs["json"] = {}
    resp = app_no_auth.request(method, path, **kwargs)
    # FastAPI retourne 401 (pas de credentials) ou 403 (acces refuse) ou 422
    # (corps invalide) mais JAMAIS 200/201/204.
    assert resp.status_code in (401, 403, 422), (
        f"{method} {path} a repondu {resp.status_code} sans JWT  "
        "route non protegee !"
    )
