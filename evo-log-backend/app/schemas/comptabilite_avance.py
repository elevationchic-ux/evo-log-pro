"""Schemas pour la comptabilité avancée - Journaux, lettrage, grand livre, balance"""
from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import date, datetime
from decimal import Decimal


# ============ JOURNAUX AUXILIAIRES ============

class JournalAuxiliaireBase(BaseModel):
    code_journal: str = Field(..., description="Code unique du journal")
    nom_journal: str = Field(..., description="Nom du journal")
    type_journal: str = Field(..., description="Type de journal (achats, ventes, banque, caisse, od, salaires, amortissements)")
    compte_centralisateur: Optional[str] = Field(None, description="Compte de centralisation")
    description: Optional[str] = Field(None, description="Description du journal")


class JournalAuxiliaireCreate(JournalAuxiliaireBase):
    pass


class JournalAuxiliaireUpdate(BaseModel):
    nom_journal: Optional[str] = None
    description: Optional[str] = None
    statut: Optional[str] = None


class JournalAuxiliaireResponse(JournalAuxiliaireBase):
    id: int
    periodical: bool
    statut: str
    devise: str
    created_at: datetime
    updated_at: Optional[datetime] = None
    
    class Config:
        from_attributes = True


# ============ LIGNES JOURNAL ============

class LigneJournalBase(BaseModel):
    ecriture_id: int
    journal_id: int
    compte_id: int
    compte_numero: Optional[str] = None
    compte_intitule: Optional[str] = None
    debit: Decimal = Field(default=0, ge=0)
    credit: Decimal = Field(default=0, ge=0)
    reference_document: Optional[str] = None
    libelle_detail: Optional[str] = None


class LigneJournalCreate(LigneJournalBase):
    pass


class LigneJournalResponse(LigneJournalBase):
    id: int
    devise: str
    order_line: int
    created_at: datetime
    
    class Config:
        from_attributes = True


# ============ LETTRAGE ============

class LettrageBase(BaseModel):
    compte_id: int
    numero_lettrage: str
    type_lettrage: str = Field(default="automatique", description="automatique, manuel, partiel")
    date_lettrage: date
    montant_lettre: Decimal
    reference_lettrage: Optional[str] = None
    notes: Optional[str] = None


class LettrageCreate(LettrageBase):
    pass


class LettrageUpdate(BaseModel):
    notes: Optional[str] = None
    motif_annulation: Optional[str] = None


class LettrageResponse(LettrageBase):
    id: int
    devise: str
    effectue_par: str
    date_annulation: Optional[date] = None
    motif_annulation: Optional[str] = None
    created_at: datetime
    updated_at: Optional[datetime] = None
    
    class Config:
        from_attributes = True


class EcritureLettreeBase(BaseModel):
    lettrage_id: int
    ecriture_id: int
    montant_lettre: Decimal


class EcritureLettreeCreate(EcritureLettreeBase):
    pass


class EcritureLettreeResponse(EcritureLettreeBase):
    id: int
    devise: str
    created_at: datetime
    
    class Config:
        from_attributes = True


class LettrageManuelRequest(BaseModel):
    compte_id: int
    ecritures_ids: List[int]
    date_lettrage: date
    effectue_par: str
    reference: Optional[str] = None


# ============ GRAND LIVRE ============

class GrandLivreLigneBase(BaseModel):
    compte_id: int
    ecriture_id: int
    date_ecriture: date
    libelle: Optional[str] = None
    debit: Decimal = Field(default=0, ge=0)
    credit: Decimal = Field(default=0, ge=0)
    solde_debit: Decimal = Field(default=0, ge=0)
    solde_credit: Decimal = Field(default=0, ge=0)
    journal: Optional[str] = None
    periode: Optional[str] = None
    statut_lettrage: Optional[str] = None


class GrandLivreLigneResponse(GrandLivreLigneBase):
    id: int
    devise: str
    lettrage_id: Optional[int] = None
    created_at: datetime
    
    class Config:
        from_attributes = True


class GrandLivreGenerateRequest(BaseModel):
    exercice_id: int
    date_debut: date
    date_fin: date


class HistoriqueCompteResponse(BaseModel):
    compte_id: int
    periode: str
    total_debit: Decimal
    total_credit: Decimal
    solde_debit: Decimal
    solde_credit: Decimal
    nombre_ecritures: int
    lignes: List[GrandLivreLigneResponse]


# ============ BALANCE ============

class BalanceVerificationBase(BaseModel):
    exercice_id: int
    periode: str
    date_balance: date


class BalanceVerificationCreate(BalanceVerificationBase):
    pass


class BalanceVerificationResponse(BalanceVerificationBase):
    id: int
    total_debit: Decimal
    total_credit: Decimal
    ecart: Decimal
    statut: str
    valide_par: Optional[str] = None
    date_validation: Optional[date] = None
    notes: Optional[str] = None
    created_at: datetime
    updated_at: Optional[datetime] = None
    
    class Config:
        from_attributes = True


class LigneBalanceBase(BaseModel):
    balance_id: int
    compte_id: int
    compte_numero: Optional[str] = None
    compte_intitule: Optional[str] = None
    total_debit: Decimal = Field(default=0, ge=0)
    total_credit: Decimal = Field(default=0, ge=0)
    solde_debit: Decimal = Field(default=0, ge=0)
    solde_credit: Decimal = Field(default=0, ge=0)


class LigneBalanceCreate(LigneBalanceBase):
    pass


class LigneBalanceResponse(LigneBalanceBase):
    id: int
    devise: str
    created_at: datetime
    
    class Config:
        from_attributes = True


class BalanceResponse(BalanceVerificationResponse):
    lignes: List[LigneBalanceResponse] = []


class BalanceParJournalResponse(BaseModel):
    journal: str
    periode: str
    total_debit: Decimal
    total_credit: Decimal
    ecart: Decimal
    nombre_ecritures: int


# ============ ÉTATS FINANCIERS OHADA ============

class BilanOHADADetailleBase(BaseModel):
    exercice_id: int
    date_bilan: date
    actif_immobilise_brut: Decimal = Field(default=0, ge=0)
    actif_immobilise_amortissements: Decimal = Field(default=0, ge=0)
    actif_immobilise_net: Decimal = Field(default=0, ge=0)
    actif_circulant_stocks: Decimal = Field(default=0, ge=0)
    actif_circulant_creances: Decimal = Field(default=0, ge=0)
    actif_circulant_total: Decimal = Field(default=0, ge=0)
    tresorerie_actif: Decimal = Field(default=0, ge=0)
    total_actif: Decimal = Field(default=0, ge=0)
    capitaux_propres_capital: Decimal = Field(default=0, ge=0)
    capitaux_propres_reserves: Decimal = Field(default=0, ge=0)
    capitaux_propres_resultat: Decimal = Field(default=0, ge=0)
    capitaux_propres_total: Decimal = Field(default=0, ge=0)
    dettes_long_terme: Decimal = Field(default=0, ge=0)
    dettes_courtes: Decimal = Field(default=0, ge=0)
    total_passif: Decimal = Field(default=0, ge=0)


class BilanOHADADetailleCreate(BilanOHADADetailleBase):
    pass


class BilanOHADADetailleResponse(BilanOHADADetailleBase):
    id: int
    devise: str
    notes: Optional[str] = None
    valide_par: Optional[str] = None
    date_validation: Optional[date] = None
    created_at: datetime
    updated_at: Optional[datetime] = None
    
    class Config:
        from_attributes = True


class CompteResultatOHADADetailleBase(BaseModel):
    exercice_id: int
    periode: str
    date_arrete: date
    ventes_marchandises: Decimal = Field(default=0, ge=0)
    ventes_produits_fabriques: Decimal = Field(default=0, ge=0)
    subventions_exploitation: Decimal = Field(default=0, ge=0)
    autres_produits_exploitation: Decimal = Field(default=0, ge=0)
    total_produits_exploitation: Decimal = Field(default=0, ge=0)
    achats_marchandises: Decimal = Field(default=0, ge=0)
    achats_matieres_premieres: Decimal = Field(default=0, ge=0)
    services_exterieurs: Decimal = Field(default=0, ge=0)
    charges_personnel: Decimal = Field(default=0, ge=0)
    impots_taxes: Decimal = Field(default=0, ge=0)
    dotations_amortissements: Decimal = Field(default=0, ge=0)
    autres_charges_exploitation: Decimal = Field(default=0, ge=0)
    total_charges_exploitation: Decimal = Field(default=0, ge=0)
    resultat_exploitation: Decimal
    produits_financiers: Decimal = Field(default=0, ge=0)
    charges_financieres: Decimal = Field(default=0, ge=0)
    resultat_financier: Decimal
    produits_exceptionnels: Decimal = Field(default=0, ge=0)
    charges_exceptionnelles: Decimal = Field(default=0, ge=0)
    resultat_exceptionnel: Decimal
    resultat_net: Decimal


class CompteResultatOHADADetailleCreate(CompteResultatOHADADetailleBase):
    pass


class CompteResultatOHADADetailleResponse(CompteResultatOHADADetailleBase):
    id: int
    devise: str
    notes: Optional[str] = None
    valide_par: Optional[str] = None
    date_validation: Optional[date] = None
    created_at: datetime
    updated_at: Optional[datetime] = None
    
    class Config:
        from_attributes = True


class TAFIREBase(BaseModel):
    exercice_id: int
    date_tafire: date
    capacit_autofinancement: Decimal = Field(default=0, ge=0)
    cession_immobilisations: Decimal = Field(default=0, ge=0)
    augmentation_capital: Decimal = Field(default=0, ge=0)
    nouveaux_emprunts: Decimal = Field(default=0, ge=0)
    total_ressources: Decimal = Field(default=0, ge=0)
    investissements_immobilisations: Decimal = Field(default=0, ge=0)
    remboursement_emprunts: Decimal = Field(default=0, ge=0)
    distribution_dividendes: Decimal = Field(default=0, ge=0)
    augmentation_besoin_fdr: Decimal = Field(default=0, ge=0)
    total_emplois: Decimal = Field(default=0, ge=0)
    variation_tresorerie: Decimal
    tresorerie_debut: Decimal = Field(default=0, ge=0)
    tresorerie_fin: Decimal = Field(default=0, ge=0)


class TAFIRECreate(TAFIREBase):
    pass


class TAFIREResponse(TAFIREBase):
    id: int
    devise: str
    notes: Optional[str] = None
    valide_par: Optional[str] = None
    date_validation: Optional[date] = None
    created_at: datetime
    updated_at: Optional[datetime] = None
    
    class Config:
        from_attributes = True


class AnnexesOHDABase(BaseModel):
    exercice_id: int
    date_annexes: date
    denomination_sociale: Optional[str] = None
    forme_juridique: Optional[str] = None
    siege_social: Optional[str] = None
    capital_social: Optional[Decimal] = None
    date_creation: Optional[date] = None
    methode_evaluation_stocks: Optional[str] = None
    methode_amortissements: Optional[str] = None
    principes_comptables: Optional[str] = None
    evenements_posterieurs: Optional[str] = None
    engagements_hors_bilan: Optional[str] = None
    notes_immobilisations: Optional[str] = None
    notes_amortissements: Optional[str] = None
    notes_provisions: Optional[str] = None
    notes_dettes: Optional[str] = None
    notes_engagements: Optional[str] = None


class AnnexesOHDACreate(AnnexesOHDABase):
    pass


class AnnexesOHDAResponse(AnnexesOHDABase):
    id: int
    devise: str
    valide_par: Optional[str] = None
    date_validation: Optional[date] = None
    created_at: datetime
    updated_at: Optional[datetime] = None
    
    class Config:
        from_attributes = True


class AnnexesGenererRequest(BaseModel):
    exercice_id: int
    date_annexes: date
    denomination: str
    forme_juridique: str
    siege: str


# ============ CLÔTURE ============

class ClotureMensuelleRequest(BaseModel):
    exercice_id: int
    periode: str
    cloture_par: str


class ClotureMensuelleResponse(BaseModel):
    exercice_id: int
    periode: str
    statut: str
    balance_id: int
    cloture_par: str
    date_cloture: date


class ClotureAnnuelleRequest(BaseModel):
    exercice_id: int
    cloture_par: str


class ClotureAnnuelleResponse(BaseModel):
    exercice_id: int
    annee: int
    statut: str
    bilan_id: int
    compte_resultat_id: int
    tafire_id: int
    resultat_net: Decimal
    cloture_par: str
    date_cloture: date


class ReportANouveauRequest(BaseModel):
    exercice_source_id: int
    exercice_cible_id: int


class ReportANouveauResponse(BaseModel):
    exercice_source_id: int
    exercice_cible_id: int
    statut: str
    nombre_comptes: int


class AffectationResultatRequest(BaseModel):
    exercice_id: int
    mode_affectation: str  # "reserve", "dividende", "report"
    montant_reserve: Decimal = Field(default=0, ge=0)
    montant_dividende: Decimal = Field(default=0, ge=0)


class AffectationResultatResponse(BaseModel):
    exercice_id: int
    resultat_net: Decimal
    mode_affectation: str
    montant_reserve: Decimal
    montant_dividende: Decimal
    montant_reporte: Decimal
    statut: str
