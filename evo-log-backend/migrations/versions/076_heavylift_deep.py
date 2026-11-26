"""076 : tables expansion convoi-exceptionnel (genere)."""
from alembic import op
import sqlalchemy as sa


revision = "076_heavylift_deep"
down_revision = "072_qhse_b_deep"
branch_labels = None
depends_on = None


TABLES = [
    "heavylift_projects",
    "heavylift_cranes",
    "heavylift_modular_trailers",
    "heavylift_route_surveys",
    "heavylift_lift_plans",
    "heavylift_permits",
    "heavylift_escorts",
    "heavylift_lashings",
    "heavylift_ballasts",
    "heavylift_rigging_methods",
]


def _has(name):
    insp = sa.inspect(op.get_bind())
    return name in set(insp.get_table_names())


def upgrade():
    if not _has("heavylift_projects"):
        op.create_table(
            "heavylift_projects",
            sa.Column("id", sa.Integer, primary_key=True, index=True),
            sa.Column("company_id", sa.Integer, nullable=False, index=True),
            sa.Column("code_projet", sa.String(200), nullable=False, index=True),
            sa.Column("nom", sa.String(200), nullable=True),
            sa.Column("client", sa.String(200), nullable=True),
            sa.Column("categorie", sa.String(200), nullable=True),
            sa.Column("poids_max_t", sa.Integer, nullable=True),
            sa.Column("volume_m3", sa.Integer, nullable=True),
            sa.Column("distance_km", sa.Integer, nullable=True),
            sa.Column("date_debut", sa.Date, nullable=True),
            sa.Column("date_fin_prevue", sa.Date, nullable=True),
            sa.Column("budget_xaf", sa.Integer, nullable=True),
            sa.Column("statut", sa.String(200), nullable=True),
            sa.Column("is_active", sa.Boolean, nullable=True),
            sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
            sa.Column("updated_at", sa.DateTime(timezone=True), nullable=True),
            sa.UniqueConstraint("company_id", "code_projet", name="uix_heavylift_projects_uniq"),
        )

    if not _has("heavylift_cranes"):
        op.create_table(
            "heavylift_cranes",
            sa.Column("id", sa.Integer, primary_key=True, index=True),
            sa.Column("company_id", sa.Integer, nullable=False, index=True),
            sa.Column("numero_grue", sa.String(200), nullable=False, index=True),
            sa.Column("type_grue", sa.String(200), nullable=True),
            sa.Column("capacite_max_t", sa.Integer, nullable=True),
            sa.Column("portee_max_m", sa.Integer, nullable=True),
            sa.Column("hauteur_max_m", sa.Integer, nullable=True),
            sa.Column("mise_en_service", sa.Date, nullable=True),
            sa.Column("prochaine_visite", sa.Date, nullable=True),
            sa.Column("cout_location_jour_xaf", sa.Integer, nullable=True),
            sa.Column("statut", sa.String(200), nullable=True),
            sa.Column("is_active", sa.Boolean, nullable=True),
            sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
            sa.Column("updated_at", sa.DateTime(timezone=True), nullable=True),
            sa.UniqueConstraint("company_id", "numero_grue", name="uix_heavylift_cranes_uniq"),
        )

    if not _has("heavylift_modular_trailers"):
        op.create_table(
            "heavylift_modular_trailers",
            sa.Column("id", sa.Integer, primary_key=True, index=True),
            sa.Column("company_id", sa.Integer, nullable=False, index=True),
            sa.Column("plaque", sa.String(200), nullable=False, index=True),
            sa.Column("type_remorque", sa.String(200), nullable=True),
            sa.Column("nb_essieux", sa.Integer, nullable=True),
            sa.Column("charge_utile_t", sa.Integer, nullable=True),
            sa.Column("longueur_m", sa.Integer, nullable=True),
            sa.Column("largeur_m", sa.Integer, nullable=True),
            sa.Column("hauteur_min_m", sa.Integer, nullable=True),
            sa.Column("angle_orientation_deg", sa.Integer, nullable=True),
            sa.Column("statut", sa.String(200), nullable=True),
            sa.Column("is_active", sa.Boolean, nullable=True),
            sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
            sa.Column("updated_at", sa.DateTime(timezone=True), nullable=True),
            sa.UniqueConstraint("company_id", "plaque", name="uix_heavylift_modular_trailers_uniq"),
        )

    if not _has("heavylift_route_surveys"):
        op.create_table(
            "heavylift_route_surveys",
            sa.Column("id", sa.Integer, primary_key=True, index=True),
            sa.Column("company_id", sa.Integer, nullable=False, index=True),
            sa.Column("reference", sa.String(200), nullable=False, index=True),
            sa.Column("projet_associe", sa.String(200), nullable=True),
            sa.Column("origine", sa.String(200), nullable=True),
            sa.Column("destination", sa.String(200), nullable=True),
            sa.Column("distance_km", sa.Integer, nullable=True),
            sa.Column("nb_obstacles", sa.Integer, nullable=True),
            sa.Column("ouvrages_franchis", sa.Text, nullable=True),
            sa.Column("cout_amenagement_xaf", sa.Integer, nullable=True),
            sa.Column("date_etude", sa.Date, nullable=True),
            sa.Column("resultat", sa.String(200), nullable=True),
            sa.Column("statut", sa.String(200), nullable=True),
            sa.Column("is_active", sa.Boolean, nullable=True),
            sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
            sa.Column("updated_at", sa.DateTime(timezone=True), nullable=True),
            sa.UniqueConstraint("company_id", "reference", name="uix_heavylift_route_surveys_uniq"),
        )

    if not _has("heavylift_lift_plans"):
        op.create_table(
            "heavylift_lift_plans",
            sa.Column("id", sa.Integer, primary_key=True, index=True),
            sa.Column("company_id", sa.Integer, nullable=False, index=True),
            sa.Column("reference", sa.String(200), nullable=False, index=True),
            sa.Column("projet_associe", sa.String(200), nullable=True),
            sa.Column("type_operation", sa.String(200), nullable=True),
            sa.Column("charge_t", sa.Integer, nullable=True),
            sa.Column("hauteur_m", sa.Integer, nullable=True),
            sa.Column("centre_gravite_haut", sa.Boolean, nullable=True),
            sa.Column("coefficient_securite_pct", sa.Integer, nullable=True),
            sa.Column("grue_prevue", sa.String(200), nullable=True),
            sa.Column("date_prevue", sa.Date, nullable=True),
            sa.Column("criticite", sa.String(200), nullable=True),
            sa.Column("statut", sa.String(200), nullable=True),
            sa.Column("is_active", sa.Boolean, nullable=True),
            sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
            sa.Column("updated_at", sa.DateTime(timezone=True), nullable=True),
            sa.UniqueConstraint("company_id", "reference", name="uix_heavylift_lift_plans_uniq"),
        )

    if not _has("heavylift_permits"):
        op.create_table(
            "heavylift_permits",
            sa.Column("id", sa.Integer, primary_key=True, index=True),
            sa.Column("company_id", sa.Integer, nullable=False, index=True),
            sa.Column("numero_permis", sa.String(200), nullable=False, index=True),
            sa.Column("type_permis", sa.String(200), nullable=True),
            sa.Column("autorite", sa.String(200), nullable=True),
            sa.Column("charge_concernee", sa.String(200), nullable=True),
            sa.Column("itineraire_depot", sa.Text, nullable=True),
            sa.Column("date_depot_demande", sa.Date, nullable=True),
            sa.Column("date_delivrance", sa.Date, nullable=True),
            sa.Column("date_validite_fin", sa.Date, nullable=True),
            sa.Column("cout_redevance_xaf", sa.Integer, nullable=True),
            sa.Column("statut", sa.String(200), nullable=True),
            sa.Column("is_active", sa.Boolean, nullable=True),
            sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
            sa.Column("updated_at", sa.DateTime(timezone=True), nullable=True),
            sa.UniqueConstraint("company_id", "numero_permis", name="uix_heavylift_permits_uniq"),
        )

    if not _has("heavylift_escorts"):
        op.create_table(
            "heavylift_escorts",
            sa.Column("id", sa.Integer, primary_key=True, index=True),
            sa.Column("company_id", sa.Integer, nullable=False, index=True),
            sa.Column("reference", sa.String(200), nullable=False, index=True),
            sa.Column("convoi_associe", sa.String(200), nullable=True),
            sa.Column("type_escorte", sa.String(200), nullable=True),
            sa.Column("nb_vehicules_escorte", sa.Integer, nullable=True),
            sa.Column("date_debut", sa.DateTime(timezone=True), nullable=True),
            sa.Column("date_fin", sa.DateTime(timezone=True), nullable=True),
            sa.Column("zone_administrative", sa.String(200), nullable=True),
            sa.Column("agent_responsable", sa.String(200), nullable=True),
            sa.Column("cout_xaf", sa.Integer, nullable=True),
            sa.Column("statut", sa.String(200), nullable=True),
            sa.Column("is_active", sa.Boolean, nullable=True),
            sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
            sa.Column("updated_at", sa.DateTime(timezone=True), nullable=True),
            sa.UniqueConstraint("company_id", "reference", name="uix_heavylift_escorts_uniq"),
        )

    if not _has("heavylift_lashings"):
        op.create_table(
            "heavylift_lashings",
            sa.Column("id", sa.Integer, primary_key=True, index=True),
            sa.Column("company_id", sa.Integer, nullable=False, index=True),
            sa.Column("reference", sa.String(200), nullable=False, index=True),
            sa.Column("methode", sa.String(200), nullable=True),
            sa.Column("charge_amarree", sa.String(200), nullable=True),
            sa.Column("nb_points", sa.Integer, nullable=True),
            sa.Column("effort_admissible_t", sa.Integer, nullable=True),
            sa.Column("coefficient_secu_pct", sa.Integer, nullable=True),
            sa.Column("operateur", sa.String(200), nullable=True),
            sa.Column("date_controle", sa.Date, nullable=True),
            sa.Column("resultat", sa.String(200), nullable=True),
            sa.Column("is_active", sa.Boolean, nullable=True),
            sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
            sa.Column("updated_at", sa.DateTime(timezone=True), nullable=True),
            sa.UniqueConstraint("company_id", "reference", name="uix_heavylift_lashings_uniq"),
        )

    if not _has("heavylift_ballasts"):
        op.create_table(
            "heavylift_ballasts",
            sa.Column("id", sa.Integer, primary_key=True, index=True),
            sa.Column("company_id", sa.Integer, nullable=False, index=True),
            sa.Column("code_ballast", sa.String(200), nullable=False, index=True),
            sa.Column("type_ballast", sa.String(200), nullable=True),
            sa.Column("masse_unitaire_t", sa.Integer, nullable=True),
            sa.Column("nb_unites", sa.Integer, nullable=True),
            sa.Column("masse_totale_t", sa.Integer, nullable=True),
            sa.Column("cout_location_jour_xaf", sa.Integer, nullable=True),
            sa.Column("lieu_stockage", sa.String(200), nullable=True),
            sa.Column("statut", sa.String(200), nullable=True),
            sa.Column("is_active", sa.Boolean, nullable=True),
            sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
            sa.Column("updated_at", sa.DateTime(timezone=True), nullable=True),
            sa.UniqueConstraint("company_id", "code_ballast", name="uix_heavylift_ballasts_uniq"),
        )

    if not _has("heavylift_rigging_methods"):
        op.create_table(
            "heavylift_rigging_methods",
            sa.Column("id", sa.Integer, primary_key=True, index=True),
            sa.Column("company_id", sa.Integer, nullable=False, index=True),
            sa.Column("code_methode", sa.String(200), nullable=False, index=True),
            sa.Column("categorie", sa.String(200), nullable=True),
            sa.Column("description", sa.Text, nullable=True),
            sa.Column("capacite_max_t", sa.Integer, nullable=True),
            sa.Column("temps_mise_en_oeuvre_h", sa.Integer, nullable=True),
            sa.Column("nb_techniciens", sa.Integer, nullable=True),
            sa.Column("cout_moyen_xaf", sa.Integer, nullable=True),
            sa.Column("is_active", sa.Boolean, nullable=True),
            sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
            sa.Column("updated_at", sa.DateTime(timezone=True), nullable=True),
            sa.UniqueConstraint("company_id", "code_methode", name="uix_heavylift_rigging_methods_uniq"),
        )


def downgrade():
    for t in reversed(TABLES):
        if _has(t):
            op.drop_table(t)
