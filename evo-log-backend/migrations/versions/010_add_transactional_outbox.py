"""add transactional outbox

Revision ID: 010_add_transactional_outbox
Revises: 009_add_transport_avance_complete
"""

from alembic import op
import sqlalchemy as sa


revision = "010_add_transactional_outbox"
down_revision = "009_add_transport_avance_complete"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "outbox_events",
        sa.Column("id", sa.String(length=36), nullable=False),
        sa.Column("event_id", sa.String(length=36), nullable=False),
        sa.Column("company_id", sa.Integer(), nullable=False),
        sa.Column("event_type", sa.String(length=120), nullable=False),
        sa.Column("aggregate_type", sa.String(length=80), nullable=False),
        sa.Column("aggregate_id", sa.String(length=160), nullable=False),
        sa.Column("payload", sa.JSON(), nullable=False),
        sa.Column("occurred_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("dedupe_key", sa.String(length=200), nullable=True),
        sa.Column("status", sa.String(length=20), nullable=False),
        sa.Column("attempts", sa.Integer(), nullable=False),
        sa.Column("available_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("locked_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("processed_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("last_error", sa.Text(), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("event_id"),
        sa.UniqueConstraint(
            "company_id",
            "event_type",
            "aggregate_type",
            "aggregate_id",
            "dedupe_key",
            name="uq_outbox_event_dedupe",
        ),
    )
    op.create_index("ix_outbox_events_company_id", "outbox_events", ["company_id"])
    op.create_index(
        "ix_outbox_events_delivery",
        "outbox_events",
        ["status", "available_at", "created_at"],
    )


def downgrade() -> None:
    op.drop_index("ix_outbox_events_delivery", table_name="outbox_events")
    op.drop_index("ix_outbox_events_company_id", table_name="outbox_events")
    op.drop_table("outbox_events")
