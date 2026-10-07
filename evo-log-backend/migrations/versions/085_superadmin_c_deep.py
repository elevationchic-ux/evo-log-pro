"""085 : tables expansion superadmin-cadc (genere)."""
from alembic import op
import sqlalchemy as sa


revision = "085_superadmin_c_deep"
down_revision = "084_admin_c_deep"
branch_labels = None
depends_on = None


TABLES = [
    "sac_audit_log_reviews",
    "sac_system_parameters",
    "sac_platform_alerts",
    "sac_migration_runs",
    "sac_license_keys",
]


def _has(name):
    insp = sa.inspect(op.get_bind())
    return name in set(insp.get_table_names())


def upgrade():
    if not _has("sac_audit_log_reviews"):
        op.create_table(
            "sac_audit_log_reviews",
            sa.Column("id", sa.Integer, primary_key=True, index=True),
            sa.Column("company_id", sa.Integer, nullable=False, index=True),
            sa.Column("reference", sa.String(200), nullable=False, index=True),
            sa.Column("perimetre", sa.String(200), nullable=True),
            sa.Column("date_debut", sa.DateTime(timezone=True), nullable=True),
            sa.Column("date_fin", sa.DateTime(timezone=True), nullable=True),
            sa.Column("evenements_examines", sa.Integer, nullable=True),
            sa.Column("reviewer", sa.String(200), nullable=True),
            sa.Column("verdict", sa.String(200), nullable=True),
            sa.Column("statut", sa.String(200), nullable=True),
            sa.Column("is_active", sa.Boolean, nullable=True),
            sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
            sa.Column("updated_at", sa.DateTime(timezone=True), nullable=True),
            sa.UniqueConstraint("company_id", "reference", name="uix_sac_audit_log_reviews_uniq"),
        )

    if not _has("sac_system_parameters"):
        op.create_table(
            "sac_system_parameters",
            sa.Column("id", sa.Integer, primary_key=True, index=True),
            sa.Column("company_id", sa.Integer, nullable=False, index=True),
            sa.Column("reference", sa.String(200), nullable=False, index=True),
            sa.Column("valeur", sa.Text, nullable=True),
            sa.Column("categorie", sa.String(200), nullable=True),
            sa.Column("portee", sa.String(200), nullable=True),
            sa.Column("modifie_par", sa.String(200), nullable=True),
            sa.Column("date_modification", sa.DateTime(timezone=True), nullable=True),
            sa.Column("statut", sa.String(200), nullable=True),
            sa.Column("is_active", sa.Boolean, nullable=True),
            sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
            sa.Column("updated_at", sa.DateTime(timezone=True), nullable=True),
            sa.UniqueConstraint("company_id", "reference", name="uix_sac_system_parameters_uniq"),
        )

    if not _has("sac_platform_alerts"):
        op.create_table(
            "sac_platform_alerts",
            sa.Column("id", sa.Integer, primary_key=True, index=True),
            sa.Column("company_id", sa.Integer, nullable=False, index=True),
            sa.Column("reference", sa.String(200), nullable=False, index=True),
            sa.Column("titre", sa.String(200), nullable=True),
            sa.Column("source", sa.String(200), nullable=True),
            sa.Column("severite", sa.String(200), nullable=True),
            sa.Column("date_detection", sa.DateTime(timezone=True), nullable=True),
            sa.Column("acquitte_par", sa.String(200), nullable=True),
            sa.Column("statut", sa.String(200), nullable=True),
            sa.Column("is_active", sa.Boolean, nullable=True),
            sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
            sa.Column("updated_at", sa.DateTime(timezone=True), nullable=True),
            sa.UniqueConstraint("company_id", "reference", name="uix_sac_platform_alerts_uniq"),
        )

    if not _has("sac_migration_runs"):
        op.create_table(
            "sac_migration_runs",
            sa.Column("id", sa.Integer, primary_key=True, index=True),
            sa.Column("company_id", sa.Integer, nullable=False, index=True),
            sa.Column("reference", sa.String(200), nullable=False, index=True),
            sa.Column("revision", sa.String(200), nullable=True),
            sa.Column("environnement", sa.String(200), nullable=True),
            sa.Column("lance_par", sa.String(200), nullable=True),
            sa.Column("date_debut", sa.DateTime(timezone=True), nullable=True),
            sa.Column("duree_sec", sa.Integer, nullable=True),
            sa.Column("statut", sa.String(200), nullable=True),
            sa.Column("is_active", sa.Boolean, nullable=True),
            sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
            sa.Column("updated_at", sa.DateTime(timezone=True), nullable=True),
            sa.UniqueConstraint("company_id", "reference", name="uix_sac_migration_runs_uniq"),
        )

    if not _has("sac_license_keys"):
        op.create_table(
            "sac_license_keys",
            sa.Column("id", sa.Integer, primary_key=True, index=True),
            sa.Column("company_id", sa.Integer, nullable=False, index=True),
            sa.Column("reference", sa.String(200), nullable=False, index=True),
            sa.Column("produit", sa.String(200), nullable=True),
            sa.Column("titulaire", sa.String(200), nullable=True),
            sa.Column("sieges_licencies", sa.Integer, nullable=True),
            sa.Column("date_activation", sa.Date, nullable=True),
            sa.Column("date_expiration", sa.Date, nullable=True),
            sa.Column("statut", sa.String(200), nullable=True),
            sa.Column("is_active", sa.Boolean, nullable=True),
            sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
            sa.Column("updated_at", sa.DateTime(timezone=True), nullable=True),
            sa.UniqueConstraint("company_id", "reference", name="uix_sac_license_keys_uniq"),
        )


def downgrade():
    for t in reversed(TABLES):
        if _has(t):
            op.drop_table(t)
