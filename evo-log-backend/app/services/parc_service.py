"""
Parc service - handles fleet and equipment business logic
"""
from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import datetime

from app.models.parc import Vehicule, Equipement, Maintenance
from app.schemas.parc import VehiculeCreate, VehiculeUpdate, EquipementCreate


class ParcService:
    """Service for fleet and equipment management"""
    
    @staticmethod
    def create_vehicule(vehicule_data: VehiculeCreate, db: Session) -> Vehicule:
        """Create a new vehicle"""
        if db.query(Vehicule).filter(Vehicule.immatriculation == vehicule_data.immatriculation).first():
            raise ValueError("Vehicle registration already exists")
        
        db_vehicule = Vehicule(**vehicule_data.model_dump())
        db.add(db_vehicule)
        db.commit()
        db.refresh(db_vehicule)
        return db_vehicule
    
    @staticmethod
    def update_vehicule(vehicule_id: int, vehicule_data: VehiculeUpdate, db: Session) -> Vehicule:
        """Update vehicle information"""
        vehicule = db.query(Vehicule).filter(Vehicule.id == vehicule_id).first()
        if not vehicule:
            raise ValueError("Vehicle not found")
        
        for field, value in vehicule_data.model_dump(exclude_unset=True).items():
            setattr(vehicule, field, value)
        
        db.commit()
        db.refresh(vehicule)
        return vehicule
    
    @staticmethod
    def create_equipement(equipement_data: EquipementCreate, db: Session) -> Equipement:
        """Create new equipment"""
        if db.query(Equipement).filter(Equipement.code == equipement_data.code).first():
            raise ValueError("Equipment code already exists")
        
        db_equipement = Equipement(**equipement_data.model_dump())
        db.add(db_equipement)
        db.commit()
        db.refresh(db_equipement)
        return db_equipement
    
    @staticmethod
    def get_vehicules_en_maintenance(db: Session) -> List[Vehicule]:
        """Get vehicles currently in maintenance"""
        return db.query(Vehicule).filter(Vehicule.status == "en_maintenance").all()
    
    @staticmethod
    def get_vehicules_disponibles(db: Session) -> List[Vehicule]:
        """Get available vehicles"""
        return db.query(Vehicule).filter(
            Vehicule.status == "disponible",
            Vehicule.is_active == True
        ).all()
    
    @staticmethod
    def schedule_maintenance(vehicule_id: int, date_planifiee: datetime, db: Session) -> Maintenance:
        """Schedule maintenance for a vehicle"""
        import random
        import string
        
        reference = f"MNT-{datetime.now().strftime('%Y%m%d')}-{''.join(random.choices(string.ascii_uppercase + string.digits, k=6))}"
        
        db_maintenance = Maintenance(
            reference=reference,
            vehicule_id=vehicule_id,
            date_planifiee=date_planifiee,
            statut="planifie"
        )
        db.add(db_maintenance)
        db.commit()
        db.refresh(db_maintenance)
        return db_maintenance