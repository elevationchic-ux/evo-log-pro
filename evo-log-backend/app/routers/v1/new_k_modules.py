from fastapi import APIRouter, Depends, HTTPException, Query
from typing import List, Optional
from datetime import datetime
from pydantic import BaseModel
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.core.security import get_current_user
from app.models.user import User
from app.models.new_k_modules import FuelTankSensor

router = APIRouter(prefix="/api/v1", tags=["New K-Modules"])

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
    derniere_station: Optional[str] = None

class PurchaseOrderCreate(BaseModel):
    fournisseur: str
    description: str
    montant_total_xaf: float

class ComplianceAuditCreate(BaseModel):
    dossier_reference: str
    type_reglementation: Optional[str] = "ZLECAF / CEMAC"
    score_conformite_pct: Optional[float] = 98.5

# --- In-Memory State for Demo/Live Integration ---
_cotations = [
    {
        "id": 1,
        "reference": "COT-2026-001",
        "client_nom": "CFAO LOGISTICS CAMEROUN",
        "origine": "Port de Douala",
        "destination": "N'Djamena (Tchad)",
        "nature_fret": "Conteneur 40ft High Cube",
        "montant_estime_xaf": 4850000.0,
        "marge_nette_pct": 18.5,
        "statut": "ACCEPTE",
        "created_at": datetime.utcnow().isoformat()
    }
]

_epods = [
    {
        "id": 1,
        "reference_mission": "OT-2026-00401",
        "nom_destinataire": "Jean-Marc MVONDO",
        "signature_url": "/signatures/sig_00401.png",
        "photo_livraison_url": "/photos/delivery_00401.jpg",
        "longitude": 9.7042,
        "latitude": 4.0511,
        "statut": "LIVRE_AVEC_SIGNATURE",
        "timestamp": datetime.utcnow().isoformat()
    }
]

_procurements = [
    {
        "id": 1,
        "numero_po": "PO-2026-089",
        "fournisseur": "MICHELIN CAMEROUN",
        "description": "8 Pneumatiques Poids Lourds 315/80 R22.5",
        "montant_total_xaf": 2400000.0,
        "match_3_voies": True,
        "statut": "APPROUVE",
        "created_at": datetime.utcnow().isoformat()
    }
]

_compliance_audits = [
    {
        "id": 1,
        "dossier_reference": "DOS-DOUANE-9021",
        "type_reglementation": "ZLECAF / CEMAC",
        "score_conformite_pct": 99.2,
        "exemption_valide": True,
        "statut": "VALIDE",
        "created_at": datetime.utcnow().isoformat()
    }
]

# --- Endpoints K-Cotations ---
@router.get("/cotations")
def get_cotations():
    return {"items": _cotations}

@router.post("/cotations")
def create_cotation(payload: CotationCreate):
    new_item = {
        "id": len(_cotations) + 1,
        "reference": f"COT-2026-00{len(_cotations) + 1}",
        **payload.dict(),
        "statut": "SOUMIS",
        "created_at": datetime.utcnow().isoformat()
    }
    _cotations.append(new_item)
    return new_item

_invoices = [
    {
        "id": 1,
        "numero_facture": "FAC-2026-00401",
        "client": "CFAO LOGISTICS CAMEROUN",
        "montant_ht_xaf": 4850000.0,
        "tva_xaf": 933625.0,
        "montant_ttc_xaf": 5783625.0,
        "statut": "EMISE_AUTOMATIQUE_APRES_EPOD",
        "date_emission": datetime.utcnow().isoformat()
    }
]

# --- Endpoints K-Tracking & e-POD ---
@router.get("/tracking/epod")
def get_epods():
    return {"items": _epods, "factures_generees": _invoices}

@router.post("/tracking/epod")
def create_epod(payload: EPodCreate):
    new_item = {
        "id": len(_epods) + 1,
        **payload.dict(),
        "statut": "LIVRE_AVEC_SIGNATURE",
        "timestamp": datetime.utcnow().isoformat()
    }
    _epods.append(new_item)
    
    # Automatisme Inter-Module : Génération automatique de la facture dans K-Finance
    new_invoice = {
        "id": len(_invoices) + 1,
        "numero_facture": f"FAC-2026-00{len(_invoices) + 401}",
        "client": "DESTINATAIRE_" + payload.nom_destinataire.upper(),
        "montant_ht_xaf": 1250000.0,
        "tva_xaf": 240625.0,
        "montant_ttc_xaf": 1490625.0,
        "statut": "EMISE_AUTOMATIQUE_APRES_EPOD",
        "reference_epod": f"EPOD-00{new_item['id']}",
        "date_emission": datetime.utcnow().isoformat()
    }
    _invoices.append(new_invoice)
    
    return {"epod": new_item, "facture_generee": new_invoice}

# --- Endpoints K-FuelGuard ---
@router.get("/fuel-guard/sensors")
def get_fuel_sensors(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    query = db.query(FuelTankSensor)
    if not current_user.is_superuser:
        query = query.filter(FuelTankSensor.company_id == current_user.company_id)
    sensors = query.order_by(FuelTankSensor.updated_at.desc()).all()
    return {"items": sensors, "incidents_securite": []}

@router.post("/fuel-guard/sensors")
def create_fuel_sensor(
    payload: FuelSensorCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    alerte = payload.niveau_actuel_litres < 50.0
    sensor = FuelTankSensor(
        company_id=current_user.company_id,
        immatriculation_camion=payload.immatriculation_camion,
        niveau_actuel_litres=payload.niveau_actuel_litres,
        capacite_totale_litres=400.0,
        alerte_vol_detectee=alerte,
        derniere_station=payload.derniere_station,
    )
    db.add(sensor)
    db.commit()
    db.refresh(sensor)
    return sensor

# --- Calculateur Tarifaire Douane Natif CEMAC / ZLECAF ---
class RequeteCalculDouane(BaseModel):
    valeur_caf_xaf: float
    origine_produit: Optional[str] = "CEMAC" # CEMAC, ZLECAF, HORS_ZONE
    categorie_tarifaire_tec: Optional[int] = 2 # 0: Essentiel (5%), 1: Matériel (10%), 2: Intermédiaire (20%), 3: Consommation (30%)

@router.post("/transit/calculateur-taxe-cemac")
def calculer_taxes_douanieres(payload: RequeteCalculDouane):
    valeur_caf = payload.valeur_caf_xaf
    
    # Exemption ZLECAF / CEMAC
    taux_dd = 0.0 if payload.origine_produit in ["CEMAC", "ZLECAF"] else [0.05, 0.10, 0.20, 0.30][min(payload.categorie_tarifaire_tec, 3)]
    
    droit_douane = valeur_caf * taux_dd
    taxe_communautaire_cci = valeur_caf * 0.004 # 0.4% CCI CEMAC
    prélèvement_ohada = valeur_caf * 0.0005 # 0.05% OHADA
    redevance_informatique = 15000.0 # Redevance fixe SYDONIA / CAMCIS
    
    assiette_tva = valeur_caf + droit_douane
    tva = assiette_tva * 0.1925 # 19.25% TVA Cameroun
    
    total_liquidation_xaf = droit_douane + taxe_communautaire_cci + prélèvement_ohada + redevance_informatique + tva
    
    return {
        "valeur_caf_xaf": valeur_caf,
        "droit_douane_xaf": droit_douane,
        "cci_cemac_xaf": taxe_communautaire_cci,
        "ohada_xaf": prélèvement_ohada,
        "redevance_sydonia_xaf": redevance_informatique,
        "tva_19_25_xaf": tva,
        "total_liquidation_douane_xaf": total_liquidation_xaf,
        "exemption_zlecaf_appliquee": payload.origine_produit in ["CEMAC", "ZLECAF"]
    }

# --- Endpoints K-Procurement ---
@router.get("/procurement/orders")
def get_procurement_orders():
    return {"items": _procurements}

@router.post("/procurement/orders")
def create_procurement_order(payload: PurchaseOrderCreate):
    new_item = {
        "id": len(_procurements) + 1,
        "numero_po": f"PO-2026-0{len(_procurements) + 90}",
        **payload.dict(),
        "match_3_voies": True,
        "statut": "APPROUVE",
        "created_at": datetime.utcnow().isoformat()
    }
    _procurements.append(new_item)
    return new_item

# --- Endpoints K-Compliance ---
@router.get("/compliance/audits")
def get_compliance_audits():
    return {"items": _compliance_audits}

@router.post("/compliance/audits")
def create_compliance_audit(payload: ComplianceAuditCreate):
    new_item = {
        "id": len(_compliance_audits) + 1,
        **payload.dict(),
        "exemption_valide": True,
        "statut": "VALIDE",
        "created_at": datetime.utcnow().isoformat()
    }
    _compliance_audits.append(new_item)
    return new_item

# --- Endpoints K-Analytics BI ---
@router.get("/bi-analytics/executive-summary")
def get_bi_summary():
    return {
        "chiffre_affaires_cumule_xaf": 142500000.0,
        "marge_brute_globale_pct": 22.4,
        "volume_fret_evp": 1280,
        "taux_livraison_ponctuel_pct": 97.8,
        "economie_carburant_xaf": 8400000.0
    }

# --- Endpoints Acconage & Handling Portuaire ---
@router.get("/acconage")
@router.get("/acconage/operations")
def get_acconage_operations():
    return {
        "items": [
            {"id": 1, "navire": "MV MAERSK CAMEROUN", "escale": "ESC-2026-089", "conteneurs_teu": 420, "quai": "Quai 23 - Port de Douala", "statut": "EN_DECHARGEMENT", "created_at": datetime.utcnow().isoformat()},
            {"id": 2, "navire": "MV CMA CGM KRIBI", "escale": "ESC-2026-092", "conteneurs_teu": 680, "quai": "Quai 04 - Kribi Deep Seaport", "statut": "TERMINÉ", "created_at": datetime.utcnow().isoformat()}
        ],
        "total": 2
    }

# --- Endpoints Transit & Douane ---
@router.get("/transit")
@router.get("/transit/dossiers")
def get_transit_dossiers():
    return {
        "items": [
            {"id": 1, "reference_dossier": "TR-2026-0012", "client": "CFAO CAMEROUN", "bureau_douane": "Douala Port V (10P)", "bva_numero": "BVA-88129", "statut": "DEDOUANE", "created_at": datetime.utcnow().isoformat()},
            {"id": 2, "reference_dossier": "TR-2026-0015", "client": "SABC BRASSERIES", "bureau_douane": "Kribi Conteneurs (K12)", "bva_numero": "BVA-99012", "statut": "EN_COURS_INSPECTION", "created_at": datetime.utcnow().isoformat()}
        ],
        "total": 2
    }

# --- Endpoints Removal Slips (Bons d'Enlèvement) ---
@router.get("/magasin/removal-slips")
def get_removal_slips():
    return {
        "items": [
            {"id": 1, "numero_be": "BE-2026-044", "client": "TOTALENERGIES MARKETING", "entrepot": "Magasin Central Zone Industrielle Bassa", "statut": "VALIDE", "created_at": datetime.utcnow().isoformat()}
        ],
        "total": 1
    }

# --- Endpoints Master Data Articles ---
@router.get("/master-data/articles")
def get_master_data_articles():
    return {
        "items": [
            {"id": 1, "code_sku": "ART-001", "designation": "Ciment Portland ZLECAF 42.5", "categorie": "MATERIAUX", "prix_unitaire_xaf": 4800, "stock_disponible": 12500},
            {"id": 2, "code_sku": "ART-002", "designation": "Huile Moteur Synthétique 15W40 20L", "categorie": "PIECES_RECHANGE", "prix_unitaire_xaf": 45000, "stock_disponible": 320}
        ],
        "total": 2
    }

# --- Endpoints Ordres de Transfert ---
@router.get("/magasin/ordres-transfert")
def get_ordres_transfert():
    return {
        "items": [
            {"id": 1, "reference": "OTR-2026-001", "source": "Magasin Douala Port", "destination": "Magasin Yaoundé Depot", "statut": "EN_TRANSIT", "created_at": datetime.utcnow().isoformat()}
        ],
        "total": 1
    }

# --- Endpoints Bandes de Livraison ---
@router.get("/magasin/bandes-livraison")
def get_bandes_livraison():
    return {
        "items": [
            {"id": 1, "reference": "BL-2026-0891", "transporteur": "EVO-LOG FREIGHT", "statut": "CONFIRME", "created_at": datetime.utcnow().isoformat()}
        ],
        "total": 1
    }
