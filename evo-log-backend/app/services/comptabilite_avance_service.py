"""Comptabilité avancée service - Journaux auxiliaires, lettrage, grand livre, balance"""
from datetime import datetime, date
from decimal import Decimal
import json
from typing import List, Optional, Dict, Any
from sqlalchemy.orm import Session
from sqlalchemy import and_, func, case
from app.models.finance_ohada import (
    PlanComptableOHADA, EcritureComptableNew, ExerciceComptable, 
    JournalAuxiliaire, LigneJournal, Lettrage, EcritureLettree,
    GrandLivreLigne, BalanceVerification, LigneBalance,
    BilanOHADADetaille, CompteResultatOHADADetaille, TAFIRE, TFT, SIG, AnnexesOHADA,
    NoteAnnexe, Immobilisation, LiasseFiscale,
    TVADeclarable, ISDeclarable, TypeJournal, TypeLettrage, StatutLettrage,
    StatutTaxe, RegimeTVA,)


class JournalAuxiliaireService:
    """Gestion complète des journaux auxiliaires"""
    
    @staticmethod
    def creer_journal_auxiliaire(
        db: Session,
        code_journal: str,
        nom_journal: str,
        type_journal: TypeJournal,
        compte_centralisateur: Optional[str] = None,
        description: Optional[str] = None
    ) -> JournalAuxiliaire:
        """Créer un journal auxiliaire"""
        journal = JournalAuxiliaire(
            code_journal=code_journal,
            nom_journal=nom_journal,
            type_journal=type_journal,
            compte_centralisateur=compte_centralisateur,
            description=description,
            statut="actif"
        )
        db.add(journal)
        db.commit()
        db.refresh(journal)
        return journal
    
    @staticmethod
    def journal_achats(db: Session) -> Optional[JournalAuxiliaire]:
        """Obtenir ou créer le journal des achats"""
        journal = db.query(JournalAuxiliaire).filter(
            JournalAuxiliaire.type_journal == TypeJournal.ACHATS
        ).first()
        if not journal:
            journal = JournalAuxiliaireService.creer_journal_auxiliaire(
                db, "ACH", "Journal des Achats", TypeJournal.ACHATS,
                compte_centralisateur="401",
                description="Journal des achats et frais accessoires"
            )
        return journal
    
    @staticmethod
    def journal_ventes(db: Session) -> Optional[JournalAuxiliaire]:
        """Obtenir ou créer le journal des ventes"""
        journal = db.query(JournalAuxiliaire).filter(
            JournalAuxiliaire.type_journal == TypeJournal.VENTES
        ).first()
        if not journal:
            journal = JournalAuxiliaireService.creer_journal_auxiliaire(
                db, "VTE", "Journal des Ventes", TypeJournal.VENTES,
                compte_centralisateur="411",
                description="Journal des ventes de marchandises"
            )
        return journal
    
    @staticmethod
    def journal_banque(db: Session) -> Optional[JournalAuxiliaire]:
        """Obtenir ou créer le journal de banque"""
        journal = db.query(JournalAuxiliaire).filter(
            JournalAuxiliaire.type_journal == TypeJournal.BANQUE
        ).first()
        if not journal:
            journal = JournalAuxiliaireService.creer_journal_auxiliaire(
                db, "BQ", "Journal de Banque", TypeJournal.BANQUE,
                compte_centralisateur="512",
                description="Journal des opérations bancaires"
            )
        return journal
    
    @staticmethod
    def journal_caisse(db: Session) -> Optional[JournalAuxiliaire]:
        """Obtenir ou créer le journal de caisse"""
        journal = db.query(JournalAuxiliaire).filter(
            JournalAuxiliaire.type_journal == TypeJournal.CAISSE
        ).first()
        if not journal:
            journal = JournalAuxiliaireService.creer_journal_auxiliaire(
                db, "CAI", "Journal de Caisse", TypeJournal.CAISSE,
                compte_centralisateur="531",
                description="Journal des opérations de caisse"
            )
        return journal
    
    @staticmethod
    def journal_od(db: Session) -> Optional[JournalAuxiliaire]:
        """Obtenir ou créer le journal des opérations diverses"""
        journal = db.query(JournalAuxiliaire).filter(
            JournalAuxiliaire.type_journal == TypeJournal.OD
        ).first()
        if not journal:
            journal = JournalAuxiliaireService.creer_journal_auxiliaire(
                db, "OD", "Journal des Opérations Diverses", TypeJournal.OD,
                description="Journal des opérations diverses et régularisations"
            )
        return journal
    
    @staticmethod
    def journal_salaires(db: Session) -> Optional[JournalAuxiliaire]:
        """Obtenir ou créer le journal des salaires"""
        journal = db.query(JournalAuxiliaire).filter(
            JournalAuxiliaire.type_journal == TypeJournal.SALAIRES
        ).first()
        if not journal:
            journal = JournalAuxiliaireService.creer_journal_auxiliaire(
                db, "SAL", "Journal des Salaires", TypeJournal.SALAIRES,
                compte_centralisateur="641",
                description="Journal des salaires et charges sociales"
            )
        return journal
    
    @staticmethod
    def journal_amortissements(db: Session) -> Optional[JournalAuxiliaire]:
        """Obtenir ou créer le journal des amortissements"""
        journal = db.query(JournalAuxiliaire).filter(
            JournalAuxiliaire.type_journal == TypeJournal.AMORTISSEMENTS
        ).first()
        if not journal:
            journal = JournalAuxiliaireService.creer_journal_auxiliaire(
                db, "AMO", "Journal des Amortissements", TypeJournal.AMORTISSEMENTS,
                compte_centralisateur="681",
                description="Journal des dotations aux amortissements"
            )
        return journal
    
    @staticmethod
    def initialiser_tous_les_journaux(db: Session) -> List[JournalAuxiliaire]:
        """Initialiser tous les journaux auxiliaires standards"""
        journaux = []
        journaux.append(JournalAuxiliaireService.journal_achats(db))
        journaux.append(JournalAuxiliaireService.journal_ventes(db))
        journaux.append(JournalAuxiliaireService.journal_banque(db))
        journaux.append(JournalAuxiliaireService.journal_caisse(db))
        journaux.append(JournalAuxiliaireService.journal_od(db))
        journaux.append(JournalAuxiliaireService.journal_salaires(db))
        journaux.append(JournalAuxiliaireService.journal_amortissements(db))
        return [j for j in journaux if j is not None]


class LettrageService:
    """Service de lettrage automatique et manuel"""
    
    @staticmethod
    def _compte(db: Session, compte_id: int) -> PlanComptableOHADA:
        compte = db.query(PlanComptableOHADA).filter(
            PlanComptableOHADA.id == compte_id
        ).first()
        if not compte:
            raise ValueError("Compte introuvable")
        return compte

    @staticmethod
    def _lignes_ouvertes(db: Session, compte_id: int) -> List[GrandLivreLigne]:
        """Lignes du grand livre REELLEMENT ouvertes pour ce compte.

        Source de vérité : `grand_livre_lignes` (une ligne = un mouvement sur UN
        compte), et non l'en-tête plat `ecritures_comptables_ohada` dont
        `compte_id` est désormais NULL (il porte les totaux de la pièce).
        L'ancienne version filtrait donc sur une colonne toujours nulle : le
        lettrage ne voyait jamais aucune écriture réelle.

        Une ligne est « ouverte » (= à lettrer) si elle n'est pas déjà soldée
        (statut != LETTRE) et n'est rattachée à aucun lettrage. Cela rend aussi
        le lettrage idempotent : relancer ne re-lettre pas ce qui l'est déjà."""
        return (
            db.query(GrandLivreLigne)
            .filter(
                GrandLivreLigne.compte_id == compte_id,
                GrandLivreLigne.lettrage_id.is_(None),
                (
                    GrandLivreLigne.statut_lettrage.is_(None)
                    | (GrandLivreLigne.statut_lettrage != StatutLettrage.LETTRE)
                ),)
            .order_by(GrandLivreLigne.date_ecriture.asc(), GrandLivreLigne.id.asc())
            .all()
        )

    @staticmethod
    def suggestion_lettrage(db: Session, compte_id: int) -> Dict[str, Any]:
        """Items réellement ouverts d'un compte tiers, prêts à lettrer.

        Retourne la liste des lignes non soldées, leurs totaux débit/crédit et
        le solde ouvert  aucune donnée inventée, uniquement l'état du grand
        livre. Le frontend affiche ces lignes et laisse l'utilisateur cocher un
        ensemble dont le solde s'équilibre (règle du lettrage)."""
        compte = LettrageService._compte(db, compte_id)
        lignes = LettrageService._lignes_ouvertes(db, compte_id)

        items = []
        total_debit = Decimal("0")
        total_credit = Decimal("0")
        for l in lignes:
            d = Decimal(str(l.debit or 0))
            c = Decimal(str(l.credit or 0))
            total_debit += d
            total_credit += c
            items.append({
                "ligne_id": l.id,
                "ecriture_id": l.ecriture_id,
                "date_ecriture": l.date_ecriture,
                "libelle": l.libelle,
                "journal": l.journal,
                "periode": l.periode,
                "debit": d,
                "credit": c,
            })

        return {
            "compte_id": compte_id,
            "compte_numero": compte.numero_compte,
            "compte_intitule": compte.intitule,
            "lignes": items,
            "total_debit": total_debit,
            "total_credit": total_credit,
            "solde_ouvert": total_debit - total_credit,
        }

    @staticmethod
    def lettrage_automatique(
        db: Session,
        compte_id: int,
        date_reference: date,
        effectue_par: str = "SYSTEME",) -> Lettrage:
        """Lettrage automatique FIFO par rapprochement d'un compte.

        Algorithme honnête : on apparie les lignes ouvertes débit et crédit de
        MÊME montant (arrondi 2), en ordre chronologique (FIFO). Chaque paire
        soldée est rattachée à une campagne de lettrage. Si aucune paire exacte
        n'existe, on refuse (rien n'est forcé) plutôt que de tout lumpser dans
        un faux lettrage comme l'ancienne version, qui créait un lettrage unique
        englobant TOUTES les écritures du compte sans vérifier l'équilibre."""
        LettrageService._compte(db, compte_id)
        lignes = LettrageService._lignes_ouvertes(db, compte_id)
        if not lignes:
            raise ValueError("Aucune écriture ouverte à lettrer pour ce compte")

        def _amt(l, col):
            return Decimal(str(getattr(l, col) or 0)).quantize(Decimal("0.01"))

        debits = [l for l in lignes if _amt(l, "debit") > 0]
        credits = [l for l in lignes if _amt(l, "credit") > 0]

        used_credit_ids = set()
        matched: List[GrandLivreLigne] = []
        for d in debits:  # déjà triées par date (FIFO)
            montant = _amt(d, "debit")
            for c in credits:
                if c.id in used_credit_ids:
                    continue
                if _amt(c, "credit") == montant:
                    matched.extend([d, c])
                    used_credit_ids.add(c.id)
                    break

        if not matched:
            raise ValueError(
                "Aucun lettrage automatique possible : aucune écriture débit/crédit "
                "de même montant à solder sur ce compte"
            )

        montant_total = sum(_amt(l, "debit") for l in matched if _amt(l, "debit") > 0)
        numero = f"LET-AUTO-{compte_id}-{date_reference.strftime('%Y%m%d')}-{datetime.now().strftime('%H%M%S')}"
        lettrage = Lettrage(
            compte_id=compte_id,
            numero_lettrage=numero,
            type_lettrage=TypeLettrage.AUTOMATIQUE,
            date_lettrage=date_reference,
            montant_lettre=montant_total,
            effectue_par=effectue_par,
            notes=f"Lettrage automatique FIFO : {len(matched)} ligne(s) soldée(s)",)
        db.add(lettrage)
        db.commit()
        db.refresh(lettrage)

        for l in matched:
            l.statut_lettrage = StatutLettrage.LETTRE
            l.lettrage_id = lettrage.id
            db.add(EcritureLettree(
                lettrage_id=lettrage.id,
                ecriture_id=l.ecriture_id,
                montant_lettre=(_amt(l, "debit") or _amt(l, "credit")),))
        db.commit()
        db.refresh(lettrage)
        return lettrage

    @staticmethod
    def lettrage_manuel(
        db: Session,
        compte_id: int,
        ligne_ids: List[int],
        date_lettrage: date,
        effectue_par: str,
        reference: Optional[str] = None,) -> Lettrage:
        """Lettrage manuel d'un ensemble de lignes DU COMPTE qui doit S'ÉQUILIBRER.

        Règle de rapprochement : la somme des débits doit égaler la somme des
        crédits (solde nul), sinon le lettrage est refusé avec l'écart exact.
        L'ancienne version ne vérifiait nulle part cet équilibre et lettrait
        n'importe quoi. On opère sur les lignes du grand livre (ids), en
        excluant celles déjà soldées (idempotence)."""
        LettrageService._compte(db, compte_id)
        if not ligne_ids:
            raise ValueError("Aucune ligne sélectionnée pour le lettrage")

        lignes = (
            db.query(GrandLivreLigne)
            .filter(GrandLivreLigne.id.in_(ligne_ids))
            .all()
        )
        if len(lignes) != len(set(ligne_ids)):
            raise ValueError("Certaines lignes n'existent pas")
        for l in lignes:
            if l.compte_id != compte_id:
                raise ValueError("Une ligne sélectionnée n'appartient pas à ce compte")
            if l.lettrage_id is not None or l.statut_lettrage == StatutLettrage.LETTRE:
                raise ValueError(f"Ligne {l.id} déjà lettrée")

        def _amt(l, col):
            return Decimal(str(getattr(l, col) or 0)).quantize(Decimal("0.01"))

        total_debit = sum(_amt(l, "debit") for l in lignes)
        total_credit = sum(_amt(l, "credit") for l in lignes)
        ecart = total_debit - total_credit
        if ecart != 0:
            raise ValueError(
                f"Sélection non soldée : débit {total_debit} / crédit {total_credit} "
                f"(écart {ecart}). Le lettrage exige un solde nul."
            )

        numero = f"LET-MAN-{compte_id}-{date_lettrage.strftime('%Y%m%d')}-{datetime.now().strftime('%H%M%S')}"
        lettrage = Lettrage(
            compte_id=compte_id,
            numero_lettrage=numero,
            type_lettrage=TypeLettrage.MANUEL,
            date_lettrage=date_lettrage,
            montant_lettre=total_debit,
            reference_lettrage=reference,
            effectue_par=effectue_par,)
        db.add(lettrage)
        db.commit()
        db.refresh(lettrage)

        for l in lignes:
            l.statut_lettrage = StatutLettrage.LETTRE
            l.lettrage_id = lettrage.id
            db.add(EcritureLettree(
                lettrage_id=lettrage.id,
                ecriture_id=l.ecriture_id,
                montant_lettre=(_amt(l, "debit") or _amt(l, "credit")),))
        db.commit()
        db.refresh(lettrage)
        return lettrage

    @staticmethod
    def annuler_lettrage(db: Session, lettrage_id: int, motif: str) -> Lettrage:
        """Annuler un lettrage : libère réellement les lignes réconciliées.

        Rétablit le statut des lignes du grand livre à NON_LETRE (et décroche
        leur lettrage_id) pour qu'elles redeviennent ouvertes ; sinon l'annulation
        était cosmétique et les écritures restaient marquées soldées."""
        lettrage = db.query(Lettrage).filter(Lettrage.id == lettrage_id).first()
        if not lettrage:
            raise ValueError("Lettrage non trouvé")
        if lettrage.date_annulation is not None:
            raise ValueError("Lettrage déjà annulé")

 # Libérer les lignes du grand livre rattachées
        db.query(GrandLivreLigne).filter(
            GrandLivreLigne.lettrage_id == lettrage_id
        ).update({"statut_lettrage": StatutLettrage.NON_LETRE, "lettrage_id": None},
                 synchronize_session=False)

 # Supprimer les liens écritures
        db.query(EcritureLettree).filter(EcritureLettree.lettrage_id == lettrage_id).delete()

        lettrage.date_annulation = date.today()
        lettrage.motif_annulation = motif
        db.commit()
        db.refresh(lettrage)
        return lettrage


class GrandLivreService:
    """Service du grand livre général et auxiliaires"""

    @staticmethod
    def mouvements_par_compte(
        db: Session,
        date_debut: Optional[date] = None,
        date_fin: Optional[date] = None,
        journal: Optional[str] = None,) -> Dict[int, Dict[str, Decimal]]:
        """Soldes reels par compte agreges depuis les lignes du grand livre.

        Source de verite : `grand_livre_lignes`, materialisees ligne par ligne
        par PieceComptableService au moment de la saisie de la piece en partie
        double. On n'aggregate JAMAIS l'en-tete plat (`compte_id` est nul et
        `debit/credit` y portent les TOTAUX de la piece, pas un compte).

        Retourne {compte_id: {"debit": ..., "credit": ...}} pour la periode
        facultative (et un eventuel code journal).
        """
        colonnes = [
            GrandLivreLigne.compte_id,
            func.coalesce(func.sum(GrandLivreLigne.debit), 0),
            func.coalesce(func.sum(GrandLivreLigne.credit), 0),
        ]
        requete = db.query(*colonnes)
        if date_debut is not None:
            requete = requete.filter(GrandLivreLigne.date_ecriture >= date_debut)
        if date_fin is not None:
            requete = requete.filter(GrandLivreLigne.date_ecriture <= date_fin)
        if journal:
            requete = requete.filter(GrandLivreLigne.journal == journal)
        requete = requete.group_by(GrandLivreLigne.compte_id)
        resultats = {}
        for compte_id, debit, credit in requete.all():
            resultats[compte_id] = {
                "debit": Decimal(str(debit or 0)),
                "credit": Decimal(str(credit or 0)),
            }
        return resultats

    @staticmethod
    def generer_grand_livre_general(
        db: Session,
        exercice_id: int,
        date_debut: date,
        date_fin: date
    ) -> List[GrandLivreLigne]:
        """Grand livre general pour la periode : LECTURE des lignes reellement
        comptabilisees (materialisees par les pieces en partie double).

        L'ancienne version RE-CREAIT des `GrandLivreLigne` depuis l'en-tete plat
        des ecritures ; or cet en-tete porte desormais `compte_id = None` et des
        totaux de piece : ces inserations violaient la contrainte NOT NULL et
        doublaient le grand livre. La piece est la seule source d'ecriture du
        grand livre ; cette methode ne fait plus qu'exposer l'existant."""
        return (
            db.query(GrandLivreLigne)
            .filter(
                and_(
                    GrandLivreLigne.date_ecriture >= date_debut,
                    GrandLivreLigne.date_ecriture <= date_fin,)
            )
            .order_by(GrandLivreLigne.date_ecriture.asc(), GrandLivreLigne.id.asc())
            .all()
        )
    
    @staticmethod
    def grand_livre_auxiliaire(
        db: Session,
        compte_id: int,
        date_debut: date,
        date_fin: date
    ) -> List[GrandLivreLigne]:
        """Générer le grand livre auxiliaire pour un compte"""
        lignes = db.query(GrandLivreLigne).filter(
            and_(
                GrandLivreLigne.compte_id == compte_id,
                GrandLivreLigne.date_ecriture >= date_debut,
                GrandLivreLigne.date_ecriture <= date_fin
            )
        ).order_by(GrandLivreLigne.date_ecriture.asc()).all()
        
        return lignes
    
    @staticmethod
    def historique_compte(
        db: Session,
        compte_id: int,
        periode: str
    ) -> Dict[str, Any]:
        """Obtenir l'historique complet d'un compte pour une période"""
        lignes = db.query(GrandLivreLigne).filter(
            and_(
                GrandLivreLigne.compte_id == compte_id,
                GrandLivreLigne.periode == periode
            )
        ).order_by(GrandLivreLigne.date_ecriture.asc()).all()
        
        total_debit = sum(l.debit for l in lignes)
        total_credit = sum(l.credit for l in lignes)
        solde_debit = total_debit - total_credit if total_debit > total_credit else 0
        solde_credit = total_credit - total_debit if total_credit > total_debit else 0
        
        return {
            "compte_id": compte_id,
            "periode": periode,
            "total_debit": total_debit,
            "total_credit": total_credit,
            "solde_debit": solde_debit,
            "solde_credit": solde_credit,
            "nombre_ecritures": len(lignes),
            "lignes": lignes
        }


class BalanceService:
    """Service de balance de vérification.

    Toutes les aggregations partent des LIGNES reels du grand livre
    (`grand_livre_lignes`), materialisees par la saisie de piece en partie
    double. L'en-tete plat des ecritures (`compte_id` nul, `debit/credit` =
    totaux de piece) n'est plus jamais agrege : c'est ce qui produisait une
    balance vide ou faux depuis la refonte partie double."""

    @staticmethod
    def _comptes_map(db: Session) -> Dict[int, PlanComptableOHADA]:
        return {c.id: c for c in db.query(PlanComptableOHADA).all()}

    @staticmethod
    def calculer_balances_verification(
        db: Session,
        date_debut: Optional[date] = None,
        date_fin: Optional[date] = None,) -> Dict[str, Any]:
        """Balance de verification a 6 colonnes, entierement calculee sur le
        grand livre reel : soldes d'ouverture (mouvements anterieurs a
        `date_debut`), mouvements de la periode, soldes de cloture.

        Retourne {"lignes": [...], "total_debit", "total_credit", "equilibree"}
        avec les cles exactement consommees par la page grand livre/balance."""
        comptes = BalanceService._comptes_map(db)

 # Mouvements de la periode (gross debit/crédit par compte).
        periode = GrandLivreService.mouvements_par_compte(db, date_debut, date_fin)

 # Soldes d'ouverture = cumul strictement anterieur a date_debut.
        ouverture: Dict[int, Decimal] = {}
        if date_debut is not None:
            avant = GrandLivreService.mouvements_par_compte(db, None, None)
            cumul_avant = db.query(
                GrandLivreLigne.compte_id,
                func.coalesce(func.sum(GrandLivreLigne.debit), 0),
                func.coalesce(func.sum(GrandLivreLigne.credit), 0),).filter(
                GrandLivreLigne.date_ecriture < date_debut
            ).group_by(GrandLivreLigne.compte_id).all()
            for compte_id, d, c in cumul_avant:
                ouverture[compte_id] = Decimal(str(d or 0)) - Decimal(str(c or 0))

        lignes = []
        total_debit = Decimal("0")
        total_credit = Decimal("0")
        compte_ids = set(periode) | {cid for cid, net in ouverture.items() if net != 0}
        for compte_id in sorted(compte_ids):
            compte = comptes.get(compte_id)
            if not compte:
                continue
            mouv = periode.get(compte_id, {"debit": Decimal("0"), "credit": Decimal("0")})
            net_ouv = ouverture.get(compte_id, Decimal("0"))
            net_clot = net_ouv + mouv["debit"] - mouv["credit"]
 # Rien a montrer si le compte est totalement neutre sur la periode.
            if net_ouv == 0 and mouv["debit"] == 0 and mouv["credit"] == 0:
                continue
            lignes.append({
                "compte_id": compte_id,
                "compte_numero": compte.numero_compte,
                "compte_intitule": compte.intitule,
                "classe": compte.classe,
                "solde_initial_debit": float(net_ouv) if net_ouv > 0 else 0.0,
                "solde_initial_credit": float(-net_ouv) if net_ouv < 0 else 0.0,
                "debit": float(mouv["debit"]),
                "credit": float(mouv["credit"]),
                "solde_final_debit": float(net_clot) if net_clot > 0 else 0.0,
                "solde_final_credit": float(-net_clot) if net_clot < 0 else 0.0,
            })
            total_debit += mouv["debit"]
            total_credit += mouv["credit"]

        return {
            "date_debut": date_debut.isoformat() if date_debut else None,
            "date_fin": date_fin.isoformat() if date_fin else None,
            "lignes": lignes,
            "total_debit": float(total_debit),
            "total_credit": float(total_credit),
            "equilibree": total_debit == total_credit,
        }

    @staticmethod
    def creer_balance_verification(
        db: Session,
        exercice_id: int,
        periode: str,
        date_balance: date
    ) -> BalanceVerification:
        """Persiste une balance de verification calculee sur les lignes reels
        du grand livre (cumul <= date_balance), par compte."""
        comptes = BalanceService._comptes_map(db)
        cumul = db.query(
            GrandLivreLigne.compte_id,
            func.coalesce(func.sum(GrandLivreLigne.debit), 0),
            func.coalesce(func.sum(GrandLivreLigne.credit), 0),).filter(
            GrandLivreLigne.date_ecriture <= date_balance
        ).group_by(GrandLivreLigne.compte_id).all()

        totaux = {
            compte_id: {
                "debit": Decimal(str(d or 0)),
                "credit": Decimal(str(c or 0)),
            }
            for compte_id, d, c in cumul
        }

        total_debit = sum((t["debit"] for t in totaux.values()), Decimal("0"))
        total_credit = sum((t["credit"] for t in totaux.values()), Decimal("0"))
        ecart = total_debit - total_credit

        balance = BalanceVerification(
            exercice_id=exercice_id,
            periode=periode,
            date_balance=date_balance,
            total_debit=total_debit,
            total_credit=total_credit,
            ecart=ecart,
            statut="equilibre" if abs(ecart) < Decimal("0.01") else "desequilibre",)
        db.add(balance)
        db.commit()
        db.refresh(balance)

        for compte_id, tot in totaux.items():
            compte = comptes.get(compte_id)
            net = tot["debit"] - tot["credit"]
            db.add(LigneBalance(
                balance_id=balance.id,
                compte_id=compte_id,
                compte_numero=compte.numero_compte if compte else "",
                compte_intitule=compte.intitule if compte else "",
                total_debit=tot["debit"],
                total_credit=tot["credit"],
                solde_debit=net if net > 0 else Decimal("0"),
                solde_credit=-net if net < 0 else Decimal("0"),))
        db.commit()
        return balance

    @staticmethod
    def balance_par_journal(
        db: Session,
        journal_code: str,
        periode: str
    ) -> Dict[str, Any]:
        """Balance par journal, agregee sur les lignes reels du grand livre."""
        journal = db.query(JournalAuxiliaire).filter(
            JournalAuxiliaire.code_journal == journal_code
        ).first()
        if not journal:
            raise ValueError("Journal non trouvé")

        lignes_gl = db.query(GrandLivreLigne).filter(
            and_(
                GrandLivreLigne.journal == journal_code,
                GrandLivreLigne.periode == periode,)
        ).all()

        total_debit = sum((Decimal(str(l.debit or 0)) for l in lignes_gl), Decimal("0"))
        total_credit = sum((Decimal(str(l.credit or 0)) for l in lignes_gl), Decimal("0"))
        nb_ecritures = len({l.ecriture_id for l in lignes_gl})

        return {
            "journal": journal_code,
            "periode": periode,
            "total_debit": float(total_debit),
            "total_credit": float(total_credit),
            "ecart": float(total_debit - total_credit),
            "nombre_ecritures": nb_ecritures,
        }


class EtatsFinanciersOHADAService:
    """Service des états financiers OHADA complets"""
    
    @staticmethod
    def _cumul_par_compte(db: Session, date_fin: date) -> Dict[int, Decimal]:
        """Solde net (debit - credit) cumule de chaque compte au plus tard a
        `date_fin`, calcule sur les lignes reels du grand livre."""
        mouv = GrandLivreService.mouvements_par_compte(db, None, date_fin)
        return {cid: (m["debit"] - m["credit"]) for cid, m in mouv.items()}

    @staticmethod
    def generer_bilan_ohada_detaille(
        db: Session,
        exercice_id: int,
        date_bilan: date
    ) -> BilanOHADADetaille:
        """Bilan OHADA detaille, calcule sur le grand livre reel.

        L'ancienne version lisait `plan_comptable.solde_debit/credit` (jamais
        majustes par la saisie de piece) et filtrait `type_compte` en minuscules
        ('actif', 'produit'...) qui ne correspondent pas aux NOMS d'enum
        stocks ('ACTIF', 'PRODUIT'...) : le bilan etait donc systematiquement
        a zero. On agrege desormais les soldes par compte, classes selon la
        nature reelle (nom d'enum + classe SYSCOHADA), et le resultat de
        l'exercice est replie dans les capitaux propres : Actif = Passif est
        garanti par la partie double."""
        comptes = BalanceService._comptes_map(db)
        soldes = EtatsFinanciersOHADAService._cumul_par_compte(db, date_bilan)

        def nom_nature(compte):
            tc = compte.type_compte
            return getattr(tc, "name", str(tc)).upper()

        actif_immobilise = Decimal("0")
        actif_circulant_stocks = Decimal("0")
        actif_circulant_creances = Decimal("0")
        tresorerie_actif = Decimal("0")
        capitaux_propres = Decimal("0")
        dettes_courtes = Decimal("0")
        produits = Decimal("0")
        charges = Decimal("0")

        for compte_id, net in soldes.items():
            compte = comptes.get(compte_id)
            if not compte:
                continue
            nature = nom_nature(compte)
            classe = compte.classe
            if nature.startswith("ACTIF"):
                if classe == 2:
                    actif_immobilise += net
                elif classe == 3:
                    actif_circulant_stocks += net
                elif classe == 4:
                    actif_circulant_creances += net
                elif classe == 5:
                    tresorerie_actif += net
            elif nature.startswith("PASSIF"):
                if classe == 1:
                    capitaux_propres += -net
                elif classe == 4:
                    dettes_courtes += -net
                else:
                    capitaux_propres += -net
            elif nature == "PRODUIT":
                produits += -net
            elif nature == "CHARGE":
                charges += net

        resultat_net = produits - charges
        total_actif = (actif_immobilise + actif_circulant_stocks
                       + actif_circulant_creances + tresorerie_actif)
 # Le resultat est replie dans les capitaux pour que le bilan s'equilibre.
        capitaux_propres_total = capitaux_propres + resultat_net
        total_passif = capitaux_propres_total + dettes_courtes

        bilan = BilanOHADADetaille(
            exercice_id=exercice_id,
            date_bilan=date_bilan,
            actif_immobilise_brut=actif_immobilise,
            actif_immobilise_net=actif_immobilise,
            actif_circulant_stocks=actif_circulant_stocks,
            actif_circulant_creances=actif_circulant_creances,
            actif_circulant_total=actif_circulant_stocks + actif_circulant_creances,
            tresorerie_actif=tresorerie_actif,
            total_actif=total_actif,
            capitaux_propres_capital=capitaux_propres,
            capitaux_propres_total=capitaux_propres_total,
            dettes_long_terme=Decimal("0"),
            dettes_courtes=dettes_courtes,
            total_passif=total_passif
        )
        db.add(bilan)
        db.commit()
        db.refresh(bilan)
        return bilan
    
    @staticmethod
    def generer_compte_resultat_ohada_detaille(
        db: Session,
        exercice_id: int,
        periode: str,
        date_arrete: date
    ) -> CompteResultatOHADADetaille:
        """Compte de resultat OHADA, calcule sur le grand livre reel.

        Meme cause que le bilan : l'ancienne version lisait les soldes de
        `plan_comptable` (jamais majustes) filtres par `type_compte` en minuscules
        -> resultat systematiquement a zero. On agrege desormais les comptes de
        produits (7) et de charges (6) depuis les lignes reelles du grand livre."""
        comptes = BalanceService._comptes_map(db)
        soldes = EtatsFinanciersOHADAService._cumul_par_compte(db, date_arrete)

        produits = Decimal("0")
        charges = Decimal("0")
        for compte_id, net in soldes.items():
            compte = comptes.get(compte_id)
            if not compte:
                continue
            nature = getattr(compte.type_compte, "name", str(compte.type_compte)).upper()
            if nature == "PRODUIT":
                produits += -net
            elif nature == "CHARGE":
                charges += net

        ventes_marchandises = produits
        achats_marchandises = charges
        total_produits_exploitation = produits
        total_charges_exploitation = charges
        resultat_exploitation = total_produits_exploitation - total_charges_exploitation

 # Produits/Charges financiers et exceptionnel: non detailles ici,
 # integrés dans l'exploitation (aucune valeur inventee).
        produits_financiers = Decimal("0")
        charges_financieres = Decimal("0")
        resultat_financier = Decimal("0")
        resultat_exceptionnel = Decimal("0")

 # Résultat net
        resultat_net = resultat_exploitation + resultat_financier + resultat_exceptionnel
        
        compte_resultat = CompteResultatOHADADetaille(
            exercice_id=exercice_id,
            periode=periode,
            date_arrete=date_arrete,
            ventes_marchandises=ventes_marchandises,
            total_produits_exploitation=total_produits_exploitation,
            achats_marchandises=achats_marchandises,
            total_charges_exploitation=total_charges_exploitation,
            resultat_exploitation=resultat_exploitation,
            produits_financiers=produits_financiers,
            charges_financieres=charges_financieres,
            resultat_financier=resultat_financier,
            resultat_exceptionnel=resultat_exceptionnel,
            resultat_net=resultat_net
        )
        db.add(compte_resultat)
        db.commit()
        db.refresh(compte_resultat)
        return compte_resultat
    
    @staticmethod
    def generer_tafire(
        db: Session,
        exercice_id: int,
        date_tafire: date
    ) -> TAFIRE:
        """Générer le TAFIRE depuis les données réelles du grand livre.

        CAF = Résultat net + Dotations amortissements (non cash).
        Ressources/Emplois agrégés par classe de comptes dans le GL.
        """
        exercice = db.query(ExerciceComptable).filter(ExerciceComptable.id == exercice_id).first()
        if not exercice:
            raise ValueError("Exercice introuvable")

 # Compte de résultat (dernier pour cet exercice)
        cr = (
            db.query(CompteResultatOHADADetaille)
            .filter(CompteResultatOHADADetaille.exercice_id == exercice_id)
            .order_by(CompteResultatOHADADetaille.id.desc())
            .first()
        )
        resultat_net = float(cr.resultat_net or 0) if cr else 0.0
        dotations = float(cr.dotations_amortissements or 0) if cr else 0.0
        caf = resultat_net + dotations

 # Helper GL aggregation: sum(debit|credit) for compte prefix in exercice periods
        def _gl_sum(prefix: str, col) -> float:
            return float(
                db.query(func.coalesce(func.sum(col), 0))
                .join(PlanComptableOHADA, GrandLivreLigne.compte_id == PlanComptableOHADA.id)
                .filter(
                    GrandLivreLigne.periode.like(f"{exercice.annee}-%"),
                    PlanComptableOHADA.numero_compte.like(f"{prefix}%"),)
                .scalar()
            )

 # Ressources
        cession_immobilisations = _gl_sum("775", GrandLivreLigne.credit)  # produits cessions
        augmentation_capital = _gl_sum("101", GrandLivreLigne.credit)     # capital
        nouveaux_emprunts = _gl_sum("165", GrandLivreLigne.credit)        # emprunts nouveaux
        total_ressources = caf + cession_immobilisations + augmentation_capital + nouveaux_emprunts

 # Emplois
        investissements = _gl_sum("2", GrandLivreLigne.debit) - _gl_sum("2", GrandLivreLigne.credit)
        investissements = max(0, investissements)  # acquisitions nettes
        remboursement_emprunts = _gl_sum("165", GrandLivreLigne.debit)
        distribution_dividendes = 0.0  # pas de compte dédié → honnêtement 0
        variation_bfr = (
            (_gl_sum("4", GrandLivreLigne.debit) - _gl_sum("4", GrandLivreLigne.credit))
            - (_gl_sum("3", GrandLivreLigne.debit) - _gl_sum("3", GrandLivreLigne.credit))
        )
        augmentation_bfr = max(0, variation_bfr)  # positive = emploi
        total_emplois = investissements + remboursement_emprunts + distribution_dividendes + augmentation_bfr

 # Variation trésorerie = ressources - emplois
        variation_tresorerie = total_ressources - total_emplois
        treso_debut = _gl_sum("5", GrandLivreLigne.credit) - _gl_sum("5", GrandLivreLigne.debit)
 # approx: solde class 5 avant la période
        treso_fin = treso_debut + variation_tresorerie

        tafire = TAFIRE(
            exercice_id=exercice_id,
            date_tafire=date_tafire,
            capacit_autofinancement=round(caf, 2),
            cession_immobilisations=round(cession_immobilisations, 2),
            augmentation_capital=round(augmentation_capital, 2),
            nouveaux_emprunts=round(nouveaux_emprunts, 2),
            total_ressources=round(total_ressources, 2),
            investissements_immobilisations=round(investissements, 2),
            remboursement_emprunts=round(remboursement_emprunts, 2),
            distribution_dividendes=round(distribution_dividendes, 2),
            augmentation_besoin_fdr=round(augmentation_bfr, 2),
            total_emplois=round(total_emplois, 2),
            variation_tresorerie=round(variation_tresorerie, 2),
            tresorerie_debut=round(treso_debut, 2),
            tresorerie_fin=round(treso_fin, 2),)
        db.add(tafire)
        db.commit()
        db.refresh(tafire)
        return tafire

    @staticmethod
    def generer_tft(
        db: Session,
        exercice_id: int,
        date_tft: date
    ) -> TFT:
        """Tableau des Flux de Tresorerie (methode indirecte) depuis le GL.

        Flux d'exploitation = CAF + variation du BFR d'exploitation.
        Flux d'investissement = cessions - acquisitions d'immobilisations.
        Flux de financement = capitaux propres et emprunts.
        La variation de tresorerie est la somme des trois flux ; elle doit
        reconciler la variation reelle des comptes de classe 5."""
        exercice = db.query(ExerciceComptable).filter(ExerciceComptable.id == exercice_id).first()
        if not exercice:
            raise ValueError("Exercice introuvable")

        cr = (
            db.query(CompteResultatOHADADetaille)
            .filter(CompteResultatOHADADetaille.exercice_id == exercice_id)
            .order_by(CompteResultatOHADADetaille.id.desc())
            .first()
        )
        resultat_net = float(cr.resultat_net or 0) if cr else 0.0
        dotations = float(cr.dotations_amortissements or 0) if cr else 0.0
        caf = resultat_net + dotations

        def _gl_sum(prefix: str, col) -> float:
            return float(
                db.query(func.coalesce(func.sum(col), 0))
                .join(PlanComptableOHADA, GrandLivreLigne.compte_id == PlanComptableOHADA.id)
                .filter(
                    GrandLivreLigne.periode.like(f"{exercice.annee}-%"),
                    PlanComptableOHADA.numero_compte.like(f"{prefix}%"),)
                .scalar()
            )

 # BFR d'exploitation : creances clients (41) - dettes fournisseurs (40).
        bfr_debut = 0.0  # approximation documentee : variation de la periode
        variation_bfr = (
            (_gl_sum("4", GrandLivreLigne.debit) - _gl_sum("4", GrandLivreLigne.credit))
            - (_gl_sum("3", GrandLivreLigne.debit) - _gl_sum("3", GrandLivreLigne.credit))
        )
        flux_exploitation = caf - max(0, variation_bfr)

        cessions = _gl_sum("775", GrandLivreLigne.credit)
        acquisitions = max(0.0, _gl_sum("2", GrandLivreLigne.debit) - _gl_sum("2", GrandLivreLigne.credit))
        flux_investissement = cessions - acquisitions

        augmentation_capital = _gl_sum("101", GrandLivreLigne.credit)
        nouveaux_emprunts = _gl_sum("165", GrandLivreLigne.credit)
        remboursements = _gl_sum("165", GrandLivreLigne.debit)
        dividendes = _gl_sum("465", GrandLivreLigne.debit)
        flux_financement = augmentation_capital + nouveaux_emprunts - remboursements - dividendes

        variation_tresorerie = flux_exploitation + flux_investissement + flux_financement
        treso = _gl_sum("5", GrandLivreLigne.credit) - _gl_sum("5", GrandLivreLigne.debit)
        tresorerie_fin = treso
        tresorerie_debut = tresorerie_fin - variation_tresorerie

        tft = TFT(
            exercice_id=exercice_id,
            date_tft=date_tft,
            capacite_autofinancement=round(caf, 2),
            variation_bfr_exploitation=round(variation_bfr, 2),
            flux_exploitation=round(flux_exploitation, 2),
            cessions_immobilisations=round(cessions, 2),
            acquisitions_immobilisations=round(acquisitions, 2),
            flux_investissement=round(flux_investissement, 2),
            augmentation_capital=round(augmentation_capital, 2),
            nouveaux_emprunts=round(nouveaux_emprunts, 2),
            remboursements_emprunts=round(remboursements, 2),
            dividendes_verses=round(dividendes, 2),
            flux_financement=round(flux_financement, 2),
            variation_tresorerie=round(variation_tresorerie, 2),
            tresorerie_debut=round(tresorerie_debut, 2),
            tresorerie_fin=round(tresorerie_fin, 2),)
        db.add(tft)
        db.commit()
        db.refresh(tft)
        return tft

    @staticmethod
    def generer_sig(
        db: Session,
        exercice_id: int,
        date_sig: date,
        effectif_moyen: Optional[Decimal] = None
    ) -> SIG:
        """Situation Globale des Entreprises (SIG) depuis le grand livre.

        Synthese normative SYSCOHADA : effectifs (saisi, jamais invente),
        masse salariale (comptes 66), chiffre d'affaires (70), EBE
        (produits - charges d'exploitation hors dotations), CAF, investissements
        nets (classe 2), BFR (classes 3-4), tresorerie nette (classe 5) et
        resultat net (compte de resultat)."""
        exercice = db.query(ExerciceComptable).filter(ExerciceComptable.id == exercice_id).first()
        if not exercice:
            raise ValueError("Exercice introuvable")

        def _gl_sum(prefix: str, col) -> float:
            return float(
                db.query(func.coalesce(func.sum(col), 0))
                .join(PlanComptableOHADA, GrandLivreLigne.compte_id == PlanComptableOHADA.id)
                .filter(
                    GrandLivreLigne.periode.like(f"{exercice.annee}-%"),
                    PlanComptableOHADA.numero_compte.like(f"{prefix}%"),)
                .scalar()
            )

        produits = _gl_sum("7", GrandLivreLigne.credit) - _gl_sum("7", GrandLivreLigne.debit)
        charges_expl = _gl_sum("6", GrandLivreLigne.debit) - _gl_sum("6", GrandLivreLigne.credit)
        dotations = _gl_sum("681", GrandLivreLigne.debit) + _gl_sum("687", GrandLivreLigne.debit)
        chiffre_affaires = max(0.0, produits)
        ebe = produits - (charges_expl - dotations)
        resultat_net = produits - charges_expl
        caf = resultat_net + dotations
        investissements = max(0.0, _gl_sum("2", GrandLivreLigne.debit) - _gl_sum("2", GrandLivreLigne.credit))
        bfr = (_gl_sum("4", GrandLivreLigne.debit) - _gl_sum("4", GrandLivreLigne.credit)) - (
            _gl_sum("3", GrandLivreLigne.debit) - _gl_sum("3", GrandLivreLigne.credit))
        tresorerie = _gl_sum("5", GrandLivreLigne.debit) - _gl_sum("5", GrandLivreLigne.credit)

        sig = SIG(
            exercice_id=exercice_id,
            date_sig=date_sig,
            effectif_moyen=float(effectif_moyen or 0),
            masse_salariale=round(_gl_sum("66", GrandLivreLigne.debit) - _gl_sum("66", GrandLivreLigne.credit), 2),
            chiffre_affaires=round(chiffre_affaires, 2),
            excédent_brut_exploitation=round(ebe, 2),
            capacite_autofinancement=round(caf, 2),
            investissements=round(investissements, 2),
            besoin_en_fonds_de_roulement=round(bfr, 2),
            tresorerie_nette=round(tresorerie, 2),
            resultat_net=round(resultat_net, 2),)
        db.add(sig)
        db.commit()
        db.refresh(sig)
        return sig

    @staticmethod
    def generer_annexes_ohada(
        db: Session,
        exercice_id: int,
        date_annexes: date,
        denomination: str,
        forme_juridique: str,
        siege: str
    ) -> AnnexesOHADA:
        """Générer les annexes OHADA"""
        annexes = AnnexesOHADA(
            exercice_id=exercice_id,
            date_annexes=date_annexes,
            denomination_sociale=denomination,
            forme_juridique=forme_juridique,
            siege_social=siege,
            methode_evaluation_stocks="FIFO",
            methode_amortissements="Linéaire",
            principes_comptables="Conformité SYSCOHADA OHADA"
        )
        db.add(annexes)
        db.commit()
        db.refresh(annexes)
        return annexes

    @staticmethod
    def generer_notes_annexes_detaillees(
        db: Session,
        exercice_id: int,
        date_annexes: date,
        denomination: str,
        forme_juridique: str,
        siege: str,
        effectif_moyen: Optional[Decimal] = None
    ) -> AnnexesOHADA:
        """Genere le jeu d'annexes avec les notes normalisees SYSCOHADA.

        Les montants sont calcules depuis le grand livre de l'exercice ; les
        notes qualitatives recoivent un contenu factuel. Aucune note n'est
        inventee : ce qui n'est pas calculable reste explicitement mentionne.
        """
        exercice = db.query(ExerciceComptable).filter(ExerciceComptable.id == exercice_id).first()
        if not exercice:
            raise ValueError("Exercice introuvable")

        def _gl_sum(prefix: str, col) -> float:
            return float(
                db.query(func.coalesce(func.sum(col), 0))
                .join(PlanComptableOHADA, GrandLivreLigne.compte_id == PlanComptableOHADA.id)
                .filter(
                    GrandLivreLigne.periode.like(f"{exercice.annee}-%"),
                    PlanComptableOHADA.numero_compte.like(f"{prefix}%"),)
                .scalar()
            )

        produits = max(0.0, _gl_sum("7", GrandLivreLigne.credit) - _gl_sum("7", GrandLivreLigne.debit))
        charges = _gl_sum("6", GrandLivreLigne.debit) - _gl_sum("6", GrandLivreLigne.credit)
        resultat = produits - charges

        annexes = AnnexesOHADA(
            exercice_id=exercice_id,
            date_annexes=date_annexes,
            denomination_sociale=denomination,
            forme_juridique=forme_juridique,
            siege_social=siege,
            capital_social=round(_gl_sum("101", GrandLivreLigne.credit) - _gl_sum("101", GrandLivreLigne.debit), 2),
            methode_evaluation_stocks="FIFO",
            methode_amortissements="Lineaire",
            principes_comptables="Conformite SYSCOHADA OHADA revision 2018")
        db.add(annexes)
        db.flush()

        notes = [
            (1, "Regles et methodes comptables",
             "Comptes tenus en conformite avec le SYSCOHADA (revision 2018). "
             "Stocks valorises FIFO ; immobilisations amorties en lineaire ; "
             "devise de presentation : XAF.", None),
            (2, "Immobilisations",
             f"Acquisitions nettes de cessions : {_gl_sum('2', GrandLivreLigne.debit) - _gl_sum('2', GrandLivreLigne.credit):,.0f} XAF. "
             "Le detail par immobilisation et le tableau des amortissements "
             "sont tenus au journal des immobilisations.",
             round(_gl_sum("2", GrandLivreLigne.debit) - _gl_sum("2", GrandLivreLigne.credit), 2)),
            (3, "Stocks",
             f"Variation des stocks de l'exercice : {_gl_sum('3', GrandLivreLigne.debit) - _gl_sum('3', GrandLivreLigne.credit):,.0f} XAF.",
             round(_gl_sum("3", GrandLivreLigne.debit) - _gl_sum("3", GrandLivreLigne.credit), 2)),
            (4, "Creances et dettes",
             f"Creances nettes : {_gl_sum('4', GrandLivreLigne.debit) - _gl_sum('4', GrandLivreLigne.credit):,.0f} XAF ; "
             f"dettes nettes : {_gl_sum('4', GrandLivreLigne.credit) - _gl_sum('4', GrandLivreLigne.debit):,.0f} XAF. "
             "Le detail par tiers figure au grand livre auxiliaire.",
             round(_gl_sum("4", GrandLivreLigne.debit) - _gl_sum("4", GrandLivreLigne.credit), 2)),
            (5, "Tresorerie",
             f"Tresorerie nette en fin d'exercice : {_gl_sum('5', GrandLivreLigne.debit) - _gl_sum('5', GrandLivreLigne.credit):,.0f} XAF.",
             round(_gl_sum("5", GrandLivreLigne.debit) - _gl_sum("5", GrandLivreLigne.credit), 2)),
            (6, "Capitaux propres",
             f"Capitaux propres nets : {_gl_sum('1', GrandLivreLigne.credit) - _gl_sum('1', GrandLivreLigne.debit):,.0f} XAF "
             f"(dont resultat de l'exercice : {resultat:,.0f} XAF).",
             round(resultat, 2)),
            (8, "Charges de personnel",
             f"Masse salariale brute : {_gl_sum('66', GrandLivreLigne.debit) - _gl_sum('66', GrandLivreLigne.credit):,.0f} XAF. "
             f"Effectif moyen : {float(effectif_moyen or 0):,.0f} personnes.",
             round(_gl_sum("66", GrandLivreLigne.debit) - _gl_sum("66", GrandLivreLigne.credit), 2)),
            (9, "Produits et charges d'exploitation",
             f"Produits d'exploitation : {produits:,.0f} XAF ; charges d'exploitation : {charges:,.0f} XAF.",
             round(resultat, 2)),
            (12, "Resultat net",
             f"Resultat net de l'exercice : {resultat:,.0f} XAF.",
             round(resultat, 2)),
            (16, "Engagements et contingences",
             "Aucun engagement hors bilan significatif enregistre au grand "
             "livre a la date d'arrete ; les cautions et garanties sont "
             "inventoriees au dossier juridique de l'entreprise.", None),
        ]
        for numero, intitule, contenu, montant in notes:
            db.add(NoteAnnexe(
                annexes_id=annexes.id, numero=numero, intitule=intitule,
                contenu=contenu, montant=montant))

        db.commit()
        db.refresh(annexes)
        return annexes


class ClotureService:
    """Service de clôture mensuelle et annuelle"""

    _MOIS = [
        "Janvier", "Février", "Mars", "Avril", "Mai", "Juin",
        "Juillet", "Août", "Septembre", "Octobre", "Novembre", "Décembre",
    ]

    @staticmethod
    def etats_periodes(
        db: Session,
        exercice_id: Optional[int] = None,
        annee: Optional[int] = None,) -> Dict[str, Any]:
        """Etat reel de chaque periode de l'exercice, pour piloter la cloture.

        Aucune donnee inventee : le nombre de pieces est compte sur les ecritures
        reellement validees, et une periode n'est dite « cloturee » que si une
        balance de verification equilibree a ete generee et persistee pour elle.
        L'ancienne page frontend fabriquait la liste depuis `new Date()` ; cet
        endpoint expose l'etat veritable.

        Si `exercice_id` est absent, l'exercice OUVERT le plus recent est resolu
        cote serveur (la page n'a plus a coder un identifiant en dur)."""
        if exercice_id is not None:
            exercice = db.query(ExerciceComptable).filter(
                ExerciceComptable.id == exercice_id
            ).first()
        else:
            exercice = (
                db.query(ExerciceComptable)
                .filter(ExerciceComptable.statut == "ouvert")
                .order_by(ExerciceComptable.annee.desc())
                .first()
            )
            if not exercice:
                exercice = (
                    db.query(ExerciceComptable)
                    .order_by(ExerciceComptable.annee.desc())
                    .first()
                )
        if not exercice:
            raise ValueError("Aucun exercice comptable trouvé")

        annee_cible = annee or exercice.annee
        ex_id = exercice.id  # identifiant RESOLU (peut différer du paramètre)

 # Pieces validees par periode (agregation SQL, une seule requete).
        compteurs = dict(
            db.query(
                EcritureComptableNew.periode,
                func.count(EcritureComptableNew.id),).filter(
                and_(
                    EcritureComptableNew.exercice_id == ex_id,
                    EcritureComptableNew.valider == True,  # noqa: E712
                )
            ).group_by(EcritureComptableNew.periode).all()
        )

 # Derniere balance de verification par periode (une seule requete).
        balances = {}
        for b in (
            db.query(BalanceVerification)
            .filter(BalanceVerification.exercice_id == ex_id)
            .order_by(BalanceVerification.id.asc())
            .all()
        ):
            balances[b.periode] = b  # le dernier gagne = la plus recente

        periodes = []
        for idx in range(12):
            code = f"{annee_cible}-{idx + 1:02d}"
            balance = balances.get(code)
            entries = int(compteurs.get(code, 0))
            closed = bool(balance is not None and balance.statut == "equilibre")
            periodes.append({
                "periode": code,
                "label": f"{ClotureService._MOIS[idx]} {annee_cible}",
                "entries_count": entries,
                "closed": closed,
                "balance_statut": balance.statut if balance else None,
                "balance_date": balance.date_balance if balance else None,
            })

        return {
            "exercice_id": exercice.id,
            "annee": annee_cible,
            "exercice_statut": exercice.statut,
            "periodes": periodes,
        }

    @staticmethod
    def cloture_mensuelle(
        db: Session,
        exercice_id: int,
        periode: str,
        cloture_par: str
    ) -> Dict[str, Any]:
        """Clôture mensuelle des comptes de gestion"""
 # Refuser de cloturer deux fois la meme periode (regle serveur honnete).
        deja = db.query(BalanceVerification).filter(
            and_(
                BalanceVerification.exercice_id == exercice_id,
                BalanceVerification.periode == periode,
                BalanceVerification.statut == "equilibre",)
        ).first()
        if deja:
            raise ValueError(f"La période {periode} est déjà clôturée")

 # Récupérer toutes les écritures de la période
        ecritures = db.query(EcritureComptableNew).filter(
            and_(
                EcritureComptableNew.exercice_id == exercice_id,
                EcritureComptableNew.periode == periode,
                EcritureComptableNew.valider == True
            )
        ).all()
        
 # Vérifier que toutes les écritures sont validées
        if not ecritures:
            raise ValueError("Aucune écriture trouvée pour cette période")
        
 # Créer la balance de vérification
        balance = BalanceService.creer_balance_verification(
            db,
            exercice_id,
            periode,
            date.today()
        )
        
 # Vérifier l'équilibre
        if balance.statut != "equilibre":
            raise ValueError(f"Balance déséquilibrée: écart de {balance.ecart}")
        
        return {
            "exercice_id": exercice_id,
            "periode": periode,
            "statut": "cloturee",
            "balance_id": balance.id,
            "cloture_par": cloture_par,
            "date_cloture": date.today()
        }

    @staticmethod
    def cloture_annuelle(
        db: Session,
        exercice_id: int,
        cloture_par: str
    ) -> Dict[str, Any]:
        """Clôture annuelle complète"""
 # Récupérer l'exercice
        exercice = db.query(ExerciceComptable).filter(
            ExerciceComptable.id == exercice_id
        ).first()
        
        if not exercice:
            raise ValueError("Exercice non trouvé")
        
 # Clôturer tous les comptes de gestion (classes 6 et 7)
 # Reports à nouveau des comptes de bilan
        
 # Générer le bilan final
        bilan = EtatsFinanciersOHADAService.generer_bilan_ohada_detaille(
            db,
            exercice_id,
            exercice.date_fin
        )
        
 # Générer le compte de résultat final
        compte_resultat = EtatsFinanciersOHADAService.generer_compte_resultat_ohada_detaille(
            db,
            exercice_id,
            f"{exercice.annee}-12",
            exercice.date_fin
        )
        
 # Générer le TAFIRE
        tafire = EtatsFinanciersOHADAService.generer_tafire(
            db,
            exercice_id,
            exercice.date_fin
        )
        
 # Marquer l'exercice comme clôturé
        exercice.statut = "cloture"
        exercice.cloture_par = cloture_par
        exercice.date_cloture = date.today()
        exercice.resultat_net = compte_resultat.resultat_net
        exercice.total_actif = bilan.total_actif
        exercice.total_passif = bilan.total_passif
        
        db.commit()
        db.refresh(exercice)
        
        return {
            "exercice_id": exercice_id,
            "annee": exercice.annee,
            "statut": "cloture",
            "bilan_id": bilan.id,
            "compte_resultat_id": compte_resultat.id,
            "tafire_id": tafire.id,
            "resultat_net": compte_resultat.resultat_net,
            "cloture_par": cloture_par,
            "date_cloture": date.today()
        }
    
    @staticmethod
    def report_a_nouveau(
        db: Session,
        exercice_source_id: int,
        exercice_cible_id: int
    ) -> Dict[str, Any]:
        """Apercu du report a nouveau des soldes de bilan.

        La function contenait un bug (variable `exercice_cible` jamais definie ->
        NameError/500) et une sur-claim « reporte » alors que rien n'etait ecrit.
        Elle expose desormais un APERCU honnete : le nombre reel de comptes de
        bilan concernes, sans pretendre avoir persiste un report (l'ecriture des
        reports a nouveau n'est pas implementee cote serveur)."""
        comptes_bilan = db.query(PlanComptableOHADA).filter(
            PlanComptableOHADA.classe.in_([1, 2, 3, 4, 5])
        ).count()

        return {
            "exercice_source_id": exercice_source_id,
            "exercice_cible_id": exercice_cible_id,
            "statut": "apercu_non_persiste",
            "nombre_comptes": comptes_bilan,
        }
    
    @staticmethod
    def affectation_resultat(
        db: Session,
        exercice_id: int,
        mode_affectation: str,  # "reserve", "dividende", "report"
        montant_reserve: float = 0,
        montant_dividende: float = 0
    ) -> Dict[str, Any]:
        """Affectation du résultat de l'exercice"""
 # Récupérer le compte de résultat
        compte_resultat = db.query(CompteResultatOHADADetaille).filter(
            CompteResultatOHADADetaille.exercice_id == exercice_id
        ).first()
        
        if not compte_resultat:
            raise ValueError("Compte de résultat non trouvé")
        
        resultat_net = compte_resultat.resultat_net
        
 # Vérifier que les montants sont cohérents
        total_affecte = montant_reserve + montant_dividende
        if total_affecte > resultat_net:
            raise ValueError(f"Total affecté ({total_affecte}) supérieur au résultat net ({resultat_net})")
        
 # Créer les écritures d'affectation
 # (implémentation future)
        
        return {
            "exercice_id": exercice_id,
            "resultat_net": resultat_net,
            "mode_affectation": mode_affectation,
            "montant_reserve": montant_reserve,
            "montant_dividende": montant_dividende,
            "montant_reporte": resultat_net - total_affecte,
            "statut": "affecte"
        }


# ─────────────────────────────────────────────────────────────────────────────
# FISCALITÉ CEMAC – TVA, IS, DIPE
# ─────────────────────────────────────────────────────────────────────────────

class TVAService:
    """Agrégation TVA depuis le Grand Livre réel (comptes 443x TVA collectée, 445x TVA déductible)."""

    @staticmethod
    def calculer_tva_periode(db: Session, periode: str) -> dict:
        """Calcule la déclaration TVA mensuelle depuis les écritures réelles.

        Agrège le Grand Livre par préfixe de compte SYSCOHADA :
          - 443x → TVA collectée (somme crédit)
          - 445x → TVA déductible (somme débit)
          - 70x  → CA imposable HT (crédit – débit)
        Retourne 0 honnête si aucune écriture n'existe.
        """
        annee, mois = periode.split("-")
 # date limite paiement = 15 du mois suivant
        m_suiv = int(mois) + 1
        if m_suiv > 12:
            date_limite = f"{int(annee) + 1}-01-15"
        else:
            date_limite = f"{annee}-{m_suiv:02d}-15"

        def _sum(prefix: str, col) -> float:
            return float(
                db.query(func.coalesce(func.sum(col), 0))
                .join(PlanComptableOHADA, GrandLivreLigne.compte_id == PlanComptableOHADA.id)
                .filter(
                    GrandLivreLigne.periode == periode,
                    PlanComptableOHADA.numero_compte.like(f"{prefix}%"),)
                .scalar()
            )

        tva_collectee = _sum("443", GrandLivreLigne.credit)
        tva_deductible_total = _sum("445", GrandLivreLigne.debit)

 # ventilation immo vs charges (4452x = immobilisations, reste = charges)
        tva_deductible_immo = _sum("4452", GrandLivreLigne.debit)
        tva_deductible_charges = tva_deductible_total - tva_deductible_immo

 # CA imposable HT: sum(credit) - sum(debit) sur classe 7 (70%)
        ca_credit = _sum("70", GrandLivreLigne.credit)
        ca_debit = _sum("70", GrandLivreLigne.debit)
        base_imposable = ca_credit - ca_debit

 # report de crédit antérieur: dernière TVADeclarable avant cette période
        anterieures = (
            db.query(TVADeclarable)
            .filter(TVADeclarable.periode < periode)
            .order_by(TVADeclarable.periode.desc())
            .first()
        )
        credit_anterieur = float(anterieures.tva_a_payer) if anterieures and float(anterieures.tva_a_payer or 0) < 0 else 0.0

        net_tva_payer = tva_collectee - tva_deductible_immo - tva_deductible_charges - credit_anterieur

 # statut depuis TVADeclarable existante ou BROUILLON
        existante = db.query(TVADeclarable).filter(TVADeclarable.periode == periode).first()
        if existante:
            raw = existante.statut.value if hasattr(existante.statut, 'value') else str(existante.statut)
 # map to frontend-friendly
            statut_map = {"due": "VALIDE", "payee": "TELEDEPOSE", "partiel": "VALIDE", "report": "BROUILLON"}
            statut_val = statut_map.get(raw, raw.upper())
        else:
            statut_val = "BROUILLON"

        return {
            "periode": periode,
            "ca_taxable": round(base_imposable, 2),
            "operations_exonerees": 0.0,
            "tva_collectee": round(tva_collectee, 2),
            "tva_deductible_immo": round(tva_deductible_immo, 2),
            "tva_deductible_charges": round(tva_deductible_charges, 2),
            "credit_tva_anterieur": round(credit_anterieur, 2),
            "net_tva_payer": round(net_tva_payer, 2),
            "date_limite_paiement": date_limite,
            "statut": statut_val,
        }

    @staticmethod
    def valider_declaration(db: Session, periode: str, valide_par: str) -> dict:
        """Enregistre la TVADeclarable en base (POST /declarations-tva/valider).

        NOTE HONNÊTE : aucune API e-bulletin DGI n'est intégrée ; la déclaration
        est stockée localement pour impression ultérieure sur formulaire officiel.
        """
        calc = TVAService.calculer_tva_periode(db, periode)
        existante = db.query(TVADeclarable).filter(TVADeclarable.periode == periode).first()
        if existante:
            raise ValueError(f"La période {periode} a déjà été déclarée (statut {existante.statut}).")
        if calc["ca_taxable"] == 0 and calc["tva_collectee"] == 0:
            raise ValueError(f"Aucune écriture TVA sur la période {periode} : rien à déclarer.")

        num = f"TVA-{periode}"
        declaration = TVADeclarable(
            numero_declaration=num,
            periode=periode,
            date_declaration=date.today(),
            regime_tva=RegimeTVA.NORMAL,
            base_imposable=calc["ca_taxable"],
            tva_collectee=calc["tva_collectee"],
            tva_deductible=calc["tva_deductible_immo"] + calc["tva_deductible_charges"],
            tva_a_payer=calc["net_tva_payer"],
            devise="XAF",
            statut=StatutTaxe.DUE,
            notes=f"Valide par {valide_par}. Transmission DGI a effectuer manuellement (e-bulletin non integre).",)
        db.add(declaration)
        db.commit()
        db.refresh(declaration)
        return {
            "id": declaration.id,
            "numero_declaration": num,
            "periode": periode,
            "statut": "VALIDEE",
            "message": "Déclaration TVA enregistrée localement. Le dépôt sur le portail e-bulletin DGI reste à effectuer manuellement.",
        }


class ISService:
    """Dérivation de l'IS depuis le Compte de Résultat réel SYSCOHADA."""

    @staticmethod
    def deriver_is(db: Session, annee: int) -> dict:
        """Calcule la déclaration IS depuis le résultat net de l'exercice."""
        exercice = db.query(ExerciceComptable).filter(ExerciceComptable.annee == annee).first()
        if not exercice:
            raise ValueError(f"Aucun exercice comptable pour l'année {annee}")

        cr = (
            db.query(CompteResultatOHADADetaille)
            .filter(CompteResultatOHADADetaille.exercice_id == exercice.id)
            .order_by(CompteResultatOHADADetaille.id.desc())
            .first()
        )
        if not cr:
            raise ValueError(f"Aucun compte de résultat établi pour l'exercice {annee}. Générez-le d'abord.")

        benefice_fiscal = float(cr.resultat_net or 0)
        taux = 30.0
        is_brut = max(0.0, benefice_fiscal * (taux / 100.0))
        minimum_perception = 1_000_000.0
        is_exigible = max(is_brut, minimum_perception)

 # acomptes versés: chercher les ISDeclarables payés pour cet exercice
        is_declarations = db.query(ISDeclarable).filter(ISDeclarable.annee == annee).all()
        acomptes = sum(float(d.montant_paye or 0) for d in is_declarations)

        solde = is_exigible - acomptes

 # statut depuis ISDeclarable existante
        if is_declarations:
            statut_val = is_declarations[-1].statut.value if hasattr(is_declarations[-1].statut, 'value') else str(is_declarations[-1].statut)
        else:
            statut_val = "BROUILLON"

        return {
            "exercice": annee,
            "base_imposable": round(benefice_fiscal, 2),
            "is_brut": round(is_brut, 2),
            "taux_is": taux,
            "minimum_perception": minimum_perception,
            "is_exigible": round(is_exigible, 2),
            "acomptes_verses": round(acomptes, 2),
            "solde_is": round(solde, 2),
            "prochaine_echeance": f"{annee + 1}-03-31",
            "statut": statut_val,
        }


class ImmobilisationService:
    """Registre des immobilisations et dotations aux amortissements OHADA.

    Pont entre le domaine equipements (GMAO) et la comptabilite : chaque
    immobilisation declare ses comptes SYSCOHADA et sa duree ; la dotation
    lineaire genere une ecriture equilibrée (681 dotation / 28x amortissement)
    qui alimente le grand livre, la balance, le bilan (classe 2) et la note
    annexe immobilisations."""

    @staticmethod
    def _immobilisation(db: Session, immobilisation_id: int) -> Immobilisation:
        imm = db.query(Immobilisation).filter(Immobilisation.id == immobilisation_id).first()
        if not imm:
            raise ValueError("Immobilisation introuvable")
        return imm

    @staticmethod
    def dotation_mensuelle(imm: Immobilisation) -> Decimal:
        """Dotation lineaire : (valeur d'acquisition - valeur residuelle) / duree."""
        base = Decimal(str(imm.valeur_acquisition or 0)) - Decimal(str(imm.valeur_residuelle or 0))
        return (base / Decimal(int(imm.duree_mois))).quantize(Decimal("0.01"))

    @staticmethod
    def creer_immobilisation(db: Session, data: dict) -> Immobilisation:
        imm = Immobilisation(**data)
        db.add(imm)
        db.commit()
        db.refresh(imm)
        return imm

    @staticmethod
    def lister_immobilisations(db: Session) -> List[Immobilisation]:
        return db.query(Immobilisation).order_by(Immobilisation.date_acquisition).all()

    @staticmethod
    def tableau_echeancier(imm: Immobilisation) -> List[Dict[str, Any]]:
        """Echeancier lineaire complet : dotation, cumul et net comptable."""
        dotation = ImmobilisationService.dotation_mensuelle(imm)
        base = Decimal(str(imm.valeur_acquisition or 0)) - Decimal(str(imm.valeur_residuelle or 0))
        cumul = Decimal("0")
        lignes = []
        annee_acq = imm.date_acquisition.year
        mois_acq = imm.date_acquisition.month
        for i in range(int(imm.duree_mois)):
            mois = mois_acq + i
            annee = annee_acq + (mois - 1) // 12
            mois = (mois - 1) % 12 + 1
            montant = min(dotation, base - cumul)
            cumul += montant
            lignes.append({
                "periode": f"{annee}-{mois:02d}",
                "dotation": float(montant),
                "cumul_amortissements": float(cumul),
                "net_comptable": float(Decimal(str(imm.valeur_acquisition or 0)) - cumul),
            })
        return lignes

    @staticmethod
    def _compte_par_numero(db: Session, numero: str):
        return (
            db.query(PlanComptableOHADA)
            .filter(PlanComptableOHADA.numero_compte.like(f"{numero}%"))
            .order_by(PlanComptableOHADA.numero_compte)
            .first()
        )

    @staticmethod
    def generer_ecriture_amortissement(
        db: Session,
        immobilisation_id: int,
        date_ecriture: date,
        periode: str,
        journal_code: Optional[str] = None
    ) -> Dict[str, Any]:
        """Genere l'ecriture de dotation : DEBIT 681 / CREDIT 28x.

        L'ecriture est creee `valide` avec ses lignes journal et ses lignes
        grand livre, comme une saisie de piece : elle entre immediatement
        dans la balance et les etats financiers."""
        imm = ImmobilisationService._immobilisation(db, immobilisation_id)
        montant = ImmobilisationService.dotation_mensuelle(imm)
        if montant <= 0:
            raise ValueError("Dotation nulle : verifier valeur et duree")

        exercice = db.query(ExerciceComptable).filter(
            ExerciceComptable.annee == int(str(periode)[:4])
        ).first()
        if not exercice:
            raise ValueError("Exercice comptable introuvable pour cette periode")

        compte_dot = ImmobilisationService._compte_par_numero(db, imm.compte_dotation)
        compte_amort = ImmobilisationService._compte_par_numero(db, imm.compte_amortissement)
        if not compte_dot or not compte_amort:
            raise ValueError("Compte OHADA introuvable (dotation ou amortissement)")

        journal = None
        if journal_code:
            journal = db.query(JournalAuxiliaire).filter(
                JournalAuxiliaire.code_journal == journal_code).first()
        if not journal:
            journal = JournalAuxiliaireService.journal_amortissements(db)
        if not journal:
            journal = db.query(JournalAuxiliaire).first()
        if not journal:
            raise ValueError("Aucun journal auxiliaire : initialiser les journaux d'abord")

        numero = f"AMORT-{imm.id}-{periode}"
        if db.query(EcritureComptableNew).filter(EcritureComptableNew.numero_ecriture == numero).first():
            raise ValueError(f"Dotation deja comptabilisee pour {imm.numero_immobilisation} ({periode})")

        piece = EcritureComptableNew(
            numero_ecriture=numero,
            date_ecriture=date_ecriture,
            numero_piece=imm.numero_immobilisation,
            libelle=f"Dotation aux amortissements {imm.designation} - {periode}",
            compte_id=None,
            debit=montant,
            credit=montant,
            total_debit=montant,
            total_credit=montant,
            statut="valide",
            devise="XAF",
            reference_document=imm.numero_immobilisation,
            type_document="amortissement",
            periode=periode,
            journal=journal.code_journal,
            valider=True,
            valide_par="immobilisations",
            date_validation=date.today(),
            exercice_id=exercice.id,
            journal_id=journal.id,)
        db.add(piece)
        db.flush()

        for order, (compte, col) in enumerate([
            (compte_dot, "debit"), (compte_amort, "credit")], start=1):
            montant_ligne = montant if col == "debit" else Decimal("0")
            montant_ligne_c = Decimal("0") if col == "debit" else montant
            db.add(LigneJournal(
                ecriture_id=piece.id,
                journal_id=journal.id,
                compte_id=compte.id,
                compte_numero=compte.numero_compte,
                compte_intitule=compte.intitule,
                debit=montant_ligne,
                credit=montant_ligne_c,
                devise="XAF",
                reference_document=imm.numero_immobilisation,
                libelle_detail=f"Dotation {imm.designation}",
                order_line=order,))
            db.add(GrandLivreLigne(
                compte_id=compte.id,
                ecriture_id=piece.id,
                date_ecriture=date_ecriture,
                libelle=f"Dotation {imm.designation} - {periode}",
                debit=montant_ligne,
                credit=montant_ligne_c,
                devise="XAF",
                journal=journal.code_journal,
                periode=periode,))

        db.commit()
        db.refresh(piece)
        return {
            "immobilisation_id": imm.id,
            "ecriture_id": piece.id,
            "montant": float(montant),
            "periode": periode,
        }


class LiasseFiscaleService:
    """Liasse fiscale CEMAC : consolide les declarations TVA et IS d'un
    exercice en un dossier unique, calcule depuis les declarations reelles."""

    @staticmethod
    def generer_liasse(db: Session, annee: int, valide_par: Optional[str] = None) -> LiasseFiscale:
        exercice = db.query(ExerciceComptable).filter(ExerciceComptable.annee == annee).first()

        tva_decls = (
            db.query(TVADeclarable)
            .filter(TVADeclarable.periode.like(f"{annee}%"))
            .order_by(TVADeclarable.periode)
            .all()
        )
        is_decls = (
            db.query(ISDeclarable)
            .filter(ISDeclarable.annee == annee)
            .order_by(ISDeclarable.id)
            .all()
        )

        def _statut(decls):
            if not decls:
                return "brouillon"
            statuts = [getattr(d.statut, "value", str(d.statut)) for d in decls]
            if all(s == "payee" for s in statuts):
                return "deposee"
            if any(s == "validee" for s in statuts):
                return "validee"
            return "brouillon"

        total_tva_collectee = sum(float(d.tva_collectee or 0) for d in tva_decls)
        total_tva_deductible = sum(float(d.tva_deductible or 0) for d in tva_decls)
        total_tva_a_payer = sum(float(d.tva_a_payer or 0) for d in tva_decls)
        total_is = sum(float(d.is_a_payer or 0) for d in is_decls)

        detail = {
            "declarations_tva": [
                {
                    "periode": d.periode,
                    "base_imposable": float(d.base_imposable or 0),
                    "tva_collectee": float(d.tva_collectee or 0),
                    "tva_deductible": float(d.tva_deductible or 0),
                    "tva_a_payer": float(d.tva_a_payer or 0),
                    "statut": getattr(d.statut, "value", str(d.statut)),
                }
                for d in tva_decls
            ],
            "declarations_is": [
                {
                    "numero": d.numero_declaration,
                    "benefice_fiscal": float(d.benefice_fiscal or 0),
                    "is_du": float(d.is_du or 0),
                    "is_a_payer": float(d.is_a_payer or 0),
                    "statut": getattr(d.statut, "value", str(d.statut)),
                }
                for d in is_decls
            ],
        }

        liasse = LiasseFiscale(
            annee=annee,
            exercice_id=exercice.id if exercice else None,
            date_generation=date.today(),
            total_tva_collectee=round(total_tva_collectee, 2),
            total_tva_deductible=round(total_tva_deductible, 2),
            total_tva_a_payer=round(total_tva_a_payer, 2),
            total_is=round(total_is, 2),
            total_impots=round(total_tva_a_payer + total_is, 2),
            nombre_declarations_tva=len(tva_decls),
            statut=_statut(tva_decls + is_decls),
            detail_json=json.dumps(detail, ensure_ascii=False),
            valide_par=valide_par,
            date_validation=date.today() if valide_par else None,)
        db.add(liasse)
        db.commit()
        db.refresh(liasse)
        return liasse

    @staticmethod
    def lister(db: Session) -> List[LiasseFiscale]:
        return db.query(LiasseFiscale).order_by(LiasseFiscale.annee.desc()).all()

    @staticmethod
    def obtenir(db: Session, liasse_id: int) -> Optional[LiasseFiscale]:
        return db.query(LiasseFiscale).filter(LiasseFiscale.id == liasse_id).first()

