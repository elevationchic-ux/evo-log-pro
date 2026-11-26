"""Service du domaine juridique : contrats, contentieux, echeances.

Regles metier :
  * Un contrat sans date de fin est un contrat a duree indeterminee — il
    n'apparait pas dans les echeances.
  * L'echeance tient compte du preavis : l'alerte arrive `preavis_jours`
    avant la date de fin pour les reconductions tacites/automatiques.
  * Un contentieux ouvert sur un contrat passe le contrat en statut
    « contentieux » ; sa cloture ne rouvre pas automatiquement le contrat.
"""
from datetime import date, timedelta
from typing import List, Optional

from sqlalchemy.orm import Session

from app.models.juridique import ContentieuxJuridique, ContratJuridique


class JuridiqueService:

    # ------------------------------------------------------------------ #
    # Contrats
    # ------------------------------------------------------------------ #
    @staticmethod
    def creer_contrat(db: Session, data: dict) -> ContratJuridique:
        if data.get("date_fin") and data["date_fin"] < data["date_debut"]:
            raise ValueError("La date de fin ne peut pas preceder la date de debut")
        if data.get("reconduction") not in ("non", "tacite", "automatique"):
            raise ValueError("reconduction invalide : non / tacite / automatique")
        contrat = ContratJuridique(**data)
        db.add(contrat)
        db.commit()
        db.refresh(contrat)
        return contrat

    @staticmethod
    def obtenir_contrat(db: Session, contrat_id: int) -> Optional[ContratJuridique]:
        return db.query(ContratJuridique).filter(
            ContratJuridique.id == contrat_id, ContratJuridique.is_active == True).first()  # noqa: E712

    @staticmethod
    def lister_contrats(db: Session, statut: Optional[str] = None) -> List[ContratJuridique]:
        q = db.query(ContratJuridique).filter(ContratJuridique.is_active == True)  # noqa: E712
        if statut:
            q = q.filter(ContratJuridique.statut == statut)
        return q.order_by(ContratJuridique.date_fin).all()

    @staticmethod
    def resilier_contrat(db: Session, contrat_id: int, motif: str) -> ContratJuridique:
        contrat = JuridiqueService.obtenir_contrat(db, contrat_id)
        if not contrat:
            raise ValueError("Contrat introuvable")
        if contrat.statut in ("resilie", "expire"):
            raise ValueError(f"Contrat deja {contrat.statut}")
        contrat.statut = "resilie"
        if motif:
            contrat.notes = (contrat.notes or "") + f"\nResiliation : {motif}"
        db.commit()
        db.refresh(contrat)
        return contrat

    # ------------------------------------------------------------------ #
    # Echeances et preavis
    # ------------------------------------------------------------------ #
    @staticmethod
    def echeances_a_surveiller(db: Session, jours: int = 90) -> List[dict]:
        """Contrats arrivant a echeance dans `jours`, preavis inclus."""
        limite = date.today() + timedelta(days=jours)
        contrats = (
            db.query(ContratJuridique)
            .filter(
                ContratJuridique.is_active == True,  # noqa: E712
                ContratJuridique.statut == "actif",
                ContratJuridique.date_fin.isnot(None),
                ContratJuridique.date_fin <= limite,
                ContratJuridique.date_fin >= date.today() - timedelta(days=365))
            .order_by(ContratJuridique.date_fin)
            .all()
        )
        resultats = []
        for c in contrats:
            jours_restants = (c.date_fin - date.today()).days
            preavis_le = c.date_fin - timedelta(days=c.preavis_jours or 0) if c.preavis_jours else None
            if jours_restants < 0:
                motif = "expire : resiliation ou reconduction a traiter"
            elif c.reconduction != "non" and preavis_le and preavis_le <= date.today():
                motif = f"fenetre de preavis fermee le {preavis_le.isoformat()} : reconduction {c.reconduction}"
            elif c.reconduction != "non":
                motif = f"reconduction {c.reconduction} prevue, preavis avant le {preavis_le.isoformat() if preavis_le else 'n/a'}"
            else:
                motif = "echeance a echeance, aucune reconduction prevue"
            resultats.append({
                "contrat_id": c.id, "reference": c.reference, "objet": c.objet,
                "date_fin": c.date_fin, "jours_restants": jours_restants,
                "preavis_a_notifier_avant_le": preavis_le, "motif": motif,
            })
        return resultats

    # ------------------------------------------------------------------ #
    # Contentieux
    # ------------------------------------------------------------------ #
    @staticmethod
    def creer_contentieux(db: Session, data: dict) -> ContentieuxJuridique:
        if data.get("contrat_id"):
            contrat = JuridiqueService.obtenir_contrat(db, data["contrat_id"])
            if not contrat:
                raise ValueError("Contrat rattache introuvable")
        if data.get("date_echeance") and data["date_echeance"] < data["date_declaration"]:
            raise ValueError("L'echeance ne peut pas preceder la declaration")
        contentieux = ContentieuxJuridique(**data)
        db.add(contentieux)
        if data.get("contrat_id"):
            contrat.statut = "contentieux"
        db.commit()
        db.refresh(contentieux)
        return contentieux

    @staticmethod
    def cloturer_contentieux(db: Session, contentieux_id: int, statut: str,
                             montant_obtenu: Optional[float] = None) -> ContentieuxJuridique:
        if statut not in ("transaction", "gagne", "perdu", "abandonne"):
            raise ValueError("Statut de cloture invalide : transaction / gagne / perdu / abandonne")
        c = db.query(ContentieuxJuridique).filter(
            ContentieuxJuridique.id == contentieux_id,
            ContentieuxJuridique.is_active == True).first()  # noqa: E712
        if not c:
            raise ValueError("Contentieux introuvable")
        if c.statut not in ("ouvert", "en_cours"):
            raise ValueError(f"Contentieux deja cloture ({c.statut})")
        c.statut = statut
        c.date_cloture = date.today()
        if montant_obtenu is not None:
            c.montant_obtenu = montant_obtenu
        db.commit()
        db.refresh(c)
        return c

    @staticmethod
    def lister_contentieux(db: Session, statut: Optional[str] = None,
                           contrat_id: Optional[int] = None) -> List[ContentieuxJuridique]:
        q = db.query(ContentieuxJuridique).filter(ContentieuxJuridique.is_active == True)  # noqa: E712
        if statut:
            q = q.filter(ContentieuxJuridique.statut == statut)
        if contrat_id:
            q = q.filter(ContentieuxJuridique.contrat_id == contrat_id)
        return q.order_by(ContentieuxJuridique.date_declaration.desc()).all()
