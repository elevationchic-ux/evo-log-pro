"""Utilitaires de pointage automatique lies au cycle de vie de session.

Phase 4 Tranche C :
- A la connexion (login ou 2fa/verify), si l'utilisateur est un collaborateur
  (niveau 3, department_id porte), une PointageVacation est CREEE automatiquement
  avec l'heure courante (heure_arrivee). Si un enregistrement existe DEJA ce jour,
  on ne duplique pas (idempotence).
- Le ecart (retard) est calcule par rapport au PlanningGarde du jour (quart
  -> heure de debut attendue). L'information est renvoyee au frontend comme
  notification non-bloquante (le login reussit toujours).
- POST /auth/pointer-depart enregistre l'heure de depart du MEME utilisateur
  (calcul heures_effectives).
"""
from __future__ import annotations

from datetime import date as _date, datetime
from typing import Any, Dict, Optional

from sqlalchemy.orm import Session

from app.models.chef_personnel import PlanningGarde, PointageVacation
from app.models.user import User

# Heures de debut de quart (correspondent aux commentaires du modele PlanningGarde).
_QUART_DEBUT: Dict[str, str] = {
    "JOUR": "07:00",
    "NUIT": "19:00",
    "MATIN": "06:00",
    "SOIR": "14:00",
    "STANDARD": "08:00",
}


def _hhmm_to_minutes(hhmm: str) -> int:
    """Convertit 'HH:MM' en minutes depuis minuit."""
    parts = hhmm.split(":")
    return int(parts[0]) * 60 + int(parts[1])


def auto_pointage_arrivee(db: Session, user: User) -> Optional[Dict[str, Any]]:
    """Enregistre une pointe d'arrivee automatique si pertinent.

    Retourne un dict descriptive (fonnee dans le payload de login sous
    ``pointage_info``) ou None si l'utilisateur n'est pas concerne (niveau > 3,
    pas de departement, deja pointe aujourd'hui, etc.).

    L'operation ne leve JAMAIS d'exception bloquante : un echec de pointage ne
    doit pas empecher la connexion (best-effort).
    """
    try:
        # Reserver aux collaborateurs de terrain (niveau 3) rattaches a un departement.
        level = getattr(user, "role_level", 99)
        if level != 3 or not getattr(user, "department_id", None):
            return None

        today = _date.today()
        now_dt = datetime.now()
        heure_arrivee = now_dt.strftime("%H:%M")

        # Idempotence : ne pas creer un second enregistrement si deja pointe aujourd'hui.
        existing = (
            db.query(PointageVacation)
            .filter(
                PointageVacation.employe_id == user.id,
                PointageVacation.date_pointage == today,
            )
            .first()
        )
        if existing:
            # Deja pointe — renvoyer l'info existante.
            return {
                "pointe": True,
                "deja_pointe": True,
                "heure_arrivee": existing.heure_arrivee,
                "ecart_minutes": None,
                "retard": False,
            }

        # Creer la pointe.
        pv = PointageVacation(
            company_id=user.company_id,
            employe_id=user.id,
            date_pointage=today,
            heure_arrivee=heure_arrivee,
            est_valide=True,  # Automatique, presume valide.
        )
        db.add(pv)
        db.commit()

        # Chercher le tour de garde d'aujourd'hui pour evaluer le retard.
        pg = (
            db.query(PlanningGarde)
            .filter(
                PlanningGarde.employe_id == user.id,
                PlanningGarde.date_jour == today,
            )
            .first()
        )
        ecart_minutes: Optional[int] = None
        retard = False
        if pg and pg.quart and pg.quart.upper() in _QUART_DEBUT:
            planned_start = _QUART_DEBUT[pg.quart.upper()]
            actual_min = _hhmm_to_minutes(heure_arrivee)
            planned_min = _hhmm_to_minutes(planned_start)
            ecart_minutes = actual_min - planned_min
            retard = ecart_minutes > 5  # Marge de 5 min toleree.

        return {
            "pointe": True,
            "deja_pointe": False,
            "heure_arrivee": heure_arrivee,
            "ecart_minutes": ecart_minutes,
            "retard": retard,
        }
    except Exception:
        # Ne JAMAIS bloquer la connexion pour un echec de pointage.
        db.rollback()
        return None


def pointer_depart(db: Session, user: User) -> Dict[str, Any]:
    """Enregistre l'heure de depart du utilisateur courant.

    Leve HTTPException (400) si aucune arrivee n'a ete enregistree aujourd'hui.
    """
    from fastapi import HTTPException

    today = _date.today()
    now_dt = datetime.now()
    heure_depart = now_dt.strftime("%H:%M")

    pv = (
        db.query(PointageVacation)
        .filter(
            PointageVacation.employe_id == user.id,
            PointageVacation.date_pointage == today,
        )
        .first()
    )
    if not pv:
        raise HTTPException(
            status_code=400,
            detail="Aucune pointe d'arrivee trouvee pour aujourd'hui.",
        )
    if pv.heure_depart:
        # Idempotent : deja parti, renvoyer les donnees existantes.
        return {
            "id": pv.id,
            "heure_arrivee": pv.heure_arrivee,
            "heure_depart": pv.heure_depart,
            "heures_effectives": float(pv.heures_effectives) if pv.heures_effectives else None,
        }

    # Calcul heures_effectives = (depart - arrivee) en heures (float).
    arrivee_min = _hhmm_to_minutes(pv.heure_arrivee)
    depart_min = _hhmm_to_minutes(heure_depart)
    diff = depart_min - arrivee_min
    # Gerer le cas nuit (depart < arrivee -> passe minuit).
    if diff < 0:
        diff += 24 * 60
    heures = round(diff / 60.0, 2)

    pv.heure_depart = heure_depart
    pv.heures_effectives = heures
    db.commit()
    db.refresh(pv)

    return {
        "id": pv.id,
        "heure_arrivee": pv.heure_arrivee,
        "heure_depart": pv.heure_depart,
        "heures_effectives": heures,
    }
