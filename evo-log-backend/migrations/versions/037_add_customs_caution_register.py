"""037 : registre local honnete des cautions douanieres & suivi DUM/CAMCIS.

L'ecran « real-customs » reclamait trois endpoints qui renvoyaient un 501
(circuits CAMCIS, teletransmission, statut des cautions) parce que les valeurs
affichees auparavant etaient codees en dur ou generees au hasard. Or le
controle douanier est un acte a valeur legale : l'ERP ne peut pas simuler une
reponse de la DGD/CAMCIS.

En revanche, l'ERP PEUT etre le registre ou le declarant enregistre ce que le
guichet lui a reellement notifie, et suivre son cautionnement :
    - ``cautions_douanieres`` : plafond de garantie souscrit (banque cautionnaire,
      formule, plafond XAF, dates), saisi par le transitaire.
    - ``dum_customs_records`` : pour chaque DUM, le circuit officiellement attribue,
      l'accuse de teletransmission, la consommation de la caution et son apurement.
Un champ NULL signifie « pas encore notifie » : aucune valeur inventee.

Les deux tables portent ``company_id`` et sont donc automatiquement scopees par
``app/core/tenant_enforcement.py``.

Proprietes (conventions 024/027/029/030/031/032) :
    - IDEMPOTENT par introspection : table deja presente -> no-op.
    - FK en mode batch SQLite, native PostgreSQL.
    - downgrade droppe les deux tables (donnees de saisie, aucune migration
      descendante complexe requise).

Revision ID: 037_add_customs_caution_register
Revises: 036_rbac_qhse_grants
Create Date: 2026-09-25
"""
from alembic import op
import sqlalchemy as sa


revision = "037_add_customs_caution_register"
down_revision = "036_rbac_qhse_grants"
branch_labels = None
depends_on = None

T_CAUTION = "cautions_douanieres"
T_DUM = "dum_customs_records"


def upgrade():
    bind = op.get_bind()
    insp = sa.inspect(bind)
    tables = set(insp.get_table_names())

    if T_CAUTION not in tables:
        op.create_table(
            T_CAUTION,
            sa.Column("id", sa.Integer(), primary_key=True),
            sa.Column("company_id", sa.Integer(), nullable=True),
            sa.Column("reference", sa.String(60), nullable=False),
            sa.Column("banque_cautionnaire", sa.String(160), nullable=True),
            sa.Column("formule", sa.String(80), nullable=True),
            sa.Column("plafond_autorise_xaf", sa.Numeric(18, 2), nullable=False, server_default="0"),
            sa.Column("devise", sa.String(8), nullable=True, server_default="XAF"),
            sa.Column("statut", sa.String(20), nullable=True, server_default="ACTIVE"),
            sa.Column("date_debut", sa.DateTime(timezone=True), nullable=True),
            sa.Column("date_fin", sa.DateTime(timezone=True), nullable=True),
            sa.Column("notes", sa.Text(), nullable=True),
            sa.Column("created_at", sa.DateTime(timezone=True), nullable=True, server_default=sa.func.now()),
            sa.Column("updated_at", sa.DateTime(timezone=True), nullable=True),
            sa.ForeignKeyConstraint(["company_id"], ["companies.id"], name=f"fk_{T_CAUTION}_company_id_companies"),
        )
        op.create_index(f"ix_{T_CAUTION}_company_id", T_CAUTION, ["company_id"])
        op.create_index(f"ix_{T_CAUTION}_reference", T_CAUTION, ["reference"], unique=True)

    if T_DUM not in set(sa.inspect(bind).get_table_names()):
        op.create_table(
            T_DUM,
            sa.Column("id", sa.Integer(), primary_key=True),
            sa.Column("company_id", sa.Integer(), nullable=True),
            sa.Column("numero_dum", sa.String(60), nullable=False),
            sa.Column("systeme", sa.String(40), nullable=True, server_default="CAMCIS"),
            sa.Column("bureau_douane", sa.String(120), nullable=True),
            sa.Column("valeur_cif_xaf", sa.Numeric(18, 2), nullable=True),
            sa.Column("circuit", sa.String(10), nullable=True),
            sa.Column("statut_recevabilite", sa.String(60), nullable=True),
            sa.Column("inspecteur_assigne", sa.String(120), nullable=True),
            sa.Column("delai_traitement_estime", sa.String(80), nullable=True),
            sa.Column("description", sa.Text(), nullable=True),
            sa.Column("date_attribution_circuit", sa.DateTime(timezone=True), nullable=True),
            sa.Column("teletransmis_le", sa.DateTime(timezone=True), nullable=True),
            sa.Column("numero_accuse_camcis", sa.String(80), nullable=True),
            sa.Column("caution_id", sa.Integer(), nullable=True),
            sa.Column("montant_garanti_xaf", sa.Numeric(18, 2), nullable=True),
            sa.Column("quittance_tresor_emise", sa.Boolean(), nullable=True, server_default=sa.false()),
            sa.Column("numero_quittance", sa.String(80), nullable=True),
            sa.Column("apure", sa.Boolean(), nullable=True, server_default=sa.false()),
            sa.Column("date_apurement", sa.DateTime(timezone=True), nullable=True),
            sa.Column("created_at", sa.DateTime(timezone=True), nullable=True, server_default=sa.func.now()),
            sa.Column("updated_at", sa.DateTime(timezone=True), nullable=True),
            sa.ForeignKeyConstraint(["company_id"], ["companies.id"], name=f"fk_{T_DUM}_company_id_companies"),
            sa.ForeignKeyConstraint(["caution_id"], [f"{T_CAUTION}.id"], name=f"fk_{T_DUM}_caution_id_{T_CAUTION}"),
        )
        op.create_index(f"ix_{T_DUM}_company_id", T_DUM, ["company_id"])
        op.create_index(f"ix_{T_DUM}_numero_dum", T_DUM, ["numero_dum"])
        op.create_index(f"ix_{T_DUM}_caution_id", T_DUM, ["caution_id"])


def downgrade():
    bind = op.get_bind()
    insp = sa.inspect(bind)
    tables = set(insp.get_table_names())
    if T_DUM in tables:
        op.drop_table(T_DUM)
    if T_CAUTION in tables:
        op.drop_table(T_CAUTION)
