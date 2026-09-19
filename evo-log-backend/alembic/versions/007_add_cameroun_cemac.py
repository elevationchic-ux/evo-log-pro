"""Add Cameroon/CEMAC specific models - Ports, Customs, Transit, Containers

Revision ID: 007_add_cameroun_cemac
Revises: 006_add_multi_tenant_saas
Create Date: 2026-01-18

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = '007_add_cameroun_cemac'
down_revision = '006_add_multi_tenant_saas'
branch_labels = None
depends_on = None


def upgrade():
    # ========== CAMEROON PORTS ==========
    
    # Ports Cameroun
    op.create_table(
        'ports_cameroun',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('code', sa.String(length=10), nullable=False),
        sa.Column('nom', sa.String(length=100), nullable=False),
        sa.Column('type_port', sa.String(length=50), nullable=False),
        sa.Column('localisation', sa.String(length=100)),
        sa.Column('capacite_annuelle_tonnes', sa.Float()),
        sa.Column('profondeur_m', sa.Float()),
        sa.Column('nombre_postes_quai', sa.Integer()),
        sa.Column('operateur', sa.String(length=100)),
        sa.Column('zone_franche', sa.Boolean(), default='false'),
        sa.Column('adresse', sa.String(length=200)),
        sa.Column('ville', sa.String(length=50)),
        sa.Column('region', sa.String(length=50)),
        sa.Column('telephone', sa.String(length=20)),
        sa.Column('email', sa.String(length=100)),
        sa.Column('website', sa.String(length=255)),
        sa.Column('est_actif', sa.Boolean(), default='true'),
        sa.Column('date_ouverture', sa.Date()),
        sa.Column('description', sa.Text()),
        sa.Column('caracteristiques', sa.Text()),
        sa.Column('services_disponibles', sa.Text()),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=True),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('code')
    )
    op.create_index(op.f('ix_ports_cameroun_id'), 'ports_cameroun', ['id'], unique=False)
    op.create_index(op.f('ix_ports_cameroun_code'), 'ports_cameroun', ['code'], unique=True)
    
    # Terminaux Portuaires
    op.create_table(
        'terminaux_portuaires',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('port_id', sa.Integer(), nullable=False),
        sa.Column('code', sa.String(length=20), nullable=False),
        sa.Column('nom', sa.String(length=100), nullable=False),
        sa.Column('type_terminal', sa.String(length=50), nullable=False),
        sa.Column('operateur', sa.String(length=100)),
        sa.Column('capacite_teus', sa.Integer()),
        sa.Column('superficie_ha', sa.Float()),
        sa.Column('longueur_quai_m', sa.Float()),
        sa.Column('profondeur_m', sa.Float()),
        sa.Column('nombre_grues', sa.Integer()),
        sa.Column('nombre_chariots', sa.Integer()),
        sa.Column('capacite_stockage', sa.Integer()),
        sa.Column('services', sa.Text()),
        sa.Column('est_actif', sa.Boolean(), default='true'),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=True),
        sa.ForeignKeyConstraint(['port_id'], ['ports_cameroun.id'], ),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('code')
    )
    op.create_index(op.f('ix_terminaux_portuaires_id'), 'terminaux_portuaires', ['id'], unique=False)
    
    # Tarifs Portuaires
    op.create_table(
        'tarifs_portuaires',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('code_tarif', sa.String(length=20), nullable=False),
        sa.Column('designation', sa.String(length=200), nullable=False),
        sa.Column('categorie', sa.String(length=50), nullable=False),
        sa.Column('sous_categorie', sa.String(length=50)),
        sa.Column('unite', sa.String(length=20), nullable=False),
        sa.Column('prix_unitaire', sa.Float(), nullable=False),
        sa.Column('devise', sa.String(length=3), default='XAF'),
        sa.Column('date_application', sa.Date(), nullable=False),
        sa.Column('date_expiration', sa.Date()),
        sa.Column('taux_tva', sa.Float(), default=19.25),
        sa.Column('est_actif', sa.Boolean(), default='true'),
        sa.Column('terminal_id', sa.Integer()),
        sa.Column('notes', sa.Text()),
        sa.Column('reference_reglementaire', sa.String(length=100)),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=True),
        sa.ForeignKeyConstraint(['terminal_id'], ['terminaux_portuaires.id'], ),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('code_tarif')
    )
    op.create_index(op.f('ix_tarifs_portuaires_id'), 'tarifs_portuaires', ['id'], unique=False)
    
    # Equipements Portuaires
    op.create_table(
        'equipements_portuaires',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('terminal_id', sa.Integer()),
        sa.Column('type_equipement', sa.String(length=50), nullable=False),
        sa.Column('modele', sa.String(length=100)),
        sa.Column('fabricant', sa.String(length=100)),
        sa.Column('numero_serie', sa.String(length=50)),
        sa.Column('capacite_tonnes', sa.Float()),
        sa.Column('date_acquisition', sa.Date()),
        sa.Column('date_mise_service', sa.Date()),
        sa.Column('date_derniere_maintenance', sa.Date()),
        sa.Column('prochaine_maintenance', sa.Date()),
        sa.Column('statut', sa.String(length=20), default='operationnel'),
        sa.Column('emplacement', sa.String(length=100)),
        sa.Column('est_disponible', sa.Boolean(), default='true'),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=True),
        sa.ForeignKeyConstraint(['terminal_id'], ['terminaux_portuaires.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_equipements_portuaires_id'), 'equipements_portuaires', ['id'], unique=False)
    
    # Zones Portuaires
    op.create_table(
        'zones_portuaires',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('terminal_id', sa.Integer()),
        sa.Column('code', sa.String(length=20), nullable=False),
        sa.Column('nom', sa.String(length=100), nullable=False),
        sa.Column('type_zone', sa.String(length=50)),
        sa.Column('capacite', sa.Integer()),
        sa.Column('capacite_utilisee', sa.Integer(), default=0),
        sa.Column('superficie_m2', sa.Float()),
        sa.Column('localisation', sa.String(length=100)),
        sa.Column('restrictions', sa.Text()),
        sa.Column('est_active', sa.Boolean(), default='true'),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=True),
        sa.ForeignKeyConstraint(['terminal_id'], ['terminaux_portuaires.id'], ),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('code')
    )
    op.create_index(op.f('ix_zones_portuaires_id'), 'zones_portuaires', ['id'], unique=False)
    
    # ========== CAMEROON CUSTOMS ==========
    
    # Articles Code des Douanes
    op.create_table(
        'articles_code_douanes',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('article', sa.String(length=20), nullable=False),
        sa.Column('chapitre', sa.String(length=20)),
        sa.Column('designation', sa.String(length=500), nullable=False),
        sa.Column('description_regime', sa.Text()),
        sa.Column('taux_droit', sa.Float()),
        sa.Column('notes_applicatives', sa.Text()),
        sa.Column('reference_legale', sa.String(length=100)),
        sa.Column('date_modification', sa.Date()),
        sa.Column('est_actif', sa.Boolean(), default='true'),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=True),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('article')
    )
    op.create_index(op.f('ix_articles_code_douanes_id'), 'articles_code_douanes', ['id'], unique=False)
    op.create_index(op.f('ix_articles_code_douanes_article'), 'articles_code_douanes', ['article'], unique=True)
    
    # Taux de Reference BEAC
    op.create_table(
        'taux_reference_beac',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('devise', sa.String(length=3), nullable=False),
        sa.Column('taux_achat', sa.Float(), nullable=False),
        sa.Column('taux_vente', sa.Float(), nullable=False),
        sa.Column('taux_moyen', sa.Float()),
        sa.Column('date_application', sa.Date(), nullable=False),
        sa.Column('source', sa.String(length=50), default='BEAC'),
        sa.Column('est_taux_officiel', sa.Boolean(), default='true'),
        sa.Column('notes', sa.Text()),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_taux_reference_beac_id'), 'taux_reference_beac', ['id'], unique=False)
    op.create_index(op.f('ix_taux_reference_beac_devise'), 'taux_reference_beac', ['devise'], unique=False)
    op.create_index(op.f('ix_taux_reference_beac_date_application'), 'taux_reference_beac', ['date_application'], unique=False)
    
    # BSC
    op.create_table(
        'bsc',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('numero_bsc', sa.String(length=50), nullable=False),
        sa.Column('numero_connaisse', sa.String(length=50), nullable=False),
        sa.Column('navire', sa.String(length=200), nullable=False),
        sa.Column('voyage', sa.String(length=50)),
        sa.Column('port_chargement', sa.String(length=100), nullable=False),
        sa.Column('port_dechargement', sa.String(length=100), nullable=False),
        sa.Column('date_emission', sa.Date(), nullable=False),
        sa.Column('date_validite', sa.Date()),
        sa.Column('agent', sa.String(length=100), nullable=False),
        sa.Column('importateur', sa.String(length=200), nullable=False),
        sa.Column('poids_brut_tonnes', sa.Float()),
        sa.Column('valeur_fob', sa.Numeric(precision=15, scale=2)),
        sa.Column('valeur_caf', sa.Numeric(precision=15, scale=2)),
        sa.Column('devise', sa.String(length=3), default='USD'),
        sa.Column('montant_frais_bsc', sa.Numeric(precision=15, scale=2)),
        sa.Column('devise_frais', sa.String(length=3), default='XAF'),
        sa.Column('statut', sa.String(length=20), default='en_attente'),
        sa.Column('reference_cncc', sa.String(length=50)),
        sa.Column('date_validation', sa.Date()),
        sa.Column('date_paiement', sa.Date()),
        sa.Column('preuve_paiement', sa.String(length=255)),
        sa.Column('notes', sa.Text()),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=True),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('numero_bsc')
    )
    op.create_index(op.f('ix_bsc_id'), 'bsc', ['id'], unique=False)
    op.create_index(op.f('ix_bsc_numero_bsc'), 'bsc', ['numero_bsc'], unique=True)
    
    # CSC
    op.create_table(
        'csc',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('numero_csc', sa.String(length=50), nullable=False),
        sa.Column('numero_connaisse', sa.String(length=50), nullable=False),
        sa.Column('navire', sa.String(length=200), nullable=False),
        sa.Column('port_origine', sa.String(length=100), nullable=False),
        sa.Column('port_destination', sa.String(length=100), nullable=False),
        sa.Column('date_demande', sa.Date(), nullable=False),
        sa.Column('date_emission', sa.Date()),
        sa.Column('date_validite', sa.Date()),
        sa.Column('inspecteur', sa.String(length=100)),
        sa.Column('compagnie_inspection', sa.String(length=100)),
        sa.Column('resultat_inspection', sa.String(length=50)),
        sa.Column('details_inspection', sa.Text()),
        sa.Column('poids_brut_tonnes', sa.Float()),
        sa.Column('nombre_colis', sa.Integer()),
        sa.Column('type_marchandise', sa.String(length=100)),
        sa.Column('valeur_fob', sa.Numeric(precision=15, scale=2)),
        sa.Column('statut', sa.String(length=20), default='en_attente'),
        sa.Column('frais_inspection', sa.Numeric(precision=15, scale=2)),
        sa.Column('date_paiement', sa.Date()),
        sa.Column('preuve_paiement', sa.String(length=255)),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=True),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('numero_csc')
    )
    op.create_index(op.f('ix_csc_id'), 'csc', ['id'], unique=False)
    op.create_index(op.f('ix_csc_numero_csc'), 'csc', ['numero_csc'], unique=True)
    
    # APE
    op.create_table(
        'ape',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('numero_ape', sa.String(length=50), nullable=False),
        sa.Column('dossier_import_id', sa.Integer()),
        sa.Column('importateur', sa.String(length=200), nullable=False),
        sa.Column('montant_xaf', sa.Numeric(precision=15, scale=2), nullable=False),
        sa.Column('montant_devise', sa.Numeric(precision=15, scale=2)),
        sa.Column('devise', sa.String(length=3), nullable=False),
        sa.Column('taux_change', sa.Float()),
        sa.Column('banque', sa.String(length=100), nullable=False),
        sa.Column('compte_bancaire', sa.String(length=30)),
        sa.Column('beneficiaire_etranger', sa.String(length=200)),
        sa.Column('pays_beneficiaire', sa.String(length=50)),
        sa.Column('objet_transfert', sa.String(length=200)),
        sa.Column('date_demande', sa.Date(), nullable=False),
        sa.Column('date_autorisation', sa.Date()),
        sa.Column('date_execution', sa.Date()),
        sa.Column('reference_beac', sa.String(length=50)),
        sa.Column('statut', sa.String(length=20), default='en_attente'),
        sa.Column('agent_beac', sa.String(length=100)),
        sa.Column('motif_refus', sa.Text()),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=True),
        sa.ForeignKeyConstraint(['dossier_import_id'], ['dossiers_transit_avance.id'], ),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('numero_ape')
    )
    op.create_index(op.f('ix_ape_id'), 'ape', ['id'], unique=False)
    op.create_index(op.f('ix_ape_numero_ape'), 'ape', ['numero_ape'], unique=True)
    
    # DUM
    op.create_table(
        'dum',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('numero_dum', sa.String(length=50), nullable=False),
        sa.Column('dossier_transit_id', sa.Integer()),
        sa.Column('type_operation', sa.String(length=20), nullable=False),
        sa.Column('regime_douanier', sa.String(length=50), nullable=False),
        sa.Column('bureau_douane', sa.String(length=100), nullable=False),
        sa.Column('date_depot', sa.Date(), nullable=False),
        sa.Column('declarant', sa.String(length=200), nullable=False),
        sa.Column('numero_agrement', sa.String(length=50)),
        sa.Column('importateur', sa.String(length=200), nullable=False),
        sa.Column('numero_contribuable', sa.String(length=50)),
        sa.Column('marchandise', sa.Text(), nullable=False),
        sa.Column('nomenclature', sa.String(length=20)),
        sa.Column('poids_brut', sa.Float()),
        sa.Column('poids_net', sa.Float()),
        sa.Column('nombre_colis', sa.Integer()),
        sa.Column('valeur_fob', sa.Numeric(precision=15, scale=2)),
        sa.Column('valeur_caf', sa.Numeric(precision=15, scale=2)),
        sa.Column('devise', sa.String(length=3), default='USD'),
        sa.Column('taux_change', sa.Float()),
        sa.Column('valeur_douane_xaf', sa.Numeric(precision=15, scale=2)),
        sa.Column('droits_douane', sa.Numeric(precision=15, scale=2)),
        sa.Column('tva', sa.Numeric(precision=15, scale=2)),
        sa.Column('centimes_additionnels', sa.Numeric(precision=15, scale=2)),
        sa.Column('timbre_usage', sa.Numeric(precision=15, scale=2)),
        sa.Column('montant_total', sa.Numeric(precision=15, scale=2)),
        sa.Column('statut', sa.String(length=20), default='en_attente'),
        sa.Column('date_validation', sa.Date()),
        sa.Column('date_liquidation', sa.Date()),
        sa.Column('agent_douane', sa.String(length=100)),
        sa.Column('reference_sydonia', sa.String(length=50)),
        sa.Column('notes', sa.Text()),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=True),
        sa.ForeignKeyConstraint(['dossier_transit_id'], ['dossiers_transit_avance.id'], ),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('numero_dum')
    )
    op.create_index(op.f('ix_dum_id'), 'dum', ['id'], unique=False)
    op.create_index(op.f('ix_dum_numero_dum'), 'dum', ['numero_dum'], unique=True)
    
    # BV
    op.create_table(
        'bv',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('numero_bv', sa.String(length=50), nullable=False),
        sa.Column('dum_id', sa.Integer()),
        sa.Column('date_validation', sa.Date(), nullable=False),
        sa.Column('validateur', sa.String(length=100), nullable=False),
        sa.Column('grade', sa.String(length=50)),
        sa.Column('resultat', sa.String(length=20), nullable=False),
        sa.Column('motifs_rejet', sa.Text()),
        sa.Column('corrections_requises', sa.Text()),
        sa.Column('date_correction', sa.Date()),
        sa.Column('statut_final', sa.String(length=20)),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=True),
        sa.ForeignKeyConstraint(['dum_id'], ['dum.id'], ),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('numero_bv')
    )
    op.create_index(op.f('ix_bv_id'), 'bv', ['id'], unique=False)
    op.create_index(op.f('ix_bv_numero_bv'), 'bv', ['numero_bv'], unique=True)
    
    # ========== CEMAC TRANSIT ==========
    
    # Corridors CEMAC
    op.create_table(
        'corridors_cemac',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('code', sa.String(length=10), nullable=False),
        sa.Column('nom', sa.String(length=100), nullable=False),
        sa.Column('origine', sa.String(length=100), nullable=False),
        sa.Column('destination', sa.String(length=100), nullable=False),
        sa.Column('distance_km', sa.Integer(), nullable=False),
        sa.Column('duree_estimee_heures', sa.Integer(), nullable=False),
        sa.Column('pays_origine', sa.String(length=2), nullable=False),
        sa.Column('pays_destination', sa.String(length=2), nullable=False),
        sa.Column('pays_traverses', sa.Text()),
        sa.Column('etat_route', sa.String(length=20), default='moyen'),
        sa.Column('description_route', sa.Text()),
        sa.Column('risques', sa.Text()),
        sa.Column('points_dangers', sa.Text()),
        sa.Column('alternatives', sa.Text()),
        sa.Column('est_actif', sa.Boolean(), default='true'),
        sa.Column('date_derniere_maj', sa.Date()),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=True),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('code')
    )
    op.create_index(op.f('ix_corridors_cemac_id'), 'corridors_cemac', ['id'], unique=False)
    op.create_index(op.f('ix_corridors_cemac_code'), 'corridors_cemac', ['code'], unique=True)
    
    # Postes Frontaliers
    op.create_table(
        'postes_frontaliers',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('corridor_id', sa.Integer(), nullable=False),
        sa.Column('code', sa.String(length=20), nullable=False),
        sa.Column('nom', sa.String(length=100), nullable=False),
        sa.Column('pays', sa.String(length=50), nullable=False),
        sa.Column('ville', sa.String(length=100)),
        sa.Column('type_poste', sa.String(length=50), nullable=False),
        sa.Column('coordonnees', sa.String(length=100)),
        sa.Column('horaires', sa.Text()),
        sa.Column('capacite_journaliere', sa.Integer()),
        sa.Column('temps_moyen_traitement_heures', sa.Float()),
        sa.Column('services_disponibles', sa.Text()),
        sa.Column('telephone', sa.String(length=20)),
        sa.Column('email', sa.String(length=100)),
        sa.Column('chef_poste', sa.String(length=100)),
        sa.Column('contact_urgence', sa.String(length=20)),
        sa.Column('est_actif', sa.Boolean(), default='true'),
        sa.Column('notes', sa.Text()),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=True),
        sa.ForeignKeyConstraint(['corridor_id'], ['corridors_cemac.id'], ),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('code')
    )
    op.create_index(op.f('ix_postes_frontaliers_id'), 'postes_frontaliers', ['id'], unique=False)
    
    # Procedures TIR
    op.create_table(
        'procedures_tir',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('numero_carnet', sa.String(length=50), nullable=False),
        sa.Column('dossier_transit_id', sa.Integer()),
        sa.Column('date_delivrance', sa.Date(), nullable=False),
        sa.Column('date_validite', sa.Date(), nullable=False),
        sa.Column('numero_assurance', sa.String(length=50), nullable=False),
        sa.Column('assureur', sa.String(length=100), nullable=False),
        sa.Column('montant_garantie', sa.Float(), nullable=False),
        sa.Column('devise', sa.String(length=3), default='XAF'),
        sa.Column('bureau_depart', sa.String(length=100), nullable=False),
        sa.Column('bureau_arrivee', sa.String(length=100), nullable=False),
        sa.Column('corridor', sa.String(length=20), nullable=False),
        sa.Column('nombre_volets', sa.Integer(), default=4),
        sa.Column('numero_scelle', sa.String(length=50)),
        sa.Column('date_depart', sa.Date()),
        sa.Column('date_arrivee', sa.Date()),
        sa.Column('statut', sa.String(length=20), default='en_cours'),
        sa.Column('observations', sa.Text()),
        sa.Column('reference_iru', sa.String(length=50)),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=True),
        sa.ForeignKeyConstraint(['dossier_transit_id'], ['dossiers_transit_avance.id'], ),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('numero_carnet')
    )
    op.create_index(op.f('ix_procedures_tir_id'), 'procedures_tir', ['id'], unique=False)
    op.create_index(op.f('ix_procedures_tir_numero_carnet'), 'procedures_tir', ['numero_carnet'], unique=True)
    
    # Procedures TSD
    op.create_table(
        'procedures_tsd',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('numero_tsd', sa.String(length=50), nullable=False),
        sa.Column('dossier_transit_id', sa.Integer()),
        sa.Column('date_delivrance', sa.Date(), nullable=False),
        sa.Column('date_validite', sa.Date(), nullable=False),
        sa.Column('bureau_depart', sa.String(length=100), nullable=False),
        sa.Column('bureau_arrivee', sa.String(length=100), nullable=False),
        sa.Column('corridor', sa.String(length=20), nullable=False),
        sa.Column('montant_garantie', sa.Float()),
        sa.Column('devise', sa.String(length=3), default='XAF'),
        sa.Column('duree_transit_jours', sa.Integer(), default=15),
        sa.Column('date_depart', sa.Date()),
        sa.Column('date_arrivee', sa.Date()),
        sa.Column('statut', sa.String(length=20), default='en_cours'),
        sa.Column('observations', sa.Text()),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=True),
        sa.ForeignKeyConstraint(['dossier_transit_id'], ['dossiers_transit_avance.id'], ),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('numero_tsd')
    )
    op.create_index(op.f('ix_procedures_tsd_id'), 'procedures_tsd', ['id'], unique=False)
    op.create_index(op.f('ix_procedures_tsd_numero_tsd'), 'procedures_tsd', ['numero_tsd'], unique=True)
    
    # Frais Corridor
    op.create_table(
        'frais_corridor',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('corridor_id', sa.Integer(), nullable=False),
        sa.Column('type_frais', sa.String(length=50), nullable=False),
        sa.Column('designation', sa.String(length=200), nullable=False),
        sa.Column('montant', sa.Float(), nullable=False),
        sa.Column('devise', sa.String(length=3), default='XAF'),
        sa.Column('unite', sa.String(length=20)),
        sa.Column('poste_frontalier_id', sa.Integer()),
        sa.Column('date_application', sa.Date(), nullable=False),
        sa.Column('est_actif', sa.Boolean(), default='true'),
        sa.Column('description', sa.Text()),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=True),
        sa.ForeignKeyConstraint(['corridor_id'], ['corridors_cemac.id'], ),
        sa.ForeignKeyConstraint(['poste_frontalier_id'], ['postes_frontaliers.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_frais_corridor_id'), 'frais_corridor', ['id'], unique=False)
    
    # Scelles Routiers
    op.create_table(
        'scelles_routiers',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('numero_scelle', sa.String(length=50), nullable=False),
        sa.Column('type_scelle', sa.String(length=20), nullable=False),
        sa.Column('dossier_transit_id', sa.Integer()),
        sa.Column('procedure_id', sa.Integer()),
        sa.Column('date_pose', sa.Date(), nullable=False),
        sa.Column('poste_pose', sa.String(length=100), nullable=False),
        sa.Column('agent_pose', sa.String(length=100), nullable=False),
        sa.Column('date_retire', sa.Date()),
        sa.Column('poste_retire', sa.String(length=100)),
        sa.Column('agent_retire', sa.String(length=100)),
        sa.Column('etat', sa.String(length=20), default='intact'),
        sa.Column('motif_casse', sa.Text()),
        sa.Column('photo', sa.String(length=255)),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=True),
        sa.ForeignKeyConstraint(['dossier_transit_id'], ['dossiers_transit_avance.id'], ),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('numero_scelle')
    )
    op.create_index(op.f('ix_scelles_routiers_id'), 'scelles_routiers', ['id'], unique=False)
    op.create_index(op.f('ix_scelles_routiers_numero_scelle'), 'scelles_routiers', ['numero_scelle'], unique=True)
    
    # Incidents Corridor
    op.create_table(
        'incidents_corridor',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('corridor_id', sa.Integer(), nullable=False),
        sa.Column('type_incident', sa.String(length=50), nullable=False),
        sa.Column('date_incident', sa.DateTime(timezone=True), nullable=False),
        sa.Column('localisation', sa.String(length=100), nullable=False),
        sa.Column('kilometrage', sa.Float()),
        sa.Column('description', sa.Text(), nullable=False),
        sa.Column('vehicule_id', sa.Integer()),
        sa.Column('conducteur_id', sa.Integer()),
        sa.Column('degats', sa.Text()),
        sa.Column('blesses', sa.Text()),
        sa.Column('montant_degats', sa.Float()),
        sa.Column('devise', sa.String(length=3), default='XAF'),
        sa.Column('police_id', sa.String(length=50)),
        sa.Column('assurance_id', sa.Integer()),
        sa.Column('statut', sa.String(length=20), default='en_cours'),
        sa.Column('date_resolution', sa.Date()),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=True),
        sa.ForeignKeyConstraint(['corridor_id'], ['corridors_cemac.id'], ),
        sa.ForeignKeyConstraint(['vehicule_id'], ['camions.id'], ),
        sa.ForeignKeyConstraint(['conducteur_id'], ['conducteurs.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_incidents_corridor_id'), 'incidents_corridor', ['id'], unique=False)
    
    # ========== CONTAINER LIFECYCLE ==========
    
    # Conteneurs
    op.create_table(
        'conteneurs',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('numero', sa.String(length=20), nullable=False),
        sa.Column('type_conteneur', sa.String(length=50), nullable=False),
        sa.Column('taille_pieds', sa.Integer(), nullable=False),
        sa.Column('etat', sa.String(length=20), default='clean'),
        sa.Column('proprietaire', sa.String(length=100)),
        sa.Column('compagnie', sa.String(length=100)),
        sa.Column('date_fabrication', sa.Date()),
        sa.Column('date_derniere_inspection', sa.Date()),
        sa.Column('prochaine_inspection', sa.Date()),
        sa.Column('tare_kg', sa.Float()),
        sa.Column('max_payload_kg', sa.Float()),
        sa.Column('volume_m3', sa.Float()),
        sa.Column('temperature_c', sa.Float()),
        sa.Column('est_hazardous', sa.Boolean(), default='false'),
        sa.Column('classe_hazard', sa.String(length=20)),
        sa.Column('notes', sa.Text()),
        sa.Column('photo_avant', sa.String(length=255)),
        sa.Column('photo_apres', sa.String(length=255)),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=True),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('numero')
    )
    op.create_index(op.f('ix_conteneurs_id'), 'conteneurs', ['id'], unique=False)
    op.create_index(op.f('ix_conteneurs_numero'), 'conteneurs', ['numero'], unique=True)
    
    # Cycle Conteneur
    op.create_table(
        'cycle_conteneur',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('conteneur_id', sa.Integer(), nullable=False),
        sa.Column('navire_id', sa.Integer()),
        sa.Column('voyage', sa.String(length=50)),
        sa.Column('date_arrivee_navire', sa.DateTime(timezone=True)),
        sa.Column('date_dechargement', sa.DateTime(timezone=True)),
        sa.Column('date_mise_quai', sa.DateTime(timezone=True)),
        sa.Column('date_sortie', sa.DateTime(timezone=True)),
        sa.Column('terminal_id', sa.Integer()),
        sa.Column('localisation', sa.String(length=100)),
        sa.Column('statut', sa.String(length=20), default='arrive'),
        sa.Column('operateur_dechargement', sa.String(length=100)),
        sa.Column('operateur_manutention', sa.String(length=100)),
        sa.Column('grue_utilisee', sa.String(length=50)),
        sa.Column('temps_cycle_heures', sa.Float()),
        sa.Column('incidents', sa.Text()),
        sa.Column('photos', sa.Text()),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=True),
        sa.ForeignKeyConstraint(['conteneur_id'], ['conteneurs.id'], ),
        sa.ForeignKeyConstraint(['navire_id'], ['navires.id'], ),
        sa.ForeignKeyConstraint(['terminal_id'], ['terminaux_portuaires.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_cycle_conteneur_id'), 'cycle_conteneur', ['id'], unique=False)
    
    # Dommages Conteneur
    op.create_table(
        'dommages_conteneur',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('conteneur_id', sa.Integer(), nullable=False),
        sa.Column('cycle_id', sa.Integer()),
        sa.Column('type_dommage', sa.String(length=50), nullable=False),
        sa.Column('description', sa.Text(), nullable=False),
        sa.Column('gravite', sa.String(length=20), nullable=False),
        sa.Column('date_constatation', sa.DateTime(timezone=True), nullable=False),
        sa.Column('lieu_constatation', sa.String(length=100), nullable=False),
        sa.Column('constatateur', sa.String(length=100), nullable=False),
        sa.Column('responsable', sa.String(length=100)),
        sa.Column('photos', sa.Text()),
        sa.Column('cout_reparation', sa.Float()),
        sa.Column('devise', sa.String(length=3), default='XAF'),
        sa.Column('numero_reclamation', sa.String(length=50)),
        sa.Column('assurance_id', sa.Integer()),
        sa.Column('statut_reclamation', sa.String(length=20), default='en_attente'),
        sa.Column('date_resolution', sa.Date()),
        sa.Column('notes', sa.Text()),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=True),
        sa.ForeignKeyConstraint(['conteneur_id'], ['conteneurs.id'], ),
        sa.ForeignKeyConstraint(['cycle_id'], ['cycle_conteneur.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_dommages_conteneur_id'), 'dommages_conteneur', ['id'], unique=False)
    
    # Empotage/Depotage
    op.create_table(
        'empotage_depotage',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('conteneur_id', sa.Integer(), nullable=False),
        sa.Column('type_operation', sa.String(length=20), nullable=False),
        sa.Column('date_operation', sa.DateTime(timezone=True), nullable=False),
        sa.Column('terminal_id', sa.Integer()),
        sa.Column('operateur', sa.String(length=100), nullable=False),
        sa.Column('chef_equipe', sa.String(length=100)),
        sa.Column('liste_marchandise', sa.Text()),
        sa.Column('poids_brut_kg', sa.Float()),
        sa.Column('poids_net_kg', sa.Float()),
        sa.Column('nombre_colis', sa.Integer()),
        sa.Column('temperature_c', sa.Float()),
        sa.Column('temps_operation_heures', sa.Float()),
        sa.Column('incident', sa.Text()),
        sa.Column('controle_qualite', sa.String(length=20), default='conforme'),
        sa.Column('notes', sa.Text()),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=True),
        sa.ForeignKeyConstraint(['conteneur_id'], ['conteneurs.id'], ),
        sa.ForeignKeyConstraint(['terminal_id'], ['terminaux_portuaires.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_empotage_depotage_id'), 'empotage_depotage', ['id'], unique=False)
    
    # Inspections Conteneur
    op.create_table(
        'inspections_conteneur',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('conteneur_id', sa.Integer(), nullable=False),
        sa.Column('type_inspection', sa.String(length=50), nullable=False),
        sa.Column('date_inspection', sa.DateTime(timezone=True), nullable=False),
        sa.Column('inspecteur', sa.String(length=100), nullable=False),
        sa.Column('certification', sa.String(length=100)),
        sa.Column('resultat', sa.String(length=20), nullable=False),
        sa.Column('points_inspection', sa.Text()),
        sa.Column('etat_caisse', sa.String(length=20)),
        sa.Column('etat_toit', sa.String(length=20)),
        sa.Column('etat_portes', sa.String(length=20)),
        sa.Column('etat_sol', sa.String(length=20)),
        sa.Column('etat_renforts', sa.String(length=20)),
        sa.Column('etat_joints', sa.String(length=20)),
        sa.Column('recommandations', sa.Text()),
        sa.Column('prochaine_inspection', sa.Date()),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=True),
        sa.ForeignKeyConstraint(['conteneur_id'], ['conteneurs.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_inspections_conteneur_id'), 'inspections_conteneur', ['id'], unique=False)


def downgrade():
    # Drop tables in reverse order
    op.drop_index(op.f('ix_inspections_conteneur_id'), table_name='inspections_conteneur')
    op.drop_table('inspections_conteneur')
    
    op.drop_index(op.f('ix_empotage_depotage_id'), table_name='empotage_depotage')
    op.drop_table('empotage_depotage')
    
    op.drop_index(op.f('ix_dommages_conteneur_id'), table_name='dommages_conteneur')
    op.drop_table('dommages_conteneur')
    
    op.drop_index(op.f('ix_cycle_conteneur_id'), table_name='cycle_conteneur')
    op.drop_table('cycle_conteneur')
    
    op.drop_index(op.f('ix_conteneurs_numero'), table_name='conteneurs')
    op.drop_index(op.f('ix_conteneurs_id'), table_name='conteneurs')
    op.drop_table('conteneurs')
    
    op.drop_index(op.f('ix_incidents_corridor_id'), table_name='incidents_corridor')
    op.drop_table('incidents_corridor')
    
    op.drop_index(op.f('ix_scelles_routiers_numero_scelle'), table_name='scelles_routiers')
    op.drop_index(op.f('ix_scelles_routiers_id'), table_name='scelles_routiers')
    op.drop_table('scelles_routiers')
    
    op.drop_index(op.f('ix_frais_corridor_id'), table_name='frais_corridor')
    op.drop_table('frais_corridor')
    
    op.drop_index(op.f('ix_procedures_tsd_numero_tsd'), table_name='procedures_tsd')
    op.drop_index(op.f('ix_procedures_tsd_id'), table_name='procedures_tsd')
    op.drop_table('procedures_tsd')
    
    op.drop_index(op.f('ix_procedures_tir_numero_carnet'), table_name='procedures_tir')
    op.drop_index(op.f('ix_procedures_tir_id'), table_name='procedures_tir')
    op.drop_table('procedures_tir')
    
    op.drop_index(op.f('ix_postes_frontaliers_id'), table_name='postes_frontaliers')
    op.drop_table('postes_frontaliers')
    
    op.drop_index(op.f('ix_corridors_cemac_code'), table_name='corridors_cemac')
    op.drop_index(op.f('ix_corridors_cemac_id'), table_name='corridors_cemac')
    op.drop_table('corridors_cemac')
    
    op.drop_index(op.f('ix_bv_numero_bv'), table_name='bv')
    op.drop_index(op.f('ix_bv_id'), table_name='bv')
    op.drop_table('bv')
    
    op.drop_index(op.f('ix_dum_numero_dum'), table_name='dum')
    op.drop_index(op.f('ix_dum_id'), table_name='dum')
    op.drop_table('dum')
    
    op.drop_index(op.f('ix_ape_numero_ape'), table_name='ape')
    op.drop_index(op.f('ix_ape_id'), table_name='ape')
    op.drop_table('ape')
    
    op.drop_index(op.f('ix_csc_numero_csc'), table_name='csc')
    op.drop_index(op.f('ix_csc_id'), table_name='csc')
    op.drop_table('csc')
    
    op.drop_index(op.f('ix_bsc_numero_bsc'), table_name='bsc')
    op.drop_index(op.f('ix_bsc_id'), table_name='bsc')
    op.drop_table('bsc')
    
    op.drop_index(op.f('ix_taux_reference_beac_date_application'), table_name='taux_reference_beac')
    op.drop_index(op.f('ix_taux_reference_beac_devise'), table_name='taux_reference_beac')
    op.drop_index(op.f('ix_taux_reference_beac_id'), table_name='taux_reference_beac')
    op.drop_table('taux_reference_beac')
    
    op.drop_index(op.f('ix_articles_code_douanes_article'), table_name='articles_code_douanes')
    op.drop_index(op.f('ix_articles_code_douanes_id'), table_name='articles_code_douanes')
    op.drop_table('articles_code_douanes')
    
    op.drop_index(op.f('ix_zones_portuaires_id'), table_name='zones_portuaires')
    op.drop_table('zones_portuaires')
    
    op.drop_index(op.f('ix_equipements_portuaires_id'), table_name='equipements_portuaires')
    op.drop_table('equipements_portuaires')
    
    op.drop_index(op.f('ix_tarifs_portuaires_id'), table_name='tarifs_portuaires')
    op.drop_table('tarifs_portuaires')
    
    op.drop_index(op.f('ix_terminaux_portuaires_id'), table_name='terminaux_portuaires')
    op.drop_table('terminaux_portuaires')
    
    op.drop_index(op.f('ix_ports_cameroun_code'), table_name='ports_cameroun')
    op.drop_index(op.f('ix_ports_cameroun_id'), table_name='ports_cameroun')
    op.drop_table('ports_cameroun')
