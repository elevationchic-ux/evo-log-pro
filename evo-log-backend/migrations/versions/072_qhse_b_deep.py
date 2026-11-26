"""072 : tables expansion qhse-securite (genere)."""
from alembic import op
import sqlalchemy as sa


revision = "072_qhse_b_deep"
down_revision = "071_parc_b_deep"
branch_labels = None
depends_on = None


TABLES = [
    "qhseb_near_misses",
    "qhseb_calibrations",
    "qhseb_waste_manifests",
    "qhseb_training_records",
    "qhseb_work_permits",
]


def _has(name):
    insp = sa.inspect(op.get_bind())
    return name in set(insp.get_table_names())


def upgrade():
    if not _has("qhseb_near_misses"):
        op.create_table(
            "qhseb_near_misses",
            sa.Column("id", sa.Integer, primary_key=True, index=True),
            sa.Column("company_id", sa.Integer, nullable=False, index=True),
            sa.Column("reference", sa.String(200), nullable=False, index=True),
            sa.Column("site", sa.String(200), nullable=True),
            sa.Column("date_evenement", sa.DateTime(timezone=True), nullable=True),
            sa.Column("zone", sa.String(200), nullable=True),
            sa.Column("description", sa.Text, nullable=True),
            sa.Column("gravite_potentielle", sa.String(200), nullable=True),
            sa.Column("statut", sa.String(200), nullable=True),
            sa.Column("is_active", sa.Boolean, nullable=True),
            sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
            sa.Column("updated_at", sa.DateTime(timezone=True), nullable=True),
            sa.UniqueConstraint("company_id", "reference", name="uix_qhseb_near_misses_uniq"),
        )

    if not _has("qhseb_calibrations"):
        op.create_table(
            "qhseb_calibrations",
            sa.Column("id", sa.Integer, primary_key=True, index=True),
            sa.Column("company_id", sa.Integer, nullable=False, index=True),
            sa.Column("numero_instrument", sa.String(200), nullable=False, index=True),
            sa.Column("designation", sa.String(200), nullable=True),
            sa.Column("service", sa.String(200), nullable=True),
            sa.Column("date_etallonage", sa.Date, nullable=True),
            sa.Column("date_prochaine", sa.Date, nullable=True),
            sa.Column("ecart_constate", sa.Numeric, nullable=True),
            sa.Column("statut", sa.String(200), nullable=True),
            sa.Column("is_active", sa.Boolean, nullable=True),
            sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
            sa.Column("updated_at", sa.DateTime(timezone=True), nullable=True),
            sa.UniqueConstraint("company_id", "numero_instrument", name="uix_qhseb_calibrations_uniq"),
        )

    if not _has("qhseb_waste_manifests"):
        op.create_table(
            "qhseb_waste_manifests",
            sa.Column("id", sa.Integer, primary_key=True, index=True),
            sa.Column("company_id", sa.Integer, nullable=False, index=True),
            sa.Column("numero_bsd", sa.String(200), nullable=False, index=True),
            sa.Column("site", sa.String(200), nullable=True),
            sa.Column("type_dechet", sa.String(200), nullable=True),
            sa.Column("dangerosite", sa.String(200), nullable=True),
            sa.Column("quantite_tonnes", sa.Numeric, nullable=True),
            sa.Column("destination", sa.String(200), nullable=True),
            sa.Column("date_enlevement", sa.Date, nullable=True),
            sa.Column("statut", sa.String(200), nullable=True),
            sa.Column("is_active", sa.Boolean, nullable=True),
            sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
            sa.Column("updated_at", sa.DateTime(timezone=True), nullable=True),
            sa.UniqueConstraint("company_id", "numero_bsd", name="uix_qhseb_waste_manifests_uniq"),
        )

    if not _has("qhseb_training_records"):
        op.create_table(
            "qhseb_training_records",
            sa.Column("id", sa.Integer, primary_key=True, index=True),
            sa.Column("company_id", sa.Integer, nullable=False, index=True),
            sa.Column("reference", sa.String(200), nullable=False, index=True),
            sa.Column("collaborateur", sa.String(200), nullable=True),
            sa.Column("type_habilitation", sa.String(200), nullable=True),
            sa.Column("date_formation", sa.Date, nullable=True),
            sa.Column("date_validite", sa.Date, nullable=True),
            sa.Column("formateur", sa.String(200), nullable=True),
            sa.Column("statut", sa.String(200), nullable=True),
            sa.Column("is_active", sa.Boolean, nullable=True),
            sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
            sa.Column("updated_at", sa.DateTime(timezone=True), nullable=True),
            sa.UniqueConstraint("company_id", "reference", name="uix_qhseb_training_records_uniq"),
        )

    if not _has("qhseb_work_permits"):
        op.create_table(
            "qhseb_work_permits",
            sa.Column("id", sa.Integer, primary_key=True, index=True),
            sa.Column("company_id", sa.Integer, nullable=False, index=True),
            sa.Column("numero_ptw", sa.String(200), nullable=False, index=True),
            sa.Column("site", sa.String(200), nullable=True),
            sa.Column("type_travaux", sa.String(200), nullable=True),
            sa.Column("zone_travail", sa.String(200), nullable=True),
            sa.Column("demandeur", sa.String(200), nullable=True),
            sa.Column("date_debut", sa.DateTime(timezone=True), nullable=True),
            sa.Column("date_fin", sa.DateTime(timezone=True), nullable=True),
            sa.Column("statut", sa.String(200), nullable=True),
            sa.Column("is_active", sa.Boolean, nullable=True),
            sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
            sa.Column("updated_at", sa.DateTime(timezone=True), nullable=True),
            sa.UniqueConstraint("company_id", "numero_ptw", name="uix_qhseb_work_permits_uniq"),
        )


def downgrade():
    for t in reversed(TABLES):
        if _has(t):
            op.drop_table(t)
