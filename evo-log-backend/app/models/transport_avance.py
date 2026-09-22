"""
Advanced transport models - Complete logistics for Cameroon/CEMAC
Includes route optimization, fleet management, subcontractors, GPS tracking
"""
from sqlalchemy import Column, Integer, String, Text, DateTime, Boolean, Float, ForeignKey, Enum, Date, Numeric
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
import enum
from app.core.database import Base


class StatutTournée(str, enum.Enum):
    """Route status"""
    PLANIFIEE = "planifiee"
    EN_COURS = "en_cours"
    TERMINEE = "terminee"
    ANNULEE = "annulee"
    EN_RETARD = "en_retard"


class Tournée(Base):
    """Route optimization model - Delivery tours"""
    __tablename__ = "tours"
    
    id = Column(Integer, primary_key=True, index=True)
    numero_tournee = Column(String(50), unique=True, nullable=False)
    conducteur_id = Column(Integer, ForeignKey('conducteurs.id'), nullable=False)
    camion_id = Column(Integer, ForeignKey('camions.id'), nullable=False)
    date_tournee = Column(Date, nullable=False)
    statut = Column(Enum(StatutTournée), default=StatutTournée.PLANIFIEE)
    nombre_livraisons = Column(Integer, default=0)
    nombre_livraisons_effectuees = Column(Integer, default=0)
    distance_totale = Column(Numeric)
    duree_estimee = Column(Integer)  # En minutes
    duree_reelle = Column(Integer)
    cout_estime = Column(Numeric)
    cout_reel = Column(Numeric)
    performance = Column(Numeric)  # Pourcentage de livraisons réussies
    type_tournee = Column(String(50))  # urbaine, rurale, longue_distance
    notes = Column(Text)
    createur = Column(Integer, ForeignKey('users.id'))
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relationships
    conducteur = relationship("Conducteur")
    camion = relationship("Camion")
    livraisons = relationship("Livraison", back_populates="tournee")


class Livraison(Base):
    """Delivery model"""
    __tablename__ = "livraisons"
    
    id = Column(Integer, primary_key=True, index=True)
    numero_livraison = Column(String(50), unique=True, nullable=False)
    tournee_id = Column(Integer, ForeignKey('tours.id'), nullable=False)
    client_id = Column(Integer, ForeignKey('clients.id'), nullable=False)
    point_dechargement = Column(String(200), nullable=False)
    heure_debut_prevue = Column(String(10))
    heure_fin_prevue = Column(String(10))
    heure_debut_reelle = Column(String(10))
    heure_fin_reelle = Column(String(10))
    statut = Column(String(20), default="en_attente")  # en_attente, en_cours, livre, echoue, annule
    nombre_colis = Column(Integer, default=0)
    poids_total = Column(Numeric)
    preuve_livraison = Column(Text)  # Signature, photo
    commentaire = Column(Text)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # Relationships
    tournee = relationship("Tournée", back_populates="livraisons")
    client = relationship("Client")


class FraisKilometrique(Base):
    """Mileage expense model - Cameroon compliant"""
    __tablename__ = "frais_kilometriques"
    
    id = Column(Integer, primary_key=True, index=True)
    employe_id = Column(Integer, ForeignKey('users.id'), nullable=False)
    mission_id = Column(Integer, ForeignKey('missions.id'))
    date_frais = Column(Date, server_default=func.current_date())
    kilometrage_parcouru = Column(Numeric, nullable=False)
    kilometrage_theorique = Column(Numeric)
    taux_indemnite = Column(Numeric, default=0)  # FCFA/km according to Cameroon rates
    montant_indemnite = Column(Numeric)
    economie_carburant = Column(Numeric)  # Fuel economy vs theoretical
    surconsommation = Column(Numeric)
    note_performance = Column(Numeric)
    statut = Column(String(20), default="en_attente")  # en_attente, valide, refuse
    validateur = Column(Integer, ForeignKey('users.id'))
    date_validation = Column(Date)
    commentaires = Column(Text)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # Relationships
    employe = relationship("User", foreign_keys=[employe_id])
    mission = relationship("Mission")


class TempsConduite(Base):
    """Driving time tracking model - Cameroon labor law compliant"""
    __tablename__ = "temps_conduite"
    
    id = Column(Integer, primary_key=True, index=True)
    conducteur_id = Column(Integer, ForeignKey('conducteurs.id'), nullable=False)
    mission_id = Column(Integer, ForeignKey('missions.id'))
    date = Column(Date, nullable=False)
    heure_debut_conduite = Column(String(10), nullable=False)
    heure_fin_conduite = Column(String(10))
    temps_conduite = Column(Integer)  # En minutes
    temps_repos = Column(Integer)  # En minutes
    temps_service = Column(Integer)  # En minutes
    depassement_temps = Column(Integer, default=0)  # En minutes
    conformite_legale = Column(Boolean, default=True)
    statut = Column(String(20), default="conforme")  # conforme, non_conforme, en_violation
    validateur = Column(Integer, ForeignKey('users.id'))
    commentaires = Column(Text)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # Relationships
    conducteur = relationship("Conducteur")
    mission = relationship("Mission")


class SousTraitant(Base):
    """Subcontractor model"""
    __tablename__ = "sous_traitants"
    
    id = Column(Integer, primary_key=True, index=True)
    code = Column(String(50), unique=True, nullable=False)
    nom = Column(String(100), nullable=False)
    type_service = Column(String(50))  # transport, logistique, manutention
    specialite = Column(String(100))
    numero_licence = Column(String(50))
    adresse = Column(Text)
    ville = Column(String(50))
    pays = Column(String(50), default="Cameroun")
    telephone = Column(String(20))
    email = Column(String(100))
    flotte_taille = Column(Integer)
    capacite_transport = Column(Numeric)  # Tonnes
    assurance_responsabilite_civile = Column(Numeric)
    statut = Column(String(20), default="actif")  # actif, inactif, suspendu
    date_debut_contrat = Column(Date)
    date_fin_contrat = Column(Date)
    evaluation_performance = Column(Numeric)  # Note 1-10
    notes = Column(Text)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relationships
    contrats = relationship("ContratSousTraitant", back_populates="sous_traitant")


class ContratSousTraitant(Base):
    """Subcontractor contract model"""
    __tablename__ = "contrats_sous_traitants"
    
    id = Column(Integer, primary_key=True, index=True)
    sous_traitant_id = Column(Integer, ForeignKey('sous_traitants.id'), nullable=False)
    numero_contrat = Column(String(50), unique=True, nullable=False)
    type_service = Column(String(50))
    date_debut = Column(Date, nullable=False)
    date_fin = Column(Date)
    tarif_unitaire = Column(Numeric)
    unite_tarif = Column(String(20))  # km, tonne, livraison
    volume_minimum = Column(Numeric)
    conditions_paiement = Column(Text)
    garanties = Column(Text)
    penalties = Column(Text)
    statut = Column(String(20), default="actif")  # actif, expire, resilie, suspendu
    notes = Column(Text)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relationships
    sous_traitant = relationship("SousTraitant", back_populates="contrats")


class MissionSousTraitant(Base):
    """Subcontractor mission model"""
    __tablename__ = "missions_sous_traitant"
    
    id = Column(Integer, primary_key=True, index=True)
    numero_mission = Column(String(50), unique=True, nullable=False)
    sous_traitant_id = Column(Integer, ForeignKey('sous_traitants.id'), nullable=False)
    contrat_id = Column(Integer, ForeignKey('contrats_sous_traitants.id'))
    client_id = Column(Date, nullable=False)
    date_mission = Column(Date, nullable=False)
    point_depart = Column(String(200), nullable=False)
    point_arrivee = Column(String(200), nullable=False)
    distance = Column(Numeric)
    type_marchandise = Column(String(100))
    poids = Column(Numeric)
    statut = Column(String(20), default="planifiee")  # planifie, en_cours, terminee, annulee
    cout_estime = Column(Numeric)
    cout_reel = Column(Numeric)
    qualite_service = Column(Numeric)  # Note 1-10
    ponctualite = Column(Numeric)  # Note 1-10
    notes = Column(Text)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relationships
    sous_traitant = relationship("SousTraitant")
    contrat = relationship("ContratSousTraitant")


class AccidentTransport(Base):
    """Transport accident model"""
    __tablename__ = "accidents_transport"
    
    id = Column(Integer, primary_key=True, index=True)
    numero_accident = Column(String(50), unique=True, nullable=False)
    vehicule_id = Column(Integer, ForeignKey('vehicules.id'), nullable=False)
    conducteur_id = Column(Integer, ForeignKey('conducteurs.id'), nullable=False)
    mission_id = Column(Integer, ForeignKey('missions.id'))
    date_accident = Column(DateTime(timezone=True), nullable=False)
    heure_accident = Column(String(10))
    lieu = Column(String(200), nullable=False)
    type_accident = Column(String(50))  # collision, renversement, blessure, materiel
    gravite = Column(String(20))  # legere, moyenne, grave, mortel
    blesses = Column(Integer, default=0)
    deces = Column(Integer, default=0)
    degats_materiels = Column(Text)
    temoins = Column(Text)
    rapport_police = Column(String(100))
    constat = Column(Text)
    assureur = Column(String(100))
    numero_police = Column(String(50))
    montant_dommages = Column(Numeric)
    montant_rembourse = Column(Numeric)
    statut = Column(String(20), default="en_cours")  # en_cours, clos, en_litige
    date_clos = Column(Date)
    notes = Column(Text)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relationships
    vehicule = relationship("Vehicule")


# ============ DISPATCH INTELLIGENT ============

class TypeOptimisation(str, enum.Enum):
    """Optimization type enumeration"""
    PLUS_COURT_CHEMIN = "plus_court_chemin"
    PLUS_RAPIDE = "plus_rapide"
    MOINS_COUT = "moins_cout"
    EQUILIBRE_CHARGE = "equilibre_charge"
    TEMPS_REEL = "temps_reel"


class StatutDispatch(str, enum.Enum):
    """Dispatch status enumeration"""
    EN_ATTENTE = "en_attente"
    PLANIFIE = "planifie"
    EN_COURS = "en_cours"
    VALIDE = "valide"
    REJETE = "rejetee"
    ANNULEE = "annulee"


class Dispatch(Base):
    """Dispatch model - Intelligent mission assignment"""
    __tablename__ = "dispatches"
    
    id = Column(Integer, primary_key=True, index=True)
    numero_dispatch = Column(String(50), unique=True, nullable=False, index=True)
    mission_id = Column(Integer, ForeignKey('missions.id'), nullable=False)
    conducteur_id = Column(Integer, ForeignKey('conducteurs.id'), nullable=False)
    camion_id = Column(Integer, ForeignKey('camions.id'), nullable=False)
    type_optimisation = Column(Enum(TypeOptimisation), default=TypeOptimisation.PLUS_COURT_CHEMIN)
    statut = Column(Enum(StatutDispatch), default=StatutDispatch.EN_ATTENTE)
    date_planification = Column(DateTime(timezone=True), server_default=func.now())
    date_debut_prevue = Column(DateTime(timezone=True))
    date_fin_prevue = Column(DateTime(timezone=True))
    date_debut_reelle = Column(DateTime(timezone=True))
    date_fin_reelle = Column(DateTime(timezone=True))
    distance_estimee = Column(Numeric)
    distance_reelle = Column(Numeric)
    duree_estimee = Column(Integer)  # En minutes
    duree_reelle = Column(Integer)
    cout_estime = Column(Numeric(15, 2))
    cout_reel = Column(Numeric(15, 2))
    priorite = Column(Integer, default=5)  # 1-10, 10 = priorité maximale
    score_confiance = Column(Numeric)  # Score de confiance de l'algorithme
    facteurs_consideres = Column(Text)  # JSON des facteurs considérés
    notes = Column(Text)
    planificateur = Column(Integer, ForeignKey('users.id'))
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relationships
    mission = relationship("Mission")
    conducteur = relationship("Conducteur")
    camion = relationship("Camion")
    arrets = relationship("Arret", back_populates="dispatch")


class Arret(Base):
    """Stop model - Delivery/pickup points"""
    __tablename__ = "arrets"
    
    id = Column(Integer, primary_key=True, index=True)
    dispatch_id = Column(Integer, ForeignKey('dispatches.id'), nullable=False)
    type_arret = Column(String(20))  # livraison, ramassage, carburant, repos
    ordre_sequence = Column(Integer, nullable=False)
    client_id = Column(Integer, ForeignKey('clients.id'))
    adresse = Column(String(200), nullable=False)
    latitude = Column(Numeric)
    longitude = Column(Numeric)
    duree_estimee = Column(Integer)  # En minutes
    duree_reelle = Column(Integer)
    heure_arrivee_prevue = Column(DateTime(timezone=True))
    heure_arrivee_reelle = Column(DateTime(timezone=True))
    heure_depart_prevue = Column(DateTime(timezone=True))
    heure_depart_reelle = Column(DateTime(timezone=True))
    statut = Column(String(20), default="en_attente")  # en_attente, arrive, en_cours, termine, saute
    notes = Column(Text)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relationships
    dispatch = relationship("Dispatch", back_populates="arrets")
    client = relationship("Client")


class ContrainteDispatch(Base):
    """Dispatch constraint model"""
    __tablename__ = "contraintes_dispatch"
    
    id = Column(Integer, primary_key=True, index=True)
    dispatch_id = Column(Integer, ForeignKey('dispatches.id'), nullable=False)
    type_contrainte = Column(String(50))  # horaire, capacite, zone, competence
    description = Column(Text)
    valeur = Column(String(100))
    unite = Column(String(20))
    respectee = Column(Boolean, default=False)
    penalite = Column(Numeric(15, 2))
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # Relationships
    dispatch = relationship("Dispatch")


# ============ E-POD (Preuve de Livraison Électronique) ============

class TypePreuve(str, enum.Enum):
    """Proof type enumeration"""
    SIGNATURE = "signature"
    PHOTO = "photo"
    DOCUMENT = "document"
    GPS = "gps"
    AUDIO = "audio"


class POD(Base):
    """Proof of Delivery model"""
    __tablename__ = "pods"
    
    id = Column(Integer, primary_key=True, index=True)
    numero_pod = Column(String(50), unique=True, nullable=False, index=True)
    livraison_id = Column(Integer, ForeignKey('livraisons.id'), nullable=False)
    date_pod = Column(DateTime(timezone=True), server_default=func.now())
    statut = Column(String(20), default="en_attente")  # en_attente, valide, refuse
    signature_client = Column(Text)  # Base64 ou URL
    photo_marchandise = Column(Text)  # Base64 ou URL
    photo_signature = Column(Text)  # Base64 ou URL
    coordonnees_livraison = Column(String(200))  # Lat,Long
    horodatage = Column(DateTime(timezone=True))
    nom_receveur = Column(String(100))
    fonction_receveur = Column(String(100))
    commentaire_client = Column(Text)
    commentaire_chauffeur = Column(Text)
    conditions_livraison = Column(Text)
    documents_attaches = Column(Text)  # JSON des URLs
    valide_par = Column(Integer, ForeignKey('users.id'))
    date_validation = Column(DateTime(timezone=True))
    hash_preuve = Column(String(255))  # Hash pour intégrité
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relationships
    livraison = relationship("Livraison")


class DocumentPOD(Base):
    """POD document model"""
    __tablename__ = "documents_pod"
    
    id = Column(Integer, primary_key=True, index=True)
    pod_id = Column(Integer, ForeignKey('pods.id'), nullable=False)
    type_document = Column(String(50))  # bon_livraison, bon_reception, facture, autre
    type_preuve = Column(Enum(TypePreuve))
    nom_fichier = Column(String(200))
    url_fichier = Column(String(500))
    taille_fichier = Column(Integer)
    type_mime = Column(String(100))
    hash_fichier = Column(String(255))
    upload_par = Column(Integer, ForeignKey('users.id'))
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # Relationships
    pod = relationship("POD")


# ============ ANALYTICS TRANSPORT ============

class KPIPerformance(Base):
    """KPI Performance model"""
    __tablename__ = "kpi_performance"
    
    id = Column(Integer, primary_key=True, index=True)
    periode = Column(String(50), nullable=False)  # "2026-01", "2026-Q1"
    type_periode = Column(String(20))  # mensuel, trimestriel, annuel
    conducteur_id = Column(Integer, ForeignKey('conducteurs.id'))
    camion_id = Column(Integer, ForeignKey('camions.id'))
    nombre_missions = Column(Integer, default=0)
    nombre_missions_reussies = Column(Integer, default=0)
    taux_reussite = Column(Numeric, default=0)
    nombre_km_parcourus = Column(Numeric, default=0)
    nombre_heures_conduite = Column(Numeric, default=0)
    consommation_moyenne = Column(Numeric)  # L/100km
    nombre_incidents = Column(Integer, default=0)
    nombre_retards = Column(Integer, default=0)
    satisfaction_client = Column(Numeric)  # 1-5
    cout_par_km = Column(Numeric(15, 2))
    revenu_total = Column(Numeric(15, 2))
    benefice = Column(Numeric(15, 2))
    note_performance = Column(Numeric)  # 0-100
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relationships
    conducteur = relationship("Conducteur")
    camion = relationship("Camion")


class TableauBordTransport(Base):
    """Transport dashboard model"""
    __tablename__ = "tableaux_bord_transport"
    
    id = Column(Integer, primary_key=True, index=True)
    date_dashboard = Column(Date, nullable=False)
    nombre_missions_actives = Column(Integer, default=0)
    nombre_missions_terminees = Column(Integer, default=0)
    nombre_missions_en_retard = Column(Integer, default=0)
    nombre_vehicules_disponibles = Column(Integer, default=0)
    nombre_vehicules_en_mission = Column(Integer, default=0)
    nombre_vehicules_hors_service = Column(Integer, default=0)
    nombre_conducteurs_disponibles = Column(Integer, default=0)
    nombre_conducteurs_en_mission = Column(Integer, default=0)
    taux_occupation = Column(Numeric)  # Pourcentage
    taux_reussite = Column(Numeric)  # Pourcentage
    cout_total_jour = Column(Numeric(15, 2))
    revenu_total_jour = Column(Numeric(15, 2))
    alertes_actives = Column(Integer, default=0)
    created_at = Column(DateTime(timezone=True), server_default=func.now())


class AlertPerformance(Base):
    """Performance alert model"""
    __tablename__ = "alertes_performance"
    
    id = Column(Integer, primary_key=True, index=True)
    type_alerte = Column(String(50))  # retard, incident, consommation, satisfaction
    gravite = Column(String(20))  # faible, moyenne, haute, critique
    description = Column(Text)
    concerne_type = Column(String(20))  # conducteur, camion, mission
    concerne_id = Column(Integer)
    valeur_actuelle = Column(Numeric)
    valeur_seuil = Column(Numeric)
    date_alerte = Column(DateTime(timezone=True), server_default=func.now())
    statut = Column(String(20), default="active")  # active, resolue, ignoree
    resolue_par = Column(Integer, ForeignKey('users.id'))
    date_resolution = Column(DateTime(timezone=True))
    resolution = Column(Text)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # Relationships
    resolueur = relationship("User", foreign_keys=[resolue_par])


class MaintenancePreventive(Base):
    """Preventive maintenance scheduling model"""
    __tablename__ = "maintenances_preventives"
    
    id = Column(Integer, primary_key=True, index=True)
    vehicule_id = Column(Integer, ForeignKey('vehicules.id'), nullable=False)
    type_maintenance = Column(String(50))  # vidange, filtre, pneumatique, general
    kilometrage_prevu = Column(Integer, nullable=False)
    date_prevue = Column(Date, nullable=False)
    date_effective = Column(Date)
    periodicite = Column(Integer)  # En jours/km
    statut = Column(String(20), default="planifie")  # planifie, realisee, reportee, annulee
    cout_estime = Column(Numeric)
    cout_reel = Column(Numeric)
    realise_par = Column(String(100))
    notes = Column(Text)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relationships
    vehicule = relationship("Vehicule")


# ============ DISPATCH INTELLIGENT ============

class PositionGPS(Base):
    """GPS tracking model - Real-time fleet tracking"""
    __tablename__ = "positions_gps"
    
    id = Column(Integer, primary_key=True, index=True)
    vehicule_id = Column(Integer, ForeignKey('vehicules.id'), nullable=False)
    conducteur_id = Column(Integer, ForeignKey('conducteurs.id'))
    latitude = Column(Numeric, nullable=False)
    longitude = Column(Numeric, nullable=False)
    altitude = Column(Numeric)
    vitesse = Column(Numeric, default=0)
    direction = Column(Numeric)  # En degrés 0-360
    horodatage = Column(DateTime(timezone=True), server_default=func.now())
    statut_moteur = Column(String(20))  # allume, eteint, demarre
    statut_vehicule = Column(String(20))  # en_mouvement, arrete, garage
    kilmetrage_actuel = Column(Integer)
    niveau_carburant = Column(Integer)  # Pourcentage
    niveau_huile = Column(Integer)  # Pourcentage
    temperature_moteur = Column(Numeric)
    code_zone = Column(String(50))  # Geofencing zone
    alerte = Column(Text)  # Zone exit, speeding, etc.
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # Relationships
    vehicule = relationship("Vehicule")


# ============ DISPATCH INTELLIGENT ============

class ZoneGeofencing(Base):
    """Geofencing zone model"""
    __tablename__ = "zones_geofencing"
    
    id = Column(Integer, primary_key=True, index=True)
    nom_zone = Column(String(100), nullable=False)
    type_zone = Column(String(50))  # client, danger, interdit, autorise
    description = Column(Text)
    latitude_centre = Column(Numeric, nullable=False)
    longitude_centre = Column(Numeric, nullable=False)
    rayon = Column(Numeric, nullable=False)  # En mètres
    ville = Column(String(50))
    pays = Column(String(50), default="Cameroun")
    alerte_entree = Column(Boolean, default=True)
    alerte_sortie = Column(Boolean, default=True)
    limite_vitesse = Column(Integer)  # km/h
    statut = Column(String(20), default="actif")
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())


class EvenementVehicule(Base):
    """Vehicle event model"""
    __tablename__ = "evenements_vehicule"
    
    id = Column(Integer, primary_key=True, index=True)
    vehicule_id = Column(Integer, ForeignKey('vehicules.id'), nullable=False)
    type_evenement = Column(String(50))  # demarrage, arret, ouverture_porte, fermeture_porte
    date_evenement = Column(DateTime(timezone=True), server_default=func.now())
    localisation = Column(String(200))
    operateur = Column(String(100))
    description = Column(Text)
    pieces_jointes = Column(Text)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # Relationships
    vehicule = relationship("Vehicule")


# ============ DISPATCH INTELLIGENT ============

