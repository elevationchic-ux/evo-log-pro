"""Magasin  exploitation des stocks (Tranche D-A).

Deuxieme routeur metier monte sur /api/v1/magasin (chemins disjoints de
`magasin.py` et `magasin_store.py`). Il repond aux pages d'exploitation du
depot que le frontend appelle sans equivalent serveur :

  * magasins            CRUD entrepot (la table `entrepots` existait deja,
                        aucune route `magasins` n'etait exposee)
  * stocks/search       recherche enrichie (statut derive, valeur, couverture)
  * stock-statuses      repartition des seuils (rupture / bas / normal / excess)
  * history             journal des mouvements (grand livre magasin)
  * export|import CSV   industrialisation des imports de masse

Toutes les donnees viennent des tables reelles (stocks, mouvements_stocks,
entrepots, articles, tiers). Le scope multi-tenant est applique globalement par
`app.core.tenant_enforcement` ; les reponses portent `pending=False` pour que le
frontend distingue une donnee reelle du fallback « module en deploiement ».
"""
from __future__ import annotations

import csv
import io
from datetime import datetime
from typing import Dict, List, Optional

from fastapi import APIRouter, Depends, File, HTTPException, Query, UploadFile
from fastapi.responses import StreamingResponse
from sqlalchemy import case, func
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.models.magasin import Entrepot, MouvementStock, MouvementType, Stock
from app.models.tiers import Client, Tiers, TiersType
from app.schemas.magasin_stock import (
    ImportResult,
    ImportRowError,
    MagasinCreate,
    MagasinResponse,
    MagasinUpdate,
    MovementLine,
    MovementListResponse,
    StockLine,
    StockSearchResponse,
    StockStatusBucket,
    StockStatusesResponse,
)

router = APIRouter()

# Statuts derives des seuils de stock : la notion est metier mais n'est pas
# stockee en dur  elle est calculee a la lecture depuis quantite min/max.
STATUT_RUPTURE = "rupture"
STATUT_BAS = "stock_bas"
STATUT_NORMAL = "normal"
STATUT_EXCES = "excedent"
STATUT_INACTIF = "inactif"

STATUT_LIBELLES = {
    STATUT_RUPTURE: "Rupture de stock",
    STATUT_BAS: "Sous le seuil minimum",
    STATUT_NORMAL: "Normal",
    STATUT_EXCES: "Surstock",
    STATUT_INACTIF: "Article inactive",
}

# Les exports CSV sont volumineux : on garde une enveloppe binaire evitant les
# separateurs Windows/CRLF qui cassent les imports Excel/LibreOffice.
_CSV_BOM = "\ufeff"


def _num(value) -> float:
    """Numeric/Decimal/None -> float (0.0) sans lever d'exception."""
    if value is None:
        return 0.0
    try:
        return float(value)
    except (TypeError, ValueError):
        return 0.0


def _statut_stock(row: Stock) -> str:
    if row.is_active is False:
        return STATUT_INACTIF
    dispo = _num(row.quantite_disponible)
    mini = _num(row.quantite_minimum) if row.quantite_minimum is not None else None
    maxi = _num(row.quantite_maximum) if row.quantite_maximum is not None else None
    if dispo <= 0:
        return STATUT_RUPTURE
    if mini is not None and dispo <= mini:
        return STATUT_BAS
    if maxi is not None and maxi > 0 and dispo >= maxi:
        return STATUT_EXCES
    return STATUT_NORMAL


def _stock_line(row: Stock, conso_jour: Optional[float] = None) -> StockLine:
    dispo = _num(row.quantite_disponible)
    prix = _num(row.prix_unitaire)
    couverture = None
    if conso_jour and conso_jour > 0:
        couverture = round(dispo / conso_jour, 1)
    return StockLine(
        id=row.id,
        code_article=row.code_article,
        designation=row.designation,
        categorie=row.categorie,
        unite_mesure=row.unite_mesure,
        quantite_disponible=dispo,
        quantite_reservee=_num(row.quantite_reservee),
        quantite_minimum=_num(row.quantite_minimum) if row.quantite_minimum is not None else None,
        quantite_maximum=_num(row.quantite_maximum) if row.quantite_maximum is not None else None,
        prix_unitaire=prix if row.prix_unitaire is not None else None,
        valeur=round(dispo * prix, 2),
        emplacement=row.emplacement,
        entrepot_id=row.entrepot_id,
        entrepot_code=row.entrepot.code if row.entrepot else None,
        entrepot_nom=row.entrepot.nom if row.entrepot else None,
        statut=_statut_stock(row),
        couverture_jours=couverture,
        date_derniere_entree=row.date_derniere_entree,
        date_derniere_sortie=row.date_derniere_sortie,
    )


def _movement_line(mvt: MouvementStock) -> MovementLine:
    stock = mvt.stock
    return MovementLine(
        id=mvt.id,
        reference=mvt.reference,
        type_mouvement=mvt.type_mouvement.value if mvt.type_mouvement else "inconnu",
        quantite=_num(mvt.quantite),
        quantite_avant=_num(mvt.quantite_avant) if mvt.quantite_avant is not None else None,
        quantite_apres=_num(mvt.quantite_apres) if mvt.quantite_apres is not None else None,
        valeur_totale=_num(mvt.valeur_totale) if mvt.valeur_totale is not None else None,
        raison=mvt.raison,
        document_reference=mvt.document_reference,
        destination=mvt.destination,
        operateur_id=mvt.operateur_id,
        date_mouvement=mvt.date_mouvement,
        code_article=stock.code_article if stock else None,
        designation=stock.designation if stock else None,
    )


# ─── MAGASINS (ENTREPOTS) ────────────────────────────────────────────────────
@router.get("/magasins", response_model=dict)
async def list_magasins(
    skip: int = 0,
    limit: int = Query(100, le=500),
    search: Optional[str] = None,
    actif: Optional[bool] = None,
    db: Session = Depends(get_db),
):
    q = db.query(Entrepot)
    if search:
        like = f"%{search}%"
        q = q.filter(
            (Entrepot.nom.ilike(like))
            | (Entrepot.code.ilike(like))
            | (Entrepot.ville.ilike(like))
        )
    if actif is not None:
        q = q.filter(Entrepot.is_active.is_(actif))
    total = q.count()
    rows = q.order_by(Entrepot.code).offset(skip).limit(limit).all()
    return {
        "items": [MagasinResponse.model_validate(e).model_dump() for e in rows],
        "total": total,
        "pending": False,
    }


@router.post("/magasins", response_model=MagasinResponse, status_code=201)
async def create_magasin(payload: MagasinCreate, db: Session = Depends(get_db)):
    if db.query(Entrepot).filter(Entrepot.code == payload.code).first():
        raise HTTPException(status_code=400, detail="Un magasin avec ce code existe deja")
    row = Entrepot(**payload.model_dump())
    db.add(row)
    db.commit()
    db.refresh(row)
    return row


@router.get("/magasins/{entrepot_id}", response_model=MagasinResponse)
async def get_magasin(entrepot_id: int, db: Session = Depends(get_db)):
    row = db.get(Entrepot, entrepot_id)
    if not row:
        raise HTTPException(status_code=404, detail="Magasin introuvable")
    return row


@router.put("/magasins/{entrepot_id}", response_model=MagasinResponse)
async def update_magasin(entrepot_id: int, payload: MagasinUpdate, db: Session = Depends(get_db)):
    row = db.get(Entrepot, entrepot_id)
    if not row:
        raise HTTPException(status_code=404, detail="Magasin introuvable")
    data = payload.model_dump(exclude_unset=True)
    if "code" in data and data["code"] != row.code:
        clash = db.query(Entrepot).filter(Entrepot.code == data["code"]).first()
        if clash:
            raise HTTPException(status_code=400, detail="Ce code de magasin est deja utilise")
    for k, v in data.items():
        setattr(row, k, v)
    db.commit()
    db.refresh(row)
    return row


@router.delete("/magasins/{entrepot_id}", status_code=204)
async def delete_magasin(entrepot_id: int, db: Session = Depends(get_db)):
    """Suppression logique : un entrepot porte des lignes de stock."""
    row = db.get(Entrepot, entrepot_id)
    if not row:
        raise HTTPException(status_code=404, detail="Magasin introuvable")
    row.is_active = False
    db.commit()
    return None


@router.get("/magasins/{entrepot_id}/stocks", response_model=StockSearchResponse)
async def magasin_stocks(entrepot_id: int, db: Session = Depends(get_db)):
    if not db.get(Entrepot, entrepot_id):
        raise HTTPException(status_code=404, detail="Magasin introuvable")
    rows = (
        db.query(Stock)
        .filter(Stock.entrepot_id == entrepot_id, Stock.is_active.is_(True))
        .order_by(Stock.code_article)
        .all()
    )
    items = [_stock_line(r) for r in rows]
    return StockSearchResponse(
        items=items,
        total=len(items),
        valeur_totale=round(sum(i.valeur for i in items), 2),
    )


# ─── EXPLOITATION DES STOCKS ─────────────────────────────────────────────────
def _stock_query(
    db: Session,
    q: Optional[str],
    categorie: Optional[str],
    entrepot_id: Optional[int],
    statut: Optional[str],
    only_low: bool,
):
    query = db.query(Stock).filter(Stock.is_active.is_(True))
    if q:
        like = f"%{q}%"
        query = query.filter(
            (Stock.designation.ilike(like))
            | (Stock.code_article.ilike(like))
            | (Stock.categorie.ilike(like))
            | (Stock.emplacement.ilike(like))
        )
    if categorie:
        query = query.filter(Stock.categorie == categorie)
    if entrepot_id is not None:
        query = query.filter(Stock.entrepot_id == entrepot_id)
    if only_low:
        query = query.filter(Stock.quantite_minimum.isnot(None))
        query = query.filter(Stock.quantite_disponible <= Stock.quantite_minimum)
    if statut:
        # Le statut etant derive, on filtre en SQL quand c'est possible et le
        # reste en Python sur l'ensemble de l'echantillon (colonnes min/max).
        if statut == STATUT_RUPTURE:
            query = query.filter(Stock.quantite_disponible <= 0)
        elif statut == STATUT_EXCES:
            query = query.filter(
                Stock.quantite_maximum.isnot(None),
                Stock.quantite_maximum > 0,
                Stock.quantite_disponible >= Stock.quantite_maximum,
            )
    return query


@router.get("/stocks/search", response_model=StockSearchResponse)
async def search_stocks(
    q: Optional[str] = Query(None, description="Code, designation, categorie ou emplacement"),
    categorie: Optional[str] = None,
    entrepot_id: Optional[int] = None,
    statut: Optional[str] = None,
    stock_faible: bool = False,
    skip: int = 0,
    limit: int = Query(100, le=500),
    db: Session = Depends(get_db),
):
    query = _stock_query(db, q, categorie, entrepot_id, statut, stock_faible)
    if statut and statut not in (STATUT_RUPTURE, STATUT_EXCES):
        rows = query.all()
        lines = [_stock_line(r) for r in rows]
        if statut == STATUT_BAS:
            lines = [l for l in lines if l.statut == STATUT_BAS]
        elif statut == STATUT_NORMAL:
            lines = [l for l in lines if l.statut == STATUT_NORMAL]
        total = len(lines)
        page = lines[skip : skip + limit]
        return StockSearchResponse(
            items=page,
            total=total,
            valeur_totale=round(sum(l.valeur for l in page), 2),
        )
    total = query.count()
    rows = query.order_by(Stock.code_article).offset(skip).limit(limit).all()
    items = [_stock_line(r) for r in rows]
    return StockSearchResponse(
        items=items,
        total=total,
        valeur_totale=round(sum(l.valeur for l in items), 2),
    )


@router.get("/stock-statuses", response_model=StockStatusesResponse)
async def stock_statuses(db: Session = Depends(get_db)):
    rows = db.query(Stock).filter(Stock.is_active.is_(True)).all()
    buckets: Dict[str, StockStatusBucket] = {
        code: StockStatusBucket(statut=code, libelle=libelle)
        for code, libelle in STATUT_LIBELLES.items()
    }
    for row in rows:
        line = _stock_line(row)
        bucket = buckets[line.statut]
        bucket.nb_articles += 1
        bucket.valeur = round(bucket.valeur + line.valeur, 2)
    ordered = sorted(buckets.values(), key=lambda b: b.nb_articles, reverse=True)
    return StockStatusesResponse(
        statuses=[b for b in ordered if b.nb_articles],
        total_articles=len(rows),
    )


# ─── GRAND LIVRE DES MOUVEMENTS ──────────────────────────────────────────────
def _list_movements(
    db: Session,
    stock_id: Optional[int],
    code_article: Optional[str],
    type_mouvement: Optional[str],
    du: Optional[datetime],
    au: Optional[datetime],
    operateur_id: Optional[int],
    q: Optional[str],
    skip: int,
    limit: int,
) -> MovementListResponse:
    query = db.query(MouvementStock)
    if stock_id is not None:
        query = query.filter(MouvementStock.stock_id == stock_id)
    if code_article:
        query = query.join(Stock, MouvementStock.stock_id == Stock.id).filter(
            Stock.code_article == code_article
        )
    if type_mouvement:
        try:
            query = query.filter(MouvementStock.type_mouvement == MouvementType(type_mouvement))
        except ValueError:
            raise HTTPException(
                status_code=400,
                detail=f"Type de mouvement inconnu : {type_mouvement}",
            )
    if du:
        query = query.filter(MouvementStock.date_mouvement >= du)
    if au:
        query = query.filter(MouvementStock.date_mouvement <= au)
    if operateur_id is not None:
        query = query.filter(MouvementStock.operateur_id == operateur_id)
    if q:
        like = f"%{q}%"
        query = query.filter(
            (MouvementStock.reference.ilike(like))
            | (MouvementStock.document_reference.ilike(like))
            | (MouvementStock.raison.ilike(like))
            | (MouvementStock.destination.ilike(like))
        )

    total = query.count()
    # Taux agreges calcules en SQL sur toute la periode filtree, pas sur la page.
    entrees, sorties = query.with_entities(
        func.coalesce(
            func.sum(
                case(
                    (MouvementStock.type_mouvement == MouvementType.ENTREE, MouvementStock.quantite),
                    else_=0,
                )
            ),
            0,
        ),
        func.coalesce(
            func.sum(
                case(
                    (MouvementStock.type_mouvement == MouvementType.SORTIE, MouvementStock.quantite),
                    else_=0,
                )
            ),
            0,
        ),
    ).one()
    rows = (
        query.order_by(MouvementStock.date_mouvement.desc(), MouvementStock.id.desc())
        .offset(skip)
        .limit(limit)
        .all()
    )
    return MovementListResponse(
        items=[_movement_line(m) for m in rows],
        total=total,
        entrees=round(_num(entrees), 2),
        sorties=round(_num(sorties), 2),
    )


@router.get("/history", response_model=MovementListResponse)
async def stock_history(
    stock_id: Optional[int] = None,
    code_article: Optional[str] = None,
    type_mouvement: Optional[str] = None,
    du: Optional[datetime] = None,
    au: Optional[datetime] = None,
    operateur_id: Optional[int] = None,
    q: Optional[str] = None,
    skip: int = 0,
    limit: int = Query(100, le=500),
    db: Session = Depends(get_db),
):
    return _list_movements(
        db, stock_id, code_article, type_mouvement, du, au, operateur_id, q, skip, limit
    )


@router.get("/transactions", response_model=MovementListResponse)
async def stock_transactions(
    stock_id: Optional[int] = None,
    code_article: Optional[str] = None,
    type_mouvement: Optional[str] = None,
    du: Optional[datetime] = None,
    au: Optional[datetime] = None,
    operateur_id: Optional[int] = None,
    q: Optional[str] = None,
    skip: int = 0,
    limit: int = Query(100, le=500),
    db: Session = Depends(get_db),
):
    """Alias metier de /history (le frontend nomme « transactions » le journal)."""
    return _list_movements(
        db, stock_id, code_article, type_mouvement, du, au, operateur_id, q, skip, limit
    )


# ─── EXPORT CSV ──────────────────────────────────────────────────────────────
def _csv_response(nom_fichier: str, entetes: List[str], lignes: List[List]) -> StreamingResponse:
    def generator():
        buffer = io.StringIO()
        writer = csv.writer(buffer, delimiter=";", lineterminator="\r\n")
        writer.writerow(entetes)
        yield (_CSV_BOM + buffer.getvalue()).encode("utf-8")
        buffer.seek(0)
        buffer.truncate(0)
        for row in lignes:
            writer.writerow(row)
            yield buffer.getvalue().encode("utf-8")
            buffer.seek(0)
            buffer.truncate(0)

    headers = {
        "Content-Disposition": f'attachment; filename="{nom_fichier}"',
        "Cache-Control": "no-store",
    }
    return StreamingResponse(
        generator(), media_type="text/csv; charset=utf-8", headers=headers
    )


_EXPORTERS: Dict[str, callable] = {}


def _export_articles(db: Session):
    from app.models.magasin import Article

    rows = db.query(Article).order_by(Article.code).all()
    entetes = [
        "code", "designation", "categorie", "unite_mesure", "prix_unitaire",
        "poids_kg", "volume_m3", "code_barres", "hs_code", "actif",
    ]
    lignes = [
        [
            a.code, a.designation, a.categorie or "", a.unite_mesure or "",
            _num(a.prix_unitaire), _num(a.poids_kg), _num(a.volume_m3),
            a.code_barres or "", a.hs_code or "",
            "OUI" if a.is_active else "NON",
        ]
        for a in rows
    ]
    return entetes, lignes


def _export_magasins(db: Session):
    rows = db.query(Entrepot).order_by(Entrepot.code).all()
    entetes = [
        "code", "nom", "ville", "adresse", "telephone", "responsable",
        "capacite", "superficie", "actif",
    ]
    lignes = [
        [
            e.code, e.nom, e.ville or "", e.adresse or "", e.telephone or "",
            e.responsable or "", _num(e.capacite), _num(e.superficie),
            "OUI" if e.is_active else "NON",
        ]
        for e in rows
    ]
    return entetes, lignes


def _export_clients(db: Session):
    rows = (
        db.query(Tiers).filter(Tiers.type == TiersType.CLIENT).order_by(Tiers.code).all()
    )
    entetes = [
        "code", "nom", "contact", "email", "telephone", "ville", "pays",
        "numero_contribuable", "encours", "limite_credit", "actif",
    ]
    lignes = [
        [
            t.code, t.name, t.contact_person or "", t.email or "", t.phone or "",
            t.city or "", t.country or "", t.tax_id or "", _num(t.balance),
            _num(t.credit_limit), "OUI" if t.is_active else "NON",
        ]
        for t in rows
    ]
    return entetes, lignes


def _export_stocks(db: Session):
    rows = db.query(Stock).order_by(Stock.code_article).all()
    entetes = [
        "code_article", "designation", "categorie", "unite_mesure",
        "quantite_disponible", "quantite_reservee", "quantite_minimum",
        "quantite_maximum", "prix_unitaire", "valeur", "statut", "entrepot",
        "emplacement",
    ]
    lignes = []
    for s in rows:
        line = _stock_line(s)
        lignes.append([
            line.code_article, line.designation, line.categorie or "",
            line.unite_mesure or "", line.quantite_disponible,
            line.quantite_reservee, line.quantite_minimum or "",
            line.quantite_maximum or "", line.prix_unitaire or "",
            line.valeur, line.statut, line.entrepot_code or "",
            line.emplacement or "",
        ])
    return entetes, lignes


_EXPORTERS.update({
    "articles": _export_articles,
    "clients": _export_clients,
    "magasins": _export_magasins,
    "entrepots": _export_magasins,
    "stocks": _export_stocks,
})


@router.get("/export/{resource}/csv")
async def export_csv(resource: str, db: Session = Depends(get_db)):
    exporter = _EXPORTERS.get(resource)
    if not exporter:
        raise HTTPException(
            status_code=404,
            detail=f"Export CSV indisponible pour '{resource}'. "
                   f"Ressources supportees : {', '.join(sorted(set(_EXPORTERS)))}.",
        )
    entetes, lignes = exporter(db)
    return _csv_response(f"{resource}_{datetime.now().strftime('%Y%m%d')}.csv", entetes, lignes)


# ─── IMPORT CSV ──────────────────────────────────────────────────────────────
async def _read_csv(file: UploadFile) -> List[Dict[str, str]]:
    raw = await file.read()
    if not raw:
        raise HTTPException(status_code=400, detail="Fichier CSV vide")
    text = raw.decode("utf-8-sig", errors="replace")
    sample = text[:4096]
    try:
        delimiter = csv.Sniffer().sniff(sample, delimiters=",;\t").delimiter
    except csv.Error:
        delimiter = ";" if sample.count(";") > sample.count(",") else ","
    reader = csv.DictReader(io.StringIO(text), delimiter=delimiter)
    if not reader.fieldnames:
        raise HTTPException(status_code=400, detail="En-tete CSV introuvable")
    reader.fieldnames = [(f or "").strip().lower() for f in reader.fieldnames]
    return [row for row in reader]


def _clean(value: Optional[str]) -> str:
    return (value or "").strip()


def _to_float(value: Optional[str]) -> Optional[float]:
    txt = _clean(value).replace(" ", "").replace("\u00a0", "")
    if not txt:
        return None
    # Format FR "1 234,56"  suppression du separateur de milliers puis de la virgule.
    txt = txt.replace(".", "").replace(",", ".") if "," in txt else txt
    try:
        return float(txt)
    except ValueError:
        raise ValueError(f"Valeur numerique invalide : {value!r}")


def _finish_import(db: Session, result: ImportResult, dry_run: bool) -> ImportResult:
    """Valide l'import : ecrit reellement, ou simule sans rien laisser en base.

    Un IntegrityError (code deja pris par un autre tenant, contrainte unique
    globale sur tiers.code ...) annule tout le lot et est rendu explicitement :
    aucun faux succes n'est renvoye.
    """
    if dry_run:
        db.rollback()
        return result
    try:
        db.commit()
    except IntegrityError as exc:
        db.rollback()
        result.erreurs.append(
            ImportRowError(
                ligne=0,
                message=(
                    "Import annule (conflit d'integrite en base) : "
                    f"{str(getattr(exc, 'orig', exc))[:200]}"
                ),
            )
        )
        result.cree = 0
        result.mis_a_jour = 0
        result.ignore = result.lu
    return result


def _upsert_articles(db: Session, rows: List[Dict[str, str]], dry_run: bool) -> ImportResult:
    from app.models.magasin import Article

    result = ImportResult(resource="articles", lu=len(rows), dry_run=dry_run)
    for index, row in enumerate(rows, start=2):
        code = _clean(row.get("code"))
        designation = _clean(row.get("designation"))
        if not code or not designation:
            result.erreurs.append(
                ImportRowError(ligne=index, message="colonnes 'code' et 'designation' obligatoires")
            )
            continue
        try:
            prix = _to_float(row.get("prix_unitaire"))
        except ValueError as exc:
            result.erreurs.append(ImportRowError(ligne=index, message=str(exc)))
            continue
        existing = db.query(Article).filter(Article.code == code).first()
        if existing:
            existing.designation = designation
            if row.get("categorie") is not None:
                existing.categorie = _clean(row.get("categorie")) or None
            if row.get("unite_mesure") is not None:
                existing.unite_mesure = _clean(row.get("unite_mesure")) or None
            if prix is not None:
                existing.prix_unitaire = prix
            result.mis_a_jour += 1
        elif not dry_run:
            db.add(
                Article(
                    code=code,
                    designation=designation,
                    categorie=_clean(row.get("categorie")) or None,
                    unite_mesure=_clean(row.get("unite_mesure")) or None,
                    prix_unitaire=prix,
                    code_barres=_clean(row.get("code_barres")) or None,
                )
            )
            result.cree += 1
        else:
            result.cree += 1
    return _finish_import(db, result, dry_run)


def _upsert_magasins(db: Session, rows: List[Dict[str, str]], dry_run: bool) -> ImportResult:
    result = ImportResult(resource="magasins", lu=len(rows), dry_run=dry_run)
    for index, row in enumerate(rows, start=2):
        code = _clean(row.get("code"))
        nom = _clean(row.get("nom"))
        if not code or not nom:
            result.erreurs.append(
                ImportRowError(ligne=index, message="colonnes 'code' et 'nom' obligatoires")
            )
            continue
        try:
            capacite = _to_float(row.get("capacite"))
            superficie = _to_float(row.get("superficie"))
        except ValueError as exc:
            result.erreurs.append(ImportRowError(ligne=index, message=str(exc)))
            continue
        existing = db.query(Entrepot).filter(Entrepot.code == code).first()
        if existing:
            existing.nom = nom
            existing.ville = _clean(row.get("ville")) or existing.ville
            existing.adresse = _clean(row.get("adresse")) or existing.adresse
            existing.telephone = _clean(row.get("telephone")) or existing.telephone
            existing.responsable = _clean(row.get("responsable")) or existing.responsable
            if capacite is not None:
                existing.capacite = capacite
            if superficie is not None:
                existing.superficie = superficie
            result.mis_a_jour += 1
        elif not dry_run:
            db.add(
                Entrepot(
                    code=code,
                    nom=nom,
                    ville=_clean(row.get("ville")) or None,
                    adresse=_clean(row.get("adresse")) or None,
                    telephone=_clean(row.get("telephone")) or None,
                    responsable=_clean(row.get("responsable")) or None,
                    capacite=capacite,
                    superficie=superficie,
                )
            )
            result.cree += 1
        else:
            result.cree += 1
    return _finish_import(db, result, dry_run)


def _upsert_clients(db: Session, rows: List[Dict[str, str]], dry_run: bool) -> ImportResult:
    result = ImportResult(resource="clients", lu=len(rows), dry_run=dry_run)
    for index, row in enumerate(rows, start=2):
        code = _clean(row.get("code"))
        nom = _clean(row.get("nom")) or _clean(row.get("name"))
        if not code or not nom:
            result.erreurs.append(
                ImportRowError(ligne=index, message="colonnes 'code' et 'nom' obligatoires")
            )
            continue
        try:
            encours = _to_float(row.get("encours") or row.get("balance"))
            limite = _to_float(row.get("limite_credit") or row.get("credit_limit"))
        except ValueError as exc:
            result.erreurs.append(ImportRowError(ligne=index, message=str(exc)))
            continue
        existing = db.query(Tiers).filter(Tiers.code == code).first()
        if existing and existing.type != TiersType.CLIENT:
            # Le code designe deja un fournisseur/partenaires : on n'ecrase pas
            # l'identite du tiers, l'operateur doit choisir un autre code.
            result.erreurs.append(
                ImportRowError(
                    ligne=index,
                    message=f"'{code}' existe deja comme {getattr(existing.type, 'value', existing.type)}",
                )
            )
            continue
        if existing:
            existing.name = nom
            existing.email = _clean(row.get("email")) or existing.email
            existing.phone = _clean(row.get("telephone") or row.get("phone")) or existing.phone
            existing.city = _clean(row.get("ville") or row.get("city")) or existing.city
            existing.contact_person = (
                _clean(row.get("contact")) or existing.contact_person
            )
            existing.tax_id = _clean(row.get("numero_contribuable")) or existing.tax_id
            if encours is not None:
                existing.balance = int(encours)
            if limite is not None:
                existing.credit_limit = int(limite)
            result.mis_a_jour += 1
        elif not dry_run:
            db.add(
                Client(
                    code=code,
                    name=nom,
                    email=_clean(row.get("email")) or None,
                    phone=_clean(row.get("telephone") or row.get("phone")) or None,
                    city=_clean(row.get("ville") or row.get("city")) or None,
                    contact_person=_clean(row.get("contact")) or None,
                    tax_id=_clean(row.get("numero_contribuable")) or None,
                    balance=int(encours or 0),
                    credit_limit=int(limite or 0),
                )
            )
            result.cree += 1
        else:
            result.cree += 1
    return _finish_import(db, result, dry_run)


_IMPORTERS = {
    "articles": _upsert_articles,
    "clients": _upsert_clients,
    "magasins": _upsert_magasins,
    "entrepots": _upsert_magasins,
}


@router.post("/import/{resource}", response_model=ImportResult)
async def import_csv(
    resource: str,
    file: UploadFile = File(...),
    dry_run: bool = Query(False, description="Valider sans ecrire en base"),
    db: Session = Depends(get_db),
):
    importer = _IMPORTERS.get(resource)
    if not importer:
        raise HTTPException(
            status_code=404,
            detail=f"Import indisponible pour '{resource}'. "
                   f"Ressources supportees : {', '.join(sorted(set(_IMPORTERS)))}.",
        )
    rows = await _read_csv(file)
    return importer(db, rows, dry_run)


@router.get("/import/{resource}/template")
async def import_template(resource: str):
    """Modele CSV telechargeable (en-tetes attendus par l'import)."""
    templates = {
        "articles": ["code", "designation", "categorie", "unite_mesure", "prix_unitaire", "code_barres"],
        "clients": ["code", "nom", "contact", "email", "telephone", "ville", "numero_contribuable", "limite_credit"],
        "magasins": ["code", "nom", "ville", "adresse", "telephone", "responsable", "capacite", "superficie"],
    }
    entetes = templates.get(resource)
    if not entetes:
        raise HTTPException(status_code=404, detail="Ressource inconnue")
    return _csv_response(f"modele_import_{resource}.csv", entetes, [])
