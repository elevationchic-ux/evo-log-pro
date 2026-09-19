from fastapi import APIRouter, Depends, HTTPException, Query
from typing import List, Optional
from datetime import datetime
from pydantic import BaseModel
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.core.security import get_current_user
from app.models.user import User
from app.models.new_k_modules import CotationDevis, ElectronicPOD, FuelTankSensor, PurchaseOrder, ComplianceAudit

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
    longitude: Optional[float] = None
    latitude: Optional[float] = None

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
    type_reglementation: Optional[str] = None
    score_conformite_pct: Optional[float] = None

# --- Endpoints K-Cotations ---
@router.get("/cotations")
def get_cotations(db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    query = db.query(CotationDevis)
    if not current_user.is_superuser:
        query = query.filter(CotationDevis.company_id == current_user.company_id)
    return {"items": query.order_by(CotationDevis.created_at.desc()).all()}

@router.post("/cotations")
def create_cotation(payload: CotationCreate, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    cotation = CotationDevis(company_id=current_user.company_id, reference=f"COT-{datetime.utcnow():%Y%m%d%H%M%S}", **payload.dict(), statut="SOUMIS")
    db.add(cotation)
    db.commit()
    db.refresh(cotation)
    return cotation

# --- Endpoints K-Tracking & e-POD ---
@router.get("/tracking/epod")
def get_epods(db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    query = db.query(ElectronicPOD)
    if not current_user.is_superuser:
        query = query.filter(ElectronicPOD.company_id == current_user.company_id)
    return {"items": query.order_by(ElectronicPOD.timestamp.desc()).all(), "factures_generees": []}

@router.post("/tracking/epod")
def create_epod(payload: EPodCreate, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    epod = ElectronicPOD(company_id=current_user.company_id, **payload.dict(), statut="LIVRE_AVEC_SIGNATURE")
    db.add(epod)
    db.commit()
    db.refresh(epod)
    return {"epod": epod, "facture_generee": None}

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
def get_procurement_orders(db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    query = db.query(PurchaseOrder)
    if not current_user.is_superuser:
        query = query.filter(PurchaseOrder.company_id == current_user.company_id)
    return {"items": query.order_by(PurchaseOrder.created_at.desc()).all()}

@router.post("/procurement/orders")
def create_procurement_order(payload: PurchaseOrderCreate, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    order = PurchaseOrder(
        company_id=current_user.company_id,
        numero_po=f"PO-{datetime.utcnow():%Y%m%d%H%M%S}",
        **payload.dict(),
        match_3_voies=False,
        statut="EN_ATTENTE",
    )
    db.add(order)
    db.commit()
    db.refresh(order)
    return order

# --- Endpoints K-Compliance ---
@router.get("/compliance/audits")
def get_compliance_audits(db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    query = db.query(ComplianceAudit)
    if not current_user.is_superuser:
        query = query.filter(ComplianceAudit.company_id == current_user.company_id)
    return {"items": query.order_by(ComplianceAudit.created_at.desc()).all()}

@router.post("/compliance/audits")
def create_compliance_audit(payload: ComplianceAuditCreate, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    audit = ComplianceAudit(
        company_id=current_user.company_id,
        dossier_reference=payload.dossier_reference,
        type_reglementation=payload.type_reglementation,
        score_conformite_pct=payload.score_conformite_pct,
        exemption_valide=False,
        statut="A_ANALYSER",
    )
    db.add(audit)
    db.commit()
    db.refresh(audit)
    return audit

# --- Endpoints K-Analytics BI ---
@router.get("/bi-analytics/executive-summary")
def get_bi_summary(current_user: User = Depends(get_current_user)):
    return {
        "chiffre_affaires_cumule_xaf": None,
        "marge_brute_globale_pct": None,
        "volume_fret_evp": None,
        "taux_livraison_ponctuel_pct": None,
        "economie_carburant_xaf": None,
    }

# --- Endpoints Acconage & Handling Portuaire ---
@router.get("/acconage")
@router.get("/acconage/operations")
def get_acconage_operations(current_user: User = Depends(get_current_user)):
    return {"items": [], "total": 0}

# --- Endpoints Transit & Douane ---
@router.get("/transit")
@router.get("/transit/dossiers")
def get_transit_dossiers(current_user: User = Depends(get_current_user)):
    return {"items": [], "total": 0}

# --- Endpoints Removal Slips (Bons d'Enlèvement) ---
@router.get("/magasin/removal-slips")
def get_removal_slips(current_user: User = Depends(get_current_user)):
    return {"items": [], "total": 0}

# --- Endpoints Master Data Articles ---
@router.get("/master-data/articles")
def get_master_data_articles(current_user: User = Depends(get_current_user)):
    return {"items": [], "total": 0}

# --- Endpoints Ordres de Transfert ---
@router.get("/magasin/ordres-transfert")
def get_ordres_transfert(current_user: User = Depends(get_current_user)):
    return {"items": [], "total": 0}

# --- Endpoints Bandes de Livraison ---
@router.get("/magasin/bandes-livraison")
def get_bandes_livraison(current_user: User = Depends(get_current_user)):
    return {"items": [], "total": 0}
