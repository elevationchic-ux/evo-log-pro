"""060 : tables expansion dashboard (genere)."""
from alembic import op
import sqlalchemy as sa


revision = "060_dashboard_deep"
down_revision = "059_superadmin_deep"
branch_labels = None
depends_on = None


TABLES = [
    "module_healths",
    "activity_records",
    "unified_tasks",
    "quick_actions",
    "team_performances",
    "financial_summaries",
    "operational_alerts",
    "recent_documents",
    "unified_agenda",
    "integration_statuses",
]


def _has(name):
    insp = sa.inspect(op.get_bind())
    return name in set(insp.get_table_names())


def upgrade():
    if not _has("module_healths"):
        op.create_table(
            "module_healths",
            sa.Column("id", sa.Integer, primary_key=True, index=True),
            sa.Column("company_id", sa.Integer, nullable=False, index=True),
            sa.Column("code_module", sa.String(200), nullable=False, index=True),
            sa.Column("etat", sa.String(50), nullable=True),
            sa.Column("nombre_requetes_jour", sa.Integer, nullable=True),
            sa.Column("taux_erreur_pct", sa.Numeric, nullable=True),
            sa.Column("latence_p95_ms", sa.Integer, nullable=True),
            sa.Column("dernier_incident", sa.DateTime(timezone=True), nullable=True),
            sa.Column("is_active", sa.Boolean, nullable=True),
            sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
            sa.Column("updated_at", sa.DateTime(timezone=True), nullable=True),
            sa.UniqueConstraint("company_id", "code_module", name="uix_module_healths_uniq"),
        )

    if not _has("activity_records"):
        op.create_table(
            "activity_records",
            sa.Column("id", sa.Integer, primary_key=True, index=True),
            sa.Column("company_id", sa.Integer, nullable=False, index=True),
            sa.Column("reference", sa.String(200), nullable=False, index=True),
            sa.Column("module_source", sa.String(200), nullable=True),
            sa.Column("type_action", sa.String(200), nullable=True),
            sa.Column("utilisateur", sa.String(200), nullable=True),
            sa.Column("entite", sa.String(200), nullable=True),
            sa.Column("horodatage", sa.DateTime(timezone=True), nullable=True),
            sa.Column("resume", sa.Text, nullable=True),
            sa.Column("is_active", sa.Boolean, nullable=True),
            sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
            sa.Column("updated_at", sa.DateTime(timezone=True), nullable=True),
            sa.UniqueConstraint("company_id", "reference", name="uix_activity_records_uniq"),
        )

    if not _has("unified_tasks"):
        op.create_table(
            "unified_tasks",
            sa.Column("id", sa.Integer, primary_key=True, index=True),
            sa.Column("company_id", sa.Integer, nullable=False, index=True),
            sa.Column("reference", sa.String(200), nullable=False, index=True),
            sa.Column("titre", sa.String(200), nullable=True),
            sa.Column("module_source", sa.String(200), nullable=True),
            sa.Column("entite_id", sa.Integer, nullable=True),
            sa.Column("assigne_a", sa.Integer, nullable=True),
            sa.Column("date_echeance", sa.DateTime(timezone=True), nullable=True),
            sa.Column("priorite", sa.String(50), nullable=True),
            sa.Column("statut", sa.String(50), nullable=True),
            sa.Column("is_active", sa.Boolean, nullable=True),
            sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
            sa.Column("updated_at", sa.DateTime(timezone=True), nullable=True),
            sa.UniqueConstraint("company_id", "reference", name="uix_unified_tasks_uniq"),
        )

    if not _has("quick_actions"):
        op.create_table(
            "quick_actions",
            sa.Column("id", sa.Integer, primary_key=True, index=True),
            sa.Column("company_id", sa.Integer, nullable=False, index=True),
            sa.Column("reference", sa.String(200), nullable=False, index=True),
            sa.Column("libelle", sa.String(200), nullable=True),
            sa.Column("module_source", sa.String(200), nullable=True),
            sa.Column("url_action", sa.String(200), nullable=True),
            sa.Column("utilisateur_id", sa.Integer, nullable=True),
            sa.Column("ordre", sa.Integer, nullable=True),
            sa.Column("actif", sa.Boolean, nullable=True),
            sa.Column("is_active", sa.Boolean, nullable=True),
            sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
            sa.Column("updated_at", sa.DateTime(timezone=True), nullable=True),
            sa.UniqueConstraint("company_id", "reference", name="uix_quick_actions_uniq"),
        )

    if not _has("team_performances"):
        op.create_table(
            "team_performances",
            sa.Column("id", sa.Integer, primary_key=True, index=True),
            sa.Column("company_id", sa.Integer, nullable=False, index=True),
            sa.Column("reference", sa.String(200), nullable=False, index=True),
            sa.Column("equipe", sa.String(200), nullable=True),
            sa.Column("periode", sa.String(200), nullable=True),
            sa.Column("objectifs_atteints_pct", sa.Numeric, nullable=True),
            sa.Column("volume_traite", sa.Numeric, nullable=True),
            sa.Column("qualite_score", sa.Numeric, nullable=True),
            sa.Column("is_active", sa.Boolean, nullable=True),
            sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
            sa.Column("updated_at", sa.DateTime(timezone=True), nullable=True),
            sa.UniqueConstraint("company_id", "reference", name="uix_team_performances_uniq"),
        )

    if not _has("financial_summaries"):
        op.create_table(
            "financial_summaries",
            sa.Column("id", sa.Integer, primary_key=True, index=True),
            sa.Column("company_id", sa.Integer, nullable=False, index=True),
            sa.Column("reference", sa.String(200), nullable=False, index=True),
            sa.Column("periode", sa.String(200), nullable=True),
            sa.Column("ca_consolide_xaf", sa.Numeric, nullable=True),
            sa.Column("marge_brute_xaf", sa.Numeric, nullable=True),
            sa.Column("ebitda_xaf", sa.Numeric, nullable=True),
            sa.Column("bfr_xaf", sa.Numeric, nullable=True),
            sa.Column("tresorerie_xaf", sa.Numeric, nullable=True),
            sa.Column("is_active", sa.Boolean, nullable=True),
            sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
            sa.Column("updated_at", sa.DateTime(timezone=True), nullable=True),
            sa.UniqueConstraint("company_id", "reference", name="uix_financial_summaries_uniq"),
        )

    if not _has("operational_alerts"):
        op.create_table(
            "operational_alerts",
            sa.Column("id", sa.Integer, primary_key=True, index=True),
            sa.Column("company_id", sa.Integer, nullable=False, index=True),
            sa.Column("reference", sa.String(200), nullable=False, index=True),
            sa.Column("module_source", sa.String(200), nullable=True),
            sa.Column("niveau", sa.String(50), nullable=True),
            sa.Column("description", sa.Text, nullable=True),
            sa.Column("date_alerte", sa.DateTime(timezone=True), nullable=True),
            sa.Column("destinataire", sa.String(200), nullable=True),
            sa.Column("statut", sa.String(50), nullable=True),
            sa.Column("is_active", sa.Boolean, nullable=True),
            sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
            sa.Column("updated_at", sa.DateTime(timezone=True), nullable=True),
            sa.UniqueConstraint("company_id", "reference", name="uix_operational_alerts_uniq"),
        )

    if not _has("recent_documents"):
        op.create_table(
            "recent_documents",
            sa.Column("id", sa.Integer, primary_key=True, index=True),
            sa.Column("company_id", sa.Integer, nullable=False, index=True),
            sa.Column("reference", sa.String(200), nullable=False, index=True),
            sa.Column("titre", sa.String(200), nullable=True),
            sa.Column("module_source", sa.String(200), nullable=True),
            sa.Column("entite_id", sa.Integer, nullable=True),
            sa.Column("url", sa.String(200), nullable=True),
            sa.Column("date_creation", sa.DateTime(timezone=True), nullable=True),
            sa.Column("partage", sa.String(50), nullable=True),
            sa.Column("is_active", sa.Boolean, nullable=True),
            sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
            sa.Column("updated_at", sa.DateTime(timezone=True), nullable=True),
            sa.UniqueConstraint("company_id", "reference", name="uix_recent_documents_uniq"),
        )

    if not _has("unified_agenda"):
        op.create_table(
            "unified_agenda",
            sa.Column("id", sa.Integer, primary_key=True, index=True),
            sa.Column("company_id", sa.Integer, nullable=False, index=True),
            sa.Column("reference", sa.String(200), nullable=False, index=True),
            sa.Column("titre", sa.String(200), nullable=True),
            sa.Column("module_source", sa.String(200), nullable=True),
            sa.Column("entite_id", sa.Integer, nullable=True),
            sa.Column("date_debut", sa.DateTime(timezone=True), nullable=True),
            sa.Column("date_fin", sa.DateTime(timezone=True), nullable=True),
            sa.Column("invite_par", sa.String(200), nullable=True),
            sa.Column("is_active", sa.Boolean, nullable=True),
            sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
            sa.Column("updated_at", sa.DateTime(timezone=True), nullable=True),
            sa.UniqueConstraint("company_id", "reference", name="uix_unified_agenda_uniq"),
        )

    if not _has("integration_statuses"):
        op.create_table(
            "integration_statuses",
            sa.Column("id", sa.Integer, primary_key=True, index=True),
            sa.Column("company_id", sa.Integer, nullable=False, index=True),
            sa.Column("reference", sa.String(200), nullable=False, index=True),
            sa.Column("nom_integration", sa.String(200), nullable=True),
            sa.Column("url_testee", sa.String(200), nullable=True),
            sa.Column("date_dernier_test", sa.DateTime(timezone=True), nullable=True),
            sa.Column("succes", sa.Boolean, nullable=True),
            sa.Column("latence_ms", sa.Integer, nullable=True),
            sa.Column("message_erreur", sa.Text, nullable=True),
            sa.Column("is_active", sa.Boolean, nullable=True),
            sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
            sa.Column("updated_at", sa.DateTime(timezone=True), nullable=True),
            sa.UniqueConstraint("company_id", "reference", name="uix_integration_statuses_uniq"),
        )


def downgrade():
    for t in reversed(TABLES):
        if _has(t):
            op.drop_table(t)
