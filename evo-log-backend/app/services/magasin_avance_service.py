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


class ReceptionService:
    """Goods receipt service"""
    
    @staticmethod
    def creer_bon_reception(
        db: Session,
        commande_id: int,
        fournisseur_id: int,
        date_reception: date
    ) -> BonReception:
        """Create goods receipt note"""
        bon = BonReception(
            commande_id=commande_id,
            fournisseur_id=fournisseur_id,
            date_reception=date_reception,
            statut="en_cours"
        )
        db.add(bon)
        db.commit()
        db.refresh(bon)
        return bon
    
    @staticmethod
    def ajouter_ligne_reception(
        db: Session,
        bon_id: int,
        article_id: int,
        quantite_recue: float,
        quantite_commandee: float,
        emplacement_id: Optional[int] = None
    ) -> LigneBonReception:
        """Add received item line"""
        ligne = LigneBonReception(
            bon_id=bon_id,
            article_id=article_id,
            quantite_recue=quantite_recue,
            quantite_commandee=quantite_commandee,
            emplacement_id=emplacement_id
        )
        db.add(ligne)
        db.commit()
        db.refresh(ligne)
        return ligne
    
    @staticmethod
    def valider_reception(db: Session, bon_id: int) -> BonReception:
        """Validate receipt and update stock"""
        bon = db.query(BonReception).filter(BonReception.id == bon_id).first()
        if not bon:
            raise ValueError("Bon de réception non trouvé")
        
        lignes = db.query(LigneBonReception).filter(
            LigneBonReception.bon_id == bon_id
        ).all()
        
        entrepot = db.query(Entrepot).first()
        
        for ligne in lignes:
            stock = db.query(Stock).filter(
                and_(
                    Stock.article_id == ligne.article_id,
                    Stock.entrepot_id == entrepot.id if entrepot else True
                )
            ).first()
            
            if stock:
                stock.quantite += ligne.quantite_recue
                stock.quantite_disponible += ligne.quantite_recue
            else:
                nouveau_stock = Stock(
                    article_id=ligne.article_id,
                    entrepot_id=entrepot.id if entrepot else 1,
                    quantite=ligne.quantite_recue,
                    quantite_disponible=ligne.quantite_recue,
                    emplacement_detail_id=ligne.emplacement_id
                )
                db.add(nouveau_stock)
        
        bon.statut = "valide"
        bon.date_validation = datetime.utcnow()
        
        db.commit()
        db.refresh(bon)
        return bon


class SortieService:
    """Goods issue service"""
    
    @staticmethod
    def creer_bon_sortie(
        db: Session,
        destinataire_id: int,
        type_sortie: str,
        date_sortie: date
    ) -> BonSortie:
        """Create goods issue note"""
        bon = BonSortie(
            destinataire_id=destinataire_id,
            type_sortie=type_sortie,
            date_sortie=date_sortie,
            statut="en_cours"
        )
        db.add(bon)
        db.commit()
        db.refresh(bon)
        return bon
    
    @staticmethod
    def ajouter_ligne_sortie(
        db: Session,
        bon_id: int,
        stock_id: int,
        quantite: float
    ) -> LigneBonSortie:
        """Add item to issue note"""
        stock = db.query(Stock).filter(Stock.id == stock_id).first()
        if not stock or stock.quantite_disponible < quantite:
            raise ValueError("Stock insuffisant")
        
        ligne = LigneBonSortie(
            bon_id=bon_id,
            stock_id=stock_id,
            quantite=quantite
        )
        db.add(ligne)
        db.commit()
        db.refresh(ligne)
        return ligne
    
    @staticmethod
    def valider_sortie(db: Session, bon_id: int) -> BonSortie:
        """Validate issue and deduct stock"""
        bon = db.query(BonSortie).filter(BonSortie.id == bon_id).first()
        if not bon:
            raise ValueError("Bon de sortie non trouvé")
        
        lignes = db.query(LigneBonSortie).filter(
            LigneBonSortie.bon_id == bon_id
        ).all()
        
        for ligne in lignes:
            stock = db.query(Stock).filter(Stock.id == ligne.stock_id).first()
            if stock:
                stock.quantite -= ligne.quantite
                stock.quantite_disponible -= ligne.quantite
        
        bon.statut = "valide"
        bon.date_validation = datetime.utcnow()
        
        db.commit()
        db.refresh(bon)
        return bon


class RetourService:
    """Customer return service"""
    
    @staticmethod
    def enregistrer_retour(
        db: Session,
        client_id: int,
        article_id: int,
        quantite: float,
        motif: str,
        etat: str = "a_reparer"
    ) -> RetourClient:
        """Register customer return"""
        retour = RetourClient(
            client_id=client_id,
            article_id=article_id,
            quantite=quantite,
            motif=motif,
            etat=etat,
            date_retour=datetime.utcnow()
        )
        db.add(retour)
        db.commit()
        db.refresh(retour)
        return retour
    
    @staticmethod
    def traiter_retour(db: Session, retour_id: int, action: str) -> RetourClient:
        """Process return (repair, replace, refund)"""
        retour = db.query(RetourClient).filter(RetourClient.id == retour_id).first()
        if not retour:
            raise ValueError("Retour non trouvé")
        
        retour.action_effectuee = action
        retour.date_traitement = datetime.utcnow()
        retour.statut = "traite"
        
        db.commit()
        db.refresh(retour)
        return retour


class ColisService:
    """Package tracking service"""
    
    @staticmethod
    def creer_colis(
        db: Session,
        reference_colis: str,
        poids: float,
        dimensions: str,
        contenu: str
    ) -> Colis:
        """Create package record"""
        colis = Colis(
            reference_colis=reference_colis,
            poids=poids,
            dimensions=dimensions,
            contenu=contenu,
            date_creation=datetime.utcnow()
        )
        db.add(colis)
        db.commit()
        db.refresh(colis)
        return colis
    
    @staticmethod
    def etiqueter_colis(db: Session, colis_id: int, code_barres: str) -> Colis:
        """Label package with barcode"""
        colis = db.query(Colis).filter(Colis.id == colis_id).first()
        if not colis:
            raise ValueError("Colis non trouvé")
        
        colis.code_barres = code_barres
        colis.date_etiquetage = datetime.utcnow()
        
        db.commit()
        db.refresh(colis)
        return colis
    
    @staticmethod
    def palettiser_colis(db: Session, colis_id: int, palette_id: str) -> Colis:
        """Palletize package"""
        colis = db.query(Colis).filter(Colis.id == colis_id).first()
        if not colis:
            raise ValueError("Colis non trouvé")
        
        colis.palette_id = palette_id
        colis.date_palettisation = datetime.utcnow()
        
        db.commit()
        db.refresh(colis)
        return colis


class KPIStockService:
    """Warehouse KPI calculation service"""
    
    @staticmethod
    def calculer_rotation_stock(db: Session, article_id: int, jours: int = 90) -> float:
        """Calculate stock turnover rate"""
        date_debut = date.today() - timedelta(days=jours)
        
        # Get total stock sold (sum of outgoing movements)
        sorties = db.query(func.sum(MouvementStock.quantite)).filter(
            and_(
                MouvementStock.article_id == article_id,
                MouvementStock.type_mouvement == "sortie",
                MouvementStock.date_mouvement >= date_debut
            )
        ).scalar() or 0
        
        # Get average stock level
        stock_actuel = db.query(Stock.quantite).filter(
            Stock.article_id == article_id
        ).scalar() or 0
        
        if stock_actuel == 0:
            return 0.0
        
        rotation = (sorties / stock_actuel) * (365 / jours)
        return round(rotation, 2)
    
    @staticmethod
    def calculer_taux_rupture(db: Session, article_id: int, jours: int = 30) -> float:
        """Calculate stock-out rate"""
        date_debut = date.today() - timedelta(days=jours)
        
        # Count days with zero stock
        # Simplified: check if stock was ever zero
        stock_actuel = db.query(Stock.quantite).filter(
            Stock.article_id == article_id
        ).scalar() or 0
        
        return 100.0 if stock_actuel == 0 else 0.0
    
    @staticmethod
    def calculer_precision_stock(db: Session, entrepot_id: int) -> float:
        """Calculate overall inventory accuracy from last cycle counts"""
        dernier_inventaire = db.query(InventaireTournant).filter(
            and_(
                InventaireTournant.entrepot_id == entrepot_id,
                InventaireTournant.statut == "valide"
            )
        ).order_by(InventaireTournant.date_inventaire.desc()).first()
        
        if not dernier_inventaire:
            return 0.0
        
        return InventaireTournantService.calculer_precision_inventaire(
            db, dernier_inventaire.id
        )
