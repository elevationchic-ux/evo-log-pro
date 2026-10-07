"""
SQLAlchemy models for EVO-LOG backend - Simplified Version
Only core models included for production deployment
"""
from app.models.user import User, Role, Permission
from app.models.accreditation import Accreditation, SharedAccess
from app.models.agency import Agency
from app.models.tiers import Tiers, Client, Fournisseur, Partenaire
from app.models.transport import Camion, Conducteur, Mission, Trajet, Panne, Atelage
from app.models.finance import Facture, Paiement, Compte, EcritureComptable, LigneFactureSimple
from app.models.parc import Vehicule, Equipement, Maintenance
from app.models.parc import ZoneParc, EmplacementParc, MouvementParc
from app.models.parc import CarburantRecord
from app.models.purchase import Requisition
from app.models.customer_support import (
    Customer, ContractCustomer, SupportTicket, SupportIncident, FleetDocument
)
from app.models.magasin import Stock, MouvementStock, Entrepot
from app.models.magasin import (
    Article, Commande, LigneCommande, OrdreTransfert, BandeLivraison
)
from app.models.transit import DossierTransit, DeclarationDouaniere, CautionDouaniere, DumCustomsRecord
from app.models.audit import AuditLog
from app.models.outbox import OutboxEvent
from app.models.numerotation import SequenceNumerotation
from app.models.conteneur_cycle import (
    ConteneurCycle, CycleConteneur, DommageConteneur, EmpotageDepotage, InspectionConteneur
)
from app.models.port_cameroun import TerminalPortuaire
# Departement Amenagement portuaire : enregistre les tables du domaine public
# (schemas directeurs, programmation, marches, titres, concessions, ouvrages,
# dragage, autorisations). Importe ici pour que Base.metadata les connaisse des
# que l'application demarre (create_all dev, autogenerate Alembic).
from app.models.amenagement_portuaire import (
    SchemaDirecteur, ProjetAmenagement, DocumentProgrammation, MarcheAmenagement,
    AutorisationDomaniale, ConcessionPortuaire, InfrastructurePortuaire,
    Dragage, AutorisationTravaux,
)
from app.models.tenant import Company, SubscriptionPlan, Subscription, Department, B2BPortal, TenantAuditLog
from app.models.finance_ohada import (
    PlanComptableOHADA, EcritureComptableNew, ExerciceComptable, FactureNew, LigneFactureOHADA,
    Reglement, TVADeclarable, RetenueSource, ISDeclarable, CentimesAdditionnels, Patente,
    Bilan, CompteResultat, SignatureElectronique, JournalAuxiliaire, LigneJournal,
    Lettrage, EcritureLettree, GrandLivreLigne, BalanceVerification, LigneBalance,
    BilanOHADADetaille, CompteResultatOHADADetaille, TAFIRE, AnnexesOHADA
)

__all__ = [
    "User", "Role", "Permission",
    "Agency",
    "Tiers", "Client", "Fournisseur", "Partenaire",
    "Camion", "Conducteur", "Mission", "Trajet", "Panne", "Atelage",
    "Facture", "Paiement", "Compte", "EcritureComptable", "LigneFactureSimple",
    "Vehicule", "Equipement", "Maintenance",
    "ZoneParc", "EmplacementParc", "MouvementParc",
    "CarburantRecord",
    "Requisition",
    "Customer", "ContractCustomer", "SupportTicket", "SupportIncident", "FleetDocument",
    "Stock", "MouvementStock", "Entrepot",
    "Article", "Commande", "LigneCommande", "OrdreTransfert", "BandeLivraison",
    "DossierTransit", "DeclarationDouaniere", "CautionDouaniere", "DumCustomsRecord",
    "AuditLog",
    "OutboxEvent",
    "SequenceNumerotation",
    "ConteneurCycle", "CycleConteneur", "DommageConteneur", "EmpotageDepotage", "InspectionConteneur",
    "TerminalPortuaire",
    "SchemaDirecteur", "ProjetAmenagement", "DocumentProgrammation", "MarcheAmenagement",
    "AutorisationDomaniale", "ConcessionPortuaire", "InfrastructurePortuaire",
    "Dragage", "AutorisationTravaux",
    "Company", "SubscriptionPlan", "Subscription", "Department", "B2BPortal", "TenantAuditLog",
    "PlanComptableOHADA", "EcritureComptableNew", "ExerciceComptable", "FactureNew", "LigneFactureOHADA",
    "Reglement", "TVADeclarable", "RetenueSource", "ISDeclarable", "CentimesAdditionnels", "Patente",
    "Bilan", "CompteResultat", "SignatureElectronique", "JournalAuxiliaire", "LigneJournal",
    "Lettrage", "EcritureLettree", "GrandLivreLigne", "BalanceVerification", "LigneBalance",
    "BilanOHADADetaille", "CompteResultatOHADADetaille", "TAFIRE", "AnnexesOHADA"
]

try:
    from app.models.new_k_modules import CotationDevis, ElectronicPOD, FuelTankSensor, PurchaseOrder, ComplianceAudit
    __all__.extend(["CotationDevis", "ElectronicPOD", "FuelTankSensor", "PurchaseOrder", "ComplianceAudit"])
except Exception:
    pass

try:
    from app.models.organization import Organization
    __all__.append("Organization")
except Exception:
    pass

try:
    from app.models.prestataire import Prestataire, DemandeCotation
    from app.models.chef_personnel import PlanningGarde, PointageVacation, DotationEPI
    __all__.extend(["Prestataire", "DemandeCotation", "PlanningGarde", "PointageVacation", "DotationEPI"])
except Exception:
    pass

try:
    from app.models.frais_mission import FraisMission, AvanceMission
    __all__.extend(["FraisMission", "AvanceMission"])
except Exception:
    pass

try:
    from app.models.gap_bridge import SystemSetting, Tarif, RegistreEntry
    __all__.extend(["SystemSetting", "Tarif"])
except Exception:
    pass

try:
    from app.models.advanced_crud import (
        CRMOpportunity, Project, FixedAsset, FreightOffer, TenantAPIKey,
        ScheduledReport, EInvoiceSignature, AIChatMessage, AIFeedback,
        LotSerial, TemperatureReading, Consignation, Block, PrivacyBreach,
        SecurityEscalationSetting, PaymentTransaction,
    )
    __all__.extend([
        "CRMOpportunity", "Project", "FixedAsset", "FreightOffer", "TenantAPIKey",
        "ScheduledReport", "EInvoiceSignature", "AIChatMessage", "AIFeedback",
        "LotSerial", "TemperatureReading", "Consignation", "Block", "PrivacyBreach",
        "SecurityEscalationSetting", "PaymentTransaction",
    ])
except Exception:
    pass

# Batch 4 : surfaces auparavant stubs 501 / succes fabrique, desormais persistees.
# Importees ici pour que Base.metadata les voie des le demarrage (create_all dev,
# autogenerate Alembic) meme si aucun router ne les a encore chargees.
try:
    from app.models.chat import ChatMeetingRoom, ChatRoomMember, EnterpriseChatMessage, ChatContextualPin
    __all__.extend(["ChatMeetingRoom", "ChatRoomMember", "EnterpriseChatMessage", "ChatContextualPin"])
except Exception:
    pass

try:
    from app.models.rh import OffreEmploi, Candidature
    __all__.extend(["OffreEmploi", "Candidature"])
except Exception:
    pass

try:
    from app.models.qhse import PermisTravail, SignaturePermis, HeuresExposition
    __all__.extend(["PermisTravail", "SignaturePermis", "HeuresExposition"])
except Exception:
    pass

# Entites metiers portant company_id mais declarees dans des modules chargés
# uniquement par les routers (app.main), jamais via app.models. L'enumeration du
# moteur d'isolation multi-tenant (tenant_enforcement._tenant_scoped_classes)
# fait `import app.models` pour figer sa liste ; si ces classes n'y sont pas, la
# liste peut etre calculee AVANT qu'app.main ne les enregistre -> entites NON
# filtres par tenant = fuite de donnees inter-entreprises. On les enregistre donc
# ici pour que `import app.models` soit la source complete et ordonnable.
from app.models.acconage import Navire, Escale
from app.models.acquisition import BonCommande
from app.models.magasin_avance import BonReception
from app.models.transport_international import OrdreTransport
from app.models.fiscalite_cameroun import (
    DeclarationFiscale, ContratFiscal, RetenueSourceCameroun,
)
__all__.extend([
    "Navire", "Escale", "BonCommande", "BonReception", "OrdreTransport",
    "DeclarationFiscale", "ContratFiscal", "RetenueSourceCameroun",
])

# Wave 1A expansion : operations portuaires approfondies (12 entites).
try:
    from app.models.port_operations_deep import (
        DraftSurvey, StevedoringCrew, CargoHandlingPlan, QuayEquipment,
        PilotageSession, TowageOperation, BunkeringOrder, VesselWasteReceipt,
        TallySheet, DemurrageCase, GatePass, YardOperation,
    )
    __all__.extend([
        "DraftSurvey", "StevedoringCrew", "CargoHandlingPlan", "QuayEquipment",
        "PilotageSession", "TowageOperation", "BunkeringOrder", "VesselWasteReceipt",
        "TallySheet", "DemurrageCase", "GatePass", "YardOperation",
    ])
except Exception:
    pass

# Wave 1B expansion : transit-douane approfondi (12 entites).
try:
    from app.models import transit_deep as _transit_deep  # noqa: F401
except Exception:
    pass
