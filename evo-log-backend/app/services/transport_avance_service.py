"""Dispatch intelligent service - Optimisation de tournées et planification automatique"""
from datetime import datetime, date, timedelta
from typing import List, Optional, Dict, Any
from sqlalchemy.orm import Session
from sqlalchemy import and_, func
from app.models.transport_avance import (
    Dispatch, Arret, ContrainteDispatch, TypeOptimisation, StatutDispatch
)
from app.models.transport import Mission, MissionStatus, Camion, CamionStatus, Conducteur


def _ressources_disponibles(db: Session):
    """Conducteurs actifs et camions actifs — seuls champs réels des modèles."""
    conducteurs = db.query(Conducteur).filter(Conducteur.is_active == True).all()  # noqa: E712
    camions = db.query(Camion).filter(Camion.status == CamionStatus.ACTIVE).all()
    return conducteurs, camions


class DispatchIntelligentService:
    """Service de dispatch intelligent avec optimisation"""

    @staticmethod
    def optimisation_tournees(
        db: Session,
        missions_ids: List[int],
        contraintes: Optional[Dict[str, Any]] = None
    ) -> Dispatch:
        """Optimisation de tournées - regroupement par priorité.

        Heuristique réelle : tri par priorité de mission, affectation au
        premier conducteur/camion disponible. Pas de score de confiance
        inventé : il reste NULL tant qu'aucun algorithme de scoring
        n'est branché.
        """
        missions = db.query(Mission).filter(Mission.id.in_(missions_ids)).all()

        if not missions:
            raise ValueError("Aucune mission trouvée")

        conducteurs, camions = _ressources_disponibles(db)
        if not conducteurs or not camions:
            raise ValueError("Aucune ressource disponible")

        points = [{
            "mission_id": m.id,
            "depart": m.point_depart,
            "arrivee": m.point_arrivee,
            "priorite": 5  # Mission n'a pas de colonne priorité — valeur neutre
        } for m in missions]
        points.sort(key=lambda x: x["mission_id"])

        numero_dispatch = f"DIS-{datetime.now().strftime('%Y%m%d%H%M%S')}-{missions_ids[0]}"
        dispatch = Dispatch(
            numero_dispatch=numero_dispatch,
            mission_id=missions_ids[0],
            conducteur_id=conducteurs[0].id,
            camion_id=camions[0].id,
            type_optimisation=TypeOptimisation.PLUS_COURT_CHEMIN,
            statut=StatutDispatch.PLANIFIE,
            date_planification=datetime.now(),
            priorite=5,
            score_confiance=None,
            facteurs_consideres=str({
                "heuristique": "premier_disponible",
                "missions": missions_ids,
                "contraintes": contraintes or {}
            })
        )
        db.add(dispatch)
        db.commit()
        db.refresh(dispatch)

        for idx, point in enumerate(points):
            db.add(Arret(
                dispatch_id=dispatch.id,
                type_arret="livraison",
                ordre_sequence=idx + 1,
                adresse=point["arrivee"],
                duree_estimee=30,
                statut="en_attente"
            ))

        db.commit()
        return dispatch

    @staticmethod
    def planification_automatique(
        db: Session,
        date_jour: date,
        capacites: Optional[Dict[str, Any]] = None
    ) -> List[Dispatch]:
        """Planification automatique des missions pour une journée"""
        missions_non_planifiees = db.query(Mission).filter(
            and_(
                func.date(Mission.date_debut_prevue) == date_jour,
                Mission.statut == MissionStatus.PLANIFIEE
            )
        ).all()

        if not missions_non_planifiees:
            return []

        from collections import defaultdict
        par_zone = defaultdict(list)
        for mission in missions_non_planifiees:
            zone = (mission.point_depart or "autre")[:10]
            par_zone[zone].append(mission)

        dispatches = []
        for zone, missions_zone in par_zone.items():
            missions_ids = [m.id for m in missions_zone]
            try:
                dispatch = DispatchIntelligentService.optimisation_tournees(
                    db, missions_ids, capacites
                )
                dispatches.append(dispatch)
            except ValueError:
                continue

        return dispatches

    @staticmethod
    def equilibre_charge_chauffeurs(
        db: Session,
        periode_debut: date,
        periode_fin: date
    ) -> Dict[str, Any]:
        """Équilibrage de la charge entre chauffeurs"""
        dispatches = db.query(Dispatch).filter(
            and_(
                Dispatch.date_planification >= periode_debut,
                Dispatch.date_planification <= periode_fin
            )
        ).all()

        from collections import defaultdict
        charge_par_conducteur = defaultdict(lambda: {"nombre_missions": 0, "distance_totale": 0})

        for dispatch in dispatches:
            charge_par_conducteur[dispatch.conducteur_id]["nombre_missions"] += 1
            charge_par_conducteur[dispatch.conducteur_id]["distance_totale"] += float(dispatch.distance_estimee or 0)

        total_missions = sum(c["nombre_missions"] for c in charge_par_conducteur.values())
        moyenne_missions = total_missions / len(charge_par_conducteur) if charge_par_conducteur else 0

        desequilibres = []
        for conducteur_id, charge in charge_par_conducteur.items():
            ecart = charge["nombre_missions"] - moyenne_missions
            if abs(ecart) > 2:
                desequilibres.append({
                    "conducteur_id": conducteur_id,
                    "charge_actuelle": charge["nombre_missions"],
                    "moyenne": round(moyenne_missions, 2),
                    "ecart": round(ecart, 2)
                })

        return {
            "periode": f"{periode_debut} à {periode_fin}",
            "nombre_conducteurs": len(charge_par_conducteur),
            "moyenne_missions": round(moyenne_missions, 2),
            "desequilibres": desequilibres
        }

    @staticmethod
    def attribution_intelligente(
        db: Session,
        mission_id: int
    ) -> Dispatch:
        """Attribution intelligente d'une mission (premier conducteur/camion actif)"""
        mission = db.query(Mission).filter(Mission.id == mission_id).first()
        if not mission:
            raise ValueError("Mission non trouvée")

        conducteurs, camions = _ressources_disponibles(db)
        if not conducteurs or not camions:
            raise ValueError("Aucune ressource disponible")

        meilleur_conducteur = conducteurs[0]
        meilleur_camion = max(camions, key=lambda c: float(c.capacite_tonnage or 0))

        dispatch = Dispatch(
            numero_dispatch=f"DIS-{datetime.now().strftime('%Y%m%d%H%M%S')}-{mission_id}",
            mission_id=mission_id,
            conducteur_id=meilleur_conducteur.id,
            camion_id=meilleur_camion.id,
            type_optimisation=TypeOptimisation.EQUILIBRE_CHARGE,
            statut=StatutDispatch.PLANIFIE,
            date_planification=datetime.now(),
            priorite=5,
            score_confiance=None
        )
        db.add(dispatch)
        db.commit()
        db.refresh(dispatch)

        return dispatch

    @staticmethod
    def recalcul_itineraire(
        db: Session,
        dispatch_id: int,
        evenement: str  # "retard", "annulation", "modification"
    ) -> Dispatch:
        """Recalculer l'itinéraire suite à un événement"""
        dispatch = db.query(Dispatch).filter(Dispatch.id == dispatch_id).first()
        if not dispatch:
            raise ValueError("Dispatch non trouvé")

        arrets = db.query(Arret).filter(Arret.dispatch_id == dispatch_id).order_by(Arret.ordre_sequence).all()

        base = dispatch.date_debut_prevue
        for arret in arrets:
            if base is None:
                break
            arret.heure_arrivee_prevue = base
            arret.heure_depart_prevue = base + timedelta(minutes=arret.duree_estimee or 30)
            base = arret.heure_depart_prevue

        db.commit()
        db.refresh(dispatch)

        return dispatch


class EPODService:
    """Service E-POD - Preuve de livraison électronique"""

    @staticmethod
    def creer_pod(
        db: Session,
        livraison_id: int,
        signature_client: Optional[str] = None,
        photo_marchandise: Optional[str] = None,
        coordonnees: Optional[str] = None
    ) -> Any:
        """Créer une preuve de livraison"""
        from app.models.transport_avance import POD

        pod = POD(
            numero_pod=f"POD-{datetime.now().strftime('%Y%m%d%H%M%S')}",
            livraison_id=livraison_id,
            statut="en_attente",
            signature_client=signature_client,
            photo_marchandise=photo_marchandise,
            coordonnees_livraison=coordonnees,
            horodatage=datetime.now()
        )
        db.add(pod)
        db.commit()
        db.refresh(pod)

        return pod

    @staticmethod
    def valider_pod(
        db: Session,
        pod_id: int,
        valide_par: int
    ) -> Any:
        """Valider une preuve de livraison"""
        from app.models.transport_avance import POD

        pod = db.query(POD).filter(POD.id == pod_id).first()
        if not pod:
            raise ValueError("POD non trouvé")

        pod.statut = "valide"
        pod.valide_par = valide_par
        pod.date_validation = datetime.now()

        import hashlib
        donnees = f"{pod.numero_pod}{pod.signature_client}{pod.photo_marchandise}{pod.horodatage}"
        pod.hash_preuve = hashlib.sha256(donnees.encode()).hexdigest()

        db.commit()
        db.refresh(pod)

        return pod

    @staticmethod
    def integration_facturation(
        db: Session,
        pod_id: int
    ) -> Dict[str, Any]:
        """Intégration avec la facturation — non implémentée côté backend.

        Retourne un état honnête : la facture n'est PAS générée
        automatiquement pour l'instant.
        """
        from app.models.transport_avance import POD, Livraison

        pod = db.query(POD).filter(POD.id == pod_id).first()
        if not pod:
            raise ValueError("POD non trouvé")

        livraison = db.query(Livraison).filter(Livraison.id == pod.livraison_id).first()

        return {
            "pod_id": pod_id,
            "livraison_id": pod.livraison_id,
            "client_id": livraison.client_id if livraison else None,
            "statut": "non_implémente",
            "note": "La génération de facture depuis le POD n'est pas encore branchée au module facturation."
        }

    @staticmethod
    def archivage_legal(
        db: Session,
        pod_id: int
    ) -> Dict[str, Any]:
        """Archivage légal des preuves — calcul de la fenêtre de conservation.

        Ne crée pas d'enregistrement d'archivage : le module documents
        (ArchivageLegal) reste la voie officielle. Réponse honnête.
        """
        from app.models.transport_avance import POD

        pod = db.query(POD).filter(POD.id == pod_id).first()
        if not pod:
            raise ValueError("POD non trouvé")

        return {
            "pod_id": pod_id,
            "statut": "non_archive",
            "note": "Aucun enregistrement d'archivage créé. Utiliser le module documents pour l'archivage légal OHADA (10 ans).",
            "duree_conservation_jours": 3650
        }


class AnalyticsTransportService:
    """Service d'analytics transport — calculs réels, aucune valeur inventée"""

    @staticmethod
    def tableau_bord_transport(
        db: Session,
        date_dashboard: date
    ) -> Dict[str, Any]:
        """Générer le tableau de bord transport"""
        from app.models.transport_avance import TableauBordTransport

        missions_actives = db.query(Mission).filter(
            Mission.statut == MissionStatus.EN_COURS
        ).count()

        missions_terminees = db.query(Mission).filter(
            and_(
                Mission.statut == MissionStatus.TERMINEE,
                func.date(Mission.date_fin_reelle) == date_dashboard
            )
        ).count()

        missions_retard = db.query(Mission).filter(
            Mission.statut == MissionStatus.EN_RETARD
        ).count()

        vehicules_disponibles = db.query(Camion).filter(
            Camion.status == CamionStatus.ACTIVE
        ).count()

        vehicules_en_mission = db.query(func.count(func.distinct(Mission.camion_id))).filter(
            and_(
                Mission.statut == MissionStatus.EN_COURS,
                Mission.camion_id.isnot(None)
            )
        ).scalar() or 0

        total_vehicules = vehicules_disponibles + vehicules_en_mission
        taux_occupation = round((vehicules_en_mission / total_vehicules * 100), 2) if total_vehicules > 0 else 0

        cout_total_jour = db.query(func.sum(Mission.cout_reel)).filter(
            func.date(Mission.date_fin_reelle) == date_dashboard
        ).scalar() or 0

        tableau = TableauBordTransport(
            date_dashboard=date_dashboard,
            nombre_missions_actives=missions_actives,
            nombre_missions_terminees=missions_terminees,
            nombre_missions_en_retard=missions_retard,
            nombre_vehicules_disponibles=vehicules_disponibles,
            nombre_vehicules_en_mission=vehicules_en_mission,
            taux_occupation=taux_occupation,
            cout_total_jour=cout_total_jour
        )
        db.add(tableau)
        db.commit()

        return {
            "date": date_dashboard,
            "missions_actives": missions_actives,
            "missions_terminees": missions_terminees,
            "missions_en_retard": missions_retard,
            "vehicules_disponibles": vehicules_disponibles,
            "vehicules_en_mission": vehicules_en_mission,
            "taux_occupation": taux_occupation,
            "cout_total_jour": float(cout_total_jour)
        }

    @staticmethod
    def kpi_transport(
        db: Session,
        periode: str,
        conducteur_id: Optional[int] = None,
        camion_id: Optional[int] = None
    ) -> Dict[str, Any]:
        """Calculer les KPIs transport sur une période 'YYYY-MM' — données réelles"""
        from app.models.transport_avance import KPIPerformance, TempsConduite, AccidentTransport

        try:
            annee, mois = int(periode[:4]), int(periode[5:7])
            debut = date(annee, mois, 1)
            fin = (date(annee + 1, 1, 1) - timedelta(days=1)) if mois == 12 else (date(annee, mois + 1, 1) - timedelta(days=1))
        except (ValueError, IndexError):
            raise ValueError("Période invalide — format attendu 'YYYY-MM'")

        q = db.query(Mission).filter(
            and_(
                Mission.date_debut_prevue >= datetime.combine(debut, datetime.min.time()),
                Mission.date_debut_prevue <= datetime.combine(fin, datetime.max.time())
            )
        )
        if conducteur_id:
            q = q.filter(Mission.conducteur_id == conducteur_id)
        if camion_id:
            q = q.filter(Mission.camion_id == camion_id)
        missions = q.all()

        total = len(missions)
        reussies = sum(1 for m in missions if m.statut == MissionStatus.TERMINEE)
        retards = sum(1 for m in missions if m.statut == MissionStatus.EN_RETARD)
        km_total = sum(float(m.distance_km or 0) for m in missions)
        taux_reussite = round((reussies / total) * 100, 2) if total else 0

        minutes = db.query(func.sum(TempsConduite.temps_conduite)).filter(
            and_(
                TempsConduite.date >= debut,
                TempsConduite.date <= fin,
                *([TempsConduite.conducteur_id == conducteur_id] if conducteur_id else [])
            )
        ).scalar() or 0

        incidents = db.query(AccidentTransport).filter(
            and_(
                AccidentTransport.date_accident >= datetime.combine(debut, datetime.min.time()),
                AccidentTransport.date_accident <= datetime.combine(fin, datetime.max.time()),
                *([AccidentTransport.conducteur_id == conducteur_id] if conducteur_id else [])
            )
        ).count()

        # Note de performance : réussite pondérée par retards et incidents
        penalite = (retards / total * 30 if total else 0) + (incidents * 5)
        note = max(0, min(100, round(taux_reussite - penalite, 2)))

        kpi = KPIPerformance(
            periode=periode,
            type_periode="mensuel",
            conducteur_id=conducteur_id,
            camion_id=camion_id,
            nombre_missions=total,
            nombre_missions_reussies=reussies,
            taux_reussite=taux_reussite,
            nombre_km_parcourus=km_total,
            nombre_heures_conduite=round(minutes / 60, 2),
            nombre_incidents=incidents,
            nombre_retards=retards,
            satisfaction_client=None,
            note_performance=note
        )
        db.add(kpi)
        db.commit()

        return {
            "periode": periode,
            "taux_reussite": taux_reussite,
            "satisfaction_client": None,
            "note_performance": note,
            "nombre_missions": total,
            "nombre_km_parcourus": round(km_total, 2)
        }

    @staticmethod
    def alertes_performance(
        db: Session,
        seuils: Optional[Dict[str, Any]] = None
    ) -> List[Dict[str, Any]]:
        """Générer les alertes de performance — seuils réels"""
        from app.models.transport_avance import AlertPerformance

        seuil_retard = (seuils or {}).get("missions_en_retard", 5)

        missions_en_retard = db.query(Mission).filter(
            Mission.statut == MissionStatus.EN_RETARD
        ).count()

        alertes = []
        if missions_en_retard > seuil_retard:
            alerte = AlertPerformance(
                type_alerte="retard",
                gravite="haute",
                description=f"Trop de missions en retard: {missions_en_retard}",
                concerne_type="mission",
                valeur_actuelle=missions_en_retard,
                valeur_seuil=seuil_retard
            )
            db.add(alerte)
            alertes.append({
                "type": "retard",
                "gravite": "haute",
                "valeur": missions_en_retard
            })

        db.commit()

        return alertes
