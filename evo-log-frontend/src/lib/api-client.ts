// src/lib/api-client.ts  Client API TypeScript EVO-LOG
import axios, { AxiosInstance, InternalAxiosRequestConfig } from 'axios';

let BASE_URL = process.env.NEXT_PUBLIC_API_URL || 'https://backend-production-83b1.up.railway.app';
if (process.env.NODE_ENV === 'production' && BASE_URL.includes('localhost')) {
  BASE_URL = 'https://backend-production-83b1.up.railway.app';
}

export const apiClient: AxiosInstance = axios.create({
  baseURL: BASE_URL,
  headers: { 'Content-Type': 'application/json' },
  timeout: 15000,
  withCredentials: true,
});

// Token storage: set by AuthProvider after login
let _authToken: string | null = null;

export function setAuthToken(token: string | null) {
  _authToken = token;
}

// Intercepteur REQUEST - inject Bearer token from NextAuth session
apiClient.interceptors.request.use(
  (config: InternalAxiosRequestConfig) => {
    if (_authToken && !config.headers['Authorization']) {
      config.headers['Authorization'] = `Bearer ${_authToken}`;
    }
    // Auto-rewrite /api/... to /api/v1/... if needed
    if (config.url && config.url.startsWith('/api/') && !config.url.startsWith('/api/v1/') && !config.url.startsWith('/api/docs') && !config.url.startsWith('/api/health')) {
      config.url = config.url.replace(/^\/api\//, '/api/v1/');
    }
    return config;
  },
  (error) => Promise.reject(error)
);

// Intercepteur RESPONSE
// IMPORTANT: Ne déclencher le logout automatique QUE pour les endpoints d'auth,
// PAS pour les appels de données (dashboard, magasin, etc.) qui peuvent retourner 401
// quand le backend distant est temporairement indisponible.
apiClient.interceptors.response.use(
  (response) => response,
  (error) => {
    if (error.response?.status === 401) {
      const url = error.config?.url || '';
      const isAuthEndpoint = url.includes('/auth/me') || url.includes('/auth/refresh');
      if (typeof window !== 'undefined' && isAuthEndpoint) {
        window.dispatchEvent(new CustomEvent('auth-error', { detail: { reason: 'unauthorized' } }));
      }
    }
    return Promise.reject(error);
  }
);


// ─── Service Admin ──────────────────────────────────────────────────────────
export const adminAPI = {
  getUsers: (params?: Record<string, unknown>) => apiClient.get('/api/admin/users', { params }),
  createUser: (data: any) => apiClient.post('/api/admin/users', data),
  updateUser: (id: number, data: any) => apiClient.put(`/api/admin/users/${id}`, data),
  toggleUserStatus: (id: number, data?: any) => apiClient.patch(`/api/admin/users/${id}/status`, data),
  resetPassword: (id: number, new_password?: string) => apiClient.post(`/api/admin/users/${id}/reset-password`, { new_password }),
  getRoles: () => apiClient.get('/api/admin/roles'),
  createRole: (data: any) => apiClient.post('/api/admin/roles', data),
  getAuditLogs: (params?: Record<string, unknown>) => apiClient.get('/api/admin/audit-logs', { params }),
  getAgencies: (params?: Record<string, unknown>) => apiClient.get('/api/admin/agencies', { params }),
  createAgency: (data: unknown) => apiClient.post('/api/admin/agencies', data),
  updateAgency: (id: number, data: unknown) => apiClient.put(`/api/admin/agencies/${id}`, data),
  deleteAgency: (id: number) => apiClient.delete(`/api/admin/agencies/${id}`),
  getDashboardKpis: () => apiClient.get('/api/admin/dashboard/global-kpis'),
  getSystemHealth: () => apiClient.get('/api/admin/system-health'),
};

// ─── Service Auth & Sécurité Compte ──────────────────────────────────────────
export const authAPI = {
  login: (data: { username: string; password: string }) =>
    apiClient.post('/api/auth/login', data),
  logout: () => apiClient.post('/api/auth/logout'),
  register: (data: unknown) =>
    apiClient.post('/api/auth/register', data),
  getMe: () =>
    apiClient.get('/api/auth/me'),
  changePassword: (data: { current_password?: string; new_password: string; user_id?: number }) =>
    apiClient.post('/api/v1/auth/change-password', data),
  toggle2FA: (enabled: boolean) =>
    apiClient.post('/api/v1/auth/2fa/toggle', { enabled }),
  revokeSessions: () =>
    apiClient.post('/api/v1/auth/revoke-sessions'),
};

// ─── Service Sécurité & Escalade ──────────────────────────────────────────
export const securityAPI = {
  getEscalationRules: () => apiClient.get('/api/v1/security/escalation-rules'),
  saveEscalationRules: (data: any) => apiClient.post('/api/v1/security/escalation-rules', data),
};


// â”€â”€â”€ Service Transport â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€
export const transportAPI = {
  getMissions: (params?: Record<string, unknown>) =>
    apiClient.get('/api/transport/missions', { params }),
  getMission: (id: number) =>
    apiClient.get(`/api/transport/missions/${id}`),
  createMission: (data: unknown) =>
    apiClient.post('/api/transport/missions', data),
  updateStatut: (id: number, statut: string) =>
    apiClient.patch(`/api/transport/missions/${id}/statut`, { statut }),
  demarrerMission: (id: number) =>
    apiClient.post(`/api/transport/missions/${id}/demarrer`),
  livrerMission: (id: any, dataOrSignature: any, nom_receptionnaire?: string) =>
    apiClient.post(`/api/transport/missions/${id}/livrer`, typeof dataOrSignature === 'string' ? { signature: dataOrSignature, nom_receptionnaire } : dataOrSignature),
  getCamions: (params?: Record<string, unknown>) =>
    apiClient.get('/api/transport/camions', { params }),
  createCamion: (data: unknown) =>
    apiClient.post('/api/transport/camions', data),
  getChauffeurs: (params?: Record<string, unknown>) =>
    apiClient.get('/api/transport/chauffeurs', { params }),
  createChauffeur: (data: unknown) =>
    apiClient.post('/api/transport/chauffeurs', data),
  genererBL: (missionId: number) =>
    apiClient.post(`/api/documents/bl`, { mission_id: missionId }),
  getFuel: () =>
    apiClient.get('/api/transport/fuel'),
  getKPIs: () =>
    apiClient.get('/api/transport/kpis'),
  getKpis: () =>
    apiClient.get('/api/transport/kpis'),
  getVehiclesHistory: (params?: Record<string, unknown>) =>
    apiClient.get('/api/transport/analytics/vehicles-history', { params }),
  getGPS: () =>
    apiClient.get('/api/transport/gps'),
  getPannes: (camionId: number) =>
    apiClient.get(`/api/transport/camions/${camionId}/pannes`),
  updatePanne: (camionId: number, panneId: number, data: unknown) =>
    apiClient.put(`/api/transport/camions/${camionId}/pannes/${panneId}`, data),
  debloquerCamion: (camionId: number) =>
    apiClient.put(`/api/transport/camions/${camionId}/debloquer`),
  associerRemorque: (camionId: number, remorqueId: number | null) =>
    apiClient.put(`/api/transport/camions/${camionId}/associer-remorque?remorque_id=${remorqueId || ''}`),
  dissocierRemorque: (camionId: number) =>
    apiClient.put(`/api/transport/camions/${camionId}/dissocier-remorque`),
  getHistoriqueCouplage: (camionId: number) =>
    apiClient.get(`/api/transport/camions/${camionId}/historique-couplage`),
  optimizeVRP: (data?: unknown) => apiClient.post('/api/v1/transport/vrp-optimize', data),
  getCorridorsCEMAC: () => apiClient.get('/api/v1/transport/corridors-cemac'),
  getFleetTCO: () => apiClient.get('/api/v1/transport/flotte/tco')
};

// â”€â”€â”€ Service Finance â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€
export const financeAPI = {
  getFactures: (params?: Record<string, unknown>) =>
    apiClient.get('/api/finance/factures', { params }),
  createFacture: (data: unknown) =>
    apiClient.post('/api/finance/factures', data),
  getEncaissements: (params?: Record<string, unknown>) =>
    apiClient.get('/api/finance/encaissements', { params }),
  getEncours: (tiersId: number) =>
    apiClient.get(`/api/finance/encours/${tiersId}`),
  enregistrerEncaissement: (data: unknown) =>
    apiClient.post('/api/finance/encaissements', data),
  getTarifs: (params?: Record<string, unknown>) =>
    apiClient.get('/api/finance/tarifs', { params }),
  createTarif: (data: unknown) =>
    apiClient.post('/api/finance/tarifs', data),
  lettrerEncaissement: (encaissementId: number, factureId: number) =>
    apiClient.post(`/api/finance/encaissements/${encaissementId}/lettrer/${factureId}`),
  getKpis: () =>
    apiClient.get('/api/finance/kpis'),
  getAnalyticsChartData: () =>
    apiClient.get('/api/finance/analytics/chart-data'),
  getPayroll: () =>
    apiClient.get('/api/finance/payroll/drivers'),
  getChartOfAccounts: (params?: Record<string, unknown>) =>
    apiClient.get('/api/finance/chart-accounts', { params }),
  createChartAccount: (data: unknown) =>
    apiClient.post('/api/finance/chart-accounts', data),
};

// â”€â”€â”€ Service Purchases (K-Achats) â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€
export const purchaseAPI = {
  getRequisitions: (params?: Record<string, unknown>) =>
    apiClient.get('/api/purchase/requisitions/', { params }),
  createRequisition: (data: unknown) =>
    apiClient.post('/api/purchase/requisitions/', data),
  getRequisition: (id: number) =>
    apiClient.get(`/api/purchase/requisitions/${id}`),
  updateRequisition: (id: number, data: unknown) =>
    apiClient.put(`/api/purchase/requisitions/${id}`, data),
  deleteRequisition: (id: number) =>
    apiClient.delete(`/api/purchase/requisitions/${id}`),
  submitRequisition: (id: number) =>
    apiClient.post(`/api/purchase/requisitions/${id}/submit`),
  approveRequisition: (id: number, notes?: string) =>
    apiClient.post(`/api/purchase/requisitions/${id}/approve`, { notes_approbation: notes }),
  rejectRequisition: (id: number, notes?: string) =>
    apiClient.post(`/api/purchase/requisitions/${id}/reject`, { notes_approbation: notes }),
};


// â”€â”€â”€ Service Parc â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€
export const parcAPI = {
  getZones: (params?: Record<string, unknown>) =>
    apiClient.get('/api/parc/zones', { params }),
  getEmplacements: (params?: Record<string, unknown>) =>
    apiClient.get('/api/parc/emplacements', { params }),
  getStock: (params?: Record<string, unknown>) =>
    apiClient.get('/api/parc/stock', { params }),
  gateIn: (data: unknown) => apiClient.post('/api/parc/gate-in', data),
  gateOut: (data: unknown) => apiClient.post('/api/parc/gate-out', data),
  extractOCR: async (file: File) => {
    const formData = new FormData();
    formData.append('file', file);
    return apiClient.post('/api/parc/ocr-extract', formData, {
      headers: {
        'Content-Type': 'multipart/form-data',
      },
    });
  },
  getWorkshopRepairs: () =>
    apiClient.get('/api/parc/workshop'),
  createZone: (data: unknown) => apiClient.post('/api/parc/zones', data),
  updateZone: (id: number, data: unknown) => apiClient.put(`/api/parc/zones/${id}`, data),
  deleteZone: (id: number) => apiClient.delete(`/api/parc/zones/${id}`),
  createEmplacement: (data: unknown) => apiClient.post('/api/parc/emplacements', data),
  updateEmplacement: (id: number, data: unknown) => apiClient.put(`/api/parc/emplacements/${id}`, data),
  deleteEmplacement: (id: number) => apiClient.delete(`/api/parc/emplacements/${id}`),
  createWorkshopRepair: (data: unknown) => apiClient.post('/api/parc/workshop', data),
  getStocksActifs: () => apiClient.get('/api/parc/stock-actifs'),
};

// â”€â”€â”€ Service Tiers â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€
export const tiersAPI = {
  getTiers: (params?: Record<string, unknown>) =>
    apiClient.get('/api/tiers', { params }),
  getClients: (params?: Record<string, unknown>) =>
    apiClient.get('/api/tiers', { params: { ...params, type_tiers: 'CLIENT' } }),
  getClient: (id: number) =>
    apiClient.get(`/api/tiers/${id}`),
  getTiersById: (id: number) =>
    apiClient.get(`/api/tiers/${id}`),
  createTiers: (data: unknown) =>
    apiClient.post('/api/tiers', data),
  updateTiers: (id: number, data: unknown) =>
    apiClient.put(`/api/tiers/${id}`, data),
  deleteTiers: (id: number) =>
    apiClient.delete(`/api/tiers/${id}`),
};

// â”€â”€â”€ Service Suppliers (Fournisseurs) â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€
export const suppliersAPI = {
  getSuppliers: (params?: Record<string, unknown>) =>
    apiClient.get('/api/suppliers', { params }),
  getSupplier: (id: number) =>
    apiClient.get(`/api/suppliers/${id}`),
  createSupplier: (data: unknown) =>
    apiClient.post('/api/suppliers', data),
  updateSupplier: (id: number, data: unknown) =>
    apiClient.put(`/api/suppliers/${id}`, data),
};

// â”€â”€â”€ Service Master Data â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€
export const masterDataAPI = {
  getArticles: (params?: Record<string, unknown>) =>
    apiClient.get('/api/master-data/articles', { params }),
  getArticle: (id: number) =>
    apiClient.get(`/api/master-data/articles/${id}`),
  createArticle: (data: unknown) =>
    apiClient.post('/api/master-data/articles', data),
  updateArticle: (id: number, data: unknown) =>
    apiClient.put(`/api/master-data/articles/${id}`, data),
  deleteArticle: (id: number) =>
    apiClient.delete(`/api/master-data/articles/${id}`),
  getTiers: (params?: Record<string, unknown>) =>
    apiClient.get('/api/tiers', { params }),
  getTier: (id: number) =>
    apiClient.get(`/api/tiers/${id}`),
  getArticleCategories: () =>
    apiClient.get('/api/master-data/article-categories'),
  getIncoterms: () =>
    apiClient.get('/api/master-data/incoterms'),
  getContainerTypes: () =>
    apiClient.get('/api/master-data/container-types'),
  getSummary: () =>
    apiClient.get('/api/v1/master-data'),
  getNomenclatures: (params?: Record<string, unknown>) =>
    apiClient.get('/api/v1/master-data/nomenclatures-cemac', { params }),
  createNomenclature: (data: unknown) =>
    apiClient.post('/api/v1/master-data/nomenclatures-cemac', data),
  getBureauxDouane: (type_bureau?: string) =>
    apiClient.get('/api/v1/master-data/bureaux-douane', { params: { type_bureau } }),
  getTauxBEAC: (devise?: string) =>
    apiClient.get('/api/v1/master-data/taux-beac', { params: { devise } }),
  getCorridors: () =>
    apiClient.get('/api/v1/master-data/corridors'),
};

// â”€â”€â”€ Service Magasin â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€ // ðŸ“¦ Service Magasin ðŸ­
export const magasinAPI = {
  generateStockValuationReport: (params: any) => apiClient.post('/api/magasin/reports/stock-valuation', params),
  generateMouvementAnalysisReport: (params: any) => apiClient.post('/api/magasin/reports/mouvement-analysis', params),
  generateClientPerformanceReport: (params: any) => apiClient.post('/api/magasin/reports/client-performance', params),
  exportReportToCSV: (data: any) => apiClient.post('/api/magasin/reports/export/csv', data),
  exportReportToJSON: (data: any) => apiClient.post('/api/magasin/reports/export/json', data),
  exportClientsToCSV: () => apiClient.get('/api/magasin/export/clients/csv'),
  exportArticlesToCSV: () => apiClient.get('/api/magasin/export/articles/csv'),
  importArticlesFromCSV: (data: any) => apiClient.post('/api/magasin/import/articles', data),
  importClientsFromCSV: (data: any) => apiClient.post('/api/magasin/import/clients', data),
  importMagasinsFromCSV: (data: any) => apiClient.post('/api/magasin/import/magasins', data),
  getArticles: (params?: any) => apiClient.get('/api/magasin/articles', { params }),
  exportMagasinsToCSV: () => apiClient.get('/api/magasin/export/magasins/csv'),
  deleteMagasin: (id: number) => apiClient.delete(`/api/magasin/magasins/${id}`),
  getMagasins: (params?: Record<string, unknown>) =>
    apiClient.get('/api/magasin/magasins', { params }),
  getStocks: (params?: Record<string, unknown>) =>
    apiClient.get('/api/magasin/stocks', { params }),
  getKpis: () =>
    apiClient.get('/api/magasin/kpis'),
  getClients: (params?: Record<string, unknown>) =>
    apiClient.get('/api/magasin/clients', { params }),
  createClient: (data: unknown) =>
    apiClient.post('/api/magasin/clients', data),
  updateClient: (id: number, data: unknown) =>
    apiClient.put(`/api/magasin/clients/${id}`, data),
  deleteClient: (id: number) =>
    apiClient.delete(`/api/magasin/clients/${id}`),
  getReceptions: (params?: Record<string, unknown>) =>
    apiClient.get('/api/magasin/receptions', { params }),
  createReception: async (data: any) => {
    const response = await apiClient.post('/api/magasin/receptions', data)
    return response.data
  },
  createRemovalSlip: async (data: any) => {
    const response = await apiClient.post('/api/magasin/removal-slips', data)
    return response.data
  },
  createReceptionMag3: (data: unknown) =>
    apiClient.post('/api/magasin/receptions-mag3', data),
  getDeclarations: (params?: Record<string, unknown>) =>
    apiClient.get('/api/magasin/declarations', { params }),
  getDeclaration: (id: number) =>
    apiClient.get(`/api/magasin/declarations/${id}`),
  getDeclarationReceptionsSummary: (id: number) =>
    apiClient.get(`/api/magasin/declarations/${id}/receptions-summary`),
  getDeclarationReceptionsHistory: (id: number) =>
    apiClient.get(`/api/magasin/declarations/${id}/receptions-history`),
  completeReception: (data: unknown) =>
    apiClient.post('/api/magasin/receptions', data),
  getCommandes: (params?: Record<string, unknown>) =>
    apiClient.get('/api/magasin/commandes', { params }),
  getHistory: (params?: Record<string, unknown>) =>
    apiClient.get('/api/magasin/history', { params }),
  // Ordres de Transfert
  getOrdresTransfert: (params?: Record<string, unknown>) =>
    apiClient.get('/api/magasin/ordres-transfert', { params }),
  getOrdreTransfert: (id: number) =>
    apiClient.get(`/api/magasin/ordres-transfert/${id}`),
  createOrdreTransfert: (data: unknown) =>
    apiClient.post('/api/magasin/ordres-transfert', data),
  validerOrdreTransfert: (id: number) =>
    apiClient.post(`/api/magasin/ordres-transfert/${id}/valider`),
  validerPaiementOT: (id: number) =>
    apiClient.post(`/api/magasin/ordres-transfert/${id}/valider-paiement`),
  expedierOrdreTransfert: (id: number) =>
    apiClient.post(`/api/magasin/ordres-transfert/${id}/expedier`),
  receptionnerOrdreTransfert: (id: number) =>
    apiClient.post(`/api/magasin/ordres-transfert/${id}/receptionner`),
  annulerOrdreTransfert: (id: number) =>
    apiClient.post(`/api/magasin/ordres-transfert/${id}/annuler`),
  getTransactions: () =>
    apiClient.get('/api/magasin/transactions'),
  getStockStatuses: () =>
    apiClient.get('/api/magasin/stock-statuses'),
  getArticleByCode: (code: string) =>
    apiClient.get(`/api/magasin/articles/by-code/${code}`),
  createDeclaration: (data: any) =>
    apiClient.post('/api/magasin/declarations', data),
  // New BandeLivraison endpoints
  getBandes: (params?: Record<string, unknown>) =>
    apiClient.get('/api/magasin/bandes-livraison', { params }),
  getBande: (id: number) =>
    apiClient.get(`/api/magasin/bandes-livraison/${id}`),
  createBande: async (data: any) => {
    const response = await apiClient.post('/api/magasin/bandes-livraison', data)
    return response.data
  },
  updateBande: (id: number, data: unknown) =>
    apiClient.put(`/api/magasin/bandes-livraison/${id}`, data),
  // Special endpoints
  createBandeFromOrdreTransfert: (otId: number, prepare_par: string) =>
    apiClient.post(`/api/magasin/bandes-livraison/from-ordre-transfert/${otId}`, { prepare_par }),
  getBandeByOrdreTransfert: (otId: number) =>
    apiClient.get(`/api/magasin/bandes-livraison/ordre-transfert/${otId}`),
  // Predictive endpoint
  getReceptionTimingPrediction: (declarationId: number) =>
    apiClient.get(`/api/magasin/predictions/reception-timing/${declarationId}`),
  // WMS Advanced methods
  executeCrossDocking: (data: unknown) => apiClient.post('/api/magasin/cross-docking', data),
  scanRFBarcode: (data: unknown) => apiClient.post('/api/magasin/rf-scan', data),
  getROPAnalysis: (articleCode?: string) => apiClient.get('/api/magasin/reapprovisionnement/rop', { params: { article_code: articleCode } }),
  generateWavePicking: (data: unknown) => apiClient.post('/api/v1/magasin-wms-avance/picking/vague', data),
  regulariserInventaire: (data: unknown) => apiClient.post('/api/v1/magasin-wms-avance/inventaire/regulariser', data)
};

// â”€â”€â”€ Advanced Analytics Endpoints â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€
export const analyticsAPI = {
  postDemandForecast: (data: {
    article_id: number;
    magasin_id?: number;
    horizon_days?: number;
  }) =>
    apiClient.post('/api/magasin/analytics/demand-forecast', data),
  postStockTurnoverAnalysis: (data: {
    article_id: number;
    months?: number;
  }) =>
    apiClient.post('/api/magasin/analytics/stock-turnover', data),
  postSafetyStockCalculation: (data: {
    article_id: number;
    magasin_id: number;
    service_level?: number;
    lead_time_days?: number;
  }) =>
    apiClient.post('/api/magasin/analytics/safety-stock', data),
  postAnomalyDetection: (data: {
    article_id: number;
    magasin_id: number;
    days?: number;
    sensitivity?: number;
  }) =>
    apiClient.post('/api/magasin/analytics/anomaly-detection', data)
};

// â”€â”€â”€ Service Notifications â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€
export const notificationsAPI = {
  getMyNotifications: (params?: Record<string, unknown>) =>
    apiClient.get('/api/notifications/', { params }),
  getStats: () =>
    apiClient.get('/api/notifications/stats'),
  markAsRead: (id: number) =>
    apiClient.put(`/api/notifications/${id}/mark-read`),
  markAllAsRead: () =>
    apiClient.put('/api/notifications/mark-all-read'),
  deleteRead: () =>
    apiClient.delete('/api/notifications/read'),
};

// â”€â”€â”€ Service Incidents (Ticketing) â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€
export const incidentsAPI = {
  getIncidents: () => apiClient.get('/api/incidents'),
  getClientIncidents: (tiersId: number) => apiClient.get(`/api/incidents/client/${tiersId}`),
  createIncident: (data: unknown) => apiClient.post('/api/incidents', data),
  updateIncident: (id: number, data: unknown) => apiClient.patch(`/api/incidents/${id}`, data),
};

// â”€â”€â”€ Service Ressources Humaines (RH) â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€
export const rhAPI = {
  getEmployes: (params?: Record<string, unknown>) => apiClient.get('/api/rh/employes', { params }),
  createEmploye: (data: unknown) => apiClient.post('/api/rh/employes', data),
  getMyProfile: () => apiClient.get('/api/rh/employes/me'),
  getConges: (params?: Record<string, unknown>) => apiClient.get('/api/rh/conges', { params }),
  createConge: (data: unknown) => apiClient.post('/api/rh/conges', data),
  updateCongeStatut: (id: number, statut: string) => apiClient.patch(`/api/rh/conges/${id}/statut`, { statut }),
  getPaie: (params?: Record<string, unknown>) => apiClient.get('/api/rh/paie', { params }),
  createFichePaie: (data: unknown) => apiClient.post('/api/rh/paie', data),
  importEmployesExcel: (data: FormData) => apiClient.post('/api/rh/employes/import-excel', data, {
    headers: { 'Content-Type': 'multipart/form-data' },
  }),
};

// ─── Service Portail Employé RH (Self-Service Salarié) ─────────────
export const portailRHAPI = {
  getMonProfil: () => apiClient.get('/api/v1/rh/portail/me'),
  getMesBulletins: () => apiClient.get('/api/v1/rh/portail/bulletins'),
  telechargerBulletin: (id: string) => `/api/v1/rh/portail/bulletins/${id}/telecharger`,
  getCalendrierPaie: () => apiClient.get('/api/v1/rh/portail/calendrier-paie'),
  getMesConges: () => apiClient.get('/api/v1/rh/portail/conges'),
  soumettreConge: (data: { type_conge: string; date_debut: string; date_fin: string; motif?: string }) =>
    apiClient.post('/api/v1/rh/portail/conges', data),
  getDocumentsRH: () => apiClient.get('/api/v1/rh/portail/documents'),
  telechargerAttestationTravail: () => '/api/v1/rh/portail/documents/attestation-travail',
};

// ─── Service Chat Collaboratif & Meeting Rooms & WebRTC ────────────
export const chatCollabAPI = {
  getDirectory: (q?: string) => apiClient.get('/api/v1/chat/directory', { params: q ? { q } : {} }),
  getForumMessages: () => apiClient.get('/api/v1/chat/forum'),
  postForumMessage: (content: string) => apiClient.post('/api/v1/chat/forum', { content }),
  getDirectMessages: (colleagueId: number) => apiClient.get(`/api/v1/chat/direct/${colleagueId}`),
  sendDirectMessage: (recipientId: number, content: string) =>
    apiClient.post('/api/v1/chat/direct', { recipient_id: recipientId, content }),
  getRooms: () => apiClient.get('/api/v1/chat/rooms'),
  createRoom: (data: { name: string; topic?: string; is_private?: boolean; participant_ids?: number[] }) =>
    apiClient.post('/api/v1/chat/rooms', data),
  getRoomMessages: (roomIdentifier: string) => apiClient.get(`/api/v1/chat/rooms/${roomIdentifier}/messages`),
  sendRoomMessage: (roomIdentifier: string, content: string) =>
    apiClient.post(`/api/v1/chat/rooms/${roomIdentifier}/messages`, { content }),
  getWebRTCConfig: () => apiClient.get('/api/v1/chat/webrtc/config'),
  sendWebRTCSignal: (data: { room_uuid: string; target_user_id?: number; signal_type: string; payload: unknown }) =>
    apiClient.post('/api/v1/chat/call/signal', data),
  fetchPendingSignals: (roomUuid: string, since = 0) =>
    apiClient.get(`/api/v1/chat/call/signals/${roomUuid}`, { params: { since } }),
  getCallStatus: (roomUuid: string) => apiClient.get(`/api/v1/chat/call/status/${roomUuid}`),
};

// ─── Service Gateway ───────────────────────────────────────────────
export const gatewayAPI = {
  getPasserellesEnAttente: () => apiClient.get('/api/passerelles/en-attente').then(r => r.data),
  getPasserelles: () => apiClient.get('/api/passerelles').then(r => r.data),
  getAll: (params?: Record<string, unknown>) => apiClient.get('/api/v1/gateway', { params }),
  getStats: () => apiClient.get('/api/v1/gateway/stats'),
  getById: (id: number) => apiClient.get(`/api/v1/gateway/${id}`),
  create: (data: unknown) => apiClient.post('/api/v1/gateway', data),
  update: (id: number, data: unknown) => apiClient.put(`/api/v1/gateway/${id}`, data),
  ping: (id: number) => apiClient.post(`/api/v1/gateway/${id}/ping`),
  delete: (id: number) => apiClient.delete(`/api/v1/gateway/${id}`),
};

export const aiAPI = {
  sendMessage: (message: string) => apiClient.post('/api/ai/chat', { message })
};

// â”€â”€â”€ Service Accostage (Acconage) â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€
export const acconageAPI = {
  getAcconages: (params?: Record<string, unknown>) => apiClient.get('/api/v1/acconage', { params }),
  getAcconage: (id: number) => apiClient.get(`/api/v1/acconage/${id}`),
  createAcconage: (data: unknown) => apiClient.post('/api/v1/acconage', data),
  updateAcconage: (id: number, data: unknown) => apiClient.put(`/api/v1/acconage/${id}`, data),
  deleteAcconage: (id: number) => apiClient.delete(`/api/v1/acconage/${id}`),
  importBaplie: (data: { escale_id: number; edi_content: string }) => apiClient.post('/api/v1/acconage/baplie/import', data),
  exportBaplie: (escaleId: number) => apiClient.get(`/api/v1/acconage/baplie/export/${escaleId}`),
  getYardState: () => apiClient.get('/api/v1/acconage/yard/state'),
  assignYardSlot: (data: unknown) => apiClient.post('/api/v1/acconage/yard/assign', data),
  calculatePortDues: (escaleId: number, portCode = 'PAD') => apiClient.get(`/api/v1/acconage/facturation-quai/${escaleId}?port_code=${portCode}`),
  generatePortInvoice: (escaleId: number, data?: unknown) => apiClient.post(`/api/v1/acconage/facturation-quai/${escaleId}/generer-facture`, data)
};

// ─── Service Transit ────────────────────────────────
export const transitAPI = {
  getTransits: (params?: Record<string, unknown>) => apiClient.get('/api/v1/transit', { params }),
  getTransit: (id: number) => apiClient.get(`/api/v1/transit/${id}`),
  createTransit: (data: unknown) => apiClient.post('/api/v1/transit', data),
  updateTransit: (id: number, data: unknown) => apiClient.put(`/api/v1/transit/${id}`, data),
  deleteTransit: (id: number) => apiClient.delete(`/api/v1/transit/${id}`)
};

// â”€â”€â”€ Service Maintenance â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€
export const maintenanceAPI = {
  getMaintenances: (params?: Record<string, unknown>) => apiClient.get('/api/v1/maintenance', { params }),
  getMaintenance: (id: number) => apiClient.get(`/api/v1/maintenance/${id}`),
  createMaintenance: (data: unknown) => apiClient.post('/api/v1/maintenance', data),
  updateMaintenance: (id: number, data: unknown) => apiClient.put(`/api/v1/maintenance/${id}`, data),
  deleteMaintenance: (id: number) => apiClient.delete(`/api/v1/maintenance/${id}`),
  destockerPieces: (data: unknown) => apiClient.post('/api/v1/maintenance/destockage-pieces', data),
  getCarnetEntretien: (vin: string) => apiClient.get(`/api/v1/maintenance/carnet-entretien/${vin}`),
  diagnostiquerTelematics: (immat: string) => apiClient.get(`/api/v1/maintenance/telematics/obd2/${immat}`),
  getKPIs: () => apiClient.get('/api/v1/maintenance/analytics/kpis')
};


// â”€â”€â”€ Service QHSE â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€
export const qhseAPI = {
  getQhseRecords: (params?: Record<string, unknown>) => apiClient.get('/api/v1/qhse', { params }),
  getIncidents: (params?: Record<string, unknown>) => apiClient.get('/api/v1/qhse', { params }),
  getQhseRecord: (id: number) => apiClient.get(`/api/v1/qhse/${id}`),
  createQhseRecord: (data: unknown) => apiClient.post('/api/v1/qhse', data),
  createIncident: (data: unknown) => apiClient.post('/api/v1/qhse', data),
  updateQhseRecord: (id: number, data: unknown) => apiClient.put(`/api/v1/qhse/${id}`, data),
  deleteQhseRecord: (id: number) => apiClient.delete(`/api/v1/qhse/${id}`),
  createPermisTravail: (data: unknown) => apiClient.post('/api/v1/qhse/permis-travail', data),
  checkIMDGSegregation: (data: { classes_imdg: string[] }) => apiClient.post('/api/v1/qhse/imdg/segregation', data),
  getBilanCSSTCNPS: (annee = 2026) => apiClient.get(`/api/v1/qhse/csst-cnps/bilan?annee=${annee}`)
};

// ─── Service Cotations & Tarification ──────────────────────────────────────────
export const cotationsAPI = {
  getCotations: () => apiClient.get('/api/v1/cotations'),
  createCotation: (data: unknown) => apiClient.post('/api/v1/cotations', data),
};

// ─── Service Tracking & e-POD ──────────────────────────────────────────
export const trackingAPI = {
  getEpods: () => apiClient.get('/api/v1/tracking/epod'),
  createEpod: (data: unknown) => apiClient.post('/api/v1/tracking/epod', data),
};

// ─── Service FuelGuard Anti-Fraude ──────────────────────────────────────────
export const fuelGuardAPI = {
  getSensors: () => apiClient.get('/api/v1/fuel-guard/sensors'),
  createSensor: (data: unknown) => apiClient.post('/api/v1/fuel-guard/sensors', data),
};

// ─── Service Procurement & Achats ──────────────────────────────────────────
export const procurementAPI = {
  getOrders: () => apiClient.get('/api/v1/procurement/orders'),
  createOrder: (data: unknown) => apiClient.post('/api/v1/procurement/orders', data),
};

// ─── Service Compliance & Réglementation ──────────────────────────────────────────
export const complianceAPI = {
  getAudits: () => apiClient.get('/api/v1/compliance/audits'),
  createAudit: (data: unknown) => apiClient.post('/api/v1/compliance/audits', data),
};

// ─── Service BI & Analytics Executive ──────────────────────────────────────────
export const biAnalyticsAPI = {
  getSummary: () => apiClient.get('/api/v1/bi-analytics/executive-summary'),
};

// ─── Service Support & Litiges ──────────────────────────────────────────
export const supportAPI = {
  getIncidents: (params?: Record<string, unknown>) => apiClient.get('/api/v1/support/incidents', { params }),
  createIncident: (data: unknown) => apiClient.post('/api/v1/support/incidents', data),
  getTickets: (params?: Record<string, unknown>) => apiClient.get('/api/v1/support/tickets', { params }),
  createTicket: (data: unknown) => apiClient.post('/api/v1/support/tickets', data),
  updateIncident: (id: number | string, data: unknown) => apiClient.put(`/api/v1/support/incidents/${id}`, data),
};

// ─── Service Portail B2B Client ──────────────────────────────────────────
export const b2bPortalAPI = {
  getDossiers: (clientId?: number) => apiClient.get('/api/v1/b2b-portal/dossiers', { params: { client_id: clientId || 1 } }),
  getFactures: (clientId?: number) => apiClient.get('/api/v1/b2b-portal/factures', { params: { client_id: clientId || 1 } }),
  createQuote: (data: unknown) => apiClient.post('/api/v1/b2b-portal/quotes', data),
  createBooking: (data: unknown) => apiClient.post('/api/v1/b2b-portal/booking', data),
  trackCargo: (query: string) => apiClient.get(`/api/v1/b2b-portal/tracking/${encodeURIComponent(query)}`),
  processPayment: (data: unknown) => apiClient.post('/api/v1/b2b-portal/payments/checkout', data),
  getNotificationPreferences: (clientId?: number) => apiClient.get('/api/v1/b2b-portal/notifications/preferences', { params: { client_id: clientId || 1 } }),
  updateNotificationPreferences: (data: unknown, clientId?: number) => apiClient.put('/api/v1/b2b-portal/notifications/preferences', data, { params: { client_id: clientId || 1 } }),
};


export const api = apiClient;

// ─── Service Fleet / Parc Véhicules ──────────────────────────────────────────
export const fleetAPI = {
  getVehicles: (params?: Record<string, unknown>) => apiClient.get('/api/v1/fleet/vehicles', { params }),
  getVehicle: (id: number) => apiClient.get(`/api/v1/fleet/vehicles/${id}`),
  createVehicle: (data: unknown) => apiClient.post('/api/v1/fleet/vehicles', data),
  updateVehicle: (id: number, data: unknown) => apiClient.put(`/api/v1/fleet/vehicles/${id}`, data),
  deleteVehicle: (id: number) => apiClient.delete(`/api/v1/fleet/vehicles/${id}`),
  getFuelRecords: (params?: Record<string, unknown>) => apiClient.get('/api/v1/fleet/fuel-records', { params }),
  createFuelRecord: (data: unknown) => apiClient.post('/api/v1/fleet/fuel-records', data),
  getDocuments: (vehicleId?: number) => apiClient.get('/api/v1/fleet/documents', { params: { vehicle_id: vehicleId } }),
  uploadDocument: (data: FormData) => apiClient.post('/api/v1/fleet/documents', data, { headers: { 'Content-Type': 'multipart/form-data' } }),
};

// ─── Service CRM / Clients B2B ──────────────────────────────────────────
export const customerAPI = {
  getCustomers: (params?: Record<string, unknown>) => apiClient.get('/api/v1/customers', { params }),
  getCustomer: (id: number) => apiClient.get(`/api/v1/customers/${id}`),
  createCustomer: (data: unknown) => apiClient.post('/api/v1/customers', data),
  updateCustomer: (id: number, data: unknown) => apiClient.put(`/api/v1/customers/${id}`, data),
  deleteCustomer: (id: number) => apiClient.delete(`/api/v1/customers/${id}`),
  getContracts: (params?: Record<string, unknown>) => apiClient.get('/api/v1/customers/contracts', { params }),
  createContract: (data: unknown) => apiClient.post('/api/v1/customers/contracts', data),
};

// ─── Service Audit Logs ──────────────────────────────────────────
export const auditAPI = {
  getLogs: (params?: Record<string, unknown>) => apiClient.get('/api/v1/audit/logs', { params }),
  getAdminLogs: (params?: Record<string, unknown>) => apiClient.get('/api/v1/audit/admin-logs', { params }),
  exportLogs: (params?: Record<string, unknown>) => apiClient.get('/api/v1/audit/export', { params, responseType: 'blob' }),
};

// ─── Service Bill of Loading / Connaissements / BSC ───────────────────────
export const billOfLoadingAPI = {
  getAll: (params?: Record<string, unknown>) => apiClient.get('/api/v1/bill-of-loading', { params }),
  getStats: () => apiClient.get('/api/v1/bill-of-loading/stats'),
  getById: (id: number) => apiClient.get(`/api/v1/bill-of-loading/${id}`),
  create: (data: unknown) => apiClient.post('/api/v1/bill-of-loading', data),
  update: (id: number, data: unknown) => apiClient.put(`/api/v1/bill-of-loading/${id}`, data),
  validate: (id: number, reference_cncc?: string) => apiClient.post(`/api/v1/bill-of-loading/${id}/validate`, null, { params: { reference_cncc } }),
  delete: (id: number) => apiClient.delete(`/api/v1/bill-of-loading/${id}`),
};

// ─── Service Transactions Financières & Règlements ────────────────────────
export const transactionsAPI = {
  getAll: (params?: Record<string, unknown>) => apiClient.get('/api/v1/transactions', { params }),
  getStats: () => apiClient.get('/api/v1/transactions/stats'),
  getById: (id: number) => apiClient.get(`/api/v1/transactions/${id}`),
  create: (data: unknown) => apiClient.post('/api/v1/transactions', data),
  update: (id: number, data: unknown) => apiClient.put(`/api/v1/transactions/${id}`, data),
  reconcile: (id: number) => apiClient.post(`/api/v1/transactions/${id}/reconcile`),
  delete: (id: number) => apiClient.delete(`/api/v1/transactions/${id}`),
};

// ─── Service Removal Slips (Bons d'Enlèvement Magasin) ────────────────────
export const removalSlipAPI = {
  getAll: (params?: Record<string, unknown>) => apiClient.get('/api/v1/magasin/removal-slips', { params }),
  getStats: () => apiClient.get('/api/v1/magasin/removal-slips/stats'),
  getById: (id: number) => apiClient.get(`/api/v1/magasin/removal-slips/${id}`),
  create: (data: unknown) => apiClient.post('/api/v1/magasin/removal-slips', data),
  update: (id: number, data: unknown) => apiClient.put(`/api/v1/magasin/removal-slips/${id}`, data),
  validate: (id: number) => apiClient.post(`/api/v1/magasin/removal-slips/${id}/validate`),
  delete: (id: number) => apiClient.delete(`/api/v1/magasin/removal-slips/${id}`),
};

// ─── Service Réceptions Magasin 3 (MAG3) ──────────────────────────────────
export const receptionMag3API = {
  getAll: (params?: Record<string, unknown>) => apiClient.get('/api/v1/magasin/receptions-mag3', { params }),
  getStats: () => apiClient.get('/api/v1/magasin/receptions-mag3/stats'),
  getById: (id: number) => apiClient.get(`/api/v1/magasin/receptions-mag3/${id}`),
  create: (data: unknown) => apiClient.post('/api/v1/magasin/receptions-mag3', data),
  update: (id: number, data: unknown) => apiClient.put(`/api/v1/magasin/receptions-mag3/${id}`, data),
  validate: (id: number) => apiClient.post(`/api/v1/magasin/receptions-mag3/${id}/validate`),
  delete: (id: number) => apiClient.delete(`/api/v1/magasin/receptions-mag3/${id}`),
};

// ─── Service Goods Declaration (DUM Douane) ──────────────────────────────
export const goodsDeclarationAPI = {
  getAll: (params?: Record<string, unknown>) => apiClient.get('/api/v1/transport/goods-declarations', { params }),
  getStats: () => apiClient.get('/api/v1/transport/goods-declarations/stats'),
  getById: (id: number) => apiClient.get(`/api/v1/transport/goods-declarations/${id}`),
  create: (data: unknown) => apiClient.post('/api/v1/transport/goods-declarations', data),
  update: (id: number, data: unknown) => apiClient.put(`/api/v1/transport/goods-declarations/${id}`, data),
  liquidate: (id: number, agent_douane?: string) => apiClient.post(`/api/v1/transport/goods-declarations/${id}/liquidate`, null, { params: { agent_douane } }),
  delete: (id: number) => apiClient.delete(`/api/v1/transport/goods-declarations/${id}`),
};

// ─── Service Admin Agencies (Succursales) ─────────────────────────────────
export const adminAgencyAPI = {
  getAll: (params?: Record<string, unknown>) => apiClient.get('/api/v1/admin/agencies', { params }),
  getStats: () => apiClient.get('/api/v1/admin/agencies/stats'),
  getById: (id: number) => apiClient.get(`/api/v1/admin/agencies/${id}`),
  create: (data: unknown) => apiClient.post('/api/v1/admin/agencies', data),
  update: (id: number, data: unknown) => apiClient.put(`/api/v1/admin/agencies/${id}`, data),
  delete: (id: number) => apiClient.delete(`/api/v1/admin/agencies/${id}`),
};

// ─── Service Notifications Multi-Canal ────────────────────────────────────
export const notificationSystemAPI = {
  getAll: (params?: Record<string, unknown>) => apiClient.get('/api/v1/notification-system', { params }),
  getStats: () => apiClient.get('/api/v1/notification-system/stats'),
  getById: (id: number) => apiClient.get(`/api/v1/notification-system/${id}`),
  send: (data: unknown) => apiClient.post('/api/v1/notification-system/send', data),
  getTemplates: (canal?: string) => apiClient.get('/api/v1/notification-system/templates', { params: { canal } }),
  createTemplate: (data: unknown) => apiClient.post('/api/v1/notification-system/templates', data),
  markRead: (id: number) => apiClient.post(`/api/v1/notification-system/${id}/read`),
};

// ─── Service Partner API B2B ──────────────────────────────────────────────
export const partnerB2BAPI = {
  getOverview: () => apiClient.get('/api/v1/partner-api'),
  getWebhooks: (statut?: string) => apiClient.get('/api/v1/partner-api/webhooks', { params: { statut } }),
  createWebhook: (data: unknown) => apiClient.post('/api/v1/partner-api/webhooks', data),
  track: (ref: string) => apiClient.get(`/api/v1/partner-api/track/${encodeURIComponent(ref)}`),
  submitCotation: (data: unknown) => apiClient.post('/api/v1/partner-api/cotation-request', data),
  deleteWebhook: (id: number) => apiClient.delete(`/api/v1/partner-api/webhooks/${id}`),
};

// ─── Service Frais & Avances Missions ─────────────────────────────────────
export const fraisMissionsAPI = {
  getAll: (params?: Record<string, unknown>) => apiClient.get('/api/v1/frais-missions', { params }),
  create: (data: unknown) => apiClient.post('/api/v1/frais-missions', data),
  validate: (id: number, action: 'VALIDER' | 'REJETER', valide_par_nom = 'Manager', motif_rejet?: string) =>
    apiClient.post(`/api/v1/frais-missions/${id}/validate`, { action, valide_par_nom, motif_rejet }),
  getAvances: (params?: Record<string, unknown>) => apiClient.get('/api/v1/frais-missions/avances', { params }),
  createAvance: (data: unknown) => apiClient.post('/api/v1/frais-missions/avances', data),
  getStats: (userId?: number) => apiClient.get('/api/v1/frais-missions/stats', { params: { user_id: userId } }),
};

// ─── Service Maintenance GMAO ─────────────────────────────────────────────
export const maintenanceGMAOAPI = {
  getWorkOrders: (params?: Record<string, unknown>) => apiClient.get('/api/v1/maintenance-gmao/ordres', { params }),
  getEquipment: (params?: Record<string, unknown>) => apiClient.get('/api/v1/maintenance-gmao/equipements', { params }),
  createWorkOrder: (data: unknown) => apiClient.post('/api/v1/maintenance-gmao/ordres', data),
  updateWorkOrder: (id: number, data: unknown) => apiClient.put(`/api/v1/maintenance-gmao/ordres/${id}`, data),
};

// ─── Service Transit Avancé ───────────────────────────────────────────────
export const transitAvanceAPI = {
  getDossiers: (params?: Record<string, unknown>) => apiClient.get('/api/v1/transit-avance/dossiers', { params }),
  getBureauxDouane: () => apiClient.get('/api/v1/transit-avance/bureaux-douane'),
  createBureau: (data: unknown) => apiClient.post('/api/v1/transit-avance/bureaux-douane', data),
};

export default apiClient;


