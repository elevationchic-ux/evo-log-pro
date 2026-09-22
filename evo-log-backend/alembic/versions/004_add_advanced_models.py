"""Add advanced RH, warehouse, and transport models

Revision ID: 004_add_advanced_models
Revises: 003_add_remaining_models
Create Date: 2024-01-01

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = '004_add_advanced_models'
down_revision = '003_add_remaining_models'
branch_labels = None
depends_on = None


def upgrade():
    # ============ RH MODELS ============
    op.create_table(
        'conges',
        sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
        sa.Column('employe_id', sa.Integer(), nullable=False),
        sa.Column('type_conge', sa.String(), nullable=False),
        sa.Column('date_debut', sa.Date(), nullable=False),
        sa.Column('date_fin', sa.Date(), nullable=False),
        sa.Column('nombre_jours', sa.Integer(), nullable=False),
        sa.Column('motif', sa.String(), nullable=False),
        sa.Column('statut', sa.String(), nullable=False),
        sa.Column('date_demande', sa.DateTime(), nullable=False),
        sa.Column('approbateur_id', sa.Integer(), nullable=True),
        sa.Column('date_approbation', sa.DateTime(), nullable=True),
        sa.Column('commentaire_approbation', sa.String(), nullable=True),
        sa.Column('motif_refus', sa.String(), nullable=True),
        sa.ForeignKeyConstraint(['employe_id'], ['users.id'], ),
        sa.ForeignKeyConstraint(['approbateur_id'], ['users.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    
    op.create_table(
        'absences',
        sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
        sa.Column('employe_id', sa.Integer(), nullable=False),
        sa.Column('type_absence', sa.String(), nullable=False),
        sa.Column('date_debut', sa.Date(), nullable=False),
        sa.Column('date_fin', sa.Date(), nullable=False),
        sa.Column('nombre_jours', sa.Integer(), nullable=False),
        sa.Column('motif', sa.String(), nullable=False),
        sa.Column('justifie', sa.Boolean(), nullable=False),
        sa.Column('date_enregistrement', sa.DateTime(), nullable=False),
        sa.ForeignKeyConstraint(['employe_id'], ['users.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    
    op.create_table(
        'temps_travail',
        sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
        sa.Column('employe_id', sa.Integer(), nullable=False),
        sa.Column('date', sa.Date(), nullable=False),
        sa.Column('heure_arrivee', sa.DateTime(), nullable=False),
        sa.Column('heure_depart', sa.DateTime(), nullable=True),
        sa.Column('heures_travaillees', sa.Float(), nullable=True),
        sa.Column('heures_sup', sa.Float(), nullable=True),
        sa.Column('statut', sa.String(), nullable=False),
        sa.ForeignKeyConstraint(['employe_id'], ['users.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    
    op.create_table(
        'formations',
        sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
        sa.Column('titre', sa.String(), nullable=False),
        sa.Column('description', sa.String(), nullable=False),
        sa.Column('date_debut', sa.Date(), nullable=False),
        sa.Column('date_fin', sa.Date(), nullable=False),
        sa.Column('duree_heures', sa.Integer(), nullable=False),
        sa.Column('cout', sa.Float(), nullable=False),
        sa.Column('formateur', sa.String(), nullable=False),
        sa.Column('lieu', sa.String(), nullable=False),
        sa.Column('agency_id', sa.Integer(), nullable=True),
        sa.Column('statut', sa.String(), nullable=False),
        sa.Column('certificat_valide_jusque', sa.Date(), nullable=True),
        sa.ForeignKeyConstraint(['agency_id'], ['agencies.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    
    op.create_table(
        'participations_formation',
        sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
        sa.Column('formation_id', sa.Integer(), nullable=False),
        sa.Column('employe_id', sa.Integer(), nullable=False),
        sa.Column('date_inscription', sa.DateTime(), nullable=False),
        sa.Column('present', sa.Boolean(), nullable=True),
        sa.Column('certificat_obtenu', sa.Boolean(), nullable=True),
        sa.Column('commentaire', sa.String(), nullable=True),
        sa.Column('statut', sa.String(), nullable=False),
        sa.ForeignKeyConstraint(['formation_id'], ['formations.id'], ),
        sa.ForeignKeyConstraint(['employe_id'], ['users.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    
    op.create_table(
        'evaluations_performance',
        sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
        sa.Column('employe_id', sa.Integer(), nullable=False),
        sa.Column('evaluateur_id', sa.Integer(), nullable=False),
        sa.Column('periode_debut', sa.Date(), nullable=False),
        sa.Column('periode_fin', sa.Date(), nullable=False),
        sa.Column('note_globale', sa.Float(), nullable=False),
        sa.Column('commentaires', sa.String(), nullable=False),
        sa.Column('objectifs_atteints', sa.Integer(), nullable=False),
        sa.Column('objectifs_total', sa.Integer(), nullable=False),
        sa.Column('date_evaluation', sa.DateTime(), nullable=False),
        sa.ForeignKeyConstraint(['employe_id'], ['users.id'], ),
        sa.ForeignKeyConstraint(['evaluateur_id'], ['users.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    
    op.create_table(
        'contrats_travail',
        sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
        sa.Column('employe_id', sa.Integer(), nullable=False),
        sa.Column('type_contrat', sa.String(), nullable=False),
        sa.Column('date_debut', sa.Date(), nullable=False),
        sa.Column('date_fin', sa.Date(), nullable=True),
        sa.Column('poste', sa.String(), nullable=False),
        sa.Column('salaire_base', sa.Float(), nullable=False),
        sa.Column('coefficient', sa.Integer(), nullable=True),
        sa.Column('classification', sa.String(), nullable=True),
        sa.Column('periode_essai_jours', sa.Integer(), nullable=False),
        sa.Column('statut', sa.String(), nullable=False),
        sa.Column('nombre_renouvellements', sa.Integer(), nullable=True),
        sa.Column('date_dernier_renouvellement', sa.DateTime(), nullable=True),
        sa.ForeignKeyConstraint(['employe_id'], ['users.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    
    op.create_table(
        'salaires',
        sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
        sa.Column('employe_id', sa.Integer(), nullable=False),
        sa.Column('mois', sa.Integer(), nullable=False),
        sa.Column('annee', sa.Integer(), nullable=False),
        sa.Column('salaire_brut', sa.Float(), nullable=False),
        sa.Column('salaire_net', sa.Float(), nullable=False),
        sa.Column('heures_sup', sa.Float(), nullable=False),
        sa.Column('primes', sa.Float(), nullable=False),
        sa.Column('deductions', sa.Float(), nullable=False),
        sa.Column('date_paiement', sa.DateTime(), nullable=True),
        sa.ForeignKeyConstraint(['employe_id'], ['users.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    
    op.create_table(
        'primes',
        sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
        sa.Column('employe_id', sa.Integer(), nullable=False),
        sa.Column('type_prime', sa.String(), nullable=False),
        sa.Column('montant', sa.Float(), nullable=False),
        sa.Column('motif', sa.String(), nullable=False),
        sa.Column('date_prime', sa.Date(), nullable=False),
        sa.ForeignKeyConstraint(['employe_id'], ['users.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    
    op.create_table(
        'documents_employe',
        sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
        sa.Column('employe_id', sa.Integer(), nullable=False),
        sa.Column('type_document', sa.String(), nullable=False),
        sa.Column('chemin_fichier', sa.String(), nullable=False),
        sa.Column('date_emission', sa.Date(), nullable=True),
        sa.Column('date_expiration', sa.Date(), nullable=True),
        sa.Column('date_ajout', sa.DateTime(), nullable=False),
        sa.ForeignKeyConstraint(['employe_id'], ['users.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    
    op.create_table(
        'organigramme',
        sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
        sa.Column('employe_id', sa.Integer(), nullable=False),
        sa.Column('manager_id', sa.Integer(), nullable=True),
        sa.Column('departement', sa.String(), nullable=False),
        sa.Column('poste', sa.String(), nullable=False),
        sa.Column('date_creation', sa.DateTime(), nullable=True),
        sa.Column('date_mise_a_jour', sa.DateTime(), nullable=True),
        sa.ForeignKeyConstraint(['employe_id'], ['users.id'], ),
        sa.ForeignKeyConstraint(['manager_id'], ['users.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    
    op.create_table(
        'competences',
        sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
        sa.Column('nom', sa.String(), nullable=False),
        sa.Column('categorie', sa.String(), nullable=False),
        sa.Column('description', sa.String(), nullable=False),
        sa.Column('niveau_requis', sa.String(), nullable=False),
        sa.PrimaryKeyConstraint('id')
    )
    
    op.create_table(
        'competences_employe',
        sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
        sa.Column('employe_id', sa.Integer(), nullable=False),
        sa.Column('competence_id', sa.Integer(), nullable=False),
        sa.Column('niveau', sa.String(), nullable=False),
        sa.Column('date_evaluation', sa.Date(), nullable=True),
        sa.ForeignKeyConstraint(['employe_id'], ['users.id'], ),
        sa.ForeignKeyConstraint(['competence_id'], ['competences.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    
    # ============ MAGASIN AVANCE MODELS ============
    op.create_table(
        'peremptions',
        sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
        sa.Column('stock_id', sa.Integer(), nullable=False),
        sa.Column('date_peremption', sa.Date(), nullable=False),
        sa.Column('lot_numero', sa.String(), nullable=False),
        sa.Column('numero_serie', sa.String(), nullable=True),
        sa.ForeignKeyConstraint(['stock_id'], ['stocks.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    
    op.create_table(
        'reservations_stock',
        sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
        sa.Column('stock_id', sa.Integer(), nullable=False),
        sa.Column('type_reservation', sa.String(), nullable=False),
        sa.Column('reference_id', sa.Integer(), nullable=False),
        sa.Column('quantite', sa.Float(), nullable=False),
        sa.Column('date_reservation', sa.DateTime(), nullable=False),
        sa.Column('date_expiration', sa.Date(), nullable=True),
        sa.Column('statut', sa.String(), nullable=False),
        sa.Column('date_liberation', sa.DateTime(), nullable=True),
        sa.Column('date_consommation', sa.DateTime(), nullable=True),
        sa.ForeignKeyConstraint(['stock_id'], ['stocks.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    
    op.create_table(
        'kits_article',
        sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
        sa.Column('article_kit_id', sa.Integer(), nullable=False),
        sa.Column('nom_kit', sa.String(), nullable=False),
        sa.Column('description', sa.String(), nullable=False),
        sa.PrimaryKeyConstraint('id')
    )
    
    op.create_table(
        'composants_kit',
        sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
        sa.Column('kit_id', sa.Integer(), nullable=False),
        sa.Column('article_composant_id', sa.Integer(), nullable=False),
        sa.Column('quantite', sa.Float(), nullable=False),
        sa.ForeignKeyConstraint(['kit_id'], ['kits_article.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    
    op.create_table(
        'emplacements_detail',
        sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
        sa.Column('entrepot_id', sa.Integer(), nullable=False),
        sa.Column('zone', sa.String(), nullable=False),
        sa.Column('allee', sa.String(), nullable=False),
        sa.Column('rack', sa.String(), nullable=True),
        sa.Column('casier', sa.String(), nullable=True),
        sa.Column('niveau', sa.String(), nullable=True),
        sa.ForeignKeyConstraint(['entrepot_id'], ['entrepots.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    
    op.create_table(
        'transferts_stock',
        sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
        sa.Column('stock_id', sa.Integer(), nullable=False),
        sa.Column('entrepot_source_id', sa.Integer(), nullable=False),
        sa.Column('entrepot_destination_id', sa.Integer(), nullable=False),
        sa.Column('quantite', sa.Float(), nullable=False),
        sa.Column('motif', sa.String(), nullable=False),
        sa.Column('date_transfert', sa.Date(), nullable=False),
        sa.Column('statut', sa.String(), nullable=False),
        sa.Column('date_execution', sa.DateTime(), nullable=True),
        sa.ForeignKeyConstraint(['stock_id'], ['stocks.id'], ),
        sa.ForeignKeyConstraint(['entrepot_source_id'], ['entrepots.id'], ),
        sa.ForeignKeyConstraint(['entrepot_destination_id'], ['entrepots.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    
    op.create_table(
        'inventaires_tournants',
        sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
        sa.Column('entrepot_id', sa.Integer(), nullable=False),
        sa.Column('date_inventaire', sa.Date(), nullable=False),
        sa.Column('type_inventaire', sa.String(), nullable=False),
        sa.Column('statut', sa.String(), nullable=False),
        sa.Column('validateur_id', sa.Integer(), nullable=True),
        sa.Column('date_validation', sa.DateTime(), nullable=True),
        sa.ForeignKeyConstraint(['entrepot_id'], ['entrepots.id'], ),
        sa.ForeignKeyConstraint(['validateur_id'], ['users.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    
    op.create_table(
        'lignes_inventaire',
        sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
        sa.Column('inventaire_id', sa.Integer(), nullable=False),
        sa.Column('stock_id', sa.Integer(), nullable=False),
        sa.Column('quantite_theorique', sa.Float(), nullable=False),
        sa.Column('quantite_comptee', sa.Float(), nullable=False),
        sa.Column('ecart', sa.Float(), nullable=False),
        sa.Column('compteur_id', sa.Integer(), nullable=False),
        sa.Column('date_comptage', sa.DateTime(), nullable=False),
        sa.ForeignKeyConstraint(['inventaire_id'], ['inventaires_tournants.id'], ),
        sa.ForeignKeyConstraint(['stock_id'], ['stocks.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    
    op.create_table(
        'fournisseurs_stock',
        sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
        sa.Column('fournisseur_id', sa.Integer(), nullable=False),
        sa.Column('delai_livraison_jours', sa.Integer(), nullable=False),
        sa.Column('qualite', sa.String(), nullable=False),
        sa.Column('fiabilite', sa.Float(), nullable=False),
        sa.ForeignKeyConstraint(['fournisseur_id'], ['tiers.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    
    op.create_table(
        'commandes_fournisseur',
        sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
        sa.Column('fournisseur_id', sa.Integer(), nullable=False),
        sa.Column('reference', sa.String(), nullable=False),
        sa.Column('date_commande', sa.Date(), nullable=False),
        sa.Column('date_prevue', sa.Date(), nullable=False),
        sa.Column('date_livraison', sa.Date(), nullable=True),
        sa.Column('statut', sa.String(), nullable=False),
        sa.ForeignKeyConstraint(['fournisseur_id'], ['tiers.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    
    op.create_table(
        'lignes_commande_fournisseur',
        sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
        sa.Column('commande_id', sa.Integer(), nullable=False),
        sa.Column('article_id', sa.Integer(), nullable=False),
        sa.Column('quantite_commandee', sa.Float(), nullable=False),
        sa.Column('quantite_recue', sa.Float(), nullable=True),
        sa.Column('prix_unitaire', sa.Float(), nullable=False),
        sa.ForeignKeyConstraint(['commande_id'], ['commandes_fournisseur.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    
    op.create_table(
        'bons_reception',
        sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
        sa.Column('commande_id', sa.Integer(), nullable=False),
        sa.Column('fournisseur_id', sa.Integer(), nullable=False),
        sa.Column('date_reception', sa.Date(), nullable=False),
        sa.Column('statut', sa.String(), nullable=False),
        sa.Column('date_validation', sa.DateTime(), nullable=True),
        sa.ForeignKeyConstraint(['commande_id'], ['commandes_fournisseur.id'], ),
        sa.ForeignKeyConstraint(['fournisseur_id'], ['tiers.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    
    op.create_table(
        'lignes_bon_reception',
        sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
        sa.Column('bon_id', sa.Integer(), nullable=False),
        sa.Column('article_id', sa.Integer(), nullable=False),
        sa.Column('quantite_recue', sa.Float(), nullable=False),
        sa.Column('quantite_commandee', sa.Float(), nullable=False),
        sa.Column('emplacement_id', sa.Integer(), nullable=True),
        sa.ForeignKeyConstraint(['bon_id'], ['bons_reception.id'], ),
        sa.ForeignKeyConstraint(['emplacement_id'], ['emplacements_detail.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    
    op.create_table(
        'bons_sortie',
        sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
        sa.Column('destinataire_id', sa.Integer(), nullable=False),
        sa.Column('type_sortie', sa.String(), nullable=False),
        sa.Column('date_sortie', sa.Date(), nullable=False),
        sa.Column('statut', sa.String(), nullable=False),
        sa.Column('date_validation', sa.DateTime(), nullable=True),
        sa.ForeignKeyConstraint(['destinataire_id'], ['tiers.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    
    op.create_table(
        'lignes_bon_sortie',
        sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
        sa.Column('bon_id', sa.Integer(), nullable=False),
        sa.Column('stock_id', sa.Integer(), nullable=False),
        sa.Column('quantite', sa.Float(), nullable=False),
        sa.ForeignKeyConstraint(['bon_id'], ['bons_sortie.id'], ),
        sa.ForeignKeyConstraint(['stock_id'], ['stocks.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    
    op.create_table(
        'retours_client',
        sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
        sa.Column('client_id', sa.Integer(), nullable=False),
        sa.Column('article_id', sa.Integer(), nullable=False),
        sa.Column('quantite', sa.Float(), nullable=False),
        sa.Column('motif', sa.String(), nullable=False),
        sa.Column('etat', sa.String(), nullable=False),
        sa.Column('date_retour', sa.DateTime(), nullable=False),
        sa.Column('action_effectuee', sa.String(), nullable=True),
        sa.Column('date_traitement', sa.DateTime(), nullable=True),
        sa.Column('statut', sa.String(), nullable=False),
        sa.ForeignKeyConstraint(['client_id'], ['tiers.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    
    op.create_table(
        'litiges_transporteur',
        sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
        sa.Column('transporteur_id', sa.Integer(), nullable=False),
        sa.Column('type_litige', sa.String(), nullable=False),
        sa.Column('description', sa.String(), nullable=False),
        sa.Column('montant_reclame', sa.Float(), nullable=True),
        sa.Column('date_litige', sa.DateTime(), nullable=False),
        sa.Column('resolution', sa.String(), nullable=True),
        sa.Column('date_resolution', sa.DateTime(), nullable=True),
        sa.Column('statut', sa.String(), nullable=False),
        sa.ForeignKeyConstraint(['transporteur_id'], ['tiers.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    
    op.create_table(
        'colis',
        sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
        sa.Column('reference_colis', sa.String(), nullable=False),
        sa.Column('poids', sa.Float(), nullable=False),
        sa.Column('dimensions', sa.String(), nullable=False),
        sa.Column('contenu', sa.String(), nullable=False),
        sa.Column('code_barres', sa.String(), nullable=True),
        sa.Column('palette_id', sa.String(), nullable=True),
        sa.Column('date_creation', sa.DateTime(), nullable=False),
        sa.Column('date_etiquetage', sa.DateTime(), nullable=True),
        sa.Column('date_palettisation', sa.DateTime(), nullable=True),
        sa.PrimaryKeyConstraint('id')
    )
    
    # ============ TRANSPORT AVANCE MODELS ============
    op.create_table(
        'tournees',
        sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
        sa.Column('vehicule_id', sa.Integer(), nullable=False),
        sa.Column('conducteur_id', sa.Integer(), nullable=False),
        sa.Column('date_tournee', sa.Date(), nullable=False),
        sa.Column('origine', sa.String(), nullable=False),
        sa.Column('destination', sa.String(), nullable=False),
        sa.Column('statut', sa.String(), nullable=False),
        sa.Column('distance_estimee_km', sa.Float(), nullable=True),
        sa.Column('duree_estimee_heures', sa.Float(), nullable=True),
        sa.Column('heure_depart', sa.DateTime(), nullable=True),
        sa.Column('heure_arrivee', sa.DateTime(), nullable=True),
        sa.Column('duree_reelle_heures', sa.Float(), nullable=True),
        sa.ForeignKeyConstraint(['vehicule_id'], ['vehicules.id'], ),
        sa.ForeignKeyConstraint(['conducteur_id'], ['conducteurs.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    
    op.create_table(
        'livraisons',
        sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
        sa.Column('tournee_id', sa.Integer(), nullable=False),
        sa.Column('client_id', sa.Integer(), nullable=False),
        sa.Column('adresse', sa.String(), nullable=False),
        sa.Column('ordre_arret', sa.Integer(), nullable=False),
        sa.Column('fenetre_horaire_debut', sa.DateTime(), nullable=False),
        sa.Column('fenetre_horaire_fin', sa.DateTime(), nullable=False),
        sa.Column('statut', sa.String(), nullable=False),
        sa.Column('date_livraison_reelle', sa.DateTime(), nullable=True),
        sa.Column('signature', sa.String(), nullable=True),
        sa.Column('photo_preuve', sa.String(), nullable=True),
        sa.ForeignKeyConstraint(['tournee_id'], ['tournees.id'], ),
        sa.ForeignKeyConstraint(['client_id'], ['tiers.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    
    op.create_table(
        'frais_kilometriques',
        sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
        sa.Column('vehicule_id', sa.Integer(), nullable=False),
        sa.Column('date_debut', sa.Date(), nullable=False),
        sa.Column('date_fin', sa.Date(), nullable=False),
        sa.Column('kilometres_parcourus', sa.Float(), nullable=False),
        sa.Column('taux_remboursement', sa.Float(), nullable=False),
        sa.Column('montant', sa.Float(), nullable=False),
        sa.ForeignKeyConstraint(['vehicule_id'], ['vehicules.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    
    op.create_table(
        'temps_conduite',
        sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
        sa.Column('conducteur_id', sa.Integer(), nullable=False),
        sa.Column('vehicule_id', sa.Integer(), nullable=False),
        sa.Column('debut_conduite', sa.DateTime(), nullable=False),
        sa.Column('fin_conduite', sa.DateTime(), nullable=False),
        sa.Column('duree_heures', sa.Float(), nullable=False),
        sa.Column('kilometres', sa.Float(), nullable=False),
        sa.ForeignKeyConstraint(['conducteur_id'], ['conducteurs.id'], ),
        sa.ForeignKeyConstraint(['vehicule_id'], ['vehicules.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    
    op.create_table(
        'sous_traitants',
        sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
        sa.Column('nom', sa.String(), nullable=False),
        sa.Column('siret', sa.String(), nullable=False),
        sa.Column('adresse', sa.String(), nullable=False),
        sa.Column('telephone', sa.String(), nullable=False),
        sa.Column('email', sa.String(), nullable=False),
        sa.Column('specialites', sa.String(), nullable=False),
        sa.Column('statut', sa.String(), nullable=False),
        sa.PrimaryKeyConstraint('id')
    )
    
    op.create_table(
        'contrats_sous_traitant',
        sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
        sa.Column('sous_traitant_id', sa.Integer(), nullable=False),
        sa.Column('date_debut', sa.Date(), nullable=False),
        sa.Column('date_fin', sa.Date(), nullable=False),
        sa.Column('tarif_km', sa.Float(), nullable=False),
        sa.Column('tarif_fixe', sa.Float(), nullable=False),
        sa.Column('conditions', sa.String(), nullable=False),
        sa.Column('statut', sa.String(), nullable=False),
        sa.ForeignKeyConstraint(['sous_traitant_id'], ['sous_traitants.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    
    op.create_table(
        'missions_sous_traitant',
        sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
        sa.Column('contrat_id', sa.Integer(), nullable=False),
        sa.Column('mission_id', sa.Integer(), nullable=False),
        sa.Column('kilometrage_estime', sa.Float(), nullable=False),
        sa.Column('kilometrage_reel', sa.Float(), nullable=True),
        sa.Column('date_livraison_prevue', sa.Date(), nullable=True),
        sa.Column('date_livraison_reelle', sa.Date(), nullable=True),
        sa.Column('date_creation', sa.DateTime(), nullable=False),
        sa.Column('statut', sa.String(), nullable=False),
        sa.ForeignKeyConstraint(['contrat_id'], ['contrats_sous_traitant.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    
    op.create_table(
        'accidents_transport',
        sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
        sa.Column('vehicule_id', sa.Integer(), nullable=False),
        sa.Column('conducteur_id', sa.Integer(), nullable=False),
        sa.Column('date_accident', sa.DateTime(), nullable=False),
        sa.Column('lieu', sa.String(), nullable=False),
        sa.Column('description', sa.String(), nullable=False),
        sa.Column('degats_materiels', sa.String(), nullable=False),
        sa.Column('blessures', sa.String(), nullable=False),
        sa.Column('temoins', sa.String(), nullable=True),
        sa.Column('enqueteur_id', sa.Integer(), nullable=True),
        sa.Column('rapport_enquete', sa.String(), nullable=True),
        sa.Column('conclusions', sa.String(), nullable=True),
        sa.Column('actions_correctives', sa.String(), nullable=True),
        sa.Column('date_enquete', sa.DateTime(), nullable=True),
        sa.Column('statut', sa.String(), nullable=False),
        sa.ForeignKeyConstraint(['vehicule_id'], ['vehicules.id'], ),
        sa.ForeignKeyConstraint(['conducteur_id'], ['conducteurs.id'], ),
        sa.ForeignKeyConstraint(['enqueteur_id'], ['users.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    
    op.create_table(
        'maintenance_preventive',
        sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
        sa.Column('vehicule_id', sa.Integer(), nullable=False),
        sa.Column('type_maintenance', sa.String(), nullable=False),
        sa.Column('date_prevue', sa.Date(), nullable=False),
        sa.Column('kilometrage_prevu', sa.Integer(), nullable=False),
        sa.Column('description', sa.String(), nullable=False),
        sa.Column('date_execution', sa.Date(), nullable=True),
        sa.Column('kilometrage_reel', sa.Integer(), nullable=True),
        sa.Column('cout', sa.Float(), nullable=True),
        sa.Column('technicien', sa.String(), nullable=True),
        sa.Column('observations', sa.String(), nullable=True),
        sa.Column('statut', sa.String(), nullable=False),
        sa.ForeignKeyConstraint(['vehicule_id'], ['vehicules.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    
    op.create_table(
        'positions_gps',
        sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
        sa.Column('vehicule_id', sa.Integer(), nullable=False),
        sa.Column('latitude', sa.Float(), nullable=False),
        sa.Column('longitude', sa.Float(), nullable=False),
        sa.Column('vitesse', sa.Float(), nullable=False),
        sa.Column('direction', sa.Float(), nullable=False),
        sa.Column('horodatage', sa.DateTime(), nullable=False),
        sa.ForeignKeyConstraint(['vehicule_id'], ['vehicules.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    
    op.create_table(
        'zones_geofencing',
        sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
        sa.Column('nom_zone', sa.String(), nullable=False),
        sa.Column('type_zone', sa.String(), nullable=False),
        sa.Column('latitude_centre', sa.Float(), nullable=False),
        sa.Column('longitude_centre', sa.Float(), nullable=False),
        sa.Column('rayon_metres', sa.Float(), nullable=False),
        sa.Column('statut', sa.String(), nullable=False),
        sa.PrimaryKeyConstraint('id')
    )
    
    op.create_table(
        'evenements_vehicule',
        sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
        sa.Column('vehicule_id', sa.Integer(), nullable=False),
        sa.Column('type_evenement', sa.String(), nullable=False),
        sa.Column('description', sa.String(), nullable=False),
        sa.Column('latitude', sa.Float(), nullable=True),
        sa.Column('longitude', sa.Float(), nullable=True),
        sa.Column('date_evenement', sa.DateTime(), nullable=False),
        sa.ForeignKeyConstraint(['vehicule_id'], ['vehicules.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    
    # Add index for performance
    op.create_index('idx_peremptions_date', 'peremptions', ['date_peremption'])
    op.create_index('idx_reservations_statut', 'reservations_stock', ['statut'])
    op.create_index('idx_positions_gps_vehicule', 'positions_gps', ['vehicule_id', 'horodatage'])
    op.create_index('idx_conges_employe', 'conges', ['employe_id', 'date_debut'])
    op.create_index('idx_absences_employe', 'absences', ['employe_id', 'date_debut'])


def downgrade():
    # Drop indexes
    op.drop_index('idx_absences_employe', table_name='absences')
    op.drop_index('idx_conges_employe', table_name='conges')
    op.drop_index('idx_positions_gps_vehicule', table_name='positions_gps')
    op.drop_index('idx_reservations_statut', table_name='reservations_stock')
    op.drop_index('idx_peremptions_date', table_name='peremptions')
    
    # Drop transport avance tables
    op.drop_table('evenements_vehicule')
    op.drop_table('zones_geofencing')
    op.drop_table('positions_gps')
    op.drop_table('maintenance_preventive')
    op.drop_table('accidents_transport')
    op.drop_table('missions_sous_traitant')
    op.drop_table('contrats_sous_traitant')
    op.drop_table('sous_traitants')
    op.drop_table('temps_conduite')
    op.drop_table('frais_kilometriques')
    op.drop_table('livraisons')
    op.drop_table('tournees')
    
    # Drop magasin avance tables
    op.drop_table('colis')
    op.drop_table('litiges_transporteur')
    op.drop_table('retours_client')
    op.drop_table('lignes_bon_sortie')
    op.drop_table('bons_sortie')
    op.drop_table('lignes_bon_reception')
    op.drop_table('bons_reception')
    op.drop_table('lignes_commande_fournisseur')
    op.drop_table('commandes_fournisseur')
    op.drop_table('fournisseurs_stock')
    op.drop_table('lignes_inventaire')
    op.drop_table('inventaires_tournants')
    op.drop_table('transferts_stock')
    op.drop_table('emplacements_detail')
    op.drop_table('composants_kit')
    op.drop_table('kits_article')
    op.drop_table('reservations_stock')
    op.drop_table('peremptions')
    
    # Drop RH tables
    op.drop_table('competences_employe')
    op.drop_table('competences')
    op.drop_table('organigramme')
    op.drop_table('documents_employe')
    op.drop_table('primes')
    op.drop_table('salaires')
    op.drop_table('contrats_travail')
    op.drop_table('evaluations_performance')
    op.drop_table('participations_formation')
    op.drop_table('formations')
    op.drop_table('temps_travail')
    op.drop_table('absences')
    op.drop_table('conges')
