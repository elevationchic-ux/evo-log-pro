"""
Maintenance service - handles equipment and vehicle maintenance business logic
"""
from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import datetime

from app.models.maintenance_gmao import OrdreMaintenance as Intervention, PieceRechangeGMAO as PieceRechange
from app.schemas.maintenance import InterventionCreate, InterventionUpdate, PieceRechangeCreate


class MaintenanceService:
    """Service for maintenance operations"""
    
    @staticmethod
    def create_intervention(intervention_data: InterventionCreate, db: Session) -> Intervention:
        """Create a new maintenance intervention"""
        import random
        import string
        
        reference = f"INT-{datetime.now().strftime('%Y%m%d')}-{''.join(random.choices(string.ascii_uppercase + string.digits, k=6))}"
        
        # Calculate total cost if not provided
        cout_total = intervention_data.cout_total
        if not cout_total:
            cout_main_oeuvre = intervention_data.cout_main_oeuvre or 0
            cout_pieces = intervention_data.cout_pieces or 0
            cout_total = cout_main_oeuvre + cout_pieces
        
        db_intervention = Intervention(
            reference=reference,
            cout_total=cout_total,
            **intervention_data.model_dump(exclude={'cout_total'})
        )
        db.add(db_intervention)
        db.commit()
        db.refresh(db_intervention)
        return db_intervention
    
    @staticmethod
    def update_intervention_status(intervention_id: int, new_status: str, db: Session) -> Intervention:
        """Update intervention status"""
        intervention = db.query(Intervention).filter(Intervention.id == intervention_id).first()
        if not intervention:
            raise ValueError("Intervention not found")
        
        intervention.statut = new_status
        
        if new_status == "en_cours" and not intervention.date_debut:
            intervention.date_debut = datetime.utcnow()
        elif new_status == "terminee" and not intervention.date_fin:
            intervention.date_fin = datetime.utcnow()
        
        db.commit()
        db.refresh(intervention)
        return intervention
    
    @staticmethod
    def create_piece_rechange(piece_data: PieceRechangeCreate, db: Session) -> PieceRechange:
        """Create a new spare part"""
        db_piece = PieceRechange(**piece_data.model_dump())
        db.add(db_piece)
        db.commit()
        db.refresh(db_piece)
        return db_piece
    
    @staticmethod
    def get_interventions_en_cours(db: Session) -> List[Intervention]:
        """Get interventions currently in progress"""
        return db.query(Intervention).filter(Intervention.statut == "en_cours").all()
    
    @staticmethod
    def get_pieces_stock_faible(db: Session) -> List[PieceRechange]:
        """Get spare parts with low stock"""
        return db.query(PieceRechange).filter(
            PieceRechange.quantite_stock <= PieceRechange.quantite_minimum
        ).all()