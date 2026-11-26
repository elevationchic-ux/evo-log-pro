"""068 : tables expansion transport-fluvial (genere)."""
from alembic import op
import sqlalchemy as sa


revision = "068_fluvial_b_deep"
down_revision = "067_log3pl_b_deep"
branch_labels = None
depends_on = None


TABLES = [
    "flvb_canal_sections",
    "flvb_convoys",
    "flvb_ballast_ops",
    "flvb_water_gauges",
    "flvb_berthing_slots",
    "flvb_crew_rosters",
    "flvb_cargo_manifests",
    "flvb_port_fees",
    "flvb_vessel_inspections",
]


def _has(name):
    insp = sa.inspect(op.get_bind())
    return name in set(insp.get_table_names())


def upgrade():
    if not _has("flvb_canal_sections"):
        op.create_table(
            "flvb_canal_sections",
            sa.Column("id", sa.Integer, primary_key=True, index=True),
            sa.Column("company_id", sa.Integer, nullable=False, index=True),
            sa.Column("code_section", sa.String(200), nullable=False, index=True),
            sa.Column("nom_bief", sa.String(200), nullable=True),
            sa.Column("longueur_km", sa.Integer, nullable=True),
            sa.Column("nb_ecluses", sa.Integer, nullable=True),
            sa.Column("gabarit_max_t", sa.Integer, nullable=True),
            sa.Column("profondeur_cote_cm", sa.Integer, nullable=True),
            sa.Column("statut", sa.String(200), nullable=True),
            sa.Column("is_active", sa.Boolean, nullable=True),
            sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
            sa.Column("updated_at", sa.DateTime(timezone=True), nullable=True),
            sa.UniqueConstraint("company_id", "code_section", name="uix_flvb_canal_sections_uniq"),
        )

    if not _has("flvb_convoys"):
        op.create_table(
            "flvb_convoys",
            sa.Column("id", sa.Integer, primary_key=True, index=True),
            sa.Column("company_id", sa.Integer, nullable=False, index=True),
            sa.Column("numero_convoi", sa.String(200), nullable=False, index=True),
            sa.Column("pousseur", sa.String(200), nullable=True),
            sa.Column("nb_peniches", sa.Integer, nullable=True),
            sa.Column("masse_total_t", sa.Integer, nullable=True),
            sa.Column("longueur_total_m", sa.Integer, nullable=True),
            sa.Column("itineraire", sa.String(200), nullable=True),
            sa.Column("date_depart", sa.DateTime(timezone=True), nullable=True),
            sa.Column("statut", sa.String(200), nullable=True),
            sa.Column("is_active", sa.Boolean, nullable=True),
            sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
            sa.Column("updated_at", sa.DateTime(timezone=True), nullable=True),
            sa.UniqueConstraint("company_id", "numero_convoi", name="uix_flvb_convoys_uniq"),
        )

    if not _has("flvb_ballast_ops"):
        op.create_table(
            "flvb_ballast_ops",
            sa.Column("id", sa.Integer, primary_key=True, index=True),
            sa.Column("company_id", sa.Integer, nullable=False, index=True),
            sa.Column("reference", sa.String(200), nullable=False, index=True),
            sa.Column("numero_flotte", sa.String(200), nullable=True),
            sa.Column("type_operation", sa.String(200), nullable=True),
            sa.Column("masse_balle_t", sa.Integer, nullable=True),
            sa.Column("date_operation", sa.DateTime(timezone=True), nullable=True),
            sa.Column("terminal", sa.String(200), nullable=True),
            sa.Column("statut", sa.String(200), nullable=True),
            sa.Column("is_active", sa.Boolean, nullable=True),
            sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
            sa.Column("updated_at", sa.DateTime(timezone=True), nullable=True),
            sa.UniqueConstraint("company_id", "reference", name="uix_flvb_ballast_ops_uniq"),
        )

    if not _has("flvb_water_gauges"):
        op.create_table(
            "flvb_water_gauges",
            sa.Column("id", sa.Integer, primary_key=True, index=True),
            sa.Column("company_id", sa.Integer, nullable=False, index=True),
            sa.Column("code_poste", sa.String(200), nullable=False, index=True),
            sa.Column("nom_poste", sa.String(200), nullable=True),
            sa.Column("bief", sa.String(200), nullable=True),
            sa.Column("cote_cm", sa.Integer, nullable=True),
            sa.Column("cote_seuil_restr_cm", sa.Integer, nullable=True),
            sa.Column("date_releve", sa.DateTime(timezone=True), nullable=True),
            sa.Column("statut", sa.String(200), nullable=True),
            sa.Column("is_active", sa.Boolean, nullable=True),
            sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
            sa.Column("updated_at", sa.DateTime(timezone=True), nullable=True),
            sa.UniqueConstraint("company_id", "code_poste", name="uix_flvb_water_gauges_uniq"),
        )

    if not _has("flvb_berthing_slots"):
        op.create_table(
            "flvb_berthing_slots",
            sa.Column("id", sa.Integer, primary_key=True, index=True),
            sa.Column("company_id", sa.Integer, nullable=False, index=True),
            sa.Column("reference", sa.String(200), nullable=False, index=True),
            sa.Column("terminal", sa.String(200), nullable=True),
            sa.Column("numero_appontement", sa.String(200), nullable=True),
            sa.Column("numero_flotte", sa.String(200), nullable=True),
            sa.Column("date_debut", sa.DateTime(timezone=True), nullable=True),
            sa.Column("date_fin", sa.DateTime(timezone=True), nullable=True),
            sa.Column("statut", sa.String(200), nullable=True),
            sa.Column("is_active", sa.Boolean, nullable=True),
            sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
            sa.Column("updated_at", sa.DateTime(timezone=True), nullable=True),
            sa.UniqueConstraint("company_id", "reference", name="uix_flvb_berthing_slots_uniq"),
        )

    if not _has("flvb_crew_rosters"):
        op.create_table(
            "flvb_crew_rosters",
            sa.Column("id", sa.Integer, primary_key=True, index=True),
            sa.Column("company_id", sa.Integer, nullable=False, index=True),
            sa.Column("reference", sa.String(200), nullable=False, index=True),
            sa.Column("numero_flotte", sa.String(200), nullable=True),
            sa.Column("chef_bord", sa.String(200), nullable=True),
            sa.Column("nb_marins", sa.Integer, nullable=True),
            sa.Column("date_debut", sa.Date, nullable=True),
            sa.Column("date_fin", sa.Date, nullable=True),
            sa.Column("heures_service", sa.Integer, nullable=True),
            sa.Column("statut", sa.String(200), nullable=True),
            sa.Column("is_active", sa.Boolean, nullable=True),
            sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
            sa.Column("updated_at", sa.DateTime(timezone=True), nullable=True),
            sa.UniqueConstraint("company_id", "reference", name="uix_flvb_crew_rosters_uniq"),
        )

    if not _has("flvb_cargo_manifests"):
        op.create_table(
            "flvb_cargo_manifests",
            sa.Column("id", sa.Integer, primary_key=True, index=True),
            sa.Column("company_id", sa.Integer, nullable=False, index=True),
            sa.Column("numero_manifeste", sa.String(200), nullable=False, index=True),
            sa.Column("numero_convoi", sa.String(200), nullable=True),
            sa.Column("terminal_depart", sa.String(200), nullable=True),
            sa.Column("terminal_arrivee", sa.String(200), nullable=True),
            sa.Column("nb_colis", sa.Integer, nullable=True),
            sa.Column("masse_total_t", sa.Integer, nullable=True),
            sa.Column("date_emission", sa.Date, nullable=True),
            sa.Column("statut", sa.String(200), nullable=True),
            sa.Column("is_active", sa.Boolean, nullable=True),
            sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
            sa.Column("updated_at", sa.DateTime(timezone=True), nullable=True),
            sa.UniqueConstraint("company_id", "numero_manifeste", name="uix_flvb_cargo_manifests_uniq"),
        )

    if not _has("flvb_port_fees"):
        op.create_table(
            "flvb_port_fees",
            sa.Column("id", sa.Integer, primary_key=True, index=True),
            sa.Column("company_id", sa.Integer, nullable=False, index=True),
            sa.Column("code_tarif", sa.String(200), nullable=False, index=True),
            sa.Column("terminal", sa.String(200), nullable=True),
            sa.Column("categorie", sa.String(200), nullable=True),
            sa.Column("assiette", sa.String(200), nullable=True),
            sa.Column("montant_xaf", sa.Integer, nullable=True),
            sa.Column("unite", sa.String(200), nullable=True),
            sa.Column("statut", sa.String(200), nullable=True),
            sa.Column("is_active", sa.Boolean, nullable=True),
            sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
            sa.Column("updated_at", sa.DateTime(timezone=True), nullable=True),
            sa.UniqueConstraint("company_id", "code_tarif", name="uix_flvb_port_fees_uniq"),
        )

    if not _has("flvb_vessel_inspections"):
        op.create_table(
            "flvb_vessel_inspections",
            sa.Column("id", sa.Integer, primary_key=True, index=True),
            sa.Column("company_id", sa.Integer, nullable=False, index=True),
            sa.Column("numero_pv", sa.String(200), nullable=False, index=True),
            sa.Column("numero_flotte", sa.String(200), nullable=True),
            sa.Column("type_visite", sa.String(200), nullable=True),
            sa.Column("date_visite", sa.Date, nullable=True),
            sa.Column("date_echeance", sa.Date, nullable=True),
            sa.Column("resultat", sa.String(200), nullable=True),
            sa.Column("observations", sa.Text, nullable=True),
            sa.Column("statut", sa.String(200), nullable=True),
            sa.Column("is_active", sa.Boolean, nullable=True),
            sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
            sa.Column("updated_at", sa.DateTime(timezone=True), nullable=True),
            sa.UniqueConstraint("company_id", "numero_pv", name="uix_flvb_vessel_inspections_uniq"),
        )


def downgrade():
    for t in reversed(TABLES):
        if _has(t):
            op.drop_table(t)
