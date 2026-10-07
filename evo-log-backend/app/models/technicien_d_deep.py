"""Modeles portail-technicien (expansion approfondie generee).

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

class TechWorkOrder_type_travaux(str, enum.Enum):
    PREVENTIF = "preventif"
    CORRECTIF = "correctif"
    AMLIORATIF = "amlioratif"
    CONTROLE = "controle"


class TechWorkOrder_statut(str, enum.Enum):
    OUVERT = "ouvert"
    EN_COURS = "en_cours"
    EN_ATTENTE_PIECE = "en_attente_piece"
    TERMINE = "termine"
    ANNULE = "annule"


class TechInterventionSheet_statut(str, enum.Enum):
    BROUILLON = "brouillon"
    VALIDEE = "validee"
    RETOUR_CLIENT = "retour_client"
    CLOTUREE = "cloturee"


class TechDiagnosis_statut(str, enum.Enum):
    EN_COURS = "en_cours"
    CONFIRME = "confirme"
    INDETERMIN = "indetermin"
    ESCALADE = "escalade"


class TechPartConsumption_statut(str, enum.Enum):
    RESERVE = "reserve"
    POSE = "pose"
    RETOURNE = "retourne"
    RUPTURE = "rupture"


class TechPreventivePlan_statut(str, enum.Enum):
    PLANIFIE = "planifie"
    PROCHE = "proche"
    EN_RETARD = "en_retard"
    FAIT = "fait"


class TechBreakdownTicket_severite(str, enum.Enum):
    BLOQUANT = "bloquant"
    MAJEUR = "majeur"
    MINEUR = "mineur"


class TechBreakdownTicket_statut(str, enum.Enum):
    NOUVEAU = "nouveau"
    AFFECTE = "affecte"
    REPARATION = "reparation"
    REMORQUE = "remorque"
    CLOTURE = "cloture"


class TechRepairReport_statut(str, enum.Enum):
    REDAIGE = "redaige"
    VALIDE = "valide"
    RETOUR = "retour"
    REMIS_SERVICE = "remis_service"


class TechCalibrationRecord_statut(str, enum.Enum):
    CONFORME = "conforme"
    AJUSTE = "ajuste"
    HORS_TOLERANCE = "hors_tolerance"
    REFORME = "reforme"


class TechEquipmentChecklist_statut(str, enum.Enum):
    CONFORME = "conforme"
    SURVEILLE = "surveille"
    INDISPONIBLE = "indisponible"


class TechToolLoan_statut(str, enum.Enum):
    EMPRUNTE = "emprunte"
    RETOURNE = "retourne"
    PERDU = "perdu"
    ENDOMMAGE = "endommage"


class TechSafetyLockout_statut(str, enum.Enum):
    POSEE = "posee"
    ACTIVE = "active"
    LEVEE = "levee"
    ANOMALIE = "anomalie"


class TechWarrantyClaim_statut(str, enum.Enum):
    SOUMISE = "soumise"
    INSTRUIT = "instruit"
    ACCEPTEE = "acceptee"
    REJETEE = "rejetee"


class TechServiceAppointment_statut(str, enum.Enum):
    PLANIFIE = "planifie"
    CONFIRME = "confirme"
    HONORE = "honore"
    MANQUE = "manque"
    REPORTE = "reporte"


class TechLaborTimesheet_statut(str, enum.Enum):
    SAISI = "saisi"
    SOUMIS = "soumis"
    VALIDE = "valide"
    AJUSTE = "ajuste"


class TechUpgradeRequest_statut(str, enum.Enum):
    PROPOSE = "propose"
    ETUDIE = "etudie"
    APPROUVE = "approuve"
    REJETE = "rejete"
    INSTALLE = "installe"


class TechFailureAnalysis_statut(str, enum.Enum):
    OUVERTE = "ouverte"
    ANALYSEE = "analysee"
    ACTION_PLANIFIEE = "action_planifiee"
    CLOTUREE = "cloturee"


class TechSpareRequest_statut(str, enum.Enum):
    SOUMISE = "soumise"
    EN_ATTENTE = "en_attente"
    SERVI = "servi"
    RUPTURE = "rupture"
    ANNULEE = "annulee"


class TechInspectionRecord_type_controle(str, enum.Enum):
    TECHNIQUE = "technique"
    SECURITE = "securite"
    ENVIRONNEMENT = "environnement"
    HABilitation = "habilitation"


class TechInspectionRecord_statut(str, enum.Enum):
    CONFORME = "conforme"
    RESERVES = "reserves"
    NON_CONFORME = "non_conforme"
    A_REFAIRE = "a_refaire"


class TechWorkOrderCost_statut(str, enum.Enum):
    ESTIME = "estime"
    EN_COURS = "en_cours"
    CLOTURE = "cloture"
    FACTURE = "facture"


# ─── Modeles ──────────────────────────────────────────────────────────────────

class TechWorkOrder(Base):
    """Ordres de travail."""
    __tablename__ = "tech_work_orders"
    __table_args__ = (
        UniqueConstraint('company_id', 'reference', name='uix_tech_work_orders_company_reference'),
    )
    id = Column(Integer, primary_key=True, index=True)
    company_id = Column(Integer, ForeignKey('companies.id'), nullable=False, index=True)
    reference = Column(String(150), nullable=False, index=True)
    vehicule = Column(String(150), nullable=True)
    type_travaux = Column(String(150), nullable=True)
    description = Column(Text(2000), nullable=True)
    ouverture = Column(DateTime(timezone=True), nullable=True)
    cloture = Column(DateTime(timezone=True), nullable=True)
    statut = Column(String(150), nullable=True)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())


class TechInterventionSheet(Base):
    """Fiches d' intervention."""
    __tablename__ = "tech_intervention_sheets"
    __table_args__ = (
        UniqueConstraint('company_id', 'reference', name='uix_tech_intervention_sh_company_reference'),
    )
    id = Column(Integer, primary_key=True, index=True)
    company_id = Column(Integer, ForeignKey('companies.id'), nullable=False, index=True)
    reference = Column(String(150), nullable=False, index=True)
    ordre_travail = Column(String(150), nullable=True)
    technicien = Column(String(150), nullable=True)
    duree_min = Column(Integer, nullable=True)
    main_oeuvre = Column(Numeric, nullable=True)
    statut = Column(String(150), nullable=True)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())


class TechDiagnosis(Base):
    """Diagnostics."""
    __tablename__ = "tech_diagnoses"
    __table_args__ = (
        UniqueConstraint('company_id', 'reference', name='uix_tech_diagnoses_company_reference'),
    )
    id = Column(Integer, primary_key=True, index=True)
    company_id = Column(Integer, ForeignKey('companies.id'), nullable=False, index=True)
    reference = Column(String(150), nullable=False, index=True)
    vehicule = Column(String(150), nullable=True)
    symptome = Column(String(150), nullable=True)
    cause_racine = Column(Text(2000), nullable=True)
    date = Column(DateTime(timezone=True), nullable=True)
    statut = Column(String(150), nullable=True)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())


class TechPartConsumption(Base):
    """Consommation de pieces."""
    __tablename__ = "tech_parts_consumption"
    __table_args__ = (
        UniqueConstraint('company_id', 'reference', name='uix_tech_parts_consumpti_company_reference'),
    )
    id = Column(Integer, primary_key=True, index=True)
    company_id = Column(Integer, ForeignKey('companies.id'), nullable=False, index=True)
    reference = Column(String(150), nullable=False, index=True)
    ordre_travail = Column(String(150), nullable=True)
    piece = Column(String(150), nullable=True)
    quantite = Column(Integer, nullable=True)
    cout_unitaire = Column(Numeric, nullable=True)
    statut = Column(String(150), nullable=True)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())


class TechPreventivePlan(Base):
    """Plans d' entretien preventif."""
    __tablename__ = "tech_preventive_plans"
    __table_args__ = (
        UniqueConstraint('company_id', 'reference', name='uix_tech_preventive_plan_company_reference'),
    )
    id = Column(Integer, primary_key=True, index=True)
    company_id = Column(Integer, ForeignKey('companies.id'), nullable=False, index=True)
    reference = Column(String(150), nullable=False, index=True)
    vehicule = Column(String(150), nullable=True)
    operation = Column(String(150), nullable=True)
    intervalle_km = Column(Integer, nullable=True)
    derniere_realisation = Column(Date, nullable=True)
    statut = Column(String(150), nullable=True)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())


class TechBreakdownTicket(Base):
    """Billets de panne."""
    __tablename__ = "tech_breakdown_tickets"
    __table_args__ = (
        UniqueConstraint('company_id', 'reference', name='uix_tech_breakdown_ticke_company_reference'),
    )
    id = Column(Integer, primary_key=True, index=True)
    company_id = Column(Integer, ForeignKey('companies.id'), nullable=False, index=True)
    reference = Column(String(150), nullable=False, index=True)
    vehicule = Column(String(150), nullable=True)
    lieu = Column(String(150), nullable=True)
    severite = Column(String(150), nullable=True)
    recu = Column(DateTime(timezone=True), nullable=True)
    statut = Column(String(150), nullable=True)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())


class TechRepairReport(Base):
    """Rapports de reparation."""
    __tablename__ = "tech_repair_reports"
    __table_args__ = (
        UniqueConstraint('company_id', 'reference', name='uix_tech_repair_reports_company_reference'),
    )
    id = Column(Integer, primary_key=True, index=True)
    company_id = Column(Integer, ForeignKey('companies.id'), nullable=False, index=True)
    reference = Column(String(150), nullable=False, index=True)
    ordre_travail = Column(String(150), nullable=True)
    travaux_realises = Column(Text(2000), nullable=True)
    test_sortie_ok = Column(Boolean, nullable=True)
    date = Column(DateTime(timezone=True), nullable=True)
    statut = Column(String(150), nullable=True)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())


class TechCalibrationRecord(Base):
    """Fiches d' etalonnage."""
    __tablename__ = "tech_calibration_records"
    __table_args__ = (
        UniqueConstraint('company_id', 'reference', name='uix_tech_calibration_rec_company_reference'),
    )
    id = Column(Integer, primary_key=True, index=True)
    company_id = Column(Integer, ForeignKey('companies.id'), nullable=False, index=True)
    reference = Column(String(150), nullable=False, index=True)
    instrument = Column(String(150), nullable=True)
    tolerance = Column(String(150), nullable=True)
    date_etalonnage = Column(Date, nullable=True)
    prochaine_date = Column(Date, nullable=True)
    statut = Column(String(150), nullable=True)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())


class TechEquipmentChecklist(Base):
    """Controles d' equipement atelier."""
    __tablename__ = "tech_equipment_checklists"
    __table_args__ = (
        UniqueConstraint('company_id', 'reference', name='uix_tech_equipment_check_company_reference'),
    )
    id = Column(Integer, primary_key=True, index=True)
    company_id = Column(Integer, ForeignKey('companies.id'), nullable=False, index=True)
    reference = Column(String(150), nullable=False, index=True)
    equipement = Column(String(150), nullable=True)
    points_controles = Column(Integer, nullable=True)
    anomalies = Column(Integer, nullable=True)
    date = Column(DateTime(timezone=True), nullable=True)
    statut = Column(String(150), nullable=True)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())


class TechToolLoan(Base):
    """Prets d' outillage."""
    __tablename__ = "tech_tool_loans"
    __table_args__ = (
        UniqueConstraint('company_id', 'reference', name='uix_tech_tool_loans_company_reference'),
    )
    id = Column(Integer, primary_key=True, index=True)
    company_id = Column(Integer, ForeignKey('companies.id'), nullable=False, index=True)
    reference = Column(String(150), nullable=False, index=True)
    outil = Column(String(150), nullable=True)
    technicien = Column(String(150), nullable=True)
    sortie = Column(DateTime(timezone=True), nullable=True)
    retour = Column(DateTime(timezone=True), nullable=True)
    statut = Column(String(150), nullable=True)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())


class TechSafetyLockout(Base):
    """Consignations de securite."""
    __tablename__ = "tech_safety_lockouts"
    __table_args__ = (
        UniqueConstraint('company_id', 'reference', name='uix_tech_safety_lockouts_company_reference'),
    )
    id = Column(Integer, primary_key=True, index=True)
    company_id = Column(Integer, ForeignKey('companies.id'), nullable=False, index=True)
    reference = Column(String(150), nullable=False, index=True)
    installation = Column(String(150), nullable=True)
    motif = Column(String(150), nullable=True)
    pose = Column(DateTime(timezone=True), nullable=True)
    levee = Column(DateTime(timezone=True), nullable=True)
    statut = Column(String(150), nullable=True)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())


class TechWarrantyClaim(Base):
    """Reclamations de garantie."""
    __tablename__ = "tech_warranty_claims"
    __table_args__ = (
        UniqueConstraint('company_id', 'reference', name='uix_tech_warranty_claims_company_reference'),
    )
    id = Column(Integer, primary_key=True, index=True)
    company_id = Column(Integer, ForeignKey('companies.id'), nullable=False, index=True)
    reference = Column(String(150), nullable=False, index=True)
    piece = Column(String(150), nullable=True)
    fournisseur = Column(String(150), nullable=True)
    date_achat = Column(Date, nullable=True)
    montant = Column(Numeric, nullable=True)
    statut = Column(String(150), nullable=True)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())


class TechServiceAppointment(Base):
    """RDV d' atelier."""
    __tablename__ = "tech_service_appointments"
    __table_args__ = (
        UniqueConstraint('company_id', 'reference', name='uix_tech_service_appoint_company_reference'),
    )
    id = Column(Integer, primary_key=True, index=True)
    company_id = Column(Integer, ForeignKey('companies.id'), nullable=False, index=True)
    reference = Column(String(150), nullable=False, index=True)
    vehicule = Column(String(150), nullable=True)
    creneau = Column(DateTime(timezone=True), nullable=True)
    atelier = Column(String(150), nullable=True)
    duree_min = Column(Integer, nullable=True)
    statut = Column(String(150), nullable=True)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())


class TechLaborTimesheet(Base):
    """Feuilles de temps main d' oeuvre."""
    __tablename__ = "tech_labor_timesheets"
    __table_args__ = (
        UniqueConstraint('company_id', 'reference', name='uix_tech_labor_timesheet_company_reference'),
    )
    id = Column(Integer, primary_key=True, index=True)
    company_id = Column(Integer, ForeignKey('companies.id'), nullable=False, index=True)
    reference = Column(String(150), nullable=False, index=True)
    ordre_travail = Column(String(150), nullable=True)
    technicien = Column(String(150), nullable=True)
    minutes = Column(Integer, nullable=True)
    date = Column(Date, nullable=True)
    statut = Column(String(150), nullable=True)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())


class TechUpgradeRequest(Base):
    """Demandes d' amlioration."""
    __tablename__ = "tech_upgrade_requests"
    __table_args__ = (
        UniqueConstraint('company_id', 'reference', name='uix_tech_upgrade_request_company_reference'),
    )
    id = Column(Integer, primary_key=True, index=True)
    company_id = Column(Integer, ForeignKey('companies.id'), nullable=False, index=True)
    reference = Column(String(150), nullable=False, index=True)
    cible = Column(String(150), nullable=True)
    objet = Column(String(150), nullable=True)
    gain_attendu = Column(Text(2000), nullable=True)
    cout_estime = Column(Numeric, nullable=True)
    statut = Column(String(150), nullable=True)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())


class TechFailureAnalysis(Base):
    """Analyses de panne."""
    __tablename__ = "tech_failure_analyses"
    __table_args__ = (
        UniqueConstraint('company_id', 'reference', name='uix_tech_failure_analyse_company_reference'),
    )
    id = Column(Integer, primary_key=True, index=True)
    company_id = Column(Integer, ForeignKey('companies.id'), nullable=False, index=True)
    reference = Column(String(150), nullable=False, index=True)
    vehicule = Column(String(150), nullable=True)
    mode_defaillance = Column(String(150), nullable=True)
    frequence = Column(Integer, nullable=True)
    date = Column(Date, nullable=True)
    statut = Column(String(150), nullable=True)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())


class TechSpareRequest(Base):
    """Demandes de pieces."""
    __tablename__ = "tech_spare_requests"
    __table_args__ = (
        UniqueConstraint('company_id', 'reference', name='uix_tech_spare_requests_company_reference'),
    )
    id = Column(Integer, primary_key=True, index=True)
    company_id = Column(Integer, ForeignKey('companies.id'), nullable=False, index=True)
    reference = Column(String(150), nullable=False, index=True)
    piece = Column(String(150), nullable=True)
    quantite = Column(Integer, nullable=True)
    demandeur = Column(String(150), nullable=True)
    date = Column(DateTime(timezone=True), nullable=True)
    statut = Column(String(150), nullable=True)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())


class TechInspectionRecord(Base):
    """Fiches de controle technique."""
    __tablename__ = "tech_inspection_records"
    __table_args__ = (
        UniqueConstraint('company_id', 'reference', name='uix_tech_inspection_reco_company_reference'),
    )
    id = Column(Integer, primary_key=True, index=True)
    company_id = Column(Integer, ForeignKey('companies.id'), nullable=False, index=True)
    reference = Column(String(150), nullable=False, index=True)
    vehicule = Column(String(150), nullable=True)
    type_controle = Column(String(150), nullable=True)
    date_controle = Column(Date, nullable=True)
    validite = Column(Date, nullable=True)
    statut = Column(String(150), nullable=True)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())


class TechWorkOrderCost(Base):
    """Couts d' ordre de travail."""
    __tablename__ = "tech_work_order_costs"
    __table_args__ = (
        UniqueConstraint('company_id', 'reference', name='uix_tech_work_order_cost_company_reference'),
    )
    id = Column(Integer, primary_key=True, index=True)
    company_id = Column(Integer, ForeignKey('companies.id'), nullable=False, index=True)
    reference = Column(String(150), nullable=False, index=True)
    ordre_travail = Column(String(150), nullable=True)
    cout_pieces = Column(Numeric, nullable=True)
    cout_mo = Column(Numeric, nullable=True)
    date = Column(Date, nullable=True)
    statut = Column(String(150), nullable=True)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

