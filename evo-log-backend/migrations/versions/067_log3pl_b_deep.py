"""067 : tables expansion logistique-3pl (genere)."""
from alembic import op
import sqlalchemy as sa


revision = "067_log3pl_b_deep"
down_revision = "066_merge_expansion_rbac"
branch_labels = None
depends_on = None


TABLES = [
    "tplb_dock_appointments",
    "tplb_loading_plans",
    "tplb_shipment_manifests",
    "tplb_inventory_transfers",
    "tplb_cold_chain_logs",
    "tplb_return_authorizations",
    "tplb_carrier_rates",
    "tplb_order_nodes",
    "tplb_damage_claims",
]


def _has(name):
    insp = sa.inspect(op.get_bind())
    return name in set(insp.get_table_names())


def upgrade():
    if not _has("tplb_dock_appointments"):
        op.create_table(
            "tplb_dock_appointments",
            sa.Column("id", sa.Integer, primary_key=True, index=True),
            sa.Column("company_id", sa.Integer, nullable=False, index=True),
            sa.Column("reference", sa.String(200), nullable=False, index=True),
            sa.Column("site", sa.String(200), nullable=True),
            sa.Column("numero_quai", sa.String(200), nullable=True),
            sa.Column("date_debut", sa.DateTime(timezone=True), nullable=True),
            sa.Column("date_fin", sa.DateTime(timezone=True), nullable=True),
            sa.Column("immatriculation", sa.String(200), nullable=True),
            sa.Column("type_mouvement", sa.String(200), nullable=True),
            sa.Column("statut", sa.String(200), nullable=True),
            sa.Column("is_active", sa.Boolean, nullable=True),
            sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
            sa.Column("updated_at", sa.DateTime(timezone=True), nullable=True),
            sa.UniqueConstraint("company_id", "reference", name="uix_tplb_dock_appointments_uniq"),
        )

    if not _has("tplb_loading_plans"):
        op.create_table(
            "tplb_loading_plans",
            sa.Column("id", sa.Integer, primary_key=True, index=True),
            sa.Column("company_id", sa.Integer, nullable=False, index=True),
            sa.Column("reference", sa.String(200), nullable=False, index=True),
            sa.Column("site", sa.String(200), nullable=True),
            sa.Column("numero_camion", sa.String(200), nullable=True),
            sa.Column("nb_colis", sa.Integer, nullable=True),
            sa.Column("poids_total_kg", sa.Integer, nullable=True),
            sa.Column("volume_m3", sa.Integer, nullable=True),
            sa.Column("taux_remplissage_pct", sa.Integer, nullable=True),
            sa.Column("date_plan", sa.DateTime(timezone=True), nullable=True),
            sa.Column("statut", sa.String(200), nullable=True),
            sa.Column("is_active", sa.Boolean, nullable=True),
            sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
            sa.Column("updated_at", sa.DateTime(timezone=True), nullable=True),
            sa.UniqueConstraint("company_id", "reference", name="uix_tplb_loading_plans_uniq"),
        )

    if not _has("tplb_shipment_manifests"):
        op.create_table(
            "tplb_shipment_manifests",
            sa.Column("id", sa.Integer, primary_key=True, index=True),
            sa.Column("company_id", sa.Integer, nullable=False, index=True),
            sa.Column("numero_manifeste", sa.String(200), nullable=False, index=True),
            sa.Column("client", sa.String(200), nullable=True),
            sa.Column("site_depart", sa.String(200), nullable=True),
            sa.Column("site_arrivee", sa.String(200), nullable=True),
            sa.Column("nb_colis", sa.Integer, nullable=True),
            sa.Column("poids_total_kg", sa.Integer, nullable=True),
            sa.Column("date_emission", sa.Date, nullable=True),
            sa.Column("statut", sa.String(200), nullable=True),
            sa.Column("is_active", sa.Boolean, nullable=True),
            sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
            sa.Column("updated_at", sa.DateTime(timezone=True), nullable=True),
            sa.UniqueConstraint("company_id", "numero_manifeste", name="uix_tplb_shipment_manifests_uniq"),
        )

    if not _has("tplb_inventory_transfers"):
        op.create_table(
            "tplb_inventory_transfers",
            sa.Column("id", sa.Integer, primary_key=True, index=True),
            sa.Column("company_id", sa.Integer, nullable=False, index=True),
            sa.Column("reference", sa.String(200), nullable=False, index=True),
            sa.Column("site_source", sa.String(200), nullable=True),
            sa.Column("site_destinataire", sa.String(200), nullable=True),
            sa.Column("sku", sa.String(200), nullable=True),
            sa.Column("quantite_expediee", sa.Integer, nullable=True),
            sa.Column("quantite_recue", sa.Integer, nullable=True),
            sa.Column("date_transfert", sa.Date, nullable=True),
            sa.Column("statut", sa.String(200), nullable=True),
            sa.Column("is_active", sa.Boolean, nullable=True),
            sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
            sa.Column("updated_at", sa.DateTime(timezone=True), nullable=True),
            sa.UniqueConstraint("company_id", "reference", name="uix_tplb_inventory_transfers_uniq"),
        )

    if not _has("tplb_cold_chain_logs"):
        op.create_table(
            "tplb_cold_chain_logs",
            sa.Column("id", sa.Integer, primary_key=True, index=True),
            sa.Column("company_id", sa.Integer, nullable=False, index=True),
            sa.Column("reference", sa.String(200), nullable=False, index=True),
            sa.Column("site", sa.String(200), nullable=True),
            sa.Column("produit", sa.String(200), nullable=True),
            sa.Column("sonde", sa.String(200), nullable=True),
            sa.Column("temperature_c", sa.Numeric, nullable=True),
            sa.Column("plage_min_c", sa.Numeric, nullable=True),
            sa.Column("plage_max_c", sa.Numeric, nullable=True),
            sa.Column("date_releve", sa.DateTime(timezone=True), nullable=True),
            sa.Column("statut", sa.String(200), nullable=True),
            sa.Column("is_active", sa.Boolean, nullable=True),
            sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
            sa.Column("updated_at", sa.DateTime(timezone=True), nullable=True),
            sa.UniqueConstraint("company_id", "reference", name="uix_tplb_cold_chain_logs_uniq"),
        )

    if not _has("tplb_return_authorizations"):
        op.create_table(
            "tplb_return_authorizations",
            sa.Column("id", sa.Integer, primary_key=True, index=True),
            sa.Column("company_id", sa.Integer, nullable=False, index=True),
            sa.Column("numero_rma", sa.String(200), nullable=False, index=True),
            sa.Column("client", sa.String(200), nullable=True),
            sa.Column("commande_originale", sa.String(200), nullable=True),
            sa.Column("motif_retour", sa.String(200), nullable=True),
            sa.Column("nb_unites", sa.Integer, nullable=True),
            sa.Column("date_demande", sa.Date, nullable=True),
            sa.Column("decision", sa.String(200), nullable=True),
            sa.Column("statut", sa.String(200), nullable=True),
            sa.Column("is_active", sa.Boolean, nullable=True),
            sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
            sa.Column("updated_at", sa.DateTime(timezone=True), nullable=True),
            sa.UniqueConstraint("company_id", "numero_rma", name="uix_tplb_return_authorizations_uniq"),
        )

    if not _has("tplb_carrier_rates"):
        op.create_table(
            "tplb_carrier_rates",
            sa.Column("id", sa.Integer, primary_key=True, index=True),
            sa.Column("company_id", sa.Integer, nullable=False, index=True),
            sa.Column("code_tarif", sa.String(200), nullable=False, index=True),
            sa.Column("transporteur", sa.String(200), nullable=True),
            sa.Column("zone", sa.String(200), nullable=True),
            sa.Column("poids_kg", sa.Integer, nullable=True),
            sa.Column("prix_base_xaf", sa.Integer, nullable=True),
            sa.Column("prix_par_kg_xaf", sa.Integer, nullable=True),
            sa.Column("validite_debut", sa.Date, nullable=True),
            sa.Column("validite_fin", sa.Date, nullable=True),
            sa.Column("statut", sa.String(200), nullable=True),
            sa.Column("is_active", sa.Boolean, nullable=True),
            sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
            sa.Column("updated_at", sa.DateTime(timezone=True), nullable=True),
            sa.UniqueConstraint("company_id", "code_tarif", name="uix_tplb_carrier_rates_uniq"),
        )

    if not _has("tplb_order_nodes"):
        op.create_table(
            "tplb_order_nodes",
            sa.Column("id", sa.Integer, primary_key=True, index=True),
            sa.Column("company_id", sa.Integer, nullable=False, index=True),
            sa.Column("reference", sa.String(200), nullable=False, index=True),
            sa.Column("numero_commande", sa.String(200), nullable=True),
            sa.Column("code_jalon", sa.String(200), nullable=True),
            sa.Column("libelle_jalon", sa.String(200), nullable=True),
            sa.Column("date_horodatage", sa.DateTime(timezone=True), nullable=True),
            sa.Column("lieu", sa.String(200), nullable=True),
            sa.Column("operateur", sa.String(200), nullable=True),
            sa.Column("statut", sa.String(200), nullable=True),
            sa.Column("is_active", sa.Boolean, nullable=True),
            sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
            sa.Column("updated_at", sa.DateTime(timezone=True), nullable=True),
            sa.UniqueConstraint("company_id", "reference", name="uix_tplb_order_nodes_uniq"),
        )

    if not _has("tplb_damage_claims"):
        op.create_table(
            "tplb_damage_claims",
            sa.Column("id", sa.Integer, primary_key=True, index=True),
            sa.Column("company_id", sa.Integer, nullable=False, index=True),
            sa.Column("numero_dossier", sa.String(200), nullable=False, index=True),
            sa.Column("client", sa.String(200), nullable=True),
            sa.Column("expedition_associee", sa.String(200), nullable=True),
            sa.Column("type_avarie", sa.String(200), nullable=True),
            sa.Column("montant_reclame_xaf", sa.Integer, nullable=True),
            sa.Column("date_ouverture", sa.Date, nullable=True),
            sa.Column("date_resolution", sa.Date, nullable=True),
            sa.Column("statut", sa.String(200), nullable=True),
            sa.Column("is_active", sa.Boolean, nullable=True),
            sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
            sa.Column("updated_at", sa.DateTime(timezone=True), nullable=True),
            sa.UniqueConstraint("company_id", "numero_dossier", name="uix_tplb_damage_claims_uniq"),
        )


def downgrade():
    for t in reversed(TABLES):
        if _has(t):
            op.drop_table(t)
