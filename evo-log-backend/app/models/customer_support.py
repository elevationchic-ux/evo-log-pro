"""
Models Tranche C : CRM customers (fiche client B2B + contrats) et support
(tickets, incidents).

Les clients "magasin" restent servis via le proxy Tiers/Client ; ici le
portail customerAPI frontend attend ses propres endpoints /api/v1/customers.
"""
from sqlalchemy import Column, Integer, String, Text, DateTime, Boolean, ForeignKey, Numeric
from sqlalchemy.sql import func

from app.core.database import Base


class Customer(Base):
    """Fiche client du portail commercial (CRM), distincte du proxy Tiers."""
    __tablename__ = "crm_customers"

    id = Column(Integer, primary_key=True, index=True)
    company_id = Column(Integer, ForeignKey('companies.id'), nullable=True, index=True)
    code = Column(String(30), nullable=False, index=True)
    name = Column(String(150), nullable=False)
    contact_person = Column(String(100))
    email = Column(String(120))
    phone = Column(String(30))
    city = Column(String(80))
    country = Column(String(60), default="Cameroun")
    segment = Column(String(40))      # e.g., "grand_compte", "pme"
    source = Column(String(40))       # e.g., "prospect", "recommandation"
    encadrant = Column(String(100))   # commercial attache
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())


class ContractCustomer(Base):
    """Contrat commercial lie a un client (engagement de service)."""
    __tablename__ = "crm_customer_contracts"

    id = Column(Integer, primary_key=True, index=True)
    company_id = Column(Integer, ForeignKey('companies.id'), nullable=True, index=True)
    reference = Column(String(50), nullable=False, index=True)
    customer_id = Column(Integer, ForeignKey('crm_customers.id'), index=True)
    objet = Column(String(200))
    type_contrat = Column(String(40))  # e.g., "cadre", "point_a_point", "acconage"
    date_debut = Column(DateTime(timezone=True))
    date_fin = Column(DateTime(timezone=True))
    montant = Column(Numeric)
    devise = Column(String(10), default="XAF")
    statut = Column(String(20), default="actif")  # actif / expire / resilie
    notes = Column(Text)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())


class SupportTicket(Base):
    """Ticket de support interne (dysfonctionnement, demande d'assistance)."""
    __tablename__ = "support_tickets"

    id = Column(Integer, primary_key=True, index=True)
    company_id = Column(Integer, ForeignKey('companies.id'), nullable=True, index=True)
    reference = Column(String(50), nullable=False, index=True)
    sujet = Column(String(200), nullable=False)
    description = Column(Text)
    categorie = Column(String(60))
    priorite = Column(String(20), default="normale")  # basse / normale / haute / urgente
    statut = Column(String(20), default="ouvert")    # ouvert / en_cours / resolu / ferme
    demandeur = Column(String(120))
    assigne_a = Column(String(120))
    module_concerne = Column(String(80))
    resolved_at = Column(DateTime(timezone=True))
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())


class FleetDocument(Base):
    """Document administratif lie a un vehicule (carte grise, visite,
    assurance). Le binaire n'est pas stocke ici : only nom + url (la
    GED complete reste un module distinct)."""
    __tablename__ = "fleet_documents"

    id = Column(Integer, primary_key=True, index=True)
    company_id = Column(Integer, ForeignKey('companies.id'), nullable=True, index=True)
    vehicule_id = Column(Integer, ForeignKey('vehicules.id'), index=True)
    type_document = Column(String(60))   # e.g., "carte_grise", "assurance", "visite"
    nom_fichier = Column(String(200))
    url = Column(String(500))
    date_expiration = Column(DateTime(timezone=True))
    statut = Column(String(20), default="valide")  # valide / expire / a_renouveler
    created_at = Column(DateTime(timezone=True), server_default=func.now())


class SupportIncident(Base):
    """Incident signale au support (panne, anomalie bloquante)."""
    __tablename__ = "support_incidents"

    id = Column(Integer, primary_key=True, index=True)
    company_id = Column(Integer, ForeignKey('companies.id'), nullable=True, index=True)
    reference = Column(String(50), nullable=False, index=True)
    titre = Column(String(200), nullable=False)
    description = Column(Text)
    type = Column(String(60))
    priorite = Column(String(20), default="normale")
    statut = Column(String(20), default="ouvert")    # ouvert / en_cours / resolu / ferme
    signale_par = Column(String(120))
    localisation = Column(String(120))
    resolved_at = Column(DateTime(timezone=True))
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
