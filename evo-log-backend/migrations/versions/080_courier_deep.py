"""080 : tables expansion courier-express (genere)."""
from alembic import op
import sqlalchemy as sa


revision = "080_courier_deep"
down_revision = "079_pipeline_deep"
branch_labels = None
depends_on = None


TABLES = [
    "courier_parcels",
    "courier_waybills",
    "courier_hubs",
    "courier_delivery_zones",
    "courier_routes",
    "courier_couriers",
    "courier_pods",
    "courier_slas",
    "courier_lockers",
    "courier_vehicules",
    "courier_tarifs",
    "courier_exceptions",
]


def _has(name):
    insp = sa.inspect(op.get_bind())
    return name in set(insp.get_table_names())


def upgrade():
    if not _has("courier_parcels"):
        op.create_table(
            "courier_parcels",
            sa.Column("id", sa.Integer, primary_key=True, index=True),
            sa.Column("company_id", sa.Integer, nullable=False, index=True),
            sa.Column("numero_colis", sa.String(150), nullable=False, index=True),
            sa.Column("type_colis", sa.String(150), nullable=True),
            sa.Column("format", sa.String(150), nullable=True),
            sa.Column("poids_kg", sa.Integer, nullable=True),
            sa.Column("dimensions_cm", sa.String(150), nullable=True),
            sa.Column("valeur_declaree_xaf", sa.Integer, nullable=True),
            sa.Column("expediteur", sa.String(150), nullable=True),
            sa.Column("destinataire", sa.String(150), nullable=True),
            sa.Column("date_prise_en_charge", sa.Date, nullable=True),
            sa.Column("date_livraison", sa.Date, nullable=True),
            sa.Column("statut", sa.String(150), nullable=True),
            sa.Column("is_active", sa.Boolean, nullable=True),
            sa.Column("created_at", sa.DateTime(timezone=True), nullable=True),
            sa.Column("updated_at", sa.DateTime(timezone=True), nullable=True),
            sa.UniqueConstraint("company_id", "numero_colis", name="uix_courier_parcels_uniq"),
        )

    if not _has("courier_waybills"):
        op.create_table(
            "courier_waybills",
            sa.Column("id", sa.Integer, primary_key=True, index=True),
            sa.Column("company_id", sa.Integer, nullable=False, index=True),
            sa.Column("numero_lse", sa.String(150), nullable=False, index=True),
            sa.Column("type_service", sa.String(150), nullable=True),
            sa.Column("client", sa.String(150), nullable=True),
            sa.Column("nb_colis", sa.Integer, nullable=True),
            sa.Column("poids_total_kg", sa.Integer, nullable=True),
            sa.Column("montant_facture_xaf", sa.Integer, nullable=True),
            sa.Column("date_emission", sa.Date, nullable=True),
            sa.Column("date_livraison_prevue", sa.Date, nullable=True),
            sa.Column("date_livraison_reelle", sa.Date, nullable=True),
            sa.Column("statut", sa.String(150), nullable=True),
            sa.Column("is_active", sa.Boolean, nullable=True),
            sa.Column("created_at", sa.DateTime(timezone=True), nullable=True),
            sa.Column("updated_at", sa.DateTime(timezone=True), nullable=True),
            sa.UniqueConstraint("company_id", "numero_lse", name="uix_courier_waybills_uniq"),
        )

    if not _has("courier_hubs"):
        op.create_table(
            "courier_hubs",
            sa.Column("id", sa.Integer, primary_key=True, index=True),
            sa.Column("company_id", sa.Integer, nullable=False, index=True),
            sa.Column("code_hub", sa.String(150), nullable=False, index=True),
            sa.Column("nom", sa.String(150), nullable=True),
            sa.Column("ville", sa.String(150), nullable=True),
            sa.Column("pays", sa.String(150), nullable=True),
            sa.Column("capacite", sa.String(150), nullable=True),
            sa.Column("nb_tri_jour", sa.Integer, nullable=True),
            sa.Column("surface_m2", sa.Integer, nullable=True),
            sa.Column("statut", sa.String(150), nullable=True),
            sa.Column("is_active", sa.Boolean, nullable=True),
            sa.Column("created_at", sa.DateTime(timezone=True), nullable=True),
            sa.Column("updated_at", sa.DateTime(timezone=True), nullable=True),
            sa.UniqueConstraint("company_id", "code_hub", name="uix_courier_hubs_uniq"),
        )

    if not _has("courier_delivery_zones"):
        op.create_table(
            "courier_delivery_zones",
            sa.Column("id", sa.Integer, primary_key=True, index=True),
            sa.Column("company_id", sa.Integer, nullable=False, index=True),
            sa.Column("code_zone", sa.String(150), nullable=False, index=True),
            sa.Column("nom", sa.String(150), nullable=True),
            sa.Column("type_zone", sa.String(150), nullable=True),
            sa.Column("ville", sa.String(150), nullable=True),
            sa.Column("nb_habitants", sa.Integer, nullable=True),
            sa.Column("nb_colis_jour", sa.Integer, nullable=True),
            sa.Column("hub_rattachement", sa.String(150), nullable=True),
            sa.Column("surcost_xaf", sa.Integer, nullable=True),
            sa.Column("is_active", sa.Boolean, nullable=True),
            sa.Column("created_at", sa.DateTime(timezone=True), nullable=True),
            sa.Column("updated_at", sa.DateTime(timezone=True), nullable=True),
            sa.UniqueConstraint("company_id", "code_zone", name="uix_courier_delivery_zones_uniq"),
        )

    if not _has("courier_routes"):
        op.create_table(
            "courier_routes",
            sa.Column("id", sa.Integer, primary_key=True, index=True),
            sa.Column("company_id", sa.Integer, nullable=False, index=True),
            sa.Column("code_tournee", sa.String(150), nullable=False, index=True),
            sa.Column("type_route", sa.String(150), nullable=True),
            sa.Column("zone_associee", sa.String(150), nullable=True),
            sa.Column("chauffeur", sa.String(150), nullable=True),
            sa.Column("vehicule", sa.String(150), nullable=True),
            sa.Column("date_tournee", sa.Date, nullable=True),
            sa.Column("nb_arrets", sa.Integer, nullable=True),
            sa.Column("distance_km", sa.Integer, nullable=True),
            sa.Column("duree_h", sa.Integer, nullable=True),
            sa.Column("statut", sa.String(150), nullable=True),
            sa.Column("is_active", sa.Boolean, nullable=True),
            sa.Column("created_at", sa.DateTime(timezone=True), nullable=True),
            sa.Column("updated_at", sa.DateTime(timezone=True), nullable=True),
            sa.UniqueConstraint("company_id", "code_tournee", name="uix_courier_routes_uniq"),
        )

    if not _has("courier_couriers"):
        op.create_table(
            "courier_couriers",
            sa.Column("id", sa.Integer, primary_key=True, index=True),
            sa.Column("company_id", sa.Integer, nullable=False, index=True),
            sa.Column("code_coursier", sa.String(150), nullable=False, index=True),
            sa.Column("nom", sa.String(150), nullable=True),
            sa.Column("telephone", sa.String(150), nullable=True),
            sa.Column("email", sa.String(150), nullable=True),
            sa.Column("type_contrat", sa.String(150), nullable=True),
            sa.Column("permis_conduire", sa.String(150), nullable=True),
            sa.Column("date_embauche", sa.Date, nullable=True),
            sa.Column("nb_livraisons_jour", sa.Integer, nullable=True),
            sa.Column("taux_ponctualite_pct", sa.Integer, nullable=True),
            sa.Column("disponibilite", sa.String(150), nullable=True),
            sa.Column("is_active", sa.Boolean, nullable=True),
            sa.Column("created_at", sa.DateTime(timezone=True), nullable=True),
            sa.Column("updated_at", sa.DateTime(timezone=True), nullable=True),
            sa.UniqueConstraint("company_id", "code_coursier", name="uix_courier_couriers_uniq"),
        )

    if not _has("courier_pods"):
        op.create_table(
            "courier_pods",
            sa.Column("id", sa.Integer, primary_key=True, index=True),
            sa.Column("company_id", sa.Integer, nullable=False, index=True),
            sa.Column("reference_pod", sa.String(150), nullable=False, index=True),
            sa.Column("numero_colis", sa.String(150), nullable=True),
            sa.Column("date_livraison", sa.DateTime(timezone=True), nullable=True),
            sa.Column("destination_finale", sa.String(150), nullable=True),
            sa.Column("agent_livreur", sa.String(150), nullable=True),
            sa.Column("resultat", sa.String(150), nullable=True),
            sa.Column("signature_recu", sa.Boolean, nullable=True),
            sa.Column("photo_url", sa.String(150), nullable=True),
            sa.Column("geo_lat", sa.String(150), nullable=True),
            sa.Column("geo_lon", sa.String(150), nullable=True),
            sa.Column("is_active", sa.Boolean, nullable=True),
            sa.Column("created_at", sa.DateTime(timezone=True), nullable=True),
            sa.Column("updated_at", sa.DateTime(timezone=True), nullable=True),
            sa.UniqueConstraint("company_id", "reference_pod", name="uix_courier_pods_uniq"),
        )

    if not _has("courier_slas"):
        op.create_table(
            "courier_slas",
            sa.Column("id", sa.Integer, primary_key=True, index=True),
            sa.Column("company_id", sa.Integer, nullable=False, index=True),
            sa.Column("code_sla", sa.String(150), nullable=False, index=True),
            sa.Column("client", sa.String(150), nullable=True),
            sa.Column("categorie", sa.String(150), nullable=True),
            sa.Column("engagement_pct", sa.Integer, nullable=True),
            sa.Column("delai_h", sa.Integer, nullable=True),
            sa.Column("penalite_xaf", sa.Integer, nullable=True),
            sa.Column("mesure_pct", sa.Integer, nullable=True),
            sa.Column("date_debut", sa.Date, nullable=True),
            sa.Column("date_fin", sa.Date, nullable=True),
            sa.Column("statut", sa.String(150), nullable=True),
            sa.Column("is_active", sa.Boolean, nullable=True),
            sa.Column("created_at", sa.DateTime(timezone=True), nullable=True),
            sa.Column("updated_at", sa.DateTime(timezone=True), nullable=True),
            sa.UniqueConstraint("company_id", "code_sla", name="uix_courier_slas_uniq"),
        )

    if not _has("courier_lockers"):
        op.create_table(
            "courier_lockers",
            sa.Column("id", sa.Integer, primary_key=True, index=True),
            sa.Column("company_id", sa.Integer, nullable=False, index=True),
            sa.Column("code_locker", sa.String(150), nullable=False, index=True),
            sa.Column("adresse", sa.String(150), nullable=True),
            sa.Column("ville", sa.String(150), nullable=True),
            sa.Column("nb_cases", sa.Integer, nullable=True),
            sa.Column("nb_cases_libres", sa.Integer, nullable=True),
            sa.Column("type_acces", sa.String(150), nullable=True),
            sa.Column("horaires_ouverture", sa.String(150), nullable=True),
            sa.Column("statut", sa.String(150), nullable=True),
            sa.Column("is_active", sa.Boolean, nullable=True),
            sa.Column("created_at", sa.DateTime(timezone=True), nullable=True),
            sa.Column("updated_at", sa.DateTime(timezone=True), nullable=True),
            sa.UniqueConstraint("company_id", "code_locker", name="uix_courier_lockers_uniq"),
        )

    if not _has("courier_vehicules"):
        op.create_table(
            "courier_vehicules",
            sa.Column("id", sa.Integer, primary_key=True, index=True),
            sa.Column("company_id", sa.Integer, nullable=False, index=True),
            sa.Column("plaque", sa.String(150), nullable=False, index=True),
            sa.Column("type_vehicule", sa.String(150), nullable=True),
            sa.Column("marque", sa.String(150), nullable=True),
            sa.Column("modele", sa.String(150), nullable=True),
            sa.Column("capacite_m3", sa.Integer, nullable=True),
            sa.Column("date_mise_circulation", sa.Date, nullable=True),
            sa.Column("kilometrage_actuel", sa.Integer, nullable=True),
            sa.Column("prochaine_revision_km", sa.Integer, nullable=True),
            sa.Column("statut", sa.String(150), nullable=True),
            sa.Column("is_active", sa.Boolean, nullable=True),
            sa.Column("created_at", sa.DateTime(timezone=True), nullable=True),
            sa.Column("updated_at", sa.DateTime(timezone=True), nullable=True),
            sa.UniqueConstraint("company_id", "plaque", name="uix_courier_vehicules_uniq"),
        )

    if not _has("courier_tarifs"):
        op.create_table(
            "courier_tarifs",
            sa.Column("id", sa.Integer, primary_key=True, index=True),
            sa.Column("company_id", sa.Integer, nullable=False, index=True),
            sa.Column("code_tarif", sa.String(150), nullable=False, index=True),
            sa.Column("zone_tarifaire", sa.String(150), nullable=True),
            sa.Column("tranche_poids_kg", sa.String(150), nullable=True),
            sa.Column("prix_base_xaf", sa.Integer, nullable=True),
            sa.Column("prix_par_kg_supp_xaf", sa.Integer, nullable=True),
            sa.Column("options_payantes", sa.String(2000), nullable=True),
            sa.Column("date_debut_validite", sa.Date, nullable=True),
            sa.Column("date_fin_validite", sa.Date, nullable=True),
            sa.Column("statut", sa.String(150), nullable=True),
            sa.Column("is_active", sa.Boolean, nullable=True),
            sa.Column("created_at", sa.DateTime(timezone=True), nullable=True),
            sa.Column("updated_at", sa.DateTime(timezone=True), nullable=True),
            sa.UniqueConstraint("company_id", "code_tarif", name="uix_courier_tarifs_uniq"),
        )

    if not _has("courier_exceptions"):
        op.create_table(
            "courier_exceptions",
            sa.Column("id", sa.Integer, primary_key=True, index=True),
            sa.Column("company_id", sa.Integer, nullable=False, index=True),
            sa.Column("reference", sa.String(150), nullable=False, index=True),
            sa.Column("numero_colis", sa.String(150), nullable=True),
            sa.Column("type_exception", sa.String(150), nullable=True),
            sa.Column("date_signalement", sa.DateTime(timezone=True), nullable=True),
            sa.Column("description", sa.String(2000), nullable=True),
            sa.Column("montant_litige_xaf", sa.Integer, nullable=True),
            sa.Column("agent", sa.String(150), nullable=True),
            sa.Column("date_resolution", sa.DateTime(timezone=True), nullable=True),
            sa.Column("statut", sa.String(150), nullable=True),
            sa.Column("is_active", sa.Boolean, nullable=True),
            sa.Column("created_at", sa.DateTime(timezone=True), nullable=True),
            sa.Column("updated_at", sa.DateTime(timezone=True), nullable=True),
            sa.UniqueConstraint("company_id", "reference", name="uix_courier_exceptions_uniq"),
        )


def downgrade():
    for t in reversed(TABLES):
        if _has(t):
            op.drop_table(t)
