from fastapi import APIRouter, Depends
from datetime import datetime
from pydantic import BaseModel
from typing import Optional

from app.core.not_implemented import not_implemented

router = APIRouter(tags=["New K-Modules"])  # monte sur /api/v1/k-modules par main.py

# Ce module etait une DEMO en memoire volatile : listes pre-remplies de donnees
# inventees (cotations, ePOD, senseurs carburant, acconage, transit, maitrise
# d'articles, bons...) et "persistances" qui disparaissaient au redemarrage.
# Toutes ces routes retournent desormais un 501 explicite au lieu d'un faux
# succes. Les vraies fonctionnalites correspondent vivent dans les routers
# metiers (acconage, transit, magasin, finance) alimentes par la base.
# Seule exception conservee : le calculateur tarifaire douanier CEMAC, qui est
# un calcul deterministe a partir de l'entree (aucune donnee inventee).


# --- Schemas ---
class CotationCreate(BaseModel):
    client_nom: str
    origine: str
    destination: str
    nature_fret: str
    montant_estime_xaf: float
    marge_nette_pct: Optional[float] = 15.0


class EPodCreate(BaseModel):
    reference_mission: str
    nom_destinataire: str
    signature_url: Optional[str] = None
    photo_livraison_url: Optional[str] = None
    longitude: Optional[float] = 9.704
    latitude: Optional[float] = 4.051


class FuelSensorCreate(BaseModel):
    immatriculation_camion: str
    niveau_actuel_litres: float
    derniere_station: Optional[str] = "TotalEnergies Douala Port"


class PurchaseOrderCreate(BaseModel):
    fournisseur: str
    description: str
    montant_total_xaf: float


class ComplianceAuditCreate(BaseModel):
    dossier_reference: str
    type_reglementation: Optional[str] = "ZLECAF / CEMAC"
    score_conformite_pct: Optional[float] = 98.5


# --- Endpoints K-Cotations (demo -> 501) ---
@router.get("/cotations")
def get_cotations():
    """K-Cotations (demo) : 501. Voir le vrai routeur cotations base en base."""
    not_implemented(
        "Cotations (module demo en memoire)",
        "le routeur cotations reel alimente par la table cotations_devis "
        "(les donnees de cette demo etaient inventees)",
    )


@router.post("/cotations")
def create_cotation(payload: CotationCreate):
    """Creation cotation (demo) : 501 (memoire volatile, faux succes)."""
    not_implemented(
        "Creation de cotation (module demo en memoire)",
        "une ecriture reelle en base via le routeur cotations metier",
    )


# --- Endpoints K-Tracking & e-POD (demo -> 501) ---
@router.get("/tracking/epod")
def get_epods():
    """e-POD (demo) : 501. Voir preuves_livraison reels en base."""
    not_implemented(
        "e-POD (module demo en memoire)",
        "la table preuves_livraison portee par le tenant (donnees inventees ici)",
    )


@router.post("/tracking/epod")
def create_epod(payload: EPodCreate):
    """Creation e-POD (demo) : 501 (generait une facture inventee, rien en base)."""
    not_implemented(
        "Creation d'e-POD + facture automatique (module demo)",
        "l'ecriture reelle de la preuve de livraison et l'emission facturation "
        "depuis les modeles persistants (montants codes en dur ici)",
    )


# --- Endpoints K-FuelGuard (demo -> 501) ---
@router.get("/fuel-guard/sensors")
def get_fuel_sensors():
    """Capteurs carburant (demo) : 501 (telemetrie inventee)."""
    not_implemented(
        "Capteurs carburant / FuelGuard (module demo)",
        "un flux telematique reel par vehicule (donnees inventees ici)",
    )


@router.post("/fuel-guard/sensors")
def create_fuel_sensor(payload: FuelSensorCreate):
    """Lecture capteur carburant (demo) : 501 (memoire volatile)."""
    not_implemented(
        "Enregistrement de niveau carburant (module demo)",
        "une ingestion telematique persistante (la detection de vol etait simulee)",
    )


# --- Calculateur Tarifaire Douane Natif CEMAC / ZLECAF (CALCUL LEGITIME - conserve) ---
class RequeteCalculDouane(BaseModel):
    valeur_caf_xaf: float
    origine_produit: Optional[str] = "CEMAC"  # CEMAC, ZLECAF, HORS_ZONE
    categorie_tarifaire_tec: Optional[int] = 2  # 0:0% 1:5% 2:10% 3:20% (TEC CEMAC)


@router.post("/transit/calculateur-taxe-cemac")
def calculer_taxes_douanieres(payload: RequeteCalculDouane):
    """Calcul deterministe des droits/taxes CEMAC a partir de la valeur CAF.

    Délégué au moteur UNIQUE ``app.services.taxation_douaniere`` (partagé avec
    transit, transit-avance et integration-cameroun). Simulation tarifaire (ne
    persiste rien) : a confirmer avec les taux SYDONIA en vigueur avant usage
    officiel.
    """
    from app.services.taxation_douaniere import calculer_liquidation

    liq = calculer_liquidation(
        valeur_en_douane=payload.valeur_caf_xaf,
        categorie_tec=payload.categorie_tarifaire_tec,
        origine=payload.origine_produit,
    )
    return {
        "valeur_caf_xaf": liq["valeur_en_douane_xaf"],
        "categorie_tarifaire_tec": payload.categorie_tarifaire_tec,
        "origine_produit": payload.origine_produit,
        "droit_douane_xaf": liq["droit_douane_dd"],
        "redevance_informatique_xaf": liq["redevance_informatique"],
        "cci_cemac_xaf": liq["cci_cemac"],
        "ohada_xaf": liq["prelevement_ohada"],
        "base_tva_xaf": liq["base_tva"],
        "tva_19_25_xaf": liq["tva_1925"],
        "precompte_is_xaf": liq["precompte_is"],
        "total_liquidation_douane_xaf": liq["total_a_liquider_xaf"],
        "exemption_zlecaf_appliquee": (payload.origine_produit or "").upper()
        in ("CEMAC", "ZLECAF", "UEAC"),
        "source_taux": liq["source_taux"],
        "simulation": liq["simulation"],
        "note": liq["note"],
    }


# --- Endpoints K-Procurement (demo -> 501) ---
@router.get("/procurement/orders")
def get_procurement_orders():
    """Bons de commande (demo) : 501 (donnees inventees)."""
    not_implemented(
        "Bons de commande (module demo)",
        "le routeur procurement/achats reel base en base",
    )


@router.post("/procurement/orders")
def create_procurement_order(payload: PurchaseOrderCreate):
    """Creation BC (demo) : 501 (memoire volatile, match 3 voies simule)."""
    not_implemented(
        "Creation de bon de commande (module demo)",
        "une ecriture reelle + un rapprochement 3 voies veritable",
    )


# --- Endpoints K-Compliance (demo -> 501) ---
@router.get("/compliance/audits")
def get_compliance_audits():
    """Audits conformite (demo) : 501 (scores inventes)."""
    not_implemented(
        "Audits de conformite ZLECAF/CEMAC (module demo)",
        "des controles reels base sur les dossiers en base",
    )


@router.post("/compliance/audits")
def create_compliance_audit(payload: ComplianceAuditCreate):
    """Creation audit (demo) : 501 (memoire volatile)."""
    not_implemented(
        "Enregistrement d'un audit de conformite (module demo)",
        "une ecriture reelle en base",
    )


# --- Endpoints K-Analytics BI (demo -> 501) ---
@router.get("/bi-analytics/executive-summary")
def get_bi_summary():
    """Resume BI (demo) : 501 (KPI codes en dur, non agreges depuis la DB)."""
    not_implemented(
        "Resume analytique executif (module demo)",
        "des aggregations SQL reelles (CA, marge, volume EVP, ponctualite)",
    )


# --- Endpoints Acconage & Handling Portuaire (demo -> 501) ---
@router.get("/acconage")
@router.get("/acconage/operations")
def get_acconage_operations():
    """Operations d'acconage (demo) : 501. Voir le vrai routeur acconage en base."""
    not_implemented(
        "Operations d'acconage/escales (module demo)",
        "le routeur acconage reel base sur les tables navires/escales "
        "(les 2 operations retournees etaient inventees)",
    )


# --- Endpoints Transit & Douane (demo -> 501) ---
@router.get("/transit")
@router.get("/transit/dossiers")
def get_transit_dossiers():
    """Dossiers transit (demo) : 501. Voir le vrai routeur transit en base."""
    not_implemented(
        "Dossiers de transit/acconage (module demo)",
        "le routeur transit reel base sur dossiers_transit "
        "(les 2 dossiers retournes etaient inventes)",
    )


# --- Endpoints Removal Slips (Bons d'Enlevement) (demo -> 501) ---
@router.get("/magasin/removal-slips")
def get_removal_slips():
    """Bons d'enlevement (demo) : 501 (donnees inventees)."""
    not_implemented(
        "Bons d'enlevement (module demo)",
        "le module magasin reel base en base",
    )


# --- Endpoints Master Data Articles (demo -> 501) ---
@router.get("/master-data/articles")
def get_master_data_articles():
    """Articles (demo) : 501. Voir le vrai stock/articles en base."""
    not_implemented(
        "Maitre d'articles (module demo)",
        "la table articles/stocks reelle portee par le tenant",
    )


# --- Endpoints Ordres de Transfert (demo -> 501) ---
@router.get("/magasin/ordres-transfert")
def get_ordres_transfert():
    """Ordres de transfert (demo) : 501 (donnees inventees)."""
    not_implemented(
        "Ordres de transfert inter-magasins (module demo)",
        "la table transferts_stock reelle portee par le tenant",
    )


# --- Endpoints Bandes de Livraison (demo -> 501) ---
@router.get("/magasin/bandes-livraison")
def get_bandes_livraison():
    """Bandes de livraison (demo) : 501 (donnees inventees)."""
    not_implemented(
        "Bandes de livraison (module demo)",
        "les documents de livraison reels base en base",
    )
