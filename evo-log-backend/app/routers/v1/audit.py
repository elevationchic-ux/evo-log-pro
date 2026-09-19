"""
Audit Router - Immutable Audit Trail & Forensics for EVO-LOG ERP
ISO 27001 & Statutory Accounting Compliance
"""
from fastapi import APIRouter, Depends, HTTPException, Query, Response
from sqlalchemy.orm import Session
from sqlalchemy import desc, or_
from typing import Optional, List, Dict, Any
from datetime import datetime
import io
import csv

from app.core.database import get_db
from app.models.audit import AuditLog
from app.models.user import User
from app.core.security import get_current_user

router = APIRouter()


@router.get("/logs")
def get_audit_logs(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=500),
    category: Optional[str] = None,
    action: Optional[str] = None,
    user_id: Optional[int] = None,
    search: Optional[str] = None,
    db: Session = Depends(get_db),
    identity: str = Depends(get_current_user),
):
    """Retrieve certified audit trail logs"""
    current_user = db.query(User).filter(User.id == int(identity)).first() if str(identity).isdigit() else db.query(User).filter(
        (User.username == str(identity)) | (User.email == str(identity))
    ).first()
    if not current_user or not current_user.is_active:
        raise HTTPException(status_code=401, detail="Utilisateur non authentifié.")
    query = db.query(AuditLog)
    if not current_user.is_superuser:
        query = query.outerjoin(User, AuditLog.user_id == User.id).filter(
            User.company_id == current_user.company_id
        )

    if action and action != "ALL":
        query = query.filter(AuditLog.method.ilike(f"%{action}%"))

    if search:
        s = f"%{search.strip()}%"
        query = query.filter(
            or_(
                AuditLog.url.ilike(s),
                AuditLog.client_host.ilike(s),
                AuditLog.error_message.ilike(s)
            )
        )

    total = query.count()
    logs = query.order_by(desc(AuditLog.timestamp)).offset(skip).limit(limit).all()

    items = []
    for l in logs:
        items.append({
            "id": f"AUD-{l.id}",
            "timestamp": l.timestamp.isoformat() if l.timestamp else datetime.utcnow().isoformat(),
            "user_email": str(l.user_id) if l.user_id else "Système",
            "action": f"{l.method} {l.url[:35]}" if l.method else "OPERATION",
            "category": "AUTH" if (l.url and "auth" in l.url) else ("RBAC" if (l.url and "role" in l.url) else "CONFIG"),
            "target": l.url or "API",
            "ip": l.client_host,
            "status": "SUCCESS" if (l.status_code and l.status_code < 400) else "FAILED"
        })

    return {"total": total, "items": items}


@router.get("/admin-logs")
def get_admin_logs(
    db: Session = Depends(get_db),
    identity: str = Depends(get_current_user),
):
    """Retrieve dedicated admin operations audit trail"""
    return get_audit_logs(skip=0, limit=100, db=db, identity=identity)


@router.get("/export")
def export_audit_logs(db: Session = Depends(get_db)):
    """Export audit log trail as CSV file certified for auditors and ISO 27001 inspections"""
    output = io.StringIO()
    writer = csv.writer(output, delimiter=';')
    
    # CSV Header
    writer.writerow([
        "ID_AUDIT", "DATE_HEURE_UTC", "UTILISATEUR", "TYPE_ACTION", 
        "CATEGORIE", "CIBLE_RESSOURCE", "ADRESSE_IP", "STATUT_EXECUTION"
    ])

    logs_data = get_audit_logs(skip=0, limit=500, db=db)
    items = logs_data.get("items", [])

    for item in items:
        writer.writerow([
            item.get("id"),
            item.get("timestamp"),
            item.get("user_email"),
            item.get("action"),
            item.get("category"),
            item.get("target"),
            item.get("ip"),
            item.get("status")
        ])

    csv_content = output.getvalue()
    filename = f"audit_trail_evolog_{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}.csv"

    return Response(
        content=csv_content,
        media_type="text/csv",
        headers={"Content-Disposition": f"attachment; filename={filename}"}
    )
