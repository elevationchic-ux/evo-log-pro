"""Schemas Pydantic pour logistique-3pl (genere)."""
from pydantic import BaseModel
from typing import Optional
from datetime import datetime, date


class TplContractCreate(BaseModel):
    numero_contrat: str
    client: Optional[str] = None
    perimetre: Optional[str] = None
    sites_couverts: Optional[str] = None
    date_debut: Optional[date] = None
    date_fin: Optional[date] = None
    valeur_annuelle_xaf: Optional[int] = None
    statut: Optional[str] = None


class TplContractUpdate(BaseModel):
    numero_contrat: Optional[str] = None
    client: Optional[str] = None
    perimetre: Optional[str] = None
    sites_couverts: Optional[str] = None
    date_debut: Optional[date] = None
    date_fin: Optional[date] = None
    valeur_annuelle_xaf: Optional[int] = None
    statut: Optional[str] = None
    is_active: Optional[bool] = None


class TplContractOut(BaseModel):
    id: int
    company_id: int
    numero_contrat: str
    client: Optional[str] = None
    perimetre: Optional[str] = None
    sites_couverts: Optional[str] = None
    date_debut: Optional[date] = None
    date_fin: Optional[date] = None
    valeur_annuelle_xaf: Optional[int] = None
    statut: Optional[str] = None
    is_active: Optional[bool] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    model_config = {"from_attributes": True}


class TplWarehouseCreate(BaseModel):
    code_site: str
    nom: Optional[str] = None
    localisation: Optional[str] = None
    surface_m2: Optional[int] = None
    capacite_palettes: Optional[int] = None
    zones_froides: Optional[bool] = None
    contract_associe: Optional[str] = None
    statut: Optional[str] = None


class TplWarehouseUpdate(BaseModel):
    code_site: Optional[str] = None
    nom: Optional[str] = None
    localisation: Optional[str] = None
    surface_m2: Optional[int] = None
    capacite_palettes: Optional[int] = None
    zones_froides: Optional[bool] = None
    contract_associe: Optional[str] = None
    statut: Optional[str] = None
    is_active: Optional[bool] = None


class TplWarehouseOut(BaseModel):
    id: int
    company_id: int
    code_site: str
    nom: Optional[str] = None
    localisation: Optional[str] = None
    surface_m2: Optional[int] = None
    capacite_palettes: Optional[int] = None
    zones_froides: Optional[bool] = None
    contract_associe: Optional[str] = None
    statut: Optional[str] = None
    is_active: Optional[bool] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    model_config = {"from_attributes": True}


class TplCrossDockCreate(BaseModel):
    reference: str
    site: Optional[str] = None
    date_operation: Optional[datetime] = None
    nb_entrees: Optional[int] = None
    nb_sorties: Optional[int] = None
    duree_foresee_min: Optional[int] = None
    statut: Optional[str] = None


class TplCrossDockUpdate(BaseModel):
    reference: Optional[str] = None
    site: Optional[str] = None
    date_operation: Optional[datetime] = None
    nb_entrees: Optional[int] = None
    nb_sorties: Optional[int] = None
    duree_foresee_min: Optional[int] = None
    statut: Optional[str] = None
    is_active: Optional[bool] = None


class TplCrossDockOut(BaseModel):
    id: int
    company_id: int
    reference: str
    site: Optional[str] = None
    date_operation: Optional[datetime] = None
    nb_entrees: Optional[int] = None
    nb_sorties: Optional[int] = None
    duree_foresee_min: Optional[int] = None
    statut: Optional[str] = None
    is_active: Optional[bool] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    model_config = {"from_attributes": True}


class TplPickingLineCreate(BaseModel):
    reference: str
    site: Optional[str] = None
    client: Optional[str] = None
    type_preparation: Optional[str] = None
    nb_lignes: Optional[int] = None
    nb_colis: Optional[int] = None
    operateur: Optional[str] = None
    date_debut: Optional[datetime] = None
    date_fin: Optional[datetime] = None
    statut: Optional[str] = None


class TplPickingLineUpdate(BaseModel):
    reference: Optional[str] = None
    site: Optional[str] = None
    client: Optional[str] = None
    type_preparation: Optional[str] = None
    nb_lignes: Optional[int] = None
    nb_colis: Optional[int] = None
    operateur: Optional[str] = None
    date_debut: Optional[datetime] = None
    date_fin: Optional[datetime] = None
    statut: Optional[str] = None
    is_active: Optional[bool] = None


class TplPickingLineOut(BaseModel):
    id: int
    company_id: int
    reference: str
    site: Optional[str] = None
    client: Optional[str] = None
    type_preparation: Optional[str] = None
    nb_lignes: Optional[int] = None
    nb_colis: Optional[int] = None
    operateur: Optional[str] = None
    date_debut: Optional[datetime] = None
    date_fin: Optional[datetime] = None
    statut: Optional[str] = None
    is_active: Optional[bool] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    model_config = {"from_attributes": True}


class TplSlaKpiCreate(BaseModel):
    reference: str
    contrat_associe: Optional[str] = None
    periode: Optional[str] = None
    kpi: Optional[str] = None
    valeur_cible: Optional[str] = None
    valeur_reelle: Optional[str] = None
    penalite_appliquee_xaf: Optional[int] = None
    statut: Optional[str] = None


class TplSlaKpiUpdate(BaseModel):
    reference: Optional[str] = None
    contrat_associe: Optional[str] = None
    periode: Optional[str] = None
    kpi: Optional[str] = None
    valeur_cible: Optional[str] = None
    valeur_reelle: Optional[str] = None
    penalite_appliquee_xaf: Optional[int] = None
    statut: Optional[str] = None
    is_active: Optional[bool] = None


class TplSlaKpiOut(BaseModel):
    id: int
    company_id: int
    reference: str
    contrat_associe: Optional[str] = None
    periode: Optional[str] = None
    kpi: Optional[str] = None
    valeur_cible: Optional[str] = None
    valeur_reelle: Optional[str] = None
    penalite_appliquee_xaf: Optional[int] = None
    statut: Optional[str] = None
    is_active: Optional[bool] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    model_config = {"from_attributes": True}


class TplInvoiceCreate(BaseModel):
    numero_facture: str
    client: Optional[str] = None
    periode: Optional[str] = None
    montant_ht_xaf: Optional[int] = None
    tva_xaf: Optional[int] = None
    total_ttc_xaf: Optional[int] = None
    date_emission: Optional[date] = None
    statut: Optional[str] = None


class TplInvoiceUpdate(BaseModel):
    numero_facture: Optional[str] = None
    client: Optional[str] = None
    periode: Optional[str] = None
    montant_ht_xaf: Optional[int] = None
    tva_xaf: Optional[int] = None
    total_ttc_xaf: Optional[int] = None
    date_emission: Optional[date] = None
    statut: Optional[str] = None
    is_active: Optional[bool] = None


class TplInvoiceOut(BaseModel):
    id: int
    company_id: int
    numero_facture: str
    client: Optional[str] = None
    periode: Optional[str] = None
    montant_ht_xaf: Optional[int] = None
    tva_xaf: Optional[int] = None
    total_ttc_xaf: Optional[int] = None
    date_emission: Optional[date] = None
    statut: Optional[str] = None
    is_active: Optional[bool] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    model_config = {"from_attributes": True}


class TplInventoryValuationCreate(BaseModel):
    reference: str
    site: Optional[str] = None
    client: Optional[str] = None
    date_inventaire: Optional[date] = None
    valeur_theorique_xaf: Optional[int] = None
    valeur_physique_xaf: Optional[int] = None
    ecart_pct: Optional[int] = None
    statut: Optional[str] = None


class TplInventoryValuationUpdate(BaseModel):
    reference: Optional[str] = None
    site: Optional[str] = None
    client: Optional[str] = None
    date_inventaire: Optional[date] = None
    valeur_theorique_xaf: Optional[int] = None
    valeur_physique_xaf: Optional[int] = None
    ecart_pct: Optional[int] = None
    statut: Optional[str] = None
    is_active: Optional[bool] = None


class TplInventoryValuationOut(BaseModel):
    id: int
    company_id: int
    reference: str
    site: Optional[str] = None
    client: Optional[str] = None
    date_inventaire: Optional[date] = None
    valeur_theorique_xaf: Optional[int] = None
    valeur_physique_xaf: Optional[int] = None
    ecart_pct: Optional[int] = None
    statut: Optional[str] = None
    is_active: Optional[bool] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    model_config = {"from_attributes": True}


class TplSubProviderCreate(BaseModel):
    code_fournisseur: str
    raison_sociale: Optional[str] = None
    type_prestation: Optional[str] = None
    zone_couverte: Optional[str] = None
    date_debut_contrat: Optional[date] = None
    date_audit_precedent: Optional[date] = None
    note_qualite: Optional[str] = None
    statut: Optional[str] = None


class TplSubProviderUpdate(BaseModel):
    code_fournisseur: Optional[str] = None
    raison_sociale: Optional[str] = None
    type_prestation: Optional[str] = None
    zone_couverte: Optional[str] = None
    date_debut_contrat: Optional[date] = None
    date_audit_precedent: Optional[date] = None
    note_qualite: Optional[str] = None
    statut: Optional[str] = None
    is_active: Optional[bool] = None


class TplSubProviderOut(BaseModel):
    id: int
    company_id: int
    code_fournisseur: str
    raison_sociale: Optional[str] = None
    type_prestation: Optional[str] = None
    zone_couverte: Optional[str] = None
    date_debut_contrat: Optional[date] = None
    date_audit_precedent: Optional[date] = None
    note_qualite: Optional[str] = None
    statut: Optional[str] = None
    is_active: Optional[bool] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    model_config = {"from_attributes": True}


class TplReverseOperationCreate(BaseModel):
    reference: str
    client: Optional[str] = None
    type_operation: Optional[str] = None
    nb_unites: Optional[int] = None
    site_prise_en_charge: Optional[str] = None
    date_prise_en_charge: Optional[date] = None
    statut: Optional[str] = None


class TplReverseOperationUpdate(BaseModel):
    reference: Optional[str] = None
    client: Optional[str] = None
    type_operation: Optional[str] = None
    nb_unites: Optional[int] = None
    site_prise_en_charge: Optional[str] = None
    date_prise_en_charge: Optional[date] = None
    statut: Optional[str] = None
    is_active: Optional[bool] = None


class TplReverseOperationOut(BaseModel):
    id: int
    company_id: int
    reference: str
    client: Optional[str] = None
    type_operation: Optional[str] = None
    nb_unites: Optional[int] = None
    site_prise_en_charge: Optional[str] = None
    date_prise_en_charge: Optional[date] = None
    statut: Optional[str] = None
    is_active: Optional[bool] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    model_config = {"from_attributes": True}


class TplControlTowerCreate(BaseModel):
    reference: str
    client: Optional[str] = None
    date_horodatage: Optional[datetime] = None
    nombre_alertes: Optional[int] = None
    nombre_incidents: Optional[int] = None
    taux_service_pct: Optional[int] = None
    operateur_tour: Optional[str] = None
    statut: Optional[str] = None


class TplControlTowerUpdate(BaseModel):
    reference: Optional[str] = None
    client: Optional[str] = None
    date_horodatage: Optional[datetime] = None
    nombre_alertes: Optional[int] = None
    nombre_incidents: Optional[int] = None
    taux_service_pct: Optional[int] = None
    operateur_tour: Optional[str] = None
    statut: Optional[str] = None
    is_active: Optional[bool] = None


class TplControlTowerOut(BaseModel):
    id: int
    company_id: int
    reference: str
    client: Optional[str] = None
    date_horodatage: Optional[datetime] = None
    nombre_alertes: Optional[int] = None
    nombre_incidents: Optional[int] = None
    taux_service_pct: Optional[int] = None
    operateur_tour: Optional[str] = None
    statut: Optional[str] = None
    is_active: Optional[bool] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    model_config = {"from_attributes": True}

