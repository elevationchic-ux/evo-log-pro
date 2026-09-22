from types import SimpleNamespace

import pytest
from fastapi import HTTPException

from app.core.config import Settings
from app.core.security import decode_token
from app.routers import collaboration
from app.services.sms_fallback import SMSFallbackService


def test_invalid_access_token_is_rejected():
    with pytest.raises(HTTPException) as error:
        decode_token("invalid-token")
    assert error.value.status_code == 401


def test_production_configuration_rejects_weak_secret():
    with pytest.raises(ValueError, match="SECRET_KEY"):
        Settings(
            ENVIRONMENT="production",
            SECRET_KEY="short",
            DATABASE_URL="postgresql://localhost/evo_log",
        )


def test_collaboration_room_is_company_and_membership_scoped():
    collaboration._rooms["p0-room"] = {
        "room_id": "p0-room",
        "company_id": 10,
        "participants": ["1"],
    }
    allowed = SimpleNamespace(id=1, company_id=10, is_superuser=False)
    foreign_company = SimpleNamespace(id=1, company_id=11, is_superuser=False)
    non_member = SimpleNamespace(id=2, company_id=10, is_superuser=False)

    assert collaboration._room_for_user("p0-room", allowed)["company_id"] == 10
    for user in (foreign_company, non_member):
        with pytest.raises(HTTPException) as error:
            collaboration._room_for_user("p0-room", user)
        assert error.value.status_code == 403


def test_sms_does_not_claim_delivery_without_provider():
    with pytest.raises(RuntimeError, match="unavailable"):
        SMSFallbackService().send_sms("+237600000000", "test")
