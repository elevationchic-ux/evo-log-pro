"""Modeles logistique-3pl (expansion approfondie generee).

9 entites de gestion, chacune scoped par company_id.
Convention d'honnetete : aucune valeur par defaut, NULL = "non enregistre".
"""
from sqlalchemy import (
    Column, Integer, String, Text, DateTime, Boolean, Float,
    ForeignKey, Date, Numeric, UniqueConstraint, Enum as SAEnum,
)
from sqlalchemy.sql import func
import enum

from app.core.database import Base


def _enum(cls):
    return SAEnum(cls, native_enum=False, create_constraint=False,
                  values_callable=lambda x: [e.value for e in x])


# ─── Enums ────────────────────────────────────────────────────────────────────

class TplDockAppointment_type_mouvement(str, enum.Enum):
    ENTREE = "entree"
    SORTIE = "sortie"


class TplDockAppointment_statut(str, enum.Enum):
    RESERVE = "reserve"
    CONFIRME = "confirme"
    EN_COURS = "en_cours"
    TERMINE = "termine"
    NO_SHOW = "no_show"
    ANNULE = "annule"


class TplLoadingPlan_statut(str, enum.Enum):
    BROUILLON = "brouillon"
    VALIDE = "valide"
    CHARGE = "charge"
    PARTI = "parti"
    ANNULE = "annule"


class TplShipmentManifest_statut(str, enum.Enum):
    OUVERT = "ouvert"
    CLOTURE = "cloture"
    TRANSFERT = "transfert"
    LIVRE = "livre"
    ANNULE = "annule"


class TplInventoryTransfer_statut(str, enum.Enum):
    DEMANDE = "demande"
    EXPEDIE = "expedie"
    EN_TRANSIT = "en_transit"
    RECU = "recu"
    ECART = "ecart"
    CLOTURE = "cloture"


class TplColdChainLog_statut(str, enum.Enum):
    CONFORME = "conforme"
    HORS_PLAGE = "hors_plage"
    RUPTURE = "rupture"
    VERIFIE = "verifie"


class TplReturnAuthorization_motif_retour(str, enum.Enum):
    CASSE = "casse"
    ERREUR_PREP = "erreur_prep"
    NON_CONFORME = "non_conforme"
    SURCOMMANDE = "surcommande"
    AUTRE = "autre"


class TplReturnAuthorization_decision(str, enum.Enum):
    ACCEPTE = "accepte"
    REFUSE = "refuse"
    REMBOURSE = "rembourse"
    REMPPLACE = "rempplace"


class TplReturnAuthorization_statut(str, enum.Enum):
    OUVERT = "ouvert"
    EN_ATTENTE = "en_attente"
    RECU = "recu"
    TRAITE = "traite"
    CLOTURE = "cloture"


class TplCarrierRate_statut(str, enum.Enum):
    ACTIF = "actif"
    BROUILLON = "brouillon"
    EXPIRE = "expire"
    GELE = "gele"


class TplOrderNode_code_jalon(str, enum.Enum):
    COMMANDE = "commande"
    PREPARATION = "preparation"
    ENLEVE = "enleve"
    TRANSIT = "transit"
    LIVRE = "livre"
    RETOUR = "retour"


class TplOrderNode_statut(str, enum.Enum):
    ATTEINT = "atteint"
    EN_RETARD = "en_retard"
    MANQUANT = "manquant"


class TplDamageClaim_type_avarie(str, enum.Enum):
    CASSE = "casse"
    PERTE = "perte"
    VOL = "vol"
    RETARD = "retard"
    MAUVAIS_ETAT = "mauvais_etat"


class TplDamageClaim_statut(str, enum.Enum):
    OUVERT = "ouvert"
    INSTRUCTION = "instruction"
    INDEMNISE = "indemnise"
    REJETE = "rejete"
    CLOTURE = "cloture"


# ─── Modeles ──────────────────────────────────────────────────────────────────

class TplDockAppointment(Base):
    """Rendez-vous quais (dock scheduling)."""
    __tablename__ = "tplb_dock_appointments"
    __table_args__ = (
        UniqueConstraint('company_id', 'reference', name='uix_tplb_dock_appointmen_company_reference'),
    )
    id = Column(Integer, primary_key=True, index=True)
    company_id = Column(Integer, ForeignKey('companies.id'), nullable=False, index=True)
    reference = Column(String(150), nullable=False, index=True)
    site = Column(String(150), nullable=True)
    numero_quai = Column(String(150), nullable=True)
    date_debut = Column(DateTime(timezone=True), nullable=True)
    date_fin = Column(DateTime(timezone=True), nullable=True)
    immatriculation = Column(String(150), nullable=True)
    type_mouvement = Column(String(150), nullable=True)
    statut = Column(String(150), nullable=True)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())


class TplLoadingPlan(Base):
    """Plans de chargement camion."""
    __tablename__ = "tplb_loading_plans"
    __table_args__ = (
        UniqueConstraint('company_id', 'reference', name='uix_tplb_loading_plans_company_reference'),
    )
    id = Column(Integer, primary_key=True, index=True)
    company_id = Column(Integer, ForeignKey('companies.id'), nullable=False, index=True)
    reference = Column(String(150), nullable=False, index=True)
    site = Column(String(150), nullable=True)
    numero_camion = Column(String(150), nullable=True)
    nb_colis = Column(Integer, nullable=True)
    poids_total_kg = Column(Integer, nullable=True)
    volume_m3 = Column(Integer, nullable=True)
    taux_remplissage_pct = Column(Integer, nullable=True)
    date_plan = Column(DateTime(timezone=True), nullable=True)
    statut = Column(String(150), nullable=True)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())


class TplShipmentManifest(Base):
    """Manifestes d' expedition."""
    __tablename__ = "tplb_shipment_manifests"
    __table_args__ = (
        UniqueConstraint('company_id', 'numero_manifeste', name='uix_tplb_shipment_manife_company_numero_manifest'),
    )
    id = Column(Integer, primary_key=True, index=True)
    company_id = Column(Integer, ForeignKey('companies.id'), nullable=False, index=True)
    numero_manifeste = Column(String(150), nullable=False, index=True)
    client = Column(String(150), nullable=True)
    site_depart = Column(String(150), nullable=True)
    site_arrivee = Column(String(150), nullable=True)
    nb_colis = Column(Integer, nullable=True)
    poids_total_kg = Column(Integer, nullable=True)
    date_emission = Column(Date, nullable=True)
    statut = Column(String(150), nullable=True)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())


class TplInventoryTransfer(Base):
    """Transferts inter-entrepots."""
    __tablename__ = "tplb_inventory_transfers"
    __table_args__ = (
        UniqueConstraint('company_id', 'reference', name='uix_tplb_inventory_trans_company_reference'),
    )
    id = Column(Integer, primary_key=True, index=True)
    company_id = Column(Integer, ForeignKey('companies.id'), nullable=False, index=True)
    reference = Column(String(150), nullable=False, index=True)
    site_source = Column(String(150), nullable=True)
    site_destinataire = Column(String(150), nullable=True)
    sku = Column(String(150), nullable=True)
    quantite_expediee = Column(Integer, nullable=True)
    quantite_recue = Column(Integer, nullable=True)
    date_transfert = Column(Date, nullable=True)
    statut = Column(String(150), nullable=True)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())


class TplColdChainLog(Base):
    """Journal chaine du froid."""
    __tablename__ = "tplb_cold_chain_logs"
    __table_args__ = (
        UniqueConstraint('company_id', 'reference', name='uix_tplb_cold_chain_logs_company_reference'),
    )
    id = Column(Integer, primary_key=True, index=True)
    company_id = Column(Integer, ForeignKey('companies.id'), nullable=False, index=True)
    reference = Column(String(150), nullable=False, index=True)
    site = Column(String(150), nullable=True)
    produit = Column(String(150), nullable=True)
    sonde = Column(String(150), nullable=True)
    temperature_c = Column(Numeric, nullable=True)
    plage_min_c = Column(Numeric, nullable=True)
    plage_max_c = Column(Numeric, nullable=True)
    date_releve = Column(DateTime(timezone=True), nullable=True)
    statut = Column(String(150), nullable=True)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())


class TplReturnAuthorization(Base):
    """Autorisations de retour (RMA)."""
    __tablename__ = "tplb_return_authorizations"
    __table_args__ = (
        UniqueConstraint('company_id', 'numero_rma', name='uix_tplb_return_authoriz_company_numero_rma'),
    )
    id = Column(Integer, primary_key=True, index=True)
    company_id = Column(Integer, ForeignKey('companies.id'), nullable=False, index=True)
    numero_rma = Column(String(150), nullable=False, index=True)
    client = Column(String(150), nullable=True)
    commande_originale = Column(String(150), nullable=True)
    motif_retour = Column(String(150), nullable=True)
    nb_unites = Column(Integer, nullable=True)
    date_demande = Column(Date, nullable=True)
    decision = Column(String(150), nullable=True)
    statut = Column(String(150), nullable=True)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())


class TplCarrierRate(Base):
    """Grille tarifaire transporteurs."""
    __tablename__ = "tplb_carrier_rates"
    __table_args__ = (
        UniqueConstraint('company_id', 'code_tarif', name='uix_tplb_carrier_rates_company_code_tarif'),
    )
    id = Column(Integer, primary_key=True, index=True)
    company_id = Column(Integer, ForeignKey('companies.id'), nullable=False, index=True)
    code_tarif = Column(String(150), nullable=False, index=True)
    transporteur = Column(String(150), nullable=True)
    zone = Column(String(150), nullable=True)
    poids_kg = Column(Integer, nullable=True)
    prix_base_xaf = Column(Integer, nullable=True)
    prix_par_kg_xaf = Column(Integer, nullable=True)
    validite_debut = Column(Date, nullable=True)
    validite_fin = Column(Date, nullable=True)
    statut = Column(String(150), nullable=True)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())


class TplOrderNode(Base):
    """Jalons de commande (track & trace)."""
    __tablename__ = "tplb_order_nodes"
    __table_args__ = (
        UniqueConstraint('company_id', 'reference', name='uix_tplb_order_nodes_company_reference'),
    )
    id = Column(Integer, primary_key=True, index=True)
    company_id = Column(Integer, ForeignKey('companies.id'), nullable=False, index=True)
    reference = Column(String(150), nullable=False, index=True)
    numero_commande = Column(String(150), nullable=True)
    code_jalon = Column(String(150), nullable=True)
    libelle_jalon = Column(String(150), nullable=True)
    date_horodatage = Column(DateTime(timezone=True), nullable=True)
    lieu = Column(String(150), nullable=True)
    operateur = Column(String(150), nullable=True)
    statut = Column(String(150), nullable=True)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())


class TplDamageClaim(Base):
    """Reclamations avaries 3PL."""
    __tablename__ = "tplb_damage_claims"
    __table_args__ = (
        UniqueConstraint('company_id', 'numero_dossier', name='uix_tplb_damage_claims_company_numero_dossier'),
    )
    id = Column(Integer, primary_key=True, index=True)
    company_id = Column(Integer, ForeignKey('companies.id'), nullable=False, index=True)
    numero_dossier = Column(String(150), nullable=False, index=True)
    client = Column(String(150), nullable=True)
    expedition_associee = Column(String(150), nullable=True)
    type_avarie = Column(String(150), nullable=True)
    montant_reclame_xaf = Column(Integer, nullable=True)
    date_ouverture = Column(Date, nullable=True)
    date_resolution = Column(Date, nullable=True)
    statut = Column(String(150), nullable=True)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

