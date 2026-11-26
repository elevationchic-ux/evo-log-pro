"""097 : tables expansion annuaire-prestataires (genere)."""
from alembic import op
import sqlalchemy as sa


revision = "097_annuaire_d_deep"
down_revision = "096_frais_d_deep"
branch_labels = None
depends_on = None


TABLES = [
    "prov_profiles",
    "prov_categories",
    "prov_certifications",
    "prov_insurance",
    "prov_contracts",
    "prov_evaluations",
    "prov_incidents",
    "prov_availability",
    "prov_price_lists",
    "prov_contacts",
    "prov_onboarding",
    "prov_reviews",
    "prov_rfq",
    "prov_interventions",
    "prov_compliance_docs",
    "prov_bank_details",
    "prov_blacklist",
]


def _has(name):
    insp = sa.inspect(op.get_bind())
    return name in set(insp.get_table_names())


def upgrade():
    if not _has("prov_profiles"):
        op.create_table(
            "prov_profiles",
            sa.Column("id", sa.Integer, primary_key=True, index=True),
            sa.Column("company_id", sa.Integer, nullable=False, index=True),
            sa.Column("reference", sa.String(200), nullable=False, index=True),
            sa.Column("raison_sociale", sa.String(200), nullable=True),
            sa.Column("type_prestation", sa.String(200), nullable=True),
            sa.Column("zone", sa.String(200), nullable=True),
            sa.Column("contact", sa.String(200), nullable=True),
            sa.Column("statut", sa.String(200), nullable=True),
            sa.Column("is_active", sa.Boolean, nullable=True),
            sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
            sa.Column("updated_at", sa.DateTime(timezone=True), nullable=True),
            sa.UniqueConstraint("company_id", "reference", name="uix_prov_profiles_uniq"),
        )

    if not _has("prov_categories"):
        op.create_table(
            "prov_categories",
            sa.Column("id", sa.Integer, primary_key=True, index=True),
            sa.Column("company_id", sa.Integer, nullable=False, index=True),
            sa.Column("reference", sa.String(200), nullable=False, index=True),
            sa.Column("libelle", sa.String(200), nullable=True),
            sa.Column("exigence_documentaire", sa.Boolean, nullable=True),
            sa.Column("nb_prestataires", sa.Integer, nullable=True),
            sa.Column("statut", sa.String(200), nullable=True),
            sa.Column("is_active", sa.Boolean, nullable=True),
            sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
            sa.Column("updated_at", sa.DateTime(timezone=True), nullable=True),
            sa.UniqueConstraint("company_id", "reference", name="uix_prov_categories_uniq"),
        )

    if not _has("prov_certifications"):
        op.create_table(
            "prov_certifications",
            sa.Column("id", sa.Integer, primary_key=True, index=True),
            sa.Column("company_id", sa.Integer, nullable=False, index=True),
            sa.Column("reference", sa.String(200), nullable=False, index=True),
            sa.Column("prestataire", sa.String(200), nullable=True),
            sa.Column("intitule", sa.String(200), nullable=True),
            sa.Column("emetteur", sa.String(200), nullable=True),
            sa.Column("expire_le", sa.Date, nullable=True),
            sa.Column("statut", sa.String(200), nullable=True),
            sa.Column("is_active", sa.Boolean, nullable=True),
            sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
            sa.Column("updated_at", sa.DateTime(timezone=True), nullable=True),
            sa.UniqueConstraint("company_id", "reference", name="uix_prov_certifications_uniq"),
        )

    if not _has("prov_insurance"):
        op.create_table(
            "prov_insurance",
            sa.Column("id", sa.Integer, primary_key=True, index=True),
            sa.Column("company_id", sa.Integer, nullable=False, index=True),
            sa.Column("reference", sa.String(200), nullable=False, index=True),
            sa.Column("prestataire", sa.String(200), nullable=True),
            sa.Column("type_assurance", sa.String(200), nullable=True),
            sa.Column("montant_couvert", sa.Numeric, nullable=True),
            sa.Column("expire_le", sa.Date, nullable=True),
            sa.Column("statut", sa.String(200), nullable=True),
            sa.Column("is_active", sa.Boolean, nullable=True),
            sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
            sa.Column("updated_at", sa.DateTime(timezone=True), nullable=True),
            sa.UniqueConstraint("company_id", "reference", name="uix_prov_insurance_uniq"),
        )

    if not _has("prov_contracts"):
        op.create_table(
            "prov_contracts",
            sa.Column("id", sa.Integer, primary_key=True, index=True),
            sa.Column("company_id", sa.Integer, nullable=False, index=True),
            sa.Column("reference", sa.String(200), nullable=False, index=True),
            sa.Column("prestataire", sa.String(200), nullable=True),
            sa.Column("objet", sa.String(200), nullable=True),
            sa.Column("montant", sa.Numeric, nullable=True),
            sa.Column("echeance", sa.Date, nullable=True),
            sa.Column("statut", sa.String(200), nullable=True),
            sa.Column("is_active", sa.Boolean, nullable=True),
            sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
            sa.Column("updated_at", sa.DateTime(timezone=True), nullable=True),
            sa.UniqueConstraint("company_id", "reference", name="uix_prov_contracts_uniq"),
        )

    if not _has("prov_evaluations"):
        op.create_table(
            "prov_evaluations",
            sa.Column("id", sa.Integer, primary_key=True, index=True),
            sa.Column("company_id", sa.Integer, nullable=False, index=True),
            sa.Column("reference", sa.String(200), nullable=False, index=True),
            sa.Column("prestataire", sa.String(200), nullable=True),
            sa.Column("periode", sa.String(200), nullable=True),
            sa.Column("score", sa.Integer, nullable=True),
            sa.Column("evalueur", sa.String(200), nullable=True),
            sa.Column("statut", sa.String(200), nullable=True),
            sa.Column("is_active", sa.Boolean, nullable=True),
            sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
            sa.Column("updated_at", sa.DateTime(timezone=True), nullable=True),
            sa.UniqueConstraint("company_id", "reference", name="uix_prov_evaluations_uniq"),
        )

    if not _has("prov_incidents"):
        op.create_table(
            "prov_incidents",
            sa.Column("id", sa.Integer, primary_key=True, index=True),
            sa.Column("company_id", sa.Integer, nullable=False, index=True),
            sa.Column("reference", sa.String(200), nullable=False, index=True),
            sa.Column("prestataire", sa.String(200), nullable=True),
            sa.Column("description", sa.Text, nullable=True),
            sa.Column("gravite", sa.String(200), nullable=True),
            sa.Column("date", sa.DateTime(timezone=True), nullable=True),
            sa.Column("statut", sa.String(200), nullable=True),
            sa.Column("is_active", sa.Boolean, nullable=True),
            sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
            sa.Column("updated_at", sa.DateTime(timezone=True), nullable=True),
            sa.UniqueConstraint("company_id", "reference", name="uix_prov_incidents_uniq"),
        )

    if not _has("prov_availability"):
        op.create_table(
            "prov_availability",
            sa.Column("id", sa.Integer, primary_key=True, index=True),
            sa.Column("company_id", sa.Integer, nullable=False, index=True),
            sa.Column("reference", sa.String(200), nullable=False, index=True),
            sa.Column("prestataire", sa.String(200), nullable=True),
            sa.Column("semaine", sa.String(200), nullable=True),
            sa.Column("creneaux_libres", sa.Integer, nullable=True),
            sa.Column("statut", sa.String(200), nullable=True),
            sa.Column("is_active", sa.Boolean, nullable=True),
            sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
            sa.Column("updated_at", sa.DateTime(timezone=True), nullable=True),
            sa.UniqueConstraint("company_id", "reference", name="uix_prov_availability_uniq"),
        )

    if not _has("prov_price_lists"):
        op.create_table(
            "prov_price_lists",
            sa.Column("id", sa.Integer, primary_key=True, index=True),
            sa.Column("company_id", sa.Integer, nullable=False, index=True),
            sa.Column("reference", sa.String(200), nullable=False, index=True),
            sa.Column("prestataire", sa.String(200), nullable=True),
            sa.Column("unite_prix", sa.Numeric, nullable=True),
            sa.Column("validite", sa.Date, nullable=True),
            sa.Column("statut", sa.String(200), nullable=True),
            sa.Column("is_active", sa.Boolean, nullable=True),
            sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
            sa.Column("updated_at", sa.DateTime(timezone=True), nullable=True),
            sa.UniqueConstraint("company_id", "reference", name="uix_prov_price_lists_uniq"),
        )

    if not _has("prov_contacts"):
        op.create_table(
            "prov_contacts",
            sa.Column("id", sa.Integer, primary_key=True, index=True),
            sa.Column("company_id", sa.Integer, nullable=False, index=True),
            sa.Column("reference", sa.String(200), nullable=False, index=True),
            sa.Column("prestataire", sa.String(200), nullable=True),
            sa.Column("nom", sa.String(200), nullable=True),
            sa.Column("role", sa.String(200), nullable=True),
            sa.Column("telephone", sa.String(200), nullable=True),
            sa.Column("statut", sa.String(200), nullable=True),
            sa.Column("is_active", sa.Boolean, nullable=True),
            sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
            sa.Column("updated_at", sa.DateTime(timezone=True), nullable=True),
            sa.UniqueConstraint("company_id", "reference", name="uix_prov_contacts_uniq"),
        )

    if not _has("prov_onboarding"):
        op.create_table(
            "prov_onboarding",
            sa.Column("id", sa.Integer, primary_key=True, index=True),
            sa.Column("company_id", sa.Integer, nullable=False, index=True),
            sa.Column("reference", sa.String(200), nullable=False, index=True),
            sa.Column("prestataire", sa.String(200), nullable=True),
            sa.Column("etapes_faites", sa.Integer, nullable=True),
            sa.Column("etapes_total", sa.Integer, nullable=True),
            sa.Column("date", sa.Date, nullable=True),
            sa.Column("statut", sa.String(200), nullable=True),
            sa.Column("is_active", sa.Boolean, nullable=True),
            sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
            sa.Column("updated_at", sa.DateTime(timezone=True), nullable=True),
            sa.UniqueConstraint("company_id", "reference", name="uix_prov_onboarding_uniq"),
        )

    if not _has("prov_reviews"):
        op.create_table(
            "prov_reviews",
            sa.Column("id", sa.Integer, primary_key=True, index=True),
            sa.Column("company_id", sa.Integer, nullable=False, index=True),
            sa.Column("reference", sa.String(200), nullable=False, index=True),
            sa.Column("prestataire", sa.String(200), nullable=True),
            sa.Column("commentaire", sa.Text, nullable=True),
            sa.Column("nb_etoiles", sa.Integer, nullable=True),
            sa.Column("date", sa.Date, nullable=True),
            sa.Column("statut", sa.String(200), nullable=True),
            sa.Column("is_active", sa.Boolean, nullable=True),
            sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
            sa.Column("updated_at", sa.DateTime(timezone=True), nullable=True),
            sa.UniqueConstraint("company_id", "reference", name="uix_prov_reviews_uniq"),
        )

    if not _has("prov_rfq"):
        op.create_table(
            "prov_rfq",
            sa.Column("id", sa.Integer, primary_key=True, index=True),
            sa.Column("company_id", sa.Integer, nullable=False, index=True),
            sa.Column("reference", sa.String(200), nullable=False, index=True),
            sa.Column("objet", sa.String(200), nullable=True),
            sa.Column("nb_offres", sa.Integer, nullable=True),
            sa.Column("date_limite", sa.Date, nullable=True),
            sa.Column("statut", sa.String(200), nullable=True),
            sa.Column("is_active", sa.Boolean, nullable=True),
            sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
            sa.Column("updated_at", sa.DateTime(timezone=True), nullable=True),
            sa.UniqueConstraint("company_id", "reference", name="uix_prov_rfq_uniq"),
        )

    if not _has("prov_interventions"):
        op.create_table(
            "prov_interventions",
            sa.Column("id", sa.Integer, primary_key=True, index=True),
            sa.Column("company_id", sa.Integer, nullable=False, index=True),
            sa.Column("reference", sa.String(200), nullable=False, index=True),
            sa.Column("prestataire", sa.String(200), nullable=True),
            sa.Column("site", sa.String(200), nullable=True),
            sa.Column("date", sa.DateTime(timezone=True), nullable=True),
            sa.Column("compte_rendu", sa.Text, nullable=True),
            sa.Column("statut", sa.String(200), nullable=True),
            sa.Column("is_active", sa.Boolean, nullable=True),
            sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
            sa.Column("updated_at", sa.DateTime(timezone=True), nullable=True),
            sa.UniqueConstraint("company_id", "reference", name="uix_prov_interventions_uniq"),
        )

    if not _has("prov_compliance_docs"):
        op.create_table(
            "prov_compliance_docs",
            sa.Column("id", sa.Integer, primary_key=True, index=True),
            sa.Column("company_id", sa.Integer, nullable=False, index=True),
            sa.Column("reference", sa.String(200), nullable=False, index=True),
            sa.Column("prestataire", sa.String(200), nullable=True),
            sa.Column("type_piece", sa.String(200), nullable=True),
            sa.Column("expire_le", sa.Date, nullable=True),
            sa.Column("statut", sa.String(200), nullable=True),
            sa.Column("is_active", sa.Boolean, nullable=True),
            sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
            sa.Column("updated_at", sa.DateTime(timezone=True), nullable=True),
            sa.UniqueConstraint("company_id", "reference", name="uix_prov_compliance_docs_uniq"),
        )

    if not _has("prov_bank_details"):
        op.create_table(
            "prov_bank_details",
            sa.Column("id", sa.Integer, primary_key=True, index=True),
            sa.Column("company_id", sa.Integer, nullable=False, index=True),
            sa.Column("reference", sa.String(200), nullable=False, index=True),
            sa.Column("prestataire", sa.String(200), nullable=True),
            sa.Column("banque", sa.String(200), nullable=True),
            sa.Column("iban_verifie", sa.Boolean, nullable=True),
            sa.Column("date", sa.Date, nullable=True),
            sa.Column("statut", sa.String(200), nullable=True),
            sa.Column("is_active", sa.Boolean, nullable=True),
            sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
            sa.Column("updated_at", sa.DateTime(timezone=True), nullable=True),
            sa.UniqueConstraint("company_id", "reference", name="uix_prov_bank_details_uniq"),
        )

    if not _has("prov_blacklist"):
        op.create_table(
            "prov_blacklist",
            sa.Column("id", sa.Integer, primary_key=True, index=True),
            sa.Column("company_id", sa.Integer, nullable=False, index=True),
            sa.Column("reference", sa.String(200), nullable=False, index=True),
            sa.Column("prestataire", sa.String(200), nullable=True),
            sa.Column("motif", sa.Text, nullable=True),
            sa.Column("debut", sa.Date, nullable=True),
            sa.Column("fin_prevue", sa.Date, nullable=True),
            sa.Column("statut", sa.String(200), nullable=True),
            sa.Column("is_active", sa.Boolean, nullable=True),
            sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
            sa.Column("updated_at", sa.DateTime(timezone=True), nullable=True),
            sa.UniqueConstraint("company_id", "reference", name="uix_prov_blacklist_uniq"),
        )


def downgrade():
    for t in reversed(TABLES):
        if _has(t):
            op.drop_table(t)
