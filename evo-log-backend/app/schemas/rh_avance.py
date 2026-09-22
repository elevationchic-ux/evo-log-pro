"""Schemas Pydantic pour les fonctionnalités RH Avancées - Paie OHADA, Recrutement, Formations"""
from datetime import datetime, date
from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field


# --- PAIE OHADA CAMEROUN ---
class BulletinPaieRequest(BaseModel):
    employe_id: int
    periode: str = Field(..., description="Format YYYY-MM (ex: 2026-08)")
    salaire_base: Optional[float] = None
    primes: Optional[float] = 0.0
    heures_sup: Optional[float] = 0.0


class BulletinPaieResponse(BaseModel):
    employe_id: int
    employe_nom: str
    periode: str
    salaire_base: float
    heures_supplementaires: float
    montant_heures_sup: float
    primes: float
    salaire_brut: float
    cnps_retraites: float
    cnps_accidents: float
    total_cnps: float
    irmg: float
    net_a_payer: float
    devise: str = "XAF"


class ChargesSocialesResponse(BaseModel):
    employe_id: int
    periode: str
    salaire_brut: float
    part_salariale: Dict[str, float]
    part_patronale: Dict[str, float]
    total_cotisations: float
    devise: str = "XAF"


class DIPEResponse(BaseModel):
    periode: str
    nombre_employes: int
    masse_salariale_brute: float
    total_cnps_patronal: float
    total_cnps_salarial: float
    total_irmg_retenu: float
    total_credit_foncier: float
    total_fne: float
    lignes_dipe: List[Dict[str, Any]]
    date_generation: str


# --- RECRUTEMENT ---
class OffreEmploiCreate(BaseModel):
    titre: str
    departement: str
    type_contrat: str = "CDI"
    description: str
    competences_requises: List[str] = []
    salaire_min: Optional[float] = None
    salaire_max: Optional[float] = None


class CandidatureCreate(BaseModel):
    offre_id: int
    candidat_nom: str
    email: str
    telephone: str
    cv_url: Optional[str] = None
    experience_annees: int = 0
    statut: str = "RECU"


# --- FORMATIONS ---
class FormationPlanCreate(BaseModel):
    titre: str
    categorie: str = "SECURITE_PORTUAIRE"
    duree_heures: int
    cout_par_personne: float
    formateur_ou_organisme: str
    date_debut: date
    date_fin: date


class InscriptionFormationRequest(BaseModel):
    formation_id: int
    employe_ids: List[int]
