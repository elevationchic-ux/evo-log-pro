"""Modeles transit-douane (expansion approfondie generee).

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

class HsClassification_statut(str, enum.Enum):
    PROVISOIRE = "provisoire"
    VALIDE = "valide"
    ABROGE = "abroge"
    MODIFIE = "modifie"


class CustomsValuation_methode_evaluation(str, enum.Enum):
    TRANSACTION = "transaction"
    IDENTIQUE = "identique"
    SIMILAIRE = "similaire"
    DEDUCTION = "deduction"
    RECONSTITUEE = "reconstituee"
    SECOURS = "secours"


class CustomsValuation_statut(str, enum.Enum):
    BROUILLON = "brouillon"
    SOUMIS = "soumis"
    VALIDE = "valide"
    REDRESSE = "redresse"


class OriginCertificate_type_certificat(str, enum.Enum):
    FORM_A = "form_a"
    EUR1 = "eur1"
    CEMAC = "cemac"
    MOYEN_ORIENT = "moyen_orient"
    DECLARATION_FOURNISSEUR = "declaration_fournisseur"
    AUTRE = "autre"


class OriginCertificate_statut(str, enum.Enum):
    EMIS = "emis"
    VERIFIE = "verifie"
    EXPIRE = "expire"
    REVOQUE = "revoque"


class BondedWarehouse_statut(str, enum.Enum):
    OUVERT = "ouvert"
    SUSPENDU = "suspendu"
    RETIRE = "retire"
    CONTROLE_EN_COURS = "controle_en_cours"


class TransitGuarantee_type_garantie(str, enum.Enum):
    GLOBALE = "globale"
    INDIVIDUELLE = "individuelle"
    CAUTION_BANCAIRE = "caution_bancaire"
    HYPOTHECAIRE = "hypothecaire"


class TransitGuarantee_statut(str, enum.Enum):
    ACTIVE = "active"
    EXPIREE = "expiree"
    BLOQUEE = "bloquee"
    REVOQUEE = "revoquee"


class ExportDeclaration_regime(str, enum.Enum):
    DEFINITIF = "definitif"
    TEMPORAIRE = "temporaire"
    PERFECTIONNEMENT = "perfectionnement"


class ExportDeclaration_statut(str, enum.Enum):
    BROUILLON = "brouillon"
    DEPOSE = "depose"
    VALIDE = "valide"
    REFUSE = "refuse"
    MODIFIE = "modifie"


class ProhibitedGood_categorie(str, enum.Enum):
    INTERDICTION_TOTAL = "interdiction_total"
    LICENCE = "licence"
    CONTINGENTEMENT = "contingentement"
    NORME_QUALITE = "norme_qualite"
    SANITAIRE = "sanitaire"


class CustomsRegime_type_regime(str, enum.Enum):
    ADMISSION_TEMPORAIRE = "admission_temporaire"
    PERFECTIONNEMENT_ACTIF = "perfectionnement_actif"
    PERFECTIONNEMENT_PASSIF = "perfectionnement_passif"
    SOUS_DOUANE = "sous_douane"
    EXPORTATION_TEMPORAIRE = "exportation_temporaire"


class CustomsRegime_statut(str, enum.Enum):
    OUVERT = "ouvert"
    PROROGEE = "prorogee"
    CLOTURE = "cloture"
    MANQUANT = "manquant"


class PhysicalInspection_canal(str, enum.Enum):
    VERT = "vert"
    ORANGE = "orange"
    ROUGE = "rouge"
    BLEU = "bleu"


class PhysicalInspection_resultat(str, enum.Enum):
    CONFORME = "conforme"
    ECART_LEGER = "ecart_leger"
    ECART_SUBSTANTIEL = "ecart_substantiel"
    FRAUDE = "fraude"


class PhysicalInspection_statut(str, enum.Enum):
    PLANIFIEE = "planifiee"
    EN_COURS = "en_cours"
    CLOTUREE = "cloturee"


class DutyPayment_type_paiement(str, enum.Enum):
    ACOMPTE = "acompte"
    SOLDE = "solde"
    REMBOURSEMENT = "remboursement"
    PENALITE = "penalite"


class DutyPayment_mode_reglement(str, enum.Enum):
    VIREMENT = "virement"
    CHEQUE = "cheque"
    ESPECES = "especes"
    MOBILE_MONEY = "mobile_money"
    COMPENSATION = "compensation"


class DutyPayment_statut(str, enum.Enum):
    DU = "du"
    PARTIEL = "partiel"
    PAYE = "paye"
    REMBOURSE = "rembourse"
    CONTESTE = "conteste"


class TraderRegistration_type_operateur(str, enum.Enum):
    IMPORTATEUR = "importateur"
    EXPORTATEUR = "exportateur"
    TRANSITAIRE = "transitaire"
    COMMISSIONNAIRE = "commissionnaire"
    PRODUCTEUR = "producteur"


class TraderRegistration_statut_oea(str, enum.Enum):
    NON_OEA = "non_oea"
    OEA_SIMPLE = "oea_simple"
    OEA_COMPLET = "oea_complet"
    RETIREE = "retiree"


class TariffReference_categorie_produit(str, enum.Enum):
    BASIC = "basic"
    INTERMEDIAIRE = "intermediaire"
    FINI = "fini"
    CAPITAL = "capital"
    SENSIBLE = "sensible"


# ─── Modeles ──────────────────────────────────────────────────────────────────

class HsClassification(Base):
    """Classification tarifaire SH."""
    __tablename__ = "hs_classifications"
    __table_args__ = (
        UniqueConstraint('company_id', 'code_hs', name='uix_hs_classifications_company_code_hs'),
    )
    id = Column(Integer, primary_key=True, index=True)
    company_id = Column(Integer, ForeignKey('companies.id'), nullable=False, index=True)
    code_hs = Column(String(150), nullable=False, index=True)
    designation = Column(Text, nullable=True)
    section = Column(String(150), nullable=True)
    chapitre = Column(String(150), nullable=True)
    position = Column(String(150), nullable=True)
    sous_position = Column(String(150), nullable=True)
    unite_mesure = Column(String(150), nullable=True)
    statut = Column(_enum(HsClassification_statut), default=HsClassification_statut.PROVISOIRE)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())


class CustomsValuation(Base):
    """Valeur en douane / INCOTERMS."""
    __tablename__ = "customs_valuations"
    __table_args__ = (
        UniqueConstraint('company_id', 'reference_dossier', name='uix_customs_valuations_company_reference_dossi'),
    )
    id = Column(Integer, primary_key=True, index=True)
    company_id = Column(Integer, ForeignKey('companies.id'), nullable=False, index=True)
    reference_dossier = Column(String(150), nullable=False, index=True)
    dum_id = Column(Integer, nullable=True)
    methode_evaluation = Column(_enum(CustomsValuation_methode_evaluation), default=CustomsValuation_methode_evaluation.TRANSACTION)
    incoterm = Column(String(150), nullable=True)
    valeur_declaree_xaf = Column(Numeric, nullable=True)
    valeur_transport_xaf = Column(Numeric, nullable=True)
    valeur_assurance_xaf = Column(Numeric, nullable=True)
    valeur_douane_xaf = Column(Numeric, nullable=True)
    taux_change = Column(Numeric, nullable=True)
    date_evaluation = Column(Date, nullable=True)
    justification = Column(Text, nullable=True)
    statut = Column(_enum(CustomsValuation_statut), default=CustomsValuation_statut.BROUILLON)
    notes = Column(Text, nullable=True)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())


class OriginCertificate(Base):
    """Certificats d'origine."""
    __tablename__ = "origin_certificates"
    __table_args__ = (
        UniqueConstraint('company_id', 'numero_certificat', name='uix_origin_certificates_company_numero_certific'),
    )
    id = Column(Integer, primary_key=True, index=True)
    company_id = Column(Integer, ForeignKey('companies.id'), nullable=False, index=True)
    numero_certificat = Column(String(150), nullable=False, index=True)
    type_certificat = Column(_enum(OriginCertificate_type_certificat), default=OriginCertificate_type_certificat.FORM_A)
    pays_origine = Column(String(150), nullable=True)
    exportateur = Column(String(150), nullable=True)
    importateur = Column(String(150), nullable=True)
    dum_id = Column(Integer, nullable=True)
    date_emission = Column(Date, nullable=True)
    date_expiration = Column(Date, nullable=True)
    chambre_delivrance = Column(String(150), nullable=True)
    statut = Column(_enum(OriginCertificate_statut), default=OriginCertificate_statut.EMIS)
    notes = Column(Text, nullable=True)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())


class BondedWarehouse(Base):
    """Entrepots sous douane."""
    __tablename__ = "bonded_warehouses"
    __table_args__ = (
        UniqueConstraint('company_id', 'code_entrepot', name='uix_bonded_warehouses_company_code_entrepot'),
    )
    id = Column(Integer, primary_key=True, index=True)
    company_id = Column(Integer, ForeignKey('companies.id'), nullable=False, index=True)
    code_entrepot = Column(String(150), nullable=False, index=True)
    nom = Column(String(150), nullable=True)
    agrement_numero = Column(String(150), nullable=True)
    date_debut_agrement = Column(Date, nullable=True)
    date_fin_agrement = Column(Date, nullable=True)
    capacite_m2 = Column(Numeric, nullable=True)
    localisation = Column(String(150), nullable=True)
    gestionnaire = Column(String(150), nullable=True)
    statut = Column(_enum(BondedWarehouse_statut), default=BondedWarehouse_statut.OUVERT)
    notes = Column(Text, nullable=True)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())


class TransitGuarantee(Base):
    """Cautions et garanties."""
    __tablename__ = "transit_guarantees"
    __table_args__ = (
        UniqueConstraint('company_id', 'reference_caution', name='uix_transit_guarantees_company_reference_cauti'),
    )
    id = Column(Integer, primary_key=True, index=True)
    company_id = Column(Integer, ForeignKey('companies.id'), nullable=False, index=True)
    reference_caution = Column(String(150), nullable=False, index=True)
    type_garantie = Column(_enum(TransitGuarantee_type_garantie), default=TransitGuarantee_type_garantie.GLOBALE)
    banque_emettrice = Column(String(150), nullable=True)
    donneur_ordre = Column(String(150), nullable=True)
    montant_caution_xaf = Column(Numeric, nullable=True)
    date_debut = Column(Date, nullable=True)
    date_fin = Column(Date, nullable=True)
    statut = Column(_enum(TransitGuarantee_statut), default=TransitGuarantee_statut.ACTIVE)
    notes = Column(Text, nullable=True)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())


class ExportDeclaration(Base):
    """Declarations export."""
    __tablename__ = "export_declarations"
    __table_args__ = (
        UniqueConstraint('company_id', 'numero_dge', name='uix_export_declarations_company_numero_dge'),
    )
    id = Column(Integer, primary_key=True, index=True)
    company_id = Column(Integer, ForeignKey('companies.id'), nullable=False, index=True)
    numero_dge = Column(String(150), nullable=False, index=True)
    declarant = Column(String(150), nullable=True)
    exportateur = Column(String(150), nullable=True)
    pays_destination = Column(String(150), nullable=True)
    valeur_xaf = Column(Numeric, nullable=True)
    poids_net_kg = Column(Numeric, nullable=True)
    regime = Column(_enum(ExportDeclaration_regime), default=ExportDeclaration_regime.DEFINITIF)
    date_depot = Column(Date, nullable=True)
    date_validation = Column(Date, nullable=True)
    statut = Column(_enum(ExportDeclaration_statut), default=ExportDeclaration_statut.BROUILLON)
    notes = Column(Text, nullable=True)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())


class ProhibitedGood(Base):
    """Marchandises prohibees / contingentees."""
    __tablename__ = "prohibited_goods"
    __table_args__ = (
        UniqueConstraint('company_id', 'code_produit', name='uix_prohibited_goods_company_code_produit'),
    )
    id = Column(Integer, primary_key=True, index=True)
    company_id = Column(Integer, ForeignKey('companies.id'), nullable=False, index=True)
    code_produit = Column(String(150), nullable=False, index=True)
    designation = Column(Text, nullable=True)
    code_hs = Column(String(150), nullable=True)
    categorie = Column(_enum(ProhibitedGood_categorie), default=ProhibitedGood_categorie.LICENCE)
    base_legale = Column(Text, nullable=True)
    autorite_competente = Column(String(150), nullable=True)
    conditions_regime = Column(Text, nullable=True)
    actif = Column(Boolean, nullable=True)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())


class CustomsRegime(Base):
    """Regimes economiques."""
    __tablename__ = "customs_regimes"
    __table_args__ = (
        UniqueConstraint('company_id', 'reference_regime', name='uix_customs_regimes_company_reference_regim'),
    )
    id = Column(Integer, primary_key=True, index=True)
    company_id = Column(Integer, ForeignKey('companies.id'), nullable=False, index=True)
    reference_regime = Column(String(150), nullable=False, index=True)
    dum_id = Column(Integer, nullable=True)
    type_regime = Column(_enum(CustomsRegime_type_regime), default=CustomsRegime_type_regime.ADMISSION_TEMPORAIRE)
    duree_max_mois = Column(Integer, nullable=True)
    date_appllication = Column(Date, nullable=True)
    date_echeance = Column(Date, nullable=True)
    caution_associee = Column(String(150), nullable=True)
    statut = Column(_enum(CustomsRegime_statut), default=CustomsRegime_statut.OUVERT)
    notes = Column(Text, nullable=True)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())


class PhysicalInspection(Base):
    """Visites et inspections physiques."""
    __tablename__ = "physical_inspections"
    __table_args__ = (
        UniqueConstraint('company_id', 'numero_pv', name='uix_physical_inspections_company_numero_pv'),
    )
    id = Column(Integer, primary_key=True, index=True)
    company_id = Column(Integer, ForeignKey('companies.id'), nullable=False, index=True)
    numero_pv = Column(String(150), nullable=False, index=True)
    dum_id = Column(Integer, nullable=True)
    canal = Column(_enum(PhysicalInspection_canal), default=PhysicalInspection_canal.VERT)
    inspecteur = Column(String(150), nullable=True)
    date_inspection = Column(DateTime(timezone=True), nullable=True)
    lieu = Column(String(150), nullable=True)
    resultat = Column(_enum(PhysicalInspection_resultat), default=PhysicalInspection_resultat.CONFORME)
    ecart_poids_kg = Column(Numeric, nullable=True)
    ecart_colis = Column(Integer, nullable=True)
    observations = Column(Text, nullable=True)
    statut = Column(_enum(PhysicalInspection_statut), default=PhysicalInspection_statut.PLANIFIEE)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())


class DutyPayment(Base):
    """Paiement droits et taxes."""
    __tablename__ = "duty_payments"
    __table_args__ = (
        UniqueConstraint('company_id', 'numero_quittance', name='uix_duty_payments_company_numero_quittanc'),
    )
    id = Column(Integer, primary_key=True, index=True)
    company_id = Column(Integer, ForeignKey('companies.id'), nullable=False, index=True)
    numero_quittance = Column(String(150), nullable=False, index=True)
    dum_id = Column(Integer, nullable=True)
    type_paiement = Column(_enum(DutyPayment_type_paiement), default=DutyPayment_type_paiement.SOLDE)
    droits_percus_xaf = Column(Numeric, nullable=True)
    tva_xaf = Column(Numeric, nullable=True)
    taxe_statistique_xaf = Column(Numeric, nullable=True)
    redevance_id = Column(String(150), nullable=True)
    mode_reglement = Column(_enum(DutyPayment_mode_reglement), default=DutyPayment_mode_reglement.VIREMENT)
    date_paiement = Column(Date, nullable=True)
    statut = Column(_enum(DutyPayment_statut), default=DutyPayment_statut.DU)
    notes = Column(Text, nullable=True)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())


class TraderRegistration(Base):
    """Enregistrement operateur economique."""
    __tablename__ = "trader_registrations"
    __table_args__ = (
        UniqueConstraint('company_id', 'numero_operateur', name='uix_trader_registrations_company_numero_operateu'),
    )
    id = Column(Integer, primary_key=True, index=True)
    company_id = Column(Integer, ForeignKey('companies.id'), nullable=False, index=True)
    numero_operateur = Column(String(150), nullable=False, index=True)
    raison_sociale = Column(String(150), nullable=True)
    niu = Column(String(150), nullable=True)
    rc_number = Column(String(150), nullable=True)
    type_operateur = Column(_enum(TraderRegistration_type_operateur), default=TraderRegistration_type_operateur.IMPORTATEUR)
    statut_oea = Column(_enum(TraderRegistration_statut_oea), default=TraderRegistration_statut_oea.NON_OEA)
    date_agrement = Column(Date, nullable=True)
    date_expiration = Column(Date, nullable=True)
    contact_email = Column(String(150), nullable=True)
    contact_telephone = Column(String(150), nullable=True)
    notes = Column(Text, nullable=True)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())


class TariffReference(Base):
    """Tarif integre CEMAC."""
    __tablename__ = "tariff_references"
    __table_args__ = (
        UniqueConstraint('company_id', 'code_ligne_tarifaire', name='uix_tariff_references_company_code_ligne_tari'),
    )
    id = Column(Integer, primary_key=True, index=True)
    company_id = Column(Integer, ForeignKey('companies.id'), nullable=False, index=True)
    code_ligne_tarifaire = Column(String(150), nullable=False, index=True)
    code_hs = Column(String(150), nullable=True)
    designation = Column(Text, nullable=True)
    droit_base_pct = Column(Numeric, nullable=True)
    cotisation_compensatoire_pct = Column(Numeric, nullable=True)
    taxe_foretiaire_pct = Column(Numeric, nullable=True)
    redevance_statistique_pct = Column(Numeric, nullable=True)
    tva_pct = Column(Numeric, nullable=True)
    categorie_produit = Column(_enum(TariffReference_categorie_produit), default=TariffReference_categorie_produit.BASIC)
    date_application = Column(Date, nullable=True)
    date_fin = Column(Date, nullable=True)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

