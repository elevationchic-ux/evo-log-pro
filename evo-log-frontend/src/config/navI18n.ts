// src/config/navI18n.ts
// Source de vérité pour la traduction FR/EN des TITRES DE MODULES de navigation.
// Le français reste la valeur d'origine dans NAVIGATION_REGISTRY (champ `title`).
// L'anglais est attaché au moment du chargement de la registry (boucle de
// normalisation) puis résolu au rendu selon la langue active via `localizeTitle`.

export const MODULE_TITLES_EN: Record<string, string> = {
  dashboard: 'ERP Global Overview',
  'port-operations': '🚢 Port & Quayside Operations',
  'transit-douane': '🛃 Transit & Customs CEMAC',
  'transport-flotte': '🚛 K-Transport & Fleet TMS',
  'magasin-stock': '📦 K-Warehouse WMS & Stock',
  'comptabilite-ohada': '📚 OHADA Accounting (Sage)',
  'finance-ohada': '💰 K-Finance & Treasury',
  'parc-vehicules': '🚗 K-Vehicle Fleet & CMMS',
  'rh-personnel': '👥 Human Resources & Payroll',
  'qhse-securite': '🛡️ K-QHSE & Port Safety',
  // Département autonome : l'aménagement (domaine public, schémas, gros œuvre)
  // se distingue nettement de l'exploitation du quai.
  'amenagement-portuaire': '📐 Port Development & Public Domain',
  'client-b2b': '🤝 B2B Client Portal & CRM',
  'reports-bi': '📊 K-Executive BI Analytics',
  'admin-saas': '👑 SaaS Platform Governance',
  'admin-tenant': '🏢 Enterprise Administration',
  chat: '💬 Enterprise Chat & Forum',
  'portail-employe': '👤 My Employee Space (HR)',
  'portail-collaborateur': '🧭 Collaborator Hub',
  'portail-chauffeur': '🚚 Driver & Route Space',
  'portail-frais': '💼 Expenses & Mission Advances',
  'portail-magasinier': '📦 Warehouseman & Quayside Space',
  'portail-technicien': '🔧 CMMS Technician Space',
  'portail-declarant': '🏛️ Customs Declarant Space',
  'portail-qhse': '🦺 Safety & QHSE Watch',
  'portail-commercial': '🤝 Sales & Quotations Space',
  'annuaire-prestataires': 'Providers & Subcontractors Directory',
  'chef-personnel': 'Head of Personnel (N+1 Passive Roles)',
  'transport-ferroviaire': 'Rail Freight & Infrastructure',
  'transport-aerien': 'Air Cargo & Airport Ops',
  'transport-fluvial': 'River & Lake Transport',
  'logistique-3pl': 'Contract Logistics 3PL',
};

export type Localizable = { title: string; titleEn?: string };

// Sobriété ERP : les titres de modules sont rendus avec leur ICÔNE LUCIDE
// dédiée ; les emoji en tête de titre (🚢 📦 👑 …) sont donc retirés à
// l'affichage (source de vérité unique pour toutes les surfaces : sidebar,
// en-tête, bulle orbitale, menus). La règle couvre pictogrammes, sélecteur de
// variation (U+FE0F), ZWJ (U+200D) et espaces qui les accompagnent.
const LEADING_EMOJI =
  /^[\u{1F000}-\u{1FAFF}\u{2600}-\u{27BF}\u{2B00}-\u{2BFF}\u{FE0F}\u{200D}\u{20E3}\s]+/u;

/** Retire les emoji et espaces en tête d'un libellé (rendu sobre). */
export function stripLeadingEmoji(value: string): string {
  return value.replace(LEADING_EMOJI, '').trimStart();
}

/** Retourne le titre anglais si disponible et langue === 'en', sinon le français. */
export function localizeTitle(item: Localizable, lang: 'fr' | 'en'): string {
  const raw = lang === 'en' && item.titleEn ? item.titleEn : item.title;
  return stripLeadingEmoji(raw);
}

// Source de vérité pour la traduction FR/EN des LIBELLES DE SOUS-MODULES.
// Clé = libellé français exact tel que déclaré dans NAVIGATION_REGISTRY
// (champ `label` des subModules). Toute clé absente retombe gracieusement sur
// le français : aucune page ne peut se retrouver vide/morte.
export const SUBMODULE_LABELS_EN: Record<string, string> = {
  'Abonnements & Licences Globales': 'Subscriptions & Global Licenses',
  'Accréditations & Habilitations': 'Accreditations & Clearances',
  'Agences & Sites Opérationnels': 'Agencies & Operational Sites',
  'Alertes & Incidents Live': 'Live Alerts & Incidents',
  'Analytics Opérationnels WMS & Transport': 'WMS & Transport Operational Analytics',
  'Annuaire & Dossiers Employés': 'Employee Directory & Records',
  'Annuaire Prestataires Certifiés': 'Certified Providers Directory',
  'Bon à Enlever (BAE) & Mainlevée': 'Delivery Order (BAE) & Release',
  'Bulletins de Paie OHADA Cameroun': 'OHADA Pay Slips (Cameroon)',
  'Carburant & FuelGuard Télémétrie': 'Fuel & FuelGuard Telemetry',
  'Cartes Grises, Assurances & Conformité': 'Registration, Insurance & Compliance',
  'Centre Dédouanement & Statuts': 'Customs Clearance Center & Statuses',
  'Centre de Sécurité & Alertes': 'Security & Alerts Center',
  'Clôtures Mensuelle & Annuelle': 'Monthly & Annual Closing',
  'Collaborateurs & Attribution des Rôles': 'Staff & Role Assignment',
  'Conformité & Agréments Portuaires': 'Compliance & Port Approvals',
  'Conformité & Licences Import/Export': 'Compliance & Import/Export Licenses',
  'Congés, Absences & Temps de Travail': 'Leave, Absence & Time Tracking',
  'Consommations, Coûts & TCO': 'Consumption, Costs & TCO',
  'Control Tower & Live Map': 'Control Tower & Live Map',
  'Control Tower Maritime': 'Maritime Control Tower',
  'Control Tower Transport': 'Transport Control Tower',
  'Dashboard Comptable OHADA': 'OHADA Accounting Dashboard',
  'Dashboard Ressources Humaines': 'Human Resources Dashboard',
  'Dashboard WMS Central': 'Central WMS Dashboard',
  'Demandes de Congés & Absences': 'Leave & Absence Requests',
  'Demandes de Cotations (RFQ)': 'Requests for Quotation (RFQ)',
  'Dettes Fournisseurs & Achats': 'Supplier Debts & Purchases',
  'Documents & Attestations RH': 'HR Documents & Certificates',
  'Dossiers & Visite Douane': 'Customs Files & Inspection',
  'Dossiers Transit CEMAC (Corridor)': 'CEMAC Transit Files (Corridor)',
  'Dotations EPI & Matériel': 'PPE & Equipment Issue',
  'Déclarations DUM & Sydonia': 'DUM & Sydonia Declarations',
  'Déclarations Sociales (CNPS & DIPE)': 'Social Declarations (CNPS & DIPE)',
  'Emplacements & Slots WMS': 'WMS Locations & Slots',
  'Espace Client B2B Central': 'Central B2B Client Space',
  'Espaces Communs par Entreprise': 'Shared Workspaces by Company',
  'Executive Dashboard Direction': 'Executive Management Dashboard',
  'Facturation & Émission Client': 'Client Billing & Issuance',
  'Factures, Règlements & Avoirs': 'Invoices, Payments & Credit Notes',
  'Fiscalité Cameroun & Règlements Locaux': 'Cameroon Taxation & Local Regulations',
  'Flotte Camions & Tracteurs': 'Trucks & Tractors Fleet',
  'Formations & Habilitations Sécurité': 'Safety Training & Certifications',
  'Gestion des Chauffeurs': 'Driver Management',
  'Grand Forum d Entreprise': 'Company Grand Forum',
  'Grand Livre & Balances': 'General Ledger & Balances',
  'Générateur de Rapports Personnalisés': 'Custom Report Generator',
  'Indicateurs Clés BI': 'Key BI Indicators',
  'Infrastructure, Quotas & API Gateway': 'Infrastructure, Quotas & API Gateway',
  'Inspections Portuaires & Norme ISPS': 'Port Inspections & ISPS Code',
  'Intégration Portuaire Douala/Kribi': 'Douala/Kribi Port Integration',
  'Inventaires Physiques & Écarts': 'Physical Counts & Discrepancies',
  'Journal d Audit de l Entreprise': 'Company Audit Journal',
  'Journaux Auxiliaires & Saisie': 'Subsidiary Journals & Data Entry',
  'Liasse Fiscale & Déclarations CEMAC': 'Tax Package & CEMAC Declarations',
  'Logs d Audit & Sécurité Plateforme': 'Audit Logs & Platform Security',
  'Ma Tournée & Missions': 'My Route & Missions',
  'Maintenance Préventive & Échéances': 'Preventive Maintenance & Deadlines',
  'Manifestes & Escales Navires': 'Ship Manifests & Port Calls',
  'Mes Bulletins de Paie OHADA': 'My OHADA Pay Slips',
  'Mes Expéditions & Tracking Live': 'My Shipments & Live Tracking',
  'Mes Notes de Frais': 'My Expense Reports',
  'Messages Directs (1-à-1)': 'Direct Messages (1-on-1)',
  'Missions & Dispatch Intelligent': 'Missions & Smart Dispatch',
  'Mouvements & Transferts de Stock': 'Stock Movements & Transfers',
  'Opérations de Quai & Acconage': 'Dockside & Stevedoring Operations',
  'Ordres de Travail & Réparations': 'Work Orders & Repairs',
  'Ordres de Travail (OT)': 'Work Orders (WO)',
  'Paramètres & Préférences Locales': 'Settings & Local Preferences',
  'Picking & Dépotage Quai': 'Picking & Dock Devanning',
  'Plan Comptable SYSCOHADA': 'SYSCOHADA Chart of Accounts',
  'Planning Accostage & Postes': 'Berthing & Berth Planning',
  'Plannings & Gardes 24/7': 'Schedules & 24/7 Shifts',
  'Pointages & Vacations de Nuit': 'Night Shift & Attendance Tracking',
  'Processus Navire → Client': 'Ship → Client Process',
  'Préparation Commandes & Picking': 'Order Picking & Preparation',
  'Rapports Financiers & Rentabilité': 'Financial Reports & Profitability',
  'Recouvrement & Créances Clients': 'Collections & Client Receivables',
  'Registre Incidents & Signalements': 'Incident & Reporting Register',
  'Réception & Entrées Magasin': 'Receiving & Warehouse Entries',
  'Réception & Entrées MAG3': 'Receiving & Warehouse Entries (MAG3)',
  'Rôles & Permissions Granulaires': 'Roles & Granular Permissions',
  'Service Client, Litiges & Tickets': 'Customer Service, Disputes & Tickets',
  'Signalement Flash Danger': 'Flash Hazard Report',
  'Simulateur Cotation CEMAC': 'CEMAC Quotation Simulator',
  'Chiffrage sur Grille Tarifaire': 'Pricing from the Tariff Grid',
  'Grille Tarifaire d Exploitation': 'Operating Tariff Grid',
  'Devis Émis & Décisions': 'Issued Quotes & Decisions',
  'Portefeuille Clients & Encours': 'Client Portfolio & Balances',
  'Statistiques Trafic Maritime': 'Maritime Traffic Statistics',
  'Supervision des Effectifs N+1': 'N+1 Workforce Supervision',
  'Supervision des Entreprises & Tenants': 'Company & Tenant Supervision',
  'Tableau de Bord Entreprise': 'Company Dashboard',
  'Tableau de Bord Parc & Atelier': 'Fleet & Workshop Dashboard',
  'Tableau de Bord Trésorerie': 'Treasury Dashboard',
  'Trésorerie, Banques & Caisses': 'Treasury, Banks & Cash',
  'Taxation & Droits Cameroun': 'Cameroon Taxation & Duties',
  'Tous les Portails Métier': 'All Business Portals',
  'Tracking GPS & e-POD Signatures': 'GPS Tracking & e-POD Signatures',
  'Validation Congés & Absences N+1': 'N+1 Leave & Absence Approval',
  "Vue d'Ensemble Executive": 'Executive Overview',
  'États Financiers (Bilan, CR, TAFIRE)': 'Financial Statements (Balance Sheet, P&L, TAFIRE)',
  // Département aménagement portuaire (libellés exacts du registre de navigation)
  'Centre de Pilotage Aménagement': 'Port Development Command Center',
  'Schémas Directeurs & Périmètres': 'Master Plans & Port Perimeters',
  "Projets d'Aménagement": 'Development Projects Portfolio',
  'Programmation & Maturité (PIP/CDMT)': 'Programming & Maturity (PIP/CDMT)',
  'Marchés Publics & PPP': 'Public Contracts & PPPs',
  'Titres Domaniaux & Occupations': 'State Land Titles & Occupations',
  'Concessions & Contrats d\'Exploitation': 'Concessions & Operation Contracts',
  'Inventaire des Infrastructures': 'Infrastructure Inventory',
  'Dragage & Profondeurs Disponibles': 'Dredging & Available Depths',
  'Autorisations Administratives (EIES)': 'Administrative Permits (EIES)',
};

/** Retourne le libellé anglais du sous-module si langue === 'en', sinon le français. */
export function localizeSubLabel(label: string, lang: 'fr' | 'en'): string {
  if (lang === 'en' && SUBMODULE_LABELS_EN[label]) return SUBMODULE_LABELS_EN[label];
  return label;
}
