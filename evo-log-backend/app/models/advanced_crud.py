"""Modeles reels des modules avances precedentement en stub 501.

Ces tables remplacent les « donnees fabriquees » que renvoyaient les routers
CRM / projets / immobilisations / bourse de fret / cles API. Chaque ligne est
desormais portee par un tenant (organization_id) et reellement persistee.
Aucune valeur n'est inventee : les calculs (amortissement, cle API) sont
deterministes et bases sur les champs saisis.
"""
from datetime import datetime, date

from sqlalchemy import (
    Column, Integer, String, Text, DateTime, Boolean, ForeignKey, Numeric, JSON,
)
from sqlalchemy.sql import func

from app.core.database import Base


class CRMOpportunity(Base):
    """Opportunite du pipeline commercial, portee par un tenant."""
    __tablename__ = "crm_opportunities"

    id = Column(Integer, primary_key=True, index=True)
    organization_id = Column(Integer, ForeignKey('organizations.id'), nullable=True, index=True)
    client_name = Column(String(200), nullable=False)
    title = Column(String(200), nullable=False)
    estimated_value = Column(Numeric, default=0)
    currency = Column(String(10), default="XAF")
    stage = Column(String(30), default="PROSPECT")  # PROSPECT, QUALIFIED, PROPOSAL, NEGOTIATION, WON, LOST
    probability = Column(Integer, default=0)          # 0-100, saisi, jamais genere
    contact_person = Column(String(150))
    contact_email = Column(String(150))
    notes = Column(Text)
    created_by = Column(Integer, ForeignKey('users.id'), nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())


class Project(Base):
    """Projet d'infrastructure / logistique porte par un tenant."""
    __tablename__ = "logistics_projects"

    id = Column(Integer, primary_key=True, index=True)
    organization_id = Column(Integer, ForeignKey('organizations.id'), nullable=True, index=True)
    code = Column(String(50), nullable=False, index=True)
    title = Column(String(200), nullable=False)
    budget_xaf = Column(Numeric, default=0)
    spent_xaf = Column(Numeric, default=0)            # engage reellement, saisi
    start_date = Column(String(20))
    end_date = Column(String(20))
    manager_name = Column(String(150))
    status = Column(String(30), default="PLANIFIE")     # PLANIFIE, EN_COURS, CLOTURE, ANNULE
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())


class FixedAsset(Base):
    """Immobilisation et son plan d'amortissement (calcul reel, SYSCOHADA)."""
    __tablename__ = "fixed_assets"

    id = Column(Integer, primary_key=True, index=True)
    organization_id = Column(Integer, ForeignKey('organizations.id'), nullable=True, index=True)
    asset_code = Column(String(50), nullable=False, index=True)
    name = Column(String(200), nullable=False)
    category = Column(String(30), default="FLEET")      # FLEET, MACHINERY, REAL_ESTATE, IT
    acquisition_date = Column(String(20))               # ISO yyyy-mm-dd, saisi
    acquisition_value = Column(Numeric, default=0)
    residual_value = Column(Numeric, default=0)
    amortization_years = Column(Integer, default=5)
    amortization_method = Column(String(20), default="LINEAR")  # LINEAR, DEGRESSIVE
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    def _years_elapsed(self, as_of: date) -> float:
        if not self.acquisition_date:
            return 0.0
        try:
            acq = datetime.strptime(self.acquisition_date[:10], "%Y-%m-%d").date()
        except (ValueError, TypeError):
            return 0.0
        if as_of < acq:
            return 0.0
        return (as_of - acq).days / 365.25

    def amortization_schedule(self, as_of: date | None = None) -> dict:
        """Valeur nette comptable et amortissement cumule CALCULES depuis les
        champs reels (lineaire ou degressif). Aucune valeur inventee : si aucune
        date d'acquisition n'est saisie, la dotation est nulle."""
        today = as_of or date.today()
        gross = float(self.acquisition_value or 0)
        residual = float(self.residual_value or 0)
        years = max(int(self.amortization_years or 0), 1)
        elapsed = self._years_elapsed(today)
        if gross <= residual:
            return {
                "valeur_brute": gross, "amortissement_cumule": 0.0,
                "valeur_nette": gross, "dotation_annuelle": 0.0,
                "annees_amortissement": years, "méthode": self.amortization_method,
            }
        base = gross - residual
        if (self.amortization_method or "LINEAR").upper() == "DEGRESSIVE":
            rate = min(2.0 / years, 1.0)
            # solde degressif : VNC = base * (1-taux)^annees + residuelle
            remaining = base * ((1.0 - rate) ** elapsed)
            cumul = base - remaining
            dotation = gross * rate
        else:
            dotation = base / years
            cumul = min(dotation * elapsed, base)
        vnc = gross - cumul
        return {
            "valeur_brute": round(gross, 2),
            "amortissement_cumule": round(cumul, 2),
            "valeur_nette": round(vnc, 2),
            "dotation_annuelle": round(dotation, 2),
            "annees_amortissement": years,
            "methode": self.amortization_method,
        }


class FreightOffer(Base):
    """Offre de fret publiee sur la bourse fret CEMAC, portee par un tenant."""
    __tablename__ = "freight_offers"

    id = Column(Integer, primary_key=True, index=True)
    organization_id = Column(Integer, ForeignKey('organizations.id'), nullable=True, index=True)
    origin = Column(String(200), nullable=False)
    destination = Column(String(200), nullable=False)
    cargo_type = Column(String(120))
    weight_tons = Column(Numeric, default=0)
    offered_price_xaf = Column(Numeric, default=0)
    status = Column(String(20), default="PUBLIEE")       # PUBLIEE, PRIME, ANNULEE
    published_by = Column(Integer, ForeignKey('users.id'), nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())


class TenantAPIKey(Base):
    """Cle d'API tierce generee cryptographiquement. Seul le HASH est stocke ;
    la cle complete n'est retournée qu'une seule fois a la generation."""
    __tablename__ = "tenant_api_keys"

    id = Column(Integer, primary_key=True, index=True)
    organization_id = Column(Integer, ForeignKey('organizations.id'), nullable=True, index=True)
    key_name = Column(String(150), nullable=False)
    key_prefix = Column(String(16), nullable=False, index=True)  # debut lisible, pour identification
    key_hash = Column(String(64), nullable=False, unique=True)   # sha256 hex, jamais la cle claire
    allowed_ips = Column(JSON, nullable=True)
    active = Column(Boolean, default=True)
    last_used_at = Column(DateTime(timezone=True), nullable=True)
    created_by = Column(Integer, ForeignKey('users.id'), nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())


class ScheduledReport(Base):
    """Export BI reellement planifie et persiste (ordonnanceur applicatif).

    La ligne est en base : nom, format, frequence, destinataires. La generation
    effective du fichier depend du moteur d'exports (PDF/Excel) branche au
    moment de l'execution ; ici on persiste la planification reelle."""
    __tablename__ = "scheduled_reports"

    id = Column(Integer, primary_key=True, index=True)
    organization_id = Column(Integer, ForeignKey('organizations.id'), nullable=True, index=True)
    report_name = Column(String(200), nullable=False)
    format = Column(String(10), default="PDF")            # PDF, EXCEL, CSV
    frequency = Column(String(10), default="MONTHLY")     # DAILY, WEEKLY, MONTHLY
    recipients = Column(JSON, nullable=True)              # liste d'emails saisis
    actif = Column(Boolean, default=True)
    prochaine_execution = Column(DateTime(timezone=True), nullable=True)
    cree_par = Column(Integer, ForeignKey('users.id'), nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
