"""048 : tables expansion transit-douane (genere)."""
from alembic import op
import sqlalchemy as sa


revision = "048_transit_deep"
down_revision = "047_port_ops_deep"
branch_labels = None
depends_on = None


TABLES = [
    "hs_classifications",
    "customs_valuations",
    "origin_certificates",
    "bonded_warehouses",
    "transit_guarantees",
    "export_declarations",
    "prohibited_goods",
    "customs_regimes",
    "physical_inspections",
    "duty_payments",
    "trader_registrations",
    "tariff_references",
]


def _has(name):
    insp = sa.inspect(op.get_bind())
    return name in set(insp.get_table_names())


def upgrade():
    if not _has("hs_classifications"):
        op.create_table(
            "hs_classifications",
            sa.Column("id", sa.Integer, primary_key=True, index=True),
            sa.Column("company_id", sa.Integer, nullable=False, index=True),
            sa.Column("code_hs", sa.String(200), nullable=False, index=True),
            sa.Column("designation", sa.Text, nullable=True),
            sa.Column("section", sa.String(200), nullable=True),
            sa.Column("chapitre", sa.String(200), nullable=True),
            sa.Column("position", sa.String(200), nullable=True),
            sa.Column("sous_position", sa.String(200), nullable=True),
            sa.Column("unite_mesure", sa.String(200), nullable=True),
            sa.Column("statut", sa.String(50), nullable=True),
            sa.Column("is_active", sa.Boolean, nullable=True),
            sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
            sa.Column("updated_at", sa.DateTime(timezone=True), nullable=True),
            sa.UniqueConstraint("company_id", "code_hs", name="uix_hs_classifications_uniq"),
        )

    if not _has("customs_valuations"):
        op.create_table(
            "customs_valuations",
            sa.Column("id", sa.Integer, primary_key=True, index=True),
            sa.Column("company_id", sa.Integer, nullable=False, index=True),
            sa.Column("reference_dossier", sa.String(200), nullable=False, index=True),
            sa.Column("dum_id", sa.Integer, nullable=True),
            sa.Column("methode_evaluation", sa.String(50), nullable=True),
            sa.Column("incoterm", sa.String(200), nullable=True),
            sa.Column("valeur_declaree_xaf", sa.Numeric, nullable=True),
            sa.Column("valeur_transport_xaf", sa.Numeric, nullable=True),
            sa.Column("valeur_assurance_xaf", sa.Numeric, nullable=True),
            sa.Column("valeur_douane_xaf", sa.Numeric, nullable=True),
            sa.Column("taux_change", sa.Numeric, nullable=True),
            sa.Column("date_evaluation", sa.Date, nullable=True),
            sa.Column("justification", sa.Text, nullable=True),
            sa.Column("statut", sa.String(50), nullable=True),
            sa.Column("notes", sa.Text, nullable=True),
            sa.Column("is_active", sa.Boolean, nullable=True),
            sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
            sa.Column("updated_at", sa.DateTime(timezone=True), nullable=True),
            sa.UniqueConstraint("company_id", "reference_dossier", name="uix_customs_valuations_uniq"),
        )

    if not _has("origin_certificates"):
        op.create_table(
            "origin_certificates",
            sa.Column("id", sa.Integer, primary_key=True, index=True),
            sa.Column("company_id", sa.Integer, nullable=False, index=True),
            sa.Column("numero_certificat", sa.String(200), nullable=False, index=True),
            sa.Column("type_certificat", sa.String(50), nullable=True),
            sa.Column("pays_origine", sa.String(200), nullable=True),
            sa.Column("exportateur", sa.String(200), nullable=True),
            sa.Column("importateur", sa.String(200), nullable=True),
            sa.Column("dum_id", sa.Integer, nullable=True),
            sa.Column("date_emission", sa.Date, nullable=True),
            sa.Column("date_expiration", sa.Date, nullable=True),
            sa.Column("chambre_delivrance", sa.String(200), nullable=True),
            sa.Column("statut", sa.String(50), nullable=True),
            sa.Column("notes", sa.Text, nullable=True),
            sa.Column("is_active", sa.Boolean, nullable=True),
            sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
            sa.Column("updated_at", sa.DateTime(timezone=True), nullable=True),
            sa.UniqueConstraint("company_id", "numero_certificat", name="uix_origin_certificates_uniq"),
        )

    if not _has("bonded_warehouses"):
        op.create_table(
            "bonded_warehouses",
            sa.Column("id", sa.Integer, primary_key=True, index=True),
            sa.Column("company_id", sa.Integer, nullable=False, index=True),
            sa.Column("code_entrepot", sa.String(200), nullable=False, index=True),
            sa.Column("nom", sa.String(200), nullable=True),
            sa.Column("agrement_numero", sa.String(200), nullable=True),
            sa.Column("date_debut_agrement", sa.Date, nullable=True),
            sa.Column("date_fin_agrement", sa.Date, nullable=True),
            sa.Column("capacite_m2", sa.Numeric, nullable=True),
            sa.Column("localisation", sa.String(200), nullable=True),
            sa.Column("gestionnaire", sa.String(200), nullable=True),
            sa.Column("statut", sa.String(50), nullable=True),
            sa.Column("notes", sa.Text, nullable=True),
            sa.Column("is_active", sa.Boolean, nullable=True),
            sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
            sa.Column("updated_at", sa.DateTime(timezone=True), nullable=True),
            sa.UniqueConstraint("company_id", "code_entrepot", name="uix_bonded_warehouses_uniq"),
        )

    if not _has("transit_guarantees"):
        op.create_table(
            "transit_guarantees",
            sa.Column("id", sa.Integer, primary_key=True, index=True),
            sa.Column("company_id", sa.Integer, nullable=False, index=True),
            sa.Column("reference_caution", sa.String(200), nullable=False, index=True),
            sa.Column("type_garantie", sa.String(50), nullable=True),
            sa.Column("banque_emettrice", sa.String(200), nullable=True),
            sa.Column("donneur_ordre", sa.String(200), nullable=True),
            sa.Column("montant_caution_xaf", sa.Numeric, nullable=True),
            sa.Column("date_debut", sa.Date, nullable=True),
            sa.Column("date_fin", sa.Date, nullable=True),
            sa.Column("statut", sa.String(50), nullable=True),
            sa.Column("notes", sa.Text, nullable=True),
            sa.Column("is_active", sa.Boolean, nullable=True),
            sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
            sa.Column("updated_at", sa.DateTime(timezone=True), nullable=True),
            sa.UniqueConstraint("company_id", "reference_caution", name="uix_transit_guarantees_uniq"),
        )

    if not _has("export_declarations"):
        op.create_table(
            "export_declarations",
            sa.Column("id", sa.Integer, primary_key=True, index=True),
            sa.Column("company_id", sa.Integer, nullable=False, index=True),
            sa.Column("numero_dge", sa.String(200), nullable=False, index=True),
            sa.Column("declarant", sa.String(200), nullable=True),
            sa.Column("exportateur", sa.String(200), nullable=True),
            sa.Column("pays_destination", sa.String(200), nullable=True),
            sa.Column("valeur_xaf", sa.Numeric, nullable=True),
            sa.Column("poids_net_kg", sa.Numeric, nullable=True),
            sa.Column("regime", sa.String(50), nullable=True),
            sa.Column("date_depot", sa.Date, nullable=True),
            sa.Column("date_validation", sa.Date, nullable=True),
            sa.Column("statut", sa.String(50), nullable=True),
            sa.Column("notes", sa.Text, nullable=True),
            sa.Column("is_active", sa.Boolean, nullable=True),
            sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
            sa.Column("updated_at", sa.DateTime(timezone=True), nullable=True),
            sa.UniqueConstraint("company_id", "numero_dge", name="uix_export_declarations_uniq"),
        )

    if not _has("prohibited_goods"):
        op.create_table(
            "prohibited_goods",
            sa.Column("id", sa.Integer, primary_key=True, index=True),
            sa.Column("company_id", sa.Integer, nullable=False, index=True),
            sa.Column("code_produit", sa.String(200), nullable=False, index=True),
            sa.Column("designation", sa.Text, nullable=True),
            sa.Column("code_hs", sa.String(200), nullable=True),
            sa.Column("categorie", sa.String(50), nullable=True),
            sa.Column("base_legale", sa.Text, nullable=True),
            sa.Column("autorite_competente", sa.String(200), nullable=True),
            sa.Column("conditions_regime", sa.Text, nullable=True),
            sa.Column("actif", sa.Boolean, nullable=True),
            sa.Column("is_active", sa.Boolean, nullable=True),
            sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
            sa.Column("updated_at", sa.DateTime(timezone=True), nullable=True),
            sa.UniqueConstraint("company_id", "code_produit", name="uix_prohibited_goods_uniq"),
        )

    if not _has("customs_regimes"):
        op.create_table(
            "customs_regimes",
            sa.Column("id", sa.Integer, primary_key=True, index=True),
            sa.Column("company_id", sa.Integer, nullable=False, index=True),
            sa.Column("reference_regime", sa.String(200), nullable=False, index=True),
            sa.Column("dum_id", sa.Integer, nullable=True),
            sa.Column("type_regime", sa.String(50), nullable=True),
            sa.Column("duree_max_mois", sa.Integer, nullable=True),
            sa.Column("date_appllication", sa.Date, nullable=True),
            sa.Column("date_echeance", sa.Date, nullable=True),
            sa.Column("caution_associee", sa.String(200), nullable=True),
            sa.Column("statut", sa.String(50), nullable=True),
            sa.Column("notes", sa.Text, nullable=True),
            sa.Column("is_active", sa.Boolean, nullable=True),
            sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
            sa.Column("updated_at", sa.DateTime(timezone=True), nullable=True),
            sa.UniqueConstraint("company_id", "reference_regime", name="uix_customs_regimes_uniq"),
        )

    if not _has("physical_inspections"):
        op.create_table(
            "physical_inspections",
            sa.Column("id", sa.Integer, primary_key=True, index=True),
            sa.Column("company_id", sa.Integer, nullable=False, index=True),
            sa.Column("numero_pv", sa.String(200), nullable=False, index=True),
            sa.Column("dum_id", sa.Integer, nullable=True),
            sa.Column("canal", sa.String(50), nullable=True),
            sa.Column("inspecteur", sa.String(200), nullable=True),
            sa.Column("date_inspection", sa.DateTime(timezone=True), nullable=True),
            sa.Column("lieu", sa.String(200), nullable=True),
            sa.Column("resultat", sa.String(50), nullable=True),
            sa.Column("ecart_poids_kg", sa.Numeric, nullable=True),
            sa.Column("ecart_colis", sa.Integer, nullable=True),
            sa.Column("observations", sa.Text, nullable=True),
            sa.Column("statut", sa.String(50), nullable=True),
            sa.Column("is_active", sa.Boolean, nullable=True),
            sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
            sa.Column("updated_at", sa.DateTime(timezone=True), nullable=True),
            sa.UniqueConstraint("company_id", "numero_pv", name="uix_physical_inspections_uniq"),
        )

    if not _has("duty_payments"):
        op.create_table(
            "duty_payments",
            sa.Column("id", sa.Integer, primary_key=True, index=True),
            sa.Column("company_id", sa.Integer, nullable=False, index=True),
            sa.Column("numero_quittance", sa.String(200), nullable=False, index=True),
            sa.Column("dum_id", sa.Integer, nullable=True),
            sa.Column("type_paiement", sa.String(50), nullable=True),
            sa.Column("droits_percus_xaf", sa.Numeric, nullable=True),
            sa.Column("tva_xaf", sa.Numeric, nullable=True),
            sa.Column("taxe_statistique_xaf", sa.Numeric, nullable=True),
            sa.Column("redevance_id", sa.String(200), nullable=True),
            sa.Column("mode_reglement", sa.String(50), nullable=True),
            sa.Column("date_paiement", sa.Date, nullable=True),
            sa.Column("statut", sa.String(50), nullable=True),
            sa.Column("notes", sa.Text, nullable=True),
            sa.Column("is_active", sa.Boolean, nullable=True),
            sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
            sa.Column("updated_at", sa.DateTime(timezone=True), nullable=True),
            sa.UniqueConstraint("company_id", "numero_quittance", name="uix_duty_payments_uniq"),
        )

    if not _has("trader_registrations"):
        op.create_table(
            "trader_registrations",
            sa.Column("id", sa.Integer, primary_key=True, index=True),
            sa.Column("company_id", sa.Integer, nullable=False, index=True),
            sa.Column("numero_operateur", sa.String(200), nullable=False, index=True),
            sa.Column("raison_sociale", sa.String(200), nullable=True),
            sa.Column("niu", sa.String(200), nullable=True),
            sa.Column("rc_number", sa.String(200), nullable=True),
            sa.Column("type_operateur", sa.String(50), nullable=True),
            sa.Column("statut_oea", sa.String(50), nullable=True),
            sa.Column("date_agrement", sa.Date, nullable=True),
            sa.Column("date_expiration", sa.Date, nullable=True),
            sa.Column("contact_email", sa.String(200), nullable=True),
            sa.Column("contact_telephone", sa.String(200), nullable=True),
            sa.Column("notes", sa.Text, nullable=True),
            sa.Column("is_active", sa.Boolean, nullable=True),
            sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
            sa.Column("updated_at", sa.DateTime(timezone=True), nullable=True),
            sa.UniqueConstraint("company_id", "numero_operateur", name="uix_trader_registrations_uniq"),
        )

    if not _has("tariff_references"):
        op.create_table(
            "tariff_references",
            sa.Column("id", sa.Integer, primary_key=True, index=True),
            sa.Column("company_id", sa.Integer, nullable=False, index=True),
            sa.Column("code_ligne_tarifaire", sa.String(200), nullable=False, index=True),
            sa.Column("code_hs", sa.String(200), nullable=True),
            sa.Column("designation", sa.Text, nullable=True),
            sa.Column("droit_base_pct", sa.Numeric, nullable=True),
            sa.Column("cotisation_compensatoire_pct", sa.Numeric, nullable=True),
            sa.Column("taxe_foretiaire_pct", sa.Numeric, nullable=True),
            sa.Column("redevance_statistique_pct", sa.Numeric, nullable=True),
            sa.Column("tva_pct", sa.Numeric, nullable=True),
            sa.Column("categorie_produit", sa.String(50), nullable=True),
            sa.Column("date_application", sa.Date, nullable=True),
            sa.Column("date_fin", sa.Date, nullable=True),
            sa.Column("is_active", sa.Boolean, nullable=True),
            sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
            sa.Column("updated_at", sa.DateTime(timezone=True), nullable=True),
            sa.UniqueConstraint("company_id", "code_ligne_tarifaire", name="uix_tariff_references_uniq"),
        )


def downgrade():
    for t in reversed(TABLES):
        if _has(t):
            op.drop_table(t)
