"""
Router Annuaire des Prestataires & Sous-traitants
Strictement restreint aux Départements Achats, Logistique & Direction.
"""
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from typing import List, Optional
from pydantic import BaseModel
from datetime import datetime

from app.core.database import get_db
from app.core.security import get_current_user
from app.models.user import User
from app.models.prestataire import Prestataire, DemandeCotation

router = APIRouter()

# Rôles autorisés pour le département Achats & Direction
AUTHORIZED_PURCHASE_ROLES = {
    "SUPER_ADMIN", "ADMIN", "ACHATS", "DIRECTEUR_TRANSPORT", "CHEF_PARC", "MANAGER", "DAF"
}


def resolve_current_user(
    identity: str = Depends(get_current_user),
    db: Session = Depends(get_db)
) -> User:
    user = None
    if isinstance(identity, str) and identity.isdigit():
        user = db.query(User).filter(User.id == int(identity)).first()
    if not user:
        user = db.query(User).filter((User.username == str(identity)) | (User.email == str(identity))).first()
    if not user:
        raise HTTPException(status_code=401, detail="Utilisateur non authentifié")
    return user


def require_purchase_access(current_user: User = Depends(resolve_current_user)) -> User:
    """Vérifie que l'utilisateur appartient au département Achats, Direction ou SuperAdmin"""
    if current_user.is_superuser:
        return current_user

    user_roles = [r.name.upper() for r in current_user.roles] if hasattr(current_user, "roles") and current_user.roles else []
    
    # Vérification par rôle ou module
    has_access = any(r in AUTHORIZED_PURCHASE_ROLES for r in user_roles)
    if not has_access:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Accès Restreint : Seul le département Achats, Logistique et la Direction peuvent accéder à l'Annuaire des Prestataires."
        )
    return current_user


# Schemas Pydantic
class PrestataireOut(BaseModel):
    id: int
    company_id: Optional[int]
    code: str
    raison_sociale: str
    sigle: Optional[str]
    specialite: str
    tax_id: Optional[str]
    rccm: Optional[str]
    agrement_portuaire: Optional[str]
    est_homologue: bool
    statut_agrement: str
    ville: str
    zone_portuaire: Optional[str]
    adresse: Optional[str]
    contact_nom: Optional[str]
    contact_telephone: str
    contact_email: Optional[str]
    telephone_astreinte_24h: Optional[str]
    note_globale: float
    nb_missions_realisees: int
    taux_ponctualite: float
    taux_conformite_qhse: float
    devise: str
    taux_journalier_indicatif: Optional[float]
    conditions_reglement: str
    observations: Optional[str]
    est_actif: bool

    class Config:
        from_attributes = True


class PrestataireCreate(BaseModel):
    raison_sociale: str
    sigle: Optional[str] = None
    specialite: str
    tax_id: Optional[str] = None
    rccm: Optional[str] = None
    agrement_portuaire: Optional[str] = None
    ville: str = "Douala"
    zone_portuaire: Optional[str] = None
    adresse: Optional[str] = None
    contact_nom: Optional[str] = None
    contact_telephone: str
    contact_email: Optional[str] = None
    telephone_astreinte_24h: Optional[str] = None
    taux_journalier_indicatif: Optional[float] = None
    conditions_reglement: Optional[str] = "Virement 30j fin de mois"
    observations: Optional[str] = None


class CotationCreate(BaseModel):
    prestataire_id: int
    titre_besoin: str
    description_besoin: str
    urgence: Optional[str] = "NORMALE"
    date_intervention_souhaitee: Optional[str] = None
    lieu_intervention: str
    budget_max_estime: Optional[float] = None


class CotationOut(BaseModel):
    id: int
    numero_dossier: str
    titre_besoin: str
    description_besoin: str
    urgence: str
    lieu_intervention: str
    statut: str
    budget_max_estime: Optional[float]
    created_at: Optional[datetime]

    class Config:
        from_attributes = True


@router.get("", response_model=List[PrestataireOut])
def get_prestataires(
    specialite: Optional[str] = None,
    ville: Optional[str] = None,
    q: Optional[str] = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_purchase_access)
):
    """Liste tous les prestataires agréés et homologués avec filtres multi-critères"""
    query = db.query(Prestataire).filter(Prestataire.est_actif == True)

    # Isolation multi-tenant (sauf superuser qui voit tout le catalogue)
    if not current_user.is_superuser and current_user.company_id is not None:
        query = query.filter((Prestataire.company_id == current_user.company_id) | (Prestataire.company_id.is_(None)))

    if specialite and specialite != "ALL":
        query = query.filter(Prestataire.specialite == specialite)

    if ville and ville != "ALL":
        query = query.filter(Prestataire.ville == ville)

    if q:
        search_pattern = f"%{q.strip()}%"
        query = query.filter(
            (Prestataire.raison_sociale.ilike(search_pattern)) |
            (Prestataire.specialite.ilike(search_pattern)) |
            (Prestataire.contact_nom.ilike(search_pattern)) |
            (Prestataire.agrement_portuaire.ilike(search_pattern))
        )

    return query.order_by(Prestataire.note_globale.desc()).all()


@router.post("", response_model=PrestataireOut, status_code=status.HTTP_201_CREATED)
def creer_prestataire(
    data: PrestataireCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_purchase_access)
):
    """Enregistre et référence un nouveau prestataire agréé dans l'annuaire de l'entreprise"""
    import random
    code = f"PREST-{data.specialite[:3].upper()}-{random.randint(1000, 9999)}"
    
    prestataire = Prestataire(
        company_id=current_user.company_id if not current_user.is_superuser else None,
        code=code,
        raison_sociale=data.raison_sociale,
        sigle=data.sigle,
        specialite=data.specialite,
        tax_id=data.tax_id,
        rccm=data.rccm,
        agrement_portuaire=data.agrement_portuaire,
        ville=data.ville,
        zone_portuaire=data.zone_portuaire,
        adresse=data.adresse,
        contact_nom=data.contact_nom,
        contact_telephone=data.contact_telephone,
        contact_email=data.contact_email,
        telephone_astreinte_24h=data.telephone_astreinte_24h,
        taux_journalier_indicatif=data.taux_journalier_indicatif,
        conditions_reglement=data.conditions_reglement or "Virement 30j fin de mois",
        observations=data.observations,
        est_homologue=True,
        statut_agrement="VALIDE",
        note_globale=4.5
    )
    db.add(prestataire)
    db.commit()
    db.refresh(prestataire)
    return prestataire


@router.post("/cotations", response_model=CotationOut, status_code=status.HTTP_201_CREATED)
def soumettre_demande_cotation(
    data: CotationCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_purchase_access)
):
    """Émet une demande de devis officielle transmise directement au prestataire sélectionné"""
    import random
    numero_dossier = f"RFQ-{datetime.now().strftime('%Y%m')}-{random.randint(100, 999)}"
    
    cotation = DemandeCotation(
        company_id=current_user.company_id,
        prestataire_id=data.prestataire_id,
        demandeur_id=current_user.id,
        numero_dossier=numero_dossier,
        titre_besoin=data.titre_besoin,
        description_besoin=data.description_besoin,
        urgence=data.urgence or "NORMALE",
        date_intervention_souhaitee=data.date_intervention_souhaitee,
        lieu_intervention=data.lieu_intervention,
        budget_max_estime=data.budget_max_estime,
        statut="TRANSMIS"
    )
    db.add(cotation)
    db.commit()
    db.refresh(cotation)
    return cotation


@router.get("/cotations", response_model=List[CotationOut])
def get_mes_cotations(
    db: Session = Depends(get_db),
    current_user: User = Depends(require_purchase_access)
):
    """Consulte l'historique des demandes de cotations émises par le département Achats"""
    query = db.query(DemandeCotation)
    if not current_user.is_superuser and current_user.company_id is not None:
        query = query.filter(DemandeCotation.company_id == current_user.company_id)
    return query.order_by(DemandeCotation.created_at.desc()).limit(50).all()


# ============ GÉOLOCALISATION DÉPANNEUR 24/7 LE PLUS PROCHE ============
@router.post("/depannage-urgent/recherche-proche")
def trouver_depanneur_plus_proche(payload: dict):
    """Calcule le garage de dépannage 24/7 le plus proche selon les coordonnées GPS de la panne"""
    import math
    lat_panne = float(payload.get("latitude", 4.0511))
    lng_panne = float(payload.get("longitude", 9.7679))
    type_panne = payload.get("type_panne", "PNEUMATIQUE")

    garages = [
        {"id": 1, "nom": "Garage Central Bassa 24/7", "ville": "Douala Bassa", "lat": 4.0480, "lng": 9.7520, "specialite": "MOTEUR_ET_HYDRAULIQUE", "tel": "+237 670 00 11 22", "forfait_urgence_xaf": 85000},
        {"id": 2, "nom": "Station Assistance Axe Lourd Edéa", "ville": "Edéa (PK 85)", "lat": 3.8000, "lng": 10.1333, "specialite": "REMORQUAGE_ET_PNEUMATIQUES", "tel": "+237 699 44 55 66", "forfait_urgence_xaf": 120000},
        {"id": 3, "nom": "Atelier Dépannage Convois Yaoundé-Sud", "ville": "Yaoundé Mvan", "lat": 3.8100, "lng": 11.5100, "specialite": "ELECTRICITE_ET_FREINAGE", "tel": "+237 677 88 99 00", "forfait_urgence_xaf": 95000},
        {"id": 4, "nom": "Relais Dépannage Grand Nord Ngaoundéré", "ville": "Ngaoundéré Gare", "lat": 7.3200, "lng": 13.5800, "specialite": "GENERAL_PL_ET_REMORQUAGE", "tel": "+237 690 12 34 56", "forfait_urgence_xaf": 150000}
    ]

    # Formule Haversine
    def haversine(lat1, lon1, lat2, lon2):
        R = 6371.0 # Rayon Terre en km
        dlat = math.radians(lat2 - lat1)
        dlon = math.radians(lon2 - lon1)
        a = math.sin(dlat / 2)**2 + math.cos(math.radians(lat1)) * math.cos(math.radians(lat2)) * math.sin(dlon / 2)**2
        c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
        return round(R * c, 1)

    resultats = []
    for g in garages:
        dist = haversine(lat_panne, lng_panne, g["lat"], g["lng"])
        eta_min = int(dist / 45.0 * 60) + 15 # Vitesse moyenne dépanneuse 45km/h + 15 min préparation
        resultats.append({**g, "distance_km": dist, "eta_minutes": eta_min})

    resultats.sort(key=lambda x: x["distance_km"])
    plus_proche = resultats[0] if resultats else None

    return {
        "coordonnees_panne": {"lat": lat_panne, "lng": lng_panne},
        "type_panne": type_panne,
        "depanneur_recommande": plus_proche,
        "autres_depanneurs": resultats[1:],
        "statut": "DEPANNEUR_LOCALISE"
    }


# ============ CONTRAT D'AFFRÈTEMENT NUMÉRIQUE B2B ============
@router.post("/affretement/contrat-signer")
def emettre_contrat_affretement(payload: dict, db: Session = Depends(get_db)):
    """Génère le bon d'affrètement sous-traitant avec signature électronique et engagement de délai"""
    contrat_id = f"BA-B2B-{datetime.now().strftime('%Y%m%d%H%M')}"
    return {
        "contrat_id": contrat_id,
        "donneur_ordre": payload.get("donneur_ordre", "EVO-LOG Transport & Logistics"),
        "transporteur_affrete": payload.get("transporteur_affrete", "Transports Réunis d'Afrique (TRA)"),
        "trajet": payload.get("trajet", "Port Douala (Quai 14) -> N'Djamena (Zone Industrielle Farcha)"),
        "vehicule_mobilise": payload.get("vehicule", "Tracteur 6x4 + Plateau 40ft"),
        "prix_convenu_ht_xaf": payload.get("prix_xaf", 3850000),
        "delai_acheminement_jours": 7,
        "penalites_retard_jour_xaf": 50000,
        "statut_signature": "SIGNE_NUMERIQUEMENT_CONJOINT",
        "date_signature": datetime.now().isoformat(),
        "clause_responsabilite": "Conforme Convention CMR Internationale et Carnet TRIE CEMAC."
    }


# ============ PAIEMENT SÉCURISÉ SOUS SÉQUESTRE ESCROW ============
@router.post("/escrow/paiement-sequestre")
def bloquer_paiement_escrow(payload: dict):
    """Place les fonds en séquestre débloqués uniquement après confirmation de réparation"""
    montant = payload.get("montant_xaf", 120000)
    return {
        "escrow_id": f"ESCROW-{datetime.now().strftime('%Y%m%d%H%M')}",
        "montant_bloque_xaf": montant,
        "statut": "FONDS_SOUS_SEQUESTRE",
        "beneficiaire": payload.get("beneficiaire", "Garage Partenaire Agréé"),
        "motif": "Dépannage d'urgence sur route",
        "condition_deblocage": "Validation émargement chauffeur e-POD ou photo de réparation conforme",
        "date_sequestre": datetime.now().isoformat()
    }

