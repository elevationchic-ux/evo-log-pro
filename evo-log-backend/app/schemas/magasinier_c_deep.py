"""Schemas Pydantic pour portail-magasinier (genere)."""
from pydantic import BaseModel
from typing import Optional
from datetime import datetime, date


class MagcPickingTaskCreate(BaseModel):
    reference: str
    ordre: Optional[str] = None
    emplacement: Optional[str] = None
    quantite: Optional[int] = None
    prepareur: Optional[str] = None
    statut: Optional[str] = None


class MagcPickingTaskUpdate(BaseModel):
    reference: Optional[str] = None
    ordre: Optional[str] = None
    emplacement: Optional[str] = None
    quantite: Optional[int] = None
    prepareur: Optional[str] = None
    statut: Optional[str] = None
    is_active: Optional[bool] = None


class MagcPickingTaskOut(BaseModel):
    id: int
    company_id: int
    reference: str
    ordre: Optional[str] = None
    emplacement: Optional[str] = None
    quantite: Optional[int] = None
    prepareur: Optional[str] = None
    statut: Optional[str] = None
    is_active: Optional[bool] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    model_config = {"from_attributes": True}


class MagcPackingSlipCreate(BaseModel):
    reference: str
    commande: Optional[str] = None
    nb_colis: Optional[int] = None
    poids: Optional[float] = None
    operateur: Optional[str] = None
    statut: Optional[str] = None


class MagcPackingSlipUpdate(BaseModel):
    reference: Optional[str] = None
    commande: Optional[str] = None
    nb_colis: Optional[int] = None
    poids: Optional[float] = None
    operateur: Optional[str] = None
    statut: Optional[str] = None
    is_active: Optional[bool] = None


class MagcPackingSlipOut(BaseModel):
    id: int
    company_id: int
    reference: str
    commande: Optional[str] = None
    nb_colis: Optional[int] = None
    poids: Optional[float] = None
    operateur: Optional[str] = None
    statut: Optional[str] = None
    is_active: Optional[bool] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    model_config = {"from_attributes": True}


class MagcPutawayTaskCreate(BaseModel):
    reference: str
    article: Optional[str] = None
    quantite: Optional[int] = None
    de: Optional[str] = None
    vers: Optional[str] = None
    statut: Optional[str] = None


class MagcPutawayTaskUpdate(BaseModel):
    reference: Optional[str] = None
    article: Optional[str] = None
    quantite: Optional[int] = None
    de: Optional[str] = None
    vers: Optional[str] = None
    statut: Optional[str] = None
    is_active: Optional[bool] = None


class MagcPutawayTaskOut(BaseModel):
    id: int
    company_id: int
    reference: str
    article: Optional[str] = None
    quantite: Optional[int] = None
    de: Optional[str] = None
    vers: Optional[str] = None
    statut: Optional[str] = None
    is_active: Optional[bool] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    model_config = {"from_attributes": True}


class MagcCycleCountCreate(BaseModel):
    reference: str
    emplacement: Optional[str] = None
    theorique: Optional[int] = None
    physique: Optional[int] = None
    compteur: Optional[str] = None
    statut: Optional[str] = None


class MagcCycleCountUpdate(BaseModel):
    reference: Optional[str] = None
    emplacement: Optional[str] = None
    theorique: Optional[int] = None
    physique: Optional[int] = None
    compteur: Optional[str] = None
    statut: Optional[str] = None
    is_active: Optional[bool] = None


class MagcCycleCountOut(BaseModel):
    id: int
    company_id: int
    reference: str
    emplacement: Optional[str] = None
    theorique: Optional[int] = None
    physique: Optional[int] = None
    compteur: Optional[str] = None
    statut: Optional[str] = None
    is_active: Optional[bool] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    model_config = {"from_attributes": True}


class MagcInternalMoveCreate(BaseModel):
    reference: str
    article: Optional[str] = None
    quantite: Optional[int] = None
    origine: Optional[str] = None
    destination: Optional[str] = None
    statut: Optional[str] = None


class MagcInternalMoveUpdate(BaseModel):
    reference: Optional[str] = None
    article: Optional[str] = None
    quantite: Optional[int] = None
    origine: Optional[str] = None
    destination: Optional[str] = None
    statut: Optional[str] = None
    is_active: Optional[bool] = None


class MagcInternalMoveOut(BaseModel):
    id: int
    company_id: int
    reference: str
    article: Optional[str] = None
    quantite: Optional[int] = None
    origine: Optional[str] = None
    destination: Optional[str] = None
    statut: Optional[str] = None
    is_active: Optional[bool] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    model_config = {"from_attributes": True}


class MagcGoodsIssueCreate(BaseModel):
    reference: str
    demande: Optional[str] = None
    article: Optional[str] = None
    quantite: Optional[int] = None
    beneficiaire: Optional[str] = None
    statut: Optional[str] = None


class MagcGoodsIssueUpdate(BaseModel):
    reference: Optional[str] = None
    demande: Optional[str] = None
    article: Optional[str] = None
    quantite: Optional[int] = None
    beneficiaire: Optional[str] = None
    statut: Optional[str] = None
    is_active: Optional[bool] = None


class MagcGoodsIssueOut(BaseModel):
    id: int
    company_id: int
    reference: str
    demande: Optional[str] = None
    article: Optional[str] = None
    quantite: Optional[int] = None
    beneficiaire: Optional[str] = None
    statut: Optional[str] = None
    is_active: Optional[bool] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    model_config = {"from_attributes": True}


class MagcReturnProcessingCreate(BaseModel):
    reference: str
    retour: Optional[str] = None
    article: Optional[str] = None
    quantite: Optional[int] = None
    motif: Optional[str] = None
    statut: Optional[str] = None


class MagcReturnProcessingUpdate(BaseModel):
    reference: Optional[str] = None
    retour: Optional[str] = None
    article: Optional[str] = None
    quantite: Optional[int] = None
    motif: Optional[str] = None
    statut: Optional[str] = None
    is_active: Optional[bool] = None


class MagcReturnProcessingOut(BaseModel):
    id: int
    company_id: int
    reference: str
    retour: Optional[str] = None
    article: Optional[str] = None
    quantite: Optional[int] = None
    motif: Optional[str] = None
    statut: Optional[str] = None
    is_active: Optional[bool] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    model_config = {"from_attributes": True}


class MagcLabelPrintCreate(BaseModel):
    reference: str
    article: Optional[str] = None
    nombre: Optional[int] = None
    type_etiquette: Optional[str] = None
    operateur: Optional[str] = None
    statut: Optional[str] = None


class MagcLabelPrintUpdate(BaseModel):
    reference: Optional[str] = None
    article: Optional[str] = None
    nombre: Optional[int] = None
    type_etiquette: Optional[str] = None
    operateur: Optional[str] = None
    statut: Optional[str] = None
    is_active: Optional[bool] = None


class MagcLabelPrintOut(BaseModel):
    id: int
    company_id: int
    reference: str
    article: Optional[str] = None
    nombre: Optional[int] = None
    type_etiquette: Optional[str] = None
    operateur: Optional[str] = None
    statut: Optional[str] = None
    is_active: Optional[bool] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    model_config = {"from_attributes": True}


class MagcPalletBuildCreate(BaseModel):
    reference: str
    commande: Optional[str] = None
    nb_cartons: Optional[int] = None
    hauteur_cm: Optional[int] = None
    poids_total: Optional[float] = None
    statut: Optional[str] = None


class MagcPalletBuildUpdate(BaseModel):
    reference: Optional[str] = None
    commande: Optional[str] = None
    nb_cartons: Optional[int] = None
    hauteur_cm: Optional[int] = None
    poids_total: Optional[float] = None
    statut: Optional[str] = None
    is_active: Optional[bool] = None


class MagcPalletBuildOut(BaseModel):
    id: int
    company_id: int
    reference: str
    commande: Optional[str] = None
    nb_cartons: Optional[int] = None
    hauteur_cm: Optional[int] = None
    poids_total: Optional[float] = None
    statut: Optional[str] = None
    is_active: Optional[bool] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    model_config = {"from_attributes": True}


class MagcEquipmentCheckCreate(BaseModel):
    reference: str
    equipment: Optional[str] = None
    numero: Optional[str] = None
    controleur: Optional[str] = None
    date_controle: Optional[datetime] = None
    statut: Optional[str] = None


class MagcEquipmentCheckUpdate(BaseModel):
    reference: Optional[str] = None
    equipment: Optional[str] = None
    numero: Optional[str] = None
    controleur: Optional[str] = None
    date_controle: Optional[datetime] = None
    statut: Optional[str] = None
    is_active: Optional[bool] = None


class MagcEquipmentCheckOut(BaseModel):
    id: int
    company_id: int
    reference: str
    equipment: Optional[str] = None
    numero: Optional[str] = None
    controleur: Optional[str] = None
    date_controle: Optional[datetime] = None
    statut: Optional[str] = None
    is_active: Optional[bool] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    model_config = {"from_attributes": True}


class MagcSafetyInspectionCreate(BaseModel):
    reference: str
    zone: Optional[str] = None
    inspecteur: Optional[str] = None
    date: Optional[datetime] = None
    anomalies: Optional[int] = None
    statut: Optional[str] = None


class MagcSafetyInspectionUpdate(BaseModel):
    reference: Optional[str] = None
    zone: Optional[str] = None
    inspecteur: Optional[str] = None
    date: Optional[datetime] = None
    anomalies: Optional[int] = None
    statut: Optional[str] = None
    is_active: Optional[bool] = None


class MagcSafetyInspectionOut(BaseModel):
    id: int
    company_id: int
    reference: str
    zone: Optional[str] = None
    inspecteur: Optional[str] = None
    date: Optional[datetime] = None
    anomalies: Optional[int] = None
    statut: Optional[str] = None
    is_active: Optional[bool] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    model_config = {"from_attributes": True}


class MagcSpillCleanupCreate(BaseModel):
    reference: str
    zone: Optional[str] = None
    produit: Optional[str] = None
    volume: Optional[float] = None
    date: Optional[datetime] = None
    statut: Optional[str] = None


class MagcSpillCleanupUpdate(BaseModel):
    reference: Optional[str] = None
    zone: Optional[str] = None
    produit: Optional[str] = None
    volume: Optional[float] = None
    date: Optional[datetime] = None
    statut: Optional[str] = None
    is_active: Optional[bool] = None


class MagcSpillCleanupOut(BaseModel):
    id: int
    company_id: int
    reference: str
    zone: Optional[str] = None
    produit: Optional[str] = None
    volume: Optional[float] = None
    date: Optional[datetime] = None
    statut: Optional[str] = None
    is_active: Optional[bool] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    model_config = {"from_attributes": True}


class MagcLoadingCheckCreate(BaseModel):
    reference: str
    chargement: Optional[str] = None
    camion: Optional[str] = None
    nb_colis: Optional[int] = None
    chargeur: Optional[str] = None
    statut: Optional[str] = None


class MagcLoadingCheckUpdate(BaseModel):
    reference: Optional[str] = None
    chargement: Optional[str] = None
    camion: Optional[str] = None
    nb_colis: Optional[int] = None
    chargeur: Optional[str] = None
    statut: Optional[str] = None
    is_active: Optional[bool] = None


class MagcLoadingCheckOut(BaseModel):
    id: int
    company_id: int
    reference: str
    chargement: Optional[str] = None
    camion: Optional[str] = None
    nb_colis: Optional[int] = None
    chargeur: Optional[str] = None
    statut: Optional[str] = None
    is_active: Optional[bool] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    model_config = {"from_attributes": True}


class MagcReceivingCheckCreate(BaseModel):
    reference: str
    reception: Optional[str] = None
    fournisseur: Optional[str] = None
    nb_colis: Optional[int] = None
    conforme: Optional[bool] = None
    statut: Optional[str] = None


class MagcReceivingCheckUpdate(BaseModel):
    reference: Optional[str] = None
    reception: Optional[str] = None
    fournisseur: Optional[str] = None
    nb_colis: Optional[int] = None
    conforme: Optional[bool] = None
    statut: Optional[str] = None
    is_active: Optional[bool] = None


class MagcReceivingCheckOut(BaseModel):
    id: int
    company_id: int
    reference: str
    reception: Optional[str] = None
    fournisseur: Optional[str] = None
    nb_colis: Optional[int] = None
    conforme: Optional[bool] = None
    statut: Optional[str] = None
    is_active: Optional[bool] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    model_config = {"from_attributes": True}


class MagcPutawayExceptionCreate(BaseModel):
    reference: str
    article: Optional[str] = None
    emplacement: Optional[str] = None
    type_probleme: Optional[str] = None
    signale_le: Optional[datetime] = None
    statut: Optional[str] = None


class MagcPutawayExceptionUpdate(BaseModel):
    reference: Optional[str] = None
    article: Optional[str] = None
    emplacement: Optional[str] = None
    type_probleme: Optional[str] = None
    signale_le: Optional[datetime] = None
    statut: Optional[str] = None
    is_active: Optional[bool] = None


class MagcPutawayExceptionOut(BaseModel):
    id: int
    company_id: int
    reference: str
    article: Optional[str] = None
    emplacement: Optional[str] = None
    type_probleme: Optional[str] = None
    signale_le: Optional[datetime] = None
    statut: Optional[str] = None
    is_active: Optional[bool] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    model_config = {"from_attributes": True}


class MagcOrderStagingCreate(BaseModel):
    reference: str
    commande: Optional[str] = None
    zone_prea: Optional[str] = None
    nb_lignes: Optional[int] = None
    operateur: Optional[str] = None
    statut: Optional[str] = None


class MagcOrderStagingUpdate(BaseModel):
    reference: Optional[str] = None
    commande: Optional[str] = None
    zone_prea: Optional[str] = None
    nb_lignes: Optional[int] = None
    operateur: Optional[str] = None
    statut: Optional[str] = None
    is_active: Optional[bool] = None


class MagcOrderStagingOut(BaseModel):
    id: int
    company_id: int
    reference: str
    commande: Optional[str] = None
    zone_prea: Optional[str] = None
    nb_lignes: Optional[int] = None
    operateur: Optional[str] = None
    statut: Optional[str] = None
    is_active: Optional[bool] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    model_config = {"from_attributes": True}


class MagcColdChainCheckCreate(BaseModel):
    reference: str
    chambre_froide: Optional[str] = None
    temperature_c: Optional[float] = None
    seuil_mini: Optional[float] = None
    seuil_maxi: Optional[float] = None
    statut: Optional[str] = None


class MagcColdChainCheckUpdate(BaseModel):
    reference: Optional[str] = None
    chambre_froide: Optional[str] = None
    temperature_c: Optional[float] = None
    seuil_mini: Optional[float] = None
    seuil_maxi: Optional[float] = None
    statut: Optional[str] = None
    is_active: Optional[bool] = None


class MagcColdChainCheckOut(BaseModel):
    id: int
    company_id: int
    reference: str
    chambre_froide: Optional[str] = None
    temperature_c: Optional[float] = None
    seuil_mini: Optional[float] = None
    seuil_maxi: Optional[float] = None
    statut: Optional[str] = None
    is_active: Optional[bool] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    model_config = {"from_attributes": True}


class MagcHazmatHandlingCreate(BaseModel):
    reference: str
    matiere: Optional[str] = None
    classe: Optional[str] = None
    quantite: Optional[float] = None
    operateur: Optional[str] = None
    statut: Optional[str] = None


class MagcHazmatHandlingUpdate(BaseModel):
    reference: Optional[str] = None
    matiere: Optional[str] = None
    classe: Optional[str] = None
    quantite: Optional[float] = None
    operateur: Optional[str] = None
    statut: Optional[str] = None
    is_active: Optional[bool] = None


class MagcHazmatHandlingOut(BaseModel):
    id: int
    company_id: int
    reference: str
    matiere: Optional[str] = None
    classe: Optional[str] = None
    quantite: Optional[float] = None
    operateur: Optional[str] = None
    statut: Optional[str] = None
    is_active: Optional[bool] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    model_config = {"from_attributes": True}


class MagcDockAssignmentCreate(BaseModel):
    reference: str
    quai: Optional[str] = None
    camion: Optional[str] = None
    creneau: Optional[datetime] = None
    operateur: Optional[str] = None
    statut: Optional[str] = None


class MagcDockAssignmentUpdate(BaseModel):
    reference: Optional[str] = None
    quai: Optional[str] = None
    camion: Optional[str] = None
    creneau: Optional[datetime] = None
    operateur: Optional[str] = None
    statut: Optional[str] = None
    is_active: Optional[bool] = None


class MagcDockAssignmentOut(BaseModel):
    id: int
    company_id: int
    reference: str
    quai: Optional[str] = None
    camion: Optional[str] = None
    creneau: Optional[datetime] = None
    operateur: Optional[str] = None
    statut: Optional[str] = None
    is_active: Optional[bool] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    model_config = {"from_attributes": True}

