"""RH avancée service - Paie OHADA Cameroon, Recrutement, Formations

PAIE SANS PLACEHOLDER (2026-09 correction) : les salaires « 500 000 » et
primes « 50 000 » codés en dur et la masse salariale fictive de la
déclaration CNPS ont été retirés. Tous les calculs partent désormais des
fiches de paie réellement enregistrées (tables salaires / primes) ; sans
donnée saisie, le service refuse au lieu d'inventer. Le barème progressif
ci-dessous est la SEULE source d'IR du backend (rh_service y délègue).
"""
from datetime import datetime, date, timedelta
from typing import List, Optional, Dict, Any
from sqlalchemy.orm import Session
from sqlalchemy import and_, func
from app.models.rh import (
    Conge, Absence, TempsTravail, Salaire, Prime,
    Formation, ParticipationFormation, OffreEmploi, Candidature,
)
from app.models.user import User


def _bornes_periode(periode: str):
    """'YYYY-MM' -> (premier jour, dernier jour) du mois."""
    d = datetime.strptime(periode, "%Y-%m")
    debut = date(d.year, d.month, 1)
    if d.month == 12:
        fin = date(d.year, 12, 31)
    else:
        fin = date(d.year, d.month + 1, 1) - timedelta(days=1)
    return debut, fin


class PaieOHADAService:
    """Service de paie OHADA Cameroon"""

    # Taux CNPS salariés (pension + risques professionnels).
    # À re-vérifier à chaque loi de finances ; source unique pour tout le backend.
    TAUX_CNPS_PENSION = 0.042
    TAUX_CNPS_ACCIDENTS = 0.005

    @staticmethod
    def _brut_enregistre(db: Session, employe_id: int, periode: str) -> float:
        """Salaire brut réel d'un employé pour un mois, depuis la table salaires.

        Lève ValueError (et n'invente AUCUN chiffre) si aucune fiche n'est
        enregistrée pour la période.
        """
        debut, fin = _bornes_periode(periode)
        rec = db.query(Salaire).filter(
            Salaire.employe_id == employe_id,
            Salaire.periode_debut <= fin,
            Salaire.periode_fin >= debut,
        ).first()
        if not rec:
            raise ValueError(
                f"Aucun salaire enregistré pour l'employé {employe_id} sur {periode}. "
                "Créez d'abord la fiche de paie  le bulletin ne peut pas être "
                "généré à partir d'un montant inventé."
            )
        heures_sup_montant = float(rec.heures_supplementaires or 0)
        if rec.taux_horaire_sup:
            heures_sup_montant = float(rec.heures_supplementaires or 0) * float(rec.taux_horaire_sup)
        primes = sum(
            float(getattr(rec, champ) or 0)
            for champ in (
                "prime_anciennete", "prime_performance", "prime_responsabilite",
                "prime_logement", "prime_transport", "prime_autre",
            )
        )
        return float(rec.salaire_base or 0) + heures_sup_montant + primes

    @staticmethod
    def bulletin_paie_complet(
        db: Session,
        employe_id: int,
        periode: str
    ) -> Dict[str, Any]:
        """Générer un bulletin de paie à partir de la fiche de paie enregistrée."""
        employe = db.query(User).filter(User.id == employe_id).first()
        if not employe:
            raise ValueError("Employé non trouvé")

        # Brut réel issu de la fiche de paie (plus de placeholder 500 000 / 50 000)
        salaire_brut = PaieOHADAService._brut_enregistre(db, employe_id, periode)

        # Primes du mois éventuellement portées par la table primes (statut approuvé)
        primes_approuvees = db.query(func.sum(Prime.montant)).filter(
            and_(Prime.employe_id == employe_id, Prime.periode == periode, Prime.statut == "approuve")
        ).scalar()
        montant_primes_table = float(primes_approuvees or 0)

        cnps_retraites = salaire_brut * PaieOHADAService.TAUX_CNPS_PENSION
        cnps_accidents = salaire_brut * PaieOHADAService.TAUX_CNPS_ACCIDENTS
        total_cnps = cnps_retraites + cnps_accidents

        # IRGM (Impôt sur revenus)  barème progressif, source unique du backend
        base_imposable = salaire_brut - total_cnps
        irgm = PaieOHADAService.calculer_irmg(base_imposable)

        net_a_payer = salaire_brut - total_cnps - irgm

        return {
            "employe_id": employe_id,
            "employe_nom": employe.full_name,
            "periode": periode,
            "salaire_brut": salaire_brut,
            "primes_table_apportees": montant_primes_table,
            "cnps_retraites": cnps_retraites,
            "cnps_accidents": cnps_accidents,
            "total_cnps": total_cnps,
            "base_imposable": base_imposable,
            "irmg": irgm,
            "net_a_payer": net_a_payer,
            "devise": "XAF",
            "source": "fiche de paie enregistrée (table salaires)"
        }
    
    @staticmethod
    def calculer_irmg(base_imposable: float) -> float:
        """Calculer l'IRGM selon barème Cameroun"""
        # Barème simplifié Cameroun 2026
        if base_imposable <= 50000:
            return 0
        elif base_imposable <= 100000:
            return (base_imposable - 50000) * 0.10
        elif base_imposable <= 200000:
            return 5000 + (base_imposable - 100000) * 0.15
        elif base_imposable <= 500000:
            return 20000 + (base_imposable - 200000) * 0.20
        elif base_imposable <= 1000000:
            return 80000 + (base_imposable - 500000) * 0.25
        else:
            return 205000 + (base_imposable - 1000000) * 0.30
    
    @staticmethod
    def charges_sociales(
        db: Session,
        employe_id: int,
        periode: str
    ) -> Dict[str, Any]:
        """Calculer les charges sociales OHADA depuis la fiche de paie enregistrée."""
        salaire_brut = PaieOHADAService._brut_enregistre(db, employe_id, periode)
        
        # CNPS
        cnps_retraites = salaire_brut * PaieOHADAService.TAUX_CNPS_PENSION
        cnps_accidents = salaire_brut * PaieOHADAService.TAUX_CNPS_ACCIDENTS
        cnps_total = cnps_retraites + cnps_accidents
        
        # Taxe apprentissage
        taxe_apprentissage = salaire_brut * 0.0025
        
        # Fonds de promotion
        fonds_promotion = salaire_brut * 0.001
        
        total_charges = cnps_total + taxe_apprentissage + fonds_promotion
        
        return {
            "employe_id": employe_id,
            "periode": periode,
            "salaire_brut": salaire_brut,
            "cnps_retraites": cnps_retraites,
            "cnps_accidents": cnps_accidents,
            "cnps_total": cnps_total,
            "taxe_apprentissage": taxe_apprentissage,
            "fonds_promotion": fonds_promotion,
            "total_charges": total_charges,
            "devise": "XAF"
        }
    
    @staticmethod
    def declaration_cnps(
        db: Session,
        periode: str
    ) -> Dict[str, Any]:
        """Déclaration CNPS mensuelle  assise sur les salaires RÉELLEMENT enregistrés.

        L'ancien code appliquait 500 000 FCFA fictifs à chaque utilisateur actif,
        produisant une masse salariale inventée pour un document opposable à
        l'employeur. Désormais : aucune fiche de paie enregistrée = erreur,
        pas de déclaration fantaisiste.
        """
        debut, fin = _bornes_periode(periode)
        fiches = db.query(Salaire).filter(
            Salaire.periode_debut <= fin,
            Salaire.periode_fin >= debut,
        ).all()
        if not fiches:
            raise ValueError(
                f"Aucun salaire enregistré sur {periode} : la déclaration CNPS ne "
                "peut pas être produite (la masse salariale uniforme de 500 000 FCFA "
                "par défaut a été supprimée comme invention)."
            )

        total_salaires = 0.0
        for rec in fiches:
            total_salaires += PaieOHADAService._brut_enregistre(db, rec.employe_id, periode)

        total_cnps = total_salaires * (
            PaieOHADAService.TAUX_CNPS_PENSION + PaieOHADAService.TAUX_CNPS_ACCIDENTS
        )

        return {
            "periode": periode,
            "nombre_employes_declares": len({rec.employe_id for rec in fiches}),
            "nombre_fiches_paie": len(fiches),
            "total_salaires": total_salaires,
            "total_cnps": total_cnps,
            "date_declaration": date.today(),
            "statut": "a_deposer",
            "source": "table salaires (calcul réel)"
        }
    
    @staticmethod
    def dipe_declaration(
        db: Session,
        periode: str
    ) -> Dict[str, Any]:
        """DIPE - Déclaration Employeur, calculée depuis les fiches de paie réelles."""
        debut, fin = _bornes_periode(periode)
        fiches = db.query(Salaire).filter(
            Salaire.periode_debut <= fin,
            Salaire.periode_fin >= debut,
        ).all()
        if not fiches:
            raise ValueError(
                f"Aucun salaire enregistré sur {periode} : la DIPE ne peut pas être "
                "pré-remplie avec des zéros comme si l'entreprise n'avait pas de salariés."
            )

        masse_salariale = sum(
            PaieOHADAService._brut_enregistre(db, rec.employe_id, periode) for rec in fiches
        )
        charges = masse_salariale * (
            PaieOHADAService.TAUX_CNPS_PENSION + PaieOHADAService.TAUX_CNPS_ACCIDENTS
        )

        return {
            "periode": periode,
            "nombre_employes": len({rec.employe_id for rec in fiches}),
            "masse_salariale": masse_salariale,
            "charges_sociales": charges,
            "statut": "a_deposer",
            "source": "table salaires (calcul réel)"
        }


class RecrutementService:
    """Service de recrutement — persistance REELLE (offres_emploi, candidatures).

    Aucun identifiant invente : l'objet creé est relis en base apres commit et
    le statut renvoie l'etat reellement stocke.
    """

    STATUTS_OFFRE = ("PUBLIEE", "CLOTUREE", "ANNULEE")
    STATUTS_CANDIDATURE = ("RECU", "PRESELECTIONNE", "ENTREVUE", "REFUSEE", "EMBAUCHE")

    @staticmethod
    def creer_offre_emploi(
        db: Session,
        titre: str,
        departement: str,
        description: str,
        type_contrat: str = "CDI",
        competences_requises: Optional[List[str]] = None,
        salaire_min: Optional[float] = None,
        salaire_max: Optional[float] = None,
    ) -> OffreEmploi:
        """Creer et enregistrer une offre d'emploi."""
        import json as _json
        offre = OffreEmploi(
            titre=titre,
            departement=departement,
            type_contrat=type_contrat,
            description=description,
            competences_requises=_json.dumps(competences_requises or [], ensure_ascii=False),
            salaire_min=salaire_min,
            salaire_max=salaire_max,
            statut="PUBLIEE",
        )
        db.add(offre)
        db.commit()
        db.refresh(offre)
        return offre

    @staticmethod
    def enregistrer_candidature(
        db: Session,
        offre_id: int,
        candidat_nom: str,
        email: str,
        telephone: str,
        cv_url: Optional[str] = None,
        experience_annees: int = 0,
    ) -> Candidature:
        """Enregistrer une candidature sur une offre existante (404 sinon)."""
        offre = db.query(OffreEmploi).filter(OffreEmploi.id == offre_id).first()
        if not offre:
            raise ValueError(f"Offre d'emploi {offre_id} introuvable")
        cand = Candidature(
            offre_id=offre.id,
            candidat_nom=candidat_nom,
            email=email,
            telephone=telephone,
            cv_url=cv_url,
            experience_annees=experience_annees or 0,
            statut="RECU",
        )
        db.add(cand)
        db.commit()
        db.refresh(cand)
        return cand

    @staticmethod
    def traiter_candidature(
        db: Session,
        candidature_id: int,
        decision: str,
        notes: Optional[str] = None
    ) -> Candidature:
        """Traiter une candidature : la decision modifie la ligne reellement en base."""
        decision = (decision or "").upper()
        if decision not in RecrutementService.STATUTS_CANDIDATURE:
            raise ValueError(
                "Decision invalide. Attendu : "
                + ", ".join(RecrutementService.STATUTS_CANDIDATURE)
            )
        cand = db.query(Candidature).filter(Candidature.id == candidature_id).first()
        if not cand:
            raise ValueError(f"Candidature {candidature_id} introuvable")
        cand.statut = decision
        cand.decision_notes = notes
        cand.date_decision = date.today()
        db.commit()
        db.refresh(cand)
        return cand


class FormationService:
    """Service de formation — persistance REELLE (formations, participations_formation)."""

    @staticmethod
    def plan_formation_annuel(
        db: Session,
        exercice_id: int
    ) -> Dict[str, Any]:
        """Bilan du plan de formation : agregation REELLE depuis la table formations.

        Sans sessions en base, les compteurs retournent 0 honnetes ; rien n'est
        invente.
        """
        from app.models.rh import Formation as _F

        sessions = db.query(_F).all()
        budget = sum(float(f.cout or 0) for f in sessions)
        nb_inscrits = db.query(func.count(ParticipationFormation.id)).scalar() or 0
        return {
            "exercice_id": exercice_id,
            "budget_formation": round(budget, 2),
            "nombre_formations": len(sessions),
            "nombre_inscrits": int(nb_inscrits),
            "statut": "en_cours" if sessions else "aucune_session",
            "source": "table formations (agregation reelle)",
        }

    @staticmethod
    def inscrire_formation(
        db: Session,
        employe_id: int,
        formation_id: int
    ) -> ParticipationFormation:
        """Inscrire un employe a une formation (identifiants reels, doublon 409)."""
        formation = db.query(Formation).filter(Formation.id == formation_id).first()
        if not formation:
            raise ValueError(f"Formation {formation_id} introuvable")
        employe = (
            db.query(User)
            .filter(User.id == employe_id, User.is_active.is_(True))
            .first()
        )
        if not employe:
            raise ValueError(f"Employe {employe_id} introuvable ou inactif")
        existant = (
            db.query(ParticipationFormation)
            .filter(
                ParticipationFormation.formation_id == formation_id,
                ParticipationFormation.employe_id == employe_id,
            )
            .first()
        )
        if existant:
            raise RuntimeError(
                f"Employe {employe_id} deja inscrit a la formation {formation_id}"
            )
        part = ParticipationFormation(formation_id=formation_id, employe_id=employe_id)
        db.add(part)
        db.commit()
        db.refresh(part)
        return part