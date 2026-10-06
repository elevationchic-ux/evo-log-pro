from datetime import datetime, timedelta

from fastapi import APIRouter, Depends
from sqlalchemy import func
from sqlalchemy.orm import Session

from app.database import get_db
from app.utils.tenant import get_current_tenant_context, TenantContext, require_module_access
from app.models.transport import Mission
from app.models.parc import Vehicule, CarburantRecord
from app.models.finance import Facture, FactureStatus

router = APIRouter()


def _company_id(context: TenantContext):
    return getattr(context.user, "company_id", None)


@router.get("/forecast-demand", dependencies=[Depends(require_module_access("bi"))])
def forecast_transport_demand(
    context: TenantContext = Depends(get_current_tenant_context),
    db: Session = Depends(get_db),
):
    """Prevision de demande transport CALCULEE sur l'historique reel des missions
    (moyenne mobile + tendance lineaire par mois). Methode statistique, pas de ML
    entraine ; si l'historique est insuffisant, la prevision est prudemment nulle."""
    cid = _company_id(context)
    depuis = datetime.utcnow() - timedelta(days=365)
    q = db.query(
        func.strftime("%Y-%m", Mission.date_debut_prevue).label("mois"),
        func.count(Mission.id).label("n"),
    ).filter(Mission.date_debut_prevue >= depuis)
    if cid is not None:
        q = q.filter(Mission.company_id == cid)
    rows = q.group_by("mois").order_by("mois").all()
    series = [{"mois": m, "missions": int(n)} for m, n in rows if m]
    valeurs = [s["missions"] for s in series]

    moyenne = (sum(valeurs) / len(valeurs)) if valeurs else 0.0
    prevision_prochain = None
    if len(valeurs) >= 3:
        # tendance lineaire simple (moindres carres) extrapolee d'un pas
        n = len(valeurs)
        xs = list(range(n))
        xm = sum(xs) / n
        ym = moyenne
        denom = sum((x - xm) ** 2 for x in xs) or 1.0
        pente = sum((xs[i] - xm) * (valeurs[i] - ym) for i in range(n)) / denom
        prevision_prochain = max(0, round(ym + pente * (n - xm)))
    return {
        "historique": series,
        "points": len(series),
        "moyenne_mensuelle_reelle": round(moyenne, 2),
        "prevision_prochain_mois": prevision_prochain,
        "methode": "moyenne + tendance lineaire sur missions reelles",
        "base_suffisante": len(valeurs) >= 3,
    }


@router.get("/fuel-anomalies", dependencies=[Depends(require_module_access("fuelguard"))])
def detect_fuel_anomalies(
    context: TenantContext = Depends(get_current_tenant_context),
    db: Session = Depends(get_db),
):
    """Detection d'anomalies carburant sur les TICKETS REELS (CarburantRecord) :
    plein superieur a la capacite du reservoir, prix au litre aberrant vs mediane,
    incoherence cout/litres. Aucune telemetrie inventee : seulement ce qui est saisi."""
    cid = _company_id(context)
    q = db.query(CarburantRecord)
    if cid is not None:
        q = q.filter(CarburantRecord.company_id == cid)
    records = q.all()

    # mediane des prix au litre observes
    prix = sorted(float(r.prix_litre) for r in records if r.prix_litre)
    mediane = (prix[len(prix) // 2] if prix else 0.0)
    capacites = {
        v.id: float(v.capacite_reservoir or 0)
        for v in db.query(Vehicule).all()
    }

    anomalies = []
    for r in records:
        litres = float(r.litres or 0)
        raisons = []
        cap = capacites.get(r.vehicule_id, 0)
        if cap and litres > cap:
            raisons.append(f"litres ({litres}) > capacite reservoir ({cap})")
        if mediane and r.prix_litre:
            p = float(r.prix_litre)
            if p > mediane * 1.5 or p < mediane * 0.5:
                raisons.append(f"prix/litre {p} aberrant vs mediane {mediane}")
        if r.cout and r.litres and r.prix_litre:
            attendu = float(r.litres) * float(r.prix_litre)
            if attendu and abs(float(r.cout) - attendu) / attendu > 0.10:
                raisons.append(f"cout {float(r.cout)} incoherent avec litres*prix ({attendu:.0f})")
        if raisons:
            anomalies.append({
                "record_id": r.id,
                "vehicule_id": r.vehicule_id,
                "immatriculation": r.immatriculation,
                "date_plein": r.date_plein.isoformat() if r.date_plein else None,
                "raisons": raisons,
            })

    return {
        "tickets_analyses": len(records),
        "mediane_prix_litre": round(mediane, 2),
        "anomalies": anomalies,
        "source_reelle": True,
        "note:telemetrie": "Capteurs embarques non branches ; analyse basee sur les tickets saisis.",
    }


@router.get("/client-risk-score/{client_id}", dependencies=[Depends(require_module_access("finance"))])
def evaluate_client_risk_score(
    client_id: int,
    context: TenantContext = Depends(get_current_tenant_context),
    db: Session = Depends(get_db),
):
    """Score de risque credit CALCULE depuis les factures/reglements reels du
    client (part echue + anciennete du retard). Aucune constante fabriquee."""
    today = datetime.utcnow().date()
    q = db.query(Facture).filter(Facture.client_id == client_id)
    cid = _company_id(context)
    if cid is not None:
        q = q.filter(Facture.company_id == cid)
    factures = q.all()

    if not factures:
        return {"client_id": client_id, "score": None, "motif": "Aucune facture pour ce client"}

    due_statuses = [FactureStatus.EMISE, FactureStatus.RETARD, FactureStatus.PAYEE_PARTIELLEMENT]
    total = len(factures)
    echues = [f for f in factures if f.statut in due_statuses and f.date_echeance and f.date_echeance < today]
    montant_du = sum(float(f.montant_ttc or 0) for f in factures if f.statut in due_statuses)
    montant_echue = sum(float(f.montant_ttc or 0) for f in echues)
    max_jours_retard = max(
        ((today - f.date_echeance).days for f in echues), default=0
    )

    part_echue = (len(echues) / total) if total else 0.0
    # score 0-100 : 60 % poids sur la part echue, 40 % sur l'anciennete (plafonnee 90 j)
    anciennete = min(max_jours_retard / 90.0, 1.0)
    score = round((0.6 * part_echue + 0.4 * anciennete) * 100)

    if score < 30:
        niveau = "FAIBLE"
    elif score < 60:
        niveau = "MOYEN"
    else:
        niveau = "ELEVE"

    return {
        "client_id": client_id,
        "factures_total": total,
        "factures_echues": len(echues),
        "montant_du_xaf": round(montant_du, 2),
        "montant_echue_xaf": round(montant_echue, 2),
        "max_jours_retard": max_jours_retard,
        "score": score,
        "niveau_risque": niveau,
        "calcule_depuis_registres_reels": True,
    }
