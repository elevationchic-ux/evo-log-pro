"""
GPS Tracking router - manages real-time fleet tracking via PositionGPS and ZoneGeofencing models
"""
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from sqlalchemy import func, desc, and_
from typing import Optional, List
from datetime import datetime, timedelta
from app.core.database import get_db
from app.core.security import get_current_user
from app.models.user import User
from app.models.transport_avance import PositionGPS, ZoneGeofencing, EvenementVehicule

router = APIRouter()


@router.get("/positions")
async def get_positions(
    vehicule_id: Optional[int] = Query(None),
    depuis_minutes: int = Query(60, description="Positions depuis N minutes"),
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Récupère les positions GPS des véhicules"""
    depuis = datetime.utcnow() - timedelta(minutes=depuis_minutes)
    query = db.query(PositionGPS).filter(PositionGPS.horodatage >= depuis)

    if vehicule_id:
        query = query.filter(PositionGPS.vehicule_id == vehicule_id)

    total = query.count()
    positions = query.order_by(desc(PositionGPS.horodatage)).offset(skip).limit(limit).all()

    return {
        "total": total,
        "skip": skip,
        "limit": limit,
        "depuis_minutes": depuis_minutes,
        "data": [
            {
                "id": p.id,
                "vehicule_id": p.vehicule_id,
                "conducteur_id": p.conducteur_id,
                "latitude": float(p.latitude),
                "longitude": float(p.longitude),
                "altitude": float(p.altitude) if p.altitude else None,
                "vitesse": float(p.vitesse) if p.vitesse else 0.0,
                "direction": float(p.direction) if p.direction else None,
                "horodatage": p.horodatage.isoformat() if p.horodatage else None,
                "statut_moteur": p.statut_moteur,
                "statut_vehicule": p.statut_vehicule,
                "kilmetrage_actuel": p.kilmetrage_actuel,
                "niveau_carburant": p.niveau_carburant,
                "code_zone": p.code_zone,
                "alerte": p.alerte,
            }
            for p in positions
        ]
    }


@router.get("/positions/derniere/{vehicule_id}")
async def get_last_position(
    vehicule_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Récupère la dernière position GPS d'un véhicule"""
    pos = db.query(PositionGPS).filter(
        PositionGPS.vehicule_id == vehicule_id
    ).order_by(desc(PositionGPS.horodatage)).first()

    if not pos:
        raise HTTPException(status_code=404, detail="Aucune position trouvée pour ce véhicule")

    return {
        "vehicule_id": pos.vehicule_id,
        "latitude": float(pos.latitude),
        "longitude": float(pos.longitude),
        "vitesse": float(pos.vitesse) if pos.vitesse else 0.0,
        "horodatage": pos.horodatage.isoformat() if pos.horodatage else None,
        "statut_moteur": pos.statut_moteur,
        "statut_vehicule": pos.statut_vehicule,
        "niveau_carburant": pos.niveau_carburant,
        "alerte": pos.alerte,
    }


@router.post("/positions")
async def enregistrer_position(
    data: dict,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Enregistre une nouvelle position GPS"""
    if not data.get("vehicule_id") or not data.get("latitude") or not data.get("longitude"):
        raise HTTPException(status_code=400, detail="vehicule_id, latitude et longitude sont requis")

    pos = PositionGPS(
        vehicule_id=data["vehicule_id"],
        conducteur_id=data.get("conducteur_id"),
        latitude=data["latitude"],
        longitude=data["longitude"],
        altitude=data.get("altitude"),
        vitesse=data.get("vitesse", 0),
        direction=data.get("direction"),
        statut_moteur=data.get("statut_moteur"),
        statut_vehicule=data.get("statut_vehicule"),
        kilmetrage_actuel=data.get("kilmetrage_actuel"),
        niveau_carburant=data.get("niveau_carburant"),
        code_zone=data.get("code_zone"),
        alerte=data.get("alerte"),
    )
    db.add(pos)
    db.commit()
    db.refresh(pos)
    return {"message": "Position enregistrée", "id": pos.id}


@router.get("/zones")
async def get_geofencing_zones(
    skip: int = 0,
    limit: int = 50,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Récupère les zones de géofencing"""
    zones = db.query(ZoneGeofencing).order_by(ZoneGeofencing.nom_zone).offset(skip).limit(limit).all()
    total = db.query(func.count(ZoneGeofencing.id)).scalar() or 0

    return {
        "total": total,
        "data": [
            {
                "id": z.id,
                "nom_zone": z.nom_zone,
                "type_zone": z.type_zone,
                "description": z.description,
                "latitude_centre": float(z.latitude_centre),
                "longitude_centre": float(z.longitude_centre),
                "rayon": float(z.rayon),
                "ville": z.ville,
                "alerte_entree": z.alerte_entree,
                "alerte_sortie": z.alerte_sortie,
                "limite_vitesse": z.limite_vitesse,
                "statut": z.statut,
            }
            for z in zones
        ]
    }


@router.post("/zones")
async def create_zone(
    data: dict,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Crée une zone de géofencing"""
    zone = ZoneGeofencing(
        nom_zone=data.get("nom_zone"),
        type_zone=data.get("type_zone", "client"),
        description=data.get("description"),
        latitude_centre=data.get("latitude_centre"),
        longitude_centre=data.get("longitude_centre"),
        rayon=data.get("rayon", 500),
        ville=data.get("ville"),
        alerte_entree=data.get("alerte_entree", True),
        alerte_sortie=data.get("alerte_sortie", True),
        limite_vitesse=data.get("limite_vitesse"),
    )
    db.add(zone)
    db.commit()
    db.refresh(zone)
    return {"message": "Zone créée", "id": zone.id}


@router.get("/evenements/{vehicule_id}")
async def get_vehicle_events(
    vehicule_id: int,
    skip: int = 0,
    limit: int = 30,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Récupère l'historique des événements d'un véhicule"""
    events = db.query(EvenementVehicule).filter(
        EvenementVehicule.vehicule_id == vehicule_id
    ).order_by(desc(EvenementVehicule.date_evenement)).offset(skip).limit(limit).all()

    return {
        "vehicule_id": vehicule_id,
        "data": [
            {
                "id": e.id,
                "type_evenement": e.type_evenement,
                "date_evenement": e.date_evenement.isoformat() if e.date_evenement else None,
                "localisation": e.localisation,
                "operateur": e.operateur,
                "description": e.description,
            }
            for e in events
        ]
    }


@router.get("/stats/flotte")
async def get_fleet_stats(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Statistiques en temps réel de la flotte"""
    maintenant = datetime.utcnow()
    il_y_a_1h = maintenant - timedelta(hours=1)

    vehicules_actifs = db.query(func.count(PositionGPS.vehicule_id.distinct())).filter(
        PositionGPS.horodatage >= il_y_a_1h
    ).scalar() or 0

    positions_avec_alerte = db.query(func.count(PositionGPS.id)).filter(
        PositionGPS.horodatage >= il_y_a_1h,
        PositionGPS.alerte != None,  # noqa
        PositionGPS.alerte != ""
    ).scalar() or 0

    vitesse_moyenne = db.query(func.avg(PositionGPS.vitesse)).filter(
        PositionGPS.horodatage >= il_y_a_1h,
        PositionGPS.vitesse > 0
    ).scalar() or 0.0

    nb_zones = db.query(func.count(ZoneGeofencing.id)).filter(
        ZoneGeofencing.statut == "actif"
    ).scalar() or 0

    return {
        "vehicules_actifs_1h": vehicules_actifs,
        "alertes_actives": positions_avec_alerte,
        "vitesse_moyenne_kmh": round(float(vitesse_moyenne), 1),
        "zones_geofencing_actives": nb_zones,
        "derniere_mise_a_jour": maintenant.isoformat(),
    }