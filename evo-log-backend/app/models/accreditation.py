"""Modeles d'habilitation avancee : Accreditations et acces partages.

Ces tables completent le RBAC existant (User.role_level + Role.modules_allowed +
Permission granulaire) sans le remplacer :

- :class:`Accreditation`  habilitation nominative, datee et comptable, portee
  par un utilisateur. Elle peut accorder une permission supplementaire
  (``permission_code``) ou restreindre le perimetre de visibilité d'un chef
  de departement a une liste explicite de collaborateurs (``type=scope``).
  Une accreditation expiree (date_fin depassee ou statut != actif) est
  ignoree par le moteur d'autorisation.

- :class:`SharedAccess`  bascule par entreprise designant les modules "communs"
  accessibles a TOUS les utilisateurs authentifies du tenant, quel que soit
  leur role (portail RH self-service, messagerie interne, notifications...).
"""
from sqlalchemy import (
    Column, Integer, String, Boolean, DateTime, ForeignKey, Text, Date,
    UniqueConstraint,
)
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.core.database import Base


# Types d'accreditation reconnus par le moteur.
ACC_TYPE_PERMISSION = "permission"   # accorde un code de permission
ACC_TYPE_SCOPE = "scope"             # restreint/etend la visibility (ids users)
ACC_TYPES = (ACC_TYPE_PERMISSION, ACC_TYPE_SCOPE)

# Statuts d'une accreditation.
ACC_STATUT_ACTIF = "actif"
ACC_STATUT_SUSPENDU = "suspendu"
ACC_STATUT_REVOQUE = "revoque"


class Accreditation(Base):
    """Habilitation nominative datee portee par un utilisateur."""
    __tablename__ = "accreditations"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    company_id = Column(Integer, ForeignKey("companies.id"), nullable=True, index=True)

    code = Column(String(80), unique=True, index=True)  # reference metier ex: ACC-COMPTA-2026-001
    libelle = Column(String(150), nullable=False)
    type = Column(String(20), default=ACC_TYPE_PERMISSION, nullable=False)

    # Pour type=permission : code d'autorisation accorde (ex: "comptabilite.journal.approve").
    permission_code = Column(String(150))
    # Pour type=scope : liste JSON des ids de collaborateurs couverts.
    perimetre_utilisateurs = Column(Text)  # JSON array [int, ...]

    module = Column(String(50))   # module rattache (affichage / regroupement)

    date_debut = Column(Date)
    date_fin = Column(Date)
    statut = Column(String(20), default=ACC_STATUT_ACTIF, nullable=False)

    motif = Column(Text)
    octroye_par = Column(Integer, ForeignKey("users.id"))

    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    user = relationship("User", foreign_keys=[user_id], back_populates="accreditations")

    def est_valide(self, aujourdhui=None) -> bool:
        """True si l'accreditation est active a la date donnee (defaut : ce jour)."""
        from datetime import date as _date
        if aujourdhui is None:
            aujourdhui = _date.today()
        if (self.statut or ACC_STATUT_ACTIF).lower() != ACC_STATUT_ACTIF:
            return False
        if self.date_debut and aujourdhui < self.date_debut:
            return False
        if self.date_fin and aujourdhui > self.date_fin:
            return False
        return True


class SharedAccess(Base):
    """Module commun accessible a tous les utilisateurs d'une entreprise."""
    __tablename__ = "shared_access"
    __table_args__ = (
        UniqueConstraint("company_id", "module_key", name="uq_shared_access_company_module"),
    )

    id = Column(Integer, primary_key=True, index=True)
    company_id = Column(Integer, ForeignKey("companies.id"), nullable=False, index=True)
    module_key = Column(String(80), nullable=False)   # ex: "rh-mon-espace", "chat"
    libelle = Column(String(150))
    autorise_tous_utilisateurs = Column(Boolean, default=True, nullable=False)

    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    company = relationship("Company", back_populates="shared_access")


# Modules communs par defaut (seed) : accessibles a tout utilisateur authentifie.
DEFAULT_SHARED_MODULES = [
    ("rh-mon-espace", "Portail RH self-service (mes infos, mes conges)"),
    ("chat", "Messagerie / chat interne"),
    ("notifications", "Centre de notifications"),
    ("documents-partages", "Documents communs de l'entreprise"),
    ("annuaire", "Annuaire interne des collaborateurs"),
]
