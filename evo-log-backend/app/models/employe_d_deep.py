"""Modeles portail-employe (expansion approfondie generee).

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

class EmpLeaveRequest_type_conge(str, enum.Enum):
    CP = "cp"
    RTT = "rtt"
    SANS_TRAITEMENT = "sans_traitement"
    EVENTEMENT = "eventement"


class EmpLeaveRequest_statut(str, enum.Enum):
    SOUMIS = "soumis"
    EN_COURS = "en_cours"
    ACCEPTE = "accepte"
    REFUSE = "refuse"
    ANNULE = "annule"


class EmpTimesheetEntry_statut(str, enum.Enum):
    SAISI = "saisi"
    SOUMIS = "soumis"
    VALIDE = "valide"
    CORRIGE = "corrige"


class EmpOvertimeRequest_statut(str, enum.Enum):
    SOUMIS = "soumis"
    ACCORD = "accord"
    REFUS = "refus"
    RECUPERE = "recupere"


class EmpAttendanceCorrection_statut(str, enum.Enum):
    DEMANDEE = "demandee"
    INSTRUIT = "instruit"
    APPLIQUEE = "appliquee"
    REFUSEE = "refusee"


class EmpShiftSwap_statut(str, enum.Enum):
    PROPOSE = "propose"
    ACCEPTE_PARTENAIRE = "accepte_partenaire"
    VALIDE_RH = "valide_rh"
    REFUSE = "refuse"


class EmpTrainingEnrollment_statut(str, enum.Enum):
    DEMANDEE = "demandee"
    VALIDEE = "validee"
    SUIVIE = "suivie"
    ABANDONNEE = "abandonnee"


class EmpSkillDeclaration_niveau(str, enum.Enum):
    DEBUTANT = "debutant"
    INTERMEDIAIRE = "intermediaire"
    AUTONOME = "autonome"
    EXPERT = "expert"


class EmpSkillDeclaration_statut(str, enum.Enum):
    DECLAREE = "declaree"
    EVALUEE = "evaluee"
    VALIDEE = "validee"
    ECARTEE = "ecartee"


class EmpCertificationRenewal_statut(str, enum.Enum):
    A_RENOUVELER = "a_renouveler"
    DEMANDEE = "demandee"
    OCTROYEE = "octroyee"
    PERIMEE = "perimee"


class EmpPersonalInfoChange_champ(str, enum.Enum):
    ADRESSE = "adresse"
    TELEPHONE = "telephone"
    SITUATION_FAMILIALE = "situation_familiale"
    BENEFICIAIRE = "beneficiaire"


class EmpPersonalInfoChange_statut(str, enum.Enum):
    DEMANDEE = "demandee"
    JUSTIFIEE = "justifiee"
    APPLIQUEE = "appliquee"
    REFUSEE = "refusee"


class EmpBankDetailsUpdate_statut(str, enum.Enum):
    DEMANDE = "demande"
    VERIFIEE = "verifiee"
    ACTIVE = "active"
    REJETEE = "rejetee"


class EmpEmergencyContact_statut(str, enum.Enum):
    A_JOUR = "a_jour"
    A_VERIFIER = "a_verifier"
    OBSOLETE = "obsolete"


class EmpBadgeRequest_motif(str, enum.Enum):
    NOUVEAU = "nouveau"
    PERTE = "perte"
    VOL = "vol"
    RENOUVELLEMENT = "renouvellement"
    DEGRADATION = "degradation"


class EmpBadgeRequest_statut(str, enum.Enum):
    DEMANDE = "demande"
    FABRIQUE = "fabrique"
    REMIS = "remis"
    BLOQUE = "bloque"


class EmpAccessRequest_type_acces(str, enum.Enum):
    LOGIQUE = "logique"
    PHYSIQUE = "physique"
    TEMPORAIRE = "temporaire"


class EmpAccessRequest_statut(str, enum.Enum):
    DEMANDE = "demande"
    INSTRUIT = "instruit"
    ACCORDE = "accorde"
    REFUSE = "refuse"
    REVOQUE = "revoque"


class EmpDocumentUpload_type_piece(str, enum.Enum):
    PIECE_IDENTITE = "piece_identite"
    RIB = "rib"
    DIPLOME = "diplome"
    ATTESTATION = "attestation"


class EmpDocumentUpload_statut(str, enum.Enum):
    DEPOSE = "depose"
    VERIFIE = "verifie"
    REJETE = "rejete"
    EXPIRE = "expire"


class EmpSelfReview_statut(str, enum.Enum):
    BROUILLON = "brouillon"
    SOUMISE = "soumise"
    DISCUTE = "discute"
    CLOTURE = "cloture"


class EmpMobilityApplication_statut(str, enum.Enum):
    DEPOSEE = "deposee"
    PRESELECTIONNE = "preselectionne"
    ENTRETIEN = "entretien"
    RETENU = "retenu"
    NON_RETENU = "non_retenu"


class EmpSicknessDeclaration_statut(str, enum.Enum):
    DECLARE = "declare"
    JUSTIFIE = "justifie"
    PROLONGE = "prolonge"
    REPRIS = "repris"
    CONTROLE = "controle"


# ─── Modeles ──────────────────────────────────────────────────────────────────

class EmpLeaveRequest(Base):
    """Demandes de conges."""
    __tablename__ = "emp_leave_requests"
    __table_args__ = (
        UniqueConstraint('company_id', 'reference', name='uix_emp_leave_requests_company_reference'),
    )
    id = Column(Integer, primary_key=True, index=True)
    company_id = Column(Integer, ForeignKey('companies.id'), nullable=False, index=True)
    reference = Column(String(150), nullable=False, index=True)
    collaborateur = Column(String(150), nullable=True)
    type_conge = Column(String(150), nullable=True)
    debut = Column(Date, nullable=True)
    fin = Column(Date, nullable=True)
    jours = Column(Integer, nullable=True)
    statut = Column(String(150), nullable=True)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())


class EmpTimesheetEntry(Base):
    """Feuilles de temps."""
    __tablename__ = "emp_timesheet_entries"
    __table_args__ = (
        UniqueConstraint('company_id', 'reference', name='uix_emp_timesheet_entrie_company_reference'),
    )
    id = Column(Integer, primary_key=True, index=True)
    company_id = Column(Integer, ForeignKey('companies.id'), nullable=False, index=True)
    reference = Column(String(150), nullable=False, index=True)
    collaborateur = Column(String(150), nullable=True)
    date = Column(Date, nullable=True)
    heures = Column(Numeric, nullable=True)
    projet = Column(String(150), nullable=True)
    statut = Column(String(150), nullable=True)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())


class EmpOvertimeRequest(Base):
    """Demandes d' heures supplementaires."""
    __tablename__ = "emp_overtime_requests"
    __table_args__ = (
        UniqueConstraint('company_id', 'reference', name='uix_emp_overtime_request_company_reference'),
    )
    id = Column(Integer, primary_key=True, index=True)
    company_id = Column(Integer, ForeignKey('companies.id'), nullable=False, index=True)
    reference = Column(String(150), nullable=False, index=True)
    collaborateur = Column(String(150), nullable=True)
    minutes = Column(Integer, nullable=True)
    motif = Column(String(150), nullable=True)
    date = Column(Date, nullable=True)
    statut = Column(String(150), nullable=True)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())


class EmpAttendanceCorrection(Base):
    """Regularisations de pointage."""
    __tablename__ = "emp_attendance_corrections"
    __table_args__ = (
        UniqueConstraint('company_id', 'reference', name='uix_emp_attendance_corre_company_reference'),
    )
    id = Column(Integer, primary_key=True, index=True)
    company_id = Column(Integer, ForeignKey('companies.id'), nullable=False, index=True)
    reference = Column(String(150), nullable=False, index=True)
    collaborateur = Column(String(150), nullable=True)
    date_concernee = Column(Date, nullable=True)
    motif = Column(Text(2000), nullable=True)
    statut = Column(String(150), nullable=True)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())


class EmpShiftSwap(Base):
    """Echanges de poste."""
    __tablename__ = "emp_shift_swaps"
    __table_args__ = (
        UniqueConstraint('company_id', 'reference', name='uix_emp_shift_swaps_company_reference'),
    )
    id = Column(Integer, primary_key=True, index=True)
    company_id = Column(Integer, ForeignKey('companies.id'), nullable=False, index=True)
    reference = Column(String(150), nullable=False, index=True)
    demandeur = Column(String(150), nullable=True)
    partenaire = Column(String(150), nullable=True)
    date_poste = Column(DateTime(timezone=True), nullable=True)
    statut = Column(String(150), nullable=True)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())


class EmpTrainingEnrollment(Base):
    """Inscriptions formation."""
    __tablename__ = "emp_training_enrollments"
    __table_args__ = (
        UniqueConstraint('company_id', 'reference', name='uix_emp_training_enrollm_company_reference'),
    )
    id = Column(Integer, primary_key=True, index=True)
    company_id = Column(Integer, ForeignKey('companies.id'), nullable=False, index=True)
    reference = Column(String(150), nullable=False, index=True)
    collaborateur = Column(String(150), nullable=True)
    formation = Column(String(150), nullable=True)
    date_debut = Column(Date, nullable=True)
    organism = Column(String(150), nullable=True)
    statut = Column(String(150), nullable=True)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())


class EmpSkillDeclaration(Base):
    """Declarations de competences."""
    __tablename__ = "emp_skill_declarations"
    __table_args__ = (
        UniqueConstraint('company_id', 'reference', name='uix_emp_skill_declaratio_company_reference'),
    )
    id = Column(Integer, primary_key=True, index=True)
    company_id = Column(Integer, ForeignKey('companies.id'), nullable=False, index=True)
    reference = Column(String(150), nullable=False, index=True)
    collaborateur = Column(String(150), nullable=True)
    competence = Column(String(150), nullable=True)
    niveau = Column(String(150), nullable=True)
    date = Column(Date, nullable=True)
    statut = Column(String(150), nullable=True)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())


class EmpCertificationRenewal(Base):
    """Renouvellements de certification."""
    __tablename__ = "emp_certification_renewals"
    __table_args__ = (
        UniqueConstraint('company_id', 'reference', name='uix_emp_certification_re_company_reference'),
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


class EmpPersonalInfoChange(Base):
    """Modifications d' etat civil."""
    __tablename__ = "emp_personal_info_changes"
    __table_args__ = (
        UniqueConstraint('company_id', 'reference', name='uix_emp_personal_info_ch_company_reference'),
    )
    id = Column(Integer, primary_key=True, index=True)
    company_id = Column(Integer, ForeignKey('companies.id'), nullable=False, index=True)
    reference = Column(String(150), nullable=False, index=True)
    collaborateur = Column(String(150), nullable=True)
    champ = Column(String(150), nullable=True)
    nouvelle_valeur = Column(String(150), nullable=True)
    date = Column(Date, nullable=True)
    statut = Column(String(150), nullable=True)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())


class EmpBankDetailsUpdate(Base):
    """Changements de RIB."""
    __tablename__ = "emp_bank_updates"
    __table_args__ = (
        UniqueConstraint('company_id', 'reference', name='uix_emp_bank_updates_company_reference'),
    )
    id = Column(Integer, primary_key=True, index=True)
    company_id = Column(Integer, ForeignKey('companies.id'), nullable=False, index=True)
    reference = Column(String(150), nullable=False, index=True)
    collaborateur = Column(String(150), nullable=True)
    banque = Column(String(150), nullable=True)
    date_effet = Column(Date, nullable=True)
    statut = Column(String(150), nullable=True)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())


class EmpEmergencyContact(Base):
    """Contacts d' urgence."""
    __tablename__ = "emp_emergency_contacts"
    __table_args__ = (
        UniqueConstraint('company_id', 'reference', name='uix_emp_emergency_contac_company_reference'),
    )
    id = Column(Integer, primary_key=True, index=True)
    company_id = Column(Integer, ForeignKey('companies.id'), nullable=False, index=True)
    reference = Column(String(150), nullable=False, index=True)
    collaborateur = Column(String(150), nullable=True)
    nom = Column(String(150), nullable=True)
    lien = Column(String(150), nullable=True)
    telephone = Column(String(150), nullable=True)
    statut = Column(String(150), nullable=True)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())


class EmpBadgeRequest(Base):
    """Demandes de badge."""
    __tablename__ = "emp_badge_requests"
    __table_args__ = (
        UniqueConstraint('company_id', 'reference', name='uix_emp_badge_requests_company_reference'),
    )
    id = Column(Integer, primary_key=True, index=True)
    company_id = Column(Integer, ForeignKey('companies.id'), nullable=False, index=True)
    reference = Column(String(150), nullable=False, index=True)
    collaborateur = Column(String(150), nullable=True)
    motif = Column(String(150), nullable=True)
    date = Column(Date, nullable=True)
    statut = Column(String(150), nullable=True)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())


class EmpAccessRequest(Base):
    """Demandes d' acces."""
    __tablename__ = "emp_access_requests"
    __table_args__ = (
        UniqueConstraint('company_id', 'reference', name='uix_emp_access_requests_company_reference'),
    )
    id = Column(Integer, primary_key=True, index=True)
    company_id = Column(Integer, ForeignKey('companies.id'), nullable=False, index=True)
    reference = Column(String(150), nullable=False, index=True)
    collaborateur = Column(String(150), nullable=True)
    ressource = Column(String(150), nullable=True)
    type_acces = Column(String(150), nullable=True)
    date = Column(Date, nullable=True)
    statut = Column(String(150), nullable=True)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())


class EmpDocumentUpload(Base):
    """Depot de documents RH."""
    __tablename__ = "emp_document_uploads"
    __table_args__ = (
        UniqueConstraint('company_id', 'reference', name='uix_emp_document_uploads_company_reference'),
    )
    id = Column(Integer, primary_key=True, index=True)
    company_id = Column(Integer, ForeignKey('companies.id'), nullable=False, index=True)
    reference = Column(String(150), nullable=False, index=True)
    collaborateur = Column(String(150), nullable=True)
    type_piece = Column(String(150), nullable=True)
    fichier = Column(String(150), nullable=True)
    date = Column(DateTime(timezone=True), nullable=True)
    statut = Column(String(150), nullable=True)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())


class EmpSelfReview(Base):
    """Auto-evaluations."""
    __tablename__ = "emp_self_reviews"
    __table_args__ = (
        UniqueConstraint('company_id', 'reference', name='uix_emp_self_reviews_company_reference'),
    )
    id = Column(Integer, primary_key=True, index=True)
    company_id = Column(Integer, ForeignKey('companies.id'), nullable=False, index=True)
    reference = Column(String(150), nullable=False, index=True)
    collaborateur = Column(String(150), nullable=True)
    periode = Column(String(150), nullable=True)
    accomplissements = Column(Text(2000), nullable=True)
    date = Column(Date, nullable=True)
    statut = Column(String(150), nullable=True)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())


class EmpMobilityApplication(Base):
    """Candidatures internes."""
    __tablename__ = "emp_mobility_apps"
    __table_args__ = (
        UniqueConstraint('company_id', 'reference', name='uix_emp_mobility_apps_company_reference'),
    )
    id = Column(Integer, primary_key=True, index=True)
    company_id = Column(Integer, ForeignKey('companies.id'), nullable=False, index=True)
    reference = Column(String(150), nullable=False, index=True)
    collaborateur = Column(String(150), nullable=True)
    poste_cible = Column(String(150), nullable=True)
    motivation = Column(Text(2000), nullable=True)
    date = Column(Date, nullable=True)
    statut = Column(String(150), nullable=True)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())


class EmpSicknessDeclaration(Base):
    """Declarations d' arret maladie."""
    __tablename__ = "emp_sickness_declarations"
    __table_args__ = (
        UniqueConstraint('company_id', 'reference', name='uix_emp_sickness_declara_company_reference'),
    )
    id = Column(Integer, primary_key=True, index=True)
    company_id = Column(Integer, ForeignKey('companies.id'), nullable=False, index=True)
    reference = Column(String(150), nullable=False, index=True)
    collaborateur = Column(String(150), nullable=True)
    debut = Column(Date, nullable=True)
    duree_jours = Column(Integer, nullable=True)
    justificatif = Column(Boolean, nullable=True)
    statut = Column(String(150), nullable=True)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

