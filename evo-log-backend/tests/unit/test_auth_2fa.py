"""Tests pour l'authentification a deux facteurs (TOTP / RFC 6238).

Deux niveaux :
  1. Primitives pures (secret, verification, jeton 2FA, durcissement du type
     de token) sans base ni HTTP.
  2. Flux complet via l'API : login -> challenge 2FA -> verify, puis le cycle
     setup / enable / disable protege par mot de passe.

Aucune base de production : les tests d'API utilisent la fixture ``client``
/base memoire (cf. tests/conftest.py).
"""
import pyotp
import pytest
from fastapi import HTTPException
from fastapi.security import HTTPAuthorizationCredentials

from app.core.security import (
    generate_totp_secret,
    build_otpauth_uri,
    verify_totp,
    create_2fa_token,
    decode_2fa_token,
    create_access_token,
    create_refresh_token,
    get_token_payload,
    get_password_hash,
)
from datetime import timedelta
from app.models.user import User


# --------------------------------------------------------------------------- #
# 1) Primitives TOTP
# --------------------------------------------------------------------------- #
def test_generate_secret_is_valid_base32():
    secret = generate_totp_secret()
    # pyotp.accepte n'importe quelle cle base32 valide ; on verifie qu'un TOTP
    # construit dessus produit bien un code a 6 chiffres.
    code = pyotp.TOTP(secret).now()
    assert code.isdigit() and len(code) == 6


def test_verify_totp_accepts_current_code():
    secret = generate_totp_secret()
    assert verify_totp(secret, pyotp.TOTP(secret).now()) is True


def test_verify_totp_rejects_wrong_code():
    secret = generate_totp_secret()
    assert verify_totp(secret, "000000") is False or verify_totp(secret, "111111") is False


@pytest.mark.parametrize("secret,code", [("", "123456"), ("ABC", ""), (None, "123456"), ("ABC", None)])
def test_verify_totp_rejects_empty_inputs(secret, code):
    assert verify_totp(secret, code) is False


def test_build_otpauth_uri_shape():
    secret = generate_totp_secret()
    uri = build_otpauth_uri(secret, "alice", issuer="EVO-LOG")
    assert uri.startswith("otpauth://totp/")
    assert "secret=" in uri and "alice" in uri


# --------------------------------------------------------------------------- #
# Jeton 2FA + durcissement du type de token
# --------------------------------------------------------------------------- #
def test_2fa_token_roundtrip_returns_user_id():
    token = create_2fa_token(42)
    assert decode_2fa_token(token) == 42


def test_2fa_token_rejects_access_token():
    # Un token d'acces n'a pas type='2fa' -> refus.
    access = create_access_token(data={"sub": "7"}, expires_delta=timedelta(minutes=5))
    with pytest.raises(HTTPException):
        decode_2fa_token(access)


def test_get_token_payload_rejects_refresh_token():
    refresh = create_refresh_token(data={"sub": "7"})
    creds = HTTPAuthorizationCredentials(scheme="Bearer", credentials=refresh)
    with pytest.raises(HTTPException) as exc:
        get_token_payload(creds)
    assert exc.value.status_code == 401


def test_get_token_payload_rejects_2fa_token():
    token = create_2fa_token(7)
    creds = HTTPAuthorizationCredentials(scheme="Bearer", credentials=token)
    with pytest.raises(HTTPException) as exc:
        get_token_payload(creds)
    assert exc.value.status_code == 401


def test_get_token_payload_accepts_access_token():
    access = create_access_token(data={"sub": "7"}, expires_delta=timedelta(minutes=5))
    creds = HTTPAuthorizationCredentials(scheme="Bearer", credentials=access)
    payload = get_token_payload(creds)
    assert payload.get("sub") == "7"


# --------------------------------------------------------------------------- #
# 2) Flux API
# --------------------------------------------------------------------------- #
PASSWORD = "Passw0rd!Securisee"


def _make_user(db, *, username, email, two_factor_enabled=False, secret=None):
    user = User(
        username=username,
        email=email,
        hashed_password=get_password_hash(PASSWORD),
        is_active=True,
        two_factor_enabled=two_factor_enabled,
        two_factor_secret=secret,
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    return user


def test_login_without_2fa_returns_session(client, db):
    _make_user(db, username="bob", email="bob@example.com")
    resp = client.post("/api/v1/auth/login", json={"username": "bob", "password": PASSWORD})
    assert resp.status_code == 200
    body = resp.json()
    assert body.get("access_token")
    assert not body.get("two_factor_required")


def test_login_with_2fa_returns_challenge(client, db):
    secret = generate_totp_secret()
    _make_user(db, username="alice", email="alice@example.com",
               two_factor_enabled=True, secret=secret)
    resp = client.post("/api/v1/auth/login", json={"username": "alice", "password": PASSWORD})
    assert resp.status_code == 200
    body = resp.json()
    assert body.get("two_factor_required") is True
    assert body.get("two_factor_token")
    # Aucun token d'acces ne doit fuite avant la verification TOTP.
    assert "access_token" not in body


def test_login_2fa_wrong_password_rejected(client, db):
    secret = generate_totp_secret()
    _make_user(db, username="carol", email="carol@example.com",
               two_factor_enabled=True, secret=secret)
    resp = client.post("/api/v1/auth/login", json={"username": "carol", "password": "mauvais"})
    assert resp.status_code == 401


def test_verify_2fa_exchanges_for_session(client, db):
    secret = generate_totp_secret()
    _make_user(db, username="dave", email="dave@example.com",
               two_factor_enabled=True, secret=secret)
    login = client.post("/api/v1/auth/login", json={"username": "dave", "password": PASSWORD})
    token = login.json()["two_factor_token"]

    ok = client.post("/api/v1/auth/2fa/verify",
                     json={"two_factor_token": token, "code": pyotp.TOTP(secret).now()})
    assert ok.status_code == 200
    assert ok.json().get("access_token")
    assert ok.json().get("username") == "dave"


def test_verify_2fa_rejects_bad_code(client, db):
    secret = generate_totp_secret()
    _make_user(db, username="erin", email="erin@example.com",
               two_factor_enabled=True, secret=secret)
    login = client.post("/api/v1/auth/login", json={"username": "erin", "password": PASSWORD})
    token = login.json()["two_factor_token"]

    bad = client.post("/api/v1/auth/2fa/verify",
                      json={"two_factor_token": token, "code": "000000"})
    assert bad.status_code == 401


def _auth_headers(client, username):
    resp = client.post("/api/v1/auth/login", json={"username": username, "password": PASSWORD})
    return {"Authorization": f"Bearer {resp.json()['access_token']}"}


def test_setup_enable_disable_cycle(client, db):
    _make_user(db, username="frank", email="frank@example.com")
    headers = _auth_headers(client, "frank")

    # statut initial : 2FA off
    status = client.get("/api/v1/auth/2fa/status", headers=headers).json()
    assert status["two_factor_enabled"] is False

    # setup : genere un secret en attente, sans activer
    setup = client.post("/api/v1/auth/2fa/setup", headers=headers)
    assert setup.status_code == 200
    secret = setup.json()["secret"]
    assert setup.json()["otpauth_uri"].startswith("otpauth://")
    assert client.get("/api/v1/auth/2fa/status", headers=headers).json()["two_factor_enabled"] is False

    # enable avec un code invalide -> 400
    bad = client.post("/api/v1/auth/2fa/enable", headers=headers, json={"code": "000000"})
    assert bad.status_code == 400

    # enable avec le bon code -> active
    ok = client.post("/api/v1/auth/2fa/enable", headers=headers, json={"code": pyotp.TOTP(secret).now()})
    assert ok.status_code == 200
    assert client.get("/api/v1/auth/2fa/status", headers=headers).json()["two_factor_enabled"] is True

    # disable exige le mot de passe
    wrong = client.post("/api/v1/auth/2fa/disable", headers=headers, json={"password": "nope"})
    assert wrong.status_code == 400
    good = client.post("/api/v1/auth/2fa/disable", headers=headers, json={"password": PASSWORD})
    assert good.status_code == 200
    assert client.get("/api/v1/auth/2fa/status", headers=headers).json()["two_factor_enabled"] is False
