"""Regression tests for authentication and tenant-bound authorization."""
import pytest

from app.models.user import Role, User
from app.core.config import Settings
from app.schemas.user import UserCreate
from app.services.role_service import RoleService
from app.services.sms_fallback import SMSFallbackService
from app.core.tenant_access import scope_query
from app.models.chat import EnterpriseChatMessage
from app.models.outbox import OutboxEvent
from app.services.outbox_service import enqueue_event


def test_public_user_schema_does_not_accept_privilege_field():
    user = UserCreate(
        username="new-user",
        email="new-user@example.com",
        password="safe-password",
        is_superuser=True,
    )

    assert not hasattr(user, "is_superuser")


def test_tenant_admin_cannot_update_role_from_another_company(db):
    actor = User(
        username="tenant-admin",
        email="admin@example.com",
        hashed_password="hash",
        company_id=1,
        role_level=1,
        is_active=True,
    )
    foreign_role = Role(
        name="FOREIGN_ROLE",
        description="Foreign tenant role",
        level=3,
        company_id=2,
        modules_allowed="[]",
        is_active=True,
        is_system=False,
    )
    db.add_all([actor, foreign_role])
    db.commit()
    db.refresh(foreign_role)

    with pytest.raises(PermissionError):
        RoleService.mettre_a_jour_modules_role(
            db, foreign_role.id, ["finance"], actor=actor
        )


def test_tenant_admin_cannot_assign_role_to_foreign_user(db):
    actor = User(
        username="tenant-admin",
        email="admin2@example.com",
        hashed_password="hash",
        company_id=1,
        role_level=1,
        is_active=True,
    )
    foreign_user = User(
        username="foreign-user",
        email="foreign@example.com",
        hashed_password="hash",
        company_id=2,
        role_level=3,
        is_active=True,
    )
    role = Role(
        name="LOCAL_ROLE",
        description="Local role",
        level=3,
        company_id=1,
        modules_allowed="[]",
        is_active=True,
        is_system=False,
    )
    db.add_all([actor, foreign_user, role])
    db.commit()
    db.refresh(foreign_user)
    db.refresh(role)

    with pytest.raises(PermissionError):
        RoleService.assigner_role_user(db, foreign_user.id, role.id, actor=actor)


def test_production_requires_explicit_strong_secret():
    with pytest.raises(ValueError, match="SECRET_KEY"):
        Settings(
            ENVIRONMENT="production",
            DATABASE_URL="postgresql://localhost/evo_log",
            SECRET_KEY="",
        )


def test_sms_fallback_never_reports_fake_delivery():
    with pytest.raises(RuntimeError, match="SMS delivery is unavailable"):
        SMSFallbackService().send_sms("+237600000000", "test")


def test_scope_query_applies_company_and_department(db):
    actor = User(
        username="scoped-user",
        email="scoped@example.com",
        hashed_password="hash",
        company_id=7,
        department_id=9,
        is_active=True,
    )
    db.add(actor)
    db.commit()

    query = scope_query(
        db.query(EnterpriseChatMessage), EnterpriseChatMessage, actor
    )
    sql = str(query.statement.compile(compile_kwargs={"literal_binds": True}))

    assert "enterprise_chat_messages.company_id = 7" in sql


def test_outbox_event_is_persisted_as_pending(db):
    event = enqueue_event(
        db,
        event_type="notification.sms",
        aggregate_type="user",
        aggregate_id="42",
        payload={"recipient": "+237600000000"},
    )
    db.commit()

    stored = db.query(OutboxEvent).filter(OutboxEvent.id == event.id).one()
    assert stored.status == "pending"
    assert stored.payload == '{"recipient":"+237600000000"}'
