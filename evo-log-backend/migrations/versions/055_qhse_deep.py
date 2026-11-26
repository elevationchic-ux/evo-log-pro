"""055 : tables expansion qhse-securite (genere)."""
from alembic import op
import sqlalchemy as sa


revision = "055_qhse_deep"
down_revision = "054_rh_deep"
branch_labels = None
depends_on = None


TABLES = [
    "environmental_measurements",
    "waste_records",
    "safety_data_sheets",
    "emergency_plans",
    "ppe_items",
    "health_visits",
    "risk_assessments",
    "corrective_actions",
    "management_reviews",
    "compliance_records",
    "quality_audits",
]


def _has(name):
    insp = sa.inspect(op.get_bind())
    return name in set(insp.get_table_names())


def upgrade():
    if not _has("environmental_measurements"):
        op.create_table(
            "environmental_measurements",
            sa.Column("id", sa.Integer, primary_key=True, index=True),
            sa.Column("company_id", sa.Integer, nullable=False, index=True),
            sa.Column("reference", sa.String(200), nullable=False, index=True),
            sa.Column("type_relevé", sa.String(50), nullable=True),
            sa.Column("polluant", sa.String(200), nullable=True),
            sa.Column("valeur", sa.Numeric, nullable=True),
            sa.Column("unite", sa.String(200), nullable=True),
            sa.Column("norme_max", sa.Numeric, nullable=True),
            sa.Column("station", sa.String(200), nullable=True),
            sa.Column("date_relevé", sa.DateTime(timezone=True), nullable=True),
            sa.Column("conformite", sa.String(50), nullable=True),
            sa.Column("is_active", sa.Boolean, nullable=True),
            sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
            sa.Column("updated_at", sa.DateTime(timezone=True), nullable=True),
            sa.UniqueConstraint("company_id", "reference", name="uix_environmental_measurements_uniq"),
        )

    if not _has("waste_records"):
        op.create_table(
            "waste_records",
            sa.Column("id", sa.Integer, primary_key=True, index=True),
            sa.Column("company_id", sa.Integer, nullable=False, index=True),
            sa.Column("numero_bsd", sa.String(200), nullable=False, index=True),
            sa.Column("type_dechet", sa.String(50), nullable=True),
            sa.Column("quantite_kg", sa.Numeric, nullable=True),
            sa.Column("date_production", sa.Date, nullable=True),
            sa.Column("transporteur", sa.String(200), nullable=True),
            sa.Column("destination", sa.String(200), nullable=True),
            sa.Column("statut", sa.String(50), nullable=True),
            sa.Column("is_active", sa.Boolean, nullable=True),
            sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
            sa.Column("updated_at", sa.DateTime(timezone=True), nullable=True),
            sa.UniqueConstraint("company_id", "numero_bsd", name="uix_waste_records_uniq"),
        )

    if not _has("safety_data_sheets"):
        op.create_table(
            "safety_data_sheets",
            sa.Column("id", sa.Integer, primary_key=True, index=True),
            sa.Column("company_id", sa.Integer, nullable=False, index=True),
            sa.Column("reference", sa.String(200), nullable=False, index=True),
            sa.Column("nom_produit", sa.String(200), nullable=True),
            sa.Column("numero_ce", sa.String(200), nullable=True),
            sa.Column("fournisseur", sa.String(200), nullable=True),
            sa.Column("phrase_risque", sa.Text, nullable=True),
            sa.Column("version_fds", sa.String(200), nullable=True),
            sa.Column("date_revision", sa.Date, nullable=True),
            sa.Column("classification", sa.String(50), nullable=True),
            sa.Column("is_active", sa.Boolean, nullable=True),
            sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
            sa.Column("updated_at", sa.DateTime(timezone=True), nullable=True),
            sa.UniqueConstraint("company_id", "reference", name="uix_safety_data_sheets_uniq"),
        )

    if not _has("emergency_plans"):
        op.create_table(
            "emergency_plans",
            sa.Column("id", sa.Integer, primary_key=True, index=True),
            sa.Column("company_id", sa.Integer, nullable=False, index=True),
            sa.Column("reference", sa.String(200), nullable=False, index=True),
            sa.Column("type_plan", sa.String(50), nullable=True),
            sa.Column("zone_concernee", sa.String(200), nullable=True),
            sa.Column("date_elaboration", sa.Date, nullable=True),
            sa.Column("date_dernier_exercice", sa.Date, nullable=True),
            sa.Column("frequence_exercice_mois", sa.Integer, nullable=True),
            sa.Column("is_active", sa.Boolean, nullable=True),
            sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
            sa.Column("updated_at", sa.DateTime(timezone=True), nullable=True),
            sa.UniqueConstraint("company_id", "reference", name="uix_emergency_plans_uniq"),
        )

    if not _has("ppe_items"):
        op.create_table(
            "ppe_items",
            sa.Column("id", sa.Integer, primary_key=True, index=True),
            sa.Column("company_id", sa.Integer, nullable=False, index=True),
            sa.Column("reference", sa.String(200), nullable=False, index=True),
            sa.Column("employe_id", sa.Integer, nullable=True),
            sa.Column("type_epi", sa.String(50), nullable=True),
            sa.Column("taille", sa.String(200), nullable=True),
            sa.Column("date_attribution", sa.Date, nullable=True),
            sa.Column("date_expiration", sa.Date, nullable=True),
            sa.Column("quantite", sa.Integer, nullable=True),
            sa.Column("statut", sa.String(50), nullable=True),
            sa.Column("is_active", sa.Boolean, nullable=True),
            sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
            sa.Column("updated_at", sa.DateTime(timezone=True), nullable=True),
            sa.UniqueConstraint("company_id", "reference", name="uix_ppe_items_uniq"),
        )

    if not _has("health_visits"):
        op.create_table(
            "health_visits",
            sa.Column("id", sa.Integer, primary_key=True, index=True),
            sa.Column("company_id", sa.Integer, nullable=False, index=True),
            sa.Column("reference", sa.String(200), nullable=False, index=True),
            sa.Column("employe_id", sa.Integer, nullable=True),
            sa.Column("type_visite", sa.String(50), nullable=True),
            sa.Column("date_visite", sa.Date, nullable=True),
            sa.Column("medecin", sa.String(200), nullable=True),
            sa.Column("resultat", sa.String(50), nullable=True),
            sa.Column("prochaine_visite", sa.Date, nullable=True),
            sa.Column("is_active", sa.Boolean, nullable=True),
            sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
            sa.Column("updated_at", sa.DateTime(timezone=True), nullable=True),
            sa.UniqueConstraint("company_id", "reference", name="uix_health_visits_uniq"),
        )

    if not _has("risk_assessments"):
        op.create_table(
            "risk_assessments",
            sa.Column("id", sa.Integer, primary_key=True, index=True),
            sa.Column("company_id", sa.Integer, nullable=False, index=True),
            sa.Column("reference", sa.String(200), nullable=False, index=True),
            sa.Column("unite_travail", sa.String(200), nullable=True),
            sa.Column("description_risque", sa.Text, nullable=True),
            sa.Column("cotation", sa.String(50), nullable=True),
            sa.Column("mesure_prevention", sa.Text, nullable=True),
            sa.Column("date_evaluation", sa.Date, nullable=True),
            sa.Column("responsable", sa.String(200), nullable=True),
            sa.Column("is_active", sa.Boolean, nullable=True),
            sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
            sa.Column("updated_at", sa.DateTime(timezone=True), nullable=True),
            sa.UniqueConstraint("company_id", "reference", name="uix_risk_assessments_uniq"),
        )

    if not _has("corrective_actions"):
        op.create_table(
            "corrective_actions",
            sa.Column("id", sa.Integer, primary_key=True, index=True),
            sa.Column("company_id", sa.Integer, nullable=False, index=True),
            sa.Column("reference", sa.String(200), nullable=False, index=True),
            sa.Column("source_ecart", sa.String(200), nullable=True),
            sa.Column("description_probleme", sa.Text, nullable=True),
            sa.Column("cause_racine", sa.Text, nullable=True),
            sa.Column("action_corrective", sa.Text, nullable=True),
            sa.Column("responsable", sa.String(200), nullable=True),
            sa.Column("date_prevue_cloture", sa.Date, nullable=True),
            sa.Column("statut", sa.String(50), nullable=True),
            sa.Column("is_active", sa.Boolean, nullable=True),
            sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
            sa.Column("updated_at", sa.DateTime(timezone=True), nullable=True),
            sa.UniqueConstraint("company_id", "reference", name="uix_corrective_actions_uniq"),
        )

    if not _has("management_reviews"):
        op.create_table(
            "management_reviews",
            sa.Column("id", sa.Integer, primary_key=True, index=True),
            sa.Column("company_id", sa.Integer, nullable=False, index=True),
            sa.Column("reference", sa.String(200), nullable=False, index=True),
            sa.Column("date_revue", sa.Date, nullable=True),
            sa.Column("participants", sa.Text, nullable=True),
            sa.Column("sujets", sa.Text, nullable=True),
            sa.Column("decisions", sa.Text, nullable=True),
            sa.Column("statut", sa.String(50), nullable=True),
            sa.Column("is_active", sa.Boolean, nullable=True),
            sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
            sa.Column("updated_at", sa.DateTime(timezone=True), nullable=True),
            sa.UniqueConstraint("company_id", "reference", name="uix_management_reviews_uniq"),
        )

    if not _has("compliance_records"):
        op.create_table(
            "compliance_records",
            sa.Column("id", sa.Integer, primary_key=True, index=True),
            sa.Column("company_id", sa.Integer, nullable=False, index=True),
            sa.Column("reference", sa.String(200), nullable=False, index=True),
            sa.Column("regulation", sa.String(200), nullable=True),
            sa.Column("domaine", sa.String(50), nullable=True),
            sa.Column("obligation", sa.Text, nullable=True),
            sa.Column("preuve", sa.Text, nullable=True),
            sa.Column("date_constat", sa.Date, nullable=True),
            sa.Column("prochaine_echeance", sa.Date, nullable=True),
            sa.Column("statut", sa.String(50), nullable=True),
            sa.Column("is_active", sa.Boolean, nullable=True),
            sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
            sa.Column("updated_at", sa.DateTime(timezone=True), nullable=True),
            sa.UniqueConstraint("company_id", "reference", name="uix_compliance_records_uniq"),
        )

    if not _has("quality_audits"):
        op.create_table(
            "quality_audits",
            sa.Column("id", sa.Integer, primary_key=True, index=True),
            sa.Column("company_id", sa.Integer, nullable=False, index=True),
            sa.Column("reference", sa.String(200), nullable=False, index=True),
            sa.Column("type_audit", sa.String(50), nullable=True),
            sa.Column("perimetre", sa.String(200), nullable=True),
            sa.Column("auditeur", sa.String(200), nullable=True),
            sa.Column("date_debut", sa.Date, nullable=True),
            sa.Column("date_fin", sa.Date, nullable=True),
            sa.Column("nb_ecarts", sa.Integer, nullable=True),
            sa.Column("statut", sa.String(50), nullable=True),
            sa.Column("is_active", sa.Boolean, nullable=True),
            sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
            sa.Column("updated_at", sa.DateTime(timezone=True), nullable=True),
            sa.UniqueConstraint("company_id", "reference", name="uix_quality_audits_uniq"),
        )


def downgrade():
    for t in reversed(TABLES):
        if _has(t):
            op.drop_table(t)
