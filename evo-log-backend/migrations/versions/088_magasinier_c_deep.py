"""088 : tables expansion portail-magasinier (genere)."""
from alembic import op
import sqlalchemy as sa


revision = "088_magasinier_c_deep"
down_revision = "087_chauffeur_c_deep"
branch_labels = None
depends_on = None


TABLES = [
    "magc_picking_tasks",
    "magc_packing_slips",
    "magc_putaway_tasks",
    "magc_cycle_counts",
    "magc_internal_moves",
    "magc_goods_issues",
    "magc_returns",
    "magc_label_prints",
    "magc_pallet_builds",
    "magc_equipment_checks",
    "magc_safety_inspections",
    "magc_spill_cleanups",
    "magc_loading_checks",
    "magc_receiving_checks",
    "magc_putaway_exceptions",
    "magc_order_staging",
    "magc_cold_checks",
    "magc_hazmat_handling",
    "magc_dock_assignments",
]


def _has(name):
    insp = sa.inspect(op.get_bind())
    return name in set(insp.get_table_names())


def upgrade():
    if not _has("magc_picking_tasks"):
        op.create_table(
            "magc_picking_tasks",
            sa.Column("id", sa.Integer, primary_key=True, index=True),
            sa.Column("company_id", sa.Integer, nullable=False, index=True),
            sa.Column("reference", sa.String(200), nullable=False, index=True),
            sa.Column("ordre", sa.String(200), nullable=True),
            sa.Column("emplacement", sa.String(200), nullable=True),
            sa.Column("quantite", sa.Integer, nullable=True),
            sa.Column("prepareur", sa.String(200), nullable=True),
            sa.Column("statut", sa.String(200), nullable=True),
            sa.Column("is_active", sa.Boolean, nullable=True),
            sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
            sa.Column("updated_at", sa.DateTime(timezone=True), nullable=True),
            sa.UniqueConstraint("company_id", "reference", name="uix_magc_picking_tasks_uniq"),
        )

    if not _has("magc_packing_slips"):
        op.create_table(
            "magc_packing_slips",
            sa.Column("id", sa.Integer, primary_key=True, index=True),
            sa.Column("company_id", sa.Integer, nullable=False, index=True),
            sa.Column("reference", sa.String(200), nullable=False, index=True),
            sa.Column("commande", sa.String(200), nullable=True),
            sa.Column("nb_colis", sa.Integer, nullable=True),
            sa.Column("poids", sa.Numeric, nullable=True),
            sa.Column("operateur", sa.String(200), nullable=True),
            sa.Column("statut", sa.String(200), nullable=True),
            sa.Column("is_active", sa.Boolean, nullable=True),
            sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
            sa.Column("updated_at", sa.DateTime(timezone=True), nullable=True),
            sa.UniqueConstraint("company_id", "reference", name="uix_magc_packing_slips_uniq"),
        )

    if not _has("magc_putaway_tasks"):
        op.create_table(
            "magc_putaway_tasks",
            sa.Column("id", sa.Integer, primary_key=True, index=True),
            sa.Column("company_id", sa.Integer, nullable=False, index=True),
            sa.Column("reference", sa.String(200), nullable=False, index=True),
            sa.Column("article", sa.String(200), nullable=True),
            sa.Column("quantite", sa.Integer, nullable=True),
            sa.Column("de", sa.String(200), nullable=True),
            sa.Column("vers", sa.String(200), nullable=True),
            sa.Column("statut", sa.String(200), nullable=True),
            sa.Column("is_active", sa.Boolean, nullable=True),
            sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
            sa.Column("updated_at", sa.DateTime(timezone=True), nullable=True),
            sa.UniqueConstraint("company_id", "reference", name="uix_magc_putaway_tasks_uniq"),
        )

    if not _has("magc_cycle_counts"):
        op.create_table(
            "magc_cycle_counts",
            sa.Column("id", sa.Integer, primary_key=True, index=True),
            sa.Column("company_id", sa.Integer, nullable=False, index=True),
            sa.Column("reference", sa.String(200), nullable=False, index=True),
            sa.Column("emplacement", sa.String(200), nullable=True),
            sa.Column("theorique", sa.Integer, nullable=True),
            sa.Column("physique", sa.Integer, nullable=True),
            sa.Column("compteur", sa.String(200), nullable=True),
            sa.Column("statut", sa.String(200), nullable=True),
            sa.Column("is_active", sa.Boolean, nullable=True),
            sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
            sa.Column("updated_at", sa.DateTime(timezone=True), nullable=True),
            sa.UniqueConstraint("company_id", "reference", name="uix_magc_cycle_counts_uniq"),
        )

    if not _has("magc_internal_moves"):
        op.create_table(
            "magc_internal_moves",
            sa.Column("id", sa.Integer, primary_key=True, index=True),
            sa.Column("company_id", sa.Integer, nullable=False, index=True),
            sa.Column("reference", sa.String(200), nullable=False, index=True),
            sa.Column("article", sa.String(200), nullable=True),
            sa.Column("quantite", sa.Integer, nullable=True),
            sa.Column("origine", sa.String(200), nullable=True),
            sa.Column("destination", sa.String(200), nullable=True),
            sa.Column("statut", sa.String(200), nullable=True),
            sa.Column("is_active", sa.Boolean, nullable=True),
            sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
            sa.Column("updated_at", sa.DateTime(timezone=True), nullable=True),
            sa.UniqueConstraint("company_id", "reference", name="uix_magc_internal_moves_uniq"),
        )

    if not _has("magc_goods_issues"):
        op.create_table(
            "magc_goods_issues",
            sa.Column("id", sa.Integer, primary_key=True, index=True),
            sa.Column("company_id", sa.Integer, nullable=False, index=True),
            sa.Column("reference", sa.String(200), nullable=False, index=True),
            sa.Column("demande", sa.String(200), nullable=True),
            sa.Column("article", sa.String(200), nullable=True),
            sa.Column("quantite", sa.Integer, nullable=True),
            sa.Column("beneficiaire", sa.String(200), nullable=True),
            sa.Column("statut", sa.String(200), nullable=True),
            sa.Column("is_active", sa.Boolean, nullable=True),
            sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
            sa.Column("updated_at", sa.DateTime(timezone=True), nullable=True),
            sa.UniqueConstraint("company_id", "reference", name="uix_magc_goods_issues_uniq"),
        )

    if not _has("magc_returns"):
        op.create_table(
            "magc_returns",
            sa.Column("id", sa.Integer, primary_key=True, index=True),
            sa.Column("company_id", sa.Integer, nullable=False, index=True),
            sa.Column("reference", sa.String(200), nullable=False, index=True),
            sa.Column("retour", sa.String(200), nullable=True),
            sa.Column("article", sa.String(200), nullable=True),
            sa.Column("quantite", sa.Integer, nullable=True),
            sa.Column("motif", sa.String(200), nullable=True),
            sa.Column("statut", sa.String(200), nullable=True),
            sa.Column("is_active", sa.Boolean, nullable=True),
            sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
            sa.Column("updated_at", sa.DateTime(timezone=True), nullable=True),
            sa.UniqueConstraint("company_id", "reference", name="uix_magc_returns_uniq"),
        )

    if not _has("magc_label_prints"):
        op.create_table(
            "magc_label_prints",
            sa.Column("id", sa.Integer, primary_key=True, index=True),
            sa.Column("company_id", sa.Integer, nullable=False, index=True),
            sa.Column("reference", sa.String(200), nullable=False, index=True),
            sa.Column("article", sa.String(200), nullable=True),
            sa.Column("nombre", sa.Integer, nullable=True),
            sa.Column("type_etiquette", sa.String(200), nullable=True),
            sa.Column("operateur", sa.String(200), nullable=True),
            sa.Column("statut", sa.String(200), nullable=True),
            sa.Column("is_active", sa.Boolean, nullable=True),
            sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
            sa.Column("updated_at", sa.DateTime(timezone=True), nullable=True),
            sa.UniqueConstraint("company_id", "reference", name="uix_magc_label_prints_uniq"),
        )

    if not _has("magc_pallet_builds"):
        op.create_table(
            "magc_pallet_builds",
            sa.Column("id", sa.Integer, primary_key=True, index=True),
            sa.Column("company_id", sa.Integer, nullable=False, index=True),
            sa.Column("reference", sa.String(200), nullable=False, index=True),
            sa.Column("commande", sa.String(200), nullable=True),
            sa.Column("nb_cartons", sa.Integer, nullable=True),
            sa.Column("hauteur_cm", sa.Integer, nullable=True),
            sa.Column("poids_total", sa.Numeric, nullable=True),
            sa.Column("statut", sa.String(200), nullable=True),
            sa.Column("is_active", sa.Boolean, nullable=True),
            sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
            sa.Column("updated_at", sa.DateTime(timezone=True), nullable=True),
            sa.UniqueConstraint("company_id", "reference", name="uix_magc_pallet_builds_uniq"),
        )

    if not _has("magc_equipment_checks"):
        op.create_table(
            "magc_equipment_checks",
            sa.Column("id", sa.Integer, primary_key=True, index=True),
            sa.Column("company_id", sa.Integer, nullable=False, index=True),
            sa.Column("reference", sa.String(200), nullable=False, index=True),
            sa.Column("equipment", sa.String(200), nullable=True),
            sa.Column("numero", sa.String(200), nullable=True),
            sa.Column("controleur", sa.String(200), nullable=True),
            sa.Column("date_controle", sa.DateTime(timezone=True), nullable=True),
            sa.Column("statut", sa.String(200), nullable=True),
            sa.Column("is_active", sa.Boolean, nullable=True),
            sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
            sa.Column("updated_at", sa.DateTime(timezone=True), nullable=True),
            sa.UniqueConstraint("company_id", "reference", name="uix_magc_equipment_checks_uniq"),
        )

    if not _has("magc_safety_inspections"):
        op.create_table(
            "magc_safety_inspections",
            sa.Column("id", sa.Integer, primary_key=True, index=True),
            sa.Column("company_id", sa.Integer, nullable=False, index=True),
            sa.Column("reference", sa.String(200), nullable=False, index=True),
            sa.Column("zone", sa.String(200), nullable=True),
            sa.Column("inspecteur", sa.String(200), nullable=True),
            sa.Column("date", sa.DateTime(timezone=True), nullable=True),
            sa.Column("anomalies", sa.Integer, nullable=True),
            sa.Column("statut", sa.String(200), nullable=True),
            sa.Column("is_active", sa.Boolean, nullable=True),
            sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
            sa.Column("updated_at", sa.DateTime(timezone=True), nullable=True),
            sa.UniqueConstraint("company_id", "reference", name="uix_magc_safety_inspections_uniq"),
        )

    if not _has("magc_spill_cleanups"):
        op.create_table(
            "magc_spill_cleanups",
            sa.Column("id", sa.Integer, primary_key=True, index=True),
            sa.Column("company_id", sa.Integer, nullable=False, index=True),
            sa.Column("reference", sa.String(200), nullable=False, index=True),
            sa.Column("zone", sa.String(200), nullable=True),
            sa.Column("produit", sa.String(200), nullable=True),
            sa.Column("volume", sa.Numeric, nullable=True),
            sa.Column("date", sa.DateTime(timezone=True), nullable=True),
            sa.Column("statut", sa.String(200), nullable=True),
            sa.Column("is_active", sa.Boolean, nullable=True),
            sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
            sa.Column("updated_at", sa.DateTime(timezone=True), nullable=True),
            sa.UniqueConstraint("company_id", "reference", name="uix_magc_spill_cleanups_uniq"),
        )

    if not _has("magc_loading_checks"):
        op.create_table(
            "magc_loading_checks",
            sa.Column("id", sa.Integer, primary_key=True, index=True),
            sa.Column("company_id", sa.Integer, nullable=False, index=True),
            sa.Column("reference", sa.String(200), nullable=False, index=True),
            sa.Column("chargement", sa.String(200), nullable=True),
            sa.Column("camion", sa.String(200), nullable=True),
            sa.Column("nb_colis", sa.Integer, nullable=True),
            sa.Column("chargeur", sa.String(200), nullable=True),
            sa.Column("statut", sa.String(200), nullable=True),
            sa.Column("is_active", sa.Boolean, nullable=True),
            sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
            sa.Column("updated_at", sa.DateTime(timezone=True), nullable=True),
            sa.UniqueConstraint("company_id", "reference", name="uix_magc_loading_checks_uniq"),
        )

    if not _has("magc_receiving_checks"):
        op.create_table(
            "magc_receiving_checks",
            sa.Column("id", sa.Integer, primary_key=True, index=True),
            sa.Column("company_id", sa.Integer, nullable=False, index=True),
            sa.Column("reference", sa.String(200), nullable=False, index=True),
            sa.Column("reception", sa.String(200), nullable=True),
            sa.Column("fournisseur", sa.String(200), nullable=True),
            sa.Column("nb_colis", sa.Integer, nullable=True),
            sa.Column("conforme", sa.Boolean, nullable=True),
            sa.Column("statut", sa.String(200), nullable=True),
            sa.Column("is_active", sa.Boolean, nullable=True),
            sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
            sa.Column("updated_at", sa.DateTime(timezone=True), nullable=True),
            sa.UniqueConstraint("company_id", "reference", name="uix_magc_receiving_checks_uniq"),
        )

    if not _has("magc_putaway_exceptions"):
        op.create_table(
            "magc_putaway_exceptions",
            sa.Column("id", sa.Integer, primary_key=True, index=True),
            sa.Column("company_id", sa.Integer, nullable=False, index=True),
            sa.Column("reference", sa.String(200), nullable=False, index=True),
            sa.Column("article", sa.String(200), nullable=True),
            sa.Column("emplacement", sa.String(200), nullable=True),
            sa.Column("type_probleme", sa.String(200), nullable=True),
            sa.Column("signale_le", sa.DateTime(timezone=True), nullable=True),
            sa.Column("statut", sa.String(200), nullable=True),
            sa.Column("is_active", sa.Boolean, nullable=True),
            sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
            sa.Column("updated_at", sa.DateTime(timezone=True), nullable=True),
            sa.UniqueConstraint("company_id", "reference", name="uix_magc_putaway_exceptions_uniq"),
        )

    if not _has("magc_order_staging"):
        op.create_table(
            "magc_order_staging",
            sa.Column("id", sa.Integer, primary_key=True, index=True),
            sa.Column("company_id", sa.Integer, nullable=False, index=True),
            sa.Column("reference", sa.String(200), nullable=False, index=True),
            sa.Column("commande", sa.String(200), nullable=True),
            sa.Column("zone_prea", sa.String(200), nullable=True),
            sa.Column("nb_lignes", sa.Integer, nullable=True),
            sa.Column("operateur", sa.String(200), nullable=True),
            sa.Column("statut", sa.String(200), nullable=True),
            sa.Column("is_active", sa.Boolean, nullable=True),
            sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
            sa.Column("updated_at", sa.DateTime(timezone=True), nullable=True),
            sa.UniqueConstraint("company_id", "reference", name="uix_magc_order_staging_uniq"),
        )

    if not _has("magc_cold_checks"):
        op.create_table(
            "magc_cold_checks",
            sa.Column("id", sa.Integer, primary_key=True, index=True),
            sa.Column("company_id", sa.Integer, nullable=False, index=True),
            sa.Column("reference", sa.String(200), nullable=False, index=True),
            sa.Column("chambre_froide", sa.String(200), nullable=True),
            sa.Column("temperature_c", sa.Numeric, nullable=True),
            sa.Column("seuil_mini", sa.Numeric, nullable=True),
            sa.Column("seuil_maxi", sa.Numeric, nullable=True),
            sa.Column("statut", sa.String(200), nullable=True),
            sa.Column("is_active", sa.Boolean, nullable=True),
            sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
            sa.Column("updated_at", sa.DateTime(timezone=True), nullable=True),
            sa.UniqueConstraint("company_id", "reference", name="uix_magc_cold_checks_uniq"),
        )

    if not _has("magc_hazmat_handling"):
        op.create_table(
            "magc_hazmat_handling",
            sa.Column("id", sa.Integer, primary_key=True, index=True),
            sa.Column("company_id", sa.Integer, nullable=False, index=True),
            sa.Column("reference", sa.String(200), nullable=False, index=True),
            sa.Column("matiere", sa.String(200), nullable=True),
            sa.Column("classe", sa.String(200), nullable=True),
            sa.Column("quantite", sa.Numeric, nullable=True),
            sa.Column("operateur", sa.String(200), nullable=True),
            sa.Column("statut", sa.String(200), nullable=True),
            sa.Column("is_active", sa.Boolean, nullable=True),
            sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
            sa.Column("updated_at", sa.DateTime(timezone=True), nullable=True),
            sa.UniqueConstraint("company_id", "reference", name="uix_magc_hazmat_handling_uniq"),
        )

    if not _has("magc_dock_assignments"):
        op.create_table(
            "magc_dock_assignments",
            sa.Column("id", sa.Integer, primary_key=True, index=True),
            sa.Column("company_id", sa.Integer, nullable=False, index=True),
            sa.Column("reference", sa.String(200), nullable=False, index=True),
            sa.Column("quai", sa.String(200), nullable=True),
            sa.Column("camion", sa.String(200), nullable=True),
            sa.Column("creneau", sa.DateTime(timezone=True), nullable=True),
            sa.Column("operateur", sa.String(200), nullable=True),
            sa.Column("statut", sa.String(200), nullable=True),
            sa.Column("is_active", sa.Boolean, nullable=True),
            sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
            sa.Column("updated_at", sa.DateTime(timezone=True), nullable=True),
            sa.UniqueConstraint("company_id", "reference", name="uix_magc_dock_assignments_uniq"),
        )


def downgrade():
    for t in reversed(TABLES):
        if _has(t):
            op.drop_table(t)
