"""Add complete models for all modules

Revision ID: 002_complete_models
Revises: 001_initial
Create Date: 2026-08-17 02:15:00.000000

"""
from alembic import op
import sqlalchemy as sa
from datetime import datetime

# revision identifiers, used by Alembic.
revision = '002_complete_models'
down_revision = '001_initial'
branch_labels = None
depends_on = None


def upgrade():
    # Transport models
    op.create_table(
        'camions',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('immatriculation', sa.String(length=20), nullable=False),
        sa.Column('marque', sa.String(length=50), nullable=True),
        sa.Column('modele', sa.String(length=50), nullable=True),
        sa.Column('annee', sa.Integer(), nullable=True),
        sa.Column('capacite_tonnage', sa.Float(), nullable=True),
        sa.Column('status', sa.String(length=50), nullable=True),
        sa.Column('kilometrage', sa.Integer(), nullable=True),
        sa.Column('date_mise_service', sa.DateTime(timezone=True), nullable=True),
        sa.Column('derniere_maintenance', sa.DateTime(timezone=True), nullable=True),
        sa.Column('prochaine_maintenance', sa.DateTime(timezone=True), nullable=True),
        sa.Column('is_active', sa.Boolean(), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('CURRENT_TIMESTAMP'), nullable=True),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=True),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('immatriculation')
    )
    op.create_index(op.f('ix_camions_id'), 'camions', ['id'], unique=False)

    op.create_table(
        'conducteurs',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('nom', sa.String(length=100), nullable=False),
        sa.Column('prenom', sa.String(length=100), nullable=False),
        sa.Column('numero_permis', sa.String(length=50), nullable=False),
        sa.Column('date_expiration_permis', sa.DateTime(timezone=True), nullable=True),
        sa.Column('telephone', sa.String(length=20), nullable=False),
        sa.Column('email', sa.String(length=100), nullable=True),
        sa.Column('adresse', sa.Text(), nullable=True),
        sa.Column('date_embauche', sa.DateTime(timezone=True), nullable=True),
        sa.Column('is_active', sa.Boolean(), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('CURRENT_TIMESTAMP'), nullable=True),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=True),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('numero_permis')
    )

    op.create_table(
        'missions',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('reference', sa.String(length=50), nullable=False),
        sa.Column('camion_id', sa.Integer(), nullable=True),
        sa.Column('conducteur_id', sa.Integer(), nullable=True),
        sa.Column('client_id', sa.Integer(), nullable=True),
        sa.Column('type_mission', sa.String(length=50), nullable=True),
        sa.Column('statut', sa.String(length=50), nullable=True),
        sa.Column('date_debut_prevue', sa.DateTime(timezone=True), nullable=True),
        sa.Column('date_fin_prevue', sa.DateTime(timezone=True), nullable=True),
        sa.Column('date_debut_reelle', sa.DateTime(timezone=True), nullable=True),
        sa.Column('date_fin_reelle', sa.DateTime(timezone=True), nullable=True),
        sa.Column('point_depart', sa.String(length=200), nullable=True),
        sa.Column('point_arrivee', sa.String(length=200), nullable=True),
        sa.Column('distance_km', sa.Float(), nullable=True),
        sa.Column('cout_estime', sa.Float(), nullable=True),
        sa.Column('cout_reel', sa.Float(), nullable=True),
        sa.Column('notes', sa.Text(), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('CURRENT_TIMESTAMP'), nullable=True),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=True),
        sa.ForeignKeyConstraint(['camion_id'], ['camions.id'], ),
        sa.ForeignKeyConstraint(['conducteur_id'], ['conducteurs.id'], ),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('reference')
    )

    # Finance models
    op.create_table(
        'factures',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('numero', sa.String(length=50), nullable=False),
        sa.Column('client_id', sa.Integer(), nullable=True),
        sa.Column('date_emission', sa.DateTime(timezone=True), nullable=False),
        sa.Column('date_echeance', sa.DateTime(timezone=True), nullable=True),
        sa.Column('statut', sa.String(length=50), nullable=True),
        sa.Column('montant_ht', sa.Float(), nullable=False),
        sa.Column('montant_tva', sa.Float(), nullable=True),
        sa.Column('montant_ttc', sa.Float(), nullable=False),
        sa.Column('montant_paye', sa.Float(), nullable=True),
        sa.Column('reste_a_payer', sa.Float(), nullable=True),
        sa.Column('devise', sa.String(length=10), nullable=True),
        sa.Column('taux_change', sa.Float(), nullable=True),
        sa.Column('notes', sa.Text(), nullable=True),
        sa.Column('reference_client', sa.String(length=100), nullable=True),
        sa.Column('conditions_paiement', sa.Text(), nullable=True),
        sa.Column('penalites_retard', sa.Float(), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('CURRENT_TIMESTAMP'), nullable=True),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=True),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('numero')
    )

    # Magasin models
    op.create_table(
        'stocks',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('code_article', sa.String(length=50), nullable=False),
        sa.Column('designation', sa.String(length=200), nullable=False),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('categorie', sa.String(length=50), nullable=True),
        sa.Column('unite_mesure', sa.String(length=20), nullable=True),
        sa.Column('quantite_disponible', sa.Float(), nullable=True),
        sa.Column('quantite_reservee', sa.Float(), nullable=True),
        sa.Column('quantite_minimum', sa.Float(), nullable=True),
        sa.Column('quantite_maximum', sa.Float(), nullable=True),
        sa.Column('prix_unitaire', sa.Float(), nullable=True),
        sa.Column('emplacement', sa.String(length=100), nullable=True),
        sa.Column('entrepot_id', sa.Integer(), nullable=True),
        sa.Column('fournisseur_id', sa.Integer(), nullable=True),
        sa.Column('date_derniere_entree', sa.DateTime(timezone=True), nullable=True),
        sa.Column('date_derniere_sortie', sa.DateTime(timezone=True), nullable=True),
        sa.Column('is_active', sa.Boolean(), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('CURRENT_TIMESTAMP'), nullable=True),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=True),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('code_article')
    )

    # Acconage models
    op.create_table(
        'navires',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('nom', sa.String(length=100), nullable=False),
        sa.Column('imo', sa.String(length=20), nullable=True),
        sa.Column('pavillon', sa.String(length=50), nullable=True),
        sa.Column('type_navire', sa.String(length=50), nullable=True),
        sa.Column('longueur', sa.Float(), nullable=True),
        sa.Column('largeur', sa.Float(), nullable=True),
        sa.Column('tirant_eau', sa.Float(), nullable=True),
        sa.Column('port_en_lourd', sa.Float(), nullable=True),
        sa.Column('deadweight', sa.Float(), nullable=True),
        sa.Column('annee_construction', sa.Integer(), nullable=True),
        sa.Column('proprietaire', sa.String(length=100), nullable=True),
        sa.Column('armateur', sa.String(length=100), nullable=True),
        sa.Column('is_active', sa.Boolean(), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('CURRENT_TIMESTAMP'), nullable=True),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=True),
        sa.PrimaryKeyConstraint('id')
    )

    op.create_table(
        'escales',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('numero_escale', sa.String(length=50), nullable=False),
        sa.Column('navire_id', sa.Integer(), nullable=True),
        sa.Column('port_id', sa.Integer(), nullable=True),
        sa.Column('poste_quai', sa.String(length=50), nullable=True),
        sa.Column('date_arrivee_prevue', sa.DateTime(timezone=True), nullable=True),
        sa.Column('date_arrivee_reelle', sa.DateTime(timezone=True), nullable=True),
        sa.Column('date_depart_prevue', sa.DateTime(timezone=True), nullable=True),
        sa.Column('date_depart_reelle', sa.DateTime(timezone=True), nullable=True),
        sa.Column('statut', sa.String(length=50), nullable=True),
        sa.Column('marchandise', sa.Text(), nullable=True),
        sa.Column('tonnage', sa.Float(), nullable=True),
        sa.Column('nombre_conteneurs', sa.Integer(), nullable=True),
        sa.Column('agent', sa.String(length=100), nullable=True),
        sa.Column('notes', sa.Text(), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('CURRENT_TIMESTAMP'), nullable=True),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=True),
        sa.ForeignKeyConstraint(['navire_id'], ['navires.id'], ),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('numero_escale')
    )

    # Transit models
    op.create_table(
        'dossiers_transit',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('numero_dossier', sa.String(length=50), nullable=False),
        sa.Column('client_id', sa.Integer(), nullable=True),
        sa.Column('transitaire_id', sa.Integer(), nullable=True),
        sa.Column('type_transit', sa.String(length=50), nullable=True),
        sa.Column('statut', sa.String(length=50), nullable=True),
        sa.Column('date_ouverture', sa.DateTime(timezone=True), server_default=sa.text('CURRENT_TIMESTAMP'), nullable=True),
        sa.Column('date_cloture', sa.DateTime(timezone=True), nullable=True),
        sa.Column('marchandise', sa.Text(), nullable=True),
        sa.Column('valeur_marchandise', sa.Float(), nullable=True),
        sa.Column('poids_brut', sa.Float(), nullable=True),
        sa.Column('poids_net', sa.Float(), nullable=True),
        sa.Column('nombre_colis', sa.Integer(), nullable=True),
        sa.Column('origine', sa.String(length=100), nullable=True),
        sa.Column('destination', sa.String(length=100), nullable=True),
        sa.Column('moyen_transport', sa.String(length=50), nullable=True),
        sa.Column('numero_connaisse', sa.String(length=50), nullable=True),
        sa.Column('taux_change', sa.Float(), nullable=True),
        sa.Column('montant_frais', sa.Float(), nullable=True),
        sa.Column('montant_droits', sa.Float(), nullable=True),
        sa.Column('montant_tva', sa.Float(), nullable=True),
        sa.Column('montant_total', sa.Float(), nullable=True),
        sa.Column('notes', sa.Text(), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('CURRENT_TIMESTAMP'), nullable=True),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=True),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('numero_dossier')
    )

    # QHSE models
    op.create_table(
        'incidents',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('reference', sa.String(length=50), nullable=False),
        sa.Column('type_incident', sa.String(length=50), nullable=True),
        sa.Column('severite', sa.String(length=50), nullable=True),
        sa.Column('statut', sa.String(length=50), nullable=True),
        sa.Column('date_incident', sa.DateTime(timezone=True), nullable=False),
        sa.Column('heure_incident', sa.String(length=10), nullable=True),
        sa.Column('lieu', sa.String(length=200), nullable=True),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('causes', sa.Text(), nullable=True),
        sa.Column('consequences', sa.Text(), nullable=True),
        sa.Column('victimes', sa.Integer(), nullable=True),
        sa.Column('blesses', sa.Integer(), nullable=True),
        sa.Column('deces', sa.Integer(), nullable=True),
        sa.Column('degats_materiels', sa.Text(), nullable=True),
        sa.Column('impact_environnemental', sa.Text(), nullable=True),
        sa.Column('temoins', sa.Text(), nullable=True),
        sa.Column('actions_immediates', sa.Text(), nullable=True),
        sa.Column('responsable_signalement', sa.Integer(), nullable=True),
        sa.Column('responsable_enquete', sa.Integer(), nullable=True),
        sa.Column('date_rapport', sa.DateTime(timezone=True), nullable=True),
        sa.Column('photos', sa.Text(), nullable=True),
        sa.Column('documents', sa.Text(), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('CURRENT_TIMESTAMP'), nullable=True),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=True),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('reference')
    )

    # Audit logs
    op.create_table(
        'audit_logs',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('method', sa.String(length=10), nullable=True),
        sa.Column('url', sa.String(length=500), nullable=True),
        sa.Column('status_code', sa.Integer(), nullable=True),
        sa.Column('client_host', sa.String(length=50), nullable=True),
        sa.Column('user_agent', sa.String(length=500), nullable=True),
        sa.Column('process_time', sa.Float(), nullable=True),
        sa.Column('timestamp', sa.DateTime(timezone=True), server_default=sa.text('CURRENT_TIMESTAMP'), nullable=True),
        sa.Column('user_id', sa.Integer(), nullable=True),
        sa.Column('request_body', sa.Text(), nullable=True),
        sa.Column('response_body', sa.Text(), nullable=True),
        sa.Column('error_message', sa.Text(), nullable=True),
        sa.PrimaryKeyConstraint('id')
    )


def downgrade():
    op.drop_table('audit_logs')
    op.drop_table('incidents')
    op.drop_table('dossiers_transit')
    op.drop_table('escales')
    op.drop_table('navires')
    op.drop_table('stocks')
    op.drop_table('factures')
    op.drop_table('missions')
    op.drop_table('conducteurs')
    op.drop_table('camions')