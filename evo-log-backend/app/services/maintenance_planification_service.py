"""Moteur de planification preventive GMAO (ISO 55000 / IEC 60812).

Evalue les plans de maintenance actifs contre les releves techniques reels
(`maint_condition_readings`) et les echeances calendaires, puis genere les
ordres de travail preventifs correspondants. Regles :

  * Plan calendaire : `prochaine_echeance` depassee -> OT preventif, puis
    l'echeance est avancee d'un cran de frequence.
  * Plan a compteur (heures / km / cycles) : delta entre le dernier releve
    et `dernier_releve_compteur` >= `frequence_valeur` -> OT preventif, puis
    la baseline est recalee sur le releve courant.
  * Lubrification : `prochaine_date` depassee -> OT preventif de type
    graissage ; l'echeance avance de `frequence_jours`.

Aucune OT n'est creee sans declencheur reel : un plan sans releve
exploitables est ignore et signale dans le rapport, jamais force."""
from datetime import date, datetime, timedelta
from typing import Any, Dict, List, Optional

from sqlalchemy.orm import Session

from app.models.maintenance_deep import (
    ConditionReading, LubricationSchedule, MaintenancePlan,
    TechnicalAsset, WorkOrder,)

_UNITES_COMPTEUR = {"heure", "heures", "km", "kilometre", "kilometres", "cycle", "cycles"}
_UNITES_CALENDAIRE = {"jour", "jours", "semaine", "semaines", "mois", "an", "annee", "annees"}

_CRITICITE_VERS_PRIORITE = {"A": "P1", "B": "P2", "C": "P3"}


def _normaliser_unite(unite: Optional[str]) -> str:
    return (unite or "").strip().lower()


def _avancer_echeance(base: date, frequence_valeur: float, unite: str) -> date:
    n = int(frequence_valeur or 1)
    u = _normaliser_unite(unite)
    if u.startswith("jour"):
        return base + timedelta(days=n)
    if u.startswith("semaine"):
        return base + timedelta(weeks=n)
    if u.startswith("mois"):
        mois = base.month - 1 + n
        return date(base.year + mois // 12, mois % 12 + 1, min(base.day, 28))
    if u.startswith(("an", "annee")):
        try:
            return base.replace(year=base.year + n)
        except ValueError:  # 29 fevrier
            return base.replace(year=base.year + n, day=28)
    return base + timedelta(days=n)


def _dernier_releve(db: Session, asset_id: int, unite: str) -> Optional[ConditionReading]:
    """Dernier releve technique de l'actif, de preference sur la bonne unite."""
    q = (
        db.query(ConditionReading)
        .filter(ConditionReading.asset_id == asset_id, ConditionReading.is_active == True)  # noqa: E712
        .order_by(ConditionReading.date_lecture.desc())
    )
    if unite:
        match = q.filter(ConditionReading.unite == unite).first()
        if match:
            return match
    return q.first()


def _ot_deja_genere_aujourdhui(db: Session, plan_id: int, aujourdhui: date) -> bool:
    numero_prefixe = f"OT-PREV-{plan_id}-{aujourdhui:%Y%m%d}"
    return db.query(WorkOrder).filter(
        WorkOrder.numero_ot.like(f"{numero_prefixe}%")
    ).first() is not None


def _creer_ot_preventif(
    db: Session,
    plan: MaintenancePlan,
    asset: TechnicalAsset,
    motif: str,
    numero_suffixe: str,
    aujourdhui: date,
) -> WorkOrder:
    numero = f"OT-PREV-{plan.id}-{aujourdhui:%Y%m%d}-{numero_suffixe}"
    ot = WorkOrder(
        company_id=plan.company_id,
        numero_ot=numero,
        type_ot="preventif",
        asset_id=asset.id,
        plan_id=plan.id,
        component_id=plan.component_id,
        titre=f"Maintenance preventive — {plan.nom}",
        description=f"Declenche par le moteur de planification. Motif : {motif}",
        priorite=_CRITICITE_VERS_PRIORITE.get(
            (asset.criticite or plan.criticite or "").upper(), "P3"),
        criticite_asset=(asset.criticite or plan.criticite),
        date_detection=datetime.combine(aujourdhui, datetime.min.time()),
        date_ouverture=datetime.combine(aujourdhui, datetime.min.time()),
        statut="planifie",
        heures_prevues=plan.duree_estimee_h,
        is_active=True,
    )
    db.add(ot)
    db.flush()
    return ot


class MaintenancePlanificationService:
    """Evalue les plans et les calendriers de lubrification, genere les OT."""

    @staticmethod
    def evaluer(
        db: Session,
        company_id: Optional[int] = None,
        aujourdhui: Optional[date] = None,
    ) -> Dict[str, Any]:
        aujourdhui = aujourdhui or date.today()
        rapport: Dict[str, Any] = {
            "date_evaluation": aujourdhui.isoformat(),
            "plans_evalues": 0,
            "ots_crees": [],
            "plans_ignores": [],
            "lubrifications_declenchees": [],
            "erreurs": [],
        }

        plans = (
            db.query(MaintenancePlan)
            .filter(MaintenancePlan.is_active == True,  # noqa: E712
                    MaintenancePlan.statut == "actif")
        )
        if company_id is not None:
            plans = plans.filter(MaintenancePlan.company_id == company_id)

        for plan in plans.all():
            rapport["plans_evalues"] += 1
            try:
                MaintenancePlanificationService._evaluer_plan(db, plan, aujourdhui, rapport)
            except Exception as exc:  # un plan en echec ne bloque pas les autres
                rapport["erreurs"].append({"plan_id": plan.id, "erreur": str(exc)})

        MaintenancePlanificationService._evaluer_lubrifications(db, company_id, aujourdhui, rapport)

        db.commit()
        return rapport

    @staticmethod
    def _evaluer_plan(db: Session, plan: MaintenancePlan, aujourdhui: date, rapport: Dict[str, Any]) -> None:
        if not plan.asset_id:
            rapport["plans_ignores"].append({"plan_id": plan.id, "motif": "sans actif rattache"})
            return
        asset = db.query(TechnicalAsset).filter(TechnicalAsset.id == plan.asset_id).first()
        if not asset or not asset.is_active:
            rapport["plans_ignores"].append({"plan_id": plan.id, "motif": "actif inexistant ou inactif"})
            return
        if _ot_deja_genere_aujourdhui(db, plan.id, aujourdhui):
            rapport["plans_ignores"].append({"plan_id": plan.id, "motif": "OT deja genere aujourd'hui"})
            return

        unite = _normaliser_unite(plan.frequence_unite)
        motif = None

        if unite in _UNITES_COMPTEUR and plan.frequence_valeur:
            releve = _dernier_releve(db, asset.id, plan.frequence_unite or "")
            if releve is None or releve.valeur_principale is None:
                rapport["plans_ignores"].append({
                    "plan_id": plan.id,
                    "motif": "aucun releve technique exploitable pour ce compteur",
                })
                return
            if plan.dernier_releve_compteur is None:
 # Premiere evaluation : on cale la baseline, pas de declenchement.
                plan.dernier_releve_compteur = releve.valeur_principale
                plan.dernier_releve_date = releve.date_lecture
                return
            delta = releve.valeur_principale - plan.dernier_releve_compteur
            if delta >= (plan.frequence_valeur or 0):
                motif = (
                    f"compteur {plan.frequence_unite} : {releve.valeur_principale} "
                    f"depuis {plan.dernier_releve_compteur} (seuil {plan.frequence_valeur})"
                )
                plan.dernier_releve_compteur = releve.valeur_principale
                plan.dernier_releve_date = releve.date_lecture
        elif unite in _UNITES_CALENDAIRE or plan.prochaine_echeance:
            if plan.prochaine_echeance and plan.prochaine_echeance <= aujourdhui:
                motif = f"echeance calendaire atteinte ({plan.prochaine_echeance.isoformat()})"
                plan.prochaine_echeance = _avancer_echeance(
                    plan.prochaine_echeance, plan.frequence_valeur or 1, plan.frequence_unite or "mois")
        else:
            rapport["plans_ignores"].append({"plan_id": plan.id, "motif": "frequence non evaluable"})
            return

        if motif:
            ot = _creer_ot_preventif(db, plan, asset, motif, "PLAN", aujourdhui)
            rapport["ots_crees"].append({
                "ot_id": ot.id, "numero_ot": ot.numero_ot,
                "plan_id": plan.id, "asset_id": asset.id, "motif": motif,
            })

    @staticmethod
    def _evaluer_lubrifications(db: Session, company_id: Optional[int], aujourdhui: date, rapport: Dict[str, Any]) -> None:
        q = db.query(LubricationSchedule).filter(
            LubricationSchedule.is_active == True,  # noqa: E712
            LubricationSchedule.statut == "actif")
        if company_id is not None:
            q = q.filter(LubricationSchedule.company_id == company_id)

        for lub in q.all():
            if not lub.prochaine_date or lub.prochaine_date > aujourdhui:
                continue
            asset = db.query(TechnicalAsset).filter(TechnicalAsset.id == lub.asset_id).first()
            if not asset or not asset.is_active:
                continue
            plan = db.query(MaintenancePlan).filter(
                MaintenancePlan.company_id == lub.company_id,
                MaintenancePlan.asset_id == lub.asset_id,
                MaintenancePlan.nom.like(f"%{lub.point_lubrifiant}%"),
            ).first()
            motif = f"graissage {lub.point_lubrifiant} : echeance {lub.prochaine_date.isoformat()} atteinte"
            suffixe = f"LUB{lub.id}"
            numero = f"OT-PREV-LUB-{lub.id}-{aujourdhui:%Y%m%d}"
            if db.query(WorkOrder).filter(WorkOrder.numero_ot.like(f"{numero}%")).first():
                continue
            ot = WorkOrder(
                company_id=lub.company_id,
                numero_ot=f"{numero}-{suffixe}",
                type_ot="preventif",
                asset_id=asset.id,
                plan_id=plan.id if plan else None,
                titre=f"Graissage — {lub.point_lubrifiant} ({asset.nom})",
                description=f"Declenche par le calendrier de lubrification. {motif}. "
                            f"Type : {lub.type_lubrifiant or 'n/a'}, grade : {lub.grade or 'n/a'}, "
                            f"quantite : {lub.quantite_litre or lub.quantite_gramme or 'n/a'}.",
                priorite="P2",
                criticite_asset=asset.criticite,
                date_detection=datetime.combine(aujourdhui, datetime.min.time()),
                date_ouverture=datetime.combine(aujourdhui, datetime.min.time()),
                statut="planifie",
                is_active=True,
            )
            db.add(ot)
            db.flush()
            if lub.frequence_jours:
                lub.prochaine_date = lub.prochaine_date + timedelta(days=int(lub.frequence_jours))
            rapport["lubrifications_declenchees"].append({
                "ot_id": ot.id, "numero_ot": ot.numero_ot,
                "lubrication_id": lub.id, "point": lub.point_lubrifiant,
            })
