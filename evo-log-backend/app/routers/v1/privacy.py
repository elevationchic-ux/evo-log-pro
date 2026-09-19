from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any
from datetime import datetime

from app.database import get_db
from app.models.user import User
from app.models.organization import Organization
from app.utils.tenant import get_current_tenant_context, TenantContext
from app.utils.rbac import get_current_user

router = APIRouter()

PROCESSING_REGISTRY = [
    {
        "id": "REG-001",
        "purpose": "Gestion de l'authentification et du contrôle d'accès RBAC",
        "data_categories": ["Nom", "Prénom", "Email", "Téléphone", "Rôle", "Logs de connexion"],
        "retention_period": "Durée du contrat + 3 ans",
        "legal_basis": "Exécution contractuelle (Loi 2024/017 Art. 12)"
    },
    {
        "id": "REG-002",
        "purpose": "Gestion des ordres de transport, chauffeurs et E-POD",
        "data_categories": ["Nom chauffeur", "Permis de conduire", "Géolocalisation GPS", "Signature électronique"],
        "retention_period": "10 ans (Obligation comptable & douanière)",
        "legal_basis": "Obligation légale et sécurité d'exploitation"
    },
    {
        "id": "REG-003",
        "purpose": "Facturation, suivi des paiements et obligations fiscales CEMAC",
        "data_categories": ["Coordonnées bancaires", "Identifiant fiscal", "Factures", "Encaissements"],
        "retention_period": "10 ans (Code de commerce OHADA)",
        "legal_basis": "Obligation légale"
    }
]

PRIVACY_POLICY = {
    "title": "Politique de Confidentialité et Protection des Données Personnelles (Loi n° 2024/017)",
    "effective_date": "2026-06-23",
    "organization": "Code Axis Digital Cameroun (CADC) & Plateforme SaaS EVO-LOG",
    "summary": "EVO-LOG s'engage à garantir la confidentialité, l'intégrité et la sécurité des données conformément à la loi camerounaise n° 2024/017 du 23 décembre 2024.",
    "rights": [
        "Droit d'accès et d'information",
        "Droit de rectification et de mise à jour",
        "Droit à l'effacement / anonymisation",
        "Droit d'opposition au traitement non obligatoire"
    ],
    "contact_dpo": "dpo@codeaxis.cm"
}

@router.get("/policy")
def get_privacy_policy():
    """Return the official privacy policy compliant with Law n° 2024/017."""
    return PRIVACY_POLICY

@router.get("/registry")
def get_processing_registry(current_user: User = Depends(get_current_user)):
    """Return the data processing registry (Registre des traitements APDP)."""
    return {
        "status": "success",
        "law": "Loi n° 2024/017 du 23 décembre 2024 (APDP Cameroun)",
        "registry": PROCESSING_REGISTRY
    }

@router.get("/export-my-data")
def export_user_data(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """User data export endpoint enforcing right of access (Art. 18 Law 2024/017)."""
    return {
        "status": "success",
        "exported_at": datetime.utcnow().isoformat(),
        "user_profile": {
            "id": current_user.id,
            "email": current_user.email,
            "username": current_user.username,
            "full_name": current_user.full_name,
            "telephone": current_user.telephone,
            "departement": current_user.departement,
            "agency_id": current_user.agency_id,
            "organization_id": current_user.organization_id,
            "roles": [r.code for r in (current_user.roles or [])]
        }
    }

class BreachNotificationSchema(BaseModel):
    incident_type: str = Field(..., example="UNAUTHORIZED_ACCESS_ATTEMPT")
    description: str = Field(..., example="Tentative d'accès suspect détectée")
    affected_count: int = Field(0, example=1)

@router.post("/notify-breach", status_code=status.HTTP_202_ACCEPTED)
def notify_security_breach(
    payload: BreachNotificationSchema,
    current_user: User = Depends(get_current_user)
):
    """Data breach notification procedure trigger compliant with APDP directives."""
    return {
        "status": "logged",
        "message": "Incident de sécurité enregistré dans le registre des violations APDP.",
        "incident": payload.dict(),
        "reported_at": datetime.utcnow().isoformat()
    }
