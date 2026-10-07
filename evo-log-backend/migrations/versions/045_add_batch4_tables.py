"""045 : tables de persistance Batch 4 (chat / QHSE permis / RH recrutement).

Contexte : ces surfaces n'avaient AUCUNE table. Les routers concernes
renvoyaient soit un stub 501, soit un succes fabrique avec un identifiant
codé en dur ("id": 101 / 501 / 12). Cette migration cree les vraies tables
pour qu'ils fassent du CRUD reel :

    - chat_contextual_pins        (epingles dossier metier <-> salon de discussion)
    - permis_travail              (permis de travail debranche, acte de securite)
    - signatures_permis_travail   (signatures reelles d'utilisateurs authentifies)
    - heures_exposition           (denominateurs CNPS saisis par l'entreprise)
    - offres_emploi               (recrutement RH avance)
    - candidatures                (candidatures recues + decisions traitees)

Proprietes :
    - IDEMPOTENT par introspection : table deja presente -> no-op (compatible
      base heritee de create_all, cas Railway actuel).
    - Cle etrangere companies.id / users.id / chat_meeting_rooms.id nullable
      sauf chainage metier obligatoire (permis_id, offre_id).
    - downgrade drop les six tables (strictement additif).

Revision ID: 045_add_batch4_tables
Revises: 044_add_batch3_tables
Create Date: 2026-10-07
"""
from alembic import op
import sqlalchemy as sa


revision = "045_add_batch4_tables"
down_revision = "044_add_batch3_tables"
branch_labels = None
depends_on = None


TABLES = [
    "chat_contextual_pins",
    "signatures_permis_travail",
    "permis_travail",
    "heures_exposition",
    "candidatures",
    "offres_emploi",
]


def _has_table(name):
    insp = sa.inspect(op.get_bind())
    return name in set(insp.get_table_names())


def upgrade():
    if not _has_table("offres_emploi"):
        op.create_table(
            "offres_emploi",
            sa.Column("id", sa.Integer, primary_key=True, index=True),
            sa.Column("titre", sa.String(200), nullable=False),
            sa.Column("departement", sa.String(100), nullable=False),
            sa.Column("type_contrat", sa.String(50), nullable=False, server_default="CDI"),
            sa.Column("description", sa.Text, nullable=False),
            sa.Column("competences_requises", sa.Text, nullable=False, server_default="[]"),
            sa.Column("salaire_min", sa.Numeric, nullable=True),
            sa.Column("salaire_max", sa.Numeric, nullable=True),
            sa.Column("statut", sa.String(20), nullable=False, server_default="PUBLIEE"),
            sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
        )

    if not _has_table("candidatures"):
        op.create_table(
            "candidatures",
            sa.Column("id", sa.Integer, primary_key=True, index=True),
            sa.Column("offre_id", sa.Integer, sa.ForeignKey("offres_emploi.id"), nullable=False, index=True),
            sa.Column("candidat_nom", sa.String(150), nullable=False),
            sa.Column("email", sa.String(150), nullable=False),
            sa.Column("telephone", sa.String(30), nullable=False),
            sa.Column("cv_url", sa.String(300), nullable=True),
            sa.Column("experience_annees", sa.Integer, nullable=False, server_default="0"),
            sa.Column("statut", sa.String(20), nullable=False, server_default="RECU"),
            sa.Column("decision_notes", sa.Text, nullable=True),
            sa.Column("date_decision", sa.Date, nullable=True),
            sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
        )

    if not _has_table("chat_contextual_pins"):
        op.create_table(
            "chat_contextual_pins",
            sa.Column("id", sa.Integer, primary_key=True, index=True),
            sa.Column("company_id", sa.Integer, sa.ForeignKey("companies.id"), nullable=True, index=True),
            sa.Column("room_id", sa.Integer, sa.ForeignKey("chat_meeting_rooms.id", ondelete="CASCADE"), nullable=False, index=True),
            sa.Column("entity_type", sa.String(40), nullable=False),
            sa.Column("entity_ref", sa.String(120), nullable=False),
            sa.Column("label", sa.String(200), nullable=True),
            sa.Column("pinned_by_id", sa.Integer, sa.ForeignKey("users.id"), nullable=True),
            sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
        )

    if not _has_table("permis_travail"):
        op.create_table(
            "permis_travail",
            sa.Column("id", sa.Integer, primary_key=True, index=True),
            sa.Column("numero_permis", sa.String(50), nullable=False, unique=True, index=True),
            sa.Column("company_id", sa.Integer, sa.ForeignKey("companies.id"), nullable=True, index=True),
            sa.Column("type_permis", sa.String(40), nullable=False),
            sa.Column("zone", sa.String(200), nullable=False),
            sa.Column("description", sa.Text, nullable=False),
            sa.Column("intervention", sa.Text, nullable=True),
            sa.Column("mesures_preventives", sa.Text, nullable=True),
            sa.Column("valide_debut", sa.DateTime(timezone=True), nullable=True),
            sa.Column("valide_fin", sa.DateTime(timezone=True), nullable=True),
            sa.Column("statut", sa.String(30), server_default="BROUILLON"),
            sa.Column("demandeur_id", sa.Integer, sa.ForeignKey("users.id"), nullable=True),
            sa.Column("executeur_id", sa.Integer, sa.ForeignKey("users.id"), nullable=True),
            sa.Column("officier_isps_id", sa.Integer, sa.ForeignKey("users.id"), nullable=True),
            sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
            sa.Column("updated_at", sa.DateTime(timezone=True), nullable=True),
        )

    if not _has_table("signatures_permis_travail"):
        op.create_table(
            "signatures_permis_travail",
            sa.Column("id", sa.Integer, primary_key=True, index=True),
            sa.Column("permis_id", sa.Integer, sa.ForeignKey("permis_travail.id", ondelete="CASCADE"), nullable=False, index=True),
            sa.Column("role_signataire", sa.String(30), nullable=False),
            sa.Column("signataire_id", sa.Integer, sa.ForeignKey("users.id"), nullable=False, index=True),
            sa.Column("signataire_nom", sa.String(150), nullable=True),
            sa.Column("date_signature", sa.DateTime(timezone=True), server_default=sa.func.now()),
        )

    if not _has_table("heures_exposition"):
        op.create_table(
            "heures_exposition",
            sa.Column("id", sa.Integer, primary_key=True, index=True),
            sa.Column("company_id", sa.Integer, sa.ForeignKey("companies.id"), nullable=True, index=True),
            sa.Column("annee", sa.Integer, nullable=False, index=True),
            sa.Column("heures_travaillees", sa.Numeric, nullable=False),
            sa.Column("nb_employes", sa.Integer, nullable=True),
            sa.Column("jours_arret_total", sa.Numeric, nullable=True),
            sa.Column("saisi_par", sa.Integer, sa.ForeignKey("users.id"), nullable=True),
            sa.Column("source_piece", sa.String(200), nullable=True),
        )


def downgrade():
    for name in TABLES:
        if _has_table(name):
            op.drop_table(name)
