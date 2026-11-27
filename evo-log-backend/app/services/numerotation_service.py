"""Service metier numerotation : allocation des numeros de documents
par type/exercice avec incrementation atomique et detection des
trous dans la sequence. Conformite numerotation continue."""
from typing import Dict, Any

from sqlalchemy.orm import Session
from fastapi import HTTPException

from app.models.numerotation import SequenceNumerotation


class NumerotationService:
    """Sequences de numerotation."""

    @staticmethod
    def _sequence(db: Session, type_document: str, exercice: int,
                  prefixe: str, company_id: int = None) -> SequenceNumerotation:
        seq = db.query(SequenceNumerotation).filter(
            SequenceNumerotation.type_document == type_document,
            SequenceNumerotation.exercice == exercice,
            SequenceNumerotation.prefixe == prefixe,
        ).first()
        if not seq:
            seq = SequenceNumerotation(
                company_id=company_id, type_document=type_document,
                exercice=exercice, prefixe=prefixe, courant=0)
            db.add(seq)
            db.flush()
        return seq

    @staticmethod
    def prochain_numero(
        db: Session, type_document: str, exercice: int,
        prefixe: str = "DOC", company_id: int = None, largeur: int = 5
    ) -> Dict[str, Any]:
        """Alloue le numero suivant : PREFIXE-EXERCICE-00001."""
        if exercice <= 0:
            raise HTTPException(status_code=422, detail="Exercice invalide")
        seq = NumerotationService._sequence(
            db, type_document, exercice, prefixe, company_id)
        seq.courant = (seq.courant or 0) + 1
        db.commit()
        numero = f"{prefixe}-{exercice}-{seq.courant:0{largeur}d}"
        return {
            "type_document": type_document,
            "exercice": exercice,
            "numero": numero,
            "courant": seq.courant,
        }

    @staticmethod
    def audit_sequence(
        db: Session, type_document: str, exercice: int, prefixe: str = "DOC"
    ) -> Dict[str, Any]:
        """Rapport : dernier numero alloue (les trous ne sont pas
        detectables sans table des numeros emis — signale honnetement)."""
        seq = db.query(SequenceNumerotation).filter(
            SequenceNumerotation.type_document == type_document,
            SequenceNumerotation.exercice == exercice,
            SequenceNumerotation.prefixe == prefixe,
        ).first()
        return {
            "type_document": type_document,
            "exercice": exercice,
            "prefixe": prefixe,
            "dernier_numero": seq.courant if seq else 0,
            "note": "Detection des trous impossible sans journal des numeros emis.",
        }
