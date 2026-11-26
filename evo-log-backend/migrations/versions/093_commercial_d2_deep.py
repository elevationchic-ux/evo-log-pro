"""093 : tables expansion portail-commercial (genere)."""
from alembic import op
import sqlalchemy as sa


revision = "093_commercial_d2_deep"
down_revision = "092_commercial_d_deep"
branch_labels = None
depends_on = None


TABLES = [
    "comm_competitor_notes",
]


def _has(name):
    insp = sa.inspect(op.get_bind())
    return name in set(insp.get_table_names())


def upgrade():
    if not _has("comm_competitor_notes"):
        op.create_table(
            "comm_competitor_notes",
            sa.Column("id", sa.Integer, primary_key=True, index=True),
            sa.Column("company_id", sa.Integer, nullable=False, index=True),
            sa.Column("reference", sa.String(200), nullable=False, index=True),
            sa.Column("concurrent", sa.String(200), nullable=True),
            sa.Column("fait_observe", sa.Text, nullable=True),
            sa.Column("marche", sa.String(200), nullable=True),
            sa.Column("date", sa.Date, nullable=True),
            sa.Column("statut", sa.String(200), nullable=True),
            sa.Column("is_active", sa.Boolean, nullable=True),
            sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
            sa.Column("updated_at", sa.DateTime(timezone=True), nullable=True),
            sa.UniqueConstraint("company_id", "reference", name="uix_comm_competitor_notes_uniq"),
        )


def downgrade():
    for t in reversed(TABLES):
        if _has(t):
            op.drop_table(t)
