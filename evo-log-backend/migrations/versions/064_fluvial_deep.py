"""064 : tables expansion transport-fluvial (genere)."""
from alembic import op
import sqlalchemy as sa


revision = "064_fluvial_deep"
down_revision = "063_aerien_deep"
branch_labels = None
depends_on = None


TABLES = [
    "fluv_barges",
    "fluv_towboats",
    "fluv_lock_transits",
    "fluv_depth_surveys",
    "fluv_terminals",
    "fluv_bulk_operations",
    "fluv_safety_records",
    "fluv_tariffs",
    "fluv_waybills",
    "fluv_positions",
]


def _has(name):
    insp = sa.inspect(op.get_bind())
    return name in set(insp.get_table_names())


def upgrade():
    if not _has("fluv_barges"):
        op.create_table(
            "fluv_barges",
            sa.Column("id", sa.Integer, primary_key=True, index=True),
            sa.Column("company_id", sa.Integer, nullable=False, index=True),
            sa.Column("numero_flotte", sa.String(200), nullable=False, index=True),
            sa.Column("type", sa.String(200), nullable=True),
            sa.Column("capacite_tonnes", sa.Integer, nullable=True),
            sa.Column("tirant_eau_max_m", sa.String(200), nullable=True),
            sa.Column("longueur_m", sa.Integer, nullable=True),
            sa.Column("largeur_m", sa.Integer, nullable=True),
            sa.Column("statut", sa.String(200), nullable=True),
            sa.Column("is_active", sa.Boolean, nullable=True),
            sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
            sa.Column("updated_at", sa.DateTime(timezone=True), nullable=True),
            sa.UniqueConstraint("company_id", "numero_flotte", name="uix_fluv_barges_uniq"),
        )

    if not _has("fluv_towboats"):
        op.create_table(
            "fluv_towboats",
            sa.Column("id", sa.Integer, primary_key=True, index=True),
            sa.Column("company_id", sa.Integer, nullable=False, index=True),
            sa.Column("numero_tug", sa.String(200), nullable=False, index=True),
            sa.Column("nom", sa.String(200), nullable=True),
            sa.Column("puissance_kw", sa.Integer, nullable=True),
            sa.Column("bollard_pull_t", sa.Integer, nullable=True),
            sa.Column("zone_operation", sa.String(200), nullable=True),
            sa.Column("statut", sa.String(200), nullable=True),
            sa.Column("is_active", sa.Boolean, nullable=True),
            sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
            sa.Column("updated_at", sa.DateTime(timezone=True), nullable=True),
            sa.UniqueConstraint("company_id", "numero_tug", name="uix_fluv_towboats_uniq"),
        )

    if not _has("fluv_lock_transits"):
        op.create_table(
            "fluv_lock_transits",
            sa.Column("id", sa.Integer, primary_key=True, index=True),
            sa.Column("company_id", sa.Integer, nullable=False, index=True),
            sa.Column("reference", sa.String(200), nullable=False, index=True),
            sa.Column("nom_ecluse", sa.String(200), nullable=True),
            sa.Column("date_passage", sa.DateTime(timezone=True), nullable=True),
            sa.Column("numero_peniche", sa.String(200), nullable=True),
            sa.Column("masse_tonnes", sa.Integer, nullable=True),
            sa.Column("tirant_eau_m", sa.String(200), nullable=True),
            sa.Column("attente_minutes", sa.Integer, nullable=True),
            sa.Column("statut", sa.String(200), nullable=True),
            sa.Column("is_active", sa.Boolean, nullable=True),
            sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
            sa.Column("updated_at", sa.DateTime(timezone=True), nullable=True),
            sa.UniqueConstraint("company_id", "reference", name="uix_fluv_lock_transits_uniq"),
        )

    if not _has("fluv_depth_surveys"):
        op.create_table(
            "fluv_depth_surveys",
            sa.Column("id", sa.Integer, primary_key=True, index=True),
            sa.Column("company_id", sa.Integer, nullable=False, index=True),
            sa.Column("reference", sa.String(200), nullable=False, index=True),
            sa.Column("bief", sa.String(200), nullable=True),
            sa.Column("date_mesure", sa.Date, nullable=True),
            sa.Column("profondeur_min_cm", sa.Integer, nullable=True),
            sa.Column("tirant_eau_pmax_cm", sa.Integer, nullable=True),
            sa.Column("debit_m3s", sa.Integer, nullable=True),
            sa.Column("statut", sa.String(200), nullable=True),
            sa.Column("is_active", sa.Boolean, nullable=True),
            sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
            sa.Column("updated_at", sa.DateTime(timezone=True), nullable=True),
            sa.UniqueConstraint("company_id", "reference", name="uix_fluv_depth_surveys_uniq"),
        )

    if not _has("fluv_terminals"):
        op.create_table(
            "fluv_terminals",
            sa.Column("id", sa.Integer, primary_key=True, index=True),
            sa.Column("company_id", sa.Integer, nullable=False, index=True),
            sa.Column("code_terminal", sa.String(200), nullable=False, index=True),
            sa.Column("nom", sa.String(200), nullable=True),
            sa.Column("fleuve", sa.String(200), nullable=True),
            sa.Column("pays", sa.String(200), nullable=True),
            sa.Column("nb_appontements", sa.Integer, nullable=True),
            sa.Column("longueur_quai_m", sa.Integer, nullable=True),
            sa.Column("connecte_port_maritime", sa.Boolean, nullable=True),
            sa.Column("statut", sa.String(200), nullable=True),
            sa.Column("is_active", sa.Boolean, nullable=True),
            sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
            sa.Column("updated_at", sa.DateTime(timezone=True), nullable=True),
            sa.UniqueConstraint("company_id", "code_terminal", name="uix_fluv_terminals_uniq"),
        )

    if not _has("fluv_bulk_operations"):
        op.create_table(
            "fluv_bulk_operations",
            sa.Column("id", sa.Integer, primary_key=True, index=True),
            sa.Column("company_id", sa.Integer, nullable=False, index=True),
            sa.Column("reference", sa.String(200), nullable=False, index=True),
            sa.Column("produit", sa.String(200), nullable=True),
            sa.Column("categorie", sa.String(200), nullable=True),
            sa.Column("quantite_tonnes", sa.Integer, nullable=True),
            sa.Column("terminal", sa.String(200), nullable=True),
            sa.Column("date_operation", sa.DateTime(timezone=True), nullable=True),
            sa.Column("duree_heures", sa.Integer, nullable=True),
            sa.Column("statut", sa.String(200), nullable=True),
            sa.Column("is_active", sa.Boolean, nullable=True),
            sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
            sa.Column("updated_at", sa.DateTime(timezone=True), nullable=True),
            sa.UniqueConstraint("company_id", "reference", name="uix_fluv_bulk_operations_uniq"),
        )

    if not _has("fluv_safety_records"):
        op.create_table(
            "fluv_safety_records",
            sa.Column("id", sa.Integer, primary_key=True, index=True),
            sa.Column("company_id", sa.Integer, nullable=False, index=True),
            sa.Column("reference", sa.String(200), nullable=False, index=True),
            sa.Column("date_evenement", sa.DateTime(timezone=True), nullable=True),
            sa.Column("bief", sa.String(200), nullable=True),
            sa.Column("type_evenement", sa.String(200), nullable=True),
            sa.Column("gravite", sa.String(200), nullable=True),
            sa.Column("batiments_impliques", sa.Text, nullable=True),
            sa.Column("description", sa.Text, nullable=True),
            sa.Column("statut", sa.String(200), nullable=True),
            sa.Column("is_active", sa.Boolean, nullable=True),
            sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
            sa.Column("updated_at", sa.DateTime(timezone=True), nullable=True),
            sa.UniqueConstraint("company_id", "reference", name="uix_fluv_safety_records_uniq"),
        )

    if not _has("fluv_tariffs"):
        op.create_table(
            "fluv_tariffs",
            sa.Column("id", sa.Integer, primary_key=True, index=True),
            sa.Column("company_id", sa.Integer, nullable=False, index=True),
            sa.Column("code_tarif", sa.String(200), nullable=False, index=True),
            sa.Column("bief", sa.String(200), nullable=True),
            sa.Column("produit", sa.String(200), nullable=True),
            sa.Column("prix_par_tonne_xaf", sa.Integer, nullable=True),
            sa.Column("saisonnalite", sa.String(200), nullable=True),
            sa.Column("remise_volume_pct", sa.Integer, nullable=True),
            sa.Column("validite_debut", sa.Date, nullable=True),
            sa.Column("validite_fin", sa.Date, nullable=True),
            sa.Column("statut", sa.String(200), nullable=True),
            sa.Column("is_active", sa.Boolean, nullable=True),
            sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
            sa.Column("updated_at", sa.DateTime(timezone=True), nullable=True),
            sa.UniqueConstraint("company_id", "code_tarif", name="uix_fluv_tariffs_uniq"),
        )

    if not _has("fluv_waybills"):
        op.create_table(
            "fluv_waybills",
            sa.Column("id", sa.Integer, primary_key=True, index=True),
            sa.Column("company_id", sa.Integer, nullable=False, index=True),
            sa.Column("numero", sa.String(200), nullable=False, index=True),
            sa.Column("expediteur", sa.String(200), nullable=True),
            sa.Column("destinataire", sa.String(200), nullable=True),
            sa.Column("port_depart", sa.String(200), nullable=True),
            sa.Column("port_arrivee", sa.String(200), nullable=True),
            sa.Column("produit", sa.String(200), nullable=True),
            sa.Column("quantite_tonnes", sa.Integer, nullable=True),
            sa.Column("date_emission", sa.Date, nullable=True),
            sa.Column("statut", sa.String(200), nullable=True),
            sa.Column("is_active", sa.Boolean, nullable=True),
            sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
            sa.Column("updated_at", sa.DateTime(timezone=True), nullable=True),
            sa.UniqueConstraint("company_id", "numero", name="uix_fluv_waybills_uniq"),
        )

    if not _has("fluv_positions"):
        op.create_table(
            "fluv_positions",
            sa.Column("id", sa.Integer, primary_key=True, index=True),
            sa.Column("company_id", sa.Integer, nullable=False, index=True),
            sa.Column("reference", sa.String(200), nullable=False, index=True),
            sa.Column("numero_flotte", sa.String(200), nullable=True),
            sa.Column("date_releve", sa.DateTime(timezone=True), nullable=True),
            sa.Column("latitude", sa.String(200), nullable=True),
            sa.Column("longitude", sa.String(200), nullable=True),
            sa.Column("vitesse_nd", sa.String(200), nullable=True),
            sa.Column("cap", sa.String(200), nullable=True),
            sa.Column("statut", sa.String(200), nullable=True),
            sa.Column("is_active", sa.Boolean, nullable=True),
            sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
            sa.Column("updated_at", sa.DateTime(timezone=True), nullable=True),
            sa.UniqueConstraint("company_id", "reference", name="uix_fluv_positions_uniq"),
        )


def downgrade():
    for t in reversed(TABLES):
        if _has(t):
            op.drop_table(t)
