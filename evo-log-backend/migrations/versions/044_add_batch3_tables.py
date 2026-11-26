"""044 : tables de persistance Batch 3 (sectoriel / securite / paiements).

Contexte : ces surfaces n'avaient AUCUNE table et renvoyaient des stubs 501 ou
des succes fabriques. Cette migration cree les vraies tables portees par tenant
pour que les routers fassent du CRUD / des agregations reels :

    - lot_serial_tracks           (tracabilite lot/serie)
    - temperature_readings        (chaine du froid, mesures saisies)
    - consignations               (palettes/conteneurs consignes)
    - blockchain_ledger           (registre append-only a chainage SHA-256 local)
    - privacy_breaches            (incidents violation APDP enregistres)
    - security_escalation_settings(regles d'escalade persistees)
    - payment_transactions        (transactions de paiement local, brouillon d'abord)

Proprietes :
    - IDEMPOTENT par introspection : table deja presente -> no-op (compatible
      base heritee de create_all, cas Railway actuel).
    - Cle etrangere organizations.id / users.id / companies.id nullable.
    - downgrade drop les sept tables (strictement additif).

Revision ID: 044_add_batch3_tables
Revises: 043_add_advanced_crud_tables
Create Date: 2026-10-07
"""
from alembic import op
import sqlalchemy as sa


revision = "044_add_batch3_tables"
down_revision = "043_add_advanced_crud_tables"
branch_labels = None
depends_on = None


TABLES = [
    "lot_serial_tracks",
    "temperature_readings",
    "consignations",
    "blockchain_ledger",
    "privacy_breaches",
    "security_escalation_settings",
    "payment_transactions",
]


def _has_table(name):
    insp = sa.inspect(op.get_bind())
    return name in set(insp.get_table_names())


def upgrade():
    if not _has_table("lot_serial_tracks"):
        op.create_table(
            "lot_serial_tracks",
            sa.Column("id", sa.Integer, primary_key=True, index=True),
            sa.Column("organization_id", sa.Integer, sa.ForeignKey("organizations.id"), nullable=True, index=True),
            sa.Column("batch_number", sa.String(80), nullable=False, index=True),
            sa.Column("serial_number", sa.String(120), nullable=True, index=True),
            sa.Column("article_code", sa.String(80), nullable=False, index=True),
            sa.Column("expiry_date", sa.String(20), nullable=True),
            sa.Column("humidity_rate_percentage", sa.Numeric, nullable=True),
            sa.Column("enregistre_par", sa.Integer, sa.ForeignKey("users.id"), nullable=True),
            sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
        )

    if not _has_table("temperature_readings"):
        op.create_table(
            "temperature_readings",
            sa.Column("id", sa.Integer, primary_key=True, index=True),
            sa.Column("organization_id", sa.Integer, sa.ForeignKey("organizations.id"), nullable=True, index=True),
            sa.Column("container_ref", sa.String(80), nullable=False, index=True),
            sa.Column("zone", sa.String(80), nullable=True),
            sa.Column("temperature_c", sa.Numeric, nullable=False),
            sa.Column("seuil_min_c", sa.Numeric, nullable=True),
            sa.Column("seuil_max_c", sa.Numeric, nullable=True),
            sa.Column("capteur_id", sa.String(80), nullable=True),
            sa.Column("mesure_le", sa.DateTime(timezone=True), nullable=True),
            sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
        )

    if not _has_table("consignations"):
        op.create_table(
            "consignations",
            sa.Column("id", sa.Integer, primary_key=True, index=True),
            sa.Column("organization_id", sa.Integer, sa.ForeignKey("organizations.id"), nullable=True, index=True),
            sa.Column("support_type", sa.String(30), nullable=True, server_default="PALETTE"),
            sa.Column("support_ref", sa.String(80), nullable=False, index=True),
            sa.Column("client_id", sa.Integer, nullable=True, index=True),
            sa.Column("quantite", sa.Numeric, nullable=True, server_default="0"),
            sa.Column("statut", sa.String(20), nullable=True, server_default="CONSIGNE"),
            sa.Column("valeur_consignation_xaf", sa.Numeric, nullable=True, server_default="0"),
            sa.Column("date_consignation", sa.DateTime(timezone=True), nullable=True),
            sa.Column("date_restitution", sa.DateTime(timezone=True), nullable=True),
            sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
        )

    if not _has_table("blockchain_ledger"):
        op.create_table(
            "blockchain_ledger",
            sa.Column("id", sa.Integer, primary_key=True, index=True),
            sa.Column("organization_id", sa.Integer, sa.ForeignKey("organizations.id"), nullable=True, index=True),
            sa.Column("height", sa.Integer, nullable=False, index=True),
            sa.Column("entity_type", sa.String(60), nullable=False),
            sa.Column("entity_id", sa.String(80), nullable=False, index=True),
            sa.Column("action", sa.String(80), nullable=False),
            sa.Column("payload_hash", sa.String(64), nullable=False),
            sa.Column("prev_hash", sa.String(64), nullable=False),
            sa.Column("block_hash", sa.String(64), nullable=False, unique=True, index=True),
            sa.Column("mined_by", sa.Integer, sa.ForeignKey("users.id"), nullable=True),
            sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
        )

    if not _has_table("privacy_breaches"):
        op.create_table(
            "privacy_breaches",
            sa.Column("id", sa.Integer, primary_key=True, index=True),
            sa.Column("organization_id", sa.Integer, sa.ForeignKey("organizations.id"), nullable=True, index=True),
            sa.Column("incident_type", sa.String(80), nullable=False),
            sa.Column("description", sa.Text, nullable=False),
            sa.Column("affected_count", sa.Integer, nullable=True, server_default="0"),
            sa.Column("statut", sa.String(30), nullable=True, server_default="ENREGISTRE"),
            sa.Column("declare_le", sa.DateTime(timezone=True), server_default=sa.func.now()),
            sa.Column("enregistre_par", sa.Integer, sa.ForeignKey("users.id"), nullable=True),
            sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
        )

    if not _has_table("security_escalation_settings"):
        op.create_table(
            "security_escalation_settings",
            sa.Column("id", sa.Integer, primary_key=True, index=True),
            sa.Column("organization_id", sa.Integer, sa.ForeignKey("organizations.id"), nullable=True, index=True),
            sa.Column("config", sa.JSON, nullable=False),
            sa.Column("updated_at", sa.DateTime(timezone=True), nullable=True),
            sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
        )

    if not _has_table("payment_transactions"):
        op.create_table(
            "payment_transactions",
            sa.Column("id", sa.Integer, primary_key=True, index=True),
            sa.Column("organization_id", sa.Integer, sa.ForeignKey("organizations.id"), nullable=True, index=True),
            sa.Column("company_id", sa.Integer, sa.ForeignKey("companies.id"), nullable=True, index=True),
            sa.Column("provider", sa.String(30), nullable=False),
            sa.Column("reference", sa.String(80), nullable=False, index=True),
            sa.Column("montant_xaf", sa.Numeric, nullable=True, server_default="0"),
            sa.Column("statut", sa.String(20), nullable=True, server_default="BROUILLON"),
            sa.Column("provider_contacte", sa.Boolean, nullable=True, server_default=sa.false()),
            sa.Column("provider_ref", sa.String(120), nullable=True),
            sa.Column("description", sa.Text, nullable=True),
            sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
            sa.Column("updated_at", sa.DateTime(timezone=True), nullable=True),
        )


def downgrade():
    for name in reversed(TABLES):
        if _has_table(name):
            op.drop_table(name)
