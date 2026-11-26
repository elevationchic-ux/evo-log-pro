"""104 : tables expansion departement (genere)."""
from alembic import op
import sqlalchemy as sa


revision = "104_departement_d5_deep"
down_revision = "103_chat_d5_deep"
branch_labels = None
depends_on = None


TABLES = [
    "dep_objectives",
    "dep_service_meetings",
    "dep_projects",
    "dep_service_requests",
]


def _has(name):
    insp = sa.inspect(op.get_bind())
    return name in set(insp.get_table_names())


def upgrade():
    if not _has("dep_objectives"):
        op.create_table(
            "dep_objectives",
            sa.Column("id", sa.Integer, primary_key=True, index=True),
            sa.Column("company_id", sa.Integer, nullable=False, index=True),
            sa.Column("reference", sa.String(200), nullable=False, index=True),
            sa.Column("libelle", sa.String(200), nullable=True, index=True),
            sa.Column("indicateur", sa.String(200), nullable=True),
            sa.Column("cible", sa.Numeric, nullable=True),
            sa.Column("realise", sa.Numeric, nullable=True),
            sa.Column("trimestre", sa.String(200), nullable=True),
            sa.Column("statut", sa.String(200), nullable=True),
            sa.Column("is_active", sa.Boolean, nullable=True),
            sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
            sa.Column("updated_at", sa.DateTime(timezone=True), nullable=True),
            sa.UniqueConstraint("company_id", "reference", name="uix_dep_objectives_uniq"),
        )

    if not _has("dep_service_meetings"):
        op.create_table(
            "dep_service_meetings",
            sa.Column("id", sa.Integer, primary_key=True, index=True),
            sa.Column("company_id", sa.Integer, nullable=False, index=True),
            sa.Column("reference", sa.String(200), nullable=False, index=True),
            sa.Column("objet", sa.String(200), nullable=True, index=True),
            sa.Column("date", sa.DateTime(timezone=True), nullable=True),
            sa.Column("participants", sa.Integer, nullable=True),
            sa.Column("compte_rendu", sa.Text, nullable=True),
            sa.Column("statut", sa.String(200), nullable=True),
            sa.Column("is_active", sa.Boolean, nullable=True),
            sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
            sa.Column("updated_at", sa.DateTime(timezone=True), nullable=True),
            sa.UniqueConstraint("company_id", "reference", name="uix_dep_service_meetings_uniq"),
        )

    if not _has("dep_projects"):
        op.create_table(
            "dep_projects",
            sa.Column("id", sa.Integer, primary_key=True, index=True),
            sa.Column("company_id", sa.Integer, nullable=False, index=True),
            sa.Column("reference", sa.String(200), nullable=False, index=True),
            sa.Column("nom", sa.String(200), nullable=True, index=True),
            sa.Column("responsable", sa.String(200), nullable=True),
            sa.Column("budget", sa.Numeric, nullable=True),
            sa.Column("echeance", sa.Date, nullable=True),
            sa.Column("statut", sa.String(200), nullable=True),
            sa.Column("is_active", sa.Boolean, nullable=True),
            sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
            sa.Column("updated_at", sa.DateTime(timezone=True), nullable=True),
            sa.UniqueConstraint("company_id", "reference", name="uix_dep_projects_uniq"),
        )

    if not _has("dep_service_requests"):
        op.create_table(
            "dep_service_requests",
            sa.Column("id", sa.Integer, primary_key=True, index=True),
            sa.Column("company_id", sa.Integer, nullable=False, index=True),
            sa.Column("reference", sa.String(200), nullable=False, index=True),
            sa.Column("objet", sa.String(200), nullable=True, index=True),
            sa.Column("service_destinataire", sa.String(200), nullable=True),
            sa.Column("urgence", sa.String(200), nullable=True),
            sa.Column("date_demande", sa.Date, nullable=True),
            sa.Column("statut", sa.String(200), nullable=True),
            sa.Column("is_active", sa.Boolean, nullable=True),
            sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
            sa.Column("updated_at", sa.DateTime(timezone=True), nullable=True),
            sa.UniqueConstraint("company_id", "reference", name="uix_dep_service_requests_uniq"),
        )


def downgrade():
    for t in reversed(TABLES):
        if _has(t):
            op.drop_table(t)
