"""Schemas Pydantic pour magasin-stock (genere)."""
from pydantic import BaseModel
from typing import Optional
from datetime import datetime, date


class ArticleCatalogCreate(BaseModel):
    code_sku: str
    designation: Optional[str] = None
    categorie: Optional[str] = None
    unite_principale: Optional[str] = None
    code_barre: Optional[str] = None
    poids_unitaire_kg: Optional[float] = None
    volume_m3: Optional[float] = None
    prix_achat_moyen_xaf: Optional[float] = None
    prix_vente_xaf: Optional[float] = None
    statut: Optional[str] = None


class ArticleCatalogUpdate(BaseModel):
    code_sku: Optional[str] = None
    designation: Optional[str] = None
    categorie: Optional[str] = None
    unite_principale: Optional[str] = None
    code_barre: Optional[str] = None
    poids_unitaire_kg: Optional[float] = None
    volume_m3: Optional[float] = None
    prix_achat_moyen_xaf: Optional[float] = None
    prix_vente_xaf: Optional[float] = None
    statut: Optional[str] = None
    is_active: Optional[bool] = None


class ArticleCatalogOut(BaseModel):
    id: int
    company_id: int
    code_sku: str
    designation: Optional[str] = None
    categorie: Optional[str] = None
    unite_principale: Optional[str] = None
    code_barre: Optional[str] = None
    poids_unitaire_kg: Optional[float] = None
    volume_m3: Optional[float] = None
    prix_achat_moyen_xaf: Optional[float] = None
    prix_vente_xaf: Optional[float] = None
    statut: Optional[str] = None
    is_active: Optional[bool] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    model_config = {"from_attributes": True}


class SupplierArticleCreate(BaseModel):
    reference: str
    article_id: Optional[int] = None
    fournisseur_id: Optional[int] = None
    prix_unitaire_xaf: Optional[float] = None
    delai_livraison_jours: Optional[int] = None
    quantite_min_commande: Optional[float] = None
    devise: Optional[str] = None
    conditions_paiement: Optional[str] = None
    actif: Optional[bool] = None


class SupplierArticleUpdate(BaseModel):
    reference: Optional[str] = None
    article_id: Optional[int] = None
    fournisseur_id: Optional[int] = None
    prix_unitaire_xaf: Optional[float] = None
    delai_livraison_jours: Optional[int] = None
    quantite_min_commande: Optional[float] = None
    devise: Optional[str] = None
    conditions_paiement: Optional[str] = None
    actif: Optional[bool] = None
    is_active: Optional[bool] = None


class SupplierArticleOut(BaseModel):
    id: int
    company_id: int
    reference: str
    article_id: Optional[int] = None
    fournisseur_id: Optional[int] = None
    prix_unitaire_xaf: Optional[float] = None
    delai_livraison_jours: Optional[int] = None
    quantite_min_commande: Optional[float] = None
    devise: Optional[str] = None
    conditions_paiement: Optional[str] = None
    actif: Optional[bool] = None
    is_active: Optional[bool] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    model_config = {"from_attributes": True}


class PurchaseOrderDeepCreate(BaseModel):
    numero_commande: str
    fournisseur_id: Optional[int] = None
    date_commande: Optional[date] = None
    date_livraison_prevue: Optional[date] = None
    montant_total_xaf: Optional[float] = None
    nb_lignes: Optional[int] = None
    acheteur: Optional[str] = None
    statut: Optional[str] = None
    notes: Optional[str] = None


class PurchaseOrderDeepUpdate(BaseModel):
    numero_commande: Optional[str] = None
    fournisseur_id: Optional[int] = None
    date_commande: Optional[date] = None
    date_livraison_prevue: Optional[date] = None
    montant_total_xaf: Optional[float] = None
    nb_lignes: Optional[int] = None
    acheteur: Optional[str] = None
    statut: Optional[str] = None
    notes: Optional[str] = None
    is_active: Optional[bool] = None


class PurchaseOrderDeepOut(BaseModel):
    id: int
    company_id: int
    numero_commande: str
    fournisseur_id: Optional[int] = None
    date_commande: Optional[date] = None
    date_livraison_prevue: Optional[date] = None
    montant_total_xaf: Optional[float] = None
    nb_lignes: Optional[int] = None
    acheteur: Optional[str] = None
    statut: Optional[str] = None
    notes: Optional[str] = None
    is_active: Optional[bool] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    model_config = {"from_attributes": True}


class QualityInspectionCreate(BaseModel):
    numero_controle: str
    reception_id: Optional[int] = None
    article_id: Optional[int] = None
    quantite_inspekte: Optional[float] = None
    quantite_conforme: Optional[float] = None
    quantite_rebutee: Optional[float] = None
    resultat: Optional[str] = None
    inspecteur: Optional[str] = None
    date_controle: Optional[date] = None
    observations: Optional[str] = None


class QualityInspectionUpdate(BaseModel):
    numero_controle: Optional[str] = None
    reception_id: Optional[int] = None
    article_id: Optional[int] = None
    quantite_inspekte: Optional[float] = None
    quantite_conforme: Optional[float] = None
    quantite_rebutee: Optional[float] = None
    resultat: Optional[str] = None
    inspecteur: Optional[str] = None
    date_controle: Optional[date] = None
    observations: Optional[str] = None
    is_active: Optional[bool] = None


class QualityInspectionOut(BaseModel):
    id: int
    company_id: int
    numero_controle: str
    reception_id: Optional[int] = None
    article_id: Optional[int] = None
    quantite_inspekte: Optional[float] = None
    quantite_conforme: Optional[float] = None
    quantite_rebutee: Optional[float] = None
    resultat: Optional[str] = None
    inspecteur: Optional[str] = None
    date_controle: Optional[date] = None
    observations: Optional[str] = None
    is_active: Optional[bool] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    model_config = {"from_attributes": True}


class StockAlertCreate(BaseModel):
    code_alerte: str
    article_id: Optional[int] = None
    depot_id: Optional[int] = None
    seuil_min: Optional[float] = None
    seuil_max: Optional[float] = None
    point_commande: Optional[float] = None
    quantite_actuelle: Optional[float] = None
    derniere_alerte: Optional[datetime] = None
    statut: Optional[str] = None


class StockAlertUpdate(BaseModel):
    code_alerte: Optional[str] = None
    article_id: Optional[int] = None
    depot_id: Optional[int] = None
    seuil_min: Optional[float] = None
    seuil_max: Optional[float] = None
    point_commande: Optional[float] = None
    quantite_actuelle: Optional[float] = None
    derniere_alerte: Optional[datetime] = None
    statut: Optional[str] = None
    is_active: Optional[bool] = None


class StockAlertOut(BaseModel):
    id: int
    company_id: int
    code_alerte: str
    article_id: Optional[int] = None
    depot_id: Optional[int] = None
    seuil_min: Optional[float] = None
    seuil_max: Optional[float] = None
    point_commande: Optional[float] = None
    quantite_actuelle: Optional[float] = None
    derniere_alerte: Optional[datetime] = None
    statut: Optional[str] = None
    is_active: Optional[bool] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    model_config = {"from_attributes": True}


class ExpiryRecordCreate(BaseModel):
    numero_lot: str
    article_id: Optional[int] = None
    quantite: Optional[float] = None
    date_peremption: Optional[date] = None
    date_reception: Optional[date] = None
    statut: Optional[str] = None
    notes: Optional[str] = None


class ExpiryRecordUpdate(BaseModel):
    numero_lot: Optional[str] = None
    article_id: Optional[int] = None
    quantite: Optional[float] = None
    date_peremption: Optional[date] = None
    date_reception: Optional[date] = None
    statut: Optional[str] = None
    notes: Optional[str] = None
    is_active: Optional[bool] = None


class ExpiryRecordOut(BaseModel):
    id: int
    company_id: int
    numero_lot: str
    article_id: Optional[int] = None
    quantite: Optional[float] = None
    date_peremption: Optional[date] = None
    date_reception: Optional[date] = None
    statut: Optional[str] = None
    notes: Optional[str] = None
    is_active: Optional[bool] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    model_config = {"from_attributes": True}


class SerialNumberCreate(BaseModel):
    numero_serial: str
    article_id: Optional[int] = None
    numero_lot: Optional[str] = None
    statut: Optional[str] = None
    date_entree: Optional[date] = None
    date_sortie: Optional[date] = None
    destination: Optional[str] = None
    notes: Optional[str] = None


class SerialNumberUpdate(BaseModel):
    numero_serial: Optional[str] = None
    article_id: Optional[int] = None
    numero_lot: Optional[str] = None
    statut: Optional[str] = None
    date_entree: Optional[date] = None
    date_sortie: Optional[date] = None
    destination: Optional[str] = None
    notes: Optional[str] = None
    is_active: Optional[bool] = None


class SerialNumberOut(BaseModel):
    id: int
    company_id: int
    numero_serial: str
    article_id: Optional[int] = None
    numero_lot: Optional[str] = None
    statut: Optional[str] = None
    date_entree: Optional[date] = None
    date_sortie: Optional[date] = None
    destination: Optional[str] = None
    notes: Optional[str] = None
    is_active: Optional[bool] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    model_config = {"from_attributes": True}


class PackingUnitCreate(BaseModel):
    code_uc: str
    type_uc: Optional[str] = None
    dimensions: Optional[str] = None
    poids_tare_kg: Optional[float] = None
    capacite_max_kg: Optional[float] = None
    nb_unites_principales: Optional[float] = None
    actif: Optional[bool] = None


class PackingUnitUpdate(BaseModel):
    code_uc: Optional[str] = None
    type_uc: Optional[str] = None
    dimensions: Optional[str] = None
    poids_tare_kg: Optional[float] = None
    capacite_max_kg: Optional[float] = None
    nb_unites_principales: Optional[float] = None
    actif: Optional[bool] = None
    is_active: Optional[bool] = None


class PackingUnitOut(BaseModel):
    id: int
    company_id: int
    code_uc: str
    type_uc: Optional[str] = None
    dimensions: Optional[str] = None
    poids_tare_kg: Optional[float] = None
    capacite_max_kg: Optional[float] = None
    nb_unites_principales: Optional[float] = None
    actif: Optional[bool] = None
    is_active: Optional[bool] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    model_config = {"from_attributes": True}


class StockReturnCreate(BaseModel):
    numero_retour: str
    type_retour: Optional[str] = None
    client_id: Optional[int] = None
    fournisseur_id: Optional[int] = None
    date_retour: Optional[date] = None
    article_id: Optional[int] = None
    quantite: Optional[float] = None
    motif: Optional[str] = None
    statut: Optional[str] = None


class StockReturnUpdate(BaseModel):
    numero_retour: Optional[str] = None
    type_retour: Optional[str] = None
    client_id: Optional[int] = None
    fournisseur_id: Optional[int] = None
    date_retour: Optional[date] = None
    article_id: Optional[int] = None
    quantite: Optional[float] = None
    motif: Optional[str] = None
    statut: Optional[str] = None
    is_active: Optional[bool] = None


class StockReturnOut(BaseModel):
    id: int
    company_id: int
    numero_retour: str
    type_retour: Optional[str] = None
    client_id: Optional[int] = None
    fournisseur_id: Optional[int] = None
    date_retour: Optional[date] = None
    article_id: Optional[int] = None
    quantite: Optional[float] = None
    motif: Optional[str] = None
    statut: Optional[str] = None
    is_active: Optional[bool] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    model_config = {"from_attributes": True}


class ConsignmentStockCreate(BaseModel):
    reference: str
    proprietaire_id: Optional[int] = None
    article_id: Optional[int] = None
    quantite_deposee: Optional[float] = None
    quantite_retiree: Optional[float] = None
    date_depot: Optional[date] = None
    date_limite: Optional[date] = None
    statut: Optional[str] = None
    notes: Optional[str] = None


class ConsignmentStockUpdate(BaseModel):
    reference: Optional[str] = None
    proprietaire_id: Optional[int] = None
    article_id: Optional[int] = None
    quantite_deposee: Optional[float] = None
    quantite_retiree: Optional[float] = None
    date_depot: Optional[date] = None
    date_limite: Optional[date] = None
    statut: Optional[str] = None
    notes: Optional[str] = None
    is_active: Optional[bool] = None


class ConsignmentStockOut(BaseModel):
    id: int
    company_id: int
    reference: str
    proprietaire_id: Optional[int] = None
    article_id: Optional[int] = None
    quantite_deposee: Optional[float] = None
    quantite_retiree: Optional[float] = None
    date_depot: Optional[date] = None
    date_limite: Optional[date] = None
    statut: Optional[str] = None
    notes: Optional[str] = None
    is_active: Optional[bool] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    model_config = {"from_attributes": True}


class StockValuationCreate(BaseModel):
    reference: str
    periode: Optional[str] = None
    article_id: Optional[int] = None
    methode: Optional[str] = None
    quantite_fin: Optional[float] = None
    valeur_cmup_xaf: Optional[float] = None
    valeur_coi_xaf: Optional[float] = None
    date_calcul: Optional[date] = None


class StockValuationUpdate(BaseModel):
    reference: Optional[str] = None
    periode: Optional[str] = None
    article_id: Optional[int] = None
    methode: Optional[str] = None
    quantite_fin: Optional[float] = None
    valeur_cmup_xaf: Optional[float] = None
    valeur_coi_xaf: Optional[float] = None
    date_calcul: Optional[date] = None
    is_active: Optional[bool] = None


class StockValuationOut(BaseModel):
    id: int
    company_id: int
    reference: str
    periode: Optional[str] = None
    article_id: Optional[int] = None
    methode: Optional[str] = None
    quantite_fin: Optional[float] = None
    valeur_cmup_xaf: Optional[float] = None
    valeur_coi_xaf: Optional[float] = None
    date_calcul: Optional[date] = None
    is_active: Optional[bool] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    model_config = {"from_attributes": True}


class WmsKpiCreate(BaseModel):
    reference: str
    periode_debut: Optional[date] = None
    periode_fin: Optional[date] = None
    rotation: Optional[float] = None
    rupture_pct: Optional[float] = None
    taux_service_pct: Optional[float] = None
    cadence_choix_lignes_h: Optional[float] = None
    ecart_inventaire_pct: Optional[float] = None
    notes: Optional[str] = None


class WmsKpiUpdate(BaseModel):
    reference: Optional[str] = None
    periode_debut: Optional[date] = None
    periode_fin: Optional[date] = None
    rotation: Optional[float] = None
    rupture_pct: Optional[float] = None
    taux_service_pct: Optional[float] = None
    cadence_choix_lignes_h: Optional[float] = None
    ecart_inventaire_pct: Optional[float] = None
    notes: Optional[str] = None
    is_active: Optional[bool] = None


class WmsKpiOut(BaseModel):
    id: int
    company_id: int
    reference: str
    periode_debut: Optional[date] = None
    periode_fin: Optional[date] = None
    rotation: Optional[float] = None
    rupture_pct: Optional[float] = None
    taux_service_pct: Optional[float] = None
    cadence_choix_lignes_h: Optional[float] = None
    ecart_inventaire_pct: Optional[float] = None
    notes: Optional[str] = None
    is_active: Optional[bool] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    model_config = {"from_attributes": True}

