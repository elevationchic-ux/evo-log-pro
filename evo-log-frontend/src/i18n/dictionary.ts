export type AppLanguage = 'fr' | 'en'

export type Dictionary = {
  home: {
    welcomeTitle: string
    welcomeSubtitle: string
    loadingSystem: string
    platformLoading: string
  }
  auth: {
    systemAuthenticationTitle: string
    systemAuthenticationSubtitle: string
    emailInstitutionalLabel: string
    passwordLabel: string
    forgotPassword: string
    rememberMeLabel: string
    loginCta: string
    loginVerifying: string
    createAccount: string
    alreadyAccount: string
    mfaSecuredLabel: string
    auditAccessLabel: string
    forgotTitle: string
    forgotSubtitle: string
    forgotCta: string
    forgotSending: string
    forgotSuccessTitle: string
    forgotSuccessBody: string
    forgotSpamNote: string
    backToLogin: string
    registerTitle: string
    registerSubtitle: string
    firstNameLabel: string
    lastNameLabel: string
    departmentLabel: string
    departmentPlaceholder: string
    passwordStrengthLabel: string
    termsLabel: string
    termsLink: string
    registerCta: string
    registerLoading: string
    resetTitle: string
    resetSubtitle: string
    newPasswordLabel: string
    confirmPasswordLabel: string
    resetCta: string
    resetLoading: string
    sessionExpiredTitle: string
    sessionExpiredBody: string
    sessionExpiredInfo: string
    reconnectCta: string
    notifTitle: string
    notifEmpty: string
    notifMarkAll: string
    notifClearRead: string
    sessionModalTitle: string
    sessionModalBody: string
    sessionModalCta: string
  }
  errors: {
    accessDeniedTitle: string
    accessDeniedMessage: string
    returnToMySpace: string
    serverErrorTitle: string
    serverErrorMessage: string
    tryAgain: string
    backToHome: string
    helpPersists: string
    notFoundTitle: string
    notFoundMessage: string
    previousPage: string
    help: string
    confidentialFooter: string
    forbiddenTitle: string
    forbiddenMessage: string
    backHome: string
    previousPage2: string
  }
  /** Labels communs partagés par toutes les pages */
  common: {
    loading: string
    loadingData: string
    search: string
    searchPlaceholder: string
    filter: string
    export: string
    add: string
    edit: string
    delete: string
    view: string
    close: string
    cancel: string
    save: string
    confirm: string
    refresh: string
    back: string
    noData: string
    noResults: string
    noResultsFor: string
    tryOtherTerm: string
    showing: string
    of: string
    results: string
    result: string
    actions: string
    status: string
    date: string
    name: string
    description: string
    amount: string
    total: string
    details: string
    recordDetail: string
    fullDataView: string
    dataUpToDate: string
    redirecting: string
    allOperationsNormal: string
    new: string
    unknown: string
    unassigned: string
    page: string
    perPage: string
  }
  /** Module Dashboard global */
  dashboard: {
    title: string
    subtitle: string
    systemOverview: string
    criticalAlerts: string
    stockValue: string
    pendingMissions: string
    totalRevenue: string
    activeVehicles: string
    moduleKMagasin: string
    moduleKAudit: string
    moduleKFinance: string
    moduleKTransport: string
    alertsNormal: string
  }
  /** Module Transport */
  transport: {
    title: string
    subtitle: string
    missionControl: string
    fleetStatus: string
    realTimeOverview: string
    activeMissions: string
    nextDeliveries: string
    today: string
    onRoad: string
    available: string
    maintenance: string
    viewAllSchedule: string
    liveMapView: string
    trackingTrucks: string
    filterById: string
    noDeliveries: string
    noMissions: string
    missionId: string
    driver: string
    route: string
    vehicle: string
    statusInTransit: string
    statusLoading: string
    statusDelivered: string
    statusMaintenance: string
    destination: string
    client: string
    unspecifiedDestination: string
    internalClient: string
    filterBtn: string
    refreshBtn: string
  }
  /** Module Finance */
  finance: {
    title: string
    subtitle: string
    overview: string
    analytics: string
    billing: string
    reconciliation: string
    transactions: string
    gateway: string
    revenue: string
    expenses: string
    balance: string
    invoices: string
    pending: string
    paid: string
    overdue: string
  }
  /** Module Magasin */
  magasin: {
    title: string
    subtitle: string
    stock: string
    reception: string
    inventory: string
    removal: string
    articles: string
    clients: string
    orders: string
    declarations: string
    transactions: string
    movements: string
    capacity: string
    history: string
    lowStock: string
    inStock: string
    outOfStock: string
  }
  /** Module Admin */
  admin: {
    title: string
    subtitle: string
    userManagement: string
    roles: string
    permissions: string
    systemHealth: string
    auditTrails: string
    mfaConfig: string
    users: string
    activeUsers: string
    lastLogin: string
    role: string
    department: string
  }
  /** Module Parc */
  parc: {
    title: string
    subtitle: string
    terminal: string
    gateInOut: string
    inventory: string
    movements: string
    zoneManagement: string
    overview: string
    newZone: string
    zoneDetails: string
    capacity: string
  }
  /** Module Audit */
  audit: {
    title: string
    subtitle: string
    health: string
    operationTrace: string
    securityAlerts: string
    notifications: string
    reports: string
    settings: string
  }
}

export const DICTIONARIES: Record<AppLanguage, Dictionary> = {
  fr: {
    home: {
      welcomeTitle: 'Bienvenue sur EVO-LOG',
      welcomeSubtitle: "La plateforme d'entreprise premium pour la gestion logistique.",
      loadingSystem: 'Chargement du système...',
      platformLoading: 'Chargement du système...'
    },
    auth: {
      systemAuthenticationTitle: 'System Authentication',
      systemAuthenticationSubtitle: 'Entrez vos identifiants pour accéder au terminal.',
      emailInstitutionalLabel: 'Email Institutionnel',
      passwordLabel: 'Mot de passe',
      forgotPassword: 'Mot de passe oublié?',
      rememberMeLabel: 'Rester connecté 12 heures',
      loginCta: 'Se connecter',
      loginVerifying: 'Vérification...',
      createAccount: 'Créer un compte',
      alreadyAccount: 'Déjà un compte ?',
      mfaSecuredLabel: 'Sécurisé par EM-ERP Multi-Factor Authentication',
      auditAccessLabel: "Accès surveillé par le Module Audit. Personnel autorisé uniquement.",
      forgotTitle: 'Mot de passe oublié ?',
      forgotSubtitle: 'Entrez votre email, nous vous enverrons un lien de réinitialisation.',
      forgotCta: 'Envoyer le lien',
      forgotSending: 'Envoi en cours...',
      forgotSuccessTitle: 'Email envoyé !',
      forgotSuccessBody: 'Un lien de réinitialisation a été envoyé à',
      forgotSpamNote: 'Vérifiez aussi vos spams. Le lien expire dans 30 minutes.',
      backToLogin: 'Retour à la connexion',
      registerTitle: 'Créer un compte',
      registerSubtitle: 'Accédez aux modules opérationnels EVO-LOG',
      firstNameLabel: 'Prénom',
      lastNameLabel: 'Nom',
      departmentLabel: "Département d'affectation",
      departmentPlaceholder: 'Sélectionner un département',
      passwordStrengthLabel: 'Sécurité',
      termsLabel: "J'accepte les",
      termsLink: "conditions d'utilisation",
      registerCta: "Finaliser l'inscription",
      registerLoading: 'Inscription en cours...',
      resetTitle: 'Nouveau mot de passe',
      resetSubtitle: 'Choisissez un mot de passe sécurisé pour votre compte.',
      newPasswordLabel: 'Nouveau mot de passe',
      confirmPasswordLabel: 'Confirmer le mot de passe',
      resetCta: 'Réinitialiser le mot de passe',
      resetLoading: 'Réinitialisation...',
      sessionExpiredTitle: 'Session expirée',
      sessionExpiredBody: 'Votre session a expiré pour des raisons de sécurité. Veuillez vous reconnecter pour continuer.',
      sessionExpiredInfo: 'Vos données non sauvegardées ont été perdues. Reconnectez-vous pour reprendre votre travail.',
      reconnectCta: 'Se reconnecter',
      notifTitle: 'Historique Alertes',
      notifEmpty: 'Aucune notification',
      notifMarkAll: 'Tout marquer lu',
      notifClearRead: 'Effacer les lus',
      sessionModalTitle: 'Session Expirée',
      sessionModalBody: 'Votre session a expiré pour des raisons de sécurité. Veuillez vous reconnecter.',
      sessionModalCta: 'Se reconnecter'
    },
    errors: {
      accessDeniedTitle: 'Accès Refusé',
      accessDeniedMessage: "Votre profil ({roles}) ne vous permet pas d'accéder à ce module.",
      returnToMySpace: 'Retourner à mon espace',
      serverErrorTitle: 'Erreur serveur',
      serverErrorMessage: "Une erreur inattendue s'est produite. Nos équipes ont été notifiées.",
      tryAgain: 'Réessayer',
      backToHome: "Retour à l'accueil",
      helpPersists: 'Le problème persiste ? ',
      notFoundTitle: 'Page non trouvée',
      notFoundMessage: "La page que vous recherchez n'existe pas ou a été déplacée.",
      previousPage: 'Page précédente',
      help: "Besoin d'aide ? ",
      confidentialFooter: '© 2026 CADC - EVO-LOG SaaS • Confidentiel',
      forbiddenTitle: 'Accès refusé',
      forbiddenMessage: "Vous n'avez pas les permissions nécessaires pour accéder à cette ressource.",
      backHome: "Retour à l'accueil",
      previousPage2: 'Page précédente'
    },
    common: {
      loading: 'Chargement...',
      loadingData: 'Chargement des données...',
      search: 'Rechercher',
      searchPlaceholder: 'Rechercher dans toutes les colonnes...',
      filter: 'Filtres',
      export: 'Exporter',
      add: 'Ajouter',
      edit: 'Modifier',
      delete: 'Supprimer',
      view: 'Voir',
      close: 'Fermer',
      cancel: 'Annuler',
      save: 'Enregistrer',
      confirm: 'Confirmer',
      refresh: 'Actualiser',
      back: 'Retour',
      noData: 'Aucune donnée disponible pour le moment.',
      noResults: 'Aucun résultat trouvé',
      noResultsFor: 'Aucun résultat pour «\u202f',
      tryOtherTerm: '\u202f». Essayez un autre terme.',
      showing: 'Affichage de',
      of: 'sur',
      results: 'résultats',
      result: 'résultat',
      actions: 'Actions',
      status: 'Statut',
      date: 'Date',
      name: 'Nom',
      description: 'Description',
      amount: 'Montant',
      total: 'Total',
      details: 'Détails',
      recordDetail: "Détail de l'enregistrement",
      fullDataView: 'Vue complète des données',
      dataUpToDate: 'Données à jour',
      redirecting: 'Redirection vers votre espace...',
      allOperationsNormal: 'Toutes les opérations sont normales. Aucune alerte critique.',
      new: 'Nouveau',
      unknown: 'Inconnu',
      unassigned: 'Non assigné',
      page: 'Page',
      perPage: 'par page',
    },
    dashboard: {
      title: 'Vue d\'ensemble',
      subtitle: 'Tableau de bord global du système EVO-LOG',
      systemOverview: 'System Overview',
      criticalAlerts: 'Alertes Critiques',
      stockValue: 'Valeur du Stock',
      pendingMissions: 'Missions en attente',
      totalRevenue: 'Chiffre d\'affaires',
      activeVehicles: 'Véhicules actifs',
      moduleKMagasin: 'K-Magasin',
      moduleKAudit: 'K-Audit',
      moduleKFinance: 'K-Finance',
      moduleKTransport: 'K-Transport',
      alertsNormal: 'Toutes les opérations sont normales. Aucune alerte critique pour le moment.',
    },
    transport: {
      title: 'K-Transport',
      subtitle: 'Centre de contrôle Transport & Flotte',
      missionControl: 'Mission Control',
      fleetStatus: 'État de la Flotte',
      realTimeOverview: 'Vue en temps réel',
      activeMissions: 'Missions Actives',
      nextDeliveries: 'Prochaines Livraisons',
      today: 'AUJOURD\'HUI',
      onRoad: 'En route',
      available: 'Disponible',
      maintenance: 'Maintenance',
      viewAllSchedule: 'Voir tout le planning',
      liveMapView: 'Carte en direct',
      trackingTrucks: 'Suivi de 25 camions actifs',
      filterById: 'Filtrer par ID...',
      noDeliveries: 'Aucune livraison en cours',
      noMissions: 'Aucune mission active.',
      missionId: 'Mission ID',
      driver: 'Chauffeur',
      route: 'Itinéraire',
      vehicle: 'Véhicule',
      statusInTransit: 'EN TRANSIT',
      statusLoading: 'CHARGEMENT',
      statusDelivered: 'LIVRÉ',
      statusMaintenance: 'MAINTENANCE',
      destination: 'Destination',
      client: 'Client',
      unspecifiedDestination: 'Destination non spécifiée',
      internalClient: 'Interne',
      filterBtn: 'Filtres',
      refreshBtn: 'Actualiser',
    },
    finance: {
      title: 'K-Finance',
      subtitle: 'Comptabilité & Gestion financière',
      overview: 'Tableau de bord financier',
      analytics: 'Analytique & Cashflow',
      billing: 'Facturation',
      reconciliation: 'Rapprochement bancaire',
      transactions: 'Saisie de transaction',
      gateway: 'Passerelle de paiement',
      revenue: 'Revenus',
      expenses: 'Dépenses',
      balance: 'Solde',
      invoices: 'Factures',
      pending: 'En attente',
      paid: 'Payé',
      overdue: 'En retard',
    },
    magasin: {
      title: 'K-Magasin',
      subtitle: 'Gestion de l\'entrepôt & des stocks',
      stock: 'Gestion des stocks',
      reception: 'Réceptions',
      inventory: 'Inventaire physique',
      removal: 'Bons d\'enlèvement',
      articles: 'Articles',
      clients: 'Clients',
      orders: 'Commandes',
      declarations: 'Déclarations (BL)',
      transactions: 'Transactions',
      movements: 'Mouvements de stock',
      capacity: 'Capacité magasin',
      history: 'Historique',
      lowStock: 'Stock faible',
      inStock: 'En stock',
      outOfStock: 'Rupture de stock',
    },
    admin: {
      title: 'Administration',
      subtitle: 'Gestion des utilisateurs, rôles et sécurité',
      userManagement: 'Gestion des utilisateurs',
      roles: 'Rôles',
      permissions: 'Permissions',
      systemHealth: 'Santé système',
      auditTrails: 'Traces d\'audit',
      mfaConfig: 'Configuration MFA',
      users: 'Utilisateurs',
      activeUsers: 'Utilisateurs actifs',
      lastLogin: 'Dernière connexion',
      role: 'Rôle',
      department: 'Département',
    },
    parc: {
      title: 'K-Parc',
      subtitle: 'Gestion du terminal, zones, conteneurs et mouvements',
      terminal: 'Terminal & Zones',
      gateInOut: 'Entrées / Sorties (Gate)',
      inventory: 'Stock Parc',
      movements: 'Mouvements & Historique',
      zoneManagement: 'Gestion des Zones',
      overview: 'Vue Globale du Parc',
      newZone: 'Nouvelle Zone',
      zoneDetails: 'Détails de la Zone',
      capacity: 'Capacité',
    },
    audit: {
      title: 'K-Audit',
      subtitle: 'Surveillance, sécurité & conformité',
      health: 'Santé système',
      operationTrace: 'Traces d\'opérations',
      securityAlerts: 'Alertes sécurité',
      notifications: 'Notifications',
      reports: 'Rapports',
      settings: 'Paramètres audit',
    },
  },

  en: {
    home: {
      welcomeTitle: 'Welcome to EVO-LOG',
      welcomeSubtitle: 'The premium enterprise platform for logistics management.',
      loadingSystem: 'Loading system...',
      platformLoading: 'Loading system...'
    },
    auth: {
      systemAuthenticationTitle: 'System Authentication',
      systemAuthenticationSubtitle: 'Enter your credentials to access the terminal.',
      emailInstitutionalLabel: 'Institutional Email',
      passwordLabel: 'Password',
      forgotPassword: 'Forgot password?',
      rememberMeLabel: 'Stay connected for 12 hours',
      loginCta: 'Sign in',
      loginVerifying: 'Verifying...',
      createAccount: 'Create an account',
      alreadyAccount: 'Already have an account?',
      mfaSecuredLabel: 'Secured by EM-ERP Multi-Factor Authentication',
      auditAccessLabel: 'Access monitored by the Audit Module. Authorized staff only.',
      forgotTitle: 'Forgot password?',
      forgotSubtitle: 'Enter your email and we will send you a reset link.',
      forgotCta: 'Send reset link',
      forgotSending: 'Sending...',
      forgotSuccessTitle: 'Email sent!',
      forgotSuccessBody: 'A reset link has been sent to',
      forgotSpamNote: 'Check your spam folder. The link expires in 30 minutes.',
      backToLogin: 'Back to login',
      registerTitle: 'Create an account',
      registerSubtitle: 'Access EVO-LOG operational modules',
      firstNameLabel: 'First name',
      lastNameLabel: 'Last name',
      departmentLabel: 'Department',
      departmentPlaceholder: 'Select a department',
      passwordStrengthLabel: 'Strength',
      termsLabel: 'I accept the',
      termsLink: 'terms of use',
      registerCta: 'Complete registration',
      registerLoading: 'Registering...',
      resetTitle: 'New password',
      resetSubtitle: 'Choose a secure password for your account.',
      newPasswordLabel: 'New password',
      confirmPasswordLabel: 'Confirm password',
      resetCta: 'Reset password',
      resetLoading: 'Resetting...',
      sessionExpiredTitle: 'Session expired',
      sessionExpiredBody: 'Your session has expired for security reasons. Please sign in again to continue.',
      sessionExpiredInfo: 'Unsaved data has been lost. Sign in again to resume your work.',
      reconnectCta: 'Sign in again',
      notifTitle: 'Alert History',
      notifEmpty: 'No notifications',
      notifMarkAll: 'Mark all as read',
      notifClearRead: 'Clear read',
      sessionModalTitle: 'Session Expired',
      sessionModalBody: 'Your session has expired for security reasons. Please sign in again.',
      sessionModalCta: 'Sign in again'
    },
    errors: {
      accessDeniedTitle: 'Access Denied',
      accessDeniedMessage: 'Your profile ({roles}) does not allow access to this module.',
      returnToMySpace: 'Go to my space',
      serverErrorTitle: 'Server error',
      serverErrorMessage: 'An unexpected error occurred. Our team has been notified.',
      tryAgain: 'Try again',
      backToHome: 'Back to home',
      helpPersists: 'The issue persists? ',
      notFoundTitle: 'Page not found',
      notFoundMessage: 'The page you are looking for does not exist or has been moved.',
      previousPage: 'Previous page',
      help: "Need help? ",
      confidentialFooter: '© 2026 CADC - EVO-LOG SaaS • Confidential',
      forbiddenTitle: 'Access refused',
      forbiddenMessage: 'You do not have the required permissions to access this resource.',
      backHome: 'Back to home',
      previousPage2: 'Previous page'
    },
    common: {
      loading: 'Loading...',
      loadingData: 'Loading data...',
      search: 'Search',
      searchPlaceholder: 'Search across all columns...',
      filter: 'Filters',
      export: 'Export',
      add: 'Add',
      edit: 'Edit',
      delete: 'Delete',
      view: 'View',
      close: 'Close',
      cancel: 'Cancel',
      save: 'Save',
      confirm: 'Confirm',
      refresh: 'Refresh',
      back: 'Back',
      noData: 'No data available at the moment.',
      noResults: 'No results found',
      noResultsFor: 'No results for "',
      tryOtherTerm: '". Try a different search term.',
      showing: 'Showing',
      of: 'of',
      results: 'results',
      result: 'result',
      actions: 'Actions',
      status: 'Status',
      date: 'Date',
      name: 'Name',
      description: 'Description',
      amount: 'Amount',
      total: 'Total',
      details: 'Details',
      recordDetail: 'Record Detail',
      fullDataView: 'Full data view',
      dataUpToDate: 'Data up to date',
      redirecting: 'Redirecting to your workspace...',
      allOperationsNormal: 'All operations are normal. No critical alerts at this time.',
      new: 'New',
      unknown: 'Unknown',
      unassigned: 'Unassigned',
      page: 'Page',
      perPage: 'per page',
    },
    dashboard: {
      title: 'Overview',
      subtitle: 'EVO-LOG system global dashboard',
      systemOverview: 'System Overview',
      criticalAlerts: 'Critical Alerts',
      stockValue: 'Stock Value',
      pendingMissions: 'Pending Missions',
      totalRevenue: 'Total Revenue',
      activeVehicles: 'Active Vehicles',
      moduleKMagasin: 'K-Magasin',
      moduleKAudit: 'K-Audit',
      moduleKFinance: 'K-Finance',
      moduleKTransport: 'K-Transport',
      alertsNormal: 'All operations are normal. No critical alerts at this time.',
    },
    transport: {
      title: 'K-Transport',
      subtitle: 'Transport & Fleet Operations Center',
      missionControl: 'Mission Control',
      fleetStatus: 'Fleet Status',
      realTimeOverview: 'Real-time overview',
      activeMissions: 'Active Missions',
      nextDeliveries: 'Next Deliveries',
      today: 'TODAY',
      onRoad: 'On Road',
      available: 'Available',
      maintenance: 'Maintenance',
      viewAllSchedule: 'View All Schedule',
      liveMapView: 'Live Map View',
      trackingTrucks: 'Tracking 25 Active Trucks',
      filterById: 'Filter ID...',
      noDeliveries: 'No ongoing deliveries',
      noMissions: 'No active missions.',
      missionId: 'Mission ID',
      driver: 'Driver',
      route: 'Route',
      vehicle: 'Vehicle',
      statusInTransit: 'IN TRANSIT',
      statusLoading: 'LOADING',
      statusDelivered: 'DELIVERED',
      statusMaintenance: 'MAINTENANCE',
      destination: 'Destination',
      client: 'Client',
      unspecifiedDestination: 'Destination not specified',
      internalClient: 'Internal',
      filterBtn: 'Filters',
      refreshBtn: 'Refresh',
    },
    finance: {
      title: 'K-Finance',
      subtitle: 'Accounting & Financial management',
      overview: 'Financial Dashboard',
      analytics: 'Analytics & Cashflow',
      billing: 'Billing',
      reconciliation: 'Bank Reconciliation',
      transactions: 'Transaction Entry',
      gateway: 'Payment Gateway',
      revenue: 'Revenue',
      expenses: 'Expenses',
      balance: 'Balance',
      invoices: 'Invoices',
      pending: 'Pending',
      paid: 'Paid',
      overdue: 'Overdue',
    },
    magasin: {
      title: 'K-Magasin',
      subtitle: 'Warehouse & Inventory Management',
      stock: 'Stock Management',
      reception: 'Receptions',
      inventory: 'Physical Inventory',
      removal: 'Removal Slips',
      articles: 'Articles',
      clients: 'Clients',
      orders: 'Orders',
      declarations: 'Declarations (BL)',
      transactions: 'Transactions',
      movements: 'Stock Movements',
      capacity: 'Warehouse Capacity',
      history: 'History',
      lowStock: 'Low Stock',
      inStock: 'In Stock',
      outOfStock: 'Out of Stock',
    },
    admin: {
      title: 'Administration',
      subtitle: 'User management, roles & security',
      userManagement: 'User Management',
      roles: 'Roles',
      permissions: 'Permissions',
      systemHealth: 'System Health',
      auditTrails: 'Audit Trails',
      mfaConfig: 'MFA Configuration',
      users: 'Users',
      activeUsers: 'Active Users',
      lastLogin: 'Last Login',
      role: 'Role',
      department: 'Department',
    },
    parc: {
      title: 'K-Parc',
      subtitle: 'Terminal management, zones, containers and movements',
      terminal: 'Terminal & Zones',
      gateInOut: 'Gate In / Out',
      inventory: 'Yard Inventory',
      movements: 'Movements & History',
      zoneManagement: 'Zone Management',
      overview: 'Yard Overview',
      newZone: 'New Zone',
      zoneDetails: 'Zone Details',
      capacity: 'Capacity',
    },
    audit: {
      title: 'K-Audit',
      subtitle: 'Monitoring, security & compliance',
      health: 'System Health',
      operationTrace: 'Operation Traces',
      securityAlerts: 'Security Alerts',
      notifications: 'Notifications',
      reports: 'Reports',
      settings: 'Audit Settings',
    },
  }
}
