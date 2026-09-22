from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from pydantic import BaseModel, Field
from typing import List, Optional
from datetime import datetime

from app.database import get_db
from app.utils.tenant import get_current_tenant_context, TenantContext
from app.models.transport import Conducteur, Mission

router = APIRouter()

@router.get("/driver-scores")
def get_driver_gamification_scores(context: TenantContext = Depends(get_current_tenant_context), db: Session = Depends(get_db)):
    """Retrieve driver eco-driving, safety scores, and earned badges."""
    try:
        # Get all drivers for the tenant
        drivers = db.query(Conducteur).filter(
            Conducteur.company_id == context.organization_id
        ).all()

        leaderboard = []
        for driver in drivers:
            # Calculate scores based on missions
            missions = db.query(Mission).filter(
                Mission.company_id == context.organization_id,
                Mission.conducteur_id == driver.id
            ).all()

            completed_missions = len([m for m in missions if m.statut == 'TERMINEE'])
            total_missions = len(missions)

            # Calculate eco-driving score (based on completion rate)
            eco_score = min(100, (completed_missions / total_missions * 100) if total_missions > 0 else 50)

            # Calculate safety score (based on no incidents - simulated)
            safety_score = min(100, eco_score + 10) if eco_score > 80 else eco_score

            # Determine badges
            badges = []
            if completed_missions >= 50:
                badges.append({"name": "Veteran", "icon": "🏆"})
            if completed_missions >= 100:
                badges.append({"name": "Elite", "icon": "⭐"})
            if safety_score >= 90:
                badges.append({"name": "Safe Driver", "icon": "🛡️"})

            leaderboard.append({
                "driver_id": driver.id,
                "driver_name": driver.nom,
                "eco_score": round(eco_score, 1),
                "safety_score": round(safety_score, 1),
                "completed_missions": completed_missions,
                "badges": badges,
                "rank": 0  # Will be calculated after sorting
            })

        # Sort by eco_score and assign ranks
        leaderboard.sort(key=lambda x: x['eco_score'], reverse=True)
        for idx, entry in enumerate(leaderboard, 1):
            entry['rank'] = idx

        return {
            "status": "success",
            "organization_id": context.organization_id,
            "leaderboard": leaderboard[:10]  # Top 10
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erreur lors de la récupération des scores: {str(e)}")
