"""062 : tables expansion transport-ferroviaire (genere)."""
from alembic import op
import sqlalchemy as sa


revision = "062_ferroviaire_deep"
down_revision = "061_amenagement_extra_deep"
branch_labels = None
depends_on = None


TABLES = [
    "rail_wagons",
    "rail_locomotives",
    "rail_train_paths",
    "rail_shunting_yards",
    "rail_terminals",
    "rail_consistency_plans",
    "rail_waybills",
    "rail_tariffs",
    "rail_wagon_tracking",
    "rail_wagon_maintenance",
    "rail_safety_records",
    "rail_corridors",
]


def _has(name):
    insp = sa.inspect(op.get_bind())
    return name in set(insp.get_table_names())


def upgrade():
    if not _has("rail_wagons"):
        op.create_table(
            "rail_wagons",
            sa.Column("id", sa.Integer, primary_key=True, index=True),
            sa.Column("company_id", sa.Integer, nullable=False, index=True),
            sa.Column("numeration_wagon", sa.String(200), nullable=False, index=True),
            sa.Column("type_wagon", sa.String(200), nullable=True),
            sa.Column("capacite_tonnes", sa.Integer, nullable=True),
            sa.Column("livree", sa.String(200), nullable=True),
            sa.Column("date_mise_circulation", sa.Date, nullable=True),
            sa.Column("prochaine_revision", sa.Date, nullable=True),
            sa.Column("statut", sa.String(200), nullable=True),
            sa.Column("is_active", sa.Boolean, nullable=True),
            sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
            sa.Column("updated_at", sa.DateTime(timezone=True), nullable=True),
            sa.UniqueConstraint("company_id", "numeration_wagon", name="uix_rail_wagons_uniq"),
        )

    if not _has("rail_locomotives"):
        op.create_table(
            "rail_locomotives",
            sa.Column("id", sa.Integer, primary_key=True, index=True),
            sa.Column("company_id", sa.Integer, nullable=False, index=True),
            sa.Column("numero_series", sa.String(200), nullable=False, index=True),
            sa.Column("modele", sa.String(200), nullable=True),
            sa.Column("type_energie", sa.String(200), nullable=True),
            sa.Column("puissance_kw", sa.Integer, nullable=True),
            sa.Column("vitesse_max_kmh", sa.Integer, nullable=True),
            sa.Column("kilometrage_actuel", sa.Integer, nullable=True),
            sa.Column("prochaine_revision_km", sa.Integer, nullable=True),
            sa.Column("statut", sa.String(200), nullable=True),
            sa.Column("is_active", sa.Boolean, nullable=True),
            sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
            sa.Column("updated_at", sa.DateTime(timezone=True), nullable=True),
            sa.UniqueConstraint("company_id", "numero_series", name="uix_rail_locomotives_uniq"),
        )

    if not _has("rail_train_paths"):
        op.create_table(
            "rail_train_paths",
            sa.Column("id", sa.Integer, primary_key=True, index=True),
            sa.Column("company_id", sa.Integer, nullable=False, index=True),
            sa.Column("code_sillon", sa.String(200), nullable=False, index=True),
            sa.Column("gare_origine", sa.String(200), nullable=True),
            sa.Column("gare_destination", sa.String(200), nullable=True),
            sa.Column("date_circulation", sa.Date, nullable=True),
            sa.Column("heure_depart", sa.String(200), nullable=True),
            sa.Column("heure_arrivee", sa.String(200), nullable=True),
            sa.Column("numero_train", sa.String(200), nullable=True),
            sa.Column("statut", sa.String(200), nullable=True),
            sa.Column("is_active", sa.Boolean, nullable=True),
            sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
            sa.Column("updated_at", sa.DateTime(timezone=True), nullable=True),
            sa.UniqueConstraint("company_id", "code_sillon", name="uix_rail_train_paths_uniq"),
        )

    if not _has("rail_shunting_yards"):
        op.create_table(
            "rail_shunting_yards",
            sa.Column("id", sa.Integer, primary_key=True, index=True),
            sa.Column("company_id", sa.Integer, nullable=False, index=True),
            sa.Column("code_triage", sa.String(200), nullable=False, index=True),
            sa.Column("nom", sa.String(200), nullable=True),
            sa.Column("localisation", sa.String(200), nullable=True),
            sa.Column("nb_voies_tri", sa.Integer, nullable=True),
            sa.Column("nb_voies_parc", sa.Integer, nullable=True),
            sa.Column("capacite_journee_wagons", sa.Integer, nullable=True),
            sa.Column("taux_occupation_pct", sa.Integer, nullable=True),
            sa.Column("statut", sa.String(200), nullable=True),
            sa.Column("is_active", sa.Boolean, nullable=True),
            sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
            sa.Column("updated_at", sa.DateTime(timezone=True), nullable=True),
            sa.UniqueConstraint("company_id", "code_triage", name="uix_rail_shunting_yards_uniq"),
        )

    if not _has("rail_terminals"):
        op.create_table(
            "rail_terminals",
            sa.Column("id", sa.Integer, primary_key=True, index=True),
            sa.Column("company_id", sa.Integer, nullable=False, index=True),
            sa.Column("code_terminal", sa.String(200), nullable=False, index=True),
            sa.Column("port_associe", sa.String(200), nullable=True),
            sa.Column("nb_voies_fond", sa.Integer, nullable=True),
            sa.Column("longueur_quai_m", sa.Integer, nullable=True),
            sa.Column("equipement_manutention", sa.String(200), nullable=True),
            sa.Column("debit_conteneur_h", sa.Integer, nullable=True),
            sa.Column("statut", sa.String(200), nullable=True),
            sa.Column("is_active", sa.Boolean, nullable=True),
            sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
            sa.Column("updated_at", sa.DateTime(timezone=True), nullable=True),
            sa.UniqueConstraint("company_id", "code_terminal", name="uix_rail_terminals_uniq"),
        )

    if not _has("rail_consistency_plans"):
        op.create_table(
            "rail_consistency_plans",
            sa.Column("id", sa.Integer, primary_key=True, index=True),
            sa.Column("company_id", sa.Integer, nullable=False, index=True),
            sa.Column("reference", sa.String(200), nullable=False, index=True),
            sa.Column("code_sillon", sa.String(200), nullable=True),
            sa.Column("type_train", sa.String(200), nullable=True),
            sa.Column("nb_wagons", sa.Integer, nullable=True),
            sa.Column("masse_totale_tonnes", sa.Integer, nullable=True),
            sa.Column("longueur_totale_m", sa.Integer, nullable=True),
            sa.Column("locomotive_atteltee", sa.String(200), nullable=True),
            sa.Column("statut", sa.String(200), nullable=True),
            sa.Column("is_active", sa.Boolean, nullable=True),
            sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
            sa.Column("updated_at", sa.DateTime(timezone=True), nullable=True),
            sa.UniqueConstraint("company_id", "reference", name="uix_rail_consistency_plans_uniq"),
        )

    if not _has("rail_waybills"):
        op.create_table(
            "rail_waybills",
            sa.Column("id", sa.Integer, primary_key=True, index=True),
            sa.Column("company_id", sa.Integer, nullable=False, index=True),
            sa.Column("numero_lcv", sa.String(200), nullable=False, index=True),
            sa.Column("expediteur", sa.String(200), nullable=True),
            sa.Column("destinataire", sa.String(200), nullable=True),
            sa.Column("gare_depart", sa.String(200), nullable=True),
            sa.Column("gare_arrivee", sa.String(200), nullable=True),
            sa.Column("date_emission", sa.Date, nullable=True),
            sa.Column("valeur_marchandise_xaf", sa.Integer, nullable=True),
            sa.Column("statut", sa.String(200), nullable=True),
            sa.Column("is_active", sa.Boolean, nullable=True),
            sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
            sa.Column("updated_at", sa.DateTime(timezone=True), nullable=True),
            sa.UniqueConstraint("company_id", "numero_lcv", name="uix_rail_waybills_uniq"),
        )

    if not _has("rail_tariffs"):
        op.create_table(
            "rail_tariffs",
            sa.Column("id", sa.Integer, primary_key=True, index=True),
            sa.Column("company_id", sa.Integer, nullable=False, index=True),
            sa.Column("code_tarif", sa.String(200), nullable=False, index=True),
            sa.Column("relation", sa.String(200), nullable=True),
            sa.Column("type_marchandise", sa.String(200), nullable=True),
            sa.Column("prix_par_tonne_km_xaf", sa.Integer, nullable=True),
            sa.Column("remise_volume_pct", sa.Integer, nullable=True),
            sa.Column("date_debut_validite", sa.Date, nullable=True),
            sa.Column("date_fin_validite", sa.Date, nullable=True),
            sa.Column("statut", sa.String(200), nullable=True),
            sa.Column("is_active", sa.Boolean, nullable=True),
            sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
            sa.Column("updated_at", sa.DateTime(timezone=True), nullable=True),
            sa.UniqueConstraint("company_id", "code_tarif", name="uix_rail_tariffs_uniq"),
        )

    if not _has("rail_wagon_tracking"):
        op.create_table(
            "rail_wagon_tracking",
            sa.Column("id", sa.Integer, primary_key=True, index=True),
            sa.Column("company_id", sa.Integer, nullable=False, index=True),
            sa.Column("reference", sa.String(200), nullable=False, index=True),
            sa.Column("numeration_wagon", sa.String(200), nullable=True),
            sa.Column("code_lcv", sa.String(200), nullable=True),
            sa.Column("gare_actuelle", sa.String(200), nullable=True),
            sa.Column("date_position", sa.DateTime(timezone=True), nullable=True),
            sa.Column("evenement", sa.String(200), nullable=True),
            sa.Column("geolocalisation_gps", sa.String(200), nullable=True),
            sa.Column("statut", sa.String(200), nullable=True),
            sa.Column("is_active", sa.Boolean, nullable=True),
            sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
            sa.Column("updated_at", sa.DateTime(timezone=True), nullable=True),
            sa.UniqueConstraint("company_id", "reference", name="uix_rail_wagon_tracking_uniq"),
        )

    if not _has("rail_wagon_maintenance"):
        op.create_table(
            "rail_wagon_maintenance",
            sa.Column("id", sa.Integer, primary_key=True, index=True),
            sa.Column("company_id", sa.Integer, nullable=False, index=True),
            sa.Column("reference", sa.String(200), nullable=False, index=True),
            sa.Column("numeration_wagon", sa.String(200), nullable=True),
            sa.Column("atelier", sa.String(200), nullable=True),
            sa.Column("type_intervention", sa.String(200), nullable=True),
            sa.Column("date_debut", sa.Date, nullable=True),
            sa.Column("date_fin_prevue", sa.Date, nullable=True),
            sa.Column("date_retour_service", sa.Date, nullable=True),
            sa.Column("cout_xaf", sa.Integer, nullable=True),
            sa.Column("statut", sa.String(200), nullable=True),
            sa.Column("is_active", sa.Boolean, nullable=True),
            sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
            sa.Column("updated_at", sa.DateTime(timezone=True), nullable=True),
            sa.UniqueConstraint("company_id", "reference", name="uix_rail_wagon_maintenance_uniq"),
        )

    if not _has("rail_safety_records"):
        op.create_table(
            "rail_safety_records",
            sa.Column("id", sa.Integer, primary_key=True, index=True),
            sa.Column("company_id", sa.Integer, nullable=False, index=True),
            sa.Column("reference", sa.String(200), nullable=False, index=True),
            sa.Column("date_evenement", sa.DateTime(timezone=True), nullable=True),
            sa.Column("type_incident", sa.String(200), nullable=True),
            sa.Column("gravite", sa.String(200), nullable=True),
            sa.Column("lgn_concernee", sa.String(200), nullable=True),
            sa.Column("wagon_train_implique", sa.String(200), nullable=True),
            sa.Column("description", sa.Text, nullable=True),
            sa.Column("mesure_correctrice", sa.Text, nullable=True),
            sa.Column("statut", sa.String(200), nullable=True),
            sa.Column("is_active", sa.Boolean, nullable=True),
            sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
            sa.Column("updated_at", sa.DateTime(timezone=True), nullable=True),
            sa.UniqueConstraint("company_id", "reference", name="uix_rail_safety_records_uniq"),
        )

    if not _has("rail_corridors"):
        op.create_table(
            "rail_corridors",
            sa.Column("id", sa.Integer, primary_key=True, index=True),
            sa.Column("company_id", sa.Integer, nullable=False, index=True),
            sa.Column("code_corridor", sa.String(200), nullable=False, index=True),
            sa.Column("nom", sa.String(200), nullable=True),
            sa.Column("pays_traverses", sa.String(200), nullable=True),
            sa.Column("longueur_km", sa.Integer, nullable=True),
            sa.Column("gares_focales", sa.Text, nullable=True),
            sa.Column("operateurs", sa.Text, nullable=True),
            sa.Column("debit_annuel_teu", sa.Integer, nullable=True),
            sa.Column("statut", sa.String(200), nullable=True),
            sa.Column("is_active", sa.Boolean, nullable=True),
            sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
            sa.Column("updated_at", sa.DateTime(timezone=True), nullable=True),
            sa.UniqueConstraint("company_id", "code_corridor", name="uix_rail_corridors_uniq"),
        )


def downgrade():
    for t in reversed(TABLES):
        if _has(t):
            op.drop_table(t)
