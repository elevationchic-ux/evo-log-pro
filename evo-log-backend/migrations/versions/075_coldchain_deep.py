"""075 : tables expansion chaine-froid (genere)."""
from alembic import op
import sqlalchemy as sa


revision = "075_coldchain_deep"
down_revision = "074_courier_deep"
branch_labels = None
depends_on = None


TABLES = [
    "coldchain_chambers",
    "coldchain_reefers",
    "coldchain_loggers",
    "coldchain_products",
    "coldchain_excursions",
    "coldchain_vaccin_batches",
    "coldchain_haccp_records",
    "coldchain_defrost_cycles",
    "coldchain_energy_meters",
    "coldchain_transport_legs",
]


def _has(name):
    insp = sa.inspect(op.get_bind())
    return name in set(insp.get_table_names())


def upgrade():
    if not _has("coldchain_chambers"):
        op.create_table(
            "coldchain_chambers",
            sa.Column("id", sa.Integer, primary_key=True, index=True),
            sa.Column("company_id", sa.Integer, nullable=False, index=True),
            sa.Column("code_chambre", sa.String(150), nullable=False, index=True),
            sa.Column("type_chambre", sa.String(150), nullable=True),
            sa.Column("plage", sa.String(150), nullable=True),
            sa.Column("temperature_consigne_c", sa.Integer, nullable=True),
            sa.Column("temperature_actuelle_c", sa.Integer, nullable=True),
            sa.Column("capacite_m3", sa.Integer, nullable=True),
            sa.Column("puissance_kw", sa.Integer, nullable=True),
            sa.Column("date_mise_service", sa.Date, nullable=True),
            sa.Column("prochaine_maintenance", sa.Date, nullable=True),
            sa.Column("statut", sa.String(150), nullable=True),
            sa.Column("is_active", sa.Boolean, nullable=True),
            sa.Column("created_at", sa.DateTime(timezone=True), nullable=True),
            sa.Column("updated_at", sa.DateTime(timezone=True), nullable=True),
            sa.UniqueConstraint("company_id", "code_chambre", name="uix_coldchain_chambers_uniq"),
        )

    if not _has("coldchain_reefers"):
        op.create_table(
            "coldchain_reefers",
            sa.Column("id", sa.Integer, primary_key=True, index=True),
            sa.Column("company_id", sa.Integer, nullable=False, index=True),
            sa.Column("numero_reefer", sa.String(150), nullable=False, index=True),
            sa.Column("type_reefer", sa.String(150), nullable=True),
            sa.Column("mode", sa.String(150), nullable=True),
            sa.Column("plage_temperature_c", sa.String(150), nullable=True),
            sa.Column("capacite_m3", sa.Integer, nullable=True),
            sa.Column("date_last_check", sa.Date, nullable=True),
            sa.Column("prochaine_pt", sa.Date, nullable=True),
            sa.Column("statut", sa.String(150), nullable=True),
            sa.Column("is_active", sa.Boolean, nullable=True),
            sa.Column("created_at", sa.DateTime(timezone=True), nullable=True),
            sa.Column("updated_at", sa.DateTime(timezone=True), nullable=True),
            sa.UniqueConstraint("company_id", "numero_reefer", name="uix_coldchain_reefers_uniq"),
        )

    if not _has("coldchain_loggers"):
        op.create_table(
            "coldchain_loggers",
            sa.Column("id", sa.Integer, primary_key=True, index=True),
            sa.Column("company_id", sa.Integer, nullable=False, index=True),
            sa.Column("numero_logger", sa.String(150), nullable=False, index=True),
            sa.Column("technologie", sa.String(150), nullable=True),
            sa.Column("frequence_lecture_s", sa.Integer, nullable=True),
            sa.Column("autonomie_jours", sa.Integer, nullable=True),
            sa.Column("precision_c", sa.Integer, nullable=True),
            sa.Column("date_achat", sa.Date, nullable=True),
            sa.Column("date_calibration", sa.Date, nullable=True),
            sa.Column("prochaine_calibration", sa.Date, nullable=True),
            sa.Column("assigned_to", sa.String(150), nullable=True),
            sa.Column("statut", sa.String(150), nullable=True),
            sa.Column("is_active", sa.Boolean, nullable=True),
            sa.Column("created_at", sa.DateTime(timezone=True), nullable=True),
            sa.Column("updated_at", sa.DateTime(timezone=True), nullable=True),
            sa.UniqueConstraint("company_id", "numero_logger", name="uix_coldchain_loggers_uniq"),
        )

    if not _has("coldchain_products"):
        op.create_table(
            "coldchain_products",
            sa.Column("id", sa.Integer, primary_key=True, index=True),
            sa.Column("company_id", sa.Integer, nullable=False, index=True),
            sa.Column("code_sku", sa.String(150), nullable=False, index=True),
            sa.Column("nom", sa.String(150), nullable=True),
            sa.Column("categorie", sa.String(150), nullable=True),
            sa.Column("classe", sa.String(150), nullable=True),
            sa.Column("temp_min_c", sa.Integer, nullable=True),
            sa.Column("temp_max_c", sa.Integer, nullable=True),
            sa.Column("duree_vie_jours", sa.Integer, nullable=True),
            sa.Column("seuil_excursion_h", sa.Integer, nullable=True),
            sa.Column("is_active", sa.Boolean, nullable=True),
            sa.Column("created_at", sa.DateTime(timezone=True), nullable=True),
            sa.Column("updated_at", sa.DateTime(timezone=True), nullable=True),
            sa.UniqueConstraint("company_id", "code_sku", name="uix_coldchain_products_uniq"),
        )

    if not _has("coldchain_excursions"):
        op.create_table(
            "coldchain_excursions",
            sa.Column("id", sa.Integer, primary_key=True, index=True),
            sa.Column("company_id", sa.Integer, nullable=False, index=True),
            sa.Column("reference", sa.String(150), nullable=False, index=True),
            sa.Column("type", sa.String(150), nullable=True),
            sa.Column("produit_concerne", sa.String(150), nullable=True),
            sa.Column("actif_associe", sa.String(150), nullable=True),
            sa.Column("date_debut", sa.DateTime(timezone=True), nullable=True),
            sa.Column("date_fin", sa.DateTime(timezone=True), nullable=True),
            sa.Column("temp_extreme_c", sa.Integer, nullable=True),
            sa.Column("duree_h", sa.Integer, nullable=True),
            sa.Column("impact", sa.String(150), nullable=True),
            sa.Column("valeur_perdue_xaf", sa.Integer, nullable=True),
            sa.Column("statut", sa.String(150), nullable=True),
            sa.Column("is_active", sa.Boolean, nullable=True),
            sa.Column("created_at", sa.DateTime(timezone=True), nullable=True),
            sa.Column("updated_at", sa.DateTime(timezone=True), nullable=True),
            sa.UniqueConstraint("company_id", "reference", name="uix_coldchain_excursions_uniq"),
        )

    if not _has("coldchain_vaccin_batches"):
        op.create_table(
            "coldchain_vaccin_batches",
            sa.Column("id", sa.Integer, primary_key=True, index=True),
            sa.Column("company_id", sa.Integer, nullable=False, index=True),
            sa.Column("numero_lot", sa.String(150), nullable=False, index=True),
            sa.Column("fabricant", sa.String(150), nullable=True),
            sa.Column("type_vaccin", sa.String(150), nullable=True),
            sa.Column("nb_doses", sa.Integer, nullable=True),
            sa.Column("date_fabrication", sa.Date, nullable=True),
            sa.Column("date_peremption", sa.Date, nullable=True),
            sa.Column("temp_stockage_c", sa.Integer, nullable=True),
            sa.Column("vvm_statut", sa.String(150), nullable=True),
            sa.Column("lieu_stockage", sa.String(150), nullable=True),
            sa.Column("statut", sa.String(150), nullable=True),
            sa.Column("is_active", sa.Boolean, nullable=True),
            sa.Column("created_at", sa.DateTime(timezone=True), nullable=True),
            sa.Column("updated_at", sa.DateTime(timezone=True), nullable=True),
            sa.UniqueConstraint("company_id", "numero_lot", name="uix_coldchain_vaccin_batches_uniq"),
        )

    if not _has("coldchain_haccp_records"):
        op.create_table(
            "coldchain_haccp_records",
            sa.Column("id", sa.Integer, primary_key=True, index=True),
            sa.Column("company_id", sa.Integer, nullable=False, index=True),
            sa.Column("reference", sa.String(150), nullable=False, index=True),
            sa.Column("pratique", sa.String(150), nullable=True),
            sa.Column("date_lecture", sa.DateTime(timezone=True), nullable=True),
            sa.Column("valeur_lue", sa.String(150), nullable=True),
            sa.Column("seuil_mini", sa.String(150), nullable=True),
            sa.Column("seuil_maxi", sa.String(150), nullable=True),
            sa.Column("operateur", sa.String(150), nullable=True),
            sa.Column("action_corrective", sa.String(2000), nullable=True),
            sa.Column("resultat", sa.String(150), nullable=True),
            sa.Column("is_active", sa.Boolean, nullable=True),
            sa.Column("created_at", sa.DateTime(timezone=True), nullable=True),
            sa.Column("updated_at", sa.DateTime(timezone=True), nullable=True),
            sa.UniqueConstraint("company_id", "reference", name="uix_coldchain_haccp_records_uniq"),
        )

    if not _has("coldchain_defrost_cycles"):
        op.create_table(
            "coldchain_defrost_cycles",
            sa.Column("id", sa.Integer, primary_key=True, index=True),
            sa.Column("company_id", sa.Integer, nullable=False, index=True),
            sa.Column("reference", sa.String(150), nullable=False, index=True),
            sa.Column("chambre_associee", sa.String(150), nullable=True),
            sa.Column("frequence", sa.String(150), nullable=True),
            sa.Column("type", sa.String(150), nullable=True),
            sa.Column("date_prevue", sa.Date, nullable=True),
            sa.Column("date_reelle_debut", sa.DateTime(timezone=True), nullable=True),
            sa.Column("date_reelle_fin", sa.DateTime(timezone=True), nullable=True),
            sa.Column("duree_h", sa.Integer, nullable=True),
            sa.Column("energie_kwh", sa.Integer, nullable=True),
            sa.Column("statut", sa.String(150), nullable=True),
            sa.Column("is_active", sa.Boolean, nullable=True),
            sa.Column("created_at", sa.DateTime(timezone=True), nullable=True),
            sa.Column("updated_at", sa.DateTime(timezone=True), nullable=True),
            sa.UniqueConstraint("company_id", "reference", name="uix_coldchain_defrost_cycles_uniq"),
        )

    if not _has("coldchain_energy_meters"):
        op.create_table(
            "coldchain_energy_meters",
            sa.Column("id", sa.Integer, primary_key=True, index=True),
            sa.Column("company_id", sa.Integer, nullable=False, index=True),
            sa.Column("code_compteur", sa.String(150), nullable=False, index=True),
            sa.Column("type_energie", sa.String(150), nullable=True),
            sa.Column("actif_alimente", sa.String(150), nullable=True),
            sa.Column("consommation_kwh", sa.Integer, nullable=True),
            sa.Column("cout_mensuel_xaf", sa.Integer, nullable=True),
            sa.Column("co2_eq_kg", sa.Integer, nullable=True),
            sa.Column("date_releve", sa.Date, nullable=True),
            sa.Column("is_active", sa.Boolean, nullable=True),
            sa.Column("created_at", sa.DateTime(timezone=True), nullable=True),
            sa.Column("updated_at", sa.DateTime(timezone=True), nullable=True),
            sa.UniqueConstraint("company_id", "code_compteur", name="uix_coldchain_energy_meters_uniq"),
        )

    if not _has("coldchain_transport_legs"):
        op.create_table(
            "coldchain_transport_legs",
            sa.Column("id", sa.Integer, primary_key=True, index=True),
            sa.Column("company_id", sa.Integer, nullable=False, index=True),
            sa.Column("reference", sa.String(150), nullable=False, index=True),
            sa.Column("mode", sa.String(150), nullable=True),
            sa.Column("reefer_utilise", sa.String(150), nullable=True),
            sa.Column("produit_transporte", sa.String(150), nullable=True),
            sa.Column("poids_kg", sa.Integer, nullable=True),
            sa.Column("origine", sa.String(150), nullable=True),
            sa.Column("destination", sa.String(150), nullable=True),
            sa.Column("date_depart", sa.DateTime(timezone=True), nullable=True),
            sa.Column("date_arrivee", sa.DateTime(timezone=True), nullable=True),
            sa.Column("temp_moyenne_c", sa.Integer, nullable=True),
            sa.Column("statut", sa.String(150), nullable=True),
            sa.Column("is_active", sa.Boolean, nullable=True),
            sa.Column("created_at", sa.DateTime(timezone=True), nullable=True),
            sa.Column("updated_at", sa.DateTime(timezone=True), nullable=True),
            sa.UniqueConstraint("company_id", "reference", name="uix_coldchain_transport_legs_uniq"),
        )


def downgrade():
    for t in reversed(TABLES):
        if _has(t):
            op.drop_table(t)
