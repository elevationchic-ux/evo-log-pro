"""Schemas Pydantic des modeles approfondis d'operations portuaires.

Chaque schema de reponse (Out) porte les champs EXACTS que le serveur serialise.
Les schemas de creation exigent les champs obligatoires, ceux de mise a jour
rendent tout optionnel (exclude_unset = seul ce qui est fourni ecrase).
"""
from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime, date


# ─── DraftSurvey ──────────────────────────────────────────────────────────────

class DraftSurveyCreate(BaseModel):
    numero_constat: str
    navire_id: Optional[int] = None
    escale_id: Optional[int] = None
    date_constat: Optional[date] = None
    lieu_constat: Optional[str] = None
    tirant_eau_avant: Optional[float] = None
    tirant_eau_arriere: Optional[float] = None
    type_avarie: Optional[str] = None
    gravite: Optional[str] = None
    description: Optional[str] = None
    statut: Optional[str] = None
    inspecteur: Optional[str] = None
    capitaine_signataire: Optional[str] = None
    notes: Optional[str] = None
    source_reference: Optional[str] = None


class DraftSurveyUpdate(BaseModel):
    numero_constat: Optional[str] = None
    navire_id: Optional[int] = None
    escale_id: Optional[int] = None
    date_constat: Optional[date] = None
    lieu_constat: Optional[str] = None
    tirant_eau_avant: Optional[float] = None
    tirant_eau_arriere: Optional[float] = None
    type_avarie: Optional[str] = None
    gravite: Optional[str] = None
    description: Optional[str] = None
    statut: Optional[str] = None
    inspecteur: Optional[str] = None
    capitaine_signataire: Optional[str] = None
    notes: Optional[str] = None
    source_reference: Optional[str] = None


class DraftSurveyOut(BaseModel):
    id: int
    company_id: int
    numero_constat: str
    navire_id: Optional[int] = None
    escale_id: Optional[int] = None
    date_constat: Optional[date] = None
    lieu_constat: Optional[str] = None
    tirant_eau_avant: Optional[float] = None
    tirant_eau_arriere: Optional[float] = None
    type_avarie: Optional[str] = None
    gravite: Optional[str] = None
    description: Optional[str] = None
    photos_jointes: Optional[str] = None
    statut: Optional[str] = None
    inspecteur: Optional[str] = None
    capitaine_signataire: Optional[str] = None
    notes: Optional[str] = None
    source_reference: Optional[str] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    model_config = {"from_attributes": True}


# ─── StevedoringCrew ─────────────────────────────────────────────────────────

class StevedoringCrewCreate(BaseModel):
    code_gang: str
    nom_gang: Optional[str] = None
    type_equipe: Optional[str] = None
    statut: Optional[str] = None
    chef_gang: Optional[str] = None
    nombre_membres: Optional[int] = None
    specialites: Optional[str] = None
    certification: Optional[str] = None
    date_expiration_certification: Optional[date] = None
    telephone_chef: Optional[str] = None
    notes: Optional[str] = None


class StevedoringCrewUpdate(BaseModel):
    code_gang: Optional[str] = None
    nom_gang: Optional[str] = None
    type_equipe: Optional[str] = None
    statut: Optional[str] = None
    chef_gang: Optional[str] = None
    nombre_membres: Optional[int] = None
    specialites: Optional[str] = None
    certification: Optional[str] = None
    date_expiration_certification: Optional[date] = None
    telephone_chef: Optional[str] = None
    notes: Optional[str] = None
    is_active: Optional[bool] = None


class StevedoringCrewOut(BaseModel):
    id: int
    company_id: int
    code_gang: str
    nom_gang: Optional[str] = None
    type_equipe: Optional[str] = None
    statut: Optional[str] = None
    chef_gang: Optional[str] = None
    nombre_membres: Optional[int] = None
    specialites: Optional[str] = None
    certification: Optional[str] = None
    date_expiration_certification: Optional[date] = None
    telephone_chef: Optional[str] = None
    notes: Optional[str] = None
    is_active: bool
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    model_config = {"from_attributes": True}


# ─── CargoHandlingPlan ────────────────────────────────────────────────────────

class CargoHandlingPlanCreate(BaseModel):
    reference_plan: str
    escale_id: Optional[int] = None
    navire_id: Optional[int] = None
    type_operation: Optional[str] = None
    statut: Optional[str] = None
    numero_cale: Optional[str] = None
    poids_total_tonnes: Optional[float] = None
    nombre_colis: Optional[int] = None
    nombre_conteneurs: Optional[int] = None
    date_debut_prevue: Optional[datetime] = None
    date_fin_prevue: Optional[datetime] = None
    date_debut_reelle: Optional[datetime] = None
    date_fin_reelle: Optional[datetime] = None
    cadence_prevue_t_h: Optional[float] = None
    cadence_reelle_t_h: Optional[float] = None
    gang_id: Optional[int] = None
    equipement_id: Optional[int] = None
    charge_a_bord_port: Optional[str] = None
    decharge_a_quai_port: Optional[str] = None
    notes: Optional[str] = None


class CargoHandlingPlanUpdate(BaseModel):
    reference_plan: Optional[str] = None
    escale_id: Optional[int] = None
    navire_id: Optional[int] = None
    type_operation: Optional[str] = None
    statut: Optional[str] = None
    numero_cale: Optional[str] = None
    poids_total_tonnes: Optional[float] = None
    nombre_colis: Optional[int] = None
    nombre_conteneurs: Optional[int] = None
    date_debut_prevue: Optional[datetime] = None
    date_fin_prevue: Optional[datetime] = None
    date_debut_reelle: Optional[datetime] = None
    date_fin_reelle: Optional[datetime] = None
    cadence_prevue_t_h: Optional[float] = None
    cadence_reelle_t_h: Optional[float] = None
    gang_id: Optional[int] = None
    equipement_id: Optional[int] = None
    charge_a_bord_port: Optional[str] = None
    decharge_a_quai_port: Optional[str] = None
    notes: Optional[str] = None


class CargoHandlingPlanOut(BaseModel):
    id: int
    company_id: int
    reference_plan: str
    escale_id: Optional[int] = None
    navire_id: Optional[int] = None
    type_operation: Optional[str] = None
    statut: Optional[str] = None
    numero_cale: Optional[str] = None
    poids_total_tonnes: Optional[float] = None
    nombre_colis: Optional[int] = None
    nombre_conteneurs: Optional[int] = None
    date_debut_prevue: Optional[datetime] = None
    date_fin_prevue: Optional[datetime] = None
    date_debut_reelle: Optional[datetime] = None
    date_fin_reelle: Optional[datetime] = None
    cadence_prevue_t_h: Optional[float] = None
    cadence_reelle_t_h: Optional[float] = None
    gang_id: Optional[int] = None
    equipement_id: Optional[int] = None
    charge_a_bord_port: Optional[str] = None
    decharge_a_quai_port: Optional[str] = None
    notes: Optional[str] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    model_config = {"from_attributes": True}


# ─── QuayEquipment ────────────────────────────────────────────────────────────

class QuayEquipmentCreate(BaseModel):
    code_equipement: str
    designation: str
    type_equipement: Optional[str] = None
    etat: Optional[str] = None
    marque: Optional[str] = None
    modele: Optional[str] = None
    capacite_max_tonnes: Optional[float] = None
    portee_max_m: Optional[float] = None
    annee_mise_service: Optional[int] = None
    fournisseur: Optional[str] = None
    numero_serial: Optional[str] = None
    prochaine_maintenance_date: Optional[date] = None
    poste_quai_assigne: Optional[str] = None
    cout_acquisition_xaf: Optional[float] = None
    notes: Optional[str] = None


class QuayEquipmentUpdate(BaseModel):
    code_equipement: Optional[str] = None
    designation: Optional[str] = None
    type_equipement: Optional[str] = None
    etat: Optional[str] = None
    marque: Optional[str] = None
    modele: Optional[str] = None
    capacite_max_tonnes: Optional[float] = None
    portee_max_m: Optional[float] = None
    annee_mise_service: Optional[int] = None
    fournisseur: Optional[str] = None
    numero_serial: Optional[str] = None
    prochaine_maintenance_date: Optional[date] = None
    heures_service_cumulees: Optional[float] = None
    poste_quai_assigne: Optional[str] = None
    cout_acquisition_xaf: Optional[float] = None
    notes: Optional[str] = None
    is_active: Optional[bool] = None


class QuayEquipmentOut(BaseModel):
    id: int
    company_id: int
    code_equipement: str
    designation: str
    type_equipement: Optional[str] = None
    etat: Optional[str] = None
    marque: Optional[str] = None
    modele: Optional[str] = None
    capacite_max_tonnes: Optional[float] = None
    portee_max_m: Optional[float] = None
    annee_mise_service: Optional[int] = None
    fournisseur: Optional[str] = None
    numero_serial: Optional[str] = None
    prochaine_maintenance_date: Optional[date] = None
    heures_service_cumulees: Optional[float] = None
    poste_quai_assigne: Optional[str] = None
    cout_acquisition_xaf: Optional[float] = None
    notes: Optional[str] = None
    is_active: bool
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    model_config = {"from_attributes": True}


# ─── PilotageSession ─────────────────────────────────────────────────────────

class PilotageSessionCreate(BaseModel):
    reference: str
    navire_id: Optional[int] = None
    escale_id: Optional[int] = None
    pilote_nom: Optional[str] = None
    pilote_matricule: Optional[str] = None
    statut: Optional[str] = None
    type_mouvement: Optional[str] = None
    date_demande: Optional[datetime] = None
    date_debut_reelle: Optional[datetime] = None
    date_fin_reelle: Optional[datetime] = None
    duree_heures: Optional[float] = None
    zone_pilotage: Optional[str] = None
    distance_nautique_mq: Optional[float] = None
    conditions_meteo: Optional[str] = None
    vitesse_navire_noeuds: Optional[float] = None
    tirant_eau_navire_m: Optional[float] = None
    tarif_pilotage_xaf: Optional[float] = None
    notes: Optional[str] = None


class PilotageSessionUpdate(PilotageSessionCreate):
    reference: Optional[str] = None  # type: ignore[assignment]


class PilotageSessionOut(BaseModel):
    id: int
    company_id: int
    reference: str
    navire_id: Optional[int] = None
    escale_id: Optional[int] = None
    pilote_nom: Optional[str] = None
    pilote_matricule: Optional[str] = None
    statut: Optional[str] = None
    type_mouvement: Optional[str] = None
    date_demande: Optional[datetime] = None
    date_debut_reelle: Optional[datetime] = None
    date_fin_reelle: Optional[datetime] = None
    duree_heures: Optional[float] = None
    zone_pilotage: Optional[str] = None
    distance_nautique_mq: Optional[float] = None
    conditions_meteo: Optional[str] = None
    vitesse_navire_noeuds: Optional[float] = None
    tirant_eau_navire_m: Optional[float] = None
    tarif_pilotage_xaf: Optional[float] = None
    notes: Optional[str] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    model_config = {"from_attributes": True}


# ─── TowageOperation ─────────────────────────────────────────────────────────

class TowageOperationCreate(BaseModel):
    reference: str
    navire_id: Optional[int] = None
    escale_id: Optional[int] = None
    remorqueur_nom: Optional[str] = None
    remorqueur_immatriculation: Optional[str] = None
    nombre_remorqueurs: Optional[int] = None
    type_prestation: Optional[str] = None
    statut: Optional[str] = None
    date_debut_reelle: Optional[datetime] = None
    date_fin_reelle: Optional[datetime] = None
    duree_heures: Optional[float] = None
    puissance_bollard_t: Optional[float] = None
    zone_operation: Optional[str] = None
    tarif_xaf: Optional[float] = None
    operateur: Optional[str] = None
    conditions_meteo: Optional[str] = None
    notes: Optional[str] = None


class TowageOperationUpdate(TowageOperationCreate):
    reference: Optional[str] = None  # type: ignore[assignment]


class TowageOperationOut(BaseModel):
    id: int
    company_id: int
    reference: str
    navire_id: Optional[int] = None
    escale_id: Optional[int] = None
    remorqueur_nom: Optional[str] = None
    remorqueur_immatriculation: Optional[str] = None
    nombre_remorqueurs: Optional[int] = None
    type_prestation: Optional[str] = None
    statut: Optional[str] = None
    date_debut_reelle: Optional[datetime] = None
    date_fin_reelle: Optional[datetime] = None
    duree_heures: Optional[float] = None
    puissance_bollard_t: Optional[float] = None
    zone_operation: Optional[str] = None
    tarif_xaf: Optional[float] = None
    operateur: Optional[str] = None
    conditions_meteo: Optional[str] = None
    notes: Optional[str] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    model_config = {"from_attributes": True}


# ─── BunkeringOrder ──────────────────────────────────────────────────────────

class BunkeringOrderCreate(BaseModel):
    reference: str
    navire_id: Optional[int] = None
    escale_id: Optional[int] = None
    type_carburant: Optional[str] = None
    quantite_tonnes: Optional[float] = None
    densite: Optional[float] = None
    soufre_pct: Optional[float] = None
    prix_tonne_xaf: Optional[float] = None
    montant_total_xaf: Optional[float] = None
    fournisseur: Optional[str] = None
    barge_nom: Optional[str] = None
    date_operation: Optional[datetime] = None
    statut: Optional[str] = None
    bon_livraison_ref: Optional[str] = None
    notes: Optional[str] = None


class BunkeringOrderUpdate(BunkeringOrderCreate):
    reference: Optional[str] = None  # type: ignore[assignment]


class BunkeringOrderOut(BaseModel):
    id: int
    company_id: int
    reference: str
    navire_id: Optional[int] = None
    escale_id: Optional[int] = None
    type_carburant: Optional[str] = None
    quantite_tonnes: Optional[float] = None
    densite: Optional[float] = None
    soufre_pct: Optional[float] = None
    prix_tonne_xaf: Optional[float] = None
    montant_total_xaf: Optional[float] = None
    fournisseur: Optional[str] = None
    barge_nom: Optional[str] = None
    date_operation: Optional[datetime] = None
    heure_debut: Optional[str] = None
    heure_fin: Optional[str] = None
    debit_t_h: Optional[float] = None
    statut: Optional[str] = None
    bon_livraison_ref: Optional[str] = None
    quantite_mesuree_t: Optional[float] = None
    ecart_quantite_t: Optional[float] = None
    capitaine_signataire: Optional[str] = None
    notes: Optional[str] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    model_config = {"from_attributes": True}


# ─── VesselWasteReceipt ──────────────────────────────────────────────────────

class VesselWasteReceiptCreate(BaseModel):
    reference: str
    navire_id: Optional[int] = None
    escale_id: Optional[int] = None
    type_dechet: Optional[str] = None
    quantite: Optional[float] = None
    unite: Optional[str] = None
    date_reception: Optional[datetime] = None
    lieu_depot: Optional[str] = None
    operateur_collecte: Optional[str] = None
    fichier_destinataire: Optional[str] = None
    marpol_annexe: Optional[str] = None
    capitaine_declare: Optional[str] = None
    recu_par: Optional[str] = None
    conforme: Optional[bool] = None
    notes: Optional[str] = None


class VesselWasteReceiptUpdate(VesselWasteReceiptCreate):
    reference: Optional[str] = None  # type: ignore[assignment]


class VesselWasteReceiptOut(BaseModel):
    id: int
    company_id: int
    reference: str
    navire_id: Optional[int] = None
    escale_id: Optional[int] = None
    type_dechet: Optional[str] = None
    quantite: Optional[float] = None
    unite: Optional[str] = None
    date_reception: Optional[datetime] = None
    lieu_depot: Optional[str] = None
    operateur_collecte: Optional[str] = None
    fichier_destinataire: Optional[str] = None
    cout_collecte_xaf: Optional[int] = None
    numero_manifeste_dechet: Optional[str] = None
    marpol_annexe: Optional[str] = None
    capitaine_declare: Optional[str] = None
    recu_par: Optional[str] = None
    conforme: Optional[bool] = None
    notes: Optional[str] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    model_config = {"from_attributes": True}


# ─── TallySheet ──────────────────────────────────────────────────────────────

class TallySheetCreate(BaseModel):
    reference: str
    escale_id: Optional[int] = None
    navire_id: Optional[int] = None
    operation_id: Optional[int] = None
    type_operation: Optional[str] = None
    date_tally: Optional[date] = None
    poste_quai: Optional[str] = None
    numero_cale: Optional[str] = None
    poids_manifeste_t: Optional[float] = None
    poids_tally_t: Optional[float] = None
    colis_manifeste: Optional[int] = None
    colis_tally: Optional[int] = None
    nombre_avaries: Optional[int] = None
    tallyeur: Optional[str] = None
    contre_tallyeur: Optional[str] = None
    notes: Optional[str] = None


class TallySheetUpdate(TallySheetCreate):
    reference: Optional[str] = None  # type: ignore[assignment]


class TallySheetOut(BaseModel):
    id: int
    company_id: int
    reference: str
    escale_id: Optional[int] = None
    navire_id: Optional[int] = None
    operation_id: Optional[int] = None
    type_operation: Optional[str] = None
    date_tally: Optional[date] = None
    poste_quai: Optional[str] = None
    numero_cale: Optional[str] = None
    poids_manifeste_t: Optional[float] = None
    poids_tally_t: Optional[float] = None
    colis_manifeste: Optional[int] = None
    colis_tally: Optional[int] = None
    ecart_poids_t: Optional[float] = None
    ecart_colis: Optional[int] = None
    nombre_avaries: Optional[int] = None
    tallyeur: Optional[str] = None
    contre_tallyeur: Optional[str] = None
    valide: Optional[bool] = None
    date_validation: Optional[datetime] = None
    notes: Optional[str] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    model_config = {"from_attributes": True}


# ─── DemurrageCase ───────────────────────────────────────────────────────────

class DemurrageCaseCreate(BaseModel):
    reference: str
    escale_id: Optional[int] = None
    navire_id: Optional[int] = None
    conteneur_id: Optional[int] = None
    client_id: Optional[int] = None
    date_debut_franchise: Optional[date] = None
    date_fin_franchise: Optional[date] = None
    date_retrait_reelle: Optional[date] = None
    nb_jours_facturables: Optional[int] = None
    tarif_journalier_xaf: Optional[float] = None
    montant_total_xaf: Optional[float] = None
    statut: Optional[str] = None
    litige_declare: Optional[bool] = None
    motif_litige: Optional[str] = None
    notes: Optional[str] = None


class DemurrageCaseUpdate(DemurrageCaseCreate):
    reference: Optional[str] = None  # type: ignore[assignment]


class DemurrageCaseOut(BaseModel):
    id: int
    company_id: int
    reference: str
    escale_id: Optional[int] = None
    navire_id: Optional[int] = None
    conteneur_id: Optional[int] = None
    client_id: Optional[int] = None
    date_debut_franchise: Optional[date] = None
    date_fin_franchise: Optional[date] = None
    date_retrait_reelle: Optional[date] = None
    nb_jours_facturables: Optional[int] = None
    tarif_journalier_xaf: Optional[float] = None
    montant_total_xaf: Optional[float] = None
    statut: Optional[str] = None
    facture_id: Optional[int] = None
    litige_declare: Optional[bool] = None
    motif_litige: Optional[str] = None
    notes: Optional[str] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    model_config = {"from_attributes": True}


# ─── GatePass ────────────────────────────────────────────────────────────────

class GatePassCreate(BaseModel):
    numero_gate: str
    type_sortie: Optional[str] = None
    conteneur_id: Optional[int] = None
    camion_immatriculation: Optional[str] = None
    chauffeur_nom: Optional[str] = None
    chauffeur_telephone: Optional[str] = None
    statut: Optional[str] = None
    poste_controle: Optional[str] = None
    agent_poste: Optional[str] = None
    poids_camion_kg: Optional[float] = None
    poids_charge_kg: Optional[float] = None
    bl_reference: Optional[str] = None
    livraison_client: Optional[str] = None
    valide_par: Optional[str] = None
    notes: Optional[str] = None


class GatePassUpdate(GatePassCreate):
    numero_gate: Optional[str] = None  # type: ignore[assignment]


class GatePassOut(BaseModel):
    id: int
    company_id: int
    numero_gate: str
    type_sortie: Optional[str] = None
    conteneur_id: Optional[int] = None
    camion_immatriculation: Optional[str] = None
    chauffeur_nom: Optional[str] = None
    chauffeur_telephone: Optional[str] = None
    statut: Optional[str] = None
    date_emission: Optional[datetime] = None
    date_passage: Optional[datetime] = None
    poste_controle: Optional[str] = None
    agent_poste: Optional[str] = None
    poids_camion_kg: Optional[float] = None
    poids_charge_kg: Optional[float] = None
    bl_reference: Optional[str] = None
    livraison_client: Optional[str] = None
    valide_par: Optional[str] = None
    notes: Optional[str] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    model_config = {"from_attributes": True}


# ─── YardOperation ───────────────────────────────────────────────────────────

class YardOperationCreate(BaseModel):
    reference: str
    conteneur_id: Optional[int] = None
    type_mouvement: Optional[str] = None
    emplacement_source: Optional[str] = None
    emplacement_destination: Optional[str] = None
    zone_yard: Optional[str] = None
    date_operation: Optional[datetime] = None
    equipment_id: Optional[int] = None
    operateur_equipment: Optional[str] = None
    poids_conteneur_t: Optional[float] = None
    statut: Optional[str] = None
    reference_gate_pass: Optional[str] = None
    reference_escale: Optional[str] = None
    notes: Optional[str] = None


class YardOperationUpdate(YardOperationCreate):
    reference: Optional[str] = None  # type: ignore[assignment]


class YardOperationOut(BaseModel):
    id: int
    company_id: int
    reference: str
    conteneur_id: Optional[int] = None
    type_mouvement: Optional[str] = None
    emplacement_source: Optional[str] = None
    emplacement_destination: Optional[str] = None
    zone_yard: Optional[str] = None
    date_operation: Optional[datetime] = None
    equipment_id: Optional[int] = None
    operateur_equipment: Optional[str] = None
    poids_conteneur_t: Optional[float] = None
    statut: Optional[str] = None
    reference_gate_pass: Optional[str] = None
    reference_escale: Optional[str] = None
    notes: Optional[str] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    model_config = {"from_attributes": True}
