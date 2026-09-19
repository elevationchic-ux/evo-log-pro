"""add_transport_avance_complete

Revision ID: 009_add_transport_avance_complete
Revises: 008_add_comptabilite_avance_complete
Create Date: 2026-01-18

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy import Integer, String, Text, DateTime, Boolean, Float, ForeignKey, Enum, Date, Numeric
from sqlalchemy.sql import func


# revision identifiers, used by Alembic.
revision = '009_add_transport_avance_complete'
down_revision = '008_add_comptabilite_avance_complete'
branch_labels = None
depends_on = None


def upgrade():
    # ============ DISPATCH INTELLIGENT ============
    op.create_table(
        'dispatches',
        sa.Column('id', Integer, primary_key=True, index=True),
        sa.Column('numero_dispatch', String(50), unique=True, nullable=False, index=True),
        sa.Column('mission_id', Integer, ForeignKey('missions.id'), nullable=False),
        sa.Column('conducteur_id', Integer, ForeignKey('conducteurs.id'), nullable=False),
        sa.Column('camion_id', Integer, ForeignKey('camions.id'), nullable=False),
        sa.Column('type_optimisation', String(50)),
        sa.Column('statut', String(50)),
        sa.Column('date_planification', DateTime(timezone=True), server_default=func.now()),
        sa.Column('date_debut_prevue', DateTime(timezone=True)),
        sa.Column('date_fin_prevue', DateTime(timezone=True)),
        sa.Column('date_debut_reelle', DateTime(timezone=True)),
        sa.Column('date_fin_reelle', DateTime(timezone=True)),
        sa.Column('distance_estimee', Numeric),
        sa.Column('distance_reelle', Numeric),
        sa.Column('duree_estimee', Integer),
        sa.Column('duree_reelle', Integer),
        sa.Column('cout_estime', Numeric(15, 2)),
        sa.Column('cout_reel', Numeric(15, 2)),
        sa.Column('priorite', Integer, default=5),
        sa.Column('score_confiance', Numeric),
        sa.Column('facteurs_consideres', Text),
        sa.Column('notes', Text),
        sa.Column('planificateur', Integer, ForeignKey('users.id')),
        sa.Column('created_at', DateTime(timezone=True), server_default=func.now()),
        sa.Column('updated_at', DateTime(timezone=True), onupdate=func.now())
    )
    
    op.create_table(
        'arrets',
        sa.Column('id', Integer, primary_key=True, index=True),
        sa.Column('dispatch_id', Integer, ForeignKey('dispatches.id'), nullable=False),
        sa.Column('type_arret', String(20)),
        sa.Column('ordre_sequence', Integer, nullable=False),
        sa.Column('client_id', Integer, ForeignKey('clients.id')),
        sa.Column('adresse', String(200), nullable=False),
        sa.Column('latitude', Numeric),
        sa.Column('longitude', Numeric),
        sa.Column('duree_estimee', Integer),
        sa.Column('duree_reelle', Integer),
        sa.Column('heure_arrivee_prevue', DateTime(timezone=True)),
        sa.Column('heure_arrivee_reelle', DateTime(timezone=True)),
        sa.Column('heure_depart_prevue', DateTime(timezone=True)),
        sa.Column('heure_depart_reelle', DateTime(timezone=True)),
        sa.Column('statut', String(20), default='en_attente'),
        sa.Column('notes', Text),
        sa.Column('created_at', DateTime(timezone=True), server_default=func.now()),
        sa.Column('updated_at', DateTime(timezone=True), onupdate=func.now())
    )
    
    op.create_table(
        'contraintes_dispatch',
        sa.Column('id', Integer, primary_key=True, index=True),
        sa.Column('dispatch_id', Integer, ForeignKey('dispatches.id'), nullable=False),
        sa.Column('type_contrainte', String(50)),
        sa.Column('description', Text),
        sa.Column('valeur', String(100)),
        sa.Column('unite', String(20)),
        sa.Column('respectee', Boolean, default=False),
        sa.Column('penalite', Numeric(15, 2)),
        sa.Column('created_at', DateTime(timezone=True), server_default=func.now())
    )
    
    # ============ E-POD ============
    op.create_table(
        'pods',
        sa.Column('id', Integer, primary_key=True, index=True),
        sa.Column('numero_pod', String(50), unique=True, nullable=False, index=True),
        sa.Column('livraison_id', Integer, ForeignKey('livraisons.id'), nullable=False),
        sa.Column('date_pod', DateTime(timezone=True), server_default=func.now()),
        sa.Column('statut', String(20), default='en_attente'),
        sa.Column('signature_client', Text),
        sa.Column('photo_marchandise', Text),
        sa.Column('photo_signature', Text),
        sa.Column('coordonnes_livraison', String(200)),
        sa.Column('horodatage', DateTime(timezone=True)),
        sa.Column('nom_receveur', String(100)),
        sa.Column('fonction_receveur', String(100)),
        sa.Column('commentaire_client', Text),
        sa.Column('commentaire_chauffeur', Text),
        sa.Column('conditions_livraison', Text),
        sa.Column('documents_attaches', Text),
        sa.Column('valide_par', Integer, ForeignKey('users.id')),
        sa.Column('date_validation', DateTime(timezone=True)),
        sa.Column('hash_preuve', String(255)),
        sa.Column('created_at', DateTime(timezone=True), server_default=func.now()),
        sa.Column('updated_at', DateTime(timezone=True), onupdate=func.now())
    )
    
    op.create_table(
        'documents_pod',
        sa.Column('id', Integer, primary_key=True, index=True),
        sa.Column('pod_id', Integer, ForeignKey('pods.id'), nullable=False),
        sa.Column('type_document', String(50)),
        sa.Column('type_preuve', String(50)),
        sa.Column('nom_fichier', String(200)),
        sa.Column('url_fichier', String(500)),
        sa.Column('taille_fichier', Integer),
        sa.Column('type_mime', String(100)),
        sa.Column('hash_fichier', String(255)),
        sa.Column('upload_par', Integer, ForeignKey('users.id')),
        sa.Column('created_at', DateTime(timezone=True), server_default=func.now())
    )
    
    # ============ ANALYTICS TRANSPORT ============
    op.create_table(
        'kpi_performance',
        sa.Column('id', Integer, primary_key=True, index=True),
        sa.Column('periode', String(50), nullable=False),
        sa.Column('type_periode', String(20)),
        sa.Column('conducteur_id', Integer, ForeignKey('conducteurs.id')),
        sa.Column('camion_id', Integer, ForeignKey('camions.id')),
        sa.Column('nombre_missions', Integer, default=0),
        sa.Column('nombre_missions_reussies', Integer, default=0),
        sa.Column('taux_reussite', Numeric, default=0),
        sa.Column('nombre_km_parcourus', Numeric, default=0),
        sa.Column('nombre_heures_conduite', Numeric, default=0),
        sa.Column('consommation_moyenne', Numeric),
        sa.Column('nombre_incidents', Integer, default=0),
        sa.Column('nombre_retards', Integer, default=0),
        sa.Column('satisfaction_client', Numeric),
        sa.Column('cout_par_km', Numeric(15, 2)),
        sa.Column('revenu_total', Numeric(15, 2)),
        sa.Column('benefice', Numeric(15, 2)),
        sa.Column('note_performance', Numeric),
        sa.Column('created_at', DateTime(timezone=True), server_default=func.now()),
        sa.Column('updated_at', DateTime(timezone=True), onupdate=func.now())
    )
    
    op.create_table(
        'tableaux_bord_transport',
        sa.Column('id', Integer, primary_key=True, index=True),
        sa.Column('date_dashboard', Date, nullable=False),
        sa.Column('nombre_missions_actives', Integer, default=0),
        sa.Column('nombre_missions_terminees', Integer, default=0),
        sa.Column('nombre_missions_en_retard', Integer, default=0),
        sa.Column('nombre_vehicules_disponibles', Integer, default=0),
        sa.Column('nombre_vehicules_en_mission', Integer, default=0),
        sa.Column('nombre_vehicules_hors_service', Integer, default=0),
        sa.Column('nombre_conducteurs_disponibles', Integer, default=0),
        sa.Column('nombre_conducteurs_en_mission', Integer, default=0),
        sa.Column('taux_occupation', Numeric),
        sa.Column('taux_reussite', Numeric),
        sa.Column('cout_total_jour', Numeric(15, 2)),
        sa.Column('revenu_total_jour', Numeric(15, 2)),
        sa.Column('alertes_actives', Integer, default=0),
        sa.Column('created_at', DateTime(timezone=True), server_default=func.now())
    )
    
    op.create_table(
        'alertes_performance',
        sa.Column('id', Integer, primary_key=True, index=True),
        sa.Column('type_alerte', String(50)),
        sa.Column('gravite', String(20)),
        sa.Column('description', Text),
        sa.Column('concerne_type', String(20)),
        sa.Column('concerne_id', Integer),
        sa.Column('valeur_actuelle', Numeric),
        sa.Column('valeur_seuil', Numeric),
        sa.Column('date_alerte', DateTime(timezone=True), server_default=func.now()),
        sa.Column('statut', String(20), default='active'),
        sa.Column('resolue_par', Integer, ForeignKey('users.id')),
        sa.Column('date_resolution', DateTime(timezone=True)),
        sa.Column('resolution', Text),
        sa.Column('created_at', DateTime(timezone=True), server_default=func.now())
    )


def downgrade():
    # Drop tables in reverse order
    op.drop_table('alertes_performance')
    op.drop_table('tableaux_bord_transport')
    op.drop_table('kpi_performance')
    op.drop_table('documents_pod')
    op.drop_table('pods')
    op.drop_table('contraintes_dispatch')
    op.drop_table('arrets')
    op.drop_table('dispatches')