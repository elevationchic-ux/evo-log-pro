"""
Transport service - handles vehicle, driver, and mission business logic
"""
from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import datetime

from app.models.transport import Camion, Conducteur, Mission
from app.schemas.transport import CamionCreate, CamionUpdate, ConducteurCreate, MissionCreate, MissionUpdate


class TransportService:
    """Service for transport operations"""
    
    @staticmethod
    def create_camion(camion_data: CamionCreate, db: Session) -> Camion:
        """Create a new truck"""
        if db.query(Camion).filter(Camion.immatriculation == camion_data.immatriculation).first():
            raise ValueError("Truck registration already exists")
        
        db_camion = Camion(**camion_data.model_dump())
        db.add(db_camion)
        db.commit()
        db.refresh(db_camion)
        return db_camion
    
    @staticmethod
    def update_camion(camion_id: int, camion_data: CamionUpdate, db: Session) -> Camion:
        """Update truck information"""
        camion = db.query(Camion).filter(Camion.id == camion_id).first()
        if not camion:
            raise ValueError("Truck not found")
        
        for field, value in camion_data.model_dump(exclude_unset=True).items():
            setattr(camion, field, value)
        
        db.commit()
        db.refresh(camion)
        return camion
    
    @staticmethod
    def create_conducteur(conducteur_data: ConducteurCreate, db: Session) -> Conducteur:
        """Create a new driver"""
        if db.query(Conducteur).filter(Conducteur.numero_permis == conducteur_data.numero_permis).first():
            raise ValueError("License number already exists")
        
        db_conducteur = Conducteur(**conducteur_data.model_dump())
        db.add(db_conducteur)
        db.commit()
        db.refresh(db_conducteur)
        return db_conducteur
    
    @staticmethod
    def create_mission(mission_data: MissionCreate, db: Session) -> Mission:
        """Create a new transport mission"""
        import random
        import string
        
        reference = f"MSN-{datetime.now().strftime('%Y%m%d')}-{''.join(random.choices(string.ascii_uppercase + string.digits, k=6))}"
        
        db_mission = Mission(reference=reference, **mission_data.model_dump())
        db.add(db_mission)
        db.commit()
        db.refresh(db_mission)
        return db_mission
    
    @staticmethod
    def update_mission_status(mission_id: int, new_status: str, db: Session) -> Mission:
        """Update mission status"""
        mission = db.query(Mission).filter(Mission.id == mission_id).first()
        if not mission:
            raise ValueError("Mission not found")
        
        mission.statut = new_status
        
        if new_status == "en_cours" and not mission.date_debut_reelle:
            mission.date_debut_reelle = datetime.utcnow()
        elif new_status == "terminee" and not mission.date_fin_reelle:
            mission.date_fin_reelle = datetime.utcnow()
        
        db.commit()
        db.refresh(mission)
        return mission
    
    @staticmethod
    def get_available_camions(db: Session) -> List[Camion]:
        """Get all available trucks"""
        return db.query(Camion).filter(Camion.status == "active", Camion.is_active == True).all()
    
    @staticmethod
    def get_available_conducteurs(db: Session) -> List[Conducteur]:
        """Get all available drivers"""
        return db.query(Conducteur).filter(Conducteur.is_active == True).all()