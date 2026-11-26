"""Ecriture comptable des ecarts d'inventaire (pont magasin -> compta).

Regle SYSCOHADA : une surperte de stock (ecart positif) debite le compte
de stock et credite la variation de stocks (6031) ; une depere fait
l'inverse. L'ecriture est creee `valide`, equilibree, avec lignes journal
et grand livre — idempotente par inventaire (cle INV-ECART-{id}).

Les comptes sont passes explicitement par le comptable : le systeme ne
devine jamais la nature comptable d'un ecart."""
from datetime import date
from decimal import Decimal
from typing import Any, Dict, Optional

from sqlalchemy.orm import Session

from app.models.finance_ohada import (
    EcritureComptableNew, ExerciceComptable, GrandLivreLigne,
    JournalAuxiliaire, LigneJournal, PlanComptableOHADA,)


class InventaireEcritureService:

    @staticmethod
    def _compte_par_numero(db: Session, numero: str) -> Optional[PlanComptableOHADA]:
        return db.query(PlanComptableOHADA).filter(
            PlanComptableOHADA.numero_compte == numero,
            PlanComptableOHADA.actif == True,  # noqa: E712
        ).first()

    @staticmethod
    def generer_ecriture_ecarts(
        db: Session,
        inventaire_id: int,
        date_ecriture: date,
        compte_stocks: str,
        compte_variation: str,
        journal_code: Optional[str] = None,
    ) -> Dict[str, Any]:
        """Genere l'ecriture d'ajustement des ecarts d'un inventaire.

        `impact_total` = somme(ecart x prix_unitaire). Si > 0 : DEBIT
        compte_stocks / CREDIT compte_variation. Si < 0 : inverse.
        Si nul : rien a comptabiliser."""
        from app.models.magasin_avance import InventaireTournant, LigneInventaire
        from app.models.magasin import Stock

        inventaire = db.query(InventaireTournant).filter(
            InventaireTournant.id == inventaire_id).first()
        if not inventaire:
            raise ValueError("Inventaire introuvable")

        numero = f"INV-ECART-{inventaire_id}"
        if db.query(EcritureComptableNew).filter(
                EcritureComptableNew.numero_ecriture == numero).first():
            raise ValueError(
                f"Ecriture d'ecarts deja comptabilisee pour {inventaire.numero_inventaire}")

 # Impact financier = somme des ecarts valorises au prix unitaire reel.
        lignes = (
            db.query(LigneInventaire, Stock)
            .join(Stock, Stock.id == LigneInventaire.stock_id)
            .filter(LigneInventaire.inventaire_id == inventaire_id)
            .all()
        )
        impact = Decimal("0")
        for ligne, stock in lignes:
            ecart = Decimal(str(ligne.ecart or 0))
            pu = Decimal(str(stock.prix_unitaire or 0))
            impact += ecart * pu
        impact = impact.quantize(Decimal("0.01"))
        if impact == 0:
            raise ValueError("Aucun ecart valorise : rien a comptabiliser")

        exercice = db.query(ExerciceComptable).filter(
            ExerciceComptable.annee == date_ecriture.year).first()
        if not exercice:
            raise ValueError("Exercice comptable introuvable pour cette date")

        c_stocks = InventaireEcritureService._compte_par_numero(db, compte_stocks)
        c_variation = InventaireEcritureService._compte_par_numero(db, compte_variation)
        if not c_stocks or not c_variation:
            raise ValueError("Compte OHADA introuvable (stocks ou variation)")

        journal = None
        if journal_code:
            journal = db.query(JournalAuxiliaire).filter(
                JournalAuxiliaire.code_journal == journal_code).first()
        if not journal:
            journal = db.query(JournalAuxiliaire).first()
        if not journal:
            raise ValueError("Aucun journal auxiliaire : initialiser les journaux d'abord")

        montant = abs(impact)
        periode = date_ecriture.strftime("%Y-%m")
        if impact > 0:
            sens = "surplus"
            debit_compte, credit_compte = c_stocks, c_variation
        else:
            sens = "dépérissement"
            debit_compte, credit_compte = c_variation, c_stocks

        piece = EcritureComptableNew(
            numero_ecriture=numero,
            date_ecriture=date_ecriture,
            numero_piece=inventaire.numero_inventaire,
            libelle=f"Ajustement ecarts inventaire {inventaire.numero_inventaire} ({sens})",
            compte_id=None,
            debit=montant,
            credit=montant,
            total_debit=montant,
            total_credit=montant,
            statut="valide",
            devise="XAF",
            reference_document=inventaire.numero_inventaire,
            type_document="inventaire",
            periode=periode,
            journal=journal.code_journal,
            valider=True,
            valide_par="inventaire",
            date_validation=date.today(),
            exercice_id=exercice.id,
            journal_id=journal.id,)
        db.add(piece)
        db.flush()

        libelle_detail = f"Ecarts inventaire {inventaire.numero_inventaire}"
        for order, (compte, est_debit) in enumerate([
                (debit_compte, True), (credit_compte, False)], start=1):
            db.add(LigneJournal(
                ecriture_id=piece.id,
                journal_id=journal.id,
                compte_id=compte.id,
                compte_numero=compte.numero_compte,
                compte_intitule=compte.intitule,
                debit=montant if est_debit else Decimal("0"),
                credit=Decimal("0") if est_debit else montant,
                devise="XAF",
                reference_document=inventaire.numero_inventaire,
                libelle_detail=libelle_detail,
                order_line=order))
            db.add(GrandLivreLigne(
                compte_id=compte.id,
                ecriture_id=piece.id,
                date_ecriture=date_ecriture,
                libelle=f"{libelle_detail} - {sens}",
                debit=montant if est_debit else Decimal("0"),
                credit=Decimal("0") if est_debit else montant,
                devise="XAF",
                journal=journal.code_journal,
                periode=periode))

        db.commit()
        db.refresh(piece)
        return {
            "inventaire_id": inventaire.id,
            "ecriture_id": piece.id,
            "montant": float(montant),
            "sens": sens,
            "periode": periode,
        }
