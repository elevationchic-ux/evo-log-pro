"""Modèles tracabilite-audit (expansion wave 6).

Couverture bout-en-bout : chaque entité qui bouge dans le système (colis,
conteneur, lot, pièce sérialisée, document, actif) doit pouvoir être
retracer depuis son origine jusqu'à sa destination finale, avec preuves
d'intégrité inaltérables.

Pattern clef : les tables `*_events`, `*_audit` et `*_transfers` sont
append-only. Elles n'ont PAS de `updated_at` ni `is_active`, car un
événement de traçabilité ne se modifie jamais (sinon on perd la valeur
probante). On y trouve en revanche :
  - hash SHA-256 de l'événement (chaîné au hash du précédent)
  - signature / horodatage / IP source / user agent / trace-id
  - index sur (company_id, asset_type, asset_id) et (date_horloge)
"""
from datetime import datetime
import enum
from sqlalchemy import (
    Boolean, Column, Date, DateTime, Enum as SAEnum, Float, ForeignKey,
    Integer, Numeric, String, Text, UniqueConstraint,
)
from sqlalchemy.orm import relationship

from app.core.database import Base


# ---------------------------------------------------------------------------
# 1. ÉVÉNEMENT DE TRAÇABILITÉ APPEND-ONLY (colonne vertébrale)
# ---------------------------------------------------------------------------

class TraceabilityEvent(Base):
    __tablename__ = "trace_events"
    __table_args__ = (
        UniqueConstraint("company_id", "event_uid", name="uix_trace_event_uid"),
    )
    id = Column(Integer, primary_key=True, index=True)
    company_id = Column(Integer, ForeignKey("companies.id"), nullable=False, index=True)
    event_uid = Column(String(80), nullable=False, index=True)     # UUIDv7 hex
    event_type = Column(String(120), nullable=False, index=True)   # ex 'colis.scan', 'conteneur.entrepose'
    module_source = Column(String(80), nullable=True, index=True)
    asset_type = Column(String(80), nullable=True, index=True)     # parcel/container/serial/lot/document/asset
    asset_id = Column(String(180), nullable=True, index=True)
    subject_ref = Column(String(180), nullable=True, index=True)
    action = Column(String(120), nullable=True)
    payload_json = Column(Text, nullable=True)                     # données métier sérialisées
    actor_id = Column(Integer, ForeignKey("users.id"), nullable=True, index=True)
    actor_ip = Column(String(60), nullable=True, index=True)
    actor_user_agent = Column(String(280), nullable=True)
    actor_role = Column(String(120), nullable=True)
    correlation_id = Column(String(120), nullable=True, index=True)  # trace-id request-scoped
    gps_lat = Column(Float, nullable=True)
    gps_lng = Column(Float, nullable=True)
    timestamp_server = Column(DateTime(timezone=True), default=datetime.utcnow, nullable=False, index=True)
    timestamp_client = Column(DateTime(timezone=True), nullable=True, index=True)
    hash_self = Column(String(80), nullable=True, index=True)      # SHA-256 hexdigest
    hash_prev = Column(String(80), nullable=True, index=True)      # hash de l'événement précédent
    signature_id = Column(Integer, ForeignKey("trace_signatures.id"), nullable=True, index=True)
    est_validite = Column(Boolean, nullable=True, default=True)    # validation Merkle
    notes = Column(Text, nullable=True)

    # PAS de is_active, PAS de updated_at : append-only


# ---------------------------------------------------------------------------
# 2. TRANSFERT DE GARDE (chaque changement de possession)
# ---------------------------------------------------------------------------

class ChainOfCustodyTransfer(Base):
    __tablename__ = "trace_custody_transfers"
    __table_args__ = (
        UniqueConstraint("company_id", "reference_transfert", name="uix_trace_custody_ref"),
    )
    id = Column(Integer, primary_key=True, index=True)
    company_id = Column(Integer, ForeignKey("companies.id"), nullable=False, index=True)
    reference_transfert = Column(String(140), nullable=False, index=True)
    asset_type = Column(String(80), nullable=False, index=True)   # parcel/container/document/goods/serial
    asset_ref = Column(String(180), nullable=False, index=True)
    lot_ref = Column(String(180), nullable=True, index=True)
    source_party = Column(String(180), nullable=True, index=True)  # ex "Magasin A" / "Client X"
    source_contact = Column(String(180), nullable=True)
    target_party = Column(String(180), nullable=True, index=True)
    target_contact = Column(String(180), nullable=True)
    type_transfert = Column(String(80), nullable=True, index=True)
    # remise_physique / chargement / dechargement / livraison / retour / consignation / depot
    date_transfert = Column(DateTime(timezone=True), nullable=False, index=True)
    lieu = Column(String(220), nullable=True)
    gps_lat = Column(Float, nullable=True)
    gps_lng = Column(Float, nullable=True)
    quantite_transferee = Column(Float, nullable=True)
    unite = Column(String(40), nullable=True)
    poids_kg = Column(Float, nullable=True)
    etat_reception = Column(String(80), nullable=True)  # conforme / endommage / incomplet / refuse
    anomalies = Column(Text, nullable=True)
    photos_url = Column(Text, nullable=True)
    signature_source_url = Column(String(280), nullable=True)
    signature_target_url = Column(String(280), nullable=True)
    hash_transfert = Column(String(80), nullable=True, index=True)
    statut = Column(String(40), nullable=True, index=True)
    is_active = Column(Boolean, default=True, nullable=True, index=True)
    created_at = Column(DateTime(timezone=True), default=datetime.utcnow)
    updated_at = Column(DateTime(timezone=True), nullable=True)


# ---------------------------------------------------------------------------
# 3. GÉNÉALOGIE DE LOT (lot parents → lot produit)
# ---------------------------------------------------------------------------

class BatchGenealogy(Base):
    __tablename__ = "trace_batch_genealogy"
    __table_args__ = (
        UniqueConstraint("company_id", "child_lot", "parent_lot", name="uix_trace_batch_lineage"),
    )
    id = Column(Integer, primary_key=True, index=True)
    company_id = Column(Integer, ForeignKey("companies.id"), nullable=False, index=True)
    child_lot = Column(String(180), nullable=False, index=True)
    child_type = Column(String(80), nullable=True, index=True)   # produit fini / semi-fini / melange
    parent_lot = Column(String(180), nullable=False, index=True)
    parent_type = Column(String(80), nullable=True, index=True)
    proportion = Column(Float, nullable=True)                     # 0..1
    quantite_mise_en_oeuvre = Column(Float, nullable=True)
    unite = Column(String(40), nullable=True)
    date_integration = Column(DateTime(timezone=True), nullable=True, index=True)
    operation = Column(String(120), nullable=True)                # mélange / réaction / assemblage
    operateur = Column(String(180), nullable=True)
    atelier = Column(String(180), nullable=True, index=True)
    certificate_url = Column(String(280), nullable=True)
    hash_certificat = Column(String(80), nullable=True)
    notes = Column(Text, nullable=True)
    is_active = Column(Boolean, default=True, nullable=True, index=True)
    created_at = Column(DateTime(timezone=True), default=datetime.utcnow)
    updated_at = Column(DateTime(timezone=True), nullable=True)


# ---------------------------------------------------------------------------
# 4. GÉNÉALOGIE DE SÉRIE (singleton)
# ---------------------------------------------------------------------------

class SerialGenealogy(Base):
    __tablename__ = "trace_serial_genealogy"
    __table_args__ = (
        UniqueConstraint("company_id", "child_serial", "parent_serial", name="uix_trace_serial_lineage"),
    )
    id = Column(Integer, primary_key=True, index=True)
    company_id = Column(Integer, ForeignKey("companies.id"), nullable=False, index=True)
    child_serial = Column(String(180), nullable=False, index=True)
    parent_serial = Column(String(180), nullable=False, index=True)
    relation_type = Column(String(80), nullable=True, index=True)
    # sous_ensemble / kit / accessoire / conteneur_interne / reconditionnement
    date_integration = Column(DateTime(timezone=True), nullable=True, index=True)
    lieu_integration = Column(String(220), nullable=True)
    operateur_id = Column(Integer, ForeignKey("users.id"), nullable=True, index=True)
    ordre_assemblage = Column(Integer, nullable=True)
    notes = Column(Text, nullable=True)
    is_active = Column(Boolean, default=True, nullable=True, index=True)
    created_at = Column(DateTime(timezone=True), default=datetime.utcnow)
    updated_at = Column(DateTime(timezone=True), nullable=True)


# ---------------------------------------------------------------------------
# 5. EMPREINTE DOCUMENTAIRE SHA-256 (GED, DUM, LSE, connaissement)
# ---------------------------------------------------------------------------

class DocumentHash(Base):
    __tablename__ = "trace_document_hashes"
    __table_args__ = (
        UniqueConstraint("company_id", "document_ref", "version", name="uix_trace_doc_version"),
    )
    id = Column(Integer, primary_key=True, index=True)
    company_id = Column(Integer, ForeignKey("companies.id"), nullable=False, index=True)
    document_ref = Column(String(180), nullable=False, index=True)
    document_type = Column(String(80), nullable=True, index=True)   # bl / lse / dum / facture / certificat
    version = Column(Integer, nullable=False, default=1)
    url = Column(String(280), nullable=True)
    mime = Column(String(80), nullable=True)
    taille_octets = Column(Integer, nullable=True)
    hash_algo = Column(String(40), nullable=True)                    # sha256 / sha3-512 / blake3
    hash_hex = Column(String(128), nullable=True, index=True)
    merkle_root = Column(String(80), nullable=True, index=True)
    signature_url = Column(String(280), nullable=True)
    signer_id = Column(Integer, ForeignKey("users.id"), nullable=True, index=True)
    date_emission = Column(DateTime(timezone=True), nullable=True, index=True)
    date_signature = Column(DateTime(timezone=True), nullable=True)
    date_archivage = Column(Date, nullable=True)
    duree_conservation_ans = Column(Integer, nullable=True)
    statut = Column(String(40), nullable=True, index=True)           # actif/remplace/archive/detruit
    notes = Column(Text, nullable=True)
    is_active = Column(Boolean, default=True, nullable=True, index=True)
    created_at = Column(DateTime(timezone=True), default=datetime.utcnow)
    updated_at = Column(DateTime(timezone=True), nullable=True)


# ---------------------------------------------------------------------------
# 6. JOURNAL GÉOLOCALISATION (GPS / AIS / geofencing)
# ---------------------------------------------------------------------------

class GeolocationTrace(Base):
    __tablename__ = "trace_geolocations"
    id = Column(Integer, primary_key=True, index=True)
    company_id = Column(Integer, ForeignKey("companies.id"), nullable=False, index=True)
    subject_type = Column(String(80), nullable=False, index=True)    # vehicule / navire / conteneur / colis / personne
    subject_ref = Column(String(180), nullable=False, index=True)
    date_position = Column(DateTime(timezone=True), nullable=False, index=True)
    gps_lat = Column(Float, nullable=False, index=True)
    gps_lng = Column(Float, nullable=False, index=True)
    altitude_m = Column(Float, nullable=True)
    vitesse_kmh = Column(Float, nullable=True)
    cap_deg = Column(Float, nullable=True)
    precision_m = Column(Float, nullable=True)
    source = Column(String(80), nullable=True, index=True)          # gps / aisc / lora / gsm / manual
    device_id = Column(String(180), nullable=True, index=True)
    geofence_id = Column(Integer, nullable=True, index=True)
    franchissement = Column(String(80), nullable=True)               # entree / sortie / aucun
    notes = Column(Text, nullable=True)
    is_active = Column(Boolean, default=True, nullable=True, index=True)
    created_at = Column(DateTime(timezone=True), default=datetime.utcnow)


# ---------------------------------------------------------------------------
# 7. TRACE CHAÎNE DU FROID (température + humidité + O2 + CO2)
# ---------------------------------------------------------------------------

class ColdChainTrace(Base):
    __tablename__ = "trace_cold_chain"
    id = Column(Integer, primary_key=True, index=True)
    company_id = Column(Integer, ForeignKey("companies.id"), nullable=False, index=True)
    subject_type = Column(String(80), nullable=False, index=True)   # reefer / chamber / parcel / vaccin / food
    subject_ref = Column(String(180), nullable=False, index=True)
    logger_id = Column(String(180), nullable=True, index=True)
    date_lecture = Column(DateTime(timezone=True), nullable=False, index=True)
    temperature_c = Column(Float, nullable=True, index=True)
    humidite_pct = Column(Float, nullable=True)
    co2_ppm = Column(Integer, nullable=True)
    o2_pct = Column(Float, nullable=True)
    pression_bar = Column(Float, nullable=True)
    seuil_min_c = Column(Float, nullable=True)
    seuil_max_c = Column(Float, nullable=True)
    excursion = Column(Boolean, nullable=True, index=True)
    porte_ouverte = Column(Boolean, nullable=True)
    duree_porte_ouverte_s = Column(Integer, nullable=True)
    device_battery_pct = Column(Float, nullable=True)
    notes = Column(Text, nullable=True)
    is_active = Column(Boolean, default=True, nullable=True, index=True)
    created_at = Column(DateTime(timezone=True), default=datetime.utcnow)


# ---------------------------------------------------------------------------
# 8. CHAÎNE DE COMMANDEMENT INCIDENT
# ---------------------------------------------------------------------------

class IncidentChainOfCommand(Base):
    __tablename__ = "trace_incident_commands"
    __table_args__ = (
        UniqueConstraint("company_id", "reference_incident", name="uix_trace_incident_ref"),
    )
    id = Column(Integer, primary_key=True, index=True)
    company_id = Column(Integer, ForeignKey("companies.id"), nullable=False, index=True)
    reference_incident = Column(String(140), nullable=False, index=True)
    type_incident = Column(String(80), nullable=False, index=True)   # accident / pollution / avarie / securite / douane
    date_debut = Column(DateTime(timezone=True), nullable=False, index=True)
    date_fin = Column(DateTime(timezone=True), nullable=True, index=True)
    severite = Column(String(30), nullable=True, index=True)          # faible/moyenne/haute/critique
    description = Column(Text, nullable=True)
    lieu = Column(String(220), nullable=True)
    gps_lat = Column(Float, nullable=True)
    gps_lng = Column(Float, nullable=True)
    chef_secours = Column(String(180), nullable=True)                  # PC = poste de commandement
    autorite_alertee = Column(String(220), nullable=True)               # JSON [{autorite,date_heure,reponse}]
    decisions_prises = Column(Text, nullable=True)                      # JSON [{heure,decision,operateur}]
    ressources_engagees = Column(Text, nullable=True)                   # JSON [{type,qte}]
    victimes = Column(Integer, nullable=True)
    dommages_materials_xaf = Column(Numeric(18, 2), nullable=True)
    arret_activite = Column(Boolean, nullable=True)
    communication_presse = Column(Boolean, nullable=True)
    rapport_final_url = Column(String(280), nullable=True)
    statut = Column(String(40), nullable=True, index=True)              # ouvert/en_cours/cloture
    is_active = Column(Boolean, default=True, nullable=True, index=True)
    created_at = Column(DateTime(timezone=True), default=datetime.utcnow)
    updated_at = Column(DateTime(timezone=True), nullable=True)


# ---------------------------------------------------------------------------
# 9. EXPORT RÉGLEMENTAIRE (SAT/DGI/MINMIVT/APN/COLIFE)
# ---------------------------------------------------------------------------

class RegulatoryTraceExport(Base):
    __tablename__ = "trace_regulatory_exports"
    __table_args__ = (
        UniqueConstraint("company_id", "numero_expedition", name="uix_trace_reg_export"),
    )
    id = Column(Integer, primary_key=True, index=True)
    company_id = Column(Integer, ForeignKey("companies.id"), nullable=False, index=True)
    numero_expedition = Column(String(140), nullable=False, index=True)
    autorite_destinataire = Column(String(180), nullable=False, index=True)  # SAT / DGI / ANINF / APN / MINMT / COLIFE / CIP
    type_declaration = Column(String(120), nullable=True, index=True)         # T1 / DUM / DM20 / T-Code
    periode_reference = Column(String(20), nullable=True, index=True)         # 'YYYY-MM'
    date_depot = Column(DateTime(timezone=True), nullable=True, index=True)
    canaux = Column(String(120), nullable=True)                               # gui_solo / tele-service / depot_physique
    nb_lignes = Column(Integer, nullable=True)
    montant_declare_xaf = Column(Numeric(18, 2), nullable=True)
    fichier_url = Column(String(280), nullable=True)
    fichier_hash = Column(String(80), nullable=True, index=True)
    numero_recu = Column(String(140), nullable=True, index=True)
    date_recu = Column(DateTime(timezone=True), nullable=True)
    statut = Column(String(40), nullable=True, index=True)
    # brouillon / transmis / accepte / rejete / complete
    reponse_autorite = Column(Text, nullable=True)
    anomalies = Column(Text, nullable=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=True, index=True)
    is_active = Column(Boolean, default=True, nullable=True, index=True)
    created_at = Column(DateTime(timezone=True), default=datetime.utcnow)
    updated_at = Column(DateTime(timezone=True), nullable=True)


# ---------------------------------------------------------------------------
# 10. JOURNAL D'AUDIT INALTÉRABLE (flux login / mutations sensibles)
# ---------------------------------------------------------------------------

class ImmutableAuditLog(Base):
    __tablename__ = "trace_audit_logs"
    id = Column(Integer, primary_key=True, index=True)
    company_id = Column(Integer, ForeignKey("companies.id"), nullable=True, index=True)
    event_uid = Column(String(80), nullable=True, index=True)
    actor_id = Column(Integer, ForeignKey("users.id"), nullable=True, index=True)
    actor_email = Column(String(180), nullable=True, index=True)
    actor_ip = Column(String(60), nullable=True, index=True)
    user_agent = Column(String(280), nullable=True)
    action = Column(String(80), nullable=True, index=True)   # login / logout / create / update / delete / export / print / permission_grant
    resource_type = Column(String(80), nullable=True, index=True)
    resource_id = Column(String(180), nullable=True, index=True)
    before_snapshot = Column(Text, nullable=True)
    after_snapshot = Column(Text, nullable=True)
    raison_metier = Column(String(220), nullable=True)
    timestamp_server = Column(DateTime(timezone=True), default=datetime.utcnow, nullable=False, index=True)
    hash_self = Column(String(80), nullable=True, index=True)
    hash_prev = Column(String(80), nullable=True, index=True)
    merkle_root = Column(String(80), nullable=True, index=True)
    validite = Column(Boolean, nullable=True, default=True)
    session_id = Column(String(180), nullable=True, index=True)

    # append-only


# ---------------------------------------------------------------------------
# 11. HORODATAGE QUALIFIÉ (eIDAS / CAMPOST cert)
# ---------------------------------------------------------------------------

class TimestampAuthority(Base):
    __tablename__ = "trace_timestamps"
    __table_args__ = (
        UniqueConstraint("company_id", "token_tsa", name="uix_trace_tsa_token"),
    )
    id = Column(Integer, primary_key=True, index=True)
    company_id = Column(Integer, ForeignKey("companies.id"), nullable=False, index=True)
    token_tsa = Column(String(140), nullable=False, index=True)
    autorite_certification = Column(String(180), nullable=True, index=True)   # CAMPOST / Docapost / DGCIS / eIDAS QTSP
    algorithme_signature = Column(String(60), nullable=True)
    objet_type = Column(String(80), nullable=True, index=True)   # document / event / audit / transaction
    objet_ref = Column(String(180), nullable=True, index=True)
    objet_hash = Column(String(128), nullable=True, index=True)
    date_horodatage = Column(DateTime(timezone=True), nullable=False, index=True)
    precision_seconde = Column(Integer, nullable=True)
    certificate_serial = Column(String(180), nullable=True, index=True)
    certificate_issuer = Column(String(220), nullable=True)
    certificate_valide_jusqu = Column(Date, nullable=True)
    token_blob = Column(Text, nullable=True)
    statut = Column(String(40), nullable=True, index=True)
    is_active = Column(Boolean, default=True, nullable=True, index=True)
    created_at = Column(DateTime(timezone=True), default=datetime.utcnow)
    updated_at = Column(DateTime(timezone=True), nullable=True)


# ---------------------------------------------------------------------------
# 12. SIGNATURE TEMOIN (counter-signature manuscrite ou digitale)
# ---------------------------------------------------------------------------

class WitnessSignature(Base):
    __tablename__ = "trace_witness_signatures"
    __table_args__ = (
        UniqueConstraint("company_id", "reference_signature", name="uix_trace_sig_ref"),
    )
    id = Column(Integer, primary_key=True, index=True)
    company_id = Column(Integer, ForeignKey("companies.id"), nullable=False, index=True)
    reference_signature = Column(String(140), nullable=False, index=True)
    type_signataire = Column(String(60), nullable=True, index=True)   # emetteur / destinataire / temoin / notaire / autorite
    signataire_nom = Column(String(180), nullable=True)
    signataire_qualite = Column(String(180), nullable=True)
    signataire_email = Column(String(180), nullable=True, index=True)
    signataire_telephone = Column(String(60), nullable=True)
    piece_identite_ref = Column(String(120), nullable=True, index=True)
    document_ref = Column(String(180), nullable=True, index=True)
    event_uid = Column(String(80), nullable=True, index=True)
    type_signature = Column(String(60), nullable=True, index=True)     # manuscrite / otp / certificat_qualifie / biom
    signature_blob_url = Column(String(280), nullable=True)
    hash_signature = Column(String(128), nullable=True, index=True)
    date_signature = Column(DateTime(timezone=True), nullable=False, index=True)
    gps_lat = Column(Float, nullable=True)
    gps_lng = Column(Float, nullable=True)
    ip_signature = Column(String(60), nullable=True, index=True)
    tsa_id = Column(Integer, ForeignKey("trace_timestamps.id"), nullable=True, index=True)
    statut = Column(String(40), nullable=True, index=True)               # en_attente / signee / refusee
    is_active = Column(Boolean, default=True, nullable=True, index=True)
    created_at = Column(DateTime(timezone=True), default=datetime.utcnow)
    updated_at = Column(DateTime(timezone=True), nullable=True)


# ---------------------------------------------------------------------------
# 13. PREUVE MERKLE (intégrité de période / bloc d'audit)
# ---------------------------------------------------------------------------

class IntegrityMerkleProof(Base):
    __tablename__ = "trace_merkle_proofs"
    __table_args__ = (
        UniqueConstraint("company_id", "periode", "racine_type", name="uix_trace_merkle_period"),
    )
    id = Column(Integer, primary_key=True, index=True)
    company_id = Column(Integer, ForeignKey("companies.id"), nullable=False, index=True)
    racine_type = Column(String(60), nullable=False, index=True)   # audit / event / cold_chain / document
    periode = Column(String(20), nullable=False, index=True)         # '2026-10' ou '2026-10-05'
    nb_leaves = Column(Integer, nullable=True)
    merkle_root = Column(String(80), nullable=True, index=True)
    first_leaf_hash = Column(String(80), nullable=True, index=True)
    last_leaf_hash = Column(String(80), nullable=True, index=True)
    chemin_verification = Column(Text, nullable=True)               # JSON [{hash, side}]
    date_publication = Column(DateTime(timezone=True), nullable=True, index=True)
    tsa_id = Column(Integer, ForeignKey("trace_timestamps.id"), nullable=True, index=True)
    publication_externe = Column(String(220), nullable=True)          # blockchain / journal officiel / tier
    statut = Column(String(40), nullable=True, index=True)            # genere / publie / verifie / invalide
    notes = Column(Text, nullable=True)
    is_active = Column(Boolean, default=True, nullable=True, index=True)
    created_at = Column(DateTime(timezone=True), default=datetime.utcnow)
    updated_at = Column(DateTime(timezone=True), nullable=True)


# ---------------------------------------------------------------------------
# 14. PLOMB / SCEAU CONTENEUR (numéro unique + intégrité)
# ---------------------------------------------------------------------------

class ContainerSeal(Base):
    __tablename__ = "trace_container_seals"
    __table_args__ = (
        UniqueConstraint("company_id", "numero_sceau", name="uix_trace_seal_num"),
    )
    id = Column(Integer, primary_key=True, index=True)
    company_id = Column(Integer, ForeignKey("companies.id"), nullable=False, index=True)
    numero_sceau = Column(String(120), nullable=False, index=True)
    type_sceau = Column(String(80), nullable=True, index=True)       # haute_securite_iso17712 / cable / plastique / electronique
    conteneur_numero = Column(String(120), nullable=True, index=True)
    b_l_numero = Column(String(120), nullable=True, index=True)
    date_apposition = Column(DateTime(timezone=True), nullable=True, index=True)
    lieu_apposition = Column(String(220), nullable=True)
    operateur_apposition = Column(String(180), nullable=True)
    signature_url = Column(String(280), nullable=True)
    photo_url = Column(String(280), nullable=True)
    date_retrait = Column(DateTime(timezone=True), nullable=True, index=True)
    lieu_retrait = Column(String(220), nullable=True)
    operateur_retrait = Column(String(180), nullable=True)
    numero_recolte = Column(String(120), nullable=True, index=True)  # si changement
    integrite_verifiee = Column(Boolean, nullable=True)
    anomalie_sceau = Column(String(220), nullable=True)
    autorite_alertee = Column(String(180), nullable=True)
    statut = Column(String(40), nullable=True, index=True)            # appose / retire / suspect / remplace
    notes = Column(Text, nullable=True)
    is_active = Column(Boolean, default=True, nullable=True, index=True)
    created_at = Column(DateTime(timezone=True), default=datetime.utcnow)
    updated_at = Column(DateTime(timezone=True), nullable=True)


# ---------------------------------------------------------------------------
# 15. HANDOFF DE CARGAISON (transfert physique entre transporteurs)
# ---------------------------------------------------------------------------

class CargoHandoff(Base):
    __tablename__ = "trace_cargo_handoffs"
    __table_args__ = (
        UniqueConstraint("company_id", "reference_handoff", name="uix_trace_handoff_ref"),
    )
    id = Column(Integer, primary_key=True, index=True)
    company_id = Column(Integer, ForeignKey("companies.id"), nullable=False, index=True)
    reference_handoff = Column(String(140), nullable=False, index=True)
    type_cargo = Column(String(80), nullable=True, index=True)   # container / pallet / parcel / bulk / reefer
    cargo_ref = Column(String(180), nullable=True, index=True)
    mode_precedent = Column(String(60), nullable=True, index=True)  # maritime / routier / fer / aerien / fluvial
    mode_suivant = Column(String(60), nullable=True, index=True)
    transporteur_precedent = Column(String(180), nullable=True, index=True)
    transporteur_suivant = Column(String(180), nullable=True, index=True)
    lieu_handoff = Column(String(220), nullable=True, index=True)   # port/aero/gare/hub/terminal
    date_debut_prise_en_charge = Column(DateTime(timezone=True), nullable=True, index=True)
    date_fin_prise_en_charge = Column(DateTime(timezone=True), nullable=True, index=True)
    poids_kg = Column(Float, nullable=True)
    volume_m3 = Column(Float, nullable=True)
    nb_colis = Column(Integer, nullable=True)
    temperature_c = Column(Float, nullable=True)
    etat_entree = Column(String(80), nullable=True)                  # conforme / avarie / retard / refuse
    etat_sortie = Column(String(80), nullable=True)
    anomalies_constatees = Column(Text, nullable=True)
    photos_url = Column(Text, nullable=True)
    signataire_entree = Column(String(180), nullable=True)
    signataire_sortie = Column(String(180), nullable=True)
    hash_handoff = Column(String(80), nullable=True, index=True)
    statut = Column(String(40), nullable=True, index=True)
    is_active = Column(Boolean, default=True, nullable=True, index=True)
    created_at = Column(DateTime(timezone=True), default=datetime.utcnow)
    updated_at = Column(DateTime(timezone=True), nullable=True)


# ---------------------------------------------------------------------------
# 16. JOURNAL D'ACCÈS SECURISÉ (auth, JWT, refresh, permission change)
# ---------------------------------------------------------------------------

class AccessSecurityLog(Base):
    __tablename__ = "trace_access_security"
    id = Column(Integer, primary_key=True, index=True)
    company_id = Column(Integer, ForeignKey("companies.id"), nullable=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=True, index=True)
    email_tente = Column(String(180), nullable=True, index=True)
    type_evenement = Column(String(60), nullable=False, index=True)
    # login_success / login_fail / logout / refresh_token / mfa_challenge / mfa_success / mfa_fail /
    # password_change / permission_granted / permission_revoked / token_revoked / account_locked
    date_evenement = Column(DateTime(timezone=True), default=datetime.utcnow, nullable=False, index=True)
    ip_source = Column(String(60), nullable=True, index=True)
    user_agent = Column(String(280), nullable=True)
    geo_pays = Column(String(80), nullable=True)
    geo_ville = Column(String(120), nullable=True)
    session_id = Column(String(180), nullable=True, index=True)
    device_fingerprint = Column(String(180), nullable=True, index=True)
    nb_echecs_successifs = Column(Integer, nullable=True)
    severite = Column(String(30), nullable=True, index=True)
    action_remediation = Column(String(220), nullable=True)
    meta_json = Column(Text, nullable=True)
    hash_self = Column(String(80), nullable=True, index=True)
    hash_prev = Column(String(80), nullable=True, index=True)

    # append-only (sécurité)


# ---------------------------------------------------------------------------
# 17. CONSENTEMENT / PRIVACY (loi camerounaise 2010/041 CYBER + RGPD export)
# ---------------------------------------------------------------------------

class ConsentGrant(Base):
    __tablename__ = "trace_consents"
    __table_args__ = (
        UniqueConstraint("company_id", "reference_consentement", name="uix_trace_consent_ref"),
    )
    id = Column(Integer, primary_key=True, index=True)
    company_id = Column(Integer, ForeignKey("companies.id"), nullable=False, index=True)
    reference_consentement = Column(String(140), nullable=False, index=True)
    subject_type = Column(String(60), nullable=True, index=True)     # user / client / prestataire
    subject_ref = Column(String(180), nullable=True, index=True)
    finalite = Column(String(220), nullable=True)                      # ex "envoi SMS suivi colis"
    categorie_donnees = Column(String(220), nullable=True)
    duree_conservation_mois = Column(Integer, nullable=True)
    tiers_partagables = Column(Text, nullable=True)                    # JSON [liste]
    date_consente = Column(DateTime(timezone=True), nullable=True, index=True)
    date_retiree = Column(DateTime(timezone=True), nullable=True, index=True)
    canal_recueil = Column(String(80), nullable=True)                   # web / borne / signature / telephone
    ip_recueil = Column(String(60), nullable=True, index=True)
    preuve_url = Column(String(280), nullable=True)
    hash_preuve = Column(String(80), nullable=True, index=True)
    statut = Column(String(40), nullable=True, index=True)              # actif / retire / expire
    is_active = Column(Boolean, default=True, nullable=True, index=True)
    created_at = Column(DateTime(timezone=True), default=datetime.utcnow)
    updated_at = Column(DateTime(timezone=True), nullable=True)


# ---------------------------------------------------------------------------
# 18. ÉVÉNEMENT ANTI-TAMPERING (détection altération)
# ---------------------------------------------------------------------------

class AntiTamperingEvent(Base):
    __tablename__ = "trace_anti_tampering"
    __table_args__ = (
        UniqueConstraint("company_id", "reference_alerte", name="uix_trace_anti_tamp_ref"),
    )
    id = Column(Integer, primary_key=True, index=True)
    company_id = Column(Integer, ForeignKey("companies.id"), nullable=False, index=True)
    reference_alerte = Column(String(140), nullable=False, index=True)
    type_alerte = Column(String(80), nullable=False, index=True)
    # hash_mismatch / audit_gap / signature_invalide / merkle_invalid / unauthorized_edit / replay / bruteforce
    date_detection = Column(DateTime(timezone=True), nullable=False, index=True)
    severite = Column(String(40), nullable=True, index=True)
    asset_type = Column(String(80), nullable=True, index=True)
    asset_ref = Column(String(180), nullable=True, index=True)
    attendu_hash = Column(String(80), nullable=True, index=True)
    constate_hash = Column(String(80), nullable=True, index=True)
    delta_description = Column(Text, nullable=True)
    detection_source = Column(String(180), nullable=True)                # cron_verif / tache_fond / manuel
    investigateur_id = Column(Integer, ForeignKey("users.id"), nullable=True, index=True)
    actions_correctives = Column(Text, nullable=True)
    escalation_autorite = Column(Boolean, nullable=True)
    statut = Column(String(40), nullable=True, index=True)               # ouvert / en_cours / resolu / fausse_alerte
    notes = Column(Text, nullable=True)
    is_active = Column(Boolean, default=True, nullable=True, index=True)
    created_at = Column(DateTime(timezone=True), default=datetime.utcnow)
    updated_at = Column(DateTime(timezone=True), nullable=True)


# ---------------------------------------------------------------------------
# 19. SIGNATURE (alias court pour relation TraceabilityEvent)
# ---------------------------------------------------------------------------
# (déjà couvert par WitnessSignature ci-dessus)

# 20. RÈGLE DE RÉTENTION (durées légales par type d'objet)
class RetentionPolicy(Base):
    __tablename__ = "trace_retention_policies"
    __table_args__ = (
        UniqueConstraint("company_id", "code_politique", name="uix_trace_retention_code"),
    )
    id = Column(Integer, primary_key=True, index=True)
    company_id = Column(Integer, ForeignKey("companies.id"), nullable=False, index=True)
    code_politique = Column(String(120), nullable=False, index=True)
    type_objet = Column(String(120), nullable=True, index=True)          # facture / bl / lse / dum / audit / event / doc
    duree_conservation_ans = Column(Integer, nullable=True, index=True)
    autorite_legale = Column(String(180), nullable=True)                  # ex 'OGIC 2017 / CGI Cameroun / SAT'
    base_texte = Column(String(280), nullable=True)
    archive_apres_echeance = Column(Boolean, nullable=True)               # true → passage froid MinIO/S3 Glacier
    destruction_apres_echeance = Column(Boolean, nullable=True)
    modalite_destruction = Column(String(180), nullable=True)
    destination_archive = Column(String(180), nullable=True)
    statut = Column(String(40), nullable=True, index=True)
    is_active = Column(Boolean, default=True, nullable=True, index=True)
    created_at = Column(DateTime(timezone=True), default=datetime.utcnow)
    updated_at = Column(DateTime(timezone=True), nullable=True)
