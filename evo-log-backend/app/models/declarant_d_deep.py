"""Modeles portail-declarant (expansion approfondie generee).

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

class DeclCustomsDeclaration_regime(str, enum.Enum):
    IMPORT = "import"
    EXPORT = "export"
    TRANSIT = "transit"
    ENTREPOT = "entrepot"


class DeclCustomsDeclaration_statut(str, enum.Enum):
    PREPARATION = "preparation"
    DEPOSEE = "deposee"
    VALIDEE = "validee"
    REJETEE = "rejetee"
    CONTROLE = "controle"


class DeclHsClassification_statut(str, enum.Enum):
    PROPOSE = "propose"
    LIE = "lie"
    REVOQUE = "revoque"
    A_REVISER = "a_reviser"


class DeclOriginCertificate_type(str, enum.Enum):
    EUR1 = "eur1"
    A.TR = "a.tr"
    CERTINE = "certine"
    ATTA_ORIGINE = "atta_origine"


class DeclOriginCertificate_statut(str, enum.Enum):
    DEMANDE = "demande"
    EMIS = "emis"
    EXPIRE = "expire"
    REVOQUE = "revoque"


class DeclCustomsValuation_methode(str, enum.Enum):
    TRANSACTION = "transaction"
    IDENTIQUE = "identique"
    SIMILAIRE = "similaire"
    DEDUCTION = "deduction"
    RECONSTITUE = "reconstitue"


class DeclCustomsValuation_statut(str, enum.Enum):
    CALCULE = "calcule"
    SOUMIS = "soumis"
    ACCEPTE = "accepte"
    RECONTESTE = "reconteste"


class DeclIncotermsRecord_code(str, enum.Enum):
    EXW = "exw"
    FCA = "fca"
    FOB = "fob"
    CFR = "cfr"
    CIF = "cif"
    DAP = "dap"
    DPU = "dpu"
    DDP = "ddp"


class DeclIncotermsRecord_statut(str, enum.Enum):
    PROPOSE = "propose"
    ACCEPTE = "accepte"
    AMENDE = "amende"
    CADUC = "caduc"


class DeclImportLicense_statut(str, enum.Enum):
    DEMANDEE = "demandee"
    OCTROYEE = "octroyee"
    EPUISEE = "epuisee"
    EXPIREE = "expiree"


class DeclExportLicense_usage(str, enum.Enum):
    CIVIL = "civil"
    DOUBLE_USAGE = "double_usage"
    MILITAIRE = "militaire"


class DeclExportLicense_statut(str, enum.Enum):
    INSTRUIT = "instruit"
    ACCORD = "accord"
    REFUSE = "refuse"
    EXPIRE = "expire"


class DeclPreClearance_statut(str, enum.Enum):
    PREPARE = "prepare"
    DEPOSE = "depose"
    ACCEPTE = "accepte"
    REFUSE = "refuse"
    TARDIF = "tardif"


class DeclCustomsInvoice_devise(str, enum.Enum):
    XOF = "xof"
    EUR = "eur"
    USD = "usd"


class DeclCustomsInvoice_statut(str, enum.Enum):
    JOINT = "joint"
    VERIFIE = "verifie"
    ECART = "ecart"
    MANQUANT = "manquant"


class DeclPackingList_statut(str, enum.Enum):
    ETABLI = "etabli"
    CONTROLE = "controle"
    ECART = "ecart"
    VALIDE = "valide"


class DeclCertificateAnalysis_statut(str, enum.Enum):
    EN_COURS = "en_cours"
    CONFORME = "conforme"
    NON_CONFORME = "non_conforme"
    REFAIRE = "refaire"


class DeclPhytosanitaryApp_statut(str, enum.Enum):
    DEMANDE = "demande"
    CONTROLE = "controle"
    DELIVRE = "delivre"
    REFUSE = "refuse"


class DeclCustomsPayment_type_droit(str, enum.Enum):
    DROIT_COMMUN = "droit_commun"
    TVA_IMPORT = "tva_import"
    STATISTIQUE = "statistique"
    PARAFISCAL = "parafiscal"


class DeclCustomsPayment_statut(str, enum.Enum):
    LIQUIDE = "liquide"
    A_PAYER = "a_payer"
    PAYE = "paye"
    CONTESTE = "conteste"


class DeclTransitDocument_type(str, enum.Enum):
    T1 = "t1"
    T2 = "t2"
    TD = "td"
    CARNET_TIR = "carnet_tir"


class DeclTransitDocument_statut(str, enum.Enum):
    EMIS = "emis"
    EN_ROUTE = "en_route"
    DECHARGE = "decharge"
    NON_DECHARGE = "non_decharge"


class DeclDangerousGoods_statut(str, enum.Enum):
    PREPAREE = "preparee"
    VERIFIEE = "verifiee"
    ACCEPT = "accept"
    REFUSEE = "refusee"


class DeclBondedWarehouseEntry_statut(str, enum.Enum):
    EN_ENTREPOT = "en_entrepot"
    PARTIELLE = "partielle"
    SORTIE = "sortie"
    LITIGE = "litige"


class DeclDutyReliefClaim_motif(str, enum.Enum):
    INVESTISSEMENT = "investissement"
    REEXPORT = "reexport"
    ENTREPOT = "entrepot"
    ACCORD = "accord"


class DeclDutyReliefClaim_statut(str, enum.Enum):
    DEMANDE = "demande"
    INSTRUIT = "instruit"
    ACCORD = "accord"
    REFUS = "refus"


class DeclManifestCorrection_statut(str, enum.Enum):
    SOUMISE = "soumise"
    EN_COURS = "en_cours"
    APPLIQUEE = "appliquee"
    REJETEE = "rejetee"


class DeclCustomsAuditSupport_statut(str, enum.Enum):
    DEMANDE = "demande"
    RASSEMBLE = "rassemble"
    SOUVIS = "souvis"
    CLOTURE = "cloture"


# ─── Modeles ──────────────────────────────────────────────────────────────────

class DeclCustomsDeclaration(Base):
    """Declarations en douane."""
    __tablename__ = "decl_customs_declarations"
    __table_args__ = (
        UniqueConstraint('company_id', 'reference', name='uix_decl_customs_declara_company_reference'),
    )
    id = Column(Integer, primary_key=True, index=True)
    company_id = Column(Integer, ForeignKey('companies.id'), nullable=False, index=True)
    reference = Column(String(150), nullable=False, index=True)
    masse = Column(String(150), nullable=True)
    regime = Column(String(150), nullable=True)
    valeur_douane = Column(Numeric, nullable=True)
    date_depot = Column(DateTime(timezone=True), nullable=True)
    statut = Column(String(150), nullable=True)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())


class DeclHsClassification(Base):
    """Classifications douanieres (HS)."""
    __tablename__ = "decl_hs_classifications"
    __table_args__ = (
        UniqueConstraint('company_id', 'reference', name='uix_decl_hs_classificati_company_reference'),
    )
    id = Column(Integer, primary_key=True, index=True)
    company_id = Column(Integer, ForeignKey('companies.id'), nullable=False, index=True)
    reference = Column(String(150), nullable=False, index=True)
    designation = Column(String(150), nullable=True)
    code_hs = Column(String(150), nullable=True)
    taux_droit = Column(Numeric, nullable=True)
    date = Column(Date, nullable=True)
    statut = Column(String(150), nullable=True)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())


class DeclOriginCertificate(Base):
    """Certificats d' origine."""
    __tablename__ = "decl_origin_certificates"
    __table_args__ = (
        UniqueConstraint('company_id', 'reference', name='uix_decl_origin_certific_company_reference'),
    )
    id = Column(Integer, primary_key=True, index=True)
    company_id = Column(Integer, ForeignKey('companies.id'), nullable=False, index=True)
    reference = Column(String(150), nullable=False, index=True)
    type = Column(String(150), nullable=True)
    pays_origine = Column(String(150), nullable=True)
    numero = Column(String(150), nullable=True)
    date_emission = Column(Date, nullable=True)
    statut = Column(String(150), nullable=True)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())


class DeclCustomsValuation(Base):
    """Valeurs en douane."""
    __tablename__ = "decl_customs_valuations"
    __table_args__ = (
        UniqueConstraint('company_id', 'reference', name='uix_decl_customs_valuati_company_reference'),
    )
    id = Column(Integer, primary_key=True, index=True)
    company_id = Column(Integer, ForeignKey('companies.id'), nullable=False, index=True)
    reference = Column(String(150), nullable=False, index=True)
    masse = Column(String(150), nullable=True)
    methode = Column(String(150), nullable=True)
    valeur = Column(Numeric, nullable=True)
    date = Column(Date, nullable=True)
    statut = Column(String(150), nullable=True)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())


class DeclIncotermsRecord(Base):
    """Incoterms."""
    __tablename__ = "decl_incoterms"
    __table_args__ = (
        UniqueConstraint('company_id', 'reference', name='uix_decl_incoterms_company_reference'),
    )
    id = Column(Integer, primary_key=True, index=True)
    company_id = Column(Integer, ForeignKey('companies.id'), nullable=False, index=True)
    reference = Column(String(150), nullable=False, index=True)
    code = Column(String(150), nullable=True)
    lieu = Column(String(150), nullable=True)
    vendeur = Column(String(150), nullable=True)
    acheteur = Column(String(150), nullable=True)
    statut = Column(String(150), nullable=True)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())


class DeclImportLicense(Base):
    """Licences d' importation."""
    __tablename__ = "decl_import_licenses"
    __table_args__ = (
        UniqueConstraint('company_id', 'reference', name='uix_decl_import_licenses_company_reference'),
    )
    id = Column(Integer, primary_key=True, index=True)
    company_id = Column(Integer, ForeignKey('companies.id'), nullable=False, index=True)
    reference = Column(String(150), nullable=False, index=True)
    produit = Column(String(150), nullable=True)
    quota = Column(Integer, nullable=True)
    utilisable = Column(Integer, nullable=True)
    validite = Column(Date, nullable=True)
    statut = Column(String(150), nullable=True)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())


class DeclExportLicense(Base):
    """Licences d' exportation."""
    __tablename__ = "decl_export_licenses"
    __table_args__ = (
        UniqueConstraint('company_id', 'reference', name='uix_decl_export_licenses_company_reference'),
    )
    id = Column(Integer, primary_key=True, index=True)
    company_id = Column(Integer, ForeignKey('companies.id'), nullable=False, index=True)
    reference = Column(String(150), nullable=False, index=True)
    bien = Column(String(150), nullable=True)
    destination = Column(String(150), nullable=True)
    usage = Column(String(150), nullable=True)
    validite = Column(Date, nullable=True)
    statut = Column(String(150), nullable=True)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())


class DeclPreClearance(Base):
    """Pre-dedouanements."""
    __tablename__ = "decl_pre_clearances"
    __table_args__ = (
        UniqueConstraint('company_id', 'reference', name='uix_decl_pre_clearances_company_reference'),
    )
    id = Column(Integer, primary_key=True, index=True)
    company_id = Column(Integer, ForeignKey('companies.id'), nullable=False, index=True)
    reference = Column(String(150), nullable=False, index=True)
    masse = Column(String(150), nullable=True)
    arrivee_prevue = Column(DateTime(timezone=True), nullable=True)
    depot = Column(DateTime(timezone=True), nullable=True)
    statut = Column(String(150), nullable=True)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())


class DeclCustomsInvoice(Base):
    """Factures commerciales."""
    __tablename__ = "decl_customs_invoices"
    __table_args__ = (
        UniqueConstraint('company_id', 'reference', name='uix_decl_customs_invoice_company_reference'),
    )
    id = Column(Integer, primary_key=True, index=True)
    company_id = Column(Integer, ForeignKey('companies.id'), nullable=False, index=True)
    reference = Column(String(150), nullable=False, index=True)
    fournisseur = Column(String(150), nullable=True)
    montant = Column(Numeric, nullable=True)
    devise = Column(String(150), nullable=True)
    date = Column(Date, nullable=True)
    statut = Column(String(150), nullable=True)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())


class DeclPackingList(Base):
    """Colisages douaniers."""
    __tablename__ = "decl_packing_lists"
    __table_args__ = (
        UniqueConstraint('company_id', 'reference', name='uix_decl_packing_lists_company_reference'),
    )
    id = Column(Integer, primary_key=True, index=True)
    company_id = Column(Integer, ForeignKey('companies.id'), nullable=False, index=True)
    reference = Column(String(150), nullable=False, index=True)
    masse = Column(String(150), nullable=True)
    nb_colis = Column(Integer, nullable=True)
    poids_net = Column(Numeric, nullable=True)
    statut = Column(String(150), nullable=True)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())


class DeclCertificateAnalysis(Base):
    """Certificats d' analyse."""
    __tablename__ = "decl_coa"
    __table_args__ = (
        UniqueConstraint('company_id', 'reference', name='uix_decl_coa_company_reference'),
    )
    id = Column(Integer, primary_key=True, index=True)
    company_id = Column(Integer, ForeignKey('companies.id'), nullable=False, index=True)
    reference = Column(String(150), nullable=False, index=True)
    produit = Column(String(150), nullable=True)
    laboratoire = Column(String(150), nullable=True)
    parametres = Column(Text(2000), nullable=True)
    date = Column(Date, nullable=True)
    statut = Column(String(150), nullable=True)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())


class DeclPhytosanitaryApp(Base):
    """Demandes phytosanitaires."""
    __tablename__ = "decl_phyto_apps"
    __table_args__ = (
        UniqueConstraint('company_id', 'reference', name='uix_decl_phyto_apps_company_reference'),
    )
    id = Column(Integer, primary_key=True, index=True)
    company_id = Column(Integer, ForeignKey('companies.id'), nullable=False, index=True)
    reference = Column(String(150), nullable=False, index=True)
    produit = Column(String(150), nullable=True)
    destination = Column(String(150), nullable=True)
    date_controle = Column(Date, nullable=True)
    statut = Column(String(150), nullable=True)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())


class DeclCustomsPayment(Base):
    """Paiements douaniers."""
    __tablename__ = "decl_customs_payments"
    __table_args__ = (
        UniqueConstraint('company_id', 'reference', name='uix_decl_customs_payment_company_reference'),
    )
    id = Column(Integer, primary_key=True, index=True)
    company_id = Column(Integer, ForeignKey('companies.id'), nullable=False, index=True)
    reference = Column(String(150), nullable=False, index=True)
    declaration = Column(String(150), nullable=True)
    montant = Column(Numeric, nullable=True)
    type_droit = Column(String(150), nullable=True)
    date = Column(DateTime(timezone=True), nullable=True)
    statut = Column(String(150), nullable=True)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())


class DeclTransitDocument(Base):
    """Documents de transit (T1/T2)."""
    __tablename__ = "decl_transit_documents"
    __table_args__ = (
        UniqueConstraint('company_id', 'reference', name='uix_decl_transit_documen_company_reference'),
    )
    id = Column(Integer, primary_key=True, index=True)
    company_id = Column(Integer, ForeignKey('companies.id'), nullable=False, index=True)
    reference = Column(String(150), nullable=False, index=True)
    type = Column(String(150), nullable=True)
    bureau_depart = Column(String(150), nullable=True)
    bureau_arrivee = Column(String(150), nullable=True)
    garantie = Column(Numeric, nullable=True)
    statut = Column(String(150), nullable=True)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())


class DeclDangerousGoods(Base):
    """Declarations marchandises dangereuses."""
    __tablename__ = "decl_dg_declarations"
    __table_args__ = (
        UniqueConstraint('company_id', 'reference', name='uix_decl_dg_declarations_company_reference'),
    )
    id = Column(Integer, primary_key=True, index=True)
    company_id = Column(Integer, ForeignKey('companies.id'), nullable=False, index=True)
    reference = Column(String(150), nullable=False, index=True)
    numero_onu = Column(String(150), nullable=True)
    classe = Column(String(150), nullable=True)
    quantite = Column(Numeric, nullable=True)
    date = Column(DateTime(timezone=True), nullable=True)
    statut = Column(String(150), nullable=True)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())


class DeclBondedWarehouseEntry(Base):
    """Entrees en entrepot sous douane."""
    __tablename__ = "decl_bonded_entries"
    __table_args__ = (
        UniqueConstraint('company_id', 'reference', name='uix_decl_bonded_entries_company_reference'),
    )
    id = Column(Integer, primary_key=True, index=True)
    company_id = Column(Integer, ForeignKey('companies.id'), nullable=False, index=True)
    reference = Column(String(150), nullable=False, index=True)
    entrepot = Column(String(150), nullable=True)
    masse = Column(String(150), nullable=True)
    entree = Column(DateTime(timezone=True), nullable=True)
    sortie_prevue = Column(DateTime(timezone=True), nullable=True)
    statut = Column(String(150), nullable=True)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())


class DeclDutyReliefClaim(Base):
    """Demandes de franchise de droits."""
    __tablename__ = "decl_duty_relief"
    __table_args__ = (
        UniqueConstraint('company_id', 'reference', name='uix_decl_duty_relief_company_reference'),
    )
    id = Column(Integer, primary_key=True, index=True)
    company_id = Column(Integer, ForeignKey('companies.id'), nullable=False, index=True)
    reference = Column(String(150), nullable=False, index=True)
    motif = Column(String(150), nullable=True)
    declaration = Column(String(150), nullable=True)
    montant_exonere = Column(Numeric, nullable=True)
    statut = Column(String(150), nullable=True)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())


class DeclManifestCorrection(Base):
    """Rectifications de manifeste."""
    __tablename__ = "decl_manifest_corrections"
    __table_args__ = (
        UniqueConstraint('company_id', 'reference', name='uix_decl_manifest_correc_company_reference'),
    )
    id = Column(Integer, primary_key=True, index=True)
    company_id = Column(Integer, ForeignKey('companies.id'), nullable=False, index=True)
    reference = Column(String(150), nullable=False, index=True)
    manifeste = Column(String(150), nullable=True)
    objet_rectification = Column(Text(2000), nullable=True)
    date = Column(DateTime(timezone=True), nullable=True)
    statut = Column(String(150), nullable=True)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())


class DeclCustomsAuditSupport(Base):
    """Support controle douanier."""
    __tablename__ = "decl_audit_support"
    __table_args__ = (
        UniqueConstraint('company_id', 'reference', name='uix_decl_audit_support_company_reference'),
    )
    id = Column(Integer, primary_key=True, index=True)
    company_id = Column(Integer, ForeignKey('companies.id'), nullable=False, index=True)
    reference = Column(String(150), nullable=False, index=True)
    controle = Column(String(150), nullable=True)
    periode = Column(String(150), nullable=True)
    pieces_fournies = Column(Integer, nullable=True)
    date = Column(Date, nullable=True)
    statut = Column(String(150), nullable=True)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

