"""Add remaining models for Version 2.0

Revision ID: 003_add_remaining_models
Revises: 002_complete_models
Create Date: 2026-08-17 02:30:00.000000

"""
from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision = '003_add_remaining_models'
down_revision = '002_complete_models'
branch_labels = None
depends_on = None


def upgrade():
    # Parc models
    op.create_table(
        'vehicules',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('immatriculation', sa.String(length=20), nullable=False),
        sa.Column('marque', sa.String(length=50), nullable=True),
        sa.Column('modele', sa.String(length=50), nullable=True),
        sa.Column('annee', sa.Integer(), nullable=True),
        sa.Column('type_vehicule', sa.String(length=50), nullable=True),
        sa.Column('carburant', sa.String(length=20), nullable=True),
        sa.Column('capacite_reservoir', sa.Float(), nullable=True),
        sa.Column('consommation_moyenne', sa.Float(), nullable=True),
        sa.Column('status', sa.String(length=50), nullable=True),
        sa.Column('kilometrage', sa.Integer(), nullable=True),
        sa.Column('localisation', sa.String(length=100), nullable=True),
        sa.Column('assigne_a', sa.Integer(), nullable=True),
        sa.Column('is_active', sa.Boolean(), nullable=True),
        sa.Column('date_acquisition', sa.DateTime(timezone=True), nullable=True),
        sa.Column('date_mise_service', sa.DateTime(timezone=True), nullable=True),
        sa.Column('valeur_acquisition', sa.Float(), nullable=True),
        sa.Column('valeur_actuelle', sa.Float(), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('CURRENT_TIMESTAMP'), nullable=True),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=True),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('immatriculation')
    )

    op.create_table(
        'equipements',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('code', sa.String(length=50), nullable=False),
        sa.Column('nom', sa.String(length=100), nullable=False),
        sa.Column('type_equipement', sa.String(length=50), nullable=True),
        sa.Column('marque', sa.String(length=50), nullable=True),
        sa.Column('modele', sa.String(length=50), nullable=True),
        sa.Column('numero_serie', sa.String(length=50), nullable=True),
        sa.Column('capacite', sa.Float(), nullable=True),
        sa.Column('status', sa.String(length=20), nullable=True),
        sa.Column('date_acquisition', sa.DateTime(timezone=True), nullable=True),
        sa.Column('localisation', sa.String(length=100), nullable=True),
        sa.Column('valeur', sa.Float(), nullable=True),
        sa.Column('is_active', sa.Boolean(), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('CURRENT_TIMESTAMP'), nullable=True),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=True),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('code')
    )

    # Maintenance models
    op.create_table(
        'interventions',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('reference', sa.String(length=50), nullable=False),
        sa.Column('equipement_id', sa.Integer(), nullable=True),
        sa.Column('type_intervention', sa.String(length=50), nullable=True),
        sa.Column('priorite', sa.String(length=20), nullable=True),
        sa.Column('statut', sa.String(length=50), nullable=True),
        sa.Column('date_planifiee', sa.DateTime(timezone=True), nullable=True),
        sa.Column('date_debut', sa.DateTime(timezone=True), nullable=True),
        sa.Column('date_fin', sa.DateTime(timezone=True), nullable=True),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('diagnostic', sa.Text(), nullable=True),
        sa.Column('travaux_realises', sa.Text(), nullable=True),
        sa.Column('cout_main_oeuvre', sa.Float(), nullable=True),
        sa.Column('cout_pieces', sa.Float(), nullable=True),
        sa.Column('cout_total', sa.Float(), nullable=True),
        sa.Column('technicien', sa.String(length=100), nullable=True),
        sa.Column('validateur', sa.String(length=100), nullable=True),
        sa.Column('date_validation', sa.DateTime(timezone=True), nullable=True),
        sa.Column('notes', sa.Text(), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('CURRENT_TIMESTAMP'), nullable=True),
        sa.Column('created_by', sa.Integer(), nullable=True),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('reference')
    )

    op.create_table(
        'pieces_rechange',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('code', sa.String(length=50), nullable=False),
        sa.Column('designation', sa.String(length=200), nullable=False),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('categorie', sa.String(length=50), nullable=True),
        sa.Column('fournisseur', sa.String(length=100), nullable=True),
        sa.Column('reference_fournisseur', sa.String(length=50), nullable=True),
        sa.Column('prix_unitaire', sa.Float(), nullable=True),
        sa.Column('quantite_stock', sa.Integer(), nullable=True),
        sa.Column('quantite_minimum', sa.Integer(), nullable=True),
        sa.Column('emplacement', sa.String(length=100), nullable=True),
        sa.Column('intervention_id', sa.Integer(), nullable=True),
        sa.Column('date_utilisation', sa.DateTime(timezone=True), nullable=True),
        sa.Column('is_active', sa.Boolean(), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('CURRENT_TIMESTAMP'), nullable=True),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=True),
        sa.ForeignKeyConstraint(['intervention_id'], ['interventions.id'], ),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('code')
    )

    # Magasin extended models
    op.create_table(
        'mouvements_stocks',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('reference', sa.String(length=50), nullable=False),
        sa.Column('stock_id', sa.Integer(), nullable=True),
        sa.Column('type_mouvement', sa.String(length=50), nullable=False),
        sa.Column('quantite', sa.Float(), nullable=False),
        sa.Column('quantite_avant', sa.Float(), nullable=True),
        sa.Column('quantite_apres', sa.Float(), nullable=True),
        sa.Column('prix_unitaire', sa.Float(), nullable=True),
        sa.Column('valeur_totale', sa.Float(), nullable=True),
        sa.Column('raison', sa.String(length=200), nullable=True),
        sa.Column('document_reference', sa.String(length=50), nullable=True),
        sa.Column('destination', sa.String(length=100), nullable=True),
        sa.Column('operateur_id', sa.Integer(), nullable=True),
        sa.Column('date_mouvement', sa.DateTime(timezone=True), server_default=sa.text('CURRENT_TIMESTAMP'), nullable=True),
        sa.Column('notes', sa.Text(), nullable=True),
        sa.ForeignKeyConstraint(['stock_id'], ['stocks.id'], ),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('reference')
    )

    op.create_table(
        'entrepots',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('code', sa.String(length=20), nullable=False),
        sa.Column('nom', sa.String(length=100), nullable=False),
        sa.Column('adresse', sa.Text(), nullable=True),
        sa.Column('ville', sa.String(length=50), nullable=True),
        sa.Column('telephone', sa.String(length=20), nullable=True),
        sa.Column('responsable', sa.String(length=100), nullable=True),
        sa.Column('capacite', sa.Float(), nullable=True),
        sa.Column('superficie', sa.Float(), nullable=True),
        sa.Column('is_active', sa.Boolean(), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('CURRENT_TIMESTAMP'), nullable=True),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=True),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('code')
    )

    # Finance extended models
    op.create_table(
        'lignes_factures',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('facture_id', sa.Integer(), nullable=False),
        sa.Column('description', sa.String(length=200), nullable=False),
        sa.Column('quantite', sa.Float(), nullable=False),
        sa.Column('prix_unitaire_ht', sa.Float(), nullable=False),
        sa.Column('taux_tva', sa.Float(), nullable=True),
        sa.Column('montant_ht', sa.Float(), nullable=False),
        sa.Column('montant_tva', sa.Float(), nullable=True),
        sa.Column('montant_ttc', sa.Float(), nullable=True),
        sa.Column('reference_article', sa.String(length=50), nullable=True),
        sa.Column('compte_comptable', sa.String(length=50), nullable=True),
        sa.ForeignKeyConstraint(['facture_id'], ['factures.id'], ),
        sa.PrimaryKeyConstraint('id')
    )

    op.create_table(
        'paiements',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('reference', sa.String(length=50), nullable=False),
        sa.Column('facture_id', sa.Integer(), nullable=True),
        sa.Column('date_paiement', sa.DateTime(timezone=True), nullable=False),
        sa.Column('montant', sa.Float(), nullable=False),
        sa.Column('mode_paiement', sa.String(length=50), nullable=True),
        sa.Column('reference_paiement', sa.String(length=100), nullable=True),
        sa.Column('banque', sa.String(length=100), nullable=True),
        sa.Column('notes', sa.Text(), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('CURRENT_TIMESTAMP'), nullable=True),
        sa.ForeignKeyConstraint(['facture_id'], ['factures.id'], ),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('reference')
    )

    op.create_table(
        'comptes',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('numero', sa.String(length=20), nullable=False),
        sa.Column('nom', sa.String(length=100), nullable=False),
        sa.Column('type_compte', sa.String(length=50), nullable=True),
        sa.Column('sous_type', sa.String(length=50), nullable=True),
        sa.Column('solde', sa.Float(), nullable=True),
        sa.Column('compte_parent_id', sa.Integer(), nullable=True),
        sa.Column('is_actif', sa.Boolean(), nullable=True),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('CURRENT_TIMESTAMP'), nullable=True),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=True),
        sa.ForeignKeyConstraint(['compte_parent_id'], ['comptes.id'], ),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('numero')
    )

    op.create_table(
        'ecritures_comptables',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('numero_piece', sa.String(length=50), nullable=False),
        sa.Column('date_ecriture', sa.DateTime(timezone=True), nullable=False),
        sa.Column('libelle', sa.String(length=200), nullable=False),
        sa.Column('compte_debit_id', sa.Integer(), nullable=True),
        sa.Column('compte_credit_id', sa.Integer(), nullable=True),
        sa.Column('montant', sa.Float(), nullable=False),
        sa.Column('devise', sa.String(length=10), nullable=True),
        sa.Column('reference_facture', sa.String(length=50), nullable=True),
        sa.Column('reference_paiement', sa.String(length=50), nullable=True),
        sa.Column('journal', sa.String(length=50), nullable=True),
        sa.Column('periode_comptable', sa.String(length=7), nullable=True),
        sa.Column('lettrage', sa.String(length=20), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('CURRENT_TIMESTAMP'), nullable=True),
        sa.Column('created_by', sa.Integer(), nullable=True),
        sa.ForeignKeyConstraint(['compte_debit_id'], ['comptes.id'], ),
        sa.ForeignKeyConstraint(['compte_credit_id'], ['comptes.id'], ),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('numero_piece')
    )

    # Acconage extended models
    op.create_table(
        'operations_acconage',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('reference', sa.String(length=50), nullable=False),
        sa.Column('escale_id', sa.Integer(), nullable=True),
        sa.Column('type_operation', sa.String(length=50), nullable=True),
        sa.Column('date_debut', sa.DateTime(timezone=True), nullable=True),
        sa.Column('date_fin', sa.DateTime(timezone=True), nullable=True),
        sa.Column('marchandise', sa.String(length=100), nullable=True),
        sa.Column('quantite', sa.Float(), nullable=True),
        sa.Column('unite', sa.String(length=20), nullable=True),
        sa.Column('taux', sa.Float(), nullable=True),
        sa.Column('montant', sa.Float(), nullable=True),
        sa.Column('equipe', sa.String(length=100), nullable=True),
        sa.Column('equipement', sa.String(length=100), nullable=True),
        sa.Column('statut', sa.String(length=20), nullable=True),
        sa.Column('notes', sa.Text(), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('CURRENT_TIMESTAMP'), nullable=True),
        sa.Column('created_by', sa.Integer(), nullable=True),
        sa.ForeignKeyConstraint(['escale_id'], ['escales.id'], ),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('reference')
    )

    # Transit extended models
    op.create_table(
        'declarations_douanieres',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('numero_declaration', sa.String(length=50), nullable=False),
        sa.Column('dossier_transit_id', sa.Integer(), nullable=True),
        sa.Column('regime_douanier', sa.String(length=50), nullable=True),
        sa.Column('bureau_douane', sa.String(length=100), nullable=True),
        sa.Column('date_enregistrement', sa.DateTime(timezone=True), nullable=True),
        sa.Column('date_validation', sa.DateTime(timezone=True), nullable=True),
        sa.Column('date_acquittement', sa.DateTime(timezone=True), nullable=True),
        sa.Column('valeur_declaree', sa.Float(), nullable=True),
        sa.Column('poids_declare', sa.Float(), nullable=True),
        sa.Column('taux_droit', sa.Float(), nullable=True),
        sa.Column('montant_droit', sa.Float(), nullable=True),
        sa.Column('taux_tva', sa.Float(), nullable=True),
        sa.Column('montant_tva', sa.Float(), nullable=True),
        sa.Column('autres_taxes', sa.Float(), nullable=True),
        sa.Column('total_taxes', sa.Float(), nullable=True),
        sa.Column('numero_b7', sa.String(length=50), nullable=True),
        sa.Column('numero_quitus', sa.String(length=50), nullable=True),
        sa.Column('statut', sa.String(length=20), nullable=True),
        sa.Column('notes', sa.Text(), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('CURRENT_TIMESTAMP'), nullable=True),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=True),
        sa.ForeignKeyConstraint(['dossier_transit_id'], ['dossiers_transit.id'], ),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('numero_declaration')
    )

    # QHSE extended models
    op.create_table(
        'rapports_qhse',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('reference', sa.String(length=50), nullable=False),
        sa.Column('incident_id', sa.Integer(), nullable=True),
        sa.Column('type_rapport', sa.String(length=50), nullable=True),
        sa.Column('date_rapport', sa.DateTime(timezone=True), nullable=False),
        sa.Column('auteur', sa.Integer(), nullable=True),
        sa.Column('constatations', sa.Text(), nullable=True),
        sa.Column('analyse_causes', sa.Text(), nullable=True),
        sa.Column('recommandations', sa.Text(), nullable=True),
        sa.Column('actions_correctives', sa.Text(), nullable=True),
        sa.Column('mesures_preventives', sa.Text(), nullable=True),
        sa.Column('delai_action', sa.DateTime(timezone=True), nullable=True),
        sa.Column('responsable_action', sa.Integer(), nullable=True),
        sa.Column('statut_action', sa.String(length=20), nullable=True),
        sa.Column('date_cloture', sa.DateTime(timezone=True), nullable=True),
        sa.Column('fichiers_joints', sa.Text(), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('CURRENT_TIMESTAMP'), nullable=True),
        sa.ForeignKeyConstraint(['incident_id'], ['incidents.id'], ),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('reference')
    )

    op.create_table(
        'procedures_securite',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('code', sa.String(length=50), nullable=False),
        sa.Column('titre', sa.String(length=200), nullable=False),
        sa.Column('categorie', sa.String(length=50), nullable=True),
        sa.Column('version', sa.String(length=20), nullable=True),
        sa.Column('date_creation', sa.DateTime(timezone=True), nullable=True),
        sa.Column('date_revision', sa.DateTime(timezone=True), nullable=True),
        sa.Column('date_approbation', sa.DateTime(timezone=True), nullable=True),
        sa.Column('auteur', sa.Integer(), nullable=True),
        sa.Column('approbateur', sa.Integer(), nullable=True),
        sa.Column('contenu', sa.Text(), nullable=True),
        sa.Column('risques_identifies', sa.Text(), nullable=True),
        sa.Column('mesures_prevention', sa.Text(), nullable=True),
        sa.Column('equipement_protection', sa.Text(), nullable=True),
        sa.Column('formations_requises', sa.Text(), nullable=True),
        sa.Column('frequence_revision', sa.String(length=50), nullable=True),
        sa.Column('est_active', sa.Boolean(), nullable=True),
        sa.Column('fichiers_joints', sa.Text(), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('CURRENT_TIMESTAMP'), nullable=True),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=True),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('code')
    )


def downgrade():
    op.drop_table('procedures_securite')
    op.drop_table('rapports_qhse')
    op.drop_table('declarations_douanieres')
    op.drop_table('operations_acconage')
    op.drop_table('ecritures_comptables')
    op.drop_table('comptes')
    op.drop_table('paiements')
    op.drop_table('lignes_factures')
    op.drop_table('entrepots')
    op.drop_table('mouvements_stocks')
    op.drop_table('pieces_rechange')
    op.drop_table('interventions')
    op.drop_table('equipements')
    op.drop_table('vehicules')