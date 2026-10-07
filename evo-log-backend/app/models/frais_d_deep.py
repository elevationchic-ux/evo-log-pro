"""Modeles portail-frais (expansion approfondie generee).

19 entites de gestion, chacune scoped par company_id.
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

class FraExpenseReport_statut(str, enum.Enum):
    BROUILLON = "brouillon"
    SOUMISE = "soumise"
    EN_COURS = "en_cours"
    APPROUVEE = "approuvee"
    REJETEE = "rejetee"


class FraExpenseReceipt_statut(str, enum.Enum):
    JOINT = "joint"
    LISIBLE = "lisible"
    ILISIBLE = "ilisible"
    DUPLIQUET = "dupliquet"


class FraExpenseAdvance_statut(str, enum.Enum):
    DEMANDEE = "demandee"
    VERSEE = "versee"
    JUSTIFIEE = "justifiee"
    REMBOURSEE = "remboursee"
    SOLDE = "solde"


class FraPerDiemClaim_statut(str, enum.Enum):
    DEMANDEE = "demandee"
    CALCULEE = "calculee"
    APPROUVEE = "approuvee"
    PAYEE = "payee"


class FraMileageClaim_statut(str, enum.Enum):
    DECLARE = "declare"
    VERIFIE = "verifie"
    APPROUVE = "approuve"
    REJETE = "rejete"


class FraMealExpense_statut(str, enum.Enum):
    DECLARE = "declare"
    JUSTIFIE = "justifie"
    APPROUVE = "approuve"
    PLAFOND_DEPASSE = "plafond_depasse"


class FraTravelBooking_mode(str, enum.Enum):
    AVION = "avion"
    TRAIN = "train"
    BUS = "bus"
    LOCATION = "location"


class FraTravelBooking_statut(str, enum.Enum):
    DEMANDEE = "demandee"
    RESERVEE = "reservee"
    ANNULEE = "annulee"
    EFFECTUE = "effectue"


class FraHotelStay_statut(str, enum.Enum):
    RESERVE = "reserve"
    EN_COURS = "en_cours"
    FACTURE = "facture"
    REMBOURSE = "rembourse"
    ANNULE = "annule"


class FraTransportExpense_type(str, enum.Enum):
    TAXI = "taxi"
    VTC = "vtc"
    PEAGE = "peage"
    METRO = "metro"
    CARBURANT = "carburant"


class FraTransportExpense_statut(str, enum.Enum):
    DECLARE = "declare"
    JUSTIFIE = "justifie"
    APPROUVE = "approuve"
    REJETE = "rejete"


class FraClientEntertainment_statut(str, enum.Enum):
    PLANIFIEE = "planifiee"
    ENGAGEE = "engagee"
    APPROUVEE = "approuvee"
    REJETEE = "rejetee"


class FraConferenceFee_statut(str, enum.Enum):
    DEMANDE = "demande"
    INSCIT = "inscit"
    FACTURE = "facture"
    REMBOURSE = "rembourse"


class FraOfficeSupply_statut(str, enum.Enum):
    DEMANDE = "demande"
    COMMANDE = "commande"
    RECU = "recu"
    PAYE = "paye"


class FraCardTransaction_statut(str, enum.Enum):
    DEBIT = "debit"
    JUSTIFIE = "justifie"
    RAPPROCHE = "rapproche"
    CONTESTE = "conteste"


class FraCurrencyConversion_statut(str, enum.Enum):
    A_CONVERTIR = "a_convertir"
    CONVERTI = "converti"
    VALIDE = "valide"
    Ecart_TAU = "ecart_tau"


class FraExpenseApproval_statut(str, enum.Enum):
    EN_ATTENTE = "en_attente"
    APPROUVE = "approuve"
    REJETE = "rejete"
    RETOUR = "retour"


class FraExpenseDispute_statut(str, enum.Enum):
    OUVERT = "ouvert"
    EXAMINE = "examine"
    RESOLU = "resolu"
    MAINTENU = "maintenu"


class FraVatRecovery_statut(str, enum.Enum):
    A_VERIFIER = "a_verifier"
    RECUPERABLE = "recuperable"
    NON_RECUPERABLE = "non_recuperable"
    INTEGRE = "integre"


class FraExpenseBudgetTracking_statut(str, enum.Enum):
    NOMINAL = "nominal"
    TENDU = "tendu"
    DEPASSE = "depasse"
    GELE = "gele"


class FraExpenseCategory_statut(str, enum.Enum):
    ACTIVE = "active"
    SUSPENDUE = "suspendue"
    ARCHIVEE = "archivee"


# ─── Modeles ──────────────────────────────────────────────────────────────────

class FraExpenseReport(Base):
    """Notes de frais."""
    __tablename__ = "fra_expense_reports"
    __table_args__ = (
        UniqueConstraint('company_id', 'reference', name='uix_fra_expense_reports_company_reference'),
    )
    id = Column(Integer, primary_key=True, index=True)
    company_id = Column(Integer, ForeignKey('companies.id'), nullable=False, index=True)
    reference = Column(String(150), nullable=False, index=True)
    collaborateur = Column(String(150), nullable=True)
    periode = Column(String(150), nullable=True)
    total = Column(Numeric, nullable=True)
    nb_justificatifs = Column(Integer, nullable=True)
    statut = Column(String(150), nullable=True)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())


class FraExpenseReceipt(Base):
    """Justificatifs de frais."""
    __tablename__ = "fra_expense_receipts"
    __table_args__ = (
        UniqueConstraint('company_id', 'reference', name='uix_fra_expense_receipts_company_reference'),
    )
    id = Column(Integer, primary_key=True, index=True)
    company_id = Column(Integer, ForeignKey('companies.id'), nullable=False, index=True)
    reference = Column(String(150), nullable=False, index=True)
    note_frais = Column(String(150), nullable=True)
    fournisseur = Column(String(150), nullable=True)
    montant = Column(Numeric, nullable=True)
    date = Column(Date, nullable=True)
    statut = Column(String(150), nullable=True)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())


class FraExpenseAdvance(Base):
    """Avances de frais."""
    __tablename__ = "fra_expense_advances"
    __table_args__ = (
        UniqueConstraint('company_id', 'reference', name='uix_fra_expense_advances_company_reference'),
    )
    id = Column(Integer, primary_key=True, index=True)
    company_id = Column(Integer, ForeignKey('companies.id'), nullable=False, index=True)
    reference = Column(String(150), nullable=False, index=True)
    collaborateur = Column(String(150), nullable=True)
    montant = Column(Numeric, nullable=True)
    motif = Column(String(150), nullable=True)
    date = Column(Date, nullable=True)
    statut = Column(String(150), nullable=True)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())


class FraPerDiemClaim(Base):
    """Indemnites forfaitaires."""
    __tablename__ = "fra_per_diem"
    __table_args__ = (
        UniqueConstraint('company_id', 'reference', name='uix_fra_per_diem_company_reference'),
    )
    id = Column(Integer, primary_key=True, index=True)
    company_id = Column(Integer, ForeignKey('companies.id'), nullable=False, index=True)
    reference = Column(String(150), nullable=False, index=True)
    collaborateur = Column(String(150), nullable=True)
    jours = Column(Integer, nullable=True)
    taux_journalier = Column(Numeric, nullable=True)
    statut = Column(String(150), nullable=True)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())


class FraMileageClaim(Base):
    """Frais kilometriques."""
    __tablename__ = "fra_mileage_claims"
    __table_args__ = (
        UniqueConstraint('company_id', 'reference', name='uix_fra_mileage_claims_company_reference'),
    )
    id = Column(Integer, primary_key=True, index=True)
    company_id = Column(Integer, ForeignKey('companies.id'), nullable=False, index=True)
    reference = Column(String(150), nullable=False, index=True)
    collaborateur = Column(String(150), nullable=True)
    km = Column(Integer, nullable=True)
    trajet = Column(String(150), nullable=True)
    montant = Column(Numeric, nullable=True)
    statut = Column(String(150), nullable=True)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())


class FraMealExpense(Base):
    """Frais de restauration."""
    __tablename__ = "fra_meal_expenses"
    __table_args__ = (
        UniqueConstraint('company_id', 'reference', name='uix_fra_meal_expenses_company_reference'),
    )
    id = Column(Integer, primary_key=True, index=True)
    company_id = Column(Integer, ForeignKey('companies.id'), nullable=False, index=True)
    reference = Column(String(150), nullable=False, index=True)
    collaborateur = Column(String(150), nullable=True)
    montant = Column(Numeric, nullable=True)
    nb_personnes = Column(Integer, nullable=True)
    date = Column(Date, nullable=True)
    statut = Column(String(150), nullable=True)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())


class FraTravelBooking(Base):
    """Reservations de deplacement."""
    __tablename__ = "fra_travel_bookings"
    __table_args__ = (
        UniqueConstraint('company_id', 'reference', name='uix_fra_travel_bookings_company_reference'),
    )
    id = Column(Integer, primary_key=True, index=True)
    company_id = Column(Integer, ForeignKey('companies.id'), nullable=False, index=True)
    reference = Column(String(150), nullable=False, index=True)
    collaborateur = Column(String(150), nullable=True)
    mode = Column(String(150), nullable=True)
    destination = Column(String(150), nullable=True)
    date_depart = Column(Date, nullable=True)
    statut = Column(String(150), nullable=True)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())


class FraHotelStay(Base):
    """Nuits d' hotel."""
    __tablename__ = "fra_hotel_stays"
    __table_args__ = (
        UniqueConstraint('company_id', 'reference', name='uix_fra_hotel_stays_company_reference'),
    )
    id = Column(Integer, primary_key=True, index=True)
    company_id = Column(Integer, ForeignKey('companies.id'), nullable=False, index=True)
    reference = Column(String(150), nullable=False, index=True)
    collaborateur = Column(String(150), nullable=True)
    hotel = Column(String(150), nullable=True)
    nuits = Column(Integer, nullable=True)
    montant = Column(Numeric, nullable=True)
    statut = Column(String(150), nullable=True)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())


class FraTransportExpense(Base):
    """Frais de transport local."""
    __tablename__ = "fra_transport_expenses"
    __table_args__ = (
        UniqueConstraint('company_id', 'reference', name='uix_fra_transport_expens_company_reference'),
    )
    id = Column(Integer, primary_key=True, index=True)
    company_id = Column(Integer, ForeignKey('companies.id'), nullable=False, index=True)
    reference = Column(String(150), nullable=False, index=True)
    collaborateur = Column(String(150), nullable=True)
    type = Column(String(150), nullable=True)
    montant = Column(Numeric, nullable=True)
    date = Column(DateTime(timezone=True), nullable=True)
    statut = Column(String(150), nullable=True)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())


class FraClientEntertainment(Base):
    """Frais de representation client."""
    __tablename__ = "fra_client_entertainment"
    __table_args__ = (
        UniqueConstraint('company_id', 'reference', name='uix_fra_client_entertain_company_reference'),
    )
    id = Column(Integer, primary_key=True, index=True)
    company_id = Column(Integer, ForeignKey('companies.id'), nullable=False, index=True)
    reference = Column(String(150), nullable=False, index=True)
    collaborateur = Column(String(150), nullable=True)
    client = Column(String(150), nullable=True)
    montant = Column(Numeric, nullable=True)
    nb_invites = Column(Integer, nullable=True)
    statut = Column(String(150), nullable=True)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())


class FraConferenceFee(Base):
    """Frais de salon et conference."""
    __tablename__ = "fra_conference_fees"
    __table_args__ = (
        UniqueConstraint('company_id', 'reference', name='uix_fra_conference_fees_company_reference'),
    )
    id = Column(Integer, primary_key=True, index=True)
    company_id = Column(Integer, ForeignKey('companies.id'), nullable=False, index=True)
    reference = Column(String(150), nullable=False, index=True)
    collaborateur = Column(String(150), nullable=True)
    evenement = Column(String(150), nullable=True)
    montant = Column(Numeric, nullable=True)
    date = Column(Date, nullable=True)
    statut = Column(String(150), nullable=True)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())


class FraOfficeSupply(Base):
    """Achats de fournitures."""
    __tablename__ = "fra_office_supplies"
    __table_args__ = (
        UniqueConstraint('company_id', 'reference', name='uix_fra_office_supplies_company_reference'),
    )
    id = Column(Integer, primary_key=True, index=True)
    company_id = Column(Integer, ForeignKey('companies.id'), nullable=False, index=True)
    reference = Column(String(150), nullable=False, index=True)
    demandeur = Column(String(150), nullable=True)
    article = Column(String(150), nullable=True)
    montant = Column(Numeric, nullable=True)
    centre_cout = Column(String(150), nullable=True)
    statut = Column(String(150), nullable=True)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())


class FraCardTransaction(Base):
    """Transactions carte entreprise."""
    __tablename__ = "fra_card_transactions"
    __table_args__ = (
        UniqueConstraint('company_id', 'reference', name='uix_fra_card_transaction_company_reference'),
    )
    id = Column(Integer, primary_key=True, index=True)
    company_id = Column(Integer, ForeignKey('companies.id'), nullable=False, index=True)
    reference = Column(String(150), nullable=False, index=True)
    titulaire = Column(String(150), nullable=True)
    marchand = Column(String(150), nullable=True)
    montant = Column(Numeric, nullable=True)
    date = Column(DateTime(timezone=True), nullable=True)
    statut = Column(String(150), nullable=True)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())


class FraCurrencyConversion(Base):
    """Conversions de devise."""
    __tablename__ = "fra_currency_conversions"
    __table_args__ = (
        UniqueConstraint('company_id', 'reference', name='uix_fra_currency_convers_company_reference'),
    )
    id = Column(Integer, primary_key=True, index=True)
    company_id = Column(Integer, ForeignKey('companies.id'), nullable=False, index=True)
    reference = Column(String(150), nullable=False, index=True)
    frais = Column(String(150), nullable=True)
    devise_source = Column(String(150), nullable=True)
    montant_source = Column(Numeric, nullable=True)
    taux = Column(Numeric, nullable=True)
    statut = Column(String(150), nullable=True)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())


class FraExpenseApproval(Base):
    """Validations de frais."""
    __tablename__ = "fra_expense_approvals"
    __table_args__ = (
        UniqueConstraint('company_id', 'reference', name='uix_fra_expense_approval_company_reference'),
    )
    id = Column(Integer, primary_key=True, index=True)
    company_id = Column(Integer, ForeignKey('companies.id'), nullable=False, index=True)
    reference = Column(String(150), nullable=False, index=True)
    note_frais = Column(String(150), nullable=True)
    valideur = Column(String(150), nullable=True)
    commentaire = Column(Text(2000), nullable=True)
    date = Column(DateTime(timezone=True), nullable=True)
    statut = Column(String(150), nullable=True)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())


class FraExpenseDispute(Base):
    """Litiges de frais."""
    __tablename__ = "fra_expense_disputes"
    __table_args__ = (
        UniqueConstraint('company_id', 'reference', name='uix_fra_expense_disputes_company_reference'),
    )
    id = Column(Integer, primary_key=True, index=True)
    company_id = Column(Integer, ForeignKey('companies.id'), nullable=False, index=True)
    reference = Column(String(150), nullable=False, index=True)
    note_frais = Column(String(150), nullable=True)
    motif = Column(Text(2000), nullable=True)
    montant_conteste = Column(Numeric, nullable=True)
    statut = Column(String(150), nullable=True)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())


class FraVatRecovery(Base):
    """Recuperation TVA sur frais."""
    __tablename__ = "fra_vat_recovery"
    __table_args__ = (
        UniqueConstraint('company_id', 'reference', name='uix_fra_vat_recovery_company_reference'),
    )
    id = Column(Integer, primary_key=True, index=True)
    company_id = Column(Integer, ForeignKey('companies.id'), nullable=False, index=True)
    reference = Column(String(150), nullable=False, index=True)
    frais = Column(String(150), nullable=True)
    montant_ht = Column(Numeric, nullable=True)
    tva = Column(Numeric, nullable=True)
    statut = Column(String(150), nullable=True)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())


class FraExpenseBudgetTracking(Base):
    """Suivi budget de frais."""
    __tablename__ = "fra_budget_tracking"
    __table_args__ = (
        UniqueConstraint('company_id', 'reference', name='uix_fra_budget_tracking_company_reference'),
    )
    id = Column(Integer, primary_key=True, index=True)
    company_id = Column(Integer, ForeignKey('companies.id'), nullable=False, index=True)
    reference = Column(String(150), nullable=False, index=True)
    centre_cout = Column(String(150), nullable=True)
    periode = Column(String(150), nullable=True)
    budget = Column(Numeric, nullable=True)
    engage = Column(Numeric, nullable=True)
    statut = Column(String(150), nullable=True)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())


class FraExpenseCategory(Base):
    """Categories de frais."""
    __tablename__ = "fra_expense_categories"
    __table_args__ = (
        UniqueConstraint('company_id', 'reference', name='uix_fra_expense_categori_company_reference'),
    )
    id = Column(Integer, primary_key=True, index=True)
    company_id = Column(Integer, ForeignKey('companies.id'), nullable=False, index=True)
    reference = Column(String(150), nullable=False, index=True)
    libelle = Column(String(150), nullable=True)
    plafond = Column(Numeric, nullable=True)
    justificatif_requis = Column(Boolean, nullable=True)
    statut = Column(String(150), nullable=True)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

