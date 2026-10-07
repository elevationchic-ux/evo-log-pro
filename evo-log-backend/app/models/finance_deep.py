"""Modeles finance-ohada (expansion approfondie generee).

12 entites de gestion, chacune scoped par company_id.
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

class MultiyearBudget_statut(str, enum.Enum):
    BROUILLON = "brouillon"
    SOUMIS = "soumis"
    ADOPTE = "adopte"
    REJETE = "rejete"


class CreditFacility_type_facilite(str, enum.Enum):
    CAISSE = "caisse"
    ESCOMPTE = "escompte"
    AFFACTURAGE = "affacturage"
    CREDIT_INVESTISSEMENT = "credit_investissement"


class CreditFacility_statut(str, enum.Enum):
    ACTIF = "actif"
    EXPIRE = "expire"
    RESILIE = "resilie"


class CashPool_statut(str, enum.Enum):
    ACTIF = "actif"
    SUSPENDU = "suspendu"
    DISSOUS = "dissous"


class FinancialInvestment_type_placement(str, enum.Enum):
    DAT = "dat"
    OAT = "oat"
    ACTION = "action"
    FOND = "fond"
    COMTE_TERME = "comte_terme"


class FinancialInvestment_statut(str, enum.Enum):
    DETENU = "detenu"
    CEDE = "cede"
    VENU = "venu"
    EXPIRE = "expire"


class FxExposure_instrument_couverture(str, enum.Enum):
    AUCUNE = "aucune"
    FORWARD = "forward"
    OPTION = "option"
    SWAP = "swap"


class FxExposure_statut(str, enum.Enum):
    OUVERT = "ouvert"
    COUVERT = "couvert"
    EXPIRE = "expire"


class PaymentSchedule_mode_reglement(str, enum.Enum):
    VIREMENT = "virement"
    CHEQUE = "cheque"
    ESPECES = "especes"
    LETTRE_CHANGE = "lettre_change"


class PaymentSchedule_statut(str, enum.Enum):
    PLANIFIE = "planifie"
    PAYE = "paye"
    RETARDE = "retarde"
    ANNULER = "annuler"


class ExpenseReport_statut(str, enum.Enum):
    SOUMIS = "soumis"
    INCOMPLET = "incomplet"
    VALIDE = "valide"
    REJETE = "rejete"
    PAYE = "paye"


class PettyCashBox_statut(str, enum.Enum):
    NORMAL = "normal"
    MANQUANT = "manquant"
    EXCEDENTAIRE = "excedentaire"
    SUSPENDU = "suspendu"


class BankGuarantee_type_garantie(str, enum.Enum):
    SOUMISSION = "soumission"
    BONNE_EXECUTION = "bonne_execution"
    AVANCE = "avance"
    VISITE = "visite"
    RESTITUTION_TVA = "restitution_tva"


class BankGuarantee_statut(str, enum.Enum):
    ACTIVE = "active"
    EXPIREE = "expiree"
    APPELEE = "appelee"


class LeaseContract_type_contrat(str, enum.Enum):
    LEASING = "leasing"
    LOCATION = "location"
    CREDIT_BAIL = "credit_bail"
    LOCATION_ACHAT = "location_achat"


class LeaseContract_statut(str, enum.Enum):
    ACTIF = "actif"
    FINI = "fini"
    RESILIE = "resilie"
    LEVE = "leve"


class TreasuryAlert_type_alerte(str, enum.Enum):
    SEUIL_BANCAIRE = "seuil_bancaire"
    BFR = "bfr"
    ECHEANCE_PAIEMENT = "echeance_paiement"
    DEPASSEMENT_BUDGET = "depassement_budget"


class TreasuryAlert_statut(str, enum.Enum):
    OUVERTE = "ouverte"
    PRISE_EN_CHARGE = "prise_en_charge"
    RESOLUE = "resolue"


# ─── Modeles ──────────────────────────────────────────────────────────────────

class MultiyearBudget(Base):
    """Budget pluriannuel."""
    __tablename__ = "multiyear_budgets"
    __table_args__ = (
        UniqueConstraint('company_id', 'reference', name='uix_multiyear_budgets_company_reference'),
    )
    id = Column(Integer, primary_key=True, index=True)
    company_id = Column(Integer, ForeignKey('companies.id'), nullable=False, index=True)
    reference = Column(String(150), nullable=False, index=True)
    exercice_debut = Column(Integer, nullable=True)
    exercice_fin = Column(Integer, nullable=True)
    montant_prevu_xaf = Column(Numeric, nullable=True)
    axes_strategiques = Column(Text(2000), nullable=True)
    vote_ba = Column(Boolean, nullable=True)
    statut = Column(_enum(MultiyearBudget_statut), default=MultiyearBudget_statut.BROUILLON)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())


class CreditFacility(Base):
    """Facilites de caisse et credits."""
    __tablename__ = "credit_facilities"
    __table_args__ = (
        UniqueConstraint('company_id', 'reference', name='uix_credit_facilities_company_reference'),
    )
    id = Column(Integer, primary_key=True, index=True)
    company_id = Column(Integer, ForeignKey('companies.id'), nullable=False, index=True)
    reference = Column(String(150), nullable=False, index=True)
    banque = Column(String(150), nullable=True)
    type_facilite = Column(_enum(CreditFacility_type_facilite), default=CreditFacility_type_facilite.CAISSE)
    montant_autorise_xaf = Column(Numeric, nullable=True)
    montant_utilise_xaf = Column(Numeric, nullable=True)
    taux_interet_pct = Column(Numeric, nullable=True)
    date_debut = Column(Date, nullable=True)
    date_fin = Column(Date, nullable=True)
    statut = Column(_enum(CreditFacility_statut), default=CreditFacility_statut.ACTIF)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())


class CashPool(Base):
    """Centralisation de tresorerie."""
    __tablename__ = "cash_pools"
    __table_args__ = (
        UniqueConstraint('company_id', 'reference', name='uix_cash_pools_company_reference'),
    )
    id = Column(Integer, primary_key=True, index=True)
    company_id = Column(Integer, ForeignKey('companies.id'), nullable=False, index=True)
    reference = Column(String(150), nullable=False, index=True)
    entite_pilote = Column(String(150), nullable=True)
    entites_participantes = Column(Text(2000), nullable=True)
    montant_pool_xaf = Column(Numeric, nullable=True)
    interet_intragroupe_pct = Column(Numeric, nullable=True)
    date_debut = Column(Date, nullable=True)
    statut = Column(_enum(CashPool_statut), default=CashPool_statut.ACTIF)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())


class FinancialInvestment(Base):
    """Investissements financiers."""
    __tablename__ = "financial_investments"
    __table_args__ = (
        UniqueConstraint('company_id', 'reference', name='uix_financial_investment_company_reference'),
    )
    id = Column(Integer, primary_key=True, index=True)
    company_id = Column(Integer, ForeignKey('companies.id'), nullable=False, index=True)
    reference = Column(String(150), nullable=False, index=True)
    type_placement = Column(_enum(FinancialInvestment_type_placement), default=FinancialInvestment_type_placement.DAT)
    institution = Column(String(150), nullable=True)
    montant_place_xaf = Column(Numeric, nullable=True)
    rendement_attendu_pct = Column(Numeric, nullable=True)
    date_debut = Column(Date, nullable=True)
    date_echeance = Column(Date, nullable=True)
    statut = Column(_enum(FinancialInvestment_statut), default=FinancialInvestment_statut.DETENU)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())


class FxExposure(Base):
    """Risque de change XAF/EUR/USD."""
    __tablename__ = "fx_exposures"
    __table_args__ = (
        UniqueConstraint('company_id', 'reference', name='uix_fx_exposures_company_reference'),
    )
    id = Column(Integer, primary_key=True, index=True)
    company_id = Column(Integer, ForeignKey('companies.id'), nullable=False, index=True)
    reference = Column(String(150), nullable=False, index=True)
    devise = Column(String(150), nullable=True)
    exposition_nette = Column(Numeric, nullable=True)
    valeur_couverte = Column(Numeric, nullable=True)
    instrument_couverture = Column(_enum(FxExposure_instrument_couverture), default=FxExposure_instrument_couverture.AUCUNE)
    taux_couverture_pct = Column(Numeric, nullable=True)
    date_echeance = Column(Date, nullable=True)
    statut = Column(_enum(FxExposure_statut), default=FxExposure_statut.OUVERT)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())


class PaymentSchedule(Base):
    """Echeancier reglements fournisseurs."""
    __tablename__ = "payment_schedules"
    __table_args__ = (
        UniqueConstraint('company_id', 'reference', name='uix_payment_schedules_company_reference'),
    )
    id = Column(Integer, primary_key=True, index=True)
    company_id = Column(Integer, ForeignKey('companies.id'), nullable=False, index=True)
    reference = Column(String(150), nullable=False, index=True)
    fournisseur_id = Column(Integer, nullable=True)
    facture_id = Column(Integer, nullable=True)
    montant_echeance_xaf = Column(Numeric, nullable=True)
    date_echeance = Column(Date, nullable=True)
    mode_reglement = Column(_enum(PaymentSchedule_mode_reglement), default=PaymentSchedule_mode_reglement.VIREMENT)
    statut = Column(_enum(PaymentSchedule_statut), default=PaymentSchedule_statut.PLANIFIE)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())


class ExpenseReport(Base):
    """Notes de frais."""
    __tablename__ = "expense_reports"
    __table_args__ = (
        UniqueConstraint('company_id', 'numero_note_frais', name='uix_expense_reports_company_numero_note_fra'),
    )
    id = Column(Integer, primary_key=True, index=True)
    company_id = Column(Integer, ForeignKey('companies.id'), nullable=False, index=True)
    numero_note_frais = Column(String(150), nullable=False, index=True)
    employe_id = Column(Integer, nullable=True)
    periode = Column(String(150), nullable=True)
    montant_total_xaf = Column(Numeric, nullable=True)
    nb_justificatifs = Column(Integer, nullable=True)
    date_depot = Column(Date, nullable=True)
    validateur = Column(String(150), nullable=True)
    statut = Column(_enum(ExpenseReport_statut), default=ExpenseReport_statut.SOUMIS)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())


class PettyCashBox(Base):
    """Regies d'avance."""
    __tablename__ = "petty_cash_boxes"
    __table_args__ = (
        UniqueConstraint('company_id', 'code_regie', name='uix_petty_cash_boxes_company_code_regie'),
    )
    id = Column(Integer, primary_key=True, index=True)
    company_id = Column(Integer, ForeignKey('companies.id'), nullable=False, index=True)
    code_regie = Column(String(150), nullable=False, index=True)
    lieu = Column(String(150), nullable=True)
    responsable = Column(String(150), nullable=True)
    fond_initial_xaf = Column(Numeric, nullable=True)
    solde_actuel_xaf = Column(Numeric, nullable=True)
    date_derniere_reconciliation = Column(Date, nullable=True)
    statut = Column(_enum(PettyCashBox_statut), default=PettyCashBox_statut.NORMAL)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())


class BankGuarantee(Base):
    """Garanties bancaires."""
    __tablename__ = "bank_guarantees"
    __table_args__ = (
        UniqueConstraint('company_id', 'reference', name='uix_bank_guarantees_company_reference'),
    )
    id = Column(Integer, primary_key=True, index=True)
    company_id = Column(Integer, ForeignKey('companies.id'), nullable=False, index=True)
    reference = Column(String(150), nullable=False, index=True)
    banque_emettrice = Column(String(150), nullable=True)
    beneficiaire = Column(String(150), nullable=True)
    type_garantie = Column(_enum(BankGuarantee_type_garantie), default=BankGuarantee_type_garantie.BONNE_EXECUTION)
    montant_xaf = Column(Numeric, nullable=True)
    commission_pct = Column(Numeric, nullable=True)
    date_debut = Column(Date, nullable=True)
    date_fin = Column(Date, nullable=True)
    statut = Column(_enum(BankGuarantee_statut), default=BankGuarantee_statut.ACTIVE)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())


class LeaseContract(Base):
    """Credit-leasing / contrats location."""
    __tablename__ = "lease_contracts"
    __table_args__ = (
        UniqueConstraint('company_id', 'reference', name='uix_lease_contracts_company_reference'),
    )
    id = Column(Integer, primary_key=True, index=True)
    company_id = Column(Integer, ForeignKey('companies.id'), nullable=False, index=True)
    reference = Column(String(150), nullable=False, index=True)
    type_contrat = Column(_enum(LeaseContract_type_contrat), default=LeaseContract_type_contrat.LEASING)
    bien_concerne = Column(String(150), nullable=True)
    loyer_mensuel_xaf = Column(Numeric, nullable=True)
    duree_mois = Column(Integer, nullable=True)
    valeur_residuelle_xaf = Column(Numeric, nullable=True)
    date_debut = Column(Date, nullable=True)
    statut = Column(_enum(LeaseContract_statut), default=LeaseContract_statut.ACTIF)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())


class CashForecast(Base):
    """Previsions de tresorerie."""
    __tablename__ = "cash_forecasts"
    __table_args__ = (
        UniqueConstraint('company_id', 'reference', name='uix_cash_forecasts_company_reference'),
    )
    id = Column(Integer, primary_key=True, index=True)
    company_id = Column(Integer, ForeignKey('companies.id'), nullable=False, index=True)
    reference = Column(String(150), nullable=False, index=True)
    horizon_mois = Column(Integer, nullable=True)
    entree_attendue_xaf = Column(Numeric, nullable=True)
    sortie_attendue_xaf = Column(Numeric, nullable=True)
    tresorerie_projete_xaf = Column(Numeric, nullable=True)
    hypothese = Column(Text(2000), nullable=True)
    date_revision = Column(Date, nullable=True)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())


class TreasuryAlert(Base):
    """Alertes tresorerie."""
    __tablename__ = "treasury_alerts"
    __table_args__ = (
        UniqueConstraint('company_id', 'reference', name='uix_treasury_alerts_company_reference'),
    )
    id = Column(Integer, primary_key=True, index=True)
    company_id = Column(Integer, ForeignKey('companies.id'), nullable=False, index=True)
    reference = Column(String(150), nullable=False, index=True)
    type_alerte = Column(_enum(TreasuryAlert_type_alerte), default=TreasuryAlert_type_alerte.SEUIL_BANCAIRE)
    seuil_declencheur = Column(Numeric, nullable=True)
    valeur_constatee = Column(Numeric, nullable=True)
    date_alerte = Column(DateTime(timezone=True), nullable=True)
    destinataire = Column(String(150), nullable=True)
    statut = Column(_enum(TreasuryAlert_statut), default=TreasuryAlert_statut.OUVERTE)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

