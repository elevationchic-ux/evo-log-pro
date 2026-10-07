"""047 : tables operations portuaires approfondies (Wave 1A expansion).

Cree les 12 tables liees au module port_operations_deep.py :
    - draft_surveys, stevedoring_crews, cargo_handling_plans,
      quay_equipments, pilotage_sessions, towage_operations,
      bunkering_orders, vessel_waste_receipts, tally_sheets,
      demurrage_cases, gate_passes, yard_operations

Chaque table porte company_id (multi-tenant) + index de unicité
metier par organisation. Idempotent via introspection.

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
    # (table, columns, unique_constraints)
    ("draft_surveys", [
        ("id", sa.Integer, {"primary_key": True}),
        ("company_id", sa.Integer, {"nullable": False, "index": True}),
        ("numero_constat", sa.String(50), {"nullable": False, "index": True}),
        ("navire_id", sa.Integer, {"nullable": True}),
        ("escale_id", sa.Integer, {"nullable": True}),
        ("date_constat", sa.Date, {"nullable": True}),
        ("lieu_constat", sa.String(100), {"nullable": True}),
        ("tirant_eau_avant", sa.Numeric, {"nullable": True}),
        ("tirant_eau_arriere", sa.Numeric, {"nullable": True}),
        ("type_avarie", sa.String(30), {"nullable": True}),
        ("gravite", sa.String(30), {"nullable": True}),
        ("description", sa.Text, {"nullable": True}),
        ("photos_jointes", sa.Text, {"nullable": True}),
        ("statut", sa.String(30), {"nullable": True}),
        ("inspecteur", sa.String(100), {"nullable": True}),
        ("capitaine_signataire", sa.String(100), {"nullable": True}),
        ("notes", sa.Text, {"nullable": True}),
        ("source_reference", sa.String(200), {"nullable": True}),
        ("created_at", sa.DateTime(timezone=True), {"nullable": True}),
        ("updated_at", sa.DateTime(timezone=True), {"nullable": True}),
    ], [("uix_draft_survey_company_num", ["company_id", "numero_constat"])]),

    ("stevedoring_crews", [
        ("id", sa.Integer, {"primary_key": True}),
        ("company_id", sa.Integer, {"nullable": False, "index": True}),
        ("code_gang", sa.String(30), {"nullable": False, "index": True}),
        ("nom_gang", sa.String(100), {"nullable": True}),
        ("type_equipe", sa.String(30), {"nullable": True}),
        ("statut", sa.String(30), {"nullable": True}),
        ("chef_gang", sa.String(100), {"nullable": True}),
        ("nombre_membres", sa.Integer, {"nullable": True}),
        ("specialites", sa.Text, {"nullable": True}),
        ("certification", sa.String(100), {"nullable": True}),
        ("date_expiration_certification", sa.Date, {"nullable": True}),
        ("telephone_chef", sa.String(30), {"nullable": True}),
        ("notes", sa.Text, {"nullable": True}),
        ("is_active", sa.Boolean, {"nullable": True}),
        ("created_at", sa.DateTime(timezone=True), {"nullable": True}),
        ("updated_at", sa.DateTime(timezone=True), {"nullable": True}),
    ], [("uix_crew_company_code", ["company_id", "code_gang"])]),

    ("cargo_handling_plans", [
        ("id", sa.Integer, {"primary_key": True}),
        ("company_id", sa.Integer, {"nullable": False, "index": True}),
        ("reference_plan", sa.String(50), {"nullable": False, "index": True}),
        ("escale_id", sa.Integer, {"nullable": True}),
        ("navire_id", sa.Integer, {"nullable": True}),
        ("type_operation", sa.String(30), {"nullable": True}),
        ("statut", sa.String(30), {"nullable": True}),
        ("numero_cale", sa.String(20), {"nullable": True}),
        ("poids_total_tonnes", sa.Numeric, {"nullable": True}),
        ("nombre_colis", sa.Integer, {"nullable": True}),
        ("nombre_conteneurs", sa.Integer, {"nullable": True}),
        ("date_debut_prevue", sa.DateTime(timezone=True), {"nullable": True}),
        ("date_fin_prevue", sa.DateTime(timezone=True), {"nullable": True}),
        ("date_debut_reelle", sa.DateTime(timezone=True), {"nullable": True}),
        ("date_fin_reelle", sa.DateTime(timezone=True), {"nullable": True}),
        ("cadence_prevue_t_h", sa.Numeric, {"nullable": True}),
        ("cadence_reelle_t_h", sa.Numeric, {"nullable": True}),
        ("gang_id", sa.Integer, {"nullable": True}),
        ("equipement_id", sa.Integer, {"nullable": True}),
        ("charge_a_bord_port", sa.String(100), {"nullable": True}),
        ("decharge_a_quai_port", sa.String(100), {"nullable": True}),
        ("notes", sa.Text, {"nullable": True}),
        ("created_at", sa.DateTime(timezone=True), {"nullable": True}),
        ("updated_at", sa.DateTime(timezone=True), {"nullable": True}),
    ], [("uix_cargo_plan_company_ref", ["company_id", "reference_plan"])]),

    ("quay_equipments", [
        ("id", sa.Integer, {"primary_key": True}),
        ("company_id", sa.Integer, {"nullable": False, "index": True}),
        ("code_equipement", sa.String(50), {"nullable": False, "index": True}),
        ("designation", sa.String(200), {"nullable": False}),
        ("type_equipement", sa.String(30), {"nullable": True}),
        ("etat", sa.String(30), {"nullable": True}),
        ("marque", sa.String(100), {"nullable": True}),
        ("modele", sa.String(100), {"nullable": True}),
        ("capacite_max_tonnes", sa.Numeric, {"nullable": True}),
        ("portee_max_m", sa.Numeric, {"nullable": True}),
        ("hauteur_sous_flèche_m", sa.Numeric, {"nullable": True}),
        ("annee_mise_service", sa.Integer, {"nullable": True}),
        ("fournisseur", sa.String(200), {"nullable": True}),
        ("numero_serial", sa.String(100), {"nullable": True}),
        ("prochaine_maintenance_date", sa.Date, {"nullable": True}),
        ("prochaine_maintenance_km", sa.Numeric, {"nullable": True}),
        ("heures_service_cumulees", sa.Numeric, {"nullable": True}),
        ("poste_quai_assigne", sa.String(50), {"nullable": True}),
        ("cout_acquisition_xaf", sa.Numeric, {"nullable": True}),
        ("notes", sa.Text, {"nullable": True}),
        ("is_active", sa.Boolean, {"nullable": True}),
        ("created_at", sa.DateTime(timezone=True), {"nullable": True}),
        ("updated_at", sa.DateTime(timezone=True), {"nullable": True}),
    ], [("uix_equip_company_code", ["company_id", "code_equipement"])]),

    ("pilotage_sessions", [
        ("id", sa.Integer, {"primary_key": True}),
        ("company_id", sa.Integer, {"nullable": False, "index": True}),
        ("reference", sa.String(50), {"nullable": False, "index": True}),
        ("navire_id", sa.Integer, {"nullable": True}),
        ("escale_id", sa.Integer, {"nullable": True}),
        ("pilote_nom", sa.String(100), {"nullable": True}),
        ("pilote_matricule", sa.String(50), {"nullable": True}),
        ("statut", sa.String(30), {"nullable": True}),
        ("type_mouvement", sa.String(30), {"nullable": True}),
        ("date_demande", sa.DateTime(timezone=True), {"nullable": True}),
        ("date_debut_reelle", sa.DateTime(timezone=True), {"nullable": True}),
        ("date_fin_reelle", sa.DateTime(timezone=True), {"nullable": True}),
        ("duree_heures", sa.Numeric, {"nullable": True}),
        ("zone_pilotage", sa.String(100), {"nullable": True}),
        ("distance_nautique_mq", sa.Numeric, {"nullable": True}),
        ("conditions_meteo", sa.String(200), {"nullable": True}),
        ("vitesse_navire_noeuds", sa.Numeric, {"nullable": True}),
        ("tirant_eau_navire_m", sa.Numeric, {"nullable": True}),
        ("tarif_pilotage_xaf", sa.Numeric, {"nullable": True}),
        ("notes", sa.Text, {"nullable": True}),
        ("created_at", sa.DateTime(timezone=True), {"nullable": True}),
        ("updated_at", sa.DateTime(timezone=True), {"nullable": True}),
    ], [("uix_pilotage_company_ref", ["company_id", "reference"])]),

    ("towage_operations", [
        ("id", sa.Integer, {"primary_key": True}),
        ("company_id", sa.Integer, {"nullable": False, "index": True}),
        ("reference", sa.String(50), {"nullable": False, "index": True}),
        ("navire_id", sa.Integer, {"nullable": True}),
        ("escale_id", sa.Integer, {"nullable": True}),
        ("remorqueur_nom", sa.String(100), {"nullable": True}),
        ("remorqueur_immatriculation", sa.String(50), {"nullable": True}),
        ("nombre_remorqueurs", sa.Integer, {"nullable": True}),
        ("type_prestation", sa.String(50), {"nullable": True}),
        ("statut", sa.String(30), {"nullable": True}),
        ("date_debut_reelle", sa.DateTime(timezone=True), {"nullable": True}),
        ("date_fin_reelle", sa.DateTime(timezone=True), {"nullable": True}),
        ("duree_heures", sa.Numeric, {"nullable": True}),
        ("puissance_bollard_t", sa.Numeric, {"nullable": True}),
        ("zone_operation", sa.String(100), {"nullable": True}),
        ("tarif_xaf", sa.Numeric, {"nullable": True}),
        ("operateur", sa.String(200), {"nullable": True}),
        ("conditions_meteo", sa.String(200), {"nullable": True}),
        ("notes", sa.Text, {"nullable": True}),
        ("created_at", sa.DateTime(timezone=True), {"nullable": True}),
        ("updated_at", sa.DateTime(timezone=True), {"nullable": True}),
    ], [("uix_towage_company_ref", ["company_id", "reference"])]),

    ("bunkering_orders", [
        ("id", sa.Integer, {"primary_key": True}),
        ("company_id", sa.Integer, {"nullable": False, "index": True}),
        ("reference", sa.String(50), {"nullable": False, "index": True}),
        ("navire_id", sa.Integer, {"nullable": True}),
        ("escale_id", sa.Integer, {"nullable": True}),
        ("type_carburant", sa.String(30), {"nullable": True}),
        ("quantite_tonnes", sa.Numeric, {"nullable": True}),
        ("densite", sa.Numeric, {"nullable": True}),
        ("soufre_pct", sa.Numeric, {"nullable": True}),
        ("prix_tonne_xaf", sa.Numeric, {"nullable": True}),
        ("montant_total_xaf", sa.Numeric, {"nullable": True}),
        ("fournisseur", sa.String(200), {"nullable": True}),
        ("barge_nom", sa.String(100), {"nullable": True}),
        ("date_operation", sa.DateTime(timezone=True), {"nullable": True}),
        ("heure_debut", sa.String(10), {"nullable": True}),
        ("heure_fin", sa.String(10), {"nullable": True}),
        ("debit_t_h", sa.Numeric, {"nullable": True}),
        ("statut", sa.String(30), {"nullable": True}),
        ("bon_livraison_ref", sa.String(100), {"nullable": True}),
        ("quantitemesuree_t", sa.Numeric, {"nullable": True}),
        ("ecart_quantite_t", sa.Numeric, {"nullable": True}),
        ("capitaine_signataire", sa.String(100), {"nullable": True}),
        ("notes", sa.Text, {"nullable": True}),
        ("created_at", sa.DateTime(timezone=True), {"nullable": True}),
        ("updated_at", sa.DateTime(timezone=True), {"nullable": True}),
    ], [("uix_bunker_company_ref", ["company_id", "reference"])]),

    ("vessel_waste_receipts", [
        ("id", sa.Integer, {"primary_key": True}),
        ("company_id", sa.Integer, {"nullable": False, "index": True}),
        ("reference", sa.String(50), {"nullable": False, "index": True}),
        ("navire_id", sa.Integer, {"nullable": True}),
        ("escale_id", sa.Integer, {"nullable": True}),
        ("type_dechet", sa.String(30), {"nullable": True}),
        ("quantite", sa.Numeric, {"nullable": True}),
        ("unite", sa.String(20), {"nullable": True}),
        ("date_reception", sa.DateTime(timezone=True), {"nullable": True}),
        ("lieu_depot", sa.String(200), {"nullable": True}),
        ("operateur_collecte", sa.String(200), {"nullable": True}),
        ("fichier_destinataire", sa.String(200), {"nullable": True}),
        ("cout_collecte_xaf", sa.Integer, {"nullable": True}),
        ("numero_manifeste_dechet", sa.String(100), {"nullable": True}),
        ("marpol_annexe", sa.String(10), {"nullable": True}),
        ("capitaine_declare", sa.String(100), {"nullable": True}),
        ("recu_par", sa.String(100), {"nullable": True}),
        ("conforme", sa.Boolean, {"nullable": True}),
        ("notes", sa.Text, {"nullable": True}),
        ("created_at", sa.DateTime(timezone=True), {"nullable": True}),
        ("updated_at", sa.DateTime(timezone=True), {"nullable": True}),
    ], [("uix_waste_company_ref", ["company_id", "reference"])]),

    ("tally_sheets", [
        ("id", sa.Integer, {"primary_key": True}),
        ("company_id", sa.Integer, {"nullable": False, "index": True}),
        ("reference", sa.String(50), {"nullable": False, "index": True}),
        ("escale_id", sa.Integer, {"nullable": True}),
        ("navire_id", sa.Integer, {"nullable": True}),
        ("operation_id", sa.Integer, {"nullable": True}),
        ("type_operation", sa.String(30), {"nullable": True}),
        ("date_tally", sa.Date, {"nullable": True}),
        ("poste_quai", sa.String(50), {"nullable": True}),
        ("numero_cale", sa.String(20), {"nullable": True}),
        ("poids_manifeste_t", sa.Numeric, {"nullable": True}),
        ("poids_tally_t", sa.Numeric, {"nullable": True}),
        ("colis_manifeste", sa.Integer, {"nullable": True}),
        ("colis_tally", sa.Integer, {"nullable": True}),
        ("ecart_poids_t", sa.Numeric, {"nullable": True}),
        ("ecart_colis", sa.Integer, {"nullable": True}),
        ("nombre_avaries", sa.Integer, {"nullable": True}),
        ("tallyeur", sa.String(100), {"nullable": True}),
        ("contre_tallyeur", sa.String(100), {"nullable": True}),
        ("valide", sa.Boolean, {"nullable": True}),
        ("date_validation", sa.DateTime(timezone=True), {"nullable": True}),
        ("notes", sa.Text, {"nullable": True}),
        ("created_at", sa.DateTime(timezone=True), {"nullable": True}),
        ("updated_at", sa.DateTime(timezone=True), {"nullable": True}),
    ], [("uix_tally_company_ref", ["company_id", "reference"])]),

    ("demurrage_cases", [
        ("id", sa.Integer, {"primary_key": True}),
        ("company_id", sa.Integer, {"nullable": False, "index": True}),
        ("reference", sa.String(50), {"nullable": False, "index": True}),
        ("escale_id", sa.Integer, {"nullable": True}),
        ("navire_id", sa.Integer, {"nullable": True}),
        ("conteneur_id", sa.Integer, {"nullable": True}),
        ("client_id", sa.Integer, {"nullable": True}),
        ("date_debut_franchise", sa.Date, {"nullable": True}),
        ("date_fin_franchise", sa.Date, {"nullable": True}),
        ("date_retrait_reelle", sa.Date, {"nullable": True}),
        ("nb_jours_facturables", sa.Integer, {"nullable": True}),
        ("tarif_journalier_xaf", sa.Numeric, {"nullable": True}),
        ("montant_total_xaf", sa.Numeric, {"nullable": True}),
        ("statut", sa.String(30), {"nullable": True}),
        ("facture_id", sa.Integer, {"nullable": True}),
        ("litige_declare", sa.Boolean, {"nullable": True}),
        ("motif_litige", sa.Text, {"nullable": True}),
        ("notes", sa.Text, {"nullable": True}),
        ("created_at", sa.DateTime(timezone=True), {"nullable": True}),
        ("updated_at", sa.DateTime(timezone=True), {"nullable": True}),
    ], [("uix_demurrage_company_ref", ["company_id", "reference"])]),

    ("gate_passes", [
        ("id", sa.Integer, {"primary_key": True}),
        ("company_id", sa.Integer, {"nullable": False, "index": True}),
        ("numero_gate", sa.String(50), {"nullable": False, "index": True}),
        ("type_sortie", sa.String(30), {"nullable": True}),
        ("conteneur_id", sa.Integer, {"nullable": True}),
        ("camion_immatriculation", sa.String(30), {"nullable": True}),
        ("chauffeur_nom", sa.String(100), {"nullable": True}),
        ("chauffeur_telephone", sa.String(30), {"nullable": True}),
        ("statut", sa.String(30), {"nullable": True}),
        ("date_emission", sa.DateTime(timezone=True), {"nullable": True}),
        ("date_passage", sa.DateTime(timezone=True), {"nullable": True}),
        ("poste_controle", sa.String(50), {"nullable": True}),
        ("agent_poste", sa.String(100), {"nullable": True}),
        ("poids_camion_kg", sa.Numeric, {"nullable": True}),
        ("poids_charge_kg", sa.Numeric, {"nullable": True}),
        ("bl_reference", sa.String(50), {"nullable": True}),
        ("livraison_client", sa.String(200), {"nullable": True}),
        ("valide_par", sa.String(100), {"nullable": True}),
        ("notes", sa.Text, {"nullable": True}),
        ("created_at", sa.DateTime(timezone=True), {"nullable": True}),
        ("updated_at", sa.DateTime(timezone=True), {"nullable": True}),
    ], [("uix_gate_company_num", ["company_id", "numero_gate"])]),

    ("yard_operations", [
        ("id", sa.Integer, {"primary_key": True}),
        ("company_id", sa.Integer, {"nullable": False, "index": True}),
        ("reference", sa.String(50), {"nullable": False, "index": True}),
        ("conteneur_id", sa.Integer, {"nullable": True}),
        ("type_mouvement", sa.String(30), {"nullable": True}),
        ("emplacement_source", sa.String(50), {"nullable": True}),
        ("emplacement_destination", sa.String(50), {"nullable": True}),
        ("zone_yard", sa.String(50), {"nullable": True}),
        ("date_operation", sa.DateTime(timezone=True), {"nullable": True}),
        ("equipment_id", sa.Integer, {"nullable": True}),
        ("operateur_equipment", sa.String(100), {"nullable": True}),
        ("poids_conteneur_t", sa.Numeric, {"nullable": True}),
        ("statut", sa.String(30), {"nullable": True}),
        ("reference_gate_pass", sa.String(50), {"nullable": True}),
        ("reference_escale", sa.String(50), {"nullable": True}),
        ("notes", sa.Text, {"nullable": True}),
        ("created_at", sa.DateTime(timezone=True), {"nullable": True}),
        ("updated_at", sa.DateTime(timezone=True), {"nullable": True}),
    ], [("uix_yardop_company_ref", ["company_id", "reference"])]),
]


def _bind(col_spec):
    name, typ, kwargs = col_spec
    clean = {k: v for k, v in kwargs.items() if k not in ("primary_key", "index")}
    return sa.Column(name, typ, **clean)


def upgrade() -> None:
    bind = op.get_bind()
    import sqlalchemy as _sa
    insp = _sa.inspect(bind)
    existing = set(insp.get_table_names())
    for tname, cols, uniques in TABLES:
        if tname in existing:
            continue
        sa_cols = [_bind(c) for c in cols]
        for c in cols:
            if c[2].get("primary_key"):
                pass
        op.create_table(
            tname,
            *_bind_cols(cols),
        )
        for cname, kwargs in [(c[0], c[2]) for c in cols]:
            pass
        # indexes
        for c in cols:
            if c[2].get("index"):
                op.create_index(f"ix_{tname}_{c[0]}", tname, [c[0]])
        for uname, ucols in uniques:
            op.create_unique_constraint(uname, tname, ucols)


def _bind_cols(cols):
    out = []
    for name, typ, kwargs in cols:
        clean = {k: v for k, v in kwargs.items() if k not in ("primary_key", "index")}
        col = sa.Column(name, typ, **clean)
        if kwargs.get("primary_key"):
            col.primary_key = True
        out.append(col)
    return out


def downgrade() -> None:
    for tname, _cols, _uniques in reversed(TABLES):
        op.drop_table(tname)
