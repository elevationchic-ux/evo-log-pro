"""065 : tables expansion logistique-3pl (genere)."""
from alembic import op
import sqlalchemy as sa


revision = "065_log3pl_deep"
down_revision = "064_fluvial_deep"
branch_labels = None
depends_on = None


TABLES = [
    "tpl_contracts",
    "tpl_warehouses",
    "tpl_crossdocks",
    "tpl_picking_lines",
    "tpl_sla_kpis",
    "tpl_invoices",
    "tpl_inventory_valuations",
    "tpl_sub_providers",
    "tpl_reverse_ops",
    "tpl_control_towers",
]


def _has(name):
    insp = sa.inspect(op.get_bind())
    return name in set(insp.get_table_names())


def upgrade():
    if not _has("tpl_contracts"):
        op.create_table(
            "tpl_contracts",
            sa.Column("id", sa.Integer, primary_key=True, index=True),
            sa.Column("company_id", sa.Integer, nullable=False, index=True),
            sa.Column("numero_contrat", sa.String(200), nullable=False, index=True),
            sa.Column("client", sa.String(200), nullable=True),
            sa.Column("perimetre", sa.String(200), nullable=True),
            sa.Column("sites_couverts", sa.Text, nullable=True),
            sa.Column("date_debut", sa.Date, nullable=True),
            sa.Column("date_fin", sa.Date, nullable=True),
            sa.Column("valeur_annuelle_xaf", sa.Integer, nullable=True),
            sa.Column("statut", sa.String(200), nullable=True),
            sa.Column("is_active", sa.Boolean, nullable=True),
            sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
            sa.Column("updated_at", sa.DateTime(timezone=True), nullable=True),
            sa.UniqueConstraint("company_id", "numero_contrat", name="uix_tpl_contracts_uniq"),
        )

    if not _has("tpl_warehouses"):
        op.create_table(
            "tpl_warehouses",
            sa.Column("id", sa.Integer, primary_key=True, index=True),
            sa.Column("company_id", sa.Integer, nullable=False, index=True),
            sa.Column("code_site", sa.String(200), nullable=False, index=True),
            sa.Column("nom", sa.String(200), nullable=True),
            sa.Column("localisation", sa.String(200), nullable=True),
            sa.Column("surface_m2", sa.Integer, nullable=True),
            sa.Column("capacite_palettes", sa.Integer, nullable=True),
            sa.Column("zones_froides", sa.Boolean, nullable=True),
            sa.Column("contract_associe", sa.String(200), nullable=True),
            sa.Column("statut", sa.String(200), nullable=True),
            sa.Column("is_active", sa.Boolean, nullable=True),
            sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
            sa.Column("updated_at", sa.DateTime(timezone=True), nullable=True),
            sa.UniqueConstraint("company_id", "code_site", name="uix_tpl_warehouses_uniq"),
        )

    if not _has("tpl_crossdocks"):
        op.create_table(
            "tpl_crossdocks",
            sa.Column("id", sa.Integer, primary_key=True, index=True),
            sa.Column("company_id", sa.Integer, nullable=False, index=True),
            sa.Column("reference", sa.String(200), nullable=False, index=True),
            sa.Column("site", sa.String(200), nullable=True),
            sa.Column("date_operation", sa.DateTime(timezone=True), nullable=True),
            sa.Column("nb_entrees", sa.Integer, nullable=True),
            sa.Column("nb_sorties", sa.Integer, nullable=True),
            sa.Column("duree_foresee_min", sa.Integer, nullable=True),
            sa.Column("statut", sa.String(200), nullable=True),
            sa.Column("is_active", sa.Boolean, nullable=True),
            sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
            sa.Column("updated_at", sa.DateTime(timezone=True), nullable=True),
            sa.UniqueConstraint("company_id", "reference", name="uix_tpl_crossdocks_uniq"),
        )

    if not _has("tpl_picking_lines"):
        op.create_table(
            "tpl_picking_lines",
            sa.Column("id", sa.Integer, primary_key=True, index=True),
            sa.Column("company_id", sa.Integer, nullable=False, index=True),
            sa.Column("reference", sa.String(200), nullable=False, index=True),
            sa.Column("site", sa.String(200), nullable=True),
            sa.Column("client", sa.String(200), nullable=True),
            sa.Column("type_preparation", sa.String(200), nullable=True),
            sa.Column("nb_lignes", sa.Integer, nullable=True),
            sa.Column("nb_colis", sa.Integer, nullable=True),
            sa.Column("operateur", sa.String(200), nullable=True),
            sa.Column("date_debut", sa.DateTime(timezone=True), nullable=True),
            sa.Column("date_fin", sa.DateTime(timezone=True), nullable=True),
            sa.Column("statut", sa.String(200), nullable=True),
            sa.Column("is_active", sa.Boolean, nullable=True),
            sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
            sa.Column("updated_at", sa.DateTime(timezone=True), nullable=True),
            sa.UniqueConstraint("company_id", "reference", name="uix_tpl_picking_lines_uniq"),
        )

    if not _has("tpl_sla_kpis"):
        op.create_table(
            "tpl_sla_kpis",
            sa.Column("id", sa.Integer, primary_key=True, index=True),
            sa.Column("company_id", sa.Integer, nullable=False, index=True),
            sa.Column("reference", sa.String(200), nullable=False, index=True),
            sa.Column("contrat_associe", sa.String(200), nullable=True),
            sa.Column("periode", sa.String(200), nullable=True),
            sa.Column("kpi", sa.String(200), nullable=True),
            sa.Column("valeur_cible", sa.String(200), nullable=True),
            sa.Column("valeur_reelle", sa.String(200), nullable=True),
            sa.Column("penalite_appliquee_xaf", sa.Integer, nullable=True),
            sa.Column("statut", sa.String(200), nullable=True),
            sa.Column("is_active", sa.Boolean, nullable=True),
            sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
            sa.Column("updated_at", sa.DateTime(timezone=True), nullable=True),
            sa.UniqueConstraint("company_id", "reference", name="uix_tpl_sla_kpis_uniq"),
        )

    if not _has("tpl_invoices"):
        op.create_table(
            "tpl_invoices",
            sa.Column("id", sa.Integer, primary_key=True, index=True),
            sa.Column("company_id", sa.Integer, nullable=False, index=True),
            sa.Column("numero_facture", sa.String(200), nullable=False, index=True),
            sa.Column("client", sa.String(200), nullable=True),
            sa.Column("periode", sa.String(200), nullable=True),
            sa.Column("montant_ht_xaf", sa.Integer, nullable=True),
            sa.Column("tva_xaf", sa.Integer, nullable=True),
            sa.Column("total_ttc_xaf", sa.Integer, nullable=True),
            sa.Column("date_emission", sa.Date, nullable=True),
            sa.Column("statut", sa.String(200), nullable=True),
            sa.Column("is_active", sa.Boolean, nullable=True),
            sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
            sa.Column("updated_at", sa.DateTime(timezone=True), nullable=True),
            sa.UniqueConstraint("company_id", "numero_facture", name="uix_tpl_invoices_uniq"),
        )

    if not _has("tpl_inventory_valuations"):
        op.create_table(
            "tpl_inventory_valuations",
            sa.Column("id", sa.Integer, primary_key=True, index=True),
            sa.Column("company_id", sa.Integer, nullable=False, index=True),
            sa.Column("reference", sa.String(200), nullable=False, index=True),
            sa.Column("site", sa.String(200), nullable=True),
            sa.Column("client", sa.String(200), nullable=True),
            sa.Column("date_inventaire", sa.Date, nullable=True),
            sa.Column("valeur_theorique_xaf", sa.Integer, nullable=True),
            sa.Column("valeur_physique_xaf", sa.Integer, nullable=True),
            sa.Column("ecart_pct", sa.Integer, nullable=True),
            sa.Column("statut", sa.String(200), nullable=True),
            sa.Column("is_active", sa.Boolean, nullable=True),
            sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
            sa.Column("updated_at", sa.DateTime(timezone=True), nullable=True),
            sa.UniqueConstraint("company_id", "reference", name="uix_tpl_inventory_valuations_uniq"),
        )

    if not _has("tpl_sub_providers"):
        op.create_table(
            "tpl_sub_providers",
            sa.Column("id", sa.Integer, primary_key=True, index=True),
            sa.Column("company_id", sa.Integer, nullable=False, index=True),
            sa.Column("code_fournisseur", sa.String(200), nullable=False, index=True),
            sa.Column("raison_sociale", sa.String(200), nullable=True),
            sa.Column("type_prestation", sa.String(200), nullable=True),
            sa.Column("zone_couverte", sa.String(200), nullable=True),
            sa.Column("date_debut_contrat", sa.Date, nullable=True),
            sa.Column("date_audit_precedent", sa.Date, nullable=True),
            sa.Column("note_qualite", sa.String(200), nullable=True),
            sa.Column("statut", sa.String(200), nullable=True),
            sa.Column("is_active", sa.Boolean, nullable=True),
            sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
            sa.Column("updated_at", sa.DateTime(timezone=True), nullable=True),
            sa.UniqueConstraint("company_id", "code_fournisseur", name="uix_tpl_sub_providers_uniq"),
        )

    if not _has("tpl_reverse_ops"):
        op.create_table(
            "tpl_reverse_ops",
            sa.Column("id", sa.Integer, primary_key=True, index=True),
            sa.Column("company_id", sa.Integer, nullable=False, index=True),
            sa.Column("reference", sa.String(200), nullable=False, index=True),
            sa.Column("client", sa.String(200), nullable=True),
            sa.Column("type_operation", sa.String(200), nullable=True),
            sa.Column("nb_unites", sa.Integer, nullable=True),
            sa.Column("site_prise_en_charge", sa.String(200), nullable=True),
            sa.Column("date_prise_en_charge", sa.Date, nullable=True),
            sa.Column("statut", sa.String(200), nullable=True),
            sa.Column("is_active", sa.Boolean, nullable=True),
            sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
            sa.Column("updated_at", sa.DateTime(timezone=True), nullable=True),
            sa.UniqueConstraint("company_id", "reference", name="uix_tpl_reverse_ops_uniq"),
        )

    if not _has("tpl_control_towers"):
        op.create_table(
            "tpl_control_towers",
            sa.Column("id", sa.Integer, primary_key=True, index=True),
            sa.Column("company_id", sa.Integer, nullable=False, index=True),
            sa.Column("reference", sa.String(200), nullable=False, index=True),
            sa.Column("client", sa.String(200), nullable=True),
            sa.Column("date_horodatage", sa.DateTime(timezone=True), nullable=True),
            sa.Column("nombre_alertes", sa.Integer, nullable=True),
            sa.Column("nombre_incidents", sa.Integer, nullable=True),
            sa.Column("taux_service_pct", sa.Integer, nullable=True),
            sa.Column("operateur_tour", sa.String(200), nullable=True),
            sa.Column("statut", sa.String(200), nullable=True),
            sa.Column("is_active", sa.Boolean, nullable=True),
            sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
            sa.Column("updated_at", sa.DateTime(timezone=True), nullable=True),
            sa.UniqueConstraint("company_id", "reference", name="uix_tpl_control_towers_uniq"),
        )


def downgrade():
    for t in reversed(TABLES):
        if _has(t):
            op.drop_table(t)
