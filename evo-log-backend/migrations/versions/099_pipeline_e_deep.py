"""099 : tables expansion pipeline-oleoduc (genere)."""
from alembic import op
import sqlalchemy as sa


revision = "099_pipeline_e_deep"
down_revision = "098_collaborateur_d_deep"
branch_labels = None
depends_on = None


TABLES = [
    "pipe2_custody_transfers",
    "pipe2_pressure_logs",
    "pipe2_pump_reads",
    "pipe2_corrosion",
    "pipe2_flow_calibrations",
    "pipe2_batch_quality",
    "pipe2_interface_detections",
    "pipe2_integrity",
    "pipe2_spill_actions",
]


def _has(name):
    insp = sa.inspect(op.get_bind())
    return name in set(insp.get_table_names())


def upgrade():
    if not _has("pipe2_custody_transfers"):
        op.create_table(
            "pipe2_custody_transfers",
            sa.Column("id", sa.Integer, primary_key=True, index=True),
            sa.Column("company_id", sa.Integer, nullable=False, index=True),
            sa.Column("reference", sa.String(200), nullable=False, index=True),
            sa.Column("interface", sa.String(200), nullable=True),
            sa.Column("produit", sa.String(200), nullable=True),
            sa.Column("volume_livre", sa.Numeric, nullable=True),
            sa.Column("volume_recu", sa.Numeric, nullable=True),
            sa.Column("statut", sa.String(200), nullable=True),
            sa.Column("is_active", sa.Boolean, nullable=True),
            sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
            sa.Column("updated_at", sa.DateTime(timezone=True), nullable=True),
            sa.UniqueConstraint("company_id", "reference", name="uix_pipe2_custody_transfers_uniq"),
        )

    if not _has("pipe2_pressure_logs"):
        op.create_table(
            "pipe2_pressure_logs",
            sa.Column("id", sa.Integer, primary_key=True, index=True),
            sa.Column("company_id", sa.Integer, nullable=False, index=True),
            sa.Column("reference", sa.String(200), nullable=False, index=True),
            sa.Column("station", sa.String(200), nullable=True),
            sa.Column("pression_bar", sa.Numeric, nullable=True),
            sa.Column("date", sa.DateTime(timezone=True), nullable=True),
            sa.Column("statut", sa.String(200), nullable=True),
            sa.Column("is_active", sa.Boolean, nullable=True),
            sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
            sa.Column("updated_at", sa.DateTime(timezone=True), nullable=True),
            sa.UniqueConstraint("company_id", "reference", name="uix_pipe2_pressure_logs_uniq"),
        )

    if not _has("pipe2_pump_reads"):
        op.create_table(
            "pipe2_pump_reads",
            sa.Column("id", sa.Integer, primary_key=True, index=True),
            sa.Column("company_id", sa.Integer, nullable=False, index=True),
            sa.Column("reference", sa.String(200), nullable=False, index=True),
            sa.Column("station", sa.String(200), nullable=True),
            sa.Column("debit", sa.Numeric, nullable=True),
            sa.Column("vibration", sa.Numeric, nullable=True),
            sa.Column("date", sa.DateTime(timezone=True), nullable=True),
            sa.Column("statut", sa.String(200), nullable=True),
            sa.Column("is_active", sa.Boolean, nullable=True),
            sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
            sa.Column("updated_at", sa.DateTime(timezone=True), nullable=True),
            sa.UniqueConstraint("company_id", "reference", name="uix_pipe2_pump_reads_uniq"),
        )

    if not _has("pipe2_corrosion"):
        op.create_table(
            "pipe2_corrosion",
            sa.Column("id", sa.Integer, primary_key=True, index=True),
            sa.Column("company_id", sa.Integer, nullable=False, index=True),
            sa.Column("reference", sa.String(200), nullable=False, index=True),
            sa.Column("troncon", sa.String(200), nullable=True),
            sa.Column("epaisseur_mm", sa.Numeric, nullable=True),
            sa.Column("date", sa.Date, nullable=True),
            sa.Column("statut", sa.String(200), nullable=True),
            sa.Column("is_active", sa.Boolean, nullable=True),
            sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
            sa.Column("updated_at", sa.DateTime(timezone=True), nullable=True),
            sa.UniqueConstraint("company_id", "reference", name="uix_pipe2_corrosion_uniq"),
        )

    if not _has("pipe2_flow_calibrations"):
        op.create_table(
            "pipe2_flow_calibrations",
            sa.Column("id", sa.Integer, primary_key=True, index=True),
            sa.Column("company_id", sa.Integer, nullable=False, index=True),
            sa.Column("reference", sa.String(200), nullable=False, index=True),
            sa.Column("debitmetre", sa.String(200), nullable=True),
            sa.Column("coefficient", sa.Numeric, nullable=True),
            sa.Column("date", sa.Date, nullable=True),
            sa.Column("statut", sa.String(200), nullable=True),
            sa.Column("is_active", sa.Boolean, nullable=True),
            sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
            sa.Column("updated_at", sa.DateTime(timezone=True), nullable=True),
            sa.UniqueConstraint("company_id", "reference", name="uix_pipe2_flow_calibrations_uniq"),
        )

    if not _has("pipe2_batch_quality"):
        op.create_table(
            "pipe2_batch_quality",
            sa.Column("id", sa.Integer, primary_key=True, index=True),
            sa.Column("company_id", sa.Integer, nullable=False, index=True),
            sa.Column("reference", sa.String(200), nullable=False, index=True),
            sa.Column("lot", sa.String(200), nullable=True),
            sa.Column("produit", sa.String(200), nullable=True),
            sa.Column("parametre", sa.String(200), nullable=True),
            sa.Column("date", sa.Date, nullable=True),
            sa.Column("statut", sa.String(200), nullable=True),
            sa.Column("is_active", sa.Boolean, nullable=True),
            sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
            sa.Column("updated_at", sa.DateTime(timezone=True), nullable=True),
            sa.UniqueConstraint("company_id", "reference", name="uix_pipe2_batch_quality_uniq"),
        )

    if not _has("pipe2_interface_detections"):
        op.create_table(
            "pipe2_interface_detections",
            sa.Column("id", sa.Integer, primary_key=True, index=True),
            sa.Column("company_id", sa.Integer, nullable=False, index=True),
            sa.Column("reference", sa.String(200), nullable=False, index=True),
            sa.Column("troncon", sa.String(200), nullable=True),
            sa.Column("volume_interface", sa.Numeric, nullable=True),
            sa.Column("date", sa.DateTime(timezone=True), nullable=True),
            sa.Column("statut", sa.String(200), nullable=True),
            sa.Column("is_active", sa.Boolean, nullable=True),
            sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
            sa.Column("updated_at", sa.DateTime(timezone=True), nullable=True),
            sa.UniqueConstraint("company_id", "reference", name="uix_pipe2_interface_detections_uniq"),
        )

    if not _has("pipe2_integrity"):
        op.create_table(
            "pipe2_integrity",
            sa.Column("id", sa.Integer, primary_key=True, index=True),
            sa.Column("company_id", sa.Integer, nullable=False, index=True),
            sa.Column("reference", sa.String(200), nullable=False, index=True),
            sa.Column("troncon", sa.String(200), nullable=True),
            sa.Column("niveau_risque", sa.String(200), nullable=True),
            sa.Column("pression_max", sa.Numeric, nullable=True),
            sa.Column("date", sa.Date, nullable=True),
            sa.Column("statut", sa.String(200), nullable=True),
            sa.Column("is_active", sa.Boolean, nullable=True),
            sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
            sa.Column("updated_at", sa.DateTime(timezone=True), nullable=True),
            sa.UniqueConstraint("company_id", "reference", name="uix_pipe2_integrity_uniq"),
        )

    if not _has("pipe2_spill_actions"):
        op.create_table(
            "pipe2_spill_actions",
            sa.Column("id", sa.Integer, primary_key=True, index=True),
            sa.Column("company_id", sa.Integer, nullable=False, index=True),
            sa.Column("reference", sa.String(200), nullable=False, index=True),
            sa.Column("lieu", sa.String(200), nullable=True),
            sa.Column("volume_rejete", sa.Numeric, nullable=True),
            sa.Column("volume_recupere", sa.Numeric, nullable=True),
            sa.Column("date", sa.DateTime(timezone=True), nullable=True),
            sa.Column("statut", sa.String(200), nullable=True),
            sa.Column("is_active", sa.Boolean, nullable=True),
            sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
            sa.Column("updated_at", sa.DateTime(timezone=True), nullable=True),
            sa.UniqueConstraint("company_id", "reference", name="uix_pipe2_spill_actions_uniq"),
        )


def downgrade():
    for t in reversed(TABLES):
        if _has(t):
            op.drop_table(t)
