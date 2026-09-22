"""Pydantic schemas for Finance module - OHADA accounting and financial management"""
from datetime import datetime, date
from typing import Optional, List
from pydantic import BaseModel


# Plan Comptable OHADA schemas
class PlanComptableOHADABase(BaseModel):
    numero_compte: str
    intitule: str
    type_compte: str
    classe: int
    sous_classe: int


class PlanComptableOHADACreate(PlanComptableOHADABase):
    compte_racine: str = ""
    description: str = ""
    compte_centralisateur: bool = False


class PlanComptableOHADAUpdate(BaseModel):
    description: Optional[str] = None
    solde_debit: Optional[float] = None
    solde_credit: Optional[float] = None
    compte_centralisateur: Optional[bool] = None
    actif: Optional[bool] = None


class PlanComptableOHADAResponse(PlanComptableOHADABase):
    id: int
    compte_racine: Optional[str] = None
    description: Optional[str] = None
    devise: str
    solde_debit: float
    solde_credit: float
    date_creation: date
    compte_centralisateur: bool
    actif: bool
    created_at: datetime
    updated_at: Optional[datetime] = None
    
    class Config:
        from_attributes = True


# Ecriture Comptable schemas
class EcritureComptableBase(BaseModel):
    numero_ecriture: str
    date_ecriture: date
    libelle: str
    compte_id: int
    debit: float
    credit: float
    journal: str
    periode: str


class EcritureComptableCreate(EcritureComptableBase):
    numero_piece: str = ""
    tiers_id: int = None
    reference_document: str = ""
    type_document: str = ""


class EcritureComptableUpdate(BaseModel):
    reference_document: Optional[str] = None
    type_document: Optional[str] = None
    valider: Optional[bool] = None
    valide_par: Optional[str] = None
    date_validation: Optional[date] = None


class EcritureComptableResponse(EcritureComptableBase):
    id: int
    numero_piece: Optional[str] = None
    tiers_id: Optional[int] = None
    devise: str
    reference_document: Optional[str] = None
    type_document: Optional[str] = None
    exercice_id: Optional[int] = None
    valider: bool
    valide_par: Optional[str] = None
    date_validation: Optional[date] = None
    created_at: datetime
    updated_at: Optional[datetime] = None
    
    class Config:
        from_attributes = True


# Exercice Comptable schemas
class ExerciceComptableBase(BaseModel):
    numero_exercice: str
    annee: int
    date_debut: date
    date_fin: date


class ExerciceComptableCreate(ExerciceComptableBase):
    pass


class ExerciceComptableUpdate(BaseModel):
    statut: Optional[str] = None
    cloture_par: Optional[str] = None
    date_cloture: Optional[date] = None
    resultat_net: Optional[float] = None
    chiffre_affaires: Optional[float] = None
    total_actif: Optional[float] = None
    total_passif: Optional[float] = None


class ExerciceComptableResponse(ExerciceComptableBase):
    id: int
    statut: str
    cloture_par: Optional[str] = None
    date_cloture: Optional[date] = None
    resultat_net: Optional[float] = None
    chiffre_affaires: Optional[float] = None
    total_actif: Optional[float] = None
    total_passif: Optional[float] = None
    devise: str
    created_at: datetime
    updated_at: Optional[datetime] = None
    
    class Config:
        from_attributes = True


# Facture schemas
class FactureBase(BaseModel):
    numero_facture: str
    client_id: int
    type_facture: str
    date_emission: date
    montant_ht: float
    taux_tva: float


class FactureCreate(FactureBase):
    date_echeance: date = None
    conditions_paiement: str = ""
    notes: str = ""


class FactureUpdate(BaseModel):
    date_echeance: Optional[date] = None
    date_paiement: Optional[date] = None
    statut: Optional[str] = None
    conditions_paiement: Optional[str] = None
    notes: Optional[str] = None
    comptabilise: Optional[bool] = None


class FactureResponse(FactureBase):
    id: int
    date_echeance: Optional[date] = None
    date_paiement: Optional[date] = None
    montant_tva: float
    montant_ttc: float
    devise: str
    statut: str
    conditions_paiement: Optional[str] = None
    notes: Optional[str] = None
    reglement_partiel: float
    solde_restant: float
    comptabilise: bool
    ecriture_id: Optional[int] = None
    created_at: datetime
    updated_at: Optional[datetime] = None
    
    class Config:
        from_attributes = True


# Ligne Facture schemas
class LigneFactureBase(BaseModel):
    facture_id: int
    article_id: int
    designation: str
    quantite: float
    prix_unitaire_ht: float


class LigneFactureCreate(LigneFactureBase):
    description: str = ""
    unite: str = ""
    taux_tva: float = 19.25
    reference_commande: str = ""


class LigneFactureUpdate(BaseModel):
    description: Optional[str] = None
    taux_tva: Optional[float] = None
    reference_commande: Optional[str] = None


class LigneFactureResponse(LigneFactureBase):
    id: int
    description: Optional[str] = None
    unite: Optional[str] = None
    montant_ht: float
    taux_tva: float
    montant_tva: float
    montant_ttc: float
    devise: str
    reference_commande: Optional[str] = None
    created_at: datetime
    updated_at: Optional[datetime] = None
    
    class Config:
        from_attributes = True


# Reglement schemas
class ReglementBase(BaseModel):
    numero_reglement: str
    facture_id: int
    date_reglement: date
    montant: float
    mode_paiement: str


class ReglementCreate(ReglementBase):
    reference_bancaire: str = ""
    banque: str = ""
    notes: str = ""


class ReglementUpdate(BaseModel):
    reference_bancaire: Optional[str] = None
    banque: Optional[str] = None
    notes: Optional[str] = None
    statut: Optional[str] = None


class ReglementResponse(ReglementBase):
    id: int
    devise: str
    reference_bancaire: Optional[str] = None
    banque: Optional[str] = None
    notes: Optional[str] = None
    effectue_par: str
    statut: str
    created_at: datetime
    updated_at: Optional[datetime] = None
    
    class Config:
        from_attributes = True


# TVA Declarable schemas
class TVADeclarableBase(BaseModel):
    numero_declaration: str
    periode: str
    regime_tva: str
    base_imposable: float
    tva_collectee: float
    tva_deductible: float


class TVADeclarableCreate(TVADeclarableBase):
    date_limite: date = None
    notes: str = ""


class TVADeclarableUpdate(BaseModel):
    date_limite: Optional[date] = None
    statut: Optional[str] = None
    montant_paye: Optional[float] = None
    date_paiement: Optional[date] = None
    reference_paiement: Optional[str] = None
    notes: Optional[str] = None


class TVADeclarableResponse(TVADeclarableBase):
    id: int
    tva_a_payer: float
    devise: str
    date_declaration: date
    date_limite: Optional[date] = None
    statut: str
    montant_paye: float
    date_paiement: Optional[date] = None
    reference_paiement: Optional[str] = None
    notes: Optional[str] = None
    created_at: datetime
    updated_at: Optional[datetime] = None
    
    class Config:
        from_attributes = True


# Retenue Source schemas
class RetenueSourceBase(BaseModel):
    numero_retenu: str
    facture_id: int
    date_retenu: date
    type_retenu: str
    taux_retenu: float
    base_imposable: float


class RetenueSourceCreate(RetenueSourceBase):
    beneficiaire: str = ""
    raison_sociale: str = ""
    notes: str = ""


class RetenueSourceUpdate(BaseModel):
    beneficiaire: Optional[str] = None
    raison_sociale: Optional[str] = None
    statut: Optional[str] = None
    date_paiement: Optional[date] = None
    reference_paiement: Optional[str] = None
    declarer: Optional[bool] = None
    notes: Optional[str] = None


class RetenueSourceResponse(RetenueSourceBase):
    id: int
    montant_retenu: float
    devise: str
    beneficiaire: Optional[str] = None
    raison_sociale: Optional[str] = None
    statut: str
    date_paiement: Optional[date] = None
    reference_paiement: Optional[str] = None
    declarer: bool
    notes: Optional[str] = None
    created_at: datetime
    updated_at: Optional[datetime] = None
    
    class Config:
        from_attributes = True


# IS Declarable schemas
class ISDeclarableBase(BaseModel):
    numero_declaration: str
    exercice_id: int
    annee: int
    regime_is: str
    benefice_fiscal: float


class ISDeclarableCreate(ISDeclarableBase):
    date_limite: date = None
    notes: str = ""


class ISDeclarableUpdate(BaseModel):
    date_limite: Optional[date] = None
    statut: Optional[str] = None
    montant_paye: Optional[float] = None
    date_paiement: Optional[date] = None
    reference_paiement: Optional[str] = None
    notes: Optional[str] = None


class ISDeclarableResponse(ISDeclarableBase):
    id: int
    taux_imposition: float
    is_du: float
    is_minimum: float
    is_a_payer: float
    devise: str
    date_declaration: date
    date_limite: Optional[date] = None
    statut: str
    montant_paye: float
    date_paiement: Optional[date] = None
    reference_paiement: Optional[str] = None
    notes: Optional[str] = None
    created_at: datetime
    updated_at: Optional[datetime] = None
    
    class Config:
        from_attributes = True


# Centimes Additionnels schemas
class CentimesAdditionnelsBase(BaseModel):
    numero_taxe: str
    periode: str
    type_taxe: str
    base_imposable: float
    taux: float
    collectivite: str


class CentimesAdditionnelsCreate(CentimesAdditionnelsBase):
    date_limite: date = None
    notes: str = ""


class CentimesAdditionnelsUpdate(BaseModel):
    date_limite: Optional[date] = None
    statut: Optional[str] = None
    montant_paye: Optional[float] = None
    date_paiement: Optional[date] = None
    reference_paiement: Optional[str] = None
    notes: Optional[str] = None


class CentimesAdditionnelsResponse(CentimesAdditionnelsBase):
    id: int
    montant_taxe: float
    devise: str
    date_declaration: date
    date_limite: Optional[date] = None
    statut: str
    montant_paye: float
    date_paiement: Optional[date] = None
    reference_paiement: Optional[str] = None
    notes: Optional[str] = None
    created_at: datetime
    updated_at: Optional[datetime] = None
    
    class Config:
        from_attributes = True


# Patente schemas
class PatenteBase(BaseModel):
    numero_patente: str
    entreprise_id: int
    annee: int
    categorie: str
    chiffre_affaires: float
    montant_patente: float


class PatenteCreate(PatenteBase):
    date_limite: date = None
    centre_fiscal: str = ""
    notes: str = ""


class PatenteUpdate(BaseModel):
    date_limite: Optional[date] = None
    statut: Optional[str] = None
    montant_paye: Optional[float] = None
    date_paiement: Optional[date] = None
    reference_paiement: Optional[str] = None
    centre_fiscal: Optional[str] = None
    notes: Optional[str] = None


class PatenteResponse(PatenteBase):
    id: int
    devise: str
    date_delivrance: date
    date_limite: Optional[date] = None
    statut: str
    montant_paye: float
    date_paiement: Optional[date] = None
    reference_paiement: Optional[str] = None
    centre_fiscal: Optional[str] = None
    notes: Optional[str] = None
    created_at: datetime
    updated_at: Optional[datetime] = None
    
    class Config:
        from_attributes = True


# Bilan schemas
class BilanBase(BaseModel):
    exercice_id: int
    date_bilan: date
    total_actif: float
    total_passif: float


class BilanCreate(BilanBase):
    actif_immobilise: float = 0.0
    actif_circulant: float = 0.0
    capitaux_propres: float = 0.0
    dettes_long_terme: float = 0.0
    dettes_courtes: float = 0.0
    resultat_exercice: float = 0.0
    notes: str = ""


class BilanUpdate(BaseModel):
    actif_immobilise: Optional[float] = None
    actif_circulant: Optional[float] = None
    capitaux_propres: Optional[float] = None
    dettes_long_terme: Optional[float] = None
    dettes_courtes: Optional[float] = None
    resultat_exercice: Optional[float] = None
    notes: Optional[str] = None
    valide_par: Optional[str] = None
    date_validation: Optional[date] = None


class BilanResponse(BilanBase):
    id: int
    devise: str
    actif_immobilise: float
    actif_circulant: float
    capitaux_propres: float
    dettes_long_terme: float
    dettes_courtes: float
    resultat_exercice: float
    notes: Optional[str] = None
    valide_par: Optional[str] = None
    date_validation: Optional[date] = None
    created_at: datetime
    updated_at: Optional[datetime] = None
    
    class Config:
        from_attributes = True


# Compte Resultat schemas
class CompteResultatBase(BaseModel):
    exercice_id: int
    periode: str
    chiffre_affaires: float
    achats: float
    resultat_net: float


class CompteResultatCreate(CompteResultatBase):
    services_exterieurs: float = 0.0
    charges_personnel: float = 0.0
    impots_taxes: float = 0.0
    dotations_amortissements: float = 0.0
    resultat_exploitation: float = 0.0
    resultat_financier: float = 0.0
    resultat_exceptionnel: float = 0.0
    notes: str = ""


class CompteResultatUpdate(BaseModel):
    services_exterieurs: Optional[float] = None
    charges_personnel: Optional[float] = None
    impots_taxes: Optional[float] = None
    dotations_amortissements: Optional[float] = None
    resultat_exploitation: Optional[float] = None
    resultat_financier: Optional[float] = None
    resultat_exceptionnel: Optional[float] = None
    notes: Optional[str] = None
    valide_par: Optional[str] = None
    date_validation: Optional[date] = None


class CompteResultatResponse(CompteResultatBase):
    id: int
    devise: str
    services_exterieurs: float
    charges_personnel: float
    impots_taxes: float
    dotations_amortissements: float
    resultat_exploitation: float
    resultat_financier: float
    resultat_exceptionnel: float
    notes: Optional[str] = None
    valide_par: Optional[str] = None
    date_validation: Optional[date] = None
    created_at: datetime
    updated_at: Optional[datetime] = None
    
    class Config:
        from_attributes = True


# Signature Electronique schemas
class SignatureElectroniqueBase(BaseModel):
    facture_id: int
    numero_signature: str
    emetteur: str
    certificat_id: str


class SignatureElectroniqueCreate(SignatureElectroniqueBase):
    date_expiration: date = None
    autorite: str = ""
    notes: str = ""


class SignatureElectroniqueUpdate(BaseModel):
    date_expiration: Optional[date] = None
    statut: Optional[str] = None
    autorite: Optional[str] = None
    notes: Optional[str] = None


class SignatureElectroniqueResponse(SignatureElectroniqueBase):
    id: int
    date_signature: datetime
    empreinte: Optional[str] = None
    date_expiration: Optional[date] = None
    statut: str
    autorite: Optional[str] = None
    notes: Optional[str] = None
    created_at: datetime
    updated_at: Optional[datetime] = None
    
    class Config:
        from_attributes = True


# Rapport Fiscal
class RapportFiscalResponse(BaseModel):
    exercice: dict
    fiscalite: dict


# Paiement (Reglement) schemas
class PaiementCreate(BaseModel):
    numero_reglement: str
    facture_id: int
    date_reglement: date
    montant: float
    devise: str = "XAF"
    mode_paiement: str = "virement"
    reference_bancaire: Optional[str] = None
    banque: Optional[str] = None
    notes: Optional[str] = None
    effectue_par: Optional[str] = None


class PaiementResponse(BaseModel):
    id: int
    numero_reglement: str
    facture_id: int
    date_reglement: date
    montant: float
    devise: str
    mode_paiement: str
    reference_bancaire: Optional[str] = None
    banque: Optional[str] = None
    notes: Optional[str] = None
    effectue_par: Optional[str] = None
    statut: str
    created_at: datetime
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True


# Compte schemas
class CompteCreate(BaseModel):
    numero_compte: str
    intitule: str
    type_compte: str = "courant"
    solde_initial: float = 0.0
    devise: str = "XAF"


class CompteResponse(BaseModel):
    id: int
    numero_compte: str
    intitule: str
    type_compte: str
    solde_initial: float
    devise: str
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True
