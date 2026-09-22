"""
Magasin service - handles warehouse and inventory business logic
"""
from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import datetime

from app.models.magasin import Stock, MouvementStock, Entrepot
from app.schemas.magasin import StockCreate, StockUpdate, MouvementStockCreate, EntrepotCreate


class MagasinService:
    """Service for warehouse and inventory operations"""
    
    @staticmethod
    def create_stock(stock_data: StockCreate, db: Session) -> Stock:
        """Create a new stock item"""
        if db.query(Stock).filter(Stock.code_article == stock_data.code_article).first():
            raise ValueError("Article code already exists")
        
        db_stock = Stock(**stock_data.model_dump())
        db.add(db_stock)
        db.commit()
        db.refresh(db_stock)
        return db_stock
    
    @staticmethod
    def create_mouvement_stock(mouvement_data: MouvementStockCreate, db: Session) -> MouvementStock:
        """Create a stock movement and update stock quantities"""
        import random
        import string
        
        reference = f"MOV-{datetime.now().strftime('%Y%m%d')}-{''.join(random.choices(string.ascii_uppercase + string.digits, k=6))}"
        
        stock = db.query(Stock).filter(Stock.id == mouvement_data.stock_id).first()
        if not stock:
            raise ValueError("Stock not found")
        
        # Calculate quantities before and after
        quantite_avant = stock.quantite_disponible
        quantite_apres = quantite_avant
        
        if mouvement_data.type_mouvement == "entree":
            quantite_apres += mouvement_data.quantite
            stock.date_derniere_entree = datetime.utcnow()
        elif mouvement_data.type_mouvement == "sortie":
            if quantite_avant < mouvement_data.quantite:
                raise ValueError("Insufficient stock quantity")
            quantite_apres -= mouvement_data.quantite
            stock.date_derniere_sortie = datetime.utcnow()
        
        # Update stock
        stock.quantite_disponible = quantite_apres
        
        # Create movement record
        db_mouvement = MouvementStock(
            reference=reference,
            quantite_avant=quantite_avant,
            quantite_apres=quantite_apres,
            **mouvement_data.model_dump()
        )
        db.add(db_mouvement)
        db.commit()
        db.refresh(db_mouvement)
        return db_mouvement
    
    @staticmethod
    def create_entrepot(entrepot_data: EntrepotCreate, db: Session) -> Entrepot:
        """Create a new warehouse"""
        if db.query(Entrepot).filter(Entrepot.code == entrepot_data.code).first():
            raise ValueError("Warehouse code already exists")
        
        db_entrepot = Entrepot(**entrepot_data.model_dump())
        db.add(db_entrepot)
        db.commit()
        db.refresh(db_entrepot)
        return db_entrepot
    
    @staticmethod
    def get_stocks_low(db: Session) -> List[Stock]:
        """Get stocks below minimum quantity"""
        return db.query(Stock).filter(
            Stock.quantite_disponible <= Stock.quantite_minimum
        ).all()
    
    @staticmethod
    def get_stock_value(stock_id: int, db: Session) -> float:
        """Calculate total value of a stock item"""
        stock = db.query(Stock).filter(Stock.id == stock_id).first()
        if not stock:
            return 0.0
        return stock.quantite_disponible * (stock.prix_unitaire or 0)
    
    @staticmethod
    def get_entrepot_value(entrepot_id: int, db: Session) -> float:
        """Calculate total value of all stock in a warehouse"""
        stocks = db.query(Stock).filter(Stock.entrepot_id == entrepot_id).all()
        total_value = 0.0
        for stock in stocks:
            total_value += stock.quantite_disponible * (stock.prix_unitaire or 0)
        return total_value