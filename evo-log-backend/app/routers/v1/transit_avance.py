"""Transit avancé router - Complete customs operations management"""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from datetime import datetime, date

from app.core.database import get_db
from app.core.security import get_current_user
from app.models.user import User
from app.schemas.transit_avance import (
    BureauDouaneCreate, BureauDouaneUpdate, BureauDouaneResponse,
    DossierTransitAvanceCreate, DossierTransitAvanceUpdate, DossierTransitAvanceResponse,
    VisitePhysiqueCreate, VisitePhysiqueUpdate, VisitePhysiqueResponse,
    ValorisationDouaniereCreate, ValorisationDouaniereResponse,
    NomenclatureCEMACCreate, NomenclatureCEMACUpdate, NomenclatureCEMACResponse,
    DeclarationDouaniereAvanceCreate, DeclarationDouaniereAvanceUpdate, DeclarationDouaniereAvanceResponse,
    LigneDeclarationCreate, LigneDeclarationResponse,
    BonADCreate, BonADUpdate, BonADResponse,
    AvisMiseConsommationCreate, AvisMiseConsommationUpdate, AvisMiseConsommationResponse,
    CreditEnlevementCreate, CreditEnlevementUpdate, CreditEnlevementResponse,
    DroitPortCreate, DroitPortUpdate, DroitPortResponse,
    TimbreUsageCreate, TimbreUsageUpdate, TimbreUsageResponse,
    LitigeDouanierCreate, LitigeDouanierUpdate, LitigeDouanierResponse,
    ArchivageDossierCreate, ArchivageDossierUpdate, ArchivageDossierResponse,
    ProcedureUrgenteCreate, ProcedureUrgenteUpdate, ProcedureUrgenteResponse,
    RapportDossierResponse
)
from app.services.transit_avance_service import (
    BureauDouaneService, DossierTransitAvanceService, VisitePhysiqueService,
    ValorisationDouaniereService, NomenclatureCEMACService, DeclarationDouaniereAvanceService,
    LigneDeclarationService, BonADService, AvisMiseConsommationService, CreditEnlevementService,
    DroitPortService, TimbreUsageService, LitigeDouanierService, ArchivageDossierService,
    ProcedureUrgenteService, TransitReportingService
)
from app.models.transit_avance import BureauDouane, DossierTransitAvance, NomenclatureCEMAC

router = APIRouter(tags=["Transit Avancé"])


# ============ BUREAUX DOUANE ============
@router.post("/bureaux-douane", response_model=BureauDouaneResponse, status_code=status.HTTP_201_CREATED)
def creer_bureau_douane(
    bureau: BureauDouaneCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Create customs office"""
    return BureauDouaneService.creer_bureau_douane(
        db, bureau.code, bureau.nom, bureau.type_bureau,
        bureau.port_id, bureau.region
    )


@router.get("/bureaux-douane", response_model=List[BureauDouaneResponse])
def lister_bureaux_douane(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """List all customs offices"""
    return db.query(BureauDouane).filter(BureauDouane.statut == "actif").all()


@router.put("/bureaux-douane/{bureau_id}", response_model=BureauDouaneResponse)
def mettre_a_jour_bureau_douane(
    bureau_id: int,
    bureau: BureauDouaneUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Update customs office"""
    b = db.query(BureauDouane).filter(BureauDouane.id == bureau_id).first()
    if not b:
        raise HTTPException(status_code=404, detail="Bureau non trouvé")
    
    for field, value in bureau.model_dump(exclude_unset=True).items():
        setattr(b, field, value)
    
    db.commit()
    db.refresh(b)
    return b


# ============ DOSSIERS TRANSIT ============
@router.post("/dossiers", response_model=DossierTransitAvanceResponse, status_code=status.HTTP_201_CREATED)
def creer_dossier_transit(
    dossier: DossierTransitAvanceCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Create enhanced transit dossier"""
    return DossierTransitAvanceService.creer_dossier_transit(
        db, dossier.numero_dossier, dossier.client_id, dossier.transitaire_id,
        dossier.type_transit, dossier.regime_douanier, dossier.bureau_entree_id,
        dossier.bureau_sortie_id, dossier.marchandise, dossier.valeur_marchandise,
        dossier.pays_origine_code, dossier.pays_destination_code
    )


@router.put("/dossiers/{dossier_id}", response_model=DossierTransitAvanceResponse)
def mettre_a_jour_dossier(
    dossier_id: int,
    dossier: DossierTransitAvanceUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Update transit dossier"""
    d = db.query(DossierTransitAvance).filter(DossierTransitAvance.id == dossier_id).first()
    if not d:
        raise HTTPException(status_code=404, detail="Dossier non trouvé")
    
    for field, value in dossier.model_dump(exclude_unset=True).items():
        setattr(d, field, value)
    
    db.commit()
    db.refresh(d)
    return d


@router.put("/dossiers/{dossier_id}/cloturer", response_model=DossierTransitAvanceResponse)
def cloturer_dossier(
    dossier_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Close transit dossier"""
    return DossierTransitAvanceService.cloturer_dossier(db, dossier_id)


@router.get("/dossiers/{dossier_id}/rapport", response_model=RapportDossierResponse)
def rapport_dossier(
    dossier_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Generate complete transit dossier report"""
    return TransitReportingService.rapport_dossier(db, dossier_id)


# ============ VISITES PHYSIQUES ============
@router.post("/visites-physiques", response_model=VisitePhysiqueResponse, status_code=status.HTTP_201_CREATED)
def enregistrer_visite(
    visite: VisitePhysiqueCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Record physical inspection"""
    return VisitePhysiqueService.enregistrer_visite(
        db, visite.dossier_transit_id, visite.inspecteur_id,
        visite.type_visite, visite.rapport, visite.prelevement, visite.echantillon
    )


@router.put("/visites-physiques/{visite_id}", response_model=VisitePhysiqueResponse)
def valider_visite(
    visite_id: int,
    conforme: bool,
    observations: str = "",
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Validate inspection result"""
    return VisitePhysiqueService.valider_visite(db, visite_id, conforme, observations)


# ============ VALORISATION DOUANIERE ============
@router.post("/valorisations", response_model=ValorisationDouaniereResponse, status_code=status.HTTP_201_CREATED)
def creer_valorisation(
    valorisation: ValorisationDouaniereCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Create customs valuation"""
    return ValorisationDouaniereService.creer_valorisation(
        db, valorisation.dossier_transit_id, valorisation.methode_valorisation,
        valorisation.valeur_caf, valorisation.fret, valorisation.assurance,
        valorisation.autres_frais, valorisation.taux_change, valorisation.valide_par
    )


# ============ NOMENCLATURE CEMAC ============
@router.post("/nomenclature-cemac", response_model=NomenclatureCEMACResponse, status_code=status.HTTP_201_CREATED)
def creer_nomenclature(
    nomenclature: NomenclatureCEMACCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Create CEMAC TARIC nomenclature entry"""
    n = NomenclatureCEMAC(**nomenclature.model_dump())
    n.date_effet = n.date_effet or date.today()
    n.statut = "actif"
    # Provenance : une saisie manuelle est tracee comme telle (distincte d'un
    # import du tarif officiel), pour ne jamais masquer l'origine d'un taux.
    if not (n.source_reference or "").strip():
        n.source_reference = f"saisie manuelle ({getattr(current_user, 'username', 'inconnu')})"
    db.add(n)
    db.commit()
    db.refresh(n)
    return n


@router.get("/nomenclature-cemac/{code_hs}", response_model=NomenclatureCEMACResponse)
def obtenir_taux_taric(
    code_hs: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get tariff rates for HS code"""
    return NomenclatureCEMACService.obtenir_taux_taric(db, code_hs)


@router.get("/nomenclature-cemac/{code_hs}/droits")
def calculer_droits(
    code_hs: str,
    valeur_declaree: float,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Calculate customs duties based on HS code"""
    return NomenclatureCEMACService.calculer_droits(db, code_hs, valeur_declaree)


@router.get("/nomenclature-cemac", response_model=List[NomenclatureCEMACResponse])
def lister_nomenclature(
    search: str | None = None,
    limite: int = 100,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Liste des positions tarifaires CEMAC chargees (recherche par code SH)."""
    q = db.query(NomenclatureCEMAC)
    if search:
        q = q.filter(NomenclatureCEMAC.code_hs.like(f"{search}%"))
    return q.order_by(NomenclatureCEMAC.code_hs).limit(min(limite, 500)).all()


@router.put("/nomenclature-cemac/{code_hs}", response_model=NomenclatureCEMACResponse)
def corriger_nomenclature(
    code_hs: str,
    modifications: NomenclatureCEMACUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Corriger le taux d'une position SH, en tracant la reference officielle.

    La provenance est obligatoire a l'ecrit : une modification de taux sans
    `source_reference` identifiee est refusee (400) - on ne reecrit pas un tarif
    sans dire d'ou vient la nouvelle valeur.
    """
    if modifications.taux_dd is None and modifications.taux_tva is None:
        raise HTTPException(status_code=400, detail="Aucun taux a modifier fourni")
    if not (modifications.source_reference or "").strip():
        raise HTTPException(
            status_code=400,
            detail="source_reference officielle requise pour modifier un taux",
        )

    entry = db.query(NomenclatureCEMAC).filter(
        NomenclatureCEMAC.code_hs == code_hs
    ).first()
    if not entry:
        raise HTTPException(status_code=404, detail=f"Position SH {code_hs} inconnue")

    for champ in ("taux_dd", "taux_tva", "restrictions", "statut",
                  "date_effet", "date_fin_effet", "source_reference"):
        valeur = getattr(modifications, champ, None)
        if valeur is not None:
            setattr(entry, champ, valeur)
    entry.updated_at = datetime.utcnow()
    db.commit()
    db.refresh(entry)
    return entry


# ============ DECLARATIONS DOUANIERES ============
@router.post("/declarations", response_model=DeclarationDouaniereAvanceResponse, status_code=status.HTTP_201_CREATED)
def creer_declaration(
    declaration: DeclarationDouaniereAvanceCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Create customs declaration"""
    return DeclarationDouaniereAvanceService.creer_declaration(
        db, declaration.numero_declaration, declaration.dossier_transit_id,
        declaration.regime_douanier, declaration.bureau_douane_id,
        declaration.valeur_declaree, declaration.code_hs
    )


@router.put("/declarations/{declaration_id}/valider", response_model=DeclarationDouaniereAvanceResponse)
def valider_declaration(
    declaration_id: int,
    reference_sygdonia: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Validate customs declaration (SYDONIA+ integration)"""
    return DeclarationDouaniereAvanceService.valider_declaration(
        db, declaration_id, reference_sygdonia
    )


@router.put("/declarations/{declaration_id}/acquitter", response_model=DeclarationDouaniereAvanceResponse)
def acquitter_declaration(
    declaration_id: int,
    numero_quitus: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Acquit customs declaration after payment"""
    return DeclarationDouaniereAvanceService.acquitter_declaration(
        db, declaration_id, numero_quitus
    )


@router.put("/declarations/{declaration_id}", response_model=DeclarationDouaniereAvanceResponse)
def mettre_a_jour_declaration(
    declaration_id: int,
    declaration: DeclarationDouaniereAvanceUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Update customs declaration"""
    d = db.query(DeclarationDouaniereAvance).filter(
        DeclarationDouaniereAvance.id == declaration_id
    ).first()
    if not d:
        raise HTTPException(status_code=404, detail="Déclaration non trouvée")
    
    for field, value in declaration.model_dump(exclude_unset=True).items():
        setattr(d, field, value)
    
    db.commit()
    db.refresh(d)
    return d


# ============ LIGNES DECLARATION ============
@router.post("/lignes-declaration", response_model=LigneDeclarationResponse, status_code=status.HTTP_201_CREATED)
def ajouter_ligne(
    ligne: LigneDeclarationCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Add line to declaration"""
    return LigneDeclarationService.ajouter_ligne(
        db, ligne.declaration_id, ligne.numero_ligne, ligne.designation,
        ligne.quantite, ligne.unite, ligne.poids_net, ligne.poids_brut,
        ligne.valeur_unitaire, ligne.code_hs
    )


# ============ BONS A DEDOUANER ============
@router.post("/bons-ad", response_model=BonADResponse, status_code=status.HTTP_201_CREATED)
def emettre_bad(
    bad: BonADCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Issue bon à dédouaner"""
    return BonADService.emettre_bad(
        db, bad.numero_bad, bad.dossier_transit_id, bad.declaration_id,
        bad.signataire, bad.qualite
    )


@router.put("/bons-ad/{bad_id}", response_model=BonADResponse)
def mettre_a_jour_bad(
    bad_id: int,
    bad: BonADUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Update bon à dédouaner"""
    b = db.query(BonAD).filter(BonAD.id == bad_id).first()
    if not b:
        raise HTTPException(status_code=404, detail="BAD non trouvé")
    
    for field, value in bad.model_dump(exclude_unset=True).items():
        setattr(b, field, value)
    
    db.commit()
    db.refresh(b)
    return b


# ============ AMC ============
@router.post("/amc", response_model=AvisMiseConsommationResponse, status_code=status.HTTP_201_CREATED)
def emettre_amc(
    amc: AvisMiseConsommationCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Issue AMC - Release for consumption"""
    return AvisMiseConsommationService.emettre_amc(
        db, amc.numero_amc, amc.dossier_transit_id, amc.declaration_id,
        amc.bureau_douane_id, amc.valide_par, amc.fonction
    )


@router.put("/amc/{amc_id}", response_model=AvisMiseConsommationResponse)
def mettre_a_jour_amc(
    amc_id: int,
    amc: AvisMiseConsommationUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Update AMC"""
    a = db.query(AvisMiseConsommation).filter(AvisMiseConsommation.id == amc_id).first()
    if not a:
        raise HTTPException(status_code=404, detail="AMC non trouvé")
    
    for field, value in amc.model_dump(exclude_unset=True).items():
        setattr(a, field, value)
    
    db.commit()
    db.refresh(a)
    return a


# ============ CREDITS ENLEVEMENT ============
@router.post("/credits-enlevement", response_model=CreditEnlevementResponse, status_code=status.HTTP_201_CREATED)
def accorder_credit(
    credit: CreditEnlevementCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Grant credit d'enlèvement"""
    return CreditEnlevementService.accorder_credit(
        db, credit.numero_credit, credit.dossier_transit_id, credit.type_garantie,
        credit.garant, credit.montant_garantie, credit.date_echeance
    )


@router.put("/credits-enlevement/{credit_id}", response_model=CreditEnlevementResponse)
def mettre_a_jour_credit(
    credit_id: int,
    credit: CreditEnlevementUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Update credit d'enlèvement"""
    c = db.query(CreditEnlevement).filter(CreditEnlevement.id == credit_id).first()
    if not c:
        raise HTTPException(status_code=404, detail="Crédit non trouvé")
    
    for field, value in credit.model_dump(exclude_unset=True).items():
        setattr(c, field, value)
    
    db.commit()
    db.refresh(c)
    return c


# ============ DROITS PORT ============
@router.post("/droits-port", response_model=DroitPortResponse, status_code=status.HTTP_201_CREATED)
def calculer_droit_port(
    droit: DroitPortCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Calculate port due"""
    return DroitPortService.calculer_droit_port(
        db, droit.dossier_transit_id, droit.type_droit, droit.description,
        droit.base_calcul, droit.quantite, droit.taux
    )


@router.put("/droits-port/{droit_id}", response_model=DroitPortResponse)
def mettre_a_jour_droit_port(
    droit_id: int,
    droit: DroitPortUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Update port due"""
    d = db.query(DroitPort).filter(DroitPort.id == droit_id).first()
    if not d:
        raise HTTPException(status_code=404, detail="Droit non trouvé")
    
    for field, value in droit.model_dump(exclude_unset=True).items():
        setattr(d, field, value)
    
    db.commit()
    db.refresh(d)
    return d


# ============ TIMBRES USAGE ============
@router.post("/timbres-usage", response_model=TimbreUsageResponse, status_code=status.HTTP_201_CREATED)
def appliquer_timbre(
    timbre: TimbreUsageCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Apply stamp duty"""
    return TimbreUsageService.appliquer_timbre(
        db, timbre.dossier_transit_id, timbre.type_timbre,
        timbre.montant, timbre.numero_timbre
    )


@router.put("/timbres-usage/{timbre_id}", response_model=TimbreUsageResponse)
def mettre_a_jour_timbre(
    timbre_id: int,
    timbre: TimbreUsageUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Update stamp duty"""
    t = db.query(TimbreUsage).filter(TimbreUsage.id == timbre_id).first()
    if not t:
        raise HTTPException(status_code=404, detail="Timbre non trouvé")
    
    for field, value in timbre.model_dump(exclude_unset=True).items():
        setattr(t, field, value)
    
    db.commit()
    db.refresh(t)
    return t


# ============ LITIGES DOUANIERS ============
@router.post("/litiges", response_model=LitigeDouanierResponse, status_code=status.HTTP_201_CREATED)
def creer_litige(
    litige: LitigeDouanierCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Create customs dispute"""
    return LitigeDouanierService.creer_litige(
        db, litige.dossier_transit_id, litige.type_litige,
        litige.description, litige.montant_en_litige
    )


@router.put("/litiges/{litige_id}/resoudre", response_model=LitigeDouanierResponse)
def resoudre_litige(
    litige_id: int,
    decision: str,
    date_decision: datetime,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Resolve customs dispute"""
    return LitigeDouanierService.resoudre_litige(db, litige_id, decision, date_decision)


@router.put("/litiges/{litige_id}", response_model=LitigeDouanierResponse)
def mettre_a_jour_litige(
    litige_id: int,
    litige: LitigeDouanierUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Update customs dispute"""
    l = db.query(LitigeDouanier).filter(LitigeDouanier.id == litige_id).first()
    if not l:
        raise HTTPException(status_code=404, detail="Litige non trouvé")
    
    for field, value in litige.model_dump(exclude_unset=True).items():
        setattr(l, field, value)
    
    db.commit()
    db.refresh(l)
    return l


# ============ ARCHIVAGE DOSSIERS ============
@router.post("/archivage", response_model=ArchivageDossierResponse, status_code=status.HTTP_201_CREATED)
def archiver_dossier(
    archivage: ArchivageDossierCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Archive dossier (10-year retention)"""
    return ArchivageDossierService.archiver_dossier(
        db, archivage.dossier_transit_id, archivage.lieu_archivage,
        archivage.numero_archive, archivage.contenu
    )


@router.put("/archivage/{archivage_id}", response_model=ArchivageDossierResponse)
def mettre_a_jour_archivage(
    archivage_id: int,
    archivage: ArchivageDossierUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Update archivage"""
    a = db.query(ArchivageDossier).filter(ArchivageDossier.id == archivage_id).first()
    if not a:
        raise HTTPException(status_code=404, detail="Archivage non trouvé")
    
    for field, value in archivage.model_dump(exclude_unset=True).items():
        setattr(a, field, value)
    
    db.commit()
    db.refresh(a)
    return a


# ============ PROCEDURES URGENTES ============
@router.post("/procedures-urgentes", response_model=ProcedureUrgenteResponse, status_code=status.HTTP_201_CREATED)
def demander_procedure_urgente(
    procedure: ProcedureUrgenteCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Request urgent customs procedure"""
    return ProcedureUrgenteService.demander_procedure_urgente(
        db, procedure.dossier_transit_id, procedure.type_urgence, procedure.justification
    )


@router.put("/procedures-urgentes/{procedure_id}/autoriser", response_model=ProcedureUrgenteResponse)
def autoriser_procedure(
    procedure_id: int,
    autorise_par: str,
    fonction: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Authorize urgent procedure"""
    return ProcedureUrgenteService.autoriser_procedure(
        db, procedure_id, autorise_par, fonction
    )


@router.put("/procedures-urgentes/{procedure_id}", response_model=ProcedureUrgenteResponse)
def mettre_a_jour_procedure(
    procedure_id: int,
    procedure: ProcedureUrgenteUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Update urgent procedure"""
    p = db.query(ProcedureUrgente).filter(ProcedureUrgente.id == procedure_id).first()
    if not p:
        raise HTTPException(status_code=404, detail="Procédure non trouvée")
    
    for field, value in procedure.model_dump(exclude_unset=True).items():
        setattr(p, field, value)
    
    db.commit()
    db.refresh(p)
    return p
