"""Acquisition service - Procurement and supplier management for Cameroon/CEMAC"""
from datetime import datetime, date, timedelta
from typing import List, Optional, Dict, Any
from sqlalchemy.orm import Session
from sqlalchemy import and_, func
from app.models.acquisition import (
    AppelOffres, CahierCharges, LigneCDC, Offre, LigneOffre, EvaluationOffre,
    Comparatif, LigneComparatif, ContratCadre, BonCommande, LigneBC,
    Reception, LigneReception, LitigeFournisseur, HistoriqueLitige, EvaluationFournisseur,
    TypeAppelOffres, StatutAppelOffres, CritereEvaluation
)


class AppelOffresService:
    """Tender/Call for bids service"""
    
    @staticmethod
    def creer_appel_offres(
        db: Session,
        numero_appel: str,
        titre: str,
        type_appel: TypeAppelOffres,
        budget_estime: float,
        date_limite: date,
        responsable: str,
        departement: str,
        description: str
    ) -> AppelOffres:
        """Create tender"""
        appel = AppelOffres(
            numero_appel=numero_appel,
            titre=titre,
            type_appel=type_appel,
            statut=StatutAppelOffres.BROUILLON,
            budget_estime=budget_estime,
            devise="XAF",
            date_limite=date_limite,
            responsable=responsable,
            departement=departement,
            description=description
        )
        db.add(appel)
        db.commit()
        db.refresh(appel)
        return appel
    
    @staticmethod
    def publier_appel(db: Session, appel_id: int) -> AppelOffres:
        """Publish tender"""
        appel = db.query(AppelOffres).filter(AppelOffres.id == appel_id).first()
        if not appel:
            raise ValueError("Appel d'offres non trouvé")
        
        appel.statut = StatutAppelOffres.PUBLIE
        appel.date_publication = date.today()
        db.commit()
        db.refresh(appel)
        return appel


class CahierChargesService:
    """Cahier des charges service"""
    
    @staticmethod
    def creer_cahier_charges(
        db: Session,
        numero_cdc: str,
        appel_offres_id: int,
        objet: str,
        description_technique: str,
        specifications: str,
        delai_livraison: int,
        penalites_retard: float
    ) -> CahierCharges:
        """Create cahier des charges"""
        cdc = CahierCharges(
            numero_cdc=numero_cdc,
            appel_offres_id=appel_offres_id,
            version=1,
            date_version=date.today(),
            objet=objet,
            description_technique=description_technique,
            specifications=specifications,
            delai_livraison=delai_livraison,
            penalites_retard=penalites_retard,
            devise="XAF",
            statut="brouillon"
        )
        db.add(cdc)
        db.commit()
        db.refresh(cdc)
        return cdc
    
    @staticmethod
    def ajouter_ligne_cdc(
        db: Session,
        cdc_id: int,
        article_id: int,
        designation: str,
        quantite: float,
        unite: str,
        specifications_detaillees: str,
        budget_unitaire: float,
        priorite: str
    ) -> LigneCDC:
        """Add line to cahier des charges"""
        budget_total = quantite * budget_unitaire
        
        ligne = LigneCDC(
            cdc_id=cdc_id,
            article_id=article_id,
            designation=designation,
            quantite=quantite,
            unite=unite,
            specifications_detaillees=specifications_detaillees,
            budget_unitaire=budget_unitaire,
            budget_total=budget_total,
            devise="XAF",
            priorite=priorite,
            statut="actif"
        )
        db.add(ligne)
        db.commit()
        db.refresh(ligne)
        return ligne


class OffreService:
    """Bid/proposal service"""
    
    @staticmethod
    def enregistrer_offre(
        db: Session,
        numero_offre: str,
        appel_offres_id: int,
        fournisseur_id: int,
        montant_total: float,
        delai_livraison: int,
        validite_offre: int
    ) -> Offre:
        """Register supplier bid"""
        offre = Offre(
            numero_offre=numero_offre,
            appel_offres_id=appel_offres_id,
            fournisseur_id=fournisseur_id,
            date_reception=date.today(),
            date_validite=date.today() + timedelta(days=validite_offre),
            montant_total=montant_total,
            devise="XAF",
            delai_livraison=delai_livraison,
            validite_offre=validite_offre,
            statut="recu"
        )
        db.add(offre)
        db.commit()
        db.refresh(offre)
        return offre
    
    @staticmethod
    def evaluer_offre(
        db: Session,
        offre_id: int,
        critere: CritereEvaluation,
        note: float,
        poids: float,
        evaluateur: str
    ) -> EvaluationOffre:
        """Evaluate bid on criterion"""
        note_ponderee = note * (poids / 100)
        
        evaluation = EvaluationOffre(
            offre_id=offre_id,
            critere=critere,
            note=note,
            poids=poids,
            note_ponderee=note_ponderee,
            evaluateur=evaluateur,
            date_evaluation=date.today()
        )
        db.add(evaluation)
        db.commit()
        db.refresh(evaluation)
        return evaluation


class ComparatifService:
    """Comparison matrix service"""
    
    @staticmethod
    def creer_comparatif(
        db: Session,
        numero_comparatif: str,
        appel_offres_id: int,
        cree_par: str
    ) -> Comparatif:
        """Create comparison matrix"""
        comparatif = Comparatif(
            numero_comparatif=numero_comparatif,
            appel_offres_id=appel_offres_id,
            date_creation=date.today(),
            cree_par=cree_par,
            statut="brouillon"
        )
        db.add(comparatif)
        db.commit()
        db.refresh(comparatif)
        return comparatif
    
    @staticmethod
    def ajouter_ligne_comparatif(
        db: Session,
        comparatif_id: int,
        fournisseur_id: int,
        offre_id: int,
        ligne_cdc_id: int,
        prix: float,
        delai: int,
        note_qualite: float,
        note_technique: float,
        note_financiere: float
    ) -> LigneComparatif:
        """Add line to comparison"""
        note_globale = (note_qualite + note_technique + note_financiere) / 3
        
        ligne = LigneComparatif(
            comparatif_id=comparatif_id,
            fournisseur_id=fournisseur_id,
            offre_id=offre_id,
            ligne_cdc_id=ligne_cdc_id,
            prix=prix,
            devise="XAF",
            delai=delai,
            note_qualite=note_qualite,
            note_technique=note_technique,
            note_financiere=note_financiere,
            note_globale=note_globale
        )
        db.add(ligne)
        db.commit()
        db.refresh(ligne)
        return ligne


class ContratCadreService:
    """Framework contract service"""
    
    @staticmethod
    def creer_contrat_cadre(
        db: Session,
        numero_contrat: str,
        fournisseur_id: int,
        type_contrat: str,
        date_signature: date,
        date_debut: date,
        date_fin: date,
        montant_annuel: float
    ) -> ContratCadre:
        """Create framework contract"""
        duree_mois = ((date_fin.year - date_debut.year) * 12) + (date_fin.month - date_debut.month)
        
        contrat = ContratCadre(
            numero_contrat=numero_contrat,
            fournisseur_id=fournisseur_id,
            type_contrat=type_contrat,
            date_signature=date_signature,
            date_debut=date_debut,
            date_fin=date_fin,
            duree_mois=duree_mois,
            montant_annuel=montant_annuel,
            devise="XAF",
            statut="actif"
        )
        db.add(contrat)
        db.commit()
        db.refresh(contrat)
        return contrat


class BonCommandeService:
    """Purchase order service"""
    
    @staticmethod
    def creer_bon_commande(
        db: Session,
        numero_bc: str,
        fournisseur_id: int,
        date_prevue_livraison: date,
        destinataire: str,
        lieu_livraison: str,
        conditions_paiement: str
    ) -> BonCommande:
        """Create purchase order"""
        bc = BonCommande(
            numero_bc=numero_bc,
            fournisseur_id=fournisseur_id,
            date_creation=date.today(),
            date_prevue_livraison=date_prevue_livraison,
            destinataire=destinataire,
            lieu_livraison=lieu_livraison,
            devise="XAF",
            conditions_paiement=conditions_paiement,
            statut="brouillon"
        )
        db.add(bc)
        db.commit()
        db.refresh(bc)
        return bc
    
    @staticmethod
    def valider_bc(db: Session, bc_id: int, valide_par: str) -> BonCommande:
        """Validate purchase order"""
        bc = db.query(BonCommande).filter(BonCommande.id == bc_id).first()
        if not bc:
            raise ValueError("Bon de commande non trouvé")
        
        bc.statut = "valide"
        bc.valide_par = valide_par
        bc.date_validation = date.today()
        db.commit()
        db.refresh(bc)
        return bc


class ReceptionService:
    """Goods receipt service"""
    
    @staticmethod
    def creer_reception(
        db: Session,
        numero_reception: str,
        bc_id: int,
        fournisseur_id: int,
        type_reception: str,
        lieu_reception: str,
        responsable: str
    ) -> Reception:
        """Create goods receipt"""
        reception = Reception(
            numero_reception=numero_reception,
            bc_id=bc_id,
            fournisseur_id=fournisseur_id,
            date_reception=date.today(),
            type_reception=type_reception,
            lieu_reception=lieu_reception,
            responsable=responsable,
            statut="en_cours"
        )
        db.add(reception)
        db.commit()
        db.refresh(reception)
        return reception
    
    @staticmethod
    def valider_reception(
        db: Session,
        reception_id: int,
        controle_par: str,
        condition_marchandise: str
    ) -> Reception:
        """Validate goods receipt"""
        reception = db.query(Reception).filter(Reception.id == reception_id).first()
        if not reception:
            raise ValueError("Réception non trouvée")
        
        reception.statut = "valide"
        reception.condition_marchandise=condition_marchandise
        reception.controle_qualite = True
        reception.date_controle = date.today()
        reception.controle_par=controle_par
        db.commit()
        db.refresh(reception)
        return reception


class LitigeFournisseurService:
    """Supplier dispute service"""
    
    @staticmethod
    def creer_litige(
        db: Session,
        numero_litige: str,
        fournisseur_id: int,
        type_litige: str,
        description: str,
        gravite: str,
        montant_en_litige: float
    ) -> LitigeFournisseur:
        """Create supplier dispute"""
        litige = LitigeFournisseur(
            numero_litige=numero_litige,
            fournisseur_id=fournisseur_id,
            type_litige=type_litige,
            date_ouverture=date.today(),
            description=description,
            gravite=gravite,
            montant_en_litige=montant_en_litige,
            devise="XAF",
            statut="ouvert"
        )
        db.add(litige)
        db.commit()
        db.refresh(litige)
        return litige
    
    @staticmethod
    def ajouter_historique(
        db: Session,
        litige_id: int,
        action: str,
        description: str,
        auteur: str,
        resultat: str
    ) -> HistoriqueLitige:
        """Add dispute history entry"""
        historique = HistoriqueLitige(
            litige_id=litige_id,
            date_action=datetime.utcnow(),
            action=action,
            description=description,
            auteur=auteur,
            resultat=resultat
        )
        db.add(historique)
        db.commit()
        db.refresh(historique)
        return historique


class EvaluationFournisseurService:
    """Supplier evaluation service"""
    
    @staticmethod
    def creer_evaluation(
        db: Session,
        fournisseur_id: int,
        periode: str,
        note_qualite: float,
        note_delai: float,
        note_prix: float,
        note_service: float,
        evaluateur: str
    ) -> EvaluationFournisseur:
        """Create supplier evaluation"""
        note_globale = (note_qualite + note_delai + note_prix + note_service) / 4
        
        # Determine ranking
        if note_globale >= 16:
            classement = "A"
        elif note_globale >= 12:
            classement = "B"
        elif note_globale >= 8:
            classement = "C"
        else:
            classement = "D"
        
        evaluation = EvaluationFournisseur(
            fournisseur_id=fournisseur_id,
            periode=periode,
            date_evaluation=date.today(),
            evaluateur=evaluateur,
            note_qualite=note_qualite,
            note_delai=note_delai,
            note_prix=note_prix,
            note_service=note_service,
            note_globale=note_globale,
            classement=classement
        )
        db.add(evaluation)
        db.commit()
        db.refresh(evaluation)
        return evaluation


class AcquisitionReportingService:
    """Acquisition reporting service"""
    
    @staticmethod
    def rapport_fournisseur(db: Session, fournisseur_id: int) -> Dict[str, Any]:
        """Generate supplier report"""
        evaluations = db.query(EvaluationFournisseur).filter(
            EvaluationFournisseur.fournisseur_id == fournisseur_id
        ).all()
        
        litiges = db.query(LitigeFournisseur).filter(
            LitigeFournisseur.fournisseur_id == fournisseur_id
        ).all()
        
        contrats = db.query(ContratCadre).filter(
            ContratCadre.fournisseur_id == fournisseur_id
        ).all()
        
        moyenne_notes = [e.note_globale for e in evaluations] if evaluations else 0
        note_moyenne = sum(moyenne_notes) / len(moyenne_notes) if moyenne_notes else 0
        
        return {
            "fournisseur_id": fournisseur_id,
            "evaluations": {
                "total": len(evaluations),
                "note_moyenne": note_moyenne,
                "derniere_classement": evaluations[-1].classement if evaluations else None
            },
            "contrats": {
                "total": len(contrats),
                "actifs": sum(1 for c in contrats if c.statut == "actif")
            },
            "litiges": {
                "total": len(litiges),
                "ouverts": sum(1 for l in litiges if l.statut == "ouvert")
            }
        }
