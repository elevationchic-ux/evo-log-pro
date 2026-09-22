"""Comptabilité avancée service - Journaux auxiliaires, lettrage, grand livre, balance"""
from datetime import datetime, date
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
    def generer_grand_livre_general(
        db: Session,
        exercice_id: int,
        date_debut: date,
        date_fin: date
    ) -> List[GrandLivreLigne]:
        """Générer le grand livre général pour une période"""
        # Récupérer toutes les écritures validées de la période
        ecritures = db.query(EcritureComptableNew).filter(
            and_(
                EcritureComptableNew.exercice_id == exercice_id,
                EcritureComptableNew.date_ecriture >= date_debut,
                EcritureComptableNew.date_ecriture <= date_fin,
                EcritureComptableNew.valider == True
            )
        ).all()
        
        lignes = []
        for ecriture in ecritures:
            ligne = GrandLivreLigne(
                compte_id=ecriture.compte_id,
                ecriture_id=ecriture.id,
                date_ecriture=ecriture.date_ecriture,
                libelle=ecriture.libelle,
                debit=ecriture.debit,
                credit=ecriture.credit,
                devise=ecriture.devise,
                journal=ecriture.journal,
                periode=ecriture.periode
            )
            lignes.append(ligne)
        
        db.add_all(lignes)
        db.commit()
        return lignes
    
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
    """Service de balance de vérification"""
    
    @staticmethod
    def creer_balance_verification(
        db: Session,
        exercice_id: int,
        periode: str,
        date_balance: date
    ) -> BalanceVerification:
        """Créer une balance de vérification"""
        # Récupérer toutes les écritures de la période
        ecritures = db.query(EcritureComptableNew).filter(
            and_(
                EcritureComptableNew.exercice_id == exercice_id,
                EcritureComptableNew.periode == periode,
                EcritureComptableNew.valider == True
            )
        ).all()
        
        # Calculer les totaux par compte
        from collections import defaultdict
        totaux = defaultdict(lambda: {"debit": 0, "credit": 0})
        for ecriture in ecritures:
            totaux[ecriture.compte_id]["debit"] += ecriture.debit
            totaux[ecriture.compte_id]["credit"] += ecriture.credit
        
        # Créer la balance
        total_debit = sum(t["debit"] for t in totaux.values())
        total_credit = sum(t["credit"] for t in totaux.values())
        ecart = total_debit - total_credit
        
        balance = BalanceVerification(
            exercice_id=exercice_id,
            periode=periode,
            date_balance=date_balance,
            total_debit=total_debit,
            total_credit=total_credit,
            ecart=ecart,
            statut="equilibre" if abs(ecart) < 0.01 else "desequilibre"
        )
        db.add(balance)
        db.commit()
        db.refresh(balance)
        
        # Créer les lignes de balance
        for compte_id, totaux_compte in totaux.items():
            compte = db.query(PlanComptableOHADA).filter(PlanComptableOHADA.id == compte_id).first()
            ligne = LigneBalance(
                balance_id=balance.id,
                compte_id=compte_id,
                compte_numero=compte.numero_compte if compte else "",
                compte_intitule=compte.intitule if compte else "",
                total_debit=totaux_compte["debit"],
                total_credit=totaux_compte["credit"],
                solde_debit=totaux_compte["debit"] - totaux_compte["credit"] if totaux_compte["debit"] > totaux_compte["credit"] else 0,
                solde_credit=totaux_compte["credit"] - totaux_compte["debit"] if totaux_compte["credit"] > totaux_compte["debit"] else 0
            )
            db.add(ligne)
        
        db.commit()
        return balance
    
    @staticmethod
    def balance_par_journal(
        db: Session,
        journal_code: str,
        periode: str
    ) -> Dict[str, Any]:
        """Balance par journal"""
        journal = db.query(JournalAuxiliaire).filter(
            JournalAuxiliaire.code_journal == journal_code
        ).first()
        
        if not journal:
            raise ValueError("Journal non trouvé")
        
        lignes = db.query(EcritureComptableNew).filter(
            and_(
                EcritureComptableNew.journal == journal_code,
                EcritureComptableNew.periode == periode,
                EcritureComptableNew.valider == True
            )
        ).all()
        
        total_debit = sum(l.debit for l in lignes)
        total_credit = sum(l.credit for l in lignes)
        
        return {
            "journal": journal_code,
            "periode": periode,
            "total_debit": total_debit,
            "total_credit": total_credit,
            "ecart": total_debit - total_credit,
            "nombre_ecritures": len(lignes)
        }


class EtatsFinanciersOHADAService:
    """Service des états financiers OHADA complets"""
    
    @staticmethod
    def generer_bilan_ohada_detaille(
        db: Session,
        exercice_id: int,
        date_bilan: date
    ) -> BilanOHADADetaille:
        """Générer le bilan OHADA détaillé"""
        # Récupérer les soldes des comptes de l'exercice
        # Actif immobilisé (classe 2)
        actif_immobilise = db.query(func.sum(PlanComptableOHADA.solde_debit)).filter(
            and_(
                PlanComptableOHADA.classe == 2,
                PlanComptableOHADA.type_compte.in_(["actif_fixe", "actif"])
            )
        ).scalar() or 0
        
        # Actif circulant (classe 3)
        actif_circulant_stocks = db.query(func.sum(PlanComptableOHADA.solde_debit)).filter(
            and_(
                PlanComptableOHADA.classe == 3,
                PlanComptableOHADA.type_compte == "actif_circulant"
            )
        ).scalar() or 0
        
        actif_circulant_creances = db.query(func.sum(PlanComptableOHADA.solde_debit)).filter(
            and_(
                PlanComptableOHADA.classe == 4,
                PlanComptableOHADA.type_compte == "actif_circulant"
            )
        ).scalar() or 0
        
        # Trésorerie (classe 5)
        tresorerie_actif = db.query(func.sum(PlanComptableOHADA.solde_debit)).filter(
            and_(
                PlanComptableOHADA.classe == 5,
                PlanComptableOHADA.type_compte == "actif_circulant"
            )
        ).scalar() or 0
        
        # Capitaux propres (classe 1)
        capitaux_propres = db.query(func.sum(PlanComptableOHADA.solde_credit)).filter(
            and_(
                PlanComptableOHADA.classe == 1,
                PlanComptableOHADA.type_compte.in_(["passif_fixe", "passif"])
            )
        ).scalar() or 0
        
        # Dettes
        dettes_long_terme = db.query(func.sum(PlanComptableOHADA.solde_credit)).filter(
            and_(
                PlanComptableOHADA.classe == 1,
                PlanComptableOHADA.type_compte == "passif_fixe"
            )
        ).scalar() or 0
        
        dettes_courtes = db.query(func.sum(PlanComptableOHADA.solde_credit)).filter(
            and_(
                PlanComptableOHADA.classe == 4,
                PlanComptableOHADA.type_compte == "passif_circulant"
            )
        ).scalar() or 0
        
        total_actif = actif_immobilise + actif_circulant_stocks + actif_circulant_creances + tresorerie_actif
        total_passif = capitaux_propres + dettes_long_terme + dettes_courtes
        
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
            capitaux_propres_total=capitaux_propres,
            dettes_long_terme=dettes_long_terme,
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
        """Générer le compte de résultat OHADA détaillé"""
        # Produits d'exploitation (classe 7)
        ventes_marchandises = db.query(func.sum(PlanComptableOHADA.solde_credit)).filter(
            and_(
                PlanComptableOHADA.classe == 7,
                PlanComptableOHADA.type_compte == "produit"
            )
        ).scalar() or 0
        
        # Charges d'exploitation (classe 6)
        achats_marchandises = db.query(func.sum(PlanComptableOHADA.solde_debit)).filter(
            and_(
                PlanComptableOHADA.classe == 6,
                PlanComptableOHADA.type_compte == "charge"
            )
        ).scalar() or 0
        
        total_produits_exploitation = ventes_marchandises
        total_charges_exploitation = achats_marchandises
        resultat_exploitation = total_produits_exploitation - total_charges_exploitation
        
        # Produits/Charges financiers
        produits_financiers = 0
        charges_financieres = 0
        resultat_financier = produits_financiers - charges_financieres
        
        # Résultat exceptionnel
        resultat_exceptionnel = 0
        
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
    
    @staticmethod
    def cloture_mensuelle(
        db: Session,
        exercice_id: int,
        periode: str,
        cloture_par: str
    ) -> Dict[str, Any]:
        """Clôture mensuelle des comptes de gestion"""
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
        
        # Marquer la période comme clôturée
        # (implémentation future avec modèle PeriodeComptable)
        
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
        """Report à nouveau des soldes de bilan"""
        # Récupérer les soldes des comptes de bilan de l'exercice source
        comptes_bilan = db.query(PlanComptableOHADA).filter(
            PlanComptableOHADA.classe.in_([1, 2, 3, 4, 5])
        ).all()
        
        # Reporter les soldes vers l'exercice cible
        # (implémentation future)
        
        return {
            "exercice_source_id": exercice_source_id,
            "exercice_cible_id": exercice_cible,
            "statut": "reporte",
            "nombre_comptes": len(comptes_bilan)
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
