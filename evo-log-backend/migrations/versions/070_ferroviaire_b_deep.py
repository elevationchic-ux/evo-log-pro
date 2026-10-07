"""070 : tables expansion transport-ferroviaire (genere)."""
from alembic import op
import sqlalchemy as sa


revision = "070_ferroviaire_b_deep"
down_revision = "069_aerien_b_deep"
branch_labels = None
depends_on = None


TABLES = [
    "railb_wheel_sets",
    "railb_loading_gauges",
    "railb_shunting_plans",
    "railb_train_consists",
    "railb_path_occupancy",
    "railb_wagon_dispatch",
    "railb_terminal_cranes",
]


def _has(name):
    insp = sa.inspect(op.get_bind())
    return name in set(insp.get_table_names())


def upgrade():
    if not _has("railb_wheel_sets"):
        op.create_table(
            "railb_wheel_sets",
            sa.Column("id", sa.Integer, primary_key=True, index=True),
            sa.Column("company_id", sa.Integer, nullable=False, index=True),
            sa.Column("numero_essieu", sa.String(200), nullable=False, index=True),
            sa.Column("type_essieu", sa.String(200), nullable=True),
            sa.Column("diametre_mm", sa.Integer, nullable=True),
            sa.Column("km_parcourus", sa.Integer, nullable=True),
            sa.Column("date_controle", sa.Date, nullable=True),
            sa.Column("statut", sa.String(200), nullable=True),
            sa.Column("is_active", sa.Boolean, nullable=True),
            sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
            sa.Column("updated_at", sa.DateTime(timezone=True), nullable=True),
            sa.UniqueConstraint("company_id", "numero_essieu", name="uix_railb_wheel_sets_uniq"),
        )

    if not _has("railb_loading_gauges"):
        op.create_table(
            "railb_loading_gauges",
            sa.Column("id", sa.Integer, primary_key=True, index=True),
            sa.Column("company_id", sa.Integer, nullable=False, index=True),
            sa.Column("code_gabarit", sa.String(200), nullable=False, index=True),
            sa.Column("ligne", sa.String(200), nullable=True),
            sa.Column("largeur_max_mm", sa.Integer, nullable=True),
            sa.Column("hauteur_max_mm", sa.Integer, nullable=True),
            sa.Column("masse_max_t", sa.Integer, nullable=True),
            sa.Column("statut", sa.String(200), nullable=True),
            sa.Column("is_active", sa.Boolean, nullable=True),
            sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
            sa.Column("updated_at", sa.DateTime(timezone=True), nullable=True),
            sa.UniqueConstraint("company_id", "code_gabarit", name="uix_railb_loading_gauges_uniq"),
        )

    if not _has("railb_shunting_plans"):
        op.create_table(
            "railb_shunting_plans",
            sa.Column("id", sa.Integer, primary_key=True, index=True),
            sa.Column("company_id", sa.Integer, nullable=False, index=True),
            sa.Column("reference", sa.String(200), nullable=False, index=True),
            sa.Column("yard", sa.String(200), nullable=True),
            sa.Column("voie_source", sa.String(200), nullable=True),
            sa.Column("voie_destinataire", sa.String(200), nullable=True),
            sa.Column("nb_wagons", sa.Integer, nullable=True),
            sa.Column("operateur", sa.String(200), nullable=True),
            sa.Column("date_plan", sa.DateTime(timezone=True), nullable=True),
            sa.Column("statut", sa.String(200), nullable=True),
            sa.Column("is_active", sa.Boolean, nullable=True),
            sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
            sa.Column("updated_at", sa.DateTime(timezone=True), nullable=True),
            sa.UniqueConstraint("company_id", "reference", name="uix_railb_shunting_plans_uniq"),
        )

    if not _has("railb_train_consists"):
        op.create_table(
            "railb_train_consists",
            sa.Column("id", sa.Integer, primary_key=True, index=True),
            sa.Column("company_id", sa.Integer, nullable=False, index=True),
            sa.Column("reference", sa.String(200), nullable=False, index=True),
            sa.Column("numero_train", sa.String(200), nullable=True),
            sa.Column("nb_wagons", sa.Integer, nullable=True),
            sa.Column("masse_total_t", sa.Integer, nullable=True),
            sa.Column("longueur_m", sa.Integer, nullable=True),
            sa.Column("locomotive", sa.String(200), nullable=True),
            sa.Column("date_composition", sa.DateTime(timezone=True), nullable=True),
            sa.Column("statut", sa.String(200), nullable=True),
            sa.Column("is_active", sa.Boolean, nullable=True),
            sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
            sa.Column("updated_at", sa.DateTime(timezone=True), nullable=True),
            sa.UniqueConstraint("company_id", "reference", name="uix_railb_train_consists_uniq"),
        )

    if not _has("railb_path_occupancy"):
        op.create_table(
            "railb_path_occupancy",
            sa.Column("id", sa.Integer, primary_key=True, index=True),
            sa.Column("company_id", sa.Integer, nullable=False, index=True),
            sa.Column("reference", sa.String(200), nullable=False, index=True),
            sa.Column("numero_train", sa.String(200), nullable=True),
            sa.Column("section", sa.String(200), nullable=True),
            sa.Column("date_debut", sa.DateTime(timezone=True), nullable=True),
            sa.Column("date_fin", sa.DateTime(timezone=True), nullable=True),
            sa.Column("attribue_par", sa.String(200), nullable=True),
            sa.Column("statut", sa.String(200), nullable=True),
            sa.Column("is_active", sa.Boolean, nullable=True),
            sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
            sa.Column("updated_at", sa.DateTime(timezone=True), nullable=True),
            sa.UniqueConstraint("company_id", "reference", name="uix_railb_path_occupancy_uniq"),
        )

    if not _has("railb_wagon_dispatch"):
        op.create_table(
            "railb_wagon_dispatch",
            sa.Column("id", sa.Integer, primary_key=True, index=True),
            sa.Column("company_id", sa.Integer, nullable=False, index=True),
            sa.Column("reference", sa.String(200), nullable=False, index=True),
            sa.Column("numero_wagon", sa.String(200), nullable=True),
            sa.Column("client", sa.String(200), nullable=True),
            sa.Column("destination", sa.String(200), nullable=True),
            sa.Column("produit", sa.String(200), nullable=True),
            sa.Column("date_affectation", sa.Date, nullable=True),
            sa.Column("statut", sa.String(200), nullable=True),
            sa.Column("is_active", sa.Boolean, nullable=True),
            sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
            sa.Column("updated_at", sa.DateTime(timezone=True), nullable=True),
            sa.UniqueConstraint("company_id", "reference", name="uix_railb_wagon_dispatch_uniq"),
        )

    if not _has("railb_terminal_cranes"):
        op.create_table(
            "railb_terminal_cranes",
            sa.Column("id", sa.Integer, primary_key=True, index=True),
            sa.Column("company_id", sa.Integer, nullable=False, index=True),
            sa.Column("code_equipment", sa.String(200), nullable=False, index=True),
            sa.Column("terminal", sa.String(200), nullable=True),
            sa.Column("type", sa.String(200), nullable=True),
            sa.Column("capacite_tonnes", sa.Integer, nullable=True),
            sa.Column("portee_m", sa.Integer, nullable=True),
            sa.Column("date_prochaine_visite", sa.Date, nullable=True),
            sa.Column("statut", sa.String(200), nullable=True),
            sa.Column("is_active", sa.Boolean, nullable=True),
            sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
            sa.Column("updated_at", sa.DateTime(timezone=True), nullable=True),
            sa.UniqueConstraint("company_id", "code_equipment", name="uix_railb_terminal_cranes_uniq"),
        )


def downgrade():
    for t in reversed(TABLES):
        if _has(t):
            op.drop_table(t)
