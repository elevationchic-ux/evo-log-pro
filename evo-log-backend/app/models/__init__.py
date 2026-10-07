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

# <expansion:transport>
try:
    from app.models.transport_deep import (
        VehicleRegistration,
        RoutePlan,
        CheckpointControl,
        CargoInsurance,
        FreightBill,
        Subcontractor,
        DangerousGoodsLoad,
        VehicleDocument,
        GpsDevice,
        TrafficPenalty,
        Convoy,
        FleetKpi,
    )
    __all__.extend(["VehicleRegistration", "RoutePlan", "CheckpointControl", "CargoInsurance", "FreightBill", "Subcontractor", "DangerousGoodsLoad", "VehicleDocument", "GpsDevice", "TrafficPenalty", "Convoy", "FleetKpi"])
except Exception:
    pass
# </expansion:transport>

# <expansion:magasin>
try:
    from app.models.magasin_deep import (
        ArticleCatalog,
        SupplierArticle,
        PurchaseOrderDeep,
        QualityInspection,
        StockAlert,
        ExpiryRecord,
        SerialNumber,
        PackingUnit,
        StockReturn,
        ConsignmentStock,
        StockValuation,
        WmsKpi,
    )
    __all__.extend(["ArticleCatalog", "SupplierArticle", "PurchaseOrderDeep", "QualityInspection", "StockAlert", "ExpiryRecord", "SerialNumber", "PackingUnit", "StockReturn", "ConsignmentStock", "StockValuation", "WmsKpi"])
except Exception:
    pass
# </expansion:magasin>

# <expansion:comptabilite>
try:
    from app.models.comptabilite_deep import (
        AssetRegistration,
        DepreciationSchedule,
        Provision,
        BankReconciliation,
        IntercompanyEntry,
        BudgetControl,
        AuditPaf,
        TaxDeclaration,
        PayrollEntry,
        TreasuryAccount,
        AnalyticalSection,
    )
    __all__.extend(["AssetRegistration", "DepreciationSchedule", "Provision", "BankReconciliation", "IntercompanyEntry", "BudgetControl", "AuditPaf", "TaxDeclaration", "PayrollEntry", "TreasuryAccount", "AnalyticalSection"])
except Exception:
    pass
# </expansion:comptabilite>

# <expansion:finance>
try:
    from app.models.finance_deep import (
        MultiyearBudget,
        CreditFacility,
        CashPool,
        FinancialInvestment,
        FxExposure,
        PaymentSchedule,
        ExpenseReport,
        PettyCashBox,
        BankGuarantee,
        LeaseContract,
        CashForecast,
        TreasuryAlert,
    )
    __all__.extend(["MultiyearBudget", "CreditFacility", "CashPool", "FinancialInvestment", "FxExposure", "PaymentSchedule", "ExpenseReport", "PettyCashBox", "BankGuarantee", "LeaseContract", "CashForecast", "TreasuryAlert"])
except Exception:
    pass
# </expansion:finance>

# <expansion:parc>
try:
    from app.models.parc_deep import (
        VehicleInventory,
        TyreRecord,
        SparePart,
        WorkshopAppointment,
        InsuranceClaim,
        RegistrationRecord,
        TechnicalVisit,
        FuelConsumption,
        VehicleLifecycle,
        CostAnalysis,
    )
    __all__.extend(["VehicleInventory", "TyreRecord", "SparePart", "WorkshopAppointment", "InsuranceClaim", "RegistrationRecord", "TechnicalVisit", "FuelConsumption", "VehicleLifecycle", "CostAnalysis"])
except Exception:
    pass
# </expansion:parc>

# <expansion:rh>
try:
    from app.models.rh_deep import (
        Recruitment,
        TrainingPlan,
        PerformanceReview,
        DisciplinaryCase,
        OrgUnit,
        WorkforcePlan,
        EmploymentContract,
        EmployeeBenefit,
        EmployeeExit,
        AttendanceDevice,
        LeaveQuota,
        EmployeeSkill,
        HrReport,
    )
    __all__.extend(["Recruitment", "TrainingPlan", "PerformanceReview", "DisciplinaryCase", "OrgUnit", "WorkforcePlan", "EmploymentContract", "EmployeeBenefit", "EmployeeExit", "AttendanceDevice", "LeaveQuota", "EmployeeSkill", "HrReport"])
except Exception:
    pass
# </expansion:rh>

# <expansion:qhse>
try:
    from app.models.qhse_deep import (
        EnvironmentalMeasurement,
        WasteRecord,
        SafetyDataSheet,
        EmergencyPlan,
        PpeItem,
        HealthVisit,
        RiskAssessment,
        CorrectiveAction,
        ManagementReview,
        ComplianceRecord,
        QualityAudit,
    )
    __all__.extend(["EnvironmentalMeasurement", "WasteRecord", "SafetyDataSheet", "EmergencyPlan", "PpeItem", "HealthVisit", "RiskAssessment", "CorrectiveAction", "ManagementReview", "ComplianceRecord", "QualityAudit"])
except Exception:
    pass
# </expansion:qhse>

# <expansion:b2b>
try:
    from app.models.b2b_deep import (
        ClientOnboarding,
        SlaContract,
        B2bContract,
        SatisfactionSurvey,
        ClientCreditLimit,
        B2bDocument,
        ServiceRequest,
        PricingAgreement,
        ShipmentBooking,
        ClientClaim,
        AccountReport,
    )
    __all__.extend(["ClientOnboarding", "SlaContract", "B2bContract", "SatisfactionSurvey", "ClientCreditLimit", "B2bDocument", "ServiceRequest", "PricingAgreement", "ShipmentBooking", "ClientClaim", "AccountReport"])
except Exception:
    pass
# </expansion:b2b>

# <expansion:reports>
try:
    from app.models.reports_deep import (
        WarehouseTable,
        Scorecard,
        IndustryBenchmark,
        PredictiveModel,
        CustomDashboard,
        ReportExport,
        KpiDefinition,
        DrillPath,
        CohortAnalysis,
        AnomalyRecord,
        RegulatoryReport,
    )
    __all__.extend(["WarehouseTable", "Scorecard", "IndustryBenchmark", "PredictiveModel", "CustomDashboard", "ReportExport", "KpiDefinition", "DrillPath", "CohortAnalysis", "AnomalyRecord", "RegulatoryReport"])
except Exception:
    pass
# </expansion:reports>


# <expansion:superadmin>
try:
    from app.models.superadmin_deep import (
        PlatformAudit,
        ComplianceDashboard,
        RetentionPolicy,
        PlatformIncident,
        AccessReview,
        SoftwareLicense,
        TechnologyPartner,
        SaasRevenueRecord,
        GlobalConfigSetting,
        DrPlan,
    )
    __all__.extend(["PlatformAudit", "ComplianceDashboard", "RetentionPolicy", "PlatformIncident", "AccessReview", "SoftwareLicense", "TechnologyPartner", "SaasRevenueRecord", "GlobalConfigSetting", "DrPlan"])
except Exception:
    pass
# </expansion:superadmin>

# <expansion:dashboard>
try:
    from app.models.dashboard_deep import (
        ModuleHealth,
        ActivityRecord,
        UnifiedTask,
        QuickAction,
        TeamPerformance,
        FinancialSummary,
        OperationalAlert,
        RecentDocument,
        UnifiedAgenda,
        IntegrationStatus,
    )
    __all__.extend(["ModuleHealth", "ActivityRecord", "UnifiedTask", "QuickAction", "TeamPerformance", "FinancialSummary", "OperationalAlert", "RecentDocument", "UnifiedAgenda", "IntegrationStatus"])
except Exception:
    pass
# </expansion:dashboard>

# <expansion:amenagement_extra>
try:
    from app.models.amenagement_extra_deep import (
        ConstructionProgress,
        InfrastructureMaintenance,
        IspsRecord,
        PortPerception,
        AnnualActivityReport,
        SigLayer,
        DomainArchive,
        AmenagementKpi,
    )
    __all__.extend(["ConstructionProgress", "InfrastructureMaintenance", "IspsRecord", "PortPerception", "AnnualActivityReport", "SigLayer", "DomainArchive", "AmenagementKpi"])
except Exception:
    pass
# </expansion:amenagement_extra>

# <expansion:admin>
try:
    from app.models.admin_deep import (
        FeatureFlag,
        ApiQuota,
        WhiteLabel,
        TenantOnboarding,
        SaasApiKey,
        TenantWebhook,
        DataMigration,
        PlatformTicket,
        BillingEntry,
        UsageAnalytics,
        UptimeRecord,
    )
    __all__.extend(["FeatureFlag", "ApiQuota", "WhiteLabel", "TenantOnboarding", "SaasApiKey", "TenantWebhook", "DataMigration", "PlatformTicket", "BillingEntry", "UsageAnalytics", "UptimeRecord"])
except Exception:
    pass
# </expansion:admin>

# <expansion:ferroviaire>
try:
    from app.models.ferroviaire_deep import (
        RailWagon,
        RailLocomotive,
        RailTrainPath,
        RailShuntingYard,
        RailTerminal,
        RailConsistencyPlan,
        RailWaybill,
        RailTariff,
        RailWagonTracking,
        RailWagonMaintenance,
        RailSafetyRecord,
        RailCorridor,
    )
    __all__.extend(["RailWagon", "RailLocomotive", "RailTrainPath", "RailShuntingYard", "RailTerminal", "RailConsistencyPlan", "RailWaybill", "RailTariff", "RailWagonTracking", "RailWagonMaintenance", "RailSafetyRecord", "RailCorridor"])
except Exception:
    pass
# </expansion:ferroviaire>

# <expansion:aerien>
try:
    from app.models.aerien_deep import (
        Aircraft,
        AirWaybill,
        AirSlot,
        GroundHandlingJob,
        ULDInventory,
        CargoSecurityScreen,
        AirDangerousGoods,
        FlightOperation,
        CrewRoster,
        AircraftCheck,
        AirportCargoWarehouse,
        AirTariff,
    )
    __all__.extend(["Aircraft", "AirWaybill", "AirSlot", "GroundHandlingJob", "ULDInventory", "CargoSecurityScreen", "AirDangerousGoods", "FlightOperation", "CrewRoster", "AircraftCheck", "AirportCargoWarehouse", "AirTariff"])
except Exception:
    pass
# </expansion:aerien>

# <expansion:fluvial>
try:
    from app.models.fluvial_deep import (
        FluvialBarge,
        FluvialTowboat,
        LockTransit,
        RiverDepthSurvey,
        FluvialTerminal,
        FluvialBulkOperation,
        FluvialSafetyRecord,
        FluvialTariff,
        FluvialWaybill,
        FluvialPosition,
    )
    __all__.extend(["FluvialBarge", "FluvialTowboat", "LockTransit", "RiverDepthSurvey", "FluvialTerminal", "FluvialBulkOperation", "FluvialSafetyRecord", "FluvialTariff", "FluvialWaybill", "FluvialPosition"])
except Exception:
    pass
# </expansion:fluvial>

# <expansion:log3pl>
try:
    from app.models.log3pl_deep import (
        TplContract,
        TplWarehouse,
        TplCrossDock,
        TplPickingLine,
        TplSlaKpi,
        TplInvoice,
        TplInventoryValuation,
        TplSubProvider,
        TplReverseOperation,
        TplControlTower,
    )
    __all__.extend(["TplContract", "TplWarehouse", "TplCrossDock", "TplPickingLine", "TplSlaKpi", "TplInvoice", "TplInventoryValuation", "TplSubProvider", "TplReverseOperation", "TplControlTower"])
except Exception:
    pass
# </expansion:log3pl>

# <expansion:log3pl_b>
try:
    from app.models.log3pl_b_deep import (
        TplDockAppointment,
        TplLoadingPlan,
        TplShipmentManifest,
        TplInventoryTransfer,
        TplColdChainLog,
        TplReturnAuthorization,
        TplCarrierRate,
        TplOrderNode,
        TplDamageClaim,
    )
    __all__.extend(["TplDockAppointment", "TplLoadingPlan", "TplShipmentManifest", "TplInventoryTransfer", "TplColdChainLog", "TplReturnAuthorization", "TplCarrierRate", "TplOrderNode", "TplDamageClaim"])
except Exception:
    pass
# </expansion:log3pl_b>

# <expansion:fluvial_b>
try:
    from app.models.fluvial_b_deep import (
        FluvialCanalSection,
        FluvialConvoy,
        FluvialBallastOperation,
        FluvialWaterGauge,
        FluvialBerthingSlot,
        FluvialCrewRoster,
        FluvialCargoManifest,
        FluvialPortFee,
        FluvialVesselInspection,
    )
    __all__.extend(["FluvialCanalSection", "FluvialConvoy", "FluvialBallastOperation", "FluvialWaterGauge", "FluvialBerthingSlot", "FluvialCrewRoster", "FluvialCargoManifest", "FluvialPortFee", "FluvialVesselInspection"])
except Exception:
    pass
# </expansion:fluvial_b>

# <expansion:aerien_b>
try:
    from app.models.aerien_b_deep import (
        HouseAirWaybill,
        PerishableCargo,
        LiveAnimalShipment,
        CharteredFlight,
        AirCustomsClearance,
        ApronMovement,
        NoiseComplianceRecord,
    )
    __all__.extend(["HouseAirWaybill", "PerishableCargo", "LiveAnimalShipment", "CharteredFlight", "AirCustomsClearance", "ApronMovement", "NoiseComplianceRecord"])
except Exception:
    pass
# </expansion:aerien_b>

# <expansion:ferroviaire_b>
try:
    from app.models.ferroviaire_b_deep import (
        RailWheelSet,
        RailLoadingGauge,
        RailShuntingPlan,
        RailTrainConsist,
        RailPathOccupancy,
        RailWagonDispatch,
        RailTerminalCrane,
    )
    __all__.extend(["RailWheelSet", "RailLoadingGauge", "RailShuntingPlan", "RailTrainConsist", "RailPathOccupancy", "RailWagonDispatch", "RailTerminalCrane"])
except Exception:
    pass
# </expansion:ferroviaire_b>

# <expansion:parc_b>
try:
    from app.models.parc_b_deep import (
        ParcDriverAssignment,
        ParcGeofenceZone,
        ParcInspectionChecklist,
        ParcLeaseContract,
        ParcTollPass,
    )
    __all__.extend(["ParcDriverAssignment", "ParcGeofenceZone", "ParcInspectionChecklist", "ParcLeaseContract", "ParcTollPass"])
except Exception:
    pass
# </expansion:parc_b>

# <expansion:qhse_b>
try:
    from app.models.qhse_b_deep import (
        QhseNearMiss,
        QhseCalibration,
        QhseWasteManifest,
        QhseTrainingRecord,
        QhseWorkPermit,
    )
    __all__.extend(["QhseNearMiss", "QhseCalibration", "QhseWasteManifest", "QhseTrainingRecord", "QhseWorkPermit"])
except Exception:
    pass
# </expansion:qhse_b>

# <expansion:pipeline>
try:
    from app.models.pipeline_deep import (
        PipelineSection,
        PipelinePumpStation,
        PipelineStorageTank,
        PipelineMeteringPoint,
        PipelineProductBatch,
        PipelinePressureReading,
        PipelineLeakDetection,
        PipelineMaintenanceWork,
        PipelineInjectionCampaign,
        PipelineShipNomination,
    )
    __all__.extend(["PipelineSection", "PipelinePumpStation", "PipelineStorageTank", "PipelineMeteringPoint", "PipelineProductBatch", "PipelinePressureReading", "PipelineLeakDetection", "PipelineMaintenanceWork", "PipelineInjectionCampaign", "PipelineShipNomination"])
except Exception:
    pass
# </expansion:pipeline>

# <expansion:courier>
try:
    from app.models.courier_deep import (
        CourierParcel,
        CourierWaybill,
        CourierHub,
        CourierDeliveryZone,
        CourierRoute,
        CourierCourier,
        CourierPod,
        CourierSla,
        CourierLocker,
        CourierVehicule,
        CourierTarif,
        CourierException,
    )
    __all__.extend(["CourierParcel", "CourierWaybill", "CourierHub", "CourierDeliveryZone", "CourierRoute", "CourierCourier", "CourierPod", "CourierSla", "CourierLocker", "CourierVehicule", "CourierTarif", "CourierException"])
except Exception:
    pass
# </expansion:courier>

# <expansion:coldchain>
try:
    from app.models.coldchain_deep import (
        ColdChainChamber,
        ColdChainReefer,
        ColdChainLogger,
        ColdChainProduct,
        ColdChainExcursion,
        ColdChainVaccinBatch,
        ColdChainHaccpRecord,
        ColdChainDefrostCycle,
        ColdChainEnergyMeter,
        ColdChainTransportLeg,
    )
    __all__.extend(["ColdChainChamber", "ColdChainReefer", "ColdChainLogger", "ColdChainProduct", "ColdChainExcursion", "ColdChainVaccinBatch", "ColdChainHaccpRecord", "ColdChainDefrostCycle", "ColdChainEnergyMeter", "ColdChainTransportLeg"])
except Exception:
    pass
# </expansion:coldchain>

# <expansion:heavylift>
try:
    from app.models.heavylift_deep import (
        HeavyLiftProject,
        HeavyLiftCrane,
        HeavyLiftModularTrailer,
        HeavyLiftRouteSurvey,
        HeavyLiftLiftPlan,
        HeavyLiftPermit,
        HeavyLiftEscort,
        HeavyLiftLashing,
        HeavyLiftBallast,
        HeavyLiftRiggingMethod,
    )
    __all__.extend(["HeavyLiftProject", "HeavyLiftCrane", "HeavyLiftModularTrailer", "HeavyLiftRouteSurvey", "HeavyLiftLiftPlan", "HeavyLiftPermit", "HeavyLiftEscort", "HeavyLiftLashing", "HeavyLiftBallast", "HeavyLiftRiggingMethod"])
except Exception:
    pass
# </expansion:heavylift>

# <expansion:port_ops_b>
try:
    from app.models.port_ops_b_deep import (
        PortbBerthSchedule,
        PortbVesselTrafficLog,
    )
    __all__.extend(["PortbBerthSchedule", "PortbVesselTrafficLog"])
except Exception:
    pass
# </expansion:port_ops_b>

# <expansion:amenagement_b>
try:
    from app.models.amenagement_b_deep import (
        AmgtbDredgingProject,
        AmgtbConcessionPlot,
    )
    __all__.extend(["AmgtbDredgingProject", "AmgtbConcessionPlot"])
except Exception:
    pass
# </expansion:amenagement_b>

# <expansion:transit_b>
try:
    from app.models.transit_b_deep import (
        TransitbIncoterm,
        TransitbInspectionRecord,
    )
    __all__.extend(["TransitbIncoterm", "TransitbInspectionRecord"])
except Exception:
    pass
# </expansion:transit_b>

# <expansion:transport_b>
try:
    from app.models.transport_b_deep import (
        TransportbDispatch,
        TransportbPod,
    )
    __all__.extend(["TransportbDispatch", "TransportbPod"])
except Exception:
    pass
# </expansion:transport_b>

# <expansion:magasin_b>
try:
    from app.models.magasin_b_deep import (
        MagasinbStockCount,
        MagasinbGoodsReceipt,
    )
    __all__.extend(["MagasinbStockCount", "MagasinbGoodsReceipt"])
except Exception:
    pass
# </expansion:magasin_b>

# <expansion:dashboard_b>
try:
    from app.models.dashboard_b_deep import (
        DashboardbOperationalKpi,
        DashboardbScorecard,
        DashboardbAlertRule,
        DashboardbRefreshJob,
        DashboardbSavedView,
    )
    __all__.extend(["DashboardbOperationalKpi", "DashboardbScorecard", "DashboardbAlertRule", "DashboardbRefreshJob", "DashboardbSavedView"])
except Exception:
    pass
# </expansion:dashboard_b>

# <expansion:compta_c>
try:
    from app.models.compta_c_deep import (
        CmptcJournalReversal,
        CmptcBankReconciliation,
    )
    __all__.extend(["CmptcJournalReversal", "CmptcBankReconciliation"])
except Exception:
    pass
# </expansion:compta_c>

# <expansion:finance_c>
try:
    from app.models.finance_c_deep import (
        FincCashFlowForecast,
        FincInvoiceFinancing,
    )
    __all__.extend(["FincCashFlowForecast", "FincInvoiceFinancing"])
except Exception:
    pass
# </expansion:finance_c>

# <expansion:rh_c>
try:
    from app.models.rh_c_deep import (
        RhCTrainingPlan,
        RhCDisciplinaryRecord,
    )
    __all__.extend(["RhCTrainingPlan", "RhCDisciplinaryRecord"])
except Exception:
    pass
# </expansion:rh_c>

# <expansion:b2b_c>
try:
    from app.models.b2b_c_deep import (
        B2bCContractAgreement,
        B2bCPriceList,
        B2bCSalesOrder,
        B2bCCreditAccount,
        B2bCSupportTicket,
    )
    __all__.extend(["B2bCContractAgreement", "B2bCPriceList", "B2bCSalesOrder", "B2bCCreditAccount", "B2bCSupportTicket"])
except Exception:
    pass
# </expansion:b2b_c>

# <expansion:reports_c>
try:
    from app.models.reports_c_deep import (
        RptcScheduledReport,
        RptcReportTemplate,
        RptcDataExport,
        RptcAdHocQuery,
        RptcOlapCube,
    )
    __all__.extend(["RptcScheduledReport", "RptcReportTemplate", "RptcDataExport", "RptcAdHocQuery", "RptcOlapCube"])
except Exception:
    pass
# </expansion:reports_c>

# <expansion:admin_c>
try:
    from app.models.admin_c_deep import (
        AdmCSubscriptionPlan,
        AdmCTenantInvite,
        AdmCApiToken,
        AdmCBillingInvoice,
        AdmCUsageMetering,
    )
    __all__.extend(["AdmCSubscriptionPlan", "AdmCTenantInvite", "AdmCApiToken", "AdmCBillingInvoice", "AdmCUsageMetering"])
except Exception:
    pass
# </expansion:admin_c>

# <expansion:superadmin_c>
try:
    from app.models.superadmin_c_deep import (
        SaCAuditLogReview,
        SaCSystemParameter,
        SaCPlatformAlert,
        SaCMigrationRun,
        SaCLicenseKey,
    )
    __all__.extend(["SaCAuditLogReview", "SaCSystemParameter", "SaCPlatformAlert", "SaCMigrationRun", "SaCLicenseKey"])
except Exception:
    pass
# </expansion:superadmin_c>

# <expansion:admin_tenant_c>
try:
    from app.models.admin_tenant_c_deep import (
        AdmtDomainConfig,
        AdmtDnsRecord,
        AdmtDataResidency,
        AdmtFeatureEntitlement,
        AdmtUsageQuota,
        AdmtImpersonationLog,
        AdmtOnboardingStep,
        AdmtWhiteLabelConfig,
        AdmtTenantBackup,
        AdmtIntegrationWebhook,
    )
    __all__.extend(["AdmtDomainConfig", "AdmtDnsRecord", "AdmtDataResidency", "AdmtFeatureEntitlement", "AdmtUsageQuota", "AdmtImpersonationLog", "AdmtOnboardingStep", "AdmtWhiteLabelConfig", "AdmtTenantBackup", "AdmtIntegrationWebhook"])
except Exception:
    pass
# </expansion:admin_tenant_c>

# <expansion:chauffeur_c>
try:
    from app.models.chauffeur_c_deep import (
        ChfTripSheet,
        ChfDailyVehicleCheck,
        ChfFuelLog,
        ChfDrivingTimeRecord,
        ChfRestBreak,
        ChfTollReceipt,
        ChfParkingSession,
        ChfCargoSeal,
        ChfRoadsideIncident,
        ChfDeliveryStop,
        ChfMileageLog,
        ChfLoadSecuringCheck,
        ChfBorderCrossing,
        ChfDeliveryAppointment,
        ChfPpeIssue,
        ChfShiftHandover,
        ChfBreakdownReport,
        ChfTyreCheck,
        ChfCargoPhoto,
    )
    __all__.extend(["ChfTripSheet", "ChfDailyVehicleCheck", "ChfFuelLog", "ChfDrivingTimeRecord", "ChfRestBreak", "ChfTollReceipt", "ChfParkingSession", "ChfCargoSeal", "ChfRoadsideIncident", "ChfDeliveryStop", "ChfMileageLog", "ChfLoadSecuringCheck", "ChfBorderCrossing", "ChfDeliveryAppointment", "ChfPpeIssue", "ChfShiftHandover", "ChfBreakdownReport", "ChfTyreCheck", "ChfCargoPhoto"])
except Exception:
    pass
# </expansion:chauffeur_c>

# <expansion:magasinier_c>
try:
    from app.models.magasinier_c_deep import (
        MagcPickingTask,
        MagcPackingSlip,
        MagcPutawayTask,
        MagcCycleCount,
        MagcInternalMove,
        MagcGoodsIssue,
        MagcReturnProcessing,
        MagcLabelPrint,
        MagcPalletBuild,
        MagcEquipmentCheck,
        MagcSafetyInspection,
        MagcSpillCleanup,
        MagcLoadingCheck,
        MagcReceivingCheck,
        MagcPutawayException,
        MagcOrderStaging,
        MagcColdChainCheck,
        MagcHazmatHandling,
        MagcDockAssignment,
    )
    __all__.extend(["MagcPickingTask", "MagcPackingSlip", "MagcPutawayTask", "MagcCycleCount", "MagcInternalMove", "MagcGoodsIssue", "MagcReturnProcessing", "MagcLabelPrint", "MagcPalletBuild", "MagcEquipmentCheck", "MagcSafetyInspection", "MagcSpillCleanup", "MagcLoadingCheck", "MagcReceivingCheck", "MagcPutawayException", "MagcOrderStaging", "MagcColdChainCheck", "MagcHazmatHandling", "MagcDockAssignment"])
except Exception:
    pass
# </expansion:magasinier_c>
