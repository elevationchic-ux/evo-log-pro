"""094 : tables expansion portail-employe (genere)."""
from alembic import op
import sqlalchemy as sa


revision = "094_employe_d_deep"
down_revision = "093_commercial_d2_deep"
branch_labels = None
depends_on = None


TABLES = [
    "emp_leave_requests",
    "emp_timesheet_entries",
    "emp_overtime_requests",
    "emp_attendance_corrections",
    "emp_shift_swaps",
    "emp_training_enrollments",
    "emp_skill_declarations",
    "emp_certification_renewals",
    "emp_personal_info_changes",
    "emp_bank_updates",
    "emp_emergency_contacts",
    "emp_badge_requests",
    "emp_access_requests",
    "emp_document_uploads",
    "emp_self_reviews",
    "emp_mobility_apps",
    "emp_sickness_declarations",
]


def _has(name):
    insp = sa.inspect(op.get_bind())
    return name in set(insp.get_table_names())


def upgrade():
    if not _has("emp_leave_requests"):
        op.create_table(
            "emp_leave_requests",
            sa.Column("id", sa.Integer, primary_key=True, index=True),
            sa.Column("company_id", sa.Integer, nullable=False, index=True),
            sa.Column("reference", sa.String(200), nullable=False, index=True),
            sa.Column("collaborateur", sa.String(200), nullable=True),
            sa.Column("type_conge", sa.String(200), nullable=True),
            sa.Column("debut", sa.Date, nullable=True),
            sa.Column("fin", sa.Date, nullable=True),
            sa.Column("jours", sa.Integer, nullable=True),
            sa.Column("statut", sa.String(200), nullable=True),
            sa.Column("is_active", sa.Boolean, nullable=True),
            sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
            sa.Column("updated_at", sa.DateTime(timezone=True), nullable=True),
            sa.UniqueConstraint("company_id", "reference", name="uix_emp_leave_requests_uniq"),
        )

    if not _has("emp_timesheet_entries"):
        op.create_table(
            "emp_timesheet_entries",
            sa.Column("id", sa.Integer, primary_key=True, index=True),
            sa.Column("company_id", sa.Integer, nullable=False, index=True),
            sa.Column("reference", sa.String(200), nullable=False, index=True),
            sa.Column("collaborateur", sa.String(200), nullable=True),
            sa.Column("date", sa.Date, nullable=True),
            sa.Column("heures", sa.Numeric, nullable=True),
            sa.Column("projet", sa.String(200), nullable=True),
            sa.Column("statut", sa.String(200), nullable=True),
            sa.Column("is_active", sa.Boolean, nullable=True),
            sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
            sa.Column("updated_at", sa.DateTime(timezone=True), nullable=True),
            sa.UniqueConstraint("company_id", "reference", name="uix_emp_timesheet_entries_uniq"),
        )

    if not _has("emp_overtime_requests"):
        op.create_table(
            "emp_overtime_requests",
            sa.Column("id", sa.Integer, primary_key=True, index=True),
            sa.Column("company_id", sa.Integer, nullable=False, index=True),
            sa.Column("reference", sa.String(200), nullable=False, index=True),
            sa.Column("collaborateur", sa.String(200), nullable=True),
            sa.Column("minutes", sa.Integer, nullable=True),
            sa.Column("motif", sa.String(200), nullable=True),
            sa.Column("date", sa.Date, nullable=True),
            sa.Column("statut", sa.String(200), nullable=True),
            sa.Column("is_active", sa.Boolean, nullable=True),
            sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
            sa.Column("updated_at", sa.DateTime(timezone=True), nullable=True),
            sa.UniqueConstraint("company_id", "reference", name="uix_emp_overtime_requests_uniq"),
        )

    if not _has("emp_attendance_corrections"):
        op.create_table(
            "emp_attendance_corrections",
            sa.Column("id", sa.Integer, primary_key=True, index=True),
            sa.Column("company_id", sa.Integer, nullable=False, index=True),
            sa.Column("reference", sa.String(200), nullable=False, index=True),
            sa.Column("collaborateur", sa.String(200), nullable=True),
            sa.Column("date_concernee", sa.Date, nullable=True),
            sa.Column("motif", sa.Text, nullable=True),
            sa.Column("statut", sa.String(200), nullable=True),
            sa.Column("is_active", sa.Boolean, nullable=True),
            sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
            sa.Column("updated_at", sa.DateTime(timezone=True), nullable=True),
            sa.UniqueConstraint("company_id", "reference", name="uix_emp_attendance_corrections_uniq"),
        )

    if not _has("emp_shift_swaps"):
        op.create_table(
            "emp_shift_swaps",
            sa.Column("id", sa.Integer, primary_key=True, index=True),
            sa.Column("company_id", sa.Integer, nullable=False, index=True),
            sa.Column("reference", sa.String(200), nullable=False, index=True),
            sa.Column("demandeur", sa.String(200), nullable=True),
            sa.Column("partenaire", sa.String(200), nullable=True),
            sa.Column("date_poste", sa.DateTime(timezone=True), nullable=True),
            sa.Column("statut", sa.String(200), nullable=True),
            sa.Column("is_active", sa.Boolean, nullable=True),
            sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
            sa.Column("updated_at", sa.DateTime(timezone=True), nullable=True),
            sa.UniqueConstraint("company_id", "reference", name="uix_emp_shift_swaps_uniq"),
        )

    if not _has("emp_training_enrollments"):
        op.create_table(
            "emp_training_enrollments",
            sa.Column("id", sa.Integer, primary_key=True, index=True),
            sa.Column("company_id", sa.Integer, nullable=False, index=True),
            sa.Column("reference", sa.String(200), nullable=False, index=True),
            sa.Column("collaborateur", sa.String(200), nullable=True),
            sa.Column("formation", sa.String(200), nullable=True),
            sa.Column("date_debut", sa.Date, nullable=True),
            sa.Column("organism", sa.String(200), nullable=True),
            sa.Column("statut", sa.String(200), nullable=True),
            sa.Column("is_active", sa.Boolean, nullable=True),
            sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
            sa.Column("updated_at", sa.DateTime(timezone=True), nullable=True),
            sa.UniqueConstraint("company_id", "reference", name="uix_emp_training_enrollments_uniq"),
        )

    if not _has("emp_skill_declarations"):
        op.create_table(
            "emp_skill_declarations",
            sa.Column("id", sa.Integer, primary_key=True, index=True),
            sa.Column("company_id", sa.Integer, nullable=False, index=True),
            sa.Column("reference", sa.String(200), nullable=False, index=True),
            sa.Column("collaborateur", sa.String(200), nullable=True),
            sa.Column("competence", sa.String(200), nullable=True),
            sa.Column("niveau", sa.String(200), nullable=True),
            sa.Column("date", sa.Date, nullable=True),
            sa.Column("statut", sa.String(200), nullable=True),
            sa.Column("is_active", sa.Boolean, nullable=True),
            sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
            sa.Column("updated_at", sa.DateTime(timezone=True), nullable=True),
            sa.UniqueConstraint("company_id", "reference", name="uix_emp_skill_declarations_uniq"),
        )

    if not _has("emp_certification_renewals"):
        op.create_table(
            "emp_certification_renewals",
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
            sa.UniqueConstraint("company_id", "reference", name="uix_emp_certification_renewals_uniq"),
        )

    if not _has("emp_personal_info_changes"):
        op.create_table(
            "emp_personal_info_changes",
            sa.Column("id", sa.Integer, primary_key=True, index=True),
            sa.Column("company_id", sa.Integer, nullable=False, index=True),
            sa.Column("reference", sa.String(200), nullable=False, index=True),
            sa.Column("collaborateur", sa.String(200), nullable=True),
            sa.Column("champ", sa.String(200), nullable=True),
            sa.Column("nouvelle_valeur", sa.String(200), nullable=True),
            sa.Column("date", sa.Date, nullable=True),
            sa.Column("statut", sa.String(200), nullable=True),
            sa.Column("is_active", sa.Boolean, nullable=True),
            sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
            sa.Column("updated_at", sa.DateTime(timezone=True), nullable=True),
            sa.UniqueConstraint("company_id", "reference", name="uix_emp_personal_info_changes_uniq"),
        )

    if not _has("emp_bank_updates"):
        op.create_table(
            "emp_bank_updates",
            sa.Column("id", sa.Integer, primary_key=True, index=True),
            sa.Column("company_id", sa.Integer, nullable=False, index=True),
            sa.Column("reference", sa.String(200), nullable=False, index=True),
            sa.Column("collaborateur", sa.String(200), nullable=True),
            sa.Column("banque", sa.String(200), nullable=True),
            sa.Column("date_effet", sa.Date, nullable=True),
            sa.Column("statut", sa.String(200), nullable=True),
            sa.Column("is_active", sa.Boolean, nullable=True),
            sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
            sa.Column("updated_at", sa.DateTime(timezone=True), nullable=True),
            sa.UniqueConstraint("company_id", "reference", name="uix_emp_bank_updates_uniq"),
        )

    if not _has("emp_emergency_contacts"):
        op.create_table(
            "emp_emergency_contacts",
            sa.Column("id", sa.Integer, primary_key=True, index=True),
            sa.Column("company_id", sa.Integer, nullable=False, index=True),
            sa.Column("reference", sa.String(200), nullable=False, index=True),
            sa.Column("collaborateur", sa.String(200), nullable=True),
            sa.Column("nom", sa.String(200), nullable=True),
            sa.Column("lien", sa.String(200), nullable=True),
            sa.Column("telephone", sa.String(200), nullable=True),
            sa.Column("statut", sa.String(200), nullable=True),
            sa.Column("is_active", sa.Boolean, nullable=True),
            sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
            sa.Column("updated_at", sa.DateTime(timezone=True), nullable=True),
            sa.UniqueConstraint("company_id", "reference", name="uix_emp_emergency_contacts_uniq"),
        )

    if not _has("emp_badge_requests"):
        op.create_table(
            "emp_badge_requests",
            sa.Column("id", sa.Integer, primary_key=True, index=True),
            sa.Column("company_id", sa.Integer, nullable=False, index=True),
            sa.Column("reference", sa.String(200), nullable=False, index=True),
            sa.Column("collaborateur", sa.String(200), nullable=True),
            sa.Column("motif", sa.String(200), nullable=True),
            sa.Column("date", sa.Date, nullable=True),
            sa.Column("statut", sa.String(200), nullable=True),
            sa.Column("is_active", sa.Boolean, nullable=True),
            sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
            sa.Column("updated_at", sa.DateTime(timezone=True), nullable=True),
            sa.UniqueConstraint("company_id", "reference", name="uix_emp_badge_requests_uniq"),
        )

    if not _has("emp_access_requests"):
        op.create_table(
            "emp_access_requests",
            sa.Column("id", sa.Integer, primary_key=True, index=True),
            sa.Column("company_id", sa.Integer, nullable=False, index=True),
            sa.Column("reference", sa.String(200), nullable=False, index=True),
            sa.Column("collaborateur", sa.String(200), nullable=True),
            sa.Column("ressource", sa.String(200), nullable=True),
            sa.Column("type_acces", sa.String(200), nullable=True),
            sa.Column("date", sa.Date, nullable=True),
            sa.Column("statut", sa.String(200), nullable=True),
            sa.Column("is_active", sa.Boolean, nullable=True),
            sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
            sa.Column("updated_at", sa.DateTime(timezone=True), nullable=True),
            sa.UniqueConstraint("company_id", "reference", name="uix_emp_access_requests_uniq"),
        )

    if not _has("emp_document_uploads"):
        op.create_table(
            "emp_document_uploads",
            sa.Column("id", sa.Integer, primary_key=True, index=True),
            sa.Column("company_id", sa.Integer, nullable=False, index=True),
            sa.Column("reference", sa.String(200), nullable=False, index=True),
            sa.Column("collaborateur", sa.String(200), nullable=True),
            sa.Column("type_piece", sa.String(200), nullable=True),
            sa.Column("fichier", sa.String(200), nullable=True),
            sa.Column("date", sa.DateTime(timezone=True), nullable=True),
            sa.Column("statut", sa.String(200), nullable=True),
            sa.Column("is_active", sa.Boolean, nullable=True),
            sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
            sa.Column("updated_at", sa.DateTime(timezone=True), nullable=True),
            sa.UniqueConstraint("company_id", "reference", name="uix_emp_document_uploads_uniq"),
        )

    if not _has("emp_self_reviews"):
        op.create_table(
            "emp_self_reviews",
            sa.Column("id", sa.Integer, primary_key=True, index=True),
            sa.Column("company_id", sa.Integer, nullable=False, index=True),
            sa.Column("reference", sa.String(200), nullable=False, index=True),
            sa.Column("collaborateur", sa.String(200), nullable=True),
            sa.Column("periode", sa.String(200), nullable=True),
            sa.Column("accomplissements", sa.Text, nullable=True),
            sa.Column("date", sa.Date, nullable=True),
            sa.Column("statut", sa.String(200), nullable=True),
            sa.Column("is_active", sa.Boolean, nullable=True),
            sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
            sa.Column("updated_at", sa.DateTime(timezone=True), nullable=True),
            sa.UniqueConstraint("company_id", "reference", name="uix_emp_self_reviews_uniq"),
        )

    if not _has("emp_mobility_apps"):
        op.create_table(
            "emp_mobility_apps",
            sa.Column("id", sa.Integer, primary_key=True, index=True),
            sa.Column("company_id", sa.Integer, nullable=False, index=True),
            sa.Column("reference", sa.String(200), nullable=False, index=True),
            sa.Column("collaborateur", sa.String(200), nullable=True),
            sa.Column("poste_cible", sa.String(200), nullable=True),
            sa.Column("motivation", sa.Text, nullable=True),
            sa.Column("date", sa.Date, nullable=True),
            sa.Column("statut", sa.String(200), nullable=True),
            sa.Column("is_active", sa.Boolean, nullable=True),
            sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
            sa.Column("updated_at", sa.DateTime(timezone=True), nullable=True),
            sa.UniqueConstraint("company_id", "reference", name="uix_emp_mobility_apps_uniq"),
        )

    if not _has("emp_sickness_declarations"):
        op.create_table(
            "emp_sickness_declarations",
            sa.Column("id", sa.Integer, primary_key=True, index=True),
            sa.Column("company_id", sa.Integer, nullable=False, index=True),
            sa.Column("reference", sa.String(200), nullable=False, index=True),
            sa.Column("collaborateur", sa.String(200), nullable=True),
            sa.Column("debut", sa.Date, nullable=True),
            sa.Column("duree_jours", sa.Integer, nullable=True),
            sa.Column("justificatif", sa.Boolean, nullable=True),
            sa.Column("statut", sa.String(200), nullable=True),
            sa.Column("is_active", sa.Boolean, nullable=True),
            sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
            sa.Column("updated_at", sa.DateTime(timezone=True), nullable=True),
            sa.UniqueConstraint("company_id", "reference", name="uix_emp_sickness_declarations_uniq"),
        )


def downgrade():
    for t in reversed(TABLES):
        if _has(t):
            op.drop_table(t)
