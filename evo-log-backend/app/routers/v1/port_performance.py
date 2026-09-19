"""
Port Performance router - manages port performance dashboard using real port models
"""
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from sqlalchemy import func, desc
from typing import Optional
from datetime import datetime, timedelta
from app.core.database import get_db
from app.core.security import get_current_user
from app.models.user import User
from app.models.port_cameroun import PortCameroun, TerminalPortuaire, EquipementPortuaire, ZonePortuaire
from app.models.conteneur_cycle import Conteneur, CycleConteneur, StatutConteneur

router = APIRouter()


@router.get("/")
async def get_port_performance(
    port_code: Optional[str] = Query(None, description="Code port: DOU, KRI, LIM, TIK"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Tableau de bord performance portuaire global"""
    query = db.query(PortCameroun).filter(PortCameroun.est_actif == True)  # noqa
    if port_code:
        query = query.filter(PortCameroun.code == port_code)

    ports = query.all()
    port_stats = []

    for port in ports:
        terminaux = db.query(TerminalPortuaire).filter(
            TerminalPortuaire.port_id == port.id,
            TerminalPortuaire.est_actif == True  # noqa
        ).all()

        terminal_ids = [t.id for t in terminaux]

        # Occupation des zones portuaires
        total_zones = db.query(func.count(ZonePortuaire.id)).filter(
            ZonePortuaire.terminal_id.in_(terminal_ids)
        ).scalar() or 0

        cap_totale = db.query(func.sum(ZonePortuaire.capacite)).filter(
            ZonePortuaire.terminal_id.in_(terminal_ids)
        ).scalar() or 0

        cap_utilisee = db.query(func.sum(ZonePortuaire.capacite_utilisee)).filter(
            ZonePortuaire.terminal_id.in_(terminal_ids)
        ).scalar() or 0

        taux_occupation = (int(cap_utilisee) / int(cap_totale) * 100) if cap_totale and cap_totale > 0 else 0.0

        # Équipements
        equip_operationnels = db.query(func.count(EquipementPortuaire.id)).filter(
            EquipementPortuaire.terminal_id.in_(terminal_ids),
            EquipementPortuaire.statut == "operationnel"
        ).scalar() or 0

        equip_maintenance = db.query(func.count(EquipementPortuaire.id)).filter(
            EquipementPortuaire.terminal_id.in_(terminal_ids),
            EquipementPortuaire.statut == "maintenance"
        ).scalar() or 0

        # Conteneurs actifs dans les terminaux de ce port
        conteneurs_en_cours = db.query(func.count(CycleConteneur.id)).filter(
            CycleConteneur.terminal_id.in_(terminal_ids),
            CycleConteneur.statut.in_([StatutConteneur.ARRIVE, StatutConteneur.STOCKE, StatutConteneur.QUAI])
        ).scalar() or 0

        port_stats.append({
            "port_id": port.id,
            "code": port.code,
            "nom": port.nom,
            "type_port": port.type_port.value if hasattr(port.type_port, "value") else str(port.type_port),
            "operateur": port.operateur,
            "nombre_terminaux": len(terminaux),
            "capacite_annuelle_tonnes": float(port.capacite_annuelle_tonnes) if port.capacite_annuelle_tonnes else None,
            "taux_occupation_pct": round(taux_occupation, 1),
            "equipements_operationnels": equip_operationnels,
            "equipements_maintenance": equip_maintenance,
            "conteneurs_en_cours": conteneurs_en_cours,
            "zones_actives": total_zones,
        })

    return {"ports": port_stats, "total_ports": len(port_stats)}


@router.get("/kpis")
async def get_port_kpis(
    port_code: Optional[str] = Query(None),
    periode_jours: int = Query(30),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """KPIs de performance portuaire"""
    depuis = datetime.utcnow() - timedelta(days=periode_jours)

    # Total conteneurs traités dans la période
    conteneurs_traites = db.query(func.count(CycleConteneur.id)).filter(
        CycleConteneur.date_arrivee_navire >= depuis
    ).scalar() or 0

    # Conteneurs sortis (terminés)
    conteneurs_sortis = db.query(func.count(CycleConteneur.id)).filter(
        CycleConteneur.date_sortie >= depuis
    ).scalar() or 0

    # Temps de cycle moyen (en heures)
    temps_cycle_moyen = db.query(func.avg(CycleConteneur.temps_cycle_heures)).filter(
        CycleConteneur.date_arrivee_navire >= depuis,
        CycleConteneur.temps_cycle_heures != None  # noqa
    ).scalar() or 0.0

    # Équipements totaux
    total_equip = db.query(func.count(EquipementPortuaire.id)).scalar() or 0
    equip_dispo = db.query(func.count(EquipementPortuaire.id)).filter(
        EquipementPortuaire.est_disponible == True  # noqa
    ).scalar() or 0

    taux_dispo_equip = (equip_dispo / total_equip * 100) if total_equip > 0 else 0.0

    # Capacité par terminal
    terminaux_stats = db.query(
        TerminalPortuaire.nom,
        TerminalPortuaire.type_terminal,
        TerminalPortuaire.capacite_teus
    ).filter(TerminalPortuaire.est_actif == True).all()  # noqa

    return {
        "periode_jours": periode_jours,
        "conteneurs_traites": conteneurs_traites,
        "conteneurs_sortis": conteneurs_sortis,
        "taux_rotation": round((conteneurs_sortis / conteneurs_traites * 100) if conteneurs_traites > 0 else 0, 1),
        "temps_cycle_moyen_heures": round(float(temps_cycle_moyen), 1),
        "taux_disponibilite_equipements_pct": round(taux_dispo_equip, 1),
        "terminaux": [
            {
                "nom": t.nom,
                "type": t.type_terminal.value if hasattr(t.type_terminal, "value") else str(t.type_terminal),
                "capacite_teus": t.capacite_teus,
            }
            for t in terminaux_stats
        ],
    }


@router.get("/terminaux")
async def get_terminaux(
    port_id: Optional[int] = Query(None),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Récupère les terminaux portuaires"""
    query = db.query(TerminalPortuaire).filter(TerminalPortuaire.est_actif == True)  # noqa
    if port_id:
        query = query.filter(TerminalPortuaire.port_id == port_id)

    terminaux = query.all()
    return {
        "total": len(terminaux),
        "data": [
            {
                "id": t.id,
                "code": t.code,
                "nom": t.nom,
                "type_terminal": t.type_terminal.value if hasattr(t.type_terminal, "value") else str(t.type_terminal),
                "operateur": t.operateur,
                "capacite_teus": t.capacite_teus,
                "superficie_ha": float(t.superficie_ha) if t.superficie_ha else None,
                "longueur_quai_m": float(t.longueur_quai_m) if t.longueur_quai_m else None,
                "nombre_grues": t.nombre_grues,
            }
            for t in terminaux
        ]
    }


@router.get("/equipements")
async def get_equipements(
    terminal_id: Optional[int] = Query(None),
    statut: Optional[str] = Query(None),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Récupère les équipements portuaires"""
    query = db.query(EquipementPortuaire)
    if terminal_id:
        query = query.filter(EquipementPortuaire.terminal_id == terminal_id)
    if statut:
        query = query.filter(EquipementPortuaire.statut == statut)

    equipements = query.all()
    return {
        "total": len(equipements),
        "data": [
            {
                "id": e.id,
                "type_equipement": e.type_equipement,
                "modele": e.modele,
                "fabricant": e.fabricant,
                "numero_serie": e.numero_serie,
                "capacite_tonnes": float(e.capacite_tonnes) if e.capacite_tonnes else None,
                "statut": e.statut,
                "est_disponible": e.est_disponible,
                "date_derniere_maintenance": e.date_derniere_maintenance.isoformat() if e.date_derniere_maintenance else None,
                "prochaine_maintenance": e.prochaine_maintenance.isoformat() if e.prochaine_maintenance else None,
            }
            for e in equipements
        ]
    }