"""Modeles portail-magasinier (expansion approfondie generee).

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

class MagcPickingTask_statut(str, enum.Enum):
    A_FAIRE = "a_faire"
    EN_COURS = "en_cours"
    FAIT = "fait"
    RUPTURE = "rupture"


class MagcPackingSlip_statut(str, enum.Enum):
    EN_PREPARATION = "en_preparation"
    EMBALLE = "emballe"
    MANQUANT = "manquant"
    EXPEDIE = "expedie"


class MagcPutawayTask_statut(str, enum.Enum):
    A_FAIRE = "a_faire"
    EN_COURS = "en_cours"
    FAIT = "fait"
    BLOQUE = "bloque"


class MagcCycleCount_statut(str, enum.Enum):
    PLANIFIE = "planifie"
    FAIT = "fait"
    ECART = "ecart"
    REGULARISE = "regularise"


class MagcInternalMove_statut(str, enum.Enum):
    DEMANDE = "demande"
    EN_COURS = "en_cours"
    FAIT = "fait"
    ANNULE = "annule"


class MagcGoodsIssue_statut(str, enum.Enum):
    DEMANDE = "demande"
    SERVI = "servi"
    PARTIEL = "partiel"
    RUPTURE = "rupture"


class MagcReturnProcessing_retour(str, enum.Enum):
    CLIENT = "client"
    FOURNISSEUR = "fournisseur"
    INTERNE = "interne"


class MagcReturnProcessing_statut(str, enum.Enum):
    RECU = "recu"
    CONTROLE = "controle"
    REINTEGRE = "reintegre"
    REFORME = "reforme"


class MagcLabelPrint_type_etiquette(str, enum.Enum):
    ARTICLE = "article"
    PALETTE = "palette"
    COLIS = "colis"
    DANGER = "danger"


class MagcLabelPrint_statut(str, enum.Enum):
    EN_ATTENTE = "en_attente"
    IMPRIME = "imprime"
    ERREUR = "erreur"


class MagcPalletBuild_statut(str, enum.Enum):
    EN_COURS = "en_cours"
    COMPACTE = "compacte"
    FILMEE = "filmee"
    BLOQUE = "bloque"


class MagcEquipmentCheck_statut(str, enum.Enum):
    CONFORME = "conforme"
    ANOMALIE = "anomalie"
    IMMOBILISE = "immobilise"


class MagcSafetyInspection_statut(str, enum.Enum):
    FAITE = "faite"
    SANS_ANOMALIE = "sans_anomalie"
    A_SUIVRE = "a_suivre"


class MagcSpillCleanup_statut(str, enum.Enum):
    DETECTE = "detecte"
    CONTENU = "contenu"
    NETTOYE = "nettoye"
    CLOTURE = "cloture"


class MagcLoadingCheck_statut(str, enum.Enum):
    EN_COURS = "en_cours"
    COMPLET = "complet"
    ECART = "ecart"
    PARTI = "parti"


class MagcReceivingCheck_statut(str, enum.Enum):
    EN_COURS = "en_cours"
    CONFORME = "conforme"
    LITIGE = "litige"
    REJETE = "rejete"


class MagcPutawayException_type_probleme(str, enum.Enum):
    EMPLACEMENT_PLEIN = "emplacement_plein"
    ACCES = "acces"
    ETIQUETTE = "etiquette"
    DAMAGE = "damage"


class MagcPutawayException_statut(str, enum.Enum):
    OUVERTE = "ouverte"
    EN_COURS = "en_cours"
    RESOLUE = "resolue"


class MagcOrderStaging_statut(str, enum.Enum):
    EN_COURS = "en_cours"
    PRET = "pret"
    EN_ATTENTE_ENLEVEMENT = "en_attente_enlevement"
    ENLEVE = "enleve"


class MagcColdChainCheck_statut(str, enum.Enum):
    CONFORME = "conforme"
    DERIVE = "derive"
    RUPTURE = "rupture"


class MagcHazmatHandling_classe(str, enum.Enum):
    V_1 = "1"
    V_2 = "2"
    V_3 = "3"
    V_5 = "5"
    V_6 = "6"
    V_8 = "8"
    V_9 = "9"


class MagcHazmatHandling_statut(str, enum.Enum):
    PREVU = "prevu"
    EN_COURS = "en_cours"
    STOCKE = "stocke"
    EVACUE = "evacue"


class MagcDockAssignment_statut(str, enum.Enum):
    PLANIFIE = "planifie"
    OCCUPE = "occupe"
    LIBERE = "libere"
    NO_SHOW = "no_show"


# ─── Modeles ──────────────────────────────────────────────────────────────────

class MagcPickingTask(Base):
    """Taches de preparation."""
    __tablename__ = "magc_picking_tasks"
    __table_args__ = (
        UniqueConstraint('company_id', 'reference', name='uix_magc_picking_tasks_company_reference'),
    )
    id = Column(Integer, primary_key=True, index=True)
    company_id = Column(Integer, ForeignKey('companies.id'), nullable=False, index=True)
    reference = Column(String(150), nullable=False, index=True)
    ordre = Column(String(150), nullable=True)
    emplacement = Column(String(150), nullable=True)
    quantite = Column(Integer, nullable=True)
    prepareur = Column(String(150), nullable=True)
    statut = Column(String(150), nullable=True)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())


class MagcPackingSlip(Base):
    """Bons de colisage."""
    __tablename__ = "magc_packing_slips"
    __table_args__ = (
        UniqueConstraint('company_id', 'reference', name='uix_magc_packing_slips_company_reference'),
    )
    id = Column(Integer, primary_key=True, index=True)
    company_id = Column(Integer, ForeignKey('companies.id'), nullable=False, index=True)
    reference = Column(String(150), nullable=False, index=True)
    commande = Column(String(150), nullable=True)
    nb_colis = Column(Integer, nullable=True)
    poids = Column(Numeric, nullable=True)
    operateur = Column(String(150), nullable=True)
    statut = Column(String(150), nullable=True)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())


class MagcPutawayTask(Base):
    """Taches de mise en place."""
    __tablename__ = "magc_putaway_tasks"
    __table_args__ = (
        UniqueConstraint('company_id', 'reference', name='uix_magc_putaway_tasks_company_reference'),
    )
    id = Column(Integer, primary_key=True, index=True)
    company_id = Column(Integer, ForeignKey('companies.id'), nullable=False, index=True)
    reference = Column(String(150), nullable=False, index=True)
    article = Column(String(150), nullable=True)
    quantite = Column(Integer, nullable=True)
    de = Column(String(150), nullable=True)
    vers = Column(String(150), nullable=True)
    statut = Column(String(150), nullable=True)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())


class MagcCycleCount(Base):
    """Inventaires tournants."""
    __tablename__ = "magc_cycle_counts"
    __table_args__ = (
        UniqueConstraint('company_id', 'reference', name='uix_magc_cycle_counts_company_reference'),
    )
    id = Column(Integer, primary_key=True, index=True)
    company_id = Column(Integer, ForeignKey('companies.id'), nullable=False, index=True)
    reference = Column(String(150), nullable=False, index=True)
    emplacement = Column(String(150), nullable=True)
    theorique = Column(Integer, nullable=True)
    physique = Column(Integer, nullable=True)
    compteur = Column(String(150), nullable=True)
    statut = Column(String(150), nullable=True)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())


class MagcInternalMove(Base):
    """Transferts internes."""
    __tablename__ = "magc_internal_moves"
    __table_args__ = (
        UniqueConstraint('company_id', 'reference', name='uix_magc_internal_moves_company_reference'),
    )
    id = Column(Integer, primary_key=True, index=True)
    company_id = Column(Integer, ForeignKey('companies.id'), nullable=False, index=True)
    reference = Column(String(150), nullable=False, index=True)
    article = Column(String(150), nullable=True)
    quantite = Column(Integer, nullable=True)
    origine = Column(String(150), nullable=True)
    destination = Column(String(150), nullable=True)
    statut = Column(String(150), nullable=True)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())


class MagcGoodsIssue(Base):
    """Sorties de magasin."""
    __tablename__ = "magc_goods_issues"
    __table_args__ = (
        UniqueConstraint('company_id', 'reference', name='uix_magc_goods_issues_company_reference'),
    )
    id = Column(Integer, primary_key=True, index=True)
    company_id = Column(Integer, ForeignKey('companies.id'), nullable=False, index=True)
    reference = Column(String(150), nullable=False, index=True)
    demande = Column(String(150), nullable=True)
    article = Column(String(150), nullable=True)
    quantite = Column(Integer, nullable=True)
    beneficiaire = Column(String(150), nullable=True)
    statut = Column(String(150), nullable=True)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())


class MagcReturnProcessing(Base):
    """Traitement des retours."""
    __tablename__ = "magc_returns"
    __table_args__ = (
        UniqueConstraint('company_id', 'reference', name='uix_magc_returns_company_reference'),
    )
    id = Column(Integer, primary_key=True, index=True)
    company_id = Column(Integer, ForeignKey('companies.id'), nullable=False, index=True)
    reference = Column(String(150), nullable=False, index=True)
    retour = Column(String(150), nullable=True)
    article = Column(String(150), nullable=True)
    quantite = Column(Integer, nullable=True)
    motif = Column(String(150), nullable=True)
    statut = Column(String(150), nullable=True)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())


class MagcLabelPrint(Base):
    """Edition d' etiquettes."""
    __tablename__ = "magc_label_prints"
    __table_args__ = (
        UniqueConstraint('company_id', 'reference', name='uix_magc_label_prints_company_reference'),
    )
    id = Column(Integer, primary_key=True, index=True)
    company_id = Column(Integer, ForeignKey('companies.id'), nullable=False, index=True)
    reference = Column(String(150), nullable=False, index=True)
    article = Column(String(150), nullable=True)
    nombre = Column(Integer, nullable=True)
    type_etiquette = Column(String(150), nullable=True)
    operateur = Column(String(150), nullable=True)
    statut = Column(String(150), nullable=True)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())


class MagcPalletBuild(Base):
    """Constitution de palettes."""
    __tablename__ = "magc_pallet_builds"
    __table_args__ = (
        UniqueConstraint('company_id', 'reference', name='uix_magc_pallet_builds_company_reference'),
    )
    id = Column(Integer, primary_key=True, index=True)
    company_id = Column(Integer, ForeignKey('companies.id'), nullable=False, index=True)
    reference = Column(String(150), nullable=False, index=True)
    commande = Column(String(150), nullable=True)
    nb_cartons = Column(Integer, nullable=True)
    hauteur_cm = Column(Integer, nullable=True)
    poids_total = Column(Numeric, nullable=True)
    statut = Column(String(150), nullable=True)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())


class MagcEquipmentCheck(Base):
    """Controles engins."""
    __tablename__ = "magc_equipment_checks"
    __table_args__ = (
        UniqueConstraint('company_id', 'reference', name='uix_magc_equipment_check_company_reference'),
    )
    id = Column(Integer, primary_key=True, index=True)
    company_id = Column(Integer, ForeignKey('companies.id'), nullable=False, index=True)
    reference = Column(String(150), nullable=False, index=True)
    equipment = Column(String(150), nullable=True)
    numero = Column(String(150), nullable=True)
    controleur = Column(String(150), nullable=True)
    date_controle = Column(DateTime(timezone=True), nullable=True)
    statut = Column(String(150), nullable=True)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())


class MagcSafetyInspection(Base):
    """Rondes de securite."""
    __tablename__ = "magc_safety_inspections"
    __table_args__ = (
        UniqueConstraint('company_id', 'reference', name='uix_magc_safety_inspecti_company_reference'),
    )
    id = Column(Integer, primary_key=True, index=True)
    company_id = Column(Integer, ForeignKey('companies.id'), nullable=False, index=True)
    reference = Column(String(150), nullable=False, index=True)
    zone = Column(String(150), nullable=True)
    inspecteur = Column(String(150), nullable=True)
    date = Column(DateTime(timezone=True), nullable=True)
    anomalies = Column(Integer, nullable=True)
    statut = Column(String(150), nullable=True)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())


class MagcSpillCleanup(Base):
    """Nettoyages de deversement."""
    __tablename__ = "magc_spill_cleanups"
    __table_args__ = (
        UniqueConstraint('company_id', 'reference', name='uix_magc_spill_cleanups_company_reference'),
    )
    id = Column(Integer, primary_key=True, index=True)
    company_id = Column(Integer, ForeignKey('companies.id'), nullable=False, index=True)
    reference = Column(String(150), nullable=False, index=True)
    zone = Column(String(150), nullable=True)
    produit = Column(String(150), nullable=True)
    volume = Column(Numeric, nullable=True)
    date = Column(DateTime(timezone=True), nullable=True)
    statut = Column(String(150), nullable=True)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())


class MagcLoadingCheck(Base):
    """Controles de chargement."""
    __tablename__ = "magc_loading_checks"
    __table_args__ = (
        UniqueConstraint('company_id', 'reference', name='uix_magc_loading_checks_company_reference'),
    )
    id = Column(Integer, primary_key=True, index=True)
    company_id = Column(Integer, ForeignKey('companies.id'), nullable=False, index=True)
    reference = Column(String(150), nullable=False, index=True)
    chargement = Column(String(150), nullable=True)
    camion = Column(String(150), nullable=True)
    nb_colis = Column(Integer, nullable=True)
    chargeur = Column(String(150), nullable=True)
    statut = Column(String(150), nullable=True)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())


class MagcReceivingCheck(Base):
    """Controles de reception."""
    __tablename__ = "magc_receiving_checks"
    __table_args__ = (
        UniqueConstraint('company_id', 'reference', name='uix_magc_receiving_check_company_reference'),
    )
    id = Column(Integer, primary_key=True, index=True)
    company_id = Column(Integer, ForeignKey('companies.id'), nullable=False, index=True)
    reference = Column(String(150), nullable=False, index=True)
    reception = Column(String(150), nullable=True)
    fournisseur = Column(String(150), nullable=True)
    nb_colis = Column(Integer, nullable=True)
    conforme = Column(Boolean, nullable=True)
    statut = Column(String(150), nullable=True)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())


class MagcPutawayException(Base):
    """Exceptions de rangement."""
    __tablename__ = "magc_putaway_exceptions"
    __table_args__ = (
        UniqueConstraint('company_id', 'reference', name='uix_magc_putaway_excepti_company_reference'),
    )
    id = Column(Integer, primary_key=True, index=True)
    company_id = Column(Integer, ForeignKey('companies.id'), nullable=False, index=True)
    reference = Column(String(150), nullable=False, index=True)
    article = Column(String(150), nullable=True)
    emplacement = Column(String(150), nullable=True)
    type_probleme = Column(String(150), nullable=True)
    signale_le = Column(DateTime(timezone=True), nullable=True)
    statut = Column(String(150), nullable=True)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())


class MagcOrderStaging(Base):
    """Zone de pre-expedition."""
    __tablename__ = "magc_order_staging"
    __table_args__ = (
        UniqueConstraint('company_id', 'reference', name='uix_magc_order_staging_company_reference'),
    )
    id = Column(Integer, primary_key=True, index=True)
    company_id = Column(Integer, ForeignKey('companies.id'), nullable=False, index=True)
    reference = Column(String(150), nullable=False, index=True)
    commande = Column(String(150), nullable=True)
    zone_prea = Column(String(150), nullable=True)
    nb_lignes = Column(Integer, nullable=True)
    operateur = Column(String(150), nullable=True)
    statut = Column(String(150), nullable=True)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())


class MagcColdChainCheck(Base):
    """Controles chaine du froid."""
    __tablename__ = "magc_cold_checks"
    __table_args__ = (
        UniqueConstraint('company_id', 'reference', name='uix_magc_cold_checks_company_reference'),
    )
    id = Column(Integer, primary_key=True, index=True)
    company_id = Column(Integer, ForeignKey('companies.id'), nullable=False, index=True)
    reference = Column(String(150), nullable=False, index=True)
    chambre_froide = Column(String(150), nullable=True)
    temperature_c = Column(Numeric, nullable=True)
    seuil_mini = Column(Numeric, nullable=True)
    seuil_maxi = Column(Numeric, nullable=True)
    statut = Column(String(150), nullable=True)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())


class MagcHazmatHandling(Base):
    """Manutention matieres dangereuses."""
    __tablename__ = "magc_hazmat_handling"
    __table_args__ = (
        UniqueConstraint('company_id', 'reference', name='uix_magc_hazmat_handling_company_reference'),
    )
    id = Column(Integer, primary_key=True, index=True)
    company_id = Column(Integer, ForeignKey('companies.id'), nullable=False, index=True)
    reference = Column(String(150), nullable=False, index=True)
    matiere = Column(String(150), nullable=True)
    classe = Column(String(150), nullable=True)
    quantite = Column(Numeric, nullable=True)
    operateur = Column(String(150), nullable=True)
    statut = Column(String(150), nullable=True)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())


class MagcDockAssignment(Base):
    """Affectations de quai."""
    __tablename__ = "magc_dock_assignments"
    __table_args__ = (
        UniqueConstraint('company_id', 'reference', name='uix_magc_dock_assignment_company_reference'),
    )
    id = Column(Integer, primary_key=True, index=True)
    company_id = Column(Integer, ForeignKey('companies.id'), nullable=False, index=True)
    reference = Column(String(150), nullable=False, index=True)
    quai = Column(String(150), nullable=True)
    camion = Column(String(150), nullable=True)
    creneau = Column(DateTime(timezone=True), nullable=True)
    operateur = Column(String(150), nullable=True)
    statut = Column(String(150), nullable=True)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

