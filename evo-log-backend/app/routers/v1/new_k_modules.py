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
    categorie_tarifaire_tec: Optional[int] = 2  # 0:5% 1:10% 2:20% 3:30%


@router.post("/transit/calculateur-taxe-cemac")
def calculer_taxes_douanieres(payload: RequeteCalculDouane):
    """Calcul deterministe des droits/taxes CEMAC a partir de la valeur CAF.

    Simulation tarifaire (ne persiste rien) : a confirmer avec les taux SYDONIA
    en vigueur avant usage officiel.
    """
    valeur_caf = payload.valeur_caf_xaf
    taux_dd = (
        0.0
        if payload.origine_produit in ["CEMAC", "ZLECAF"]
        else [0.05, 0.10, 0.20, 0.30][min(payload.categorie_tarifaire_tec, 3)]
    )
    droit_douane = valeur_caf * taux_dd
    taxe_communautaire_cci = valeur_caf * 0.004  # 0.4% CCI CEMAC
    prelevement_ohada = valeur_caf * 0.0005       # 0.05% OHADA
    redevance_informatique = 15000.0              # Redevance fixe SYDONIA / CAMCIS
    assiette_tva = valeur_caf + droit_douane
    tva = assiette_tva * 0.1925                    # 19.25% TVA Cameroun
    total = (
        droit_douane + taxe_communautaire_cci + prelevement_ohada
        + redevance_informatique + tva
    )
    return {
        "valeur_caf_xaf": valeur_caf,
        "droit_douane_xaf": droit_douane,
        "cci_cemac_xaf": taxe_communautaire_cci,
        "ohada_xaf": prelevement_ohada,
        "redevance_sydonia_xaf": redevance_informatique,
        "tva_19_25_xaf": tva,
        "total_liquidation_douane_xaf": total,
        "exemption_zlecaf_appliquee": payload.origine_produit in ["CEMAC", "ZLECAF"],
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
