"""054 : tables expansion rh-personnel (genere)."""
from alembic import op
import sqlalchemy as sa


revision = "054_rh_deep"
down_revision = "053_parc_deep"
branch_labels = None
depends_on = None


TABLES = [
    "recruitments",
    "training_plans",
    "performance_reviews",
    "disciplinary_cases",
    "org_units",
    "workforce_plans",
    "employment_contracts",
    "employee_benefits",
    "employee_exits",
    "attendance_devices",
    "leave_quotas",
    "employee_skills",
    "hr_reports",
]


def _has(name):
    insp = sa.inspect(op.get_bind())
    return name in set(insp.get_table_names())


def upgrade():
    if not _has("recruitments"):
        op.create_table(
            "recruitments",
            sa.Column("id", sa.Integer, primary_key=True, index=True),
            sa.Column("company_id", sa.Integer, nullable=False, index=True),
            sa.Column("reference", sa.String(200), nullable=False, index=True),
            sa.Column("poste", sa.String(200), nullable=True),
            sa.Column("departement", sa.String(200), nullable=True),
            sa.Column("type_contrat", sa.String(50), nullable=True),
            sa.Column("date_ouverture", sa.Date, nullable=True),
            sa.Column("date_cloture", sa.Date, nullable=True),
            sa.Column("candidats_recus", sa.Integer, nullable=True),
            sa.Column("statut", sa.String(50), nullable=True),
            sa.Column("is_active", sa.Boolean, nullable=True),
            sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
            sa.Column("updated_at", sa.DateTime(timezone=True), nullable=True),
            sa.UniqueConstraint("company_id", "reference", name="uix_recruitments_uniq"),
        )

    if not _has("training_plans"):
        op.create_table(
            "training_plans",
            sa.Column("id", sa.Integer, primary_key=True, index=True),
            sa.Column("company_id", sa.Integer, nullable=False, index=True),
            sa.Column("reference", sa.String(200), nullable=False, index=True),
            sa.Column("intitule", sa.String(200), nullable=True),
            sa.Column("type_action", sa.String(50), nullable=True),
            sa.Column("organisme", sa.String(200), nullable=True),
            sa.Column("date_debut", sa.Date, nullable=True),
            sa.Column("date_fin", sa.Date, nullable=True),
            sa.Column("duree_heures", sa.Integer, nullable=True),
            sa.Column("cout_xaf", sa.Numeric, nullable=True),
            sa.Column("statut", sa.String(50), nullable=True),
            sa.Column("is_active", sa.Boolean, nullable=True),
            sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
            sa.Column("updated_at", sa.DateTime(timezone=True), nullable=True),
            sa.UniqueConstraint("company_id", "reference", name="uix_training_plans_uniq"),
        )

    if not _has("performance_reviews"):
        op.create_table(
            "performance_reviews",
            sa.Column("id", sa.Integer, primary_key=True, index=True),
            sa.Column("company_id", sa.Integer, nullable=False, index=True),
            sa.Column("reference", sa.String(200), nullable=False, index=True),
            sa.Column("employe_id", sa.Integer, nullable=True),
            sa.Column("periode", sa.String(200), nullable=True),
            sa.Column("date_entretien", sa.Date, nullable=True),
            sa.Column("evaluateur", sa.String(200), nullable=True),
            sa.Column("note_global", sa.Numeric, nullable=True),
            sa.Column("objectifs_atteints_pct", sa.Numeric, nullable=True),
            sa.Column("statut", sa.String(50), nullable=True),
            sa.Column("is_active", sa.Boolean, nullable=True),
            sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
            sa.Column("updated_at", sa.DateTime(timezone=True), nullable=True),
            sa.UniqueConstraint("company_id", "reference", name="uix_performance_reviews_uniq"),
        )

    if not _has("disciplinary_cases"):
        op.create_table(
            "disciplinary_cases",
            sa.Column("id", sa.Integer, primary_key=True, index=True),
            sa.Column("company_id", sa.Integer, nullable=False, index=True),
            sa.Column("reference", sa.String(200), nullable=False, index=True),
            sa.Column("employe_id", sa.Integer, nullable=True),
            sa.Column("date_fait", sa.Date, nullable=True),
            sa.Column("type_sanction", sa.String(50), nullable=True),
            sa.Column("motif", sa.Text, nullable=True),
            sa.Column("date_convocation", sa.Date, nullable=True),
            sa.Column("date_decision", sa.Date, nullable=True),
            sa.Column("statut", sa.String(50), nullable=True),
            sa.Column("is_active", sa.Boolean, nullable=True),
            sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
            sa.Column("updated_at", sa.DateTime(timezone=True), nullable=True),
            sa.UniqueConstraint("company_id", "reference", name="uix_disciplinary_cases_uniq"),
        )

    if not _has("org_units"):
        op.create_table(
            "org_units",
            sa.Column("id", sa.Integer, primary_key=True, index=True),
            sa.Column("company_id", sa.Integer, nullable=False, index=True),
            sa.Column("code_unite", sa.String(200), nullable=False, index=True),
            sa.Column("nom", sa.String(200), nullable=True),
            sa.Column("parent_code", sa.String(200), nullable=True),
            sa.Column("type_unite", sa.String(50), nullable=True),
            sa.Column("responsable", sa.String(200), nullable=True),
            sa.Column("effectif", sa.Integer, nullable=True),
            sa.Column("is_active", sa.Boolean, nullable=True),
            sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
            sa.Column("updated_at", sa.DateTime(timezone=True), nullable=True),
            sa.UniqueConstraint("company_id", "code_unite", name="uix_org_units_uniq"),
        )

    if not _has("workforce_plans"):
        op.create_table(
            "workforce_plans",
            sa.Column("id", sa.Integer, primary_key=True, index=True),
            sa.Column("company_id", sa.Integer, nullable=False, index=True),
            sa.Column("reference", sa.String(200), nullable=False, index=True),
            sa.Column("exercice", sa.Integer, nullable=True),
            sa.Column("mois", sa.String(200), nullable=True),
            sa.Column("masse_salariale_prevue_xaf", sa.Numeric, nullable=True),
            sa.Column("effectif_cadre", sa.Integer, nullable=True),
            sa.Column("effectif_non_cadre", sa.Integer, nullable=True),
            sa.Column("hypothese_inflation_pct", sa.Numeric, nullable=True),
            sa.Column("is_active", sa.Boolean, nullable=True),
            sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
            sa.Column("updated_at", sa.DateTime(timezone=True), nullable=True),
            sa.UniqueConstraint("company_id", "reference", name="uix_workforce_plans_uniq"),
        )

    if not _has("employment_contracts"):
        op.create_table(
            "employment_contracts",
            sa.Column("id", sa.Integer, primary_key=True, index=True),
            sa.Column("company_id", sa.Integer, nullable=False, index=True),
            sa.Column("numero_contrat", sa.String(200), nullable=False, index=True),
            sa.Column("employe_id", sa.Integer, nullable=True),
            sa.Column("type_contrat", sa.String(50), nullable=True),
            sa.Column("date_debut", sa.Date, nullable=True),
            sa.Column("date_fin", sa.Date, nullable=True),
            sa.Column("avenants", sa.Text, nullable=True),
            sa.Column("statut", sa.String(50), nullable=True),
            sa.Column("is_active", sa.Boolean, nullable=True),
            sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
            sa.Column("updated_at", sa.DateTime(timezone=True), nullable=True),
            sa.UniqueConstraint("company_id", "numero_contrat", name="uix_employment_contracts_uniq"),
        )

    if not _has("employee_benefits"):
        op.create_table(
            "employee_benefits",
            sa.Column("id", sa.Integer, primary_key=True, index=True),
            sa.Column("company_id", sa.Integer, nullable=False, index=True),
            sa.Column("reference", sa.String(200), nullable=False, index=True),
            sa.Column("employe_id", sa.Integer, nullable=True),
            sa.Column("type_avantage", sa.String(50), nullable=True),
            sa.Column("montant_annuel_xaf", sa.Numeric, nullable=True),
            sa.Column("date_debut", sa.Date, nullable=True),
            sa.Column("date_fin", sa.Date, nullable=True),
            sa.Column("statut", sa.String(50), nullable=True),
            sa.Column("is_active", sa.Boolean, nullable=True),
            sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
            sa.Column("updated_at", sa.DateTime(timezone=True), nullable=True),
            sa.UniqueConstraint("company_id", "reference", name="uix_employee_benefits_uniq"),
        )

    if not _has("employee_exits"):
        op.create_table(
            "employee_exits",
            sa.Column("id", sa.Integer, primary_key=True, index=True),
            sa.Column("company_id", sa.Integer, nullable=False, index=True),
            sa.Column("reference", sa.String(200), nullable=False, index=True),
            sa.Column("employe_id", sa.Integer, nullable=True),
            sa.Column("type_depart", sa.String(50), nullable=True),
            sa.Column("date_depart", sa.Date, nullable=True),
            sa.Column("preavis_debut", sa.Date, nullable=True),
            sa.Column("preavis_fin", sa.Date, nullable=True),
            sa.Column("solde_tout_compte_xaf", sa.Numeric, nullable=True),
            sa.Column("statut", sa.String(50), nullable=True),
            sa.Column("is_active", sa.Boolean, nullable=True),
            sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
            sa.Column("updated_at", sa.DateTime(timezone=True), nullable=True),
            sa.UniqueConstraint("company_id", "reference", name="uix_employee_exits_uniq"),
        )

    if not _has("attendance_devices"):
        op.create_table(
            "attendance_devices",
            sa.Column("id", sa.Integer, primary_key=True, index=True),
            sa.Column("company_id", sa.Integer, nullable=False, index=True),
            sa.Column("code_terminal", sa.String(200), nullable=False, index=True),
            sa.Column("lieu", sa.String(200), nullable=True),
            sa.Column("type_terminal", sa.String(50), nullable=True),
            sa.Column("adresse_ip", sa.String(200), nullable=True),
            sa.Column("derniere_synchro", sa.DateTime(timezone=True), nullable=True),
            sa.Column("statut", sa.String(50), nullable=True),
            sa.Column("is_active", sa.Boolean, nullable=True),
            sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
            sa.Column("updated_at", sa.DateTime(timezone=True), nullable=True),
            sa.UniqueConstraint("company_id", "code_terminal", name="uix_attendance_devices_uniq"),
        )

    if not _has("leave_quotas"):
        op.create_table(
            "leave_quotas",
            sa.Column("id", sa.Integer, primary_key=True, index=True),
            sa.Column("company_id", sa.Integer, nullable=False, index=True),
            sa.Column("reference", sa.String(200), nullable=False, index=True),
            sa.Column("employe_id", sa.Integer, nullable=True),
            sa.Column("exercice", sa.Integer, nullable=True),
            sa.Column("droit_initial_jours", sa.Numeric, nullable=True),
            sa.Column("jours_pris", sa.Numeric, nullable=True),
            sa.Column("jours_reportes", sa.Numeric, nullable=True),
            sa.Column("solde_actuel", sa.Numeric, nullable=True),
            sa.Column("is_active", sa.Boolean, nullable=True),
            sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
            sa.Column("updated_at", sa.DateTime(timezone=True), nullable=True),
            sa.UniqueConstraint("company_id", "reference", name="uix_leave_quotas_uniq"),
        )

    if not _has("employee_skills"):
        op.create_table(
            "employee_skills",
            sa.Column("id", sa.Integer, primary_key=True, index=True),
            sa.Column("company_id", sa.Integer, nullable=False, index=True),
            sa.Column("reference", sa.String(200), nullable=False, index=True),
            sa.Column("employe_id", sa.Integer, nullable=True),
            sa.Column("competence", sa.String(200), nullable=True),
            sa.Column("niveau", sa.String(50), nullable=True),
            sa.Column("date_evaluation", sa.Date, nullable=True),
            sa.Column("date_expiration", sa.Date, nullable=True),
            sa.Column("is_active", sa.Boolean, nullable=True),
            sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
            sa.Column("updated_at", sa.DateTime(timezone=True), nullable=True),
            sa.UniqueConstraint("company_id", "reference", name="uix_employee_skills_uniq"),
        )

    if not _has("hr_reports"):
        op.create_table(
            "hr_reports",
            sa.Column("id", sa.Integer, primary_key=True, index=True),
            sa.Column("company_id", sa.Integer, nullable=False, index=True),
            sa.Column("reference", sa.String(200), nullable=False, index=True),
            sa.Column("periode_debut", sa.Date, nullable=True),
            sa.Column("periode_fin", sa.Date, nullable=True),
            sa.Column("effectif_debut", sa.Integer, nullable=True),
            sa.Column("effectif_fin", sa.Integer, nullable=True),
            sa.Column("taux_absent_pct", sa.Numeric, nullable=True),
            sa.Column("taux_turnover_pct", sa.Numeric, nullable=True),
            sa.Column("masse_salariale_xaf", sa.Numeric, nullable=True),
            sa.Column("is_active", sa.Boolean, nullable=True),
            sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
            sa.Column("updated_at", sa.DateTime(timezone=True), nullable=True),
            sa.UniqueConstraint("company_id", "reference", name="uix_hr_reports_uniq"),
        )


def downgrade():
    for t in reversed(TABLES):
        if _has(t):
            op.drop_table(t)
