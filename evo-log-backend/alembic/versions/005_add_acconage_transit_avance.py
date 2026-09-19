"""Add advanced acconage, transit, warehouse and transport international models

Revision ID: 005_add_complete_modules
Revises: 004_add_advanced_models
Create Date: 2026-08-17

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql, sqlite

# revision identifiers, used by Alembic.
revision = '005_add_complete_modules'
down_revision = '004_add_advanced_models'
branch_labels = None
depends_on = None


def upgrade():
    # Check if using PostgreSQL or SQLite
    dialect = op.get_context().dialect.name
    
    # ========== ACCONAGE TABLES ==========
    
    # Stowage Plans
    op.create_table(
        'stowage_plans',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('navire_id', sa.Integer(), nullable=True),
        sa.Column('voyage_id', sa.String(length=50), nullable=True),
        sa.Column('plan_pdf', sa.String(length=255), nullable=True),
        sa.Column('date_creation', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
        sa.Column('valide', sa.Boolean(), nullable=True, server_default='false'),
        sa.Column('valide_par', sa.Integer(), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
        sa.ForeignKeyConstraint(['navire_id'], ['navires.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_stowage_plans_id'), 'stowage_plans', ['id'], unique=False)
    
    # Container Positions
    op.create_table(
        'positions_conteneur',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('stowage_plan_id', sa.Integer(), nullable=True),
        sa.Column('conteneur_id', sa.Integer(), nullable=True),
        sa.Column('bay', sa.Integer(), nullable=True),
        sa.Column('row', sa.Integer(), nullable=True),
        sa.Column('tier', sa.Integer(), nullable=True),
        sa.Column('poids', sa.Float(), nullable=True),
        sa.Column('type_marchandise', sa.String(length=50), nullable=True),
        sa.Column('port_dechargement', sa.String(length=50), nullable=True),
        sa.Column('dangereux', sa.Boolean(), nullable=True, server_default='false'),
        sa.Column('classe_imdg', sa.String(length=10), nullable=True),
        sa.Column('reefer', sa.Boolean(), nullable=True, server_default='false'),
        sa.Column('temperature', sa.Float(), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
        sa.ForeignKeyConstraint(['conteneur_id'], ['conteneurs.id'], ),
        sa.ForeignKeyConstraint(['stowage_plan_id'], ['stowage_plans.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_positions_conteneur_id'), 'positions_conteneur', ['id'], unique=False)
    
    # Grues
    op.create_table(
        'grues',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('code', sa.String(length=50), nullable=False),
        sa.Column('type_grue', sa.String(length=50), nullable=True),
        sa.Column('capacite_tonnes', sa.Float(), nullable=True),
        sa.Column('portee_metres', sa.Float(), nullable=True),
        sa.Column('hauteur_metres', sa.Float(), nullable=True),
        sa.Column('poste_quai', sa.String(length=50), nullable=True),
        sa.Column('statut', sa.String(length=20), nullable=True, server_default='disponible'),
        sa.Column('date_maintenance', sa.Date(), nullable=True),
        sa.Column('prochaine_maintenance', sa.Date(), nullable=True),
        sa.Column('operator_id', sa.Integer(), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=True),
        sa.ForeignKeyConstraint(['operator_id'], ['users.id'], ),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('code')
    )
    op.create_index(op.f('ix_grues_id'), 'grues', ['id'], unique=False)
    
    # Crane Reservations
    op.create_table(
        'reservations_grue',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('grue_id', sa.Integer(), nullable=True),
        sa.Column('operation_id', sa.Integer(), nullable=True),
        sa.Column('date_debut', sa.DateTime(timezone=True), nullable=True),
        sa.Column('date_fin', sa.DateTime(timezone=True), nullable=True),
        sa.Column('statut', sa.String(length=20), nullable=True, server_default='reserve'),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
        sa.ForeignKeyConstraint(['grue_id'], ['grues.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_reservations_grue_id'), 'reservations_grue', ['id'], unique=False)
    
    # Tugboats
    op.create_table(
        'remorqueurs',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('nom', sa.String(length=100), nullable=False),
        sa.Column('puissance_cv', sa.Integer(), nullable=True),
        sa.Column('longueur', sa.Float(), nullable=True),
        sa.Column('port_id', sa.Integer(), nullable=True),
        sa.Column('statut', sa.String(length=20), nullable=True, server_default='disponible'),
        sa.Column('capitaine_id', sa.Integer(), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=True),
        sa.ForeignKeyConstraint(['capitaine_id'], ['users.id'], ),
        sa.ForeignKeyConstraint(['port_id'], ['agencies.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_remorqueurs_id'), 'remorqueurs', ['id'], unique=False)
    
    # Berthing Operations
    op.create_table(
        'amarages',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('escale_id', sa.Integer(), nullable=True),
        sa.Column('remorqueur_id', sa.Integer(), nullable=True),
        sa.Column('type_amarage', sa.String(length=50), nullable=True),
        sa.Column('date_debut', sa.DateTime(timezone=True), nullable=True),
        sa.Column('date_fin', sa.DateTime(timezone=True), nullable=True),
        sa.Column('duree_heures', sa.Float(), nullable=True),
        sa.Column('cout', sa.Float(), nullable=True),
        sa.Column('notes', sa.Text(), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
        sa.ForeignKeyConstraint(['escale_id'], ['escales.id'], ),
        sa.ForeignKeyConstraint(['remorqueur_id'], ['remorqueurs.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_amarages_id'), 'amarages', ['id'], unique=False)
    
    # Containers
    op.create_table(
        'conteneurs',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('numero', sa.String(length=20), nullable=False),
        sa.Column('type_conteneur', sa.String(length=20), nullable=True),
        sa.Column('statut', sa.String(length=20), nullable=True),
        sa.Column('tare_weight', sa.Float(), nullable=True),
        sa.Column('gross_weight', sa.Float(), nullable=True),
        sa.Column('net_weight', sa.Float(), nullable=True),
        sa.Column('navire_id', sa.Integer(), nullable=True),
        sa.Column('proprietaire', sa.String(length=100), nullable=True),
        sa.Column('scelle', sa.String(length=50), nullable=True),
        sa.Column('date_scelle', sa.Date(), nullable=True),
        sa.Column('inspection_phasanitaire', sa.Boolean(), nullable=True, server_default='false'),
        sa.Column('date_inspection', sa.Date(), nullable=True),
        sa.Column('certificat_origine', sa.String(length=255), nullable=True),
        sa.Column('notes', sa.Text(), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=True),
        sa.ForeignKeyConstraint(['navire_id'], ['navires.id'], ),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('numero')
    )
    op.create_index(op.f('ix_conteneurs_id'), 'conteneurs', ['id'], unique=False)
    op.create_index(op.f('ix_conteneurs_numero'), 'conteneurs', ['numero'], unique=True)
    
    # Bill of Lading
    op.create_table(
        'connaissements',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('numero_bl', sa.String(length=50), nullable=False),
        sa.Column('conteneur_id', sa.Integer(), nullable=True),
        sa.Column('type_bl', sa.String(length=20), nullable=True),
        sa.Column('chargeur', sa.String(length=100), nullable=True),
        sa.Column('destinataire', sa.String(length=100), nullable=True),
        sa.Column('port_embarquement', sa.String(length=50), nullable=True),
        sa.Column('port_dechargement', sa.String(length=50), nullable=True),
        sa.Column('date_emission', sa.Date(), nullable=True),
        sa.Column('montant_freight', sa.Numeric(precision=15, scale=2), nullable=True),
        sa.Column('devise', sa.String(length=3), nullable=True, server_default='XAF'),
        sa.Column('signe_par', sa.String(length=100), nullable=True),
        sa.Column('statut', sa.String(length=20), nullable=True, server_default='emis'),
        sa.Column('escale_id', sa.Integer(), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=True),
        sa.ForeignKeyConstraint(['conteneur_id'], ['conteneurs.id'], ),
        sa.ForeignKeyConstraint(['escale_id'], ['escales.id'], ),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('numero_bl')
    )
    op.create_index(op.f('ix_connaissements_id'), 'connaissements', ['id'], unique=False)
    op.create_index(op.f('ix_connaissements_numero_bl'), 'connaissements', ['numero_bl'], unique=True)
    
    # ========== TRANSIT AVANCE TABLES ==========
    
    # Customs Offices
    op.create_table(
        'bureaux_douane',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('code', sa.String(length=20), nullable=False),
        sa.Column('nom', sa.String(length=100), nullable=False),
        sa.Column('type_bureau', sa.String(length=20), nullable=True),
        sa.Column('port_id', sa.Integer(), nullable=True),
        sa.Column('region', sa.String(length=50), nullable=True),
        sa.Column('adresse', sa.String(length=200), nullable=True),
        sa.Column('telephone', sa.String(length=50), nullable=True),
        sa.Column('email', sa.String(length=100), nullable=True),
        sa.Column('horaires', sa.Text(), nullable=True),
        sa.Column('statut', sa.String(length=20), nullable=True, server_default='actif'),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=True),
        sa.ForeignKeyConstraint(['port_id'], ['agencies.id'], ),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('code')
    )
    op.create_index(op.f('ix_bureaux_douane_id'), 'bureaux_douane', ['id'], unique=False)
    
    # ========== MAGASIN DOUANE TABLES ==========
    
    # Customs Warehouses
    op.create_table(
        'entrepots_douane',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('code', sa.String(length=50), nullable=False),
        sa.Column('nom', sa.String(length=100), nullable=False),
        sa.Column('type_entrepot', sa.String(length=50), nullable=True),
        sa.Column('regime', sa.String(length=50), nullable=True),
        sa.Column('adresse', sa.String(length=200), nullable=True),
        sa.Column('surface_m2', sa.Float(), nullable=True),
        sa.Column('capacite_tonnage', sa.Float(), nullable=True),
        sa.Column('temperature_controlee', sa.Boolean(), nullable=True, server_default='false'),
        sa.Column('temperature_min', sa.Float(), nullable=True),
        sa.Column('temperature_max', sa.Float(), nullable=True),
        sa.Column('controle_humidite', sa.Boolean(), nullable=True, server_default='false'),
        sa.Column('zone_dangereuse', sa.Boolean(), nullable=True, server_default='false'),
        sa.Column('equipe_surveillance', sa.String(length=100), nullable=True),
        sa.Column('garde_agree', sa.String(length=100), nullable=True),
        sa.Column('numero_agrement', sa.String(length=50), nullable=True),
        sa.Column('date_agrement', sa.Date(), nullable=True),
        sa.Column('date_expiration_agrement', sa.Date(), nullable=True),
        sa.Column('statut', sa.String(length=20), nullable=True, server_default='actif'),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=True),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('code')
    )
    op.create_index(op.f('ix_entrepots_douane_id'), 'entrepots_douane', ['id'], unique=False)
    
    # ========== TRANSPORT INTERNATIONAL TABLES ==========
    
    # Transport Orders
    op.create_table(
        'ordres_transport',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('numero_ot', sa.String(length=50), nullable=False),
        sa.Column('client_id', sa.Integer(), nullable=True),
        sa.Column('transporteur_id', sa.Integer(), nullable=True),
        sa.Column('camion_id', sa.Integer(), nullable=True),
        sa.Column('conducteur_id', sa.Integer(), nullable=True),
        sa.Column('type_transit', sa.String(length=50), nullable=True),
        sa.Column('statut', sa.String(length=20), nullable=True, server_default='planifie'),
        sa.Column('date_creation', sa.Date(), nullable=True),
        sa.Column('date_chargement_prevue', sa.Date(), nullable=True),
        sa.Column('date_chargement_reelle', sa.Date(), nullable=True),
        sa.Column('date_livraison_prevue', sa.Date(), nullable=True),
        sa.Column('date_livraison_reelle', sa.Date(), nullable=True),
        sa.Column('lieu_chargement', sa.String(length=200), nullable=True),
        sa.Column('lieu_livraison', sa.String(length=200), nullable=True),
        sa.Column('pays_destination', sa.String(length=50), nullable=True),
        sa.Column('code_pays_destination', sa.String(length=2), nullable=True),
        sa.Column('marchandise', sa.Text(), nullable=True),
        sa.Column('poids_net', sa.Float(), nullable=True),
        sa.Column('poids_brut', sa.Float(), nullable=True),
        sa.Column('nombre_colis', sa.Integer(), nullable=True),
        sa.Column('volume_m3', sa.Float(), nullable=True),
        sa.Column('valeur_marchandise', sa.Numeric(precision=15, scale=2), nullable=True),
        sa.Column('devise', sa.String(length=3), nullable=True, server_default='XAF'),
        sa.Column('montant_freight', sa.Numeric(precision=15, scale=2), nullable=True),
        sa.Column('devis', sa.String(length=50), nullable=True),
        sa.Column('observations', sa.Text(), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=True),
        sa.ForeignKeyConstraint(['camion_id'], ['camions.id'], ),
        sa.ForeignKeyConstraint(['conducteur_id'], ['conducteurs.id'], ),
        sa.ForeignKeyConstraint(['client_id'], ['tiers.id'], ),
        sa.ForeignKeyConstraint(['transporteur_id'], ['tiers.id'], ),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('numero_ot')
    )
    op.create_index(op.f('ix_ordres_transport_id'), 'ordres_transport', ['id'], unique=False)
    op.create_index(op.f('ix_ordres_transport_numero_ot'), 'ordres_transport', ['numero_ot'], unique=True)
    
    # TIR Carnets
    op.create_table(
        'carnets_tir',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('numero_carnet', sa.String(length=50), nullable=False),
        sa.Column('ordre_transport_id', sa.Integer(), nullable=True),
        sa.Column('pays_emission', sa.String(length=50), nullable=True),
        sa.Column('code_pays_emission', sa.String(length=2), nullable=True),
        sa.Column('date_emission', sa.Date(), nullable=True),
        sa.Column('date_validite', sa.Date(), nullable=True),
        sa.Column('nombre_virements', sa.Integer(), nullable=True, server_default='0'),
        sa.Column('bureau_depart', sa.String(length=100), nullable=True),
        sa.Column('bureau_arrivee', sa.String(length=100), nullable=True),
        sa.Column('bureau_transit', sa.String(length=100), nullable=True),
        sa.Column('montant_garantie', sa.Numeric(precision=15, scale=2), nullable=True),
        sa.Column('devise', sa.String(length=3), nullable=True, server_default='XAF'),
        sa.Column('statut', sa.String(length=20), nullable=True, server_default='actif'),
        sa.Column('observations', sa.Text(), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=True),
        sa.ForeignKeyConstraint(['ordre_transport_id'], ['ordres_transport.id'], ),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('numero_carnet')
    )
    op.create_index(op.f('ix_carnets_tir_id'), 'carnets_tir', ['id'], unique=False)
    op.create_index(op.f('ix_carnets_tir_numero_carnet'), 'carnets_tir', ['numero_carnet'], unique=True)
    
    # CMR
    op.create_table(
        'cmrs',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('numero_cmr', sa.String(length=50), nullable=False),
        sa.Column('ordre_transport_id', sa.Integer(), nullable=True),
        sa.Column('expediteur', sa.String(length=100), nullable=True),
        sa.Column('destinataire', sa.String(length=100), nullable=True),
        sa.Column('transporteur', sa.String(length=100), nullable=True),
        sa.Column('lieu_chargement', sa.String(length=200), nullable=True),
        sa.Column('lieu_livraison', sa.String(length=200), nullable=True),
        sa.Column('date_emission', sa.Date(), nullable=True),
        sa.Column('date_chargement', sa.Date(), nullable=True),
        sa.Column('date_livraison', sa.Date(), nullable=True),
        sa.Column('marchandise', sa.Text(), nullable=True),
        sa.Column('poids_net', sa.Float(), nullable=True),
        sa.Column('poids_brut', sa.Float(), nullable=True),
        sa.Column('nombre_colis', sa.Integer(), nullable=True),
        sa.Column('type_emballage', sa.String(length=50), nullable=True),
        sa.Column('valeur_marchandise', sa.Numeric(precision=15, scale=2), nullable=True),
        sa.Column('devise', sa.String(length=3), nullable=True, server_default='XAF'),
        sa.Column('instructions_speciales', sa.Text(), nullable=True),
        sa.Column('reserve', sa.Text(), nullable=True),
        sa.Column('signature_expediteur', sa.Boolean(), nullable=True, server_default='false'),
        sa.Column('signature_transporteur', sa.Boolean(), nullable=True, server_default='false'),
        sa.Column('signature_destinataire', sa.Boolean(), nullable=True, server_default='false'),
        sa.Column('statut', sa.String(length=20), nullable=True, server_default='emis'),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=True),
        sa.ForeignKeyConstraint(['ordre_transport_id'], ['ordres_transport.id'], ),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('numero_cmr')
    )
    op.create_index(op.f('ix_cmrs_id'), 'cmrs', ['id'], unique=False)
    op.create_index(op.f('ix_cmrs_numero_cmr'), 'cmrs', ['numero_cmr'], unique=True)
    
    # ========== ACQUISITION TABLES ==========
    
    # Appels Offres
    op.create_table(
        'appels_offres',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('numero_appel', sa.String(length=50), nullable=False),
        sa.Column('titre', sa.String(length=200), nullable=False),
        sa.Column('type_appel', sa.String(length=50), nullable=True),
        sa.Column('statut', sa.String(length=20), nullable=True, server_default='brouillon'),
        sa.Column('date_publication', sa.Date(), nullable=True),
        sa.Column('date_limite', sa.Date(), nullable=True),
        sa.Column('date_ouverture', sa.Date(), nullable=True),
        sa.Column('date_attribution', sa.Date(), nullable=True),
        sa.Column('budget_estime', sa.Numeric(precision=15, scale=2), nullable=True),
        sa.Column('devise', sa.String(length=3), nullable=True, server_default='XAF'),
        sa.Column('responsable', sa.String(length=100), nullable=True),
        sa.Column('departement', sa.String(length=50), nullable=True),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('conditions_participation', sa.Text(), nullable=True),
        sa.Column('documents_requis', sa.Text(), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=True),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('numero_appel')
    )
    op.create_index(op.f('ix_appels_offres_id'), 'appels_offres', ['id'], unique=False)
    op.create_index(op.f('ix_appels_offres_numero_appel'), 'appels_offres', ['numero_appel'], unique=True)
    
    # Cahiers Charges
    op.create_table(
        'cahiers_charges',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('numero_cdc', sa.String(length=50), nullable=False),
        sa.Column('appel_offres_id', sa.Integer(), nullable=True),
        sa.Column('version', sa.Integer(), nullable=True, server_default='1'),
        sa.Column('date_version', sa.Date(), nullable=True),
        sa.Column('objet', sa.String(length=500), nullable=False),
        sa.Column('description_technique', sa.Text(), nullable=True),
        sa.Column('specifications', sa.Text(), nullable=True),
        sa.Column('normes', sa.Text(), nullable=True),
        sa.Column('conditions_commerciales', sa.Text(), nullable=True),
        sa.Column('conditions_paiement', sa.Text(), nullable=True),
        sa.Column('delai_livraison', sa.Integer(), nullable=True),
        sa.Column('penalites_retard', sa.Numeric(precision=15, scale=2), nullable=True),
        sa.Column('devise', sa.String(length=3), nullable=True, server_default='XAF'),
        sa.Column('garanties', sa.Text(), nullable=True),
        sa.Column('clauses_speciales', sa.Text(), nullable=True),
        sa.Column('approuve_par', sa.String(length=100), nullable=True),
        sa.Column('date_approbation', sa.Date(), nullable=True),
        sa.Column('statut', sa.String(length=20), nullable=True, server_default='brouillon'),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=True),
        sa.ForeignKeyConstraint(['appel_offres_id'], ['appels_offres.id'], ),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('numero_cdc')
    )
    op.create_index(op.f('ix_cahiers_charges_id'), 'cahiers_charges', ['id'], unique=False)
    op.create_index(op.f('ix_cahiers_charges_numero_cdc'), 'cahiers_charges', ['numero_cdc'], unique=True)
    
    # Lignes CDC
    op.create_table(
        'lignes_cdc',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('cdc_id', sa.Integer(), nullable=True),
        sa.Column('article_id', sa.Integer(), nullable=True),
        sa.Column('designation', sa.String(length=200), nullable=False),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('quantite', sa.Float(), nullable=True),
        sa.Column('unite', sa.String(length=20), nullable=True),
        sa.Column('specifications_detaillees', sa.Text(), nullable=True),
        sa.Column('norme', sa.String(length=50), nullable=True),
        sa.Column('classe', sa.String(length=50), nullable=True),
        sa.Column('origine', sa.String(length=50), nullable=True),
        sa.Column('budget_unitaire', sa.Numeric(precision=15, scale=2), nullable=True),
        sa.Column('budget_total', sa.Numeric(precision=15, scale=2), nullable=True),
        sa.Column('devise', sa.String(length=3), nullable=True, server_default='XAF'),
        sa.Column('priorite', sa.String(length=20), nullable=True),
        sa.Column('statut', sa.String(length=20), nullable=True, server_default='actif'),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=True),
        sa.ForeignKeyConstraint(['article_id'], ['stocks.id'], ),
        sa.ForeignKeyConstraint(['cdc_id'], ['cahiers_charges.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_lignes_cdc_id'), 'lignes_cdc', ['id'], unique=False)
    
    # Offres
    op.create_table(
        'offres',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('numero_offre', sa.String(length=50), nullable=False),
        sa.Column('appel_offres_id', sa.Integer(), nullable=True),
        sa.Column('fournisseur_id', sa.Integer(), nullable=True),
        sa.Column('date_reception', sa.Date(), nullable=True),
        sa.Column('date_validite', sa.Date(), nullable=True),
        sa.Column('montant_total', sa.Numeric(precision=15, scale=2), nullable=True),
        sa.Column('devise', sa.String(length=3), nullable=True, server_default='XAF'),
        sa.Column('delai_livraison', sa.Integer(), nullable=True),
        sa.Column('validite_offre', sa.Integer(), nullable=True),
        sa.Column('notes', sa.Text(), nullable=True),
        sa.Column('statut', sa.String(length=20), nullable=True, server_default='recu'),
        sa.Column('raison_rejet', sa.Text(), nullable=True),
        sa.Column('rang', sa.Integer(), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=True),
        sa.ForeignKeyConstraint(['appel_offres_id'], ['appels_offres.id'], ),
        sa.ForeignKeyConstraint(['fournisseur_id'], ['tiers.id'], ),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('numero_offre')
    )
    op.create_index(op.f('ix_offres_id'), 'offres', ['id'], unique=False)
    op.create_index(op.f('ix_offres_numero_offre'), 'offres', ['numero_offre'], unique=True)
    
    # Bons Commande
    op.create_table(
        'bons_commande',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('numero_bc', sa.String(length=50), nullable=False),
        sa.Column('contrat_cadre_id', sa.Integer(), nullable=True),
        sa.Column('fournisseur_id', sa.Integer(), nullable=True),
        sa.Column('date_creation', sa.Date(), nullable=True),
        sa.Column('date_prevue_livraison', sa.Date(), nullable=True),
        sa.Column('date_reelle_livraison', sa.Date(), nullable=True),
        sa.Column('destinataire', sa.String(length=100), nullable=True),
        sa.Column('lieu_livraison', sa.String(length=200), nullable=True),
        sa.Column('devise', sa.String(length=3), nullable=True, server_default='XAF'),
        sa.Column('montant_total', sa.Numeric(precision=15, scale=2), nullable=True),
        sa.Column('statut', sa.String(length=20), nullable=True, server_default='brouillon'),
        sa.Column('conditions_paiement', sa.String(length=50), nullable=True),
        sa.Column('notes', sa.Text(), nullable=True),
        sa.Column('valide_par', sa.String(length=100), nullable=True),
        sa.Column('date_validation', sa.Date(), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=True),
        sa.ForeignKeyConstraint(['contrat_cadre_id'], ['contrats_cadre.id'], ),
        sa.ForeignKeyConstraint(['fournisseur_id'], ['tiers.id'], ),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('numero_bc')
    )
    op.create_index(op.f('ix_bons_commande_id'), 'bons_commande', ['id'], unique=False)
    op.create_index(op.f('ix_bons_commande_numero_bc'), 'bons_commande', ['numero_bc'], unique=True)
    
    # Contrats Cadre
    op.create_table(
        'contrats_cadre',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('numero_contrat', sa.String(length=50), nullable=False),
        sa.Column('fournisseur_id', sa.Integer(), nullable=True),
        sa.Column('type_contrat', sa.String(length=50), nullable=True),
        sa.Column('date_signature', sa.Date(), nullable=True),
        sa.Column('date_debut', sa.Date(), nullable=True),
        sa.Column('date_fin', sa.Date(), nullable=True),
        sa.Column('duree_mois', sa.Integer(), nullable=True),
        sa.Column('montant_annuel', sa.Numeric(precision=15, scale=2), nullable=True),
        sa.Column('devise', sa.String(length=3), nullable=True, server_default='XAF'),
        sa.Column('conditions_renouvellement', sa.Text(), nullable=True),
        sa.Column('conditions_resiliation', sa.Text(), nullable=True),
        sa.Column('garanties', sa.Text(), nullable=True),
        sa.Column('clauses_speciales', sa.Text(), nullable=True),
        sa.Column('signe_par', sa.String(length=100), nullable=True),
        sa.Column('fonction', sa.String(length=50), nullable=True),
        sa.Column('statut', sa.String(length=20), nullable=True, server_default='actif'),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=True),
        sa.ForeignKeyConstraint(['fournisseur_id'], ['tiers.id'], ),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('numero_contrat')
    )
    op.create_index(op.f('ix_contrats_cadre_id'), 'contrats_cadre', ['id'], unique=False)
    op.create_index(op.f('ix_contrats_cadre_numero_contrat'), 'contrats_cadre', ['numero_contrat'], unique=True)
    
    # ========== FINANCE TABLES ==========
    
    # Plan Comptable OHADA
    op.create_table(
        'plan_comptable_ohada',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('numero_compte', sa.String(length=20), nullable=False),
        sa.Column('intitule', sa.String(length=200), nullable=False),
        sa.Column('type_compte', sa.String(length=50), nullable=True),
        sa.Column('classe', sa.Integer(), nullable=True),
        sa.Column('sous_classe', sa.Integer(), nullable=True),
        sa.Column('compte_racine', sa.String(length=20), nullable=True),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('devise', sa.String(length=3), nullable=True, server_default='XAF'),
        sa.Column('solde_debit', sa.Numeric(precision=15, scale=2), nullable=True, server_default='0'),
        sa.Column('solde_credit', sa.Numeric(precision=15, scale=2), nullable=True, server_default='0'),
        sa.Column('date_creation', sa.Date(), nullable=True),
        sa.Column('compte_centralisateur', sa.Boolean(), nullable=True, server_default='false'),
        sa.Column('actif', sa.Boolean(), nullable=True, server_default='true'),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=True),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('numero_compte')
    )
    op.create_index(op.f('ix_plan_comptable_ohada_id'), 'plan_comptable_ohada', ['id'], unique=False)
    op.create_index(op.f('ix_plan_comptable_ohada_numero_compte'), 'plan_comptable_ohada', ['numero_compte'], unique=True)
    
    # Ecritures Comptables
    op.create_table(
        'ecritures_comptables',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('numero_ecriture', sa.String(length=50), nullable=False),
        sa.Column('date_ecriture', sa.Date(), nullable=False),
        sa.Column('numero_piece', sa.String(length=50), nullable=True),
        sa.Column('libelle', sa.String(length=500), nullable=False),
        sa.Column('compte_id', sa.Integer(), nullable=True),
        sa.Column('tiers_id', sa.Integer(), nullable=True),
        sa.Column('debit', sa.Numeric(precision=15, scale=2), nullable=True, server_default='0'),
        sa.Column('credit', sa.Numeric(precision=15, scale=2), nullable=True, server_default='0'),
        sa.Column('devise', sa.String(length=3), nullable=True, server_default='XAF'),
        sa.Column('reference_document', sa.String(length=100), nullable=True),
        sa.Column('type_document', sa.String(length=50), nullable=True),
        sa.Column('periode', sa.String(length=50), nullable=True),
        sa.Column('journal', sa.String(length=50), nullable=True),
        sa.Column('valider', sa.Boolean(), nullable=True, server_default='false'),
        sa.Column('valide_par', sa.String(length=100), nullable=True),
        sa.Column('date_validation', sa.Date(), nullable=True),
        sa.Column('exercice_id', sa.Integer(), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=True),
        sa.ForeignKeyConstraint(['compte_id'], ['plan_comptable_ohada.id'], ),
        sa.ForeignKeyConstraint(['exercice_id'], ['exercices_comptables.id'], ),
        sa.ForeignKeyConstraint(['tiers_id'], ['tiers.id'], ),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('numero_ecriture')
    )
    op.create_index(op.f('ix_ecritures_comptables_id'), 'ecritures_comptables', ['id'], unique=False)
    op.create_index(op.f('ix_ecritures_comptables_numero_ecriture'), 'ecritures_comptables', ['numero_ecriture'], unique=True)
    
    # Exercices Comptables
    op.create_table(
        'exercices_comptables',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('numero_exercice', sa.String(length=50), nullable=False),
        sa.Column('annee', sa.Integer(), nullable=False),
        sa.Column('date_debut', sa.Date(), nullable=False),
        sa.Column('date_fin', sa.Date(), nullable=False),
        sa.Column('statut', sa.String(length=20), nullable=True, server_default='ouvert'),
        sa.Column('cloture_par', sa.String(length=100), nullable=True),
        sa.Column('date_cloture', sa.Date(), nullable=True),
        sa.Column('resultat_net', sa.Numeric(precision=15, scale=2), nullable=True),
        sa.Column('chiffre_affaires', sa.Numeric(precision=15, scale=2), nullable=True),
        sa.Column('total_actif', sa.Numeric(precision=15, scale=2), nullable=True),
        sa.Column('total_passif', sa.Numeric(precision=15, scale=2), nullable=True),
        sa.Column('devise', sa.String(length=3), nullable=True, server_default='XAF'),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=True),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('numero_exercice')
    )
    op.create_index(op.f('ix_exercices_comptables_id'), 'exercices_comptables', ['id'], unique=False)
    op.create_index(op.f('ix_exercices_comptables_numero_exercice'), 'exercices_comptables', ['numero_exercice'], unique=True)
    
    # Factures
    op.create_table(
        'factures',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('numero_facture', sa.String(length=50), nullable=False),
        sa.Column('client_id', sa.Integer(), nullable=True),
        sa.Column('type_facture', sa.String(length=20), nullable=True),
        sa.Column('date_emission', sa.Date(), nullable=False),
        sa.Column('date_echeance', sa.Date(), nullable=True),
        sa.Column('date_paiement', sa.Date(), nullable=True),
        sa.Column('montant_ht', sa.Numeric(precision=15, scale=2), nullable=False),
        sa.Column('taux_tva', sa.Float(), nullable=True, server_default='19.25'),
        sa.Column('montant_tva', sa.Numeric(precision=15, scale=2), nullable=True, server_default='0'),
        sa.Column('montant_ttc', sa.Numeric(precision=15, scale=2), nullable=False),
        sa.Column('devise', sa.String(length=3), nullable=True, server_default='XAF'),
        sa.Column('statut', sa.String(length=20), nullable=True, server_default='brouillon'),
        sa.Column('conditions_paiement', sa.String(length=50), nullable=True),
        sa.Column('notes', sa.Text(), nullable=True),
        sa.Column('reglement_partiel', sa.Numeric(precision=15, scale=2), nullable=True, server_default='0'),
        sa.Column('solde_restant', sa.Numeric(precision=15, scale=2), nullable=True),
        sa.Column('comptabilise', sa.Boolean(), nullable=True, server_default='false'),
        sa.Column('ecriture_id', sa.Integer(), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=True),
        sa.ForeignKeyConstraint(['client_id'], ['tiers.id'], ),
        sa.ForeignKeyConstraint(['ecriture_id'], ['ecritures_comptables.id'], ),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('numero_facture')
    )
    op.create_index(op.f('ix_factures_id'), 'factures', ['id'], unique=False)
    op.create_index(op.f('ix_factures_numero_facture'), 'factures', ['numero_facture'], unique=True)
    
    # TVA Declarable
    op.create_table(
        'tva_declarables',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('numero_declaration', sa.String(length=50), nullable=False),
        sa.Column('periode', sa.String(length=50), nullable=False),
        sa.Column('date_declaration', sa.Date(), nullable=True),
        sa.Column('date_limite', sa.Date(), nullable=True),
        sa.Column('regime_tva', sa.String(length=50), nullable=True),
        sa.Column('base_imposable', sa.Numeric(precision=15, scale=2), nullable=True, server_default='0'),
        sa.Column('tva_collectee', sa.Numeric(precision=15, scale=2), nullable=True, server_default='0'),
        sa.Column('tva_deductible', sa.Numeric(precision=15, scale=2), nullable=True, server_default='0'),
        sa.Column('tva_a_payer', sa.Numeric(precision=15, scale=2), nullable=True, server_default='0'),
        sa.Column('devise', sa.String(length=3), nullable=True, server_default='XAF'),
        sa.Column('statut', sa.String(length=20), nullable=True, server_default='due'),
        sa.Column('montant_paye', sa.Numeric(precision=15, scale=2), nullable=True, server_default='0'),
        sa.Column('date_paiement', sa.Date(), nullable=True),
        sa.Column('reference_paiement', sa.String(length=100), nullable=True),
        sa.Column('notes', sa.Text(), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=True),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('numero_declaration')
    )
    op.create_index(op.f('ix_tva_declarables_id'), 'tva_declarables', ['id'], unique=False)
    op.create_index(op.f('ix_tva_declarables_numero_declaration'), 'tva_declarables', ['numero_declaration'], unique=True)
    
    # IS Declarable
    op.create_table(
        'is_declarables',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('numero_declaration', sa.String(length=50), nullable=False),
        sa.Column('exercice_id', sa.Integer(), nullable=True),
        sa.Column('annee', sa.Integer(), nullable=False),
        sa.Column('regime_is', sa.String(length=50), nullable=True),
        sa.Column('benefice_fiscal', sa.Numeric(precision=15, scale=2), nullable=True, server_default='0'),
        sa.Column('taux_imposition', sa.Float(), nullable=True, server_default='33'),
        sa.Column('is_du', sa.Numeric(precision=15, scale=2), nullable=True, server_default='0'),
        sa.Column('is_minimum', sa.Numeric(precision=15, scale=2), nullable=True, server_default='0'),
        sa.Column('is_a_payer', sa.Numeric(precision=15, scale=2), nullable=True, server_default='0'),
        sa.Column('devise', sa.String(length=3), nullable=True, server_default='XAF'),
        sa.Column('statut', sa.String(length=20), nullable=True, server_default='due'),
        sa.Column('date_declaration', sa.Date(), nullable=True),
        sa.Column('date_limite', sa.Date(), nullable=True),
        sa.Column('montant_paye', sa.Numeric(precision=15, scale=2), nullable=True, server_default='0'),
        sa.Column('date_paiement', sa.Date(), nullable=True),
        sa.Column('reference_paiement', sa.String(length=100), nullable=True),
        sa.Column('notes', sa.Text(), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=True),
        sa.ForeignKeyConstraint(['exercice_id'], ['exercices_comptables.id'], ),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('numero_declaration')
    )
    op.create_index(op.f('ix_is_declarables_id'), 'is_declarables', ['id'], unique=False)
    op.create_index(op.f('ix_is_declarables_numero_declaration'), 'is_declarables', ['numero_declaration'], unique=True)
    
    # Bilan
    op.create_table(
        'bilans',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('exercice_id', sa.Integer(), nullable=True),
        sa.Column('date_bilan', sa.Date(), nullable=False),
        sa.Column('total_actif', sa.Numeric(precision=15, scale=2), nullable=True, server_default='0'),
        sa.Column('total_passif', sa.Numeric(precision=15, scale=2), nullable=True, server_default='0'),
        sa.Column('actif_immobilise', sa.Numeric(precision=15, scale=2), nullable=True, server_default='0'),
        sa.Column('actif_circulant', sa.Numeric(precision=15, scale=2), nullable=True, server_default='0'),
        sa.Column('capitaux_propres', sa.Numeric(precision=15, scale=2), nullable=True, server_default='0'),
        sa.Column('dettes_long_terme', sa.Numeric(precision=15, scale=2), nullable=True, server_default='0'),
        sa.Column('dettes_courtes', sa.Numeric(precision=15, scale=2), nullable=True, server_default='0'),
        sa.Column('resultat_exercice', sa.Numeric(precision=15, scale=2), nullable=True, server_default='0'),
        sa.Column('devise', sa.String(length=3), nullable=True, server_default='XAF'),
        sa.Column('notes', sa.Text(), nullable=True),
        sa.Column('valide_par', sa.String(length=100), nullable=True),
        sa.Column('date_validation', sa.Date(), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=True),
        sa.ForeignKeyConstraint(['exercice_id'], ['exercices_comptables.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_bilans_id'), 'bilans', ['id'], unique=False)
    
    # Compte Resultat
    op.create_table(
        'comptes_resultat',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('exercice_id', sa.Integer(), nullable=True),
        sa.Column('periode', sa.String(length=50), nullable=False),
        sa.Column('chiffre_affaires', sa.Numeric(precision=15, scale=2), nullable=True, server_default='0'),
        sa.Column('achats', sa.Numeric(precision=15, scale=2), nullable=True, server_default='0'),
        sa.Column('services_exterieurs', sa.Numeric(precision=15, scale=2), nullable=True, server_default='0'),
        sa.Column('charges_personnel', sa.Numeric(precision=15, scale=2), nullable=True, server_default='0'),
        sa.Column('impots_taxes', sa.Numeric(precision=15, scale=2), nullable=True, server_default='0'),
        sa.Column('dotations_amortissements', sa.Numeric(precision=15, scale=2), nullable=True, server_default='0'),
        sa.Column('resultat_exploitation', sa.Numeric(precision=15, scale=2), nullable=True, server_default='0'),
        sa.Column('resultat_financier', sa.Numeric(precision=15, scale=2), nullable=True, server_default='0'),
        sa.Column('resultat_exceptionnel', sa.Numeric(precision=15, scale=2), nullable=True, server_default='0'),
        sa.Column('resultat_net', sa.Numeric(precision=15, scale=2), nullable=True, server_default='0'),
        sa.Column('devise', sa.String(length=3), nullable=True, server_default='XAF'),
        sa.Column('notes', sa.Text(), nullable=True),
        sa.Column('valide_par', sa.String(length=100), nullable=True),
        sa.Column('date_validation', sa.Date(), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=True),
        sa.ForeignKeyConstraint(['exercice_id'], ['exercices_comptables.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_comptes_resultat_id'), 'comptes_resultat', ['id'], unique=False)
    
    # ========== QHSE TABLES ==========
    
    # Analyses Risques
    op.create_table(
        'analyses_risques',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('numero_analyse', sa.String(length=50), nullable=False),
        sa.Column('zone', sa.String(length=100), nullable=False),
        sa.Column('processus', sa.String(length=100), nullable=False),
        sa.Column('date_analyse', sa.Date(), nullable=False),
        sa.Column('type_risque', sa.String(length=50), nullable=True),
        sa.Column('description_danger', sa.Text(), nullable=False),
        sa.Column('causes_potentielles', sa.Text(), nullable=True),
        sa.Column('consequences', sa.Text(), nullable=True),
        sa.Column('population_exposee', sa.Integer(), nullable=True),
        sa.Column('frequence', sa.String(length=50), nullable=True),
        sa.Column('gravite', sa.String(length=20), nullable=True),
        sa.Column('probabilite', sa.Integer(), nullable=True),
        sa.Column('risque_calcule', sa.Integer(), nullable=True),
        sa.Column('niveau_risque', sa.String(length=20), nullable=True),
        sa.Column('mesures_existantes', sa.Text(), nullable=True),
        sa.Column('mesures_recommandees', sa.Text(), nullable=True),
        sa.Column('responsable', sa.String(length=100), nullable=True),
        sa.Column('date_revision', sa.Date(), nullable=True),
        sa.Column('statut', sa.String(length=20), nullable=True, server_default='actif'),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=True),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('numero_analyse')
    )
    op.create_index(op.f('ix_analyses_risques_id'), 'analyses_risques', ['id'], unique=False)
    op.create_index(op.f('ix_analyses_risques_numero_analyse'), 'analyses_risques', ['numero_analyse'], unique=True)
    
    # Accidents Travail
    op.create_table(
        'accidents_travail',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('numero_accident', sa.String(length=50), nullable=False),
        sa.Column('employe_id', sa.Integer(), nullable=True),
        sa.Column('date_accident', sa.DateTime(timezone=True), nullable=False),
        sa.Column('lieu', sa.String(length=200), nullable=False),
        sa.Column('type_accident', sa.String(length=50), nullable=True),
        sa.Column('description', sa.Text(), nullable=False),
        sa.Column('partie_corps', sa.String(length=100), nullable=True),
        sa.Column('gravite', sa.String(length=20), nullable=True),
        sa.Column('temoin1', sa.String(length=100), nullable=True),
        sa.Column('temoin2', sa.String(length=100), nullable=True),
        sa.Column('premier_secours', sa.Text(), nullable=True),
        sa.Column('hospitalisation', sa.Boolean(), nullable=True, server_default='false'),
        sa.Column('duree_hospitalisation', sa.Integer(), nullable=True),
        sa.Column('arret_travail', sa.Integer(), nullable=True),
        sa.Column('statut', sa.String(length=20), nullable=True, server_default='signale'),
        sa.Column('declarant', sa.String(length=100), nullable=True),
        sa.Column('date_declaration', sa.Date(), nullable=True),
        sa.Column('rapport_medical', sa.String(length=255), nullable=True),
        sa.Column('photos', sa.Text(), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=True),
        sa.ForeignKeyConstraint(['employe_id'], ['users.id'], ),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('numero_accident')
    )
    op.create_index(op.f('ix_accidents_travail_id'), 'accidents_travail', ['id'], unique=False)
    op.create_index(op.f('ix_accidents_travail_numero_accident'), 'accidents_travail', ['numero_accident'], unique=True)
    
    # Normes Certifications
    op.create_table(
        'normes_certifications',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('numero_certificat', sa.String(length=50), nullable=False),
        sa.Column('norme', sa.String(length=50), nullable=True),
        sa.Column('organisme', sa.String(length=100), nullable=False),
        sa.Column('date_obtention', sa.Date(), nullable=False),
        sa.Column('date_expiration', sa.Date(), nullable=False),
        sa.Column('scope', sa.Text(), nullable=True),
        sa.Column('statut', sa.String(length=20), nullable=True, server_default='actif'),
        sa.Column('numero_audit', sa.String(length=50), nullable=True),
        sa.Column('date_dernier_audit', sa.Date(), nullable=True),
        sa.Column('resultat_audit', sa.String(length=50), nullable=True),
        sa.Column('non_conformites', sa.Text(), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=True),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('numero_certificat')
    )
    op.create_index(op.f('ix_normes_certifications_id'), 'normes_certifications', ['id'], unique=False)
    op.create_index(op.f('ix_normes_certifications_numero_certificat'), 'normes_certifications', ['numero_certificat'], unique=True)
    
    # ========== DOCUMENTS TABLES ==========
    
    # Dossiers
    op.create_table(
        'dossiers',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('nom', sa.String(length=200), nullable=False),
        sa.Column('dossier_parent_id', sa.Integer(), nullable=True),
        sa.Column('proprietaire_id', sa.Integer(), nullable=True),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('chemin', sa.String(length=500), nullable=True),
        sa.Column('statut', sa.String(length=20), nullable=True, server_default='actif'),
        sa.Column('date_creation', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
        sa.Column('cree_par', sa.String(length=100), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=True),
        sa.ForeignKeyConstraint(['dossier_parent_id'], ['dossiers.id'], ),
        sa.ForeignKeyConstraint(['proprietaire_id'], ['users.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_dossiers_id'), 'dossiers', ['id'], unique=False)
    
    # Documents
    op.create_table(
        'documents',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('numero_document', sa.String(length=50), nullable=False),
        sa.Column('type_document', sa.String(length=50), nullable=True),
        sa.Column('titre', sa.String(length=200), nullable=False),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('proprietaire_id', sa.Integer(), nullable=True),
        sa.Column('dossier_id', sa.Integer(), nullable=True),
        sa.Column('fichier', sa.LargeBinary(), nullable=True),
        sa.Column('nom_fichier', sa.String(length=255), nullable=True),
        sa.Column('type_mime', sa.String(length=100), nullable=True),
        sa.Column('taille_octets', sa.Integer(), nullable=True),
        sa.Column('emplacement_stockage', sa.String(length=500), nullable=True),
        sa.Column('checksum', sa.String(length=64), nullable=True),
        sa.Column('statut', sa.String(length=20), nullable=True, server_default='brouillon'),
        sa.Column('date_creation', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
        sa.Column('date_modification', sa.DateTime(timezone=True), nullable=True),
        sa.Column('date_expiration', sa.Date(), nullable=True),
        sa.Column('confidential', sa.Boolean(), nullable=True, server_default='false'),
        sa.Column('mots_cles', sa.Text(), nullable=True),
        sa.Column('version', sa.Integer(), nullable=True, server_default='1'),
        sa.Column('version_active', sa.Boolean(), nullable=True, server_default='true'),
        sa.Column('cree_par', sa.String(length=100), nullable=True),
        sa.Column('modifie_par', sa.String(length=100), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=True),
        sa.ForeignKeyConstraint(['dossier_id'], ['dossiers.id'], ),
        sa.ForeignKeyConstraint(['proprietaire_id'], ['users.id'], ),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('numero_document')
    )
    op.create_index(op.f('ix_documents_id'), 'documents', ['id'], unique=False)
    op.create_index(op.f('ix_documents_numero_document'), 'documents', ['numero_document'], unique=True)
    
    # Versions Document
    op.create_table(
        'versions_document',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('document_id', sa.Integer(), nullable=True),
        sa.Column('numero_version', sa.Integer(), nullable=False),
        sa.Column('fichier', sa.LargeBinary(), nullable=True),
        sa.Column('nom_fichier', sa.String(length=255), nullable=True),
        sa.Column('type_mime', sa.String(length=100), nullable=True),
        sa.Column('taille_octets', sa.Integer(), nullable=True),
        sa.Column('emplacement_stockage', sa.String(length=500), nullable=True),
        sa.Column('checksum', sa.String(length=64), nullable=True),
        sa.Column('modifications', sa.Text(), nullable=True),
        sa.Column('modifie_par', sa.String(length=100), nullable=True),
        sa.Column('date_version', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
        sa.ForeignKeyConstraint(['document_id'], ['documents.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_versions_document_id'), 'versions_document', ['id'], unique=False)
    
    # Signatures Document
    op.create_table(
        'signatures_document',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('document_id', sa.Integer(), nullable=True),
        sa.Column('signataire_id', sa.Integer(), nullable=True),
        sa.Column('type_signature', sa.String(length=50), nullable=True),
        sa.Column('date_signature', sa.DateTime(timezone=True), nullable=False),
        sa.Column('certificat_id', sa.String(length=100), nullable=True),
        sa.Column('empreinte', sa.String(length=255), nullable=True),
        sa.Column('raison', sa.String(length=200), nullable=True),
        sa.Column('statut', sa.String(length=20), nullable=True, server_default='valide'),
        sa.Column('date_expiration', sa.Date(), nullable=True),
        sa.Column('ip_adresse', sa.String(length=50), nullable=True),
        sa.Column('user_agent', sa.String(length=255), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
        sa.ForeignKeyConstraint(['document_id'], ['documents.id'], ),
        sa.ForeignKeyConstraint(['signataire_id'], ['users.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_signatures_document_id'), 'signatures_document', ['id'], unique=False)
    
    # Workflows Document
    op.create_table(
        'workflows_document',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('document_id', sa.Integer(), nullable=True),
        sa.Column('nom_workflow', sa.String(length=100), nullable=False),
        sa.Column('etape_actuelle', sa.String(length=50), nullable=True),
        sa.Column('statut', sa.String(length=20), nullable=True, server_default='en_attente'),
        sa.Column('date_debut', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
        sa.Column('date_fin', sa.DateTime(timezone=True), nullable=True),
        sa.Column('initiateur_id', sa.Integer(), nullable=True),
        sa.Column('approbateur_id', sa.Integer(), nullable=True),
        sa.Column('commentaires', sa.Text(), nullable=True),
        sa.Column('historique', sa.Text(), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=True),
        sa.ForeignKeyConstraint(['approbateur_id'], ['users.id'], ),
        sa.ForeignKeyConstraint(['document_id'], ['documents.id'], ),
        sa.ForeignKeyConstraint(['initiateur_id'], ['users.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_workflows_document_id'), 'workflows_document', ['id'], unique=False)
    
    # Sceaux Numeriques
    op.create_table(
        'sceaux_numeriques',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('document_id', sa.Integer(), nullable=True),
        sa.Column('numero_sceau', sa.String(length=100), nullable=False),
        sa.Column('type_sceau', sa.String(length=50), nullable=True),
        sa.Column('createur_id', sa.Integer(), nullable=True),
        sa.Column('date_creation', sa.DateTime(timezone=True), nullable=False),
        sa.Column('date_expiration', sa.Date(), nullable=True),
        sa.Column('contenu_sceau', sa.Text(), nullable=True),
        sa.Column('url_sceau', sa.String(length=500), nullable=True),
        sa.Column('statut', sa.String(length=20), nullable=True, server_default='actif'),
        sa.Column('public', sa.Boolean(), nullable=True, server_default='false'),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=True),
        sa.ForeignKeyConstraint(['createur_id'], ['users.id'], ),
        sa.ForeignKeyConstraint(['document_id'], ['documents.id'], ),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('numero_sceau')
    )
    op.create_index(op.f('ix_sceaux_numeriques_id'), 'sceaux_numeriques', ['id'], unique=False)
    op.create_index(op.f('ix_sceaux_numeriques_numero_sceau'), 'sceaux_numeriques', ['numero_sceau'], unique=True)
    
    # Templates Document
    op.create_table(
        'templates_document',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('nom', sa.String(length=200), nullable=False),
        sa.Column('type_document', sa.String(length=50), nullable=True),
        sa.Column('categorie', sa.String(length=50), nullable=True),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('contenu', sa.Text(), nullable=True),
        sa.Column('variables', sa.Text(), nullable=True),
        sa.Column('proprietaire_id', sa.Integer(), nullable=True),
        sa.Column('statut', sa.String(length=20), nullable=True, server_default='actif'),
        sa.Column('date_creation', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
        sa.Column('cree_par', sa.String(length=100), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=True),
        sa.ForeignKeyConstraint(['proprietaire_id'], ['users.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_templates_document_id'), 'templates_document', ['id'], unique=False)
    
    # ========== MAINTENANCE GMAO TABLES ==========
    
    # Equipements GMAO
    op.create_table(
        'equipements_gmao',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('numero_serie', sa.String(length=50), nullable=False),
        sa.Column('designation', sa.String(length=200), nullable=False),
        sa.Column('type_equipement', sa.String(length=50), nullable=True),
        sa.Column('marque', sa.String(length=100), nullable=True),
        sa.Column('modele', sa.String(length=100), nullable=True),
        sa.Column('annee_fabrication', sa.Integer(), nullable=True),
        sa.Column('date_mise_service', sa.Date(), nullable=True),
        sa.Column('localisation', sa.String(length=200), nullable=True),
        sa.Column('departement', sa.String(length=100), nullable=True),
        sa.Column('responsable', sa.String(length=100), nullable=True),
        sa.Column('statut', sa.String(length=20), nullable=True, server_default='operationnel'),
        sa.Column('date_achat', sa.Date(), nullable=True),
        sa.Column('fournisseur', sa.String(length=200), nullable=True),
        sa.Column('cout_achat', sa.Numeric(precision=15, scale=2), nullable=True),
        sa.Column('devise', sa.String(length=3), nullable=True, server_default='XAF'),
        sa.Column('valeur_residuelle', sa.Numeric(precision=15, scale=2), nullable=True),
        sa.Column('duree_vie_estimee', sa.Integer(), nullable=True),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('caracteristiques', sa.Text(), nullable=True),
        sa.Column('manuel_fabricant', sa.String(length=255), nullable=True),
        sa.Column('manuel_maintenance', sa.String(length=255), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=True),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('numero_serie')
    )
    op.create_index(op.f('ix_equipements_gmao_id'), 'equipements_gmao', ['id'], unique=False)
    op.create_index(op.f('ix_equipements_gmao_numero_serie'), 'equipements_gmao', ['numero_serie'], unique=True)
    
    # Ordres Maintenance
    op.create_table(
        'ordres_maintenance',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('numero_ordre', sa.String(length=50), nullable=False),
        sa.Column('equipement_id', sa.Integer(), nullable=True),
        sa.Column('type_maintenance', sa.String(length=50), nullable=True),
        sa.Column('priorite', sa.String(length=20), nullable=True),
        sa.Column('date_creation', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
        sa.Column('date_planifiee', sa.Date(), nullable=True),
        sa.Column('date_debut', sa.DateTime(timezone=True), nullable=True),
        sa.Column('date_fin', sa.DateTime(timezone=True), nullable=True),
        sa.Column('duree_estimee', sa.Integer(), nullable=True),
        sa.Column('duree_reelle', sa.Integer(), nullable=True),
        sa.Column('description', sa.Text(), nullable=False),
        sa.Column('travaux', sa.Text(), nullable=True),
        sa.Column('technicien_id', sa.Integer(), nullable=True),
        sa.Column('statut', sa.String(length=20), nullable=True, server_default='planifiee'),
        sa.Column('cout_pieces', sa.Numeric(precision=15, scale=2), nullable=True, server_default='0'),
        sa.Column('cout_main_oeuvre', sa.Numeric(precision=15, scale=2), nullable=True, server_default='0'),
        sa.Column('cout_total', sa.Numeric(precision=15, scale=2), nullable=True, server_default='0'),
        sa.Column('devise', sa.String(length=3), nullable=True, server_default='XAF'),
        sa.Column('observations', sa.Text(), nullable=True),
        sa.Column('validation_technicien', sa.Boolean(), nullable=True, server_default='false'),
        sa.Column('date_validation', sa.Date(), nullable=True),
        sa.Column('valide_par', sa.String(length=100), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=True),
        sa.ForeignKeyConstraint(['equipement_id'], ['equipements_gmao.id'], ),
        sa.ForeignKeyConstraint(['technicien_id'], ['users.id'], ),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('numero_ordre')
    )
    op.create_index(op.f('ix_ordres_maintenance_id'), 'ordres_maintenance', ['id'], unique=False)
    op.create_index(op.f('ix_ordres_maintenance_numero_ordre'), 'ordres_maintenance', ['numero_ordre'], unique=True)
    
    # Plans Maintenance
    op.create_table(
        'plans_maintenance',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('numero_plan', sa.String(length=50), nullable=False),
        sa.Column('equipement_id', sa.Integer(), nullable=True),
        sa.Column('type_maintenance', sa.String(length=50), nullable=True),
        sa.Column('frequence', sa.String(length=50), nullable=True),
        sa.Column('intervalle_jours', sa.Integer(), nullable=True),
        sa.Column('date_debut', sa.Date(), nullable=False),
        sa.Column('date_fin', sa.Date(), nullable=True),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('taches', sa.Text(), nullable=True),
        sa.Column('duree_estimee', sa.Integer(), nullable=True),
        sa.Column('technicien_assigne', sa.String(length=100), nullable=True),
        sa.Column('pieces_requises', sa.Text(), nullable=True),
        sa.Column('statut', sa.String(length=20), nullable=True, server_default='actif'),
        sa.Column('dernier_execution', sa.Date(), nullable=True),
        sa.Column('prochaine_execution', sa.Date(), nullable=True),
        sa.Column('nombre_executions', sa.Integer(), nullable=True, server_default='0'),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=True),
        sa.ForeignKeyConstraint(['equipement_id'], ['equipements_gmao.id'], ),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('numero_plan')
    )
    op.create_index(op.f('ix_plans_maintenance_id'), 'plans_maintenance', ['id'], unique=False)
    op.create_index(op.f('ix_plans_maintenance_numero_plan'), 'plans_maintenance', ['numero_plan'], unique=True)
    
    # Pieces Rechange GMAO
    op.create_table(
        'pieces_rechange_gmao',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('reference', sa.String(length=50), nullable=False),
        sa.Column('designation', sa.String(length=200), nullable=False),
        sa.Column('equipement_id', sa.Integer(), nullable=True),
        sa.Column('categorie', sa.String(length=100), nullable=True),
        sa.Column('marque', sa.String(length=100), nullable=True),
        sa.Column('modele', sa.String(length=100), nullable=True),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('stock_minimum', sa.Integer(), nullable=True, server_default='0'),
        sa.Column('stock_actuel', sa.Integer(), nullable=True, server_default='0'),
        sa.Column('stock_maximum', sa.Integer(), nullable=True),
        sa.Column('unite', sa.String(length=20), nullable=True),
        sa.Column('prix_unitaire', sa.Numeric(precision=15, scale=2), nullable=True),
        sa.Column('devise', sa.String(length=3), nullable=True, server_default='XAF'),
        sa.Column('fournisseur', sa.String(length=200), nullable=True),
        sa.Column('reference_fournisseur', sa.String(length=100), nullable=True),
        sa.Column('emplacement_stockage', sa.String(length=200), nullable=True),
        sa.Column('date_achat', sa.Date(), nullable=True),
        sa.Column('date_expiration', sa.Date(), nullable=True),
        sa.Column('perissable', sa.Boolean(), nullable=True, server_default='false'),
        sa.Column('statut', sa.String(length=20), nullable=True, server_default='disponible'),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=True),
        sa.ForeignKeyConstraint(['equipement_id'], ['equipements_gmao.id'], ),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('reference')
    )
    op.create_index(op.f('ix_pieces_rechange_gmao_id'), 'pieces_rechange_gmao', ['id'], unique=False)
    op.create_index(op.f('ix_pieces_rechange_gmao_reference'), 'pieces_rechange_gmao', ['reference'], unique=True)
    
    # Calibrations
    op.create_table(
        'calibrations',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('numero_calibration', sa.String(length=50), nullable=False),
        sa.Column('equipement_id', sa.Integer(), nullable=True),
        sa.Column('instrument', sa.String(length=200), nullable=False),
        sa.Column('date_calibration', sa.Date(), nullable=False),
        sa.Column('date_prochaine', sa.Date(), nullable=True),
        sa.Column('intervalle_mois', sa.Integer(), nullable=True),
        sa.Column('laboratoire', sa.String(length=200), nullable=True),
        sa.Column('technicien', sa.String(length=100), nullable=True),
        sa.Column('valeurs_avant', sa.Text(), nullable=True),
        sa.Column('valeurs_apres', sa.Text(), nullable=True),
        sa.Column('tolerance', sa.String(length=100), nullable=True),
        sa.Column('resultat', sa.String(length=20), nullable=True),
        sa.Column('actions', sa.Text(), nullable=True),
        sa.Column('certificat', sa.String(length=255), nullable=True),
        sa.Column('statut', sa.String(length=20), nullable=True, server_default='valide'),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=True),
        sa.ForeignKeyConstraint(['equipement_id'], ['equipements_gmao.id'], ),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('numero_calibration')
    )
    op.create_index(op.f('ix_calibrations_id'), 'calibrations', ['id'], unique=False)
    op.create_index(op.f('ix_calibrations_numero_calibration'), 'calibrations', ['numero_calibration'], unique=True)
    
    # ========== INTEGRATION TABLES ==========
    
    # Integrations
    op.create_table(
        'integrations',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('code_integration', sa.String(length=50), nullable=False),
        sa.Column('type_integration', sa.String(length=50), nullable=True),
        sa.Column('nom', sa.String(length=200), nullable=False),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('url_api', sa.String(length=500), nullable=True),
        sa.Column('api_key', sa.String(length=255), nullable=True),
        sa.Column('api_secret', sa.String(length=255), nullable=True),
        sa.Column('cert_path', sa.String(length=255), nullable=True),
        sa.Column('timeout', sa.Integer(), nullable=True, server_default='30'),
        sa.Column('retry_attempts', sa.Integer(), nullable=True, server_default='3'),
        sa.Column('statut', sa.String(length=20), nullable=True, server_default='actif'),
        sa.Column('date_activation', sa.Date(), nullable=True),
        sa.Column('date_desactivation', sa.Date(), nullable=True),
        sa.Column('derniere_synchronisation', sa.DateTime(timezone=True), nullable=True),
        sa.Column('frequence_synchronisation', sa.String(length=50), nullable=True),
        sa.Column('configuration', sa.Text(), nullable=True),
        sa.Column('parametres', sa.Text(), nullable=True),
        sa.Column('logs_retention_jours', sa.Integer(), nullable=True, server_default='30'),
        sa.Column('actif', sa.Boolean(), nullable=True, server_default='true'),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=True),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('code_integration')
    )
    op.create_index(op.f('ix_integrations_id'), 'integrations', ['id'], unique=False)
    op.create_index(op.f('ix_integrations_code_integration'), 'integrations', ['code_integration'], unique=True)
    
    # Requetes Integration
    op.create_table(
        'requetes_integration',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('integration_id', sa.Integer(), nullable=True),
        sa.Column('numero_requete', sa.String(length=50), nullable=False),
        sa.Column('type_requete', sa.String(length=50), nullable=True),
        sa.Column('direction', sa.String(length=20), nullable=True),
        sa.Column('donnees_envoyees', sa.Text(), nullable=True),
        sa.Column('donnees_recues', sa.Text(), nullable=True),
        sa.Column('headers', sa.Text(), nullable=True),
        sa.Column('statut', sa.String(length=20), nullable=True, server_default='en_attente'),
        sa.Column('date_creation', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
        sa.Column('date_envoi', sa.DateTime(timezone=True), nullable=True),
        sa.Column('date_reponse', sa.DateTime(timezone=True), nullable=True),
        sa.Column('duree_ms', sa.Integer(), nullable=True),
        sa.Column('code_reponse', sa.Integer(), nullable=True),
        sa.Column('message_erreur', sa.Text(), nullable=True),
        sa.Column('reference_externe', sa.String(length=100), nullable=True),
        sa.Column('correlation_id', sa.String(length=100), nullable=True),
        sa.ForeignKeyConstraint(['integration_id'], ['integrations.id'], ),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('numero_requete')
    )
    op.create_index(op.f('ix_requetes_integration_id'), 'requetes_integration', ['id'], unique=False)
    op.create_index(op.f('ix_requetes_integration_numero_requete'), 'requetes_integration', ['numero_requete'], unique=True)
    
    # SYDONIA Plus
    op.create_table(
        'sydonia_plus',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('numero_dossier', sa.String(length=50), nullable=False),
        sa.Column('bureau_douane', sa.String(length=100), nullable=False),
        sa.Column('type_operation', sa.String(length=50), nullable=True),
        sa.Column('regime', sa.String(length=50), nullable=True),
        sa.Column('numero_declaration', sa.String(length=50), nullable=True),
        sa.Column('date_declaration', sa.Date(), nullable=True),
        sa.Column('statut_douane', sa.String(length=50), nullable=True),
        sa.Column('date_statut', sa.Date(), nullable=True),
        sa.Column('valeur_douane', sa.Numeric(precision=15, scale=2), nullable=True),
        sa.Column('droits_taxes', sa.Numeric(precision=15, scale=2), nullable=True),
        sa.Column('numero_tva', sa.String(length=50), nullable=True),
        sa.Column('montant_tva', sa.Numeric(precision=15, scale=2), nullable=True),
        sa.Column('date_validation', sa.Date(), nullable=True),
        sa.Column('numero_bad', sa.String(length=50), nullable=True),
        sa.Column('date_bad', sa.Date(), nullable=True),
        sa.Column('observateur_douane', sa.String(length=100), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=True),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('numero_dossier')
    )
    op.create_index(op.f('ix_sydonia_plus_id'), 'sydonia_plus', ['id'], unique=False)
    op.create_index(op.f('ix_sydonia_plus_numero_dossier'), 'sydonia_plus', ['numero_dossier'], unique=True)
    
    # Guichet Unique
    op.create_table(
        'guichet_unique',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('numero_transaction', sa.String(length=50), nullable=False),
        sa.Column('service', sa.String(length=100), nullable=False),
        sa.Column('type_service', sa.String(length=50), nullable=True),
        sa.Column('date_transaction', sa.DateTime(timezone=True), nullable=False),
        sa.Column('utilisateur', sa.String(length=100), nullable=True),
        sa.Column('reference_externe', sa.String(length=100), nullable=True),
        sa.Column('statut', sa.String(length=20), nullable=True, server_default='en_cours'),
        sa.Column('resultat', sa.Text(), nullable=True),
        sa.Column('date_resultat', sa.DateTime(timezone=True), nullable=True),
        sa.Column('erreur', sa.Text(), nullable=True),
        sa.Column('ip_origine', sa.String(length=50), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=True),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('numero_transaction')
    )
    op.create_index(op.f('ix_guichet_unique_id'), 'guichet_unique', ['id'], unique=False)
    op.create_index(op.f('ix_guichet_unique_numero_transaction'), 'guichet_unique', ['numero_transaction'], unique=True)
    
    # PCS
    op.create_table(
        'pcs',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('reference_pcs', sa.String(length=50), nullable=False),
        sa.Column('type_operation', sa.String(length=50), nullable=True),
        sa.Column('navire', sa.String(length=200), nullable=True),
        sa.Column('voyage', sa.String(length=50), nullable=True),
        sa.Column('port', sa.String(length=100), nullable=True),
        sa.Column('date_operation', sa.Date(), nullable=True),
        sa.Column('numero_equipement', sa.String(length=50), nullable=True),
        sa.Column('type_equipement', sa.String(length=50), nullable=True),
        sa.Column('statut_pcs', sa.String(length=20), nullable=True),
        sa.Column('date_statut', sa.Date(), nullable=True),
        sa.Column('poids', sa.Float(), nullable=True),
        sa.Column('unite_poids', sa.String(length=20), nullable=True),
        sa.Column('nombre_conteneurs', sa.Integer(), nullable=True),
        sa.Column('observateur', sa.String(length=100), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=True),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('reference_pcs')
    )
    op.create_index(op.f('ix_pcs_id'), 'pcs', ['id'], unique=False)
    op.create_index(op.f('ix_pcs_reference_pcs'), 'pcs', ['reference_pcs'], unique=True)
    
    # ========== NOTIFICATIONS TABLES ==========
    
    # Notifications
    op.create_table(
        'notifications',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('numero_notification', sa.String(length=50), nullable=False),
        sa.Column('destinataire_id', sa.Integer(), nullable=True),
        sa.Column('type_canal', sa.String(length=50), nullable=True),
        sa.Column('categorie', sa.String(length=50), nullable=True),
        sa.Column('titre', sa.String(length=200), nullable=False),
        sa.Column('corps', sa.Text(), nullable=False),
        sa.Column('donnees', sa.JSON(), nullable=True),
        sa.Column('priorite', sa.String(length=20), nullable=True),
        sa.Column('statut', sa.String(length=20), nullable=True, server_default='en_attente'),
        sa.Column('date_creation', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
        sa.Column('date_envoi', sa.DateTime(timezone=True), nullable=True),
        sa.Column('date_livraison', sa.DateTime(timezone=True), nullable=True),
        sa.Column('date_lecture', sa.DateTime(timezone=True), nullable=True),
        sa.Column('nombre_tentatives', sa.Integer(), nullable=True, server_default='0'),
        sa.Column('derniere_tentative', sa.DateTime(timezone=True), nullable=True),
        sa.Column('expire_le', sa.DateTime(timezone=True), nullable=True),
        sa.Column('reference_externe', sa.String(length=100), nullable=True),
        sa.Column('correlation_id', sa.String(length=100), nullable=True),
        sa.Column('reponse_canal', sa.Text(), nullable=True),
        sa.Column('erreur', sa.Text(), nullable=True),
        sa.Column('template_id', sa.Integer(), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=True),
        sa.ForeignKeyConstraint(['destinataire_id'], ['users.id'], ),
        sa.ForeignKeyConstraint(['template_id'], ['templates_notification.id'], ),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('numero_notification')
    )
    op.create_index(op.f('ix_notifications_id'), 'notifications', ['id'], unique=False)
    op.create_index(op.f('ix_notifications_numero_notification'), 'notifications', ['numero_notification'], unique=True)
    
    # Templates Notification
    op.create_table(
        'templates_notification',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('code', sa.String(length=50), nullable=False),
        sa.Column('nom', sa.String(length=200), nullable=False),
        sa.Column('type_template', sa.String(length=50), nullable=True),
        sa.Column('type_canal', sa.String(length=50), nullable=True),
        sa.Column('sujet', sa.String(length=200), nullable=True),
        sa.Column('corps', sa.Text(), nullable=False),
        sa.Column('variables', sa.JSON(), nullable=True),
        sa.Column('langue', sa.String(length=10), nullable=True, server_default='fra'),
        sa.Column('actif', sa.Boolean(), nullable=True, server_default='true'),
        sa.Column('version', sa.Integer(), nullable=True, server_default='1'),
        sa.Column('cree_par', sa.String(length=100), nullable=True),
        sa.Column('date_creation', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=True),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('code')
    )
    op.create_index(op.f('ix_templates_notification_id'), 'templates_notification', ['id'], unique=False)
    op.create_index(op.f('ix_templates_notification_code'), 'templates_notification', ['code'], unique=True)
    
    # Preferences Notification
    op.create_table(
        'preferences_notification',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('utilisateur_id', sa.Integer(), nullable=True),
        sa.Column('type_canal', sa.String(length=50), nullable=True),
        sa.Column('categorie', sa.String(length=50), nullable=True),
        sa.Column('active', sa.Boolean(), nullable=True, server_default='true'),
        sa.Column('frequence', sa.String(length=50), nullable=True),
        sa.Column('heures_silence', sa.JSON(), nullable=True),
        sa.Column('jours_silence', sa.JSON(), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=True),
        sa.ForeignKeyConstraint(['utilisateur_id'], ['users.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_preferences_notification_id'), 'preferences_notification', ['id'], unique=False)
    
    # Campagnes Notification
    op.create_table(
        'campagnes_notification',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('numero_campagne', sa.String(length=50), nullable=False),
        sa.Column('nom', sa.String(length=200), nullable=False),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('type_canal', sa.String(length=50), nullable=True),
        sa.Column('template_id', sa.Integer(), nullable=True),
        sa.Column('segment', sa.JSON(), nullable=True),
        sa.Column('date_debut', sa.DateTime(timezone=True), nullable=False),
        sa.Column('date_fin', sa.DateTime(timezone=True), nullable=True),
        sa.Column('statut', sa.String(length=20), nullable=True, server_default='planifie'),
        sa.Column('nombre_destinataires', sa.Integer(), nullable=True, server_default='0'),
        sa.Column('nombre_envoyes', sa.Integer(), nullable=True, server_default='0'),
        sa.Column('nombre_livres', sa.Integer(), nullable=True, server_default='0'),
        sa.Column('nombre_echecs', sa.Integer(), nullable=True, server_default='0'),
        sa.Column('taux_ouverture', sa.Float(), nullable=True),
        sa.Column('taux_clic', sa.Float(), nullable=True),
        sa.Column('cree_par', sa.String(length=100), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=True),
        sa.ForeignKeyConstraint(['template_id'], ['templates_notification.id'], ),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('numero_campagne')
    )
    op.create_index(op.f('ix_campagnes_notification_id'), 'campagnes_notification', ['id'], unique=False)
    op.create_index(op.f('ix_campagnes_notification_numero_campagne'), 'campagnes_notification', ['numero_campagne'], unique=True)
    
    # ========== REPORTING TABLES ==========
    
    # Dashboards Executifs
    op.create_table(
        'dashboards_executifs',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('code', sa.String(length=50), nullable=False),
        sa.Column('nom', sa.String(length=200), nullable=False),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('layout', sa.JSON(), nullable=True),
        sa.Column('widgets', sa.JSON(), nullable=True),
        sa.Column('filtres', sa.JSON(), nullable=True),
        sa.Column('role_autorise', sa.JSON(), nullable=True),
        sa.Column('proprietaire_id', sa.Integer(), nullable=True),
        sa.Column('actif', sa.Boolean(), nullable=True, server_default='true'),
        sa.Column('date_creation', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
        sa.Column('modifie_par', sa.String(length=100), nullable=True),
        sa.Column('date_modification', sa.DateTime(timezone=True), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=True),
        sa.ForeignKeyConstraint(['proprietaire_id'], ['users.id'], ),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('code')
    )
    op.create_index(op.f('ix_dashboards_executifs_id'), 'dashboards_executifs', ['id'], unique=False)
    op.create_index(op.f('ix_dashboards_executifs_code'), 'dashboards_executifs', ['code'], unique=True)
    
    # KPIs
    op.create_table(
        'kpis',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('code', sa.String(length=50), nullable=False),
        sa.Column('nom', sa.String(length=200), nullable=False),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('type_rapport', sa.String(length=50), nullable=True),
        sa.Column('categorie', sa.String(length=50), nullable=True),
        sa.Column('formule', sa.Text(), nullable=True),
        sa.Column('unite', sa.String(length=20), nullable=True),
        sa.Column('objectif', sa.Float(), nullable=True),
        sa.Column('seuil_alerte', sa.Float(), nullable=True),
        sa.Column('couleur_alerte', sa.String(length=20), nullable=True),
        sa.Column('source_donnees', sa.String(length=100), nullable=True),
        sa.Column('frequence_calcul', sa.String(length=50), nullable=True),
        sa.Column('derniere_valeur', sa.Float(), nullable=True),
        sa.Column('date_derniere_valeur', sa.DateTime(timezone=True), nullable=True),
        sa.Column('tendance', sa.String(length=20), nullable=True),
        sa.Column('variation_pourcentage', sa.Float(), nullable=True),
        sa.Column('historique', sa.JSON(), nullable=True),
        sa.Column('actif', sa.Boolean(), nullable=True, server_default='true'),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=True),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('code')
    )
    op.create_index(op.f('ix_kpis_id'), 'kpis', ['id'], unique=False)
    op.create_index(op.f('ix_kpis_code'), 'kpis', ['code'], unique=True)
    
    # Rapports
    op.create_table(
        'rapports',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('numero_rapport', sa.String(length=50), nullable=False),
        sa.Column('titre', sa.String(length=200), nullable=False),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('type_rapport', sa.String(length=50), nullable=True),
        sa.Column('frequence', sa.String(length=50), nullable=True),
        sa.Column('requetes', sa.JSON(), nullable=True),
        sa.Column('colonnes', sa.JSON(), nullable=True),
        sa.Column('filtres', sa.JSON(), nullable=True),
        sa.Column('parametres', sa.JSON(), nullable=True),
        sa.Column('tri', sa.JSON(), nullable=True),
        sa.Column('graphiques', sa.JSON(), nullable=True),
        sa.Column('tables', sa.JSON(), nullable=True),
        sa.Column('statut', sa.String(length=20), nullable=True, server_default='en_preparation'),
        sa.Column('cree_par', sa.Integer(), nullable=True),
        sa.Column('date_creation', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
        sa.Column('date_generation', sa.DateTime(timezone=True), nullable=True),
        sa.Column('date_expiration', sa.DateTime(timezone=True), nullable=True),
        sa.Column('fichier', sa.String(length=255), nullable=True),
        sa.Column('taille_octets', sa.Integer(), nullable=True),
        sa.Column('nombre_lignes', sa.Integer(), nullable=True),
        sa.Column('duree_generation', sa.Integer(), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=True),
        sa.ForeignKeyConstraint(['cree_par'], ['users.id'], ),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('numero_rapport')
    )
    op.create_index(op.f('ix_rapports_id'), 'rapports', ['id'], unique=False)
    op.create_index(op.f('ix_rapports_numero_rapport'), 'rapports', ['numero_rapport'], unique=True)
    
    # Exports
    op.create_table(
        'exports',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('numero_export', sa.String(length=50), nullable=False),
        sa.Column('rapport_id', sa.Integer(), nullable=True),
        sa.Column('type_rapport', sa.String(length=50), nullable=True),
        sa.Column('format_export', sa.String(length=50), nullable=True),
        sa.Column('parametres', sa.JSON(), nullable=True),
        sa.Column('date_demande', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
        sa.Column('date_debut', sa.DateTime(timezone=True), nullable=True),
        sa.Column('date_fin', sa.DateTime(timezone=True), nullable=True),
        sa.Column('statut', sa.String(length=20), nullable=True, server_default='en_attente'),
        sa.Column('utilisateur_id', sa.Integer(), nullable=True),
        sa.Column('progression', sa.Integer(), nullable=True, server_default='0'),
        sa.Column('fichier', sa.String(length=255), nullable=True),
        sa.Column('taille_octets', sa.Integer(), nullable=True),
        sa.Column('nombre_enregistrements', sa.Integer(), nullable=True),
        sa.Column('erreur', sa.Text(), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=True),
        sa.ForeignKeyConstraint(['rapport_id'], ['rapports.id'], ),
        sa.ForeignKeyConstraint(['utilisateur_id'], ['users.id'], ),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('numero_export')
    )
    op.create_index(op.f('ix_exports_id'), 'exports', ['id'], unique=False)
    op.create_index(op.f('ix_exports_numero_export'), 'exports', ['numero_export'], unique=True)
    
    # Widgets
    op.create_table(
        'widgets',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('code', sa.String(length=50), nullable=False),
        sa.Column('nom', sa.String(length=200), nullable=False),
        sa.Column('type_widget', sa.String(length=50), nullable=True),
        sa.Column('type_rapport', sa.String(length=50), nullable=True),
        sa.Column('requete', sa.Text(), nullable=True),
        sa.Column('configuration', sa.JSON(), nullable=True),
        sa.Column('couleurs', sa.JSON(), nullable=True),
        sa.Column('filtres', sa.JSON(), nullable=True),
        sa.Column('refresh_secondes', sa.Integer(), nullable=True, server_default='300'),
        sa.Column('largeur', sa.Integer(), nullable=True),
        sa.Column('hauteur', sa.Integer(), nullable=True),
        sa.Column('position_x', sa.Integer(), nullable=True),
        sa.Column('position_y', sa.Integer(), nullable=True),
        sa.Column('actif', sa.Boolean(), nullable=True, server_default='true'),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=True),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('code')
    )
    op.create_index(op.f('ix_widgets_id'), 'widgets', ['id'], unique=False)
    op.create_index(op.f('ix_widgets_code'), 'widgets', ['code'], unique=True)
    
    # Tableaux Bords Operationnels
    op.create_table(
        'tableaux_bord_operationnels',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('code', sa.String(length=50), nullable=False),
        sa.Column('nom', sa.String(length=200), nullable=False),
        sa.Column('module', sa.String(length=50), nullable=True),
        sa.Column('metriques', sa.JSON(), nullable=True),
        sa.Column('graphiques', sa.JSON(), nullable=True),
        sa.Column('alertes', sa.JSON(), nullable=True),
        sa.Column('filtres', sa.JSON(), nullable=True),
        sa.Column('actualisation', sa.JSON(), nullable=True),
        sa.Column('derniere_actualisation', sa.DateTime(timezone=True), nullable=True),
        sa.Column('responsable', sa.String(length=100), nullable=True),
        sa.Column('actif', sa.Boolean(), nullable=True, server_default='true'),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=True),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('code')
    )
    op.create_index(op.f('ix_tableaux_bord_operationnels_id'), 'tableaux_bord_operationnels', ['id'], unique=False)
    op.create_index(op.f('ix_tableaux_bord_operationnels_code'), 'tableaux_bord_operationnels', ['code'], unique=True)
    
    # Indicateurs Financiers
    op.create_table(
        'indicateurs_financiers',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('code', sa.String(length=50), nullable=False),
        sa.Column('nom', sa.String(length=200), nullable=False),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('categorie', sa.String(length=50), nullable=True),
        sa.Column('periode', sa.String(length=50), nullable=True),
        sa.Column('valeur_actuelle', sa.Float(), nullable=True),
        sa.Column('valeur_precedente', sa.Float(), nullable=True),
        sa.Column('objectif', sa.Float(), nullable=True),
        sa.Column('variation', sa.Float(), nullable=True),
        sa.Column('tendance', sa.String(length=20), nullable=True),
        sa.Column('unite', sa.String(length=20), nullable=True),
        sa.Column('devise', sa.String(length=3), nullable=True, server_default='XAF'),
        sa.Column('date_mesure', sa.Date(), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=True),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('code')
    )
    op.create_index(op.f('ix_indicateurs_financiers_id'), 'indicateurs_financiers', ['id'], unique=False)
    op.create_index(op.f('ix_indicateurs_financiers_code'), 'indicateurs_financiers', ['code'], unique=True)
    
    # Indicateurs Douaniers
    op.create_table(
        'indicateurs_douaniers',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('code', sa.String(length=50), nullable=False),
        sa.Column('nom', sa.String(length=200), nullable=False),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('categorie', sa.String(length=50), nullable=True),
        sa.Column('periode', sa.String(length=50), nullable=True),
        sa.Column('valeur_actuelle', sa.Float(), nullable=True),
        sa.Column('valeur_precedente', sa.Float(), nullable=True),
        sa.Column('objectif', sa.Float(), nullable=True),
        sa.Column('variation', sa.Float(), nullable=True),
        sa.Column('tendance', sa.String(length=20), nullable=True),
        sa.Column('unite', sa.String(length=20), nullable=True),
        sa.Column('date_mesure', sa.Date(), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=True),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('code')
    )
    op.create_index(op.f('ix_indicateurs_douaniers_id'), 'indicateurs_douaniers', ['id'], unique=False)
    op.create_index(op.f('ix_indicateurs_douaniers_code'), 'indicateurs_douaniers', ['code'], unique=True)


def downgrade():
    # Drop tables in reverse order
    
    # Transport International
    op.drop_index(op.f('ix_cmrs_numero_cmr'), table_name='cmrs')
    op.drop_index(op.f('ix_cmrs_id'), table_name='cmrs')
    op.drop_table('cmrs')
    
    op.drop_index(op.f('ix_carnets_tir_numero_carnet'), table_name='carnets_tir')
    op.drop_index(op.f('ix_carnets_tir_id'), table_name='carnets_tir')
    op.drop_table('carnets_tir')
    
    op.drop_index(op.f('ix_ordres_transport_numero_ot'), table_name='ordres_transport')
    op.drop_index(op.f('ix_ordres_transport_id'), table_name='ordres_transport')
    op.drop_table('ordres_transport')
    
    # Magasin Douane
    op.drop_index(op.f('ix_entrepots_douane_id'), table_name='entrepots_douane')
    op.drop_table('entrepots_douane')
    
    # Transit Avance
    op.drop_index(op.f('ix_bureaux_douane_id'), table_name='bureaux_douane')
    op.drop_table('bureaux_douane')
    
    # Acconage
    op.drop_index(op.f('ix_connaissements_numero_bl'), table_name='connaissements')
    op.drop_index(op.f('ix_connaissements_id'), table_name='connaissements')
    op.drop_table('connaissements')
    
    op.drop_index(op.f('ix_conteneurs_numero'), table_name='conteneurs')
    op.drop_index(op.f('ix_conteneurs_id'), table_name='conteneurs')
    op.drop_table('conteneurs')
    
    op.drop_index(op.f('ix_amarages_id'), table_name='amarages')
    op.drop_table('amarages')
    
    op.drop_index(op.f('ix_remorqueurs_id'), table_name='remorqueurs')
    op.drop_table('remorqueurs')
    
    op.drop_index(op.f('ix_reservations_grue_id'), table_name='reservations_grue')
    op.drop_table('reservations_grue')
    
    op.drop_index(op.f('ix_grues_id'), table_name='grues')
    op.drop_table('grues')
    
    op.drop_index(op.f('ix_positions_conteneur_id'), table_name='positions_conteneur')
    op.drop_table('positions_conteneur')
    
    op.drop_index(op.f('ix_stowage_plans_id'), table_name='stowage_plans')
    op.drop_table('stowage_plans')
    
    # Acquisition
    op.drop_index(op.f('ix_contrats_cadre_numero_contrat'), table_name='contrats_cadre')
    op.drop_index(op.f('ix_contrats_cadre_id'), table_name='contrats_cadre')
    op.drop_table('contrats_cadre')
    
    op.drop_index(op.f('ix_bons_commande_numero_bc'), table_name='bons_commande')
    op.drop_index(op.f('ix_bons_commande_id'), table_name='bons_commande')
    op.drop_table('bons_commande')
    
    op.drop_index(op.f('ix_offres_numero_offre'), table_name='offres')
    op.drop_index(op.f('ix_offres_id'), table_name='offres')
    op.drop_table('offres')
    
    op.drop_index(op.f('ix_lignes_cdc_id'), table_name='lignes_cdc')
    op.drop_table('lignes_cdc')
    
    op.drop_index(op.f('ix_cahiers_charges_numero_cdc'), table_name='cahiers_charges')
    op.drop_index(op.f('ix_cahiers_charges_id'), table_name='cahiers_charges')
    op.drop_table('cahiers_charges')
    
    op.drop_index(op.f('ix_appels_offres_numero_appel'), table_name='appels_offres')
    op.drop_index(op.f('ix_appels_offres_id'), table_name='appels_offres')
    op.drop_table('appels_offres')
    
    # Finance
    op.drop_index(op.f('ix_comptes_resultat_id'), table_name='comptes_resultat')
    op.drop_table('comptes_resultat')
    
    op.drop_index(op.f('ix_bilans_id'), table_name='bilans')
    op.drop_table('bilans')
    
    op.drop_index(op.f('ix_is_declarables_numero_declaration'), table_name='is_declarables')
    op.drop_index(op.f('ix_is_declarables_id'), table_name='is_declarables')
    op.drop_table('is_declarables')
    
    op.drop_index(op.f('ix_tva_declarables_numero_declaration'), table_name='tva_declarables')
    op.drop_index(op.f('ix_tva_declarables_id'), table_name='tva_declarables')
    op.drop_table('tva_declarables')
    
    op.drop_index(op.f('ix_factures_numero_facture'), table_name='factures')
    op.drop_index(op.f('ix_factures_id'), table_name='factures')
    op.drop_table('factures')
    
    op.drop_index(op.f('ix_exercices_comptables_numero_exercice'), table_name='exercices_comptables')
    op.drop_index(op.f('ix_exercices_comptables_id'), table_name='exercices_comptables')
    op.drop_table('exercices_comptables')
    
    op.drop_index(op.f('ix_ecritures_comptables_numero_ecriture'), table_name='ecritures_comptables')
    op.drop_index(op.f('ix_ecritures_comptables_id'), table_name='ecritures_comptables')
    op.drop_table('ecritures_comptables')
    
    op.drop_index(op.f('ix_plan_comptable_ohada_numero_compte'), table_name='plan_comptable_ohada')
    op.drop_index(op.f('ix_plan_comptable_ohada_id'), table_name='plan_comptable_ohada')
    op.drop_table('plan_comptable_ohada')
    
    # QHSE
    op.drop_index(op.f('ix_normes_certifications_numero_certificat'), table_name='normes_certifications')
    op.drop_index(op.f('ix_normes_certifications_id'), table_name='normes_certifications')
    op.drop_table('normes_certifications')
    
    op.drop_index(op.f('ix_accidents_travail_numero_accident'), table_name='accidents_travail')
    op.drop_index(op.f('ix_accidents_travail_id'), table_name='accidents_travail')
    op.drop_table('accidents_travail')
    
    op.drop_index(op.f('ix_analyses_risques_numero_analyse'), table_name='analyses_risques')
    op.drop_index(op.f('ix_analyses_risques_id'), table_name='analyses_risques')
    op.drop_table('analyses_risques')
    
    # Documents
    op.drop_index(op.f('ix_documents_numero_document'), table_name='documents')
    op.drop_index(op.f('ix_documents_id'), table_name='documents')
    op.drop_table('documents')
    
    op.drop_index(op.f('ix_dossiers_id'), table_name='dossiers')
    op.drop_table('dossiers')
    
    op.drop_index(op.f('ix_templates_document_id'), table_name='templates_document')
    op.drop_table('templates_document')
    
    op.drop_index(op.f('ix_sceaux_numeriques_numero_sceau'), table_name='sceaux_numeriques')
    op.drop_index(op.f('ix_sceaux_numeriques_id'), table_name='sceaux_numeriques')
    op.drop_table('sceaux_numeriques')
    
    op.drop_index(op.f('ix_workflows_document_id'), table_name='workflows_document')
    op.drop_table('workflows_document')
    
    op.drop_index(op.f('ix_signatures_document_id'), table_name='signatures_document')
    op.drop_table('signatures_document')
    
    op.drop_index(op.f('ix_versions_document_id'), table_name='versions_document')
    op.drop_table('versions_document')
    
    # Maintenance GMAO
    op.drop_index(op.f('ix_calibrations_numero_calibration'), table_name='calibrations')
    op.drop_index(op.f('ix_calibrations_id'), table_name='calibrations')
    op.drop_table('calibrations')
    
    op.drop_index(op.f('ix_pieces_rechange_gmao_reference'), table_name='pieces_rechange_gmao')
    op.drop_index(op.f('ix_pieces_rechange_gmao_id'), table_name='pieces_rechange_gmao')
    op.drop_table('pieces_rechange_gmao')
    
    op.drop_index(op.f('ix_plans_maintenance_numero_plan'), table_name='plans_maintenance')
    op.drop_index(op.f('ix_plans_maintenance_id'), table_name='plans_maintenance')
    op.drop_table('plans_maintenance')
    
    op.drop_index(op.f('ix_ordres_maintenance_numero_ordre'), table_name='ordres_maintenance')
    op.drop_index(op.f('ix_ordres_maintenance_id'), table_name='ordres_maintenance')
    op.drop_table('ordres_maintenance')
    
    op.drop_index(op.f('ix_equipements_gmao_numero_serie'), table_name='equipements_gmao')
    op.drop_index(op.f('ix_equipements_gmao_id'), table_name='equipements_gmao')
    op.drop_table('equipements_gmao')
    
    # Integration
    op.drop_index(op.f('ix_pcs_reference_pcs'), table_name='pcs')
    op.drop_index(op.f('ix_pcs_id'), table_name='pcs')
    op.drop_table('pcs')
    
    op.drop_index(op.f('ix_guichet_unique_numero_transaction'), table_name='guichet_unique')
    op.drop_index(op.f('ix_guichet_unique_id'), table_name='guichet_unique')
    op.drop_table('guichet_unique')
    
    op.drop_index(op.f('ix_sydonia_plus_numero_dossier'), table_name='sydonia_plus')
    op.drop_index(op.f('ix_sydonia_plus_id'), table_name='sydonia_plus')
    op.drop_table('sydonia_plus')
    
    op.drop_index(op.f('ix_requetes_integration_numero_requete'), table_name='requetes_integration')
    op.drop_index(op.f('ix_requetes_integration_id'), table_name='requetes_integration')
    op.drop_table('requetes_integration')
    
    op.drop_index(op.f('ix_integrations_code_integration'), table_name='integrations')
    op.drop_index(op.f('ix_integrations_id'), table_name='integrations')
    op.drop_table('integrations')
    
    # Notifications
    op.drop_index(op.f('ix_campagnes_notification_numero_campagne'), table_name='campagnes_notification')
    op.drop_index(op.f('ix_campagnes_notification_id'), table_name='campagnes_notification')
    op.drop_table('campagnes_notification')
    
    op.drop_index(op.f('ix_preferences_notification_id'), table_name='preferences_notification')
    op.drop_table('preferences_notification')
    
    op.drop_index(op.f('ix_templates_notification_code'), table_name='templates_notification')
    op.drop_index(op.f('ix_templates_notification_id'), table_name='templates_notification')
    op.drop_table('templates_notification')
    
    op.drop_index(op.f('ix_notifications_numero_notification'), table_name='notifications')
    op.drop_index(op.f('ix_notifications_id'), table_name='notifications')
    op.drop_table('notifications')
    
    # Reporting
    op.drop_index(op.f('ix_indicateurs_douaniers_code'), table_name='indicateurs_douaniers')
    op.drop_index(op.f('ix_indicateurs_douaniers_id'), table_name='indicateurs_douaniers')
    op.drop_table('indicateurs_douaniers')
    
    op.drop_index(op.f('ix_indicateurs_financiers_code'), table_name='indicateurs_financiers')
    op.drop_index(op.f('ix_indicateurs_financiers_id'), table_name='indicateurs_financiers')
    op.drop_table('indicateurs_financiers')
    
    op.drop_index(op.f('ix_tableaux_bord_operationnels_code'), table_name='tableaux_bord_operationnels')
    op.drop_index(op.f('ix_tableaux_bord_operationnels_id'), table_name='tableaux_bord_operationnels')
    op.drop_table('tableaux_bord_operationnels')
    
    op.drop_index(op.f('ix_widgets_code'), table_name='widgets')
    op.drop_index(op.f('ix_widgets_id'), table_name='widgets')
    op.drop_table('widgets')
    
    op.drop_index(op.f('ix_exports_numero_export'), table_name='exports')
    op.drop_index(op.f('ix_exports_id'), table_name='exports')
    op.drop_table('exports')
    
    op.drop_index(op.f('ix_rapports_numero_rapport'), table_name='rapports')
    op.drop_index(op.f('ix_rapports_id'), table_name='rapports')
    op.drop_table('rapports')
    
    op.drop_index(op.f('ix_kpis_code'), table_name='kpis')
    op.drop_index(op.f('ix_kpis_id'), table_name='kpis')
    op.drop_table('kpis')
    
    op.drop_index(op.f('ix_dashboards_executifs_code'), table_name='dashboards_executifs')
    op.drop_index(op.f('ix_dashboards_executifs_id'), table_name='dashboards_executifs')
    op.drop_table('dashboards_executifs')
