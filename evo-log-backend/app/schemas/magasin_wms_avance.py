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
    # Lot/expiration : aucun modele "lot" ni "date_peremption" n'existe en base;
    # ces champs ne sont plus remplis avec des valeurs inventees.
    lot_numero: Optional[str] = None
    date_expiration: Optional[str] = None
    # Distance physique entre cases : non mesuree en base -> jamais simulee.
    distance_parcours_m: Optional[int] = None


class VaguePickingResponse(BaseModel):
    vague_code: str
    regle_appliquee: str
    nb_lignes: int
    distance_totale_m: Optional[int] = None
    temps_estime_min: int
    lignes: List[LigneVaguePicking]
    note: Optional[str] = None


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
    # Honnetete produit : la regularisation n'ecrit rien en base (aucune table
    # de campagne) -> le statut doit rester visible de l'appelant.
    statut: Optional[str] = None
    note: Optional[str] = None
