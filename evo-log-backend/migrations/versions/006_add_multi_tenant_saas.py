"""Add multi-tenant SAAS tables

Revision ID: 006_add_multi_tenant_saas
Revises: 005_add_acconage_transit_avance
Create Date: 2026-01-18

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = '006_add_multi_tenant_saas'
down_revision = '005_add_acconage_transit_avance'
branch_labels = None
depends_on = None


def upgrade():
    # ========== MULTI-TENANT TABLES ==========
    
    # Subscription Plans
    op.create_table(
        'subscription_plans',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('code', sa.String(length=50), nullable=False),
        sa.Column('nom', sa.String(length=100), nullable=False),
        sa.Column('type_plan', sa.String(length=50), nullable=False),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('prix_mensuel', sa.Float(), nullable=True, server_default='0.0'),
        sa.Column('prix_annuel', sa.Float(), nullable=True, server_default='0.0'),
        sa.Column('devise', sa.String(length=3), nullable=True, server_default='XAF'),
        sa.Column('features', sa.Text(), nullable=True),
        sa.Column('modules_inclus', sa.Text(), nullable=True),
        sa.Column('max_users', sa.Integer(), nullable=True, server_default='10'),
        sa.Column('max_storage_mb', sa.Integer(), nullable=True, server_default='1024'),
        sa.Column('max_apis_per_day', sa.Integer(), nullable=True, server_default='1000'),
        sa.Column('max_companies', sa.Integer(), nullable=True, server_default='1'),
        sa.Column('trial_days', sa.Integer(), nullable=True, server_default='14'),
        sa.Column('is_active', sa.Boolean(), nullable=True, server_default='true'),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=True),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('code')
    )
    op.create_index(op.f('ix_subscription_plans_id'), 'subscription_plans', ['id'], unique=False)
    op.create_index(op.f('ix_subscription_plans_code'), 'subscription_plans', ['code'], unique=True)
    
    # Companies
    op.create_table(
        'companies',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('code', sa.String(length=50), nullable=False),
        sa.Column('nom', sa.String(length=200), nullable=False),
        sa.Column('legal_form', sa.String(length=50), nullable=True),
        sa.Column('tax_id', sa.String(length=50), nullable=True),
        sa.Column('adresse', sa.Text(), nullable=True),
        sa.Column('ville', sa.String(length=100), nullable=True),
        sa.Column('pays', sa.String(length=50), nullable=True, server_default='Cameroun'),
        sa.Column('telephone', sa.String(length=20), nullable=True),
        sa.Column('email', sa.String(length=100), nullable=True),
        sa.Column('website', sa.String(length=255), nullable=True),
        sa.Column('logo_url', sa.String(length=255), nullable=True),
        sa.Column('is_active', sa.Boolean(), nullable=True, server_default='true'),
        sa.Column('is_verified', sa.Boolean(), nullable=True, server_default='false'),
        sa.Column('verification_date', sa.DateTime(timezone=True), nullable=True),
        sa.Column('subscription_plan_id', sa.Integer(), nullable=True),
        sa.Column('subscription_start', sa.Date(), nullable=True),
        sa.Column('subscription_end', sa.Date(), nullable=True),
        sa.Column('max_users', sa.Integer(), nullable=True, server_default='10'),
        sa.Column('max_storage_mb', sa.Integer(), nullable=True, server_default='1024'),
        sa.Column('max_apis_per_day', sa.Integer(), nullable=True, server_default='1000'),
        sa.Column('current_users', sa.Integer(), nullable=True, server_default='0'),
        sa.Column('current_storage_mb', sa.Integer(), nullable=True, server_default='0'),
        sa.Column('current_apis_today', sa.Integer(), nullable=True, server_default='0'),
        sa.Column('last_api_reset', sa.Date(), nullable=True),
        sa.Column('subdomain', sa.String(length=100), nullable=True),
        sa.Column('custom_domain', sa.String(length=100), nullable=True),
        sa.Column('primary_color', sa.String(length=7), nullable=True, server_default='#3B82F6'),
        sa.Column('secondary_color', sa.String(length=7), nullable=True, server_default='#10B981'),
        sa.Column('banner_url', sa.String(length=255), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('created_by', sa.Integer(), nullable=True),
        sa.ForeignKeyConstraint(['subscription_plan_id'], ['subscription_plans.id'], ),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('code'),
        sa.UniqueConstraint('subdomain'),
        sa.UniqueConstraint('custom_domain')
    )
    op.create_index(op.f('ix_companies_id'), 'companies', ['id'], unique=False)
    op.create_index(op.f('ix_companies_code'), 'companies', ['code'], unique=True)
    
    # Subscriptions
    op.create_table(
        'subscriptions',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('company_id', sa.Integer(), nullable=False),
        sa.Column('plan_id', sa.Integer(), nullable=False),
        sa.Column('start_date', sa.Date(), nullable=False),
        sa.Column('end_date', sa.Date(), nullable=False),
        sa.Column('trial_end_date', sa.Date(), nullable=True),
        sa.Column('status', sa.String(length=50), nullable=True, server_default='trial'),
        sa.Column('amount', sa.Float(), nullable=True),
        sa.Column('currency', sa.String(length=3), nullable=True, server_default='XAF'),
        sa.Column('payment_method', sa.String(length=50), nullable=True),
        sa.Column('payment_reference', sa.String(length=100), nullable=True),
        sa.Column('auto_renew', sa.Boolean(), nullable=True, server_default='true'),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=True),
        sa.ForeignKeyConstraint(['company_id'], ['companies.id'], ),
        sa.ForeignKeyConstraint(['plan_id'], ['subscription_plans.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_subscriptions_id'), 'subscriptions', ['id'], unique=False)
    
    # Departments
    op.create_table(
        'departments',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('company_id', sa.Integer(), nullable=False),
        sa.Column('code', sa.String(length=50), nullable=False),
        sa.Column('nom', sa.String(length=100), nullable=False),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('parent_id', sa.Integer(), nullable=True),
        sa.Column('manager_id', sa.Integer(), nullable=True),
        sa.Column('modules_allowed', sa.Text(), nullable=True),
        sa.Column('is_active', sa.Boolean(), nullable=True, server_default='true'),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=True),
        sa.ForeignKeyConstraint(['company_id'], ['companies.id'], ),
        sa.ForeignKeyConstraint(['parent_id'], ['departments.id'], ),
        sa.ForeignKeyConstraint(['manager_id'], ['users.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_departments_id'), 'departments', ['id'], unique=False)
    
    # B2B Portals
    op.create_table(
        'b2b_portals',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('company_id', sa.Integer(), nullable=False),
        sa.Column('subdomain', sa.String(length=100), nullable=True),
        sa.Column('custom_domain', sa.String(length=100), nullable=True),
        sa.Column('primary_color', sa.String(length=7), nullable=True, server_default='#3B82F6'),
        sa.Column('secondary_color', sa.String(length=7), nullable=True, server_default='#10B981'),
        sa.Column('accent_color', sa.String(length=7), nullable=True, server_default='#F59E0B'),
        sa.Column('background_color', sa.String(length=7), nullable=True, server_default='#FFFFFF'),
        sa.Column('text_color', sa.String(length=7), nullable=True, server_default='#1F2937'),
        sa.Column('logo_url', sa.String(length=255), nullable=True),
        sa.Column('banner_url', sa.String(length=255), nullable=True),
        sa.Column('favicon_url', sa.String(length=255), nullable=True),
        sa.Column('custom_css', sa.Text(), nullable=True),
        sa.Column('custom_js', sa.Text(), nullable=True),
        sa.Column('enable_chat', sa.Boolean(), nullable=True, server_default='true'),
        sa.Column('enable_quotes', sa.Boolean(), nullable=True, server_default='true'),
        sa.Column('enable_tracking', sa.Boolean(), nullable=True, server_default='true'),
        sa.Column('enable_api', sa.Boolean(), nullable=True, server_default='false'),
        sa.Column('email_from_name', sa.String(length=100), nullable=True),
        sa.Column('email_from_address', sa.String(length=100), nullable=True),
        sa.Column('email_signature', sa.Text(), nullable=True),
        sa.Column('is_active', sa.Boolean(), nullable=True, server_default='true'),
        sa.Column('published_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=True),
        sa.ForeignKeyConstraint(['company_id'], ['companies.id'], ),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('company_id'),
        sa.UniqueConstraint('subdomain'),
        sa.UniqueConstraint('custom_domain')
    )
    op.create_index(op.f('ix_b2b_portals_id'), 'b2b_portals', ['id'], unique=False)
    
    # Tenant Audit Logs
    op.create_table(
        'tenant_audit_logs',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('company_id', sa.Integer(), nullable=True),
        sa.Column('user_id', sa.Integer(), nullable=True),
        sa.Column('action', sa.String(length=100), nullable=False),
        sa.Column('entity_type', sa.String(length=50), nullable=True),
        sa.Column('entity_id', sa.Integer(), nullable=True),
        sa.Column('old_values', sa.Text(), nullable=True),
        sa.Column('new_values', sa.Text(), nullable=True),
        sa.Column('ip_address', sa.String(length=50), nullable=True),
        sa.Column('user_agent', sa.String(length=255), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
        sa.ForeignKeyConstraint(['company_id'], ['companies.id'], ),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_tenant_audit_logs_id'), 'tenant_audit_logs', ['id'], unique=False)
    
    # Add multi-tenant columns to users table
    op.add_column('users', sa.Column('company_id', sa.Integer(), nullable=True))
    op.add_column('users', sa.Column('department_id', sa.Integer(), nullable=True))
    op.add_column('users', sa.Column('role_level', sa.Integer(), nullable=True, server_default='3'))
    op.add_column('users', sa.Column('is_b2b', sa.Boolean(), nullable=True, server_default='false'))
    op.add_column('users', sa.Column('b2b_portal_id', sa.Integer(), nullable=True))
    op.add_column('users', sa.Column('avatar_url', sa.String(length=255), nullable=True))
    op.add_column('users', sa.Column('bio', sa.Text(), nullable=True))
    op.add_column('users', sa.Column('language', sa.String(length=10), nullable=True, server_default='fr'))
    op.add_column('users', sa.Column('timezone', sa.String(length=50), nullable=True, server_default='Africa/Douala'))
    op.add_column('users', sa.Column('failed_login_attempts', sa.Integer(), nullable=True, server_default='0'))
    op.add_column('users', sa.Column('locked_until', sa.DateTime(timezone=True), nullable=True))
    op.add_column('users', sa.Column('created_by', sa.Integer(), nullable=True))
    
    op.create_foreign_key('users_company_id_fkey', 'users', 'companies', ['company_id'], ['id'])
    op.create_foreign_key('users_department_id_fkey', 'users', 'departments', ['department_id'], ['id'])
    op.create_foreign_key('users_b2b_portal_id_fkey', 'users', 'b2b_portals', ['b2b_portal_id'], ['id'])
    
    # Add role_level and company_id to roles table
    op.add_column('roles', sa.Column('level', sa.Integer(), nullable=True, server_default='3'))
    op.add_column('roles', sa.Column('company_id', sa.Integer(), nullable=True))
    op.add_column('roles', sa.Column('is_system', sa.Boolean(), nullable=True, server_default='false'))
    
    op.create_foreign_key('roles_company_id_fkey', 'roles', 'companies', ['company_id'], ['id'])


def downgrade():
    # Remove foreign keys
    op.drop_constraint('roles_company_id_fkey', 'roles', type_='foreignkey')
    op.drop_constraint('users_b2b_portal_id_fkey', 'users', type_='foreignkey')
    op.drop_constraint('users_department_id_fkey', 'users', type_='foreignkey')
    op.drop_constraint('users_company_id_fkey', 'users', type_='foreignkey')
    
    # Remove columns from users
    op.drop_column('users', 'created_by')
    op.drop_column('users', 'locked_until')
    op.drop_column('users', 'failed_login_attempts')
    op.drop_column('users', 'timezone')
    op.drop_column('users', 'language')
    op.drop_column('users', 'bio')
    op.drop_column('users', 'avatar_url')
    op.drop_column('users', 'b2b_portal_id')
    op.drop_column('users', 'is_b2b')
    op.drop_column('users', 'role_level')
    op.drop_column('users', 'department_id')
    op.drop_column('users', 'company_id')
    
    # Remove columns from roles
    op.drop_column('roles', 'is_system')
    op.drop_column('roles', 'company_id')
    op.drop_column('roles', 'level')
    
    # Drop tables
    op.drop_index(op.f('ix_tenant_audit_logs_id'), table_name='tenant_audit_logs')
    op.drop_table('tenant_audit_logs')
    
    op.drop_index(op.f('ix_b2b_portals_id'), table_name='b2b_portals')
    op.drop_table('b2b_portals')
    
    op.drop_index(op.f('ix_departments_id'), table_name='departments')
    op.drop_table('departments')
    
    op.drop_index(op.f('ix_subscriptions_id'), table_name='subscriptions')
    op.drop_table('subscriptions')
    
    op.drop_index(op.f('ix_companies_code'), table_name='companies')
    op.drop_index(op.f('ix_companies_id'), table_name='companies')
    op.drop_table('companies')
    
    op.drop_index(op.f('ix_subscription_plans_code'), table_name='subscription_plans')
    op.drop_index(op.f('ix_subscription_plans_id'), table_name='subscription_plans')
    op.drop_table('subscription_plans')
