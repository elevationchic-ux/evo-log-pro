"""Modeles logistique-3pl (expansion approfondie generee).

10 entites de gestion, chacune scoped par company_id.
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

class TplContract_perimetre(str, enum.Enum):
    ENTREPOT = "entrepot"
    TRANSPORT = "transport"
    BOUT_BOUT = "bout_bout"
    CUSTOMS = "customs"
    FULL_3PL = "full_3pl"


class TplContract_statut(str, enum.Enum):
    BROUILLON = "brouillon"
    EN_VIGUEUR = "en_vigueur"
    RENEGOCIE = "renegocie"
    EXPIRE = "expire"
    RESILIE = "resilie"


class TplWarehouse_statut(str, enum.Enum):
    ACTIF = "actif"
    SATURATION = "saturation"
    TRAVAUX = "travaux"
    FERME = "ferme"


class TplCrossDock_statut(str, enum.Enum):
    PLANIFIE = "planifie"
    EN_COURS = "en_cours"
    TERMINE = "termine"
    RETARDE = "retarde"
    ANNULE = "annule"


class TplPickingLine_type_preparation(str, enum.Enum):
    PCE = "pce"
    COLIS = "colis"
    PAL = "pal"
    CROSSDOCK = "crossdock"


class TplPickingLine_statut(str, enum.Enum):
    EN_ATTENTE = "en_attente"
    EN_COURS = "en_cours"
    TERMINE = "termine"
    BLOQUE = "bloque"
    ANNULE = "annule"


class TplSlaKpi_kpi(str, enum.Enum):
    OTIF = "otif"
    TAUX_SERVICE = "taux_service"
    ERREUR_PREP = "erreur_prep"
    RETARD_LIVRAISON = "retard_livraison"
    CASSE = "casse"
    AUTRE = "autre"


class TplSlaKpi_statut(str, enum.Enum):
    CONFORME = "conforme"
    SOUS_SEUIL = "sous_seuil"
    AU_DESSUS = "au_dessus"
    LITIGE = "litige"


class TplInvoice_statut(str, enum.Enum):
    BROUILLON = "brouillon"
    EMISE = "emise"
    ENVOYEE = "envoyee"
    PAYEE = "payee"
    REJETEE = "rejetee"


class TplInventoryValuation_statut(str, enum.Enum):
    PLANIFIE = "planifie"
    EN_COURS = "en_cours"
    CLOTURE = "cloture"
    EXPERTISE = "expertise"
    VALIDE = "valide"


class TplSubProvider_type_prestation(str, enum.Enum):
    TRANSPORT = "transport"
    MANUTENTION = "manutention"
    STOCKAGE = "stockage"
    CUSTOMS = "customs"
    SECURITE = "securite"
    NETTOIEMENT = "nettoiement"


class TplSubProvider_statut(str, enum.Enum):
    ACTIF = "actif"
    SUSPENDU = "suspendu"
    NOIR = "noir"
    SORTI = "sorti"


class TplReverseOperation_type_operation(str, enum.Enum):
    RETOUR_STANDARD = "retour_standard"
    SAV_REPARATION = "sav_reparation"
    RECONDITIONNEMENT = "reconditionnement"
    RECYCLAGE = "recyclage"
    DESTRUCTION = "destruction"


class TplReverseOperation_statut(str, enum.Enum):
    PLANIFIE = "planifie"
    EN_COURS = "en_cours"
    TERMINE = "termine"
    BLOQUE = "bloque"


class TplControlTower_statut(str, enum.Enum):
    EN_MARCHE = "en_marche"
    DEGRADE = "degrade"
    HORS_LIGNE = "hors_ligne"


# ─── Modeles ──────────────────────────────────────────────────────────────────

class TplContract(Base):
    """Contrats cadres 3PL."""
    __tablename__ = "tpl_contracts"
    __table_args__ = (
        UniqueConstraint('company_id', 'numero_contrat', name='uix_tpl_contracts_company_numero_contrat'),
    )
    id = Column(Integer, primary_key=True, index=True)
    company_id = Column(Integer, ForeignKey('companies.id'), nullable=False, index=True)
    numero_contrat = Column(String(150), nullable=False, index=True)
    client = Column(String(150), nullable=True)
    perimetre = Column(String(150), nullable=True)
    sites_couverts = Column(Text(2000), nullable=True)
    date_debut = Column(Date, nullable=True)
    date_fin = Column(Date, nullable=True)
    valeur_annuelle_xaf = Column(Integer, nullable=True)
    statut = Column(String(150), nullable=True)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())


class TplWarehouse(Base):
    """Entrepots sous contrat."""
    __tablename__ = "tpl_warehouses"
    __table_args__ = (
        UniqueConstraint('company_id', 'code_site', name='uix_tpl_warehouses_company_code_site'),
    )
    id = Column(Integer, primary_key=True, index=True)
    company_id = Column(Integer, ForeignKey('companies.id'), nullable=False, index=True)
    code_site = Column(String(150), nullable=False, index=True)
    nom = Column(String(150), nullable=True)
    localisation = Column(String(150), nullable=True)
    surface_m2 = Column(Integer, nullable=True)
    capacite_palettes = Column(Integer, nullable=True)
    zones_froides = Column(Boolean, nullable=True)
    contract_associe = Column(String(150), nullable=True)
    statut = Column(String(150), nullable=True)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())


class TplCrossDock(Base):
    """Plans cross-dock."""
    __tablename__ = "tpl_crossdocks"
    __table_args__ = (
        UniqueConstraint('company_id', 'reference', name='uix_tpl_crossdocks_company_reference'),
    )
    id = Column(Integer, primary_key=True, index=True)
    company_id = Column(Integer, ForeignKey('companies.id'), nullable=False, index=True)
    reference = Column(String(150), nullable=False, index=True)
    site = Column(String(150), nullable=True)
    date_operation = Column(DateTime(timezone=True), nullable=True)
    nb_entrees = Column(Integer, nullable=True)
    nb_sorties = Column(Integer, nullable=True)
    duree_foresee_min = Column(Integer, nullable=True)
    statut = Column(String(150), nullable=True)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())


class TplPickingLine(Base):
    """Lignes de preparation."""
    __tablename__ = "tpl_picking_lines"
    __table_args__ = (
        UniqueConstraint('company_id', 'reference', name='uix_tpl_picking_lines_company_reference'),
    )
    id = Column(Integer, primary_key=True, index=True)
    company_id = Column(Integer, ForeignKey('companies.id'), nullable=False, index=True)
    reference = Column(String(150), nullable=False, index=True)
    site = Column(String(150), nullable=True)
    client = Column(String(150), nullable=True)
    type_preparation = Column(String(150), nullable=True)
    nb_lignes = Column(Integer, nullable=True)
    nb_colis = Column(Integer, nullable=True)
    operateur = Column(String(150), nullable=True)
    date_debut = Column(DateTime(timezone=True), nullable=True)
    date_fin = Column(DateTime(timezone=True), nullable=True)
    statut = Column(String(150), nullable=True)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())


class TplSlaKpi(Base):
    """KPI / SLA contractuels."""
    __tablename__ = "tpl_sla_kpis"
    __table_args__ = (
        UniqueConstraint('company_id', 'reference', name='uix_tpl_sla_kpis_company_reference'),
    )
    id = Column(Integer, primary_key=True, index=True)
    company_id = Column(Integer, ForeignKey('companies.id'), nullable=False, index=True)
    reference = Column(String(150), nullable=False, index=True)
    contrat_associe = Column(String(150), nullable=True)
    periode = Column(String(150), nullable=True)
    kpi = Column(String(150), nullable=True)
    valeur_cible = Column(String(150), nullable=True)
    valeur_reelle = Column(String(150), nullable=True)
    penalite_appliquee_xaf = Column(Integer, nullable=True)
    statut = Column(String(150), nullable=True)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())


class TplInvoice(Base):
    """Facturation 3PL."""
    __tablename__ = "tpl_invoices"
    __table_args__ = (
        UniqueConstraint('company_id', 'numero_facture', name='uix_tpl_invoices_company_numero_facture'),
    )
    id = Column(Integer, primary_key=True, index=True)
    company_id = Column(Integer, ForeignKey('companies.id'), nullable=False, index=True)
    numero_facture = Column(String(150), nullable=False, index=True)
    client = Column(String(150), nullable=True)
    periode = Column(String(150), nullable=True)
    montant_ht_xaf = Column(Integer, nullable=True)
    tva_xaf = Column(Integer, nullable=True)
    total_ttc_xaf = Column(Integer, nullable=True)
    date_emission = Column(Date, nullable=True)
    statut = Column(String(150), nullable=True)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())


class TplInventoryValuation(Base):
    """Valorisation stock client."""
    __tablename__ = "tpl_inventory_valuations"
    __table_args__ = (
        UniqueConstraint('company_id', 'reference', name='uix_tpl_inventory_valuat_company_reference'),
    )
    id = Column(Integer, primary_key=True, index=True)
    company_id = Column(Integer, ForeignKey('companies.id'), nullable=False, index=True)
    reference = Column(String(150), nullable=False, index=True)
    site = Column(String(150), nullable=True)
    client = Column(String(150), nullable=True)
    date_inventaire = Column(Date, nullable=True)
    valeur_theorique_xaf = Column(Integer, nullable=True)
    valeur_physique_xaf = Column(Integer, nullable=True)
    ecart_pct = Column(Integer, nullable=True)
    statut = Column(String(150), nullable=True)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())


class TplSubProvider(Base):
    """Sous-traitants secondaires."""
    __tablename__ = "tpl_sub_providers"
    __table_args__ = (
        UniqueConstraint('company_id', 'code_fournisseur', name='uix_tpl_sub_providers_company_code_fournisseu'),
    )
    id = Column(Integer, primary_key=True, index=True)
    company_id = Column(Integer, ForeignKey('companies.id'), nullable=False, index=True)
    code_fournisseur = Column(String(150), nullable=False, index=True)
    raison_sociale = Column(String(150), nullable=True)
    type_prestation = Column(String(150), nullable=True)
    zone_couverte = Column(String(150), nullable=True)
    date_debut_contrat = Column(Date, nullable=True)
    date_audit_precedent = Column(Date, nullable=True)
    note_qualite = Column(String(150), nullable=True)
    statut = Column(String(150), nullable=True)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())


class TplReverseOperation(Base):
    """Logistique retour / SAV."""
    __tablename__ = "tpl_reverse_ops"
    __table_args__ = (
        UniqueConstraint('company_id', 'reference', name='uix_tpl_reverse_ops_company_reference'),
    )
    id = Column(Integer, primary_key=True, index=True)
    company_id = Column(Integer, ForeignKey('companies.id'), nullable=False, index=True)
    reference = Column(String(150), nullable=False, index=True)
    client = Column(String(150), nullable=True)
    type_operation = Column(String(150), nullable=True)
    nb_unites = Column(Integer, nullable=True)
    site_prise_en_charge = Column(String(150), nullable=True)
    date_prise_en_charge = Column(Date, nullable=True)
    statut = Column(String(150), nullable=True)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())


class TplControlTower(Base):
    """Tour de controle multi-flux."""
    __tablename__ = "tpl_control_towers"
    __table_args__ = (
        UniqueConstraint('company_id', 'reference', name='uix_tpl_control_towers_company_reference'),
    )
    id = Column(Integer, primary_key=True, index=True)
    company_id = Column(Integer, ForeignKey('companies.id'), nullable=False, index=True)
    reference = Column(String(150), nullable=False, index=True)
    client = Column(String(150), nullable=True)
    date_horodatage = Column(DateTime(timezone=True), nullable=True)
    nombre_alertes = Column(Integer, nullable=True)
    nombre_incidents = Column(Integer, nullable=True)
    taux_service_pct = Column(Integer, nullable=True)
    operateur_tour = Column(String(150), nullable=True)
    statut = Column(String(150), nullable=True)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

