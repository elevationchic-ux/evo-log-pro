"""Finance service - OHADA accounting and financial management for Cameroon/CEMAC"""
from datetime import datetime, date, timedelta
from decimal import Decimal
from typing import List, Optional, Dict, Any
from fastapi import HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import and_, func
from app.models.finance_ohada import (
    PlanComptableOHADA, EcritureComptableNew as EcritureComptable, ExerciceComptable, FactureNew as Facture, LigneFactureOHADA as LigneFacture,
    Reglement, TVADeclarable, RetenueSource, ISDeclarable, CentimesAdditionnels,
    Patente, Bilan, CompteResultat, SignatureElectronique,
    TypeCompte, RegimeTVA, RegimeIS, StatutTaxe,
    JournalAuxiliaire, LigneJournal, GrandLivreLigne, TypeJournal,
)


class PlanComptableOHADAService:
    """OHADA accounting plan service"""
    
    @staticmethod
    def creer_compte(
        db: Session,
        numero_compte: str,
        intitule: str,
        type_compte: TypeCompte,
        classe: int,
        sous_classe: int
    ) -> PlanComptableOHADA:
        """Create OHADA account"""
        compte = PlanComptableOHADA(
            numero_compte=numero_compte,
            intitule=intitule,
            type_compte=type_compte,
            classe=classe,
            sous_classe=sous_classe,
            date_creation=date.today(),
            devise="XAF"
        )
        db.add(compte)
        db.commit()
        db.refresh(compte)
        return compte


class EcritureComptableService:
    """Ecritures comptables : la partie double est la SEULE regle acceptee.

    L'ancien chemin "plat" (un compte portant a la fois un debit et un credit,
    sans contrepartie ni controle d'equilibre) produisait des ecritures
    comptablement fausses. Il est supprime : `creer_ecriture` refuse desormais
    tout ecriture non equilibree et renvoie vers la creation de piece.
    """

    @staticmethod
    def creer_ecriture(*_args, **_kwargs):
        raise HTTPException(
            status_code=410,
            detail=(
                "La creation d'ecriture 'plate' (un seul compte, non controlee en "
                "equilibre) est supprimee. Utilisez POST /api/v1/finance/pieces "
                "qui impose la partie double (>= 2 lignes, somme debit == somme credit)."
            ),
        )

    @staticmethod
    def valider_ecriture(db: Session, ecriture_id: int, valide_par: str) -> EcritureComptable:
        """Valider une ecriture : refuse toute piece desequilibree."""
        ecriture = db.query(EcritureComptable).filter(EcritureComptable.id == ecriture_id).first()
        if not ecriture:
            raise HTTPException(status_code=404, detail="Écriture comptable non trouvée")
        lignes = ecriture.lignes_journal or []
        if lignes:
            total_d = sum((Decimal(str(l.debit or 0)) for l in lignes), Decimal("0"))
            total_c = sum((Decimal(str(l.credit or 0)) for l in lignes), Decimal("0"))
            if total_d != total_c:
                raise HTTPException(
                    status_code=422,
                    detail=f"Piece desequilibree : ecart debit-credit = {total_d - total_c}."
                )
        elif Decimal(str(ecriture.debit or 0)) != Decimal(str(ecriture.credit or 0)):
            raise HTTPException(
                status_code=422,
                detail=(
                    "Cette ecriture est 'plate' et desequilibree ; elle ne peut pas "
                    "etre validee. Reprenez-la via POST /api/v1/finance/pieces."
                ),
            )

        ecriture.statut = "valide"
        ecriture.valider = True
        ecriture.valide_par = valide_par
        ecriture.date_validation = date.today()
        db.commit()
        db.refresh(ecriture)
        return ecriture


class PieceComptableService:
    """Piece comptable SYSCOHADA reellement en partie double.

    Une piece = un EN-TETE (`ecritures_comptables_ohada`) + des LIGNES
    (`lignes_journal`), chaque ligne portant UN compte et un debit OU un credit.

    Regles appliquees ici (et nulle part ailleurs), dans une transaction
    unique : au moins 2 lignes, une seule colonne remplie par ligne, comptes
    existants et actifs, somme(debit) == somme(credit), date comprise dans un
    exercice OUVERT, journal existant, numerotation continue par periode sans
    trou. Chaque ligne est egalement materialisee au grand livre.
    """

    @staticmethod
    def _d(valeur: Any) -> Decimal:
        return Decimal(str(valeur if valeur is not None else 0))

    @staticmethod
    def _serializer_ligne(ligne: LigneJournal) -> Dict[str, Any]:
        return {
            "id": ligne.id,
            "compte_id": ligne.compte_id,
            "compte_numero": ligne.compte_numero,
            "compte_intitule": ligne.compte_intitule,
            "debit": float(ligne.debit or 0),
            "credit": float(ligne.credit or 0),
            "libelle_detail": ligne.libelle_detail,
            "order_line": ligne.order_line,
        }

    @staticmethod
    def serializer(piece: EcritureComptable) -> Dict[str, Any]:
        total_debit = PieceComptableService._d(piece.total_debit)
        total_credit = PieceComptableService._d(piece.total_credit)
        return {
            "id": piece.id,
            "numero_ecriture": piece.numero_ecriture,
            "date_ecriture": piece.date_ecriture,
            "libelle": piece.libelle,
            "numero_piece": piece.numero_piece,
            "journal_id": piece.journal_id,
            "journal": piece.journal,
            "periode": piece.periode,
            "statut": piece.statut,
            "total_debit": float(total_debit),
            "total_credit": float(total_credit),
            "equilibree": total_debit == total_credit,
            "devise": piece.devise,
            "valider": bool(piece.valider),
            "exercice_id": piece.exercice_id,
            "lignes": [PieceComptableService._serializer_ligne(l) for l in (piece.lignes_journal or [])],
            "created_at": piece.created_at,
        }

    @staticmethod
    def _valider_lignes(lignes: List[Any]) -> None:
        """Refuse toute ligne ne respectant pas la partie double (422)."""
        if len(lignes) < 2:
            raise HTTPException(
                status_code=422,
                detail=(
                    f"Partie double exigee : au moins 2 lignes de journal, "
                    f"{len(lignes)} recue(s) - un debit et une contrepartie en credit."
                ),
            )
        for index, ligne in enumerate(lignes, start=1):
            debit = PieceComptableService._d(ligne.debit)
            credit = PieceComptableService._d(ligne.credit)
            if debit < 0 or credit < 0:
                raise HTTPException(status_code=422, detail=f"Ligne {index}: montant negatif interdit.")
            if (debit > 0) == (credit > 0):
                raise HTTPException(
                    status_code=422,
                    detail=(
                        f"Ligne {index}: une ligne porte soit un debit, soit un credit "
                        f"(exactement l'un des deux, non nul)."
                    ),
                )

    @staticmethod
    def _charger_comptes(db: Session, lignes: List[Any]) -> Dict[int, PlanComptableOHADA]:
        comptes = {}
        for ligne in lignes:
            if ligne.compte_id in comptes:
                continue
            compte = db.query(PlanComptableOHADA).filter(
                PlanComptableOHADA.id == ligne.compte_id
            ).first()
            if not compte:
                raise HTTPException(
                    status_code=422,
                    detail=f"Compte {ligne.compte_id} inexistant dans le plan comptable.",
                )
            if not compte.actif:
                raise HTTPException(
                    status_code=422,
                    detail=f"Compte {compte.numero_compte} inactif : saisie refusee.",
                )
            comptes[compte.id] = compte
        return comptes

    @staticmethod
    def _controle_equilibre(lignes: List[Any]) -> tuple:
        total_debit = sum((PieceComptableService._d(l.debit) for l in lignes), Decimal("0"))
        total_credit = sum((PieceComptableService._d(l.credit) for l in lignes), Decimal("0"))
        if total_debit != total_credit:
            raise HTTPException(
                status_code=422,
                detail=(
                    f"Piece desequilibree : total debit {total_debit} != total credit "
                    f"{total_credit} (ecart {total_debit - total_credit})."
                ),
            )
        return total_debit, total_credit

    @staticmethod
    def _exercice_ouvert(db: Session, date_ecriture: date) -> ExerciceComptable:
        exercice = (
            db.query(ExerciceComptable)
            .filter(
                ExerciceComptable.statut == "ouvert",
                ExerciceComptable.date_debut <= date_ecriture,
                ExerciceComptable.date_fin >= date_ecriture,
            )
            .first()
        )
        if not exercice:
            raise HTTPException(
                status_code=422,
                detail=(
                    f"Aucun exercice ouvert ne couvre la date {date_ecriture.isoformat()} : "
                    "ouvrez l'exercice correspondant avant de comptabiliser."
                ),
            )
        return exercice

    @staticmethod
    def _resoudre_journal(db: Session, piece_in: Any) -> JournalAuxiliaire:
        if piece_in.journal_id:
            journal = db.query(JournalAuxiliaire).filter(
                JournalAuxiliaire.id == piece_in.journal_id
            ).first()
            if not journal:
                raise HTTPException(status_code=422, detail=f"Journal {piece_in.journal_id} inexistant.")
            return journal
        if piece_in.type_journal:
            nom = piece_in.type_journal.strip().upper()
            try:
                type_journal = TypeJournal[nom]
            except KeyError:
                raise HTTPException(status_code=422, detail=f"Type de journal inconnu : '{piece_in.type_journal}'.")
            journal = db.query(JournalAuxiliaire).filter(
                JournalAuxiliaire.type_journal == type_journal
            ).first()
            if not journal:
                raise HTTPException(status_code=422, detail=f"Aucun journal de type '{nom}' configure.")
            return journal
        raise HTTPException(
            status_code=422,
            detail="journal_id ou type_journal requis (ACHATS, VENTES, BANQUE, CAISSE, OD, SALAIRES, AMORTISSEMENTS, TVA).",
        )

    @staticmethod
    def _prochain_numero(db: Session, date_ecriture: date) -> str:
        """Numero ECR-AAAAMM-NNNN sequentiel par periode, sans trou.

        Reprise sur le MAX deja pose pour la periode (pas de compteur qui
        saute quand une insertion echoue)."""
        patron = f"ECR-{date_ecriture.strftime('%Y%m')}-"
        poses = db.query(EcritureComptable.numero_ecriture).filter(
            EcritureComptable.numero_ecriture.like(patron + "%")
        ).all()
        courant = 0
        for (numero,) in poses:
            suffixe = str(numero)[len(patron):]
            if suffixe.isdigit():
                courant = max(courant, int(suffixe))
        return f"{patron}{courant + 1:04d}"

    @staticmethod
    def creer_piece(db: Session, piece_in: Any) -> Dict[str, Any]:
        """Cree une piece equilibree : en-tete + lignes + grand livre, atomique."""
        lignes = list(piece_in.lignes or [])
        PieceComptableService._valider_lignes(lignes)
        comptes = PieceComptableService._charger_comptes(db, lignes)
        total_debit, total_credit = PieceComptableService._controle_equilibre(lignes)
        exercice = PieceComptableService._exercice_ouvert(db, piece_in.date_ecriture)
        journal = PieceComptableService._resoudre_journal(db, piece_in)
        periode = piece_in.date_ecriture.strftime("%Y-%m")

        try:
            piece = EcritureComptable(
                numero_ecriture=PieceComptableService._prochain_numero(db, piece_in.date_ecriture),
                date_ecriture=piece_in.date_ecriture,
                numero_piece=piece_in.numero_piece,
                libelle=piece_in.libelle,
                compte_id=None,
                tiers_id=piece_in.tiers_id,
                debit=total_debit,
                credit=total_credit,
                total_debit=total_debit,
                total_credit=total_credit,
                statut="valide",
                devise="XAF",
                reference_document=piece_in.reference_document,
                type_document=piece_in.type_document,
                periode=periode,
                journal=journal.nom_journal,
                valider=True,
                valide_par="saisie_piece",
                date_validation=date.today(),
                exercice_id=exercice.id,
                journal_id=journal.id,
            )
            db.add(piece)
            db.flush()

            for index, ligne in enumerate(lignes, start=1):
                compte = comptes[ligne.compte_id]
                db.add(LigneJournal(
                    ecriture_id=piece.id,
                    journal_id=journal.id,
                    compte_id=compte.id,
                    compte_numero=compte.numero_compte,
                    compte_intitule=compte.intitule,
                    debit=PieceComptableService._d(ligne.debit),
                    credit=PieceComptableService._d(ligne.credit),
                    devise="XAF",
                    reference_document=ligne.reference_document,
                    libelle_detail=ligne.libelle_detail,
                    order_line=index,
                ))
                db.add(GrandLivreLigne(
                    compte_id=compte.id,
                    ecriture_id=piece.id,
                    date_ecriture=piece_in.date_ecriture,
                    libelle=ligne.libelle_detail or piece_in.libelle,
                    debit=PieceComptableService._d(ligne.debit),
                    credit=PieceComptableService._d(ligne.credit),
                    devise="XAF",
                    journal=journal.code_journal,
                    periode=periode,
                ))
            db.commit()
        except Exception:
            db.rollback()
            raise

        db.refresh(piece)
        return PieceComptableService.serializer(piece)

    @staticmethod
    def obtenir_piece(db: Session, piece_id: int) -> Dict[str, Any]:
        piece = db.query(EcritureComptable).filter(EcritureComptable.id == piece_id).first()
        if not piece:
            raise HTTPException(status_code=404, detail="Piece comptable introuvable.")
        return PieceComptableService.serializer(piece)

    @staticmethod
    def lister_pieces(
        db: Session,
        skip: int = 0,
        limit: int = 100,
        periode: Optional[str] = None,
        journal_id: Optional[int] = None,
        statut: Optional[str] = None,
    ) -> List[Dict[str, Any]]:
        q = db.query(EcritureComptable)
        if periode:
            q = q.filter(EcritureComptable.periode == periode)
        if journal_id:
            q = q.filter(EcritureComptable.journal_id == journal_id)
        if statut:
            q = q.filter(EcritureComptable.statut == statut)
        pieces = q.order_by(EcritureComptable.date_ecriture.desc(), EcritureComptable.id.desc()).offset(skip).limit(limit).all()
        return [PieceComptableService.serializer(p) for p in pieces]

    @staticmethod
    def valider_piece(db: Session, piece_id: int, valide_par: str) -> Dict[str, Any]:
        piece = db.query(EcritureComptable).filter(EcritureComptable.id == piece_id).first()
        if not piece:
            raise HTTPException(status_code=404, detail="Piece comptable introuvable.")
        lignes = piece.lignes_journal or []
        if lignes:
            total_d = sum((PieceComptableService._d(l.debit) for l in lignes), Decimal("0"))
            total_c = sum((PieceComptableService._d(l.credit) for l in lignes), Decimal("0"))
            if total_d != total_c:
                raise HTTPException(
                    status_code=422,
                    detail=f"Validation refusee : piece desequilibree (ecart {total_d - total_c}).",
                )
        else:
            raise HTTPException(
                status_code=422,
                detail="Validation refusee : cette ecriture n'a pas de lignes de piece (chemin plat obsolete).",
            )
        piece.statut = "comptabilise"
        piece.valider = True
        piece.valide_par = valide_par
        piece.date_validation = date.today()
        db.commit()
        db.refresh(piece)
        return PieceComptableService.serializer(piece)


class ExerciceComptableService:
    """Fiscal year service"""
    
    @staticmethod
    def creer_exercice(
        db: Session,
        numero_exercice: str,
        annee: int,
        date_debut: date,
        date_fin: date
    ) -> ExerciceComptable:
        """Create fiscal year"""
        exercice = ExerciceComptable(
            numero_exercice=numero_exercice,
            annee=annee,
            date_debut=date_debut,
            date_fin=date_fin,
            statut="ouvert",
            devise="XAF"
        )
        db.add(exercice)
        db.commit()
        db.refresh(exercice)
        return exercice
    
    @staticmethod
    def cloturer_exercice(db: Session, exercice_id: int, cloture_par: str) -> ExerciceComptable:
        """Close fiscal year"""
        exercice = db.query(ExerciceComptable).filter(ExerciceComptable.id == exercice_id).first()
        if not exercice:
            raise ValueError("Exercice comptable non trouvé")
        
        exercice.statut = "cloture"
        exercice.cloture_par = cloture_par
        exercice.date_cloture = date.today()
        db.commit()
        db.refresh(exercice)
        return exercice


class FactureService:
    """Invoice service"""
    
    @staticmethod
    def creer_facture(
        db: Session,
        numero_facture: Optional[str] = None,
        client_id: int = None,
        type_facture: str = "vente",
        date_emission: date = None,
        montant_ht: float = None,
        taux_tva: float = 19.25,
        # --- aliases de l'ancienne signature (appels existants) ---
        date_facture: date = None,
        date_echeance: date = None,
        montant_tva: float = None,
        montant_ttc: float = None,
        statut: Optional[str] = None,
    ) -> Facture:
        """Create invoice.

        Numerotation : si `numero_facture` est absent, la sequence LEGALE
        continue est utilisee (FAC-ANNEE-0001, exigence DGI). Un numero
        manuel n'est accepte que s'il est conforme (sequente) : sinon, les
        avoirs/prestations prennent leur propre prefixe automatique.

        Totaux : montants TVA/TTC calcules reellement depuis HT x taux si
        non fournis  jamais inventes.
        """
        from app.utils.numerotation import prochaine_reference

        date_emission = date_emission or date_facture or date.today()

        type_piece = "AVOIR" if (type_facture or "").lower() in ("avoir", "credit_note", "note_credit") else "FACTURE"
        if not numero_facture:
            numero_facture = prochaine_reference(
                db, type_piece, date_reference=date_emission
            )

        if montant_tva is None:
            montant_tva = round((montant_ht or 0) * (float(taux_tva or 0) / 100), 2)
        if montant_ttc is None:
            montant_ttc = round((montant_ht or 0) + montant_tva, 2)

        facture = Facture(
            numero_facture=numero_facture,
            client_id=client_id,
            type_facture=type_facture,
            date_emission=date_emission,
            date_echeance=date_echeance,
            montant_ht=montant_ht,
            taux_tva=taux_tva,
            montant_tva=montant_tva,
            montant_ttc=montant_ttc,
            devise="XAF",
            solde_restant=montant_ttc,
            statut=statut or "brouillon",
        )
        db.add(facture)
        db.commit()
        db.refresh(facture)
        return facture
    
    @staticmethod
    def ajouter_ligne_facture(
        db: Session,
        facture_id: int,
        article_id: Optional[int] = None,
        designation: Optional[str] = None,
        quantite: float = None,
        prix_unitaire_ht: float = None,
        taux_tva: float = 19.25,
        # --- alias de l'ancienne signature ---
        article: Optional[str] = None,
        prix_unitaire: Optional[float] = None,
        montant_ht: Optional[float] = None,
        unite: Optional[str] = None,
    ) -> LigneFacture:
        """Add line to invoice.

        designation/article : meme champ (l'ancien appelait la designation
        "article"). Les totaux sont recalcules depuis quantite x PU, jamais
        repris d'un montant passes en dur.
        """
        designation = designation or article
        if not designation:
            raise HTTPException(status_code=400, detail="Designation de la ligne obligatoire.")
        prix_unitaire_ht = prix_unitaire_ht if prix_unitaire_ht is not None else prix_unitaire
        if quantite is None or prix_unitaire_ht is None:
            raise HTTPException(status_code=400, detail="Quantite et prix unitaire obligatoires.")

        montant_ht = round(quantite * prix_unitaire_ht, 2)
        montant_tva = round(montant_ht * (float(taux_tva or 0) / 100), 2)
        montant_ttc = round(montant_ht + montant_tva, 2)

        ligne = LigneFacture(
            facture_id=facture_id,
            article_id=article_id,
            designation=designation,
            quantite=quantite,
            unite=unite,
            prix_unitaire_ht=prix_unitaire_ht,
            montant_ht=montant_ht,
            taux_tva=taux_tva,
            montant_tva=montant_tva,
            montant_ttc=montant_ttc,
            devise="XAF"
        )
        db.add(ligne)
        db.commit()
        db.refresh(ligne)
        return ligne


class ReglementService:
    """Payment service"""
    
    @staticmethod
    def enregistrer_reglement(
        db: Session,
        numero_reglement: str,
        facture_id: int,
        date_reglement: date,
        montant: float,
        mode_paiement: str,
        effectue_par: str
    ) -> Reglement:
        """Record payment"""
        reglement = Reglement(
            numero_reglement=numero_reglement,
            facture_id=facture_id,
            date_reglement=date_reglement,
            montant=montant,
            devise="XAF",
            mode_paiement=mode_paiement,
            effectue_par=effectue_par,
            statut="valide"
        )
        db.add(reglement)
        
        # Update invoice
        facture = db.query(Facture).filter(Facture.id == facture_id).first()
        if facture:
            facture.reglement_partiel += montant
            facture.solde_restant = facture.montant_ttc - facture.reglement_partiel
            if facture.solde_restant <= 0:
                facture.statut = "payee"
                facture.date_paiement = date_reglement
            else:
                facture.statut = "payee_partiel"
        
        db.commit()
        db.refresh(reglement)
        return reglement


class TVADeclarableService:
    """VAT declaration service"""
    
    @staticmethod
    def creer_declaration_tva(
        db: Session,
        numero_declaration: str,
        periode: str,
        regime_tva: RegimeTVA,
        base_imposable: float,
        tva_collectee: float,
        tva_deductible: float
    ) -> TVADeclarable:
        """Create VAT declaration"""
        tva_a_payer = tva_collectee - tva_deductible
        
        declaration = TVADeclarable(
            numero_declaration=numero_declaration,
            periode=periode,
            date_declaration=date.today(),
            regime_tva=regime_tva,
            base_imposable=base_imposable,
            tva_collectee=tva_collectee,
            tva_deductible=tva_deductible,
            tva_a_payer=tva_a_payer,
            devise="XAF",
            statut=StatutTaxe.DUE
        )
        db.add(declaration)
        db.commit()
        db.refresh(declaration)
        return declaration


class RetenueSourceService:
    """Withholding tax service"""
    
    @staticmethod
    def creer_retenue_source(
        db: Session,
        numero_retenu: str,
        facture_id: int,
        date_retenu: date,
        type_retenu: str,
        taux_retenu: float,
        base_imposable: float
    ) -> RetenueSource:
        """Create withholding tax"""
        montant_retenu = base_imposable * (taux_retenu / 100)
        
        retenue = RetenueSource(
            numero_retenu=numero_retenu,
            facture_id=facture_id,
            date_retenu=date_retenu,
            type_retenu=type_retenu,
            taux_retenu=taux_retenu,
            base_imposable=base_imposable,
            montant_retenu=montant_retenu,
            devise="XAF",
            statut=StatutTaxe.DUE
        )
        db.add(retenue)
        db.commit()
        db.refresh(retenue)
        return retenue


class ISDeclarableService:
    """Corporate tax declaration service"""
    
    @staticmethod
    def creer_declaration_is(
        db: Session,
        numero_declaration: str,
        exercice_id: int,
        annee: int,
        regime_is: RegimeIS,
        benefice_fiscal: float
    ) -> ISDeclarable:
        """Create corporate tax declaration"""
        taux_imposition = 33  # % OHADA
        is_du = benefice_fiscal * (taux_imposition / 100)
        is_minimum = benefice_fiscal * 0.01  # 1% minimum according to OHADA
        is_a_payer = max(is_du, is_minimum)
        
        declaration = ISDeclarable(
            numero_declaration=numero_declaration,
            exercice_id=exercice_id,
            annee=annee,
            regime_is=regime_is,
            benefice_fiscal=benefice_fiscal,
            taux_imposition=taux_imposition,
            is_du=is_du,
            is_minimum=is_minimum,
            is_a_payer=is_a_payer,
            devise="XAF",
            statut=StatutTaxe.DUE
        )
        db.add(declaration)
        db.commit()
        db.refresh(declaration)
        return declaration


class CentimesAdditionnelsService:
    """Additional local taxes service"""
    
    @staticmethod
    def creer_centimes(
        db: Session,
        numero_taxe: str,
        periode: str,
        type_taxe: str,
        base_imposable: float,
        taux: float,
        collectivite: str
    ) -> CentimesAdditionnels:
        """Create additional local tax"""
        montant_taxe = base_imposable * (taux / 100)
        
        centimes = CentimesAdditionnels(
            numero_taxe=numero_taxe,
            periode=periode,
            type_taxe=type_taxe,
            base_imposable=base_imposable,
            taux=taux,
            montant_taxe=montant_taxe,
            devise="XAF",
            statut=StatutTaxe.DUE,
            collectivite=collectivite
        )
        db.add(centimes)
        db.commit()
        db.refresh(centimes)
        return centimes


class PatenteService:
    """Business license tax service"""
    
    @staticmethod
    def creer_patente(
        db: Session,
        numero_patente: str,
        entreprise_id: int,
        annee: int,
        categorie: str,
        chiffre_affaires: float,
        montant_patente: float
    ) -> Patente:
        """Create business license tax"""
        patente = Patente(
            numero_patente=numero_patente,
            entreprise_id=entreprise_id,
            annee=annee,
            categorie=categorie,
            chiffre_affaires=chiffre_affaires,
            montant_patente=montant_patente,
            devise="XAF",
            statut=StatutTaxe.DUE
        )
        db.add(patente)
        db.commit()
        db.refresh(patente)
        return patente


class BilanService:
    """Balance sheet service"""
    
    @staticmethod
    def creer_bilan(
        db: Session,
        exercice_id: int,
        date_bilan: date,
        total_actif: float,
        total_passif: float
    ) -> Bilan:
        """Create balance sheet"""
        bilan = Bilan(
            exercice_id=exercice_id,
            date_bilan=date_bilan,
            total_actif=total_actif,
            total_passif=total_passif,
            devise="XAF"
        )
        db.add(bilan)
        db.commit()
        db.refresh(bilan)
        return bilan


class CompteResultatService:
    """Income statement service"""
    
    @staticmethod
    def creer_compte_resultat(
        db: Session,
        exercice_id: int,
        periode: str,
        chiffre_affaires: float,
        achats: float,
        resultat_net: float
    ) -> CompteResultat:
        """Create income statement"""
        compte = CompteResultat(
            exercice_id=exercice_id,
            periode=periode,
            chiffre_affaires=chiffre_affaires,
            achats=achats,
            resultat_net=resultat_net,
            devise="XAF"
        )
        db.add(compte)
        db.commit()
        db.refresh(compte)
        return compte


class SignatureElectroniqueService:
    """Electronic signature service"""
    
    @staticmethod
    def signer_facture(
        db: Session,
        facture_id: int,
        numero_signature: str,
        emetteur: str,
        certificat_id: str
    ) -> SignatureElectronique:
        """Sign invoice electronically"""
        signature = SignatureElectronique(
            facture_id=facture_id,
            numero_signature=numero_signature,
            date_signature=datetime.utcnow(),
            emetteur=emetteur,
            certificat_id=certificat_id,
            statut="valide"
        )
        db.add(signature)
        db.commit()
        db.refresh(signature)
        return signature


class FinanceReportingService:
    """Financial reporting service"""
    
    @staticmethod
    def rapport_fiscal(db: Session, exercice_id: int) -> Dict[str, Any]:
        """Generate fiscal report"""
        exercice = db.query(ExerciceComptable).filter(
            ExerciceComptable.id == exercice_id
        ).first()
        if not exercice:
            raise ValueError("Exercice comptable non trouvé")
        
        tva_declarations = db.query(TVADeclarable).filter(
            TVADeclarable.periode.startswith(str(exercice.annee))
        ).all()
        
        is_declarations = db.query(ISDeclarable).filter(
            ISDeclarable.exercice_id == exercice_id
        ).all()
        
        total_tva = sum(d.tva_a_payer or 0 for d in tva_declarations)
        total_is = sum(d.is_a_payer or 0 for d in is_declarations)
        
        return {
            "exercice": {
                "annee": exercice.annee,
                "statut": exercice.statut,
                "resultat_net": exercice.resultat_net
            },
            "fiscalite": {
                "total_tva": total_tva,
                "total_is": total_is,
                "total_charges_fiscales": total_tva + total_is
            }
        }


# Facade service for backward compatibility
class FinanceService:
    """Unified finance service facade"""
    plan_comptable = PlanComptableOHADAService
    ecritures = EcritureComptableService
    exercices = ExerciceComptableService
    factures = FactureService
    reglements = ReglementService
    tva = TVADeclarableService
    retenues = RetenueSourceService
    is_decl = ISDeclarableService
    centimes = CentimesAdditionnelsService
    patente = PatenteService
    bilan = BilanService
    compte_resultat = CompteResultatService
    signature = SignatureElectroniqueService
    reporting = FinanceReportingService

# Compatibility exports retained during the EVO-LOG Pro reconciliation.
PlanComptableService = PlanComptableOHADAService
PaiementService = ReglementService
TaxeService = TVADeclarableService


def _legacy_plan_creer(db: Session, numero: str, libelle: str, classe: int, categorie: str,
                      solde_debit: float = 0.0, solde_credit: float = 0.0) -> PlanComptableOHADA:
    category = {
        "ACTIF": TypeCompte.ACTIF,
        "PASSIF": TypeCompte.PASSIF,
        "CHARGE": TypeCompte.CHARGE,
        "PRODUIT": TypeCompte.PRODUIT,
    }.get(categorie.upper(), TypeCompte.ACTIF)
    compte = PlanComptableOHADA(
        numero_compte=numero,
        intitule=libelle,
        type_compte=category,
        classe=classe,
        sous_classe=0,
        date_creation=date.today(),
        devise="XAF",
        solde_debit=solde_debit,
        solde_credit=solde_credit,
        actif=True,
    )
    db.add(compte)
    db.commit()
    db.refresh(compte)
    return compte


PlanComptableOHADAService.creer_compte = staticmethod(_legacy_plan_creer)


def _legacy_plan_solde_update(db: Session, compte_id: int, debit: float = 0.0, credit: float = 0.0):
    compte = db.query(PlanComptableOHADA).filter(PlanComptableOHADA.id == compte_id).first()
    if not compte:
        raise ValueError("Compte non trouvé")
    # Colonnes Numeric -> Decimal : conversion explicite (Decimal + float leve un TypeError).
    from decimal import Decimal as _Decimal
    compte.solde_debit = (compte.solde_debit or _Decimal(0)) + _Decimal(str(debit))
    compte.solde_credit = (compte.solde_credit or _Decimal(0)) + _Decimal(str(credit))
    db.commit()
    db.refresh(compte)
    return compte


PlanComptableOHADAService.mettre_a_jour_solde = staticmethod(_legacy_plan_solde_update)


def _legacy_ecriture_creer(db: Session, numero_ecriture: str, date_ecriture: date,
                          reference: str, libelle: str, montant_debit: float, montant_credit: float) -> EcritureComptable:
    ecriture = EcritureComptable(
        numero_ecriture=numero_ecriture,
        date_ecriture=date_ecriture,
        numero_piece=reference,
        libelle=libelle,
        compte_id=1,
        debit=montant_debit,
        credit=montant_credit,
        devise="XAF",
        journal="ACHATS",
        periode=date_ecriture.strftime("%Y-%m"),
        valider=True,
    )
    ecriture.statut = "validee"
    ecriture.montant_debit = montant_debit
    ecriture.montant_credit = montant_credit
    db.add(ecriture)
    db.commit()
    db.refresh(ecriture)
    return ecriture


EcritureComptableService.creer_ecriture = staticmethod(_legacy_ecriture_creer)


# creer_facture / ajouter_ligne_facture : l'app "legacy" qui écrasait ces deux
# méthodes avec une signature incompatible cassait en réalité le routeur
# POST /finance/factures (7 arguments passés, 9 attendus -> TypeError).
# La version unique ci-dessus accepte les deux formes ; plus de patch ici.


def _legacy_paiement_creer(db: Session, numero_paiement: str, facture_id: int, date_paiement: date,
                         montant: float, mode_paiement: str, reference_bancaire: str) -> Reglement:
    paiement = Reglement(
        numero_reglement=numero_paiement,
        facture_id=facture_id,
        date_reglement=date_paiement,
        montant=montant,
        devise="XAF",
        mode_paiement=mode_paiement,
        effectue_par="system",
        statut="valide",
    )
    paiement.reference_bancaire = reference_bancaire
    db.add(paiement)
    db.commit()
    db.refresh(paiement)
    return paiement


ReglementService.creer_paiement = staticmethod(_legacy_paiement_creer)


def _legacy_tva_calculer(db: Session, numero_tva: str, base_imposable: float, taux: float,
                        date: date):
    montant_tva = base_imposable * (taux / 100)
    # Colonnes reelles de TVADeclarable : tva_collectee / tva_deductible / tva_a_payer
    # (l'ancien code passait montant_tva et taux, inexistants -> TypeError au runtime).
    declaration = TVADeclarable(
        numero_declaration=numero_tva,
        periode=date.strftime("%Y-%m"),
        date_declaration=date,
        regime_tva=RegimeTVA.NORMAL,
        base_imposable=base_imposable,
        tva_collectee=montant_tva,
        tva_deductible=0,
        tva_a_payer=montant_tva,
        devise="XAF",
        statut=StatutTaxe.DUE,
    )
    db.add(declaration)
    db.commit()
    db.refresh(declaration)
    return declaration


TVADeclarableService.calculer_tva = staticmethod(_legacy_tva_calculer)


def _legacy_retenue_calculer(db: Session, numero_retenu: str, base_imposable: float, taux: float,
                            date: date):
    montant_retenu = base_imposable * (taux / 100)
    # Colonnes reelles de RetenueSource : numero_retenu / date_retenu / taux_retenu /
    # montant_retenu (l'ancien code utilisait numero_retenue, date_retenue... -> TypeError).
    retenue = RetenueSource(
        numero_retenu=numero_retenu,
        date_retenu=date,
        type_retenu="ARS",
        taux_retenu=taux,
        base_imposable=base_imposable,
        montant_retenu=montant_retenu,
        devise="XAF",
        statut=StatutTaxe.DUE,
    )
    db.add(retenue)
    db.commit()
    db.refresh(retenue)
    return retenue


RetenueSourceService.calculer_retenu_source = staticmethod(_legacy_retenue_calculer)
# Alias historique : calcul de la retenue a la source exposee sur TaxeService.
TaxeService.calculer_retenu_source = staticmethod(_legacy_retenue_calculer)
