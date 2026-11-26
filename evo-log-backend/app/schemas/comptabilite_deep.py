"""Schemas Pydantic pour comptabilite-ohada (genere)."""
from pydantic import BaseModel
from typing import Optional
from datetime import datetime, date


class AssetRegistrationCreate(BaseModel):
    numero_inventaire: str
    designation: Optional[str] = None
    categorie: Optional[str] = None
    date_acquisition: Optional[date] = None
    valeur_acquisition_xaf: Optional[float] = None
    valeur_residuelle_xaf: Optional[float] = None
    duree_amortissement_an: Optional[int] = None
    mode_amortissement: Optional[str] = None
    compte_immo: Optional[str] = None
    statut: Optional[str] = None


class AssetRegistrationUpdate(BaseModel):
    numero_inventaire: Optional[str] = None
    designation: Optional[str] = None
    categorie: Optional[str] = None
    date_acquisition: Optional[date] = None
    valeur_acquisition_xaf: Optional[float] = None
    valeur_residuelle_xaf: Optional[float] = None
    duree_amortissement_an: Optional[int] = None
    mode_amortissement: Optional[str] = None
    compte_immo: Optional[str] = None
    statut: Optional[str] = None
    is_active: Optional[bool] = None


class AssetRegistrationOut(BaseModel):
    id: int
    company_id: int
    numero_inventaire: str
    designation: Optional[str] = None
    categorie: Optional[str] = None
    date_acquisition: Optional[date] = None
    valeur_acquisition_xaf: Optional[float] = None
    valeur_residuelle_xaf: Optional[float] = None
    duree_amortissement_an: Optional[int] = None
    mode_amortissement: Optional[str] = None
    compte_immo: Optional[str] = None
    statut: Optional[str] = None
    is_active: Optional[bool] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    model_config = {"from_attributes": True}


class DepreciationScheduleCreate(BaseModel):
    reference: str
    asset_id: Optional[int] = None
    exercice: Optional[int] = None
    dotation_xaf: Optional[float] = None
    cumul_xaf: Optional[float] = None
    valeur_nette_xaf: Optional[float] = None
    date_ecriture: Optional[date] = None
    statut: Optional[str] = None


class DepreciationScheduleUpdate(BaseModel):
    reference: Optional[str] = None
    asset_id: Optional[int] = None
    exercice: Optional[int] = None
    dotation_xaf: Optional[float] = None
    cumul_xaf: Optional[float] = None
    valeur_nette_xaf: Optional[float] = None
    date_ecriture: Optional[date] = None
    statut: Optional[str] = None
    is_active: Optional[bool] = None


class DepreciationScheduleOut(BaseModel):
    id: int
    company_id: int
    reference: str
    asset_id: Optional[int] = None
    exercice: Optional[int] = None
    dotation_xaf: Optional[float] = None
    cumul_xaf: Optional[float] = None
    valeur_nette_xaf: Optional[float] = None
    date_ecriture: Optional[date] = None
    statut: Optional[str] = None
    is_active: Optional[bool] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    model_config = {"from_attributes": True}


class ProvisionCreate(BaseModel):
    reference: str
    type_provision: Optional[str] = None
    exercice: Optional[int] = None
    montant_xaf: Optional[float] = None
    date_constat: Optional[date] = None
    compte_charge: Optional[str] = None
    comporte_passif: Optional[str] = None
    statut: Optional[str] = None
    motivation: Optional[str] = None


class ProvisionUpdate(BaseModel):
    reference: Optional[str] = None
    type_provision: Optional[str] = None
    exercice: Optional[int] = None
    montant_xaf: Optional[float] = None
    date_constat: Optional[date] = None
    compte_charge: Optional[str] = None
    comporte_passif: Optional[str] = None
    statut: Optional[str] = None
    motivation: Optional[str] = None
    is_active: Optional[bool] = None


class ProvisionOut(BaseModel):
    id: int
    company_id: int
    reference: str
    type_provision: Optional[str] = None
    exercice: Optional[int] = None
    montant_xaf: Optional[float] = None
    date_constat: Optional[date] = None
    compte_charge: Optional[str] = None
    comporte_passif: Optional[str] = None
    statut: Optional[str] = None
    motivation: Optional[str] = None
    is_active: Optional[bool] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    model_config = {"from_attributes": True}


class BankReconciliationCreate(BaseModel):
    reference: str
    compte_banque: Optional[str] = None
    periode_debut: Optional[date] = None
    periode_fin: Optional[date] = None
    solde_banque_xaf: Optional[float] = None
    solde_compta_xaf: Optional[float] = None
    ecart_xaf: Optional[float] = None
    nb_lignes_pointees: Optional[int] = None
    statut: Optional[str] = None


class BankReconciliationUpdate(BaseModel):
    reference: Optional[str] = None
    compte_banque: Optional[str] = None
    periode_debut: Optional[date] = None
    periode_fin: Optional[date] = None
    solde_banque_xaf: Optional[float] = None
    solde_compta_xaf: Optional[float] = None
    ecart_xaf: Optional[float] = None
    nb_lignes_pointees: Optional[int] = None
    statut: Optional[str] = None
    is_active: Optional[bool] = None


class BankReconciliationOut(BaseModel):
    id: int
    company_id: int
    reference: str
    compte_banque: Optional[str] = None
    periode_debut: Optional[date] = None
    periode_fin: Optional[date] = None
    solde_banque_xaf: Optional[float] = None
    solde_compta_xaf: Optional[float] = None
    ecart_xaf: Optional[float] = None
    nb_lignes_pointees: Optional[int] = None
    statut: Optional[str] = None
    is_active: Optional[bool] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    model_config = {"from_attributes": True}


class IntercompanyEntryCreate(BaseModel):
    reference: str
    entite_emettrice: Optional[str] = None
    entite_destinatrice: Optional[str] = None
    date_ecriture: Optional[date] = None
    montant_xaf: Optional[float] = None
    nature: Optional[str] = None
    statut: Optional[str] = None
    notes: Optional[str] = None


class IntercompanyEntryUpdate(BaseModel):
    reference: Optional[str] = None
    entite_emettrice: Optional[str] = None
    entite_destinatrice: Optional[str] = None
    date_ecriture: Optional[date] = None
    montant_xaf: Optional[float] = None
    nature: Optional[str] = None
    statut: Optional[str] = None
    notes: Optional[str] = None
    is_active: Optional[bool] = None


class IntercompanyEntryOut(BaseModel):
    id: int
    company_id: int
    reference: str
    entite_emettrice: Optional[str] = None
    entite_destinatrice: Optional[str] = None
    date_ecriture: Optional[date] = None
    montant_xaf: Optional[float] = None
    nature: Optional[str] = None
    statut: Optional[str] = None
    notes: Optional[str] = None
    is_active: Optional[bool] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    model_config = {"from_attributes": True}


class BudgetControlCreate(BaseModel):
    reference: str
    centre_cout: Optional[str] = None
    exercice: Optional[int] = None
    budget_prevu_xaf: Optional[float] = None
    consomme_xaf: Optional[float] = None
    engagement_xaf: Optional[float] = None
    ecart_pct: Optional[float] = None
    statut: Optional[str] = None


class BudgetControlUpdate(BaseModel):
    reference: Optional[str] = None
    centre_cout: Optional[str] = None
    exercice: Optional[int] = None
    budget_prevu_xaf: Optional[float] = None
    consomme_xaf: Optional[float] = None
    engagement_xaf: Optional[float] = None
    ecart_pct: Optional[float] = None
    statut: Optional[str] = None
    is_active: Optional[bool] = None


class BudgetControlOut(BaseModel):
    id: int
    company_id: int
    reference: str
    centre_cout: Optional[str] = None
    exercice: Optional[int] = None
    budget_prevu_xaf: Optional[float] = None
    consomme_xaf: Optional[float] = None
    engagement_xaf: Optional[float] = None
    ecart_pct: Optional[float] = None
    statut: Optional[str] = None
    is_active: Optional[bool] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    model_config = {"from_attributes": True}


class AuditPafCreate(BaseModel):
    hash_ligne: str
    date_ecriture: Optional[date] = None
    numero_piece: Optional[str] = None
    compte: Optional[str] = None
    libelle: Optional[str] = None
    debit_xaf: Optional[float] = None
    credit_xaf: Optional[float] = None
    hash_precedent: Optional[str] = None
    validite: Optional[bool] = None


class AuditPafUpdate(BaseModel):
    hash_ligne: Optional[str] = None
    date_ecriture: Optional[date] = None
    numero_piece: Optional[str] = None
    compte: Optional[str] = None
    libelle: Optional[str] = None
    debit_xaf: Optional[float] = None
    credit_xaf: Optional[float] = None
    hash_precedent: Optional[str] = None
    validite: Optional[bool] = None
    is_active: Optional[bool] = None


class AuditPafOut(BaseModel):
    id: int
    company_id: int
    hash_ligne: str
    date_ecriture: Optional[date] = None
    numero_piece: Optional[str] = None
    compte: Optional[str] = None
    libelle: Optional[str] = None
    debit_xaf: Optional[float] = None
    credit_xaf: Optional[float] = None
    hash_precedent: Optional[str] = None
    validite: Optional[bool] = None
    is_active: Optional[bool] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    model_config = {"from_attributes": True}


class TaxDeclarationCreate(BaseModel):
    reference: str
    type_declaration: Optional[str] = None
    periode_debut: Optional[date] = None
    periode_fin: Optional[date] = None
    base_imposable_xaf: Optional[float] = None
    droits_xaf: Optional[float] = None
    date_depot: Optional[date] = None
    statut: Optional[str] = None


class TaxDeclarationUpdate(BaseModel):
    reference: Optional[str] = None
    type_declaration: Optional[str] = None
    periode_debut: Optional[date] = None
    periode_fin: Optional[date] = None
    base_imposable_xaf: Optional[float] = None
    droits_xaf: Optional[float] = None
    date_depot: Optional[date] = None
    statut: Optional[str] = None
    is_active: Optional[bool] = None


class TaxDeclarationOut(BaseModel):
    id: int
    company_id: int
    reference: str
    type_declaration: Optional[str] = None
    periode_debut: Optional[date] = None
    periode_fin: Optional[date] = None
    base_imposable_xaf: Optional[float] = None
    droits_xaf: Optional[float] = None
    date_depot: Optional[date] = None
    statut: Optional[str] = None
    is_active: Optional[bool] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    model_config = {"from_attributes": True}


class PayrollEntryCreate(BaseModel):
    reference: str
    periode: Optional[str] = None
    masse_salariale_xaf: Optional[float] = None
    charges_patronales_xaf: Optional[float] = None
    impot_retenu_xaf: Optional[float] = None
    net_paye_xaf: Optional[float] = None
    date_passage: Optional[date] = None
    statut: Optional[str] = None


class PayrollEntryUpdate(BaseModel):
    reference: Optional[str] = None
    periode: Optional[str] = None
    masse_salariale_xaf: Optional[float] = None
    charges_patronales_xaf: Optional[float] = None
    impot_retenu_xaf: Optional[float] = None
    net_paye_xaf: Optional[float] = None
    date_passage: Optional[date] = None
    statut: Optional[str] = None
    is_active: Optional[bool] = None


class PayrollEntryOut(BaseModel):
    id: int
    company_id: int
    reference: str
    periode: Optional[str] = None
    masse_salariale_xaf: Optional[float] = None
    charges_patronales_xaf: Optional[float] = None
    impot_retenu_xaf: Optional[float] = None
    net_paye_xaf: Optional[float] = None
    date_passage: Optional[date] = None
    statut: Optional[str] = None
    is_active: Optional[bool] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    model_config = {"from_attributes": True}


class TreasuryAccountCreate(BaseModel):
    code_compte: str
    intitule: Optional[str] = None
    type_compte: Optional[str] = None
    banque: Optional[str] = None
    rib: Optional[str] = None
    solde_actuel_xaf: Optional[float] = None
    devise: Optional[str] = None
    responsable: Optional[str] = None
    statut: Optional[str] = None


class TreasuryAccountUpdate(BaseModel):
    code_compte: Optional[str] = None
    intitule: Optional[str] = None
    type_compte: Optional[str] = None
    banque: Optional[str] = None
    rib: Optional[str] = None
    solde_actuel_xaf: Optional[float] = None
    devise: Optional[str] = None
    responsable: Optional[str] = None
    statut: Optional[str] = None
    is_active: Optional[bool] = None


class TreasuryAccountOut(BaseModel):
    id: int
    company_id: int
    code_compte: str
    intitule: Optional[str] = None
    type_compte: Optional[str] = None
    banque: Optional[str] = None
    rib: Optional[str] = None
    solde_actuel_xaf: Optional[float] = None
    devise: Optional[str] = None
    responsable: Optional[str] = None
    statut: Optional[str] = None
    is_active: Optional[bool] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    model_config = {"from_attributes": True}


class AnalyticalSectionCreate(BaseModel):
    code_section: str
    intitule: Optional[str] = None
    type_section: Optional[str] = None
    cle_repartition: Optional[str] = None
    unite_oeuvre: Optional[str] = None
    cout_total_xaf: Optional[float] = None
    actif: Optional[bool] = None


class AnalyticalSectionUpdate(BaseModel):
    code_section: Optional[str] = None
    intitule: Optional[str] = None
    type_section: Optional[str] = None
    cle_repartition: Optional[str] = None
    unite_oeuvre: Optional[str] = None
    cout_total_xaf: Optional[float] = None
    actif: Optional[bool] = None
    is_active: Optional[bool] = None


class AnalyticalSectionOut(BaseModel):
    id: int
    company_id: int
    code_section: str
    intitule: Optional[str] = None
    type_section: Optional[str] = None
    cle_repartition: Optional[str] = None
    unite_oeuvre: Optional[str] = None
    cout_total_xaf: Optional[float] = None
    actif: Optional[bool] = None
    is_active: Optional[bool] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    model_config = {"from_attributes": True}

