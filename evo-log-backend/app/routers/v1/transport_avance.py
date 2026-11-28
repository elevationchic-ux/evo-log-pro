"""Advanced transport router - Route optimization, fuel tracking, subcontractors"""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy import func, and_
from typing import List, Optional
from datetime import date, datetime, timedelta
from uuid import uuid4

from app.core.database import get_db
from app.core.permissions import require_perm
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
    StatistiquesAccidentsResponse, ComportementConducteurResponse
)


router = APIRouter(tags=["Transport Avancé"])  # monte sur /api/v1/transport-avance par main.py

LIMITE_CONDUITE_MINUTES = 540  # 9 h/jour


def _code(prefix: str) -> str:
    return f"{prefix}-{datetime.now().strftime('%Y%m%d')}-{uuid4().hex[:6].upper()}"


def _get_or_404(db: Session, model, ident: int, label: str):
    obj = db.query(model).filter(model.id == ident).first()
    if not obj:
        raise HTTPException(status_code=404, detail=f"{label} non trouvé(e)")
    return obj


# ============ TOURNÉES ============
@router.post("/tournees", response_model=TourneeResponse, status_code=status.HTTP_201_CREATED)
def creer_tournee(
    tournee: TourneeCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_perm("transport.dispatch.create"))
):
    """Create delivery tour/route"""
    from app.models.transport_avance import Tournée, StatutTournée
    t = Tournée(
        numero_tournee=_code("TRN"),
        conducteur_id=tournee.conducteur_id,
        camion_id=tournee.camion_id,
        date_tournee=tournee.date_tournee,
        type_tournee=tournee.type_tournee,
        notes=tournee.notes,
        statut=StatutTournée.PLANIFIEE,
        createur=current_user.id
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
    current_user: User = Depends(require_perm("transport.dispatch.create"))
):
    """Add delivery stop to tour"""
    from app.models.transport_avance import Tournée, Livraison
    tournee = _get_or_404(db, Tournée, tournee_id, "Tournée")
    l = Livraison(
        numero_livraison=_code("LIV"),
        tournee_id=tournee_id,
        client_id=livraison.client_id,
        point_dechargement=livraison.point_dechargement,
        heure_debut_prevue=livraison.heure_debut_prevue,
        heure_fin_prevue=livraison.heure_fin_prevue,
        nombre_colis=livraison.nombre_colis,
        poids_total=livraison.poids_total,
        commentaire=livraison.commentaire,
        statut="en_attente"
    )
    db.add(l)
    tournee.nombre_livraisons = (tournee.nombre_livraisons or 0) + 1
    db.commit()
    db.refresh(l)
    return l


@router.put("/tournees/{tournee_id}/optimiser", response_model=TourneeResponse)
def optimiser_tournee(
    tournee_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_perm("transport.dispatch.modify"))
):
    """Resynchronise le compteur de livraisons de la tournée.

    Aucun moteur de routage n'est branché : l'endpoint vérifie la tournée,
    recompte ses arrêts réels et renvoie l'état courant (pas de statut
    'optimise' fictif — l'enum StatutTournée n'en prévoit pas).
    """
    from app.models.transport_avance import Tournée, Livraison
    tournee = _get_or_404(db, Tournée, tournee_id, "Tournée")
    nb = db.query(func.count(Livraison.id)).filter(Livraison.tournee_id == tournee_id).scalar() or 0
    tournee.nombre_livraisons = nb
    db.commit()
    db.refresh(tournee)
    return tournee


@router.put("/tournees/{tournee_id}/demarrer", response_model=TourneeResponse)
def demarrer_tournee(
    tournee_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_perm("transport.dispatch.modify"))
):
    """Start tour execution"""
    from app.models.transport_avance import Tournée, StatutTournée
    tournee = _get_or_404(db, Tournée, tournee_id, "Tournée")
    if tournee.statut == StatutTournée.EN_COURS:
        raise HTTPException(status_code=409, detail="Tournée déjà en cours")
    if tournee.statut == StatutTournée.TERMINEE:
        raise HTTPException(status_code=409, detail="Tournée déjà terminée")
    tournee.statut = StatutTournée.EN_COURS
    db.commit()
    db.refresh(tournee)
    return tournee


@router.put("/tournees/{tournee_id}/completer", response_model=TourneeResponse)
def completer_tournee(
    tournee_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_perm("transport.dispatch.modify"))
):
    """Complete tour — recalcule livraisons effectuées et performance réelle"""
    from app.models.transport_avance import Tournée, Livraison, StatutTournée
    tournee = _get_or_404(db, Tournée, tournee_id, "Tournée")
    effectuees = db.query(func.count(Livraison.id)).filter(
        Livraison.tournee_id == tournee_id,
        Livraison.statut == "livre"
    ).scalar() or 0
    total = tournee.nombre_livraisons or 0
    tournee.nombre_livraisons_effectuees = effectuees
    if total > 0:
        tournee.performance = round((effectuees / total) * 100, 2)
    tournee.statut = StatutTournée.TERMINEE
    db.commit()
    db.refresh(tournee)
    return tournee


# ============ FRAIS KILOMÉTRIQUES ============
@router.post("/frais-km", response_model=FraisKilometriqueResponse, status_code=status.HTTP_201_CREATED)
def enregistrer_frais_kilometrique(
    frais: FraisKilometriqueCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_perm("transport.dispatch.create"))
):
    """Record mileage expense (indemnité kilométrique)"""
    from app.models.transport_avance import FraisKilometrique
    km = frais.kilometrage_parcouru
    theorique = frais.kilometrage_theorique
    montant = round(km * frais.taux_indemnite, 2) if frais.taux_indemnite is not None else None
    surplus = round(km - theorique, 2) if theorique is not None else None
    f = FraisKilometrique(
        employe_id=frais.employe_id,
        mission_id=frais.mission_id,
        kilometrage_parcouru=km,
        kilometrage_theorique=theorique,
        taux_indemnite=frais.taux_indemnite,
        montant_indemnite=montant,
        surconsommation=surplus,
        statut="en_attente",
        commentaires=frais.commentaires
    )
    db.add(f)
    db.commit()
    db.refresh(f)
    return f


@router.get("/frais-km/cout/{camion_id}/{mois}/{annee}", response_model=CoutKmResponse)
def calculer_cout_km(
    camion_id: int,
    mois: int,
    annee: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_perm("transport.dispatch.read"))
):
    """Calculate cost per kilometer for month (via missions du camion)"""
    from app.models.transport_avance import FraisKilometrique
    from app.models.transport import Mission

    if not 1 <= mois <= 12:
        raise HTTPException(status_code=400, detail="Mois invalide (1-12)")
    debut_mois = date(annee, mois, 1)
    fin_mois = (date(annee + 1, 1, 1) - timedelta(days=1)) if mois == 12 else (date(annee, mois + 1, 1) - timedelta(days=1))

    result = db.query(
        func.sum(FraisKilometrique.kilometrage_parcouru).label("km"),
        func.sum(FraisKilometrique.montant_indemnite).label("cout")
    ).join(Mission, FraisKilometrique.mission_id == Mission.id).filter(
        and_(
            Mission.camion_id == camion_id,
            FraisKilometrique.date_frais >= debut_mois,
            FraisKilometrique.date_frais <= fin_mois
        )
    ).first()

    km = float(result.km or 0)
    cout = float(result.cout or 0)
    return {
        "camion_id": camion_id,
        "mois": mois,
        "annee": annee,
        "kilometres": km,
        "cout_total": cout,
        "cout_par_km": round(cout / km, 2) if km > 0 else 0
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
    numero_ticket: Optional[str] = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_perm("transport.dispatch.create"))
):
    """Record fuel fill-up — persisté dans fleet_carburant_records (parc)
    et consommation calculée si l'index précédent est connu."""
    from app.models.parc import CarburantRecord, Vehicule

    vehicule = db.query(Vehicule).filter(Vehicule.id == vehicule_id).first()
    precedent = db.query(CarburantRecord).filter(
        CarburantRecord.vehicule_id == vehicule_id,
        CarburantRecord.kilometrage.isnot(None)
    ).order_by(CarburantRecord.kilometrage.desc()).first()
    index_precedent = precedent.kilometrage if precedent else None

    record = CarburantRecord(
        vehicule_id=vehicule_id,
        immatriculation=vehicule.immatriculation if vehicule else None,
        date_plein=date_plein,
        litres=litres,
        prix_litre=prix_litre,
        cout=round(litres * prix_litre, 2),
        kilometrage=kilometrage,
        station=station,
        numero_ticket=numero_ticket,
        index_precedent=index_precedent,
        statut="valide"
    )
    db.add(record)
    db.commit()
    db.refresh(record)

    conso_100km = None
    if index_precedent is not None and kilometrage > index_precedent:
        conso_100km = round((litres / (kilometrage - index_precedent)) * 100, 2)

    return {
        "id": record.id,
        "vehicule_id": vehicule_id,
        "immatriculation": record.immatriculation,
        "date_plein": record.date_plein,
        "litres": float(litres),
        "prix_litre": float(prix_litre),
        "cout": float(record.cout or 0),
        "kilometrage": kilometrage,
        "station": station,
        "index_precedent": index_precedent,
        "consommation_l_100km": conso_100km
    }


@router.get("/carburant/anomalie/{vehicule_id}", response_model=AnomalieCarburantResponse)
def detecter_anomalie_carburant(
    vehicule_id: int,
    consommation_actuelle: float,
    consommation_theorique: float,
    tolerance: float = 0.2,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_perm("transport.dispatch.read"))
):
    """Detect fuel fraud/anomaly"""
    difference = abs(consommation_actuelle - consommation_theorique)
    pourcentage_difference = (difference / consommation_theorique) * 100 if consommation_theorique > 0 else 0
    anomalie = pourcentage_difference > (tolerance * 100)

    return {
        "vehicule_id": vehicule_id,
        "consommation_actuelle": consommation_actuelle,
        "consommation_theorique": consommation_theorique,
        "difference": round(difference, 2),
        "pourcentage_difference": round(pourcentage_difference, 2),
        "anomalie_detectee": anomalie,
        "niveau_alerte": "critique" if pourcentage_difference > 50 else "modere" if anomalie else "normal"
    }


# ============ TEMPS DE CONDUITE ============
@router.post("/temps-conduite", response_model=TempsConduiteResponse, status_code=status.HTTP_201_CREATED)
def enregistrer_temps_conduite(
    temps: TempsConduiteCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_perm("transport.dispatch.create"))
):
    """Record driving period (minutes) — conformité légale 9 h/j calculée"""
    from app.models.transport_avance import TempsConduite
    conformite = temps.temps_conduite <= LIMITE_CONDUITE_MINUTES
    t = TempsConduite(
        conducteur_id=temps.conducteur_id,
        mission_id=temps.mission_id,
        date=temps.date,
        heure_debut_conduite=temps.heure_debut_conduite,
        heure_fin_conduite=temps.heure_fin_conduite,
        temps_conduite=temps.temps_conduite,
        temps_repos=temps.temps_repos,
        temps_service=(temps.temps_conduite or 0) + (temps.temps_repos or 0),
        conformite_legale=conformite,
        statut="conforme" if conformite else "non_conforme",
        commentaires=temps.commentaires
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
    current_user: User = Depends(require_perm("transport.dispatch.read"))
):
    """Check driving time compliance for a driver on a given day"""
    from app.models.transport_avance import TempsConduite

    enregistrements = db.query(TempsConduite).filter(
        and_(
            TempsConduite.conducteur_id == conducteur_id,
            TempsConduite.date == date_verif
        )
    ).all()

    total_minutes = sum(t.temps_conduite or 0 for t in enregistrements)
    infractions = sum(1 for t in enregistrements if t.conformite_legale is False)
    depassement = total_minutes > LIMITE_CONDUITE_MINUTES
    conforme = not depassement and infractions == 0

    return {
        "conducteur_id": conducteur_id,
        "date": date_verif,
        "total_minutes_conduite": total_minutes,
        "limite_journaliere_minutes": LIMITE_CONDUITE_MINUTES,
        "infractions": infractions,
        "conforme": conforme,
        "alerte": "Dépassement du temps de conduite journalier" if depassement else
                  (f"{infractions} enregistrement(s) non conforme(s)" if infractions else None)
    }


# ============ SOUS-TRAITANTS ============
@router.post("/sous-traitants", response_model=SousTraitantResponse, status_code=status.HTTP_201_CREATED)
def creer_sous_traitant(
    sous_traitant: SousTraitantCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_perm("transport.dispatch.create"))
):
    """Create subcontractor record"""
    from app.models.transport_avance import SousTraitant

    s = SousTraitant(
        code=sous_traitant.code or _code("ST"),
        nom=sous_traitant.nom,
        type_service=sous_traitant.type_service,
        specialite=sous_traitant.specialite,
        numero_licence=sous_traitant.numero_licence,
        adresse=sous_traitant.adresse,
        ville=sous_traitant.ville,
        telephone=sous_traitant.telephone,
        email=sous_traitant.email,
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
    current_user: User = Depends(require_perm("transport.dispatch.create"))
):
    """Create subcontractor contract"""
    from app.models.transport_avance import ContratSousTraitant, SousTraitant
    _get_or_404(db, SousTraitant, contrat.sous_traitant_id, "Sous-traitant")

    c = ContratSousTraitant(
        sous_traitant_id=contrat.sous_traitant_id,
        numero_contrat=contrat.numero_contrat,
        type_service=contrat.type_service,
        date_debut=contrat.date_debut,
        date_fin=contrat.date_fin,
        tarif_unitaire=contrat.tarif_unitaire,
        unite_tarif=contrat.unite_tarif,
        volume_minimum=contrat.volume_minimum,
        conditions_paiement=contrat.conditions_paiement,
        notes=contrat.notes,
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
    current_user: User = Depends(require_perm("transport.dispatch.create"))
):
    """Assign mission to subcontractor"""
    from app.models.transport_avance import MissionSousTraitant, SousTraitant
    _get_or_404(db, SousTraitant, mission.sous_traitant_id, "Sous-traitant")

    m = MissionSousTraitant(
        numero_mission=_code("STM"),
        sous_traitant_id=mission.sous_traitant_id,
        contrat_id=mission.contrat_id,
        client_id=mission.client_id,
        date_mission=mission.date_mission,
        point_depart=mission.point_depart,
        point_arrivee=mission.point_arrivee,
        distance=mission.distance,
        type_marchandise=mission.type_marchandise,
        poids=mission.poids,
        cout_estime=mission.cout_estime,
        notes=mission.notes,
        statut="planifiee"
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
    current_user: User = Depends(require_perm("transport.dispatch.read"))
):
    """Evaluate subcontractor performance from real mission records"""
    from app.models.transport_avance import MissionSousTraitant

    missions = db.query(MissionSousTraitant).filter(
        and_(
            MissionSousTraitant.sous_traitant_id == sous_traitant_id,
            MissionSousTraitant.date_mission >= debut_periode,
            MissionSousTraitant.date_mission <= fin_periode
        )
    ).all()

    total = len(missions)
    if total == 0:
        return {
            "sous_traitant_id": sous_traitant_id,
            "missions_totales": 0,
            "missions_terminees": 0,
            "taux_completion": 0,
            "ponctualite_moyenne": None,
            "qualite_moyenne": None,
            "note": 0
        }

    terminees = [m for m in missions if m.statut == "terminee"]
    ponctualites = [m.ponctualite for m in missions if m.ponctualite is not None]
    qualites = [m.qualite_service for m in missions if m.qualite_service is not None]

    taux_completion = (len(terminees) / total) * 100
    ponctualite_moy = sum(ponctualites) / len(ponctualites) if ponctualites else None
    qualite_moy = sum(qualites) / len(qualites) if qualites else None

    # Note : moyenne des évaluations saisies si présentes, sinon taux de completion
    notes = [n for n in ponctualites + qualites]
    note = round(sum(notes) / len(notes), 2) if notes else round(taux_completion, 2)

    return {
        "sous_traitant_id": sous_traitant_id,
        "missions_totales": total,
        "missions_terminees": len(terminees),
        "taux_completion": round(taux_completion, 2),
        "ponctualite_moyenne": round(ponctualite_moy, 2) if ponctualite_moy is not None else None,
        "qualite_moyenne": round(qualite_moy, 2) if qualite_moy is not None else None,
        "note": note
    }


# ============ ACCIDENTS ============
@router.post("/accidents", response_model=AccidentTransportResponse, status_code=status.HTTP_201_CREATED)
def declarer_accident(
    accident: AccidentTransportCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_perm("transport.dispatch.create"))
):
    """Report transport accident"""
    from app.models.transport_avance import AccidentTransport

    a = AccidentTransport(
        numero_accident=_code("ACC"),
        vehicule_id=accident.vehicule_id,
        conducteur_id=accident.conducteur_id,
        mission_id=accident.mission_id,
        date_accident=accident.date_accident,
        heure_accident=accident.heure_accident,
        lieu=accident.lieu,
        type_accident=accident.type_accident,
        gravite=accident.gravite,
        blesses=accident.blesses,
        deces=accident.deces,
        degats_materiels=accident.degats_materiels,
        temoins=accident.temoins,
        constat=accident.constat,
        assureur=accident.assureur,
        numero_police=accident.numero_police,
        montant_dommages=accident.montant_dommages,
        notes=accident.notes,
        statut="en_cours"
    )
    db.add(a)
    db.commit()
    db.refresh(a)
    return a


@router.put("/accidents/{accident_id}/enquete", response_model=AccidentTransportResponse)
def ajouter_enquete(
    accident_id: int,
    enquete: AccidentTransportUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_perm("transport.dispatch.modify"))
):
    """Add investigation findings (constat, statut, clôture)"""
    from app.models.transport_avance import AccidentTransport

    accident = _get_or_404(db, AccidentTransport, accident_id, "Accident")
    for field, value in enquete.model_dump(exclude_unset=True).items():
        setattr(accident, field, value)
    db.commit()
    db.refresh(accident)
    return accident


@router.get("/accidents/statistiques", response_model=StatistiquesAccidentsResponse)
def obtenir_statistiques_accidents(
    debut_periode: date,
    fin_periode: date,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_perm("transport.dispatch.read"))
):
    """Get accident statistics for period"""
    from app.models.transport_avance import AccidentTransport

    accidents = db.query(AccidentTransport).filter(
        and_(
            AccidentTransport.date_accident >= datetime.combine(debut_periode, datetime.min.time()),
            AccidentTransport.date_accident <= datetime.combine(fin_periode, datetime.max.time())
        )
    ).all()

    return {
        "debut_periode": debut_periode,
        "fin_periode": fin_periode,
        "accidents_totaux": len(accidents),
        "avec_blesses": sum(1 for a in accidents if (a.blesses or 0) > 0),
        "avec_deces": sum(1 for a in accidents if (a.deces or 0) > 0),
        "montant_total_dommages": round(sum(float(a.montant_dommages or 0) for a in accidents), 2),
        "montant_total_rembourse": round(sum(float(a.montant_rembourse or 0) for a in accidents), 2)
    }


# ============ MAINTENANCE PRÉVENTIVE ============
@router.post("/maintenance-preventive", response_model=MaintenancePreventiveResponse, status_code=status.HTTP_201_CREATED)
def planifier_maintenance_preventive(
    maintenance: MaintenancePreventiveCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_perm("transport.dispatch.create"))
):
    """Schedule preventive maintenance"""
    from app.models.transport_avance import MaintenancePreventive

    m = MaintenancePreventive(
        vehicule_id=maintenance.vehicule_id,
        type_maintenance=maintenance.type_maintenance,
        kilometrage_prevu=maintenance.kilometrage_prevu,
        date_prevue=maintenance.date_prevue,
        periodicite=maintenance.periodicite,
        cout_estime=maintenance.cout_estime,
        notes=maintenance.notes,
        statut="planifie"
    )
    db.add(m)
    db.commit()
    db.refresh(m)
    return m


@router.put("/maintenance-preventive/{maintenance_id}/executer", response_model=MaintenancePreventiveResponse)
def executer_maintenance(
    maintenance_id: int,
    date_effective: date,
    cout_reel: Optional[float] = None,
    realise_par: Optional[str] = None,
    notes: Optional[str] = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_perm("transport.dispatch.modify"))
):
    """Execute preventive maintenance"""
    from app.models.transport_avance import MaintenancePreventive

    m = _get_or_404(db, MaintenancePreventive, maintenance_id, "Maintenance")
    m.date_effective = date_effective
    m.cout_reel = cout_reel
    m.realise_par = realise_par
    if notes:
        m.notes = notes
    m.statut = "realisee"

    db.commit()
    db.refresh(m)
    return m


@router.get("/maintenance-preventive/urgentes")
def obtenir_maintenances_urgentes(
    jours_critique: int = 7,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_perm("transport.dispatch.read"))
):
    """Get maintenance due within critical period"""
    from app.models.transport_avance import MaintenancePreventive

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
    current_user: User = Depends(require_perm("transport.dispatch.create"))
):
    """Record GPS position"""
    from app.models.transport_avance import PositionGPS

    p = PositionGPS(
        vehicule_id=position.vehicule_id,
        conducteur_id=position.conducteur_id,
        latitude=position.latitude,
        longitude=position.longitude,
        altitude=position.altitude,
        vitesse=position.vitesse,
        direction=position.direction,
        statut_moteur=position.statut_moteur,
        statut_vehicule=position.statut_vehicule,
        kilmetrage_actuel=position.kilmetrage_actuel,
        niveau_carburant=position.niveau_carburant,
        alerte=position.alerte,
        horodatage=position.horodatage or datetime.utcnow()
    )
    db.add(p)
    db.commit()
    db.refresh(p)
    return p


@router.get("/gps/derniere-position/{vehicule_id}", response_model=PositionGPSResponse)
def obtenir_derniere_position(
    vehicule_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_perm("transport.dispatch.read"))
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
    current_user: User = Depends(require_perm("transport.dispatch.read"))
):
    """Get vehicle trajectory for time period"""
    from app.models.transport_avance import PositionGPS

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
    current_user: User = Depends(require_perm("transport.dispatch.create"))
):
    """Create geofencing zone"""
    from app.models.transport_avance import ZoneGeofencing

    z = ZoneGeofencing(
        nom_zone=zone.nom_zone,
        type_zone=zone.type_zone,
        description=zone.description,
        latitude_centre=zone.latitude_centre,
        longitude_centre=zone.longitude_centre,
        rayon=zone.rayon_metres,
        ville=zone.ville,
        limite_vitesse=zone.limite_vitesse,
        alerte_entree=zone.alerte_entree,
        alerte_sortie=zone.alerte_sortie,
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
    current_user: User = Depends(require_perm("transport.dispatch.read"))
):
    """Check if position is inside any active geofencing zone (approx. equirectangulaire)"""
    from app.models.transport_avance import ZoneGeofencing
    import math

    zones = db.query(ZoneGeofencing).filter(ZoneGeofencing.statut == "actif").all()

    dedans = []
    for zone in zones:
        lat_rad = math.radians(float(zone.latitude_centre or 0))
        dx = (longitude - float(zone.longitude_centre or 0)) * math.cos(lat_rad) * 111320
        dy = (latitude - float(zone.latitude_centre or 0)) * 110540
        distance = math.sqrt(dx * dx + dy * dy)
        if distance <= float(zone.rayon or 0):
            dedans.append({
                "id": zone.id,
                "nom_zone": zone.nom_zone,
                "type_zone": zone.type_zone,
                "distance_metres": round(distance, 1)
            })

    return {
        "vehicule_id": vehicule_id,
        "latitude": latitude,
        "longitude": longitude,
        "zones_actives_detectees": dedans,
        "violation": len(dedans) > 0
    }


@router.post("/geofencing/evenements", response_model=EvenementVehiculeResponse, status_code=status.HTTP_201_CREATED)
def enregistrer_evenement_vehicule(
    evenement: EvenementVehiculeCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_perm("transport.dispatch.create"))
):
    """Record vehicle event (geofence violation, speeding, etc.)"""
    from app.models.transport_avance import EvenementVehicule

    e = EvenementVehicule(
        vehicule_id=evenement.vehicule_id,
        type_evenement=evenement.type_evenement,
        description=evenement.description,
        localisation=evenement.localisation,
        operateur=evenement.operateur,
        date_evenement=evenement.date_evenement or datetime.utcnow()
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
    current_user: User = Depends(require_perm("transport.dispatch.read"))
):
    """Evaluate driver behavior score from real records (heures, accidents, missions)"""
    from app.models.transport_avance import TempsConduite, AccidentTransport
    from app.models.transport import Mission, MissionStatus

    debut = datetime.combine(debut_periode, datetime.min.time())
    fin = datetime.combine(fin_periode, datetime.max.time())

    minutes = db.query(func.sum(TempsConduite.temps_conduite)).filter(
        and_(
            TempsConduite.conducteur_id == conducteur_id,
            TempsConduite.date >= debut_periode,
            TempsConduite.date <= fin_periode
        )
    ).scalar() or 0
    heures_conduite = round(minutes / 60, 2)

    accidents = db.query(AccidentTransport).filter(
        and_(
            AccidentTransport.conducteur_id == conducteur_id,
            AccidentTransport.date_accident >= debut,
            AccidentTransport.date_accident <= fin
        )
    ).count()

    missions = db.query(Mission).filter(
        and_(
            Mission.conducteur_id == conducteur_id,
            Mission.date_debut_reelle >= debut,
            Mission.date_debut_reelle <= fin
        )
    ).count()

    # Score : 100 - 20/accident - 2 point par heure au-delà de 45h/semaine-equivalent
    score = 100 - (accidents * 20) - max(0, heures_conduite - 45) * 2
    score = max(0, min(100, round(score, 2)))
    niveau = "excellent" if score >= 90 else "bon" if score >= 70 else "moyen" if score >= 50 else "critique"

    return {
        "conducteur_id": conducteur_id,
        "debut_periode": debut_periode,
        "fin_periode": fin_periode,
        "heures_conduite": heures_conduite,
        "accidents": accidents,
        "missions": missions,
        "score_comportement": score,
        "niveau": niveau
    }


# ============ KPIs TRANSPORT ============
@router.get("/kpi/livraison-ponctuelle")
def calculer_taux_livraison_ponctuelle(
    debut_periode: date,
    fin_periode: date,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_perm("transport.dispatch.read"))
):
    """Taux de livraisons terminées à l'heure (date_fin_reelle <= date_fin_prevue)"""
    from app.models.transport import Mission, MissionStatus

    missions = db.query(Mission).filter(
        and_(
            Mission.statut == MissionStatus.TERMINEE,
            Mission.date_fin_reelle.isnot(None),
            Mission.date_fin_reelle >= datetime.combine(debut_periode, datetime.min.time()),
            Mission.date_fin_reelle <= datetime.combine(fin_periode, datetime.max.time())
        )
    ).all()

    evaluables = [m for m in missions if m.date_fin_prevue is not None]
    if not evaluables:
        return {"taux_livraison_ponctuelle": None, "missions_evaluees": 0,
                "note": "Aucune mission terminée avec date de fin prévue sur la période"}

    a_lheure = sum(1 for m in evaluables if m.date_fin_reelle <= m.date_fin_prevue)
    taux = round((a_lheure / len(evaluables)) * 100, 2)
    return {"taux_livraison_ponctuelle": taux, "missions_evaluees": len(evaluables)}


@router.get("/kpi/utilisation-vehicules/{camion_id}")
def calculer_taux_utilisation_vehicules(
    camion_id: int,
    jours: int = 30,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_perm("transport.dispatch.read"))
):
    """Taux d'utilisation d'un camion : jours avec mission / jours observés"""
    from app.models.transport import Mission

    depuis = datetime.utcnow() - timedelta(days=jours)
    missions = db.query(Mission).filter(
        and_(
            Mission.camion_id == camion_id,
            Mission.date_debut_reelle >= depuis
        )
    ).all()

    jours_utilises = len({m.date_debut_reelle.date() for m in missions if m.date_debut_reelle})
    km_total = sum(float(m.distance_km or 0) for m in missions)
    taux = round((jours_utilises / jours) * 100, 2) if jours > 0 else 0

    return {
        "camion_id": camion_id,
        "periode_jours": jours,
        "missions": len(missions),
        "jours_utilises": jours_utilises,
        "distance_km_totale": round(km_total, 2),
        "taux_utilisation": taux
    }


@router.get("/kpi/variance-carburant/{vehicule_id}")
def calculer_variance_carburant(
    vehicule_id: int,
    debut_periode: date,
    fin_periode: date,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_perm("transport.dispatch.read"))
):
    """Variance carburant : consommation réelle (pleins) vs consommation_moyenne du véhicule"""
    from app.models.parc import CarburantRecord, Vehicule

    vehicule = db.query(Vehicule).filter(Vehicule.id == vehicule_id).first()
    if not vehicule:
        raise HTTPException(status_code=404, detail="Véhicule non trouvé")

    records = db.query(CarburantRecord).filter(
        and_(
            CarburantRecord.vehicule_id == vehicule_id,
            CarburantRecord.date_plein >= datetime.combine(debut_periode, datetime.min.time()),
            CarburantRecord.date_plein <= datetime.combine(fin_periode, datetime.max.time()),
            CarburantRecord.kilometrage.isnot(None)
        )
    ).order_by(CarburantRecord.kilometrage.asc()).all()

    if len(records) < 2:
        return {
            "vehicule_id": vehicule_id,
            "note": "Au moins deux pleins avec index kilométrique sont requis pour calculer la consommation"
        }

    litres_total = sum(float(r.litres or 0) for r in records)
    km_total = float(records[-1].kilometrage) - float(records[0].kilometrage)
    if km_total <= 0:
        return {"vehicule_id": vehicule_id, "note": "Index kilométrique non croissant — mesure impossible"}

    conso_reelle = round((litres_total / km_total) * 100, 2)
    conso_theorique = float(vehicule.consommation_moyenne) if vehicule.consommation_moyenne else None
    variance = round(((conso_reelle - conso_theorique) / conso_theorique) * 100, 2) if conso_theorique else None

    return {
        "vehicule_id": vehicule_id,
        "pleins": len(records),
        "litres_total": round(litres_total, 2),
        "kilometres": round(km_total, 2),
        "consommation_reelle_l_100km": conso_reelle,
        "consommation_theorique_l_100km": conso_theorique,
        "variance_pourcentage": variance
    }
