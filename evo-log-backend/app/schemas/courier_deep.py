"""Schemas Pydantic auto- genere (expansion wave 5)."""
from pydantic import BaseModel
from typing import Optional
from datetime import datetime, date


class CourierParcelCreate(BaseModel):
    numero_colis: str
    type_colis: Optional[str] = None
    format: Optional[str] = None
    poids_kg: Optional[int] = None
    dimensions_cm: Optional[str] = None
    valeur_declaree_xaf: Optional[int] = None
    expediteur: Optional[str] = None
    destinataire: Optional[str] = None
    date_prise_en_charge: Optional[date] = None
    date_livraison: Optional[date] = None
    statut: Optional[str] = None


class CourierParcelUpdate(BaseModel):
    numero_colis: Optional[str] = None
    type_colis: Optional[str] = None
    format: Optional[str] = None
    poids_kg: Optional[int] = None
    dimensions_cm: Optional[str] = None
    valeur_declaree_xaf: Optional[int] = None
    expediteur: Optional[str] = None
    destinataire: Optional[str] = None
    date_prise_en_charge: Optional[date] = None
    date_livraison: Optional[date] = None
    statut: Optional[str] = None
    is_active: Optional[bool] = None


class CourierParcelOut(BaseModel):
    id: int
    company_id: int
    numero_colis: str
    type_colis: Optional[str] = None
    format: Optional[str] = None
    poids_kg: Optional[int] = None
    dimensions_cm: Optional[str] = None
    valeur_declaree_xaf: Optional[int] = None
    expediteur: Optional[str] = None
    destinataire: Optional[str] = None
    date_prise_en_charge: Optional[date] = None
    date_livraison: Optional[date] = None
    statut: Optional[str] = None
    is_active: Optional[bool] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    model_config = {"from_attributes": True}


class CourierWaybillCreate(BaseModel):
    numero_lse: str
    type_service: Optional[str] = None
    client: Optional[str] = None
    nb_colis: Optional[int] = None
    poids_total_kg: Optional[int] = None
    montant_facture_xaf: Optional[int] = None
    date_emission: Optional[date] = None
    date_livraison_prevue: Optional[date] = None
    date_livraison_reelle: Optional[date] = None
    statut: Optional[str] = None


class CourierWaybillUpdate(BaseModel):
    numero_lse: Optional[str] = None
    type_service: Optional[str] = None
    client: Optional[str] = None
    nb_colis: Optional[int] = None
    poids_total_kg: Optional[int] = None
    montant_facture_xaf: Optional[int] = None
    date_emission: Optional[date] = None
    date_livraison_prevue: Optional[date] = None
    date_livraison_reelle: Optional[date] = None
    statut: Optional[str] = None
    is_active: Optional[bool] = None


class CourierWaybillOut(BaseModel):
    id: int
    company_id: int
    numero_lse: str
    type_service: Optional[str] = None
    client: Optional[str] = None
    nb_colis: Optional[int] = None
    poids_total_kg: Optional[int] = None
    montant_facture_xaf: Optional[int] = None
    date_emission: Optional[date] = None
    date_livraison_prevue: Optional[date] = None
    date_livraison_reelle: Optional[date] = None
    statut: Optional[str] = None
    is_active: Optional[bool] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    model_config = {"from_attributes": True}


class CourierHubCreate(BaseModel):
    code_hub: str
    nom: Optional[str] = None
    ville: Optional[str] = None
    pays: Optional[str] = None
    capacite: Optional[str] = None
    nb_tri_jour: Optional[int] = None
    surface_m2: Optional[int] = None
    statut: Optional[str] = None


class CourierHubUpdate(BaseModel):
    code_hub: Optional[str] = None
    nom: Optional[str] = None
    ville: Optional[str] = None
    pays: Optional[str] = None
    capacite: Optional[str] = None
    nb_tri_jour: Optional[int] = None
    surface_m2: Optional[int] = None
    statut: Optional[str] = None
    is_active: Optional[bool] = None


class CourierHubOut(BaseModel):
    id: int
    company_id: int
    code_hub: str
    nom: Optional[str] = None
    ville: Optional[str] = None
    pays: Optional[str] = None
    capacite: Optional[str] = None
    nb_tri_jour: Optional[int] = None
    surface_m2: Optional[int] = None
    statut: Optional[str] = None
    is_active: Optional[bool] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    model_config = {"from_attributes": True}


class CourierDeliveryZoneCreate(BaseModel):
    code_zone: str
    nom: Optional[str] = None
    type_zone: Optional[str] = None
    ville: Optional[str] = None
    nb_habitants: Optional[int] = None
    nb_colis_jour: Optional[int] = None
    hub_rattachement: Optional[str] = None
    surcost_xaf: Optional[int] = None


class CourierDeliveryZoneUpdate(BaseModel):
    code_zone: Optional[str] = None
    nom: Optional[str] = None
    type_zone: Optional[str] = None
    ville: Optional[str] = None
    nb_habitants: Optional[int] = None
    nb_colis_jour: Optional[int] = None
    hub_rattachement: Optional[str] = None
    surcost_xaf: Optional[int] = None
    is_active: Optional[bool] = None


class CourierDeliveryZoneOut(BaseModel):
    id: int
    company_id: int
    code_zone: str
    nom: Optional[str] = None
    type_zone: Optional[str] = None
    ville: Optional[str] = None
    nb_habitants: Optional[int] = None
    nb_colis_jour: Optional[int] = None
    hub_rattachement: Optional[str] = None
    surcost_xaf: Optional[int] = None
    is_active: Optional[bool] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    model_config = {"from_attributes": True}


class CourierRouteCreate(BaseModel):
    code_tournee: str
    type_route: Optional[str] = None
    zone_associee: Optional[str] = None
    chauffeur: Optional[str] = None
    vehicule: Optional[str] = None
    date_tournee: Optional[date] = None
    nb_arrets: Optional[int] = None
    distance_km: Optional[int] = None
    duree_h: Optional[int] = None
    statut: Optional[str] = None


class CourierRouteUpdate(BaseModel):
    code_tournee: Optional[str] = None
    type_route: Optional[str] = None
    zone_associee: Optional[str] = None
    chauffeur: Optional[str] = None
    vehicule: Optional[str] = None
    date_tournee: Optional[date] = None
    nb_arrets: Optional[int] = None
    distance_km: Optional[int] = None
    duree_h: Optional[int] = None
    statut: Optional[str] = None
    is_active: Optional[bool] = None


class CourierRouteOut(BaseModel):
    id: int
    company_id: int
    code_tournee: str
    type_route: Optional[str] = None
    zone_associee: Optional[str] = None
    chauffeur: Optional[str] = None
    vehicule: Optional[str] = None
    date_tournee: Optional[date] = None
    nb_arrets: Optional[int] = None
    distance_km: Optional[int] = None
    duree_h: Optional[int] = None
    statut: Optional[str] = None
    is_active: Optional[bool] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    model_config = {"from_attributes": True}


class CourierCourierCreate(BaseModel):
    code_coursier: str
    nom: Optional[str] = None
    telephone: Optional[str] = None
    email: Optional[str] = None
    type_contrat: Optional[str] = None
    permis_conduire: Optional[str] = None
    date_embauche: Optional[date] = None
    nb_livraisons_jour: Optional[int] = None
    taux_ponctualite_pct: Optional[int] = None
    disponibilite: Optional[str] = None


class CourierCourierUpdate(BaseModel):
    code_coursier: Optional[str] = None
    nom: Optional[str] = None
    telephone: Optional[str] = None
    email: Optional[str] = None
    type_contrat: Optional[str] = None
    permis_conduire: Optional[str] = None
    date_embauche: Optional[date] = None
    nb_livraisons_jour: Optional[int] = None
    taux_ponctualite_pct: Optional[int] = None
    disponibilite: Optional[str] = None
    is_active: Optional[bool] = None


class CourierCourierOut(BaseModel):
    id: int
    company_id: int
    code_coursier: str
    nom: Optional[str] = None
    telephone: Optional[str] = None
    email: Optional[str] = None
    type_contrat: Optional[str] = None
    permis_conduire: Optional[str] = None
    date_embauche: Optional[date] = None
    nb_livraisons_jour: Optional[int] = None
    taux_ponctualite_pct: Optional[int] = None
    disponibilite: Optional[str] = None
    is_active: Optional[bool] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    model_config = {"from_attributes": True}


class CourierPodCreate(BaseModel):
    reference_pod: str
    numero_colis: Optional[str] = None
    date_livraison: Optional[datetime] = None
    destination_finale: Optional[str] = None
    agent_livreur: Optional[str] = None
    resultat: Optional[str] = None
    signature_recu: Optional[bool] = None
    photo_url: Optional[str] = None
    geo_lat: Optional[str] = None
    geo_lon: Optional[str] = None


class CourierPodUpdate(BaseModel):
    reference_pod: Optional[str] = None
    numero_colis: Optional[str] = None
    date_livraison: Optional[datetime] = None
    destination_finale: Optional[str] = None
    agent_livreur: Optional[str] = None
    resultat: Optional[str] = None
    signature_recu: Optional[bool] = None
    photo_url: Optional[str] = None
    geo_lat: Optional[str] = None
    geo_lon: Optional[str] = None
    is_active: Optional[bool] = None


class CourierPodOut(BaseModel):
    id: int
    company_id: int
    reference_pod: str
    numero_colis: Optional[str] = None
    date_livraison: Optional[datetime] = None
    destination_finale: Optional[str] = None
    agent_livreur: Optional[str] = None
    resultat: Optional[str] = None
    signature_recu: Optional[bool] = None
    photo_url: Optional[str] = None
    geo_lat: Optional[str] = None
    geo_lon: Optional[str] = None
    is_active: Optional[bool] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    model_config = {"from_attributes": True}


class CourierSlaCreate(BaseModel):
    code_sla: str
    client: Optional[str] = None
    categorie: Optional[str] = None
    engagement_pct: Optional[int] = None
    delai_h: Optional[int] = None
    penalite_xaf: Optional[int] = None
    mesure_pct: Optional[int] = None
    date_debut: Optional[date] = None
    date_fin: Optional[date] = None
    statut: Optional[str] = None


class CourierSlaUpdate(BaseModel):
    code_sla: Optional[str] = None
    client: Optional[str] = None
    categorie: Optional[str] = None
    engagement_pct: Optional[int] = None
    delai_h: Optional[int] = None
    penalite_xaf: Optional[int] = None
    mesure_pct: Optional[int] = None
    date_debut: Optional[date] = None
    date_fin: Optional[date] = None
    statut: Optional[str] = None
    is_active: Optional[bool] = None


class CourierSlaOut(BaseModel):
    id: int
    company_id: int
    code_sla: str
    client: Optional[str] = None
    categorie: Optional[str] = None
    engagement_pct: Optional[int] = None
    delai_h: Optional[int] = None
    penalite_xaf: Optional[int] = None
    mesure_pct: Optional[int] = None
    date_debut: Optional[date] = None
    date_fin: Optional[date] = None
    statut: Optional[str] = None
    is_active: Optional[bool] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    model_config = {"from_attributes": True}


class CourierLockerCreate(BaseModel):
    code_locker: str
    adresse: Optional[str] = None
    ville: Optional[str] = None
    nb_cases: Optional[int] = None
    nb_cases_libres: Optional[int] = None
    type_acces: Optional[str] = None
    horaires_ouverture: Optional[str] = None
    statut: Optional[str] = None


class CourierLockerUpdate(BaseModel):
    code_locker: Optional[str] = None
    adresse: Optional[str] = None
    ville: Optional[str] = None
    nb_cases: Optional[int] = None
    nb_cases_libres: Optional[int] = None
    type_acces: Optional[str] = None
    horaires_ouverture: Optional[str] = None
    statut: Optional[str] = None
    is_active: Optional[bool] = None


class CourierLockerOut(BaseModel):
    id: int
    company_id: int
    code_locker: str
    adresse: Optional[str] = None
    ville: Optional[str] = None
    nb_cases: Optional[int] = None
    nb_cases_libres: Optional[int] = None
    type_acces: Optional[str] = None
    horaires_ouverture: Optional[str] = None
    statut: Optional[str] = None
    is_active: Optional[bool] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    model_config = {"from_attributes": True}


class CourierVehiculeCreate(BaseModel):
    plaque: str
    type_vehicule: Optional[str] = None
    marque: Optional[str] = None
    modele: Optional[str] = None
    capacite_m3: Optional[int] = None
    date_mise_circulation: Optional[date] = None
    kilometrage_actuel: Optional[int] = None
    prochaine_revision_km: Optional[int] = None
    statut: Optional[str] = None


class CourierVehiculeUpdate(BaseModel):
    plaque: Optional[str] = None
    type_vehicule: Optional[str] = None
    marque: Optional[str] = None
    modele: Optional[str] = None
    capacite_m3: Optional[int] = None
    date_mise_circulation: Optional[date] = None
    kilometrage_actuel: Optional[int] = None
    prochaine_revision_km: Optional[int] = None
    statut: Optional[str] = None
    is_active: Optional[bool] = None


class CourierVehiculeOut(BaseModel):
    id: int
    company_id: int
    plaque: str
    type_vehicule: Optional[str] = None
    marque: Optional[str] = None
    modele: Optional[str] = None
    capacite_m3: Optional[int] = None
    date_mise_circulation: Optional[date] = None
    kilometrage_actuel: Optional[int] = None
    prochaine_revision_km: Optional[int] = None
    statut: Optional[str] = None
    is_active: Optional[bool] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    model_config = {"from_attributes": True}


class CourierTarifCreate(BaseModel):
    code_tarif: str
    zone_tarifaire: Optional[str] = None
    tranche_poids_kg: Optional[str] = None
    prix_base_xaf: Optional[int] = None
    prix_par_kg_supp_xaf: Optional[int] = None
    options_payantes: Optional[str] = None
    date_debut_validite: Optional[date] = None
    date_fin_validite: Optional[date] = None
    statut: Optional[str] = None


class CourierTarifUpdate(BaseModel):
    code_tarif: Optional[str] = None
    zone_tarifaire: Optional[str] = None
    tranche_poids_kg: Optional[str] = None
    prix_base_xaf: Optional[int] = None
    prix_par_kg_supp_xaf: Optional[int] = None
    options_payantes: Optional[str] = None
    date_debut_validite: Optional[date] = None
    date_fin_validite: Optional[date] = None
    statut: Optional[str] = None
    is_active: Optional[bool] = None


class CourierTarifOut(BaseModel):
    id: int
    company_id: int
    code_tarif: str
    zone_tarifaire: Optional[str] = None
    tranche_poids_kg: Optional[str] = None
    prix_base_xaf: Optional[int] = None
    prix_par_kg_supp_xaf: Optional[int] = None
    options_payantes: Optional[str] = None
    date_debut_validite: Optional[date] = None
    date_fin_validite: Optional[date] = None
    statut: Optional[str] = None
    is_active: Optional[bool] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    model_config = {"from_attributes": True}


class CourierExceptionCreate(BaseModel):
    reference: str
    numero_colis: Optional[str] = None
    type_exception: Optional[str] = None
    date_signalement: Optional[datetime] = None
    description: Optional[str] = None
    montant_litige_xaf: Optional[int] = None
    agent: Optional[str] = None
    date_resolution: Optional[datetime] = None
    statut: Optional[str] = None


class CourierExceptionUpdate(BaseModel):
    reference: Optional[str] = None
    numero_colis: Optional[str] = None
    type_exception: Optional[str] = None
    date_signalement: Optional[datetime] = None
    description: Optional[str] = None
    montant_litige_xaf: Optional[int] = None
    agent: Optional[str] = None
    date_resolution: Optional[datetime] = None
    statut: Optional[str] = None
    is_active: Optional[bool] = None


class CourierExceptionOut(BaseModel):
    id: int
    company_id: int
    reference: str
    numero_colis: Optional[str] = None
    type_exception: Optional[str] = None
    date_signalement: Optional[datetime] = None
    description: Optional[str] = None
    montant_litige_xaf: Optional[int] = None
    agent: Optional[str] = None
    date_resolution: Optional[datetime] = None
    statut: Optional[str] = None
    is_active: Optional[bool] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    model_config = {"from_attributes": True}

