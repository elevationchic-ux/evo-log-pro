"""
Tiers service - handles clients, suppliers, and partners business logic
"""
from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import datetime

from app.models.tiers import Tiers, Client, Fournisseur
from app.schemas.tiers import TiersCreate, TiersUpdate, ClientCreate, FournisseurCreate


class TiersService:
    """Service for managing clients, suppliers, and partners"""
    
    @staticmethod
    def create_tiers(tiers_data: TiersCreate, db: Session) -> Tiers:
        """Create a new tiers (client/supplier/partner)"""
        if db.query(Tiers).filter(Tiers.code == tiers_data.code).first():
            raise ValueError("Tiers code already exists")
        
        db_tiers = Tiers(**tiers_data.model_dump())
        db.add(db_tiers)
        db.commit()
        db.refresh(db_tiers)
        return db_tiers
    
    @staticmethod
    def create_client(client_data: ClientCreate, db: Session) -> Client:
        """Create a new client"""
        if db.query(Tiers).filter(Tiers.code == client_data.code).first():
            raise ValueError("Client code already exists")
        
        db_client = Client(**client_data.model_dump())
        db.add(db_client)
        db.commit()
        db.refresh(db_client)
        return db_client
    
    @staticmethod
    def create_fournisseur(fournisseur_data: FournisseurCreate, db: Session) -> Fournisseur:
        """Create a new supplier"""
        if db.query(Tiers).filter(Tiers.code == fournisseur_data.code).first():
            raise ValueError("Supplier code already exists")
        
        db_fournisseur = Fournisseur(**fournisseur_data.model_dump())
        db.add(db_fournisseur)
        db.commit()
        db.refresh(db_fournisseur)
        return db_fournisseur
    
    @staticmethod
    def update_tiers(tiers_id: int, tiers_data: TiersUpdate, db: Session) -> Tiers:
        """Update tiers information"""
        tiers = db.query(Tiers).filter(Tiers.id == tiers_id).first()
        if not tiers:
            raise ValueError("Tiers not found")
        
        for field, value in tiers_data.model_dump(exclude_unset=True).items():
            setattr(tiers, field, value)
        
        db.commit()
        db.refresh(tiers)
        return tiers
    
    @staticmethod
    def get_clients_actifs(db: Session) -> List[Client]:
        """Get all active clients"""
        return db.query(Client).filter(Client.is_active == True).all()
    
    @staticmethod
    def get_fournisseurs_actifs(db: Session) -> List[Fournisseur]:
        """Get all active suppliers"""
        return db.query(Fournisseur).filter(Fournisseur.is_active == True, Fournisseur.approved == True).all()
    
    @staticmethod
    def check_credit_limit(tiers_id: int, montant: float, db: Session) -> bool:
        """Check if tiers has sufficient credit limit"""
        tiers = db.query(Tiers).filter(Tiers.id == tiers_id).first()
        if not tiers:
            return False
        
        nouveau_balance = tiers.balance + montant
        return nouveau_balance <= tiers.credit_limit
    
    @staticmethod
    def update_tiers_balance(tiers_id: int, montant: float, db: Session) -> Tiers:
        """Update tiers balance"""
        tiers = db.query(Tiers).filter(Tiers.id == tiers_id).first()
        if not tiers:
            raise ValueError("Tiers not found")
        
        tiers.balance += montant
        db.commit()
        db.refresh(tiers)
        return tiers