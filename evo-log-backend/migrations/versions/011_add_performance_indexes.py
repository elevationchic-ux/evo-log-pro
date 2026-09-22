"""Add performance indexes for multi-tenant scalability

Revision ID: 011_add_performance_indexes
Revises: 010_add_transactional_outbox
Create Date: 2026-09-23

"""
from alembic import op
import sqlalchemy as sa

# revision identifiers
revision = '011_add_performance_indexes'
down_revision = '010_add_transactional_outbox'
branch_labels = None
depends_on = None

def upgrade():
    # Critical indexes for multi-tenant performance
    op.create_index(
        'idx_missions_tenant_id_date',
        'missions',
        ['tenant_id', 'date_creation']
    )
    op.create_index(
        'idx_missions_statut_tenant',
        'missions',
        ['statut', 'tenant_id']
    )
    op.create_index(
        'idx_stocks_tenant_article',
        'stocks',
        ['tenant_id', 'article_id']
    )
    op.create_index(
        'idx_transactions_tenant_date',
        'transactions',
        ['tenant_id', 'date_transaction']
    )
    op.create_index(
        'idx_users_tenant_email',
        'users',
        ['tenant_id', 'email']
    )
    op.create_index(
        'idx_audit_logs_tenant_timestamp',
        'audit_logs',
        ['tenant_id', 'timestamp']
    )
    op.create_index(
        'idx_incidents_tenant_status',
        'incidents',
        ['tenant_id', 'statut']
    )
    op.create_index(
        'idx_notifications_tenant_read',
        'notifications',
        ['tenant_id', 'is_read']
    )
    op.create_index(
        'idx_company_tenant_status',
        'company',
        ['tenant_id', 'is_active']
    )

def downgrade():
    op.drop_index('idx_company_tenant_status', 'company')
    op.drop_index('idx_notifications_tenant_read', 'notifications')
    op.drop_index('idx_incidents_tenant_status', 'incidents')
    op.drop_index('idx_audit_logs_tenant_timestamp', 'audit_logs')
    op.drop_index('idx_users_tenant_email', 'users')
    op.drop_index('idx_transactions_tenant_date', 'transactions')
    op.drop_index('idx_stocks_tenant_article', 'stocks')
    op.drop_index('idx_missions_statut_tenant', 'missions')
    op.drop_index('idx_missions_tenant_id_date', 'missions')
