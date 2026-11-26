"""Modeles portail-qhse (expansion approfondie generee).

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

class QspHazardReport_gravite(str, enum.Enum):
    FAIBLE = "faible"
    MOYENNE = "moyenne"
    ELEVEE = "elevee"
    CRITIQUE = "critique"


class QspHazardReport_statut(str, enum.Enum):
    SIGNAL = "signal"
    EVALUE = "evalue"
    MAITRISE = "maitrise"
    SUPPRIME = "supprime"


class QspNearMiss_statut(str, enum.Enum):
    DECLARE = "declare"
    ANALYSE = "analyse"
    ACTION_EN_COURS = "action_en_cours"
    CLOTURE = "cloture"


class QspSafetyObservation_nature(str, enum.Enum):
    BONNE_PRATIQUE = "bonne_pratique"
    ECART = "ecart"
    DANGER = "danger"


class QspSafetyObservation_statut(str, enum.Enum):
    ENREGISTRE = "enregistre"
    SUIVI = "suivi"
    CLOTURE = "cloture"


class QspPpeAttestation_statut(str, enum.Enum):
    CONFORME = "conforme"
    PARTIEL = "partiel"
    NON_CONFORME = "non_conforme"
    RAPPEL = "rappel"


class QspToolboxTalk_statut(str, enum.Enum):
    PLANIFIE = "planifie"
    ANIME = "anime"
    REPORTE = "reporte"
    ANNULE = "annule"


class QspWorkPermitRequest_type(str, enum.Enum):
    POINT_CHAUD = "point_chaud"
    ESPACE_CONFINE = "espace_confine"
    HAUTEUR = "hauteur"
    ELECTRIQUE = "electrique"


class QspWorkPermitRequest_statut(str, enum.Enum):
    SOUMIS = "soumis"
    EN_COURS_VALID = "en_cours_valid"
    ACCEPTE = "accepte"
    REFUSE = "refuse"
    CLOTURE = "cloture"


class QspSafetyTrainingLog_statut(str, enum.Enum):
    INSCIT = "inscit"
    SUIVI = "suivi"
    REUSSI = "reussi"
    ECHOUE = "echoue"
    EXPIRE = "expire"


class QspExposureRecord_statut(str, enum.Enum):
    SOUS_SEUIL = "sous_seuil"
    PROCHE_SEUIL = "proche_seuil"
    DEPASSE = "depasse"
    A_REMETRE = "a_remetre"


class QspFirstAidLog_statut(str, enum.Enum):
    SOINS_LOCAUX = "soins_locaux"
    ORIENTE = "oriente"
    HOSPITALISE = "hospitalise"
    CLOTURE = "cloture"


class QspSafetySuggestion_statut(str, enum.Enum):
    SOUMISE = "soumise"
    EVALUEE = "evaluee"
    RETENUE = "retenue"
    ECARTEE = "ecartee"
    MISE_EN_OEUVRE = "mise_en_oeuvre"


class QspStopWorkAuthority_statut(str, enum.Enum):
    EN_COURS = "en_cours"
    DANGER_EVALUE = "danger_evalue"
    REPRIS = "repris"
    CONSTATE_ABUSIF = "constate_abusif"


class QspSpillReport_statut(str, enum.Enum):
    SIGNAL = "signal"
    CONTENU = "contenu"
    DECONTAMINE = "decontamine"
    DECLARE_AUTORITE = "declare_autorite"


class QspMsdsAck_statut(str, enum.Enum):
    A_LIRE = "a_lire"
    LU = "lu"
    EXPIRE = "expire"
    A_RENOUVELER = "a_renouveler"


class QspErgonomicsAssessment_contrainte(str, enum.Enum):
    REPETITIF = "repetitif"
    PORT_CHARGE = "port_charge"
    POSTURE = "posture"
    VIBRATION = "vibration"


class QspErgonomicsAssessment_statut(str, enum.Enum):
    EVALUE = "evalue"
    A_AMENAGER = "a_amenager"
    AMENAGE = "amenage"
    RECONTROLE = "recontrole"


class QspHygieneCheck_statut(str, enum.Enum):
    CONFORME = "conforme"
    A_NETTOYER = "a_nettoyer"
    NON_CONFORME = "non_conforme"
    RECONTROLE = "recontrole"


class QspInspectionFinding_criticite(str, enum.Enum):
    MINEUR = "mineur"
    MAJEUR = "majeur"
    CRITIQUE = "critique"


class QspInspectionFinding_statut(str, enum.Enum):
    RELEVE = "releve"
    EN_COURS = "en_cours"
    RESOLU = "resolu"
    VERIFIE = "verifie"


class QspCapaReply_statut(str, enum.Enum):
    A_FAIRE = "a_faire"
    REPONDUE = "repondue"
    VALIDE = "valide"
    INSUFFISANTE = "insuffisante"


class QspRiskAssessmentInput_statut(str, enum.Enum):
    PROPOSE = "propose"
    INTEGRE = "integre"
    ECARTE = "ecarte"
    REVISER = "reviser"


class QspEvacuationDrill_statut(str, enum.Enum):
    PLANIFIE = "planifie"
    EFFECTUE = "effectue"
    NON_CONFORME = "non_conforme"
    REPROGRAMME = "reprogramme"


# ─── Modeles ──────────────────────────────────────────────────────────────────

class QspHazardReport(Base):
    """Signalements de dangers."""
    __tablename__ = "qsp_hazard_reports"
    __table_args__ = (
        UniqueConstraint('company_id', 'reference', name='uix_qsp_hazard_reports_company_reference'),
    )
    id = Column(Integer, primary_key=True, index=True)
    company_id = Column(Integer, ForeignKey('companies.id'), nullable=False, index=True)
    reference = Column(String(150), nullable=False, index=True)
    lieu = Column(String(150), nullable=True)
    description = Column(Text, nullable=True)
    gravite = Column(String(150), nullable=True)
    signale_le = Column(DateTime(timezone=True), nullable=True)
    statut = Column(String(150), nullable=True)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())


class QspNearMiss(Base):
    """Presqu' accidents."""
    __tablename__ = "qsp_near_misses"
    __table_args__ = (
        UniqueConstraint('company_id', 'reference', name='uix_qsp_near_misses_company_reference'),
    )
    id = Column(Integer, primary_key=True, index=True)
    company_id = Column(Integer, ForeignKey('companies.id'), nullable=False, index=True)
    reference = Column(String(150), nullable=False, index=True)
    lieu = Column(String(150), nullable=True)
    situation = Column(Text, nullable=True)
    date = Column(DateTime(timezone=True), nullable=True)
    témoin = Column(String(150), nullable=True)
    statut = Column(String(150), nullable=True)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())


class QspSafetyObservation(Base):
    """Observations de securite."""
    __tablename__ = "qsp_safety_observations"
    __table_args__ = (
        UniqueConstraint('company_id', 'reference', name='uix_qsp_safety_observati_company_reference'),
    )
    id = Column(Integer, primary_key=True, index=True)
    company_id = Column(Integer, ForeignKey('companies.id'), nullable=False, index=True)
    reference = Column(String(150), nullable=False, index=True)
    zone = Column(String(150), nullable=True)
    observation = Column(Text, nullable=True)
    nature = Column(String(150), nullable=True)
    date = Column(DateTime(timezone=True), nullable=True)
    statut = Column(String(150), nullable=True)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())


class QspPpeAttestation(Base):
    """Attestations de port d' EPI."""
    __tablename__ = "qsp_ppe_attestations"
    __table_args__ = (
        UniqueConstraint('company_id', 'reference', name='uix_qsp_ppe_attestations_company_reference'),
    )
    id = Column(Integer, primary_key=True, index=True)
    company_id = Column(Integer, ForeignKey('companies.id'), nullable=False, index=True)
    reference = Column(String(150), nullable=False, index=True)
    operateur = Column(String(150), nullable=True)
    epi_controles = Column(Integer, nullable=True)
    conforme = Column(Boolean, nullable=True)
    date = Column(DateTime(timezone=True), nullable=True)
    statut = Column(String(150), nullable=True)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())


class QspToolboxTalk(Base):
    """Quarts d' heure securite."""
    __tablename__ = "qsp_toolbox_talks"
    __table_args__ = (
        UniqueConstraint('company_id', 'reference', name='uix_qsp_toolbox_talks_company_reference'),
    )
    id = Column(Integer, primary_key=True, index=True)
    company_id = Column(Integer, ForeignKey('companies.id'), nullable=False, index=True)
    reference = Column(String(150), nullable=False, index=True)
    sujet = Column(String(150), nullable=True)
    anime_par = Column(String(150), nullable=True)
    nb_participants = Column(Integer, nullable=True)
    date = Column(Date, nullable=True)
    statut = Column(String(150), nullable=True)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())


class QspWorkPermitRequest(Base):
    """Demandes de permis de travail."""
    __tablename__ = "qsp_work_permits"
    __table_args__ = (
        UniqueConstraint('company_id', 'reference', name='uix_qsp_work_permits_company_reference'),
    )
    id = Column(Integer, primary_key=True, index=True)
    company_id = Column(Integer, ForeignKey('companies.id'), nullable=False, index=True)
    reference = Column(String(150), nullable=False, index=True)
    type = Column(String(150), nullable=True)
    lieu = Column(String(150), nullable=True)
    demandeur = Column(String(150), nullable=True)
    debut = Column(DateTime(timezone=True), nullable=True)
    statut = Column(String(150), nullable=True)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())


class QspSafetyTrainingLog(Base):
    """Suivi formation securite."""
    __tablename__ = "qsp_safety_training_logs"
    __table_args__ = (
        UniqueConstraint('company_id', 'reference', name='uix_qsp_safety_training__company_reference'),
    )
    id = Column(Integer, primary_key=True, index=True)
    company_id = Column(Integer, ForeignKey('companies.id'), nullable=False, index=True)
    reference = Column(String(150), nullable=False, index=True)
    operateur = Column(String(150), nullable=True)
    formation = Column(String(150), nullable=True)
    date = Column(Date, nullable=True)
    validite = Column(Date, nullable=True)
    statut = Column(String(150), nullable=True)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())


class QspExposureRecord(Base):
    """Registres d' exposition."""
    __tablename__ = "qsp_exposure_records"
    __table_args__ = (
        UniqueConstraint('company_id', 'reference', name='uix_qsp_exposure_records_company_reference'),
    )
    id = Column(Integer, primary_key=True, index=True)
    company_id = Column(Integer, ForeignKey('companies.id'), nullable=False, index=True)
    reference = Column(String(150), nullable=False, index=True)
    operateur = Column(String(150), nullable=True)
    agent = Column(String(150), nullable=True)
    valeur = Column(Numeric, nullable=True)
    date = Column(Date, nullable=True)
    statut = Column(String(150), nullable=True)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())


class QspFirstAidLog(Base):
    """Registre de premiers secours."""
    __tablename__ = "qsp_first_aid_log"
    __table_args__ = (
        UniqueConstraint('company_id', 'reference', name='uix_qsp_first_aid_log_company_reference'),
    )
    id = Column(Integer, primary_key=True, index=True)
    company_id = Column(Integer, ForeignKey('companies.id'), nullable=False, index=True)
    reference = Column(String(150), nullable=False, index=True)
    personne = Column(String(150), nullable=True)
    nature_blessure = Column(String(150), nullable=True)
    date = Column(DateTime(timezone=True), nullable=True)
    secouriste = Column(String(150), nullable=True)
    statut = Column(String(150), nullable=True)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())


class QspSafetySuggestion(Base):
    """Suggestions de securite."""
    __tablename__ = "qsp_safety_suggestions"
    __table_args__ = (
        UniqueConstraint('company_id', 'reference', name='uix_qsp_safety_suggestio_company_reference'),
    )
    id = Column(Integer, primary_key=True, index=True)
    company_id = Column(Integer, ForeignKey('companies.id'), nullable=False, index=True)
    reference = Column(String(150), nullable=False, index=True)
    auteur = Column(String(150), nullable=True)
    idee = Column(Text, nullable=True)
    date = Column(Date, nullable=True)
    statut = Column(String(150), nullable=True)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())


class QspStopWorkAuthority(Base):
    """Droits de retrait."""
    __tablename__ = "qsp_stop_work"
    __table_args__ = (
        UniqueConstraint('company_id', 'reference', name='uix_qsp_stop_work_company_reference'),
    )
    id = Column(Integer, primary_key=True, index=True)
    company_id = Column(Integer, ForeignKey('companies.id'), nullable=False, index=True)
    reference = Column(String(150), nullable=False, index=True)
    motif = Column(Text, nullable=True)
    declenche_le = Column(DateTime(timezone=True), nullable=True)
    reprise_le = Column(DateTime(timezone=True), nullable=True)
    statut = Column(String(150), nullable=True)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())


class QspSpillReport(Base):
    """Signalements de deversement."""
    __tablename__ = "qsp_spill_reports"
    __table_args__ = (
        UniqueConstraint('company_id', 'reference', name='uix_qsp_spill_reports_company_reference'),
    )
    id = Column(Integer, primary_key=True, index=True)
    company_id = Column(Integer, ForeignKey('companies.id'), nullable=False, index=True)
    reference = Column(String(150), nullable=False, index=True)
    produit = Column(String(150), nullable=True)
    volume = Column(Numeric, nullable=True)
    lieu = Column(String(150), nullable=True)
    date = Column(DateTime(timezone=True), nullable=True)
    statut = Column(String(150), nullable=True)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())


class QspMsdsAck(Base):
    """Accuses FDS."""
    __tablename__ = "qsp_msds_acks"
    __table_args__ = (
        UniqueConstraint('company_id', 'reference', name='uix_qsp_msds_acks_company_reference'),
    )
    id = Column(Integer, primary_key=True, index=True)
    company_id = Column(Integer, ForeignKey('companies.id'), nullable=False, index=True)
    reference = Column(String(150), nullable=False, index=True)
    produit = Column(String(150), nullable=True)
    operateur = Column(String(150), nullable=True)
    date = Column(Date, nullable=True)
    version_fds = Column(String(150), nullable=True)
    statut = Column(String(150), nullable=True)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())


class QspErgonomicsAssessment(Base):
    """Evaluations ergonomiques."""
    __tablename__ = "qsp_ergonomics"
    __table_args__ = (
        UniqueConstraint('company_id', 'reference', name='uix_qsp_ergonomics_company_reference'),
    )
    id = Column(Integer, primary_key=True, index=True)
    company_id = Column(Integer, ForeignKey('companies.id'), nullable=False, index=True)
    reference = Column(String(150), nullable=False, index=True)
    poste = Column(String(150), nullable=True)
    contrainte = Column(String(150), nullable=True)
    score = Column(Integer, nullable=True)
    date = Column(Date, nullable=True)
    statut = Column(String(150), nullable=True)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())


class QspHygieneCheck(Base):
    """Controles d' hygiene."""
    __tablename__ = "qsp_hygiene_checks"
    __table_args__ = (
        UniqueConstraint('company_id', 'reference', name='uix_qsp_hygiene_checks_company_reference'),
    )
    id = Column(Integer, primary_key=True, index=True)
    company_id = Column(Integer, ForeignKey('companies.id'), nullable=False, index=True)
    reference = Column(String(150), nullable=False, index=True)
    local = Column(String(150), nullable=True)
    point_controle = Column(String(150), nullable=True)
    date = Column(DateTime(timezone=True), nullable=True)
    statut = Column(String(150), nullable=True)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())


class QspInspectionFinding(Base):
    """Constats d' inspection."""
    __tablename__ = "qsp_inspection_findings"
    __table_args__ = (
        UniqueConstraint('company_id', 'reference', name='uix_qsp_inspection_findi_company_reference'),
    )
    id = Column(Integer, primary_key=True, index=True)
    company_id = Column(Integer, ForeignKey('companies.id'), nullable=False, index=True)
    reference = Column(String(150), nullable=False, index=True)
    inspection = Column(String(150), nullable=True)
    constat = Column(Text, nullable=True)
    criticite = Column(String(150), nullable=True)
    date = Column(Date, nullable=True)
    statut = Column(String(150), nullable=True)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())


class QspCapaReply(Base):
    """Reponses aux actions correctives."""
    __tablename__ = "qsp_capa_replies"
    __table_args__ = (
        UniqueConstraint('company_id', 'reference', name='uix_qsp_capa_replies_company_reference'),
    )
    id = Column(Integer, primary_key=True, index=True)
    company_id = Column(Integer, ForeignKey('companies.id'), nullable=False, index=True)
    reference = Column(String(150), nullable=False, index=True)
    action_corrective = Column(String(150), nullable=True)
    reponse = Column(Text, nullable=True)
    operateur = Column(String(150), nullable=True)
    date = Column(DateTime(timezone=True), nullable=True)
    statut = Column(String(150), nullable=True)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())


class QspRiskAssessmentInput(Base):
    """Contributions a l' evaluation des risques."""
    __tablename__ = "qsp_risk_inputs"
    __table_args__ = (
        UniqueConstraint('company_id', 'reference', name='uix_qsp_risk_inputs_company_reference'),
    )
    id = Column(Integer, primary_key=True, index=True)
    company_id = Column(Integer, ForeignKey('companies.id'), nullable=False, index=True)
    reference = Column(String(150), nullable=False, index=True)
    activite = Column(String(150), nullable=True)
    risque_identifie = Column(Text, nullable=True)
    cotation = Column(Integer, nullable=True)
    date = Column(Date, nullable=True)
    statut = Column(String(150), nullable=True)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())


class QspEvacuationDrill(Base):
    """Exercices d' evacuation."""
    __tablename__ = "qsp_evacuation_drills"
    __table_args__ = (
        UniqueConstraint('company_id', 'reference', name='uix_qsp_evacuation_drill_company_reference'),
    )
    id = Column(Integer, primary_key=True, index=True)
    company_id = Column(Integer, ForeignKey('companies.id'), nullable=False, index=True)
    reference = Column(String(150), nullable=False, index=True)
    site = Column(String(150), nullable=True)
    date = Column(DateTime(timezone=True), nullable=True)
    duree_sec = Column(Integer, nullable=True)
    nb_evacues = Column(Integer, nullable=True)
    statut = Column(String(150), nullable=True)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

