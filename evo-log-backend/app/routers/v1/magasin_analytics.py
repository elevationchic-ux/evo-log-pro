"""Magasin  analytics & rapports (Tranche D-A).

Routeur monte sur /api/v1/magasin. Il ne stocke rien : chaque calcul est une
agrégation réelle sur `stocks`, `mouvements_stocks`, `articles`, `commandes`,
`bandes_livraison` et `tiers`.

  * analytics/stock-turnover     rotation, couverture et valeur des sorties
  * analytics/safety-stock       stock de securite et seuil de reappro (ROP)
                                 calcules sur la variabilite reelle des sorties
  * analytics/demand-forecast    projection lineaire des sorties mensuelles
  * analytics/anomaly-detection  regles de controle (incoherences, derivations,
                                 ruptures, mouvements sans piece justificative)
  * reports/stock-valuation      valorisation du stock par axe d'analyse
  * reports/mouvement-analysis   activite du depot (types, operateurs, jours)
  * reports/client-performance   fiabilite logistique par client
  * reports/export/{csv,json}    export d'un rapport calcule a la volée

Un rapport sans donnee renvoie des lignes vides : aucune serie n'est inventee.
"""
from __future__ import annotations

import csv
import io
import json
import math
import statistics
from collections import defaultdict
from datetime import datetime, timedelta
from typing import Any, Dict, List, Optional, Tuple

from fastapi import APIRouter, Body, Depends, Query
from fastapi.responses import StreamingResponse
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.models.magasin import (
    BandeLivraison,
    Commande,
    MouvementStock,
    MouvementType,
    Stock,
)
from app.models.tiers import Tiers
from app.schemas.magasin_stock import (
    AnomalyItem,
    AnomalyResponse,
    ForecastLine,
    ForecastPoint,
    ReportResponse,
    SafetyStockLine,
    TurnoverLine,
)

router = APIRouter()


def _num(value, default: float = 0.0) -> float:
    if value is None:
        return default
    try:
        return float(value)
    except (TypeError, ValueError):
        return default


def _now() -> datetime:
    """Reference de temps naive, alignee sur les colonnes server_default=now()."""
    return datetime.utcnow()


def _debut(jours: int) -> datetime:
    return _now() - timedelta(days=jours)


def _z_score(niveau_service: float) -> float:
    """Quantile inverse de la normale centree reduite (approximation d'Acklam).

    Utilise pour traduire un niveau de service cible (0.95 -> 1.645) en facteur
    de securite. Approximation relative < 1e-3 sur [0.5, 0.999].
    """
    p = min(max(niveau_service, 0.5), 0.9999)
    a = (-3.969683028665376e01, 2.209460984245205e02, -2.759285104469687e02,
         1.383577518672690e02, -3.066479806614716e01, 2.506628277459239e00)
    b = (-5.447609879822406e01, 1.615858368580409e02, -1.556989798598866e02,
         6.680131188771972e01, -1.328068155288572e01)
    c = (-7.784894002430293e-03, -3.223964580411365e-01, -2.400758277161838e00,
         -2.549732539343734e00, 4.374664141464968e00, 2.938163982698783e00)
    d = (7.784695709041462e-03, 3.224671290700398e-01, 2.445134137142996e00,
         3.754408661907416e00)
    plow, phigh = 0.02425, 1 - 0.02425
    if p < plow:
        q = math.sqrt(-2 * math.log(p))
        return (((((c[0] * q + c[1]) * q + c[2]) * q + c[3]) * q + c[4]) * q + c[5]) / \
               ((((d[0] * q + d[1]) * q + d[2]) * q + d[3]) * q + 1)
    if p <= phigh:
        q = p - 0.5
        r = q * q
        return (((((a[0] * r + a[1]) * r + a[2]) * r + a[3]) * r + a[4]) * r + a[5]) * q / \
               (((((b[0] * r + b[1]) * r + b[2]) * r + b[3]) * r + b[4]) * r + 1)
    q = math.sqrt(-2 * math.log(1 - p))
    return -(((((c[0] * q + c[1]) * q + c[2]) * q + c[3]) * q + c[4]) * q + c[5]) / \
           ((((d[0] * q + d[1]) * q + d[2]) * q + d[3]) * q + 1)


def _stocks_filtres(
    db: Session,
    article_code: Optional[str],
    categorie: Optional[str],
    entrepot_id: Optional[int],
) -> List[Stock]:
    q = db.query(Stock).filter(Stock.is_active.is_(True))
    if article_code:
        q = q.filter(Stock.code_article == article_code)
    if categorie:
        q = q.filter(Stock.categorie == categorie)
    if entrepot_id is not None:
        q = q.filter(Stock.entrepot_id == entrepot_id)
    return q.all()


def _sorties_par_article(
    db: Session, codes: List[str], debut: datetime
) -> Dict[str, List[MouvementStock]]:
    """Mouvements de sortie reels par article sur la periode."""
    if not codes:
        return {}
    rows = (
        db.query(MouvementStock)
        .join(Stock, MouvementStock.stock_id == Stock.id)
        .filter(
            Stock.code_article.in_(codes),
            MouvementStock.type_mouvement == MouvementType.SORTIE,
            MouvementStock.date_mouvement >= debut,
        )
        .order_by(MouvementStock.date_mouvement)
        .all()
    )
    par_code: Dict[str, List[MouvementStock]] = defaultdict(list)
    code_par_stock = {s.id: s.code_article for s in db.query(Stock).filter(Stock.code_article.in_(codes)).all()}
    for mvt in rows:
        code = code_par_stock.get(mvt.stock_id)
        if code:
            par_code[code].append(mvt)
    return par_code


# ─── ROTATION DES STOCKS ─────────────────────────────────────────────────────
def _calcul_rotation(
    db: Session,
    jours: int,
    article_code: Optional[str],
    categorie: Optional[str],
    entrepot_id: Optional[int],
    limit: int,
) -> Tuple[List[dict], dict]:
    debut = _debut(jours)
    stocks = _stocks_filtres(db, article_code, categorie, entrepot_id)
    sorties = _sorties_par_article(db, [s.code_article for s in stocks], debut)

    lignes: List[TurnoverLine] = []
    for stock in stocks:
        mvts = sorties.get(stock.code_article, [])
        qte_sortie = sum(_num(m.quantite) for m in mvts)
        valeur_sortie = sum(
            _num(m.quantite) * _num(m.prix_unitaire if m.prix_unitaire is not None else stock.prix_unitaire)
            for m in mvts
        )
        dispo = _num(stock.quantite_disponible)
        if mvts:
            # Stock d'ouverture reconstitue depuis le premier mouvement de la
            # fenetre (quantite_avant) : moyenne = (ouverture + cloture) / 2.
            ouverture = _num(mvts[0].quantite_avant, dispo)
            stock_moyen = round((ouverture + dispo) / 2, 3)
        else:
            stock_moyen = dispo
        conso_jour = qte_sortie / jours if jours else 0.0
        rotation = round(qte_sortie / stock_moyen, 3) if stock_moyen > 0 else None
        lignes.append(
            TurnoverLine(
                code_article=stock.code_article,
                designation=stock.designation,
                categorie=stock.categorie,
                quantite_sortie=round(qte_sortie, 3),
                stock_actuel=round(dispo, 3),
                stock_moyen=round(stock_moyen, 3),
                taux_rotation=rotation,
                rotation_annualisee=round(rotation * 365 / jours, 2) if rotation is not None else None,
                jours_couverture=round(dispo / conso_jour, 1) if conso_jour > 0 else None,
                valeur_sortie=round(valeur_sortie, 2),
            )
        )
    lignes.sort(key=lambda l: (l.taux_rotation is None, -(l.taux_rotation or 0), l.code_article))
    total_valeur = sum(l.valeur_sortie for l in lignes)
    rot_valides = [l.taux_rotation for l in lignes if l.taux_rotation is not None]
    meta = {
        "periode_jours": jours,
        "nb_articles": len(lignes),
        "nb_articles_avec_sortie": sum(1 for l in lignes if l.quantite_sortie > 0),
        "rotation_moyenne": round(statistics.mean(rot_valides), 3) if rot_valides else None,
        "valeur_sorties": round(total_valeur, 2),
    }
    return [l.model_dump() for l in lignes[:limit]], meta


@router.get("/analytics/stock-turnover", response_model=dict)
async def turnover_get(
    jours: int = Query(90, ge=1, le=1095),
    article_code: Optional[str] = None,
    categorie: Optional[str] = None,
    entrepot_id: Optional[int] = None,
    limit: int = Query(100, ge=1, le=500),
    db: Session = Depends(get_db),
):
    lignes, meta = _calcul_rotation(db, jours, article_code, categorie, entrepot_id, limit)
    return {"items": lignes, "pending": False, **meta}


@router.post("/analytics/stock-turnover", response_model=dict)
async def turnover_post(payload: Dict[str, Any] = Body(default_factory=dict), db: Session = Depends(get_db)):
    lignes, meta = _calcul_rotation(
        db,
        int(payload.get("jours", 90)),
        payload.get("article_code"),
        payload.get("categorie"),
        payload.get("entrepot_id"),
        int(payload.get("limit", 100)),
    )
    return {"items": lignes, "pending": False, **meta}


# ─── STOCK DE SECURITE ───────────────────────────────────────────────────────
def _calcul_safety_stock(
    db: Session, jours: int, niveau_service: float, delai: float,
    article_code: Optional[str], categorie: Optional[str],
    entrepot_id: Optional[int], limit: int,
) -> Tuple[List[dict], dict]:
    debut = _debut(jours)
    stocks = _stocks_filtres(db, article_code, categorie, entrepot_id)
    sorties = _sorties_par_article(db, [s.code_article for s in stocks], debut)
    z = _z_score(niveau_service)

    lignes: List[SafetyStockLine] = []
    for stock in stocks:
        mvts = sorties.get(stock.code_article, [])
        # Serie journaliere reelle : on agregue les sorties par jour calendaire.
        par_jour: Dict[str, float] = defaultdict(float)
        for m in mvts:
            date_mvt = m.date_mouvement or debut
            par_jour[date_mvt.strftime("%Y-%m-%d")] += _num(m.quantite)
        jours_oberves = max(jours, 1)
        series = [par_jour.get((_now() - timedelta(days=i)).strftime("%Y-%m-%d"), 0.0)
                  for i in range(jours_oberves)]
        conso_moyenne = statistics.fmean(series) if series else 0.0
        sigma = statistics.pstdev(series) if len(series) > 1 else 0.0
        if conso_moyenne <= 0:
            continue  # aucun historique de sortie : pas de calcul pertinent
        securite = z * sigma * math.sqrt(delai)
        rop = conso_moyenne * delai + securite
        dispo = _num(stock.quantite_disponible)
        if dispo <= 0:
            statut = "rupture"
        elif dispo < securite:
            statut = "sous_securite"
        elif dispo < rop:
            statut = "a_reapprovisionner"
        else:
            statut = "conforme"
        lignes.append(
            SafetyStockLine(
                code_article=stock.code_article,
                designation=stock.designation,
                conso_moyenne_jour=round(conso_moyenne, 3),
                ecart_type_jour=round(sigma, 3),
                stock_securs=round(securite, 3),
                seuil_reappro=round(rop, 3),
                stock_actuel=round(dispo, 3),
                statut=statut,
            )
        )
    lignes.sort(key=lambda l: (l.stock_actuel - l.seuil_reappro))
    meta = {
        "periode_jours": jours,
        "niveau_service": niveau_service,
        "facteur_securite_z": round(z, 3),
        "delai_approvisionnement_jours": delai,
        "nb_articles_calcules": len(lignes),
        "nb_a_reapprovisionner": sum(1 for l in lignes if l.statut in ("sous_securite", "a_reapprovisionner", "rupture")),
    }
    return [l.model_dump() for l in lignes[:limit]], meta


@router.get("/analytics/safety-stock", response_model=dict)
async def safety_stock_get(
    jours: int = Query(90, ge=1, le=1095),
    niveau_service: float = Query(0.95, gt=0, lt=1),
    delai_approvisionnement_jours: float = Query(7.0, gt=0, le=365),
    article_code: Optional[str] = None,
    categorie: Optional[str] = None,
    entrepot_id: Optional[int] = None,
    limit: int = Query(100, ge=1, le=500),
    db: Session = Depends(get_db),
):
    lignes, meta = _calcul_safety_stock(
        db, jours, niveau_service, delai_approvisionnement_jours,
        article_code, categorie, entrepot_id, limit,
    )
    return {"items": lignes, "pending": False, **meta}


@router.post("/analytics/safety-stock", response_model=dict)
async def safety_stock_post(payload: Dict[str, Any] = Body(default_factory=dict), db: Session = Depends(get_db)):
    lignes, meta = _calcul_safety_stock(
        db,
        int(payload.get("jours", 90)),
        float(payload.get("niveau_service", 0.95)),
        float(payload.get("delai_approvisionnement_jours", 7.0)),
        payload.get("article_code"),
        payload.get("categorie"),
        payload.get("entrepot_id"),
        int(payload.get("limit", 100)),
    )
    return {"items": lignes, "pending": False, **meta}


# ─── PROJECTION DE DEMANDE ───────────────────────────────────────────────────
def _mois(dt: datetime) -> str:
    return dt.strftime("%Y-%m")


def _calcul_forecast(
    db: Session, jours: int, horizon: int, article_code: Optional[str],
    categorie: Optional[str], entrepot_id: Optional[int], limit: int,
) -> Tuple[List[dict], dict]:
    debut = _debut(max(jours, 365))
    stocks = _stocks_filtres(db, article_code, categorie, entrepot_id)
    sorties = _sorties_par_article(db, [s.code_article for s in stocks], debut)

    lignes: List[ForecastLine] = []
    for stock in stocks:
        mvts = sorties.get(stock.code_article, [])
        if len(mvts) < 2:
            continue
        par_mois: Dict[str, float] = defaultdict(float)
        for m in mvts:
            par_mois[_mois(m.date_mouvement or debut)] += _num(m.quantite)
        mois_ordonnes = sorted(par_mois)
        if len(mois_ordonnes) < 2:
            continue
        y = [par_mois[m] for m in mois_ordonnes]
        x = list(range(len(y)))
        n = len(y)
        mx, my = statistics.fmean(x), statistics.fmean(y)
        sxx = sum((xi - mx) ** 2 for xi in x)
        if sxx == 0:
            continue
        pente = sum((x[i] - mx) * (y[i] - my) for i in range(n)) / sxx
        intercept = my - pente * mx
        sst = sum((yi - my) ** 2 for yi in y)
        sse = sum((y[i] - (pente * x[i] + intercept)) ** 2 for i in range(n))
        r2 = 1 - sse / sst if sst > 0 else 0.0
        confiance = "haute" if (r2 >= 0.6 and n >= 4) else "moyenne" if (r2 >= 0.3 and n >= 3) else "faible"

        dernier = datetime.strptime(mois_ordonnes[-1], "%Y-%m")
        points: List[ForecastPoint] = []
        for h in range(1, horizon + 1):
            idx = len(y) - 1 + h
            valeur = max(0.0, pente * idx + intercept)
            mois_cible = _ajoute_mois(dernier, h)
            points.append(ForecastPoint(periode=mois_cible, quantite_prevue=round(valeur, 3)))
        lignes.append(
            ForecastLine(
                code_article=stock.code_article,
                designation=stock.designation,
                historique={m: round(par_mois[m], 3) for m in mois_ordonnes},
                projections=points,
                pente_mensuelle=round(pente, 3),
                confiance=confiance,
            )
        )
    lignes.sort(key=lambda l: -abs(l.pente_mensuelle))
    meta = {
        "periode_analysee_jours": max(jours, 365),
        "horizon_mois": horizon,
        "nb_articles_projetes": len(lignes),
        "methode": "moindres carres lineaires sur les sorties mensuelles reelles",
    }
    return [l.model_dump() for l in lignes[:limit]], meta


def _ajoute_mois(ref: datetime, delta: int) -> str:
    total = (ref.year * 12 + (ref.month - 1)) + delta
    return f"{total // 12:04d}-{total % 12 + 1:02d}"


@router.get("/analytics/demand-forecast", response_model=dict)
async def forecast_get(
    jours: int = Query(365, ge=1, le=1095),
    horizon: int = Query(3, ge=1, le=24),
    article_code: Optional[str] = None,
    categorie: Optional[str] = None,
    entrepot_id: Optional[int] = None,
    limit: int = Query(50, ge=1, le=500),
    db: Session = Depends(get_db),
):
    lignes, meta = _calcul_forecast(db, jours, horizon, article_code, categorie, entrepot_id, limit)
    return {"items": lignes, "pending": False, **meta}


@router.post("/analytics/demand-forecast", response_model=dict)
async def forecast_post(payload: Dict[str, Any] = Body(default_factory=dict), db: Session = Depends(get_db)):
    lignes, meta = _calcul_forecast(
        db,
        int(payload.get("jours", 365)),
        int(payload.get("horizon", 3)),
        payload.get("article_code"),
        payload.get("categorie"),
        payload.get("entrepot_id"),
        int(payload.get("limit", 50)),
    )
    return {"items": lignes, "pending": False, **meta}


# ─── DETECTION D'ANOMALIES ───────────────────────────────────────────────────
def _detecter_anomalies(db: Session, jours: int, seuil_sigma: float, limit: int) -> AnomalyResponse:
    debut = _debut(jours)
    items: List[AnomalyItem] = []
    stocks = db.query(Stock).filter(Stock.is_active.is_(True)).all()
    par_code = {s.code_article: s for s in stocks}
    mvts = (
        db.query(MouvementStock)
        .filter(MouvementStock.date_mouvement >= debut)
        .order_by(MouvementStock.date_mouvement)
        .all()
    )

    # 1) Ruptures et reserves superieures au disponible.
    for s in stocks:
        dispo = _num(s.quantite_disponible)
        if dispo < 0:
            items.append(AnomalyItem(
                niveau="critique", type_anomalie="stock_negatif",
                code_article=s.code_article, designation=s.designation,
                description="Quantite disponible negative : inventaire a regulariser.",
                valeur_constate=dispo,
            ))
        elif dispo == 0 and _num(s.quantite_minimum, 0) > 0:
            items.append(AnomalyItem(
                niveau="critique", type_anomalie="rupture",
                code_article=s.code_article, designation=s.designation,
                description="Rupture sur un article a seuil minimum defini.",
                valeur_constate=dispo,
            ))
        if dispo and _num(s.quantite_reservee) > dispo:
            items.append(AnomalyItem(
                niveau="avertissement", type_anomalie="sur_reservation",
                code_article=s.code_article, designation=s.designation,
                description="Les quantites reservees depassent le stock disponible.",
                valeur_constate=_num(s.quantite_reservee) - dispo,
            ))

    # 2) Chaine de solde incoherente + derivation statistique des sorties.
    sorties_par_article: Dict[str, List[float]] = defaultdict(list)
    soldes: Dict[int, List[MouvementStock]] = defaultdict(list)
    for m in mvts:
        soldes[m.stock_id].append(m)
    for stock_id, serie in soldes.items():
        stock = db.get(Stock, stock_id) if stock_id else None
        code = stock.code_article if stock else None
        designation = stock.designation if stock else None
        for m in serie:
            if m.quantite_avant is not None and m.quantite_apres is not None:
                attendu = _num(m.quantite_avant)
                signe = -1 if m.type_mouvement in (MouvementType.SORTIE, MouvementType.TRANSFERT) else 1
                attendu += signe * _num(m.quantite)
                if abs(attendu - _num(m.quantite_apres)) > 0.01:
                    items.append(AnomalyItem(
                        niveau="critique", type_anomalie="solde_incoherent",
                        code_article=code, designation=designation, reference=m.reference,
                        description=(
                            "Le solde apres mouvement ne correspond pas au mouvement enregistre "
                            f"(attendu {attendu}, constate {_num(m.quantite_apres)})."
                        ),
                        valeur_constate=_num(m.quantite_apres) - attendu,
                    ))
            if not m.document_reference:
                items.append(AnomalyItem(
                    niveau="information", type_anomalie="sans_justificatif",
                    code_article=code, designation=designation, reference=m.reference,
                    description="Mouvement sans piece justificative : tracabilite incomplete.",
                ))
            if m.type_mouvement == MouvementType.SORTIE and code:
                sorties_par_article[code].append(_num(m.quantite))

    for code, quantites in sorties_par_article.items():
        stock = par_code.get(code)
        if stock is None or len(quantites) < 4:
            continue
        moyenne = statistics.fmean(quantites)
        sigma = statistics.pstdev(quantites)
        if sigma <= 0:
            continue
        for m in [x for x in soldes.get(stock.id, []) if x.type_mouvement == MouvementType.SORTIE]:
            qte = _num(m.quantite)
            ecart = (qte - moyenne) / sigma
            if ecart >= seuil_sigma:
                items.append(AnomalyItem(
                    niveau="avertissement", type_anomalie="sortie_hors_norme",
                    code_article=code, designation=stock.designation if stock else None,
                    reference=m.reference,
                    description=(
                        f"Sortie de {qte} a {ecart:.1f} ecarts-type de la moyenne "
                        f"({moyenne:.1f}) : a verifier."
                    ),
                    valeur_constate=qte,
                ))

    # 3) Articles actifs sans aucun mouvement sur la periode.
    vus = {sid for sid in soldes if sid}
    pourvus = [s for s in stocks if _num(s.quantite_disponible) > 0 and s.id not in vus]
    for s in pourvus:
        items.append(AnomalyItem(
            niveau="information", type_anomalie="dormant",
            code_article=s.code_article, designation=s.designation,
            description=(
                f"Stock present mais aucun mouvement enregistre depuis {jours} jours "
                "(immobilisation possible)."
            ),
            valeur_constate=_num(s.quantite_disponible),
        ))

    ordre = {"critique": 0, "avertissement": 1, "information": 2}
    items.sort(key=lambda i: (ordre.get(i.niveau, 3), i.code_article or ""))
    return AnomalyResponse(
        items=items[:limit],
        total=len(items),
        analysed_movements=len(mvts),
        periode_jours=jours,
    )


@router.get("/analytics/anomaly-detection", response_model=AnomalyResponse)
async def anomalies_get(
    jours: int = Query(90, ge=1, le=1095),
    seuil_sigma: float = Query(3.0, gt=0, le=10),
    limit: int = Query(200, ge=1, le=1000),
    db: Session = Depends(get_db),
):
    return _detecter_anomalies(db, jours, seuil_sigma, limit)


@router.post("/analytics/anomaly-detection", response_model=AnomalyResponse)
async def anomalies_post(payload: Dict[str, Any] = Body(default_factory=dict), db: Session = Depends(get_db)):
    return _detecter_anomalies(
        db,
        int(payload.get("jours", 90)),
        float(payload.get("seuil_sigma", 3.0)),
        int(payload.get("limit", 200)),
    )


# ─── RAPPORTS ────────────────────────────────────────────────────────────────
_AXES_VALORISATION = {
    "categorie": lambda s: s.categorie or "non classe",
    "entrepot": lambda s: (s.entrepot.nom if s.entrepot else "sans entrepot"),
    "statut": None,  # resolu localement (see _rapport_valorisation)
    "article": lambda s: s.code_article,
}


def _rapport_valorisation(db: Session, group_by: str, categorie: Optional[str],
                          entrepot_id: Optional[int]) -> ReportResponse:
    axe = group_by if group_by in _AXES_VALORISATION else "categorie"
    q = db.query(Stock).filter(Stock.is_active.is_(True))
    if categorie:
        q = q.filter(Stock.categorie == categorie)
    if entrepot_id is not None:
        q = q.filter(Stock.entrepot_id == entrepot_id)
    buckets: Dict[str, dict] = {}
    for s in q.all():
        if axe == "statut":
            cle = "sous_seuil" if (s.quantite_minimum is not None
                                   and _num(s.quantite_disponible) <= _num(s.quantite_minimum)) else "conforme"
        else:
            cle = str(_AXES_VALORISATION[axe](s))
        b = buckets.setdefault(cle, {
            "axe": cle, "nb_references": 0, "quantite": 0.0,
            "valeur": 0.0, "reserve": 0.0,
        })
        b["nb_references"] += 1
        b["quantite"] += _num(s.quantite_disponible)
        b["valeur"] += _num(s.quantite_disponible) * _num(s.prix_unitaire)
        b["reserve"] += _num(s.quantite_reservee)
    lignes = sorted(buckets.values(), key=lambda r: -r["valeur"])
    for r in lignes:
        r["quantite"] = round(r["quantite"], 3)
        r["valeur"] = round(r["valeur"], 2)
        r["reserve"] = round(r["reserve"], 3)
    total_valeur = round(sum(r["valeur"] for r in lignes), 2)
    for r in lignes:
        r["poids_valeur_pct"] = round(100 * r["valeur"] / total_valeur, 2) if total_valeur else 0.0
    return ReportResponse(
        rapport="stock-valuation",
        genere_le=_now(),
        periode_jours=0,
        colonnes=["axe", "nb_references", "quantite", "reserve", "valeur", "poids_valeur_pct"],
        lignes=lignes,
        totaux={
            "valeur_totale": total_valeur,
            "nb_references": sum(r["nb_references"] for r in lignes),
            "axe_analyse": axe,
        },
        total_lignes=len(lignes),
    )


def _rapport_mouvements(db: Session, jours: int, group_by: str,
                        categorie: Optional[str]) -> ReportResponse:
    debut = _debut(jours)
    q = db.query(MouvementStock).filter(MouvementStock.date_mouvement >= debut)
    rows = q.all()
    buckets: Dict[str, dict] = {}

    def cle_de(m: MouvementStock) -> str:
        if group_by == "operateur":
            return str(m.operateur_id or "non attribue")
        if group_by == "jour":
            return (m.date_mouvement or debut).strftime("%Y-%m-%d")
        if group_by == "article":
            return m.stock.code_article if m.stock else "hors stock"
        return m.type_mouvement.value if m.type_mouvement else "inconnu"

    for m in rows:
        if categorie and (not m.stock or m.stock.categorie != categorie):
            continue
        cle = cle_de(m)
        b = buckets.setdefault(cle, {
            "axe": cle, "nb_mouvements": 0, "quantite": 0.0,
            "valeur": 0.0, "entrees": 0, "sorties": 0, "sans_piece": 0,
        })
        b["nb_mouvements"] += 1
        b["quantite"] += _num(m.quantite)
        b["valeur"] += _num(m.quantite) * _num(m.prix_unitaire)
        if m.type_mouvement == MouvementType.ENTREE:
            b["entrees"] += 1
        elif m.type_mouvement == MouvementType.SORTIE:
            b["sorties"] += 1
        if not m.document_reference:
            b["sans_piece"] += 1
    lignes = sorted(buckets.values(), key=lambda r: -r["nb_mouvements"])
    for r in lignes:
        r["quantite"] = round(r["quantite"], 3)
        r["valeur"] = round(r["valeur"], 2)
    return ReportResponse(
        rapport="mouvement-analysis",
        genere_le=_now(),
        periode_jours=jours,
        colonnes=["axe", "nb_mouvements", "entrees", "sorties", "quantite", "valeur", "sans_piece"],
        lignes=lignes,
        totaux={
            "nb_mouvements": sum(r["nb_mouvements"] for r in lignes),
            "quantite_totale": round(sum(r["quantite"] for r in lignes), 3),
            "valeur_totale": round(sum(r["valeur"] for r in lignes), 2),
            "axe_analyse": group_by,
        },
        total_lignes=len(lignes),
    )


def _rapport_clients(db: Session, jours: int, client_id: Optional[int]) -> ReportResponse:
    debut = _debut(jours)
    q = db.query(Commande).filter(Commande.date_commande >= debut)
    if client_id is not None:
        q = q.filter(Commande.client_id == client_id)
    commandes = q.all()
    par_client: Dict[int, dict] = {}
    for c in commandes:
        cle = c.client_id or 0
        b = par_client.setdefault(cle, {
            "client_id": cle, "client": None, "nb_commandes": 0, "montant_total": 0.0,
            "livrees": 0, "annulees": 0, "en_cours": 0, "livraisons": 0,
            "delai_heures": [],
        })
        b["nb_commandes"] += 1
        b["montant_total"] += _num(c.montant_total)
        statut = getattr(c.statut, "value", str(c.statut))
        if statut == "livree":
            b["livrees"] += 1
        elif statut == "annulee":
            b["annulees"] += 1
        else:
            b["en_cours"] += 1

    bandes = db.query(BandeLivraison).filter(BandeLivraison.is_active.is_(True)).all()
    for bl in bandes:
        cle = bl.client_id or 0
        if cle not in par_client:
            continue
        b = par_client[cle]
        b["livraisons"] += 1
        if bl.date_livraison and bl.date_preparation:
            heures = (bl.date_livraison - bl.date_preparation).total_seconds() / 3600
            if heures >= 0:
                b["delai_heures"].append(heures)

    lignes: List[dict] = []
    for cle, b in par_client.items():
        tiers = db.get(Tiers, cle) if cle else None
        service = b["nb_commandes"] - b["annulees"]
        lignes.append({
            "client_id": cle or None,
            "client": tiers.name if tiers else (f"client #{cle}" if cle else "sans client"),
            "code_client": tiers.code if tiers else None,
            "nb_commandes": b["nb_commandes"],
            "montant_total": round(b["montant_total"], 2),
            "commandes_livrees": b["livrees"],
            "commandes_annulees": b["annulees"],
            "commandes_en_cours": b["en_cours"],
            "nb_livraisons": b["livraisons"],
            "taux_service_pct": round(100 * b["livrees"] / service, 1) if service else 0.0,
            "delai_moyen_heures": round(statistics.fmean(b["delai_heures"]), 1) if b["delai_heures"] else None,
        })
    lignes.sort(key=lambda r: -r["montant_total"])
    return ReportResponse(
        rapport="client-performance",
        genere_le=_now(),
        periode_jours=jours,
        colonnes=["client", "code_client", "nb_commandes", "montant_total", "nb_livraisons",
                  "taux_service_pct", "delai_moyen_heures", "commandes_annulees"],
        lignes=lignes,
        totaux={
            "nb_clients": len(lignes),
            "nb_commandes": sum(r["nb_commandes"] for r in lignes),
            "montant_total": round(sum(r["montant_total"] for r in lignes), 2),
        },
        total_lignes=len(lignes),
    )


def _construire_rapport(db: Session, rapport: str, payload: Dict[str, Any]) -> ReportResponse:
    jours = int(payload.get("jours", 90))
    if rapport == "mouvement-analysis":
        return _rapport_mouvements(db, jours, str(payload.get("group_by", "type")), payload.get("categorie"))
    if rapport == "client-performance":
        client = payload.get("client_id")
        return _rapport_clients(db, jours, int(client) if client is not None else None)
    return _rapport_valorisation(
        db, str(payload.get("group_by", "categorie")),
        payload.get("categorie"), payload.get("entrepot_id"),
    )


@router.post("/reports/stock-valuation", response_model=ReportResponse)
async def report_valuation_post(payload: Dict[str, Any] = Body(default_factory=dict), db: Session = Depends(get_db)):
    return _construire_rapport(db, "stock-valuation", payload)


@router.get("/reports/stock-valuation", response_model=ReportResponse)
async def report_valuation_get(
    group_by: str = "categorie",
    categorie: Optional[str] = None,
    entrepot_id: Optional[int] = None,
    db: Session = Depends(get_db),
):
    return _construire_rapport(db, "stock-valuation", {
        "group_by": group_by, "categorie": categorie, "entrepot_id": entrepot_id,
    })


@router.post("/reports/mouvement-analysis", response_model=ReportResponse)
async def report_mouvements_post(payload: Dict[str, Any] = Body(default_factory=dict), db: Session = Depends(get_db)):
    return _construire_rapport(db, "mouvement-analysis", payload)


@router.get("/reports/mouvement-analysis", response_model=ReportResponse)
async def report_mouvements_get(
    jours: int = Query(90, ge=1, le=1095),
    group_by: str = "type",
    categorie: Optional[str] = None,
    db: Session = Depends(get_db),
):
    return _construire_rapport(db, "mouvement-analysis", {
        "jours": jours, "group_by": group_by, "categorie": categorie,
    })


@router.post("/reports/client-performance", response_model=ReportResponse)
async def report_clients_post(payload: Dict[str, Any] = Body(default_factory=dict), db: Session = Depends(get_db)):
    return _construire_rapport(db, "client-performance", payload)


@router.get("/reports/client-performance", response_model=ReportResponse)
async def report_clients_get(
    jours: int = Query(90, ge=1, le=1095),
    client_id: Optional[int] = None,
    db: Session = Depends(get_db),
):
    return _construire_rapport(db, "client-performance", {"jours": jours, "client_id": client_id})


_RAPPORTS = ("stock-valuation", "mouvement-analysis", "client-performance")


@router.post("/reports/export/json")
async def export_report_json(payload: Dict[str, Any] = Body(default_factory=dict), db: Session = Depends(get_db)):
    rapport = str(payload.pop("rapport", "stock-valuation"))
    if rapport not in _RAPPORTS:
        rapport = "stock-valuation"
    data = _construire_rapport(db, rapport, payload).model_dump()
    return StreamingResponse(
        io.BytesIO(json.dumps(data, ensure_ascii=False, default=str).encode("utf-8")),
        media_type="application/json",
        headers={"Content-Disposition": f'attachment; filename="rapport_{rapport}.json"'},
    )


@router.post("/reports/export/csv")
async def export_report_csv(payload: Dict[str, Any] = Body(default_factory=dict), db: Session = Depends(get_db)):
    rapport = str(payload.pop("rapport", "stock-valuation"))
    if rapport not in _RAPPORTS:
        rapport = "stock-valuation"
    data = _construire_rapport(db, rapport, payload)
    buffer = io.StringIO()
    writer = csv.writer(buffer, delimiter=";", lineterminator="\r\n")
    writer.writerow(data.colonnes)
    for ligne in data.lignes:
        writer.writerow([ligne.get(c, "") for c in data.colonnes])
    writer.writerow([])
    writer.writerow(["TOTAUX"])
    for cle, valeur in data.totaux.items():
        writer.writerow([cle, valeur])
    content = ("\ufeff" + buffer.getvalue()).encode("utf-8")
    return StreamingResponse(
        io.BytesIO(content),
        media_type="text/csv; charset=utf-8",
        headers={"Content-Disposition": f'attachment; filename="rapport_{rapport}.csv"'},
    )
