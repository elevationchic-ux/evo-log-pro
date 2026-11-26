"""Schemas Pydantic pour logistique-3pl (genere)."""
from pydantic import BaseModel
from typing import Optional
from datetime import datetime, date


class TplDockAppointmentCreate(BaseModel):
    reference: str
    site: Optional[str] = None
    numero_quai: Optional[str] = None
    date_debut: Optional[datetime] = None
    date_fin: Optional[datetime] = None
    immatriculation: Optional[str] = None
    type_mouvement: Optional[str] = None
    statut: Optional[str] = None


class TplDockAppointmentUpdate(BaseModel):
    reference: Optional[str] = None
    site: Optional[str] = None
    numero_quai: Optional[str] = None
    date_debut: Optional[datetime] = None
    date_fin: Optional[datetime] = None
    immatriculation: Optional[str] = None
    type_mouvement: Optional[str] = None
    statut: Optional[str] = None
    is_active: Optional[bool] = None


class TplDockAppointmentOut(BaseModel):
    id: int
    company_id: int
    reference: str
    site: Optional[str] = None
    numero_quai: Optional[str] = None
    date_debut: Optional[datetime] = None
    date_fin: Optional[datetime] = None
    immatriculation: Optional[str] = None
    type_mouvement: Optional[str] = None
    statut: Optional[str] = None
    is_active: Optional[bool] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    model_config = {"from_attributes": True}


class TplLoadingPlanCreate(BaseModel):
    reference: str
    site: Optional[str] = None
    numero_camion: Optional[str] = None
    nb_colis: Optional[int] = None
    poids_total_kg: Optional[int] = None
    volume_m3: Optional[int] = None
    taux_remplissage_pct: Optional[int] = None
    date_plan: Optional[datetime] = None
    statut: Optional[str] = None


class TplLoadingPlanUpdate(BaseModel):
    reference: Optional[str] = None
    site: Optional[str] = None
    numero_camion: Optional[str] = None
    nb_colis: Optional[int] = None
    poids_total_kg: Optional[int] = None
    volume_m3: Optional[int] = None
    taux_remplissage_pct: Optional[int] = None
    date_plan: Optional[datetime] = None
    statut: Optional[str] = None
    is_active: Optional[bool] = None


class TplLoadingPlanOut(BaseModel):
    id: int
    company_id: int
    reference: str
    site: Optional[str] = None
    numero_camion: Optional[str] = None
    nb_colis: Optional[int] = None
    poids_total_kg: Optional[int] = None
    volume_m3: Optional[int] = None
    taux_remplissage_pct: Optional[int] = None
    date_plan: Optional[datetime] = None
    statut: Optional[str] = None
    is_active: Optional[bool] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    model_config = {"from_attributes": True}


class TplShipmentManifestCreate(BaseModel):
    numero_manifeste: str
    client: Optional[str] = None
    site_depart: Optional[str] = None
    site_arrivee: Optional[str] = None
    nb_colis: Optional[int] = None
    poids_total_kg: Optional[int] = None
    date_emission: Optional[date] = None
    statut: Optional[str] = None


class TplShipmentManifestUpdate(BaseModel):
    numero_manifeste: Optional[str] = None
    client: Optional[str] = None
    site_depart: Optional[str] = None
    site_arrivee: Optional[str] = None
    nb_colis: Optional[int] = None
    poids_total_kg: Optional[int] = None
    date_emission: Optional[date] = None
    statut: Optional[str] = None
    is_active: Optional[bool] = None


class TplShipmentManifestOut(BaseModel):
    id: int
    company_id: int
    numero_manifeste: str
    client: Optional[str] = None
    site_depart: Optional[str] = None
    site_arrivee: Optional[str] = None
    nb_colis: Optional[int] = None
    poids_total_kg: Optional[int] = None
    date_emission: Optional[date] = None
    statut: Optional[str] = None
    is_active: Optional[bool] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    model_config = {"from_attributes": True}


class TplInventoryTransferCreate(BaseModel):
    reference: str
    site_source: Optional[str] = None
    site_destinataire: Optional[str] = None
    sku: Optional[str] = None
    quantite_expediee: Optional[int] = None
    quantite_recue: Optional[int] = None
    date_transfert: Optional[date] = None
    statut: Optional[str] = None


class TplInventoryTransferUpdate(BaseModel):
    reference: Optional[str] = None
    site_source: Optional[str] = None
    site_destinataire: Optional[str] = None
    sku: Optional[str] = None
    quantite_expediee: Optional[int] = None
    quantite_recue: Optional[int] = None
    date_transfert: Optional[date] = None
    statut: Optional[str] = None
    is_active: Optional[bool] = None


class TplInventoryTransferOut(BaseModel):
    id: int
    company_id: int
    reference: str
    site_source: Optional[str] = None
    site_destinataire: Optional[str] = None
    sku: Optional[str] = None
    quantite_expediee: Optional[int] = None
    quantite_recue: Optional[int] = None
    date_transfert: Optional[date] = None
    statut: Optional[str] = None
    is_active: Optional[bool] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    model_config = {"from_attributes": True}


class TplColdChainLogCreate(BaseModel):
    reference: str
    site: Optional[str] = None
    produit: Optional[str] = None
    sonde: Optional[str] = None
    temperature_c: Optional[float] = None
    plage_min_c: Optional[float] = None
    plage_max_c: Optional[float] = None
    date_releve: Optional[datetime] = None
    statut: Optional[str] = None


class TplColdChainLogUpdate(BaseModel):
    reference: Optional[str] = None
    site: Optional[str] = None
    produit: Optional[str] = None
    sonde: Optional[str] = None
    temperature_c: Optional[float] = None
    plage_min_c: Optional[float] = None
    plage_max_c: Optional[float] = None
    date_releve: Optional[datetime] = None
    statut: Optional[str] = None
    is_active: Optional[bool] = None


class TplColdChainLogOut(BaseModel):
    id: int
    company_id: int
    reference: str
    site: Optional[str] = None
    produit: Optional[str] = None
    sonde: Optional[str] = None
    temperature_c: Optional[float] = None
    plage_min_c: Optional[float] = None
    plage_max_c: Optional[float] = None
    date_releve: Optional[datetime] = None
    statut: Optional[str] = None
    is_active: Optional[bool] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    model_config = {"from_attributes": True}


class TplReturnAuthorizationCreate(BaseModel):
    numero_rma: str
    client: Optional[str] = None
    commande_originale: Optional[str] = None
    motif_retour: Optional[str] = None
    nb_unites: Optional[int] = None
    date_demande: Optional[date] = None
    decision: Optional[str] = None
    statut: Optional[str] = None


class TplReturnAuthorizationUpdate(BaseModel):
    numero_rma: Optional[str] = None
    client: Optional[str] = None
    commande_originale: Optional[str] = None
    motif_retour: Optional[str] = None
    nb_unites: Optional[int] = None
    date_demande: Optional[date] = None
    decision: Optional[str] = None
    statut: Optional[str] = None
    is_active: Optional[bool] = None


class TplReturnAuthorizationOut(BaseModel):
    id: int
    company_id: int
    numero_rma: str
    client: Optional[str] = None
    commande_originale: Optional[str] = None
    motif_retour: Optional[str] = None
    nb_unites: Optional[int] = None
    date_demande: Optional[date] = None
    decision: Optional[str] = None
    statut: Optional[str] = None
    is_active: Optional[bool] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    model_config = {"from_attributes": True}


class TplCarrierRateCreate(BaseModel):
    code_tarif: str
    transporteur: Optional[str] = None
    zone: Optional[str] = None
    poids_kg: Optional[int] = None
    prix_base_xaf: Optional[int] = None
    prix_par_kg_xaf: Optional[int] = None
    validite_debut: Optional[date] = None
    validite_fin: Optional[date] = None
    statut: Optional[str] = None


class TplCarrierRateUpdate(BaseModel):
    code_tarif: Optional[str] = None
    transporteur: Optional[str] = None
    zone: Optional[str] = None
    poids_kg: Optional[int] = None
    prix_base_xaf: Optional[int] = None
    prix_par_kg_xaf: Optional[int] = None
    validite_debut: Optional[date] = None
    validite_fin: Optional[date] = None
    statut: Optional[str] = None
    is_active: Optional[bool] = None


class TplCarrierRateOut(BaseModel):
    id: int
    company_id: int
    code_tarif: str
    transporteur: Optional[str] = None
    zone: Optional[str] = None
    poids_kg: Optional[int] = None
    prix_base_xaf: Optional[int] = None
    prix_par_kg_xaf: Optional[int] = None
    validite_debut: Optional[date] = None
    validite_fin: Optional[date] = None
    statut: Optional[str] = None
    is_active: Optional[bool] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    model_config = {"from_attributes": True}


class TplOrderNodeCreate(BaseModel):
    reference: str
    numero_commande: Optional[str] = None
    code_jalon: Optional[str] = None
    libelle_jalon: Optional[str] = None
    date_horodatage: Optional[datetime] = None
    lieu: Optional[str] = None
    operateur: Optional[str] = None
    statut: Optional[str] = None


class TplOrderNodeUpdate(BaseModel):
    reference: Optional[str] = None
    numero_commande: Optional[str] = None
    code_jalon: Optional[str] = None
    libelle_jalon: Optional[str] = None
    date_horodatage: Optional[datetime] = None
    lieu: Optional[str] = None
    operateur: Optional[str] = None
    statut: Optional[str] = None
    is_active: Optional[bool] = None


class TplOrderNodeOut(BaseModel):
    id: int
    company_id: int
    reference: str
    numero_commande: Optional[str] = None
    code_jalon: Optional[str] = None
    libelle_jalon: Optional[str] = None
    date_horodatage: Optional[datetime] = None
    lieu: Optional[str] = None
    operateur: Optional[str] = None
    statut: Optional[str] = None
    is_active: Optional[bool] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    model_config = {"from_attributes": True}


class TplDamageClaimCreate(BaseModel):
    numero_dossier: str
    client: Optional[str] = None
    expedition_associee: Optional[str] = None
    type_avarie: Optional[str] = None
    montant_reclame_xaf: Optional[int] = None
    date_ouverture: Optional[date] = None
    date_resolution: Optional[date] = None
    statut: Optional[str] = None


class TplDamageClaimUpdate(BaseModel):
    numero_dossier: Optional[str] = None
    client: Optional[str] = None
    expedition_associee: Optional[str] = None
    type_avarie: Optional[str] = None
    montant_reclame_xaf: Optional[int] = None
    date_ouverture: Optional[date] = None
    date_resolution: Optional[date] = None
    statut: Optional[str] = None
    is_active: Optional[bool] = None


class TplDamageClaimOut(BaseModel):
    id: int
    company_id: int
    numero_dossier: str
    client: Optional[str] = None
    expedition_associee: Optional[str] = None
    type_avarie: Optional[str] = None
    montant_reclame_xaf: Optional[int] = None
    date_ouverture: Optional[date] = None
    date_resolution: Optional[date] = None
    statut: Optional[str] = None
    is_active: Optional[bool] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    model_config = {"from_attributes": True}

