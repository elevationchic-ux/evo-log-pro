"""Routeur CRUD des operations portuaires approfondies (Wave 1A).

Expose 12 registres operationnels sous /api/v1/port-operations/ :
  /draft-surveys, /stevedoring-crews, /cargo-handling-plans,
  /quay-equipments, /pilotage-sessions, /towage-operations,
  /bunkering-orders, /vessel-waste-receipts, /tally-sheets,
  /demurrage-cases, /gate-passes, /yard-operations

Chaque registre : list, create, update (4 endpoints incl. get-by-id).
Les nomenclatures sont servies via /port-operations/nomenclatures.

RBAC : require_perm("port_ops.{sous_module}.{action}").
Multi-tenant : company_id injecte depuis la session utilisateur.
"""
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session
from typing import Optional, List

from app.core.database import get_db
from app.core.permissions import require_perm
from app.models.user import User
from app.models.port_operations_deep import (
    DraftSurvey, StevedoringCrew, CargoHandlingPlan, QuayEquipment,
    PilotageSession, TowageOperation, BunkeringOrder, VesselWasteReceipt,
    TallySheet, DemurrageCase, GatePass, YardOperation,
    TypeAvarie, GraviteAvarie, StatutConstat, TypeEquipage, StatutGang,
    TypeOperationQuai, StatutPlanManutention, TypeEquipement, EtatEquipement,
    StatutPilotage, TypeSoute, TypeDechet, StatutGatePass, TypeMouvementYard,
)
from app.schemas.port_operations_deep import (
    DraftSurveyCreate, DraftSurveyUpdate, DraftSurveyOut,
    StevedoringCrewCreate, StevedoringCrewUpdate, StevedoringCrewOut,
    CargoHandlingPlanCreate, CargoHandlingPlanUpdate, CargoHandlingPlanOut,
    QuayEquipmentCreate, QuayEquipmentUpdate, QuayEquipmentOut,
    PilotageSessionCreate, PilotageSessionUpdate, PilotageSessionOut,
    TowageOperationCreate, TowageOperationUpdate, TowageOperationOut,
    BunkeringOrderCreate, BunkeringOrderUpdate, BunkeringOrderOut,
    VesselWasteReceiptCreate, VesselWasteReceiptUpdate, VesselWasteReceiptOut,
    TallySheetCreate, TallySheetUpdate, TallySheetOut,
    DemurrageCaseCreate, DemurrageCaseUpdate, DemurrageCaseOut,
    GatePassCreate, GatePassUpdate, GatePassOut,
    YardOperationCreate, YardOperationUpdate, YardOperationOut,
)

router = APIRouter(tags=["Operations portuaires approfondies"])


# ─── Helpers generiques ──────────────────────────────────────────────────────

def _enum_catalog(cls):
    return [{"code": m.name, "valeur": m.value} for m in cls]


def _get_or_404(db: Session, model, ident: int, label: str):
    row = db.query(model).filter(model.id == ident).first()
    if not row:
        raise HTTPException(status_code=404, detail=f"{label} introuvable (id={ident})")
    return row


def _check_unique(db: Session, model, field: str, value, label: str, company_id: int, exclude_id=None):
    if value is None:
        return
    q = db.query(model).filter(getattr(model, field) == value, model.company_id == company_id)
    if exclude_id is not None:
        q = q.filter(model.id != exclude_id)
    if q.first():
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=f"{label} « {value} » existe deja dans votre organisation.",
        )


def _scoped_list(db, model, company_id, filters=None, order_col=None):
    q = db.query(model).filter(model.company_id == company_id)
    if hasattr(model, 'is_active'):
        q = q.filter(model.is_active.is_(True))
    if filters:
        for key, val in filters.items():
            if val is not None and hasattr(model, key):
                q = q.filter(getattr(model, key) == val)
    if order_col and hasattr(model, order_col):
        q = q.order_by(getattr(model, order_col).desc())
    else:
        q = q.order_by(model.id.desc())
    return q.all()


def _apply(payload: dict, obj):
    for key, value in payload.items():
        setattr(obj, key, value)


def _company_id(user: User) -> int:
    if not user.company_id:
        raise HTTPException(status_code=400, detail="Votre compte n'est rattache a aucune organisation.")
    return user.company_id


# ─── Nomenclatures ───────────────────────────────────────────────────────────

@router.get("/nomenclatures", summary="Vocabulaire metier des operations portuaires")
def nomenclatures(user: User = Depends(require_perm("port_ops.vessel_registry.read"))):
    return {
        "type_avarie": _enum_catalog(TypeAvarie),
        "gravite_avarie": _enum_catalog(GraviteAvarie),
        "statut_constat": _enum_catalog(StatutConstat),
        "type_equipage": _enum_catalog(TypeEquipage),
        "statut_gang": _enum_catalog(StatutGang),
        "type_operation_quai": _enum_catalog(TypeOperationQuai),
        "statut_plan_manutention": _enum_catalog(StatutPlanManutention),
        "type_equipement": _enum_catalog(TypeEquipement),
        "etat_equipement": _enum_catalog(EtatEquipement),
        "statut_pilotage": _enum_catalog(StatutPilotage),
        "type_soute": _enum_catalog(TypeSoute),
        "type_dechet": _enum_catalog(TypeDechet),
        "statut_gate_pass": _enum_catalog(StatutGatePass),
        "type_mouvement_yard": _enum_catalog(TypeMouvementYard),
    }


# ─── 1. Draft Surveys ────────────────────────────────────────────────────────

@router.get("/draft-surveys", response_model=List[DraftSurveyOut])
def list_draft_surveys(
    statut: Optional[str] = None,
    navire_id: Optional[int] = None,
    db: Session = Depends(get_db),
    user: User = Depends(require_perm("port_ops.draft_survey.read")),
):
    cid = _company_id(user)
    return _scoped_list(db, DraftSurvey, cid, {"statut": statut, "navire_id": navire_id})


@router.post("/draft-surveys", response_model=DraftSurveyOut, status_code=201)
def create_draft_survey(
    payload: DraftSurveyCreate,
    db: Session = Depends(get_db),
    user: User = Depends(require_perm("port_ops.draft_survey.create")),
):
    cid = _company_id(user)
    data = payload.model_dump(exclude_unset=True)
    _check_unique(db, DraftSurvey, "numero_constat", data.get("numero_constat"), "Numero de constat", cid)
    obj = DraftSurvey(company_id=cid)
    _apply(data, obj)
    db.add(obj)
    db.commit()
    db.refresh(obj)
    return obj


@router.put("/draft-surveys/{ident}", response_model=DraftSurveyOut)
def update_draft_survey(
    ident: int,
    payload: DraftSurveyUpdate,
    db: Session = Depends(get_db),
    user: User = Depends(require_perm("port_ops.draft_survey.modify")),
):
    cid = _company_id(user)
    obj = _get_or_404(db, DraftSurvey, ident, "Constat")
    if obj.company_id != cid:
        raise HTTPException(403, "Acces refuse.")
    _apply(payload.model_dump(exclude_unset=True), obj)
    db.commit()
    db.refresh(obj)
    return obj


# ─── 2. Stevedoring Crews ────────────────────────────────────────────────────

@router.get("/stevedoring-crews", response_model=List[StevedoringCrewOut])
def list_crews(
    statut: Optional[str] = None,
    type_equipe: Optional[str] = None,
    db: Session = Depends(get_db),
    user: User = Depends(require_perm("port_ops.stevedoring_crew.read")),
):
    cid = _company_id(user)
    return _scoped_list(db, StevedoringCrew, cid, {"statut": statut, "type_equipe": type_equipe})


@router.post("/stevedoring-crews", response_model=StevedoringCrewOut, status_code=201)
def create_crew(
    payload: StevedoringCrewCreate,
    db: Session = Depends(get_db),
    user: User = Depends(require_perm("port_ops.stevedoring_crew.create")),
):
    cid = _company_id(user)
    data = payload.model_dump(exclude_unset=True)
    _check_unique(db, StevedoringCrew, "code_gang", data.get("code_gang"), "Code gang", cid)
    obj = StevedoringCrew(company_id=cid)
    _apply(data, obj)
    db.add(obj)
    db.commit()
    db.refresh(obj)
    return obj


@router.put("/stevedoring-crews/{ident}", response_model=StevedoringCrewOut)
def update_crew(
    ident: int, payload: StevedoringCrewUpdate,
    db: Session = Depends(get_db),
    user: User = Depends(require_perm("port_ops.stevedoring_crew.modify")),
):
    cid = _company_id(user)
    obj = _get_or_404(db, StevedoringCrew, ident, "Gang")
    if obj.company_id != cid:
        raise HTTPException(403, "Acces refuse.")
    _apply(payload.model_dump(exclude_unset=True), obj)
    db.commit()
    db.refresh(obj)
    return obj


# ─── 3. Cargo Handling Plans ─────────────────────────────────────────────────

@router.get("/cargo-handling-plans", response_model=List[CargoHandlingPlanOut])
def list_cargo_plans(
    statut: Optional[str] = None,
    type_operation: Optional[str] = None,
    escale_id: Optional[int] = None,
    db: Session = Depends(get_db),
    user: User = Depends(require_perm("port_ops.cargo_plan.read")),
):
    cid = _company_id(user)
    return _scoped_list(db, CargoHandlingPlan, cid, {"statut": statut, "type_operation": type_operation, "escale_id": escale_id})


@router.post("/cargo-handling-plans", response_model=CargoHandlingPlanOut, status_code=201)
def create_cargo_plan(
    payload: CargoHandlingPlanCreate,
    db: Session = Depends(get_db),
    user: User = Depends(require_perm("port_ops.cargo_plan.create")),
):
    cid = _company_id(user)
    data = payload.model_dump(exclude_unset=True)
    _check_unique(db, CargoHandlingPlan, "reference_plan", data.get("reference_plan"), "Reference plan", cid)
    obj = CargoHandlingPlan(company_id=cid)
    _apply(data, obj)
    db.add(obj)
    db.commit()
    db.refresh(obj)
    return obj


@router.put("/cargo-handling-plans/{ident}", response_model=CargoHandlingPlanOut)
def update_cargo_plan(
    ident: int, payload: CargoHandlingPlanUpdate,
    db: Session = Depends(get_db),
    user: User = Depends(require_perm("port_ops.cargo_plan.modify")),
):
    cid = _company_id(user)
    obj = _get_or_404(db, CargoHandlingPlan, ident, "Plan manutention")
    if obj.company_id != cid:
        raise HTTPException(403, "Acces refuse.")
    _apply(payload.model_dump(exclude_unset=True), obj)
    db.commit()
    db.refresh(obj)
    return obj


# ─── 4. Quay Equipment ───────────────────────────────────────────────────────

@router.get("/quay-equipments", response_model=List[QuayEquipmentOut])
def list_quay_equipments(
    type_equipement: Optional[str] = None,
    etat: Optional[str] = None,
    db: Session = Depends(get_db),
    user: User = Depends(require_perm("port_ops.quay_equipment.read")),
):
    cid = _company_id(user)
    return _scoped_list(db, QuayEquipment, cid, {"type_equipement": type_equipement, "etat": etat})


@router.post("/quay-equipments", response_model=QuayEquipmentOut, status_code=201)
def create_quay_equipment(
    payload: QuayEquipmentCreate,
    db: Session = Depends(get_db),
    user: User = Depends(require_perm("port_ops.quay_equipment.create")),
):
    cid = _company_id(user)
    data = payload.model_dump(exclude_unset=True)
    _check_unique(db, QuayEquipment, "code_equipement", data.get("code_equipement"), "Code equipement", cid)
    obj = QuayEquipment(company_id=cid)
    _apply(data, obj)
    db.add(obj)
    db.commit()
    db.refresh(obj)
    return obj


@router.put("/quay-equipments/{ident}", response_model=QuayEquipmentOut)
def update_quay_equipment(
    ident: int, payload: QuayEquipmentUpdate,
    db: Session = Depends(get_db),
    user: User = Depends(require_perm("port_ops.quay_equipment.modify")),
):
    cid = _company_id(user)
    obj = _get_or_404(db, QuayEquipment, ident, "Equipement")
    if obj.company_id != cid:
        raise HTTPException(403, "Acces refuse.")
    _apply(payload.model_dump(exclude_unset=True), obj)
    db.commit()
    db.refresh(obj)
    return obj


# ─── 5. Pilotage Sessions ────────────────────────────────────────────────────

@router.get("/pilotage-sessions", response_model=List[PilotageSessionOut])
def list_pilotage(
    statut: Optional[str] = None,
    navire_id: Optional[int] = None,
    db: Session = Depends(get_db),
    user: User = Depends(require_perm("port_ops.pilotage.read")),
):
    cid = _company_id(user)
    return _scoped_list(db, PilotageSession, cid, {"statut": statut, "navire_id": navire_id})


@router.post("/pilotage-sessions", response_model=PilotageSessionOut, status_code=201)
def create_pilotage(
    payload: PilotageSessionCreate,
    db: Session = Depends(get_db),
    user: User = Depends(require_perm("port_ops.pilotage.create")),
):
    cid = _company_id(user)
    data = payload.model_dump(exclude_unset=True)
    _check_unique(db, PilotageSession, "reference", data.get("reference"), "Reference pilotage", cid)
    obj = PilotageSession(company_id=cid)
    _apply(data, obj)
    db.add(obj)
    db.commit()
    db.refresh(obj)
    return obj


@router.put("/pilotage-sessions/{ident}", response_model=PilotageSessionOut)
def update_pilotage(
    ident: int, payload: PilotageSessionUpdate,
    db: Session = Depends(get_db),
    user: User = Depends(require_perm("port_ops.pilotage.modify")),
):
    cid = _company_id(user)
    obj = _get_or_404(db, PilotageSession, ident, "Session pilotage")
    if obj.company_id != cid:
        raise HTTPException(403, "Acces refuse.")
    _apply(payload.model_dump(exclude_unset=True), obj)
    db.commit()
    db.refresh(obj)
    return obj


# ─── 6. Towage Operations ────────────────────────────────────────────────────

@router.get("/towage-operations", response_model=List[TowageOperationOut])
def list_towage(
    statut: Optional[str] = None,
    db: Session = Depends(get_db),
    user: User = Depends(require_perm("port_ops.towage.read")),
):
    cid = _company_id(user)
    return _scoped_list(db, TowageOperation, cid, {"statut": statut})


@router.post("/towage-operations", response_model=TowageOperationOut, status_code=201)
def create_towage(
    payload: TowageOperationCreate,
    db: Session = Depends(get_db),
    user: User = Depends(require_perm("port_ops.towage.create")),
):
    cid = _company_id(user)
    data = payload.model_dump(exclude_unset=True)
    _check_unique(db, TowageOperation, "reference", data.get("reference"), "Reference remorquage", cid)
    obj = TowageOperation(company_id=cid)
    _apply(data, obj)
    db.add(obj)
    db.commit()
    db.refresh(obj)
    return obj


@router.put("/towage-operations/{ident}", response_model=TowageOperationOut)
def update_towage(
    ident: int, payload: TowageOperationUpdate,
    db: Session = Depends(get_db),
    user: User = Depends(require_perm("port_ops.towage.modify")),
):
    cid = _company_id(user)
    obj = _get_or_404(db, TowageOperation, ident, "Operation remorquage")
    if obj.company_id != cid:
        raise HTTPException(403, "Acces refuse.")
    _apply(payload.model_dump(exclude_unset=True), obj)
    db.commit()
    db.refresh(obj)
    return obj


# ─── 7. Bunkering Orders ─────────────────────────────────────────────────────

@router.get("/bunkering-orders", response_model=List[BunkeringOrderOut])
def list_bunkering(
    statut: Optional[str] = None,
    type_carburant: Optional[str] = None,
    db: Session = Depends(get_db),
    user: User = Depends(require_perm("port_ops.bunkering.read")),
):
    cid = _company_id(user)
    return _scoped_list(db, BunkeringOrder, cid, {"statut": statut, "type_carburant": type_carburant})


@router.post("/bunkering-orders", response_model=BunkeringOrderOut, status_code=201)
def create_bunkering(
    payload: BunkeringOrderCreate,
    db: Session = Depends(get_db),
    user: User = Depends(require_perm("port_ops.bunkering.create")),
):
    cid = _company_id(user)
    data = payload.model_dump(exclude_unset=True)
    _check_unique(db, BunkeringOrder, "reference", data.get("reference"), "Reference soute", cid)
    obj = BunkeringOrder(company_id=cid)
    _apply(data, obj)
    db.add(obj)
    db.commit()
    db.refresh(obj)
    return obj


@router.put("/bunkering-orders/{ident}", response_model=BunkeringOrderOut)
def update_bunkering(
    ident: int, payload: BunkeringOrderUpdate,
    db: Session = Depends(get_db),
    user: User = Depends(require_perm("port_ops.bunkering.modify")),
):
    cid = _company_id(user)
    obj = _get_or_404(db, BunkeringOrder, ident, "Ordre soute")
    if obj.company_id != cid:
        raise HTTPException(403, "Acces refuse.")
    _apply(payload.model_dump(exclude_unset=True), obj)
    db.commit()
    db.refresh(obj)
    return obj


# ─── 8. Vessel Waste Receipts ────────────────────────────────────────────────

@router.get("/vessel-waste-receipts", response_model=List[VesselWasteReceiptOut])
def list_waste(
    type_dechet: Optional[str] = None,
    navire_id: Optional[int] = None,
    db: Session = Depends(get_db),
    user: User = Depends(require_perm("port_ops.vessel_waste.read")),
):
    cid = _company_id(user)
    return _scoped_list(db, VesselWasteReceipt, cid, {"type_dechet": type_dechet, "navire_id": navire_id})


@router.post("/vessel-waste-receipts", response_model=VesselWasteReceiptOut, status_code=201)
def create_waste(
    payload: VesselWasteReceiptCreate,
    db: Session = Depends(get_db),
    user: User = Depends(require_perm("port_ops.vessel_waste.create")),
):
    cid = _company_id(user)
    data = payload.model_dump(exclude_unset=True)
    _check_unique(db, VesselWasteReceipt, "reference", data.get("reference"), "Reference dechet", cid)
    obj = VesselWasteReceipt(company_id=cid)
    _apply(data, obj)
    db.add(obj)
    db.commit()
    db.refresh(obj)
    return obj


@router.put("/vessel-waste-receipts/{ident}", response_model=VesselWasteReceiptOut)
def update_waste(
    ident: int, payload: VesselWasteReceiptUpdate,
    db: Session = Depends(get_db),
    user: User = Depends(require_perm("port_ops.vessel_waste.modify")),
):
    cid = _company_id(user)
    obj = _get_or_404(db, VesselWasteReceipt, ident, "Recu dechet")
    if obj.company_id != cid:
        raise HTTPException(403, "Acces refuse.")
    _apply(payload.model_dump(exclude_unset=True), obj)
    db.commit()
    db.refresh(obj)
    return obj


# ─── 9. Tally Sheets ─────────────────────────────────────────────────────────

@router.get("/tally-sheets", response_model=List[TallySheetOut])
def list_tally(
    type_operation: Optional[str] = None,
    escale_id: Optional[int] = None,
    valide: Optional[bool] = None,
    db: Session = Depends(get_db),
    user: User = Depends(require_perm("port_ops.tally.read")),
):
    cid = _company_id(user)
    return _scoped_list(db, TallySheet, cid, {"type_operation": type_operation, "escale_id": escale_id, "valide": valide})


@router.post("/tally-sheets", response_model=TallySheetOut, status_code=201)
def create_tally(
    payload: TallySheetCreate,
    db: Session = Depends(get_db),
    user: User = Depends(require_perm("port_ops.tally.create")),
):
    cid = _company_id(user)
    data = payload.model_dump(exclude_unset=True)
    _check_unique(db, TallySheet, "reference", data.get("reference"), "Reference tally", cid)
    obj = TallySheet(company_id=cid)
    _apply(data, obj)
    db.add(obj)
    db.commit()
    db.refresh(obj)
    return obj


@router.put("/tally-sheets/{ident}", response_model=TallySheetOut)
def update_tally(
    ident: int, payload: TallySheetUpdate,
    db: Session = Depends(get_db),
    user: User = Depends(require_perm("port_ops.tally.modify")),
):
    cid = _company_id(user)
    obj = _get_or_404(db, TallySheet, ident, "Feuille tally")
    if obj.company_id != cid:
        raise HTTPException(403, "Acces refuse.")
    _apply(payload.model_dump(exclude_unset=True), obj)
    db.commit()
    db.refresh(obj)
    return obj


# ─── 10. Demurrage Cases ─────────────────────────────────────────────────────

@router.get("/demurrage-cases", response_model=List[DemurrageCaseOut])
def list_demurrage(
    statut: Optional[str] = None,
    client_id: Optional[int] = None,
    db: Session = Depends(get_db),
    user: User = Depends(require_perm("port_ops.demurrage.read")),
):
    cid = _company_id(user)
    return _scoped_list(db, DemurrageCase, cid, {"statut": statut, "client_id": client_id})


@router.post("/demurrage-cases", response_model=DemurrageCaseOut, status_code=201)
def create_demurrage(
    payload: DemurrageCaseCreate,
    db: Session = Depends(get_db),
    user: User = Depends(require_perm("port_ops.demurrage.create")),
):
    cid = _company_id(user)
    data = payload.model_dump(exclude_unset=True)
    _check_unique(db, DemurrageCase, "reference", data.get("reference"), "Reference surestarie", cid)
    obj = DemurrageCase(company_id=cid)
    _apply(data, obj)
    db.add(obj)
    db.commit()
    db.refresh(obj)
    return obj


@router.put("/demurrage-cases/{ident}", response_model=DemurrageCaseOut)
def update_demurrage(
    ident: int, payload: DemurrageCaseUpdate,
    db: Session = Depends(get_db),
    user: User = Depends(require_perm("port_ops.demurrage.modify")),
):
    cid = _company_id(user)
    obj = _get_or_404(db, DemurrageCase, ident, "Dossier surestarie")
    if obj.company_id != cid:
        raise HTTPException(403, "Acces refuse.")
    _apply(payload.model_dump(exclude_unset=True), obj)
    db.commit()
    db.refresh(obj)
    return obj


# ─── 11. Gate Passes ─────────────────────────────────────────────────────────

@router.get("/gate-passes", response_model=List[GatePassOut])
def list_gate_passes(
    statut: Optional[str] = None,
    conteneur_id: Optional[int] = None,
    db: Session = Depends(get_db),
    user: User = Depends(require_perm("port_ops.gate_pass.read")),
):
    cid = _company_id(user)
    return _scoped_list(db, GatePass, cid, {"statut": statut, "conteneur_id": conteneur_id})


@router.post("/gate-passes", response_model=GatePassOut, status_code=201)
def create_gate_pass(
    payload: GatePassCreate,
    db: Session = Depends(get_db),
    user: User = Depends(require_perm("port_ops.gate_pass.create")),
):
    cid = _company_id(user)
    data = payload.model_dump(exclude_unset=True)
    _check_unique(db, GatePass, "numero_gate", data.get("numero_gate"), "Numero gate pass", cid)
    obj = GatePass(company_id=cid)
    _apply(data, obj)
    db.add(obj)
    db.commit()
    db.refresh(obj)
    return obj


@router.put("/gate-passes/{ident}", response_model=GatePassOut)
def update_gate_pass(
    ident: int, payload: GatePassUpdate,
    db: Session = Depends(get_db),
    user: User = Depends(require_perm("port_ops.gate_pass.modify")),
):
    cid = _company_id(user)
    obj = _get_or_404(db, GatePass, ident, "Gate pass")
    if obj.company_id != cid:
        raise HTTPException(403, "Acces refuse.")
    _apply(payload.model_dump(exclude_unset=True), obj)
    db.commit()
    db.refresh(obj)
    return obj


# ─── 12. Yard Operations ─────────────────────────────────────────────────────

@router.get("/yard-operations", response_model=List[YardOperationOut])
def list_yard_ops(
    type_mouvement: Optional[str] = None,
    conteneur_id: Optional[int] = None,
    statut: Optional[str] = None,
    db: Session = Depends(get_db),
    user: User = Depends(require_perm("port_ops.yard.read")),
):
    cid = _company_id(user)
    return _scoped_list(db, YardOperation, cid, {"type_mouvement": type_mouvement, "conteneur_id": conteneur_id, "statut": statut})


@router.post("/yard-operations", response_model=YardOperationOut, status_code=201)
def create_yard_op(
    payload: YardOperationCreate,
    db: Session = Depends(get_db),
    user: User = Depends(require_perm("port_ops.yard.create")),
):
    cid = _company_id(user)
    data = payload.model_dump(exclude_unset=True)
    _check_unique(db, YardOperation, "reference", data.get("reference"), "Reference mouvement yard", cid)
    obj = YardOperation(company_id=cid)
    _apply(data, obj)
    db.add(obj)
    db.commit()
    db.refresh(obj)
    return obj


@router.put("/yard-operations/{ident}", response_model=YardOperationOut)
def update_yard_op(
    ident: int, payload: YardOperationUpdate,
    db: Session = Depends(get_db),
    user: User = Depends(require_perm("port_ops.yard.modify")),
):
    cid = _company_id(user)
    obj = _get_or_404(db, YardOperation, ident, "Mouvement yard")
    if obj.company_id != cid:
        raise HTTPException(403, "Acces refuse.")
    _apply(payload.model_dump(exclude_unset=True), obj)
    db.commit()
    db.refresh(obj)
    return obj
