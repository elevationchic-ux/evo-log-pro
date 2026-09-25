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
from app.models.transit import DossierTransit, DeclarationDouaniere
from app.models.audit import AuditLog
from app.models.outbox import OutboxEvent
from app.models.numerotation import SequenceNumerotation
from app.models.conteneur_cycle import (
    ConteneurCycle, CycleConteneur, DommageConteneur, EmpotageDepotage, InspectionConteneur
)
from app.models.port_cameroun import TerminalPortuaire
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
    "DossierTransit", "DeclarationDouaniere",
    "AuditLog",
    "OutboxEvent",
    "SequenceNumerotation",
    "ConteneurCycle", "CycleConteneur", "DommageConteneur", "EmpotageDepotage", "InspectionConteneur",
    "TerminalPortuaire",
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
