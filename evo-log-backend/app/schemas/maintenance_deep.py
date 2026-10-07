"""Schemas Pydantic auto-genere (expansion wave 6)."""
from pydantic import BaseModel
from typing import Optional
from datetime import datetime, date


class TechnicalAssetCreate(BaseModel):
    tag_actif: str
    nom: str
    categorie: Optional[str] = None
    sous_categorie: Optional[str] = None
    module_source: Optional[str] = None
    ref_entite_source: Optional[str] = None
    parent_id: Optional[int] = None
    emplacement: Optional[str] = None
    fabricant: Optional[str] = None
    modele: Optional[str] = None
    numero_serie: Optional[str] = None
    annee_fabrication: Optional[int] = None
    date_mise_service: Optional[date] = None
    criticite: Optional[str] = None
    statut: Optional[str] = None
    cout_acquisition_xaf: Optional[float] = None
    valeur_residuelle_xaf: Optional[float] = None
    duree_vieutile_ans: Optional[int] = None
    notes_techniques: Optional[str] = None


class TechnicalAssetUpdate(BaseModel):
    tag_actif: Optional[str] = None
    nom: Optional[str] = None
    categorie: Optional[str] = None
    sous_categorie: Optional[str] = None
    module_source: Optional[str] = None
    ref_entite_source: Optional[str] = None
    parent_id: Optional[int] = None
    emplacement: Optional[str] = None
    fabricant: Optional[str] = None
    modele: Optional[str] = None
    numero_serie: Optional[str] = None
    annee_fabrication: Optional[int] = None
    date_mise_service: Optional[date] = None
    criticite: Optional[str] = None
    statut: Optional[str] = None
    cout_acquisition_xaf: Optional[float] = None
    valeur_residuelle_xaf: Optional[float] = None
    duree_vieutile_ans: Optional[int] = None
    notes_techniques: Optional[str] = None
    is_active: Optional[bool] = None


class TechnicalAssetOut(BaseModel):
    id: int
    company_id: int
    tag_actif: str
    nom: str
    categorie: Optional[str] = None
    sous_categorie: Optional[str] = None
    module_source: Optional[str] = None
    ref_entite_source: Optional[str] = None
    parent_id: Optional[int] = None
    emplacement: Optional[str] = None
    fabricant: Optional[str] = None
    modele: Optional[str] = None
    numero_serie: Optional[str] = None
    annee_fabrication: Optional[int] = None
    date_mise_service: Optional[date] = None
    criticite: Optional[str] = None
    statut: Optional[str] = None
    cout_acquisition_xaf: Optional[float] = None
    valeur_residuelle_xaf: Optional[float] = None
    duree_vieutile_ans: Optional[int] = None
    notes_techniques: Optional[str] = None
    is_active: Optional[bool] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    model_config = {"from_attributes": True}


class AssetComponentCreate(BaseModel):
    asset_id: int
    code_composant: str
    nom_composant: str
    type_composant: Optional[str] = None
    ref_fabricant: Optional[str] = None
    numero_serie: Optional[str] = None
    nombre_pieces: Optional[int] = None
    masse_kg: Optional[float] = None
    seuil_reforme: Optional[str] = None
    criticite: Optional[str] = None
    date_mise_service: Optional[date] = None
    statut: Optional[str] = None
    notes: Optional[str] = None


class AssetComponentUpdate(BaseModel):
    asset_id: Optional[int] = None
    code_composant: Optional[str] = None
    nom_composant: Optional[str] = None
    type_composant: Optional[str] = None
    ref_fabricant: Optional[str] = None
    numero_serie: Optional[str] = None
    nombre_pieces: Optional[int] = None
    masse_kg: Optional[float] = None
    seuil_reforme: Optional[str] = None
    criticite: Optional[str] = None
    date_mise_service: Optional[date] = None
    statut: Optional[str] = None
    notes: Optional[str] = None
    is_active: Optional[bool] = None


class AssetComponentOut(BaseModel):
    id: int
    company_id: int
    asset_id: int
    code_composant: str
    nom_composant: str
    type_composant: Optional[str] = None
    ref_fabricant: Optional[str] = None
    numero_serie: Optional[str] = None
    nombre_pieces: Optional[int] = None
    masse_kg: Optional[float] = None
    seuil_reforme: Optional[str] = None
    criticite: Optional[str] = None
    date_mise_service: Optional[date] = None
    statut: Optional[str] = None
    notes: Optional[str] = None
    is_active: Optional[bool] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    model_config = {"from_attributes": True}


class SparePartCatalogCreate(BaseModel):
    reference_interne: str
    designation: str
    origine: Optional[str] = None
    ref_fabricant: Optional[str] = None
    ref_essaiere_group: Optional[str] = None
    categorie: Optional[str] = None
    sous_categorie: Optional[str] = None
    type_rechange: Optional[str] = None
    unite_mesure: Optional[str] = None
    unit_cost_xaf: Optional[float] = None
    cost_achat_actuel_xaf: Optional[float] = None
    fournisseur_principal_id: Optional[int] = None
    alternative_fournisseur_id: Optional[int] = None
    delai_approvisionnement_j: Optional[int] = None
    duree_vie_moyenne_h: Optional[int] = None
    garantie_mois: Optional[int] = None
    serialise_obligatoire: Optional[bool] = None
    poids_kg: Optional[float] = None
    volume_cm3: Optional[int] = None
    classification_hs: Optional[str] = None
    notes_techniques: Optional[str] = None


class SparePartCatalogUpdate(BaseModel):
    reference_interne: Optional[str] = None
    designation: Optional[str] = None
    origine: Optional[str] = None
    ref_fabricant: Optional[str] = None
    ref_essaiere_group: Optional[str] = None
    categorie: Optional[str] = None
    sous_categorie: Optional[str] = None
    type_rechange: Optional[str] = None
    unite_mesure: Optional[str] = None
    unit_cost_xaf: Optional[float] = None
    cost_achat_actuel_xaf: Optional[float] = None
    fournisseur_principal_id: Optional[int] = None
    alternative_fournisseur_id: Optional[int] = None
    delai_approvisionnement_j: Optional[int] = None
    duree_vie_moyenne_h: Optional[int] = None
    garantie_mois: Optional[int] = None
    serialise_obligatoire: Optional[bool] = None
    poids_kg: Optional[float] = None
    volume_cm3: Optional[int] = None
    classification_hs: Optional[str] = None
    notes_techniques: Optional[str] = None
    is_active: Optional[bool] = None


class SparePartCatalogOut(BaseModel):
    id: int
    company_id: int
    reference_interne: str
    designation: str
    origine: Optional[str] = None
    ref_fabricant: Optional[str] = None
    ref_essaiere_group: Optional[str] = None
    categorie: Optional[str] = None
    sous_categorie: Optional[str] = None
    type_rechange: Optional[str] = None
    unite_mesure: Optional[str] = None
    unit_cost_xaf: Optional[float] = None
    cost_achat_actuel_xaf: Optional[float] = None
    fournisseur_principal_id: Optional[int] = None
    alternative_fournisseur_id: Optional[int] = None
    delai_approvisionnement_j: Optional[int] = None
    duree_vie_moyenne_h: Optional[int] = None
    garantie_mois: Optional[int] = None
    serialise_obligatoire: Optional[bool] = None
    poids_kg: Optional[float] = None
    volume_cm3: Optional[int] = None
    classification_hs: Optional[str] = None
    notes_techniques: Optional[str] = None
    is_active: Optional[bool] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    model_config = {"from_attributes": True}


class BillOfMaterialCreate(BaseModel):
    asset_id: int
    component_id: Optional[int] = None
    part_id: int
    position_index: int
    quantite_par_assemblage: Optional[float] = None
    unit: Optional[str] = None
    niveau: Optional[int] = None
    level_parent_id: Optional[int] = None
    obligatoire: Optional[bool] = None
    remplacement_interval: Optional[str] = None
    notes: Optional[str] = None


class BillOfMaterialUpdate(BaseModel):
    asset_id: Optional[int] = None
    component_id: Optional[int] = None
    part_id: Optional[int] = None
    position_index: Optional[int] = None
    quantite_par_assemblage: Optional[float] = None
    unit: Optional[str] = None
    niveau: Optional[int] = None
    level_parent_id: Optional[int] = None
    obligatoire: Optional[bool] = None
    remplacement_interval: Optional[str] = None
    notes: Optional[str] = None
    is_active: Optional[bool] = None


class BillOfMaterialOut(BaseModel):
    id: int
    company_id: int
    asset_id: int
    component_id: Optional[int] = None
    part_id: int
    position_index: int
    quantite_par_assemblage: Optional[float] = None
    unit: Optional[str] = None
    niveau: Optional[int] = None
    level_parent_id: Optional[int] = None
    obligatoire: Optional[bool] = None
    remplacement_interval: Optional[str] = None
    notes: Optional[str] = None
    is_active: Optional[bool] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    model_config = {"from_attributes": True}


class SerializedPartCreate(BaseModel):
    part_id: int
    numero_serial: str
    numero_lot: Optional[str] = None
    date_fabrication: Optional[date] = None
    date_reception: Optional[date] = None
    date_mise_service: Optional[date] = None
    date_reforme: Optional[date] = None
    cycles_utilisation: Optional[int] = None
    heures_utilisees: Optional[float] = None
    kilometres_utilises: Optional[float] = None
    statut: Optional[str] = None
    asset_id_actuel: Optional[int] = None
    composant_id_actuel: Optional[int] = None
    emplacement_stock: Optional[str] = None
    fournisseur_id: Optional[int] = None
    numero_bl_achat: Optional[str] = None
    numero_facture_achat: Optional[str] = None
    date_garantie_fin: Optional[date] = None
    valeur_achat_xaf: Optional[float] = None
    hashs_certificat: Optional[str] = None
    notes: Optional[str] = None


class SerializedPartUpdate(BaseModel):
    part_id: Optional[int] = None
    numero_serial: Optional[str] = None
    numero_lot: Optional[str] = None
    date_fabrication: Optional[date] = None
    date_reception: Optional[date] = None
    date_mise_service: Optional[date] = None
    date_reforme: Optional[date] = None
    cycles_utilisation: Optional[int] = None
    heures_utilisees: Optional[float] = None
    kilometres_utilises: Optional[float] = None
    statut: Optional[str] = None
    asset_id_actuel: Optional[int] = None
    composant_id_actuel: Optional[int] = None
    emplacement_stock: Optional[str] = None
    fournisseur_id: Optional[int] = None
    numero_bl_achat: Optional[str] = None
    numero_facture_achat: Optional[str] = None
    date_garantie_fin: Optional[date] = None
    valeur_achat_xaf: Optional[float] = None
    hashs_certificat: Optional[str] = None
    notes: Optional[str] = None
    is_active: Optional[bool] = None


class SerializedPartOut(BaseModel):
    id: int
    company_id: int
    part_id: int
    numero_serial: str
    numero_lot: Optional[str] = None
    date_fabrication: Optional[date] = None
    date_reception: Optional[date] = None
    date_mise_service: Optional[date] = None
    date_reforme: Optional[date] = None
    cycles_utilisation: Optional[int] = None
    heures_utilisees: Optional[float] = None
    kilometres_utilises: Optional[float] = None
    statut: Optional[str] = None
    asset_id_actuel: Optional[int] = None
    composant_id_actuel: Optional[int] = None
    emplacement_stock: Optional[str] = None
    fournisseur_id: Optional[int] = None
    numero_bl_achat: Optional[str] = None
    numero_facture_achat: Optional[str] = None
    date_garantie_fin: Optional[date] = None
    valeur_achat_xaf: Optional[float] = None
    hashs_certificat: Optional[str] = None
    notes: Optional[str] = None
    is_active: Optional[bool] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    model_config = {"from_attributes": True}


class PartInventoryCreate(BaseModel):
    part_id: int
    magasin_id: Optional[int] = None
    emplacement: Optional[str] = None
    quantite_en_stock: int
    quantite_reservee: Optional[int] = None
    quantite_min: Optional[int] = None
    quantite_max: Optional[int] = None
    point_commande: Optional[int] = None
    cout_moyen_pondere_xaf: Optional[float] = None
    valeur_totale_xaf: Optional[float] = None
    date_dernier_mouvement: Optional[datetime] = None
    date_dernier_inventaire: Optional[date] = None


class PartInventoryUpdate(BaseModel):
    part_id: Optional[int] = None
    magasin_id: Optional[int] = None
    emplacement: Optional[str] = None
    quantite_en_stock: Optional[int] = None
    quantite_reservee: Optional[int] = None
    quantite_min: Optional[int] = None
    quantite_max: Optional[int] = None
    point_commande: Optional[int] = None
    cout_moyen_pondere_xaf: Optional[float] = None
    valeur_totale_xaf: Optional[float] = None
    date_dernier_mouvement: Optional[datetime] = None
    date_dernier_inventaire: Optional[date] = None
    is_active: Optional[bool] = None


class PartInventoryOut(BaseModel):
    id: int
    company_id: int
    part_id: int
    magasin_id: Optional[int] = None
    emplacement: Optional[str] = None
    quantite_en_stock: int
    quantite_reservee: Optional[int] = None
    quantite_min: Optional[int] = None
    quantite_max: Optional[int] = None
    point_commande: Optional[int] = None
    cout_moyen_pondere_xaf: Optional[float] = None
    valeur_totale_xaf: Optional[float] = None
    date_dernier_mouvement: Optional[datetime] = None
    date_dernier_inventaire: Optional[date] = None
    is_active: Optional[bool] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    model_config = {"from_attributes": True}


class PartMovementCreate(BaseModel):
    reference_mouvement: str
    part_id: int
    serialized_part_id: Optional[int] = None
    type_mouvement: str
    quantite: float
    magasin_source_id: Optional[int] = None
    magasin_destination_id: Optional[int] = None
    work_order_id: Optional[int] = None
    bon_livraison_id: Optional[int] = None
    facture_achat_id: Optional[int] = None
    user_id: Optional[int] = None
    date_mouvement: datetime
    valeur_xaf: Optional[float] = None
    motif: Optional[str] = None
    notes: Optional[str] = None


class PartMovementUpdate(BaseModel):
    reference_mouvement: Optional[str] = None
    part_id: Optional[int] = None
    serialized_part_id: Optional[int] = None
    type_mouvement: Optional[str] = None
    quantite: Optional[float] = None
    magasin_source_id: Optional[int] = None
    magasin_destination_id: Optional[int] = None
    work_order_id: Optional[int] = None
    bon_livraison_id: Optional[int] = None
    facture_achat_id: Optional[int] = None
    user_id: Optional[int] = None
    date_mouvement: Optional[datetime] = None
    valeur_xaf: Optional[float] = None
    motif: Optional[str] = None
    notes: Optional[str] = None
    is_active: Optional[bool] = None


class PartMovementOut(BaseModel):
    id: int
    company_id: int
    reference_mouvement: str
    part_id: int
    serialized_part_id: Optional[int] = None
    type_mouvement: str
    quantite: float
    magasin_source_id: Optional[int] = None
    magasin_destination_id: Optional[int] = None
    work_order_id: Optional[int] = None
    bon_livraison_id: Optional[int] = None
    facture_achat_id: Optional[int] = None
    user_id: Optional[int] = None
    date_mouvement: datetime
    valeur_xaf: Optional[float] = None
    motif: Optional[str] = None
    notes: Optional[str] = None
    is_active: Optional[bool] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    model_config = {"from_attributes": True}


class FailureModeCreate(BaseModel):
    code_fmea: str
    asset_id: Optional[int] = None
    component_id: Optional[int] = None
    fonction: Optional[str] = None
    mode_defaillance: str
    mecanisme: Optional[str] = None
    causes: Optional[str] = None
    effets: Optional[str] = None
    gravite: Optional[int] = None
    occurrence: Optional[int] = None
    detection: Optional[int] = None
    ipr: Optional[int] = None
    methode_detection: Optional[str] = None
    actions_preventives: Optional[str] = None
    actions_correctives: Optional[str] = None
    responsable: Optional[str] = None
    date_evaluation: Optional[date] = None
    statut: Optional[str] = None


class FailureModeUpdate(BaseModel):
    code_fmea: Optional[str] = None
    asset_id: Optional[int] = None
    component_id: Optional[int] = None
    fonction: Optional[str] = None
    mode_defaillance: Optional[str] = None
    mecanisme: Optional[str] = None
    causes: Optional[str] = None
    effets: Optional[str] = None
    gravite: Optional[int] = None
    occurrence: Optional[int] = None
    detection: Optional[int] = None
    ipr: Optional[int] = None
    methode_detection: Optional[str] = None
    actions_preventives: Optional[str] = None
    actions_correctives: Optional[str] = None
    responsable: Optional[str] = None
    date_evaluation: Optional[date] = None
    statut: Optional[str] = None
    is_active: Optional[bool] = None


class FailureModeOut(BaseModel):
    id: int
    company_id: int
    code_fmea: str
    asset_id: Optional[int] = None
    component_id: Optional[int] = None
    fonction: Optional[str] = None
    mode_defaillance: str
    mecanisme: Optional[str] = None
    causes: Optional[str] = None
    effets: Optional[str] = None
    gravite: Optional[int] = None
    occurrence: Optional[int] = None
    detection: Optional[int] = None
    ipr: Optional[int] = None
    methode_detection: Optional[str] = None
    actions_preventives: Optional[str] = None
    actions_correctives: Optional[str] = None
    responsable: Optional[str] = None
    date_evaluation: Optional[date] = None
    statut: Optional[str] = None
    is_active: Optional[bool] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    model_config = {"from_attributes": True}


class MaintenancePlanCreate(BaseModel):
    code_plan: str
    nom: str
    asset_id: Optional[int] = None
    component_id: Optional[int] = None
    type_plan: str
    frequence_type: Optional[str] = None
    frequence_valeur: Optional[float] = None
    frequence_unite: Optional[str] = None
    seuil_declenchement: Optional[str] = None
    prochaine_echeance: Optional[date] = None
    duree_estimee_h: Optional[float] = None
    criticite: Optional[str] = None
    cout_estime_par_cycle_xaf: Optional[float] = None
    skills_requis: Optional[str] = None
    outillage_requis: Optional[str] = None
    pieces_cle: Optional[str] = None
    version: Optional[int] = None
    statut: Optional[str] = None


class MaintenancePlanUpdate(BaseModel):
    code_plan: Optional[str] = None
    nom: Optional[str] = None
    asset_id: Optional[int] = None
    component_id: Optional[int] = None
    type_plan: Optional[str] = None
    frequence_type: Optional[str] = None
    frequence_valeur: Optional[float] = None
    frequence_unite: Optional[str] = None
    seuil_declenchement: Optional[str] = None
    prochaine_echeance: Optional[date] = None
    duree_estimee_h: Optional[float] = None
    criticite: Optional[str] = None
    cout_estime_par_cycle_xaf: Optional[float] = None
    skills_requis: Optional[str] = None
    outillage_requis: Optional[str] = None
    pieces_cle: Optional[str] = None
    version: Optional[int] = None
    statut: Optional[str] = None
    is_active: Optional[bool] = None


class MaintenancePlanOut(BaseModel):
    id: int
    company_id: int
    code_plan: str
    nom: str
    asset_id: Optional[int] = None
    component_id: Optional[int] = None
    type_plan: str
    frequence_type: Optional[str] = None
    frequence_valeur: Optional[float] = None
    frequence_unite: Optional[str] = None
    seuil_declenchement: Optional[str] = None
    prochaine_echeance: Optional[date] = None
    duree_estimee_h: Optional[float] = None
    criticite: Optional[str] = None
    cout_estime_par_cycle_xaf: Optional[float] = None
    skills_requis: Optional[str] = None
    outillage_requis: Optional[str] = None
    pieces_cle: Optional[str] = None
    version: Optional[int] = None
    statut: Optional[str] = None
    is_active: Optional[bool] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    model_config = {"from_attributes": True}


class MaintenanceTaskCreate(BaseModel):
    code_tache: str
    plan_id: Optional[int] = None
    titre: str
    description_geste: Optional[str] = None
    duree_estimee_min: Optional[int] = None
    nb_techniciens: Optional[int] = None
    competence_requise: Optional[str] = None
    niveau_habiliture: Optional[str] = None
    epi_requis: Optional[str] = None
    outillage: Optional[str] = None
    couples_re_serrage: Optional[str] = None
    pieces_requises: Optional[str] = None
    ordre_execution: Optional[int] = None


class MaintenanceTaskUpdate(BaseModel):
    code_tache: Optional[str] = None
    plan_id: Optional[int] = None
    titre: Optional[str] = None
    description_geste: Optional[str] = None
    duree_estimee_min: Optional[int] = None
    nb_techniciens: Optional[int] = None
    competence_requise: Optional[str] = None
    niveau_habiliture: Optional[str] = None
    epi_requis: Optional[str] = None
    outillage: Optional[str] = None
    couples_re_serrage: Optional[str] = None
    pieces_requises: Optional[str] = None
    ordre_execution: Optional[int] = None
    is_active: Optional[bool] = None


class MaintenanceTaskOut(BaseModel):
    id: int
    company_id: int
    code_tache: str
    plan_id: Optional[int] = None
    titre: str
    description_geste: Optional[str] = None
    duree_estimee_min: Optional[int] = None
    nb_techniciens: Optional[int] = None
    competence_requise: Optional[str] = None
    niveau_habiliture: Optional[str] = None
    epi_requis: Optional[str] = None
    outillage: Optional[str] = None
    couples_re_serrage: Optional[str] = None
    pieces_requises: Optional[str] = None
    ordre_execution: Optional[int] = None
    is_active: Optional[bool] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    model_config = {"from_attributes": True}


class WorkOrderCreate(BaseModel):
    numero_ot: str
    type_ot: str
    asset_id: int
    component_id: Optional[int] = None
    plan_id: Optional[int] = None
    defaillance_id: Optional[int] = None
    titre: str
    description: Optional[str] = None
    priorite: Optional[str] = None
    criticite_asset: Optional[str] = None
    date_detection: Optional[datetime] = None
    date_ouverture: Optional[datetime] = None
    date_prevue_debut: Optional[datetime] = None
    date_prevue_fin: Optional[datetime] = None
    date_reel_debut: Optional[datetime] = None
    date_reel_fin: Optional[datetime] = None
    statut: Optional[str] = None
    technicien_principal_id: Optional[int] = None
    prestataire_id: Optional[int] = None
    heures_prevues: Optional[float] = None
    heures_reelles: Optional[float] = None
    cout_pieces_xaf: Optional[float] = None
    cout_main_oeuvre_xaf: Optional[float] = None
    cout_prestataire_xaf: Optional[float] = None
    cout_total_xaf: Optional[float] = None
    cause_racine_id: Optional[int] = None
    arret_production: Optional[bool] = None
    impact_securite: Optional[bool] = None
    compte_rendu: Optional[str] = None
    pieces_ressorties: Optional[str] = None
    photos_url: Optional[str] = None


class WorkOrderUpdate(BaseModel):
    numero_ot: Optional[str] = None
    type_ot: Optional[str] = None
    asset_id: Optional[int] = None
    component_id: Optional[int] = None
    plan_id: Optional[int] = None
    defaillance_id: Optional[int] = None
    titre: Optional[str] = None
    description: Optional[str] = None
    priorite: Optional[str] = None
    criticite_asset: Optional[str] = None
    date_detection: Optional[datetime] = None
    date_ouverture: Optional[datetime] = None
    date_prevue_debut: Optional[datetime] = None
    date_prevue_fin: Optional[datetime] = None
    date_reel_debut: Optional[datetime] = None
    date_reel_fin: Optional[datetime] = None
    statut: Optional[str] = None
    technicien_principal_id: Optional[int] = None
    prestataire_id: Optional[int] = None
    heures_prevues: Optional[float] = None
    heures_reelles: Optional[float] = None
    cout_pieces_xaf: Optional[float] = None
    cout_main_oeuvre_xaf: Optional[float] = None
    cout_prestataire_xaf: Optional[float] = None
    cout_total_xaf: Optional[float] = None
    cause_racine_id: Optional[int] = None
    arret_production: Optional[bool] = None
    impact_securite: Optional[bool] = None
    compte_rendu: Optional[str] = None
    pieces_ressorties: Optional[str] = None
    photos_url: Optional[str] = None
    is_active: Optional[bool] = None


class WorkOrderOut(BaseModel):
    id: int
    company_id: int
    numero_ot: str
    type_ot: str
    asset_id: int
    component_id: Optional[int] = None
    plan_id: Optional[int] = None
    defaillance_id: Optional[int] = None
    titre: str
    description: Optional[str] = None
    priorite: Optional[str] = None
    criticite_asset: Optional[str] = None
    date_detection: Optional[datetime] = None
    date_ouverture: Optional[datetime] = None
    date_prevue_debut: Optional[datetime] = None
    date_prevue_fin: Optional[datetime] = None
    date_reel_debut: Optional[datetime] = None
    date_reel_fin: Optional[datetime] = None
    statut: Optional[str] = None
    technicien_principal_id: Optional[int] = None
    prestataire_id: Optional[int] = None
    heures_prevues: Optional[float] = None
    heures_reelles: Optional[float] = None
    cout_pieces_xaf: Optional[float] = None
    cout_main_oeuvre_xaf: Optional[float] = None
    cout_prestataire_xaf: Optional[float] = None
    cout_total_xaf: Optional[float] = None
    cause_racine_id: Optional[int] = None
    arret_production: Optional[bool] = None
    impact_securite: Optional[bool] = None
    compte_rendu: Optional[str] = None
    pieces_ressorties: Optional[str] = None
    photos_url: Optional[str] = None
    is_active: Optional[bool] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    model_config = {"from_attributes": True}


class AssetFailureCreate(BaseModel):
    reference_defaillance: str
    asset_id: int
    component_id: Optional[int] = None
    mode_id: Optional[int] = None
    date_detection: datetime
    detecteur: Optional[str] = None
    source_signalement: Optional[str] = None
    severite: Optional[str] = None
    description: Optional[str] = None
    symptomes: Optional[str] = None
    code_defaut: Optional[str] = None
    heures_arret: Optional[float] = None
    cout_indirect_xaf: Optional[float] = None
    statut: Optional[str] = None


class AssetFailureUpdate(BaseModel):
    reference_defaillance: Optional[str] = None
    asset_id: Optional[int] = None
    component_id: Optional[int] = None
    mode_id: Optional[int] = None
    date_detection: Optional[datetime] = None
    detecteur: Optional[str] = None
    source_signalement: Optional[str] = None
    severite: Optional[str] = None
    description: Optional[str] = None
    symptomes: Optional[str] = None
    code_defaut: Optional[str] = None
    heures_arret: Optional[float] = None
    cout_indirect_xaf: Optional[float] = None
    statut: Optional[str] = None
    is_active: Optional[bool] = None


class AssetFailureOut(BaseModel):
    id: int
    company_id: int
    reference_defaillance: str
    asset_id: int
    component_id: Optional[int] = None
    mode_id: Optional[int] = None
    date_detection: datetime
    detecteur: Optional[str] = None
    source_signalement: Optional[str] = None
    severite: Optional[str] = None
    description: Optional[str] = None
    symptomes: Optional[str] = None
    code_defaut: Optional[str] = None
    heures_arret: Optional[float] = None
    cout_indirect_xaf: Optional[float] = None
    statut: Optional[str] = None
    is_active: Optional[bool] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    model_config = {"from_attributes": True}


class WorkOrderPartCreate(BaseModel):
    work_order_id: int
    part_id: int
    serialized_part_id: Optional[int] = None
    quantite_demandee: float
    quantite_livree: Optional[float] = None
    quantite_consommee: Optional[float] = None
    quantite_retour: Optional[float] = None
    valeur_xaf: Optional[float] = None
    date_sortie: Optional[datetime] = None
    motif_retour: Optional[str] = None
    magasin_id: Optional[int] = None


class WorkOrderPartUpdate(BaseModel):
    work_order_id: Optional[int] = None
    part_id: Optional[int] = None
    serialized_part_id: Optional[int] = None
    quantite_demandee: Optional[float] = None
    quantite_livree: Optional[float] = None
    quantite_consommee: Optional[float] = None
    quantite_retour: Optional[float] = None
    valeur_xaf: Optional[float] = None
    date_sortie: Optional[datetime] = None
    motif_retour: Optional[str] = None
    magasin_id: Optional[int] = None
    is_active: Optional[bool] = None


class WorkOrderPartOut(BaseModel):
    id: int
    company_id: int
    work_order_id: int
    part_id: int
    serialized_part_id: Optional[int] = None
    quantite_demandee: float
    quantite_livree: Optional[float] = None
    quantite_consommee: Optional[float] = None
    quantite_retour: Optional[float] = None
    valeur_xaf: Optional[float] = None
    date_sortie: Optional[datetime] = None
    motif_retour: Optional[str] = None
    magasin_id: Optional[int] = None
    is_active: Optional[bool] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    model_config = {"from_attributes": True}


class WorkOrderLabourCreate(BaseModel):
    work_order_id: int
    user_id: int
    role_intervenant: Optional[str] = None
    date_travail: date
    heures_prevues: Optional[float] = None
    heures_reelles: float
    taux_horaire_xaf: Optional[float] = None
    cout_total_xaf: Optional[float] = None
    statut: Optional[str] = None
    notes: Optional[str] = None


class WorkOrderLabourUpdate(BaseModel):
    work_order_id: Optional[int] = None
    user_id: Optional[int] = None
    role_intervenant: Optional[str] = None
    date_travail: Optional[date] = None
    heures_prevues: Optional[float] = None
    heures_reelles: Optional[float] = None
    taux_horaire_xaf: Optional[float] = None
    cout_total_xaf: Optional[float] = None
    statut: Optional[str] = None
    notes: Optional[str] = None
    is_active: Optional[bool] = None


class WorkOrderLabourOut(BaseModel):
    id: int
    company_id: int
    work_order_id: int
    user_id: int
    role_intervenant: Optional[str] = None
    date_travail: date
    heures_prevues: Optional[float] = None
    heures_reelles: float
    taux_horaire_xaf: Optional[float] = None
    cout_total_xaf: Optional[float] = None
    statut: Optional[str] = None
    notes: Optional[str] = None
    is_active: Optional[bool] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    model_config = {"from_attributes": True}


class WorkOrderToolCreate(BaseModel):
    work_order_id: int
    reference_outillage: str
    designation: Optional[str] = None
    type_outillage: Optional[str] = None
    proprietaire: Optional[str] = None
    numero_inventaire: Optional[str] = None
    date_pret_debut: Optional[date] = None
    date_pret_fin: Optional[date] = None
    date_calibration: Optional[date] = None
    cout_location_xaf: Optional[float] = None
    statut: Optional[str] = None
    notes: Optional[str] = None


class WorkOrderToolUpdate(BaseModel):
    work_order_id: Optional[int] = None
    reference_outillage: Optional[str] = None
    designation: Optional[str] = None
    type_outillage: Optional[str] = None
    proprietaire: Optional[str] = None
    numero_inventaire: Optional[str] = None
    date_pret_debut: Optional[date] = None
    date_pret_fin: Optional[date] = None
    date_calibration: Optional[date] = None
    cout_location_xaf: Optional[float] = None
    statut: Optional[str] = None
    notes: Optional[str] = None
    is_active: Optional[bool] = None


class WorkOrderToolOut(BaseModel):
    id: int
    company_id: int
    work_order_id: int
    reference_outillage: str
    designation: Optional[str] = None
    type_outillage: Optional[str] = None
    proprietaire: Optional[str] = None
    numero_inventaire: Optional[str] = None
    date_pret_debut: Optional[date] = None
    date_pret_fin: Optional[date] = None
    date_calibration: Optional[date] = None
    cout_location_xaf: Optional[float] = None
    statut: Optional[str] = None
    notes: Optional[str] = None
    is_active: Optional[bool] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    model_config = {"from_attributes": True}


class RootCauseAnalysisCreate(BaseModel):
    reference_rca: str
    work_order_id: Optional[int] = None
    asset_id: Optional[int] = None
    methode: Optional[str] = None
    probleme: str
    pourquoi_1: Optional[str] = None
    pourquoi_2: Optional[str] = None
    pourquoi_3: Optional[str] = None
    pourquoi_4: Optional[str] = None
    pourquoi_5: Optional[str] = None
    categories_ishikawa: Optional[str] = None
    cause_racine: Optional[str] = None
    causes_contributives: Optional[str] = None
    actions_correctives: Optional[str] = None
    actions_preventives_globales: Optional[str] = None
    responsable_id: Optional[int] = None
    date_cloture: Optional[date] = None
    statut: Optional[str] = None


class RootCauseAnalysisUpdate(BaseModel):
    reference_rca: Optional[str] = None
    work_order_id: Optional[int] = None
    asset_id: Optional[int] = None
    methode: Optional[str] = None
    probleme: Optional[str] = None
    pourquoi_1: Optional[str] = None
    pourquoi_2: Optional[str] = None
    pourquoi_3: Optional[str] = None
    pourquoi_4: Optional[str] = None
    pourquoi_5: Optional[str] = None
    categories_ishikawa: Optional[str] = None
    cause_racine: Optional[str] = None
    causes_contributives: Optional[str] = None
    actions_correctives: Optional[str] = None
    actions_preventives_globales: Optional[str] = None
    responsable_id: Optional[int] = None
    date_cloture: Optional[date] = None
    statut: Optional[str] = None
    is_active: Optional[bool] = None


class RootCauseAnalysisOut(BaseModel):
    id: int
    company_id: int
    reference_rca: str
    work_order_id: Optional[int] = None
    asset_id: Optional[int] = None
    methode: Optional[str] = None
    probleme: str
    pourquoi_1: Optional[str] = None
    pourquoi_2: Optional[str] = None
    pourquoi_3: Optional[str] = None
    pourquoi_4: Optional[str] = None
    pourquoi_5: Optional[str] = None
    categories_ishikawa: Optional[str] = None
    cause_racine: Optional[str] = None
    causes_contributives: Optional[str] = None
    actions_correctives: Optional[str] = None
    actions_preventives_globales: Optional[str] = None
    responsable_id: Optional[int] = None
    date_cloture: Optional[date] = None
    statut: Optional[str] = None
    is_active: Optional[bool] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    model_config = {"from_attributes": True}


class OverhaulCampaignCreate(BaseModel):
    code_overhaul: str
    asset_id: int
    type_overhaul: Optional[str] = None
    intervalle_heures: Optional[float] = None
    intervalle_km: Optional[float] = None
    intervalle_mois: Optional[int] = None
    prochaine_echeance_date: Optional[date] = None
    prochaine_echeance_heures: Optional[float] = None
    prestataire_id: Optional[int] = None
    budget_estime_xaf: Optional[float] = None
    date_debut: Optional[date] = None
    date_fin: Optional[date] = None
    duree_reelle_j: Optional[int] = None
    kits_pieces_utilises: Optional[str] = None
    rapport_technique: Optional[str] = None
    statut: Optional[str] = None


class OverhaulCampaignUpdate(BaseModel):
    code_overhaul: Optional[str] = None
    asset_id: Optional[int] = None
    type_overhaul: Optional[str] = None
    intervalle_heures: Optional[float] = None
    intervalle_km: Optional[float] = None
    intervalle_mois: Optional[int] = None
    prochaine_echeance_date: Optional[date] = None
    prochaine_echeance_heures: Optional[float] = None
    prestataire_id: Optional[int] = None
    budget_estime_xaf: Optional[float] = None
    date_debut: Optional[date] = None
    date_fin: Optional[date] = None
    duree_reelle_j: Optional[int] = None
    kits_pieces_utilises: Optional[str] = None
    rapport_technique: Optional[str] = None
    statut: Optional[str] = None
    is_active: Optional[bool] = None


class OverhaulCampaignOut(BaseModel):
    id: int
    company_id: int
    code_overhaul: str
    asset_id: int
    type_overhaul: Optional[str] = None
    intervalle_heures: Optional[float] = None
    intervalle_km: Optional[float] = None
    intervalle_mois: Optional[int] = None
    prochaine_echeance_date: Optional[date] = None
    prochaine_echeance_heures: Optional[float] = None
    prestataire_id: Optional[int] = None
    budget_estime_xaf: Optional[float] = None
    date_debut: Optional[date] = None
    date_fin: Optional[date] = None
    duree_reelle_j: Optional[int] = None
    kits_pieces_utilises: Optional[str] = None
    rapport_technique: Optional[str] = None
    statut: Optional[str] = None
    is_active: Optional[bool] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    model_config = {"from_attributes": True}


class LubricationScheduleCreate(BaseModel):
    asset_id: int
    component_id: Optional[int] = None
    point_lubrifiant: str
    type_lubrifiant: Optional[str] = None
    grade: Optional[str] = None
    marque: Optional[str] = None
    quantite_litre: Optional[float] = None
    quantite_gramme: Optional[float] = None
    frequence_heures: Optional[float] = None
    frequence_jours: Optional[int] = None
    prochaine_date: Optional[date] = None
    methode: Optional[str] = None
    statut: Optional[str] = None
    notes: Optional[str] = None


class LubricationScheduleUpdate(BaseModel):
    asset_id: Optional[int] = None
    component_id: Optional[int] = None
    point_lubrifiant: Optional[str] = None
    type_lubrifiant: Optional[str] = None
    grade: Optional[str] = None
    marque: Optional[str] = None
    quantite_litre: Optional[float] = None
    quantite_gramme: Optional[float] = None
    frequence_heures: Optional[float] = None
    frequence_jours: Optional[int] = None
    prochaine_date: Optional[date] = None
    methode: Optional[str] = None
    statut: Optional[str] = None
    notes: Optional[str] = None
    is_active: Optional[bool] = None


class LubricationScheduleOut(BaseModel):
    id: int
    company_id: int
    asset_id: int
    component_id: Optional[int] = None
    point_lubrifiant: str
    type_lubrifiant: Optional[str] = None
    grade: Optional[str] = None
    marque: Optional[str] = None
    quantite_litre: Optional[float] = None
    quantite_gramme: Optional[float] = None
    frequence_heures: Optional[float] = None
    frequence_jours: Optional[int] = None
    prochaine_date: Optional[date] = None
    methode: Optional[str] = None
    statut: Optional[str] = None
    notes: Optional[str] = None
    is_active: Optional[bool] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    model_config = {"from_attributes": True}


class ConditionReadingCreate(BaseModel):
    reference_lecture: str
    asset_id: int
    component_id: Optional[int] = None
    type_technique: str
    capteur_id: Optional[int] = None
    point_mesure: Optional[str] = None
    date_lecture: datetime
    valeur_principale: Optional[float] = None
    unite: Optional[str] = None
    seuil_alerte: Optional[float] = None
    seuil_critical: Optional[float] = None
    statut_resultat: Optional[str] = None
    spectre_url: Optional[str] = None
    analyse_experte: Optional[str] = None
    operateur: Optional[str] = None


class ConditionReadingUpdate(BaseModel):
    reference_lecture: Optional[str] = None
    asset_id: Optional[int] = None
    component_id: Optional[int] = None
    type_technique: Optional[str] = None
    capteur_id: Optional[int] = None
    point_mesure: Optional[str] = None
    date_lecture: Optional[datetime] = None
    valeur_principale: Optional[float] = None
    unite: Optional[str] = None
    seuil_alerte: Optional[float] = None
    seuil_critical: Optional[float] = None
    statut_resultat: Optional[str] = None
    spectre_url: Optional[str] = None
    analyse_experte: Optional[str] = None
    operateur: Optional[str] = None
    is_active: Optional[bool] = None


class ConditionReadingOut(BaseModel):
    id: int
    company_id: int
    reference_lecture: str
    asset_id: int
    component_id: Optional[int] = None
    type_technique: str
    capteur_id: Optional[int] = None
    point_mesure: Optional[str] = None
    date_lecture: datetime
    valeur_principale: Optional[float] = None
    unite: Optional[str] = None
    seuil_alerte: Optional[float] = None
    seuil_critical: Optional[float] = None
    statut_resultat: Optional[str] = None
    spectre_url: Optional[str] = None
    analyse_experte: Optional[str] = None
    operateur: Optional[str] = None
    is_active: Optional[bool] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    model_config = {"from_attributes": True}


class SensorCreate(BaseModel):
    code_capteur: str
    asset_id: Optional[int] = None
    composant_id: Optional[int] = None
    type_capteur: Optional[str] = None
    protocol: Optional[str] = None
    adresse_mqtt: Optional[str] = None
    url_flux: Optional[str] = None
    frequence_echantillonnage_hz: Optional[int] = None
    resolution_bits: Optional[int] = None
    unite_sortie: Optional[str] = None
    plage_min: Optional[float] = None
    plage_max: Optional[float] = None
    seuil_alerte_bas: Optional[float] = None
    seuil_alerte_haut: Optional[float] = None
    calibration_periodicite_mois: Optional[int] = None
    derniere_calibration: Optional[date] = None
    fabricant: Optional[str] = None
    modele: Optional[str] = None
    numero_serie: Optional[str] = None
    statut: Optional[str] = None
    date_installation: Optional[date] = None


class SensorUpdate(BaseModel):
    code_capteur: Optional[str] = None
    asset_id: Optional[int] = None
    composant_id: Optional[int] = None
    type_capteur: Optional[str] = None
    protocol: Optional[str] = None
    adresse_mqtt: Optional[str] = None
    url_flux: Optional[str] = None
    frequence_echantillonnage_hz: Optional[int] = None
    resolution_bits: Optional[int] = None
    unite_sortie: Optional[str] = None
    plage_min: Optional[float] = None
    plage_max: Optional[float] = None
    seuil_alerte_bas: Optional[float] = None
    seuil_alerte_haut: Optional[float] = None
    calibration_periodicite_mois: Optional[int] = None
    derniere_calibration: Optional[date] = None
    fabricant: Optional[str] = None
    modele: Optional[str] = None
    numero_serie: Optional[str] = None
    statut: Optional[str] = None
    date_installation: Optional[date] = None
    is_active: Optional[bool] = None


class SensorOut(BaseModel):
    id: int
    company_id: int
    code_capteur: str
    asset_id: Optional[int] = None
    composant_id: Optional[int] = None
    type_capteur: Optional[str] = None
    protocol: Optional[str] = None
    adresse_mqtt: Optional[str] = None
    url_flux: Optional[str] = None
    frequence_echantillonnage_hz: Optional[int] = None
    resolution_bits: Optional[int] = None
    unite_sortie: Optional[str] = None
    plage_min: Optional[float] = None
    plage_max: Optional[float] = None
    seuil_alerte_bas: Optional[float] = None
    seuil_alerte_haut: Optional[float] = None
    calibration_periodicite_mois: Optional[int] = None
    derniere_calibration: Optional[date] = None
    fabricant: Optional[str] = None
    modele: Optional[str] = None
    numero_serie: Optional[str] = None
    statut: Optional[str] = None
    date_installation: Optional[date] = None
    is_active: Optional[bool] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    model_config = {"from_attributes": True}


class PredictiveModelCreate(BaseModel):
    code_modele: str
    nom: Optional[str] = None
    asset_id: Optional[int] = None
    composant_id: Optional[int] = None
    type_modele: Optional[str] = None
    variable_entree: Optional[str] = None
    variable_sortie: Optional[str] = None
    heuristique: Optional[str] = None
    precision_pct: Optional[float] = None
    rappel_pct: Optional[float] = None
    auc: Optional[float] = None
    version: Optional[str] = None
    date_entrainement: Optional[date] = None
    date_debut_production: Optional[date] = None
    seuil_declenchement_ot: Optional[float] = None
    statut: Optional[str] = None
    notes: Optional[str] = None


class PredictiveModelUpdate(BaseModel):
    code_modele: Optional[str] = None
    nom: Optional[str] = None
    asset_id: Optional[int] = None
    composant_id: Optional[int] = None
    type_modele: Optional[str] = None
    variable_entree: Optional[str] = None
    variable_sortie: Optional[str] = None
    heuristique: Optional[str] = None
    precision_pct: Optional[float] = None
    rappel_pct: Optional[float] = None
    auc: Optional[float] = None
    version: Optional[str] = None
    date_entrainement: Optional[date] = None
    date_debut_production: Optional[date] = None
    seuil_declenchement_ot: Optional[float] = None
    statut: Optional[str] = None
    notes: Optional[str] = None
    is_active: Optional[bool] = None


class PredictiveModelOut(BaseModel):
    id: int
    company_id: int
    code_modele: str
    nom: Optional[str] = None
    asset_id: Optional[int] = None
    composant_id: Optional[int] = None
    type_modele: Optional[str] = None
    variable_entree: Optional[str] = None
    variable_sortie: Optional[str] = None
    heuristique: Optional[str] = None
    precision_pct: Optional[float] = None
    rappel_pct: Optional[float] = None
    auc: Optional[float] = None
    version: Optional[str] = None
    date_entrainement: Optional[date] = None
    date_debut_production: Optional[date] = None
    seuil_declenchement_ot: Optional[float] = None
    statut: Optional[str] = None
    notes: Optional[str] = None
    is_active: Optional[bool] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    model_config = {"from_attributes": True}


class ReliabilityKpiCreate(BaseModel):
    asset_id: int
    periode: str
    nb_defaillances: Optional[int] = None
    nb_ot_preventif: Optional[int] = None
    nb_ot_curatif: Optional[int] = None
    heures_fonctionnement: Optional[float] = None
    heures_arret: Optional[float] = None
    mtbf_heures: Optional[float] = None
    mttr_heures: Optional[float] = None
    mttf_heures: Optional[float] = None
    disponibilite_pct: Optional[float] = None
    cout_maintenance_xaf: Optional[float] = None
    cout_indirect_arret_xaf: Optional[float] = None
    oee_pct: Optional[float] = None
    notes: Optional[str] = None


class ReliabilityKpiUpdate(BaseModel):
    asset_id: Optional[int] = None
    periode: Optional[str] = None
    nb_defaillances: Optional[int] = None
    nb_ot_preventif: Optional[int] = None
    nb_ot_curatif: Optional[int] = None
    heures_fonctionnement: Optional[float] = None
    heures_arret: Optional[float] = None
    mtbf_heures: Optional[float] = None
    mttr_heures: Optional[float] = None
    mttf_heures: Optional[float] = None
    disponibilite_pct: Optional[float] = None
    cout_maintenance_xaf: Optional[float] = None
    cout_indirect_arret_xaf: Optional[float] = None
    oee_pct: Optional[float] = None
    notes: Optional[str] = None
    is_active: Optional[bool] = None


class ReliabilityKpiOut(BaseModel):
    id: int
    company_id: int
    asset_id: int
    periode: str
    nb_defaillances: Optional[int] = None
    nb_ot_preventif: Optional[int] = None
    nb_ot_curatif: Optional[int] = None
    heures_fonctionnement: Optional[float] = None
    heures_arret: Optional[float] = None
    mtbf_heures: Optional[float] = None
    mttr_heures: Optional[float] = None
    mttf_heures: Optional[float] = None
    disponibilite_pct: Optional[float] = None
    cout_maintenance_xaf: Optional[float] = None
    cout_indirect_arret_xaf: Optional[float] = None
    oee_pct: Optional[float] = None
    notes: Optional[str] = None
    is_active: Optional[bool] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    model_config = {"from_attributes": True}


class RegulatoryInspectionCreate(BaseModel):
    numero_pv: str
    asset_id: int
    type_controle: Optional[str] = None
    autorite: Optional[str] = None
    organisme_controle: Optional[str] = None
    date_controle: Optional[date] = None
    date_validite: Optional[date] = None
    resultat: Optional[str] = None
    observations: Optional[str] = None
    pv_url: Optional[str] = None
    prochaine_echeance: Optional[date] = None
    inspecteur: Optional[str] = None
    statut: Optional[str] = None


class RegulatoryInspectionUpdate(BaseModel):
    numero_pv: Optional[str] = None
    asset_id: Optional[int] = None
    type_controle: Optional[str] = None
    autorite: Optional[str] = None
    organisme_controle: Optional[str] = None
    date_controle: Optional[date] = None
    date_validite: Optional[date] = None
    resultat: Optional[str] = None
    observations: Optional[str] = None
    pv_url: Optional[str] = None
    prochaine_echeance: Optional[date] = None
    inspecteur: Optional[str] = None
    statut: Optional[str] = None
    is_active: Optional[bool] = None


class RegulatoryInspectionOut(BaseModel):
    id: int
    company_id: int
    numero_pv: str
    asset_id: int
    type_controle: Optional[str] = None
    autorite: Optional[str] = None
    organisme_controle: Optional[str] = None
    date_controle: Optional[date] = None
    date_validite: Optional[date] = None
    resultat: Optional[str] = None
    observations: Optional[str] = None
    pv_url: Optional[str] = None
    prochaine_echeance: Optional[date] = None
    inspecteur: Optional[str] = None
    statut: Optional[str] = None
    is_active: Optional[bool] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    model_config = {"from_attributes": True}


class MaintenanceBudgetCreate(BaseModel):
    asset_id: int
    exercice: str
    budget_prevu_pieces_xaf: Optional[float] = None
    budget_prevu_main_oeuvre_xaf: Optional[float] = None
    budget_prevu_prestataire_xaf: Optional[float] = None
    budget_total_prevu_xaf: Optional[float] = None
    consomme_pieces_xaf: Optional[float] = None
    consomme_main_oeuvre_xaf: Optional[float] = None
    consomme_prestataire_xaf: Optional[float] = None
    total_consomme_xaf: Optional[float] = None
    ecart_pct: Optional[float] = None
    statut: Optional[str] = None
    notes: Optional[str] = None


class MaintenanceBudgetUpdate(BaseModel):
    asset_id: Optional[int] = None
    exercice: Optional[str] = None
    budget_prevu_pieces_xaf: Optional[float] = None
    budget_prevu_main_oeuvre_xaf: Optional[float] = None
    budget_prevu_prestataire_xaf: Optional[float] = None
    budget_total_prevu_xaf: Optional[float] = None
    consomme_pieces_xaf: Optional[float] = None
    consomme_main_oeuvre_xaf: Optional[float] = None
    consomme_prestataire_xaf: Optional[float] = None
    total_consomme_xaf: Optional[float] = None
    ecart_pct: Optional[float] = None
    statut: Optional[str] = None
    notes: Optional[str] = None
    is_active: Optional[bool] = None


class MaintenanceBudgetOut(BaseModel):
    id: int
    company_id: int
    asset_id: int
    exercice: str
    budget_prevu_pieces_xaf: Optional[float] = None
    budget_prevu_main_oeuvre_xaf: Optional[float] = None
    budget_prevu_prestataire_xaf: Optional[float] = None
    budget_total_prevu_xaf: Optional[float] = None
    consomme_pieces_xaf: Optional[float] = None
    consomme_main_oeuvre_xaf: Optional[float] = None
    consomme_prestataire_xaf: Optional[float] = None
    total_consomme_xaf: Optional[float] = None
    ecart_pct: Optional[float] = None
    statut: Optional[str] = None
    notes: Optional[str] = None
    is_active: Optional[bool] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    model_config = {"from_attributes": True}


class MaintenanceVendorCreate(BaseModel):
    code_prestataire: str
    raison_sociale: str
    pays: Optional[str] = None
    specialites: Optional[str] = None
    habilitations: Optional[str] = None
    certifications_iso: Optional[str] = None
    contact_nom: Optional[str] = None
    contact_email: Optional[str] = None
    contact_telephone: Optional[str] = None
    delai_reponse_h: Optional[int] = None
    astreinte_247: Optional[bool] = None
    zone_intervention: Optional[str] = None
    tarif_horaire_xaf: Optional[float] = None
    note_satisfaction: Optional[float] = None
    statut: Optional[str] = None


class MaintenanceVendorUpdate(BaseModel):
    code_prestataire: Optional[str] = None
    raison_sociale: Optional[str] = None
    pays: Optional[str] = None
    specialites: Optional[str] = None
    habilitations: Optional[str] = None
    certifications_iso: Optional[str] = None
    contact_nom: Optional[str] = None
    contact_email: Optional[str] = None
    contact_telephone: Optional[str] = None
    delai_reponse_h: Optional[int] = None
    astreinte_247: Optional[bool] = None
    zone_intervention: Optional[str] = None
    tarif_horaire_xaf: Optional[float] = None
    note_satisfaction: Optional[float] = None
    statut: Optional[str] = None
    is_active: Optional[bool] = None


class MaintenanceVendorOut(BaseModel):
    id: int
    company_id: int
    code_prestataire: str
    raison_sociale: str
    pays: Optional[str] = None
    specialites: Optional[str] = None
    habilitations: Optional[str] = None
    certifications_iso: Optional[str] = None
    contact_nom: Optional[str] = None
    contact_email: Optional[str] = None
    contact_telephone: Optional[str] = None
    delai_reponse_h: Optional[int] = None
    astreinte_247: Optional[bool] = None
    zone_intervention: Optional[str] = None
    tarif_horaire_xaf: Optional[float] = None
    note_satisfaction: Optional[float] = None
    statut: Optional[str] = None
    is_active: Optional[bool] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    model_config = {"from_attributes": True}

