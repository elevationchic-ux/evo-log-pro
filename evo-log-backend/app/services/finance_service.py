"""Finance service - OHADA accounting and financial management for Cameroon/CEMAC"""
from datetime import datetime, date, timedelta
from typing import List, Optional, Dict, Any
from sqlalchemy.orm import Session
from sqlalchemy import and_, func
from app.models.finance_ohada import (
    PlanComptableOHADA, EcritureComptableNew as EcritureComptable, ExerciceComptable, FactureNew as Facture, LigneFactureOHADA as LigneFacture,
    Reglement, TVADeclarable, RetenueSource, ISDeclarable, CentimesAdditionnels,
    Patente, Bilan, CompteResultat, SignatureElectronique,
    TypeCompte, RegimeTVA, RegimeIS, StatutTaxe
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
    """Accounting entry service"""
    
    @staticmethod
    def creer_ecriture(
        db: Session,
        numero_ecriture: str,
        date_ecriture: date,
        libelle: str,
        compte_id: int,
        debit: float,
        credit: float,
        journal: str,
        periode: str
    ) -> EcritureComptable:
        """Create accounting entry"""
        ecriture = EcritureComptable(
            numero_ecriture=numero_ecriture,
            date_ecriture=date_ecriture,
            libelle=libelle,
            compte_id=compte_id,
            debit=debit,
            credit=credit,
            devise="XAF",
            journal=journal,
            periode=periode
        )
        db.add(ecriture)
        db.commit()
        db.refresh(ecriture)
        return ecriture
    
    @staticmethod
    def valider_ecriture(db: Session, ecriture_id: int, valide_par: str) -> EcritureComptable:
        """Validate accounting entry"""
        ecriture = db.query(EcritureComptable).filter(EcritureComptable.id == ecriture_id).first()
        if not ecriture:
            raise ValueError("Écriture comptable non trouvée")
        
        ecriture.valider = True
        ecriture.valide_par = valide_par
        ecriture.date_validation = date.today()
        db.commit()
        db.refresh(ecriture)
        return ecriture


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
        numero_facture: str,
        client_id: int,
        type_facture: str,
        date_emission: date,
        montant_ht: float,
        taux_tva: float
    ) -> Facture:
        """Create invoice"""
        montant_tva = montant_ht * (taux_tva / 100)
        montant_ttc = montant_ht + montant_tva
        
        facture = Facture(
            numero_facture=numero_facture,
            client_id=client_id,
            type_facture=type_facture,
            date_emission=date_emission,
            montant_ht=montant_ht,
            taux_tva=taux_tva,
            montant_tva=montant_tva,
            montant_ttc=montant_ttc,
            devise="XAF",
            solde_restant=montant_ttc
        )
        db.add(facture)
        db.commit()
        db.refresh(facture)
        return facture
    
    @staticmethod
    def ajouter_ligne_facture(
        db: Session,
        facture_id: int,
        article_id: int,
        designation: str,
        quantite: float,
        prix_unitaire_ht: float,
        taux_tva: float
    ) -> LigneFacture:
        """Add line to invoice"""
        montant_ht = quantite * prix_unitaire_ht
        montant_tva = montant_ht * (taux_tva / 100)
        montant_ttc = montant_ht + montant_tva
        
        ligne = LigneFacture(
            facture_id=facture_id,
            article_id=article_id,
            designation=designation,
            quantite=quantite,
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
