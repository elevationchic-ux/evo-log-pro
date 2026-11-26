"""098 : tables expansion portail-collaborateur (genere)."""
from alembic import op
import sqlalchemy as sa


revision = "098_collaborateur_d_deep"
down_revision = "097_annuaire_d_deep"
branch_labels = None
depends_on = None


TABLES = [
    "coll_assignments",
    "coll_activity_logs",
    "coll_deliverables",
    "coll_timesheets",
    "coll_site_access",
    "coll_instruction_receipts",
    "coll_incidents",
    "coll_quality_checks",
    "coll_training_completions",
    "coll_equipment_issues",
    "coll_shift_attendance",
    "coll_travel_orders",
    "coll_expense_declarations",
    "coll_cert_uploads",
    "coll_task_completions",
    "coll_feedback",
    "coll_availability",
    "coll_contract_renewals",
    "coll_document_requests",
]


def _has(name):
    insp = sa.inspect(op.get_bind())
    return name in set(insp.get_table_names())


def upgrade():
    if not _has("coll_assignments"):
        op.create_table(
            "coll_assignments",
            sa.Column("id", sa.Integer, primary_key=True, index=True),
            sa.Column("company_id", sa.Integer, nullable=False, index=True),
            sa.Column("reference", sa.String(200), nullable=False, index=True),
            sa.Column("collaborateur", sa.String(200), nullable=True),
            sa.Column("mission", sa.String(200), nullable=True),
            sa.Column("site", sa.String(200), nullable=True),
            sa.Column("debut", sa.Date, nullable=True),
            sa.Column("statut", sa.String(200), nullable=True),
            sa.Column("is_active", sa.Boolean, nullable=True),
            sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
            sa.Column("updated_at", sa.DateTime(timezone=True), nullable=True),
            sa.UniqueConstraint("company_id", "reference", name="uix_coll_assignments_uniq"),
        )

    if not _has("coll_activity_logs"):
        op.create_table(
            "coll_activity_logs",
            sa.Column("id", sa.Integer, primary_key=True, index=True),
            sa.Column("company_id", sa.Integer, nullable=False, index=True),
            sa.Column("reference", sa.String(200), nullable=False, index=True),
            sa.Column("collaborateur", sa.String(200), nullable=True),
            sa.Column("date", sa.Date, nullable=True),
            sa.Column("heures", sa.Numeric, nullable=True),
            sa.Column("activite", sa.Text, nullable=True),
            sa.Column("statut", sa.String(200), nullable=True),
            sa.Column("is_active", sa.Boolean, nullable=True),
            sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
            sa.Column("updated_at", sa.DateTime(timezone=True), nullable=True),
            sa.UniqueConstraint("company_id", "reference", name="uix_coll_activity_logs_uniq"),
        )

    if not _has("coll_deliverables"):
        op.create_table(
            "coll_deliverables",
            sa.Column("id", sa.Integer, primary_key=True, index=True),
            sa.Column("company_id", sa.Integer, nullable=False, index=True),
            sa.Column("reference", sa.String(200), nullable=False, index=True),
            sa.Column("collaborateur", sa.String(200), nullable=True),
            sa.Column("livrable", sa.String(200), nullable=True),
            sa.Column("mission", sa.String(200), nullable=True),
            sa.Column("date", sa.DateTime(timezone=True), nullable=True),
            sa.Column("statut", sa.String(200), nullable=True),
            sa.Column("is_active", sa.Boolean, nullable=True),
            sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
            sa.Column("updated_at", sa.DateTime(timezone=True), nullable=True),
            sa.UniqueConstraint("company_id", "reference", name="uix_coll_deliverables_uniq"),
        )

    if not _has("coll_timesheets"):
        op.create_table(
            "coll_timesheets",
            sa.Column("id", sa.Integer, primary_key=True, index=True),
            sa.Column("company_id", sa.Integer, nullable=False, index=True),
            sa.Column("reference", sa.String(200), nullable=False, index=True),
            sa.Column("collaborateur", sa.String(200), nullable=True),
            sa.Column("mission", sa.String(200), nullable=True),
            sa.Column("heures", sa.Numeric, nullable=True),
            sa.Column("semaine", sa.String(200), nullable=True),
            sa.Column("statut", sa.String(200), nullable=True),
            sa.Column("is_active", sa.Boolean, nullable=True),
            sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
            sa.Column("updated_at", sa.DateTime(timezone=True), nullable=True),
            sa.UniqueConstraint("company_id", "reference", name="uix_coll_timesheets_uniq"),
        )

    if not _has("coll_site_access"):
        op.create_table(
            "coll_site_access",
            sa.Column("id", sa.Integer, primary_key=True, index=True),
            sa.Column("company_id", sa.Integer, nullable=False, index=True),
            sa.Column("reference", sa.String(200), nullable=False, index=True),
            sa.Column("collaborateur", sa.String(200), nullable=True),
            sa.Column("site", sa.String(200), nullable=True),
            sa.Column("entree", sa.DateTime(timezone=True), nullable=True),
            sa.Column("sortie", sa.DateTime(timezone=True), nullable=True),
            sa.Column("statut", sa.String(200), nullable=True),
            sa.Column("is_active", sa.Boolean, nullable=True),
            sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
            sa.Column("updated_at", sa.DateTime(timezone=True), nullable=True),
            sa.UniqueConstraint("company_id", "reference", name="uix_coll_site_access_uniq"),
        )

    if not _has("coll_instruction_receipts"):
        op.create_table(
            "coll_instruction_receipts",
            sa.Column("id", sa.Integer, primary_key=True, index=True),
            sa.Column("company_id", sa.Integer, nullable=False, index=True),
            sa.Column("reference", sa.String(200), nullable=False, index=True),
            sa.Column("collaborateur", sa.String(200), nullable=True),
            sa.Column("consigne", sa.String(200), nullable=True),
            sa.Column("date", sa.DateTime(timezone=True), nullable=True),
            sa.Column("statut", sa.String(200), nullable=True),
            sa.Column("is_active", sa.Boolean, nullable=True),
            sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
            sa.Column("updated_at", sa.DateTime(timezone=True), nullable=True),
            sa.UniqueConstraint("company_id", "reference", name="uix_coll_instruction_receipts_uniq"),
        )

    if not _has("coll_incidents"):
        op.create_table(
            "coll_incidents",
            sa.Column("id", sa.Integer, primary_key=True, index=True),
            sa.Column("company_id", sa.Integer, nullable=False, index=True),
            sa.Column("reference", sa.String(200), nullable=False, index=True),
            sa.Column("collaborateur", sa.String(200), nullable=True),
            sa.Column("lieu", sa.String(200), nullable=True),
            sa.Column("description", sa.Text, nullable=True),
            sa.Column("gravite", sa.String(200), nullable=True),
            sa.Column("statut", sa.String(200), nullable=True),
            sa.Column("is_active", sa.Boolean, nullable=True),
            sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
            sa.Column("updated_at", sa.DateTime(timezone=True), nullable=True),
            sa.UniqueConstraint("company_id", "reference", name="uix_coll_incidents_uniq"),
        )

    if not _has("coll_quality_checks"):
        op.create_table(
            "coll_quality_checks",
            sa.Column("id", sa.Integer, primary_key=True, index=True),
            sa.Column("company_id", sa.Integer, nullable=False, index=True),
            sa.Column("reference", sa.String(200), nullable=False, index=True),
            sa.Column("collaborateur", sa.String(200), nullable=True),
            sa.Column("controle", sa.String(200), nullable=True),
            sa.Column("point_testes", sa.Integer, nullable=True),
            sa.Column("anomalies", sa.Integer, nullable=True),
            sa.Column("statut", sa.String(200), nullable=True),
            sa.Column("is_active", sa.Boolean, nullable=True),
            sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
            sa.Column("updated_at", sa.DateTime(timezone=True), nullable=True),
            sa.UniqueConstraint("company_id", "reference", name="uix_coll_quality_checks_uniq"),
        )

    if not _has("coll_training_completions"):
        op.create_table(
            "coll_training_completions",
            sa.Column("id", sa.Integer, primary_key=True, index=True),
            sa.Column("company_id", sa.Integer, nullable=False, index=True),
            sa.Column("reference", sa.String(200), nullable=False, index=True),
            sa.Column("collaborateur", sa.String(200), nullable=True),
            sa.Column("formation", sa.String(200), nullable=True),
            sa.Column("date", sa.Date, nullable=True),
            sa.Column("score", sa.Integer, nullable=True),
            sa.Column("statut", sa.String(200), nullable=True),
            sa.Column("is_active", sa.Boolean, nullable=True),
            sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
            sa.Column("updated_at", sa.DateTime(timezone=True), nullable=True),
            sa.UniqueConstraint("company_id", "reference", name="uix_coll_training_completions_uniq"),
        )

    if not _has("coll_equipment_issues"):
        op.create_table(
            "coll_equipment_issues",
            sa.Column("id", sa.Integer, primary_key=True, index=True),
            sa.Column("company_id", sa.Integer, nullable=False, index=True),
            sa.Column("reference", sa.String(200), nullable=False, index=True),
            sa.Column("collaborateur", sa.String(200), nullable=True),
            sa.Column("equipement", sa.String(200), nullable=True),
            sa.Column("probleme", sa.Text, nullable=True),
            sa.Column("date", sa.DateTime(timezone=True), nullable=True),
            sa.Column("statut", sa.String(200), nullable=True),
            sa.Column("is_active", sa.Boolean, nullable=True),
            sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
            sa.Column("updated_at", sa.DateTime(timezone=True), nullable=True),
            sa.UniqueConstraint("company_id", "reference", name="uix_coll_equipment_issues_uniq"),
        )

    if not _has("coll_shift_attendance"):
        op.create_table(
            "coll_shift_attendance",
            sa.Column("id", sa.Integer, primary_key=True, index=True),
            sa.Column("company_id", sa.Integer, nullable=False, index=True),
            sa.Column("reference", sa.String(200), nullable=False, index=True),
            sa.Column("collaborateur", sa.String(200), nullable=True),
            sa.Column("poste", sa.String(200), nullable=True),
            sa.Column("date", sa.Date, nullable=True),
            sa.Column("arrivee", sa.DateTime(timezone=True), nullable=True),
            sa.Column("statut", sa.String(200), nullable=True),
            sa.Column("is_active", sa.Boolean, nullable=True),
            sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
            sa.Column("updated_at", sa.DateTime(timezone=True), nullable=True),
            sa.UniqueConstraint("company_id", "reference", name="uix_coll_shift_attendance_uniq"),
        )

    if not _has("coll_travel_orders"):
        op.create_table(
            "coll_travel_orders",
            sa.Column("id", sa.Integer, primary_key=True, index=True),
            sa.Column("company_id", sa.Integer, nullable=False, index=True),
            sa.Column("reference", sa.String(200), nullable=False, index=True),
            sa.Column("collaborateur", sa.String(200), nullable=True),
            sa.Column("destination", sa.String(200), nullable=True),
            sa.Column("debut", sa.Date, nullable=True),
            sa.Column("fin", sa.Date, nullable=True),
            sa.Column("statut", sa.String(200), nullable=True),
            sa.Column("is_active", sa.Boolean, nullable=True),
            sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
            sa.Column("updated_at", sa.DateTime(timezone=True), nullable=True),
            sa.UniqueConstraint("company_id", "reference", name="uix_coll_travel_orders_uniq"),
        )

    if not _has("coll_expense_declarations"):
        op.create_table(
            "coll_expense_declarations",
            sa.Column("id", sa.Integer, primary_key=True, index=True),
            sa.Column("company_id", sa.Integer, nullable=False, index=True),
            sa.Column("reference", sa.String(200), nullable=False, index=True),
            sa.Column("collaborateur", sa.String(200), nullable=True),
            sa.Column("mission", sa.String(200), nullable=True),
            sa.Column("montant", sa.Numeric, nullable=True),
            sa.Column("date", sa.Date, nullable=True),
            sa.Column("statut", sa.String(200), nullable=True),
            sa.Column("is_active", sa.Boolean, nullable=True),
            sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
            sa.Column("updated_at", sa.DateTime(timezone=True), nullable=True),
            sa.UniqueConstraint("company_id", "reference", name="uix_coll_expense_declarations_uniq"),
        )

    if not _has("coll_cert_uploads"):
        op.create_table(
            "coll_cert_uploads",
            sa.Column("id", sa.Integer, primary_key=True, index=True),
            sa.Column("company_id", sa.Integer, nullable=False, index=True),
            sa.Column("reference", sa.String(200), nullable=False, index=True),
            sa.Column("collaborateur", sa.String(200), nullable=True),
            sa.Column("certification", sa.String(200), nullable=True),
            sa.Column("expire_le", sa.Date, nullable=True),
            sa.Column("statut", sa.String(200), nullable=True),
            sa.Column("is_active", sa.Boolean, nullable=True),
            sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
            sa.Column("updated_at", sa.DateTime(timezone=True), nullable=True),
            sa.UniqueConstraint("company_id", "reference", name="uix_coll_cert_uploads_uniq"),
        )

    if not _has("coll_task_completions"):
        op.create_table(
            "coll_task_completions",
            sa.Column("id", sa.Integer, primary_key=True, index=True),
            sa.Column("company_id", sa.Integer, nullable=False, index=True),
            sa.Column("reference", sa.String(200), nullable=False, index=True),
            sa.Column("collaborateur", sa.String(200), nullable=True),
            sa.Column("tache", sa.String(200), nullable=True),
            sa.Column("acheve_le", sa.DateTime(timezone=True), nullable=True),
            sa.Column("statut", sa.String(200), nullable=True),
            sa.Column("is_active", sa.Boolean, nullable=True),
            sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
            sa.Column("updated_at", sa.DateTime(timezone=True), nullable=True),
            sa.UniqueConstraint("company_id", "reference", name="uix_coll_task_completions_uniq"),
        )

    if not _has("coll_feedback"):
        op.create_table(
            "coll_feedback",
            sa.Column("id", sa.Integer, primary_key=True, index=True),
            sa.Column("company_id", sa.Integer, nullable=False, index=True),
            sa.Column("reference", sa.String(200), nullable=False, index=True),
            sa.Column("collaborateur", sa.String(200), nullable=True),
            sa.Column("sujet", sa.String(200), nullable=True),
            sa.Column("contenu", sa.Text, nullable=True),
            sa.Column("date", sa.Date, nullable=True),
            sa.Column("statut", sa.String(200), nullable=True),
            sa.Column("is_active", sa.Boolean, nullable=True),
            sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
            sa.Column("updated_at", sa.DateTime(timezone=True), nullable=True),
            sa.UniqueConstraint("company_id", "reference", name="uix_coll_feedback_uniq"),
        )

    if not _has("coll_availability"):
        op.create_table(
            "coll_availability",
            sa.Column("id", sa.Integer, primary_key=True, index=True),
            sa.Column("company_id", sa.Integer, nullable=False, index=True),
            sa.Column("reference", sa.String(200), nullable=False, index=True),
            sa.Column("collaborateur", sa.String(200), nullable=True),
            sa.Column("periode", sa.String(200), nullable=True),
            sa.Column("statut", sa.String(200), nullable=True),
            sa.Column("is_active", sa.Boolean, nullable=True),
            sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
            sa.Column("updated_at", sa.DateTime(timezone=True), nullable=True),
            sa.UniqueConstraint("company_id", "reference", name="uix_coll_availability_uniq"),
        )

    if not _has("coll_contract_renewals"):
        op.create_table(
            "coll_contract_renewals",
            sa.Column("id", sa.Integer, primary_key=True, index=True),
            sa.Column("company_id", sa.Integer, nullable=False, index=True),
            sa.Column("reference", sa.String(200), nullable=False, index=True),
            sa.Column("collaborateur", sa.String(200), nullable=True),
            sa.Column("echeance", sa.Date, nullable=True),
            sa.Column("type", sa.String(200), nullable=True),
            sa.Column("statut", sa.String(200), nullable=True),
            sa.Column("is_active", sa.Boolean, nullable=True),
            sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
            sa.Column("updated_at", sa.DateTime(timezone=True), nullable=True),
            sa.UniqueConstraint("company_id", "reference", name="uix_coll_contract_renewals_uniq"),
        )

    if not _has("coll_document_requests"):
        op.create_table(
            "coll_document_requests",
            sa.Column("id", sa.Integer, primary_key=True, index=True),
            sa.Column("company_id", sa.Integer, nullable=False, index=True),
            sa.Column("reference", sa.String(200), nullable=False, index=True),
            sa.Column("collaborateur", sa.String(200), nullable=True),
            sa.Column("document", sa.String(200), nullable=True),
            sa.Column("delai", sa.Date, nullable=True),
            sa.Column("statut", sa.String(200), nullable=True),
            sa.Column("is_active", sa.Boolean, nullable=True),
            sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
            sa.Column("updated_at", sa.DateTime(timezone=True), nullable=True),
            sa.UniqueConstraint("company_id", "reference", name="uix_coll_document_requests_uniq"),
        )


def downgrade():
    for t in reversed(TABLES):
        if _has(t):
            op.drop_table(t)
