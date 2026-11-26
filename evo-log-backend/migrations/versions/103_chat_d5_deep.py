"""103 : tables expansion chat (genere)."""
from alembic import op
import sqlalchemy as sa


revision = "103_chat_d5_deep"
down_revision = "102_heavylift_e_deep"
branch_labels = None
depends_on = None


TABLES = [
    "cht_announcements",
    "cht_channels",
    "cht_content_reports",
]


def _has(name):
    insp = sa.inspect(op.get_bind())
    return name in set(insp.get_table_names())


def upgrade():
    if not _has("cht_announcements"):
        op.create_table(
            "cht_announcements",
            sa.Column("id", sa.Integer, primary_key=True, index=True),
            sa.Column("company_id", sa.Integer, nullable=False, index=True),
            sa.Column("reference", sa.String(200), nullable=False, index=True),
            sa.Column("titre", sa.String(200), nullable=True, index=True),
            sa.Column("contenu", sa.Text, nullable=True),
            sa.Column("cible", sa.String(200), nullable=True),
            sa.Column("auteur", sa.String(200), nullable=True),
            sa.Column("epingle", sa.Boolean, nullable=True),
            sa.Column("date_publication", sa.DateTime(timezone=True), nullable=True),
            sa.Column("statut", sa.String(200), nullable=True),
            sa.Column("is_active", sa.Boolean, nullable=True),
            sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
            sa.Column("updated_at", sa.DateTime(timezone=True), nullable=True),
            sa.UniqueConstraint("company_id", "reference", name="uix_cht_announcements_uniq"),
        )

    if not _has("cht_channels"):
        op.create_table(
            "cht_channels",
            sa.Column("id", sa.Integer, primary_key=True, index=True),
            sa.Column("company_id", sa.Integer, nullable=False, index=True),
            sa.Column("reference", sa.String(200), nullable=False, index=True),
            sa.Column("nom", sa.String(200), nullable=True, index=True),
            sa.Column("thematique", sa.String(200), nullable=True),
            sa.Column("description", sa.Text, nullable=True),
            sa.Column("createur", sa.String(200), nullable=True),
            sa.Column("membres", sa.Integer, nullable=True),
            sa.Column("statut", sa.String(200), nullable=True),
            sa.Column("is_active", sa.Boolean, nullable=True),
            sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
            sa.Column("updated_at", sa.DateTime(timezone=True), nullable=True),
            sa.UniqueConstraint("company_id", "reference", name="uix_cht_channels_uniq"),
        )

    if not _has("cht_content_reports"):
        op.create_table(
            "cht_content_reports",
            sa.Column("id", sa.Integer, primary_key=True, index=True),
            sa.Column("company_id", sa.Integer, nullable=False, index=True),
            sa.Column("reference", sa.String(200), nullable=False, index=True),
            sa.Column("signalant", sa.String(200), nullable=True),
            sa.Column("contenu_signale", sa.Text, nullable=True),
            sa.Column("motif", sa.String(200), nullable=True),
            sa.Column("severite", sa.String(200), nullable=True),
            sa.Column("date_signalement", sa.DateTime(timezone=True), nullable=True),
            sa.Column("statut", sa.String(200), nullable=True),
            sa.Column("is_active", sa.Boolean, nullable=True),
            sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
            sa.Column("updated_at", sa.DateTime(timezone=True), nullable=True),
            sa.UniqueConstraint("company_id", "reference", name="uix_cht_content_reports_uniq"),
        )


def downgrade():
    for t in reversed(TABLES):
        if _has(t):
            op.drop_table(t)
