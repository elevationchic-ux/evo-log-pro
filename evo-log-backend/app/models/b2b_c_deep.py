"""Modeles client-b2b (expansion approfondie generee).

5 entites de gestion, chacune scoped par company_id.
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

class B2bCContractAgreement_type_contrat(str, enum.Enum):
    CADRE = "cadre"
    PRESTATION = "prestation"
    TRANSPORT = "transport"
    MANUTENTION = "manutention"


class B2bCContractAgreement_statut(str, enum.Enum):
    NEGOCIATION = "negociation"
    SIGNE = "signe"
    EXECUTION = "execution"
    EXPIRE = "expire"
    RESILIE = "resilie"


class B2bCPriceList_devise(str, enum.Enum):
    XOF = "xof"
    EUR = "eur"
    USD = "usd"


class B2bCPriceList_statut(str, enum.Enum):
    BROUILLON = "brouillon"
    ACTIVE = "active"
    GELEE = "gelee"
    REMPLEE = "remplee"


class B2bCSalesOrder_statut(str, enum.Enum):
    NOUVELLE = "nouvelle"
    CONFIRME = "confirme"
    EN_PREPARATION = "en_preparation"
    EXPEDIEE = "expediee"
    LIVREE = "livree"
    ANNULEE = "annulee"


class B2bCCreditAccount_statut(str, enum.Enum):
    A_TEMPS = "a_temps"
    EN_RETARD = "en_retard"
    BLOQUE = "bloque"
    SUSPENDU = "suspendu"


class B2bCSupportTicket_categorie(str, enum.Enum):
    LIVRAISON = "livraison"
    FACTURATION = "facturation"
    QUALITE = "qualite"
    TECHNIQUE = "technique"


class B2bCSupportTicket_priorite(str, enum.Enum):
    BASSE = "basse"
    NORMALE = "normale"
    HAUTE = "haute"
    URGENTE = "urgente"


class B2bCSupportTicket_statut(str, enum.Enum):
    OUVERT = "ouvert"
    EN_COURS = "en_cours"
    RESOLU = "resolu"
    CLOTURE = "cloture"
    REOUVERT = "reouvert"


# ─── Modeles ──────────────────────────────────────────────────────────────────

class B2bCContractAgreement(Base):
    """Contrats-cadres clients."""
    __tablename__ = "b2bc_contracts"
    __table_args__ = (
        UniqueConstraint('company_id', 'reference', name='uix_b2bc_contracts_company_reference'),
    )
    id = Column(Integer, primary_key=True, index=True)
    company_id = Column(Integer, ForeignKey('companies.id'), nullable=False, index=True)
    reference = Column(String(150), nullable=False, index=True)
    client = Column(String(150), nullable=True)
    type_contrat = Column(String(150), nullable=True)
    date_debut = Column(Date, nullable=True)
    date_fin = Column(Date, nullable=True)
    valeur_annuelle = Column(Numeric, nullable=True)
    contact = Column(String(150), nullable=True)
    statut = Column(String(150), nullable=True)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())


class B2bCPriceList(Base):
    """Grilles tarifaires client."""
    __tablename__ = "b2bc_price_lists"
    __table_args__ = (
        UniqueConstraint('company_id', 'reference', name='uix_b2bc_price_lists_company_reference'),
    )
    id = Column(Integer, primary_key=True, index=True)
    company_id = Column(Integer, ForeignKey('companies.id'), nullable=False, index=True)
    reference = Column(String(150), nullable=False, index=True)
    client = Column(String(150), nullable=True)
    version = Column(String(150), nullable=True)
    devise = Column(String(150), nullable=True)
    date_debut_validite = Column(Date, nullable=True)
    date_fin_validite = Column(Date, nullable=True)
    remise_globale_pct = Column(Integer, nullable=True)
    statut = Column(String(150), nullable=True)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())


class B2bCSalesOrder(Base):
    """Commandes clients."""
    __tablename__ = "b2bc_sales_orders"
    __table_args__ = (
        UniqueConstraint('company_id', 'reference', name='uix_b2bc_sales_orders_company_reference'),
    )
    id = Column(Integer, primary_key=True, index=True)
    company_id = Column(Integer, ForeignKey('companies.id'), nullable=False, index=True)
    reference = Column(String(150), nullable=False, index=True)
    client = Column(String(150), nullable=True)
    date_commande = Column(Date, nullable=True)
    nb_lignes = Column(Integer, nullable=True)
    montant_total = Column(Numeric, nullable=True)
    date_livraison_souhaitee = Column(Date, nullable=True)
    contrat_ref = Column(String(150), nullable=True)
    statut = Column(String(150), nullable=True)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())


class B2bCCreditAccount(Base):
    """Encours clients."""
    __tablename__ = "b2bc_credit_accounts"
    __table_args__ = (
        UniqueConstraint('company_id', 'reference', name='uix_b2bc_credit_accounts_company_reference'),
    )
    id = Column(Integer, primary_key=True, index=True)
    company_id = Column(Integer, ForeignKey('companies.id'), nullable=False, index=True)
    reference = Column(String(150), nullable=False, index=True)
    client = Column(String(150), nullable=True)
    limite_credit = Column(Numeric, nullable=True)
    encours = Column(Numeric, nullable=True)
    delai_paiement_jours = Column(Integer, nullable=True)
    date_dernier_paiement = Column(Date, nullable=True)
    statut = Column(String(150), nullable=True)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())


class B2bCSupportTicket(Base):
    """Tickets support client."""
    __tablename__ = "b2bc_support_tickets"
    __table_args__ = (
        UniqueConstraint('company_id', 'reference', name='uix_b2bc_support_tickets_company_reference'),
    )
    id = Column(Integer, primary_key=True, index=True)
    company_id = Column(Integer, ForeignKey('companies.id'), nullable=False, index=True)
    reference = Column(String(150), nullable=False, index=True)
    client = Column(String(150), nullable=True)
    sujet = Column(String(150), nullable=True)
    categorie = Column(String(150), nullable=True)
    priorite = Column(String(150), nullable=True)
    date_ouverture = Column(DateTime(timezone=True), nullable=True)
    date_resolution = Column(DateTime(timezone=True), nullable=True)
    statut = Column(String(150), nullable=True)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

