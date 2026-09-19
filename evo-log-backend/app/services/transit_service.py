"""
Transit service - handles customs and transit business logic
"""
from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import datetime

from app.models.transit import DossierTransit, DeclarationDouaniere
from app.schemas.transit import DossierTransitCreate, DossierTransitUpdate, DeclarationDouaniereCreate


class TransitService:
    """Service for customs and transit operations - SYDONIA+ integration"""
    
    @staticmethod
    def create_dossier_transit(dossier_data: DossierTransitCreate, db: Session) -> DossierTransit:
        """Create a new transit dossier"""
        import random
        import string
        
        numero_dossier = f"DTR-{datetime.now().strftime('%Y%m%d')}-{''.join(random.choices(string.ascii_uppercase + string.digits, k=6))}"
        
        db_dossier = DossierTransit(numero_dossier=numero_dossier, **dossier_data.model_dump())
        db.add(db_dossier)
        db.commit()
        db.refresh(db_dossier)
        return db_dossier
    
    @staticmethod
    def update_dossier_status(dossier_id: int, new_status: str, db: Session) -> DossierTransit:
        """Update transit dossier status"""
        dossier = db.query(DossierTransit).filter(DossierTransit.id == dossier_id).first()
        if not dossier:
            raise ValueError("Transit dossier not found")
        
        dossier.statut = new_status
        
        if new_status == "cloture" and not dossier.date_cloture:
            dossier.date_cloture = datetime.utcnow()
        
        db.commit()
        db.refresh(dossier)
        return dossier
    
    @staticmethod
    def create_declaration_douaniere(declaration_data: DeclarationDouaniereCreate, db: Session) -> DeclarationDouaniere:
        """Create a new customs declaration - SYDONIA+ integration"""
        import random
        import string
        
        numero_declaration = f"DEC-{datetime.now().strftime('%Y%m%d')}-{''.join(random.choices(string.ascii_uppercase + string.digits, k=6))}"
        
        # Calculate taxes if not provided
        if not declaration_data.montant_droit and declaration_data.valeur_declaree and declaration_data.taux_droit:
            declaration_data.montant_droit = declaration_data.valeur_declaree * (declaration_data.taux_droit / 100)
        
        if not declaration_data.montant_tva and declaration_data.valeur_declaree and declaration_data.taux_tva:
            declaration_data.montant_tva = declaration_data.valeur_declaree * (declaration_data.taux_tva / 100)
        
        if declaration_data.montant_droit and declaration_data.montant_tva:
            declaration_data.total_taxes = declaration_data.montant_droit + declaration_data.montant_tva + (declaration_data.autres_taxes or 0)
        
        db_declaration = DeclarationDouaniere(numero_declaration=numero_declaration, **declaration_data.model_dump())
        db.add(db_declaration)
        db.commit()
        db.refresh(db_declaration)
        return db_declaration
    
    @staticmethod
    def get_dossiers_en_cours(db: Session) -> List[DossierTransit]:
        """Get all transit dossiers in progress"""
        return db.query(DossierTransit).filter(
            DossierTransit.statut.in_(["ouvert", "en_cours", "en_douane"])
        ).all()
    
    @staticmethod
    def calculate_dossier_taxes(dossier_id: int, db: Session) -> dict:
        """Calculate total taxes for a transit dossier"""
        dossier = db.query(DossierTransit).filter(DossierTransit.id == dossier_id).first()
        if not dossier:
            return {}
        
        declarations = db.query(DeclarationDouaniere).filter(DeclarationDouaniere.dossier_transit_id == dossier_id).all()
        
        total_droits = sum(d.montant_droit or 0 for d in declarations)
        total_tva = sum(d.montant_tva or 0 for d in declarations)
        total_autres = sum(d.autres_taxes or 0 for d in declarations)
        total_general = total_droits + total_tva + total_autres
        
        return {
            "total_droits": total_droits,
            "total_tva": total_tva,
            "total_autres": total_autres,
            "total_general": total_general,
            "nombre_declarations": len(declarations)
        }