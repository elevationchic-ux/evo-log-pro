"""Transit avancé service - Complete customs operations for Cameroon/CEMAC"""
from datetime import datetime, date, timedelta
from typing import List, Optional, Dict, Any
from sqlalchemy.orm import Session
from sqlalchemy import and_, func
from app.models.transit_avance import (
    BureauDouane, DossierTransitAvance, VisitePhysique, ValorisationDouaniere,
    NomenclatureCEMAC, DeclarationDouaniereAvance, LigneDeclaration, BonAD,
    AvisMiseConsommation, CreditEnlevement, DroitPort, TimbreUsage,
    LitigeDouanier, ArchivageDossier, ProcedureUrgente, TypeTransit, RegimeDouanier
)


class BureauDouaneService:
    """Customs office management service"""
    
    @staticmethod
    def creer_bureau_douane(
        db: Session,
        code: str,
        nom: str,
        type_bureau: str,
        port_id: int,
        region: str
    ) -> BureauDouane:
        """Create customs office"""
        bureau = BureauDouane(
            code=code,
            nom=nom,
            type_bureau=type_bureau,
            port_id=port_id,
            region=region,
            statut="actif"
        )
        db.add(bureau)
        db.commit()
        db.refresh(bureau)
        return bureau


class DossierTransitAvanceService:
    """Enhanced transit dossier service"""
    
    @staticmethod
    def creer_dossier_transit(
        db: Session,
        numero_dossier: str,
        client_id: int,
        transitaire_id: int,
        type_transit: TypeTransit,
        regime_douanier: RegimeDouanier,
        bureau_entree_id: int,
        bureau_sortie_id: int,
        marchandise: str,
        valeur_marchandise: float,
        pays_origine_code: str,
        pays_destination_code: str
    ) -> DossierTransitAvance:
        """Create enhanced transit dossier"""
        dossier = DossierTransitAvance(
            numero_dossier=numero_dossier,
            client_id=client_id,
            transitaire_id=transitaire_id,
            type_transit=type_transit,
            regime_douanier=regime_douanier,
            bureau_entree_id=bureau_entree_id,
            bureau_sortie_id=bureau_sortie_id,
            marchandise=marchandise,
            valeur_marchandise=valeur_marchandise,
            devise="XAF",
            pays_origine_code=pays_origine_code,
            pays_destination_code=pays_destination_code,
            statut="ouvert"
        )
        db.add(dossier)
        db.commit()
        db.refresh(dossier)
        return dossier
    
    @staticmethod
    def cloturer_dossier(db: Session, dossier_id: int) -> DossierTransitAvance:
        """Close transit dossier"""
        dossier = db.query(DossierTransitAvance).filter(
            DossierTransitAvance.id == dossier_id
        ).first()
        if not dossier:
            raise ValueError("Dossier non trouvé")
        
        dossier.statut = "cloture"
        dossier.date_cloture = datetime.utcnow()
        db.commit()
        db.refresh(dossier)
        return dossier


class VisitePhysiqueService:
    """Physical inspection service"""
    
    @staticmethod
    def enregistrer_visite(
        db: Session,
        dossier_transit_id: int,
        inspecteur_id: int,
        type_visite: str,
        rapport: str,
        prelevement: bool = False,
        echantillon: Optional[str] = None
    ) -> VisitePhysique:
        """Record physical inspection"""
        visite = VisitePhysique(
            dossier_transit_id=dossier_transit_id,
            date_visite=datetime.utcnow(),
            inspecteur_id=inspecteur_id,
            type_visite=type_visite,
            rapport=rapport,
            prelevement=prelevement,
            echantillon=echantillon,
            resultat="analyse_en_cours" if prelevement else "conforme"
        )
        db.add(visite)
        db.commit()
        db.refresh(visite)
        return visite
    
    @staticmethod
    def valider_visite(
        db: Session,
        visite_id: int,
        conforme: bool,
        observations: str = ""
    ) -> VisitePhysique:
        """Validate inspection result"""
        visite = db.query(VisitePhysique).filter(VisitePhysique.id == visite_id).first()
        if not visite:
            raise ValueError("Visite non trouvée")
        
        visite.conformite = conforme
        visite.resultat = "conforme" if conforme else "non_conforme"
        visite.observations = observations
        db.commit()
        db.refresh(visite)
        return visite


class ValorisationDouaniereService:
    """Customs valuation service"""
    
    @staticmethod
    def creer_valorisation(
        db: Session,
        dossier_transit_id: int,
        methode_valorisation: str,
        valeur_caf: float,
        fret: float,
        assurance: float,
        autres_frais: float,
        taux_change: float,
        valide_par: int
    ) -> ValorisationDouaniere:
        """Create customs valuation"""
        valeur_fob = valeur_caf - fret - assurance - autres_frais
        
        valorisation = ValorisationDouaniere(
            dossier_transit_id=dossier_transit_id,
            methode_valorisation=methode_valorisation,
            valeur_caf=valeur_caf,
            fret=fret,
            assurance=assurance,
            autres_frais=autres_frais,
            valeur_fob=valeur_fob,
            taux_change=taux_change,
            devise="XAF",
            date_valorisation=date.today(),
            valide_par=valide_par
        )
        db.add(valorisation)
        db.commit()
        db.refresh(valorisation)
        return valorisation


class NomenclatureCEMACService:
    """CEMAC TARIC nomenclature service"""
    
    @staticmethod
    def obtenir_taux_taric(db: Session, code_hs: str) -> Optional[NomenclatureCEMAC]:
        """Get tariff rates for HS code"""
        return db.query(NomenclatureCEMAC).filter(
            NomenclatureCEMAC.code_hs == code_hs,
            NomenclatureCEMAC.statut == "actif"
        ).first()
    
    @staticmethod
    def calculer_droits(
        db: Session,
        code_hs: str,
        valeur_declaree: float
    ) -> Dict[str, float]:
        """Calculate customs duties based on HS code"""
        taric = NomenclatureCEMACService.obtenir_taux_taric(db, code_hs)
        if not taric:
            raise ValueError(f"Code HS {code_hs} non trouvé")
        
        montant_dd = valeur_declaree * (taric.taux_dd / 100)
        montant_tva = valeur_declaree * (taric.taux_tva / 100)
        
        return {
            "taux_dd": taric.taux_dd,
            "montant_dd": montant_dd,
            "taux_tva": taric.taux_tva,
            "montant_tva": montant_tva,
            "total_taxes": montant_dd + montant_tva
        }


class DeclarationDouaniereAvanceService:
    """Enhanced customs declaration service"""
    
    @staticmethod
    def creer_declaration(
        db: Session,
        numero_declaration: str,
        dossier_transit_id: int,
        regime_douanier: RegimeDouanier,
        bureau_douane_id: int,
        valeur_declaree: float,
        code_hs: str
    ) -> DeclarationDouaniereAvance:
        """Create customs declaration"""
        # Calculate duties based on TARIC
        taric = NomenclatureCEMACService.obtenir_taux_taric(db, code_hs)
        if not taric:
            raise ValueError(f"Code HS {code_hs} non trouvé")
        
        taux_dd = taric.taux_dd
        montant_dd = valeur_declaree * (taux_dd / 100)
        taux_tva = taric.taux_tva
        montant_tva = valeur_declaree * (taux_tva / 100)
        total_taxes = montant_dd + montant_tva
        
        declaration = DeclarationDouaniereAvance(
            numero_declaration=numero_declaration,
            dossier_transit_id=dossier_transit_id,
            regime_douanier=regime_douanier,
            bureau_douane_id=bureau_douane_id,
            date_enregistrement=datetime.utcnow(),
            valeur_declaree=valeur_declaree,
            devise="XAF",
            code_hs=code_hs,
            taux_dd=taux_dd,
            montant_dd=montant_dd,
            taux_tva=taux_tva,
            montant_tva=montant_tva,
            total_taxes=total_taxes,
            statut="brouillon"
        )
        db.add(declaration)
        db.commit()
        db.refresh(declaration)
        return declaration
    
    @staticmethod
    def valider_declaration(
        db: Session,
        declaration_id: int,
        reference_sygdonia: str
    ) -> DeclarationDouaniereAvance:
        """Validate customs declaration (SYDONIA+ integration)"""
        declaration = db.query(DeclarationDouaniereAvance).filter(
            DeclarationDouaniereAvance.id == declaration_id
        ).first()
        if not declaration:
            raise ValueError("Déclaration non trouvée")
        
        declaration.statut = "valide"
        declaration.date_validation = datetime.utcnow()
        declaration.reference_sygdonia = reference_sygdonia
        db.commit()
        db.refresh(declaration)
        return declaration
    
    @staticmethod
    def acquitter_declaration(
        db: Session,
        declaration_id: int,
        numero_quitus: str
    ) -> DeclarationDouaniereAvance:
        """Acquit customs declaration after payment"""
        declaration = db.query(DeclarationDouaniereAvance).filter(
            DeclarationDouaniereAvance.id == declaration_id
        ).first()
        if not declaration:
            raise ValueError("Déclaration non trouvée")
        
        declaration.statut = "acquitte"
        declaration.date_acquittement = datetime.utcnow()
        declaration.numero_quitus = numero_quitus
        db.commit()
        db.refresh(declaration)
        return declaration


class LigneDeclarationService:
    """Declaration line item service"""
    
    @staticmethod
    def ajouter_ligne(
        db: Session,
        declaration_id: int,
        numero_ligne: int,
        designation: str,
        quantite: float,
        unite: str,
        poids_net: float,
        poids_brut: float,
        valeur_unitaire: float,
        code_hs: str
    ) -> LigneDeclaration:
        """Add line to declaration"""
        valeur_totale = quantite * valeur_unitaire
        
        # Calculate duties for this line
        taric = NomenclatureCEMACService.obtenir_taux_taric(db, code_hs)
        if not taric:
            raise ValueError(f"Code HS {code_hs} non trouvé")
        
        taux_dd = taric.taux_dd
        montant_dd = valeur_totale * (taux_dd / 100)
        taux_tva = taric.taux_tva
        montant_tva = valeur_totale * (taux_tva / 100)
        
        ligne = LigneDeclaration(
            declaration_id=declaration_id,
            numero_ligne=numero_ligne,
            designation=designation,
            quantite=quantite,
            unite=unite,
            poids_net=poids_net,
            poids_brut=poids_brut,
            valeur_unitaire=valeur_unitaire,
            valeur_totale=valeur_totale,
            code_hs=code_hs,
            taux_dd=taux_dd,
            montant_dd=montant_dd,
            taux_tva=taux_tva,
            montant_tva=montant_tva
        )
        db.add(ligne)
        db.commit()
        db.refresh(ligne)
        return ligne


class BonADService:
    """Bon à dédouaner service"""
    
    @staticmethod
    def emettre_bad(
        db: Session,
        numero_bad: str,
        dossier_transit_id: int,
        declaration_id: int,
        signataire: str,
        qualite: str
    ) -> BonAD:
        """Issue bon à dédouaner"""
        bad = BonAD(
            numero_bad=numero_bad,
            dossier_transit_id=dossier_transit_id,
            declaration_id=declaration_id,
            signataire=signataire,
            qualite=qualite,
            date_signature=date.today(),
            statut="emis"
        )
        db.add(bad)
        db.commit()
        db.refresh(bad)
        return bad


class AvisMiseConsommationService:
    """AMC - Release for consumption service"""
    
    @staticmethod
    def emettre_amc(
        db: Session,
        numero_amc: str,
        dossier_transit_id: int,
        declaration_id: int,
        bureau_douane_id: int,
        valide_par: str,
        fonction: str
    ) -> AvisMiseConsommation:
        """Issue AMC"""
        # Get declaration amounts
        declaration = db.query(DeclarationDouaniereAvance).filter(
            DeclarationDouaniereAvance.id == declaration_id
        ).first()
        if not declaration:
            raise ValueError("Déclaration non trouvée")
        
        amc = AvisMiseConsommation(
            numero_amc=numero_amc,
            dossier_transit_id=dossier_transit_id,
            declaration_id=declaration_id,
            bureau_douane_id=bureau_douane_id,
            date_emission=date.today(),
            valide_par=valide_par,
            fonction=fonction,
            date_validite=date.today() + timedelta(days=30),
            date_limite=date.today() + timedelta(days=90),
            montant_dd=declaration.montant_dd,
            montant_tva=declaration.montant_tva,
            montant_total=declaration.total_taxes,
            devise="XAF",
            statut="emis"
        )
        db.add(amc)
        db.commit()
        db.refresh(amc)
        return amc


class CreditEnlevementService:
    """Credit d'enlèvement service"""
    
    @staticmethod
    def accorder_credit(
        db: Session,
        numero_credit: str,
        dossier_transit_id: int,
        type_garantie: str,
        garant: str,
        montant_garantie: float,
        date_echeance: date
    ) -> CreditEnlevement:
        """Grant credit d'enlèvement"""
        credit = CreditEnlevement(
            numero_credit=numero_credit,
            dossier_transit_id=dossier_transit_id,
            type_garantie=type_garantie,
            garant=garant,
            montant_garantie=montant_garantie,
            devise="XAF",
            date_echeance=date_echeance,
            date_delivrance=date.today(),
            statut="accordé"
        )
        db.add(credit)
        db.commit()
        db.refresh(credit)
        return credit


class DroitPortService:
    """Port dues service"""
    
    @staticmethod
    def calculer_droit_port(
        db: Session,
        dossier_transit_id: int,
        type_droit: str,
        description: str,
        base_calcul: str,
        quantite: float,
        taux: float
    ) -> DroitPort:
        """Calculate port due"""
        montant = quantite * taux
        
        droit = DroitPort(
            dossier_transit_id=dossier_transit_id,
            type_droit=type_droit,
            description=description,
            base_calcul=base_calcul,
            quantite=quantite,
            taux=taux,
            montant=montant,
            devise="XAF",
            date_facturation=date.today(),
            statut="facture"
        )
        db.add(droit)
        db.commit()
        db.refresh(droit)
        return droit


class TimbreUsageService:
    """Stamp duty service"""
    
    @staticmethod
    def appliquer_timbre(
        db: Session,
        dossier_transit_id: int,
        type_timbre: str,
        montant: float,
        numero_timbre: str
    ) -> TimbreUsage:
        """Apply stamp duty"""
        timbre = TimbreUsage(
            dossier_transit_id=dossier_transit_id,
            type_timbre=type_timbre,
            montant=montant,
            devise="XAF",
            date_apposition=date.today(),
            numero_timbre=numero_timbre,
            statut="appose"
        )
        db.add(timbre)
        db.commit()
        db.refresh(timbre)
        return timbre


class LitigeDouanierService:
    """Customs dispute service"""
    
    @staticmethod
    def creer_litige(
        db: Session,
        dossier_transit_id: int,
        type_litige: str,
        description: str,
        montant_en_litige: float
    ) -> LitigeDouanier:
        """Create customs dispute"""
        litige = LitigeDouanier(
            dossier_transit_id=dossier_transit_id,
            type_litige=type_litige,
            description=description,
            date_litige=datetime.utcnow(),
            statut="ouvert",
            montant_en_litige=montant_en_litige,
            devise="XAF"
        )
        db.add(litige)
        db.commit()
        db.refresh(litige)
        return litige
    
    @staticmethod
    def resoudre_litige(
        db: Session,
        litige_id: int,
        decision: str,
        date_decision: datetime
    ) -> LitigeDouanier:
        """Resolve customs dispute"""
        litige = db.query(LitigeDouanier).filter(LitigeDouanier.id == litige_id).first()
        if not litige:
            raise ValueError("Litige non trouvé")
        
        litige.statut = "resolu"
        litige.decision = decision
        litige.date_decision = date_decision
        db.commit()
        db.refresh(litige)
        return litige


class ArchivageDossierService:
    """Dossier archiving service"""
    
    @staticmethod
    def archiver_dossier(
        db: Session,
        dossier_transit_id: int,
        lieu_archivage: str,
        numero_archive: str,
        contenu: str
    ) -> ArchivageDossier:
        """Archive dossier (10-year retention)"""
        date_destruction = date.today() + timedelta(days=3650)  # 10 years
        
        archivage = ArchivageDossier(
            dossier_transit_id=dossier_transit_id,
            date_archivage=date.today(),
            date_destruction=date_destruction,
            lieu_archivage=lieu_archivage,
            numero_archive=numero_archive,
            contenu=contenu,
            statut="archive",
            accessible=True
        )
        db.add(archivage)
        db.commit()
        db.refresh(archivage)
        return archivage


class ProcedureUrgenteService:
    """Urgent customs procedure service"""
    
    @staticmethod
    def demander_procedure_urgente(
        db: Session,
        dossier_transit_id: int,
        type_urgence: str,
        justification: str
    ) -> ProcedureUrgente:
        """Request urgent customs procedure"""
        procedure = ProcedureUrgente(
            dossier_transit_id=dossier_transit_id,
            type_urgence=type_urgence,
            justification=justification,
            date_demande=datetime.utcnow(),
            statut="en_attente"
        )
        db.add(procedure)
        db.commit()
        db.refresh(procedure)
        return procedure
    
    @staticmethod
    def autoriser_procedure(
        db: Session,
        procedure_id: int,
        autorise_par: str,
        fonction: str
    ) -> ProcedureUrgente:
        """Authorize urgent procedure"""
        procedure = db.query(ProcedureUrgente).filter(ProcedureUrgente.id == procedure_id).first()
        if not procedure:
            raise ValueError("Procédure non trouvée")
        
        procedure.statut = "autorise"
        procedure.date_autorisation = datetime.utcnow()
        procedure.autorise_par = autorise_par
        procedure.fonction = fonction
        db.commit()
        db.refresh(procedure)
        return procedure


class TransitReportingService:
    """Transit reporting service"""
    
    @staticmethod
    def rapport_dossier(db: Session, dossier_id: int) -> Dict[str, Any]:
        """Generate complete transit dossier report"""
        dossier = db.query(DossierTransitAvance).filter(
            DossierTransitAvance.id == dossier_id
        ).first()
        if not dossier:
            raise ValueError("Dossier non trouvé")
        
        declarations = db.query(DeclarationDouaniereAvance).filter(
            DeclarationDouaniereAvance.dossier_transit_id == dossier_id
        ).all()
        
        visites = db.query(VisitePhysique).filter(
            VisitePhysique.dossier_transit_id == dossier_id
        ).all()
        
        total_droits = sum(d.total_taxes or 0 for d in declarations)
        total_visites = len(visites)
        visites_conformes = sum(1 for v in visites if v.conformite)
        
        return {
            "dossier": {
                "numero": dossier.numero_dossier,
                "type_transit": dossier.type_transit.value,
                "regime": dossier.regime_douanier.value,
                "statut": dossier.statut,
                "valeur": float(dossier.valeur_marchandise or 0)
            },
            "declarations": {
                "total": len(declarations),
                "total_droits": total_droits
            },
            "visites": {
                "total": total_visites,
                "conformes": visites_conformes
            }
        }
