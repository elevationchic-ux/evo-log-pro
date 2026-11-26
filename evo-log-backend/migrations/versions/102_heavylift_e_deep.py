"""102 : tables expansion convoi-exceptionnel (genere)."""
from alembic import op
import sqlalchemy as sa


revision = "102_heavylift_e_deep"
down_revision = "101_coldchain_e_deep"
branch_labels = None
depends_on = None


TABLES = [
    "heavy2_lift_plans",
    "heavy2_route_surveys",
    "heavy2_escorts",
    "heavy2_load_moment",
    "heavy2_crane_setup",
    "heavy2_permits",
    "heavy2_lashing",
    "heavy2_axle_loads",
    "heavy2_staging",
]


def _has(name):
    insp = sa.inspect(op.get_bind())
    return name in set(insp.get_table_names())


def upgrade():
    if not _has("heavy2_lift_plans"):
        op.create_table(
            "heavy2_lift_plans",
            sa.Column("id", sa.Integer, primary_key=True, index=True),
            sa.Column("company_id", sa.Integer, nullable=False, index=True),
            sa.Column("reference", sa.String(200), nullable=False, index=True),
            sa.Column("charge", sa.String(200), nullable=True),
            sa.Column("poids_tonnes", sa.Numeric, nullable=True),
            sa.Column("portee_m", sa.Numeric, nullable=True),
            sa.Column("date", sa.Date, nullable=True),
            sa.Column("statut", sa.String(200), nullable=True),
            sa.Column("is_active", sa.Boolean, nullable=True),
            sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
            sa.Column("updated_at", sa.DateTime(timezone=True), nullable=True),
            sa.UniqueConstraint("company_id", "reference", name="uix_heavy2_lift_plans_uniq"),
        )

    if not _has("heavy2_route_surveys"):
        op.create_table(
            "heavy2_route_surveys",
            sa.Column("id", sa.Integer, primary_key=True, index=True),
            sa.Column("company_id", sa.Integer, nullable=False, index=True),
            sa.Column("reference", sa.String(200), nullable=False, index=True),
            sa.Column("itineraire", sa.String(200), nullable=True),
            sa.Column("largeur_m", sa.Numeric, nullable=True),
            sa.Column("hauteur_m", sa.Numeric, nullable=True),
            sa.Column("statut", sa.String(200), nullable=True),
            sa.Column("is_active", sa.Boolean, nullable=True),
            sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
            sa.Column("updated_at", sa.DateTime(timezone=True), nullable=True),
            sa.UniqueConstraint("company_id", "reference", name="uix_heavy2_route_surveys_uniq"),
        )

    if not _has("heavy2_escorts"):
        op.create_table(
            "heavy2_escorts",
            sa.Column("id", sa.Integer, primary_key=True, index=True),
            sa.Column("company_id", sa.Integer, nullable=False, index=True),
            sa.Column("reference", sa.String(200), nullable=False, index=True),
            sa.Column("convoi", sa.String(200), nullable=True),
            sa.Column("nb_vehicules", sa.Integer, nullable=True),
            sa.Column("debut", sa.DateTime(timezone=True), nullable=True),
            sa.Column("statut", sa.String(200), nullable=True),
            sa.Column("is_active", sa.Boolean, nullable=True),
            sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
            sa.Column("updated_at", sa.DateTime(timezone=True), nullable=True),
            sa.UniqueConstraint("company_id", "reference", name="uix_heavy2_escorts_uniq"),
        )

    if not _has("heavy2_load_moment"):
        op.create_table(
            "heavy2_load_moment",
            sa.Column("id", sa.Integer, primary_key=True, index=True),
            sa.Column("company_id", sa.Integer, nullable=False, index=True),
            sa.Column("reference", sa.String(200), nullable=False, index=True),
            sa.Column("configuration", sa.String(200), nullable=True),
            sa.Column("moment_applique", sa.Numeric, nullable=True),
            sa.Column("capacite", sa.Numeric, nullable=True),
            sa.Column("statut", sa.String(200), nullable=True),
            sa.Column("is_active", sa.Boolean, nullable=True),
            sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
            sa.Column("updated_at", sa.DateTime(timezone=True), nullable=True),
            sa.UniqueConstraint("company_id", "reference", name="uix_heavy2_load_moment_uniq"),
        )

    if not _has("heavy2_crane_setup"):
        op.create_table(
            "heavy2_crane_setup",
            sa.Column("id", sa.Integer, primary_key=True, index=True),
            sa.Column("company_id", sa.Integer, nullable=False, index=True),
            sa.Column("reference", sa.String(200), nullable=False, index=True),
            sa.Column("grue", sa.String(200), nullable=True),
            sa.Column("portance_sol", sa.String(200), nullable=True),
            sa.Column("date", sa.DateTime(timezone=True), nullable=True),
            sa.Column("statut", sa.String(200), nullable=True),
            sa.Column("is_active", sa.Boolean, nullable=True),
            sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
            sa.Column("updated_at", sa.DateTime(timezone=True), nullable=True),
            sa.UniqueConstraint("company_id", "reference", name="uix_heavy2_crane_setup_uniq"),
        )

    if not _has("heavy2_permits"):
        op.create_table(
            "heavy2_permits",
            sa.Column("id", sa.Integer, primary_key=True, index=True),
            sa.Column("company_id", sa.Integer, nullable=False, index=True),
            sa.Column("reference", sa.String(200), nullable=False, index=True),
            sa.Column("convoi", sa.String(200), nullable=True),
            sa.Column("autorite", sa.String(200), nullable=True),
            sa.Column("validite", sa.Date, nullable=True),
            sa.Column("statut", sa.String(200), nullable=True),
            sa.Column("is_active", sa.Boolean, nullable=True),
            sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
            sa.Column("updated_at", sa.DateTime(timezone=True), nullable=True),
            sa.UniqueConstraint("company_id", "reference", name="uix_heavy2_permits_uniq"),
        )

    if not _has("heavy2_lashing"):
        op.create_table(
            "heavy2_lashing",
            sa.Column("id", sa.Integer, primary_key=True, index=True),
            sa.Column("company_id", sa.Integer, nullable=False, index=True),
            sa.Column("reference", sa.String(200), nullable=False, index=True),
            sa.Column("charge", sa.String(200), nullable=True),
            sa.Column("nb_sangles", sa.Integer, nullable=True),
            sa.Column("angle_deg", sa.Integer, nullable=True),
            sa.Column("statut", sa.String(200), nullable=True),
            sa.Column("is_active", sa.Boolean, nullable=True),
            sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
            sa.Column("updated_at", sa.DateTime(timezone=True), nullable=True),
            sa.UniqueConstraint("company_id", "reference", name="uix_heavy2_lashing_uniq"),
        )

    if not _has("heavy2_axle_loads"):
        op.create_table(
            "heavy2_axle_loads",
            sa.Column("id", sa.Integer, primary_key=True, index=True),
            sa.Column("company_id", sa.Integer, nullable=False, index=True),
            sa.Column("reference", sa.String(200), nullable=False, index=True),
            sa.Column("vehicule", sa.String(200), nullable=True),
            sa.Column("essieu", sa.Integer, nullable=True),
            sa.Column("charge_t", sa.Numeric, nullable=True),
            sa.Column("statut", sa.String(200), nullable=True),
            sa.Column("is_active", sa.Boolean, nullable=True),
            sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
            sa.Column("updated_at", sa.DateTime(timezone=True), nullable=True),
            sa.UniqueConstraint("company_id", "reference", name="uix_heavy2_axle_loads_uniq"),
        )

    if not _has("heavy2_staging"):
        op.create_table(
            "heavy2_staging",
            sa.Column("id", sa.Integer, primary_key=True, index=True),
            sa.Column("company_id", sa.Integer, nullable=False, index=True),
            sa.Column("reference", sa.String(200), nullable=False, index=True),
            sa.Column("convoi", sa.String(200), nullable=True),
            sa.Column("lieu_rassemblement", sa.String(200), nullable=True),
            sa.Column("depart", sa.DateTime(timezone=True), nullable=True),
            sa.Column("statut", sa.String(200), nullable=True),
            sa.Column("is_active", sa.Boolean, nullable=True),
            sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
            sa.Column("updated_at", sa.DateTime(timezone=True), nullable=True),
            sa.UniqueConstraint("company_id", "reference", name="uix_heavy2_staging_uniq"),
        )


def downgrade():
    for t in reversed(TABLES):
        if _has(t):
            op.drop_table(t)
