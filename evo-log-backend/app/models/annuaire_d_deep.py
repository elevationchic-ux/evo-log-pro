"""Modeles annuaire-prestataires (expansion approfondie generee).

17 entites de gestion, chacune scoped par company_id.
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

class ProvProfile_type_prestation(str, enum.Enum):
    TRANSPORT = "transport"
    MANUTENTION = "manutention"
    SECURITE = "securite"
    NETTOYAGE = "nettoyage"
    INGENIERIE = "ingenierie"


class ProvProfile_statut(str, enum.Enum):
    PROSPECT = "prospect"
    REFERENC = "referenc"
    ACTIF = "actif"
    SUSPENDU = "suspendu"
    SORTI = "sorti"


class ProvCategory_statut(str, enum.Enum):
    ACTIVE = "active"
    ARCHIVEE = "archivee"


class ProvCertification_statut(str, enum.Enum):
    VALIDE = "valide"
    EXAMEN = "examen"
    EXPIRE = "expire"
    REVOQUE = "revoque"


class ProvInsuranceAttestation_type_assurance(str, enum.Enum):
    RC_PRO = "rc_pro"
    MARCHANDISE_TRANSPORT = "marchandise_transport"
    CAUTION = "caution"
    FLOTTE = "flotte"


class ProvInsuranceAttestation_statut(str, enum.Enum):
    A_JOUR = "a_jour"
    A_RENOUVELER = "a_renouveler"
    EXPIREE = "expiree"


class ProvServiceContract_statut(str, enum.Enum):
    NEGOCIE = "negocie"
    SIGNE = "signe"
    EN_COURS = "en_cours"
    ECHOUE = "echoue"
    RESILIE = "resilie"


class ProvEvaluation_statut(str, enum.Enum):
    REUNIE = "reunie"
    EN_COURS = "en_cours"
    PUBLIEE = "publiee"
    CONTESTEE = "contestee"


class ProvIncident_gravite(str, enum.Enum):
    MINEUR = "mineur"
    MAJEUR = "majeur"
    CRITIQUE = "critique"


class ProvIncident_statut(str, enum.Enum):
    OUVERT = "ouvert"
    RECONNU = "reconnu"
    CORRIGE = "corrige"
    SANCTIONNE = "sanctionne"


class ProvAvailabilityCalendar_statut(str, enum.Enum):
    DISPONIBLE = "disponible"
    PARTIEL = "partiel"
    COMPLET = "complet"
    INJOIGNABLE = "injoignable"


class ProvPriceList_statut(str, enum.Enum):
    PROPOSEE = "proposee"
    HARMONISEE = "harmonisee"
    REJETEE = "rejetee"
    EXPIREE = "expiree"


class ProvContact_role(str, enum.Enum):
    COMMERCIAL = "commercial"
    EXPLOITATION = "exploitation"
    DIRECTION = "direction"
    FACTURATION = "facturation"


class ProvContact_statut(str, enum.Enum):
    ACTIF = "actif"
    ANCIEN = "ancien"
    A_VERIFIER = "a_verifier"


class ProvOnboarding_statut(str, enum.Enum):
    DEMARRE = "demarre"
    EN_COURS = "en_cours"
    BLOQUE = "bloque"
    REFERENC = "referenc"
    ABANDONNE = "abandonne"


class ProvReview_statut(str, enum.Enum):
    PUBLIE = "publie"
    MODERE = "modere"
    SIGNALE = "signale"


class ProvRfqRequest_statut(str, enum.Enum):
    OUVERTE = "ouverte"
    CLOTUREE = "cloturee"
    ATTRIBUEE = "attribuee"
    INFROME = "infrome"


class ProvIntervention_statut(str, enum.Enum):
    PLANIFIEE = "planifiee"
    EN_COURS = "en_cours"
    FAITE = "faite"
    VALIDEE = "validee"
    REFAIRE = "refaire"


class ProvComplianceDoc_type_piece(str, enum.Enum):
    REGISTRE_COMMERCE = "registre_commerce"
    ATTEST_FISCALE = "attest_fiscale"
    ATTEST_SOCIALE = "attest_sociale"
    AGREMENT = "agrement"


class ProvComplianceDoc_statut(str, enum.Enum):
    VALIDE = "valide"
    MANQUANT = "manquant"
    EXPIRE = "expire"
    EN_COURS = "en_cours"


class ProvBankDetail_statut(str, enum.Enum):
    ENREGISTRE = "enregistre"
    VERIFIE = "verifie"
    CHANGEMENT = "changement"
    REJETE = "rejete"


class ProvBlacklist_statut(str, enum.Enum):
    PROPOSEE = "proposee"
    ACTIVE = "active"
    LEVEE = "levee"
    PERPETUELLE = "perpetuelle"


# ─── Modeles ──────────────────────────────────────────────────────────────────

class ProvProfile(Base):
    """Fiches prestataires."""
    __tablename__ = "prov_profiles"
    __table_args__ = (
        UniqueConstraint('company_id', 'reference', name='uix_prov_profiles_company_reference'),
    )
    id = Column(Integer, primary_key=True, index=True)
    company_id = Column(Integer, ForeignKey('companies.id'), nullable=False, index=True)
    reference = Column(String(150), nullable=False, index=True)
    raison_sociale = Column(String(150), nullable=True)
    type_prestation = Column(String(150), nullable=True)
    zone = Column(String(150), nullable=True)
    contact = Column(String(150), nullable=True)
    statut = Column(String(150), nullable=True)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())


class ProvCategory(Base):
    """Categories de prestataires."""
    __tablename__ = "prov_categories"
    __table_args__ = (
        UniqueConstraint('company_id', 'reference', name='uix_prov_categories_company_reference'),
    )
    id = Column(Integer, primary_key=True, index=True)
    company_id = Column(Integer, ForeignKey('companies.id'), nullable=False, index=True)
    reference = Column(String(150), nullable=False, index=True)
    libelle = Column(String(150), nullable=True)
    exigence_documentaire = Column(Boolean, nullable=True)
    nb_prestataires = Column(Integer, nullable=True)
    statut = Column(String(150), nullable=True)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())


class ProvCertification(Base):
    """Certifications prestataires."""
    __tablename__ = "prov_certifications"
    __table_args__ = (
        UniqueConstraint('company_id', 'reference', name='uix_prov_certifications_company_reference'),
    )
    id = Column(Integer, primary_key=True, index=True)
    company_id = Column(Integer, ForeignKey('companies.id'), nullable=False, index=True)
    reference = Column(String(150), nullable=False, index=True)
    prestataire = Column(String(150), nullable=True)
    intitule = Column(String(150), nullable=True)
    emetteur = Column(String(150), nullable=True)
    expire_le = Column(Date, nullable=True)
    statut = Column(String(150), nullable=True)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())


class ProvInsuranceAttestation(Base):
    """Attestations d' assurance."""
    __tablename__ = "prov_insurance"
    __table_args__ = (
        UniqueConstraint('company_id', 'reference', name='uix_prov_insurance_company_reference'),
    )
    id = Column(Integer, primary_key=True, index=True)
    company_id = Column(Integer, ForeignKey('companies.id'), nullable=False, index=True)
    reference = Column(String(150), nullable=False, index=True)
    prestataire = Column(String(150), nullable=True)
    type_assurance = Column(String(150), nullable=True)
    montant_couvert = Column(Numeric, nullable=True)
    expire_le = Column(Date, nullable=True)
    statut = Column(String(150), nullable=True)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())


class ProvServiceContract(Base):
    """Contrats de prestation."""
    __tablename__ = "prov_contracts"
    __table_args__ = (
        UniqueConstraint('company_id', 'reference', name='uix_prov_contracts_company_reference'),
    )
    id = Column(Integer, primary_key=True, index=True)
    company_id = Column(Integer, ForeignKey('companies.id'), nullable=False, index=True)
    reference = Column(String(150), nullable=False, index=True)
    prestataire = Column(String(150), nullable=True)
    objet = Column(String(150), nullable=True)
    montant = Column(Numeric, nullable=True)
    echeance = Column(Date, nullable=True)
    statut = Column(String(150), nullable=True)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())


class ProvEvaluation(Base):
    """Evaluations de prestataires."""
    __tablename__ = "prov_evaluations"
    __table_args__ = (
        UniqueConstraint('company_id', 'reference', name='uix_prov_evaluations_company_reference'),
    )
    id = Column(Integer, primary_key=True, index=True)
    company_id = Column(Integer, ForeignKey('companies.id'), nullable=False, index=True)
    reference = Column(String(150), nullable=False, index=True)
    prestataire = Column(String(150), nullable=True)
    periode = Column(String(150), nullable=True)
    score = Column(Integer, nullable=True)
    evalueur = Column(String(150), nullable=True)
    statut = Column(String(150), nullable=True)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())


class ProvIncident(Base):
    """Incidents prestataires."""
    __tablename__ = "prov_incidents"
    __table_args__ = (
        UniqueConstraint('company_id', 'reference', name='uix_prov_incidents_company_reference'),
    )
    id = Column(Integer, primary_key=True, index=True)
    company_id = Column(Integer, ForeignKey('companies.id'), nullable=False, index=True)
    reference = Column(String(150), nullable=False, index=True)
    prestataire = Column(String(150), nullable=True)
    description = Column(Text(2000), nullable=True)
    gravite = Column(String(150), nullable=True)
    date = Column(DateTime(timezone=True), nullable=True)
    statut = Column(String(150), nullable=True)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())


class ProvAvailabilityCalendar(Base):
    """Calendriers de disponibilite."""
    __tablename__ = "prov_availability"
    __table_args__ = (
        UniqueConstraint('company_id', 'reference', name='uix_prov_availability_company_reference'),
    )
    id = Column(Integer, primary_key=True, index=True)
    company_id = Column(Integer, ForeignKey('companies.id'), nullable=False, index=True)
    reference = Column(String(150), nullable=False, index=True)
    prestataire = Column(String(150), nullable=True)
    semaine = Column(String(150), nullable=True)
    creneaux_libres = Column(Integer, nullable=True)
    statut = Column(String(150), nullable=True)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())


class ProvPriceList(Base):
    """Grilles tarifaires prestataires."""
    __tablename__ = "prov_price_lists"
    __table_args__ = (
        UniqueConstraint('company_id', 'reference', name='uix_prov_price_lists_company_reference'),
    )
    id = Column(Integer, primary_key=True, index=True)
    company_id = Column(Integer, ForeignKey('companies.id'), nullable=False, index=True)
    reference = Column(String(150), nullable=False, index=True)
    prestataire = Column(String(150), nullable=True)
    unite_prix = Column(Numeric, nullable=True)
    validite = Column(Date, nullable=True)
    statut = Column(String(150), nullable=True)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())


class ProvContact(Base):
    """Contacts prestataires."""
    __tablename__ = "prov_contacts"
    __table_args__ = (
        UniqueConstraint('company_id', 'reference', name='uix_prov_contacts_company_reference'),
    )
    id = Column(Integer, primary_key=True, index=True)
    company_id = Column(Integer, ForeignKey('companies.id'), nullable=False, index=True)
    reference = Column(String(150), nullable=False, index=True)
    prestataire = Column(String(150), nullable=True)
    nom = Column(String(150), nullable=True)
    role = Column(String(150), nullable=True)
    telephone = Column(String(150), nullable=True)
    statut = Column(String(150), nullable=True)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())


class ProvOnboarding(Base):
    """Onboarding prestataires."""
    __tablename__ = "prov_onboarding"
    __table_args__ = (
        UniqueConstraint('company_id', 'reference', name='uix_prov_onboarding_company_reference'),
    )
    id = Column(Integer, primary_key=True, index=True)
    company_id = Column(Integer, ForeignKey('companies.id'), nullable=False, index=True)
    reference = Column(String(150), nullable=False, index=True)
    prestataire = Column(String(150), nullable=True)
    etapes_faites = Column(Integer, nullable=True)
    etapes_total = Column(Integer, nullable=True)
    date = Column(Date, nullable=True)
    statut = Column(String(150), nullable=True)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())


class ProvReview(Base):
    """Avis sur prestataires."""
    __tablename__ = "prov_reviews"
    __table_args__ = (
        UniqueConstraint('company_id', 'reference', name='uix_prov_reviews_company_reference'),
    )
    id = Column(Integer, primary_key=True, index=True)
    company_id = Column(Integer, ForeignKey('companies.id'), nullable=False, index=True)
    reference = Column(String(150), nullable=False, index=True)
    prestataire = Column(String(150), nullable=True)
    commentaire = Column(Text(2000), nullable=True)
    nb_etoiles = Column(Integer, nullable=True)
    date = Column(Date, nullable=True)
    statut = Column(String(150), nullable=True)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())


class ProvRfqRequest(Base):
    """Demandes de devis."""
    __tablename__ = "prov_rfq"
    __table_args__ = (
        UniqueConstraint('company_id', 'reference', name='uix_prov_rfq_company_reference'),
    )
    id = Column(Integer, primary_key=True, index=True)
    company_id = Column(Integer, ForeignKey('companies.id'), nullable=False, index=True)
    reference = Column(String(150), nullable=False, index=True)
    objet = Column(String(150), nullable=True)
    nb_offres = Column(Integer, nullable=True)
    date_limite = Column(Date, nullable=True)
    statut = Column(String(150), nullable=True)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())


class ProvIntervention(Base):
    """Interventions prestataires."""
    __tablename__ = "prov_interventions"
    __table_args__ = (
        UniqueConstraint('company_id', 'reference', name='uix_prov_interventions_company_reference'),
    )
    id = Column(Integer, primary_key=True, index=True)
    company_id = Column(Integer, ForeignKey('companies.id'), nullable=False, index=True)
    reference = Column(String(150), nullable=False, index=True)
    prestataire = Column(String(150), nullable=True)
    site = Column(String(150), nullable=True)
    date = Column(DateTime(timezone=True), nullable=True)
    compte_rendu = Column(Text(2000), nullable=True)
    statut = Column(String(150), nullable=True)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())


class ProvComplianceDoc(Base):
    """Documents de conformite."""
    __tablename__ = "prov_compliance_docs"
    __table_args__ = (
        UniqueConstraint('company_id', 'reference', name='uix_prov_compliance_docs_company_reference'),
    )
    id = Column(Integer, primary_key=True, index=True)
    company_id = Column(Integer, ForeignKey('companies.id'), nullable=False, index=True)
    reference = Column(String(150), nullable=False, index=True)
    prestataire = Column(String(150), nullable=True)
    type_piece = Column(String(150), nullable=True)
    expire_le = Column(Date, nullable=True)
    statut = Column(String(150), nullable=True)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())


class ProvBankDetail(Base):
    """Coordonnees bancaires prestataires."""
    __tablename__ = "prov_bank_details"
    __table_args__ = (
        UniqueConstraint('company_id', 'reference', name='uix_prov_bank_details_company_reference'),
    )
    id = Column(Integer, primary_key=True, index=True)
    company_id = Column(Integer, ForeignKey('companies.id'), nullable=False, index=True)
    reference = Column(String(150), nullable=False, index=True)
    prestataire = Column(String(150), nullable=True)
    banque = Column(String(150), nullable=True)
    iban_verifie = Column(Boolean, nullable=True)
    date = Column(Date, nullable=True)
    statut = Column(String(150), nullable=True)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())


class ProvBlacklist(Base):
    """Exclusions de prestataires."""
    __tablename__ = "prov_blacklist"
    __table_args__ = (
        UniqueConstraint('company_id', 'reference', name='uix_prov_blacklist_company_reference'),
    )
    id = Column(Integer, primary_key=True, index=True)
    company_id = Column(Integer, ForeignKey('companies.id'), nullable=False, index=True)
    reference = Column(String(150), nullable=False, index=True)
    prestataire = Column(String(150), nullable=True)
    motif = Column(Text(2000), nullable=True)
    debut = Column(Date, nullable=True)
    fin_prevue = Column(Date, nullable=True)
    statut = Column(String(150), nullable=True)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

