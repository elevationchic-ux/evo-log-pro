"""Tests reproductibles pour les durcissements de securite (track C).

Couvre les primitives ajoutees lors du durcissement :
  - la politique de mot de passe ``validate_password_strength`` ;
  - le gating des endpoints d'initialisation ``_enforce_setup_access``
    (jeton X-Setup-Token + fail-closed en production).
"""
import pytest

from app.core.security import validate_password_strength


# --------------------------------------------------------------------------- #
# Politique de mot de passe
# --------------------------------------------------------------------------- #
def test_password_too_short_rejected():
    with pytest.raises(ValueError):
        validate_password_strength("Ab1")


def test_password_without_digit_rejected():
    with pytest.raises(ValueError):
        validate_password_strength("MotDePasseSansChiffre")


def test_password_without_letter_rejected():
    with pytest.raises(ValueError):
        validate_password_strength("1234567890")


def test_common_password_rejected():
    with pytest.raises(ValueError):
        validate_password_strength("admin123")


def test_password_equal_to_username_rejected():
    with pytest.raises(ValueError):
        validate_password_strength("jeanpierre", username="jeanpierre")


def test_strong_password_accepted():
    # Ne doit PAS lever.
    validate_password_strength("Corr3cte#2026", username="jean")


# --------------------------------------------------------------------------- #
# Gating /api/setup et /api/seed
# --------------------------------------------------------------------------- #
def _enforce(token):
    from app.main import _enforce_setup_access
    _enforce_setup_access(token)


def test_setup_access_ok_when_token_matches(monkeypatch):
    import app.main as m
    monkeypatch.setattr(m.settings, "SETUP_TOKEN", "s3cret-token")
    monkeypatch.setattr(m.settings, "ENVIRONMENT", "production")
    _enforce("s3cret-token")  # ne leve pas


def test_setup_access_rejects_wrong_token(monkeypatch):
    import app.main as m
    from fastapi import HTTPException
    monkeypatch.setattr(m.settings, "SETUP_TOKEN", "s3cret-token")
    monkeypatch.setattr(m.settings, "ENVIRONMENT", "production")
    with pytest.raises(HTTPException) as exc:
        _enforce("mauvais-token")
    assert exc.value.status_code == 403


def test_setup_access_rejects_missing_token(monkeypatch):
    import app.main as m
    from fastapi import HTTPException
    monkeypatch.setattr(m.settings, "SETUP_TOKEN", "s3cret-token")
    monkeypatch.setattr(m.settings, "ENVIRONMENT", "production")
    with pytest.raises(HTTPException) as exc:
        _enforce(None)
    assert exc.value.status_code == 403


def test_setup_access_fail_closed_in_production_without_token(monkeypatch):
    import app.main as m
    from fastapi import HTTPException
    monkeypatch.setattr(m.settings, "SETUP_TOKEN", "")
    monkeypatch.setattr(m.settings, "ENVIRONMENT", "production")
    with pytest.raises(HTTPException) as exc:
        _enforce(None)
    assert exc.value.status_code == 403


def test_setup_access_open_in_development_without_token(monkeypatch):
    import app.main as m
    monkeypatch.setattr(m.settings, "SETUP_TOKEN", "")
    monkeypatch.setattr(m.settings, "ENVIRONMENT", "development")
    _enforce(None)  # ne leve pas : convenance locale uniquement
