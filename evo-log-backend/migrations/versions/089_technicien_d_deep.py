"""089 : tables expansion portail-technicien (genere)."""
from alembic import op
import sqlalchemy as sa


revision = "089_technicien_d_deep"
down_revision = "088_magasinier_c_deep"
branch_labels = None
depends_on = None


TABLES = [
    "tech_work_orders",
    "tech_intervention_sheets",
    "tech_diagnoses",
    "tech_parts_consumption",
    "tech_preventive_plans",
    "tech_breakdown_tickets",
    "tech_repair_reports",
    "tech_calibration_records",
    "tech_equipment_checklists",
    "tech_tool_loans",
    "tech_safety_lockouts",
    "tech_warranty_claims",
    "tech_service_appointments",
    "tech_labor_timesheets",
    "tech_upgrade_requests",
    "tech_failure_analyses",
    "tech_spare_requests",
    "tech_inspection_records",
    "tech_work_order_costs",
]


def _has(name):
    insp = sa.inspect(op.get_bind())
    return name in set(insp.get_table_names())


def upgrade():
    if not _has("tech_work_orders"):
        op.create_table(
            "tech_work_orders",
            sa.Column("id", sa.Integer, primary_key=True, index=True),
            sa.Column("company_id", sa.Integer, nullable=False, index=True),
            sa.Column("reference", sa.String(200), nullable=False, index=True),
            sa.Column("vehicule", sa.String(200), nullable=True),
            sa.Column("type_travaux", sa.String(200), nullable=True),
            sa.Column("description", sa.Text, nullable=True),
            sa.Column("ouverture", sa.DateTime(timezone=True), nullable=True),
            sa.Column("cloture", sa.DateTime(timezone=True), nullable=True),
            sa.Column("statut", sa.String(200), nullable=True),
            sa.Column("is_active", sa.Boolean, nullable=True),
            sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
            sa.Column("updated_at", sa.DateTime(timezone=True), nullable=True),
            sa.UniqueConstraint("company_id", "reference", name="uix_tech_work_orders_uniq"),
        )

    if not _has("tech_intervention_sheets"):
        op.create_table(
            "tech_intervention_sheets",
            sa.Column("id", sa.Integer, primary_key=True, index=True),
            sa.Column("company_id", sa.Integer, nullable=False, index=True),
            sa.Column("reference", sa.String(200), nullable=False, index=True),
            sa.Column("ordre_travail", sa.String(200), nullable=True),
            sa.Column("technicien", sa.String(200), nullable=True),
            sa.Column("duree_min", sa.Integer, nullable=True),
            sa.Column("main_oeuvre", sa.Numeric, nullable=True),
            sa.Column("statut", sa.String(200), nullable=True),
            sa.Column("is_active", sa.Boolean, nullable=True),
            sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
            sa.Column("updated_at", sa.DateTime(timezone=True), nullable=True),
            sa.UniqueConstraint("company_id", "reference", name="uix_tech_intervention_sheets_uniq"),
        )

    if not _has("tech_diagnoses"):
        op.create_table(
            "tech_diagnoses",
            sa.Column("id", sa.Integer, primary_key=True, index=True),
            sa.Column("company_id", sa.Integer, nullable=False, index=True),
            sa.Column("reference", sa.String(200), nullable=False, index=True),
            sa.Column("vehicule", sa.String(200), nullable=True),
            sa.Column("symptome", sa.String(200), nullable=True),
            sa.Column("cause_racine", sa.Text, nullable=True),
            sa.Column("date", sa.DateTime(timezone=True), nullable=True),
            sa.Column("statut", sa.String(200), nullable=True),
            sa.Column("is_active", sa.Boolean, nullable=True),
            sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
            sa.Column("updated_at", sa.DateTime(timezone=True), nullable=True),
            sa.UniqueConstraint("company_id", "reference", name="uix_tech_diagnoses_uniq"),
        )

    if not _has("tech_parts_consumption"):
        op.create_table(
            "tech_parts_consumption",
            sa.Column("id", sa.Integer, primary_key=True, index=True),
            sa.Column("company_id", sa.Integer, nullable=False, index=True),
            sa.Column("reference", sa.String(200), nullable=False, index=True),
            sa.Column("ordre_travail", sa.String(200), nullable=True),
            sa.Column("piece", sa.String(200), nullable=True),
            sa.Column("quantite", sa.Integer, nullable=True),
            sa.Column("cout_unitaire", sa.Numeric, nullable=True),
            sa.Column("statut", sa.String(200), nullable=True),
            sa.Column("is_active", sa.Boolean, nullable=True),
            sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
            sa.Column("updated_at", sa.DateTime(timezone=True), nullable=True),
            sa.UniqueConstraint("company_id", "reference", name="uix_tech_parts_consumption_uniq"),
        )

    if not _has("tech_preventive_plans"):
        op.create_table(
            "tech_preventive_plans",
            sa.Column("id", sa.Integer, primary_key=True, index=True),
            sa.Column("company_id", sa.Integer, nullable=False, index=True),
            sa.Column("reference", sa.String(200), nullable=False, index=True),
            sa.Column("vehicule", sa.String(200), nullable=True),
            sa.Column("operation", sa.String(200), nullable=True),
            sa.Column("intervalle_km", sa.Integer, nullable=True),
            sa.Column("derniere_realisation", sa.Date, nullable=True),
            sa.Column("statut", sa.String(200), nullable=True),
            sa.Column("is_active", sa.Boolean, nullable=True),
            sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
            sa.Column("updated_at", sa.DateTime(timezone=True), nullable=True),
            sa.UniqueConstraint("company_id", "reference", name="uix_tech_preventive_plans_uniq"),
        )

    if not _has("tech_breakdown_tickets"):
        op.create_table(
            "tech_breakdown_tickets",
            sa.Column("id", sa.Integer, primary_key=True, index=True),
            sa.Column("company_id", sa.Integer, nullable=False, index=True),
            sa.Column("reference", sa.String(200), nullable=False, index=True),
            sa.Column("vehicule", sa.String(200), nullable=True),
            sa.Column("lieu", sa.String(200), nullable=True),
            sa.Column("severite", sa.String(200), nullable=True),
            sa.Column("recu", sa.DateTime(timezone=True), nullable=True),
            sa.Column("statut", sa.String(200), nullable=True),
            sa.Column("is_active", sa.Boolean, nullable=True),
            sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
            sa.Column("updated_at", sa.DateTime(timezone=True), nullable=True),
            sa.UniqueConstraint("company_id", "reference", name="uix_tech_breakdown_tickets_uniq"),
        )

    if not _has("tech_repair_reports"):
        op.create_table(
            "tech_repair_reports",
            sa.Column("id", sa.Integer, primary_key=True, index=True),
            sa.Column("company_id", sa.Integer, nullable=False, index=True),
            sa.Column("reference", sa.String(200), nullable=False, index=True),
            sa.Column("ordre_travail", sa.String(200), nullable=True),
            sa.Column("travaux_realises", sa.Text, nullable=True),
            sa.Column("test_sortie_ok", sa.Boolean, nullable=True),
            sa.Column("date", sa.DateTime(timezone=True), nullable=True),
            sa.Column("statut", sa.String(200), nullable=True),
            sa.Column("is_active", sa.Boolean, nullable=True),
            sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
            sa.Column("updated_at", sa.DateTime(timezone=True), nullable=True),
            sa.UniqueConstraint("company_id", "reference", name="uix_tech_repair_reports_uniq"),
        )

    if not _has("tech_calibration_records"):
        op.create_table(
            "tech_calibration_records",
            sa.Column("id", sa.Integer, primary_key=True, index=True),
            sa.Column("company_id", sa.Integer, nullable=False, index=True),
            sa.Column("reference", sa.String(200), nullable=False, index=True),
            sa.Column("instrument", sa.String(200), nullable=True),
            sa.Column("tolerance", sa.String(200), nullable=True),
            sa.Column("date_etalonnage", sa.Date, nullable=True),
            sa.Column("prochaine_date", sa.Date, nullable=True),
            sa.Column("statut", sa.String(200), nullable=True),
            sa.Column("is_active", sa.Boolean, nullable=True),
            sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
            sa.Column("updated_at", sa.DateTime(timezone=True), nullable=True),
            sa.UniqueConstraint("company_id", "reference", name="uix_tech_calibration_records_uniq"),
        )

    if not _has("tech_equipment_checklists"):
        op.create_table(
            "tech_equipment_checklists",
            sa.Column("id", sa.Integer, primary_key=True, index=True),
            sa.Column("company_id", sa.Integer, nullable=False, index=True),
            sa.Column("reference", sa.String(200), nullable=False, index=True),
            sa.Column("equipement", sa.String(200), nullable=True),
            sa.Column("points_controles", sa.Integer, nullable=True),
            sa.Column("anomalies", sa.Integer, nullable=True),
            sa.Column("date", sa.DateTime(timezone=True), nullable=True),
            sa.Column("statut", sa.String(200), nullable=True),
            sa.Column("is_active", sa.Boolean, nullable=True),
            sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
            sa.Column("updated_at", sa.DateTime(timezone=True), nullable=True),
            sa.UniqueConstraint("company_id", "reference", name="uix_tech_equipment_checklists_uniq"),
        )

    if not _has("tech_tool_loans"):
        op.create_table(
            "tech_tool_loans",
            sa.Column("id", sa.Integer, primary_key=True, index=True),
            sa.Column("company_id", sa.Integer, nullable=False, index=True),
            sa.Column("reference", sa.String(200), nullable=False, index=True),
            sa.Column("outil", sa.String(200), nullable=True),
            sa.Column("technicien", sa.String(200), nullable=True),
            sa.Column("sortie", sa.DateTime(timezone=True), nullable=True),
            sa.Column("retour", sa.DateTime(timezone=True), nullable=True),
            sa.Column("statut", sa.String(200), nullable=True),
            sa.Column("is_active", sa.Boolean, nullable=True),
            sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
            sa.Column("updated_at", sa.DateTime(timezone=True), nullable=True),
            sa.UniqueConstraint("company_id", "reference", name="uix_tech_tool_loans_uniq"),
        )

    if not _has("tech_safety_lockouts"):
        op.create_table(
            "tech_safety_lockouts",
            sa.Column("id", sa.Integer, primary_key=True, index=True),
            sa.Column("company_id", sa.Integer, nullable=False, index=True),
            sa.Column("reference", sa.String(200), nullable=False, index=True),
            sa.Column("installation", sa.String(200), nullable=True),
            sa.Column("motif", sa.String(200), nullable=True),
            sa.Column("pose", sa.DateTime(timezone=True), nullable=True),
            sa.Column("levee", sa.DateTime(timezone=True), nullable=True),
            sa.Column("statut", sa.String(200), nullable=True),
            sa.Column("is_active", sa.Boolean, nullable=True),
            sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
            sa.Column("updated_at", sa.DateTime(timezone=True), nullable=True),
            sa.UniqueConstraint("company_id", "reference", name="uix_tech_safety_lockouts_uniq"),
        )

    if not _has("tech_warranty_claims"):
        op.create_table(
            "tech_warranty_claims",
            sa.Column("id", sa.Integer, primary_key=True, index=True),
            sa.Column("company_id", sa.Integer, nullable=False, index=True),
            sa.Column("reference", sa.String(200), nullable=False, index=True),
            sa.Column("piece", sa.String(200), nullable=True),
            sa.Column("fournisseur", sa.String(200), nullable=True),
            sa.Column("date_achat", sa.Date, nullable=True),
            sa.Column("montant", sa.Numeric, nullable=True),
            sa.Column("statut", sa.String(200), nullable=True),
            sa.Column("is_active", sa.Boolean, nullable=True),
            sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
            sa.Column("updated_at", sa.DateTime(timezone=True), nullable=True),
            sa.UniqueConstraint("company_id", "reference", name="uix_tech_warranty_claims_uniq"),
        )

    if not _has("tech_service_appointments"):
        op.create_table(
            "tech_service_appointments",
            sa.Column("id", sa.Integer, primary_key=True, index=True),
            sa.Column("company_id", sa.Integer, nullable=False, index=True),
            sa.Column("reference", sa.String(200), nullable=False, index=True),
            sa.Column("vehicule", sa.String(200), nullable=True),
            sa.Column("creneau", sa.DateTime(timezone=True), nullable=True),
            sa.Column("atelier", sa.String(200), nullable=True),
            sa.Column("duree_min", sa.Integer, nullable=True),
            sa.Column("statut", sa.String(200), nullable=True),
            sa.Column("is_active", sa.Boolean, nullable=True),
            sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
            sa.Column("updated_at", sa.DateTime(timezone=True), nullable=True),
            sa.UniqueConstraint("company_id", "reference", name="uix_tech_service_appointments_uniq"),
        )

    if not _has("tech_labor_timesheets"):
        op.create_table(
            "tech_labor_timesheets",
            sa.Column("id", sa.Integer, primary_key=True, index=True),
            sa.Column("company_id", sa.Integer, nullable=False, index=True),
            sa.Column("reference", sa.String(200), nullable=False, index=True),
            sa.Column("ordre_travail", sa.String(200), nullable=True),
            sa.Column("technicien", sa.String(200), nullable=True),
            sa.Column("minutes", sa.Integer, nullable=True),
            sa.Column("date", sa.Date, nullable=True),
            sa.Column("statut", sa.String(200), nullable=True),
            sa.Column("is_active", sa.Boolean, nullable=True),
            sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
            sa.Column("updated_at", sa.DateTime(timezone=True), nullable=True),
            sa.UniqueConstraint("company_id", "reference", name="uix_tech_labor_timesheets_uniq"),
        )

    if not _has("tech_upgrade_requests"):
        op.create_table(
            "tech_upgrade_requests",
            sa.Column("id", sa.Integer, primary_key=True, index=True),
            sa.Column("company_id", sa.Integer, nullable=False, index=True),
            sa.Column("reference", sa.String(200), nullable=False, index=True),
            sa.Column("cible", sa.String(200), nullable=True),
            sa.Column("objet", sa.String(200), nullable=True),
            sa.Column("gain_attendu", sa.Text, nullable=True),
            sa.Column("cout_estime", sa.Numeric, nullable=True),
            sa.Column("statut", sa.String(200), nullable=True),
            sa.Column("is_active", sa.Boolean, nullable=True),
            sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
            sa.Column("updated_at", sa.DateTime(timezone=True), nullable=True),
            sa.UniqueConstraint("company_id", "reference", name="uix_tech_upgrade_requests_uniq"),
        )

    if not _has("tech_failure_analyses"):
        op.create_table(
            "tech_failure_analyses",
            sa.Column("id", sa.Integer, primary_key=True, index=True),
            sa.Column("company_id", sa.Integer, nullable=False, index=True),
            sa.Column("reference", sa.String(200), nullable=False, index=True),
            sa.Column("vehicule", sa.String(200), nullable=True),
            sa.Column("mode_defaillance", sa.String(200), nullable=True),
            sa.Column("frequence", sa.Integer, nullable=True),
            sa.Column("date", sa.Date, nullable=True),
            sa.Column("statut", sa.String(200), nullable=True),
            sa.Column("is_active", sa.Boolean, nullable=True),
            sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
            sa.Column("updated_at", sa.DateTime(timezone=True), nullable=True),
            sa.UniqueConstraint("company_id", "reference", name="uix_tech_failure_analyses_uniq"),
        )

    if not _has("tech_spare_requests"):
        op.create_table(
            "tech_spare_requests",
            sa.Column("id", sa.Integer, primary_key=True, index=True),
            sa.Column("company_id", sa.Integer, nullable=False, index=True),
            sa.Column("reference", sa.String(200), nullable=False, index=True),
            sa.Column("piece", sa.String(200), nullable=True),
            sa.Column("quantite", sa.Integer, nullable=True),
            sa.Column("demandeur", sa.String(200), nullable=True),
            sa.Column("date", sa.DateTime(timezone=True), nullable=True),
            sa.Column("statut", sa.String(200), nullable=True),
            sa.Column("is_active", sa.Boolean, nullable=True),
            sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
            sa.Column("updated_at", sa.DateTime(timezone=True), nullable=True),
            sa.UniqueConstraint("company_id", "reference", name="uix_tech_spare_requests_uniq"),
        )

    if not _has("tech_inspection_records"):
        op.create_table(
            "tech_inspection_records",
            sa.Column("id", sa.Integer, primary_key=True, index=True),
            sa.Column("company_id", sa.Integer, nullable=False, index=True),
            sa.Column("reference", sa.String(200), nullable=False, index=True),
            sa.Column("vehicule", sa.String(200), nullable=True),
            sa.Column("type_controle", sa.String(200), nullable=True),
            sa.Column("date_controle", sa.Date, nullable=True),
            sa.Column("validite", sa.Date, nullable=True),
            sa.Column("statut", sa.String(200), nullable=True),
            sa.Column("is_active", sa.Boolean, nullable=True),
            sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
            sa.Column("updated_at", sa.DateTime(timezone=True), nullable=True),
            sa.UniqueConstraint("company_id", "reference", name="uix_tech_inspection_records_uniq"),
        )

    if not _has("tech_work_order_costs"):
        op.create_table(
            "tech_work_order_costs",
            sa.Column("id", sa.Integer, primary_key=True, index=True),
            sa.Column("company_id", sa.Integer, nullable=False, index=True),
            sa.Column("reference", sa.String(200), nullable=False, index=True),
            sa.Column("ordre_travail", sa.String(200), nullable=True),
            sa.Column("cout_pieces", sa.Numeric, nullable=True),
            sa.Column("cout_mo", sa.Numeric, nullable=True),
            sa.Column("date", sa.Date, nullable=True),
            sa.Column("statut", sa.String(200), nullable=True),
            sa.Column("is_active", sa.Boolean, nullable=True),
            sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
            sa.Column("updated_at", sa.DateTime(timezone=True), nullable=True),
            sa.UniqueConstraint("company_id", "reference", name="uix_tech_work_order_costs_uniq"),
        )


def downgrade():
    for t in reversed(TABLES):
        if _has(t):
            op.drop_table(t)
