"""043 : tables reelles des modules avances (CRM / projets / immobilisations /
bourse de fret / cles API tenant).

Contexte : ces cinq surfaces n'avaient AUCUNE table et renvoyaient des stubs 501
(des lignes « fabriquees »). Cette migration cree de veritables tables portees
par le tenant (organization_id) pour que les routers fassent du CRUD reel.

Proprietes :
    - IDEMPOTENT par introspection : table deja presente -> no-op (compatible
      base heritee de create_all, cas Railway actuel).
    - Cle etrangere organizations.id / users.id nullable : un superadmin sans
      organisation rattachee ecrayonne organization_id = NULL, jamais de FK dur.
    - downgrade drop les cinq tables (strictement additif, aucune donnee metier).

Revision ID: 043_add_advanced_crud_tables
Revises: 042_rbac_amenagement_place_grants
Create Date: 2026-10-07
"""
from alembic import op
import sqlalchemy as sa


revision = "043_add_advanced_crud_tables"
down_revision = "042_rbac_amenagement_place_grants"
branch_labels = None
depends_on = None


TABLES = [
    "crm_opportunities",
    "logistics_projects",
    "fixed_assets",
    "freight_offers",
    "tenant_api_keys",
    "scheduled_reports",
]


def _has_table(name):
    insp = sa.inspect(op.get_bind())
    return name in set(insp.get_table_names())


def upgrade():
    if not _has_table("crm_opportunities"):
        op.create_table(
            "crm_opportunities",
            sa.Column("id", sa.Integer, primary_key=True, index=True),
            sa.Column("organization_id", sa.Integer, sa.ForeignKey("organizations.id"), nullable=True, index=True),
            sa.Column("client_name", sa.String(200), nullable=False),
            sa.Column("title", sa.String(200), nullable=False),
            sa.Column("estimated_value", sa.Numeric, nullable=True, server_default="0"),
            sa.Column("currency", sa.String(10), nullable=True, server_default="XAF"),
            sa.Column("stage", sa.String(30), nullable=True, server_default="PROSPECT"),
            sa.Column("probability", sa.Integer, nullable=True, server_default="0"),
            sa.Column("contact_person", sa.String(150), nullable=True),
            sa.Column("contact_email", sa.String(150), nullable=True),
            sa.Column("notes", sa.Text, nullable=True),
            sa.Column("created_by", sa.Integer, sa.ForeignKey("users.id"), nullable=True),
            sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
            sa.Column("updated_at", sa.DateTime(timezone=True), nullable=True),
        )

    if not _has_table("logistics_projects"):
        op.create_table(
            "logistics_projects",
            sa.Column("id", sa.Integer, primary_key=True, index=True),
            sa.Column("organization_id", sa.Integer, sa.ForeignKey("organizations.id"), nullable=True, index=True),
            sa.Column("code", sa.String(50), nullable=False, index=True),
            sa.Column("title", sa.String(200), nullable=False),
            sa.Column("budget_xaf", sa.Numeric, nullable=True, server_default="0"),
            sa.Column("spent_xaf", sa.Numeric, nullable=True, server_default="0"),
            sa.Column("start_date", sa.String(20), nullable=True),
            sa.Column("end_date", sa.String(20), nullable=True),
            sa.Column("manager_name", sa.String(150), nullable=True),
            sa.Column("status", sa.String(30), nullable=True, server_default="PLANIFIE"),
            sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
            sa.Column("updated_at", sa.DateTime(timezone=True), nullable=True),
        )

    if not _has_table("fixed_assets"):
        op.create_table(
            "fixed_assets",
            sa.Column("id", sa.Integer, primary_key=True, index=True),
            sa.Column("organization_id", sa.Integer, sa.ForeignKey("organizations.id"), nullable=True, index=True),
            sa.Column("asset_code", sa.String(50), nullable=False, index=True),
            sa.Column("name", sa.String(200), nullable=False),
            sa.Column("category", sa.String(30), nullable=True, server_default="FLEET"),
            sa.Column("acquisition_date", sa.String(20), nullable=True),
            sa.Column("acquisition_value", sa.Numeric, nullable=True, server_default="0"),
            sa.Column("residual_value", sa.Numeric, nullable=True, server_default="0"),
            sa.Column("amortization_years", sa.Integer, nullable=True, server_default="5"),
            sa.Column("amortization_method", sa.String(20), nullable=True, server_default="LINEAR"),
            sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
            sa.Column("updated_at", sa.DateTime(timezone=True), nullable=True),
        )

    if not _has_table("freight_offers"):
        op.create_table(
            "freight_offers",
            sa.Column("id", sa.Integer, primary_key=True, index=True),
            sa.Column("organization_id", sa.Integer, sa.ForeignKey("organizations.id"), nullable=True, index=True),
            sa.Column("origin", sa.String(200), nullable=False),
            sa.Column("destination", sa.String(200), nullable=False),
            sa.Column("cargo_type", sa.String(120), nullable=True),
            sa.Column("weight_tons", sa.Numeric, nullable=True, server_default="0"),
            sa.Column("offered_price_xaf", sa.Numeric, nullable=True, server_default="0"),
            sa.Column("status", sa.String(20), nullable=True, server_default="PUBLIEE"),
            sa.Column("published_by", sa.Integer, sa.ForeignKey("users.id"), nullable=True),
            sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
            sa.Column("updated_at", sa.DateTime(timezone=True), nullable=True),
        )

    if not _has_table("tenant_api_keys"):
        op.create_table(
            "tenant_api_keys",
            sa.Column("id", sa.Integer, primary_key=True, index=True),
            sa.Column("organization_id", sa.Integer, sa.ForeignKey("organizations.id"), nullable=True, index=True),
            sa.Column("key_name", sa.String(150), nullable=False),
            sa.Column("key_prefix", sa.String(16), nullable=False, index=True),
            sa.Column("key_hash", sa.String(64), nullable=False, unique=True),
            sa.Column("allowed_ips", sa.JSON, nullable=True),
            sa.Column("active", sa.Boolean, nullable=True, server_default=sa.true()),
            sa.Column("last_used_at", sa.DateTime(timezone=True), nullable=True),
            sa.Column("created_by", sa.Integer, sa.ForeignKey("users.id"), nullable=True),
            sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
        )

    if not _has_table("scheduled_reports"):
        op.create_table(
            "scheduled_reports",
            sa.Column("id", sa.Integer, primary_key=True, index=True),
            sa.Column("organization_id", sa.Integer, sa.ForeignKey("organizations.id"), nullable=True, index=True),
            sa.Column("report_name", sa.String(200), nullable=False),
            sa.Column("format", sa.String(10), nullable=True, server_default="PDF"),
            sa.Column("frequency", sa.String(10), nullable=True, server_default="MONTHLY"),
            sa.Column("recipients", sa.JSON, nullable=True),
            sa.Column("actif", sa.Boolean, nullable=True, server_default=sa.true()),
            sa.Column("prochaine_execution", sa.DateTime(timezone=True), nullable=True),
            sa.Column("cree_par", sa.Integer, sa.ForeignKey("users.id"), nullable=True),
            sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
        )


def downgrade():
    for name in reversed(TABLES):
        if _has_table(name):
            op.drop_table(name)
