"""091 : tables expansion portail-declarant (genere)."""
from alembic import op
import sqlalchemy as sa


revision = "091_declarant_d_deep"
down_revision = "090_qhse_portal_d_deep"
branch_labels = None
depends_on = None


TABLES = [
    "decl_customs_declarations",
    "decl_hs_classifications",
    "decl_origin_certificates",
    "decl_customs_valuations",
    "decl_incoterms",
    "decl_import_licenses",
    "decl_export_licenses",
    "decl_pre_clearances",
    "decl_customs_invoices",
    "decl_packing_lists",
    "decl_coa",
    "decl_phyto_apps",
    "decl_customs_payments",
    "decl_transit_documents",
    "decl_dg_declarations",
    "decl_bonded_entries",
    "decl_duty_relief",
    "decl_manifest_corrections",
    "decl_audit_support",
]


def _has(name):
    insp = sa.inspect(op.get_bind())
    return name in set(insp.get_table_names())


def upgrade():
    if not _has("decl_customs_declarations"):
        op.create_table(
            "decl_customs_declarations",
            sa.Column("id", sa.Integer, primary_key=True, index=True),
            sa.Column("company_id", sa.Integer, nullable=False, index=True),
            sa.Column("reference", sa.String(200), nullable=False, index=True),
            sa.Column("masse", sa.String(200), nullable=True),
            sa.Column("regime", sa.String(200), nullable=True),
            sa.Column("valeur_douane", sa.Numeric, nullable=True),
            sa.Column("date_depot", sa.DateTime(timezone=True), nullable=True),
            sa.Column("statut", sa.String(200), nullable=True),
            sa.Column("is_active", sa.Boolean, nullable=True),
            sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
            sa.Column("updated_at", sa.DateTime(timezone=True), nullable=True),
            sa.UniqueConstraint("company_id", "reference", name="uix_decl_customs_declarations_uniq"),
        )

    if not _has("decl_hs_classifications"):
        op.create_table(
            "decl_hs_classifications",
            sa.Column("id", sa.Integer, primary_key=True, index=True),
            sa.Column("company_id", sa.Integer, nullable=False, index=True),
            sa.Column("reference", sa.String(200), nullable=False, index=True),
            sa.Column("designation", sa.String(200), nullable=True),
            sa.Column("code_hs", sa.String(200), nullable=True),
            sa.Column("taux_droit", sa.Numeric, nullable=True),
            sa.Column("date", sa.Date, nullable=True),
            sa.Column("statut", sa.String(200), nullable=True),
            sa.Column("is_active", sa.Boolean, nullable=True),
            sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
            sa.Column("updated_at", sa.DateTime(timezone=True), nullable=True),
            sa.UniqueConstraint("company_id", "reference", name="uix_decl_hs_classifications_uniq"),
        )

    if not _has("decl_origin_certificates"):
        op.create_table(
            "decl_origin_certificates",
            sa.Column("id", sa.Integer, primary_key=True, index=True),
            sa.Column("company_id", sa.Integer, nullable=False, index=True),
            sa.Column("reference", sa.String(200), nullable=False, index=True),
            sa.Column("type", sa.String(200), nullable=True),
            sa.Column("pays_origine", sa.String(200), nullable=True),
            sa.Column("numero", sa.String(200), nullable=True),
            sa.Column("date_emission", sa.Date, nullable=True),
            sa.Column("statut", sa.String(200), nullable=True),
            sa.Column("is_active", sa.Boolean, nullable=True),
            sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
            sa.Column("updated_at", sa.DateTime(timezone=True), nullable=True),
            sa.UniqueConstraint("company_id", "reference", name="uix_decl_origin_certificates_uniq"),
        )

    if not _has("decl_customs_valuations"):
        op.create_table(
            "decl_customs_valuations",
            sa.Column("id", sa.Integer, primary_key=True, index=True),
            sa.Column("company_id", sa.Integer, nullable=False, index=True),
            sa.Column("reference", sa.String(200), nullable=False, index=True),
            sa.Column("masse", sa.String(200), nullable=True),
            sa.Column("methode", sa.String(200), nullable=True),
            sa.Column("valeur", sa.Numeric, nullable=True),
            sa.Column("date", sa.Date, nullable=True),
            sa.Column("statut", sa.String(200), nullable=True),
            sa.Column("is_active", sa.Boolean, nullable=True),
            sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
            sa.Column("updated_at", sa.DateTime(timezone=True), nullable=True),
            sa.UniqueConstraint("company_id", "reference", name="uix_decl_customs_valuations_uniq"),
        )

    if not _has("decl_incoterms"):
        op.create_table(
            "decl_incoterms",
            sa.Column("id", sa.Integer, primary_key=True, index=True),
            sa.Column("company_id", sa.Integer, nullable=False, index=True),
            sa.Column("reference", sa.String(200), nullable=False, index=True),
            sa.Column("code", sa.String(200), nullable=True),
            sa.Column("lieu", sa.String(200), nullable=True),
            sa.Column("vendeur", sa.String(200), nullable=True),
            sa.Column("acheteur", sa.String(200), nullable=True),
            sa.Column("statut", sa.String(200), nullable=True),
            sa.Column("is_active", sa.Boolean, nullable=True),
            sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
            sa.Column("updated_at", sa.DateTime(timezone=True), nullable=True),
            sa.UniqueConstraint("company_id", "reference", name="uix_decl_incoterms_uniq"),
        )

    if not _has("decl_import_licenses"):
        op.create_table(
            "decl_import_licenses",
            sa.Column("id", sa.Integer, primary_key=True, index=True),
            sa.Column("company_id", sa.Integer, nullable=False, index=True),
            sa.Column("reference", sa.String(200), nullable=False, index=True),
            sa.Column("produit", sa.String(200), nullable=True),
            sa.Column("quota", sa.Integer, nullable=True),
            sa.Column("utilisable", sa.Integer, nullable=True),
            sa.Column("validite", sa.Date, nullable=True),
            sa.Column("statut", sa.String(200), nullable=True),
            sa.Column("is_active", sa.Boolean, nullable=True),
            sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
            sa.Column("updated_at", sa.DateTime(timezone=True), nullable=True),
            sa.UniqueConstraint("company_id", "reference", name="uix_decl_import_licenses_uniq"),
        )

    if not _has("decl_export_licenses"):
        op.create_table(
            "decl_export_licenses",
            sa.Column("id", sa.Integer, primary_key=True, index=True),
            sa.Column("company_id", sa.Integer, nullable=False, index=True),
            sa.Column("reference", sa.String(200), nullable=False, index=True),
            sa.Column("bien", sa.String(200), nullable=True),
            sa.Column("destination", sa.String(200), nullable=True),
            sa.Column("usage", sa.String(200), nullable=True),
            sa.Column("validite", sa.Date, nullable=True),
            sa.Column("statut", sa.String(200), nullable=True),
            sa.Column("is_active", sa.Boolean, nullable=True),
            sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
            sa.Column("updated_at", sa.DateTime(timezone=True), nullable=True),
            sa.UniqueConstraint("company_id", "reference", name="uix_decl_export_licenses_uniq"),
        )

    if not _has("decl_pre_clearances"):
        op.create_table(
            "decl_pre_clearances",
            sa.Column("id", sa.Integer, primary_key=True, index=True),
            sa.Column("company_id", sa.Integer, nullable=False, index=True),
            sa.Column("reference", sa.String(200), nullable=False, index=True),
            sa.Column("masse", sa.String(200), nullable=True),
            sa.Column("arrivee_prevue", sa.DateTime(timezone=True), nullable=True),
            sa.Column("depot", sa.DateTime(timezone=True), nullable=True),
            sa.Column("statut", sa.String(200), nullable=True),
            sa.Column("is_active", sa.Boolean, nullable=True),
            sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
            sa.Column("updated_at", sa.DateTime(timezone=True), nullable=True),
            sa.UniqueConstraint("company_id", "reference", name="uix_decl_pre_clearances_uniq"),
        )

    if not _has("decl_customs_invoices"):
        op.create_table(
            "decl_customs_invoices",
            sa.Column("id", sa.Integer, primary_key=True, index=True),
            sa.Column("company_id", sa.Integer, nullable=False, index=True),
            sa.Column("reference", sa.String(200), nullable=False, index=True),
            sa.Column("fournisseur", sa.String(200), nullable=True),
            sa.Column("montant", sa.Numeric, nullable=True),
            sa.Column("devise", sa.String(200), nullable=True),
            sa.Column("date", sa.Date, nullable=True),
            sa.Column("statut", sa.String(200), nullable=True),
            sa.Column("is_active", sa.Boolean, nullable=True),
            sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
            sa.Column("updated_at", sa.DateTime(timezone=True), nullable=True),
            sa.UniqueConstraint("company_id", "reference", name="uix_decl_customs_invoices_uniq"),
        )

    if not _has("decl_packing_lists"):
        op.create_table(
            "decl_packing_lists",
            sa.Column("id", sa.Integer, primary_key=True, index=True),
            sa.Column("company_id", sa.Integer, nullable=False, index=True),
            sa.Column("reference", sa.String(200), nullable=False, index=True),
            sa.Column("masse", sa.String(200), nullable=True),
            sa.Column("nb_colis", sa.Integer, nullable=True),
            sa.Column("poids_net", sa.Numeric, nullable=True),
            sa.Column("statut", sa.String(200), nullable=True),
            sa.Column("is_active", sa.Boolean, nullable=True),
            sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
            sa.Column("updated_at", sa.DateTime(timezone=True), nullable=True),
            sa.UniqueConstraint("company_id", "reference", name="uix_decl_packing_lists_uniq"),
        )

    if not _has("decl_coa"):
        op.create_table(
            "decl_coa",
            sa.Column("id", sa.Integer, primary_key=True, index=True),
            sa.Column("company_id", sa.Integer, nullable=False, index=True),
            sa.Column("reference", sa.String(200), nullable=False, index=True),
            sa.Column("produit", sa.String(200), nullable=True),
            sa.Column("laboratoire", sa.String(200), nullable=True),
            sa.Column("parametres", sa.Text, nullable=True),
            sa.Column("date", sa.Date, nullable=True),
            sa.Column("statut", sa.String(200), nullable=True),
            sa.Column("is_active", sa.Boolean, nullable=True),
            sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
            sa.Column("updated_at", sa.DateTime(timezone=True), nullable=True),
            sa.UniqueConstraint("company_id", "reference", name="uix_decl_coa_uniq"),
        )

    if not _has("decl_phyto_apps"):
        op.create_table(
            "decl_phyto_apps",
            sa.Column("id", sa.Integer, primary_key=True, index=True),
            sa.Column("company_id", sa.Integer, nullable=False, index=True),
            sa.Column("reference", sa.String(200), nullable=False, index=True),
            sa.Column("produit", sa.String(200), nullable=True),
            sa.Column("destination", sa.String(200), nullable=True),
            sa.Column("date_controle", sa.Date, nullable=True),
            sa.Column("statut", sa.String(200), nullable=True),
            sa.Column("is_active", sa.Boolean, nullable=True),
            sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
            sa.Column("updated_at", sa.DateTime(timezone=True), nullable=True),
            sa.UniqueConstraint("company_id", "reference", name="uix_decl_phyto_apps_uniq"),
        )

    if not _has("decl_customs_payments"):
        op.create_table(
            "decl_customs_payments",
            sa.Column("id", sa.Integer, primary_key=True, index=True),
            sa.Column("company_id", sa.Integer, nullable=False, index=True),
            sa.Column("reference", sa.String(200), nullable=False, index=True),
            sa.Column("declaration", sa.String(200), nullable=True),
            sa.Column("montant", sa.Numeric, nullable=True),
            sa.Column("type_droit", sa.String(200), nullable=True),
            sa.Column("date", sa.DateTime(timezone=True), nullable=True),
            sa.Column("statut", sa.String(200), nullable=True),
            sa.Column("is_active", sa.Boolean, nullable=True),
            sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
            sa.Column("updated_at", sa.DateTime(timezone=True), nullable=True),
            sa.UniqueConstraint("company_id", "reference", name="uix_decl_customs_payments_uniq"),
        )

    if not _has("decl_transit_documents"):
        op.create_table(
            "decl_transit_documents",
            sa.Column("id", sa.Integer, primary_key=True, index=True),
            sa.Column("company_id", sa.Integer, nullable=False, index=True),
            sa.Column("reference", sa.String(200), nullable=False, index=True),
            sa.Column("type", sa.String(200), nullable=True),
            sa.Column("bureau_depart", sa.String(200), nullable=True),
            sa.Column("bureau_arrivee", sa.String(200), nullable=True),
            sa.Column("garantie", sa.Numeric, nullable=True),
            sa.Column("statut", sa.String(200), nullable=True),
            sa.Column("is_active", sa.Boolean, nullable=True),
            sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
            sa.Column("updated_at", sa.DateTime(timezone=True), nullable=True),
            sa.UniqueConstraint("company_id", "reference", name="uix_decl_transit_documents_uniq"),
        )

    if not _has("decl_dg_declarations"):
        op.create_table(
            "decl_dg_declarations",
            sa.Column("id", sa.Integer, primary_key=True, index=True),
            sa.Column("company_id", sa.Integer, nullable=False, index=True),
            sa.Column("reference", sa.String(200), nullable=False, index=True),
            sa.Column("numero_onu", sa.String(200), nullable=True),
            sa.Column("classe", sa.String(200), nullable=True),
            sa.Column("quantite", sa.Numeric, nullable=True),
            sa.Column("date", sa.DateTime(timezone=True), nullable=True),
            sa.Column("statut", sa.String(200), nullable=True),
            sa.Column("is_active", sa.Boolean, nullable=True),
            sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
            sa.Column("updated_at", sa.DateTime(timezone=True), nullable=True),
            sa.UniqueConstraint("company_id", "reference", name="uix_decl_dg_declarations_uniq"),
        )

    if not _has("decl_bonded_entries"):
        op.create_table(
            "decl_bonded_entries",
            sa.Column("id", sa.Integer, primary_key=True, index=True),
            sa.Column("company_id", sa.Integer, nullable=False, index=True),
            sa.Column("reference", sa.String(200), nullable=False, index=True),
            sa.Column("entrepot", sa.String(200), nullable=True),
            sa.Column("masse", sa.String(200), nullable=True),
            sa.Column("entree", sa.DateTime(timezone=True), nullable=True),
            sa.Column("sortie_prevue", sa.DateTime(timezone=True), nullable=True),
            sa.Column("statut", sa.String(200), nullable=True),
            sa.Column("is_active", sa.Boolean, nullable=True),
            sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
            sa.Column("updated_at", sa.DateTime(timezone=True), nullable=True),
            sa.UniqueConstraint("company_id", "reference", name="uix_decl_bonded_entries_uniq"),
        )

    if not _has("decl_duty_relief"):
        op.create_table(
            "decl_duty_relief",
            sa.Column("id", sa.Integer, primary_key=True, index=True),
            sa.Column("company_id", sa.Integer, nullable=False, index=True),
            sa.Column("reference", sa.String(200), nullable=False, index=True),
            sa.Column("motif", sa.String(200), nullable=True),
            sa.Column("declaration", sa.String(200), nullable=True),
            sa.Column("montant_exonere", sa.Numeric, nullable=True),
            sa.Column("statut", sa.String(200), nullable=True),
            sa.Column("is_active", sa.Boolean, nullable=True),
            sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
            sa.Column("updated_at", sa.DateTime(timezone=True), nullable=True),
            sa.UniqueConstraint("company_id", "reference", name="uix_decl_duty_relief_uniq"),
        )

    if not _has("decl_manifest_corrections"):
        op.create_table(
            "decl_manifest_corrections",
            sa.Column("id", sa.Integer, primary_key=True, index=True),
            sa.Column("company_id", sa.Integer, nullable=False, index=True),
            sa.Column("reference", sa.String(200), nullable=False, index=True),
            sa.Column("manifeste", sa.String(200), nullable=True),
            sa.Column("objet_rectification", sa.Text, nullable=True),
            sa.Column("date", sa.DateTime(timezone=True), nullable=True),
            sa.Column("statut", sa.String(200), nullable=True),
            sa.Column("is_active", sa.Boolean, nullable=True),
            sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
            sa.Column("updated_at", sa.DateTime(timezone=True), nullable=True),
            sa.UniqueConstraint("company_id", "reference", name="uix_decl_manifest_corrections_uniq"),
        )

    if not _has("decl_audit_support"):
        op.create_table(
            "decl_audit_support",
            sa.Column("id", sa.Integer, primary_key=True, index=True),
            sa.Column("company_id", sa.Integer, nullable=False, index=True),
            sa.Column("reference", sa.String(200), nullable=False, index=True),
            sa.Column("controle", sa.String(200), nullable=True),
            sa.Column("periode", sa.String(200), nullable=True),
            sa.Column("pieces_fournies", sa.Integer, nullable=True),
            sa.Column("date", sa.Date, nullable=True),
            sa.Column("statut", sa.String(200), nullable=True),
            sa.Column("is_active", sa.Boolean, nullable=True),
            sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
            sa.Column("updated_at", sa.DateTime(timezone=True), nullable=True),
            sa.UniqueConstraint("company_id", "reference", name="uix_decl_audit_support_uniq"),
        )


def downgrade():
    for t in reversed(TABLES):
        if _has(t):
            op.drop_table(t)
