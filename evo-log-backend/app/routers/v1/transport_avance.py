"""Advanced transport router - Route optimization, fuel tracking, subcontractors"""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from datetime import date, datetime

from app.core.database import get_db
from app.core.security import get_current_user
from app.models.user import User
from app.schemas.transport_avance import (
    TourneeCreate, TourneeUpdate, TourneeResponse,
    LivraisonCreate, LivraisonUpdate, LivraisonResponse,
    FraisKilometriqueCreate, FraisKilometriqueResponse,
    TempsConduiteCreate, TempsConduiteResponse, ConformiteTempsResponse,
    SousTraitantCreate, SousTraitantUpdate, SousTraitantResponse,
    ContratSousTraitantCreate, ContratSousTraitantUpdate, ContratSousTraitantResponse,
    MissionSousTraitantCreate, MissionSousTraitantUpdate, MissionSousTraitantResponse,
    AccidentTransportCreate, AccidentTransportUpdate, AccidentTransportResponse,
    MaintenancePreventiveCreate, MaintenancePreventiveUpdate, MaintenancePreventiveResponse,
    PositionGPSCreate, PositionGPSResponse,
    ZoneGeofencingCreate, ZoneGeofencingUpdate, ZoneGeofencingResponse,
    EvenementVehiculeCreate, EvenementVehiculeResponse,
    CoutKmResponse, AnomalieCarburantResponse, PerformanceSousTraitantResponse,
    StatistiquesAccidentsResponse, ComportementConducteurResponse, KPITransportResponse
)


router = APIRouter(prefix="/transport-avance", tags=["Transport Avancé"])


# ============ TOURNÉES ============
@router.post("/tournees", response_model=TourneeResponse, status_code=status.HTTP_201_CREATED)
def creer_tournee(
    tournee: TourneeCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Create delivery tour/route"""
    from app.models.transport_avance import Tournée
    t = Tournée(
        vehicule_id=tournee.vehicule_id,
        conducteur_id=tournee.conducteur_id,
        date_tournee=tournee.date_tournee,
        origine=tournee.origine,
        destination=tournee.destination,
        statut="planifie"
    )
    db.add(t)
    db.commit()
    db.refresh(t)
    return t


@router.post("/tournees/{tournee_id}/livraisons", response_model=LivraisonResponse, status_code=status.HTTP_201_CREATED)
def ajouter_livraison(
    tournee_id: int,
    livraison: LivraisonCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Add delivery stop to tour"""
    from app.models.transport_avance import Livraison
    l = Livraison(
        tournee_id=tournee_id,
        client_id=livraison.client_id,
        adresse=livraison.adresse,
        ordre_arret=livraison.ordre_arret,
        fenetre_horaire_debut=livraison.fenetre_horaire_debut,
        fenetre_horaire_fin=livraison.fenetre_horaire_fin,
        statut="en_attente"
    )
    db.add(l)
    db.commit()
    db.refresh(l)
    return l


@router.put("/tournees/{tournee_id}/optimiser", response_model=TourneeResponse)
def optimiser_tournee(
    tournee_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Optimize route (placeholder for actual routing algorithm)"""
    from app.models.transport_avance import Tournée, Livraison
    
    tournee = db.query(Tournée).filter(Tournée.id == tournee_id).first()
    if not tournee:
        raise HTTPException(status_code=404, detail="Tournée non trouvée")
    
    livraisons = db.query(Livraison).filter(Livraison.tournee_id == tournee_id).all()
    
    for idx, livraison in enumerate(livraisons):
        livraison.ordre_arret = idx + 1
    
    tournee.statut = "optimise"
    db.commit()
    db.refresh(tournee)
    return tournee


@router.put("/tournees/{tournee_id}/demarrer", response_model=TourneeResponse)
def demarrer_tournee(
    tournee_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Start tour execution"""
    from app.models.transport_avance import Tournée
    
    tournee = db.query(Tournée).filter(Tournée.id == tournee_id).first()
    if not tournee:
        raise HTTPException(status_code=404, detail="Tournée non trouvée")
    
    tournee.statut = "en_cours"
    tournee.heure_depart = datetime.utcnow()
    
    db.commit()
    db.refresh(tournee)
    return tournee


@router.put("/tournees/{tournee_id}/completer", response_model=TourneeResponse)
def completer_tournee(
    tournee_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Complete tour"""
    from app.models.transport_avance import Tournée
    
    tournee = db.query(Tournée).filter(Tournée.id == tournee_id).first()
    if not tournee:
        raise HTTPException(status_code=404, detail="Tournée non trouvée")
    
    tournee.statut = "complete"
    tournee.heure_arrivee = datetime.utcnow()
    
    if tournee.heure_depart:
        tournee.duree_reelle_heures = (tournee.heure_arrivee - tournee.heure_depart).total_seconds() / 3600
    
    db.commit()
    db.refresh(tournee)
    return tournee


# ============ FRAIS KILOMÉTRIQUES ============
@router.post("/frais-km", response_model=FraisKilometriqueResponse, status_code=status.HTTP_201_CREATED)
def enregistrer_frais_kilometrique(
    frais: FraisKilometriqueCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Record mileage expense"""
    from app.models.transport_avance import FraisKilometrique
    f = FraisKilometrique(
        vehicule_id=frais.vehicule_id,
        date_debut=frais.date_debut,
        date_fin=frais.date_fin,
        kilometres_parcourus=frais.kilometres_parcourus,
        taux_remboursement=frais.taux_remboursement,
        montant=frais.montant
    )
    db.add(f)
    db.commit()
    db.refresh(f)
    return f


@router.get("/frais-km/cout/{vehicule_id}/{mois}/{annee}", response_model=CoutKmResponse)
def calculer_cout_km(
    vehicule_id: int,
    mois: int,
    annee: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Calculate cost per kilometer for month"""
    from app.models.transport_avance import FraisKilometrique
    from sqlalchemy import func, and_
    from datetime import timedelta
    
    debut_mois = date(annee, mois, 1)
    fin_mois = (date(annee, mois + 1, 1) - timedelta(days=1)) if mois < 12 else date(annee, 12, 31)
    
    result = db.query(
        func.sum(FraisKilometrique.kilometres_parcourus).label("km"),
        func.sum(FraisKilometrique.montant).label("cout")
    ).filter(
        and_(
            FraisKilometrique.vehicule_id == vehicule_id,
            FraisKilometrique.date_debut >= debut_mois,
            FraisKilometrique.date_fin <= fin_mois
        )
    ).first()
    
    km = result.km or 0
    cout = result.cout or 0
    cout_par_km = cout / km if km > 0 else 0
    
    return {
        "kilometres": km,
        "cout_total": cout,
        "cout_par_km": round(cout_par_km, 2)
    }


# ============ CARBURANT ============
@router.post("/carburant/plein")
def enregistrer_plein_carburant(
    vehicule_id: int,
    date_plein: datetime,
    litres: float,
    prix_litre: float,
    kilometrage: int,
    station: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Record fuel fill-up and calculate consumption"""
    return {
        "vehicule_id": vehicule_id,
        "date_plein": date_plein,
        "litres": litres,
        "prix_litre": prix_litre,
        "kilometrage": kilometrage,
        "station": station
    }


@router.get("/carburant/anomalie/{vehicule_id}", response_model=AnomalieCarburantResponse)
def detecter_anomalie_carburant(
    vehicule_id: int,
    consommation_actuelle: float,
    consommation_theorique: float,
    tolerance: float = 0.2,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Detect fuel fraud/anomaly"""
    difference = abs(consommation_actuelle - consommation_theorique)
    pourcentage_difference = (difference / consommation_theorique) * 100 if consommation_theorique > 0 else 0
    anomalie = pourcentage_difference > (tolerance * 100)
    
    return {
        "consommation_actuelle": consommation_actuelle,
        "consommation_theorique": consommation_theorique,
        "difference": difference,
        "pourcentage_difference": round(pourcentage_difference, 2),
        "anomalie_detectee": anomalie,
        "niveau_alerte": "critique" if pourcentage_difference > 50 else "modere" if anomalie else "normal"
    }


# ============ TEMPS DE CONDUITE ============
@router.post("/temps-conduite", response_model=TempsConduiteResponse, status_code=status.HTTP_201_CREATED)
def enregistrer_temps_conduite(
    temps: TempsConduiteCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Record driving period"""
    from app.models.transport_avance import TempsConduite
    
    duree_heures = (temps.fin_conduite - temps.debut_conduite).total_seconds() / 3600
    
    t = TempsConduite(
        conducteur_id=temps.conducteur_id,
        vehicule_id=temps.vehicule_id,
        debut_conduite=temps.debut_conduite,
        fin_conduite=temps.fin_conduite,
        duree_heures=duree_heures,
        kilometres=temps.kilometres
    )
    db.add(t)
    db.commit()
    db.refresh(t)
    return t


@router.get("/temps-conduite/conformite/{conducteur_id}/{date_verif}", response_model=ConformiteTempsResponse)
def verifier_conformite_temps(
    conducteur_id: int,
    date_verif: date,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Check driving time compliance"""
    from app.models.transport_avance import TempsConduite
    from sqlalchemy import and_, func
    
    debut_jour = datetime.combine(date_verif, datetime.min.time())
    fin_jour = datetime.combine(date_verif, datetime.max.time())
    
    temps_conduite = db.query(TempsConduite).filter(
        and_(
            TempsConduite.conducteur_id == conducteur_id,
            TempsConduite.debut_conduite >= debut_jour,
            TempsConduite.debut_conduite <= fin_jour
        )
    ).all()
    
    total_heures = sum(t.duree_heures for t in temps_conduite)
    non_conforme = total_heures > 9.0
    
    return {
        "date": date_verif,
        "total_heures_conduite": round(total_heures, 2),
        "limite_journaliere": 9.0,
        "conforme": not non_conforme,
        "alerte": "Depassement temps de conduite journalier" if non_conforme else None
    }


# ============ SOUS-TRAITANTS ============
@router.post("/sous-traitants", response_model=SousTraitantResponse, status_code=status.HTTP_201_CREATED)
def creer_sous_traitant(
    sous_traitant: SousTraitantCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Create subcontractor record"""
    from app.models.transport_avance import SousTraitant
    
    s = SousTraitant(
        nom=sous_traitant.nom,
        siret=sous_traitant.siret,
        adresse=sous_traitant.adresse,
        telephone=sous_traitant.telephone,
        email=sous_traitant.email,
        specialites=",".join(sous_traitant.specialites),
        statut="actif"
    )
    db.add(s)
    db.commit()
    db.refresh(s)
    return s


@router.post("/sous-traitants/contrats", response_model=ContratSousTraitantResponse, status_code=status.HTTP_201_CREATED)
def creer_contrat_sous_traitant(
    contrat: ContratSousTraitantCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Create subcontractor contract"""
    from app.models.transport_avance import ContratSousTraitant
    
    c = ContratSousTraitant(
        sous_traitant_id=contrat.sous_traitant_id,
        date_debut=contrat.date_debut,
        date_fin=contrat.date_fin,
        tarif_km=contrat.tarif_km,
        tarif_fixe=contrat.tarif_fixe,
        conditions=contrat.conditions,
        statut="actif"
    )
    db.add(c)
    db.commit()
    db.refresh(c)
    return c


@router.post("/sous-traitants/missions", response_model=MissionSousTraitantResponse, status_code=status.HTTP_201_CREATED)
def attribuer_mission_sous_traitant(
    mission: MissionSousTraitantCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Assign mission to subcontractor"""
    from app.models.transport_avance import MissionSousTraitant
    
    m = MissionSousTraitant(
        contrat_id=mission.contrat_id,
        mission_id=mission.mission_id,
        kilometrage_estime=mission.kilometrage_estime,
        statut="attribue"
    )
    db.add(m)
    db.commit()
    db.refresh(m)
    return m


@router.get("/sous-traitants/{sous_traitant_id}/performance", response_model=PerformanceSousTraitantResponse)
def evaluer_performance_sous_traitant(
    sous_traitant_id: int,
    debut_periode: date,
    fin_periode: date,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Evaluate subcontractor performance"""
    from app.models.transport_avance import MissionSousTraitant, ContratSousTraitant
    from sqlalchemy import and_
    
    missions = db.query(MissionSousTraitant).join(ContratSousTraitant).filter(
        and_(
            ContratSousTraitant.sous_traitant_id == sous_traitant_id,
            MissionSousTraitant.date_creation >= debut_periode,
            MissionSousTraitant.date_creation <= fin_periode
        )
    ).all()
    
    if not missions:
        return {"note": 0, "missions": 0, "taux_completion": 0}
    
    total_missions = len(missions)
    missions_completees = sum(1 for m in missions if m.statut == "complete")
    taux_completion = (missions_completees / total_missions) * 100
    
    retards = []
    for mission in missions:
        if mission.date_livraison_reelle and mission.date_livraison_prevue:
            retard = (mission.date_livraison_reelle - mission.date_livraison_prevue).days
            retards.append(retard)
    
    retard_moyen = sum(retards) / len(retards) if retards else 0
    note = min(100, taux_completion * 0.7 + max(0, 100 - abs(retard_moyen)) * 0.3)
    
    return {
        "note": round(note, 2),
        "missions": total_missions,
        "missions_completees": missions_completees,
        "taux_completion": round(taux_completion, 2),
        "retard_moyen_jours": round(retard_moyen, 2)
    }


# ============ ACCIDENTS ============
@router.post("/accidents", response_model=AccidentTransportResponse, status_code=status.HTTP_201_CREATED)
def declarer_accident(
    accident: AccidentTransportCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Report transport accident"""
    from app.models.transport_avance import AccidentTransport
    
    a = AccidentTransport(
        vehicule_id=accident.vehicule_id,
        conducteur_id=accident.conducteur_id,
        date_accident=accident.date_accident,
        lieu=accident.lieu,
        description=accident.description,
        degats_materiels=accident.degats_materiels,
        blessures=accident.blessures,
        temoins=accident.temoins,
        statut="enquete_en_cours"
    )
    db.add(a)
    db.commit()
    db.refresh(a)
    return a


@router.put("/accidents/{accident_id}/enquete", response_model=AccidentTransportResponse)
def ajouter_enquete(
    accident_id: int,
    enqueteur_id: int,
    rapport: str,
    conclusions: str,
    actions_correctives: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Add investigation findings"""
    from app.models.transport_avance import AccidentTransport
    
    accident = db.query(AccidentTransport).filter(AccidentTransport.id == accident_id).first()
    if not accident:
        raise HTTPException(status_code=404, detail="Accident non trouvé")
    
    accident.enqueteur_id = enqueteur_id
    accident.rapport_enquete = rapport
    accident.conclusions = conclusions
    accident.actions_correctives = actions_correctives
    accident.date_enquete = datetime.utcnow()
    accident.statut = "enquete_complete"
    
    db.commit()
    db.refresh(accident)
    return accident


@router.get("/accidents/statistiques", response_model=StatistiquesAccidentsResponse)
def obtenir_statistiques_accidents(
    debut_periode: date,
    fin_periode: date,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get accident statistics for period"""
    from app.models.transport_avance import AccidentTransport
    from sqlalchemy import and_
    
    accidents = db.query(AccidentTransport).filter(
        and_(
            AccidentTransport.date_accident >= datetime.combine(debut_periode, datetime.min.time()),
            AccidentTransport.date_accident <= datetime.combine(fin_periode, datetime.max.time())
        )
    ).all()
    
    total = len(accidents)
    avec_blessures = sum(1 for a in accidents if a.blessures and a.blessures.lower() != "aucune")
    avec_degats = sum(1 for a in accidents if a.degats_materiels and a.degats_materiels.lower() != "aucun")
    
    return {
        "total_accidents": total,
        "avec_blessures": avec_blessures,
        "avec_degats_materiels": avec_degats,
        "taux_avec_blessures": round((avec_blessures / total) * 100, 2) if total > 0 else 0
    }


# ============ MAINTENANCE PRÉVENTIVE ============
@router.post("/maintenance-preventive", response_model=MaintenancePreventiveResponse, status_code=status.HTTP_201_CREATED)
def planifier_maintenance_preventive(
    maintenance: MaintenancePreventiveCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Schedule preventive maintenance"""
    from app.models.transport_avance import MaintenancePreventive
    
    m = MaintenancePreventive(
        vehicule_id=maintenance.vehicule_id,
        type_maintenance=maintenance.type_maintenance,
        date_prevue=maintenance.date_prevue,
        kilometrage_prevu=maintenance.kilometrage_prevu,
        description=maintenance.description,
        statut="planifie"
    )
    db.add(m)
    db.commit()
    db.refresh(m)
    return m


@router.put("/maintenance-preventive/{maintenance_id}/executer", response_model=MaintenancePreventiveResponse)
def executer_maintenance(
    maintenance_id: int,
    date_execution: date,
    kilometrage_reel: int,
    cout: float,
    technicien: str,
    observations: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Execute preventive maintenance"""
    from app.models.transport_avance import MaintenancePreventive
    
    m = db.query(MaintenancePreventive).filter(MaintenancePreventive.id == maintenance_id).first()
    if not m:
        raise HTTPException(status_code=404, detail="Maintenance non trouvée")
    
    m.date_execution = date_execution
    m.kilometrage_reel = kilometrage_reel
    m.cout = cout
    m.technicien = technicien
    m.observations = observations
    m.statut = "execute"
    
    db.commit()
    db.refresh(m)
    return m


@router.get("/maintenance-preventive/urgentes")
def obtenir_maintenances_urgentes(
    jours_critique: int = 7,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get maintenance due within critical period"""
    from app.models.transport_avance import MaintenancePreventive
    from sqlalchemy import and_
    
    date_limite = date.today() + timedelta(days=jours_critique)
    
    maintenances = db.query(MaintenancePreventive).filter(
        and_(
            MaintenancePreventive.date_prevue <= date_limite,
            MaintenancePreventive.statut == "planifie"
        )
    ).order_by(MaintenancePreventive.date_prevue.asc()).all()
    
    return maintenances


# ============ GPS TRACKING ============
@router.post("/gps/positions", response_model=PositionGPSResponse, status_code=status.HTTP_201_CREATED)
def enregistrer_position(
    position: PositionGPSCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Record GPS position"""
    from app.models.transport_avance import PositionGPS
    
    p = PositionGPS(
        vehicule_id=position.vehicule_id,
        latitude=position.latitude,
        longitude=position.longitude,
        vitesse=position.vitesse,
        direction=position.direction,
        horodatage=position.horodatage
    )
    db.add(p)
    db.commit()
    db.refresh(p)
    return p


@router.get("/gps/derniere-position/{vehicule_id}", response_model=PositionGPSResponse)
def obtenir_derniere_position(
    vehicule_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get last known position of vehicle"""
    from app.models.transport_avance import PositionGPS
    
    position = db.query(PositionGPS).filter(
        PositionGPS.vehicule_id == vehicule_id
    ).order_by(PositionGPS.horodatage.desc()).first()
    
    if not position:
        raise HTTPException(status_code=404, detail="Position non trouvée")
    return position


@router.get("/gps/trajectoire/{vehicule_id}")
def obtenir_trajectoire(
    vehicule_id: int,
    debut: datetime,
    fin: datetime,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get vehicle trajectory for time period"""
    from app.models.transport_avance import PositionGPS
    from sqlalchemy import and_
    
    return db.query(PositionGPS).filter(
        and_(
            PositionGPS.vehicule_id == vehicule_id,
            PositionGPS.horodatage >= debut,
            PositionGPS.horodatage <= fin
        )
    ).order_by(PositionGPS.horodatage.asc()).all()


# ============ GEOFENCING ============
@router.post("/geofencing/zones", response_model=ZoneGeofencingResponse, status_code=status.HTTP_201_CREATED)
def creer_zone_geofencing(
    zone: ZoneGeofencingCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Create geofencing zone"""
    from app.models.transport_avance import ZoneGeofencing
    
    z = ZoneGeofencing(
        nom_zone=zone.nom_zone,
        type_zone=zone.type_zone,
        latitude_centre=zone.latitude_centre,
        longitude_centre=zone.longitude_centre,
        rayon_metres=zone.rayon_metres,
        statut="actif"
    )
    db.add(z)
    db.commit()
    db.refresh(z)
    return z


@router.get("/geofencing/verifier/{vehicule_id}")
def verifier_violation_geofencing(
    vehicule_id: int,
    latitude: float,
    longitude: float,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Check if position violates any geofencing zones"""
    from app.models.transport_avance import ZoneGeofencing
    
    zones = db.query(ZoneGeofencing).filter(ZoneGeofencing.statut == "actif").all()
    
    violations = []
    for zone in zones:
        distance = ((latitude - zone.latitude_centre) ** 2 + 
                   (longitude - zone.longitude_centre) ** 2) ** 0.5 * 111000
        
        if distance <= zone.rayon_metres:
            violations.append(zone)
    
    return violations


@router.post("/geofencing/evenements", response_model=EvenementVehiculeResponse, status_code=status.HTTP_201_CREATED)
def enregistrer_evenement_vehicule(
    evenement: EvenementVehiculeCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Record vehicle event (geofence violation, speeding, etc.)"""
    from app.models.transport_avance import EvenementVehicule
    
    e = EvenementVehicule(
        vehicule_id=evenement.vehicule_id,
        type_evenement=evenement.type_evenement,
        description=evenement.description,
        latitude=evenement.latitude,
        longitude=evenement.longitude,
        date_evenement=datetime.utcnow()
    )
    db.add(e)
    db.commit()
    db.refresh(e)
    return e


# ============ COMPORTEMENT CONDUCTEUR ============
@router.get("/conducteurs/{conducteur_id}/comportement", response_model=ComportementConducteurResponse)
def evaluer_conducteur(
    conducteur_id: int,
    debut_periode: date,
    fin_periode: date,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Evaluate driver behavior score"""
    from app.models.transport_avance import TempsConduite, AccidentTransport, EvenementVehicule
    from app.models.parc import Vehicule
    from app.models.transport import Mission
    from sqlalchemy import and_, func
    
    debut = datetime.combine(debut_periode, datetime.min.time())
    fin = datetime.combine(fin_periode, datetime.max.time())
    
    temps_conduite = db.query(func.sum(TempsConduite.duree_heures)).filter(
        and_(
            TempsConduite.conducteur_id == conducteur_id,
            TempsConduite.debut_conduite >= debut,
            TempsConduite.debut_conduite <= fin
        )
    ).scalar() or 0
    
    accidents = db.query(AccidentTransport).filter(
        and_(
            AccidentTransport.conducteur_id == conducteur_id,
            AccidentTransport.date_accident >= debut,
            AccidentTransport.date_accident <= fin
        )
    ).count()
    
    violations = db.query(EvenementVehicule).filter(
        and_(
            EvenementVehicule.vehicule_id.in_(
                db.query(Vehicule.id).join(Mission).filter(
                    Mission.conducteur_id == conducteur_id
                )
            ),
            EvenementVehicule.type_evenement == "violation_geofence",
            EvenementVehicule.date_evenement >= debut,
            EvenementVehicule.date_evenement <= fin
        )
    ).count()
    
    score_base = 100
    score = score_base - (accidents * 20) - (violations * 5)
    score = max(0, min(100, score))
    
    return {
        "conducteur_id": conducteur_id,
        "heures_conduite": round(temps_conduite, 2),
        "accidents": accidents,
        "violations_geofence": violations,
        "score_comportement": round(score, 2),
        "niveau": "excellent" if score >= 90 else "bon" if score >= 70 else "moyen" if score >= 50 else "critique"
    }


# ============ KPIs TRANSPORT ============
@router.get("/kpi/livraison-ponctuelle")
def calculer_taux_livraison_ponctuelle(
    debut_periode: date,
    fin_periode: date,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Calculate on-time delivery rate"""
    taux = KPITransportService.calculer_taux_livraison_ponctuelle(db, debut_periode, fin_periode)
    return {"taux_livraison_ponctuelle": taux}


@router.get("/kpi/utilisation-vehicules/{vehicule_id}")
def calculer_taux_utilisation_vehicules(
    vehicule_id: int,
    jours: int = 30,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Calculate vehicle utilization rate"""
    taux = KPITransportService.calculer_taux_utilisation_vehicules(db, vehicule_id, jours)
    return {"vehicule_id": vehicule_id, "taux_utilisation": taux}


@router.get("/kpi/variance-carburant/{vehicule_id}")
def calculer_variance_carburant(
    vehicule_id: int,
    debut_periode: date,
    fin_periode: date,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Calculate fuel variance (actual vs theoretical)"""
    return KPITransportService.calculer_variance_carburant(
        db, vehicule_id, debut_periode, fin_periode
    )
