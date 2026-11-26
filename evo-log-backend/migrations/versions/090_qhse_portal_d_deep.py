"""090 : tables expansion portail-qhse (genere)."""
from alembic import op
import sqlalchemy as sa


revision = "090_qhse_portal_d_deep"
down_revision = "089_technicien_d_deep"
branch_labels = None
depends_on = None


TABLES = [
    "qsp_hazard_reports",
    "qsp_near_misses",
    "qsp_safety_observations",
    "qsp_ppe_attestations",
    "qsp_toolbox_talks",
    "qsp_work_permits",
    "qsp_safety_training_logs",
    "qsp_exposure_records",
    "qsp_first_aid_log",
    "qsp_safety_suggestions",
    "qsp_stop_work",
    "qsp_spill_reports",
    "qsp_msds_acks",
    "qsp_ergonomics",
    "qsp_hygiene_checks",
    "qsp_inspection_findings",
    "qsp_capa_replies",
    "qsp_risk_inputs",
    "qsp_evacuation_drills",
]


def _has(name):
    insp = sa.inspect(op.get_bind())
    return name in set(insp.get_table_names())


def upgrade():
    if not _has("qsp_hazard_reports"):
        op.create_table(
            "qsp_hazard_reports",
            sa.Column("id", sa.Integer, primary_key=True, index=True),
            sa.Column("company_id", sa.Integer, nullable=False, index=True),
            sa.Column("reference", sa.String(200), nullable=False, index=True),
            sa.Column("lieu", sa.String(200), nullable=True),
            sa.Column("description", sa.Text, nullable=True),
            sa.Column("gravite", sa.String(200), nullable=True),
            sa.Column("signale_le", sa.DateTime(timezone=True), nullable=True),
            sa.Column("statut", sa.String(200), nullable=True),
            sa.Column("is_active", sa.Boolean, nullable=True),
            sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
            sa.Column("updated_at", sa.DateTime(timezone=True), nullable=True),
            sa.UniqueConstraint("company_id", "reference", name="uix_qsp_hazard_reports_uniq"),
        )

    if not _has("qsp_near_misses"):
        op.create_table(
            "qsp_near_misses",
            sa.Column("id", sa.Integer, primary_key=True, index=True),
            sa.Column("company_id", sa.Integer, nullable=False, index=True),
            sa.Column("reference", sa.String(200), nullable=False, index=True),
            sa.Column("lieu", sa.String(200), nullable=True),
            sa.Column("situation", sa.Text, nullable=True),
            sa.Column("date", sa.DateTime(timezone=True), nullable=True),
            sa.Column("témoin", sa.String(200), nullable=True),
            sa.Column("statut", sa.String(200), nullable=True),
            sa.Column("is_active", sa.Boolean, nullable=True),
            sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
            sa.Column("updated_at", sa.DateTime(timezone=True), nullable=True),
            sa.UniqueConstraint("company_id", "reference", name="uix_qsp_near_misses_uniq"),
        )

    if not _has("qsp_safety_observations"):
        op.create_table(
            "qsp_safety_observations",
            sa.Column("id", sa.Integer, primary_key=True, index=True),
            sa.Column("company_id", sa.Integer, nullable=False, index=True),
            sa.Column("reference", sa.String(200), nullable=False, index=True),
            sa.Column("zone", sa.String(200), nullable=True),
            sa.Column("observation", sa.Text, nullable=True),
            sa.Column("nature", sa.String(200), nullable=True),
            sa.Column("date", sa.DateTime(timezone=True), nullable=True),
            sa.Column("statut", sa.String(200), nullable=True),
            sa.Column("is_active", sa.Boolean, nullable=True),
            sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
            sa.Column("updated_at", sa.DateTime(timezone=True), nullable=True),
            sa.UniqueConstraint("company_id", "reference", name="uix_qsp_safety_observations_uniq"),
        )

    if not _has("qsp_ppe_attestations"):
        op.create_table(
            "qsp_ppe_attestations",
            sa.Column("id", sa.Integer, primary_key=True, index=True),
            sa.Column("company_id", sa.Integer, nullable=False, index=True),
            sa.Column("reference", sa.String(200), nullable=False, index=True),
            sa.Column("operateur", sa.String(200), nullable=True),
            sa.Column("epi_controles", sa.Integer, nullable=True),
            sa.Column("conforme", sa.Boolean, nullable=True),
            sa.Column("date", sa.DateTime(timezone=True), nullable=True),
            sa.Column("statut", sa.String(200), nullable=True),
            sa.Column("is_active", sa.Boolean, nullable=True),
            sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
            sa.Column("updated_at", sa.DateTime(timezone=True), nullable=True),
            sa.UniqueConstraint("company_id", "reference", name="uix_qsp_ppe_attestations_uniq"),
        )

    if not _has("qsp_toolbox_talks"):
        op.create_table(
            "qsp_toolbox_talks",
            sa.Column("id", sa.Integer, primary_key=True, index=True),
            sa.Column("company_id", sa.Integer, nullable=False, index=True),
            sa.Column("reference", sa.String(200), nullable=False, index=True),
            sa.Column("sujet", sa.String(200), nullable=True),
            sa.Column("anime_par", sa.String(200), nullable=True),
            sa.Column("nb_participants", sa.Integer, nullable=True),
            sa.Column("date", sa.Date, nullable=True),
            sa.Column("statut", sa.String(200), nullable=True),
            sa.Column("is_active", sa.Boolean, nullable=True),
            sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
            sa.Column("updated_at", sa.DateTime(timezone=True), nullable=True),
            sa.UniqueConstraint("company_id", "reference", name="uix_qsp_toolbox_talks_uniq"),
        )

    if not _has("qsp_work_permits"):
        op.create_table(
            "qsp_work_permits",
            sa.Column("id", sa.Integer, primary_key=True, index=True),
            sa.Column("company_id", sa.Integer, nullable=False, index=True),
            sa.Column("reference", sa.String(200), nullable=False, index=True),
            sa.Column("type", sa.String(200), nullable=True),
            sa.Column("lieu", sa.String(200), nullable=True),
            sa.Column("demandeur", sa.String(200), nullable=True),
            sa.Column("debut", sa.DateTime(timezone=True), nullable=True),
            sa.Column("statut", sa.String(200), nullable=True),
            sa.Column("is_active", sa.Boolean, nullable=True),
            sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
            sa.Column("updated_at", sa.DateTime(timezone=True), nullable=True),
            sa.UniqueConstraint("company_id", "reference", name="uix_qsp_work_permits_uniq"),
        )

    if not _has("qsp_safety_training_logs"):
        op.create_table(
            "qsp_safety_training_logs",
            sa.Column("id", sa.Integer, primary_key=True, index=True),
            sa.Column("company_id", sa.Integer, nullable=False, index=True),
            sa.Column("reference", sa.String(200), nullable=False, index=True),
            sa.Column("operateur", sa.String(200), nullable=True),
            sa.Column("formation", sa.String(200), nullable=True),
            sa.Column("date", sa.Date, nullable=True),
            sa.Column("validite", sa.Date, nullable=True),
            sa.Column("statut", sa.String(200), nullable=True),
            sa.Column("is_active", sa.Boolean, nullable=True),
            sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
            sa.Column("updated_at", sa.DateTime(timezone=True), nullable=True),
            sa.UniqueConstraint("company_id", "reference", name="uix_qsp_safety_training_logs_uniq"),
        )

    if not _has("qsp_exposure_records"):
        op.create_table(
            "qsp_exposure_records",
            sa.Column("id", sa.Integer, primary_key=True, index=True),
            sa.Column("company_id", sa.Integer, nullable=False, index=True),
            sa.Column("reference", sa.String(200), nullable=False, index=True),
            sa.Column("operateur", sa.String(200), nullable=True),
            sa.Column("agent", sa.String(200), nullable=True),
            sa.Column("valeur", sa.Numeric, nullable=True),
            sa.Column("date", sa.Date, nullable=True),
            sa.Column("statut", sa.String(200), nullable=True),
            sa.Column("is_active", sa.Boolean, nullable=True),
            sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
            sa.Column("updated_at", sa.DateTime(timezone=True), nullable=True),
            sa.UniqueConstraint("company_id", "reference", name="uix_qsp_exposure_records_uniq"),
        )

    if not _has("qsp_first_aid_log"):
        op.create_table(
            "qsp_first_aid_log",
            sa.Column("id", sa.Integer, primary_key=True, index=True),
            sa.Column("company_id", sa.Integer, nullable=False, index=True),
            sa.Column("reference", sa.String(200), nullable=False, index=True),
            sa.Column("personne", sa.String(200), nullable=True),
            sa.Column("nature_blessure", sa.String(200), nullable=True),
            sa.Column("date", sa.DateTime(timezone=True), nullable=True),
            sa.Column("secouriste", sa.String(200), nullable=True),
            sa.Column("statut", sa.String(200), nullable=True),
            sa.Column("is_active", sa.Boolean, nullable=True),
            sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
            sa.Column("updated_at", sa.DateTime(timezone=True), nullable=True),
            sa.UniqueConstraint("company_id", "reference", name="uix_qsp_first_aid_log_uniq"),
        )

    if not _has("qsp_safety_suggestions"):
        op.create_table(
            "qsp_safety_suggestions",
            sa.Column("id", sa.Integer, primary_key=True, index=True),
            sa.Column("company_id", sa.Integer, nullable=False, index=True),
            sa.Column("reference", sa.String(200), nullable=False, index=True),
            sa.Column("auteur", sa.String(200), nullable=True),
            sa.Column("idee", sa.Text, nullable=True),
            sa.Column("date", sa.Date, nullable=True),
            sa.Column("statut", sa.String(200), nullable=True),
            sa.Column("is_active", sa.Boolean, nullable=True),
            sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
            sa.Column("updated_at", sa.DateTime(timezone=True), nullable=True),
            sa.UniqueConstraint("company_id", "reference", name="uix_qsp_safety_suggestions_uniq"),
        )

    if not _has("qsp_stop_work"):
        op.create_table(
            "qsp_stop_work",
            sa.Column("id", sa.Integer, primary_key=True, index=True),
            sa.Column("company_id", sa.Integer, nullable=False, index=True),
            sa.Column("reference", sa.String(200), nullable=False, index=True),
            sa.Column("motif", sa.Text, nullable=True),
            sa.Column("declenche_le", sa.DateTime(timezone=True), nullable=True),
            sa.Column("reprise_le", sa.DateTime(timezone=True), nullable=True),
            sa.Column("statut", sa.String(200), nullable=True),
            sa.Column("is_active", sa.Boolean, nullable=True),
            sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
            sa.Column("updated_at", sa.DateTime(timezone=True), nullable=True),
            sa.UniqueConstraint("company_id", "reference", name="uix_qsp_stop_work_uniq"),
        )

    if not _has("qsp_spill_reports"):
        op.create_table(
            "qsp_spill_reports",
            sa.Column("id", sa.Integer, primary_key=True, index=True),
            sa.Column("company_id", sa.Integer, nullable=False, index=True),
            sa.Column("reference", sa.String(200), nullable=False, index=True),
            sa.Column("produit", sa.String(200), nullable=True),
            sa.Column("volume", sa.Numeric, nullable=True),
            sa.Column("lieu", sa.String(200), nullable=True),
            sa.Column("date", sa.DateTime(timezone=True), nullable=True),
            sa.Column("statut", sa.String(200), nullable=True),
            sa.Column("is_active", sa.Boolean, nullable=True),
            sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
            sa.Column("updated_at", sa.DateTime(timezone=True), nullable=True),
            sa.UniqueConstraint("company_id", "reference", name="uix_qsp_spill_reports_uniq"),
        )

    if not _has("qsp_msds_acks"):
        op.create_table(
            "qsp_msds_acks",
            sa.Column("id", sa.Integer, primary_key=True, index=True),
            sa.Column("company_id", sa.Integer, nullable=False, index=True),
            sa.Column("reference", sa.String(200), nullable=False, index=True),
            sa.Column("produit", sa.String(200), nullable=True),
            sa.Column("operateur", sa.String(200), nullable=True),
            sa.Column("date", sa.Date, nullable=True),
            sa.Column("version_fds", sa.String(200), nullable=True),
            sa.Column("statut", sa.String(200), nullable=True),
            sa.Column("is_active", sa.Boolean, nullable=True),
            sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
            sa.Column("updated_at", sa.DateTime(timezone=True), nullable=True),
            sa.UniqueConstraint("company_id", "reference", name="uix_qsp_msds_acks_uniq"),
        )

    if not _has("qsp_ergonomics"):
        op.create_table(
            "qsp_ergonomics",
            sa.Column("id", sa.Integer, primary_key=True, index=True),
            sa.Column("company_id", sa.Integer, nullable=False, index=True),
            sa.Column("reference", sa.String(200), nullable=False, index=True),
            sa.Column("poste", sa.String(200), nullable=True),
            sa.Column("contrainte", sa.String(200), nullable=True),
            sa.Column("score", sa.Integer, nullable=True),
            sa.Column("date", sa.Date, nullable=True),
            sa.Column("statut", sa.String(200), nullable=True),
            sa.Column("is_active", sa.Boolean, nullable=True),
            sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
            sa.Column("updated_at", sa.DateTime(timezone=True), nullable=True),
            sa.UniqueConstraint("company_id", "reference", name="uix_qsp_ergonomics_uniq"),
        )

    if not _has("qsp_hygiene_checks"):
        op.create_table(
            "qsp_hygiene_checks",
            sa.Column("id", sa.Integer, primary_key=True, index=True),
            sa.Column("company_id", sa.Integer, nullable=False, index=True),
            sa.Column("reference", sa.String(200), nullable=False, index=True),
            sa.Column("local", sa.String(200), nullable=True),
            sa.Column("point_controle", sa.String(200), nullable=True),
            sa.Column("date", sa.DateTime(timezone=True), nullable=True),
            sa.Column("statut", sa.String(200), nullable=True),
            sa.Column("is_active", sa.Boolean, nullable=True),
            sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
            sa.Column("updated_at", sa.DateTime(timezone=True), nullable=True),
            sa.UniqueConstraint("company_id", "reference", name="uix_qsp_hygiene_checks_uniq"),
        )

    if not _has("qsp_inspection_findings"):
        op.create_table(
            "qsp_inspection_findings",
            sa.Column("id", sa.Integer, primary_key=True, index=True),
            sa.Column("company_id", sa.Integer, nullable=False, index=True),
            sa.Column("reference", sa.String(200), nullable=False, index=True),
            sa.Column("inspection", sa.String(200), nullable=True),
            sa.Column("constat", sa.Text, nullable=True),
            sa.Column("criticite", sa.String(200), nullable=True),
            sa.Column("date", sa.Date, nullable=True),
            sa.Column("statut", sa.String(200), nullable=True),
            sa.Column("is_active", sa.Boolean, nullable=True),
            sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
            sa.Column("updated_at", sa.DateTime(timezone=True), nullable=True),
            sa.UniqueConstraint("company_id", "reference", name="uix_qsp_inspection_findings_uniq"),
        )

    if not _has("qsp_capa_replies"):
        op.create_table(
            "qsp_capa_replies",
            sa.Column("id", sa.Integer, primary_key=True, index=True),
            sa.Column("company_id", sa.Integer, nullable=False, index=True),
            sa.Column("reference", sa.String(200), nullable=False, index=True),
            sa.Column("action_corrective", sa.String(200), nullable=True),
            sa.Column("reponse", sa.Text, nullable=True),
            sa.Column("operateur", sa.String(200), nullable=True),
            sa.Column("date", sa.DateTime(timezone=True), nullable=True),
            sa.Column("statut", sa.String(200), nullable=True),
            sa.Column("is_active", sa.Boolean, nullable=True),
            sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
            sa.Column("updated_at", sa.DateTime(timezone=True), nullable=True),
            sa.UniqueConstraint("company_id", "reference", name="uix_qsp_capa_replies_uniq"),
        )

    if not _has("qsp_risk_inputs"):
        op.create_table(
            "qsp_risk_inputs",
            sa.Column("id", sa.Integer, primary_key=True, index=True),
            sa.Column("company_id", sa.Integer, nullable=False, index=True),
            sa.Column("reference", sa.String(200), nullable=False, index=True),
            sa.Column("activite", sa.String(200), nullable=True),
            sa.Column("risque_identifie", sa.Text, nullable=True),
            sa.Column("cotation", sa.Integer, nullable=True),
            sa.Column("date", sa.Date, nullable=True),
            sa.Column("statut", sa.String(200), nullable=True),
            sa.Column("is_active", sa.Boolean, nullable=True),
            sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
            sa.Column("updated_at", sa.DateTime(timezone=True), nullable=True),
            sa.UniqueConstraint("company_id", "reference", name="uix_qsp_risk_inputs_uniq"),
        )

    if not _has("qsp_evacuation_drills"):
        op.create_table(
            "qsp_evacuation_drills",
            sa.Column("id", sa.Integer, primary_key=True, index=True),
            sa.Column("company_id", sa.Integer, nullable=False, index=True),
            sa.Column("reference", sa.String(200), nullable=False, index=True),
            sa.Column("site", sa.String(200), nullable=True),
            sa.Column("date", sa.DateTime(timezone=True), nullable=True),
            sa.Column("duree_sec", sa.Integer, nullable=True),
            sa.Column("nb_evacues", sa.Integer, nullable=True),
            sa.Column("statut", sa.String(200), nullable=True),
            sa.Column("is_active", sa.Boolean, nullable=True),
            sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
            sa.Column("updated_at", sa.DateTime(timezone=True), nullable=True),
            sa.UniqueConstraint("company_id", "reference", name="uix_qsp_evacuation_drills_uniq"),
        )


def downgrade():
    for t in reversed(TABLES):
        if _has(t):
            op.drop_table(t)
