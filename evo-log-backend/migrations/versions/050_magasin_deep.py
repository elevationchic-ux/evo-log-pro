"""050 : tables expansion magasin-stock (genere)."""
from alembic import op
import sqlalchemy as sa


revision = "050_magasin_deep"
down_revision = "049_transport_deep"
branch_labels = None
depends_on = None


TABLES = [
    "article_catalogs",
    "supplier_articles",
    "purchase_orders_deep",
    "quality_inspections",
    "stock_alerts",
    "expiry_records",
    "serial_numbers",
    "packing_units",
    "stock_returns",
    "consignment_stocks",
    "stock_valuations",
    "wms_kpis",
]


def _has(name):
    insp = sa.inspect(op.get_bind())
    return name in set(insp.get_table_names())


def upgrade():
    if not _has("article_catalogs"):
        op.create_table(
            "article_catalogs",
            sa.Column("id", sa.Integer, primary_key=True, index=True),
            sa.Column("company_id", sa.Integer, nullable=False, index=True),
            sa.Column("code_sku", sa.String(200), nullable=False, index=True),
            sa.Column("designation", sa.String(200), nullable=True),
            sa.Column("categorie", sa.String(200), nullable=True),
            sa.Column("unite_principale", sa.String(200), nullable=True),
            sa.Column("code_barre", sa.String(200), nullable=True),
            sa.Column("poids_unitaire_kg", sa.Numeric, nullable=True),
            sa.Column("volume_m3", sa.Numeric, nullable=True),
            sa.Column("prix_achat_moyen_xaf", sa.Numeric, nullable=True),
            sa.Column("prix_vente_xaf", sa.Numeric, nullable=True),
            sa.Column("statut", sa.String(50), nullable=True),
            sa.Column("is_active", sa.Boolean, nullable=True),
            sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
            sa.Column("updated_at", sa.DateTime(timezone=True), nullable=True),
            sa.UniqueConstraint("company_id", "code_sku", name="uix_article_catalogs_uniq"),
        )

    if not _has("supplier_articles"):
        op.create_table(
            "supplier_articles",
            sa.Column("id", sa.Integer, primary_key=True, index=True),
            sa.Column("company_id", sa.Integer, nullable=False, index=True),
            sa.Column("reference", sa.String(200), nullable=False, index=True),
            sa.Column("article_id", sa.Integer, nullable=True),
            sa.Column("fournisseur_id", sa.Integer, nullable=True),
            sa.Column("prix_unitaire_xaf", sa.Numeric, nullable=True),
            sa.Column("delai_livraison_jours", sa.Integer, nullable=True),
            sa.Column("quantite_min_commande", sa.Numeric, nullable=True),
            sa.Column("devise", sa.String(200), nullable=True),
            sa.Column("conditions_paiement", sa.String(200), nullable=True),
            sa.Column("actif", sa.Boolean, nullable=True),
            sa.Column("is_active", sa.Boolean, nullable=True),
            sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
            sa.Column("updated_at", sa.DateTime(timezone=True), nullable=True),
            sa.UniqueConstraint("company_id", "reference", name="uix_supplier_articles_uniq"),
        )

    if not _has("purchase_orders_deep"):
        op.create_table(
            "purchase_orders_deep",
            sa.Column("id", sa.Integer, primary_key=True, index=True),
            sa.Column("company_id", sa.Integer, nullable=False, index=True),
            sa.Column("numero_commande", sa.String(200), nullable=False, index=True),
            sa.Column("fournisseur_id", sa.Integer, nullable=True),
            sa.Column("date_commande", sa.Date, nullable=True),
            sa.Column("date_livraison_prevue", sa.Date, nullable=True),
            sa.Column("montant_total_xaf", sa.Numeric, nullable=True),
            sa.Column("nb_lignes", sa.Integer, nullable=True),
            sa.Column("acheteur", sa.String(200), nullable=True),
            sa.Column("statut", sa.String(50), nullable=True),
            sa.Column("notes", sa.Text, nullable=True),
            sa.Column("is_active", sa.Boolean, nullable=True),
            sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
            sa.Column("updated_at", sa.DateTime(timezone=True), nullable=True),
            sa.UniqueConstraint("company_id", "numero_commande", name="uix_purchase_orders_deep_uniq"),
        )

    if not _has("quality_inspections"):
        op.create_table(
            "quality_inspections",
            sa.Column("id", sa.Integer, primary_key=True, index=True),
            sa.Column("company_id", sa.Integer, nullable=False, index=True),
            sa.Column("numero_controle", sa.String(200), nullable=False, index=True),
            sa.Column("reception_id", sa.Integer, nullable=True),
            sa.Column("article_id", sa.Integer, nullable=True),
            sa.Column("quantite_inspekte", sa.Numeric, nullable=True),
            sa.Column("quantite_conforme", sa.Numeric, nullable=True),
            sa.Column("quantite_rebutee", sa.Numeric, nullable=True),
            sa.Column("resultat", sa.String(50), nullable=True),
            sa.Column("inspecteur", sa.String(200), nullable=True),
            sa.Column("date_controle", sa.Date, nullable=True),
            sa.Column("observations", sa.Text, nullable=True),
            sa.Column("is_active", sa.Boolean, nullable=True),
            sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
            sa.Column("updated_at", sa.DateTime(timezone=True), nullable=True),
            sa.UniqueConstraint("company_id", "numero_controle", name="uix_quality_inspections_uniq"),
        )

    if not _has("stock_alerts"):
        op.create_table(
            "stock_alerts",
            sa.Column("id", sa.Integer, primary_key=True, index=True),
            sa.Column("company_id", sa.Integer, nullable=False, index=True),
            sa.Column("code_alerte", sa.String(200), nullable=False, index=True),
            sa.Column("article_id", sa.Integer, nullable=True),
            sa.Column("depot_id", sa.Integer, nullable=True),
            sa.Column("seuil_min", sa.Numeric, nullable=True),
            sa.Column("seuil_max", sa.Numeric, nullable=True),
            sa.Column("point_commande", sa.Numeric, nullable=True),
            sa.Column("quantite_actuelle", sa.Numeric, nullable=True),
            sa.Column("derniere_alerte", sa.DateTime(timezone=True), nullable=True),
            sa.Column("statut", sa.String(50), nullable=True),
            sa.Column("is_active", sa.Boolean, nullable=True),
            sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
            sa.Column("updated_at", sa.DateTime(timezone=True), nullable=True),
            sa.UniqueConstraint("company_id", "code_alerte", name="uix_stock_alerts_uniq"),
        )

    if not _has("expiry_records"):
        op.create_table(
            "expiry_records",
            sa.Column("id", sa.Integer, primary_key=True, index=True),
            sa.Column("company_id", sa.Integer, nullable=False, index=True),
            sa.Column("numero_lot", sa.String(200), nullable=False, index=True),
            sa.Column("article_id", sa.Integer, nullable=True),
            sa.Column("quantite", sa.Numeric, nullable=True),
            sa.Column("date_peremption", sa.Date, nullable=True),
            sa.Column("date_reception", sa.Date, nullable=True),
            sa.Column("statut", sa.String(50), nullable=True),
            sa.Column("notes", sa.Text, nullable=True),
            sa.Column("is_active", sa.Boolean, nullable=True),
            sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
            sa.Column("updated_at", sa.DateTime(timezone=True), nullable=True),
            sa.UniqueConstraint("company_id", "numero_lot", name="uix_expiry_records_uniq"),
        )

    if not _has("serial_numbers"):
        op.create_table(
            "serial_numbers",
            sa.Column("id", sa.Integer, primary_key=True, index=True),
            sa.Column("company_id", sa.Integer, nullable=False, index=True),
            sa.Column("numero_serial", sa.String(200), nullable=False, index=True),
            sa.Column("article_id", sa.Integer, nullable=True),
            sa.Column("numero_lot", sa.String(200), nullable=True),
            sa.Column("statut", sa.String(50), nullable=True),
            sa.Column("date_entree", sa.Date, nullable=True),
            sa.Column("date_sortie", sa.Date, nullable=True),
            sa.Column("destination", sa.String(200), nullable=True),
            sa.Column("notes", sa.Text, nullable=True),
            sa.Column("is_active", sa.Boolean, nullable=True),
            sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
            sa.Column("updated_at", sa.DateTime(timezone=True), nullable=True),
            sa.UniqueConstraint("company_id", "numero_serial", name="uix_serial_numbers_uniq"),
        )

    if not _has("packing_units"):
        op.create_table(
            "packing_units",
            sa.Column("id", sa.Integer, primary_key=True, index=True),
            sa.Column("company_id", sa.Integer, nullable=False, index=True),
            sa.Column("code_uc", sa.String(200), nullable=False, index=True),
            sa.Column("type_uc", sa.String(50), nullable=True),
            sa.Column("dimensions", sa.String(200), nullable=True),
            sa.Column("poids_tare_kg", sa.Numeric, nullable=True),
            sa.Column("capacite_max_kg", sa.Numeric, nullable=True),
            sa.Column("nb_unites_principales", sa.Numeric, nullable=True),
            sa.Column("actif", sa.Boolean, nullable=True),
            sa.Column("is_active", sa.Boolean, nullable=True),
            sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
            sa.Column("updated_at", sa.DateTime(timezone=True), nullable=True),
            sa.UniqueConstraint("company_id", "code_uc", name="uix_packing_units_uniq"),
        )

    if not _has("stock_returns"):
        op.create_table(
            "stock_returns",
            sa.Column("id", sa.Integer, primary_key=True, index=True),
            sa.Column("company_id", sa.Integer, nullable=False, index=True),
            sa.Column("numero_retour", sa.String(200), nullable=False, index=True),
            sa.Column("type_retour", sa.String(50), nullable=True),
            sa.Column("client_id", sa.Integer, nullable=True),
            sa.Column("fournisseur_id", sa.Integer, nullable=True),
            sa.Column("date_retour", sa.Date, nullable=True),
            sa.Column("article_id", sa.Integer, nullable=True),
            sa.Column("quantite", sa.Numeric, nullable=True),
            sa.Column("motif", sa.Text, nullable=True),
            sa.Column("statut", sa.String(50), nullable=True),
            sa.Column("is_active", sa.Boolean, nullable=True),
            sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
            sa.Column("updated_at", sa.DateTime(timezone=True), nullable=True),
            sa.UniqueConstraint("company_id", "numero_retour", name="uix_stock_returns_uniq"),
        )

    if not _has("consignment_stocks"):
        op.create_table(
            "consignment_stocks",
            sa.Column("id", sa.Integer, primary_key=True, index=True),
            sa.Column("company_id", sa.Integer, nullable=False, index=True),
            sa.Column("reference", sa.String(200), nullable=False, index=True),
            sa.Column("proprietaire_id", sa.Integer, nullable=True),
            sa.Column("article_id", sa.Integer, nullable=True),
            sa.Column("quantite_deposee", sa.Numeric, nullable=True),
            sa.Column("quantite_retiree", sa.Numeric, nullable=True),
            sa.Column("date_depot", sa.Date, nullable=True),
            sa.Column("date_limite", sa.Date, nullable=True),
            sa.Column("statut", sa.String(50), nullable=True),
            sa.Column("notes", sa.Text, nullable=True),
            sa.Column("is_active", sa.Boolean, nullable=True),
            sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
            sa.Column("updated_at", sa.DateTime(timezone=True), nullable=True),
            sa.UniqueConstraint("company_id", "reference", name="uix_consignment_stocks_uniq"),
        )

    if not _has("stock_valuations"):
        op.create_table(
            "stock_valuations",
            sa.Column("id", sa.Integer, primary_key=True, index=True),
            sa.Column("company_id", sa.Integer, nullable=False, index=True),
            sa.Column("reference", sa.String(200), nullable=False, index=True),
            sa.Column("periode", sa.String(200), nullable=True),
            sa.Column("article_id", sa.Integer, nullable=True),
            sa.Column("methode", sa.String(50), nullable=True),
            sa.Column("quantite_fin", sa.Numeric, nullable=True),
            sa.Column("valeur_cmup_xaf", sa.Numeric, nullable=True),
            sa.Column("valeur_coi_xaf", sa.Numeric, nullable=True),
            sa.Column("date_calcul", sa.Date, nullable=True),
            sa.Column("is_active", sa.Boolean, nullable=True),
            sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
            sa.Column("updated_at", sa.DateTime(timezone=True), nullable=True),
            sa.UniqueConstraint("company_id", "reference", name="uix_stock_valuations_uniq"),
        )

    if not _has("wms_kpis"):
        op.create_table(
            "wms_kpis",
            sa.Column("id", sa.Integer, primary_key=True, index=True),
            sa.Column("company_id", sa.Integer, nullable=False, index=True),
            sa.Column("reference", sa.String(200), nullable=False, index=True),
            sa.Column("periode_debut", sa.Date, nullable=True),
            sa.Column("periode_fin", sa.Date, nullable=True),
            sa.Column("rotation", sa.Numeric, nullable=True),
            sa.Column("rupture_pct", sa.Numeric, nullable=True),
            sa.Column("taux_service_pct", sa.Numeric, nullable=True),
            sa.Column("cadence_choix_lignes_h", sa.Numeric, nullable=True),
            sa.Column("ecart_inventaire_pct", sa.Numeric, nullable=True),
            sa.Column("notes", sa.Text, nullable=True),
            sa.Column("is_active", sa.Boolean, nullable=True),
            sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
            sa.Column("updated_at", sa.DateTime(timezone=True), nullable=True),
            sa.UniqueConstraint("company_id", "reference", name="uix_wms_kpis_uniq"),
        )


def downgrade():
    for t in reversed(TABLES):
        if _has(t):
            op.drop_table(t)
