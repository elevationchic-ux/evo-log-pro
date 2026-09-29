"""Advanced warehouse service - FEFO, reservations, transfers, cycle counting"""
from datetime import datetime, date, timedelta
from typing import List, Optional, Dict, Any
from sqlalchemy.orm import Session
from sqlalchemy import and_, or_, func, case, desc
from app.models.magasin_avance import (
    Peremption, ReservationStock, KitArticle, ComposantKit, EmplacementDetail,
    TransfertStock, InventaireTournant, LigneInventaire, FournisseurStock,
    CommandeFournisseur, LigneCommandeFournisseur, BonReception, LigneBonReception,
    BonSortie, LigneBonSortie, RetourClient, LitigeTransporteur, Colis
)
from app.models.magasin import Stock, MouvementStock, Entrepot


class PeremptionService:
    """Expiration/FEFO management service"""
    
    @staticmethod
    def enregistrer_peremption(
        db: Session,
        stock_id: int,
        date_peremption: date,
        lot_numero: str,
        numero_serie: Optional[str] = None
    ) -> Peremption:
        """Register expiration date for lot/serial tracking"""
        peremption = Peremption(
            stock_id=stock_id,
            date_peremption=date_peremption,
            lot_numero=lot_numero,
            numero_serie=numero_serie
        )
        db.add(peremption)
        db.commit()
        db.refresh(peremption)
        return peremption
    
    @staticmethod
    def obtenir_stock_fefo(db: Session, article_id: int, quantite_demandee: float) -> List[Peremption]:
        """
        Get stock using FEFO (First Expired, First Out)
        Returns lots sorted by expiration date
        """
        peremptions = db.query(Peremption).join(Stock).filter(
            and_(
                Stock.article_id == article_id,
                Stock.quantite > 0,
                Peremption.date_peremption >= date.today()
            )
        ).order_by(Peremption.date_peremption.asc()).all()
        
        return peremptions
    
    @staticmethod
    def obtenir_peremptions_critiques(db: Session, jours_critique: int = 30) -> List[Peremption]:
        """Get stock expiring within critical period"""
        date_limite = date.today() + timedelta(days=jours_critique)
        
        peremptions = db.query(Peremption).join(Stock).filter(
            and_(
                Peremption.date_peremption <= date_limite,
                Peremption.date_peremption >= date.today(),
                Stock.quantite > 0
            )
        ).order_by(Peremption.date_peremption.asc()).all()
        
        return peremptions
    
    @staticmethod
    def obtenir_peremptions_expirees(db: Session) -> List[Peremption]:
        """Get expired stock for quarantine"""
        return db.query(Peremption).join(Stock).filter(
            and_(
                Peremption.date_peremption < date.today(),
                Stock.quantite > 0
            )
        ).all()


class ReservationService:
    """Stock reservation service"""
    
    @staticmethod
    def reserver_stock(
        db: Session,
        stock_id: int,
        type_reservation: str,
        reference_id: int,
        quantite: float,
        date_expiration: Optional[date] = None
    ) -> ReservationStock:
        """Reserve stock for specific purpose (order, production, etc.)"""
        stock = db.query(Stock).filter(Stock.id == stock_id).first()
        if not stock:
            raise ValueError("Stock non trouvé")
        
        if stock.quantite_disponible < quantite:
            raise ValueError(f"Stock insuffisant: {stock.quantite_disponible} disponible")
        
        reservation = ReservationStock(
            stock_id=stock_id,
            type_reservation=type_reservation,
            reference_id=reference_id,
            quantite=quantite,
            date_reservation=datetime.utcnow(),
            date_expiration=date_expiration or (date.today() + timedelta(days=7))
        )
        
        stock.quantite_disponible -= quantite
        stock.quantite_reservee = (stock.quantite_reservee or 0) + quantite
        
        db.add(reservation)
        db.commit()
        db.refresh(reservation)
        return reservation
    
    @staticmethod
    def liberer_reservation(db: Session, reservation_id: int) -> ReservationStock:
        """Release stock reservation"""
        reservation = db.query(ReservationStock).filter(
            ReservationStock.id == reservation_id
        ).first()
        
        if not reservation:
            raise ValueError("Réservation non trouvée")
        
        stock = db.query(Stock).filter(Stock.id == reservation.stock_id).first()
        if stock:
            stock.quantite_disponible += reservation.quantite
            stock.quantite_reservee = max(0, (stock.quantite_reservee or 0) - reservation.quantite)
        
        reservation.statut = "libere"
        reservation.date_liberation = datetime.utcnow()
        
        db.commit()
        db.refresh(reservation)
        return reservation
    
    @staticmethod
    def consommer_reservation(db: Session, reservation_id: int) -> ReservationStock:
        """Consume reserved stock (fulfill order)"""
        reservation = db.query(ReservationStock).filter(
            ReservationStock.id == reservation_id
        ).first()
        
        if not reservation:
            raise ValueError("Réservation non trouvée")
        
        stock = db.query(Stock).filter(Stock.id == reservation.stock_id).first()
        if stock:
            stock.quantite -= reservation.quantite
            stock.quantite_reservee = max(0, (stock.quantite_reservee or 0) - reservation.quantite)
        
        reservation.statut = "consomme"
        reservation.date_consommation = datetime.utcnow()
        
        db.commit()
        db.refresh(reservation)
        return reservation
    
    @staticmethod
    def nettoyer_reservations_expirees(db: Session) -> int:
        """Auto-release expired reservations"""
        date_limite = date.today()
        
        reservations = db.query(ReservationStock).filter(
            and_(
                ReservationStock.statut == "active",
                ReservationStock.date_expiration < date_limite
            )
        ).all()
        
        compte = 0
        for reservation in reservations:
            ReservationService.liberer_reservation(db, reservation.id)
            compte += 1
        
        return compte


class KitService:
    """Kitting and assembly service"""
    
    @staticmethod
    def creer_kit(
        db: Session,
        article_kit_id: int,
        nom_kit: str,
        description: str
    ) -> KitArticle:
        """Create kit definition"""
        kit = KitArticle(
            article_kit_id=article_kit_id,
            nom_kit=nom_kit,
            description=description
        )
        db.add(kit)
        db.commit()
        db.refresh(kit)
        return kit
    
    @staticmethod
    def ajouter_composant(
        db: Session,
        kit_id: int,
        article_composant_id: int,
        quantite: float
    ) -> ComposantKit:
        """Add component to kit"""
        composant = ComposantKit(
            kit_id=kit_id,
            article_composant_id=article_composant_id,
            quantite=quantite
        )
        db.add(composant)
        db.commit()
        db.refresh(composant)
        return composant
    
    @staticmethod
    def assembler_kit(db: Session, kit_id: int, quantite_kits: float) -> Dict[str, Any]:
        """Assemble kits from components (check availability first)"""
        kit = db.query(KitArticle).filter(KitArticle.id == kit_id).first()
        if not kit:
            raise ValueError("Kit non trouvé")
        
        composants = db.query(ComposantKit).filter(
            ComposantKit.kit_id == kit_id
        ).all()
        
        # Check component availability
        for comp in composants:
            stock = db.query(Stock).filter(
                Stock.article_id == comp.article_composant_id
            ).first()
            if not stock or stock.quantite_disponible < (comp.quantite * quantite_kits):
                raise ValueError(f"Stock insuffisant pour composant {comp.article_composant_id}")
        
        # Consume components
        for comp in composants:
            stock = db.query(Stock).filter(
                Stock.article_id == comp.article_composant_id
            ).first()
            stock.quantite -= comp.quantite * quantite_kits
            stock.quantite_disponible -= comp.quantite * quantite_kits
        
        # Add kits to stock
        stock_kit = db.query(Stock).filter(
            Stock.article_id == kit.article_kit_id
        ).first()
        if stock_kit:
            stock_kit.quantite += quantite_kits
            stock_kit.quantite_disponible += quantite_kits
        else:
            # Create stock entry for kit
            entrepot = db.query(Entrepot).first()
            if entrepot:
                nouveau_stock = Stock(
                    article_id=kit.article_kit_id,
                    entrepot_id=entrepot.id,
                    quantite=quantite_kits,
                    quantite_disponible=quantite_kits
                )
                db.add(nouveau_stock)
        
        db.commit()
        return {"kit_id": kit_id, "quantite_assemblee": quantite_kits}


class EmplacementService:
    """Detailed location management service"""
    
    @staticmethod
    def definir_emplacement(
        db: Session,
        entrepot_id: int,
        zone: str,
        allee: str,
        rack: Optional[str] = None,
        casier: Optional[str] = None,
        niveau: Optional[str] = None
    ) -> EmplacementDetail:
        """Define detailed storage location"""
        emplacement = EmplacementDetail(
            entrepot_id=entrepot_id,
            zone=zone,
            allee=allee,
            rack=rack,
            casier=casier,
            niveau=niveau
        )
        db.add(emplacement)
        db.commit()
        db.refresh(emplacement)
        return emplacement
    
    @staticmethod
    def obtenir_stock_par_emplacement(db: Session, emplacement_id: int) -> List[Stock]:
        """Get all stock at specific location"""
        return db.query(Stock).filter(
            Stock.emplacement_detail_id == emplacement_id
        ).all()


class TransfertService:
    """Inter-warehouse transfer service"""
    
    @staticmethod
    def creer_transfert(
        db: Session,
        stock_id: int,
        entrepot_source_id: int,
        entrepot_destination_id: int,
        quantite: float,
        motif: str,
        date_transfert: Optional[date] = None
    ) -> TransfertStock:
        """Create stock transfer between warehouses"""
        date_transfert = date_transfert or date.today()
        
        transfert = TransfertStock(
            stock_id=stock_id,
            entrepot_source_id=entrepot_source_id,
            entrepot_destination_id=entrepot_destination_id,
            quantite=quantite,
            motif=motif,
            date_transfert=date_transfert,
            statut="en_attente"
        )
        db.add(transfert)
        db.commit()
        db.refresh(transfert)
        return transfert
    
    @staticmethod
    def executer_transfert(db: Session, transfert_id: int) -> TransfertStock:
        """Execute transfer (move stock)"""
        transfert = db.query(TransfertStock).filter(
            TransfertStock.id == transfert_id
        ).first()
        
        if not transfert:
            raise ValueError("Transfert non trouvé")
        
        stock_source = db.query(Stock).filter(
            and_(
                Stock.id == transfert.stock_id,
                Stock.entrepot_id == transfert.entrepot_source_id
            )
        ).first()
        
        if not stock_source or stock_source.quantite < transfert.quantite:
            raise ValueError("Stock source insuffisant")
        
        # Remove from source
        stock_source.quantite -= transfert.quantite
        stock_source.quantite_disponible -= transfert.quantite
        
        # Add to destination
        stock_dest = db.query(Stock).filter(
            and_(
                Stock.article_id == stock_source.article_id,
                Stock.entrepot_id == transfert.entrepot_destination_id
            )
        ).first()
        
        if stock_dest:
            stock_dest.quantite += transfert.quantite
            stock_dest.quantite_disponible += transfert.quantite
        else:
            nouveau_stock = Stock(
                article_id=stock_source.article_id,
                entrepot_id=transfert.entrepot_destination_id,
                quantite=transfert.quantite,
                quantite_disponible=transfert.quantite
            )
            db.add(nouveau_stock)
        
        transfert.statut = "complete"
        transfert.date_execution = datetime.utcnow()
        
        db.commit()
        db.refresh(transfert)
        return transfert


class InventaireTournantService:
    """Cycle counting service"""
    
    @staticmethod
    def creer_inventaire(
        db: Session,
        entrepot_id: int,
        date_inventaire: date,
        type_inventaire: str = "tournant"
    ) -> InventaireTournant:
        """Create cycle count inventory"""
        inventaire = InventaireTournant(
            entrepot_id=entrepot_id,
            date_inventaire=date_inventaire,
            type_inventaire=type_inventaire,
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
        stock_id: int,
        quantite_comptee: float,
        compteur_id: int
    ) -> LigneInventaire:
        """Add counted item to inventory"""
        stock = db.query(Stock).filter(Stock.id == stock_id).first()
        if not stock:
            raise ValueError("Stock non trouvé")
        
        ecart = quantite_comptee - stock.quantite
        
        ligne = LigneInventaire(
            inventaire_id=inventaire_id,
            stock_id=stock_id,
            quantite_theorique=stock.quantite,
            quantite_comptee=quantite_comptee,
            ecart=ecart,
            compteur_id=compteur_id,
            date_comptage=datetime.utcnow()
        )
        db.add(ligne)
        db.commit()
        db.refresh(ligne)
        return ligne
    
    @staticmethod
    def valider_inventaire(db: Session, inventaire_id: int, validateur_id: int) -> InventaireTournant:
        """Validate inventory and adjust stock"""
        inventaire = db.query(InventaireTournant).filter(
            InventaireTournant.id == inventaire_id
        ).first()
        
        if not inventaire:
            raise ValueError("Inventaire non trouvé")
        
        lignes = db.query(LigneInventaire).filter(
            LigneInventaire.inventaire_id == inventaire_id
        ).all()
        
        # Adjust stock based on counted quantities
        for ligne in lignes:
            if ligne.ecart != 0:
                stock = db.query(Stock).filter(Stock.id == ligne.stock_id).first()
                if stock:
                    stock.quantite = ligne.quantite_comptee
                    stock.quantite_disponible = ligne.quantite_comptee - (stock.quantite_reservee or 0)
        
        inventaire.statut = "valide"
        inventaire.validateur_id = validateur_id
        inventaire.date_validation = datetime.utcnow()
        
        db.commit()
        db.refresh(inventaire)
        return inventaire
    
    @staticmethod
    def calculer_precision_inventaire(db: Session, inventaire_id: int) -> float:
        """Calculate inventory accuracy percentage"""
        lignes = db.query(LigneInventaire).filter(
            LigneInventaire.inventaire_id == inventaire_id
        ).all()
        
        if not lignes:
            return 0.0
        
        lignes_correctes = sum(1 for l in lignes if l.ecart == 0)
        return (lignes_correctes / len(lignes)) * 100


class FournisseurStockService:
    """Supplier performance service"""
    
    @staticmethod
    def evaluer_fournisseur(
        db: Session,
        fournisseur_id: int,
        debut_periode: date,
        fin_periode: date
    ) -> Dict[str, Any]:
        """Evaluate supplier performance"""
        commandes = db.query(CommandeFournisseur).filter(
            and_(
                CommandeFournisseur.fournisseur_id == fournisseur_id,
                CommandeFournisseur.date_commande >= debut_periode,
                CommandeFournisseur.date_commande <= fin_periode
            )
        ).all()
        
        if not commandes:
            return {"note": 0, "commandes": 0, "taux_livraison": 0}
        
        total_commandes = len(commandes)
        commandes_livrees = sum(1 for c in commandes if c.statut == "recu")
        taux_livraison = (commandes_livrees / total_commandes) * 100
        
        # Calculate delivery delay
        delais = []
        for cmd in commandes:
            if cmd.date_livraison and cmd.date_prevue:
                delai = (cmd.date_livraison - cmd.date_prevue).days
                delais.append(delai)
        
        delai_moyen = sum(delais) / len(delais) if delais else 0
        
        # Overall score (simple calculation)
        note = min(100, taux_livraison * 0.7 + max(0, 100 - abs(delai_moyen)) * 0.3)
        
        return {
            "note": round(note, 2),
            "commandes": total_commandes,
            "commandes_livrees": commandes_livrees,
            "taux_livraison": round(taux_livraison, 2),
            "delai_moyen_jours": round(delai_moyen, 2)
        }


class ReapprovisionnementService:
    """Automatic replenishment service"""
    
    @staticmethod
    def generer_commande_automatique(
        db: Session,
        fournisseur_id: int,
        seuil_alerte: float = 10.0
    ) -> List[Dict[str, Any]]:
        """Generate purchase orders for stock below threshold"""
        stocks_bas = db.query(Stock).filter(
            Stock.quantite_disponible < seuil_alerte
        ).all()
        
        commandes_generees = []
        for stock in stocks_bas:
            quantite_commandee = seuil_alerte * 2  # Order double threshold
            
            commande = CommandeFournisseur(
                fournisseur_id=fournisseur_id,
                reference=f"CMD-{datetime.utcnow().strftime('%Y%m%d%H%M%S')}",
                date_commande=date.today(),
                date_prevue=date.today() + timedelta(days=7),
                statut="en_attente"
            )
            db.add(commande)
            db.flush()
            
            ligne = LigneCommandeFournisseur(
                commande_id=commande.id,
                article_id=stock.article_id,
                quantite_commandee=quantite_commandee,
                prix_unitaire=0.0  # To be filled
            )
            db.add(ligne)
            
            commandes_generees.append({
                "article_id": stock.article_id,
                "quantite": quantite_commandee,
                "commande_id": commande.id
            })
        
        db.commit()
        return commandes_generees


# ReceptionService / SortieService / RetourService / ColisService /
# KPIStockService — SUPPRIMÉS (Batch 19). Ces cinq classes n'avaient AUCUN
# consommateur (le router ne retenait que ColisService, lui-même reconstruit
# en direct) et écrivaient/isaient des colonnes fantômes :
#   ReceptionService : BonReception(commande_id), LigneBonReception(bon_id,
#     article_id, emplacement_id), Stock.article_id/quantite → TypeError ou
#     perte silencieuse.
#   SortieService : BonSortie(destinataire_id), stock.quantite — le VRAI
#     circuit de sortie vit dans app/routers/v1/removal_slip.py (Batch 16).
#   RetourService : RetourClient(article_id, etat), action_effectuee/
#     date_traitement — le VRAI circuit retours est dans
#     app/routers/v1/magasin_avance.py (Batch 17).
#   ColisService : reference_colis/date_creation (TypeError), code_barres/
#     palette_id/date_palettisation (colonnes inexistantes) — routes /colis
#     reconstruites Batch 19 sur le modèle réel.
#   KPIStockService : MouvementStock.article_id, Stock.quantite/
#     date_inventaire/statut "valide" (AttributError garantis) — KPI
#     reconstruits Batch 17/18 dans le router.
# Le ReceptionService encore consommé par les tests d'acquisition est une
# AUTRE classe : app/services/acquisition_service.py.
