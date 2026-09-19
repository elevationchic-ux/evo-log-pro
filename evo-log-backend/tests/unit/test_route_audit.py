from fastapi import FastAPI

from app.core.route_audit import assert_no_duplicate_routes, duplicate_routes


def test_duplicate_routes_are_reported():
    app = FastAPI()

    @app.get("/same")
    def first():
        return {"ok": True}

    @app.get("/same")
    def second():
        return {"ok": True}

    duplicates = duplicate_routes(app)
    assert duplicates[("GET", "/same")] == ["first", "second"]


def test_unique_routes_pass():
    app = FastAPI()

    @app.get("/one")
    def one():
        return {"ok": True}

    assert_no_duplicate_routes(app)
