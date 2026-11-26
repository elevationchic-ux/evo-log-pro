"""Schemas du domaine « exploitation magasin » (Tranche D).

Couvre les ressources appellees par le frontend sous /api/v1/magasin/* :
magasins (entrepots), exploitation des stocks, historique des mouvements,
import/export CSV, analytics et rapports. Tous les champs sont calculs depuis
les tables reelles (stocks, mouvements_stocks, entrepots, articles, commandes,
bandes_livraison, tiers)  aucune donnee n'est simulee.
"""
from __future__ import annotations

from datetime import datetime
from typing import Any, List, Optional

from pydantic import BaseModel, Field


# ─── MAGASINS (ENTREPOTS) ────────────────────────────────────────────────────
class MagasinBase(BaseModel):
    code: str = Field(min_length=1, max_length=20)
    nom: str = Field(min_length=1, max_length=100)
    adresse: Optional[str] = None
    ville: Optional[str] = None
    telephone: Optional[str] = None
    responsable: Optional[str] = None
    capacite: Optional[float] = None
    superficie: Optional[float] = None
    is_active: bool = True


class MagasinCreate(MagasinBase):
    pass


class MagasinUpdate(BaseModel):
    code: Optional[str] = None
    nom: Optional[str] = None
    adresse: Optional[str] = None
    ville: Optional[str] = None
    telephone: Optional[str] = None
    responsable: Optional[str] = None
    capacite: Optional[float] = None
    superficie: Optional[float] = None
    is_active: Optional[bool] = None


class MagasinResponse(MagasinBase):
    id: int
    company_id: Optional[int] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True


# ─── STOCKS ──────────────────────────────────────────────────────────────────
class StockLine(BaseModel):
    """Ligne de stock enrichie : statut et valeur sont derives, pas stockes."""
    id: int
    code_article: str
    designation: str
    categorie: Optional[str] = None
    unite_mesure: Optional[str] = None
    quantite_disponible: float = 0
    quantite_reservee: float = 0
    quantite_minimum: Optional[float] = None
    quantite_maximum: Optional[float] = None
    prix_unitaire: Optional[float] = None
    valeur: float = 0
    emplacement: Optional[str] = None
    entrepot_id: Optional[int] = None
    entrepot_code: Optional[str] = None
    entrepot_nom: Optional[str] = None
    statut: str = "normal"
    couverture_jours: Optional[float] = None
    date_derniere_entree: Optional[datetime] = None
    date_derniere_sortie: Optional[datetime] = None


class StockSearchResponse(BaseModel):
    items: List[StockLine] = []
    total: int = 0
    valeur_totale: float = 0
    pending: bool = False


class StockStatusBucket(BaseModel):
    statut: str
    libelle: str
    nb_articles: int = 0
    valeur: float = 0


class StockStatusesResponse(BaseModel):
    statuses: List[StockStatusBucket] = []
    total_articles: int = 0
    pending: bool = False


# ─── HISTORIQUE / MOUVEMENTS ─────────────────────────────────────────────────
class MovementLine(BaseModel):
    id: int
    reference: str
    type_mouvement: str
    quantite: float
    quantite_avant: Optional[float] = None
    quantite_apres: Optional[float] = None
    valeur_totale: Optional[float] = None
    raison: Optional[str] = None
    document_reference: Optional[str] = None
    destination: Optional[str] = None
    operateur_id: Optional[int] = None
    date_mouvement: Optional[datetime] = None
    code_article: Optional[str] = None
    designation: Optional[str] = None


class MovementListResponse(BaseModel):
    items: List[MovementLine] = []
    total: int = 0
    entrees: float = 0
    sorties: float = 0
    pending: bool = False


# ─── IMPORT / EXPORT CSV ─────────────────────────────────────────────────────
class ImportRowError(BaseModel):
    ligne: int
    message: str


class ImportResult(BaseModel):
    resource: str
    lu: int = 0
    cree: int = 0
    mis_a_jour: int = 0
    ignore: int = 0
    erreurs: List[ImportRowError] = []
    dry_run: bool = False
    pending: bool = False


# ─── ANALYTICS ───────────────────────────────────────────────────────────────
class AnalyticsRequest(BaseModel):
    """Parametres communs aux calculs analytics (tous facultatifs)."""
    article_code: Optional[str] = None
    categorie: Optional[str] = None
    entrepot_id: Optional[int] = None
    jours: int = Field(default=90, ge=1, le=1095)
    horizon: int = Field(default=3, ge=1, le=24)
    niveau_service: float = Field(default=0.95, gt=0, lt=1)
    delai_approvisionnement_jours: float = Field(default=7.0, gt=0, le=365)
    seuil_sigma: float = Field(default=3.0, gt=0, le=10)
    limit: int = Field(default=100, ge=1, le=500)

    model_config = {"extra": "allow"}


class TurnoverLine(BaseModel):
    code_article: str
    designation: str
    categorie: Optional[str] = None
    quantite_sortie: float = 0
    stock_actuel: float = 0
    stock_moyen: float = 0
    taux_rotation: Optional[float] = None
    rotation_annualisee: Optional[float] = None
    jours_couverture: Optional[float] = None
    valeur_sortie: float = 0


class SafetyStockLine(BaseModel):
    code_article: str
    designation: str
    conso_moyenne_jour: float = 0
    ecart_type_jour: float = 0
    stock_securs: float = 0
    seuil_reappro: float = 0
    stock_actuel: float = 0
    statut: str = "normal"


class ForecastPoint(BaseModel):
    periode: str
    quantite_prevue: float


class ForecastLine(BaseModel):
    code_article: str
    designation: str
    historique: dict = {}
    projections: List[ForecastPoint] = []
    pente_mensuelle: float = 0
    confiance: str = "faible"


class AnomalyItem(BaseModel):
    niveau: str  # critique / avertissement / information
    type_anomalie: str
    code_article: Optional[str] = None
    designation: Optional[str] = None
    reference: Optional[str] = None
    description: str
    valeur_constate: Optional[float] = None


class AnomalyResponse(BaseModel):
    items: List[AnomalyItem] = []
    total: int = 0
    analysed_movements: int = 0
    periode_jours: int = 0
    pending: bool = False


# ─── RAPPORTS ────────────────────────────────────────────────────────────────
class ReportRequest(BaseModel):
    categorie: Optional[str] = None
    entrepot_id: Optional[int] = None
    client_id: Optional[int] = None
    jours: int = Field(default=90, ge=1, le=1095)
    group_by: str = Field(default="categorie")
    date_debut: Optional[datetime] = None
    date_fin: Optional[datetime] = None

    model_config = {"extra": "allow"}


class ReportResponse(BaseModel):
    rapport: str
    genere_le: datetime
    periode_jours: int
    colonnes: List[str] = []
    lignes: List[dict] = []
    totaux: dict = {}
    total_lignes: int = 0
    pending: bool = False


class ExportRequest(ReportRequest):
    rapport: str = "stock-valuation"
    format: str = "csv"


class ImportOptions(BaseModel):
    dry_run: bool = False
    create_missing: bool = True
