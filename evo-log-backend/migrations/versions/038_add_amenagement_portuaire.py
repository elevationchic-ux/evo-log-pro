"""038 : departement Amenagement portuaire (Douala, Kribi, Limbe).

Le module tient le registre de la maitrise d'ouvrage du domaine portuaire,
aligne sur le circuit camerounais reel :

    schemas_directeurs_amgt      schemas / plans directeurs (APN, autorite portuaire)
    projets_amenagement          operations d'investissement programmees
    registres_dto_amgt           Documents Techniques Outil et visas du controle financier
    marches_amenagement          marches publics (COLIFE/CIP) et contrats PPP (loi 2023/008)
    autorisations_domaniales_amgt titres d'occupation du domaine portuaire
    concessions_amenagement      affermage, concession, BOT/CET, AOT
    infrastructures_amenagees    inventaire technique des ouvrages livres
    campagnes_dragage            dragages de construction et d'entretien
    autorisations_travaux_amgt   EIES, permis, visas administratifs (loi 96/012)

AUCUNE DONNEE N'EST INSEREE : ces tables decrivent le domaine public, dont le
contenu appartient aux documents officiels. Un champ NULL veut dire « non
renseigne », et la migration 039 ne seed que des droits RBAC.

Colonnes nomenclature : l'ORM declare des enums Python en VARCHAR (sans type
natif ni CHECK, voir app/models/amenagement_portuaire._enum) — le DDL est donc
identique sur SQLite et PostgreSQL, et cette migration reproduit exactement les
memes types.

Proprietes (conventions 024/027/029/030/031/032/037) :
    - IDEMPOTENT par introspection : table deja presente -> no-op.
    - contraintes FK nommees, mode batch SQLite.
    - ajoute aussi les deux colonnes reclamees par GET /api/v1/public/ports
      (autorite_portuaire, tirant_eau_max) qui manquaient dans ports_cameroun :
      colonnees NULL, aucune valeur n'est completee.
    - downgrade droppe les neuf tables et les deux colonnes.

Revision ID: 038_add_amenagement_portuaire
Revises: 037_add_customs_caution_register
Create Date: 2026-10-04
"""
from alembic import op
import sqlalchemy as sa


revision = "038_add_amenagement_portuaire"
down_revision = "037_add_customs_caution_register"
branch_labels = None
depends_on = None

# Ports du departement : colonnees mais JAMAIS remplies automatiquement.
T_PORTS = "ports_cameroun"
NEW_PORT_COLS = ("autorite_portuaire", "tirant_eau_max")

T_SCHEMADIRECTEUR = "schemas_directeurs_amgt"
T_PROJETAMENAGEMENT = "projets_amenagement"
T_REGISTREDTO = "registres_dto_amgt"
T_MARCHEAMENAGEMENT = "marches_amenagement"
T_AUTORISATIONDOMANIALE = "autorisations_domaniales_amgt"
T_CONCESSIONPORTUAIRE = "concessions_amenagement"
T_INFRASTRUCTUREPORTUAIRE = "infrastructures_amenagees"
T_DRAGAGE = "campagnes_dragage"
T_AUTORISATIONTRAVAUX = "autorisations_travaux_amgt"


def upgrade():
    bind = op.get_bind()
    insp = sa.inspect(bind)
    tables = set(insp.get_table_names())

    if T_SCHEMADIRECTEUR not in tables:
        op.create_table(
            T_SCHEMADIRECTEUR,
            sa.Column("id", sa.Integer(), primary_key=True),
            sa.Column("code", sa.String(40), nullable=False),
            sa.Column("libelle", sa.String(200), nullable=False),
            sa.Column("port_id", sa.Integer(), nullable=True),
            sa.Column("type_schema", sa.String(17), nullable=False),
            sa.Column("perimetre", sa.String(), nullable=True),
            sa.Column("horizon_debut", sa.Integer(), nullable=True),
            sa.Column("horizon_fin", sa.Integer(), nullable=True),
            sa.Column("statut", sa.String(12), nullable=False),
            sa.Column("autorite_elaboratrice", sa.String(160), nullable=True),
            sa.Column("reference_approbatrice", sa.String(120), nullable=True),
            sa.Column("date_approbation", sa.Date(), nullable=True),
            sa.Column("date_depot", sa.Date(), nullable=True),
            sa.Column("date_echeance_revision", sa.Date(), nullable=True),
            sa.Column("cout_elaboration_xaf", sa.Numeric(18, 2), nullable=True),
            sa.Column("budget_alloue_travaux_xaf", sa.Numeric(18, 2), nullable=True),
            sa.Column("superficie_totale_ha", sa.Numeric(14, 3), nullable=True),
            sa.Column("surface_eau_ha", sa.Numeric(14, 3), nullable=True),
            sa.Column("zones_prevues", sa.String(), nullable=True),
            sa.Column("lignes_directrices", sa.String(), nullable=True),
            sa.Column("documents_sources", sa.String(), nullable=True),
            sa.Column("source_reference", sa.String(200), nullable=True),
            sa.Column("date_verification", sa.Date(), nullable=True),
            sa.Column("auteur_saisie", sa.String(120), nullable=True),
            sa.Column("notes", sa.String(), nullable=True),
            sa.Column("est_actif", sa.Boolean(), nullable=False),
            sa.Column("created_at", sa.DateTime(timezone=True), nullable=True),
            sa.Column("updated_at", sa.DateTime(timezone=True), nullable=True),
            sa.ForeignKeyConstraint(["port_id"], ["ports_cameroun.id"], name="fk_schemas_directeurs_amgt_port_id_ports_cameroun"),
        )
        op.create_index("ix_schemas_directeurs_amgt_id", "schemas_directeurs_amgt", ["id"])
        op.create_index("ix_schemas_directeurs_amgt_code", "schemas_directeurs_amgt", ["code"], unique=True, unique=True)
        op.create_index("ix_schemas_directeurs_amgt_port_id", "schemas_directeurs_amgt", ["port_id"])
        op.create_index("ix_schemas_directeurs_amgt_statut", "schemas_directeurs_amgt", ["statut"])

    if T_PROJETAMENAGEMENT not in tables:
        op.create_table(
            T_PROJETAMENAGEMENT,
            sa.Column("id", sa.Integer(), primary_key=True),
            sa.Column("code_projet", sa.String(40), nullable=False),
            sa.Column("libelle", sa.String(200), nullable=False),
            sa.Column("description", sa.String(), nullable=True),
            sa.Column("port_id", sa.Integer(), nullable=True),
            sa.Column("terminal_id", sa.Integer(), nullable=True),
            sa.Column("schema_id", sa.Integer(), nullable=True),
            sa.Column("type_ouvrage", sa.String(21), nullable=False),
            sa.Column("statut", sa.String(15), nullable=False),
            sa.Column("priorite", sa.String(20), nullable=True),
            sa.Column("origines_financement", sa.String(), nullable=True),
            sa.Column("cout_previsionnel_xaf", sa.Numeric(18, 2), nullable=True),
            sa.Column("cout_reel_xaf", sa.Numeric(18, 2), nullable=True),
            sa.Column("devise", sa.String(6), nullable=True),
            sa.Column("financement_public_xaf", sa.Numeric(18, 2), nullable=True),
            sa.Column("financement_prive_xaf", sa.Numeric(18, 2), nullable=True),
            sa.Column("date_debut_prevue", sa.Date(), nullable=True),
            sa.Column("date_fin_prevue", sa.Date(), nullable=True),
            sa.Column("date_reelle_demarrage", sa.Date(), nullable=True),
            sa.Column("date_reelle_achevement", sa.Date(), nullable=True),
            sa.Column("avancement_physique_pct", sa.Numeric(5, 2), nullable=True),
            sa.Column("avancement_financier_pct", sa.Numeric(5, 2), nullable=True),
            sa.Column("maitre_ouvrage", sa.String(160), nullable=True),
            sa.Column("maitre_doeuvre", sa.String(160), nullable=True),
            sa.Column("bureau_controle", sa.String(160), nullable=True),
            sa.Column("entreprise_attributaire", sa.String(200), nullable=True),
            sa.Column("dto_reference", sa.String(120), nullable=True),
            sa.Column("date_notification_minepf", sa.Date(), nullable=True),
            sa.Column("eies_obligatoire", sa.Boolean(), nullable=True),
            sa.Column("superficie_impactee_ha", sa.Numeric(14, 3), nullable=True),
            sa.Column("capacite_additionnelle", sa.String(120), nullable=True),
            sa.Column("justificatif_utilite", sa.String(), nullable=True),
            sa.Column("risques", sa.String(), nullable=True),
            sa.Column("source_reference", sa.String(200), nullable=True),
            sa.Column("date_verification", sa.Date(), nullable=True),
            sa.Column("auteur_saisie", sa.String(120), nullable=True),
            sa.Column("notes", sa.String(), nullable=True),
            sa.Column("est_actif", sa.Boolean(), nullable=False),
            sa.Column("created_at", sa.DateTime(timezone=True), nullable=True),
            sa.Column("updated_at", sa.DateTime(timezone=True), nullable=True),
            sa.ForeignKeyConstraint(["port_id"], ["ports_cameroun.id"], name="fk_projets_amenagement_port_id_ports_cameroun"),
            sa.ForeignKeyConstraint(["terminal_id"], ["terminaux_portuaires.id"], name="fk_projets_amenagement_terminal_id_terminaux_portuaires"),
            sa.ForeignKeyConstraint(["schema_id"], ["schemas_directeurs_amgt.id"], name="fk_projets_amenagement_schema_id_schemas_directeurs_amgt"),
        )
        op.create_index("ix_projets_amenagement_id", "projets_amenagement", ["id"])
        op.create_index("ix_projets_amenagement_code_projet", "projets_amenagement", ["code_projet"], unique=True, unique=True)
        op.create_index("ix_projets_amenagement_port_id", "projets_amenagement", ["port_id"])
        op.create_index("ix_projets_amenagement_schema_id", "projets_amenagement", ["schema_id"])
        op.create_index("ix_projets_amenagement_type_ouvrage", "projets_amenagement", ["type_ouvrage"])
        op.create_index("ix_projets_amenagement_statut", "projets_amenagement", ["statut"])

    if T_REGISTREDTO not in tables:
        op.create_table(
            T_REGISTREDTO,
            sa.Column("id", sa.Integer(), primary_key=True),
            sa.Column("reference_dto", sa.String(80), nullable=False),
            sa.Column("exercice", sa.Integer(), nullable=False),
            sa.Column("projet_id", sa.Integer(), nullable=True),
            sa.Column("port_id", sa.Integer(), nullable=True),
            sa.Column("objet", sa.String(300), nullable=False),
            sa.Column("montant_inscrit_xaf", sa.Numeric(18, 2), nullable=True),
            sa.Column("montant_paye_xaf", sa.Numeric(18, 2), nullable=True),
            sa.Column("source_financement", sa.String(25), nullable=True),
            sa.Column("chapitre", sa.String(120), nullable=True),
            sa.Column("statut", sa.String(30), nullable=True),
            sa.Column("date_presentation", sa.Date(), nullable=True),
            sa.Column("date_visa_controle_financier", sa.Date(), nullable=True),
            sa.Column("autorite_visa", sa.String(160), nullable=True),
            sa.Column("numero_engagement", sa.String(80), nullable=True),
            sa.Column("date_notification_minepf", sa.Date(), nullable=True),
            sa.Column("source_reference", sa.String(200), nullable=True),
            sa.Column("date_verification", sa.Date(), nullable=True),
            sa.Column("auteur_saisie", sa.String(120), nullable=True),
            sa.Column("notes", sa.String(), nullable=True),
            sa.Column("created_at", sa.DateTime(timezone=True), nullable=True),
            sa.Column("updated_at", sa.DateTime(timezone=True), nullable=True),
            sa.ForeignKeyConstraint(["projet_id"], ["projets_amenagement.id"], name="fk_registres_dto_amgt_projet_id_projets_amenagement"),
            sa.ForeignKeyConstraint(["port_id"], ["ports_cameroun.id"], name="fk_registres_dto_amgt_port_id_ports_cameroun"),
        )
        op.create_index("ix_registres_dto_amgt_id", "registres_dto_amgt", ["id"])
        op.create_index("ix_registres_dto_amgt_reference_dto", "registres_dto_amgt", ["reference_dto"], unique=True, unique=True)
        op.create_index("ix_registres_dto_amgt_exercice", "registres_dto_amgt", ["exercice"])
        op.create_index("ix_registres_dto_amgt_projet_id", "registres_dto_amgt", ["projet_id"])
        op.create_index("ix_registres_dto_amgt_statut", "registres_dto_amgt", ["statut"])

    if T_MARCHEAMENAGEMENT not in tables:
        op.create_table(
            T_MARCHEAMENAGEMENT,
            sa.Column("id", sa.Integer(), primary_key=True),
            sa.Column("reference", sa.String(80), nullable=False),
            sa.Column("designations", sa.String(300), nullable=False),
            sa.Column("projet_id", sa.Integer(), nullable=True),
            sa.Column("port_id", sa.Integer(), nullable=True),
            sa.Column("type_marche", sa.String(21), nullable=False),
            sa.Column("code_marche", sa.String(13), nullable=True),
            sa.Column("statut", sa.String(19), nullable=False),
            sa.Column("procedure_controle", sa.String(60), nullable=True),
            sa.Column("dossier_appel_offre", sa.String(120), nullable=True),
            sa.Column("date_publication_dao", sa.Date(), nullable=True),
            sa.Column("date_remise_offres", sa.Date(), nullable=True),
            sa.Column("date_colife", sa.Date(), nullable=True),
            sa.Column("avis_colife", sa.String(40), nullable=True),
            sa.Column("date_attribution", sa.Date(), nullable=True),
            sa.Column("attributaire", sa.String(200), nullable=True),
            sa.Column("montant_attribue_xaf", sa.Numeric(18, 2), nullable=True),
            sa.Column("montant_initial_xaf", sa.Numeric(18, 2), nullable=True),
            sa.Column("montant_final_xaf", sa.Numeric(18, 2), nullable=True),
            sa.Column("devise", sa.String(6), nullable=True),
            sa.Column("part_pmp_pct", sa.Numeric(5, 2), nullable=True),
            sa.Column("avance_demarrage_xaf", sa.Numeric(18, 2), nullable=True),
            sa.Column("retenue_garantie_pct", sa.Numeric(5, 2), nullable=True),
            sa.Column("caution_banque", sa.String(160), nullable=True),
            sa.Column("delai_execution_mois", sa.Integer(), nullable=True),
            sa.Column("date_notification", sa.Date(), nullable=True),
            sa.Column("date_ouverture_chantier", sa.Date(), nullable=True),
            sa.Column("date_reception_provisoire", sa.Date(), nullable=True),
            sa.Column("date_reception_definitive", sa.Date(), nullable=True),
            sa.Column("garant_result_annees", sa.Integer(), nullable=True),
            sa.Column("nrd_max_jours", sa.Integer(), nullable=True),
            sa.Column("source_reference", sa.String(200), nullable=True),
            sa.Column("date_verification", sa.Date(), nullable=True),
            sa.Column("auteur_saisie", sa.String(120), nullable=True),
            sa.Column("notes", sa.String(), nullable=True),
            sa.Column("created_at", sa.DateTime(timezone=True), nullable=True),
            sa.Column("updated_at", sa.DateTime(timezone=True), nullable=True),
            sa.ForeignKeyConstraint(["projet_id"], ["projets_amenagement.id"], name="fk_marches_amenagement_projet_id_projets_amenagement"),
            sa.ForeignKeyConstraint(["port_id"], ["ports_cameroun.id"], name="fk_marches_amenagement_port_id_ports_cameroun"),
        )
        op.create_index("ix_marches_amenagement_id", "marches_amenagement", ["id"])
        op.create_index("ix_marches_amenagement_reference", "marches_amenagement", ["reference"], unique=True, unique=True)
        op.create_index("ix_marches_amenagement_projet_id", "marches_amenagement", ["projet_id"])
        op.create_index("ix_marches_amenagement_statut", "marches_amenagement", ["statut"])

    if T_AUTORISATIONDOMANIALE not in tables:
        op.create_table(
            T_AUTORISATIONDOMANIALE,
            sa.Column("id", sa.Integer(), primary_key=True),
            sa.Column("numero_piece", sa.String(80), nullable=False),
            sa.Column("type_titre", sa.String(34), nullable=False),
            sa.Column("port_id", sa.Integer(), nullable=True),
            sa.Column("terminal_id", sa.Integer(), nullable=True),
            sa.Column("zone_id", sa.Integer(), nullable=True),
            sa.Column("beneficiaire", sa.String(200), nullable=False),
            sa.Column("objet", sa.String(300), nullable=True),
            sa.Column("assiette", sa.String(), nullable=True),
            sa.Column("superficie_m2", sa.Numeric(14, 3), nullable=True),
            sa.Column("destination", sa.String(120), nullable=True),
            sa.Column("redevance_annuelle_xaf", sa.Numeric(18, 2), nullable=True),
            sa.Column("taux_redevance", sa.String(60), nullable=True),
            sa.Column("date_demande", sa.Date(), nullable=True),
            sa.Column("date_signature", sa.Date(), nullable=True),
            sa.Column("date_effet", sa.Date(), nullable=True),
            sa.Column("date_expiration", sa.Date(), nullable=True),
            sa.Column("renouvelable", sa.Boolean(), nullable=True),
            sa.Column("delai_renouvellement_mois", sa.Integer(), nullable=True),
            sa.Column("autorite_emettrice", sa.String(160), nullable=True),
            sa.Column("reference_deliberation", sa.String(120), nullable=True),
            sa.Column("piece_jointe", sa.String(300), nullable=True),
            sa.Column("statut", sa.String(30), nullable=True),
            sa.Column("motif_refus", sa.String(), nullable=True),
            sa.Column("source_reference", sa.String(200), nullable=True),
            sa.Column("date_verification", sa.Date(), nullable=True),
            sa.Column("auteur_saisie", sa.String(120), nullable=True),
            sa.Column("notes", sa.String(), nullable=True),
            sa.Column("created_at", sa.DateTime(timezone=True), nullable=True),
            sa.Column("updated_at", sa.DateTime(timezone=True), nullable=True),
            sa.ForeignKeyConstraint(["port_id"], ["ports_cameroun.id"], name="fk_autorisations_domaniales_amgt_port_id_ports_cameroun"),
            sa.ForeignKeyConstraint(["terminal_id"], ["terminaux_portuaires.id"], name="fk_autorisations_domaniales_amgt_terminal_id_terminaux_portuaires"),
            sa.ForeignKeyConstraint(["zone_id"], ["zones_portuaires.id"], name="fk_autorisations_domaniales_amgt_zone_id_zones_portuaires"),
        )
        op.create_index("ix_autorisations_domaniales_amgt_id", "autorisations_domaniales_amgt", ["id"])
        op.create_index("ix_autorisations_domaniales_amgt_numero_piece", "autorisations_domaniales_amgt", ["numero_piece"], unique=True, unique=True)
        op.create_index("ix_autorisations_domaniales_amgt_type_titre", "autorisations_domaniales_amgt", ["type_titre"])
        op.create_index("ix_autorisations_domaniales_amgt_port_id", "autorisations_domaniales_amgt", ["port_id"])
        op.create_index("ix_autorisations_domaniales_amgt_date_expiration", "autorisations_domaniales_amgt", ["date_expiration"])
        op.create_index("ix_autorisations_domaniales_amgt_statut", "autorisations_domaniales_amgt", ["statut"])

    if T_CONCESSIONPORTUAIRE not in tables:
        op.create_table(
            T_CONCESSIONPORTUAIRE,
            sa.Column("id", sa.Integer(), primary_key=True),
            sa.Column("code_contrat", sa.String(60), nullable=False),
            sa.Column("nom_contrat", sa.String(200), nullable=False),
            sa.Column("port_id", sa.Integer(), nullable=False),
            sa.Column("terminal_id", sa.Integer(), nullable=True),
            sa.Column("type_contrat", sa.String(21), nullable=False),
            sa.Column("statut", sa.String(11), nullable=False),
            sa.Column("autorite_concedante", sa.String(160), nullable=False),
            sa.Column("concessionnaire", sa.String(200), nullable=False),
            sa.Column("groupe_final", sa.String(160), nullable=True),
            sa.Column("objet", sa.String(), nullable=True),
            sa.Column("perimetre", sa.String(), nullable=True),
            sa.Column("superficie_concedee_ha", sa.Numeric(14, 3), nullable=True),
            sa.Column("longueur_quai_ml", sa.Numeric(12, 2), nullable=True),
            sa.Column("capacite_contractuelle", sa.String(120), nullable=True),
            sa.Column("date_effet", sa.Date(), nullable=True),
            sa.Column("date_echeance", sa.Date(), nullable=True),
            sa.Column("duree_mois", sa.Integer(), nullable=True),
            sa.Column("prolongations", sa.String(), nullable=True),
            sa.Column("investissement_promis_xaf", sa.Numeric(18, 2), nullable=True),
            sa.Column("investissement_realise_xaf", sa.Numeric(18, 2), nullable=True),
            sa.Column("redevance_concession_xaf", sa.Numeric(18, 2), nullable=True),
            sa.Column("redevance_par_unite", sa.Numeric(18, 2), nullable=True),
            sa.Column("unite_redevance", sa.String(40), nullable=True),
            sa.Column("clauses_revolution", sa.String(), nullable=True),
            sa.Column("sanctions_contractuelles", sa.String(), nullable=True),
            sa.Column("biens_reversibles", sa.String(), nullable=True),
            sa.Column("reference_approbation", sa.String(120), nullable=True),
            sa.Column("date_approbation", sa.Date(), nullable=True),
            sa.Column("arret_travail", sa.Boolean(), nullable=True),
            sa.Column("source_reference", sa.String(200), nullable=True),
            sa.Column("date_verification", sa.Date(), nullable=True),
            sa.Column("auteur_saisie", sa.String(120), nullable=True),
            sa.Column("notes", sa.String(), nullable=True),
            sa.Column("created_at", sa.DateTime(timezone=True), nullable=True),
            sa.Column("updated_at", sa.DateTime(timezone=True), nullable=True),
            sa.ForeignKeyConstraint(["port_id"], ["ports_cameroun.id"], name="fk_concessions_amenagement_port_id_ports_cameroun"),
            sa.ForeignKeyConstraint(["terminal_id"], ["terminaux_portuaires.id"], name="fk_concessions_amenagement_terminal_id_terminaux_portuaires"),
        )
        op.create_index("ix_concessions_amenagement_id", "concessions_amenagement", ["id"])
        op.create_index("ix_concessions_amenagement_code_contrat", "concessions_amenagement", ["code_contrat"], unique=True, unique=True)
        op.create_index("ix_concessions_amenagement_port_id", "concessions_amenagement", ["port_id"])
        op.create_index("ix_concessions_amenagement_type_contrat", "concessions_amenagement", ["type_contrat"])
        op.create_index("ix_concessions_amenagement_statut", "concessions_amenagement", ["statut"])
        op.create_index("ix_concessions_amenagement_date_echeance", "concessions_amenagement", ["date_echeance"])

    if T_INFRASTRUCTUREPORTUAIRE not in tables:
        op.create_table(
            T_INFRASTRUCTUREPORTUAIRE,
            sa.Column("id", sa.Integer(), primary_key=True),
            sa.Column("code", sa.String(60), nullable=False),
            sa.Column("designation", sa.String(200), nullable=False),
            sa.Column("type_infrastructure", sa.String(14), nullable=False),
            sa.Column("port_id", sa.Integer(), nullable=False),
            sa.Column("terminal_id", sa.Integer(), nullable=True),
            sa.Column("projet_id", sa.Integer(), nullable=True),
            sa.Column("zone_id", sa.Integer(), nullable=True),
            sa.Column("emplacement", sa.String(200), nullable=True),
            sa.Column("statut", sa.String(15), nullable=False),
            sa.Column("longueur_ml", sa.Numeric(12, 2), nullable=True),
            sa.Column("largeur_m", sa.Numeric(10, 2), nullable=True),
            sa.Column("superficie_m2", sa.Numeric(14, 3), nullable=True),
            sa.Column("profondeur_utile_m", sa.Numeric(8, 2), nullable=True),
            sa.Column("hauteur_parement_m", sa.Integer(), nullable=True),
            sa.Column("portance_tonnes_m2", sa.Numeric(8, 2), nullable=True),
            sa.Column("capacite_teus", sa.Integer(), nullable=True),
            sa.Column("date_mise_service", sa.Date(), nullable=True),
            sa.Column("date_derniere_inspection", sa.Date(), nullable=True),
            sa.Column("periodicite_inspection_mois", sa.Integer(), nullable=True),
            sa.Column("prochaine_inspection", sa.Date(), nullable=True),
            sa.Column("etat_structural", sa.String(30), nullable=True),
            sa.Column("note_genie_civil", sa.Numeric(5, 2), nullable=True),
            sa.Column("travaux_renovation_prevus", sa.Boolean(), nullable=True),
            sa.Column("estimation_renovation_xaf", sa.Numeric(18, 2), nullable=True),
            sa.Column("valeur_patrimoniale_xaf", sa.Numeric(18, 2), nullable=True),
            sa.Column("date_entree_patrimoine", sa.Date(), nullable=True),
            sa.Column("regime_fiscal", sa.String(60), nullable=True),
            sa.Column("reversable", sa.Boolean(), nullable=True),
            sa.Column("operateur_entretien", sa.String(160), nullable=True),
            sa.Column("sources_documents", sa.String(), nullable=True),
            sa.Column("source_reference", sa.String(200), nullable=True),
            sa.Column("date_verification", sa.Date(), nullable=True),
            sa.Column("auteur_saisie", sa.String(120), nullable=True),
            sa.Column("notes", sa.String(), nullable=True),
            sa.Column("est_actif", sa.Boolean(), nullable=False),
            sa.Column("created_at", sa.DateTime(timezone=True), nullable=True),
            sa.Column("updated_at", sa.DateTime(timezone=True), nullable=True),
            sa.ForeignKeyConstraint(["port_id"], ["ports_cameroun.id"], name="fk_infrastructures_amenagees_port_id_ports_cameroun"),
            sa.ForeignKeyConstraint(["terminal_id"], ["terminaux_portuaires.id"], name="fk_infrastructures_amenagees_terminal_id_terminaux_portuaires"),
            sa.ForeignKeyConstraint(["projet_id"], ["projets_amenagement.id"], name="fk_infrastructures_amenagees_projet_id_projets_amenagement"),
            sa.ForeignKeyConstraint(["zone_id"], ["zones_portuaires.id"], name="fk_infrastructures_amenagees_zone_id_zones_portuaires"),
        )
        op.create_index("ix_infrastructures_amenagees_id", "infrastructures_amenagees", ["id"])
        op.create_index("ix_infrastructures_amenagees_code", "infrastructures_amenagees", ["code"], unique=True, unique=True)
        op.create_index("ix_infrastructures_amenagees_type_infrastructure", "infrastructures_amenagees", ["type_infrastructure"])
        op.create_index("ix_infrastructures_amenagees_port_id", "infrastructures_amenagees", ["port_id"])
        op.create_index("ix_infrastructures_amenagees_projet_id", "infrastructures_amenagees", ["projet_id"])
        op.create_index("ix_infrastructures_amenagees_statut", "infrastructures_amenagees", ["statut"])

    if T_DRAGAGE not in tables:
        op.create_table(
            T_DRAGAGE,
            sa.Column("id", sa.Integer(), primary_key=True),
            sa.Column("code_campagne", sa.String(60), nullable=False),
            sa.Column("libelle", sa.String(200), nullable=False),
            sa.Column("port_id", sa.Integer(), nullable=False),
            sa.Column("projet_id", sa.Integer(), nullable=True),
            sa.Column("type_dragage", sa.String(18), nullable=False),
            sa.Column("zone_traitee", sa.String(200), nullable=True),
            sa.Column("superficie_draguee_m2", sa.Numeric(14, 3), nullable=True),
            sa.Column("volume_mesure_m3", sa.Numeric(18, 2), nullable=True),
            sa.Column("volume_facture_m3", sa.Numeric(18, 2), nullable=True),
            sa.Column("profondeur_avant_m", sa.Numeric(8, 2), nullable=True),
            sa.Column("profondeur_visee_m", sa.Numeric(8, 2), nullable=True),
            sa.Column("profondeur_obtenue_m", sa.Numeric(8, 2), nullable=True),
            sa.Column("nature_sediment", sa.String(120), nullable=True),
            sa.Column("exutoire_rejet", sa.String(200), nullable=True),
            sa.Column("autorisation_rejet_reference", sa.String(120), nullable=True),
            sa.Column("entreprise", sa.String(200), nullable=True),
            sa.Column("type_drague", sa.String(80), nullable=True),
            sa.Column("cout_xaf", sa.Numeric(18, 2), nullable=True),
            sa.Column("devise", sa.String(6), nullable=True),
            sa.Column("date_debut", sa.Date(), nullable=True),
            sa.Column("date_fin", sa.Date(), nullable=True),
            sa.Column("jours_arret", sa.Integer(), nullable=True),
            sa.Column("statut", sa.String(30), nullable=True),
            sa.Column("leve_bathymetrique_apres", sa.Boolean(), nullable=True),
            sa.Column("date_releve", sa.Date(), nullable=True),
            sa.Column("autorisation_administrative", sa.String(200), nullable=True),
            sa.Column("impact_environnemental", sa.String(), nullable=True),
            sa.Column("source_reference", sa.String(200), nullable=True),
            sa.Column("date_verification", sa.Date(), nullable=True),
            sa.Column("auteur_saisie", sa.String(120), nullable=True),
            sa.Column("notes", sa.String(), nullable=True),
            sa.Column("created_at", sa.DateTime(timezone=True), nullable=True),
            sa.Column("updated_at", sa.DateTime(timezone=True), nullable=True),
            sa.ForeignKeyConstraint(["port_id"], ["ports_cameroun.id"], name="fk_campagnes_dragage_port_id_ports_cameroun"),
            sa.ForeignKeyConstraint(["projet_id"], ["projets_amenagement.id"], name="fk_campagnes_dragage_projet_id_projets_amenagement"),
        )
        op.create_index("ix_campagnes_dragage_id", "campagnes_dragage", ["id"])
        op.create_index("ix_campagnes_dragage_code_campagne", "campagnes_dragage", ["code_campagne"], unique=True, unique=True)
        op.create_index("ix_campagnes_dragage_port_id", "campagnes_dragage", ["port_id"])
        op.create_index("ix_campagnes_dragage_projet_id", "campagnes_dragage", ["projet_id"])
        op.create_index("ix_campagnes_dragage_type_dragage", "campagnes_dragage", ["type_dragage"])
        op.create_index("ix_campagnes_dragage_statut", "campagnes_dragage", ["statut"])

    if T_AUTORISATIONTRAVAUX not in tables:
        op.create_table(
            T_AUTORISATIONTRAVAUX,
            sa.Column("id", sa.Integer(), primary_key=True),
            sa.Column("reference", sa.String(80), nullable=False),
            sa.Column("type_autorisation", sa.String(20), nullable=False),
            sa.Column("projet_id", sa.Integer(), nullable=True),
            sa.Column("port_id", sa.Integer(), nullable=True),
            sa.Column("administration", sa.String(160), nullable=True),
            sa.Column("categorie_projet", sa.String(40), nullable=True),
            sa.Column("objet", sa.String(300), nullable=True),
            sa.Column("statut", sa.String(17), nullable=False),
            sa.Column("date_depot", sa.Date(), nullable=True),
            sa.Column("date_accord", sa.Date(), nullable=True),
            sa.Column("date_expiration", sa.Date(), nullable=True),
            sa.Column("numero_arrete", sa.String(120), nullable=True),
            sa.Column("conditions_particulieres", sa.String(), nullable=True),
            sa.Column("charges_enviro_xaf", sa.Numeric(18, 2), nullable=True),
            sa.Column("audit_date_prochaine", sa.Date(), nullable=True),
            sa.Column("piece_jointe", sa.String(300), nullable=True),
            sa.Column("source_reference", sa.String(200), nullable=True),
            sa.Column("date_verification", sa.Date(), nullable=True),
            sa.Column("auteur_saisie", sa.String(120), nullable=True),
            sa.Column("notes", sa.String(), nullable=True),
            sa.Column("created_at", sa.DateTime(timezone=True), nullable=True),
            sa.Column("updated_at", sa.DateTime(timezone=True), nullable=True),
            sa.ForeignKeyConstraint(["projet_id"], ["projets_amenagement.id"], name="fk_autorisations_travaux_amgt_projet_id_projets_amenagement"),
            sa.ForeignKeyConstraint(["port_id"], ["ports_cameroun.id"], name="fk_autorisations_travaux_amgt_port_id_ports_cameroun"),
        )
        op.create_index("ix_autorisations_travaux_amgt_id", "autorisations_travaux_amgt", ["id"])
        op.create_index("ix_autorisations_travaux_amgt_reference", "autorisations_travaux_amgt", ["reference"], unique=True, unique=True)
        op.create_index("ix_autorisations_travaux_amgt_type_autorisation", "autorisations_travaux_amgt", ["type_autorisation"])
        op.create_index("ix_autorisations_travaux_amgt_projet_id", "autorisations_travaux_amgt", ["projet_id"])
        op.create_index("ix_autorisations_travaux_amgt_statut", "autorisations_travaux_amgt", ["statut"])
    # ── ports_cameroun : colonnes attendues par GET /api/v1/public/ports ──────
    if T_PORTS in tables:
        cols = {c["name"] for c in sa.inspect(bind).get_columns(T_PORTS)}
        if "autorite_portuaire" not in cols:
            op.add_column(T_PORTS, sa.Column("autorite_portuaire", sa.String(160), nullable=True))
        if "tirant_eau_max" not in cols:
            op.add_column(T_PORTS, sa.Column("tirant_eau_max", sa.Numeric(6, 2), nullable=True))


def downgrade():
    bind = op.get_bind()
    tables = set(sa.inspect(bind).get_table_names())
    insp = sa.inspect(bind)
    if T_PORTS in tables:
        cols = {c["name"] for c in insp.get_columns(T_PORTS)}
        with op.batch_alter_table(T_PORTS) as batch:
            if "tirant_eau_max" in cols:
                batch.drop_column("tirant_eau_max")
            if "autorite_portuaire" in cols:
                batch.drop_column("autorite_portuaire")
    if T_AUTORISATIONTRAVAUX in tables:
        op.drop_table(T_AUTORISATIONTRAVAUX)
    if T_DRAGAGE in tables:
        op.drop_table(T_DRAGAGE)
    if T_INFRASTRUCTUREPORTUAIRE in tables:
        op.drop_table(T_INFRASTRUCTUREPORTUAIRE)
    if T_CONCESSIONPORTUAIRE in tables:
        op.drop_table(T_CONCESSIONPORTUAIRE)
    if T_AUTORISATIONDOMANIALE in tables:
        op.drop_table(T_AUTORISATIONDOMANIALE)
    if T_MARCHEAMENAGEMENT in tables:
        op.drop_table(T_MARCHEAMENAGEMENT)
    if T_REGISTREDTO in tables:
        op.drop_table(T_REGISTREDTO)
    if T_PROJETAMENAGEMENT in tables:
        op.drop_table(T_PROJETAMENAGEMENT)
    if T_SCHEMADIRECTEUR in tables:
        op.drop_table(T_SCHEMADIRECTEUR)
