"""add_comptabilite_avance_complete

Revision ID: 008_add_comptabilite_avance_complete
Revises: 007_add_cameroun_cemac
Create Date: 2026-01-18

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy import Integer, String, Text, DateTime, Boolean, Float, ForeignKey, Enum, Date, Numeric
from sqlalchemy.sql import func


# revision identifiers, used by Alembic.
revision = '008_add_comptabilite_avance_complete'
down_revision = '008_add_cameroun_cemac_phase2'
branch_labels = None
depends_on = None


def upgrade():
    # ============ JOURNAUX AUXILIAIRES ============
    op.create_table(
        'journaux_auxiliaires',
        sa.Column('id', Integer, primary_key=True, index=True),
        sa.Column('code_journal', String(10), unique=True, nullable=False, index=True),
        sa.Column('nom_journal', String(100), nullable=False),
        sa.Column('type_journal', String(50), nullable=False),
        sa.Column('description', Text),
        sa.Column('compte_centralisateur', String(20)),
        sa.Column('periodical', Boolean, default=True),
        sa.Column('statut', String(20), default='actif'),
        sa.Column('devise', String(3), default='XAF'),
        sa.Column('created_at', DateTime(timezone=True), server_default=func.now()),
        sa.Column('updated_at', DateTime(timezone=True), onupdate=func.now())
    )
    
    op.create_table(
        'lignes_journal',
        sa.Column('id', Integer, primary_key=True, index=True),
        sa.Column('ecriture_id', Integer, ForeignKey('ecritures_comptables_ohada.id'), nullable=False),
        sa.Column('journal_id', Integer, ForeignKey('journaux_auxiliaires.id'), nullable=False),
        sa.Column('compte_id', Integer, ForeignKey('plan_comptable_ohada.id'), nullable=False),
        sa.Column('compte_numero', String(20)),
        sa.Column('compte_intitule', String(200)),
        sa.Column('debit', Numeric(15, 2), default=0),
        sa.Column('credit', Numeric(15, 2), default=0),
        sa.Column('devise', String(3), default='XAF'),
        sa.Column('reference_document', String(100)),
        sa.Column('libelle_detail', String(500)),
        sa.Column('order_line', Integer, default=0),
        sa.Column('created_at', DateTime(timezone=True), server_default=func.now())
    )
    
    # ============ LETTRAGE ============
    op.create_table(
        'lettrages',
        sa.Column('id', Integer, primary_key=True, index=True),
        sa.Column('compte_id', Integer, ForeignKey('plan_comptable_ohada.id'), nullable=False),
        sa.Column('numero_lettrage', String(50), unique=True, nullable=False, index=True),
        sa.Column('type_lettrage', String(50)),
        sa.Column('date_lettrage', Date, nullable=False),
        sa.Column('montant_lettre', Numeric(15, 2), nullable=False),
        sa.Column('devise', String(3), default='XAF'),
        sa.Column('reference_lettrage', String(100)),
        sa.Column('notes', Text),
        sa.Column('effectue_par', String(100)),
        sa.Column('date_annulation', Date),
        sa.Column('motif_annulation', Text),
        sa.Column('created_at', DateTime(timezone=True), server_default=func.now()),
        sa.Column('updated_at', DateTime(timezone=True), onupdate=func.now())
    )
    
    op.create_table(
        'ecritures_lettrees',
        sa.Column('id', Integer, primary_key=True, index=True),
        sa.Column('lettrage_id', Integer, ForeignKey('lettrages.id'), nullable=False),
        sa.Column('ecriture_id', Integer, ForeignKey('ecritures_comptables_ohada.id'), nullable=False),
        sa.Column('montant_lettre', Numeric(15, 2), nullable=False),
        sa.Column('devise', String(3), default='XAF'),
        sa.Column('created_at', DateTime(timezone=True), server_default=func.now())
    )
    
    # ============ GRAND LIVRE ============
    op.create_table(
        'grand_livre_lignes',
        sa.Column('id', Integer, primary_key=True, index=True),
        sa.Column('compte_id', Integer, ForeignKey('plan_comptable_ohada.id'), nullable=False),
        sa.Column('ecriture_id', Integer, ForeignKey('ecritures_comptables_ohada.id'), nullable=False),
        sa.Column('date_ecriture', Date, nullable=False),
        sa.Column('libelle', String(500)),
        sa.Column('debit', Numeric(15, 2), default=0),
        sa.Column('credit', Numeric(15, 2), default=0),
        sa.Column('solde_debit', Numeric(15, 2), default=0),
        sa.Column('solde_credit', Numeric(15, 2), default=0),
        sa.Column('devise', String(3), default='XAF'),
        sa.Column('journal', String(50)),
        sa.Column('periode', String(50)),
        sa.Column('statut_lettrage', String(50)),
        sa.Column('lettrage_id', Integer, ForeignKey('lettrages.id')),
        sa.Column('created_at', DateTime(timezone=True), server_default=func.now())
    )
    
    # ============ BALANCE ============
    op.create_table(
        'balances_verification',
        sa.Column('id', Integer, primary_key=True, index=True),
        sa.Column('exercice_id', Integer, ForeignKey('exercices_comptables.id'), nullable=False),
        sa.Column('periode', String(50), nullable=False),
        sa.Column('date_balance', Date, nullable=False),
        sa.Column('total_debit', Numeric(15, 2), default=0),
        sa.Column('total_credit', Numeric(15, 2), default=0),
        sa.Column('ecart', Numeric(15, 2), default=0),
        sa.Column('statut', String(20), default='en_cours'),
        sa.Column('valide_par', String(100)),
        sa.Column('date_validation', Date),
        sa.Column('notes', Text),
        sa.Column('created_at', DateTime(timezone=True), server_default=func.now()),
        sa.Column('updated_at', DateTime(timezone=True), onupdate=func.now())
    )
    
    op.create_table(
        'lignes_balance',
        sa.Column('id', Integer, primary_key=True, index=True),
        sa.Column('balance_id', Integer, ForeignKey('balances_verification.id'), nullable=False),
        sa.Column('compte_id', Integer, ForeignKey('plan_comptable_ohada.id'), nullable=False),
        sa.Column('compte_numero', String(20)),
        sa.Column('compte_intitule', String(200)),
        sa.Column('total_debit', Numeric(15, 2), default=0),
        sa.Column('total_credit', Numeric(15, 2), default=0),
        sa.Column('solde_debit', Numeric(15, 2), default=0),
        sa.Column('solde_credit', Numeric(15, 2), default=0),
        sa.Column('devise', String(3), default='XAF'),
        sa.Column('created_at', DateTime(timezone=True), server_default=func.now())
    )
    
    # ============ ÉTATS FINANCIERS OHADA ============
    op.create_table(
        'bilans_ohada_detailles',
        sa.Column('id', Integer, primary_key=True, index=True),
        sa.Column('exercice_id', Integer, ForeignKey('exercices_comptables.id'), nullable=False),
        sa.Column('date_bilan', Date, nullable=False),
        sa.Column('actif_immobilise_brut', Numeric(15, 2), default=0),
        sa.Column('actif_immobilise_amortissements', Numeric(15, 2), default=0),
        sa.Column('actif_immobilise_net', Numeric(15, 2), default=0),
        sa.Column('actif_circulant_stocks', Numeric(15, 2), default=0),
        sa.Column('actif_circulant_creances', Numeric(15, 2), default=0),
        sa.Column('actif_circulant_total', Numeric(15, 2), default=0),
        sa.Column('tresorerie_actif', Numeric(15, 2), default=0),
        sa.Column('total_actif', Numeric(15, 2), default=0),
        sa.Column('capitaux_propres_capital', Numeric(15, 2), default=0),
        sa.Column('capitaux_propres_reserves', Numeric(15, 2), default=0),
        sa.Column('capitaux_propres_resultat', Numeric(15, 2), default=0),
        sa.Column('capitaux_propres_total', Numeric(15, 2), default=0),
        sa.Column('dettes_long_terme', Numeric(15, 2), default=0),
        sa.Column('dettes_courtes', Numeric(15, 2), default=0),
        sa.Column('total_passif', Numeric(15, 2), default=0),
        sa.Column('devise', String(3), default='XAF'),
        sa.Column('notes', Text),
        sa.Column('valide_par', String(100)),
        sa.Column('date_validation', Date),
        sa.Column('created_at', DateTime(timezone=True), server_default=func.now()),
        sa.Column('updated_at', DateTime(timezone=True), onupdate=func.now())
    )
    
    op.create_table(
        'comptes_resultat_ohada_detailles',
        sa.Column('id', Integer, primary_key=True, index=True),
        sa.Column('exercice_id', Integer, ForeignKey('exercices_comptables.id'), nullable=False),
        sa.Column('periode', String(50), nullable=False),
        sa.Column('date_arrete', Date, nullable=False),
        sa.Column('ventes_marchandises', Numeric(15, 2), default=0),
        sa.Column('ventes_produits_fabriques', Numeric(15, 2), default=0),
        sa.Column('subventions_exploitation', Numeric(15, 2), default=0),
        sa.Column('autres_produits_exploitation', Numeric(15, 2), default=0),
        sa.Column('total_produits_exploitation', Numeric(15, 2), default=0),
        sa.Column('achats_marchandises', Numeric(15, 2), default=0),
        sa.Column('achats_matieres_premieres', Numeric(15, 2), default=0),
        sa.Column('services_exterieurs', Numeric(15, 2), default=0),
        sa.Column('charges_personnel', Numeric(15, 2), default=0),
        sa.Column('impots_taxes', Numeric(15, 2), default=0),
        sa.Column('dotations_amortissements', Numeric(15, 2), default=0),
        sa.Column('autres_charges_exploitation', Numeric(15, 2), default=0),
        sa.Column('total_charges_exploitation', Numeric(15, 2), default=0),
        sa.Column('resultat_exploitation', Numeric(15, 2), default=0),
        sa.Column('produits_financiers', Numeric(15, 2), default=0),
        sa.Column('charges_financieres', Numeric(15, 2), default=0),
        sa.Column('resultat_financier', Numeric(15, 2), default=0),
        sa.Column('produits_exceptionnels', Numeric(15, 2), default=0),
        sa.Column('charges_exceptionnelles', Numeric(15, 2), default=0),
        sa.Column('resultat_exceptionnel', Numeric(15, 2), default=0),
        sa.Column('resultat_net', Numeric(15, 2), default=0),
        sa.Column('devise', String(3), default='XAF'),
        sa.Column('notes', Text),
        sa.Column('valide_par', String(100)),
        sa.Column('date_validation', Date),
        sa.Column('created_at', DateTime(timezone=True), server_default=func.now()),
        sa.Column('updated_at', DateTime(timezone=True), onupdate=func.now())
    )
    
    op.create_table(
        'tafire',
        sa.Column('id', Integer, primary_key=True, index=True),
        sa.Column('exercice_id', Integer, ForeignKey('exercices_comptables.id'), nullable=False),
        sa.Column('date_tafire', Date, nullable=False),
        sa.Column('capacit_autofinancement', Numeric(15, 2), default=0),
        sa.Column('cession_immobilisations', Numeric(15, 2), default=0),
        sa.Column('augmentation_capital', Numeric(15, 2), default=0),
        sa.Column('nouveaux_emprunts', Numeric(15, 2), default=0),
        sa.Column('total_ressources', Numeric(15, 2), default=0),
        sa.Column('investissements_immobilisations', Numeric(15, 2), default=0),
        sa.Column('remboursement_emprunts', Numeric(15, 2), default=0),
        sa.Column('distribution_dividendes', Numeric(15, 2), default=0),
        sa.Column('augmentation_besoin_fdr', Numeric(15, 2), default=0),
        sa.Column('total_emplois', Numeric(15, 2), default=0),
        sa.Column('variation_tresorerie', Numeric(15, 2)),
        sa.Column('tresorerie_debut', Numeric(15, 2), default=0),
        sa.Column('tresorerie_fin', Numeric(15, 2), default=0),
        sa.Column('devise', String(3), default='XAF'),
        sa.Column('notes', Text),
        sa.Column('valide_par', String(100)),
        sa.Column('date_validation', Date),
        sa.Column('created_at', DateTime(timezone=True), server_default=func.now()),
        sa.Column('updated_at', DateTime(timezone=True), onupdate=func.now())
    )
    
    op.create_table(
        'annexes_ohada',
        sa.Column('id', Integer, primary_key=True, index=True),
        sa.Column('exercice_id', Integer, ForeignKey('exercices_comptables.id'), nullable=False),
        sa.Column('date_annexes', Date, nullable=False),
        sa.Column('denomination_sociale', String(200)),
        sa.Column('forme_juridique', String(100)),
        sa.Column('siege_social', String(200)),
        sa.Column('capital_social', Numeric(15, 2)),
        sa.Column('date_creation', Date),
        sa.Column('methode_evaluation_stocks', Text),
        sa.Column('methode_amortissements', Text),
        sa.Column('principes_comptables', Text),
        sa.Column('evenements_posterieurs', Text),
        sa.Column('engagements_hors_bilan', Text),
        sa.Column('notes_immobilisations', Text),
        sa.Column('notes_amortissements', Text),
        sa.Column('notes_provisions', Text),
        sa.Column('notes_dettes', Text),
        sa.Column('notes_engagements', Text),
        sa.Column('devise', String(3), default='XAF'),
        sa.Column('valide_par', String(100)),
        sa.Column('date_validation', Date),
        sa.Column('created_at', DateTime(timezone=True), server_default=func.now()),
        sa.Column('updated_at', DateTime(timezone=True), onupdate=func.now())
    )


def downgrade():
    # Drop tables in reverse order
    op.drop_table('annexes_ohada')
    op.drop_table('tafire')
    op.drop_table('comptes_resultat_ohada_detailles')
    op.drop_table('bilans_ohada_detailles')
    op.drop_table('lignes_balance')
    op.drop_table('balances_verification')
    op.drop_table('grand_livre_lignes')
    op.drop_table('ecritures_lettrees')
    op.drop_table('lettrages')
    op.drop_table('lignes_journal')
    op.drop_table('journaux_auxiliaires')
