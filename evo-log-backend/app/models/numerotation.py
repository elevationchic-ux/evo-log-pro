"""Sequences de numerotation legales (exigence DGI / OHADA).

Le Code general des impots du Cameroun impose une numerotation **continue,
sans blanc ni rupture** des pieces comptables (factures notamment), par
exercice et par entite. Un simple ID auto-incremente recyclable ou une
reference basee sur un timestamp/uuid ne le garantit pas.

Cette table materialise le compteur : une ligne = (entreprise, type de
document, annee civile). Le compteur n'est incremente QUE dans la
transaction qui cree la piece : si l'insertion echoue, le numero est
restitue (pas de trou artificiel).
"""
from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, UniqueConstraint
from sqlalchemy.sql import func

from app.core.database import Base


class SequenceNumerotation(Base):
    """Compteur legal par entreprise / type de piece / exercice."""

    __tablename__ = "sequences_numerotation"
    __table_args__ = (
        UniqueConstraint(
            "company_id", "type_document", "exercice",
            name="uix_sequence_company_type_annee",
        ),
    )

    id = Column(Integer, primary_key=True, index=True)
    # NULL = entreprise non renseignee (mono-tenant / donnees historiques).
    company_id = Column(Integer, ForeignKey("companies.id"), nullable=True, index=True)
    # "FACTURE", "AVOIR", "REGLEMENT"...
    type_document = Column(String(30), nullable=False, index=True)
    exercice = Column(Integer, nullable=False)  # annee civile
    prefixe = Column(String(10), nullable=False, default="FAC")
    courant = Column(Integer, nullable=False, default=0)
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    def __repr__(self) -> str:
        return (
            f"<SequenceNumerotation company={self.company_id} "
            f"type={self.type_document} annee={self.exercice} courant={self.courant}>"
        )
