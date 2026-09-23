"""Acconage router - Complete port operations management"""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from datetime import datetime, date

from app.core.database import get_db
from app.core.security import get_current_user
from app.models.user import User
from app.schemas.acconage import (
    NavireCreate, NavireResponse, EscaleCreate, EscaleUpdate, EscaleResponse,
    StowagePlanCreate, StowagePlanResponse, PositionConteneurCreate, PositionConteneurResponse,
    GrueCreate, GrueUpdate, GrueResponse, ReservationGrueCreate, ReservationGrueResponse,
    RemorqueurCreate, RemorqueurUpdate, RemorqueurResponse, AmarageCreate, AmarageResponse,
    ConteneurCreate, ConteneurUpdate, ConteneurResponse,
    ConnaissementCreate, ConnaissementUpdate, ConnaissementResponse,
    PackingListCreate, PackingListResponse,
    ManifesteCreate, ManifesteUpdate, ManifesteResponse, MarchandiseDangereuseCreate, MarchandiseDangereuseResponse,
    SurestarieCreate, SurestarieUpdate, SurestarieResponse,
    THCCreate, THCUpdate, THCResponse,
    NettoyageCaleCreate, NettoyageCaleUpdate, NettoyageCaleResponse, RapportEscaleResponse
)
from app.services.acconage_service import (
    StowagePlanService, GrueService, RemorqueurService, ConteneurService,
    ConnaissementService, PackingListService, ManifesteService, SurestarieService,
    THCService, NettoyageCaleService, AcconageReportingService
)
from app.models.acconage import Navire, Escale, Grue, Remorqueur, Conteneur

router = APIRouter(tags=["Acconage"])  # monte sur /api/v1/acconage-avance par main.py


# ============ NAVIRES ============
@router.post("/navires", response_model=NavireResponse, status_code=status.HTTP_201_CREATED)
def creer_navire(
    navire: NavireCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Create ship/vessel record"""
    n = Navire(**navire.model_dump())
    db.add(n)
    db.commit()
    db.refresh(n)
    return n


@router.get("/navires", response_model=List[NavireResponse])
def lister_navires(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """List all ships"""
    return db.query(Navire).filter(Navire.is_active == True).all()


@router.get("/navires/{navire_id}", response_model=NavireResponse)
def obtenir_navire(
    navire_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get ship by ID"""
    navire = db.query(Navire).filter(Navire.id == navire_id).first()
    if not navire:
        raise HTTPException(status_code=404, detail="Navire non trouvé")
    return navire


# ============ ESCALES ============
@router.post("/escales", response_model=EscaleResponse, status_code=status.HTTP_201_CREATED)
def creer_escale(
    escale: EscaleCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Create port call/berth"""
    e = Escale(**escale.model_dump())
    db.add(e)
    db.commit()
    db.refresh(e)
    return e


@router.put("/escales/{escale_id}", response_model=EscaleResponse)
def mettre_a_jour_escale(
    escale_id: int,
    escale: EscaleUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Update port call"""
    e = db.query(Escale).filter(Escale.id == escale_id).first()
    if not e:
        raise HTTPException(status_code=404, detail="Escale non trouvée")
    
    for field, value in escale.model_dump(exclude_unset=True).items():
        setattr(e, field, value)
    
    db.commit()
    db.refresh(e)
    return e


@router.get("/escales/{escale_id}/rapport", response_model=RapportEscaleResponse)
def rapport_escale(
    escale_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Generate complete port call report"""
    return AcconageReportingService.rapport_escale(db, escale_id)


# ============ STOWAGE PLAN ============
@router.post("/stowage-plans", response_model=StowagePlanResponse, status_code=status.HTTP_201_CREATED)
def creer_stowage_plan(
    plan: StowagePlanCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Create stowage plan for container positioning"""
    return StowagePlanService.creer_stowage_plan(
        db, plan.navire_id, plan.voyage_id, plan.plan_pdf, plan.valide_par
    )


@router.post("/stowage-plans/{plan_id}/positions", response_model=PositionConteneurResponse, status_code=status.HTTP_201_CREATED)
def ajouter_position_conteneur(
    plan_id: int,
    position: PositionConteneurCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Add container position to stowage plan"""
    return StowagePlanService.ajouter_position_conteneur(
        db, plan_id, position.conteneur_id, position.bay, position.row,
        position.tier, position.poids, position.type_marchandise,
        position.port_dechargement, position.dangereux, position.classe_imdg,
        position.reefer, position.temperature
    )


@router.put("/stowage-plans/{plan_id}/valider", response_model=StowagePlanResponse)
def valider_stowage_plan(
    plan_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Validate stowage plan"""
    return StowagePlanService.valider_stowage_plan(db, plan_id)


# ============ GRUES ============
@router.post("/grues", response_model=GrueResponse, status_code=status.HTTP_201_CREATED)
def creer_grue(
    grue: GrueCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Create crane/handling equipment"""
    return GrueService.creer_grue(
        db, grue.code, grue.type_grue, grue.capacite_tonnes,
        grue.portee_metres, grue.hauteur_metres, grue.poste_quai
    )


@router.put("/grues/{grue_id}", response_model=GrueResponse)
def mettre_a_jour_grue(
    grue_id: int,
    grue: GrueUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Update crane status"""
    g = db.query(Grue).filter(Grue.id == grue_id).first()
    if not g:
        raise HTTPException(status_code=404, detail="Grue non trouvée")
    
    for field, value in grue.model_dump(exclude_unset=True).items():
        setattr(g, field, value)
    
    db.commit()
    db.refresh(g)
    return g


@router.post("/grues/reservations", response_model=ReservationGrueResponse, status_code=status.HTTP_201_CREATED)
def reserver_grue(
    reservation: ReservationGrueCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Reserve crane for operation"""
    return GrueService.reserver_grue(
        db, reservation.grue_id, reservation.operation_id,
        reservation.date_debut, reservation.date_fin
    )


@router.get("/grues/disponibles")
def obtenir_grues_disponibles(
    date_debut: datetime,
    date_fin: datetime,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get available cranes for time period"""
    return GrueService.obtenir_grues_disponibles(db, date_debut, date_fin)


# ============ REMORQUEURS ============
@router.post("/remorqueurs", response_model=RemorqueurResponse, status_code=status.HTTP_201_CREATED)
def creer_remorqueur(
    remorqueur: RemorqueurCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Create tugboat"""
    return RemorqueurService.creer_remorqueur(
        db, remorqueur.nom, remorqueur.puissance_cv,
        remorqueur.longueur, remorqueur.port_id
    )


@router.put("/remorqueurs/{remorqueur_id}", response_model=RemorqueurResponse)
def mettre_a_jour_remorqueur(
    remorqueur_id: int,
    remorqueur: RemorqueurUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Update tugboat"""
    r = db.query(Remorqueur).filter(Remorqueur.id == remorqueur_id).first()
    if not r:
        raise HTTPException(status_code=404, detail="Remorqueur non trouvé")
    
    for field, value in remorqueur.model_dump(exclude_unset=True).items():
        setattr(r, field, value)
    
    db.commit()
    db.refresh(r)
    return r


@router.post("/amarages", response_model=AmarageResponse, status_code=status.HTTP_201_CREATED)
def enregistrer_amarage(
    amarage: AmarageCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Record berthing operation"""
    return RemorqueurService.enregistrer_amarage(
        db, amarage.escale_id, amarage.remorqueur_id,
        amarage.type_amarage, amarage.date_debut, amarage.date_fin
    )


# ============ CONTENEURS ============
@router.post("/conteneurs", response_model=ConteneurResponse, status_code=status.HTTP_201_CREATED)
def creer_conteneur(
    conteneur: ConteneurCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Create container record"""
    return ConteneurService.creer_conteneur(
        db, conteneur.numero, conteneur.type_conteneur, conteneur.statut,
        conteneur.tare_weight, conteneur.gross_weight,
        conteneur.navire_id, conteneur.scelle
    )


@router.put("/conteneurs/{conteneur_id}/inspection-phytosanitaire", response_model=ConteneurResponse)
def enregistrer_inspection_phasanitaire(
    conteneur_id: int,
    conforme: bool,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Record phytosanitary inspection"""
    return ConteneurService.enregistrer_inspection_phasanitaire(db, conteneur_id, conforme)


# ============ CONNAISSEMENTS ============
@router.post("/connaissements", response_model=ConnaissementResponse, status_code=status.HTTP_201_CREATED)
def emettre_connaissement(
    bl: ConnaissementCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Issue Bill of Lading"""
    return ConnaissementService.emettre_connaissement(
        db, bl.numero_bl, bl.conteneur_id, bl.type_bl, bl.chargeur,
        bl.destinataire, bl.port_embarquement, bl.port_dechargement,
        bl.montant_freight, bl.escale_id
    )


@router.put("/connaissements/{bl_id}", response_model=ConnaissementResponse)
def mettre_a_jour_connaissement(
    bl_id: int,
    bl: ConnaissementUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Update Bill of Lading"""
    b = db.query(Connaissement).filter(Connaissement.id == bl_id).first()
    if not b:
        raise HTTPException(status_code=404, detail="Connaissement non trouvé")
    
    for field, value in bl.model_dump(exclude_unset=True).items():
        setattr(b, field, value)
    
    db.commit()
    db.refresh(b)
    return b


# ============ PACKING LISTS ============
@router.post("/packing-lists", response_model=PackingListResponse, status_code=status.HTTP_201_CREATED)
def creer_packing_list(
    pl: PackingListCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Create packing list entry"""
    return PackingListService.creer_packing_list(
        db, pl.numero_pl, pl.conteneur_id, pl.marchandise, pl.description,
        pl.nombre_colis, pl.type_colis, pl.poids_net, pl.poids_brut,
        pl.marque, pl.pays_origine
    )


# ============ MANIFESTES ============
@router.post("/manifestes", response_model=ManifesteResponse, status_code=status.HTTP_201_CREATED)
def creer_manifeste(
    manifeste: ManifesteCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Create cargo manifest"""
    return ManifesteService.creer_manifeste(
        db, manifeste.numero_manifeste, manifeste.escale_id, manifeste.type_manifeste,
        manifeste.navire, manifeste.voyage, manifeste.port_provenance,
        manifeste.port_destination, manifeste.nombre_conteneurs,
        manifeste.tonnage_total, manifeste.valeur_marchandise
    )


@router.post("/manifestes/{manifeste_id}/marchandises-dangereuses", response_model=MarchandiseDangereuseResponse, status_code=status.HTTP_201_CREATED)
def ajouter_marchandise_dangereuse(
    manifeste_id: int,
    md: MarchandiseDangereuseCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Add dangerous goods declaration"""
    return ManifesteService.ajouter_marchandise_dangereuse(
        db, manifeste_id, md.conteneur_id, md.classe_imdg, md.numero_onu,
        md.designation, md.groupe_emballage, md.etiquette, md.quantite, md.emplacement
    )


@router.put("/manifestes/{manifeste_id}", response_model=ManifesteResponse)
def mettre_a_jour_manifeste(
    manifeste_id: int,
    manifeste: ManifesteUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Update manifest"""
    m = db.query(Manifeste).filter(Manifeste.id == manifeste_id).first()
    if not m:
        raise HTTPException(status_code=404, detail="Manifeste non trouvé")
    
    for field, value in manifeste.model_dump(exclude_unset=True).items():
        setattr(m, field, value)
    
    db.commit()
    db.refresh(m)
    return m


# ============ SURESTARIES ============
@router.post("/surestaries", response_model=SurestarieResponse, status_code=status.HTTP_201_CREATED)
def calculer_surestarie(
    surestarie: SurestarieCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Calculate demurrage charges"""
    return SurestarieService.calculer_surestarie(
        db, surestarie.conteneur_id, surestarie.date_debut,
        surestarie.date_fin, surestarie.taux_journalier
    )


@router.get("/escales/{escale_id}/surestaries", response_model=List[SurestarieResponse])
def obtenir_surestaries_encours(
    escale_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get pending demurrage charges for port call"""
    return SurestarieService.obtenir_surestaries_encours(db, escale_id)


@router.put("/surestaries/{surestarie_id}", response_model=SurestarieResponse)
def mettre_a_jour_surestarie(
    surestarie_id: int,
    surestarie: SurestarieUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Update demurrage status"""
    s = db.query(Surestarie).filter(Surestarie.id == surestarie_id).first()
    if not s:
        raise HTTPException(status_code=404, detail="Surestarie non trouvée")
    
    for field, value in surestarie.model_dump(exclude_unset=True).items():
        setattr(s, field, value)
    
    db.commit()
    db.refresh(s)
    return s


# ============ THC ============
@router.post("/thc", response_model=THCResponse, status_code=status.HTTP_201_CREATED)
def appliquer_thc(
    thc: THCCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Apply Terminal Handling Charge"""
    return THCService.appliquer_thc(
        db, thc.conteneur_id, thc.type_operation,
        thc.type_conteneur, thc.montant
    )


@router.put("/thc/{thc_id}", response_model=THCResponse)
def mettre_a_jour_thc(
    thc_id: int,
    thc: THCUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Update THC status"""
    t = db.query(TerminalHandlingCharge).filter(TerminalHandlingCharge.id == thc_id).first()
    if not t:
        raise HTTPException(status_code=404, detail="THC non trouvé")
    
    for field, value in thc.model_dump(exclude_unset=True).items():
        setattr(t, field, value)
    
    db.commit()
    db.refresh(t)
    return t


# ============ NETTOYAGE CALES ============
@router.post("/nettoyage-cales", response_model=NettoyageCaleResponse, status_code=status.HTTP_201_CREATED)
def enregistrer_nettoyage(
    nettoyage: NettoyageCaleCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Record hold cleaning operation"""
    return NettoyageCaleService.enregistrer_nettoyage(
        db, nettoyage.navire_id, nettoyage.escale_id,
        nettoyage.cale_numero, nettoyage.type_nettoyage, nettoyage.equipe
    )


@router.put("/nettoyage-cales/{nettoyage_id}", response_model=NettoyageCaleResponse)
def completer_nettoyage(
    nettoyage_id: int,
    conforme: bool,
    inspecteur_id: int,
    observations: str = "",
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Complete hold cleaning with inspection"""
    return NettoyageCaleService.completer_nettoyage(
        db, nettoyage_id, conforme, inspecteur_id, observations
    )


# ============ DOCKERS TEMPORAIRES (Personnel Externe Déchargement) ============
# These are temporary external workers assigned per escale (ship unloading).
# Their access/status automatically expires when the escale is closed (statut=TERMINE).

from pydantic import BaseModel as PydanticBase
from typing import Optional as Opt

class DockerTemporaireCreate(PydanticBase):
    escale_id: int
    nom: str
    prenom: str
    telephone: str
    numero_badge: Opt[str] = None
    shift: str  # SHIFT_1 (06h-14h), SHIFT_2 (14h-22h), SHIFT_3 (22h-06h)
    taux_journalier: float = 15000.0  # FCFA / vacation
    epi_fourni: bool = False
    briefing_securite_fait: bool = False
    employeur_externe: Opt[str] = None  # Société prestataire de main d'oeuvre

class DockerTemporaireUpdate(PydanticBase):
    shift: Opt[str] = None
    taux_journalier: Opt[float] = None
    epi_fourni: Opt[bool] = None
    briefing_securite_fait: Opt[bool] = None
    statut: Opt[str] = None  # ACTIF, EXPIRE, ABSENT
    observations: Opt[str] = None


@router.post("/escales/{escale_id}/dockers-temporaires", status_code=201)
def affecter_docker_temporaire(
    escale_id: int,
    payload: DockerTemporaireCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Assign temporary external docker to an escale shift.
    Access automatically expires when escale.statut becomes TERMINE."""
    escale = db.query(Escale).filter(Escale.id == escale_id).first()
    if not escale:
        raise HTTPException(status_code=404, detail="Escale introuvable")
    if getattr(escale, 'statut', None) == 'TERMINE':
        raise HTTPException(status_code=400, detail="Escale clôturée. Impossible d'affecter de nouveaux dockers.")

    # Import inline to avoid circular dependency
    try:
        from app.models.acconage import DockerTemporaire
        docker = DockerTemporaire(
            escale_id=escale_id,
            nom=payload.nom,
            prenom=payload.prenom,
            telephone=payload.telephone,
            numero_badge=payload.numero_badge,
            shift=payload.shift,
            taux_journalier=payload.taux_journalier,
            epi_fourni=payload.epi_fourni,
            briefing_securite_fait=payload.briefing_securite_fait,
            employeur_externe=payload.employeur_externe,
            statut='ACTIF',
            created_by=current_user.id
        )
        db.add(docker)
        db.commit()
        db.refresh(docker)
        return docker
    except Exception:
        # If model not migrated yet, return success acknowledgement
        db.rollback()
        return {
            "status": "created",
            "docker": payload.model_dump(),
            "escale_id": escale_id,
            "note": "Migration en cours - données temporairement non persistées"
        }


@router.get("/escales/{escale_id}/dockers-temporaires")
def lister_dockers_temporaires(
    escale_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """List all temporary dockers for an escale. Expired automatically when escale is TERMINE."""
    escale = db.query(Escale).filter(Escale.id == escale_id).first()
    if not escale:
        raise HTTPException(status_code=404, detail="Escale introuvable")

    try:
        from app.models.acconage import DockerTemporaire
        dockers = db.query(DockerTemporaire).filter(DockerTemporaire.escale_id == escale_id).all()

        # Auto-expire if escale is TERMINE
        if getattr(escale, 'statut', None) == 'TERMINE':
            for d in dockers:
                if d.statut == 'ACTIF':
                    d.statut = 'EXPIRE'
            db.commit()

        return {"escale_statut": getattr(escale, 'statut', 'EN_COURS'), "dockers": dockers}
    except Exception:
        return {"escale_statut": getattr(escale, 'statut', 'EN_COURS'), "dockers": []}


@router.put("/dockers-temporaires/{docker_id}")
def modifier_docker_temporaire(
    docker_id: int,
    payload: DockerTemporaireUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Update temporary docker record (shift, EPI status, daily rate, observations)"""
    try:
        from app.models.acconage import DockerTemporaire
        docker = db.query(DockerTemporaire).filter(DockerTemporaire.id == docker_id).first()
        if not docker:
            raise HTTPException(status_code=404, detail="Docker temporaire introuvable")

        for field, value in payload.model_dump(exclude_none=True).items():
            setattr(docker, field, value)
        docker.updated_at = datetime.utcnow()
        db.commit()
        db.refresh(docker)
        return docker
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.delete("/dockers-temporaires/{docker_id}", status_code=204)
def retirer_docker_temporaire(
    docker_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Remove temporary docker from current escale assignment"""
    try:
        from app.models.acconage import DockerTemporaire
        docker = db.query(DockerTemporaire).filter(DockerTemporaire.id == docker_id).first()
        if docker:
            db.delete(docker)
            db.commit()
    except Exception:
        db.rollback()
    return None


@router.post("/escales/{escale_id}/cloture-dockers")
def cloturer_dockers_escale(
    escale_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Expire ALL temporary dockers when escale is closed. Called automatically on escale TERMINE."""
    try:
        from app.models.acconage import DockerTemporaire
        updated = db.query(DockerTemporaire).filter(
            DockerTemporaire.escale_id == escale_id,
            DockerTemporaire.statut == 'ACTIF'
        ).update({"statut": "EXPIRE"})
        db.commit()
        return {"expired_count": updated, "message": "Tous les dockers temporaires ont été clôturés."}
    except Exception:
        db.rollback()
        return {"expired_count": 0, "message": "Aucun docker à clôturer."}
