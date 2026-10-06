"""QHSE service - Quality, Health, Safety, Environment management for Cameroon/CEMAC"""
from datetime import datetime, date, timedelta
from typing import List, Optional, Dict, Any
from sqlalchemy.orm import Session
from sqlalchemy import and_, func
from app.core.not_implemented import not_implemented
from app.models.qhse import (
    AnalyseRisque, ActionPrevention, PlanPrevention, EPIRequis,
    AccidentTravail, InvestigationAccident, NormeCertification, AuditQualite,
    HACCPPlan, PointCritiqueCCP, EnregistrementHACCP, FormationQHSE, IndicateurQHSE,
    TypeRisque, GraviteRisque, TypeEPI, StatutAccident, NormeISO
)


class AnalyseRisqueService:
    """Risk analysis service"""
    
    @staticmethod
    def creer_analyse_risque(
        db: Session,
        numero_analyse: str,
        zone: str,
        processus: str,
        type_risque: TypeRisque,
        description_danger: str,
        causes_potentielles: str,
        consequences: str,
        population_exposee: int,
        frequence: str,
        gravite: GraviteRisque,
        probabilite: int
    ) -> AnalyseRisque:
        """Create risk analysis"""
        # Calculate risk level
        risque_calcule = probabilite * (5 if gravite == GraviteRisque.CATASTROPHIQUE else
                                       4 if gravite == GraviteRisque.CRITIQUE else
                                       3 if gravite == GraviteRisque.MAJEUR else
                                       2 if gravite == GraviteRisque.MODERE else
                                       1 if gravite == GraviteRisque.MINEUR else 0)
        
        if risque_calcule >= 15:
            niveau_risque = "critique"
        elif risque_calcule >= 10:
            niveau_risque = "eleve"
        elif risque_calcule >= 5:
            niveau_risque = "moyen"
        else:
            niveau_risque = "faible"
        
        analyse = AnalyseRisque(
            numero_analyse=numero_analyse,
            zone=zone,
            processus=processus,
            date_analyse=date.today(),
            type_risque=type_risque,
            description_danger=description_danger,
            causes_potentielles=causes_potentielles,
            consequences=consequences,
            population_exposee=population_exposee,
            frequence=frequence,
            gravite=gravite,
            probabilite=probabilite,
            risque_calcule=risque_calcule,
            niveau_risque=niveau_risque,
            statut="actif"
        )
        db.add(analyse)
        db.commit()
        db.refresh(analyse)
        return analyse


class ActionPreventionService:
    """Prevention action service"""
    
    @staticmethod
    def creer_action_prevention(
        db: Session,
        numero_action: str,
        analyse_risque_id: int,
        type_action: str,
        description: str,
        priorite: str,
        responsable: str,
        date_prevue: date
    ) -> ActionPrevention:
        """Create prevention action"""
        action = ActionPrevention(
            numero_action=numero_action,
            analyse_risque_id=analyse_risque_id,
            type_action=type_action,
            description=description,
            priorite=priorite,
            responsable=responsable,
            date_prevue=date_prevue,
            statut="en_attente"
        )
        db.add(action)
        db.commit()
        db.refresh(action)
        return action


class PlanPreventionService:
    """Prevention plan service"""
    
    @staticmethod
    def creer_plan_prevention(
        db: Session,
        numero_plan: str,
        type_activite: str,
        zone: str,
        date_debut: date,
        date_fin: date,
        responsable: str,
        description: str
    ) -> PlanPrevention:
        """Create prevention plan"""
        plan = PlanPrevention(
            numero_plan=numero_plan,
            type_activite=type_activite,
            zone=zone,
            date_debut=date_debut,
            date_fin=date_fin,
            responsable=responsable,
            description=description,
            statut="en_cours"
        )
        db.add(plan)
        db.commit()
        db.refresh(plan)
        return plan


class EPIRequisService:
    """Required PPE service"""
    
    @staticmethod
    def ajouter_epi(
        db: Session,
        plan_prevention_id: int,
        type_epi: TypeEPI,
        designation: str,
        quantite: int,
        norme: str
    ) -> EPIRequis:
        """Add required PPE"""
        epi = EPIRequis(
            plan_prevention_id=plan_prevention_id,
            type_epi=type_epi,
            designation=designation,
            quantite=quantite,
            norme=norme,
            statut="disponible"
        )
        db.add(epi)
        db.commit()
        db.refresh(epi)
        return epi


class AccidentTravailService:
    """Work accident service"""
    
    @staticmethod
    def declarer_accident(
        db: Session,
        numero_accident: str,
        employe_id: int,
        date_accident: datetime,
        lieu: str,
        type_accident: str,
        description: str,
        gravite: str
    ) -> AccidentTravail:
        """Declare work accident"""
        accident = AccidentTravail(
            numero_accident=numero_accident,
            employe_id=employe_id,
            date_accident=date_accident,
            lieu=lieu,
            type_accident=type_accident,
            description=description,
            gravite=gravite,
            statut=StatutAccident.SIGNALE,
            date_declaration=date.today()
        )
        db.add(accident)
        db.commit()
        db.refresh(accident)
        return accident


class InvestigationAccidentService:
    """Accident investigation service"""
    
    @staticmethod
    def creer_investigation(
        db: Session,
        accident_id: int,
        numero_investigation: str,
        date_investigation: date,
        investigateur: str
    ) -> InvestigationAccident:
        """Create accident investigation"""
        investigation = InvestigationAccident(
            accident_id=accident_id,
            numero_investigation=numero_investigation,
            date_investigation=date_investigation,
            investigateur=investigateur,
            statut="en_cours"
        )
        db.add(investigation)
        db.commit()
        db.refresh(investigation)
        return investigation


class NormeCertificationService:
    """ISO certification service"""
    
    @staticmethod
    def creer_certification(
        db: Session,
        numero_certificat: str,
        norme: NormeISO,
        organisme: str,
        date_obtention: date,
        date_expiration: date,
        scope: str
    ) -> NormeCertification:
        """Create ISO certification"""
        certification = NormeCertification(
            numero_certificat=numero_certificat,
            norme=norme,
            organisme=organisme,
            date_obtention=date_obtention,
            date_expiration=date_expiration,
            scope=scope,
            statut="actif"
        )
        db.add(certification)
        db.commit()
        db.refresh(certification)
        return certification


class AuditQualiteService:
    """Quality audit service"""
    
    @staticmethod
    def creer_audit(
        db: Session,
        numero_audit: str,
        certification_id: int,
        type_audit: str,
        date_debut: date,
        date_fin: date,
        auditeur: str
    ) -> AuditQualite:
        """Create quality audit"""
        audit = AuditQualite(
            numero_audit=numero_audit,
            certification_id=certification_id,
            type_audit=type_audit,
            date_debut=date_debut,
            date_fin=date_fin,
            auditeur=auditeur,
            statut="en_cours"
        )
        db.add(audit)
        db.commit()
        db.refresh(audit)
        return audit


class HACCPPlanService:
    """HACCP plan service"""
    
    @staticmethod
    def creer_plan_haccp(
        db: Session,
        numero_plan: str,
        produit: str,
        processus: str,
        responsable: str
    ) -> HACCPPlan:
        """Create HACCP plan"""
        plan = HACCPPlan(
            numero_plan=numero_plan,
            produit=produit,
            processus=processus,
            date_creation=date.today(),
            responsable=responsable,
            statut="actif"
        )
        db.add(plan)
        db.commit()
        db.refresh(plan)
        return plan


class PointCritiqueCCPService:
    """Critical Control Point service"""
    
    @staticmethod
    def ajouter_ccp(
        db: Session,
        haccp_plan_id: int,
        numero_ccp: str,
        etape: str,
        danger: str,
        limites_critiques: str,
        surveillance: str
    ) -> PointCritiqueCCP:
        """Add critical control point"""
        ccp = PointCritiqueCCP(
            haccp_plan_id=haccp_plan_id,
            numero_ccp=numero_ccp,
            etape=etape,
            danger=danger,
            limites_critiques=limites_critiques,
            surveillance=surveillance,
            statut="actif"
        )
        db.add(ccp)
        db.commit()
        db.refresh(ccp)
        return ccp


class EnregistrementHACCPService:
    """HACCP record service"""
    
    @staticmethod
    def enregistrer_controle(
        db: Session,
        point_critique_id: int,
        valeur_mesuree: float,
        unite: str,
        operateur: str
    ) -> EnregistrementHACCP:
        """Record HACCP control"""
        enregistrement = EnregistrementHACCP(
            point_critique_id=point_critique_id,
            date_enregistrement=datetime.utcnow(),
            valeur_mesuree=valeur_mesuree,
            unite=unite,
            conforme=True,
            operateur=operateur
        )
        db.add(enregistrement)
        db.commit()
        db.refresh(enregistrement)
        return enregistrement


class FormationQHSEService:
    """QHSE training service"""
    
    @staticmethod
    def creer_formation(
        db: Session,
        numero_formation: str,
        type_formation: str,
        titre: str,
        formateur: str,
        date_debut: date,
        date_fin: date,
        duree_heures: int
    ) -> FormationQHSE:
        """Create QHSE training"""
        formation = FormationQHSE(
            numero_formation=numero_formation,
            type_formation=type_formation,
            titre=titre,
            formateur=formateur,
            date_debut=date_debut,
            date_fin=date_fin,
            duree_heures=duree_heures,
            statut="planifie"
        )
        db.add(formation)
        db.commit()
        db.refresh(formation)
        return formation


class IndicateurQHSEService:
    """QHSE indicator service"""
    
    @staticmethod
    def creer_indicateur(
        db: Session,
        code: str,
        nom: str,
        type_indicateur: str,
        unite: str,
        objectif: float
    ) -> IndicateurQHSE:
        """Create QHSE indicator"""
        indicateur = IndicateurQHSE(
            code=code,
            nom=nom,
            type_indicateur=type_indicateur,
            unite=unite,
            objectif=objectif,
            statut="actif"
        )
        db.add(indicateur)
        db.commit()
        db.refresh(indicateur)
        return indicateur
    
    @staticmethod
    def mettre_a_jour_valeur(
        db: Session,
        indicateur_id: int,
        valeur_actuelle: float
    ) -> IndicateurQHSE:
        """Update indicator value"""
        indicateur = db.query(IndicateurQHSE).filter(IndicateurQHSE.id == indicateur_id).first()
        if not indicateur:
            raise ValueError("Indicateur non trouvé")
        
        valeur_previous = indicateur.valeur_actuelle or 0
        variation = valeur_actuelle - valeur_previous
        
        if variation > 0:
            tendance = "amelioration"
        elif variation < 0:
            tendance = "degradation"
        else:
            tendance = "stagnation"
        
        indicateur.valeur_actuelle = valeur_actuelle
        indicateur.valeur_previous = valeur_previous
        indicateur.variation = variation
        indicateur.tendance = tendance
        indicateur.date_mesure = date.today()
        
        db.commit()
        db.refresh(indicateur)
        return indicateur


class QHSEReportingService:
    """QHSE reporting service"""
    
    @staticmethod
    def rapport_securite(db: Session, annee: int) -> Dict[str, Any]:
        """Generate safety report"""
        accidents = db.query(AccidentTravail).filter(
            func.extract('year', AccidentTravail.date_accident) == annee
        ).all()
        
        analyses = db.query(AnalyseRisque).filter(
            AnalyseRisque.date_analyse.between(date(annee, 1, 1), date(annee, 12, 31))
        ).all()
        
        return {
            "annee": annee,
            "accidents": {
                "total": len(accidents),
                "graves": sum(1 for a in accidents if a.gravite in ["grave", "mortel"]),
                "arrets_travail": sum(a.arret_travail or 0 for a in accidents)
            },
            "risques": {
                "total": len(analyses),
                "critiques": sum(1 for a in analyses if a.niveau_risque == "critique"),
                "eleves": sum(1 for a in analyses if a.niveau_risque == "eleve")
            }
        }


class WorkPermitsIMDGService:
    """Gestion des Permis de Travail Dématérialisés et Matrice Ségrégation IMDG / CSST-CNPS"""

    TYPES_PERMIS = {"feu", "hauteur", "espace_confine", "eleve", "excavation", "autre"}

    @staticmethod
    def creer_permis_travail(db: Session, payload: Dict[str, Any], current_user) -> Dict[str, Any]:
        """Enregistre reellement un permis de travail BROUILLON/EN_ATTENTE_SIGN.

        Aucune signature n'est apposee ici : chaque signataire (donneur d'ordre,
        executant, officier ISPS) est un utilisateur authentifie qui signe via
        /permis-travail/{id}/signer. L'ancienne version fabriquait un permis
        « APPROUVE_ACTIF » tripartite : un acte de securite ne se simule pas.
        """
        from fastapi import HTTPException
        from app.models.qhse import PermisTravail, SignaturePermis
        from app.models.user import User

        type_permis = (payload.get("type_permis") or payload.get("type") or "").strip().lower()
        zone = (payload.get("zone") or "").strip()
        description = (payload.get("description") or "").strip()
        if not type_permis or not zone or not description:
            raise HTTPException(status_code=400, detail="Champs requis : type_permis, zone, description.")
        if type_permis not in WorkPermitsIMDGService.TYPES_PERMIS:
            raise HTTPException(
                status_code=400,
                detail=f"type_permis inconnu : {type_permis}. Attendu : {sorted(WorkPermitsIMDGService.TYPES_PERMIS)}.",
            )

        def _resolve_user_id(cle: str):
            uid = payload.get(cle)
            if uid is None:
                return None
            u = db.query(User).filter(User.id == int(uid)).first()
            if u is None:
                raise HTTPException(status_code=404, detail=f"Utilisateur {uid} introuvable ({cle}).")
            return u.id

        cid = getattr(current_user, "company_id", None)
        seq = (db.query(func.count(PermisTravail.id)).filter(PermisTravail.company_id == cid).scalar() or 0) + 1
        numero = f"PT-{date.today().year}-{seq:04d}"
        while db.query(PermisTravail.id).filter(PermisTravail.numero_permis == numero).first() is not None:
            seq += 1
            numero = f"PT-{date.today().year}-{seq:04d}"

        permis = PermisTravail(
            numero_permis=numero,
            company_id=cid,
            type_permis=type_permis,
            zone=zone[:200],
            description=description,
            intervention=payload.get("intervention"),
            mesures_preventives=payload.get("mesures_preventives"),
            demandeur_id=_resolve_user_id("demandeur_user_id") or current_user.id,
            executeur_id=_resolve_user_id("executeur_user_id"),
            officier_isps_id=_resolve_user_id("officier_isps_user_id"),
            statut="EN_ATTENTE_SIGN",
        )
        db.add(permis)
        db.commit()
        db.refresh(permis)
        return WorkPermitsIMDGService._permis_dict(db, permis)

    @staticmethod
    def _permis_dict(db: Session, permis) -> Dict[str, Any]:
        from app.models.qhse import SignaturePermis

        sigs = (
            db.query(SignaturePermis)
            .filter(SignaturePermis.permis_id == permis.id)
            .order_by(SignaturePermis.date_signature)
            .all()
        )
        return {
            "id": permis.id,
            "numero_permis": permis.numero_permis,
            "type_permis": permis.type_permis,
            "zone": permis.zone,
            "description": permis.description,
            "statut": permis.statut,
            "signataires_designes": {
                "demandeur": permis.demandeur_id,
                "executeur": permis.executeur_id,
                "officier_isps": permis.officier_isps_id,
            },
            "signatures": [
                {
                    "role": s.role_signataire,
                    "signataire_id": s.signataire_id,
                    "signataire_nom": s.signataire_nom,
                    "date_signature": s.date_signature.isoformat() if s.date_signature else None,
                }
                for s in sigs
            ],
            "created_at": permis.created_at.isoformat() if permis.created_at else None,
        }

    @staticmethod
    def verifier_segregation_imdg(classes_imdg: List[str]) -> Dict[str, Any]:
        """Aide-mémoire de ségrégation (Code IMDG 41-22) : deux règles majeures
        seulement, sur comparaison EXACTE de classes.

        Batch 24 : l'ancienne version testait « "1" in "".join(classes) »  la
        concaténation faisait des faux positifs ("4.1"+"3" → "4.13" contenant
        "1" et "3") et des faux négatifs ("5.1"+"3" → "5.13" ne contenant pas
        "5.1"). Une matrice IMDG complète (classes 1 à 9, amendements, prescriptions
        « à distance » vs « séparé ») exige le référentiel officiel : cette
        fonction reste un rappel, jamais une décision d'arrimage.
        """
        classes = {c.strip() for c in classes_imdg if c and c.strip()}
        conflits = []
        is_compatible = True

        # Classe 1 (explosifs) vs classes 3 / 5.1 : incompatibilité majeure.
        if "1" in classes and ({"3", "5.1"} & classes):
            conflits.append(
                "INCOMPATIBILITÉ MAJEURE : Classe 1 (Explosifs) et Classe 3/5.1 "
                "(Inflammables/Comburants). Ségrégation minimale : 24 mètres ou "
                "cloison pare-feu."
            )
            is_compatible = False

        # Classe 4.3 (gaz inflammable au contact de l'eau) vs classe 8 (corrosifs).
        if "4.3" in classes and "8" in classes:
            conflits.append(
                "ATTENTION : Classe 4.3 (Dégage gaz inflammable au contact de "
                "l'eau) et Classe 8 (Acides corrosifs). Séparation obligatoire."
            )
            is_compatible = False

        return {
            "classes_analysees": sorted(classes),
            "compatible": is_compatible,
            # Jamais « CONFORME_CODE_IMDG » : la conformité se prononce sur la
            # matrice officielle en vigueur, pas sur cet aide-mémoire. Nom de
            # champ conserve (niveau_segregation) pour la carte API existante.
            "niveau_segregation": "AUCUNE_REGLE_MAJEURE_DETECTEE" if is_compatible else "REGLE_MAJEURE_ENFREINTEE",
            "conflits_identifies": conflits,
            "avertissement": (
                "AIDE-MÉMOIRE NON RÉGLEMENTAIRE : vérifie seulement 2 règles de "
                "ségrégation parmi les prescriptions de la matrice IMDG en vigueur. "
                "Ne remplace pas la consultation de la matrice officielle (Code IMDG, "
                "colonne de segregation) pour décider un co-arrimage ou un stockage."
            ),
        }

    @staticmethod
    def bilan_annuel_csst_cnps(annee: int = 2026) -> Dict[str, Any]:
        """Batch 24 : DEBRANCHE (501). L'ancienne version renvoyait un « bilan
        officiel CNPS/CSST » avec heures d'exposition (2 850 000), accidents,
        jours d'arret et certifications ISO fabriques en dur, pour n'importe
        quel tenant. Une declaration annuelle a valeur declarative aupres de
        la CNPS : des chiffres inventes exposent l'entreprise. La stat basee
        en DB (accidents declares, risques) reste disponible via
        QHSEReportingService.rapport_securite.
        """
        not_implemented(
            f"Bilan annuel officiel CSST/CNPS {annee}",
            "la saisie réelle des heures d'exposition au risque par le tenant "
            "(les accidentés et jours d'arrêt proviennent déjà des AccidentTravail "
            "en base ; il manque la dénominateur heures travaillées). Aucun taux "
            "TF/TG n'est calculé avant saisie  voir /api/v1/qhse/rapports/securite/"
            f"{annee} pour les chiffres réellement déclarés dans la base"
        )


# Facade service for backward compatibility
class QHSEService:
    """Unified QHSE service facade"""
    risques = AnalyseRisqueService
    prevention = ActionPreventionService
    plans = PlanPreventionService
    epi = EPIRequisService
    accidents = AccidentTravailService
    investigations = InvestigationAccidentService
    normes = NormeCertificationService
    audits = AuditQualiteService
    haccp = HACCPPlanService
    points_critiques = PointCritiqueCCPService
    enregistrements = EnregistrementHACCPService
    formations = FormationQHSEService
    indicateurs = IndicateurQHSEService
    reporting = QHSEReportingService
    permits = WorkPermitsIMDGService

# Compatibility exports retained during the EVO-LOG Pro reconciliation.
AuditService = AuditQualiteService


def _legacy_analyse_creer(db: Session, numero_analyse: str, type_risque: str, zone: str,
                         description: str, probabilite: int, gravite: str, niveau_risque: str) -> AnalyseRisque:
    resolved_type = getattr(type_risque, "value", type_risque)
    resolved_type = str(resolved_type).upper()
    if isinstance(gravite, int):
        gravite_map = {
            1: "MINEUR",
            2: "MODERE",
            3: "MAJEUR",
            4: "CRITIQUE",
            5: "CATASTROPHIQUE",
        }
        resolved_gravite = gravite_map.get(int(gravite), "MAJEUR")
    else:
        resolved_gravite = str(getattr(gravite, "value", gravite)).upper()
    analyse = AnalyseRisque(
        numero_analyse=numero_analyse,
        zone=zone,
        processus="DEFAULT",
        date_analyse=date.today(),
        type_risque=resolved_type,
        description_danger=description,
        causes_potentielles="",
        consequences="",
        population_exposee=1,
        frequence="frequent",
        gravite=resolved_gravite,
        probabilite=probabilite,
        risque_calcule=probabilite * 5,
        niveau_risque=str(niveau_risque).upper(),
        statut="actif",
    )
    db.add(analyse)
    db.commit()
    db.refresh(analyse)
    return analyse


AnalyseRisqueService.creer_analyse_risque = staticmethod(_legacy_analyse_creer)


def _legacy_action_creer(db: Session, numero_action: str, type_action: str, description: str,
                        responsable_id: int, date_echeance: date) -> ActionPrevention:
    action = ActionPrevention(
        numero_action=numero_action,
        analyse_risque_id=1,
        type_action=type_action,
        description=description,
        priorite="moyenne",
        responsable=str(responsable_id),
        date_prevue=date_echeance,
        statut="planifie",
    )
    db.add(action)
    db.commit()
    db.refresh(action)
    return action


ActionPreventionService.creer_action_prevention = staticmethod(_legacy_action_creer)


def _legacy_analyse_evaluer(db: Session, analyse_id: int, nouvelles_mesures: str) -> AnalyseRisque:
    analyse = db.query(AnalyseRisque).filter(AnalyseRisque.id == analyse_id).first()
    if not analyse:
        raise ValueError("Analyse non trouvée")
    analyse.statut = "traite"
    analyse.mesures_recommandees = nouvelles_mesures
    db.commit()
    db.refresh(analyse)
    return analyse


AnalyseRisqueService.evaluer_risque = staticmethod(_legacy_analyse_evaluer)


def _legacy_accident_declarer(db: Session, numero_accident: str, employe_id: int,
                             date_accident: datetime, lieu: str, description: str, gravite: str) -> AccidentTravail:
    accident = AccidentTravail(
        numero_accident=numero_accident,
        employe_id=employe_id,
        date_accident=date_accident,
        lieu=lieu,
        type_accident="autre",
        description=description,
        gravite=gravite,
        statut="declare",
        date_declaration=date.today(),
    )
    db.add(accident)
    db.commit()
    db.refresh(accident)
    return accident


AccidentTravailService.declarer_accident = staticmethod(_legacy_accident_declarer)


def _legacy_investigation_lancer(db: Session, accident_id: int, investigateur_id: int) -> InvestigationAccident:
    investigation = InvestigationAccident(
        accident_id=accident_id,
        numero_investigation=f"INV-{accident_id}",
        date_investigation=date.today(),
        investigateur=str(investigateur_id),
        statut="en_cours",
    )
    db.add(investigation)
    db.commit()
    db.refresh(investigation)
    return investigation


AccidentTravailService.lancer_investigation = staticmethod(_legacy_investigation_lancer)


def _legacy_audit_creer(db: Session, numero_audit: str, type_audit: str, date_debut: date,
                       date_fin: date, scope: str) -> AuditQualite:
    audit = AuditQualite(
        numero_audit=numero_audit,
        certification_id=1,
        type_audit=str(type_audit).upper(),
        date_debut=date_debut,
        date_fin=date_fin,
        auditeur="system",
        scope=scope,
        statut="planifie",
    )
    db.add(audit)
    db.commit()
    db.refresh(audit)
    return audit


AuditQualiteService.creer_audit = staticmethod(_legacy_audit_creer)
