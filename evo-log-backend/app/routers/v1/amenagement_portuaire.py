"""Routeur du departement Amenagement portuaire (Douala, Kribi, Limbe).

Ce que fait cette API : tenir le registre des actes d'amenagement du domaine
portuaire — schemas directeurs, programmation (DTO), marches/PPP, titres
domaniaux, concessions, ouvrages, dragages, autorisations environnementales.

Ce qu'elle ne fait PAS (conscience du projet, see docs/RBAC_ACCREDITATIONS.md) :
  * elle ne teletransmet rien au MINMIVT, au MINEPF, a la COLIFE, au MINEPPT ni
    a l'APN : ces actes appartiennent a des systemes externes qui n'existent
    pas ici. Les routes correspondantes repondent 501 (jamais un faux succes) ;
  * elle n'invente aucune valeur : montant, date ou reference non saisi reste
    NULL et s'affiche « non enregistre » cote frontend ;
  * elle ne durcit aucun tarif, aucune capacite ni aucun nom d'operateur : les
    referentiels viennent des tables ports_cameroun / terminaux_portuaires /
    zones_portuaires, alimentees par les agents.

Donnees nationales non scopees par tenant : les objets decrivent le domaine
public camerounais (comme ports_cameroun). L'acces est donc purgene par le RBAC
granulaire (``amenagement.<sous-module>.<action>``) et non par company_id.
"""
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy import func, or_
from sqlalchemy.orm import Session
from typing import Any, Dict, List, Optional

import json
from datetime import date, timedelta

from app.core.database import get_db
from app.core.not_implemented import not_implemented
from app.core.permissions import require_perm
from app.models.user import User
from app.models.port_cameroun import PortCameroun
from app.models.amenagement_portuaire import (
    SchemaDirecteur, ProjetAmenagement, RegistreDTO, MarcheAmenagement,
    AutorisationDomaniale, ConcessionPortuaire, InfrastructurePortuaire,
    Dragage, AutorisationTravaux,
    TypeSchema, StatutSchema, TypeProjet, StatutProjet, OrigineFinancement,
    TypeMarche, CodeMarche, StatutMarche, TypeTitreDomanial,
    TypeContratExploitation, StatutContrat, TypeInfrastructure,
    EtatInfrastructure, TypeDragage, TypeAutorisationTravaux, StatutAutorisation,
)
from app.schemas.amenagement_portuaire import (
    SchemaDirecteurCreate, SchemaDirecteurUpdate, SchemaDirecteurOut,
    ProjetAmenagementCreate, ProjetAmenagementUpdate, ProjetAmenagementOut,
    RegistreDTOCreate, RegistreDTOUpdate, RegistreDTOOut,
    MarcheAmenagementCreate, MarcheAmenagementUpdate, MarcheAmenagementOut,
    AutorisationDomanialeCreate, AutorisationDomanialeUpdate, AutorisationDomanialeOut,
    ConcessionPortuaireCreate, ConcessionPortuaireUpdate, ConcessionPortuaireOut,
    InfrastructurePortuaireCreate, InfrastructurePortuaireUpdate, InfrastructurePortuaireOut,
    DragageCreate, DragageUpdate, DragageOut,
    AutorisationTravauxCreate, AutorisationTravauxUpdate, AutorisationTravauxOut,
)

router = APIRouter(tags=["Amenagement portuaire"])

# Perimetre d'etude du departement : les trois places a grand gabarit dont la
# tutelle d'amenagement est concernee. Ce n'est PAS une donnee metier — c'est
# un filtre applique aux lignes reellement presentes dans ports_cameroun. Une
# place absente de la table (ou inactive) n'apparait simplement pas.
PLACES_DU_DEPARTEMENT = ("DOU", "KRI", "LIM")

# Champs serialises en JSON dans des colonnes Text (les listes restent des
# listes cote client, jamais des chaines brutes).
_JSON_FIELDS = {
    "zones_prevues", "lignes_directrices", "documents_sources",
    "origines_financement", "risques", "prolongations", "sources_documents",
}


# ─── Utilitaires ─────────────────────────────────────────────────────────────

def _load_json(value: Any) -> Any:
    if value is None:
        return None
    if isinstance(value, (list, dict)):
        return value
    try:
        return json.loads(value)
    except (TypeError, ValueError):
        return None


def _dump_json(value: Any) -> Optional[str]:
    if value is None:
        return None
    if isinstance(value, str):
        value = value.strip()
        if not value:
            return None
    return json.dumps(value, ensure_ascii=False)


def _to_out(obj: Any):
    """Normalise les colonnes JSON Text avant validation Pydantic."""
    for field in _JSON_FIELDS:
        if hasattr(obj, field):
            try:
                setattr(obj, field, _load_json(getattr(obj, field)))
            except (TypeError, ValueError):
                pass
    return obj


def _apply(payload: Dict[str, Any], obj: Any, *, create: bool) -> None:
    """Affecte uniquement les champs fournis : rien n'est completé d'office.

    ``create`` n'autorise aucune valeur par defaut metier : il sert seulement a
    garder l'appel explicite (les listes JSON sont sérialisées à l'identique
    dans les deux cas).
    """
    for key, value in payload.items():
        if key not in _JSON_FIELDS:
            setattr(obj, key, value)
            continue
        setattr(obj, key, _dump_json(value))


def _get_or_404(db: Session, model, ident: int, label: str):
    row = db.query(model).filter(model.id == ident).first()
    if not row:
        raise HTTPException(status_code=404, detail=f"{label} introuvable (id={ident})")
    return row


def _check_unique(db: Session, model, field: str, value: Any, label: str,
                  exclude_id: Optional[int] = None) -> None:
    """Reference metier unique : evite deux lignes pour un meme arrete ou DTO."""
    if value is None:
        return
    q = db.query(model).filter(getattr(model, field) == value)
    if exclude_id is not None:
        q = q.filter(model.id != exclude_id)
    if q.first():
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=f"{label} « {value} » existe deja — corrigez la reference au lieu d'en creer une seconde.",
        )


def _enum_catalog(model) -> List[Dict[str, str]]:
    return [{"code": m.name, "valeur": m.value} for m in model]


def _dans_un_an(ref: date) -> date:
    """Horizon glissant 12 mois (365 jours) — borne de veille, pas une duree contractuelle."""
    return ref + timedelta(days=365)


# ─── 0. Nomenclatures & perimetre ────────────────────────────────────────────

@router.get("/nomenclatures", summary="Vocabulaire metier du departement")
def nomenclatures(user: User = Depends(require_perm("amenagement.projet.read"))):
    """Enums reels du circuit camerounais (aucune valeur inventee, aucun defaut metier)."""
    return {
        "type_schema": _enum_catalog(TypeSchema),
        "statut_schema": _enum_catalog(StatutSchema),
        "type_projet": _enum_catalog(TypeProjet),
        "statut_projet": _enum_catalog(StatutProjet),
        "origine_financement": _enum_catalog(OrigineFinancement),
        "type_marche": _enum_catalog(TypeMarche),
        "code_marche": _enum_catalog(CodeMarche),
        "statut_marche": _enum_catalog(StatutMarche),
        "type_titre_domanial": _enum_catalog(TypeTitreDomanial),
        "type_contrat": _enum_catalog(TypeContratExploitation),
        "statut_contrat": _enum_catalog(StatutContrat),
        "type_infrastructure": _enum_catalog(TypeInfrastructure),
        "etat_infrastructure": _enum_catalog(EtatInfrastructure),
        "type_dragage": _enum_catalog(TypeDragage),
        "type_autorisation_travaux": _enum_catalog(TypeAutorisationTravaux),
        "statut_autorisation": _enum_catalog(StatutAutorisation),
    }


@router.get("/places", summary="Places portuaires couvertes, telles qu'en base")
def lister_places(
    db: Session = Depends(get_db),
    user: User = Depends(require_perm("amenagement.projet.read")),
):
    """Douala / Kribi / Limbe depuis ``ports_cameroun`` (aucun nom code en dur).

    Si une place n'est pas encore enregistree dans le referentiel national,
    elle n'est pas inventee : la reponse la simplement omet.
    """
    rows = (
        db.query(PortCameroun)
        .filter(or_(PortCameroun.code.in_(PLACES_DU_DEPARTEMENT),
                    PortCameroun.autorite_portuaire.isnot(None)))
        .order_by(PortCameroun.code)
        .all()
    )
    return {
        "data": [
            {
                "id": p.id,
                "code": p.code,
                "nom": p.nom,
                "ville": p.ville,
                "region": p.region,
                "autorite_portuaire": p.autorite_portuaire,
                "tirant_eau_max": float(p.tirant_eau_max) if p.tirant_eau_max is not None else None,
                "profondeur_m": float(p.profondeur_m) if p.profondeur_m is not None else None,
                "est_actif": bool(p.est_actif),
            }
            for p in rows
        ],
        "total": len(rows),
        "note": (
            "Donnees issues du referentiel national des ports. Un champ NULL "
            "signifie que l'information n'a pas encore ete saisie depuis un "
            "document officiel."
        ),
    }


# ─── 1. Schémas directeurs ───────────────────────────────────────────────────

@router.get("/schemas-directeurs", response_model=List[SchemaDirecteurOut],
            summary="Consulter les schemas directeurs d'amenagement")
def lister_schemas(
    statut: Optional[StatutSchema] = None,
    port_id: Optional[int] = Query(None),
    db: Session = Depends(get_db),
    user: User = Depends(require_perm("amenagement.schema_directeur.read")),
):
    q = db.query(SchemaDirecteur).filter(SchemaDirecteur.est_actif.is_(True))
    if statut:
        q = q.filter(SchemaDirecteur.statut == statut)
    if port_id:
        q = q.filter(SchemaDirecteur.port_id == port_id)
    return [_to_out(s) for s in q.order_by(SchemaDirecteur.horizon_debut.desc().nullslast()).all()]


@router.post("/schemas-directeurs", response_model=SchemaDirecteurOut,
             status_code=status.HTTP_201_CREATED,
             summary="Enregistrer un schema directeur")
def creer_schema(
    payload: SchemaDirecteurCreate,
    db: Session = Depends(get_db),
    user: User = Depends(require_perm("amenagement.schema_directeur.create")),
):
    _check_unique(db, SchemaDirecteur, "code", payload.code, "Code de schema directeur")
    data = payload.model_dump(exclude_unset=True)
    obj = SchemaDirecteur()
    _apply(data, obj, create=True)
    obj.auteur_saisie = obj.auteur_saisie or getattr(user, "username", None) or getattr(user, "email", None)
    db.add(obj)
    db.commit()
    db.refresh(obj)
    return _to_out(obj)


@router.get("/schemas-directeurs/{ident}", response_model=SchemaDirecteurOut,
            summary="Detail d'un schema directeur")
def detail_schema(
    ident: int,
    db: Session = Depends(get_db),
    user: User = Depends(require_perm("amenagement.schema_directeur.read")),
):
    return _to_out(_get_or_404(db, SchemaDirecteur, ident, "Schema directeur"))


@router.put("/schemas-directeurs/{ident}", response_model=SchemaDirecteurOut,
            summary="Modifier un schema directeur")
def modifier_schema(
    ident: int,
    payload: SchemaDirecteurUpdate,
    db: Session = Depends(get_db),
    user: User = Depends(require_perm("amenagement.schema_directeur.modify")),
):
    obj = _get_or_404(db, SchemaDirecteur, ident, "Schema directeur")
    _apply(payload.model_dump(exclude_unset=True), obj, create=False)
    db.commit()
    db.refresh(obj)
    return _to_out(obj)


@router.post("/schemas-directeurs/{ident}/approbation", response_model=SchemaDirecteurOut,
             summary="Attester l'approbation officielle d'un schema")
def approuver_schema(
    ident: int,
    reference_approbatrice: str = Query(..., min_length=2,
                                        description="Numero reel du decret/arrete approbatif"),
    date_approbation: date = Query(..., description="Date d'approbation officielle"),
    db: Session = Depends(get_db),
    user: User = Depends(require_perm("amenagement.schema_directeur.approve")),
):
    """N'APPROUVE RIEN : enregistre l'acte pris par le gouvernement.

    Le departement ne peut pas approuver un schema directeur a la place du
    MINMIVT. Cette route saisit la reference et la date de l'arrete reel ; la
    valeur« approuve » n'est pas supposee, elle derive du document cite.
    """
    obj = _get_or_404(db, SchemaDirecteur, ident, "Schema directeur")
    obj.reference_approbatrice = reference_approbatrice
    obj.date_approbation = date_approbation
    obj.statut = StatutSchema.APPROUVE
    obj.date_verification = date.today()
    obj.auteur_saisie = getattr(user, "username", None) or obj.auteur_saisie
    db.commit()
    db.refresh(obj)
    return _to_out(obj)


@router.post("/schemas-directeurs/{ident}/demande-visa-minmivt",
             summary="Transmission du schema pour visa ministeriel (501)")
def demande_visa_schema(ident: int, user: User = Depends(require_perm("amenagement.schema_directeur.approve"))):
    """Teleprocedures MINMIVT/APN inexistantes cote serveur (501 explicite)."""
    not_implemented(
        "Transmission dematerialisee d'un schema directeur au MINMIVT / APN",
        "un connecteur officiel avec l'Autorite Portuaire Nationale et le "
        "ministere en charge des Ports (aucun depot automatique n'existe au "
        "Cameroun pour ces pieces)",
    )


# ─── 2. Projets d'aménagement ────────────────────────────────────────────────

@router.get("/projets", response_model=List[ProjetAmenagementOut],
            summary="Portefeuille de projets d'amenagement")
def lister_projets(
    statut: Optional[StatutProjet] = None,
    port_id: Optional[int] = Query(None),
    type_ouvrage: Optional[TypeProjet] = None,
    db: Session = Depends(get_db),
    user: User = Depends(require_perm("amenagement.projet.read")),
):
    q = db.query(ProjetAmenagement).filter(ProjetAmenagement.est_actif.is_(True))
    if statut:
        q = q.filter(ProjetAmenagement.statut == statut)
    if port_id:
        q = q.filter(ProjetAmenagement.port_id == port_id)
    if type_ouvrage:
        q = q.filter(ProjetAmenagement.type_ouvrage == type_ouvrage)
    return [_to_out(p) for p in q.order_by(ProjetAmenagement.code_projet).all()]


@router.post("/projets", response_model=ProjetAmenagementOut,
             status_code=status.HTTP_201_CREATED, summary="Inscrire un projet d'amenagement")
def creer_projet(
    payload: ProjetAmenagementCreate,
    db: Session = Depends(get_db),
    user: User = Depends(require_perm("amenagement.projet.create")),
):
    _check_unique(db, ProjetAmenagement, "code_projet", payload.code_projet, "Code de projet")
    data = payload.model_dump(exclude_unset=True)
    obj = ProjetAmenagement()
    _apply(data, obj, create=True)
    obj.auteur_saisie = obj.auteur_saisie or getattr(user, "username", None) or getattr(user, "email", None)
    db.add(obj)
    db.commit()
    db.refresh(obj)
    return _to_out(obj)


@router.get("/projets/{ident}", response_model=ProjetAmenagementOut,
            summary="Detail d'un projet")
def detail_projet(
    ident: int,
    db: Session = Depends(get_db),
    user: User = Depends(require_perm("amenagement.projet.read")),
):
    return _to_out(_get_or_404(db, ProjetAmenagement, ident, "Projet d'amenagement"))


@router.put("/projets/{ident}", response_model=ProjetAmenagementOut,
            summary="Mettre a jour un projet")
def modifier_projet(
    ident: int,
    payload: ProjetAmenagementUpdate,
    db: Session = Depends(get_db),
    user: User = Depends(require_perm("amenagement.projet.modify")),
):
    obj = _get_or_404(db, ProjetAmenagement, ident, "Projet d'amenagement")
    _apply(payload.model_dump(exclude_unset=True), obj, create=False)
    db.commit()
    db.refresh(obj)
    return _to_out(obj)


@router.delete("/projets/{ident}", status_code=status.HTTP_200_OK,
               summary="Retirer un projet de la programmation")
def desactiver_projet(
    ident: int,
    motif: str = Query(..., min_length=3, description="Motif retire (abandon, repositionnement...)"),
    db: Session = Depends(get_db),
    user: User = Depends(require_perm("amenagement.projet.delete")),
):
    """Retrait declaratif : la ligne reste, le projet sort du portefeuille."""
    obj = _get_or_404(db, ProjetAmenagement, ident, "Projet d'amenagement")
    obj.est_actif = False
    obj.statut = StatutProjet.ABANDONNE
    obj.notes = (obj.notes + "\n" if obj.notes else "") + f"Retire : {motif}"
    db.commit()
    return {"id": obj.id, "code_projet": obj.code_projet, "statut": obj.statut,
            "message": "Projet retire de la programmation (motif enregistre)."}


@router.post("/projets/{ident}/avancement", response_model=ProjetAmenagementOut,
             summary="Saisir un releve d'avancement physique/financier")
def saisir_avancement(
    ident: int,
    avancement_physique_pct: Optional[float] = Query(None, ge=0, le=100),
    avancement_financier_pct: Optional[float] = Query(None, ge=0, le=100),
    date_releve: Optional[date] = Query(None, description="Date du releve (jamais today implicite)"),
    source_reference: Optional[str] = Query(None, description="PV de chantier, decompte..."),
    db: Session = Depends(get_db),
    user: User = Depends(require_perm("amenagement.projet.modify")),
):
    """Enregistre un releve ; un pourcentage absent reste NULL, pas 0 %.

    L'avancement n'est jamais calcule par le logiciel : il provient d'un
    decompte ou d'un PV signe. Sans releve, l'affichage dit « non mesure ».
    """
    obj = _get_or_404(db, ProjetAmenagement, ident, "Projet d'amenagement")
    if avancement_physique_pct is not None:
        obj.avancement_physique_pct = avancement_physique_pct
    if avancement_financier_pct is not None:
        obj.avancement_financier_pct = avancement_financier_pct
    if source_reference:
        obj.source_reference = source_reference
    if date_releve:
        obj.date_verification = date_releve
    obj.auteur_saisie = getattr(user, "username", None) or obj.auteur_saisie
    db.commit()
    db.refresh(obj)
    return _to_out(obj)


# ─── 3. Programmation budgétaire (DTO) ───────────────────────────────────────

@router.get("/dto", response_model=List[RegistreDTOOut], summary="Registre des DTO")
def lister_dto(
    exercice: Optional[int] = Query(None),
    statut: Optional[str] = Query(None),
    db: Session = Depends(get_db),
    user: User = Depends(require_perm("amenagement.dto.read")),
):
    q = db.query(RegistreDTO)
    if exercice:
        q = q.filter(RegistreDTO.exercice == exercice)
    if statut:
        q = q.filter(RegistreDTO.statut == statut.upper())
    return [_to_out(d) for d in q.order_by(RegistreDTO.exercice.desc(), RegistreDTO.reference_dto).all()]


@router.post("/dto", response_model=RegistreDTOOut, status_code=status.HTTP_201_CREATED,
             summary="Inscrire une ligne DTO")
def creer_dto(
    payload: RegistreDTOCreate,
    db: Session = Depends(get_db),
    user: User = Depends(require_perm("amenagement.dto.create")),
):
    _check_unique(db, RegistreDTO, "reference_dto", payload.reference_dto, "Reference DTO")
    obj = RegistreDTO()
    _apply(payload.model_dump(exclude_unset=True), obj, create=True)
    obj.auteur_saisie = obj.auteur_saisie or getattr(user, "username", None) or getattr(user, "email", None)
    db.add(obj)
    db.commit()
    db.refresh(obj)
    return _to_out(obj)


@router.get("/dto/{ident}", response_model=RegistreDTOOut, summary="Detail d'une ligne DTO")
def detail_dto(
    ident: int,
    db: Session = Depends(get_db),
    user: User = Depends(require_perm("amenagement.dto.read")),
):
    return _to_out(_get_or_404(db, RegistreDTO, ident, "Ligne DTO"))


@router.put("/dto/{ident}", response_model=RegistreDTOOut, summary="Corriger une ligne DTO")
def modifier_dto(
    ident: int,
    payload: RegistreDTOUpdate,
    db: Session = Depends(get_db),
    user: User = Depends(require_perm("amenagement.dto.modify")),
):
    obj = _get_or_404(db, RegistreDTO, ident, "Ligne DTO")
    _apply(payload.model_dump(exclude_unset=True), obj, create=False)
    db.commit()
    db.refresh(obj)
    return _to_out(obj)


@router.post("/dto/{ident}/visa-controle-financier", response_model=RegistreDTOOut,
             summary="Attester le visa du controle financier")
def viser_dto(
    ident: int,
    date_visa: date = Query(..., description="Date reellement apposee sur le DTO"),
    autorite_visa: str = Query(..., min_length=2, description="Controleur financier / direction emisrice"),
    numero_engagement: Optional[str] = Query(None),
    db: Session = Depends(get_db),
    user: User = Depends(require_perm("amenagement.dto.approve")),
):
    """Enregistre le visa appose par le controle financier, ne le simule pas."""
    obj = _get_or_404(db, RegistreDTO, ident, "Ligne DTO")
    obj.date_visa_controle_financier = date_visa
    obj.autorite_visa = autorite_visa
    if numero_engagement:
        obj.numero_engagement = numero_engagement
    obj.statut = "VISE"
    obj.date_verification = date.today()
    obj.auteur_saisie = getattr(user, "username", None) or obj.auteur_saisie
    db.commit()
    db.refresh(obj)
    return _to_out(obj)


@router.post("/dto/{ident}/notification-minepf", summary="Notification MINEPF (501)")
def notifier_minepf(ident: int, user: User = Depends(require_perm("amenagement.dto.approve"))):
    """Aucune interconnexion avec le MINEPF/CELIBER n'est deployee ici (501)."""
    not_implemented(
        "Notification teletransmise d'un engagement au MINEPF",
        "un canal officiel de teletransmission des DTO vers la tresor public / "
        "MINEPF (le depot reste papier ou email adresse au greffe)",
    )


# ─── 4. Marchés publics & PPP ────────────────────────────────────────────────

@router.get("/marches", response_model=List[MarcheAmenagementOut],
            summary="Marches et contrats d'amenagement")
def lister_marches(
    statut: Optional[StatutMarche] = None,
    port_id: Optional[int] = Query(None),
    db: Session = Depends(get_db),
    user: User = Depends(require_perm("amenagement.marche.read")),
):
    q = db.query(MarcheAmenagement)
    if statut:
        q = q.filter(MarcheAmenagement.statut == statut)
    if port_id:
        q = q.filter(MarcheAmenagement.port_id == port_id)
    return [_to_out(m) for m in q.order_by(MarcheAmenagement.reference).all()]


@router.post("/marches", response_model=MarcheAmenagementOut, status_code=status.HTTP_201_CREATED,
             summary="Enregistrer un marche ou un contrat PPP")
def creer_marche(
    payload: MarcheAmenagementCreate,
    db: Session = Depends(get_db),
    user: User = Depends(require_perm("amenagement.marche.create")),
):
    _check_unique(db, MarcheAmenagement, "reference", payload.reference, "Reference de marche")
    obj = MarcheAmenagement()
    _apply(payload.model_dump(exclude_unset=True), obj, create=True)
    obj.auteur_saisie = obj.auteur_saisie or getattr(user, "username", None) or getattr(user, "email", None)
    db.add(obj)
    db.commit()
    db.refresh(obj)
    return _to_out(obj)


@router.get("/marches/{ident}", response_model=MarcheAmenagementOut, summary="Detail d'un marche")
def detail_marche(
    ident: int,
    db: Session = Depends(get_db),
    user: User = Depends(require_perm("amenagement.marche.read")),
):
    return _to_out(_get_or_404(db, MarcheAmenagement, ident, "Marche d'amenagement"))


@router.put("/marches/{ident}", response_model=MarcheAmenagementOut,
            summary="Mettre a jour un marche")
def modifier_marche(
    ident: int,
    payload: MarcheAmenagementUpdate,
    db: Session = Depends(get_db),
    user: User = Depends(require_perm("amenagement.marche.modify")),
):
    obj = _get_or_404(db, MarcheAmenagement, ident, "Marche d'amenagement")
    _apply(payload.model_dump(exclude_unset=True), obj, create=False)
    db.commit()
    db.refresh(obj)
    return _to_out(obj)


@router.post("/marches/{ident}/attribution", response_model=MarcheAmenagementOut,
             summary="Enregistrer l'attribution decidee par la commission")
def attribuer_marche(
    ident: int,
    attributaire: str = Query(..., min_length=2),
    date_attribution: date = Query(..., description="Date de la decision reelle"),
    montant_attribue_xaf: Optional[float] = Query(None),
    reference_deliberation: Optional[str] = Query(None, description="PV de la COLIFE/CIP"),
    db: Session = Depends(get_db),
    user: User = Depends(require_perm("amenagement.marche.approve")),
):
    """Trace l'attribution prononcee par l'organe competant, sans la prononcer."""
    obj = _get_or_404(db, MarcheAmenagement, ident, "Marche d'amenagement")
    obj.attributaire = attributaire
    obj.date_attribution = date_attribution
    if montant_attribue_xaf is not None:
        obj.montant_attribue_xaf = montant_attribue_xaf
    if reference_deliberation:
        obj.dossier_appel_offre = obj.dossier_appel_offre or reference_deliberation
        obj.notes = (obj.notes + "\n" if obj.notes else "") + f"Deliberation : {reference_deliberation}"
    obj.statut = StatutMarche.ATTRIBUE
    obj.date_verification = date.today()
    obj.auteur_saisie = getattr(user, "username", None) or obj.auteur_saisie
    db.commit()
    db.refresh(obj)
    return _to_out(obj)


@router.post("/marches/{ident}/reception", response_model=MarcheAmenagementOut,
             summary="Enregistrer une reception (provisoire ou definitive)")
def receptionner_marche(
    ident: int,
    provisoire: bool = Query(True, description="True = reception provisoire, False = definitive"),
    date_reception: date = Query(...),
    db: Session = Depends(get_db),
    user: User = Depends(require_perm("amenagement.marche.approve")),
):
    obj = _get_or_404(db, MarcheAmenagement, ident, "Marche d'amenagement")
    if provisoire:
        obj.date_reception_provisoire = date_reception
        obj.statut = StatutMarche.RECEPTIONNE
    else:
        if not obj.date_reception_provisoire:
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail="Aucune reception provisoire enregistree : une reception "
                       "definitive ne peut pas etre declaree avant elle.",
            )
        obj.date_reception_definitive = date_reception
    obj.date_verification = date.today()
    obj.auteur_saisie = getattr(user, "username", None) or obj.auteur_saisie
    db.commit()
    db.refresh(obj)
    return _to_out(obj)


@router.post("/marches/{ident}/soumission-colife", summary="Passage en COLIFE (501)")
def soumettre_colife(ident: int, user: User = Depends(require_perm("amenagement.marche.approve"))):
    """La COLIFE/CIP instruit sur son propre circuit (501, rien n'est simule)."""
    not_implemented(
        "Soumission dematerialisee d'un dossier d'amenagement a la COLIFE ou a la CIP",
        "un acces au circuit officiel de controle des marches publics "
        "(plateforme MINFI/ARMP) ; le module tient deja l'avis rendu quand il "
        "est notifie",
    )


# ─── 5. Titres domaniaux ─────────────────────────────────────────────────────

@router.get("/titres-domaniaux", response_model=List[AutorisationDomanialeOut],
            summary="Registre des occupations du domaine portuaire")
def lister_titres(
    port_id: Optional[int] = Query(None),
    beneficiaire: Optional[str] = Query(None, description="Fille du nom, insensible a la casse"),
    expire: Optional[bool] = Query(None, description="True = titres echus, False = encore valables"),
    db: Session = Depends(get_db),
    user: User = Depends(require_perm("amenagement.titre_domanial.read")),
):
    q = db.query(AutorisationDomaniale)
    if port_id:
        q = q.filter(AutorisationDomaniale.port_id == port_id)
    if beneficiaire:
        q = q.filter(func.lower(AutorisationDomaniale.beneficiaire).contains(beneficiaire.lower()))
    if expire is True:
        q = q.filter(AutorisationDomaniale.date_expiration.isnot(None),
                     AutorisationDomaniale.date_expiration < date.today())
    elif expire is False:
        q = q.filter(or_(AutorisationDomaniale.date_expiration.is_(None),
                         AutorisationDomaniale.date_expiration >= date.today()))
    return [_to_out(t) for t in q.order_by(AutorisationDomaniale.date_expiration).all()]


@router.post("/titres-domaniaux", response_model=AutorisationDomanialeOut,
             status_code=status.HTTP_201_CREATED, summary="Inscrire un titre d'occupation")
def creer_titre(
    payload: AutorisationDomanialeCreate,
    db: Session = Depends(get_db),
    user: User = Depends(require_perm("amenagement.titre_domanial.create")),
):
    _check_unique(db, AutorisationDomaniale, "numero_piece", payload.numero_piece, "Numero de piece domaniale")
    obj = AutorisationDomaniale()
    _apply(payload.model_dump(exclude_unset=True), obj, create=True)
    obj.auteur_saisie = obj.auteur_saisie or getattr(user, "username", None) or getattr(user, "email", None)
    db.add(obj)
    db.commit()
    db.refresh(obj)
    return _to_out(obj)


@router.get("/titres-domaniaux/{ident}", response_model=AutorisationDomanialeOut,
            summary="Detail d'un titre domanial")
def detail_titre(
    ident: int,
    db: Session = Depends(get_db),
    user: User = Depends(require_perm("amenagement.titre_domanial.read")),
):
    return _to_out(_get_or_404(db, AutorisationDomaniale, ident, "Titre domanial"))


@router.put("/titres-domaniaux/{ident}", response_model=AutorisationDomanialeOut,
            summary="Mettre a jour un titre domanial")
def modifier_titre(
    ident: int,
    payload: AutorisationDomanialeUpdate,
    db: Session = Depends(get_db),
    user: User = Depends(require_perm("amenagement.titre_domanial.modify")),
):
    obj = _get_or_404(db, AutorisationDomaniale, ident, "Titre domanial")
    _apply(payload.model_dump(exclude_unset=True), obj, create=False)
    db.commit()
    db.refresh(obj)
    return _to_out(obj)


@router.post("/titres-domaniaux/{ident}/decision", response_model=AutorisationDomanialeOut,
             summary="Enregistrer la decision de l'autorite portuaire")
def decider_titre(
    ident: int,
    accord: bool = Query(..., description="True = titre delivre, False = demande rejetee"),
    date_decision: date = Query(...),
    autorite_emettrice: Optional[str] = Query(None),
    reference_deliberation: Optional[str] = Query(None),
    motif_refus: Optional[str] = Query(None),
    db: Session = Depends(get_db),
    user: User = Depends(require_perm("amenagement.titre_domanial.approve")),
):
    """Saisit la decision de l'autorite portuaire ; ne la remplace pas."""
    obj = _get_or_404(db, AutorisationDomaniale, ident, "Titre domanial")
    if accord:
        obj.statut = "DELIVRE"
        obj.date_signature = date_decision
        obj.date_effet = obj.date_effet or date_decision
    else:
        if not motif_refus:
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail="Un refus doit etre motive : la loi impose que la decision "
                       "de l'autorite portuaire soit ecrite et justifiee.",
            )
        obj.statut = "REFUSE"
        obj.motif_refus = motif_refus
    if autorite_emettrice:
        obj.autorite_emettrice = autorite_emettrice
    if reference_deliberation:
        obj.reference_deliberation = reference_deliberation
    obj.date_verification = date.today()
    obj.auteur_saisie = getattr(user, "username", None) or obj.auteur_saisie
    db.commit()
    db.refresh(obj)
    return _to_out(obj)


# ─── 6. Concessions & contrats d'exploitation ────────────────────────────────

@router.get("/concessions", response_model=List[ConcessionPortuaireOut],
            summary="Contrats de concession, affermage, BOT/AOT")
def lister_concessions(
    port_id: Optional[int] = Query(None),
    statut: Optional[StatutContrat] = None,
    db: Session = Depends(get_db),
    user: User = Depends(require_perm("amenagement.concession.read")),
):
    q = db.query(ConcessionPortuaire)
    if port_id:
        q = q.filter(ConcessionPortuaire.port_id == port_id)
    if statut:
        q = q.filter(ConcessionPortuaire.statut == statut)
    return [_to_out(c) for c in q.order_by(ConcessionPortuaire.date_echeance).all()]


@router.post("/concessions", response_model=ConcessionPortuaireOut,
             status_code=status.HTTP_201_CREATED, summary="Inscrire un contrat d'exploitation")
def creer_concession(
    payload: ConcessionPortuaireCreate,
    db: Session = Depends(get_db),
    user: User = Depends(require_perm("amenagement.concession.create")),
):
    _check_unique(db, ConcessionPortuaire, "code_contrat", payload.code_contrat, "Code de contrat")
    obj = ConcessionPortuaire()
    _apply(payload.model_dump(exclude_unset=True), obj, create=True)
    obj.auteur_saisie = obj.auteur_saisie or getattr(user, "username", None) or getattr(user, "email", None)
    db.add(obj)
    db.commit()
    db.refresh(obj)
    return _to_out(obj)


@router.get("/concessions/{ident}", response_model=ConcessionPortuaireOut,
            summary="Detail d'un contrat")
def detail_concession(
    ident: int,
    db: Session = Depends(get_db),
    user: User = Depends(require_perm("amenagement.concession.read")),
):
    return _to_out(_get_or_404(db, ConcessionPortuaire, ident, "Contrat d'exploitation"))


@router.put("/concessions/{ident}", response_model=ConcessionPortuaireOut,
            summary="Mettre a jour un contrat")
def modifier_concession(
    ident: int,
    payload: ConcessionPortuaireUpdate,
    db: Session = Depends(get_db),
    user: User = Depends(require_perm("amenagement.concession.modify")),
):
    obj = _get_or_404(db, ConcessionPortuaire, ident, "Contrat d'exploitation")
    _apply(payload.model_dump(exclude_unset=True), obj, create=False)
    db.commit()
    db.refresh(obj)
    return _to_out(obj)


@router.get("/concessions/{ident}/obligations",
            summary="Ecart entre investissements promis et realises")
def suivi_obligations(
    ident: int,
    db: Session = Depends(get_db),
    user: User = Depends(require_perm("amenagement.concession.read")),
):
    """Comparaison des deux montants SAISIS. Rien n'est projectil ni suppose.

    Si un seul des deux est connu, l'ecart est declare non calculable plutot
    que d'inventer le manquant.
    """
    obj = _get_or_404(db, ConcessionPortuaire, ident, "Contrat d'exploitation")
    promis = float(obj.investissement_promis_xaf) if obj.investissement_promis_xaf is not None else None
    realise = float(obj.investissement_realise_xaf) if obj.investissement_realise_xaf is not None else None
    calculable = promis is not None and realise is not None and promis > 0
    return {
        "id": obj.id,
        "code_contrat": obj.code_contrat,
        "concessionnaire": obj.concessionnaire,
        "investissement_promis_xaf": promis,
        "investissement_realise_xaf": realise,
        "ecart_xaf": round(promis - realise, 2) if calculable else None,
        "respect_pct": round((realise / promis) * 100, 2) if calculable else None,
        "exploit_calculable": calculable,
        "date_echeance": obj.date_echeance.isoformat() if obj.date_echeance else None,
        "note": (
            None if calculable else
            "Au moins un des deux montants n'a pas ete saisi depuis une piece "
            "contractuelle : l'ecart n'est pas calcule (aucune estimation)."
        ),
    }


@router.post("/concessions/{ident}/reversaison", summary="Prononcer la reversaison (501)")
def reverser_concession(ident: int, user: User = Depends(require_perm("amenagement.concession.approve"))):
    """La reversaison est un acte juridique de l'autorite concedante (501)."""
    not_implemented(
        "Prononce de la reversaison du patrimoine concessionne",
        "un acte officiel de l'autorite portuaire (proces-verbal de transfer "
        "et evaluation des biens) ; le module tient deja la liste des biens "
        "reversibles saisie au contrat",
    )


# ─── 7. Inventaire des infrastructures ───────────────────────────────────────

@router.get("/infrastructures", response_model=List[InfrastructurePortuaireOut],
            summary="Inventaire technique du domaine amenage")
def lister_infrastructures(
    port_id: Optional[int] = Query(None),
    statut: Optional[EtatInfrastructure] = None,
    type_infrastructure: Optional[TypeInfrastructure] = None,
    db: Session = Depends(get_db),
    user: User = Depends(require_perm("amenagement.infrastructure.read")),
):
    q = db.query(InfrastructurePortuaire).filter(InfrastructurePortuaire.est_actif.is_(True))
    if port_id:
        q = q.filter(InfrastructurePortuaire.port_id == port_id)
    if statut:
        q = q.filter(InfrastructurePortuaire.statut == statut)
    if type_infrastructure:
        q = q.filter(InfrastructurePortuaire.type_infrastructure == type_infrastructure)
    return [_to_out(i) for i in q.order_by(InfrastructurePortuaire.code).all()]


@router.post("/infrastructures", response_model=InfrastructurePortuaireOut,
             status_code=status.HTTP_201_CREATED, summary="Declarer un ouvrage livre ou projete")
def creer_infrastructure(
    payload: InfrastructurePortuaireCreate,
    db: Session = Depends(get_db),
    user: User = Depends(require_perm("amenagement.infrastructure.create")),
):
    _check_unique(db, InfrastructurePortuaire, "code", payload.code, "Code d'infrastructure")
    obj = InfrastructurePortuaire()
    _apply(payload.model_dump(exclude_unset=True), obj, create=True)
    obj.auteur_saisie = obj.auteur_saisie or getattr(user, "username", None) or getattr(user, "email", None)
    db.add(obj)
    db.commit()
    db.refresh(obj)
    return _to_out(obj)


@router.get("/infrastructures/{ident}", response_model=InfrastructurePortuaireOut,
            summary="Fiche technique d'une infrastructure")
def detail_infrastructure(
    ident: int,
    db: Session = Depends(get_db),
    user: User = Depends(require_perm("amenagement.infrastructure.read")),
):
    return _to_out(_get_or_404(db, InfrastructurePortuaire, ident, "Infrastructure amenagee"))


@router.put("/infrastructures/{ident}", response_model=InfrastructurePortuaireOut,
            summary="Mettre a jour une fiche d'infrastructure")
def modifier_infrastructure(
    ident: int,
    payload: InfrastructurePortuaireUpdate,
    db: Session = Depends(get_db),
    user: User = Depends(require_perm("amenagement.infrastructure.modify")),
):
    obj = _get_or_404(db, InfrastructurePortuaire, ident, "Infrastructure amenagee")
    _apply(payload.model_dump(exclude_unset=True), obj, create=False)
    db.commit()
    db.refresh(obj)
    return _to_out(obj)


@router.post("/infrastructures/{ident}/inspection", response_model=InfrastructurePortuaireOut,
             summary="Enregistrer un releve d'inspection")
def inserer_inspection(
    ident: int,
    date_inspection: date = Query(..., description="Date du rapport de visite"),
    etat_structural: Optional[str] = Query(None, description="Appreciation du rapport, saisie telle quelle"),
    note_genie_civil: Optional[float] = Query(None, ge=0, le=100,
                                              description="Note issue de l'expertise, jamais calculee ici"),
    prochaine_inspection: Optional[date] = Query(None),
    db: Session = Depends(get_db),
    user: User = Depends(require_perm("amenagement.infrastructure.modify")),
):
    obj = _get_or_404(db, InfrastructurePortuaire, ident, "Infrastructure amenagee")
    obj.date_derniere_inspection = date_inspection
    if etat_structural:
        obj.etat_structural = etat_structural.upper()
    if note_genie_civil is not None:
        obj.note_genie_civil = note_genie_civil
    if prochaine_inspection:
        obj.prochaine_inspection = prochaine_inspection
    obj.date_verification = date.today()
    obj.auteur_saisie = getattr(user, "username", None) or obj.auteur_saisie
    db.commit()
    db.refresh(obj)
    return _to_out(obj)


@router.delete("/infrastructures/{ident}", summary="Retirer un ouvrage de l'inventaire")
def desactiver_infrastructure(
    ident: int,
    motif: str = Query(..., min_length=3, description="Demolition, sortie de patrimoine, erreur de saisie..."),
    db: Session = Depends(get_db),
    user: User = Depends(require_perm("amenagement.infrastructure.delete")),
):
    obj = _get_or_404(db, InfrastructurePortuaire, ident, "Infrastructure amenagee")
    obj.est_actif = False
    obj.statut = EtatInfrastructure.DEMOLIE if "demoli" in motif.lower() else obj.statut
    obj.notes = (obj.notes + "\n" if obj.notes else "") + f"Retire : {motif}"
    db.commit()
    return {"id": obj.id, "code": obj.code, "message": "Ouvrage sorti de l'inventaire actif."}


# ─── 8. Dragage & chenal ─────────────────────────────────────────────────────

@router.get("/dragage", response_model=List[DragageOut], summary="Campagnes de dragage")
def lister_dragages(
    port_id: Optional[int] = Query(None),
    type_dragage: Optional[TypeDragage] = None,
    db: Session = Depends(get_db),
    user: User = Depends(require_perm("amenagement.dragage.read")),
):
    q = db.query(Dragage)
    if port_id:
        q = q.filter(Dragage.port_id == port_id)
    if type_dragage:
        q = q.filter(Dragage.type_dragage == type_dragage)
    return [_to_out(d) for d in q.order_by(Dragage.date_debut.desc().nullslast()).all()]


@router.post("/dragage", response_model=DragageOut, status_code=status.HTTP_201_CREATED,
             summary="Ouvrir une campagne de dragage")
def creer_dragage(
    payload: DragageCreate,
    db: Session = Depends(get_db),
    user: User = Depends(require_perm("amenagement.dragage.create")),
):
    _check_unique(db, Dragage, "code_campagne", payload.code_campagne, "Code de campagne")
    obj = Dragage()
    _apply(payload.model_dump(exclude_unset=True), obj, create=True)
    obj.auteur_saisie = obj.auteur_saisie or getattr(user, "username", None) or getattr(user, "email", None)
    db.add(obj)
    db.commit()
    db.refresh(obj)
    return _to_out(obj)


@router.get("/dragage/{ident}", response_model=DragageOut, summary="Detail d'une campagne")
def detail_dragage(
    ident: int,
    db: Session = Depends(get_db),
    user: User = Depends(require_perm("amenagement.dragage.read")),
):
    return _to_out(_get_or_404(db, Dragage, ident, "Campagne de dragage"))


@router.put("/dragage/{ident}", response_model=DragageOut, summary="Mettre a jour une campagne")
def modifier_dragage(
    ident: int,
    payload: DragageUpdate,
    db: Session = Depends(get_db),
    user: User = Depends(require_perm("amenagement.dragage.modify")),
):
    obj = _get_or_404(db, Dragage, ident, "Campagne de dragage")
    _apply(payload.model_dump(exclude_unset=True), obj, create=False)
    db.commit()
    db.refresh(obj)
    return _to_out(obj)


@router.post("/dragage/{ident}/bathymetrie", response_model=DragageOut,
             summary="Consigner un leve bathymetrique")
def consigner_bathymetrie(
    ident: int,
    profondeur_obtenue_m: float = Query(..., ge=0, description="Profondeur relevee apres dragage"),
    date_releve: date = Query(..., description="Date du leve"),
    volume_mesure_m3: Optional[float] = Query(None, ge=0,
                                              description="Cubage releve par le contractant"),
    db: Session = Depends(get_db),
    user: User = Depends(require_perm("amenagement.dragage.modify")),
):
    obj = _get_or_404(db, Dragage, ident, "Campagne de dragage")
    obj.profondeur_obtenue_m = profondeur_obtenue_m
    obj.date_releve = date_releve
    obj.leve_bathymetrique_apres = True
    if volume_mesure_m3 is not None:
        obj.volume_mesure_m3 = volume_mesure_m3
    obj.date_verification = date.today()
    obj.auteur_saisie = getattr(user, "username", None) or obj.auteur_saisie
    db.commit()
    db.refresh(obj)
    return _to_out(obj)


@router.post("/dragage/{ident}/autorisation-rejet", summary="Demande d'exutoire (501)")
def demande_exutoire(ident: int, user: User = Depends(require_perm("amenagement.dragage.approve"))):
    """L'autorisation de rejet releve du MINEPPT (501, aucune decision simulee)."""
    not_implemented(
        "Demande dematerialisee d'exutoire de rejet de drague",
        "un canal officiel aupre du MINEPPT / autorite portuaire pour "
        "l'agrement des sites de disposal ; le module conserve deja la "
        "reference de l'autorisation quand elle est notifiee"
    )


# ─── 9. Autorisations administratives ────────────────────────────────────────

@router.get("/autorisations", response_model=List[AutorisationTravauxOut],
            summary="Registre des autorisations et visas administratifs")
def lister_autorisations(
    statut: Optional[StatutAutorisation] = None,
    type_autorisation: Optional[TypeAutorisationTravaux] = None,
    db: Session = Depends(get_db),
    user: User = Depends(require_perm("amenagement.autorisation.read")),
):
    q = db.query(AutorisationTravaux)
    if statut:
        q = q.filter(AutorisationTravaux.statut == statut)
    if type_autorisation:
        q = q.filter(AutorisationTravaux.type_autorisation == type_autorisation)
    return [_to_out(a) for a in q.order_by(AutorisationTravaux.date_depot.desc().nullslast()).all()]


@router.post("/autorisations", response_model=AutorisationTravauxOut,
             status_code=status.HTTP_201_CREATED, summary="Preparer un dossier d'autorisation")
def creer_autorisation(
    payload: AutorisationTravauxCreate,
    db: Session = Depends(get_db),
    user: User = Depends(require_perm("amenagement.autorisation.create")),
):
    _check_unique(db, AutorisationTravaux, "reference", payload.reference, "Reference d'autorisation")
    obj = AutorisationTravaux()
    _apply(payload.model_dump(exclude_unset=True), obj, create=True)
    obj.auteur_saisie = obj.auteur_saisie or getattr(user, "username", None) or getattr(user, "email", None)
    db.add(obj)
    db.commit()
    db.refresh(obj)
    return _to_out(obj)


@router.get("/autorisations/{ident}", response_model=AutorisationTravauxOut,
            summary="Detail d'un dossier")
def detail_autorisation(
    ident: int,
    db: Session = Depends(get_db),
    user: User = Depends(require_perm("amenagement.autorisation.read")),
):
    return _to_out(_get_or_404(db, AutorisationTravaux, ident, "Autorisation de travaux"))


@router.put("/autorisations/{ident}", response_model=AutorisationTravauxOut,
            summary="Mettre a jour un dossier")
def modifier_autorisation(
    ident: int,
    payload: AutorisationTravauxUpdate,
    db: Session = Depends(get_db),
    user: User = Depends(require_perm("amenagement.autorisation.modify")),
):
    obj = _get_or_404(db, AutorisationTravaux, ident, "Autorisation de travaux")
    _apply(payload.model_dump(exclude_unset=True), obj, create=False)
    db.commit()
    db.refresh(obj)
    return _to_out(obj)


@router.post("/autorisations/{ident}/depot", summary="Depot aupres de l'administration (501)")
def depot_autorisation(ident: int, user: User = Depends(require_perm("amenagement.autorisation.approve"))):
    """Le depot d'une EIES/d'un permis se fait aupres du MINEPPT (501)."""
    not_implemented(
        "Depot teleprogramme d'un dossier EIES / permis aupres du MINEPPT",
        "une interconnexion avec le guichet environnemental officiel ; le "
        "module enregistre la date de depot et l'arrete quand ils sont notifiees"
    )


# ─── 10. Tableau de bord : agrégats calculés à partir des saisies ────────────

def _count(db: Session, model, *crit) -> int:
    return db.query(func.count(model.id)).filter(*crit).scalar() or 0


def _sum(db: Session, column, *crit) -> Optional[float]:
    total = db.query(func.sum(column)).filter(*crit).scalar()
    return float(total) if total is not None else None


@router.get("/synthese", summary="Synthese du departement (agregee depuis les saisies)")
def synthese(
    port_id: Optional[int] = Query(None),
    db: Session = Depends(get_db),
    user: User = Depends(require_perm("amenagement.projet.read")),
):
    """Aucun chiffre n'est estime : un agrégat NULL veut dire « rien de saisi ».

    Les totaux financiers n'additionnent que les montants reellement enregistres
    et signalent les lignes encore vides, pour qu'un solde partiel ne passe pas
    pour un budget complet.
    """
    pf = [ProjetAmenagement.est_actif.is_(True)]
    inf = [InfrastructurePortuaire.est_actif.is_(True)]
    sf = [SchemaDirecteur.est_actif.is_(True)]
    if port_id:
        pf.append(ProjetAmenagement.port_id == port_id)
        inf.append(InfrastructurePortuaire.port_id == port_id)
        sf.append(SchemaDirecteur.port_id == port_id)

    projets_en_cours = _count(
        db, ProjetAmenagement, *pf,
        ProjetAmenagement.statut.in_([
            StatutProjet.EN_CONSTRUCTION, StatutProjet.EN_ATTRIBUTION,
            StatutProjet.ATTRIBUE, StatutProjet.INSCRIT_DTO,
        ]),
    )
    dto_manquants = _count(db, ProjetAmenagement, *pf, ProjetAmenagement.dto_reference.is_(None))
    cout_previsionnel = _sum(db, ProjetAmenagement.cout_previsionnel_xaf, *pf)
    cout_reel = _sum(db, ProjetAmenagement.cout_reel_xaf, *pf)
    marches_engages = _sum(
        db, MarcheAmenagement.montant_attribue_xaf,
        MarcheAmenagement.statut.in_([
            StatutMarche.ATTRIBUE, StatutMarche.NOTIFIE,
            StatutMarche.EN_EXECUTION, StatutMarche.RECEPTIONNE,
        ]),
    )
    aujourd_hui = date.today()
    return {
        "perimetre": {
            "port_id": port_id,
            "places": list(PLACES_DU_DEPARTEMENT),
            "explication": (
                "Les codes de places correspondent au perimetre d'etude du "
                "departement ; les donnees affichees proviennent uniquement des "
                "lignes saisies en base."
            ),
        },
        "schemas_directeurs": {
            "actifs": _count(db, SchemaDirecteur, *sf),
            "approuves": _count(db, SchemaDirecteur, *sf, SchemaDirecteur.statut == StatutSchema.APPROUVE),
            "en_elaboration": _count(db, SchemaDirecteur, *sf, SchemaDirecteur.statut == StatutSchema.ELABORATION),
            "a_reviser": _count(
                db, SchemaDirecteur, *sf,
                SchemaDirecteur.date_echeance_revision.isnot(None),
                SchemaDirecteur.date_echeance_revision < aujourd_hui,
            ),
        },
        "projets": {
            "total": _count(db, ProjetAmenagement, *pf),
            "en_cours": projets_en_cours,
            "sans_dto": dto_manquants,
            "cout_previsionnel_total_xaf": cout_previsionnel,
            "cout_reel_total_xaf": cout_reel,
            "suivi_financier_complet": cout_previsionnel is not None and cout_reel is not None,
        },
        "passation": {
            "marches_total": _count(db, MarcheAmenagement, *( [MarcheAmenagement.port_id == port_id] if port_id else [] )),
            "marches_en_execution": _count(db, MarcheAmenagement, MarcheAmenagement.statut == StatutMarche.EN_EXECUTION),
            "montant_engage_xaf": marches_engages,
            "en_attente_colife": _count(
                db, MarcheAmenagement, MarcheAmenagement.avis_colife.is_(None),
                MarcheAmenagement.statut.in_([StatutMarche.PUBLIE, StatutMarche.EN_COURS_EVALUATION]),
            ),
        },
        "domaine": {
            "titres_actifs": _count(db, AutorisationDomaniale,
                                    AutorisationDomaniale.statut.in_(["DELIVRE", "SIGNATURE", "EN_VIGUEUR"])),
            "titres_expire": _count(db, AutorisationDomaniale,
                                    AutorisationDomaniale.date_expiration.isnot(None),
                                    AutorisationDomaniale.date_expiration < aujourd_hui),
            "concessions_en_vigueur": _count(db, ConcessionPortuaire,
                                             ConcessionPortuaire.statut == StatutContrat.EN_VIGUEUR),
            "concessions_echeance_12_mois": _count(
                db, ConcessionPortuaire,
                ConcessionPortuaire.statut == StatutContrat.EN_VIGUEUR,
                ConcessionPortuaire.date_echeance.isnot(None),
                ConcessionPortuaire.date_echeance >= aujourd_hui,
                ConcessionPortuaire.date_echeance <= _dans_un_an(aujourd_hui),
            ),
        },
        "patrimoine": {
            "ouvrages_inventories": _count(db, InfrastructurePortuaire, *inf),
            "operationnels": _count(db, InfrastructurePortuaire, *inf,
                                    InfrastructurePortuaire.statut == EtatInfrastructure.OPERATIONNELLE),
            "degrades_ou_hors_service": _count(
                db, InfrastructurePortuaire, *inf,
                InfrastructurePortuaire.statut.in_([
                    EtatInfrastructure.DEGRADEE, EtatInfrastructure.HORS_SERVICE,
                    EtatInfrastructure.SOUS_UTILISEE,
                ]),
            ),
            "sans_date_inspection": _count(db, InfrastructurePortuaire, *inf,
                                           InfrastructurePortuaire.date_derniere_inspection.is_(None)),
        },
        "dragage": {
            "campagnes": _count(db, Dragage, *([Dragage.port_id == port_id] if port_id else [])),
            "volume_total_releve_m3": _sum(db, Dragage.volume_mesure_m3,
                                           *([Dragage.port_id == port_id] if port_id else [])),
            "sans_leve_apres": _count(db, Dragage, Dragage.leve_bathymetrique_apres.isnot(True),
                                      *([Dragage.port_id == port_id] if port_id else [])),
        },
        "conformite": {
            "dossiers_total": _count(db, AutorisationTravaux, *([AutorisationTravaux.port_id == port_id] if port_id else [])),
            "en_attente_de_decision": _count(db, AutorisationTravaux,
                                             AutorisationTravaux.statut.in_(
                                                 [StatutAutorisation.DEPOSEE, StatutAutorisation.COMPLEMENT_REQUIS])),
            "accordees": _count(db, AutorisationTravaux, AutorisationTravaux.statut == StatutAutorisation.ACCORDEE),
            "expirees": _count(db, AutorisationTravaux,
                              AutorisationTravaux.statut == StatutAutorisation.EXPIREE),
        },
    }

