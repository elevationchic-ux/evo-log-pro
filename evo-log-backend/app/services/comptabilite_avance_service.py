"""Comptabilité avancée service - Journaux auxiliaires, lettrage, grand livre, balance"""
from datetime import datetime, date
from decimal import Decimal
from typing import List, Optional, Dict, Any
from sqlalchemy.orm import Session
from sqlalchemy import and_, func, case
from app.models.finance_ohada import (
    PlanComptableOHADA, EcritureComptableNew, ExerciceComptable, 
    JournalAuxiliaire, LigneJournal, Lettrage, EcritureLettree,
    GrandLivreLigne, BalanceVerification, LigneBalance,
    BilanOHADADetaille, CompteResultatOHADADetaille, TAFIRE, AnnexesOHADA,
    TypeJournal, TypeLettrage, StatutLettrage
)


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
    def lettrage_automatique(
        db: Session,
        compte_id: int,
        date_reference: date
    ) -> Lettrage:
        """Lettrage automatique des écritures d'un compte"""
        # Récupérer les écritures non lettrées du compte
        ecritures = db.query(EcritureComptableNew).filter(
            and_(
                EcritureComptableNew.compte_id == compte_id,
                EcritureComptableNew.valider == True
            )
        ).all()
        
        if not ecritures:
            raise ValueError("Aucune écriture à lettrer pour ce compte")
        
        # Grouper par montants pour correspondance
        from collections import defaultdict
        groupes = defaultdict(list)
        for ecriture in ecritures:
            groupes[ecriture.debit].append(ecriture)
            groupes[ecriture.credit].append(ecriture)
        
        # Créer le lettrage
        numero_lettrage = f"LET-{date_reference.strftime('%Y%m%d')}-{compte_id}"
        lettrage = Lettrage(
            compte_id=compte_id,
            numero_lettrage=numero_lettrage,
            type_lettrage=TypeLettrage.AUTOMATIQUE,
            date_lettrage=date_reference,
            montant_lettre=sum(e.debit for e in ecritures if e.debit > 0) or sum(e.credit for e in ecritures if e.credit > 0),
            effectue_par="SYSTEME"
        )
        db.add(lettrage)
        db.commit()
        db.refresh(lettrage)
        
        # Lier les écritures au lettrage
        for ecriture in ecritures:
            ecriture_lettree = EcritureLettree(
                lettrage_id=lettrage.id,
                ecriture_id=ecriture.id,
                montant_lettre=ecriture.debit if ecriture.debit > 0 else ecriture.credit
            )
            db.add(ecriture_lettree)
        
        db.commit()
        return lettrage
    
    @staticmethod
    def lettrage_manuel(
        db: Session,
        compte_id: int,
        ecritures_ids: List[int],
        date_lettrage: date,
        effectue_par: str,
        reference: Optional[str] = None
    ) -> Lettrage:
        """Lettrage manuel d'écritures sélectionnées"""
        # Vérifier que les écritures existent et appartiennent au compte
        ecritures = db.query(EcritureComptableNew).filter(
            and_(
                EcritureComptableNew.id.in_(ecritures_ids),
                EcritureComptableNew.compte_id == compte_id,
                EcritureComptableNew.valider == True
            )
        ).all()
        
        if len(ecritures) != len(ecritures_ids):
            raise ValueError("Certaines écritures n'existent pas ou n'appartiennent pas à ce compte")
        
        # Calculer le montant total
        montant_total = sum(e.debit for e in ecritures if e.debit > 0) or sum(e.credit for e in ecritures if e.credit > 0)
        
        # Créer le lettrage
        numero_lettrage = f"LET-{date_lettrage.strftime('%Y%m%d')}-{compte_id}"
        lettrage = Lettrage(
            compte_id=compte_id,
            numero_lettrage=numero_lettrage,
            type_lettrage=TypeLettrage.MANUEL,
            date_lettrage=date_lettrage,
            montant_lettre=montant_total,
            reference_lettrage=reference,
            effectue_par=effectue_par
        )
        db.add(lettrage)
        db.commit()
        db.refresh(lettrage)
        
        # Lier les écritures au lettrage
        for ecriture in ecritures:
            ecriture_lettree = EcritureLettree(
                lettrage_id=lettrage.id,
                ecriture_id=ecriture.id,
                montant_lettre=ecriture.debit if ecriture.debit > 0 else ecriture.credit
            )
            db.add(ecriture_lettree)
        
        db.commit()
        return lettrage
    
    @staticmethod
    def annuler_lettrage(db: Session, lettrage_id: int, motif: str) -> Lettrage:
        """Annuler un lettrage"""
        lettrage = db.query(Lettrage).filter(Lettrage.id == lettrage_id).first()
        if not lettrage:
            raise ValueError("Lettrage non trouvé")
        
        # Supprimer les liens
        db.query(EcritureLettree).filter(EcritureLettree.lettrage_id == lettrage_id).delete()
        
        # Marquer comme annulé
        lettrage.date_annulation = date.today()
        lettrage.motif_annulation = motif
        
        db.commit()
        db.refresh(lettrage)
        return lettrage
    
    @staticmethod
    def suggestion_lettrage(db: Session, compte_id: int) -> List[Dict[str, Any]]:
        """Suggérer des écritures à lettrer"""
        ecritures = db.query(EcritureComptableNew).filter(
            and_(
                EcritureComptableNew.compte_id == compte_id,
                EcritureComptableNew.valider == True
            )
        ).all()
        
        suggestions = []
        for ecriture in ecritures:
            suggestions.append({
                "ecriture_id": ecriture.id,
                "date": ecriture.date_ecriture,
                "libelle": ecriture.libelle,
                "debit": ecriture.debit,
                "credit": ecriture.credit
            })
        
        return suggestions


class GrandLivreService:
    """Service du grand livre général et auxiliaires"""

    @staticmethod
    def mouvements_par_compte(
        db: Session,
        date_debut: Optional[date] = None,
        date_fin: Optional[date] = None,
        journal: Optional[str] = None,
    ) -> Dict[int, Dict[str, Decimal]]:
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
                    GrandLivreLigne.date_ecriture <= date_fin,
                )
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
        date_fin: Optional[date] = None,
    ) -> Dict[str, Any]:
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
                func.coalesce(func.sum(GrandLivreLigne.credit), 0),
            ).filter(
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
            func.coalesce(func.sum(GrandLivreLigne.credit), 0),
        ).filter(
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
            statut="equilibre" if abs(ecart) < Decimal("0.01") else "desequilibre",
        )
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
                solde_credit=-net if net < 0 else Decimal("0"),
            ))
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
                GrandLivreLigne.periode == periode,
            )
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

        # Produits/Charges financiers et exceptionnel : non detailles ici,
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
        """Générer le TAFIRE (Tableau Financier des Ressources et Emplois)"""
        # Capacité d'autofinancement = Résultat net + Dotations aux amortissements
        resultat_net = db.query(CompteResultatOHADADetaille).filter(
            CompteResultatOHADADetaille.exercice_id == exercice_id
        ).first()
        
        caf = resultat_net.resultat_net if resultat_net else 0
        
        tafire = TAFIRE(
            exercice_id=exercice_id,
            date_tafire=date_tafire,
            capacit_autofinancement=caf,
            total_ressources=caf,
            investissements_immobilisations=0,
            total_emplois=0,
            variation_tresorerie=caf,
            tresorerie_debut=0,
            tresorerie_fin=caf
        )
        db.add(tafire)
        db.commit()
        db.refresh(tafire)
        return tafire
    
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
        annee: Optional[int] = None,
    ) -> Dict[str, Any]:
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

        # Pieces validees par periode (agregation SQL, une seule requete).
        compteurs = dict(
            db.query(
                EcritureComptableNew.periode,
                func.count(EcritureComptableNew.id),
            ).filter(
                and_(
                    EcritureComptableNew.exercice_id == exercice_id,
                    EcritureComptableNew.valider == True,  # noqa: E712
                )
            ).group_by(EcritureComptableNew.periode).all()
        )

        # Derniere balance de verification par periode (une seule requete).
        balances = {}
        for b in (
            db.query(BalanceVerification)
            .filter(BalanceVerification.exercice_id == exercice_id)
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
            "exercice_id": exercice_id,
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
                BalanceVerification.statut == "equilibre",
            )
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
