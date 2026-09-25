"""Finance service - OHADA accounting and financial management for Cameroon/CEMAC"""
from datetime import datetime, date, timedelta
from typing import List, Optional, Dict, Any
from fastapi import HTTPException
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
