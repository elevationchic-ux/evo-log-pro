"""Finance models - OHADA accounting and financial management for Cameroon/CEMAC"""
from sqlalchemy import Column, Integer, String, Text, DateTime, Boolean, Float, ForeignKey, Enum, Date, Numeric
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
import enum
from app.core.database import Base


class TypeCompte(str, enum.Enum):
    """Account type enumeration following OHADA plan"""
    ACTIF = "actif"
    PASSIF = "passif"
    CHARGE = "charge"
    PRODUIT = "produit"
    ACTIF_FIXE = "actif_fixe"
    ACTIF_CIRCULANT = "actif_circulant"
    PASSIF_FIXE = "passif_fixe"
    PASSIF_CIRCULANT = "passif_circulant"


class RegimeTVA(str, enum.Enum):
    """VAT regime enumeration"""
    NORMAL = "normal"
    SIMPLIFIE = "simplifie"
    EXONERE = "exonere"
    SUSPENSION = "suspension"


class RegimeIS(str, enum.Enum):
    """Corporate tax regime enumeration"""
    NORMAL = "normal"
    MINIMAL = "minimal"
    IMPOT_FORFAITAIRE = "impot_forfaitaire"


class StatutTaxe(str, enum.Enum):
    """Tax status enumeration"""
    DUE = "due"
    PAYEE = "payee"
    PARTIEL = "partiel"
    REPORT = "report"
    CONTENTIEUX = "contentieux"


class PlanComptableOHADA(Base):
    """OHADA Accounting Plan"""
    __tablename__ = "plan_comptable_ohada"
    
    id = Column(Integer, primary_key=True, index=True)
    numero_compte = Column(String(20), unique=True, nullable=False, index=True)
    intitule = Column(String(200), nullable=False)
    type_compte = Column(Enum(TypeCompte))
    classe = Column(Integer)  # 1-5 selon OHADA
    sous_classe = Column(Integer)
    compte_racine = Column(String(20))
    description = Column(Text)
    devise = Column(String(3), default="XAF")
    solde_debit = Column(Numeric(15, 2), default=0)
    solde_credit = Column(Numeric(15, 2), default=0)
    date_creation = Column(Date)
    compte_centralisateur = Column(Boolean, default=False)
    actif = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relationships
    ecritures_comptables = relationship("EcritureComptableNew", back_populates="compte")


class EcritureComptableNew(Base):
    """Accounting entry"""
    __tablename__ = "ecritures_comptables_ohada"
    
    id = Column(Integer, primary_key=True, index=True)
    numero_ecriture = Column(String(50), unique=True, nullable=False, index=True)
    date_ecriture = Column(Date, nullable=False)
    numero_piece = Column(String(50))
    libelle = Column(String(500), nullable=False)
    compte_id = Column(Integer, ForeignKey('plan_comptable_ohada.id'))
    tiers_id = Column(Integer, ForeignKey('tiers.id'), nullable=True)
    debit = Column(Numeric(15, 2), default=0)
    credit = Column(Numeric(15, 2), default=0)
    devise = Column(String(3), default="XAF")
    reference_document = Column(String(100))
    type_document = Column(String(50))  # "facture", "avoir", "bq", "caisse"
    periode = Column(String(50))  # "2026-01", "2026-Q1"
    journal = Column(String(50))  # "ACHATS", "VENTES", "BANQUE", "CAISSE"
    valider = Column(Boolean, default=False)
    valide_par = Column(String(100))
    date_validation = Column(Date)
    exercice_id = Column(Integer, ForeignKey('exercices_comptables.id'))
    journal_id = Column(Integer, ForeignKey('journaux_auxiliaires.id'), nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relationships
    compte = relationship("PlanComptableOHADA", back_populates="ecritures_comptables")
    exercice = relationship("ExerciceComptable")
    journal_auxiliaire = relationship("JournalAuxiliaire", back_populates="ecritures")


class ExerciceComptable(Base):
    """Fiscal year/Accounting period"""
    __tablename__ = "exercices_comptables"
    
    id = Column(Integer, primary_key=True, index=True)
    numero_exercice = Column(String(50), unique=True, nullable=False, index=True)
    annee = Column(Integer, nullable=False)
    date_debut = Column(Date, nullable=False)
    date_fin = Column(Date, nullable=False)
    statut = Column(String(20), default="ouvert")  # ouvert, cloture, arrete
    cloture_par = Column(String(100))
    date_cloture = Column(Date)
    resultat_net = Column(Numeric(15, 2))
    chiffre_affaires = Column(Numeric(15, 2))
    total_actif = Column(Numeric(15, 2))
    total_passif = Column(Numeric(15, 2))
    devise = Column(String(3), default="XAF")
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relationships
    ecritures = relationship("EcritureComptableNew", overlaps="exercice")
    bilan = relationship("Bilan", back_populates="exercice")
    compte_resultat = relationship("CompteResultat", back_populates="exercice")


class FactureNew(Base):
    """Invoice"""
    __tablename__ = "factures_ohada"
    
    id = Column(Integer, primary_key=True, index=True)
    numero_facture = Column(String(50), unique=True, nullable=False, index=True)
    client_id = Column(Integer, ForeignKey('tiers.id'))
    type_facture = Column(String(20))  # "vente", "achat", "avoir", "prestation"
    date_emission = Column(Date, nullable=False)
    date_echeance = Column(Date)
    date_paiement = Column(Date)
    montant_ht = Column(Numeric(15, 2), nullable=False)
    taux_tva = Column(Numeric, default=19.25)  # TVA Cameroun
    montant_tva = Column(Numeric(15, 2), default=0)
    montant_ttc = Column(Numeric(15, 2), nullable=False)
    devise = Column(String(3), default="XAF")
    statut = Column(String(20), default="brouillon")  # brouillon, emise, payee_partiel, payee, annulee
    conditions_paiement = Column(String(50))
    notes = Column(Text)
    reglement_partiel = Column(Numeric(15, 2), default=0)
    solde_restant = Column(Numeric(15, 2))
    comptabilise = Column(Boolean, default=False)
    ecriture_id = Column(Integer, ForeignKey('ecritures_comptables.id'))
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relationships
    lignes_facture = relationship("LigneFactureOHADA", back_populates="facture")


class LigneFactureOHADA(Base):
    """Invoice line item (OHADA version)"""
    __tablename__ = "lignes_facture_ohada"
    __table_args__ = {'extend_existing': True}
    
    id = Column(Integer, primary_key=True, index=True)
    facture_id = Column(Integer, ForeignKey('factures_ohada.id'))
    article_id = Column(Integer, ForeignKey('stocks.id'))
    designation = Column(String(200), nullable=False)
    description = Column(Text)
    quantite = Column(Numeric, nullable=False)
    unite = Column(String(20))
    prix_unitaire_ht = Column(Numeric(15, 2), nullable=False)
    montant_ht = Column(Numeric(15, 2), nullable=False)
    taux_tva = Column(Numeric, default=19.25)
    montant_tva = Column(Numeric(15, 2), default=0)
    montant_ttc = Column(Numeric(15, 2), nullable=False)
    devise = Column(String(3), default="XAF")
    reference_commande = Column(String(50))
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relationships
    facture = relationship("FactureNew", back_populates="lignes_facture")


class Reglement(Base):
    """Payment/Settlement"""
    __tablename__ = "reglements"
    
    id = Column(Integer, primary_key=True, index=True)
    numero_reglement = Column(String(50), unique=True, nullable=False, index=True)
    facture_id = Column(Integer, ForeignKey('factures.id'))
    date_reglement = Column(Date, nullable=False)
    montant = Column(Numeric(15, 2), nullable=False)
    devise = Column(String(3), default="XAF")
    mode_paiement = Column(String(50))  # "especes", "cheque", "virement", "cb", "mobile"
    reference_bancaire = Column(String(100))
    banque = Column(String(100))
    notes = Column(Text)
    effectue_par = Column(String(100))
    statut = Column(String(20), default="valide")  # valide, annule, rembourse
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relationships
    facture = relationship("Facture", back_populates="reglements")


class TVADeclarable(Base):
    """VAT declaration"""
    __tablename__ = "tva_declarables"
    
    id = Column(Integer, primary_key=True, index=True)
    numero_declaration = Column(String(50), unique=True, nullable=False, index=True)
    periode = Column(String(50), nullable=False)  # "2026-01", "2026-Q1"
    date_declaration = Column(Date)
    date_limite = Column(Date)
    regime_tva = Column(Enum(RegimeTVA))
    base_imposable = Column(Numeric(15, 2), default=0)
    tva_collectee = Column(Numeric(15, 2), default=0)
    tva_deductible = Column(Numeric(15, 2), default=0)
    tva_a_payer = Column(Numeric(15, 2), default=0)
    devise = Column(String(3), default="XAF")
    statut = Column(Enum(StatutTaxe), default=StatutTaxe.DUE)
    montant_paye = Column(Numeric(15, 2), default=0)
    date_paiement = Column(Date)
    reference_paiement = Column(String(100))
    notes = Column(Text)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())


class RetenueSource(Base):
    """Withholding tax"""
    __tablename__ = "retenues_source"
    
    id = Column(Integer, primary_key=True, index=True)
    numero_retenu = Column(String(50), unique=True, nullable=False, index=True)
    facture_id = Column(Integer, ForeignKey('factures.id'))
    date_retenu = Column(Date, nullable=False)
    type_retenu = Column(String(50))  # "redevance", "honoraires", "dividendes", "interets"
    taux_retenu = Column(Numeric, nullable=False)  # % selon OHADA
    base_imposable = Column(Numeric(15, 2), nullable=False)
    montant_retenu = Column(Numeric(15, 2), nullable=False)
    devise = Column(String(3), default="XAF")
    beneficiaire = Column(String(100))
    raison_sociale = Column(String(200))
    statut = Column(Enum(StatutTaxe), default=StatutTaxe.DUE)
    date_paiement = Column(Date)
    reference_paiement = Column(String(100))
    declarer = Column(Boolean, default=False)
    notes = Column(Text)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relationships
    facture = relationship("Facture", back_populates="retenues_source")


class ISDeclarable(Base):
    """Corporate tax declaration"""
    __tablename__ = "is_declarables"
    
    id = Column(Integer, primary_key=True, index=True)
    numero_declaration = Column(String(50), unique=True, nullable=False, index=True)
    exercice_id = Column(Integer, ForeignKey('exercices_comptables.id'))
    annee = Column(Integer, nullable=False)
    regime_is = Column(Enum(RegimeIS))
    benefice_fiscal = Column(Numeric(15, 2), default=0)
    taux_imposition = Column(Numeric, default=33)  # % OHADA
    is_du = Column(Numeric(15, 2), default=0)
    is_minimum = Column(Numeric(15, 2), default=0)
    is_a_payer = Column(Numeric(15, 2), default=0)
    devise = Column(String(3), default="XAF")
    statut = Column(Enum(StatutTaxe), default=StatutTaxe.DUE)
    date_declaration = Column(Date)
    date_limite = Column(Date)
    montant_paye = Column(Numeric(15, 2), default=0)
    date_paiement = Column(Date)
    reference_paiement = Column(String(100))
    notes = Column(Text)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relationships
    exercice = relationship("ExerciceComptable")


class CentimesAdditionnels(Base):
    """Additional local taxes"""
    __tablename__ = "centimes_additionnels"
    
    id = Column(Integer, primary_key=True, index=True)
    numero_taxe = Column(String(50), unique=True, nullable=False, index=True)
    periode = Column(String(50), nullable=False)
    type_taxe = Column(String(50))  # "communale", "regionale", "centimes_charges"
    base_imposable = Column(Numeric(15, 2), default=0)
    taux = Column(Numeric, nullable=False)
    montant_taxe = Column(Numeric(15, 2), default=0)
    devise = Column(String(3), default="XAF")
    statut = Column(Enum(StatutTaxe), default=StatutTaxe.DUE)
    date_declaration = Column(Date)
    date_limite = Column(Date)
    montant_paye = Column(Numeric(15, 2), default=0)
    date_paiement = Column(Date)
    reference_paiement = Column(String(100))
    collectivite = Column(String(100))
    notes = Column(Text)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())


class Patente(Base):
    """Business license tax"""
    __tablename__ = "patentes"
    
    id = Column(Integer, primary_key=True, index=True)
    numero_patente = Column(String(50), unique=True, nullable=False, index=True)
    entreprise_id = Column(Integer, ForeignKey('tiers.id'))
    annee = Column(Integer, nullable=False)
    categorie = Column(String(50))  # "A", "B", "C", "D" selon taille
    chiffre_affaires = Column(Numeric(15, 2), default=0)
    montant_patente = Column(Numeric(15, 2), nullable=False)
    devise = Column(String(3), default="XAF")
    statut = Column(Enum(StatutTaxe), default=StatutTaxe.DUE)
    date_delivrance = Column(Date)
    date_limite = Column(Date)
    montant_paye = Column(Numeric(15, 2), default=0)
    date_paiement = Column(Date)
    reference_paiement = Column(String(100))
    centre_fiscal = Column(String(100))
    notes = Column(Text)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())


class Bilan(Base):
    """Balance sheet"""
    __tablename__ = "bilans"
    
    id = Column(Integer, primary_key=True, index=True)
    exercice_id = Column(Integer, ForeignKey('exercices_comptables.id'))
    date_bilan = Column(Date, nullable=False)
    total_actif = Column(Numeric(15, 2), default=0)
    total_passif = Column(Numeric(15, 2), default=0)
    actif_immobilise = Column(Numeric(15, 2), default=0)
    actif_circulant = Column(Numeric(15, 2), default=0)
    capitaux_propres = Column(Numeric(15, 2), default=0)
    dettes_long_terme = Column(Numeric(15, 2), default=0)
    dettes_courtes = Column(Numeric(15, 2), default=0)
    resultat_exercice = Column(Numeric(15, 2), default=0)
    devise = Column(String(3), default="XAF")
    notes = Column(Text)
    valide_par = Column(String(100))
    date_validation = Column(Date)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relationships
    exercice = relationship("ExerciceComptable", back_populates="bilan")


class CompteResultat(Base):
    """Income statement"""
    __tablename__ = "comptes_resultat"
    
    id = Column(Integer, primary_key=True, index=True)
    exercice_id = Column(Integer, ForeignKey('exercices_comptables.id'))
    periode = Column(String(50), nullable=False)
    chiffre_affaires = Column(Numeric(15, 2), default=0)
    achats = Column(Numeric(15, 2), default=0)
    services_exterieurs = Column(Numeric(15, 2), default=0)
    charges_personnel = Column(Numeric(15, 2), default=0)
    impots_taxes = Column(Numeric(15, 2), default=0)
    dotations_amortissements = Column(Numeric(15, 2), default=0)
    resultat_exploitation = Column(Numeric(15, 2), default=0)
    resultat_financier = Column(Numeric(15, 2), default=0)
    resultat_exceptionnel = Column(Numeric(15, 2), default=0)
    resultat_net = Column(Numeric(15, 2), default=0)
    devise = Column(String(3), default="XAF")
    notes = Column(Text)
    valide_par = Column(String(100))
    date_validation = Column(Date)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relationships
    exercice = relationship("ExerciceComptable", back_populates="compte_resultat")


class SignatureElectronique(Base):
    """Electronic signature for invoices"""
    __tablename__ = "signatures_electroniques"
    
    id = Column(Integer, primary_key=True, index=True)
    facture_id = Column(Integer, ForeignKey('factures.id'))
    numero_signature = Column(String(100), unique=True, nullable=False, index=True)
    date_signature = Column(DateTime(timezone=True), nullable=False)
    emetteur = Column(String(100), nullable=False)
    certificat_id = Column(String(100))
    empreinte = Column(String(255))
    statut = Column(String(20), default="valide")  # valide, expire, revoque
    date_expiration = Column(Date)
    autorite = Column(String(100))
    notes = Column(Text)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())


# ============ JOURNAUX AUXILIAIRES ============

class TypeJournal(str, enum.Enum):
    """Journal type enumeration"""
    ACHATS = "achats"
    VENTES = "ventes"
    BANQUE = "banque"
    CAISSE = "caisse"
    OD = "od"  # Opérations Diverses
    SALAIRES = "salaires"
    AMORTISSEMENTS = "amortissements"
    TVA = "tva"


class JournalAuxiliaire(Base):
    """Auxiliary journal model - Complete journal management"""
    __tablename__ = "journaux_auxiliaires"
    
    id = Column(Integer, primary_key=True, index=True)
    code_journal = Column(String(10), unique=True, nullable=False, index=True)
    nom_journal = Column(String(100), nullable=False)
    type_journal = Column(Enum(TypeJournal), nullable=False)
    description = Column(Text)
    compte_centralisateur = Column(String(20))  # Compte de centralisation
    periodical = Column(Boolean, default=True)  # Journal périodique
    statut = Column(String(20), default="actif")  # actif, inactif, cloture
    devise = Column(String(3), default="XAF")
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relationships
    ecritures = relationship("EcritureComptableNew", back_populates="journal_auxiliaire")


class LigneJournal(Base):
    """Journal line item - Detailed entry breakdown"""
    __tablename__ = "lignes_journal"
    
    id = Column(Integer, primary_key=True, index=True)
    ecriture_id = Column(Integer, ForeignKey('ecritures_comptables_ohada.id'), nullable=False)
    journal_id = Column(Integer, ForeignKey('journaux_auxiliaires.id'), nullable=False)
    compte_id = Column(Integer, ForeignKey('plan_comptable_ohada.id'), nullable=False)
    compte_numero = Column(String(20))
    compte_intitule = Column(String(200))
    debit = Column(Numeric(15, 2), default=0)
    credit = Column(Numeric(15, 2), default=0)
    devise = Column(String(3), default="XAF")
    reference_document = Column(String(100))
    libelle_detail = Column(String(500))
    order_line = Column(Integer, default=0)  # Ordre dans l'écriture
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # Relationships
    ecriture = relationship("EcritureComptableNew")
    journal = relationship("JournalAuxiliaire")
    compte = relationship("PlanComptableOHADA")


# ============ LETTRAGE ============

class TypeLettrage(str, enum.Enum):
    """Lettering type enumeration"""
    AUTOMATIQUE = "automatique"
    MANUEL = "manuel"
    PARTIEL = "partiel"


class StatutLettrage(str, enum.Enum):
    """Lettering status enumeration"""
    NON_LETRE = "non_letre"
    LETTRE = "lettre"
    PARTIELLEMENT_LETRE = "partiellement_lettre"
    A_LETTRER = "a_lettrer"


class Lettrage(Base):
    """Lettering model - Account reconciliation"""
    __tablename__ = "lettrages"
    
    id = Column(Integer, primary_key=True, index=True)
    compte_id = Column(Integer, ForeignKey('plan_comptable_ohada.id'), nullable=False)
    numero_lettrage = Column(String(50), unique=True, nullable=False, index=True)
    type_lettrage = Column(Enum(TypeLettrage), default=TypeLettrage.AUTOMATIQUE)
    date_lettrage = Column(Date, nullable=False)
    montant_lettre = Column(Numeric(15, 2), nullable=False)
    devise = Column(String(3), default="XAF")
    reference_lettrage = Column(String(100))
    notes = Column(Text)
    effectue_par = Column(String(100))
    date_annulation = Column(Date)
    motif_annulation = Column(Text)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relationships
    compte = relationship("PlanComptableOHADA")
    ecritures_lettrees = relationship("EcritureLettree", back_populates="lettrage")


class EcritureLettree(Base):
    """Lettered entry relationship"""
    __tablename__ = "ecritures_lettrees"
    
    id = Column(Integer, primary_key=True, index=True)
    lettrage_id = Column(Integer, ForeignKey('lettrages.id'), nullable=False)
    ecriture_id = Column(Integer, ForeignKey('ecritures_comptables_ohada.id'), nullable=False)
    montant_lettre = Column(Numeric(15, 2), nullable=False)
    devise = Column(String(3), default="XAF")
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # Relationships
    lettrage = relationship("Lettrage", back_populates="ecritures_lettrees")
    ecriture = relationship("EcritureComptableNew")


# ============ GRAND LIVRE ============

class GrandLivreLigne(Base):
    """General ledger line - Account history"""
    __tablename__ = "grand_livre_lignes"
    
    id = Column(Integer, primary_key=True, index=True)
    compte_id = Column(Integer, ForeignKey('plan_comptable_ohada.id'), nullable=False)
    ecriture_id = Column(Integer, ForeignKey('ecritures_comptables_ohada.id'), nullable=False)
    date_ecriture = Column(Date, nullable=False)
    libelle = Column(String(500))
    debit = Column(Numeric(15, 2), default=0)
    credit = Column(Numeric(15, 2), default=0)
    solde_debit = Column(Numeric(15, 2), default=0)
    solde_credit = Column(Numeric(15, 2), default=0)
    devise = Column(String(3), default="XAF")
    journal = Column(String(50))
    periode = Column(String(50))
    statut_lettrage = Column(Enum(StatutLettrage), default=StatutLettrage.NON_LETRE)
    lettrage_id = Column(Integer, ForeignKey('lettrages.id'))
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # Relationships
    compte = relationship("PlanComptableOHADA")
    ecriture = relationship("EcritureComptableNew")
    lettrage = relationship("Lettrage")


# ============ BALANCE ============

class BalanceVerification(Base):
    """Trial balance model"""
    __tablename__ = "balances_verification"
    
    id = Column(Integer, primary_key=True, index=True)
    exercice_id = Column(Integer, ForeignKey('exercices_comptables.id'), nullable=False)
    periode = Column(String(50), nullable=False)
    date_balance = Column(Date, nullable=False)
    total_debit = Column(Numeric(15, 2), default=0)
    total_credit = Column(Numeric(15, 2), default=0)
    ecart = Column(Numeric(15, 2), default=0)
    statut = Column(String(20), default="en_cours")  # en_cours, equilibre, desequilibre
    valide_par = Column(String(100))
    date_validation = Column(Date)
    notes = Column(Text)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relationships
    exercice = relationship("ExerciceComptable")
    lignes_balance = relationship("LigneBalance", back_populates="balance")


class LigneBalance(Base):
    """Trial balance line item"""
    __tablename__ = "lignes_balance"
    
    id = Column(Integer, primary_key=True, index=True)
    balance_id = Column(Integer, ForeignKey('balances_verification.id'), nullable=False)
    compte_id = Column(Integer, ForeignKey('plan_comptable_ohada.id'), nullable=False)
    compte_numero = Column(String(20))
    compte_intitule = Column(String(200))
    total_debit = Column(Numeric(15, 2), default=0)
    total_credit = Column(Numeric(15, 2), default=0)
    solde_debit = Column(Numeric(15, 2), default=0)
    solde_credit = Column(Numeric(15, 2), default=0)
    devise = Column(String(3), default="XAF")
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # Relationships
    balance = relationship("BalanceVerification", back_populates="lignes_balance")
    compte = relationship("PlanComptableOHADA")


# ============ ÉTATS FINANCIERS OHADA COMPLETS ============

class BilanOHADADetaille(Base):
    """Bilan OHADA détaillé - Balance sheet complete"""
    __tablename__ = "bilans_ohada_detailles"
    
    id = Column(Integer, primary_key=True, index=True)
    exercice_id = Column(Integer, ForeignKey('exercices_comptables.id'), nullable=False)
    date_bilan = Column(Date, nullable=False)
    
    # ACTIF
    actif_immobilise_brut = Column(Numeric(15, 2), default=0)
    actif_immobilise_amortissements = Column(Numeric(15, 2), default=0)
    actif_immobilise_net = Column(Numeric(15, 2), default=0)
    
    actif_circulant_stocks = Column(Numeric(15, 2), default=0)
    actif_circulant_creances = Column(Numeric(15, 2), default=0)
    actif_circulant_total = Column(Numeric(15, 2), default=0)
    
    tresorerie_actif = Column(Numeric(15, 2), default=0)
    
    total_actif = Column(Numeric(15, 2), default=0)
    
    # PASSIF
    capitaux_propres_capital = Column(Numeric(15, 2), default=0)
    capitaux_propres_reserves = Column(Numeric(15, 2), default=0)
    capitaux_propres_resultat = Column(Numeric(15, 2), default=0)
    capitaux_propres_total = Column(Numeric(15, 2), default=0)
    
    dettes_long_terme = Column(Numeric(15, 2), default=0)
    dettes_courtes = Column(Numeric(15, 2), default=0)
    
    total_passif = Column(Numeric(15, 2), default=0)
    
    devise = Column(String(3), default="XAF")
    notes = Column(Text)
    valide_par = Column(String(100))
    date_validation = Column(Date)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relationships
    exercice = relationship("ExerciceComptable")


class CompteResultatOHADADetaille(Base):
    """Compte de résultat OHADA détaillé - Income statement complete"""
    __tablename__ = "comptes_resultat_ohada_detailles"
    
    id = Column(Integer, primary_key=True, index=True)
    exercice_id = Column(Integer, ForeignKey('exercices_comptables.id'), nullable=False)
    periode = Column(String(50), nullable=False)
    date_arrete = Column(Date, nullable=False)
    
    # PRODUITS D'EXPLOITATION (70)
    ventes_marchandises = Column(Numeric(15, 2), default=0)
    ventes_produits_fabriques = Column(Numeric(15, 2), default=0)
    subventions_exploitation = Column(Numeric(15, 2), default=0)
    autres_produits_exploitation = Column(Numeric(15, 2), default=0)
    total_produits_exploitation = Column(Numeric(15, 2), default=0)
    
    # CHARGES D'EXPLOITATION (60)
    achats_marchandises = Column(Numeric(15, 2), default=0)
    achats_matieres_premieres = Column(Numeric(15, 2), default=0)
    services_exterieurs = Column(Numeric(15, 2), default=0)
    charges_personnel = Column(Numeric(15, 2), default=0)
    impots_taxes = Column(Numeric(15, 2), default=0)
    dotations_amortissements = Column(Numeric(15, 2), default=0)
    autres_charges_exploitation = Column(Numeric(15, 2), default=0)
    total_charges_exploitation = Column(Numeric(15, 2), default=0)
    
    # RÉSULTAT D'EXPLOITATION
    resultat_exploitation = Column(Numeric(15, 2), default=0)
    
    # PRODUITS FINANCIERS (76)
    produits_financiers = Column(Numeric(15, 2), default=0)
    
    # CHARGES FINANCIÈRES (66)
    charges_financieres = Column(Numeric(15, 2), default=0)
    
    # RÉSULTAT FINANCIER
    resultat_financier = Column(Numeric(15, 2), default=0)
    
    # RÉSULTAT EXCEPTIONNEL
    produits_exceptionnels = Column(Numeric(15, 2), default=0)
    charges_exceptionnelles = Column(Numeric(15, 2), default=0)
    resultat_exceptionnel = Column(Numeric(15, 2), default=0)
    
    # RÉSULTAT NET
    resultat_net = Column(Numeric(15, 2), default=0)
    
    devise = Column(String(3), default="XAF")
    notes = Column(Text)
    valide_par = Column(String(100))
    date_validation = Column(Date)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relationships
    exercice = relationship("ExerciceComptable")


class TAFIRE(Base):
    """Tableau Financier des Ressources et Emplois - TAFIRE OHADA"""
    __tablename__ = "tafire"
    
    id = Column(Integer, primary_key=True, index=True)
    exercice_id = Column(Integer, ForeignKey('exercices_comptables.id'), nullable=False)
    date_tafire = Column(Date, nullable=False)
    
    # RESSOURCES
    capacit_autofinancement = Column(Numeric(15, 2), default=0)
    cession_immobilisations = Column(Numeric(15, 2), default=0)
    augmentation_capital = Column(Numeric(15, 2), default=0)
    nouveaux_emprunts = Column(Numeric(15, 2), default=0)
    total_ressources = Column(Numeric(15, 2), default=0)
    
    # EMPLOIS
    investissements_immobilisations = Column(Numeric(15, 2), default=0)
    remboursement_emprunts = Column(Numeric(15, 2), default=0)
    distribution_dividendes = Column(Numeric(15, 2), default=0)
    augmentation_besoin_fdr = Column(Numeric(15, 2), default=0)
    total_emplois = Column(Numeric(15, 2), default=0)
    
    # VARIATION TRESORERIE
    variation_tresorerie = Column(Numeric(15, 2), default=0)
    tresorerie_debut = Column(Numeric(15, 2), default=0)
    tresorerie_fin = Column(Numeric(15, 2), default=0)
    
    devise = Column(String(3), default="XAF")
    notes = Column(Text)
    valide_par = Column(String(100))
    date_validation = Column(Date)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relationships
    exercice = relationship("ExerciceComptable")


class AnnexesOHADA(Base):
    """Annexes OHADA - Notes et informations complémentaires"""
    __tablename__ = "annexes_ohada"
    
    id = Column(Integer, primary_key=True, index=True)
    exercice_id = Column(Integer, ForeignKey('exercices_comptables.id'), nullable=False)
    date_annexes = Column(Date, nullable=False)
    
    # INFORMATIONS GÉNÉRALES
    denomination_sociale = Column(String(200))
    forme_juridique = Column(String(100))
    siege_social = Column(String(200))
    capital_social = Column(Numeric(15, 2))
    date_creation = Column(Date)
    
    # INFORMATIONS COMPLÉMENTAIRES
    methode_evaluation_stocks = Column(Text)
    methode_amortissements = Column(Text)
    principes_comptables = Column(Text)
    evenements_posterieurs = Column(Text)
    engagements_hors_bilan = Column(Text)
    
    # NOTES DETAILLÉES
    notes_immobilisations = Column(Text)
    notes_amortissements = Column(Text)
    notes_provisions = Column(Text)
    notes_dettes = Column(Text)
    notes_engagements = Column(Text)
    
    devise = Column(String(3), default="XAF")
    valide_par = Column(String(100))
    date_validation = Column(Date)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relationships
    exercice = relationship("ExerciceComptable")
