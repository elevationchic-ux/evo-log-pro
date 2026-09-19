"""Magasin Douane service - Warehouse under customs operations for Cameroon/CEMAC"""
from datetime import datetime, date, timedelta
from typing import List, Optional, Dict, Any
from sqlalchemy.orm import Session
from sqlalchemy import and_, func
from app.models.magasin_douane import (
    EntrepotDouane, DeclarationEntrepot, LigneEntrepot, FicheMagasin, MouvementFiche,
    InventaireDouanier, LigneInventaireDouanier, SurveillanceMagazin, MiseConsommation,
    Reexportation, Destruction, EntretienStock, AssuranceStock, CompteRenduManutention,
    TypeEntrepotDouane, RegimeEntrepot
)


class EntrepotDouaneService:
    """Customs warehouse management service"""
    
    @staticmethod
    def creer_entrepot_douane(
        db: Session,
        code: str,
        nom: str,
        type_entrepot: TypeEntrepotDouane,
        regime: RegimeEntrepot,
        adresse: str,
        surface_m2: float,
        capacite_tonnage: float,
        numero_agrement: str,
        date_agrement: date,
        date_expiration_agrement: date
    ) -> EntrepotDouane:
        """Create customs warehouse"""
        entrepot = EntrepotDouane(
            code=code,
            nom=nom,
            type_entrepot=type_entrepot,
            regime=regime,
            adresse=adresse,
            surface_m2=surface_m2,
            capacite_tonnage=capacite_tonnage,
            numero_agrement=numero_agrement,
            date_agrement=date_agrement,
            date_expiration_agrement=date_expiration_agrement,
            statut="actif"
        )
        db.add(entrepot)
        db.commit()
        db.refresh(entrepot)
        return entrepot


class DeclarationEntrepotService:
    """Warehouse declaration service"""
    
    @staticmethod
    def creer_declaration_entrepot(
        db: Session,
        numero_declaration: str,
        entrepot_id: int,
        dossier_transit_id: int,
        regime: RegimeEntrepot,
        valeur_marchandise: float
    ) -> DeclarationEntrepot:
        """Create warehouse declaration"""
        declaration = DeclarationEntrepot(
            numero_declaration=numero_declaration,
            entrepot_id=entrepot_id,
            dossier_transit_id=dossier_transit_id,
            regime=regime,
            date_declaration=date.today(),
            valeur_marchandise=valeur_marchandise,
            devise="XAF",
            statut="en_attente"
        )
        db.add(declaration)
        db.commit()
        db.refresh(declaration)
        return declaration
    
    @staticmethod
    def accepter_declaration(
        db: Session,
        declaration_id: int,
        valide_par: str,
        fonction: str,
        reference_sygdonia: str
    ) -> DeclarationEntrepot:
        """Accept warehouse declaration"""
        declaration = db.query(DeclarationEntrepot).filter(
            DeclarationEntrepot.id == declaration_id
        ).first()
        if not declaration:
            raise ValueError("Déclaration non trouvée")
        
        declaration.statut = "accepte"
        declaration.date_acceptation = date.today()
        declaration.date_limite = date.today() + timedelta(days=365)  # 1 year for typical regime
        declaration.valide_par = valide_par
        declaration.fonction = fonction
        declaration.reference_sygdonia = reference_sygdonia
        
        db.commit()
        db.refresh(declaration)
        return declaration


class LigneEntrepotService:
    """Warehouse declaration line service"""
    
    @staticmethod
    def ajouter_ligne(
        db: Session,
        declaration_id: int,
        article_id: int,
        designation: str,
        quantite: float,
        unite: str,
        poids_net: float,
        poids_brut: float,
        valeur_unitaire: float,
        emplacement: str,
        numero_lot: str
    ) -> LigneEntrepot:
        """Add line to warehouse declaration"""
        valeur_totale = quantite * valeur_unitaire
        
        ligne = LigneEntrepot(
            declaration_id=declaration_id,
            article_id=article_id,
            designation=designation,
            quantite=quantite,
            unite=unite,
            poids_net=poids_net,
            poids_brut=poids_brut,
            valeur_unitaire=valeur_unitaire,
            valeur_totale=valeur_totale,
            emplacement=emplacement,
            numero_lot=numero_lot,
            statut="stocke"
        )
        db.add(ligne)
        db.commit()
        db.refresh(ligne)
        return ligne


class FicheMagasinService:
    """Stock card management service"""
    
    @staticmethod
    def creer_fiche_magasin(
        db: Session,
        numero_fiche: str,
        entrepot_id: int,
        article_id: int,
        designation: str,
        numero_lot: str,
        stock_initial: float,
        unite: str,
        emplacement: str,
        valeur_unitaire: float
    ) -> FicheMagasin:
        """Create stock card"""
        valeur_totale = stock_initial * valeur_unitaire
        
        fiche = FicheMagasin(
            numero_fiche=numero_fiche,
            entrepot_id=entrepot_id,
            article_id=article_id,
            designation=designation,
            numero_lot=numero_lot,
            date_creation=date.today(),
            stock_initial=stock_initial,
            stock_actuel=stock_initial,
            unite=unite,
            emplacement=emplacement,
            valeur_unitaire=valeur_unitaire,
            valeur_totale=valeur_totale,
            statut="actif"
        )
        db.add(fiche)
        db.commit()
        db.refresh(fiche)
        return fiche
    
    @staticmethod
    def enregistrer_mouvement(
        db: Session,
        fiche_id: int,
        type_mouvement: str,
        quantite: float,
        type_operation: str,
        document_reference: str,
        operateur: str,
        motif: str = ""
    ) -> MouvementFiche:
        """Record stock movement"""
        fiche = db.query(FicheMagasin).filter(FicheMagasin.id == fiche_id).first()
        if not fiche:
            raise ValueError("Fiche non trouvée")
        
        # Update stock
        if type_mouvement == "entree":
            fiche.stock_actuel += quantite
        elif type_mouvement == "sortie":
            fiche.stock_actuel -= quantite
        elif type_mouvement == "ajustement":
            fiche.stock_actuel = quantite
        
        stock_apres = fiche.stock_actuel
        fiche.derniere_mouvement = datetime.utcnow()
        fiche.valeur_totale = fiche.stock_actuel * fiche.valeur_unitaire
        
        mouvement = MouvementFiche(
            fiche_id=fiche_id,
            type_mouvement=type_mouvement,
            date_mouvement=datetime.utcnow(),
            quantite=quantite,
            stock_apres=stock_apres,
            type_operation=type_operation,
            document_reference=document_reference,
            operateur=operateur,
            motif=motif
        )
        db.add(mouvement)
        db.commit()
        db.refresh(mouvement)
        return mouvement


class InventaireDouanierService:
    """Customs inventory service"""
    
    @staticmethod
    def creer_inventaire(
        db: Session,
        numero_inventaire: str,
        entrepot_id: int,
        type_inventaire: str,
        operateur: str
    ) -> InventaireDouanier:
        """Create customs inventory"""
        inventaire = InventaireDouanier(
            numero_inventaire=numero_inventaire,
            entrepot_id=entrepot_id,
            type_inventaire=type_inventaire,
            date_debut=date.today(),
            operateur=operateur,
            statut="en_cours"
        )
        db.add(inventaire)
        db.commit()
        db.refresh(inventaire)
        return inventaire
    
    @staticmethod
    def ajouter_ligne_inventaire(
        db: Session,
        inventaire_id: int,
        article_id: int,
        designation: str,
        numero_lot: str,
        emplacement: str,
        stock_theorique: float,
        stock_reel: float,
        unite: str,
        valeur_unitaire: float
    ) -> LigneInventaireDouanier:
        """Add line to customs inventory"""
        ecart = stock_reel - stock_theorique
        valeur_ecart = ecart * valeur_unitaire
        conforme = abs(ecart) < 0.01  # Small tolerance
        
        ligne = LigneInventaireDouanier(
            inventaire_id=inventaire_id,
            article_id=article_id,
            designation=designation,
            numero_lot=numero_lot,
            emplacement=emplacement,
            stock_theorique=stock_theorique,
            stock_reel=stock_reel,
            ecart=ecart,
            unite=unite,
            valeur_unitaire=valeur_unitaire,
            valeur_ecart=valeur_ecart,
            conforme=conforme
        )
        db.add(ligne)
        db.commit()
        db.refresh(ligne)
        return ligne
    
    @staticmethod
    def completer_inventaire(
        db: Session,
        inventaire_id: int,
        inspecteur_douane: str,
        resultat: str,
        ecart_tonnage: float,
        ecart_valeur: float,
        motif_ecart: str = ""
    ) -> InventaireDouanier:
        """Complete customs inventory"""
        inventaire = db.query(InventaireDouanier).filter(
            InventaireDouanier.id == inventaire_id
        ).first()
        if not inventaire:
            raise ValueError("Inventaire non trouvé")
        
        inventaire.date_fin = date.today()
        inventaire.inspecteur_douane = inspecteur_douane
        inventaire.date_inspection = datetime.utcnow()
        inventaire.resultat = resultat
        inventaire.ecart_tonnage = ecart_tonnage
        inventaire.ecart_valeur = ecart_valeur
        inventaire.motif_ecart = motif_ecart
        inventaire.statut = "termine"
        
        db.commit()
        db.refresh(inventaire)
        return inventaire


class SurveillanceMagazinService:
    """Warehouse surveillance service"""
    
    @staticmethod
    def enregistrer_patrouille(
        db: Session,
        entrepot_id: int,
        gardien: str,
        type_controle: str,
        zones_controlees: str,
        incidents: str = "",
        anomalies: str = ""
    ) -> SurveillanceMagazin:
        """Record patrol"""
        patrouille = SurveillanceMagazin(
            entrepot_id=entrepot_id,
            date_patrouille=datetime.utcnow(),
            gardien=gardien,
            type_controle=type_controle,
            zones_controlees=zones_controlees,
            incidents=incidents,
            anomalies=anomalies,
            statut="normal" if not incidents else "alerte"
        )
        db.add(patrouille)
        db.commit()
        db.refresh(patrouille)
        return patrouille


class MiseConsommationService:
    """Release to consumption service"""
    
    @staticmethod
    def creer_mise_consommation(
        db: Session,
        numero_mise: str,
        declaration_entrepot_id: int,
        valide_par: str,
        fonction: str
    ) -> MiseConsommation:
        """Create release to consumption"""
        mise = MiseConsommation(
            numero_mise=numero_mise,
            declaration_entrepot_id=declaration_entrepot_id,
            date_mise=date.today(),
            valide_par=valide_par,
            fonction=fonction,
            statut="en_attente"
        )
        db.add(mise)
        db.commit()
        db.refresh(mise)
        return mise


class ReexportationService:
    """Re-export service"""
    
    @staticmethod
    def creer_reexportation(
        db: Session,
        numero_reexport: str,
        declaration_entrepot_id: int,
        pays_destination: str,
        code_pays_destination: str,
        motif: str,
        moyen_transport: str
    ) -> Reexportation:
        """Create re-export"""
        reexport = Reexportation(
            numero_reexport=numero_reexport,
            declaration_entrepot_id=declaration_entrepot_id,
            pays_destination=pays_destination,
            code_pays_destination=code_pays_destination,
            motif=motif,
            moyen_transport=moyen_transport,
            date_reexport=date.today(),
            statut="en_attente"
        )
        db.add(reexport)
        db.commit()
        db.refresh(reexport)
        return reexport


class DestructionService:
    """Destruction service"""
    
    @staticmethod
    def creer_destruction(
        db: Session,
        numero_destruction: str,
        declaration_entrepot_id: int,
        motif: str,
        type_destruction: str
    ) -> Destruction:
        """Create destruction request"""
        destruction = Destruction(
            numero_destruction=numero_destruction,
            declaration_entrepot_id=declaration_entrepot_id,
            date_demande=date.today(),
            motif=motif,
            type_destruction=type_destruction,
            statut="en_attente"
        )
        db.add(destruction)
        db.commit()
        db.refresh(destruction)
        return destruction
    
    @staticmethod
    def autoriser_destruction(
        db: Session,
        destruction_id: int,
        autorise_par: str,
        fonction: str,
        temoin: str
    ) -> Destruction:
        """Authorize destruction"""
        destruction = db.query(Destruction).filter(Destruction.id == destruction_id).first()
        if not destruction:
            raise ValueError("Destruction non trouvée")
        
        destruction.date_autorisation = date.today()
        destruction.autorise_par = autorise_par
        destruction.fonction = fonction
        destruction.temoin = temoin
        destruction.statut = "autorise"
        
        db.commit()
        db.refresh(destruction)
        return destruction
    
    @staticmethod
    def effectuer_destruction(
        db: Session,
        destruction_id: int,
        poids_destruct: float,
        valeur_destruct: float,
        rapport_destruction: str,
        photos: str
    ) -> Destruction:
        """Record destruction execution"""
        destruction = db.query(Destruction).filter(Destruction.id == destruction_id).first()
        if not destruction:
            raise ValueError("Destruction non trouvée")
        
        destruction.date_destruction = date.today()
        destruction.poids_destruct = poids_destruct
        destruction.valeur_destruct = valeur_destruct
        destruction.rapport_destruction = rapport_destruction
        destruction.photos = photos
        destruction.statut = "effectue"
        
        db.commit()
        db.refresh(destruction)
        return destruction


class EntretienStockService:
    """Stock maintenance service"""
    
    @staticmethod
    def creer_entretien(
        db: Session,
        numero_entretien: str,
        declaration_entrepot_id: int,
        type_entretien: str,
        article_id: int,
        quantite: float,
        unite: str,
        operateur: str,
        description: str
    ) -> EntretienStock:
        """Create stock maintenance"""
        entretien = EntretienStock(
            numero_entretien=numero_entretien,
            declaration_entrepot_id=declaration_entrepot_id,
            date_entretien=date.today(),
            type_entretien=type_entretien,
            article_id=article_id,
            quantite=quantite,
            unite=unite,
            operateur=operateur,
            description=description,
            statut="en_attente"
        )
        db.add(entretien)
        db.commit()
        db.refresh(entretien)
        return entretien


class AssuranceStockService:
    """Stock insurance service"""
    
    @staticmethod
    def creer_assurance(
        db: Session,
        entrepot_id: int,
        numero_police: str,
        assureur: str,
        type_couverture: str,
        valeur_assuree: float,
        prime_annuelle: float,
        date_debut: date,
        date_fin: date,
        franchise: float
    ) -> AssuranceStock:
        """Create stock insurance"""
        assurance = AssuranceStock(
            entrepot_id=entrepot_id,
            numero_police=numero_police,
            assureur=assureur,
            type_couverture=type_couverture,
            valeur_assuree=valeur_assuree,
            devise="XAF",
            prime_annuelle=prime_annuelle,
            date_debut=date_debut,
            date_fin=date_fin,
            franchise=franchise,
            statut="actif"
        )
        db.add(assurance)
        db.commit()
        db.refresh(assurance)
        return assurance


class CompteRenduManutentionService:
    """Handling operations report service"""
    
    @staticmethod
    def creer_compte_rendu(
        db: Session,
        numero_cr: str,
        entrepot_id: int,
        type_operation: str,
        equipe: str,
        equipement: str,
        duree_heures: float,
        nombre_mouvements: int,
        tonnage_total: float
    ) -> CompteRenduManutention:
        """Create handling operations report"""
        cr = CompteRenduManutention(
            numero_cr=numero_cr,
            entrepot_id=entrepot_id,
            date_operation=date.today(),
            type_operation=type_operation,
            equipe=equipe,
            equipement=equipement,
            duree_heures=duree_heures,
            nombre_mouvements=nombre_mouvements,
            tonnage_total=tonnage_total
        )
        db.add(cr)
        db.commit()
        db.refresh(cr)
        return cr


class MagasinDouaneReportingService:
    """Warehouse reporting service"""
    
    @staticmethod
    def rapport_entrepot(db: Session, entrepot_id: int) -> Dict[str, Any]:
        """Generate warehouse report"""
        entrepot = db.query(EntrepotDouane).filter(
            EntrepotDouane.id == entrepot_id
        ).first()
        if not entrepot:
            raise ValueError("Entrepôt non trouvé")
        
        declarations = db.query(DeclarationEntrepot).filter(
            DeclarationEntrepot.entrepot_id == entrepot_id
        ).all()
        
        fiches = db.query(FicheMagasin).filter(
            FicheMagasin.entrepot_id == entrepot_id
        ).all()
        
        total_valeur = sum(f.valeur_totale or 0 for f in fiches)
        total_tonnage = sum(f.stock_actuel or 0 for f in fiches)
        
        return {
            "entrepot": {
                "code": entrepot.code,
                "nom": entrepot.nom,
                "type": entrepot.type_entrepot.value,
                "regime": entrepot.regime.value,
                "capacite_tonnage": entrepot.capacite_tonnage
            },
            "stock": {
                "total_articles": len(fiches),
                "valeur_totale": total_valeur,
                "tonnage_total": total_tonnage
            },
            "declarations": {
                "total": len(declarations),
                "en_cours": sum(1 for d in declarations if d.statut == "en_attente")
            }
        }
