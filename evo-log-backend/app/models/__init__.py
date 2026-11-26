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
# Departement Amenagement portuaire: enregistre les tables du domaine public
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

# surfaces auparavant stubs 501 / succes fabrique, desormais persistees.
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

# operations portuaires approfondies (12 entites).
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

# transit-douane approfondi (12 entites).
try:
    from app.models import transit_deep as _transit_deep  # noqa: F401
except Exception:
    pass

# <:transport>
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
# </transport>

# <:magasin>
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
# </magasin>

# <:comptabilite>
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
# </comptabilite>

# <:finance>
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
# </finance>

# <:parc>
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
# </parc>

# <:rh>
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
# </rh>

# <:qhse>
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
# </qhse>

# <:b2b>
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
# </b2b>

# <:reports>
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
# </reports>


# <:superadmin>
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
# </superadmin>

# <:dashboard>
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
# </dashboard>

# <:amenagement_extra>
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
# </amenagement_extra>

# <:admin>
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
# </admin>

# <:ferroviaire>
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
# </ferroviaire>

# <:aerien>
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
# </aerien>

# <:fluvial>
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
# </fluvial>

# <:log3pl>
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
# </log3pl>

# <:log3pl_b>
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
# </log3pl_b>

# <:fluvial_b>
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
# </fluvial_b>

# <:aerien_b>
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
# </aerien_b>

# <:ferroviaire_b>
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
# </ferroviaire_b>

# <:parc_b>
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
# </parc_b>

# <:qhse_b>
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
# </qhse_b>

# <:pipeline>
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
# </pipeline>

# <:courier>
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
# </courier>

# <:coldchain>
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
# </coldchain>

# <:heavylift>
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
# </heavylift>

# <:port_ops_b>
try:
    from app.models.port_ops_b_deep import (
        PortbBerthSchedule,
        PortbVesselTrafficLog,
    )
    __all__.extend(["PortbBerthSchedule", "PortbVesselTrafficLog"])
except Exception:
    pass
# </port_ops_b>

# <:amenagement_b>
try:
    from app.models.amenagement_b_deep import (
        AmgtbDredgingProject,
        AmgtbConcessionPlot,
    )
    __all__.extend(["AmgtbDredgingProject", "AmgtbConcessionPlot"])
except Exception:
    pass
# </amenagement_b>

# <:transit_b>
try:
    from app.models.transit_b_deep import (
        TransitbIncoterm,
        TransitbInspectionRecord,
    )
    __all__.extend(["TransitbIncoterm", "TransitbInspectionRecord"])
except Exception:
    pass
# </transit_b>

# <:transport_b>
try:
    from app.models.transport_b_deep import (
        TransportbDispatch,
        TransportbPod,
    )
    __all__.extend(["TransportbDispatch", "TransportbPod"])
except Exception:
    pass
# </transport_b>

# <:magasin_b>
try:
    from app.models.magasin_b_deep import (
        MagasinbStockCount,
        MagasinbGoodsReceipt,
    )
    __all__.extend(["MagasinbStockCount", "MagasinbGoodsReceipt"])
except Exception:
    pass
# </magasin_b>

# <:dashboard_b>
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
# </dashboard_b>

# <:compta_c>
try:
    from app.models.compta_c_deep import (
        CmptcJournalReversal,
        CmptcBankReconciliation,
    )
    __all__.extend(["CmptcJournalReversal", "CmptcBankReconciliation"])
except Exception:
    pass
# </compta_c>

# <:finance_c>
try:
    from app.models.finance_c_deep import (
        FincCashFlowForecast,
        FincInvoiceFinancing,
    )
    __all__.extend(["FincCashFlowForecast", "FincInvoiceFinancing"])
except Exception:
    pass
# </finance_c>

# <:rh_c>
try:
    from app.models.rh_c_deep import (
        RhCTrainingPlan,
        RhCDisciplinaryRecord,
    )
    __all__.extend(["RhCTrainingPlan", "RhCDisciplinaryRecord"])
except Exception:
    pass
# </rh_c>

# <:b2b_c>
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
# </b2b_c>

# <:reports_c>
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
# </reports_c>

# <:admin_c>
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
# </admin_c>

# <:superadmin_c>
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
# </superadmin_c>

# <:admin_tenant_c>
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
# </admin_tenant_c>

# <:chauffeur_c>
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
# </chauffeur_c>

# <:magasinier_c>
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
# </magasinier_c>

# <:technicien_d>
try:
    from app.models.technicien_d_deep import (
        TechWorkOrder,
        TechInterventionSheet,
        TechDiagnosis,
        TechPartConsumption,
        TechPreventivePlan,
        TechBreakdownTicket,
        TechRepairReport,
        TechCalibrationRecord,
        TechEquipmentChecklist,
        TechToolLoan,
        TechSafetyLockout,
        TechWarrantyClaim,
        TechServiceAppointment,
        TechLaborTimesheet,
        TechUpgradeRequest,
        TechFailureAnalysis,
        TechSpareRequest,
        TechInspectionRecord,
        TechWorkOrderCost,
    )
    __all__.extend(["TechWorkOrder", "TechInterventionSheet", "TechDiagnosis", "TechPartConsumption", "TechPreventivePlan", "TechBreakdownTicket", "TechRepairReport", "TechCalibrationRecord", "TechEquipmentChecklist", "TechToolLoan", "TechSafetyLockout", "TechWarrantyClaim", "TechServiceAppointment", "TechLaborTimesheet", "TechUpgradeRequest", "TechFailureAnalysis", "TechSpareRequest", "TechInspectionRecord", "TechWorkOrderCost"])
except Exception:
    pass
# </technicien_d>

# <:qhse_portal_d>
try:
    from app.models.qhse_portal_d_deep import (
        QspHazardReport,
        QspNearMiss,
        QspSafetyObservation,
        QspPpeAttestation,
        QspToolboxTalk,
        QspWorkPermitRequest,
        QspSafetyTrainingLog,
        QspExposureRecord,
        QspFirstAidLog,
        QspSafetySuggestion,
        QspStopWorkAuthority,
        QspSpillReport,
        QspMsdsAck,
        QspErgonomicsAssessment,
        QspHygieneCheck,
        QspInspectionFinding,
        QspCapaReply,
        QspRiskAssessmentInput,
        QspEvacuationDrill,
    )
    __all__.extend(["QspHazardReport", "QspNearMiss", "QspSafetyObservation", "QspPpeAttestation", "QspToolboxTalk", "QspWorkPermitRequest", "QspSafetyTrainingLog", "QspExposureRecord", "QspFirstAidLog", "QspSafetySuggestion", "QspStopWorkAuthority", "QspSpillReport", "QspMsdsAck", "QspErgonomicsAssessment", "QspHygieneCheck", "QspInspectionFinding", "QspCapaReply", "QspRiskAssessmentInput", "QspEvacuationDrill"])
except Exception:
    pass
# </qhse_portal_d>

# <:declarant_d>
try:
    from app.models.declarant_d_deep import (
        DeclCustomsDeclaration,
        DeclHsClassification,
        DeclOriginCertificate,
        DeclCustomsValuation,
        DeclIncotermsRecord,
        DeclImportLicense,
        DeclExportLicense,
        DeclPreClearance,
        DeclCustomsInvoice,
        DeclPackingList,
        DeclCertificateAnalysis,
        DeclPhytosanitaryApp,
        DeclCustomsPayment,
        DeclTransitDocument,
        DeclDangerousGoods,
        DeclBondedWarehouseEntry,
        DeclDutyReliefClaim,
        DeclManifestCorrection,
        DeclCustomsAuditSupport,
    )
    __all__.extend(["DeclCustomsDeclaration", "DeclHsClassification", "DeclOriginCertificate", "DeclCustomsValuation", "DeclIncotermsRecord", "DeclImportLicense", "DeclExportLicense", "DeclPreClearance", "DeclCustomsInvoice", "DeclPackingList", "DeclCertificateAnalysis", "DeclPhytosanitaryApp", "DeclCustomsPayment", "DeclTransitDocument", "DeclDangerousGoods", "DeclBondedWarehouseEntry", "DeclDutyReliefClaim", "DeclManifestCorrection", "DeclCustomsAuditSupport"])
except Exception:
    pass
# </declarant_d>

# <:commercial_d>
try:
    from app.models.commercial_d_deep import (
        CommLead,
        CommOpportunity,
        CommQuote,
        CommSalesOrder,
        CommCustomerVisit,
        CommSampleRequest,
        CommTender,
        CommContractRenewal,
        CommPriceRequest,
        CommCreditRequest,
        CommOrderModification,
        CommCustomerComplaint,
        CommUpsellRecord,
        CommCommissionStatement,
        CommPipelineReview,
    )
    __all__.extend(["CommLead", "CommOpportunity", "CommQuote", "CommSalesOrder", "CommCustomerVisit", "CommSampleRequest", "CommTender", "CommContractRenewal", "CommPriceRequest", "CommCreditRequest", "CommOrderModification", "CommCustomerComplaint", "CommUpsellRecord", "CommCommissionStatement", "CommPipelineReview"])
except Exception:
    pass
# </commercial_d>

# <:commercial_d2>
try:
    from app.models.commercial_d2_deep import (
        CommCompetitorNote,
    )
    __all__.extend(["CommCompetitorNote"])
except Exception:
    pass
# </commercial_d2>

# <:employe_d>
try:
    from app.models.employe_d_deep import (
        EmpLeaveRequest,
        EmpTimesheetEntry,
        EmpOvertimeRequest,
        EmpAttendanceCorrection,
        EmpShiftSwap,
        EmpTrainingEnrollment,
        EmpSkillDeclaration,
        EmpCertificationRenewal,
        EmpPersonalInfoChange,
        EmpBankDetailsUpdate,
        EmpEmergencyContact,
        EmpBadgeRequest,
        EmpAccessRequest,
        EmpDocumentUpload,
        EmpSelfReview,
        EmpMobilityApplication,
        EmpSicknessDeclaration,
    )
    __all__.extend(["EmpLeaveRequest", "EmpTimesheetEntry", "EmpOvertimeRequest", "EmpAttendanceCorrection", "EmpShiftSwap", "EmpTrainingEnrollment", "EmpSkillDeclaration", "EmpCertificationRenewal", "EmpPersonalInfoChange", "EmpBankDetailsUpdate", "EmpEmergencyContact", "EmpBadgeRequest", "EmpAccessRequest", "EmpDocumentUpload", "EmpSelfReview", "EmpMobilityApplication", "EmpSicknessDeclaration"])
except Exception:
    pass
# </employe_d>

# <:chef_personnel_d>
try:
    from app.models.chef_personnel_d_deep import (
        ChpRecruitmentCampaign,
        ChpJobPosting,
        ChpCandidateSelection,
        ChpInterviewSchedule,
        ChpOfferApproval,
        ChpOnboardingChecklist,
        ChpProbationReview,
        ChpExitInterview,
        ChpHeadcountRequest,
        ChpOrgMovement,
        ChpDisciplinaryAction,
        ChpTrainingPlan,
        ChpAbsenceApproval,
        ChpPayrollAdjustmentRequest,
        ChpPolicyAck,
    )
    __all__.extend(["ChpRecruitmentCampaign", "ChpJobPosting", "ChpCandidateSelection", "ChpInterviewSchedule", "ChpOfferApproval", "ChpOnboardingChecklist", "ChpProbationReview", "ChpExitInterview", "ChpHeadcountRequest", "ChpOrgMovement", "ChpDisciplinaryAction", "ChpTrainingPlan", "ChpAbsenceApproval", "ChpPayrollAdjustmentRequest", "ChpPolicyAck"])
except Exception:
    pass
# </chef_personnel_d>

# <:frais_d>
try:
    from app.models.frais_d_deep import (
        FraExpenseReport,
        FraExpenseReceipt,
        FraExpenseAdvance,
        FraPerDiemClaim,
        FraMileageClaim,
        FraMealExpense,
        FraTravelBooking,
        FraHotelStay,
        FraTransportExpense,
        FraClientEntertainment,
        FraConferenceFee,
        FraOfficeSupply,
        FraCardTransaction,
        FraCurrencyConversion,
        FraExpenseApproval,
        FraExpenseDispute,
        FraVatRecovery,
        FraExpenseBudgetTracking,
        FraExpenseCategory,
    )
    __all__.extend(["FraExpenseReport", "FraExpenseReceipt", "FraExpenseAdvance", "FraPerDiemClaim", "FraMileageClaim", "FraMealExpense", "FraTravelBooking", "FraHotelStay", "FraTransportExpense", "FraClientEntertainment", "FraConferenceFee", "FraOfficeSupply", "FraCardTransaction", "FraCurrencyConversion", "FraExpenseApproval", "FraExpenseDispute", "FraVatRecovery", "FraExpenseBudgetTracking", "FraExpenseCategory"])
except Exception:
    pass
# </frais_d>

# <:annuaire_d>
try:
    from app.models.annuaire_d_deep import (
        ProvProfile,
        ProvCategory,
        ProvCertification,
        ProvInsuranceAttestation,
        ProvServiceContract,
        ProvEvaluation,
        ProvIncident,
        ProvAvailabilityCalendar,
        ProvPriceList,
        ProvContact,
        ProvOnboarding,
        ProvReview,
        ProvRfqRequest,
        ProvIntervention,
        ProvComplianceDoc,
        ProvBankDetail,
        ProvBlacklist,
    )
    __all__.extend(["ProvProfile", "ProvCategory", "ProvCertification", "ProvInsuranceAttestation", "ProvServiceContract", "ProvEvaluation", "ProvIncident", "ProvAvailabilityCalendar", "ProvPriceList", "ProvContact", "ProvOnboarding", "ProvReview", "ProvRfqRequest", "ProvIntervention", "ProvComplianceDoc", "ProvBankDetail", "ProvBlacklist"])
except Exception:
    pass
# </annuaire_d>

# <:collaborateur_d>
try:
    from app.models.collaborateur_d_deep import (
        CollAssignment,
        CollActivityLog,
        CollDeliverable,
        CollTimesheet,
        CollSiteAccessLog,
        CollWorkInstructionReceipt,
        CollIncidentReport,
        CollQualityCheck,
        CollTrainingCompletion,
        CollEquipmentIssue,
        CollShiftAttendance,
        CollTravelOrder,
        CollExpenseDeclaration,
        CollCertificationUpload,
        CollTaskCompletion,
        CollFeedback,
        CollAvailability,
        CollContractRenewalRequest,
        CollDocumentRequest,
    )
    __all__.extend(["CollAssignment", "CollActivityLog", "CollDeliverable", "CollTimesheet", "CollSiteAccessLog", "CollWorkInstructionReceipt", "CollIncidentReport", "CollQualityCheck", "CollTrainingCompletion", "CollEquipmentIssue", "CollShiftAttendance", "CollTravelOrder", "CollExpenseDeclaration", "CollCertificationUpload", "CollTaskCompletion", "CollFeedback", "CollAvailability", "CollContractRenewalRequest", "CollDocumentRequest"])
except Exception:
    pass
# </collaborateur_d>

# <:maintenance_deep>
# maintenance industrielle experte (FMEA / RCM / TPM, MTBF/MTTR/OEE,
# singleton piece de rechange serialisee, chaine de cote BOM, predictif).
try:
    from app.models.maintenance_deep import (
        TechnicalAsset,
        AssetComponent,
        SparePartCatalog,
        BillOfMaterial,
        SerializedPart,
        PartInventory,
        PartMovement,
        FailureMode,
        MaintenancePlan,
        MaintenanceTask,
        WorkOrder,
        AssetFailure,
        WorkOrderPart,
        WorkOrderLabour,
        WorkOrderTool,
        RootCauseAnalysis,
        OverhaulCampaign,
        LubricationSchedule,
        ConditionReading,
        Sensor,
        PredictiveModel,
        ReliabilityKpi,
        RegulatoryInspection,
        MaintenanceBudget,
        MaintenanceVendor,
    )
    __all__.extend(["TechnicalAsset", "AssetComponent", "SparePartCatalog", "BillOfMaterial", "SerializedPart", "PartInventory", "PartMovement", "FailureMode", "MaintenancePlan", "MaintenanceTask", "WorkOrder", "AssetFailure", "WorkOrderPart", "WorkOrderLabour", "WorkOrderTool", "RootCauseAnalysis", "OverhaulCampaign", "LubricationSchedule", "ConditionReading", "Sensor", "PredictiveModel", "ReliabilityKpi", "RegulatoryInspection", "MaintenanceBudget", "MaintenanceVendor"])
except Exception:
    pass
# </maintenance_deep>

# <:tracabilite_deep>
# tracaibilite bout-en-bout (chaine de custody, Merkle / hash chain,
# sceau ISO 17712, horodatage qualifie eIDAS/CAMPOST, RGPD + loi Cameroun
# 2010/041, anti-falsification, rétention légale OGIC/CGI).
try:
    from app.models.tracabilite_deep import (
        TraceabilityEvent,
        ChainOfCustodyTransfer,
        BatchGenealogy,
        SerialGenealogy,
        DocumentHash,
        GeolocationTrace,
        ColdChainTrace,
        IncidentChainOfCommand,
        RegulatoryTraceExport,
        ImmutableAuditLog,
        TimestampAuthority,
        WitnessSignature,
        IntegrityMerkleProof,
        ContainerSeal,
        CargoHandoff,
        AccessSecurityLog,
        ConsentGrant,
        AntiTamperingEvent,
        RetentionPolicy,
    )
    __all__.extend(["TraceabilityEvent", "ChainOfCustodyTransfer", "BatchGenealogy", "SerialGenealogy", "DocumentHash", "GeolocationTrace", "ColdChainTrace", "IncidentChainOfCommand", "RegulatoryTraceExport", "ImmutableAuditLog", "TimestampAuthority", "WitnessSignature", "IntegrityMerkleProof", "ContainerSeal", "CargoHandoff", "AccessSecurityLog", "ConsentGrant", "AntiTamperingEvent", "RetentionPolicy"])
except Exception:
    pass
# </tracabilite_deep>

# <:pipeline_e>
try:
    from app.models.pipeline_e_deep import (
        Pipe2CustodyTransfer,
        Pipe2PressureLog,
        Pipe2PumpStationRead,
        Pipe2CorrosionReading,
        Pipe2FlowCalibration,
        Pipe2BatchQualityTest,
        Pipe2InterfaceDetection,
        Pipe2IntegrityAssessment,
        Pipe2SpillResponseAction,
    )
    __all__.extend(["Pipe2CustodyTransfer", "Pipe2PressureLog", "Pipe2PumpStationRead", "Pipe2CorrosionReading", "Pipe2FlowCalibration", "Pipe2BatchQualityTest", "Pipe2InterfaceDetection", "Pipe2IntegrityAssessment", "Pipe2SpillResponseAction"])
except Exception:
    pass
# </pipeline_e>

# <:courier_e>
try:
    from app.models.courier_e_deep import (
        Cour2RouteScan,
        Cour2LastMileHandoff,
        Cour2DeliveryAttempt,
        Cour2ExceptionParcel,
        Cour2ReturnToSender,
        Cour2CourierShiftLog,
        Cour2SlaBreachLog,
    )
    __all__.extend(["Cour2RouteScan", "Cour2LastMileHandoff", "Cour2DeliveryAttempt", "Cour2ExceptionParcel", "Cour2ReturnToSender", "Cour2CourierShiftLog", "Cour2SlaBreachLog"])
except Exception:
    pass
# </courier_e>

# <:coldchain_e>
try:
    from app.models.coldchain_e_deep import (
        Cold2TemperatureLog,
        Cold2ColdExcursion,
        Cold2ProbeCalibration,
        Cold2BlastFreezeCycle,
        Cold2DoorOpenEvent,
        Cold2HumidityLog,
        Cold2RefrigerantCharge,
        Cold2ShipmentApproval,
        Cold2IceBatteryCharge,
    )
    __all__.extend(["Cold2TemperatureLog", "Cold2ColdExcursion", "Cold2ProbeCalibration", "Cold2BlastFreezeCycle", "Cold2DoorOpenEvent", "Cold2HumidityLog", "Cold2RefrigerantCharge", "Cold2ShipmentApproval", "Cold2IceBatteryCharge"])
except Exception:
    pass
# </coldchain_e>

# <:heavylift_e>
try:
    from app.models.heavylift_e_deep import (
        Heavy2LiftPlan,
        Heavy2RouteSurvey,
        Heavy2EscortSchedule,
        Heavy2LoadMomentCalc,
        Heavy2CraneSetupRecord,
        Heavy2PermitObtention,
        Heavy2LashingRig,
        Heavy2AxleLoadReading,
        Heavy2ConvoyStagingReport,
    )
    __all__.extend(["Heavy2LiftPlan", "Heavy2RouteSurvey", "Heavy2EscortSchedule", "Heavy2LoadMomentCalc", "Heavy2CraneSetupRecord", "Heavy2PermitObtention", "Heavy2LashingRig", "Heavy2AxleLoadReading", "Heavy2ConvoyStagingReport"])
except Exception:
    pass
# </heavylift_e>

# <:chat_d5>
try:
    from app.models.chat_d5_deep import (
        ChtAnnouncement,
        ChtChannel,
        ChtContentReport,
    )
    __all__.extend(["ChtAnnouncement", "ChtChannel", "ChtContentReport"])
except Exception:
    pass
# </chat_d5>

# <:departement_d5>
try:
    from app.models.departement_d5_deep import (
        DepObjective,
        DepServiceMeeting,
        DepProject,
        DepServiceRequest,
    )
    __all__.extend(["DepObjective", "DepServiceMeeting", "DepProject", "DepServiceRequest"])
except Exception:
    pass
# </departement_d5>
