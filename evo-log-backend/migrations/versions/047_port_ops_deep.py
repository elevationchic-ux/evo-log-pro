"""047 : tables operations portuaires approfondies (Wave 1A expansion).

Cree les 12 tables liees au module port_operations_deep.py :
    draft_surveys, stevedoring_crews, cargo_handling_plans, quay_equipments,
    pilotage_sessions, towage_operations, bunkering_orders,
    vessel_waste_receipts, tally_sheets, demurrage_cases, gate_passes,
    yard_operations

Chaque table porte company_id (multi-tenant) + index de unicite metier.
Idempotent via introspection (compatible base issuee de create_all).

Revision ID: 047_port_ops_deep
Revises: 046_rbac_qhse_permis_read_grant
Create Date: 2026-10-07
"""
from alembic import op
import sqlalchemy as sa


revision = "047_port_ops_deep"
down_revision = "046_rbac_qhse_permis_read_grant"
branch_labels = None
depends_on = None


TABLES = [
    "draft_surveys", "stevedoring_crews", "cargo_handling_plans",
    "quay_equipments", "pilotage_sessions", "towage_operations",
    "bunkering_orders", "vessel_waste_receipts", "tally_sheets",
    "demurrage_cases", "gate_passes", "yard_operations",
]


def _has(name):
    insp = sa.inspect(op.get_bind())
    return name in set(insp.get_table_names())


def upgrade():
    if not _has("draft_surveys"):
        op.create_table(
            "draft_surveys",
            sa.Column("id", sa.Integer, primary_key=True, index=True),
            sa.Column("company_id", sa.Integer, nullable=False, index=True),
            sa.Column("numero_constat", sa.String(50), nullable=False, index=True),
            sa.Column("navire_id", sa.Integer, nullable=True),
            sa.Column("escale_id", sa.Integer, nullable=True),
            sa.Column("date_constat", sa.Date, nullable=True),
            sa.Column("lieu_constat", sa.String(100), nullable=True),
            sa.Column("tirant_eau_avant", sa.Numeric, nullable=True),
            sa.Column("tirant_eau_arriere", sa.Numeric, nullable=True),
            sa.Column("type_avarie", sa.String(30), nullable=True),
            sa.Column("gravite", sa.String(30), nullable=True),
            sa.Column("description", sa.Text, nullable=True),
            sa.Column("photos_jointes", sa.Text, nullable=True),
            sa.Column("statut", sa.String(30), nullable=True),
            sa.Column("inspecteur", sa.String(100), nullable=True),
            sa.Column("capitaine_signataire", sa.String(100), nullable=True),
            sa.Column("notes", sa.Text, nullable=True),
            sa.Column("source_reference", sa.String(200), nullable=True),
            sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
            sa.Column("updated_at", sa.DateTime(timezone=True), nullable=True),
            sa.UniqueConstraint("company_id", "numero_constat", name="uix_draft_survey_company_num"),
        )

    if not _has("stevedoring_crews"):
        op.create_table(
            "stevedoring_crews",
            sa.Column("id", sa.Integer, primary_key=True, index=True),
            sa.Column("company_id", sa.Integer, nullable=False, index=True),
            sa.Column("code_gang", sa.String(30), nullable=False, index=True),
            sa.Column("nom_gang", sa.String(100), nullable=True),
            sa.Column("type_equipe", sa.String(30), nullable=True),
            sa.Column("statut", sa.String(30), nullable=True),
            sa.Column("chef_gang", sa.String(100), nullable=True),
            sa.Column("nombre_membres", sa.Integer, nullable=True),
            sa.Column("specialites", sa.Text, nullable=True),
            sa.Column("certification", sa.String(100), nullable=True),
            sa.Column("date_expiration_certification", sa.Date, nullable=True),
            sa.Column("telephone_chef", sa.String(30), nullable=True),
            sa.Column("notes", sa.Text, nullable=True),
            sa.Column("is_active", sa.Boolean, nullable=True),
            sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
            sa.Column("updated_at", sa.DateTime(timezone=True), nullable=True),
            sa.UniqueConstraint("company_id", "code_gang", name="uix_crew_company_code"),
        )

    if not _has("cargo_handling_plans"):
        op.create_table(
            "cargo_handling_plans",
            sa.Column("id", sa.Integer, primary_key=True, index=True),
            sa.Column("company_id", sa.Integer, nullable=False, index=True),
            sa.Column("reference_plan", sa.String(50), nullable=False, index=True),
            sa.Column("escale_id", sa.Integer, nullable=True),
            sa.Column("navire_id", sa.Integer, nullable=True),
            sa.Column("type_operation", sa.String(30), nullable=True),
            sa.Column("statut", sa.String(30), nullable=True),
            sa.Column("numero_cale", sa.String(20), nullable=True),
            sa.Column("poids_total_tonnes", sa.Numeric, nullable=True),
            sa.Column("nombre_colis", sa.Integer, nullable=True),
            sa.Column("nombre_conteneurs", sa.Integer, nullable=True),
            sa.Column("date_debut_prevue", sa.DateTime(timezone=True), nullable=True),
            sa.Column("date_fin_prevue", sa.DateTime(timezone=True), nullable=True),
            sa.Column("date_debut_reelle", sa.DateTime(timezone=True), nullable=True),
            sa.Column("date_fin_reelle", sa.DateTime(timezone=True), nullable=True),
            sa.Column("cadence_prevue_t_h", sa.Numeric, nullable=True),
            sa.Column("cadence_reelle_t_h", sa.Numeric, nullable=True),
            sa.Column("gang_id", sa.Integer, nullable=True),
            sa.Column("equipement_id", sa.Integer, nullable=True),
            sa.Column("charge_a_bord_port", sa.String(100), nullable=True),
            sa.Column("decharge_a_quai_port", sa.String(100), nullable=True),
            sa.Column("notes", sa.Text, nullable=True),
            sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
            sa.Column("updated_at", sa.DateTime(timezone=True), nullable=True),
            sa.UniqueConstraint("company_id", "reference_plan", name="uix_cargo_plan_company_ref"),
        )

    if not _has("quay_equipments"):
        op.create_table(
            "quay_equipments",
            sa.Column("id", sa.Integer, primary_key=True, index=True),
            sa.Column("company_id", sa.Integer, nullable=False, index=True),
            sa.Column("code_equipement", sa.String(50), nullable=False, index=True),
            sa.Column("designation", sa.String(200), nullable=False),
            sa.Column("type_equipement", sa.String(30), nullable=True),
            sa.Column("etat", sa.String(30), nullable=True),
            sa.Column("marque", sa.String(100), nullable=True),
            sa.Column("modele", sa.String(100), nullable=True),
            sa.Column("capacite_max_tonnes", sa.Numeric, nullable=True),
            sa.Column("portee_max_m", sa.Numeric, nullable=True),
            sa.Column("hauteur_sous_flèche_m", sa.Numeric, nullable=True),
            sa.Column("annee_mise_service", sa.Integer, nullable=True),
            sa.Column("fournisseur", sa.String(200), nullable=True),
            sa.Column("numero_serial", sa.String(100), nullable=True),
            sa.Column("prochaine_maintenance_date", sa.Date, nullable=True),
            sa.Column("prochaine_maintenance_km", sa.Numeric, nullable=True),
            sa.Column("heures_service_cumulees", sa.Numeric, nullable=True),
            sa.Column("poste_quai_assigne", sa.String(50), nullable=True),
            sa.Column("cout_acquisition_xaf", sa.Numeric, nullable=True),
            sa.Column("notes", sa.Text, nullable=True),
            sa.Column("is_active", sa.Boolean, nullable=True),
            sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
            sa.Column("updated_at", sa.DateTime(timezone=True), nullable=True),
            sa.UniqueConstraint("company_id", "code_equipement", name="uix_equip_company_code"),
        )

    if not _has("pilotage_sessions"):
        op.create_table(
            "pilotage_sessions",
            sa.Column("id", sa.Integer, primary_key=True, index=True),
            sa.Column("company_id", sa.Integer, nullable=False, index=True),
            sa.Column("reference", sa.String(50), nullable=False, index=True),
            sa.Column("navire_id", sa.Integer, nullable=True),
            sa.Column("escale_id", sa.Integer, nullable=True),
            sa.Column("pilote_nom", sa.String(100), nullable=True),
            sa.Column("pilote_matricule", sa.String(50), nullable=True),
            sa.Column("statut", sa.String(30), nullable=True),
            sa.Column("type_mouvement", sa.String(30), nullable=True),
            sa.Column("date_demande", sa.DateTime(timezone=True), nullable=True),
            sa.Column("date_debut_reelle", sa.DateTime(timezone=True), nullable=True),
            sa.Column("date_fin_reelle", sa.DateTime(timezone=True), nullable=True),
            sa.Column("duree_heures", sa.Numeric, nullable=True),
            sa.Column("zone_pilotage", sa.String(100), nullable=True),
            sa.Column("distance_nautique_mq", sa.Numeric, nullable=True),
            sa.Column("conditions_meteo", sa.String(200), nullable=True),
            sa.Column("vitesse_navire_noeuds", sa.Numeric, nullable=True),
            sa.Column("tirant_eau_navire_m", sa.Numeric, nullable=True),
            sa.Column("tarif_pilotage_xaf", sa.Numeric, nullable=True),
            sa.Column("notes", sa.Text, nullable=True),
            sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
            sa.Column("updated_at", sa.DateTime(timezone=True), nullable=True),
            sa.UniqueConstraint("company_id", "reference", name="uix_pilotage_company_ref"),
        )

    if not _has("towage_operations"):
        op.create_table(
            "towage_operations",
            sa.Column("id", sa.Integer, primary_key=True, index=True),
            sa.Column("company_id", sa.Integer, nullable=False, index=True),
            sa.Column("reference", sa.String(50), nullable=False, index=True),
            sa.Column("navire_id", sa.Integer, nullable=True),
            sa.Column("escale_id", sa.Integer, nullable=True),
            sa.Column("remorqueur_nom", sa.String(100), nullable=True),
            sa.Column("remorqueur_immatriculation", sa.String(50), nullable=True),
            sa.Column("nombre_remorqueurs", sa.Integer, nullable=True),
            sa.Column("type_prestation", sa.String(50), nullable=True),
            sa.Column("statut", sa.String(30), nullable=True),
            sa.Column("date_debut_reelle", sa.DateTime(timezone=True), nullable=True),
            sa.Column("date_fin_reelle", sa.DateTime(timezone=True), nullable=True),
            sa.Column("duree_heures", sa.Numeric, nullable=True),
            sa.Column("puissance_bollard_t", sa.Numeric, nullable=True),
            sa.Column("zone_operation", sa.String(100), nullable=True),
            sa.Column("tarif_xaf", sa.Numeric, nullable=True),
            sa.Column("operateur", sa.String(200), nullable=True),
            sa.Column("conditions_meteo", sa.String(200), nullable=True),
            sa.Column("notes", sa.Text, nullable=True),
            sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
            sa.Column("updated_at", sa.DateTime(timezone=True), nullable=True),
            sa.UniqueConstraint("company_id", "reference", name="uix_towage_company_ref"),
        )

    if not _has("bunkering_orders"):
        op.create_table(
            "bunkering_orders",
            sa.Column("id", sa.Integer, primary_key=True, index=True),
            sa.Column("company_id", sa.Integer, nullable=False, index=True),
            sa.Column("reference", sa.String(50), nullable=False, index=True),
            sa.Column("navire_id", sa.Integer, nullable=True),
            sa.Column("escale_id", sa.Integer, nullable=True),
            sa.Column("type_carburant", sa.String(30), nullable=True),
            sa.Column("quantite_tonnes", sa.Numeric, nullable=True),
            sa.Column("densite", sa.Numeric, nullable=True),
            sa.Column("soufre_pct", sa.Numeric, nullable=True),
            sa.Column("prix_tonne_xaf", sa.Numeric, nullable=True),
            sa.Column("montant_total_xaf", sa.Numeric, nullable=True),
            sa.Column("fournisseur", sa.String(200), nullable=True),
            sa.Column("barge_nom", sa.String(100), nullable=True),
            sa.Column("date_operation", sa.DateTime(timezone=True), nullable=True),
            sa.Column("heure_debut", sa.String(10), nullable=True),
            sa.Column("heure_fin", sa.String(10), nullable=True),
            sa.Column("debit_t_h", sa.Numeric, nullable=True),
            sa.Column("statut", sa.String(30), nullable=True),
            sa.Column("bon_livraison_ref", sa.String(100), nullable=True),
            sa.Column("quantitemesuree_t", sa.Numeric, nullable=True),
            sa.Column("ecart_quantite_t", sa.Numeric, nullable=True),
            sa.Column("capitaine_signataire", sa.String(100), nullable=True),
            sa.Column("notes", sa.Text, nullable=True),
            sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
            sa.Column("updated_at", sa.DateTime(timezone=True), nullable=True),
            sa.UniqueConstraint("company_id", "reference", name="uix_bunker_company_ref"),
        )

    if not _has("vessel_waste_receipts"):
        op.create_table(
            "vessel_waste_receipts",
            sa.Column("id", sa.Integer, primary_key=True, index=True),
            sa.Column("company_id", sa.Integer, nullable=False, index=True),
            sa.Column("reference", sa.String(50), nullable=False, index=True),
            sa.Column("navire_id", sa.Integer, nullable=True),
            sa.Column("escale_id", sa.Integer, nullable=True),
            sa.Column("type_dechet", sa.String(30), nullable=True),
            sa.Column("quantite", sa.Numeric, nullable=True),
            sa.Column("unite", sa.String(20), nullable=True),
            sa.Column("date_reception", sa.DateTime(timezone=True), nullable=True),
            sa.Column("lieu_depot", sa.String(200), nullable=True),
            sa.Column("operateur_collecte", sa.String(200), nullable=True),
            sa.Column("fichier_destinataire", sa.String(200), nullable=True),
            sa.Column("cout_collecte_xaf", sa.Integer, nullable=True),
            sa.Column("numero_manifeste_dechet", sa.String(100), nullable=True),
            sa.Column("marpol_annexe", sa.String(10), nullable=True),
            sa.Column("capitaine_declare", sa.String(100), nullable=True),
            sa.Column("recu_par", sa.String(100), nullable=True),
            sa.Column("conforme", sa.Boolean, nullable=True),
            sa.Column("notes", sa.Text, nullable=True),
            sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
            sa.Column("updated_at", sa.DateTime(timezone=True), nullable=True),
            sa.UniqueConstraint("company_id", "reference", name="uix_waste_company_ref"),
        )

    if not _has("tally_sheets"):
        op.create_table(
            "tally_sheets",
            sa.Column("id", sa.Integer, primary_key=True, index=True),
            sa.Column("company_id", sa.Integer, nullable=False, index=True),
            sa.Column("reference", sa.String(50), nullable=False, index=True),
            sa.Column("escale_id", sa.Integer, nullable=True),
            sa.Column("navire_id", sa.Integer, nullable=True),
            sa.Column("operation_id", sa.Integer, nullable=True),
            sa.Column("type_operation", sa.String(30), nullable=True),
            sa.Column("date_tally", sa.Date, nullable=True),
            sa.Column("poste_quai", sa.String(50), nullable=True),
            sa.Column("numero_cale", sa.String(20), nullable=True),
            sa.Column("poids_manifeste_t", sa.Numeric, nullable=True),
            sa.Column("poids_tally_t", sa.Numeric, nullable=True),
            sa.Column("colis_manifeste", sa.Integer, nullable=True),
            sa.Column("colis_tally", sa.Integer, nullable=True),
            sa.Column("ecart_poids_t", sa.Numeric, nullable=True),
            sa.Column("ecart_colis", sa.Integer, nullable=True),
            sa.Column("nombre_avaries", sa.Integer, nullable=True),
            sa.Column("tallyeur", sa.String(100), nullable=True),
            sa.Column("contre_tallyeur", sa.String(100), nullable=True),
            sa.Column("valide", sa.Boolean, nullable=True),
            sa.Column("date_validation", sa.DateTime(timezone=True), nullable=True),
            sa.Column("notes", sa.Text, nullable=True),
            sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
            sa.Column("updated_at", sa.DateTime(timezone=True), nullable=True),
            sa.UniqueConstraint("company_id", "reference", name="uix_tally_company_ref"),
        )

    if not _has("demurrage_cases"):
        op.create_table(
            "demurrage_cases",
            sa.Column("id", sa.Integer, primary_key=True, index=True),
            sa.Column("company_id", sa.Integer, nullable=False, index=True),
            sa.Column("reference", sa.String(50), nullable=False, index=True),
            sa.Column("escale_id", sa.Integer, nullable=True),
            sa.Column("navire_id", sa.Integer, nullable=True),
            sa.Column("conteneur_id", sa.Integer, nullable=True),
            sa.Column("client_id", sa.Integer, nullable=True),
            sa.Column("date_debut_franchise", sa.Date, nullable=True),
            sa.Column("date_fin_franchise", sa.Date, nullable=True),
            sa.Column("date_retrait_reelle", sa.Date, nullable=True),
            sa.Column("nb_jours_facturables", sa.Integer, nullable=True),
            sa.Column("tarif_journalier_xaf", sa.Numeric, nullable=True),
            sa.Column("montant_total_xaf", sa.Numeric, nullable=True),
            sa.Column("statut", sa.String(30), nullable=True),
            sa.Column("facture_id", sa.Integer, nullable=True),
            sa.Column("litige_declare", sa.Boolean, nullable=True),
            sa.Column("motif_litige", sa.Text, nullable=True),
            sa.Column("notes", sa.Text, nullable=True),
            sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
            sa.Column("updated_at", sa.DateTime(timezone=True), nullable=True),
            sa.UniqueConstraint("company_id", "reference", name="uix_demurrage_company_ref"),
        )

    if not _has("gate_passes"):
        op.create_table(
            "gate_passes",
            sa.Column("id", sa.Integer, primary_key=True, index=True),
            sa.Column("company_id", sa.Integer, nullable=False, index=True),
            sa.Column("numero_gate", sa.String(50), nullable=False, index=True),
            sa.Column("type_sortie", sa.String(30), nullable=True),
            sa.Column("conteneur_id", sa.Integer, nullable=True),
            sa.Column("camion_immatriculation", sa.String(30), nullable=True),
            sa.Column("chauffeur_nom", sa.String(100), nullable=True),
            sa.Column("chauffeur_telephone", sa.String(30), nullable=True),
            sa.Column("statut", sa.String(30), nullable=True),
            sa.Column("date_emission", sa.DateTime(timezone=True), nullable=True),
            sa.Column("date_passage", sa.DateTime(timezone=True), nullable=True),
            sa.Column("poste_controle", sa.String(50), nullable=True),
            sa.Column("agent_poste", sa.String(100), nullable=True),
            sa.Column("poids_camion_kg", sa.Numeric, nullable=True),
            sa.Column("poids_charge_kg", sa.Numeric, nullable=True),
            sa.Column("bl_reference", sa.String(50), nullable=True),
            sa.Column("livraison_client", sa.String(200), nullable=True),
            sa.Column("valide_par", sa.String(100), nullable=True),
            sa.Column("notes", sa.Text, nullable=True),
            sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
            sa.Column("updated_at", sa.DateTime(timezone=True), nullable=True),
            sa.UniqueConstraint("company_id", "numero_gate", name="uix_gate_company_num"),
        )

    if not _has("yard_operations"):
        op.create_table(
            "yard_operations",
            sa.Column("id", sa.Integer, primary_key=True, index=True),
            sa.Column("company_id", sa.Integer, nullable=False, index=True),
            sa.Column("reference", sa.String(50), nullable=False, index=True),
            sa.Column("conteneur_id", sa.Integer, nullable=True),
            sa.Column("type_mouvement", sa.String(30), nullable=True),
            sa.Column("emplacement_source", sa.String(50), nullable=True),
            sa.Column("emplacement_destination", sa.String(50), nullable=True),
            sa.Column("zone_yard", sa.String(50), nullable=True),
            sa.Column("date_operation", sa.DateTime(timezone=True), nullable=True),
            sa.Column("equipment_id", sa.Integer, nullable=True),
            sa.Column("operateur_equipment", sa.String(100), nullable=True),
            sa.Column("poids_conteneur_t", sa.Numeric, nullable=True),
            sa.Column("statut", sa.String(30), nullable=True),
            sa.Column("reference_gate_pass", sa.String(50), nullable=True),
            sa.Column("reference_escale", sa.String(50), nullable=True),
            sa.Column("notes", sa.Text, nullable=True),
            sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
            sa.Column("updated_at", sa.DateTime(timezone=True), nullable=True),
            sa.UniqueConstraint("company_id", "reference", name="uix_yardop_company_ref"),
        )


def downgrade():
    for t in reversed(TABLES):
        if _has(t):
            op.drop_table(t)
