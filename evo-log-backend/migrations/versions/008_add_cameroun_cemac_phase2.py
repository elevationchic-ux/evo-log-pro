"""Add Cameroon/CEMAC specific models - Ports, Customs, Transit, Containers, Fiscalite, Regulatory, Training

Revision ID: 008_add_cameroun_cemac_phase2
Revises: 007_add_cameroun_cemac
Create Date: 2026-01-18

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = '008_add_cameroun_cemac_phase2'
down_revision = '007_add_cameroun_cemac'
branch_labels = None
depends_on = None


def upgrade():
    # ========== FISCALITE CAMEROUN ==========
    
    # Impots Cameroun
    op.create_table(
        'impots_cameroun',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('code', sa.String(length=20), nullable=False),
        sa.Column('designation', sa.String(length=200), nullable=False),
        sa.Column('description', sa.Text()),
        sa.Column('type_impot', sa.String(length=50), nullable=False),
        sa.Column('taux', sa.Float()),
        sa.Column('base_calcul', sa.String(length=50), nullable=False),
        sa.Column('periodicite', sa.String(length=20), nullable=False),
        sa.Column('date_limite', sa.Integer()),
        sa.Column('reference_legale', sa.String(length=100)),
        sa.Column('taux_minimum', sa.Float()),
        sa.Column('est_actif', sa.Boolean(), default='true'),
        sa.Column('date_maj', sa.Date()),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=True),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('code')
    )
    op.create_index(op.f('ix_impots_cameroun_id'), 'impots_cameroun', ['id'], unique=False)
    op.create_index(op.f('ix_impots_cameroun_code'), 'impots_cameroun', ['code'], unique=True)
    
    # Declarations Fiscales
    op.create_table(
        'declarations_fiscales',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('company_id', sa.Integer(), nullable=False),
        sa.Column('type_impot', sa.String(length=20), nullable=False),
        sa.Column('periode_debut', sa.Date(), nullable=False),
        sa.Column('periode_fin', sa.Date(), nullable=False),
        sa.Column('chiffre_affaires', sa.Numeric(precision=15, scale=2)),
        sa.Column('benefice', sa.Numeric(precision=15, scale=2)),
        sa.Column('salaire_total', sa.Numeric(precision=15, scale=2)),
        sa.Column('tonnage', sa.Float()),
        sa.Column('montant_du', sa.Numeric(precision=15, scale=2), nullable=False),
        sa.Column('montant_paye', sa.Numeric(precision=15, scale=2), default=0),
        sa.Column('reste_a_payer', sa.Numeric(precision=15, scale=2)),
        sa.Column('statut', sa.String(length=20), default='en_attente'),
        sa.Column('date_soumission', sa.Date()),
        sa.Column('date_validation', sa.Date()),
        sa.Column('date_paiement', sa.Date()),
        sa.Column('reference_declaration', sa.String(length=50)),
        sa.Column('agent_fiscal', sa.String(length=100)),
        sa.Column('notes', sa.Text()),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=True),
        sa.ForeignKeyConstraint(['company_id'], ['companies.id'], ),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('reference_declaration')
    )
    op.create_index(op.f('ix_declarations_fiscales_id'), 'declarations_fiscales', ['id'], unique=False)
    
    # Paiements Locaux
    op.create_table(
        'paiements_locaux',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('type_paiement', sa.String(length=20), nullable=False),
        sa.Column('reference', sa.String(length=50), nullable=False),
        sa.Column('montant', sa.Numeric(precision=15, scale=2), nullable=False),
        sa.Column('devise', sa.String(length=3), default='XAF'),
        sa.Column('beneficiaire', sa.String(length=100), nullable=False),
        sa.Column('banque', sa.String(length=100)),
        sa.Column('compte', sa.String(length=30)),
        sa.Column('date_paiement', sa.Date(), nullable=False),
        sa.Column('preuve', sa.String(length=255)),
        sa.Column('declarant_id', sa.Integer()),
        sa.Column('description', sa.Text()),
        sa.Column('statut', sa.String(length=20), default='valide'),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=True),
        sa.ForeignKeyConstraint(['declarant_id'], ['users.id'], ),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('reference')
    )
    op.create_index(op.f('ix_paiements_locaux_id'), 'paiements_locaux', ['id'], unique=False)
    
    # Contrats Fiscaux
    op.create_table(
        'contrats_fiscaux',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('company_id', sa.Integer(), nullable=False),
        sa.Column('type_contrat', sa.String(length=50), nullable=False),
        sa.Column('date_debut', sa.Date(), nullable=False),
        sa.Column('date_fin', sa.Date(), nullable=False),
        sa.Column('montant_minimum', sa.Numeric(precision=15, scale=2)),
        sa.Column('devise', sa.String(length=3), default='XAF'),
        sa.Column('periodicite', sa.String(length=20), nullable=False),
        sa.Column('conditions', sa.Text()),
        sa.Column('reference_contrat', sa.String(length=50)),
        sa.Column('signataire', sa.String(length=100)),
        sa.Column('date_signature', sa.Date()),
        sa.Column('statut', sa.String(length=20), default='actif'),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=True),
        sa.ForeignKeyConstraint(['company_id'], ['companies.id'], ),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('reference_contrat')
    )
    op.create_index(op.f('ix_contrats_fiscaux_id'), 'contrats_fiscaux', ['id'], unique=False)
    
    # Retenues Source
    op.create_table(
        'retenues_source',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('company_id', sa.Integer(), nullable=False),
        sa.Column('type_retenue', sa.String(length=50), nullable=False),
        sa.Column('montant_brut', sa.Numeric(precision=15, scale=2), nullable=False),
        sa.Column('taux_retenue', sa.Float(), nullable=False),
        sa.Column('montant_retenue', sa.Numeric(precision=15, scale=2), nullable=False),
        sa.Column('montant_net', sa.Numeric(precision=15, scale=2), nullable=False),
        sa.Column('beneficiaire', sa.String(length=200), nullable=False),
        sa.Column('numero_contribuable', sa.String(length=50)),
        sa.Column('date_operation', sa.Date(), nullable=False),
        sa.Column('reference_paiement', sa.String(length=50)),
        sa.Column('statut', sa.String(length=20), default='declare'),
        sa.Column('date_declaration', sa.Date()),
        sa.Column('date_versement', sa.Date()),
        sa.Column('admin_fiscale', sa.String(length=100)),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=True),
        sa.ForeignKeyConstraint(['company_id'], ['companies.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_retenues_source_id'), 'retenues_source', ['id'], unique=False)
    
    # ========== REGLEMENTAIRE ==========
    
    # Reglementations
    op.create_table(
        'reglementations',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('code', sa.String(length=50), nullable=False),
        sa.Column('titre', sa.String(length=200), nullable=False),
        sa.Column('type_reglement', sa.String(length=50), nullable=False),
        sa.Column('numero', sa.String(length=50)),
        sa.Column('date_promulgation', sa.Date(), nullable=False),
        sa.Column('date_application', sa.Date(), nullable=False),
        sa.Column('ministere', sa.String(length=100)),
        sa.Column('description', sa.Text(), nullable=False),
        sa.Column('resume', sa.Text()),
        sa.Column('url_officielle', sa.String(length=255)),
        sa.Column('fichier_pdf', sa.String(length=255)),
        sa.Column('est_actif', sa.Boolean(), default='true'),
        sa.Column('version', sa.String(length=20)),
        sa.Column('date_maj', sa.Date()),
        sa.Column('categorie', sa.String(length=50)),
        sa.Column('mots_cles', sa.Text()),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=True),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('code')
    )
    op.create_index(op.f('ix_reglementations_id'), 'reglementations', ['id'], unique=False)
    op.create_index(op.f('ix_reglementations_code'), 'reglementations', ['code'], unique=True)
    
    # Alertes Reglementaires
    op.create_table(
        'alertes_reglementaires',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('reglementation_id', sa.Integer()),
        sa.Column('type_alerte', sa.String(length=20), nullable=False),
        sa.Column('titre', sa.String(length=200), nullable=False),
        sa.Column('description', sa.Text(), nullable=False),
        sa.Column('date_publication', sa.Date(), nullable=False),
        sa.Column('date_application', sa.Date()),
        sa.Column('severite', sa.String(length=20), default='moyenne'),
        sa.Column('impact_operationnel', sa.Text()),
        sa.Column('actions_requises', sa.Text()),
        sa.Column('est_resolue', sa.Boolean(), default='false'),
        sa.Column('date_resolution', sa.Date()),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=True),
        sa.ForeignKeyConstraint(['reglementation_id'], ['reglementations.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_alertes_reglementaires_id'), 'alertes_reglementaires', ['id'], unique=False)
    
    # Documents Utilisateur
    op.create_table(
        'documents_utilisateur',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('titre', sa.String(length=200), nullable=False),
        sa.Column('type_document', sa.String(length=20), nullable=False),
        sa.Column('categorie', sa.String(length=50), nullable=False),
        sa.Column('sous_categorie', sa.String(length=50)),
        sa.Column('contenu', sa.Text(), nullable=False),
        sa.Column('contenu_html', sa.Text()),
        sa.Column('video_url', sa.String(length=255)),
        sa.Column('duree_minutes', sa.Integer()),
        sa.Column('langue', sa.String(length=10), default='fr'),
        sa.Column('niveau', sa.String(length=20), default='debutant'),
        sa.Column('date_publication', sa.Date(), nullable=False),
        sa.Column('auteur', sa.String(length=100)),
        sa.Column('version', sa.String(length=20)),
        sa.Column('fichier_pdf', sa.String(length=255)),
        sa.Column('est_publie', sa.Boolean(), default='true'),
        sa.Column('nombre_vues', sa.Integer(), default=0),
        sa.Column('nombre_telechargements', sa.Integer(), default=0),
        sa.Column('note', sa.Float()),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=True),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_documents_utilisateur_id'), 'documents_utilisateur', ['id'], unique=False)
    
    # Procedures Operationnelles
    op.create_table(
        'procedures_operationnelles',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('code', sa.String(length=50), nullable=False),
        sa.Column('titre', sa.String(length=200), nullable=False),
        sa.Column('description', sa.Text(), nullable=False),
        sa.Column('categorie', sa.String(length=50), nullable=False),
        sa.Column('duree_estimee_minutes', sa.Integer()),
        sa.Column('difficulte', sa.String(length=20), default='moyenne'),
        sa.Column('documents_requis', sa.Text()),
        sa.Column('preconditions', sa.Text()),
        sa.Column('etapes', sa.Text(), nullable=False),
        sa.Column('risques', sa.Text()),
        sa.Column('alternatives', sa.Text()),
        sa.Column('est_actif', sa.Boolean(), default='true'),
        sa.Column('date_creation', sa.Date(), nullable=False),
        sa.Column('date_maj', sa.Date()),
        sa.Column('created_by', sa.Integer()),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=True),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('code')
    )
    op.create_index(op.f('ix_procedures_operationnelles_id'), 'procedures_operationnelles', ['id'], unique=False)
    
    # FAQ
    op.create_table(
        'faqs',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('question', sa.String(length=500), nullable=False),
        sa.Column('reponse', sa.Text(), nullable=False),
        sa.Column('categorie', sa.String(length=50), nullable=False),
        sa.Column('sous_categorie', sa.String(length=50)),
        sa.Column('mots_cles', sa.Text()),
        sa.Column('ordre', sa.Integer(), default=0),
        sa.Column('langue', sa.String(length=10), default='fr'),
        sa.Column('nombre_vues', sa.Integer(), default=0),
        sa.Column('est_utile', sa.Integer(), default=0),
        sa.Column('est_publie', sa.Boolean(), default='true'),
        sa.Column('date_creation', sa.Date(), nullable=False),
        sa.Column('date_maj', sa.Date()),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=True),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_faqs_id'), 'faqs', ['id'], unique=False)
    
    # ========== FORMATION ==========
    
    # Modules Formation
    op.create_table(
        'modules_formation',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('titre', sa.String(length=200), nullable=False),
        sa.Column('description', sa.Text(), nullable=False),
        sa.Column('contenu', sa.Text(), nullable=False),
        sa.Column('contenu_html', sa.Text()),
        sa.Column('video_url', sa.String(length=255)),
        sa.Column('duree_minutes', sa.Integer(), nullable=False),
        sa.Column('categorie', sa.String(length=50), nullable=False),
        sa.Column('sous_categorie', sa.String(length=50)),
        sa.Column('niveau', sa.String(length=20), default='debutant'),
        sa.Column('prerequis', sa.Text()),
        sa.Column('objectifs', sa.Text()),
        sa.Column('langue', sa.String(length=10), default='fr'),
        sa.Column('ordre', sa.Integer(), default=0),
        sa.Column('est_publie', sa.Boolean(), default='true'),
        sa.Column('date_publication', sa.Date(), nullable=False),
        sa.Column('auteur', sa.String(length=100)),
        sa.Column('version', sa.String(length=20)),
        sa.Column('nombre_vues', sa.Integer(), default=0),
        sa.Column('note_moyenne', sa.Float()),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=True),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_modules_formation_id'), 'modules_formation', ['id'], unique=False)
    
    # Quizzes Formation
    op.create_table(
        'quizzes_formation',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('module_id', sa.Integer(), nullable=False),
        sa.Column('titre', sa.String(length=200), nullable=False),
        sa.Column('description', sa.Text()),
        sa.Column('nombre_questions', sa.Integer(), nullable=False),
        sa.Column('score_reussite', sa.Integer(), nullable=False),
        sa.Column('duree_minutes', sa.Integer(), default=30),
        sa.Column('melange_questions', sa.Boolean(), default='true'),
        sa.Column('est_actif', sa.Boolean(), default='true'),
        sa.Column('date_creation', sa.Date(), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=True),
        sa.ForeignKeyConstraint(['module_id'], ['modules_formation.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_quizzes_formation_id'), 'quizzes_formation', ['id'], unique=False)
    
    # Questions Quiz
    op.create_table(
        'questions_quiz',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('quiz_id', sa.Integer(), nullable=False),
        sa.Column('question', sa.Text(), nullable=False),
        sa.Column('type_question', sa.String(length=20), nullable=False),
        sa.Column('options', sa.Text(), nullable=False),
        sa.Column('reponse_correcte', sa.Text(), nullable=False),
        sa.Column('explication', sa.Text()),
        sa.Column('points', sa.Integer(), default=1),
        sa.Column('ordre', sa.Integer(), default=0),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
        sa.ForeignKeyConstraint(['quiz_id'], ['quizzes_formation.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_questions_quiz_id'), 'questions_quiz', ['id'], unique=False)
    
    # Tentatives Quiz
    op.create_table(
        'tentatives_quiz',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('quiz_id', sa.Integer(), nullable=False),
        sa.Column('utilisateur_id', sa.Integer(), nullable=False),
        sa.Column('date_debut', sa.DateTime(timezone=True), nullable=False),
        sa.Column('date_fin', sa.DateTime(timezone=True)),
        sa.Column('score', sa.Integer()),
        sa.Column('score_maximum', sa.Integer()),
        sa.Column('pourcentage', sa.Float()),
        sa.Column('statut', sa.String(length=20), default='en_cours'),
        sa.Column('reponses', sa.Text()),
        sa.Column('duree_minutes', sa.Integer()),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=True),
        sa.ForeignKeyConstraint(['quiz_id'], ['quizzes_formation.id'], ),
        sa.ForeignKeyConstraint(['utilisateur_id'], ['users.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_tentatives_quiz_id'), 'tentatives_quiz', ['id'], unique=False)
    
    # Certifications Utilisateur
    op.create_table(
        'certifications_utilisateurs',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('utilisateur_id', sa.Integer(), nullable=False),
        sa.Column('module_id', sa.Integer(), nullable=False),
        sa.Column('date_passage', sa.DateTime(timezone=True), nullable=False),
        sa.Column('score', sa.Integer(), nullable=False),
        sa.Column('score_maximum', sa.Integer(), nullable=False),
        sa.Column('pourcentage', sa.Float(), nullable=False),
        sa.Column('statut', sa.String(length=20), default='en_cours'),
        sa.Column('date_expiration', sa.Date()),
        sa.Column('numero_certificat', sa.String(length=50), unique=True),
        sa.Column('certificat_url', sa.String(length=255)),
        sa.Column('valide_par', sa.String(length=100)),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=True),
        sa.ForeignKeyConstraint(['utilisateur_id'], ['users.id'], ),
        sa.ForeignKeyConstraint(['module_id'], ['modules_formation.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_certifications_utilisateurs_id'), 'certifications_utilisateurs', ['id'], unique=False)
    
    # Support Utilisateur
    op.create_table(
        'support_utilisateurs',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('utilisateur_id', sa.Integer(), nullable=False),
        sa.Column('type_support', sa.String(length=20), nullable=False),
        sa.Column('titre', sa.String(length=200), nullable=False),
        sa.Column('description', sa.Text(), nullable=False),
        sa.Column('categorie', sa.String(length=50)),
        sa.Column('priorite', sa.String(length=20), default='normale'),
        sa.Column('statut', sa.String(length=20), default='ouvert'),
        sa.Column('date_creation', sa.DateTime(timezone=True), nullable=False),
        sa.Column('date_resolution', sa.DateTime(timezone=True)),
        sa.Column('duree_resolution_heures', sa.Float()),
        sa.Column('assigne_a', sa.Integer()),
        sa.Column('solution', sa.Text()),
        sa.Column('satisfaction', sa.Integer()),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=True),
        sa.ForeignKeyConstraint(['utilisateur_id'], ['users.id'], ),
        sa.ForeignKeyConstraint(['assigne_a'], ['users.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_support_utilisateurs_id'), 'support_utilisateurs', ['id'], unique=False)


def downgrade():
    # Drop tables in reverse order
    op.drop_index(op.f('ix_support_utilisateurs_id'), table_name='support_utilisateurs')
    op.drop_table('support_utilisateurs')
    
    op.drop_index(op.f('ix_certifications_utilisateurs_id'), table_name='certifications_utilisateurs')
    op.drop_table('certifications_utilisateurs')
    
    op.drop_index(op.f('ix_tentatives_quiz_id'), table_name='tentatives_quiz')
    op.drop_table('tentatives_quiz')
    
    op.drop_index(op.f('ix_questions_quiz_id'), table_name='questions_quiz')
    op.drop_table('questions_quiz')
    
    op.drop_index(op.f('ix_quizzes_formation_id'), table_name='quizzes_formation')
    op.drop_table('quizzes_formation')
    
    op.drop_index(op.f('ix_modules_formation_id'), table_name='modules_formation')
    op.drop_table('modules_formation')
    
    op.drop_index(op.f('ix_faqs_id'), table_name='faqs')
    op.drop_table('faqs')
    
    op.drop_index(op.f('ix_procedures_operationnelles_id'), table_name='procedures_operationnelles')
    op.drop_table('procedures_operationnelles')
    
    op.drop_index(op.f('ix_documents_utilisateur_id'), table_name='documents_utilisateur')
    op.drop_table('documents_utilisateur')
    
    op.drop_index(op.f('ix_alertes_reglementaires_id'), table_name='alertes_reglementaires')
    op.drop_table('alertes_reglementaires')
    
    op.drop_index(op.f('ix_reglementations_code'), table_name='reglementations')
    op.drop_index(op.f('ix_reglementations_id'), table_name='reglementations')
    op.drop_table('reglementations')
    
    op.drop_index(op.f('ix_retenues_source_id'), table_name='retenues_source')
    op.drop_table('retenues_source')
    
    op.drop_index(op.f('ix_contrats_fiscaux_id'), table_name='contrats_fiscaux')
    op.drop_table('contrats_fiscaux')
    
    op.drop_index(op.f('ix_paiements_locaux_id'), table_name='paiements_locaux')
    op.drop_table('paiements_locaux')
    
    op.drop_index(op.f('ix_declarations_fiscales_id'), table_name='declarations_fiscales')
    op.drop_table('declarations_fiscales')
    
    op.drop_index(op.f('ix_impots_cameroun_code'), table_name='impots_cameroun')
    op.drop_index(op.f('ix_impots_cameroun_id'), table_name='impots_cameroun')
    op.drop_table('impots_cameroun')
