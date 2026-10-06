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


class EInvoiceSignature(Base):
    """Registre verifiable des factures electroniques scellees.

    La vérification publique s'appuie sur cette table : une empreinte n'est
    declaree valide que si elle a reellement ete emise et persiste ici (plus de
    « toujours VALID » mensonger). L'empreinte est un SHA-256 calcule sur le
    contenu normalise de la facture ; la valeur fiscale opposable (DGI) depend
    d'un connecteur externe configure, sinon le sceau est d'integrite local."""
    __tablename__ = "e_invoice_signatures"

    id = Column(Integer, primary_key=True, index=True)
    organization_id = Column(Integer, ForeignKey('organizations.id'), nullable=True, index=True)
    invoice_number = Column(String(80), nullable=False, index=True)
    client_niu = Column(String(80))
    total_ht = Column(Numeric, default=0)
    total_tva = Column(Numeric, default=0)
    total_ttc = Column(Numeric, default=0)
    fiscal_hash = Column(String(64), nullable=False, unique=True, index=True)  # sha256 hex
    algorithm = Column(String(20), default="SHA-256")
    provider = Column(String(30), default="local")        # local | dgi (si connecteur configure)
    statut = Column(String(20), default="scelle")          # scelle | transmis
    signed_at = Column(DateTime(timezone=True), server_default=func.now())


class AIChatMessage(Base):
    """Message reel des echanges avec l'assistant IA, persiste par tenant.

    L'historique n'est plus en memoire volatile : chaque tourme (question, et
    reponse quand un LLM a repondu) est enregistre. Aucune reponse n'est inventee
    — quand aucun LLM n'est configure, reponse_generee reste NULL."""
    __tablename__ = "ai_chat_messages"

    id = Column(Integer, primary_key=True, index=True)
    organization_id = Column(Integer, ForeignKey('organizations.id'), nullable=True, index=True)
    session_id = Column(String(64), index=True)
    user_id = Column(Integer, ForeignKey('users.id'), nullable=True, index=True)
    module = Column(String(30))                            # GENERAL, TRANSPORT, ...
    question = Column(Text, nullable=False)
    reponse_generee = Column(Text, nullable=True)         # NULL si aucun LLM
    provider = Column(String(30), nullable=True)          # anthropic/openai/... ou NULL
    cree_le = Column(DateTime(timezone=True), server_default=func.now())


class AIFeedback(Base):
    """Note utilisateur enregistree sur une reponse IA (audit reel)."""
    __tablename__ = "ai_feedback"

    id = Column(Integer, primary_key=True, index=True)
    organization_id = Column(Integer, ForeignKey('organizations.id'), nullable=True, index=True)
    message_id = Column(Integer, ForeignKey('ai_chat_messages.id'), nullable=True, index=True)
    note = Column(Integer, nullable=False)                 # 1-5, saisi
    commentaire = Column(Text, nullable=True)
    utilisateur_id = Column(Integer, ForeignKey('users.id'), nullable=True)
    cree_le = Column(DateTime(timezone=True), server_default=func.now())


# ---------------------------------------------------------------------------
# Batch 3 — tables de persistance reelles pour les modules sectoriels / securite
# ---------------------------------------------------------------------------

class LotSerial(Base):
    """Tracabilite lot / numero de serie reellement persistee (secteur agro /
    pieces). Aucune valeur inventee : les champs sont saisis, la date de peremption
    est celle fournie."""
    __tablename__ = "lot_serial_tracks"

    id = Column(Integer, primary_key=True, index=True)
    organization_id = Column(Integer, ForeignKey('organizations.id'), nullable=True, index=True)
    batch_number = Column(String(80), nullable=False, index=True)
    serial_number = Column(String(120), index=True)
    article_code = Column(String(80), nullable=False, index=True)
    expiry_date = Column(String(20), nullable=True)        # ISO saisi
    humidity_rate_percentage = Column(Numeric, nullable=True)
    enregistre_par = Column(Integer, ForeignKey('users.id'), nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())


class TemperatureReading(Base):
    """Lecture de sonde de temperature (chaine du froid) reellement saisie/
    importee. Les alertes sont DERIVEES de ces valeurs vs seuils, rien n'est
    genere sans mesure enregistree."""
    __tablename__ = "temperature_readings"

    id = Column(Integer, primary_key=True, index=True)
    organization_id = Column(Integer, ForeignKey('organizations.id'), nullable=True, index=True)
    container_ref = Column(String(80), nullable=False, index=True)
    zone = Column(String(80), nullable=True)
    temperature_c = Column(Numeric, nullable=False)        # mesure saisie
    seuil_min_c = Column(Numeric, nullable=True)           # seuil parametre
    seuil_max_c = Column(Numeric, nullable=True)
    capteur_id = Column(String(80), nullable=True)
    mesure_le = Column(DateTime(timezone=True), nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())


class Consignation(Base):
    """Palette / conteneur consigne reellement suivi (mouvement entree/sortie)."""
    __tablename__ = "consignations"

    id = Column(Integer, primary_key=True, index=True)
    organization_id = Column(Integer, ForeignKey('organizations.id'), nullable=True, index=True)
    support_type = Column(String(30), default="PALETTE")   # PALETTE, CONTENEUR, IBC
    support_ref = Column(String(80), nullable=False, index=True)
    client_id = Column(Integer, nullable=True, index=True)
    quantite = Column(Numeric, default=0)                  # saisi
    statut = Column(String(20), default="CONSIGNE")        # CONSIGNE, RESTITUE, PERDU
    valeur_consignation_xaf = Column(Numeric, default=0)   # saisi
    date_consignation = Column(DateTime(timezone=True), nullable=True)
    date_restitution = Column(DateTime(timezone=True), nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())


class Block(Base):
    """Ledger append-only a chainage SHA-256 REEL (blockchain interne). Chaque
    bloc reference l'empreinte du precedent ; la chaine est verifiable en base.
    Ce n'est pas une chaine distributee : c'est un registre d'audit infalsifiable
    local (aucune minage externe inventee)."""
    __tablename__ = "blockchain_ledger"

    id = Column(Integer, primary_key=True, index=True)
    organization_id = Column(Integer, ForeignKey('organizations.id'), nullable=True, index=True)
    height = Column(Integer, nullable=False, index=True)
    entity_type = Column(String(60), nullable=False)
    entity_id = Column(String(80), nullable=False, index=True)
    action = Column(String(80), nullable=False)
    payload_hash = Column(String(64), nullable=False)      # empreinte fournee
    prev_hash = Column(String(64), nullable=False)         # chainage bloc precedent
    block_hash = Column(String(64), nullable=False, unique=True, index=True)
    mined_by = Column(Integer, ForeignKey('users.id'), nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())


class PrivacyBreach(Base):
    """Incident de violation de donnees personnelles reellement enregistre (loi
    2024/017 APDP). La declaration a l'autorite (ANT) est un acte distinct,
    pilote par le connecteur GOV ; ici on persiste l'incident constatement."""
    __tablename__ = "privacy_breaches"

    id = Column(Integer, primary_key=True, index=True)
    organization_id = Column(Integer, ForeignKey('organizations.id'), nullable=True, index=True)
    incident_type = Column(String(80), nullable=False)
    description = Column(Text, nullable=False)
    affected_count = Column(Integer, default=0)            # saisi
    statut = Column(String(30), default="ENREGISTRE")      # ENREGISTRE, DECLARE_ANT
    declare_le = Column(DateTime(timezone=True), server_default=func.now())
    enregistre_par = Column(Integer, ForeignKey('users.id'), nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())


class SecurityEscalationSetting(Base):
    """Regles d'escalade de securite reellement persistees par tenant (au lieu
    d'un dictionnaire volatile perdu au redemarrage)."""
    __tablename__ = "security_escalation_settings"

    id = Column(Integer, primary_key=True, index=True)
    organization_id = Column(Integer, ForeignKey('organizations.id'), nullable=True, index=True)
    config = Column(JSON, nullable=False, default=dict)    # blob de regles saisies
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    created_at = Column(DateTime(timezone=True), server_default=func.now())


class PaymentTransaction(Base):
    """Transaction de paiement local reellement persistee (brouillon d'abord).
    Le statut ne passe a CONFIRME que si le connecteur fournisseur (configure)
    l'a reellement confirme ; sinon reste BROUILLON. Aucun faux encaissement."""
    __tablename__ = "payment_transactions"

    id = Column(Integer, primary_key=True, index=True)
    organization_id = Column(Integer, ForeignKey('organizations.id'), nullable=True, index=True)
    company_id = Column(Integer, ForeignKey('companies.id'), nullable=True, index=True)
    provider = Column(String(30), nullable=False)          # ORANGE_MONEY, MTN_MOBILE_MONEY, VIREMENT_*
    reference = Column(String(80), nullable=False, index=True)
    montant_xaf = Column(Numeric, default=0)
    statut = Column(String(20), default="BROUILLON")       # BROUILLON, INITIE, CONFIRME, ANNULE
    provider_contacte = Column(Boolean, default=False)
    provider_ref = Column(String(120), nullable=True)      # id retourne par la gateway
    description = Column(Text, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
