"""Modeles portail-commercial (expansion approfondie generee).

15 entites de gestion, chacune scoped par company_id.
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

class CommLead_source(str, enum.Enum):
    SALON = "salon"
    INBOUND = "inbound"
    PROSPECTION = "prospection"
    RECOMMANDATION = "recommandation"


class CommLead_statut(str, enum.Enum):
    NOUVEAU = "nouveau"
    QUALIFIE = "qualifie"
    TRANSFORME = "transforme"
    PERDU = "perdu"


class CommOpportunity_statut(str, enum.Enum):
    QUALIFIEE = "qualifiee"
    PROPOSITION = "proposition"
    NEGOCIATION = "negociation"
    GAGNEE = "gagnee"
    PERDUE = "perdue"


class CommQuote_statut(str, enum.Enum):
    BROUILLON = "brouillon"
    EMIS = "emis"
    ACCEPTE = "accepte"
    REFUSE = "refuse"
    EXPIRE = "expire"


class CommSalesOrder_statut(str, enum.Enum):
    ENREGISTREE = "enregistree"
    CONFIRME = "confirme"
    EN_PREPARATION = "en_preparation"
    LIVREE = "livree"
    ANNULEE = "annulee"


class CommCustomerVisit_statut(str, enum.Enum):
    PLANIFIE = "planifie"
    EFFECTUE = "effectue"
    REPORTE = "reporte"
    ANNULE = "annule"


class CommSampleRequest_statut(str, enum.Enum):
    DEMANDE = "demande"
    PREPARE = "prepare"
    EXPEDIE = "expedie"
    FEEDBACK = "feedback"
    REFUSE = "refuse"


class CommTender_statut(str, enum.Enum):
    IDENTIFIE = "identifie"
    EN_PREPARATION = "en_preparation"
    SOUMIS = "soumis"
    GAGNE = "gagne"
    PERDU = "perdu"


class CommContractRenewal_statut(str, enum.Enum):
    A_TRAITER = "a_traiter"
    NEGOCIE = "negocie"
    RENOUVELE = "renouvele"
    RESILIE = "resilie"


class CommPriceRequest_statut(str, enum.Enum):
    REÇUE = "reçue"
    INSTRUIT = "instruit"
    ACCEPTE = "accepte"
    REFUSE = "refuse"


class CommCreditRequest_statut(str, enum.Enum):
    SOUMIS = "soumis"
    INSTRUIT = "instruit"
    ACCORDE = "accorde"
    REFUSE = "refuse"
    EXPIRE = "expire"


class CommOrderModification_statut(str, enum.Enum):
    DEMANDE = "demande"
    APPLIQUE = "applique"
    REFUSE = "refuse"
    IMPACT_COUT = "impact_cout"


class CommCustomerComplaint_canal(str, enum.Enum):
    EMAIL = "email"
    TELEPHONE = "telephone"
    PORTAIL = "portail"
    VISITE = "visite"


class CommCustomerComplaint_statut(str, enum.Enum):
    OUVERTE = "ouverte"
    EN_COURS = "en_cours"
    RESOLUE = "resolue"
    ESCALADEE = "escaladee"


class CommUpsellRecord_statut(str, enum.Enum):
    IDENTIFIE = "identifie"
    PROPOSE = "propose"
    CONVERTI = "converti"
    PERDU = "perdu"


class CommCommissionStatement_statut(str, enum.Enum):
    CALCULE = "calcule"
    SOUMIS = "soumis"
    VALIDE = "valide"
    PAYE = "paye"
    CONTESTE = "conteste"


class CommPipelineReview_statut(str, enum.Enum):
    PLANIFIE = "planifie"
    FAITE = "faite"
    A_ACTION = "a_action"
    CLOTURE = "cloture"


# ─── Modeles ──────────────────────────────────────────────────────────────────

class CommLead(Base):
    """Pistes commerciales."""
    __tablename__ = "comm_leads"
    __table_args__ = (
        UniqueConstraint('company_id', 'reference', name='uix_comm_leads_company_reference'),
    )
    id = Column(Integer, primary_key=True, index=True)
    company_id = Column(Integer, ForeignKey('companies.id'), nullable=False, index=True)
    reference = Column(String(150), nullable=False, index=True)
    prospect = Column(String(150), nullable=True)
    source = Column(String(150), nullable=True)
    segment = Column(String(150), nullable=True)
    date = Column(Date, nullable=True)
    statut = Column(String(150), nullable=True)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())


class CommOpportunity(Base):
    """ opportunites."""
    __tablename__ = "comm_opportunities"
    __table_args__ = (
        UniqueConstraint('company_id', 'reference', name='uix_comm_opportunities_company_reference'),
    )
    id = Column(Integer, primary_key=True, index=True)
    company_id = Column(Integer, ForeignKey('companies.id'), nullable=False, index=True)
    reference = Column(String(150), nullable=False, index=True)
    client = Column(String(150), nullable=True)
    libelle = Column(String(150), nullable=True)
    montant_estime = Column(Numeric, nullable=True)
    cloture_prevue = Column(Date, nullable=True)
    statut = Column(String(150), nullable=True)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())


class CommQuote(Base):
    """Devis."""
    __tablename__ = "comm_quotes"
    __table_args__ = (
        UniqueConstraint('company_id', 'reference', name='uix_comm_quotes_company_reference'),
    )
    id = Column(Integer, primary_key=True, index=True)
    company_id = Column(Integer, ForeignKey('companies.id'), nullable=False, index=True)
    reference = Column(String(150), nullable=False, index=True)
    client = Column(String(150), nullable=True)
    montant = Column(Numeric, nullable=True)
    validite = Column(Date, nullable=True)
    date_emission = Column(Date, nullable=True)
    statut = Column(String(150), nullable=True)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())


class CommSalesOrder(Base):
    """Commandes clients."""
    __tablename__ = "comm_sales_orders"
    __table_args__ = (
        UniqueConstraint('company_id', 'reference', name='uix_comm_sales_orders_company_reference'),
    )
    id = Column(Integer, primary_key=True, index=True)
    company_id = Column(Integer, ForeignKey('companies.id'), nullable=False, index=True)
    reference = Column(String(150), nullable=False, index=True)
    client = Column(String(150), nullable=True)
    devis = Column(String(150), nullable=True)
    montant = Column(Numeric, nullable=True)
    date = Column(DateTime(timezone=True), nullable=True)
    statut = Column(String(150), nullable=True)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())


class CommCustomerVisit(Base):
    """Visites clients."""
    __tablename__ = "comm_customer_visits"
    __table_args__ = (
        UniqueConstraint('company_id', 'reference', name='uix_comm_customer_visits_company_reference'),
    )
    id = Column(Integer, primary_key=True, index=True)
    company_id = Column(Integer, ForeignKey('companies.id'), nullable=False, index=True)
    reference = Column(String(150), nullable=False, index=True)
    client = Column(String(150), nullable=True)
    date = Column(DateTime(timezone=True), nullable=True)
    interlocuteur = Column(String(150), nullable=True)
    compte_rendu = Column(Text(2000), nullable=True)
    statut = Column(String(150), nullable=True)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())


class CommSampleRequest(Base):
    """Demandes d' echantillons."""
    __tablename__ = "comm_samples"
    __table_args__ = (
        UniqueConstraint('company_id', 'reference', name='uix_comm_samples_company_reference'),
    )
    id = Column(Integer, primary_key=True, index=True)
    company_id = Column(Integer, ForeignKey('companies.id'), nullable=False, index=True)
    reference = Column(String(150), nullable=False, index=True)
    client = Column(String(150), nullable=True)
    produit = Column(String(150), nullable=True)
    quantite = Column(Integer, nullable=True)
    date = Column(Date, nullable=True)
    statut = Column(String(150), nullable=True)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())


class CommTender(Base):
    """Appels d' offres."""
    __tablename__ = "comm_tenders"
    __table_args__ = (
        UniqueConstraint('company_id', 'reference', name='uix_comm_tenders_company_reference'),
    )
    id = Column(Integer, primary_key=True, index=True)
    company_id = Column(Integer, ForeignKey('companies.id'), nullable=False, index=True)
    reference = Column(String(150), nullable=False, index=True)
    acheteur = Column(String(150), nullable=True)
    objet = Column(String(150), nullable=True)
    date_limite = Column(Date, nullable=True)
    montant_offre = Column(Numeric, nullable=True)
    statut = Column(String(150), nullable=True)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())


class CommContractRenewal(Base):
    """Renouvellements de contrat."""
    __tablename__ = "comm_contract_renewals"
    __table_args__ = (
        UniqueConstraint('company_id', 'reference', name='uix_comm_contract_renewa_company_reference'),
    )
    id = Column(Integer, primary_key=True, index=True)
    company_id = Column(Integer, ForeignKey('companies.id'), nullable=False, index=True)
    reference = Column(String(150), nullable=False, index=True)
    client = Column(String(150), nullable=True)
    contrat = Column(String(150), nullable=True)
    echeance = Column(Date, nullable=True)
    valeur = Column(Numeric, nullable=True)
    statut = Column(String(150), nullable=True)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())


class CommPriceRequest(Base):
    """Demandes de prix."""
    __tablename__ = "comm_price_requests"
    __table_args__ = (
        UniqueConstraint('company_id', 'reference', name='uix_comm_price_requests_company_reference'),
    )
    id = Column(Integer, primary_key=True, index=True)
    company_id = Column(Integer, ForeignKey('companies.id'), nullable=False, index=True)
    reference = Column(String(150), nullable=False, index=True)
    client = Column(String(150), nullable=True)
    produit = Column(String(150), nullable=True)
    remise = Column(Numeric, nullable=True)
    date = Column(Date, nullable=True)
    statut = Column(String(150), nullable=True)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())


class CommCreditRequest(Base):
    """Demandes d' encours client."""
    __tablename__ = "comm_credit_requests"
    __table_args__ = (
        UniqueConstraint('company_id', 'reference', name='uix_comm_credit_requests_company_reference'),
    )
    id = Column(Integer, primary_key=True, index=True)
    company_id = Column(Integer, ForeignKey('companies.id'), nullable=False, index=True)
    reference = Column(String(150), nullable=False, index=True)
    client = Column(String(150), nullable=True)
    encours_actuel = Column(Numeric, nullable=True)
    montant_souhaite = Column(Numeric, nullable=True)
    date = Column(Date, nullable=True)
    statut = Column(String(150), nullable=True)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())


class CommOrderModification(Base):
    """Modifications de commande."""
    __tablename__ = "comm_order_modifications"
    __table_args__ = (
        UniqueConstraint('company_id', 'reference', name='uix_comm_order_modificat_company_reference'),
    )
    id = Column(Integer, primary_key=True, index=True)
    company_id = Column(Integer, ForeignKey('companies.id'), nullable=False, index=True)
    reference = Column(String(150), nullable=False, index=True)
    commande = Column(String(150), nullable=True)
    changement = Column(Text(2000), nullable=True)
    date = Column(DateTime(timezone=True), nullable=True)
    statut = Column(String(150), nullable=True)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())


class CommCustomerComplaint(Base):
    """Reclamations clients."""
    __tablename__ = "comm_complaints"
    __table_args__ = (
        UniqueConstraint('company_id', 'reference', name='uix_comm_complaints_company_reference'),
    )
    id = Column(Integer, primary_key=True, index=True)
    company_id = Column(Integer, ForeignKey('companies.id'), nullable=False, index=True)
    reference = Column(String(150), nullable=False, index=True)
    client = Column(String(150), nullable=True)
    objet = Column(String(150), nullable=True)
    canal = Column(String(150), nullable=True)
    date = Column(DateTime(timezone=True), nullable=True)
    statut = Column(String(150), nullable=True)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())


class CommUpsellRecord(Base):
    """Actions de vente additionnelle."""
    __tablename__ = "comm_upsells"
    __table_args__ = (
        UniqueConstraint('company_id', 'reference', name='uix_comm_upsells_company_reference'),
    )
    id = Column(Integer, primary_key=True, index=True)
    company_id = Column(Integer, ForeignKey('companies.id'), nullable=False, index=True)
    reference = Column(String(150), nullable=False, index=True)
    client = Column(String(150), nullable=True)
    offre = Column(String(150), nullable=True)
    montant_potentiel = Column(Numeric, nullable=True)
    date = Column(Date, nullable=True)
    statut = Column(String(150), nullable=True)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())


class CommCommissionStatement(Base):
    """Etats de commission."""
    __tablename__ = "comm_commissions"
    __table_args__ = (
        UniqueConstraint('company_id', 'reference', name='uix_comm_commissions_company_reference'),
    )
    id = Column(Integer, primary_key=True, index=True)
    company_id = Column(Integer, ForeignKey('companies.id'), nullable=False, index=True)
    reference = Column(String(150), nullable=False, index=True)
    commercial = Column(String(150), nullable=True)
    periode = Column(String(150), nullable=True)
    base_vente = Column(Numeric, nullable=True)
    taux = Column(Numeric, nullable=True)
    statut = Column(String(150), nullable=True)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())


class CommPipelineReview(Base):
    """Revues de pipeline."""
    __tablename__ = "comm_pipeline_reviews"
    __table_args__ = (
        UniqueConstraint('company_id', 'reference', name='uix_comm_pipeline_review_company_reference'),
    )
    id = Column(Integer, primary_key=True, index=True)
    company_id = Column(Integer, ForeignKey('companies.id'), nullable=False, index=True)
    reference = Column(String(150), nullable=False, index=True)
    commercial = Column(String(150), nullable=True)
    nb_opportunites = Column(Integer, nullable=True)
    valeur_ponderee = Column(Numeric, nullable=True)
    date = Column(Date, nullable=True)
    statut = Column(String(150), nullable=True)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

