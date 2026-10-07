"""Modeles portail-collaborateur (expansion approfondie generee).

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

class CollAssignment_statut(str, enum.Enum):
    AFFECTE = "affecte"
    EN_COURS = "en_cours"
    TERMINE = "termine"
    INTERROMPU = "interrompu"


class CollActivityLog_statut(str, enum.Enum):
    SAISI = "saisi"
    SOUMIS = "soumis"
    VALIDE = "valide"
    CORRIGE = "corrige"


class CollDeliverable_statut(str, enum.Enum):
    SOUMIS = "soumis"
    EN_REVUE = "en_revue"
    ACCEPTE = "accepte"
    RETOUR = "retour"
    REJETE = "rejete"


class CollTimesheet_statut(str, enum.Enum):
    SAISI = "saisi"
    SOUMIS = "soumis"
    APPROUVE = "approuve"
    FACTURE = "facture"
    REJETE = "rejete"


class CollSiteAccessLog_statut(str, enum.Enum):
    OUVERT = "ouvert"
    FERME = "ferme"
    ANOMALE = "anomale"


class CollWorkInstructionReceipt_statut(str, enum.Enum):
    A_LIRE = "a_lire"
    ACCEPTE = "accepte"
    REFUSE = "refuse"
    EXPIRE = "expire"


class CollIncidentReport_gravite(str, enum.Enum):
    MINEUR = "mineur"
    MAJEUR = "majeur"
    CRITIQUE = "critique"


class CollIncidentReport_statut(str, enum.Enum):
    DECLARE = "declare"
    PRIS_EN_CHARGE = "pris_en_charge"
    RESOLU = "resolu"
    ESCALADE = "escalade"


class CollQualityCheck_statut(str, enum.Enum):
    SAISI = "saisi"
    CONFORME = "conforme"
    NON_CONFORME = "non_conforme"
    A_REFAIRE = "a_refaire"


class CollTrainingCompletion_statut(str, enum.Enum):
    SUIVI = "suivi"
    REUSSI = "reussi"
    ECHOUE = "echoue"
    CERTIFIE = "certifie"


class CollEquipmentIssue_statut(str, enum.Enum):
    SIGNAL = "signal"
    REPARATION = "reparation"
    REMPLACER = "remplacer"
    RESOLU = "resolu"


class CollShiftAttendance_statut(str, enum.Enum):
    PRESENT = "present"
    ABSENT = "absent"
    RETARD = "retard"
    JUSTIFIE = "justifie"


class CollTravelOrder_statut(str, enum.Enum):
    DEMANDE = "demande"
    APPROUVE = "approuve"
    EN_COURS = "en_cours"
    CLOTURE = "cloture"
    ANNULE = "annule"


class CollExpenseDeclaration_statut(str, enum.Enum):
    DECLARE = "declare"
    JUSTIFIE = "justifie"
    REMBOURSE = "rembourse"
    REJETE = "rejete"


class CollCertificationUpload_statut(str, enum.Enum):
    DEPOSE = "depose"
    VERIFIE = "verifie"
    REJETE = "rejete"
    EXPIRE = "expire"


class CollTaskCompletion_statut(str, enum.Enum):
    EN_COURS = "en_cours"
    FAITE = "faite"
    VALIDEE = "validee"
    REOUVERTE = "reouverte"


class CollFeedback_statut(str, enum.Enum):
    EMIS = "emis"
    PRIS_EN_COMPTE = "pris_en_compte"
    TRAITE = "traite"
    CLASSE = "classe"


class CollAvailability_statut(str, enum.Enum):
    DISPONIBLE = "disponible"
    PARTIEL = "partiel"
    INDISPONIBLE = "indisponible"


class CollContractRenewalRequest_type(str, enum.Enum):
    CDD = "cdd"
    INTERIM = "interim"
    PRESTATION = "prestation"
    ALTERNANCE = "alternance"


class CollContractRenewalRequest_statut(str, enum.Enum):
    DEMANDE = "demande"
    INSTRUIT = "instruit"
    RENOUVELE = "renouvele"
    NON_RENOUVELE = "non_renouvele"


class CollDocumentRequest_statut(str, enum.Enum):
    DEMANDE = "demande"
    REPONDUE = "repondue"
    RELANCE = "relance"
    CLASSE = "classe"


# ─── Modeles ──────────────────────────────────────────────────────────────────

class CollAssignment(Base):
    """Affectations de mission."""
    __tablename__ = "coll_assignments"
    __table_args__ = (
        UniqueConstraint('company_id', 'reference', name='uix_coll_assignments_company_reference'),
    )
    id = Column(Integer, primary_key=True, index=True)
    company_id = Column(Integer, ForeignKey('companies.id'), nullable=False, index=True)
    reference = Column(String(150), nullable=False, index=True)
    collaborateur = Column(String(150), nullable=True)
    mission = Column(String(150), nullable=True)
    site = Column(String(150), nullable=True)
    debut = Column(Date, nullable=True)
    statut = Column(String(150), nullable=True)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())


class CollActivityLog(Base):
    """Journaux d' activite."""
    __tablename__ = "coll_activity_logs"
    __table_args__ = (
        UniqueConstraint('company_id', 'reference', name='uix_coll_activity_logs_company_reference'),
    )
    id = Column(Integer, primary_key=True, index=True)
    company_id = Column(Integer, ForeignKey('companies.id'), nullable=False, index=True)
    reference = Column(String(150), nullable=False, index=True)
    collaborateur = Column(String(150), nullable=True)
    date = Column(Date, nullable=True)
    heures = Column(Numeric, nullable=True)
    activite = Column(Text, nullable=True)
    statut = Column(String(150), nullable=True)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())


class CollDeliverable(Base):
    """Remises de livrables."""
    __tablename__ = "coll_deliverables"
    __table_args__ = (
        UniqueConstraint('company_id', 'reference', name='uix_coll_deliverables_company_reference'),
    )
    id = Column(Integer, primary_key=True, index=True)
    company_id = Column(Integer, ForeignKey('companies.id'), nullable=False, index=True)
    reference = Column(String(150), nullable=False, index=True)
    collaborateur = Column(String(150), nullable=True)
    livrable = Column(String(150), nullable=True)
    mission = Column(String(150), nullable=True)
    date = Column(DateTime(timezone=True), nullable=True)
    statut = Column(String(150), nullable=True)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())


class CollTimesheet(Base):
    """Declarations de temps."""
    __tablename__ = "coll_timesheets"
    __table_args__ = (
        UniqueConstraint('company_id', 'reference', name='uix_coll_timesheets_company_reference'),
    )
    id = Column(Integer, primary_key=True, index=True)
    company_id = Column(Integer, ForeignKey('companies.id'), nullable=False, index=True)
    reference = Column(String(150), nullable=False, index=True)
    collaborateur = Column(String(150), nullable=True)
    mission = Column(String(150), nullable=True)
    heures = Column(Numeric, nullable=True)
    semaine = Column(String(150), nullable=True)
    statut = Column(String(150), nullable=True)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())


class CollSiteAccessLog(Base):
    """Journaux d' acces site."""
    __tablename__ = "coll_site_access"
    __table_args__ = (
        UniqueConstraint('company_id', 'reference', name='uix_coll_site_access_company_reference'),
    )
    id = Column(Integer, primary_key=True, index=True)
    company_id = Column(Integer, ForeignKey('companies.id'), nullable=False, index=True)
    reference = Column(String(150), nullable=False, index=True)
    collaborateur = Column(String(150), nullable=True)
    site = Column(String(150), nullable=True)
    entree = Column(DateTime(timezone=True), nullable=True)
    sortie = Column(DateTime(timezone=True), nullable=True)
    statut = Column(String(150), nullable=True)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())


class CollWorkInstructionReceipt(Base):
    """Accuses de consignes."""
    __tablename__ = "coll_instruction_receipts"
    __table_args__ = (
        UniqueConstraint('company_id', 'reference', name='uix_coll_instruction_rec_company_reference'),
    )
    id = Column(Integer, primary_key=True, index=True)
    company_id = Column(Integer, ForeignKey('companies.id'), nullable=False, index=True)
    reference = Column(String(150), nullable=False, index=True)
    collaborateur = Column(String(150), nullable=True)
    consigne = Column(String(150), nullable=True)
    date = Column(DateTime(timezone=True), nullable=True)
    statut = Column(String(150), nullable=True)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())


class CollIncidentReport(Base):
    """Signalements d' incident."""
    __tablename__ = "coll_incidents"
    __table_args__ = (
        UniqueConstraint('company_id', 'reference', name='uix_coll_incidents_company_reference'),
    )
    id = Column(Integer, primary_key=True, index=True)
    company_id = Column(Integer, ForeignKey('companies.id'), nullable=False, index=True)
    reference = Column(String(150), nullable=False, index=True)
    collaborateur = Column(String(150), nullable=True)
    lieu = Column(String(150), nullable=True)
    description = Column(Text, nullable=True)
    gravite = Column(String(150), nullable=True)
    statut = Column(String(150), nullable=True)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())


class CollQualityCheck(Base):
    """Remises de controles qualite."""
    __tablename__ = "coll_quality_checks"
    __table_args__ = (
        UniqueConstraint('company_id', 'reference', name='uix_coll_quality_checks_company_reference'),
    )
    id = Column(Integer, primary_key=True, index=True)
    company_id = Column(Integer, ForeignKey('companies.id'), nullable=False, index=True)
    reference = Column(String(150), nullable=False, index=True)
    collaborateur = Column(String(150), nullable=True)
    controle = Column(String(150), nullable=True)
    point_testes = Column(Integer, nullable=True)
    anomalies = Column(Integer, nullable=True)
    statut = Column(String(150), nullable=True)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())


class CollTrainingCompletion(Base):
    """Attestations de formation."""
    __tablename__ = "coll_training_completions"
    __table_args__ = (
        UniqueConstraint('company_id', 'reference', name='uix_coll_training_comple_company_reference'),
    )
    id = Column(Integer, primary_key=True, index=True)
    company_id = Column(Integer, ForeignKey('companies.id'), nullable=False, index=True)
    reference = Column(String(150), nullable=False, index=True)
    collaborateur = Column(String(150), nullable=True)
    formation = Column(String(150), nullable=True)
    date = Column(Date, nullable=True)
    score = Column(Integer, nullable=True)
    statut = Column(String(150), nullable=True)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())


class CollEquipmentIssue(Base):
    """Signalements de probleme equipement."""
    __tablename__ = "coll_equipment_issues"
    __table_args__ = (
        UniqueConstraint('company_id', 'reference', name='uix_coll_equipment_issue_company_reference'),
    )
    id = Column(Integer, primary_key=True, index=True)
    company_id = Column(Integer, ForeignKey('companies.id'), nullable=False, index=True)
    reference = Column(String(150), nullable=False, index=True)
    collaborateur = Column(String(150), nullable=True)
    equipement = Column(String(150), nullable=True)
    probleme = Column(Text, nullable=True)
    date = Column(DateTime(timezone=True), nullable=True)
    statut = Column(String(150), nullable=True)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())


class CollShiftAttendance(Base):
    """Presences par poste."""
    __tablename__ = "coll_shift_attendance"
    __table_args__ = (
        UniqueConstraint('company_id', 'reference', name='uix_coll_shift_attendanc_company_reference'),
    )
    id = Column(Integer, primary_key=True, index=True)
    company_id = Column(Integer, ForeignKey('companies.id'), nullable=False, index=True)
    reference = Column(String(150), nullable=False, index=True)
    collaborateur = Column(String(150), nullable=True)
    poste = Column(String(150), nullable=True)
    date = Column(Date, nullable=True)
    arrivee = Column(DateTime(timezone=True), nullable=True)
    statut = Column(String(150), nullable=True)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())


class CollTravelOrder(Base):
    """Ordres de mission."""
    __tablename__ = "coll_travel_orders"
    __table_args__ = (
        UniqueConstraint('company_id', 'reference', name='uix_coll_travel_orders_company_reference'),
    )
    id = Column(Integer, primary_key=True, index=True)
    company_id = Column(Integer, ForeignKey('companies.id'), nullable=False, index=True)
    reference = Column(String(150), nullable=False, index=True)
    collaborateur = Column(String(150), nullable=True)
    destination = Column(String(150), nullable=True)
    debut = Column(Date, nullable=True)
    fin = Column(Date, nullable=True)
    statut = Column(String(150), nullable=True)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())


class CollExpenseDeclaration(Base):
    """Declarations de frais."""
    __tablename__ = "coll_expense_declarations"
    __table_args__ = (
        UniqueConstraint('company_id', 'reference', name='uix_coll_expense_declara_company_reference'),
    )
    id = Column(Integer, primary_key=True, index=True)
    company_id = Column(Integer, ForeignKey('companies.id'), nullable=False, index=True)
    reference = Column(String(150), nullable=False, index=True)
    collaborateur = Column(String(150), nullable=True)
    mission = Column(String(150), nullable=True)
    montant = Column(Numeric, nullable=True)
    date = Column(Date, nullable=True)
    statut = Column(String(150), nullable=True)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())


class CollCertificationUpload(Base):
    """Depot de certifications."""
    __tablename__ = "coll_cert_uploads"
    __table_args__ = (
        UniqueConstraint('company_id', 'reference', name='uix_coll_cert_uploads_company_reference'),
    )
    id = Column(Integer, primary_key=True, index=True)
    company_id = Column(Integer, ForeignKey('companies.id'), nullable=False, index=True)
    reference = Column(String(150), nullable=False, index=True)
    collaborateur = Column(String(150), nullable=True)
    certification = Column(String(150), nullable=True)
    expire_le = Column(Date, nullable=True)
    statut = Column(String(150), nullable=True)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())


class CollTaskCompletion(Base):
    """Achevements de taches."""
    __tablename__ = "coll_task_completions"
    __table_args__ = (
        UniqueConstraint('company_id', 'reference', name='uix_coll_task_completion_company_reference'),
    )
    id = Column(Integer, primary_key=True, index=True)
    company_id = Column(Integer, ForeignKey('companies.id'), nullable=False, index=True)
    reference = Column(String(150), nullable=False, index=True)
    collaborateur = Column(String(150), nullable=True)
    tache = Column(String(150), nullable=True)
    acheve_le = Column(DateTime(timezone=True), nullable=True)
    statut = Column(String(150), nullable=True)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())


class CollFeedback(Base):
    """Remontees terrain."""
    __tablename__ = "coll_feedback"
    __table_args__ = (
        UniqueConstraint('company_id', 'reference', name='uix_coll_feedback_company_reference'),
    )
    id = Column(Integer, primary_key=True, index=True)
    company_id = Column(Integer, ForeignKey('companies.id'), nullable=False, index=True)
    reference = Column(String(150), nullable=False, index=True)
    collaborateur = Column(String(150), nullable=True)
    sujet = Column(String(150), nullable=True)
    contenu = Column(Text, nullable=True)
    date = Column(Date, nullable=True)
    statut = Column(String(150), nullable=True)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())


class CollAvailability(Base):
    """Declarations de disponibilite."""
    __tablename__ = "coll_availability"
    __table_args__ = (
        UniqueConstraint('company_id', 'reference', name='uix_coll_availability_company_reference'),
    )
    id = Column(Integer, primary_key=True, index=True)
    company_id = Column(Integer, ForeignKey('companies.id'), nullable=False, index=True)
    reference = Column(String(150), nullable=False, index=True)
    collaborateur = Column(String(150), nullable=True)
    periode = Column(String(150), nullable=True)
    statut = Column(String(150), nullable=True)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())


class CollContractRenewalRequest(Base):
    """Demandes de renouvellement de contrat."""
    __tablename__ = "coll_contract_renewals"
    __table_args__ = (
        UniqueConstraint('company_id', 'reference', name='uix_coll_contract_renewa_company_reference'),
    )
    id = Column(Integer, primary_key=True, index=True)
    company_id = Column(Integer, ForeignKey('companies.id'), nullable=False, index=True)
    reference = Column(String(150), nullable=False, index=True)
    collaborateur = Column(String(150), nullable=True)
    echeance = Column(Date, nullable=True)
    type = Column(String(150), nullable=True)
    statut = Column(String(150), nullable=True)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())


class CollDocumentRequest(Base):
    """Demandes de documents."""
    __tablename__ = "coll_document_requests"
    __table_args__ = (
        UniqueConstraint('company_id', 'reference', name='uix_coll_document_reques_company_reference'),
    )
    id = Column(Integer, primary_key=True, index=True)
    company_id = Column(Integer, ForeignKey('companies.id'), nullable=False, index=True)
    reference = Column(String(150), nullable=False, index=True)
    collaborateur = Column(String(150), nullable=True)
    document = Column(String(150), nullable=True)
    delai = Column(Date, nullable=True)
    statut = Column(String(150), nullable=True)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

