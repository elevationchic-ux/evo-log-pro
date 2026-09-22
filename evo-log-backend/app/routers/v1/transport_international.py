"""Transport International router - Road transport management for Cameroon/CEMAC"""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from datetime import datetime, date

from app.core.database import get_db
from app.core.security import get_current_user
from app.models.user import User
from app.schemas.transport_international import (
    OrdreTransportCreate, OrdreTransportUpdate, OrdreTransportResponse,
    CarnetTIRCreate, CarnetTIRUpdate, CarnetTIRResponse,
    CMRCreate, CMRUpdate, CMRResponse,
    ScelleRoutierCreate, ScelleRoutierUpdate, ScelleRoutierResponse,
    PositionTransportCreate, PositionTransportResponse,
    CETSuiviCreate, CETSuiviResponse,
    AssuranceFAPCreate, AssuranceFAPUpdate, AssuranceFAPResponse,
    PlanningLivraisonCreate, PlanningLivraisonUpdate, PlanningLivraisonResponse,
    PreuveLivraisonCreate, PreuveLivraisonUpdate, PreuveLivraisonResponse,
    IncidentTransportCreate, IncidentTransportUpdate, IncidentTransportResponse,
    ControleRoutierCreate, ControleRoutierResponse,
    TaxeRoutiereCreate, TaxeRoutiereResponse,
    CorridorCEMACCreate, CorridorCEMACUpdate, CorridorCEMACResponse,
    RapportTransportResponse
)
from app.services.transport_international_service import (
    OrdreTransportService, CarnetTIRService, CMRService, ScelleRoutierService,
    PositionTransportService, CETSuiviService, AssuranceFAPService, PlanningLivraisonService,
    PreuveLivraisonService, IncidentTransportService, ControleRoutierService,
    TaxeRoutiereService, CorridorCEMACService, TransportInternationalReportingService
)
from app.models.transport_international import OrdreTransport, CarnetTIR, CMR, CorridorCEMAC

router = APIRouter(tags=["Transport International"])


# ============ ORDRES TRANSPORT ============
@router.post("/ordres-transport", response_model=OrdreTransportResponse, status_code=status.HTTP_201_CREATED)
def creer_ordre_transport(
    ot: OrdreTransportCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Create transport order"""
    return OrdreTransportService.creer_ordre_transport(
        db, ot.numero_ot, ot.client_id, ot.transporteur_id, ot.camion_id,
        ot.conducteur_id, ot.type_transit, ot.lieu_chargement, ot.lieu_livraison,
        ot.pays_destination, ot.code_pays_destination, ot.marchandise,
        ot.poids_net, ot.poids_brut, ot.nombre_colis, ot.valeur_marchandise, ot.montant_freight
    )


@router.put("/ordres-transport/{ot_id}/en-transit", response_model=OrdreTransportResponse)
def mettre_en_transit(
    ot_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Mark transport as in transit"""
    return OrdreTransportService.mettre_en_transit(db, ot_id)


@router.put("/ordres-transport/{ot_id}/livre", response_model=OrdreTransportResponse)
def marquer_livre(
    ot_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Mark transport as delivered"""
    return OrdreTransportService.marquer_livre(db, ot_id)


@router.put("/ordres-transport/{ot_id}", response_model=OrdreTransportResponse)
def mettre_a_jour_ordre(
    ot_id: int,
    ot: OrdreTransportUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Update transport order"""
    o = db.query(OrdreTransport).filter(OrdreTransport.id == ot_id).first()
    if not o:
        raise HTTPException(status_code=404, detail="Ordre de transport non trouvé")
    
    for field, value in ot.model_dump(exclude_unset=True).items():
        setattr(o, field, value)
    
    db.commit()
    db.refresh(o)
    return o


@router.get("/ordres-transport/{ot_id}/rapport", response_model=RapportTransportResponse)
def rapport_transport(
    ot_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Generate transport report"""
    return TransportInternationalReportingService.rapport_transport(db, ot_id)


# ============ CARNETS TIR ============
@router.post("/carnets-tir", response_model=CarnetTIRResponse, status_code=status.HTTP_201_CREATED)
def creer_carnet_tir(
    carnet: CarnetTIRCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Create TIR Carnet"""
    return CarnetTIRService.creer_carnet_tir(
        db, carnet.numero_carnet, carnet.ordre_transport_id,
        carnet.pays_emission, carnet.code_pays_emission,
        carnet.bureau_depart, carnet.bureau_arrivee, carnet.montant_garantie
    )


@router.put("/carnets-tir/{carnet_id}", response_model=CarnetTIRResponse)
def mettre_a_jour_carnet(
    carnet_id: int,
    carnet: CarnetTIRUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Update TIR Carnet"""
    c = db.query(CarnetTIR).filter(CarnetTIR.id == carnet_id).first()
    if not c:
        raise HTTPException(status_code=404, detail="Carnet TIR non trouvé")
    
    for field, value in carnet.model_dump(exclude_unset=True).items():
        setattr(c, field, value)
    
    db.commit()
    db.refresh(c)
    return c


# ============ CMR ============
@router.post("/cmr", response_model=CMRResponse, status_code=status.HTTP_201_CREATED)
def emettre_cmr(
    cmr: CMRCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Issue CMR"""
    return CMRService.emettre_cmr(
        db, cmr.numero_cmr, cmr.ordre_transport_id, cmr.expediteur,
        cmr.destinataire, cmr.transporteur, cmr.lieu_chargement,
        cmr.lieu_livraison, cmr.marchandise, cmr.poids_net,
        cmr.poids_brut, cmr.nombre_colis, cmr.type_emballage, cmr.valeur_marchandise
    )


@router.put("/cmr/{cmr_id}/signer", response_model=CMRResponse)
def signer_cmr(
    cmr_id: int,
    type_signature: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Sign CMR"""
    return CMRService.signer_cmr(db, cmr_id, type_signature)


@router.put("/cmr/{cmr_id}", response_model=CMRResponse)
def mettre_a_jour_cmr(
    cmr_id: int,
    cmr: CMRUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Update CMR"""
    c = db.query(CMR).filter(CMR.id == cmr_id).first()
    if not c:
        raise HTTPException(status_code=404, detail="CMR non trouvé")
    
    for field, value in cmr.model_dump(exclude_unset=True).items():
        setattr(c, field, value)
    
    db.commit()
    db.refresh(c)
    return c


# ============ SCELLES ROUTIERS ============
@router.post("/scelles-routiers", response_model=ScelleRoutierResponse, status_code=status.HTTP_201_CREATED)
def poser_scelle(
    scelle: ScelleRoutierCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Apply road seal"""
    return ScelleRoutierService.poser_scelle(
        db, scelle.numero_scelle, scelle.ordre_transport_id,
        scelle.type_scelle, scelle.emplacement, current_user.username
    )


@router.put("/scelles-routiers/{scelle_id}/verifier", response_model=ScelleRoutierResponse)
def verifier_scelle(
    scelle_id: int,
    intact: bool,
    motif_bris: str = "",
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Verify road seal"""
    return ScelleRoutierService.verifier_scelle(
        db, scelle_id, current_user.username, intact, motif_bris
    )


@router.put("/scelles-routiers/{scelle_id}", response_model=ScelleRoutierResponse)
def mettre_a_jour_scelle(
    scelle_id: int,
    scelle: ScelleRoutierUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Update road seal"""
    s = db.query(ScelleRoutier).filter(ScelleRoutier.id == scelle_id).first()
    if not s:
        raise HTTPException(status_code=404, detail="Scellé non trouvé")
    
    for field, value in scelle.model_dump(exclude_unset=True).items():
        setattr(s, field, value)
    
    db.commit()
    db.refresh(s)
    return s


# ============ POSITIONS TRANSPORT ============
@router.post("/positions", response_model=PositionTransportResponse, status_code=status.HTTP_201_CREATED)
def enregistrer_position(
    position: PositionTransportCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Record transport position"""
    return PositionTransportService.enregistrer_position(
        db, position.ordre_transport_id, position.latitude,
        position.longitude, position.vitesse_kmh, position.direction, position.statut
    )


# ============ CET SUIVI ============
@router.post("/cet-suivi", response_model=CETSuiviResponse, status_code=status.HTTP_201_CREATED)
def enregistrer_controle_cet(
    cet: CETSuiviCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Record CET control"""
    return CETSuiviService.enregistrer_controle_cet(
        db, cet.ordre_transport_id, cet.numero_cet, cet.bureau_douane,
        cet.type_controle, cet.resultat, cet.agent, cet.fonction
    )


# ============ ASSURANCE FAP ============
@router.post("/assurances-fap", response_model=AssuranceFAPResponse, status_code=status.HTTP_201_CREATED)
def creer_assurance_fap(
    assurance: AssuranceFAPCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Create FAP insurance"""
    return AssuranceFAPService.creer_assurance_fap(
        db, assurance.numero_police, assurance.ordre_transport_id,
        assurance.assureur, assurance.type_couverture,
        assurance.valeur_assuree, assurance.prime, assurance.franchise
    )


@router.put("/assurances-fap/{assurance_id}", response_model=AssuranceFAPResponse)
def mettre_a_jour_assurance_fap(
    assurance_id: int,
    assurance: AssuranceFAPUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Update FAP insurance"""
    a = db.query(AssuranceFAP).filter(AssuranceFAP.id == assurance_id).first()
    if not a:
        raise HTTPException(status_code=404, detail="Assurance FAP non trouvée")
    
    for field, value in assurance.model_dump(exclude_unset=True).items():
        setattr(a, field, value)
    
    db.commit()
    db.refresh(a)
    return a


# ============ PLANNING LIVRAISON ============
@router.post("/planning-livraison", response_model=PlanningLivraisonResponse, status_code=status.HTTP_201_CREATED)
def creer_planning(
    planning: PlanningLivraisonCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Create delivery planning"""
    return PlanningLivraisonService.creer_planning(
        db, planning.ordre_transport_id, planning.date_livraison,
        planning.heure_debut, planning.heure_fin, planning.adresse_livraison,
        planning.contact_client, planning.telephone_client,
        planning.poids_decharge, planning.duree_estimee_heures
    )


@router.put("/planning-livraison/{planning_id}", response_model=PlanningLivraisonResponse)
def mettre_a_jour_planning(
    planning_id: int,
    planning: PlanningLivraisonUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Update delivery planning"""
    p = db.query(PlanningLivraison).filter(PlanningLivraison.id == planning_id).first()
    if not p:
        raise HTTPException(status_code=404, detail="Planning non trouvé")
    
    for field, value in planning.model_dump(exclude_unset=True).items():
        setattr(p, field, value)
    
    db.commit()
    db.refresh(p)
    return p


# ============ PREUVE LIVRAISON ============
@router.post("/preuves-livraison", response_model=PreuveLivraisonResponse, status_code=status.HTTP_201_CREATED)
def enregistrer_premiere_livraison(
    pod: PreuveLivraisonCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Record proof of delivery"""
    return PreuveLivraisonService.enregistrer_premiere_livraison(
        db, pod.ordre_transport_id, pod.planning_id, pod.destinataire,
        pod.fonction, pod.colis_recus, pod.colis_refuses,
        pod.etat_marchandise, pod.latitude, pod.longitude
    )


@router.put("/preuves-livraison/{pod_id}", response_model=PreuveLivraisonResponse)
def mettre_a_jour_premiere_livraison(
    pod_id: int,
    pod: PreuveLivraisonUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Update proof of delivery"""
    p = db.query(PreuveLivraison).filter(PreuveLivraison.id == pod_id).first()
    if not p:
        raise HTTPException(status_code=404, detail="Preuve de livraison non trouvée")
    
    for field, value in pod.model_dump(exclude_unset=True).items():
        setattr(p, field, value)
    
    db.commit()
    db.refresh(p)
    return p


# ============ INCIDENTS TRANSPORT ============
@router.post("/incidents", response_model=IncidentTransportResponse, status_code=status.HTTP_201_CREATED)
def declarer_incident(
    incident: IncidentTransportCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Declare transport incident"""
    return IncidentTransportService.declarer_incident(
        db, incident.ordre_transport_id, incident.type_incident,
        incident.date_incident, incident.lieu, incident.description, incident.gravite
    )


@router.put("/incidents/{incident_id}", response_model=IncidentTransportResponse)
def mettre_a_jour_incident(
    incident_id: int,
    incident: IncidentTransportUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Update transport incident"""
    i = db.query(IncidentTransport).filter(IncidentTransport.id == incident_id).first()
    if not i:
        raise HTTPException(status_code=404, detail="Incident non trouvé")
    
    for field, value in incident.model_dump(exclude_unset=True).items():
        setattr(i, field, value)
    
    db.commit()
    db.refresh(i)
    return i


# ============ CONTROLES ROUTIERS ============
@router.post("/controles-routiers", response_model=ControleRoutierResponse, status_code=status.HTTP_201_CREATED)
def enregistrer_controle(
    controle: ControleRoutierCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Record road control"""
    return ControleRoutierService.enregistrer_controle(
        db, controle.ordre_transport_id, controle.type_controle,
        controle.date_controle, controle.lieu, controle.autorite, controle.resultat
    )


# ============ TAXES ROUTIERES ============
@router.post("/taxes-routieres", response_model=TaxeRoutiereResponse, status_code=status.HTTP_201_CREATED)
def enregistrer_taxe(
    taxe: TaxeRoutiereCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Record road tax"""
    return TaxeRoutiereService.enregistrer_taxe(
        db, taxe.ordre_transport_id, taxe.type_taxe, taxe.lieu,
        taxe.montant, taxe.numero_ticket, taxe.kilometrage
    )


# ============ CORRIDORS CEMAC ============
@router.post("/corridors-cemac", response_model=CorridorCEMACResponse, status_code=status.HTTP_201_CREATED)
def creer_corridor(
    corridor: CorridorCEMACCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Create CEMAC corridor"""
    return CorridorCEMACService.creer_corridor(
        db, corridor.nom, corridor.pays_depart, corridor.code_pays_depart,
        corridor.pays_arrivee, corridor.code_pays_arrivee,
        corridor.distance_km, corridor.duree_estimee_heures
    )


@router.put("/corridors-cemac/{corridor_id}", response_model=CorridorCEMACResponse)
def mettre_a_jour_corridor(
    corridor_id: int,
    corridor: CorridorCEMACUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Update CEMAC corridor"""
    c = db.query(CorridorCEMAC).filter(CorridorCEMAC.id == corridor_id).first()
    if not c:
        raise HTTPException(status_code=404, detail="Corridor non trouvé")
    
    for field, value in corridor.model_dump(exclude_unset=True).items():
        setattr(c, field, value)
    
    db.commit()
    db.refresh(c)
    return c
