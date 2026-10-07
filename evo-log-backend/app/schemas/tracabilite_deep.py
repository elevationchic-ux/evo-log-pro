"""Schemas Pydantic auto-genere (expansion wave 6)."""
from pydantic import BaseModel
from typing import Optional
from datetime import datetime, date


class TraceabilityEventCreate(BaseModel):
    event_uid: str
    event_type: str
    module_source: Optional[str] = None
    asset_type: Optional[str] = None
    asset_id: Optional[str] = None
    subject_ref: Optional[str] = None
    action: Optional[str] = None
    payload_json: Optional[str] = None
    actor_id: Optional[int] = None
    actor_ip: Optional[str] = None
    actor_user_agent: Optional[str] = None
    actor_role: Optional[str] = None
    correlation_id: Optional[str] = None
    gps_lat: Optional[float] = None
    gps_lng: Optional[float] = None
    timestamp_server: datetime
    timestamp_client: Optional[datetime] = None
    hash_self: Optional[str] = None
    hash_prev: Optional[str] = None
    signature_id: Optional[int] = None
    est_validite: Optional[bool] = None
    notes: Optional[str] = None


class TraceabilityEventUpdate(BaseModel):
    event_uid: Optional[str] = None
    event_type: Optional[str] = None
    module_source: Optional[str] = None
    asset_type: Optional[str] = None
    asset_id: Optional[str] = None
    subject_ref: Optional[str] = None
    action: Optional[str] = None
    payload_json: Optional[str] = None
    actor_id: Optional[int] = None
    actor_ip: Optional[str] = None
    actor_user_agent: Optional[str] = None
    actor_role: Optional[str] = None
    correlation_id: Optional[str] = None
    gps_lat: Optional[float] = None
    gps_lng: Optional[float] = None
    timestamp_server: Optional[datetime] = None
    timestamp_client: Optional[datetime] = None
    hash_self: Optional[str] = None
    hash_prev: Optional[str] = None
    signature_id: Optional[int] = None
    est_validite: Optional[bool] = None
    notes: Optional[str] = None
    is_active: Optional[bool] = None


class TraceabilityEventOut(BaseModel):
    id: int
    company_id: int
    event_uid: str
    event_type: str
    module_source: Optional[str] = None
    asset_type: Optional[str] = None
    asset_id: Optional[str] = None
    subject_ref: Optional[str] = None
    action: Optional[str] = None
    payload_json: Optional[str] = None
    actor_id: Optional[int] = None
    actor_ip: Optional[str] = None
    actor_user_agent: Optional[str] = None
    actor_role: Optional[str] = None
    correlation_id: Optional[str] = None
    gps_lat: Optional[float] = None
    gps_lng: Optional[float] = None
    timestamp_server: datetime
    timestamp_client: Optional[datetime] = None
    hash_self: Optional[str] = None
    hash_prev: Optional[str] = None
    signature_id: Optional[int] = None
    est_validite: Optional[bool] = None
    notes: Optional[str] = None
    is_active: Optional[bool] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    model_config = {"from_attributes": True}


class ChainOfCustodyTransferCreate(BaseModel):
    reference_transfert: str
    asset_type: str
    asset_ref: str
    lot_ref: Optional[str] = None
    source_party: Optional[str] = None
    source_contact: Optional[str] = None
    target_party: Optional[str] = None
    target_contact: Optional[str] = None
    type_transfert: Optional[str] = None
    date_transfert: datetime
    lieu: Optional[str] = None
    gps_lat: Optional[float] = None
    gps_lng: Optional[float] = None
    quantite_transferee: Optional[float] = None
    unite: Optional[str] = None
    poids_kg: Optional[float] = None
    etat_reception: Optional[str] = None
    anomalies: Optional[str] = None
    photos_url: Optional[str] = None
    signature_source_url: Optional[str] = None
    signature_target_url: Optional[str] = None
    hash_transfert: Optional[str] = None
    statut: Optional[str] = None


class ChainOfCustodyTransferUpdate(BaseModel):
    reference_transfert: Optional[str] = None
    asset_type: Optional[str] = None
    asset_ref: Optional[str] = None
    lot_ref: Optional[str] = None
    source_party: Optional[str] = None
    source_contact: Optional[str] = None
    target_party: Optional[str] = None
    target_contact: Optional[str] = None
    type_transfert: Optional[str] = None
    date_transfert: Optional[datetime] = None
    lieu: Optional[str] = None
    gps_lat: Optional[float] = None
    gps_lng: Optional[float] = None
    quantite_transferee: Optional[float] = None
    unite: Optional[str] = None
    poids_kg: Optional[float] = None
    etat_reception: Optional[str] = None
    anomalies: Optional[str] = None
    photos_url: Optional[str] = None
    signature_source_url: Optional[str] = None
    signature_target_url: Optional[str] = None
    hash_transfert: Optional[str] = None
    statut: Optional[str] = None
    is_active: Optional[bool] = None


class ChainOfCustodyTransferOut(BaseModel):
    id: int
    company_id: int
    reference_transfert: str
    asset_type: str
    asset_ref: str
    lot_ref: Optional[str] = None
    source_party: Optional[str] = None
    source_contact: Optional[str] = None
    target_party: Optional[str] = None
    target_contact: Optional[str] = None
    type_transfert: Optional[str] = None
    date_transfert: datetime
    lieu: Optional[str] = None
    gps_lat: Optional[float] = None
    gps_lng: Optional[float] = None
    quantite_transferee: Optional[float] = None
    unite: Optional[str] = None
    poids_kg: Optional[float] = None
    etat_reception: Optional[str] = None
    anomalies: Optional[str] = None
    photos_url: Optional[str] = None
    signature_source_url: Optional[str] = None
    signature_target_url: Optional[str] = None
    hash_transfert: Optional[str] = None
    statut: Optional[str] = None
    is_active: Optional[bool] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    model_config = {"from_attributes": True}


class BatchGenealogyCreate(BaseModel):
    child_lot: str
    child_type: Optional[str] = None
    parent_lot: str
    parent_type: Optional[str] = None
    proportion: Optional[float] = None
    quantite_mise_en_oeuvre: Optional[float] = None
    unite: Optional[str] = None
    date_integration: Optional[datetime] = None
    operation: Optional[str] = None
    operateur: Optional[str] = None
    atelier: Optional[str] = None
    certificate_url: Optional[str] = None
    hash_certificat: Optional[str] = None
    notes: Optional[str] = None


class BatchGenealogyUpdate(BaseModel):
    child_lot: Optional[str] = None
    child_type: Optional[str] = None
    parent_lot: Optional[str] = None
    parent_type: Optional[str] = None
    proportion: Optional[float] = None
    quantite_mise_en_oeuvre: Optional[float] = None
    unite: Optional[str] = None
    date_integration: Optional[datetime] = None
    operation: Optional[str] = None
    operateur: Optional[str] = None
    atelier: Optional[str] = None
    certificate_url: Optional[str] = None
    hash_certificat: Optional[str] = None
    notes: Optional[str] = None
    is_active: Optional[bool] = None


class BatchGenealogyOut(BaseModel):
    id: int
    company_id: int
    child_lot: str
    child_type: Optional[str] = None
    parent_lot: str
    parent_type: Optional[str] = None
    proportion: Optional[float] = None
    quantite_mise_en_oeuvre: Optional[float] = None
    unite: Optional[str] = None
    date_integration: Optional[datetime] = None
    operation: Optional[str] = None
    operateur: Optional[str] = None
    atelier: Optional[str] = None
    certificate_url: Optional[str] = None
    hash_certificat: Optional[str] = None
    notes: Optional[str] = None
    is_active: Optional[bool] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    model_config = {"from_attributes": True}


class SerialGenealogyCreate(BaseModel):
    child_serial: str
    parent_serial: str
    relation_type: Optional[str] = None
    date_integration: Optional[datetime] = None
    lieu_integration: Optional[str] = None
    operateur_id: Optional[int] = None
    ordre_assemblage: Optional[int] = None
    notes: Optional[str] = None


class SerialGenealogyUpdate(BaseModel):
    child_serial: Optional[str] = None
    parent_serial: Optional[str] = None
    relation_type: Optional[str] = None
    date_integration: Optional[datetime] = None
    lieu_integration: Optional[str] = None
    operateur_id: Optional[int] = None
    ordre_assemblage: Optional[int] = None
    notes: Optional[str] = None
    is_active: Optional[bool] = None


class SerialGenealogyOut(BaseModel):
    id: int
    company_id: int
    child_serial: str
    parent_serial: str
    relation_type: Optional[str] = None
    date_integration: Optional[datetime] = None
    lieu_integration: Optional[str] = None
    operateur_id: Optional[int] = None
    ordre_assemblage: Optional[int] = None
    notes: Optional[str] = None
    is_active: Optional[bool] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    model_config = {"from_attributes": True}


class DocumentHashCreate(BaseModel):
    document_ref: str
    document_type: Optional[str] = None
    version: int
    url: Optional[str] = None
    mime: Optional[str] = None
    taille_octets: Optional[int] = None
    hash_algo: Optional[str] = None
    hash_hex: Optional[str] = None
    merkle_root: Optional[str] = None
    signature_url: Optional[str] = None
    signer_id: Optional[int] = None
    date_emission: Optional[datetime] = None
    date_signature: Optional[datetime] = None
    date_archivage: Optional[date] = None
    duree_conservation_ans: Optional[int] = None
    statut: Optional[str] = None
    notes: Optional[str] = None


class DocumentHashUpdate(BaseModel):
    document_ref: Optional[str] = None
    document_type: Optional[str] = None
    version: Optional[int] = None
    url: Optional[str] = None
    mime: Optional[str] = None
    taille_octets: Optional[int] = None
    hash_algo: Optional[str] = None
    hash_hex: Optional[str] = None
    merkle_root: Optional[str] = None
    signature_url: Optional[str] = None
    signer_id: Optional[int] = None
    date_emission: Optional[datetime] = None
    date_signature: Optional[datetime] = None
    date_archivage: Optional[date] = None
    duree_conservation_ans: Optional[int] = None
    statut: Optional[str] = None
    notes: Optional[str] = None
    is_active: Optional[bool] = None


class DocumentHashOut(BaseModel):
    id: int
    company_id: int
    document_ref: str
    document_type: Optional[str] = None
    version: int
    url: Optional[str] = None
    mime: Optional[str] = None
    taille_octets: Optional[int] = None
    hash_algo: Optional[str] = None
    hash_hex: Optional[str] = None
    merkle_root: Optional[str] = None
    signature_url: Optional[str] = None
    signer_id: Optional[int] = None
    date_emission: Optional[datetime] = None
    date_signature: Optional[datetime] = None
    date_archivage: Optional[date] = None
    duree_conservation_ans: Optional[int] = None
    statut: Optional[str] = None
    notes: Optional[str] = None
    is_active: Optional[bool] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    model_config = {"from_attributes": True}


class GeolocationTraceCreate(BaseModel):
    subject_type: str
    subject_ref: str
    date_position: datetime
    gps_lat: float
    gps_lng: float
    altitude_m: Optional[float] = None
    vitesse_kmh: Optional[float] = None
    cap_deg: Optional[float] = None
    precision_m: Optional[float] = None
    source: Optional[str] = None
    device_id: Optional[str] = None
    geofence_id: Optional[int] = None
    franchissement: Optional[str] = None
    notes: Optional[str] = None


class GeolocationTraceUpdate(BaseModel):
    subject_type: Optional[str] = None
    subject_ref: Optional[str] = None
    date_position: Optional[datetime] = None
    gps_lat: Optional[float] = None
    gps_lng: Optional[float] = None
    altitude_m: Optional[float] = None
    vitesse_kmh: Optional[float] = None
    cap_deg: Optional[float] = None
    precision_m: Optional[float] = None
    source: Optional[str] = None
    device_id: Optional[str] = None
    geofence_id: Optional[int] = None
    franchissement: Optional[str] = None
    notes: Optional[str] = None
    is_active: Optional[bool] = None


class GeolocationTraceOut(BaseModel):
    id: int
    company_id: int
    subject_type: str
    subject_ref: str
    date_position: datetime
    gps_lat: float
    gps_lng: float
    altitude_m: Optional[float] = None
    vitesse_kmh: Optional[float] = None
    cap_deg: Optional[float] = None
    precision_m: Optional[float] = None
    source: Optional[str] = None
    device_id: Optional[str] = None
    geofence_id: Optional[int] = None
    franchissement: Optional[str] = None
    notes: Optional[str] = None
    is_active: Optional[bool] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    model_config = {"from_attributes": True}


class ColdChainTraceCreate(BaseModel):
    subject_type: str
    subject_ref: str
    logger_id: Optional[str] = None
    date_lecture: datetime
    temperature_c: Optional[float] = None
    humidite_pct: Optional[float] = None
    co2_ppm: Optional[int] = None
    o2_pct: Optional[float] = None
    pression_bar: Optional[float] = None
    seuil_min_c: Optional[float] = None
    seuil_max_c: Optional[float] = None
    excursion: Optional[bool] = None
    porte_ouverte: Optional[bool] = None
    duree_porte_ouverte_s: Optional[int] = None
    device_battery_pct: Optional[float] = None
    notes: Optional[str] = None


class ColdChainTraceUpdate(BaseModel):
    subject_type: Optional[str] = None
    subject_ref: Optional[str] = None
    logger_id: Optional[str] = None
    date_lecture: Optional[datetime] = None
    temperature_c: Optional[float] = None
    humidite_pct: Optional[float] = None
    co2_ppm: Optional[int] = None
    o2_pct: Optional[float] = None
    pression_bar: Optional[float] = None
    seuil_min_c: Optional[float] = None
    seuil_max_c: Optional[float] = None
    excursion: Optional[bool] = None
    porte_ouverte: Optional[bool] = None
    duree_porte_ouverte_s: Optional[int] = None
    device_battery_pct: Optional[float] = None
    notes: Optional[str] = None
    is_active: Optional[bool] = None


class ColdChainTraceOut(BaseModel):
    id: int
    company_id: int
    subject_type: str
    subject_ref: str
    logger_id: Optional[str] = None
    date_lecture: datetime
    temperature_c: Optional[float] = None
    humidite_pct: Optional[float] = None
    co2_ppm: Optional[int] = None
    o2_pct: Optional[float] = None
    pression_bar: Optional[float] = None
    seuil_min_c: Optional[float] = None
    seuil_max_c: Optional[float] = None
    excursion: Optional[bool] = None
    porte_ouverte: Optional[bool] = None
    duree_porte_ouverte_s: Optional[int] = None
    device_battery_pct: Optional[float] = None
    notes: Optional[str] = None
    is_active: Optional[bool] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    model_config = {"from_attributes": True}


class IncidentChainOfCommandCreate(BaseModel):
    reference_incident: str
    type_incident: str
    date_debut: datetime
    date_fin: Optional[datetime] = None
    severite: Optional[str] = None
    description: Optional[str] = None
    lieu: Optional[str] = None
    gps_lat: Optional[float] = None
    gps_lng: Optional[float] = None
    chef_secours: Optional[str] = None
    autorite_alertee: Optional[str] = None
    decisions_prises: Optional[str] = None
    ressources_engagees: Optional[str] = None
    victimes: Optional[int] = None
    dommages_materials_xaf: Optional[float] = None
    arret_activite: Optional[bool] = None
    communication_presse: Optional[bool] = None
    rapport_final_url: Optional[str] = None
    statut: Optional[str] = None


class IncidentChainOfCommandUpdate(BaseModel):
    reference_incident: Optional[str] = None
    type_incident: Optional[str] = None
    date_debut: Optional[datetime] = None
    date_fin: Optional[datetime] = None
    severite: Optional[str] = None
    description: Optional[str] = None
    lieu: Optional[str] = None
    gps_lat: Optional[float] = None
    gps_lng: Optional[float] = None
    chef_secours: Optional[str] = None
    autorite_alertee: Optional[str] = None
    decisions_prises: Optional[str] = None
    ressources_engagees: Optional[str] = None
    victimes: Optional[int] = None
    dommages_materials_xaf: Optional[float] = None
    arret_activite: Optional[bool] = None
    communication_presse: Optional[bool] = None
    rapport_final_url: Optional[str] = None
    statut: Optional[str] = None
    is_active: Optional[bool] = None


class IncidentChainOfCommandOut(BaseModel):
    id: int
    company_id: int
    reference_incident: str
    type_incident: str
    date_debut: datetime
    date_fin: Optional[datetime] = None
    severite: Optional[str] = None
    description: Optional[str] = None
    lieu: Optional[str] = None
    gps_lat: Optional[float] = None
    gps_lng: Optional[float] = None
    chef_secours: Optional[str] = None
    autorite_alertee: Optional[str] = None
    decisions_prises: Optional[str] = None
    ressources_engagees: Optional[str] = None
    victimes: Optional[int] = None
    dommages_materials_xaf: Optional[float] = None
    arret_activite: Optional[bool] = None
    communication_presse: Optional[bool] = None
    rapport_final_url: Optional[str] = None
    statut: Optional[str] = None
    is_active: Optional[bool] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    model_config = {"from_attributes": True}


class RegulatoryTraceExportCreate(BaseModel):
    numero_expedition: str
    autorite_destinataire: str
    type_declaration: Optional[str] = None
    periode_reference: Optional[str] = None
    date_depot: Optional[datetime] = None
    canaux: Optional[str] = None
    nb_lignes: Optional[int] = None
    montant_declare_xaf: Optional[float] = None
    fichier_url: Optional[str] = None
    fichier_hash: Optional[str] = None
    numero_recu: Optional[str] = None
    date_recu: Optional[datetime] = None
    statut: Optional[str] = None
    reponse_autorite: Optional[str] = None
    anomalies: Optional[str] = None
    user_id: Optional[int] = None


class RegulatoryTraceExportUpdate(BaseModel):
    numero_expedition: Optional[str] = None
    autorite_destinataire: Optional[str] = None
    type_declaration: Optional[str] = None
    periode_reference: Optional[str] = None
    date_depot: Optional[datetime] = None
    canaux: Optional[str] = None
    nb_lignes: Optional[int] = None
    montant_declare_xaf: Optional[float] = None
    fichier_url: Optional[str] = None
    fichier_hash: Optional[str] = None
    numero_recu: Optional[str] = None
    date_recu: Optional[datetime] = None
    statut: Optional[str] = None
    reponse_autorite: Optional[str] = None
    anomalies: Optional[str] = None
    user_id: Optional[int] = None
    is_active: Optional[bool] = None


class RegulatoryTraceExportOut(BaseModel):
    id: int
    company_id: int
    numero_expedition: str
    autorite_destinataire: str
    type_declaration: Optional[str] = None
    periode_reference: Optional[str] = None
    date_depot: Optional[datetime] = None
    canaux: Optional[str] = None
    nb_lignes: Optional[int] = None
    montant_declare_xaf: Optional[float] = None
    fichier_url: Optional[str] = None
    fichier_hash: Optional[str] = None
    numero_recu: Optional[str] = None
    date_recu: Optional[datetime] = None
    statut: Optional[str] = None
    reponse_autorite: Optional[str] = None
    anomalies: Optional[str] = None
    user_id: Optional[int] = None
    is_active: Optional[bool] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    model_config = {"from_attributes": True}


class ImmutableAuditLogCreate(BaseModel):
    event_uid: Optional[str] = None
    actor_id: Optional[int] = None
    actor_email: Optional[str] = None
    actor_ip: Optional[str] = None
    user_agent: Optional[str] = None
    action: Optional[str] = None
    resource_type: Optional[str] = None
    resource_id: Optional[str] = None
    before_snapshot: Optional[str] = None
    after_snapshot: Optional[str] = None
    raison_metier: Optional[str] = None
    timestamp_server: datetime
    hash_self: Optional[str] = None
    hash_prev: Optional[str] = None
    merkle_root: Optional[str] = None
    validite: Optional[bool] = None
    session_id: Optional[str] = None


class ImmutableAuditLogUpdate(BaseModel):
    event_uid: Optional[str] = None
    actor_id: Optional[int] = None
    actor_email: Optional[str] = None
    actor_ip: Optional[str] = None
    user_agent: Optional[str] = None
    action: Optional[str] = None
    resource_type: Optional[str] = None
    resource_id: Optional[str] = None
    before_snapshot: Optional[str] = None
    after_snapshot: Optional[str] = None
    raison_metier: Optional[str] = None
    timestamp_server: Optional[datetime] = None
    hash_self: Optional[str] = None
    hash_prev: Optional[str] = None
    merkle_root: Optional[str] = None
    validite: Optional[bool] = None
    session_id: Optional[str] = None
    is_active: Optional[bool] = None


class ImmutableAuditLogOut(BaseModel):
    id: int
    company_id: int
    event_uid: Optional[str] = None
    actor_id: Optional[int] = None
    actor_email: Optional[str] = None
    actor_ip: Optional[str] = None
    user_agent: Optional[str] = None
    action: Optional[str] = None
    resource_type: Optional[str] = None
    resource_id: Optional[str] = None
    before_snapshot: Optional[str] = None
    after_snapshot: Optional[str] = None
    raison_metier: Optional[str] = None
    timestamp_server: datetime
    hash_self: Optional[str] = None
    hash_prev: Optional[str] = None
    merkle_root: Optional[str] = None
    validite: Optional[bool] = None
    session_id: Optional[str] = None
    is_active: Optional[bool] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    model_config = {"from_attributes": True}


class TimestampAuthorityCreate(BaseModel):
    token_tsa: str
    autorite_certification: Optional[str] = None
    algorithme_signature: Optional[str] = None
    objet_type: Optional[str] = None
    objet_ref: Optional[str] = None
    objet_hash: Optional[str] = None
    date_horodatage: datetime
    precision_seconde: Optional[int] = None
    certificate_serial: Optional[str] = None
    certificate_issuer: Optional[str] = None
    certificate_valide_jusqu: Optional[date] = None
    token_blob: Optional[str] = None
    statut: Optional[str] = None


class TimestampAuthorityUpdate(BaseModel):
    token_tsa: Optional[str] = None
    autorite_certification: Optional[str] = None
    algorithme_signature: Optional[str] = None
    objet_type: Optional[str] = None
    objet_ref: Optional[str] = None
    objet_hash: Optional[str] = None
    date_horodatage: Optional[datetime] = None
    precision_seconde: Optional[int] = None
    certificate_serial: Optional[str] = None
    certificate_issuer: Optional[str] = None
    certificate_valide_jusqu: Optional[date] = None
    token_blob: Optional[str] = None
    statut: Optional[str] = None
    is_active: Optional[bool] = None


class TimestampAuthorityOut(BaseModel):
    id: int
    company_id: int
    token_tsa: str
    autorite_certification: Optional[str] = None
    algorithme_signature: Optional[str] = None
    objet_type: Optional[str] = None
    objet_ref: Optional[str] = None
    objet_hash: Optional[str] = None
    date_horodatage: datetime
    precision_seconde: Optional[int] = None
    certificate_serial: Optional[str] = None
    certificate_issuer: Optional[str] = None
    certificate_valide_jusqu: Optional[date] = None
    token_blob: Optional[str] = None
    statut: Optional[str] = None
    is_active: Optional[bool] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    model_config = {"from_attributes": True}


class WitnessSignatureCreate(BaseModel):
    reference_signature: str
    type_signataire: Optional[str] = None
    signataire_nom: Optional[str] = None
    signataire_qualite: Optional[str] = None
    signataire_email: Optional[str] = None
    signataire_telephone: Optional[str] = None
    piece_identite_ref: Optional[str] = None
    document_ref: Optional[str] = None
    event_uid: Optional[str] = None
    type_signature: Optional[str] = None
    signature_blob_url: Optional[str] = None
    hash_signature: Optional[str] = None
    date_signature: datetime
    gps_lat: Optional[float] = None
    gps_lng: Optional[float] = None
    ip_signature: Optional[str] = None
    tsa_id: Optional[int] = None
    statut: Optional[str] = None


class WitnessSignatureUpdate(BaseModel):
    reference_signature: Optional[str] = None
    type_signataire: Optional[str] = None
    signataire_nom: Optional[str] = None
    signataire_qualite: Optional[str] = None
    signataire_email: Optional[str] = None
    signataire_telephone: Optional[str] = None
    piece_identite_ref: Optional[str] = None
    document_ref: Optional[str] = None
    event_uid: Optional[str] = None
    type_signature: Optional[str] = None
    signature_blob_url: Optional[str] = None
    hash_signature: Optional[str] = None
    date_signature: Optional[datetime] = None
    gps_lat: Optional[float] = None
    gps_lng: Optional[float] = None
    ip_signature: Optional[str] = None
    tsa_id: Optional[int] = None
    statut: Optional[str] = None
    is_active: Optional[bool] = None


class WitnessSignatureOut(BaseModel):
    id: int
    company_id: int
    reference_signature: str
    type_signataire: Optional[str] = None
    signataire_nom: Optional[str] = None
    signataire_qualite: Optional[str] = None
    signataire_email: Optional[str] = None
    signataire_telephone: Optional[str] = None
    piece_identite_ref: Optional[str] = None
    document_ref: Optional[str] = None
    event_uid: Optional[str] = None
    type_signature: Optional[str] = None
    signature_blob_url: Optional[str] = None
    hash_signature: Optional[str] = None
    date_signature: datetime
    gps_lat: Optional[float] = None
    gps_lng: Optional[float] = None
    ip_signature: Optional[str] = None
    tsa_id: Optional[int] = None
    statut: Optional[str] = None
    is_active: Optional[bool] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    model_config = {"from_attributes": True}


class IntegrityMerkleProofCreate(BaseModel):
    racine_type: str
    periode: str
    nb_leaves: Optional[int] = None
    merkle_root: Optional[str] = None
    first_leaf_hash: Optional[str] = None
    last_leaf_hash: Optional[str] = None
    chemin_verification: Optional[str] = None
    date_publication: Optional[datetime] = None
    tsa_id: Optional[int] = None
    publication_externe: Optional[str] = None
    statut: Optional[str] = None
    notes: Optional[str] = None


class IntegrityMerkleProofUpdate(BaseModel):
    racine_type: Optional[str] = None
    periode: Optional[str] = None
    nb_leaves: Optional[int] = None
    merkle_root: Optional[str] = None
    first_leaf_hash: Optional[str] = None
    last_leaf_hash: Optional[str] = None
    chemin_verification: Optional[str] = None
    date_publication: Optional[datetime] = None
    tsa_id: Optional[int] = None
    publication_externe: Optional[str] = None
    statut: Optional[str] = None
    notes: Optional[str] = None
    is_active: Optional[bool] = None


class IntegrityMerkleProofOut(BaseModel):
    id: int
    company_id: int
    racine_type: str
    periode: str
    nb_leaves: Optional[int] = None
    merkle_root: Optional[str] = None
    first_leaf_hash: Optional[str] = None
    last_leaf_hash: Optional[str] = None
    chemin_verification: Optional[str] = None
    date_publication: Optional[datetime] = None
    tsa_id: Optional[int] = None
    publication_externe: Optional[str] = None
    statut: Optional[str] = None
    notes: Optional[str] = None
    is_active: Optional[bool] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    model_config = {"from_attributes": True}


class ContainerSealCreate(BaseModel):
    numero_sceau: str
    type_sceau: Optional[str] = None
    conteneur_numero: Optional[str] = None
    b_l_numero: Optional[str] = None
    date_apposition: Optional[datetime] = None
    lieu_apposition: Optional[str] = None
    operateur_apposition: Optional[str] = None
    signature_url: Optional[str] = None
    photo_url: Optional[str] = None
    date_retrait: Optional[datetime] = None
    lieu_retrait: Optional[str] = None
    operateur_retrait: Optional[str] = None
    numero_recolte: Optional[str] = None
    integrite_verifiee: Optional[bool] = None
    anomalie_sceau: Optional[str] = None
    autorite_alertee: Optional[str] = None
    statut: Optional[str] = None
    notes: Optional[str] = None


class ContainerSealUpdate(BaseModel):
    numero_sceau: Optional[str] = None
    type_sceau: Optional[str] = None
    conteneur_numero: Optional[str] = None
    b_l_numero: Optional[str] = None
    date_apposition: Optional[datetime] = None
    lieu_apposition: Optional[str] = None
    operateur_apposition: Optional[str] = None
    signature_url: Optional[str] = None
    photo_url: Optional[str] = None
    date_retrait: Optional[datetime] = None
    lieu_retrait: Optional[str] = None
    operateur_retrait: Optional[str] = None
    numero_recolte: Optional[str] = None
    integrite_verifiee: Optional[bool] = None
    anomalie_sceau: Optional[str] = None
    autorite_alertee: Optional[str] = None
    statut: Optional[str] = None
    notes: Optional[str] = None
    is_active: Optional[bool] = None


class ContainerSealOut(BaseModel):
    id: int
    company_id: int
    numero_sceau: str
    type_sceau: Optional[str] = None
    conteneur_numero: Optional[str] = None
    b_l_numero: Optional[str] = None
    date_apposition: Optional[datetime] = None
    lieu_apposition: Optional[str] = None
    operateur_apposition: Optional[str] = None
    signature_url: Optional[str] = None
    photo_url: Optional[str] = None
    date_retrait: Optional[datetime] = None
    lieu_retrait: Optional[str] = None
    operateur_retrait: Optional[str] = None
    numero_recolte: Optional[str] = None
    integrite_verifiee: Optional[bool] = None
    anomalie_sceau: Optional[str] = None
    autorite_alertee: Optional[str] = None
    statut: Optional[str] = None
    notes: Optional[str] = None
    is_active: Optional[bool] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    model_config = {"from_attributes": True}


class CargoHandoffCreate(BaseModel):
    reference_handoff: str
    type_cargo: Optional[str] = None
    cargo_ref: Optional[str] = None
    mode_precedent: Optional[str] = None
    mode_suivant: Optional[str] = None
    transporteur_precedent: Optional[str] = None
    transporteur_suivant: Optional[str] = None
    lieu_handoff: Optional[str] = None
    date_debut_prise_en_charge: Optional[datetime] = None
    date_fin_prise_en_charge: Optional[datetime] = None
    poids_kg: Optional[float] = None
    volume_m3: Optional[float] = None
    nb_colis: Optional[int] = None
    temperature_c: Optional[float] = None
    etat_entree: Optional[str] = None
    etat_sortie: Optional[str] = None
    anomalies_constatees: Optional[str] = None
    photos_url: Optional[str] = None
    signataire_entree: Optional[str] = None
    signataire_sortie: Optional[str] = None
    hash_handoff: Optional[str] = None
    statut: Optional[str] = None


class CargoHandoffUpdate(BaseModel):
    reference_handoff: Optional[str] = None
    type_cargo: Optional[str] = None
    cargo_ref: Optional[str] = None
    mode_precedent: Optional[str] = None
    mode_suivant: Optional[str] = None
    transporteur_precedent: Optional[str] = None
    transporteur_suivant: Optional[str] = None
    lieu_handoff: Optional[str] = None
    date_debut_prise_en_charge: Optional[datetime] = None
    date_fin_prise_en_charge: Optional[datetime] = None
    poids_kg: Optional[float] = None
    volume_m3: Optional[float] = None
    nb_colis: Optional[int] = None
    temperature_c: Optional[float] = None
    etat_entree: Optional[str] = None
    etat_sortie: Optional[str] = None
    anomalies_constatees: Optional[str] = None
    photos_url: Optional[str] = None
    signataire_entree: Optional[str] = None
    signataire_sortie: Optional[str] = None
    hash_handoff: Optional[str] = None
    statut: Optional[str] = None
    is_active: Optional[bool] = None


class CargoHandoffOut(BaseModel):
    id: int
    company_id: int
    reference_handoff: str
    type_cargo: Optional[str] = None
    cargo_ref: Optional[str] = None
    mode_precedent: Optional[str] = None
    mode_suivant: Optional[str] = None
    transporteur_precedent: Optional[str] = None
    transporteur_suivant: Optional[str] = None
    lieu_handoff: Optional[str] = None
    date_debut_prise_en_charge: Optional[datetime] = None
    date_fin_prise_en_charge: Optional[datetime] = None
    poids_kg: Optional[float] = None
    volume_m3: Optional[float] = None
    nb_colis: Optional[int] = None
    temperature_c: Optional[float] = None
    etat_entree: Optional[str] = None
    etat_sortie: Optional[str] = None
    anomalies_constatees: Optional[str] = None
    photos_url: Optional[str] = None
    signataire_entree: Optional[str] = None
    signataire_sortie: Optional[str] = None
    hash_handoff: Optional[str] = None
    statut: Optional[str] = None
    is_active: Optional[bool] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    model_config = {"from_attributes": True}


class AccessSecurityLogCreate(BaseModel):
    user_id: Optional[int] = None
    email_tente: Optional[str] = None
    type_evenement: str
    date_evenement: datetime
    ip_source: Optional[str] = None
    user_agent: Optional[str] = None
    geo_pays: Optional[str] = None
    geo_ville: Optional[str] = None
    session_id: Optional[str] = None
    device_fingerprint: Optional[str] = None
    nb_echecs_successifs: Optional[int] = None
    severite: Optional[str] = None
    action_remediation: Optional[str] = None
    meta_json: Optional[str] = None
    hash_self: Optional[str] = None
    hash_prev: Optional[str] = None


class AccessSecurityLogUpdate(BaseModel):
    user_id: Optional[int] = None
    email_tente: Optional[str] = None
    type_evenement: Optional[str] = None
    date_evenement: Optional[datetime] = None
    ip_source: Optional[str] = None
    user_agent: Optional[str] = None
    geo_pays: Optional[str] = None
    geo_ville: Optional[str] = None
    session_id: Optional[str] = None
    device_fingerprint: Optional[str] = None
    nb_echecs_successifs: Optional[int] = None
    severite: Optional[str] = None
    action_remediation: Optional[str] = None
    meta_json: Optional[str] = None
    hash_self: Optional[str] = None
    hash_prev: Optional[str] = None
    is_active: Optional[bool] = None


class AccessSecurityLogOut(BaseModel):
    id: int
    company_id: int
    user_id: Optional[int] = None
    email_tente: Optional[str] = None
    type_evenement: str
    date_evenement: datetime
    ip_source: Optional[str] = None
    user_agent: Optional[str] = None
    geo_pays: Optional[str] = None
    geo_ville: Optional[str] = None
    session_id: Optional[str] = None
    device_fingerprint: Optional[str] = None
    nb_echecs_successifs: Optional[int] = None
    severite: Optional[str] = None
    action_remediation: Optional[str] = None
    meta_json: Optional[str] = None
    hash_self: Optional[str] = None
    hash_prev: Optional[str] = None
    is_active: Optional[bool] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    model_config = {"from_attributes": True}


class ConsentGrantCreate(BaseModel):
    reference_consentement: str
    subject_type: Optional[str] = None
    subject_ref: Optional[str] = None
    finalite: Optional[str] = None
    categorie_donnees: Optional[str] = None
    duree_conservation_mois: Optional[int] = None
    tiers_partagables: Optional[str] = None
    date_consente: Optional[datetime] = None
    date_retiree: Optional[datetime] = None
    canal_recueil: Optional[str] = None
    ip_recueil: Optional[str] = None
    preuve_url: Optional[str] = None
    hash_preuve: Optional[str] = None
    statut: Optional[str] = None


class ConsentGrantUpdate(BaseModel):
    reference_consentement: Optional[str] = None
    subject_type: Optional[str] = None
    subject_ref: Optional[str] = None
    finalite: Optional[str] = None
    categorie_donnees: Optional[str] = None
    duree_conservation_mois: Optional[int] = None
    tiers_partagables: Optional[str] = None
    date_consente: Optional[datetime] = None
    date_retiree: Optional[datetime] = None
    canal_recueil: Optional[str] = None
    ip_recueil: Optional[str] = None
    preuve_url: Optional[str] = None
    hash_preuve: Optional[str] = None
    statut: Optional[str] = None
    is_active: Optional[bool] = None


class ConsentGrantOut(BaseModel):
    id: int
    company_id: int
    reference_consentement: str
    subject_type: Optional[str] = None
    subject_ref: Optional[str] = None
    finalite: Optional[str] = None
    categorie_donnees: Optional[str] = None
    duree_conservation_mois: Optional[int] = None
    tiers_partagables: Optional[str] = None
    date_consente: Optional[datetime] = None
    date_retiree: Optional[datetime] = None
    canal_recueil: Optional[str] = None
    ip_recueil: Optional[str] = None
    preuve_url: Optional[str] = None
    hash_preuve: Optional[str] = None
    statut: Optional[str] = None
    is_active: Optional[bool] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    model_config = {"from_attributes": True}


class AntiTamperingEventCreate(BaseModel):
    reference_alerte: str
    type_alerte: str
    date_detection: datetime
    severite: Optional[str] = None
    asset_type: Optional[str] = None
    asset_ref: Optional[str] = None
    attendu_hash: Optional[str] = None
    constate_hash: Optional[str] = None
    delta_description: Optional[str] = None
    detection_source: Optional[str] = None
    investigateur_id: Optional[int] = None
    actions_correctives: Optional[str] = None
    escalation_autorite: Optional[bool] = None
    statut: Optional[str] = None
    notes: Optional[str] = None


class AntiTamperingEventUpdate(BaseModel):
    reference_alerte: Optional[str] = None
    type_alerte: Optional[str] = None
    date_detection: Optional[datetime] = None
    severite: Optional[str] = None
    asset_type: Optional[str] = None
    asset_ref: Optional[str] = None
    attendu_hash: Optional[str] = None
    constate_hash: Optional[str] = None
    delta_description: Optional[str] = None
    detection_source: Optional[str] = None
    investigateur_id: Optional[int] = None
    actions_correctives: Optional[str] = None
    escalation_autorite: Optional[bool] = None
    statut: Optional[str] = None
    notes: Optional[str] = None
    is_active: Optional[bool] = None


class AntiTamperingEventOut(BaseModel):
    id: int
    company_id: int
    reference_alerte: str
    type_alerte: str
    date_detection: datetime
    severite: Optional[str] = None
    asset_type: Optional[str] = None
    asset_ref: Optional[str] = None
    attendu_hash: Optional[str] = None
    constate_hash: Optional[str] = None
    delta_description: Optional[str] = None
    detection_source: Optional[str] = None
    investigateur_id: Optional[int] = None
    actions_correctives: Optional[str] = None
    escalation_autorite: Optional[bool] = None
    statut: Optional[str] = None
    notes: Optional[str] = None
    is_active: Optional[bool] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    model_config = {"from_attributes": True}


class RetentionPolicyCreate(BaseModel):
    code_politique: str
    type_objet: Optional[str] = None
    duree_conservation_ans: Optional[int] = None
    autorite_legale: Optional[str] = None
    base_texte: Optional[str] = None
    archive_apres_echeance: Optional[bool] = None
    destruction_apres_echeance: Optional[bool] = None
    modalite_destruction: Optional[str] = None
    destination_archive: Optional[str] = None
    statut: Optional[str] = None


class RetentionPolicyUpdate(BaseModel):
    code_politique: Optional[str] = None
    type_objet: Optional[str] = None
    duree_conservation_ans: Optional[int] = None
    autorite_legale: Optional[str] = None
    base_texte: Optional[str] = None
    archive_apres_echeance: Optional[bool] = None
    destruction_apres_echeance: Optional[bool] = None
    modalite_destruction: Optional[str] = None
    destination_archive: Optional[str] = None
    statut: Optional[str] = None
    is_active: Optional[bool] = None


class RetentionPolicyOut(BaseModel):
    id: int
    company_id: int
    code_politique: str
    type_objet: Optional[str] = None
    duree_conservation_ans: Optional[int] = None
    autorite_legale: Optional[str] = None
    base_texte: Optional[str] = None
    archive_apres_echeance: Optional[bool] = None
    destruction_apres_echeance: Optional[bool] = None
    modalite_destruction: Optional[str] = None
    destination_archive: Optional[str] = None
    statut: Optional[str] = None
    is_active: Optional[bool] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    model_config = {"from_attributes": True}

