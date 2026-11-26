"""100 : tables expansion courier-express (genere)."""
from alembic import op
import sqlalchemy as sa


revision = "100_courier_e_deep"
down_revision = "099_pipeline_e_deep"
branch_labels = None
depends_on = None


TABLES = [
    "cour2_route_scans",
    "cour2_last_mile",
    "cour2_delivery_attempts",
    "cour2_exceptions",
    "cour2_returns",
    "cour2_shift_logs",
    "cour2_sla_breaches",
]


def _has(name):
    insp = sa.inspect(op.get_bind())
    return name in set(insp.get_table_names())


def upgrade():
    if not _has("cour2_route_scans"):
        op.create_table(
            "cour2_route_scans",
            sa.Column("id", sa.Integer, primary_key=True, index=True),
            sa.Column("company_id", sa.Integer, nullable=False, index=True),
            sa.Column("reference", sa.String(200), nullable=False, index=True),
            sa.Column("colis", sa.String(200), nullable=True),
            sa.Column("etape", sa.String(200), nullable=True),
            sa.Column("lieu", sa.String(200), nullable=True),
            sa.Column("date", sa.DateTime(timezone=True), nullable=True),
            sa.Column("statut", sa.String(200), nullable=True),
            sa.Column("is_active", sa.Boolean, nullable=True),
            sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
            sa.Column("updated_at", sa.DateTime(timezone=True), nullable=True),
            sa.UniqueConstraint("company_id", "reference", name="uix_cour2_route_scans_uniq"),
        )

    if not _has("cour2_last_mile"):
        op.create_table(
            "cour2_last_mile",
            sa.Column("id", sa.Integer, primary_key=True, index=True),
            sa.Column("company_id", sa.Integer, nullable=False, index=True),
            sa.Column("reference", sa.String(200), nullable=False, index=True),
            sa.Column("colis", sa.String(200), nullable=True),
            sa.Column("livreur", sa.String(200), nullable=True),
            sa.Column("agencer", sa.String(200), nullable=True),
            sa.Column("date", sa.DateTime(timezone=True), nullable=True),
            sa.Column("statut", sa.String(200), nullable=True),
            sa.Column("is_active", sa.Boolean, nullable=True),
            sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
            sa.Column("updated_at", sa.DateTime(timezone=True), nullable=True),
            sa.UniqueConstraint("company_id", "reference", name="uix_cour2_last_mile_uniq"),
        )

    if not _has("cour2_delivery_attempts"):
        op.create_table(
            "cour2_delivery_attempts",
            sa.Column("id", sa.Integer, primary_key=True, index=True),
            sa.Column("company_id", sa.Integer, nullable=False, index=True),
            sa.Column("reference", sa.String(200), nullable=False, index=True),
            sa.Column("colis", sa.String(200), nullable=True),
            sa.Column("livreur", sa.String(200), nullable=True),
            sa.Column("date", sa.DateTime(timezone=True), nullable=True),
            sa.Column("motif", sa.String(200), nullable=True),
            sa.Column("statut", sa.String(200), nullable=True),
            sa.Column("is_active", sa.Boolean, nullable=True),
            sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
            sa.Column("updated_at", sa.DateTime(timezone=True), nullable=True),
            sa.UniqueConstraint("company_id", "reference", name="uix_cour2_delivery_attempts_uniq"),
        )

    if not _has("cour2_exceptions"):
        op.create_table(
            "cour2_exceptions",
            sa.Column("id", sa.Integer, primary_key=True, index=True),
            sa.Column("company_id", sa.Integer, nullable=False, index=True),
            sa.Column("reference", sa.String(200), nullable=False, index=True),
            sa.Column("colis", sa.String(200), nullable=True),
            sa.Column("type_exception", sa.String(200), nullable=True),
            sa.Column("detecte_le", sa.DateTime(timezone=True), nullable=True),
            sa.Column("statut", sa.String(200), nullable=True),
            sa.Column("is_active", sa.Boolean, nullable=True),
            sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
            sa.Column("updated_at", sa.DateTime(timezone=True), nullable=True),
            sa.UniqueConstraint("company_id", "reference", name="uix_cour2_exceptions_uniq"),
        )

    if not _has("cour2_returns"):
        op.create_table(
            "cour2_returns",
            sa.Column("id", sa.Integer, primary_key=True, index=True),
            sa.Column("company_id", sa.Integer, nullable=False, index=True),
            sa.Column("reference", sa.String(200), nullable=False, index=True),
            sa.Column("colis", sa.String(200), nullable=True),
            sa.Column("motif", sa.String(200), nullable=True),
            sa.Column("date_depart", sa.DateTime(timezone=True), nullable=True),
            sa.Column("statut", sa.String(200), nullable=True),
            sa.Column("is_active", sa.Boolean, nullable=True),
            sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
            sa.Column("updated_at", sa.DateTime(timezone=True), nullable=True),
            sa.UniqueConstraint("company_id", "reference", name="uix_cour2_returns_uniq"),
        )

    if not _has("cour2_shift_logs"):
        op.create_table(
            "cour2_shift_logs",
            sa.Column("id", sa.Integer, primary_key=True, index=True),
            sa.Column("company_id", sa.Integer, nullable=False, index=True),
            sa.Column("reference", sa.String(200), nullable=False, index=True),
            sa.Column("livreur", sa.String(200), nullable=True),
            sa.Column("date", sa.Date, nullable=True),
            sa.Column("colis_livres", sa.Integer, nullable=True),
            sa.Column("km", sa.Integer, nullable=True),
            sa.Column("statut", sa.String(200), nullable=True),
            sa.Column("is_active", sa.Boolean, nullable=True),
            sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
            sa.Column("updated_at", sa.DateTime(timezone=True), nullable=True),
            sa.UniqueConstraint("company_id", "reference", name="uix_cour2_shift_logs_uniq"),
        )

    if not _has("cour2_sla_breaches"):
        op.create_table(
            "cour2_sla_breaches",
            sa.Column("id", sa.Integer, primary_key=True, index=True),
            sa.Column("company_id", sa.Integer, nullable=False, index=True),
            sa.Column("reference", sa.String(200), nullable=False, index=True),
            sa.Column("colis", sa.String(200), nullable=True),
            sa.Column("retard_min", sa.Integer, nullable=True),
            sa.Column("date", sa.DateTime(timezone=True), nullable=True),
            sa.Column("statut", sa.String(200), nullable=True),
            sa.Column("is_active", sa.Boolean, nullable=True),
            sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
            sa.Column("updated_at", sa.DateTime(timezone=True), nullable=True),
            sa.UniqueConstraint("company_id", "reference", name="uix_cour2_sla_breaches_uniq"),
        )


def downgrade():
    for t in reversed(TABLES):
        if _has(t):
            op.drop_table(t)
