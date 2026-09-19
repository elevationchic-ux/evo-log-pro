"""Schemas Pydantic pour le module Transit & Douane Avancé (DUM, GUCE, Taxation TEC CEMAC)"""
from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field


class DumCreateRequest(BaseModel):
    regime: str = Field(..., description="Régime douanier: IM4 (Mise à la consommation), IM7 (Entrepôt), T1 (Transit)")
    importateur_id: int
    valeur_cif_xaf: float
    code_sh: str = Field(..., description="Code Système Harmonisé 6 ou 8 chiffres")
    pays_origine: str = "FR"


class SimulationTaxationRequest(BaseModel):
    valeur_cif_xaf: float
    code_sh: str
    regime: str = "IM4"


class TaxationResultResponse(BaseModel):
    valeur_cif_xaf: float
    droit_douane_dd: float
    redevance_informatique: float
    cci_cemac: float
    base_tva: float
    tva_1925: float
    precompte_is: float
    total_a_liquider_xaf: float
    devise: str = "XAF"


class GuceTeletransmissionResponse(BaseModel):
    reference_guce: str
    numero_dum: str
    statut_reception: str
    message: str
    date_acquit: str
