"""Modeles client-b2b (expansion approfondie generee).

11 entites de gestion, chacune scoped par company_id.
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

class ClientOnboarding_statut(str, enum.Enum):
    SOUMIS = "soumis"
    INCOMPLET = "incomplet"
    VALIDE = "valide"
    REFUSE = "refuse"


class SlaContract_statut(str, enum.Enum):
    CONFORME = "conforme"
    ALERTE = "alerte"
    PENALISE = "penalise"
    EXCEDENT = "excedent"


class B2bContract_type_contrat(str, enum.Enum):
    CADRE = "cadre"
    PRESTATION = "prestation"
    LICENSE = "license"
    PARTENARIAT = "partenariat"


class B2bContract_statut(str, enum.Enum):
    ACTIF = "actif"
    RENEGOCIE = "renegocie"
    EXPIRE = "expire"
    RESILIE = "resilie"


class ClientCreditLimit_statut(str, enum.Enum):
    NORMAL = "normal"
    VIGIE = "vigie"
    BLOQUE = "bloque"


class B2bDocument_statut(str, enum.Enum):
    ENVOYE = "envoye"
    RECU = "recu"
    ACQUITE = "acquite"
    PERDU = "perdu"


class ServiceRequest_priorite(str, enum.Enum):
    BASSE = "basse"
    NORMALE = "normale"
    HAUTE = "haute"
    URGENTE = "urgente"


class ServiceRequest_statut(str, enum.Enum):
    OUVERT = "ouvert"
    EN_COURS = "en_cours"
    RESOLU = "resolu"
    CLOTURE = "cloture"


class PricingAgreement_statut(str, enum.Enum):
    ACTIF = "actif"
    EXPIRE = "expire"
    RENEGOCIE = "renegocie"


class ShipmentBooking_type_expedition(str, enum.Enum):
    IMPORT = "import"
    EXPORT = "export"
    TRANSBORD = "transbord"


class ShipmentBooking_statut(str, enum.Enum):
    DEMANDE = "demande"
    CONFIRME = "confirme"
    ANNULE = "annule"
    REALISE = "realise"


class ClientClaim_statut(str, enum.Enum):
    RECU = "recu"
    INSTRUCTION = "instruction"
    TRANSACTION = "transaction"
    JURIDIQUE = "juridique"
    CLOTURE = "cloture"


# ─── Modeles ──────────────────────────────────────────────────────────────────

class ClientOnboarding(Base):
    """Admission nouveau client."""
    __tablename__ = "client_onboardings"
    __table_args__ = (
        UniqueConstraint('company_id', 'reference', name='uix_client_onboardings_company_reference'),
    )
    id = Column(Integer, primary_key=True, index=True)
    company_id = Column(Integer, ForeignKey('companies.id'), nullable=False, index=True)
    reference = Column(String(150), nullable=False, index=True)
    raison_sociale = Column(String(150), nullable=True)
    niu = Column(String(150), nullable=True)
    rc = Column(String(150), nullable=True)
    contact_principal = Column(String(150), nullable=True)
    email = Column(String(150), nullable=True)
    telephone = Column(String(150), nullable=True)
    date_demande = Column(Date, nullable=True)
    statut = Column(_enum(ClientOnboarding_statut), default=ClientOnboarding_statut.SOUMIS)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())


class SlaContract(Base):
    """Niveau de service / penalisations."""
    __tablename__ = "sla_contracts"
    __table_args__ = (
        UniqueConstraint('company_id', 'reference', name='uix_sla_contracts_company_reference'),
    )
    id = Column(Integer, primary_key=True, index=True)
    company_id = Column(Integer, ForeignKey('companies.id'), nullable=False, index=True)
    reference = Column(String(150), nullable=False, index=True)
    client_id = Column(Integer, nullable=True)
    type_prestation = Column(String(150), nullable=True)
    engagement_valeur = Column(Numeric, nullable=True)
    taux_atteint_pct = Column(Numeric, nullable=True)
    penalite_xaf = Column(Numeric, nullable=True)
    periode = Column(String(150), nullable=True)
    statut = Column(_enum(SlaContract_statut), default=SlaContract_statut.CONFORME)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())


class B2bContract(Base):
    """Contrats cadres / avenants."""
    __tablename__ = "b2b_contracts"
    __table_args__ = (
        UniqueConstraint('company_id', 'numero_contrat', name='uix_b2b_contracts_company_numero_contrat'),
    )
    id = Column(Integer, primary_key=True, index=True)
    company_id = Column(Integer, ForeignKey('companies.id'), nullable=False, index=True)
    numero_contrat = Column(String(150), nullable=False, index=True)
    client_id = Column(Integer, nullable=True)
    type_contrat = Column(_enum(B2bContract_type_contrat), default=B2bContract_type_contrat.CADRE)
    date_debut = Column(Date, nullable=True)
    date_fin = Column(Date, nullable=True)
    montant_engage_xaf = Column(Numeric, nullable=True)
    nb_avenants = Column(Integer, nullable=True)
    statut = Column(_enum(B2bContract_statut), default=B2bContract_statut.ACTIF)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())


class SatisfactionSurvey(Base):
    """Enquetes satisfaction NPS."""
    __tablename__ = "satisfaction_surveys"
    __table_args__ = (
        UniqueConstraint('company_id', 'reference', name='uix_satisfaction_surveys_company_reference'),
    )
    id = Column(Integer, primary_key=True, index=True)
    company_id = Column(Integer, ForeignKey('companies.id'), nullable=False, index=True)
    reference = Column(String(150), nullable=False, index=True)
    client_id = Column(Integer, nullable=True)
    date_enquete = Column(Date, nullable=True)
    note_global = Column(Numeric, nullable=True)
    score_nps = Column(Integer, nullable=True)
    commentaires = Column(Text(2000), nullable=True)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())


class ClientCreditLimit(Base):
    """Plafonds de credit client."""
    __tablename__ = "client_credit_limits"
    __table_args__ = (
        UniqueConstraint('company_id', 'reference', name='uix_client_credit_limits_company_reference'),
    )
    id = Column(Integer, primary_key=True, index=True)
    company_id = Column(Integer, ForeignKey('companies.id'), nullable=False, index=True)
    reference = Column(String(150), nullable=False, index=True)
    client_id = Column(Integer, nullable=True)
    plafond_xaf = Column(Numeric, nullable=True)
    encours_actuel_xaf = Column(Numeric, nullable=True)
    delai_paiement_jours = Column(Integer, nullable=True)
    date_revision = Column(Date, nullable=True)
    statut = Column(_enum(ClientCreditLimit_statut), default=ClientCreditLimit_statut.NORMAL)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())


class B2bDocument(Base):
    """Echange documents contractuels."""
    __tablename__ = "b2b_documents"
    __table_args__ = (
        UniqueConstraint('company_id', 'reference', name='uix_b2b_documents_company_reference'),
    )
    id = Column(Integer, primary_key=True, index=True)
    company_id = Column(Integer, ForeignKey('companies.id'), nullable=False, index=True)
    reference = Column(String(150), nullable=False, index=True)
    client_id = Column(Integer, nullable=True)
    type_document = Column(String(150), nullable=True)
    nom_fichier = Column(String(150), nullable=True)
    date_envoi = Column(DateTime(timezone=True), nullable=True)
    date_reception = Column(DateTime(timezone=True), nullable=True)
    statut = Column(_enum(B2bDocument_statut), default=B2bDocument_statut.ENVOYE)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())


class ServiceRequest(Base):
    """Demandes de service client."""
    __tablename__ = "service_requests"
    __table_args__ = (
        UniqueConstraint('company_id', 'reference', name='uix_service_requests_company_reference'),
    )
    id = Column(Integer, primary_key=True, index=True)
    company_id = Column(Integer, ForeignKey('companies.id'), nullable=False, index=True)
    reference = Column(String(150), nullable=False, index=True)
    client_id = Column(Integer, nullable=True)
    type_demande = Column(String(150), nullable=True)
    description = Column(Text(2000), nullable=True)
    date_creation = Column(DateTime(timezone=True), nullable=True)
    date_echeance = Column(DateTime(timezone=True), nullable=True)
    priorite = Column(_enum(ServiceRequest_priorite), default=ServiceRequest_priorite.NORMALE)
    statut = Column(_enum(ServiceRequest_statut), default=ServiceRequest_statut.OUVERT)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())


class PricingAgreement(Base):
    """Accords tarifaires / remises."""
    __tablename__ = "pricing_agreements"
    __table_args__ = (
        UniqueConstraint('company_id', 'reference', name='uix_pricing_agreements_company_reference'),
    )
    id = Column(Integer, primary_key=True, index=True)
    company_id = Column(Integer, ForeignKey('companies.id'), nullable=False, index=True)
    reference = Column(String(150), nullable=False, index=True)
    client_id = Column(Integer, nullable=True)
    type_prestation = Column(String(150), nullable=True)
    remise_pct = Column(Numeric, nullable=True)
    palier_volume = Column(String(150), nullable=True)
    date_debut = Column(Date, nullable=True)
    date_fin = Column(Date, nullable=True)
    statut = Column(_enum(PricingAgreement_statut), default=PricingAgreement_statut.ACTIF)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())


class ShipmentBooking(Base):
    """Reservation expedition client."""
    __tablename__ = "shipment_bookings"
    __table_args__ = (
        UniqueConstraint('company_id', 'reference', name='uix_shipment_bookings_company_reference'),
    )
    id = Column(Integer, primary_key=True, index=True)
    company_id = Column(Integer, ForeignKey('companies.id'), nullable=False, index=True)
    reference = Column(String(150), nullable=False, index=True)
    client_id = Column(Integer, nullable=True)
    escale_id = Column(Integer, nullable=True)
    type_expedition = Column(_enum(ShipmentBooking_type_expedition), default=ShipmentBooking_type_expedition.IMPORT)
    date_reservation = Column(DateTime(timezone=True), nullable=True)
    date_prevue = Column(DateTime(timezone=True), nullable=True)
    conteneurs_prevus = Column(Integer, nullable=True)
    statut = Column(_enum(ShipmentBooking_statut), default=ShipmentBooking_statut.DEMANDE)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())


class ClientClaim(Base):
    """Reclamation / litige client."""
    __tablename__ = "client_claims"
    __table_args__ = (
        UniqueConstraint('company_id', 'reference', name='uix_client_claims_company_reference'),
    )
    id = Column(Integer, primary_key=True, index=True)
    company_id = Column(Integer, ForeignKey('companies.id'), nullable=False, index=True)
    reference = Column(String(150), nullable=False, index=True)
    client_id = Column(Integer, nullable=True)
    objet = Column(String(150), nullable=True)
    description = Column(Text(2000), nullable=True)
    date_reclamation = Column(Date, nullable=True)
    montant_reclame_xaf = Column(Numeric, nullable=True)
    statut = Column(_enum(ClientClaim_statut), default=ClientClaim_statut.RECU)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())


class AccountReport(Base):
    """Releves periodiques compte client."""
    __tablename__ = "account_reports"
    __table_args__ = (
        UniqueConstraint('company_id', 'reference', name='uix_account_reports_company_reference'),
    )
    id = Column(Integer, primary_key=True, index=True)
    company_id = Column(Integer, ForeignKey('companies.id'), nullable=False, index=True)
    reference = Column(String(150), nullable=False, index=True)
    client_id = Column(Integer, nullable=True)
    periode_debut = Column(Date, nullable=True)
    periode_fin = Column(Date, nullable=True)
    factures_emises_xaf = Column(Numeric, nullable=True)
    reglements_recus_xaf = Column(Numeric, nullable=True)
    solde_a_payer_xaf = Column(Numeric, nullable=True)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

