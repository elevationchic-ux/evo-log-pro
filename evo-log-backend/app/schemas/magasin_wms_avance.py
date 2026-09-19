"""Schemas Pydantic pour Magasin WMS Avancé (Picking FIFO/FEFO, Inventaires OHADA)"""
from pydantic import BaseModel, Field
from typing import List, Optional


class VaguePickingRequest(BaseModel):
    commandes_ids: List[int] = Field(..., description="Liste des IDs de commandes à inclure dans la vague")
    regle: str = Field("FEFO", pattern="^(FIFO|FEFO|LIFO)$", description="Règle de gestion des lots: FIFO, FEFO ou LIFO")


class LigneVaguePicking(BaseModel):
    commande_id: int
    article_code: str
    emplacement: str
    quantite: float
    lot_numero: str
    date_expiration: Optional[str] = None
    distance_parcours_m: int


class VaguePickingResponse(BaseModel):
    vague_code: str
    regle_appliquee: str
    nb_lignes: int
    distance_totale_m: int
    temps_estime_min: int
    lignes: List[LigneVaguePicking]


class LigneComptageInventaire(BaseModel):
    article_code: str
    emplacement: str
    quantite_physique: float
    quantite_theorique: float


class CampagneInventaireRequest(BaseModel):
    campagne_id: int
    lignes_comptage: List[LigneComptageInventaire]


class EcartInventaire(BaseModel):
    article_code: str
    emplacement: str
    ecart_quantite: float
    valeur_ecart_xaf: float
    imputation_comptable: str


class InventaireRegularisationResponse(BaseModel):
    campagne_id: int
    nb_articles_controles: int
    nb_ecarts_detectes: int
    valeur_totale_ecarts_xaf: float
    ecarts: List[EcartInventaire]
    pv_reference: str
    journal_comptable: str = "603 - Variations de stocks (OHADA)"
