"""Schemas Pydantic pour finance-ohada (genere)."""
from pydantic import BaseModel
from typing import Optional
from datetime import datetime, date


class MultiyearBudgetCreate(BaseModel):
    reference: str
    exercice_debut: Optional[int] = None
    exercice_fin: Optional[int] = None
    montant_prevu_xaf: Optional[float] = None
    axes_strategiques: Optional[str] = None
    vote_ba: Optional[bool] = None
    statut: Optional[str] = None


class MultiyearBudgetUpdate(BaseModel):
    reference: Optional[str] = None
    exercice_debut: Optional[int] = None
    exercice_fin: Optional[int] = None
    montant_prevu_xaf: Optional[float] = None
    axes_strategiques: Optional[str] = None
    vote_ba: Optional[bool] = None
    statut: Optional[str] = None
    is_active: Optional[bool] = None


class MultiyearBudgetOut(BaseModel):
    id: int
    company_id: int
    reference: str
    exercice_debut: Optional[int] = None
    exercice_fin: Optional[int] = None
    montant_prevu_xaf: Optional[float] = None
    axes_strategiques: Optional[str] = None
    vote_ba: Optional[bool] = None
    statut: Optional[str] = None
    is_active: Optional[bool] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    model_config = {"from_attributes": True}


class CreditFacilityCreate(BaseModel):
    reference: str
    banque: Optional[str] = None
    type_facilite: Optional[str] = None
    montant_autorise_xaf: Optional[float] = None
    montant_utilise_xaf: Optional[float] = None
    taux_interet_pct: Optional[float] = None
    date_debut: Optional[date] = None
    date_fin: Optional[date] = None
    statut: Optional[str] = None


class CreditFacilityUpdate(BaseModel):
    reference: Optional[str] = None
    banque: Optional[str] = None
    type_facilite: Optional[str] = None
    montant_autorise_xaf: Optional[float] = None
    montant_utilise_xaf: Optional[float] = None
    taux_interet_pct: Optional[float] = None
    date_debut: Optional[date] = None
    date_fin: Optional[date] = None
    statut: Optional[str] = None
    is_active: Optional[bool] = None


class CreditFacilityOut(BaseModel):
    id: int
    company_id: int
    reference: str
    banque: Optional[str] = None
    type_facilite: Optional[str] = None
    montant_autorise_xaf: Optional[float] = None
    montant_utilise_xaf: Optional[float] = None
    taux_interet_pct: Optional[float] = None
    date_debut: Optional[date] = None
    date_fin: Optional[date] = None
    statut: Optional[str] = None
    is_active: Optional[bool] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    model_config = {"from_attributes": True}


class CashPoolCreate(BaseModel):
    reference: str
    entite_pilote: Optional[str] = None
    entites_participantes: Optional[str] = None
    montant_pool_xaf: Optional[float] = None
    interet_intragroupe_pct: Optional[float] = None
    date_debut: Optional[date] = None
    statut: Optional[str] = None


class CashPoolUpdate(BaseModel):
    reference: Optional[str] = None
    entite_pilote: Optional[str] = None
    entites_participantes: Optional[str] = None
    montant_pool_xaf: Optional[float] = None
    interet_intragroupe_pct: Optional[float] = None
    date_debut: Optional[date] = None
    statut: Optional[str] = None
    is_active: Optional[bool] = None


class CashPoolOut(BaseModel):
    id: int
    company_id: int
    reference: str
    entite_pilote: Optional[str] = None
    entites_participantes: Optional[str] = None
    montant_pool_xaf: Optional[float] = None
    interet_intragroupe_pct: Optional[float] = None
    date_debut: Optional[date] = None
    statut: Optional[str] = None
    is_active: Optional[bool] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    model_config = {"from_attributes": True}


class FinancialInvestmentCreate(BaseModel):
    reference: str
    type_placement: Optional[str] = None
    institution: Optional[str] = None
    montant_place_xaf: Optional[float] = None
    rendement_attendu_pct: Optional[float] = None
    date_debut: Optional[date] = None
    date_echeance: Optional[date] = None
    statut: Optional[str] = None


class FinancialInvestmentUpdate(BaseModel):
    reference: Optional[str] = None
    type_placement: Optional[str] = None
    institution: Optional[str] = None
    montant_place_xaf: Optional[float] = None
    rendement_attendu_pct: Optional[float] = None
    date_debut: Optional[date] = None
    date_echeance: Optional[date] = None
    statut: Optional[str] = None
    is_active: Optional[bool] = None


class FinancialInvestmentOut(BaseModel):
    id: int
    company_id: int
    reference: str
    type_placement: Optional[str] = None
    institution: Optional[str] = None
    montant_place_xaf: Optional[float] = None
    rendement_attendu_pct: Optional[float] = None
    date_debut: Optional[date] = None
    date_echeance: Optional[date] = None
    statut: Optional[str] = None
    is_active: Optional[bool] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    model_config = {"from_attributes": True}


class FxExposureCreate(BaseModel):
    reference: str
    devise: Optional[str] = None
    exposition_nette: Optional[float] = None
    valeur_couverte: Optional[float] = None
    instrument_couverture: Optional[str] = None
    taux_couverture_pct: Optional[float] = None
    date_echeance: Optional[date] = None
    statut: Optional[str] = None


class FxExposureUpdate(BaseModel):
    reference: Optional[str] = None
    devise: Optional[str] = None
    exposition_nette: Optional[float] = None
    valeur_couverte: Optional[float] = None
    instrument_couverture: Optional[str] = None
    taux_couverture_pct: Optional[float] = None
    date_echeance: Optional[date] = None
    statut: Optional[str] = None
    is_active: Optional[bool] = None


class FxExposureOut(BaseModel):
    id: int
    company_id: int
    reference: str
    devise: Optional[str] = None
    exposition_nette: Optional[float] = None
    valeur_couverte: Optional[float] = None
    instrument_couverture: Optional[str] = None
    taux_couverture_pct: Optional[float] = None
    date_echeance: Optional[date] = None
    statut: Optional[str] = None
    is_active: Optional[bool] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    model_config = {"from_attributes": True}


class PaymentScheduleCreate(BaseModel):
    reference: str
    fournisseur_id: Optional[int] = None
    facture_id: Optional[int] = None
    montant_echeance_xaf: Optional[float] = None
    date_echeance: Optional[date] = None
    mode_reglement: Optional[str] = None
    statut: Optional[str] = None


class PaymentScheduleUpdate(BaseModel):
    reference: Optional[str] = None
    fournisseur_id: Optional[int] = None
    facture_id: Optional[int] = None
    montant_echeance_xaf: Optional[float] = None
    date_echeance: Optional[date] = None
    mode_reglement: Optional[str] = None
    statut: Optional[str] = None
    is_active: Optional[bool] = None


class PaymentScheduleOut(BaseModel):
    id: int
    company_id: int
    reference: str
    fournisseur_id: Optional[int] = None
    facture_id: Optional[int] = None
    montant_echeance_xaf: Optional[float] = None
    date_echeance: Optional[date] = None
    mode_reglement: Optional[str] = None
    statut: Optional[str] = None
    is_active: Optional[bool] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    model_config = {"from_attributes": True}


class ExpenseReportCreate(BaseModel):
    numero_note_frais: str
    employe_id: Optional[int] = None
    periode: Optional[str] = None
    montant_total_xaf: Optional[float] = None
    nb_justificatifs: Optional[int] = None
    date_depot: Optional[date] = None
    validateur: Optional[str] = None
    statut: Optional[str] = None


class ExpenseReportUpdate(BaseModel):
    numero_note_frais: Optional[str] = None
    employe_id: Optional[int] = None
    periode: Optional[str] = None
    montant_total_xaf: Optional[float] = None
    nb_justificatifs: Optional[int] = None
    date_depot: Optional[date] = None
    validateur: Optional[str] = None
    statut: Optional[str] = None
    is_active: Optional[bool] = None


class ExpenseReportOut(BaseModel):
    id: int
    company_id: int
    numero_note_frais: str
    employe_id: Optional[int] = None
    periode: Optional[str] = None
    montant_total_xaf: Optional[float] = None
    nb_justificatifs: Optional[int] = None
    date_depot: Optional[date] = None
    validateur: Optional[str] = None
    statut: Optional[str] = None
    is_active: Optional[bool] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    model_config = {"from_attributes": True}


class PettyCashBoxCreate(BaseModel):
    code_regie: str
    lieu: Optional[str] = None
    responsable: Optional[str] = None
    fond_initial_xaf: Optional[float] = None
    solde_actuel_xaf: Optional[float] = None
    date_derniere_reconciliation: Optional[date] = None
    statut: Optional[str] = None


class PettyCashBoxUpdate(BaseModel):
    code_regie: Optional[str] = None
    lieu: Optional[str] = None
    responsable: Optional[str] = None
    fond_initial_xaf: Optional[float] = None
    solde_actuel_xaf: Optional[float] = None
    date_derniere_reconciliation: Optional[date] = None
    statut: Optional[str] = None
    is_active: Optional[bool] = None


class PettyCashBoxOut(BaseModel):
    id: int
    company_id: int
    code_regie: str
    lieu: Optional[str] = None
    responsable: Optional[str] = None
    fond_initial_xaf: Optional[float] = None
    solde_actuel_xaf: Optional[float] = None
    date_derniere_reconciliation: Optional[date] = None
    statut: Optional[str] = None
    is_active: Optional[bool] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    model_config = {"from_attributes": True}


class BankGuaranteeCreate(BaseModel):
    reference: str
    banque_emettrice: Optional[str] = None
    beneficiaire: Optional[str] = None
    type_garantie: Optional[str] = None
    montant_xaf: Optional[float] = None
    commission_pct: Optional[float] = None
    date_debut: Optional[date] = None
    date_fin: Optional[date] = None
    statut: Optional[str] = None


class BankGuaranteeUpdate(BaseModel):
    reference: Optional[str] = None
    banque_emettrice: Optional[str] = None
    beneficiaire: Optional[str] = None
    type_garantie: Optional[str] = None
    montant_xaf: Optional[float] = None
    commission_pct: Optional[float] = None
    date_debut: Optional[date] = None
    date_fin: Optional[date] = None
    statut: Optional[str] = None
    is_active: Optional[bool] = None


class BankGuaranteeOut(BaseModel):
    id: int
    company_id: int
    reference: str
    banque_emettrice: Optional[str] = None
    beneficiaire: Optional[str] = None
    type_garantie: Optional[str] = None
    montant_xaf: Optional[float] = None
    commission_pct: Optional[float] = None
    date_debut: Optional[date] = None
    date_fin: Optional[date] = None
    statut: Optional[str] = None
    is_active: Optional[bool] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    model_config = {"from_attributes": True}


class LeaseContractCreate(BaseModel):
    reference: str
    type_contrat: Optional[str] = None
    bien_concerne: Optional[str] = None
    loyer_mensuel_xaf: Optional[float] = None
    duree_mois: Optional[int] = None
    valeur_residuelle_xaf: Optional[float] = None
    date_debut: Optional[date] = None
    statut: Optional[str] = None


class LeaseContractUpdate(BaseModel):
    reference: Optional[str] = None
    type_contrat: Optional[str] = None
    bien_concerne: Optional[str] = None
    loyer_mensuel_xaf: Optional[float] = None
    duree_mois: Optional[int] = None
    valeur_residuelle_xaf: Optional[float] = None
    date_debut: Optional[date] = None
    statut: Optional[str] = None
    is_active: Optional[bool] = None


class LeaseContractOut(BaseModel):
    id: int
    company_id: int
    reference: str
    type_contrat: Optional[str] = None
    bien_concerne: Optional[str] = None
    loyer_mensuel_xaf: Optional[float] = None
    duree_mois: Optional[int] = None
    valeur_residuelle_xaf: Optional[float] = None
    date_debut: Optional[date] = None
    statut: Optional[str] = None
    is_active: Optional[bool] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    model_config = {"from_attributes": True}


class CashForecastCreate(BaseModel):
    reference: str
    horizon_mois: Optional[int] = None
    entree_attendue_xaf: Optional[float] = None
    sortie_attendue_xaf: Optional[float] = None
    tresorerie_projete_xaf: Optional[float] = None
    hypothese: Optional[str] = None
    date_revision: Optional[date] = None


class CashForecastUpdate(BaseModel):
    reference: Optional[str] = None
    horizon_mois: Optional[int] = None
    entree_attendue_xaf: Optional[float] = None
    sortie_attendue_xaf: Optional[float] = None
    tresorerie_projete_xaf: Optional[float] = None
    hypothese: Optional[str] = None
    date_revision: Optional[date] = None
    is_active: Optional[bool] = None


class CashForecastOut(BaseModel):
    id: int
    company_id: int
    reference: str
    horizon_mois: Optional[int] = None
    entree_attendue_xaf: Optional[float] = None
    sortie_attendue_xaf: Optional[float] = None
    tresorerie_projete_xaf: Optional[float] = None
    hypothese: Optional[str] = None
    date_revision: Optional[date] = None
    is_active: Optional[bool] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    model_config = {"from_attributes": True}


class TreasuryAlertCreate(BaseModel):
    reference: str
    type_alerte: Optional[str] = None
    seuil_declencheur: Optional[float] = None
    valeur_constatee: Optional[float] = None
    date_alerte: Optional[datetime] = None
    destinataire: Optional[str] = None
    statut: Optional[str] = None


class TreasuryAlertUpdate(BaseModel):
    reference: Optional[str] = None
    type_alerte: Optional[str] = None
    seuil_declencheur: Optional[float] = None
    valeur_constatee: Optional[float] = None
    date_alerte: Optional[datetime] = None
    destinataire: Optional[str] = None
    statut: Optional[str] = None
    is_active: Optional[bool] = None


class TreasuryAlertOut(BaseModel):
    id: int
    company_id: int
    reference: str
    type_alerte: Optional[str] = None
    seuil_declencheur: Optional[float] = None
    valeur_constatee: Optional[float] = None
    date_alerte: Optional[datetime] = None
    destinataire: Optional[str] = None
    statut: Optional[str] = None
    is_active: Optional[bool] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    model_config = {"from_attributes": True}

