"""Schemas pour la finance avancée - Trésorerie, Créances, Dettes, Budget"""
from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import date
from decimal import Decimal


# ============ TRÉSORERIE ============

class TableauBordTresorerieResponse(BaseModel):
    date: date
    encaissements: Decimal
    decaissements: Decimal
    solde_tresorerie: Decimal
    creances_a_recevoir: Decimal
    dettes_a_payer: Decimal
    besoin_fdr: Decimal


class PrevisionsTresorerieResponse(BaseModel):
    horizon_jours: int
    date_debut: date
    date_fin: date
    encaissements_prevus: Decimal
    decaissements_prevus: Decimal
    solde_prevu: Decimal


class BFRResponse(BaseModel):
    periode: str
    stock_moyen: Decimal
    creances_clients: Decimal
    dettes_fournisseurs: Decimal
    bfr: Decimal


# ============ CRÉANCES ============

class BalanceAgeeClientsResponse(BaseModel):
    client_id: int
    client_nom: str
    total_solde: Decimal
    nombre_factures: int


class DSOResponse(BaseModel):
    periode: str
    creances: Decimal
    ventes: Decimal
    jours_periode: int
    ventes_quotidiennes: Decimal
    dso: float


class ScoringClientResponse(BaseModel):
    client_id: int
    client_nom: str
    nombre_factures: int
    factures_en_retard: int
    taux_paiement: float
    score: float


# ============ DETTES ============

class BalanceAgeeFournisseursResponse(BaseModel):
    fournisseur_id: int
    fournisseur_nom: str
    total_solde: Decimal
    nombre_factures: int


class DPOResponse(BaseModel):
    periode: str
    dettes: Decimal
    achats: Decimal
    jours_periode: int
    achats_quotidiens: Decimal
    dpo: float


# ============ BUDGET ============

class BudgetAnnuelRequest(BaseModel):
    exercice_id: int
    total: Decimal
    details: dict


class BudgetAnnuelResponse(BaseModel):
    exercice_id: int
    budget_total: Decimal
    statut: str


class SuiviBudgetResponse(BaseModel):
    exercice_id: int
    periode: str
    budget: Decimal
    realise: Decimal
    ecart: Decimal
    taux_realisation: float