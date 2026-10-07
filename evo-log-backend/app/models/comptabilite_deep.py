"""Modeles comptabilite-ohada (expansion approfondie generee).

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

class AssetRegistration_categorie(str, enum.Enum):
    INCORPORELLE = "incorporelle"
    CORPORELLE = "corporelle"
    FINANCIERE = "financiere"


class AssetRegistration_mode_amortissement(str, enum.Enum):
    LINEAIRE = "lineaire"
    DECLINANT = "declinant"
    PROGRESSIF = "progressif"


class AssetRegistration_statut(str, enum.Enum):
    ACTIF = "actif"
    CEDE = "cede"
    REFORME = "reforme"
    EN_COURS = "en_cours"


class DepreciationSchedule_statut(str, enum.Enum):
    PLANIFIE = "planifie"
    PASSER = "passer"
    ANNULE = "annule"


class Provision_type_provision(str, enum.Enum):
    RISQUE = "risque"
    DEPRECIATION = "depreciation"
    LITIGE = "litige"
    RESTRUCTURATION = "restructuration"


class Provision_statut(str, enum.Enum):
    DOTE = "dote"
    REPRIS = "repris"
    MAINTENU = "maintenu"


class BankReconciliation_statut(str, enum.Enum):
    OUVERT = "ouvert"
    EN_COURS = "en_cours"
    VALIDE = "valide"
    BLOQUE = "bloque"


class IntercompanyEntry_nature(str, enum.Enum):
    FACTURATION = "facturation"
    AVANCE = "avance"
    REMBoursement = "remboursement"
    RESTRUCTURATION = "restructuration"


class IntercompanyEntry_statut(str, enum.Enum):
    OUVERT = "ouvert"
    LETTRER = "lettrer"
    ELIMINE = "elimine"


class BudgetControl_statut(str, enum.Enum):
    NORMAL = "normal"
    ALERTE = "alerte"
    DEPASSE = "depasse"
    BLOQUE = "bloque"


class TaxDeclaration_type_declaration(str, enum.Enum):
    TVA = "tva"
    IS = "is"
    IRAM = "iram"
    IRGM = "irgm"
    PATENTE = "patente"
    TITRE_FC = "titre_fc"


class TaxDeclaration_statut(str, enum.Enum):
    BROUILLON = "brouillon"
    DEPOSE = "depose"
    PAYE = "paye"
    RECLAME = "reclame"


class PayrollEntry_statut(str, enum.Enum):
    BROUILLON = "brouillon"
    PASSER = "passer"
    VALIDE = "valide"


class TreasuryAccount_type_compte(str, enum.Enum):
    BANQUE = "banque"
    CAISSE = "caisse"
    REGIE = "regie"
    VIREMENT = "virement"


class TreasuryAccount_statut(str, enum.Enum):
    ACTIF = "actif"
    GELE = "gele"
    CLOTURE = "cloture"


class AnalyticalSection_type_section(str, enum.Enum):
    HOMEGENE = "homegene"
    ANALYTIQUE = "analytique"
    AUXILIAIRE = "auxiliaire"


# ─── Modeles ──────────────────────────────────────────────────────────────────

class AssetRegistration(Base):
    """Registre immobilisations."""
    __tablename__ = "asset_registrations"
    __table_args__ = (
        UniqueConstraint('company_id', 'numero_inventaire', name='uix_asset_registrations_company_numero_inventai'),
    )
    id = Column(Integer, primary_key=True, index=True)
    company_id = Column(Integer, ForeignKey('companies.id'), nullable=False, index=True)
    numero_inventaire = Column(String(150), nullable=False, index=True)
    designation = Column(String(150), nullable=True)
    categorie = Column(_enum(AssetRegistration_categorie), default=AssetRegistration_categorie.CORPORELLE)
    date_acquisition = Column(Date, nullable=True)
    valeur_acquisition_xaf = Column(Numeric, nullable=True)
    valeur_residuelle_xaf = Column(Numeric, nullable=True)
    duree_amortissement_an = Column(Integer, nullable=True)
    mode_amortissement = Column(_enum(AssetRegistration_mode_amortissement), default=AssetRegistration_mode_amortissement.LINEAIRE)
    compte_immo = Column(String(150), nullable=True)
    statut = Column(_enum(AssetRegistration_statut), default=AssetRegistration_statut.ACTIF)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())


class DepreciationSchedule(Base):
    """Plans d'amortissement."""
    __tablename__ = "depreciation_schedules"
    __table_args__ = (
        UniqueConstraint('company_id', 'reference', name='uix_depreciation_schedul_company_reference'),
    )
    id = Column(Integer, primary_key=True, index=True)
    company_id = Column(Integer, ForeignKey('companies.id'), nullable=False, index=True)
    reference = Column(String(150), nullable=False, index=True)
    asset_id = Column(Integer, nullable=True)
    exercice = Column(Integer, nullable=True)
    dotation_xaf = Column(Numeric, nullable=True)
    cumul_xaf = Column(Numeric, nullable=True)
    valeur_nette_xaf = Column(Numeric, nullable=True)
    date_ecriture = Column(Date, nullable=True)
    statut = Column(_enum(DepreciationSchedule_statut), default=DepreciationSchedule_statut.PLANIFIE)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())


class Provision(Base):
    """Dotations et reprises."""
    __tablename__ = "provisions"
    __table_args__ = (
        UniqueConstraint('company_id', 'reference', name='uix_provisions_company_reference'),
    )
    id = Column(Integer, primary_key=True, index=True)
    company_id = Column(Integer, ForeignKey('companies.id'), nullable=False, index=True)
    reference = Column(String(150), nullable=False, index=True)
    type_provision = Column(_enum(Provision_type_provision), default=Provision_type_provision.RISQUE)
    exercice = Column(Integer, nullable=True)
    montant_xaf = Column(Numeric, nullable=True)
    date_constat = Column(Date, nullable=True)
    compte_charge = Column(String(150), nullable=True)
    comporte_passif = Column(String(150), nullable=True)
    statut = Column(_enum(Provision_statut), default=Provision_statut.DOTE)
    motivation = Column(Text(2000), nullable=True)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())


class BankReconciliation(Base):
    """Rapprochement bancaire."""
    __tablename__ = "bank_reconciliations"
    __table_args__ = (
        UniqueConstraint('company_id', 'reference', name='uix_bank_reconciliations_company_reference'),
    )
    id = Column(Integer, primary_key=True, index=True)
    company_id = Column(Integer, ForeignKey('companies.id'), nullable=False, index=True)
    reference = Column(String(150), nullable=False, index=True)
    compte_banque = Column(String(150), nullable=True)
    periode_debut = Column(Date, nullable=True)
    periode_fin = Column(Date, nullable=True)
    solde_banque_xaf = Column(Numeric, nullable=True)
    solde_compta_xaf = Column(Numeric, nullable=True)
    ecart_xaf = Column(Numeric, nullable=True)
    nb_lignes_pointees = Column(Integer, nullable=True)
    statut = Column(_enum(BankReconciliation_statut), default=BankReconciliation_statut.OUVERT)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())


class IntercompanyEntry(Base):
    """Comptes inter-societes."""
    __tablename__ = "intercompany_entries"
    __table_args__ = (
        UniqueConstraint('company_id', 'reference', name='uix_intercompany_entries_company_reference'),
    )
    id = Column(Integer, primary_key=True, index=True)
    company_id = Column(Integer, ForeignKey('companies.id'), nullable=False, index=True)
    reference = Column(String(150), nullable=False, index=True)
    entite_emettrice = Column(String(150), nullable=True)
    entite_destinatrice = Column(String(150), nullable=True)
    date_ecriture = Column(Date, nullable=True)
    montant_xaf = Column(Numeric, nullable=True)
    nature = Column(_enum(IntercompanyEntry_nature), default=IntercompanyEntry_nature.FACTURATION)
    statut = Column(_enum(IntercompanyEntry_statut), default=IntercompanyEntry_statut.OUVERT)
    notes = Column(Text(2000), nullable=True)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())


class BudgetControl(Base):
    """Budget et controle budgetaire."""
    __tablename__ = "budget_controls"
    __table_args__ = (
        UniqueConstraint('company_id', 'reference', name='uix_budget_controls_company_reference'),
    )
    id = Column(Integer, primary_key=True, index=True)
    company_id = Column(Integer, ForeignKey('companies.id'), nullable=False, index=True)
    reference = Column(String(150), nullable=False, index=True)
    centre_cout = Column(String(150), nullable=True)
    exercice = Column(Integer, nullable=True)
    budget_prevu_xaf = Column(Numeric, nullable=True)
    consomme_xaf = Column(Numeric, nullable=True)
    engagement_xaf = Column(Numeric, nullable=True)
    ecart_pct = Column(Numeric, nullable=True)
    statut = Column(_enum(BudgetControl_statut), default=BudgetControl_statut.NORMAL)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())


class AuditPaf(Base):
    """Piste d'audit fiable."""
    __tablename__ = "audit_pafs"
    __table_args__ = (
        UniqueConstraint('company_id', 'hash_ligne', name='uix_audit_pafs_company_hash_ligne'),
    )
    id = Column(Integer, primary_key=True, index=True)
    company_id = Column(Integer, ForeignKey('companies.id'), nullable=False, index=True)
    hash_ligne = Column(String(150), nullable=False, index=True)
    date_ecriture = Column(Date, nullable=True)
    numero_piece = Column(String(150), nullable=True)
    compte = Column(String(150), nullable=True)
    libelle = Column(Text(2000), nullable=True)
    debit_xaf = Column(Numeric, nullable=True)
    credit_xaf = Column(Numeric, nullable=True)
    hash_precedent = Column(String(150), nullable=True)
    validite = Column(Boolean, nullable=True)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())


class TaxDeclaration(Base):
    """Declarations fiscales periodiques."""
    __tablename__ = "tax_declarations"
    __table_args__ = (
        UniqueConstraint('company_id', 'reference', name='uix_tax_declarations_company_reference'),
    )
    id = Column(Integer, primary_key=True, index=True)
    company_id = Column(Integer, ForeignKey('companies.id'), nullable=False, index=True)
    reference = Column(String(150), nullable=False, index=True)
    type_declaration = Column(_enum(TaxDeclaration_type_declaration), default=TaxDeclaration_type_declaration.TVA)
    periode_debut = Column(Date, nullable=True)
    periode_fin = Column(Date, nullable=True)
    base_imposable_xaf = Column(Numeric, nullable=True)
    droits_xaf = Column(Numeric, nullable=True)
    date_depot = Column(Date, nullable=True)
    statut = Column(_enum(TaxDeclaration_statut), default=TaxDeclaration_statut.BROUILLON)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())


class PayrollEntry(Base):
    """Ecritures de paie."""
    __tablename__ = "payroll_entries"
    __table_args__ = (
        UniqueConstraint('company_id', 'reference', name='uix_payroll_entries_company_reference'),
    )
    id = Column(Integer, primary_key=True, index=True)
    company_id = Column(Integer, ForeignKey('companies.id'), nullable=False, index=True)
    reference = Column(String(150), nullable=False, index=True)
    periode = Column(String(150), nullable=True)
    masse_salariale_xaf = Column(Numeric, nullable=True)
    charges_patronales_xaf = Column(Numeric, nullable=True)
    impot_retenu_xaf = Column(Numeric, nullable=True)
    net_paye_xaf = Column(Numeric, nullable=True)
    date_passage = Column(Date, nullable=True)
    statut = Column(_enum(PayrollEntry_statut), default=PayrollEntry_statut.BROUILLON)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())


class TreasuryAccount(Base):
    """Comptes de tresorerie."""
    __tablename__ = "treasury_accounts"
    __table_args__ = (
        UniqueConstraint('company_id', 'code_compte', name='uix_treasury_accounts_company_code_compte'),
    )
    id = Column(Integer, primary_key=True, index=True)
    company_id = Column(Integer, ForeignKey('companies.id'), nullable=False, index=True)
    code_compte = Column(String(150), nullable=False, index=True)
    intitule = Column(String(150), nullable=True)
    type_compte = Column(_enum(TreasuryAccount_type_compte), default=TreasuryAccount_type_compte.BANQUE)
    banque = Column(String(150), nullable=True)
    rib = Column(String(150), nullable=True)
    solde_actuel_xaf = Column(Numeric, nullable=True)
    devise = Column(String(150), nullable=True)
    responsable = Column(String(150), nullable=True)
    statut = Column(_enum(TreasuryAccount_statut), default=TreasuryAccount_statut.ACTIF)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())


class AnalyticalSection(Base):
    """Comptabilite analytique."""
    __tablename__ = "analytical_sections"
    __table_args__ = (
        UniqueConstraint('company_id', 'code_section', name='uix_analytical_sections_company_code_section'),
    )
    id = Column(Integer, primary_key=True, index=True)
    company_id = Column(Integer, ForeignKey('companies.id'), nullable=False, index=True)
    code_section = Column(String(150), nullable=False, index=True)
    intitule = Column(String(150), nullable=True)
    type_section = Column(_enum(AnalyticalSection_type_section), default=AnalyticalSection_type_section.ANALYTIQUE)
    cle_repartition = Column(String(150), nullable=True)
    unite_oeuvre = Column(String(150), nullable=True)
    cout_total_xaf = Column(Numeric, nullable=True)
    actif = Column(Boolean, nullable=True)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

