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
    # code_sh reste requis (position SH saisie) ; la resolution du taux_dd suit
    # l'ordre du moteur UNIQUE : nomenclature CEMAC -> taux explicite -> categorie
    # TEC -> defaut de simulation. Aucun taux n'est jamais invente silencieusement.
    code_sh: str
    regime: str = "IM4"
    origine: str = "HORS_ZONE"
    # Secours honnetes quand la nomenclature n'est pas encore importee en base :
    # categorie TEC (0..3) ou taux DD saisi explicitement (en % ou fraction).
    categorie_tec: Optional[int] = None
    taux_dd_explicite: Optional[float] = None


class TaxationResultResponse(BaseModel):
    valeur_cif_xaf: float
    taux_dd: float
    taux_tva: float
    droit_douane_dd: float
    redevance_informatique: float
    cci_cemac: float
    prelevement_ohada: float
    base_tva: float
    tva_1925: float
    precompte_is: float
    total_a_liquider_xaf: float
    devise: str = "XAF"
    regime: str = "IM4"
    origine: str = "HORS_ZONE"
    # Provenance du taux + caractere simulateur : rendus visibles a l'ecran pour
    # que l'utilisateur sache si le montant repose sur la nomenclature officielle
    # ou sur une hypothese de simulation.
    source_taux: str
    simulation: bool
    note: str


class GuceTeletransmissionResponse(BaseModel):
    reference_guce: str
    numero_dum: str
    statut_reception: str
    message: str
    date_acquit: str
