// src/lib/api-client.ts  Client API TypeScript EVO-LOG  SOURCE UNIQUE DE VÉRITÉ
// Toutes les pages doivent passer par ce client (apiClient ou les services *API exportés ici).
import axios, { AxiosInstance, InternalAxiosRequestConfig } from 'axios';

// Fallback = le backend Railway reellement en ligne (health/login prouves 200).
let BASE_URL = process.env.NEXT_PUBLIC_API_URL || 'https://evo-log-backend-production.up.railway.app';
if (process.env.NODE_ENV === 'production' && BASE_URL.includes('localhost')) {
  BASE_URL = 'https://evo-log-backend-production.up.railway.app';
}

/** Préfixe d'API versionné exposé par le backend FastAPI. */
export const API_PREFIX = '/api/v1';

/**
 * Construit une URL d'API canonique : apiUrl('/magasin/articles')
 * -> '/api/v1/magasin/articles'. Accepte les variantes '/api/x', 'x', '/api/v1/x'.
 */
export function apiUrl(path: string): string {
  let p = path;
  if (p.startsWith(API_PREFIX + '/') || p === API_PREFIX) return p;
  if (p.startsWith('/api/v1/')) return p;
  if (p.startsWith('/api/')) return API_PREFIX + p.slice('/api'.length);
  if (p.startsWith('api/')) return API_PREFIX + p.slice('api'.length);
  return API_PREFIX + (p.startsWith('/') ? p : '/' + p);
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

/** Token courant (mémoire, puis localStorage)  pour les appels fetch hors axios
 *  (ex. synchronisation offline). Side navigateur uniquement. */
export function getAccessToken(): string | null {
  if (typeof window === 'undefined') return null;
  return _authToken || localStorage.getItem('access_token');
}

/** Base de l'API (même source de vérité que apiClient). */
export function getApiBaseUrl(): string {
  return BASE_URL;
}

// Intercepteur REQUEST  injecte le Bearer token (session NextAuth ou localStorage)
// et normalise les URLs d'API vers le préfixe versionné /api/v1.
apiClient.interceptors.request.use(
  (config: InternalAxiosRequestConfig) => {
    const hasAuthHeader = Boolean(config.headers['Authorization'] || config.headers?.get?.('Authorization'));
    if (!hasAuthHeader) {
      const fallbackToken = typeof window !== 'undefined' ? localStorage.getItem('access_token') : null;
      const token = _authToken || fallbackToken;
      if (token) config.headers['Authorization'] = `Bearer ${token}`;
    }
    // Normalisation explicite /api/... et variantes -> /api/v1/... (documents + tolérante)
    if (config.url && config.url.startsWith('/') && !config.url.startsWith('/api/docs') && !config.url.startsWith('/api/health')) {
      config.url = apiUrl(config.url);
    }
    return config;
  },
  (error) => Promise.reject(error)
);

// Intercepteur RESPONSE
// IMPORTANT: ne déclencher le logout automatique QUE pour les endpoints d'auth;
// les appels de données peuvent légitimement retourner 401 quand le backend distant
// est temporairement indisponible  le refresh est tenté une fois avant de renoncer.
let _refreshInFlight: Promise<boolean> | null = null;

export async function tryRefreshToken(): Promise<boolean> {
  if (typeof window === 'undefined') return false;
  const refreshToken = localStorage.getItem('refresh_token');
  if (!refreshToken) return false;
  try {
    const res = await axios.post(`${BASE_URL}${API_PREFIX}/auth/refresh`, { refresh_token: refreshToken }, { timeout: 10000 });
    const { access_token, refresh_token } = res.data || {};
    if (access_token) {
      localStorage.setItem('access_token', access_token);
      if (refresh_token) localStorage.setItem('refresh_token', refresh_token);
      _authToken = access_token;
      return true;
    }
    return false;
  } catch {
    return false;
  }
}

apiClient.interceptors.response.use(
  (response) => response,
  async (error) => {
    const status = error.response?.status;
    const url: string = error.config?.url || '';
    const isAuthEndpoint = url.includes('/auth/me') || url.includes('/auth/refresh') || url.includes('/auth/login');

    if (status === 401 && !isAuthEndpoint && error.config && !error.config._retriedAfterRefresh) {
      _refreshInFlight = _refreshInFlight ?? tryRefreshToken().finally(() => { _refreshInFlight = null; });
      const refreshed = await _refreshInFlight;
      if (refreshed) {
        error.config._retriedAfterRefresh = true;
        if (error.config.headers) error.config.headers['Authorization'] = `Bearer ${_authToken}`;
        return apiClient(error.config);
      }
    }

    if (status === 401 && isAuthEndpoint && typeof window !== 'undefined') {
      window.dispatchEvent(new CustomEvent('auth-error', { detail: { reason: 'unauthorized' } }));
    }
    return Promise.reject(error);
  }
);


// ─── Service Admin ──────────────────────────────────────────────────────────
// Le routeur admin n'est monte que sur /api/v1/admin (main.py) : les appels en
// /api/admin/... retombaient systematiquement sur le fallback « pending », ce
// qui vidait tous les ecrans d'administration. /api/v1/admin/agencies est bien
// distinct (routeur admin_agency monte sur ce meme prefixe).
export const adminAPI = {
  getUsers: (params?: Record<string, unknown>) => apiClient.get('/api/v1/admin/users', { params }),
  createUser: (data: any) => apiClient.post('/api/v1/admin/users', data),
  updateUser: (id: number, data: any) => apiClient.put(`/api/v1/admin/users/${id}`, data),
  toggleUserStatus: (id: number, data?: any) => apiClient.patch(`/api/v1/admin/users/${id}/status`, data),
  resetPassword: (id: number, new_password?: string) => apiClient.post(`/api/v1/admin/users/${id}/reset-password`, { new_password }),
  getRoles: () => apiClient.get('/api/v1/admin/roles'),
  createRole: (data: any) => apiClient.post('/api/v1/admin/roles', data),
  getAuditLogs: (params?: Record<string, unknown>) => apiClient.get('/api/v1/admin/audit-logs', { params }),
  getAgencies: (params?: Record<string, unknown>) => apiClient.get('/api/v1/admin/agencies', { params }),
  createAgency: (data: unknown) => apiClient.post('/api/v1/admin/agencies', data),
  updateAgency: (id: number, data: unknown) => apiClient.put(`/api/v1/admin/agencies/${id}`, data),
  deleteAgency: (id: number) => apiClient.delete(`/api/v1/admin/agencies/${id}`),
  getDashboardKpis: () => apiClient.get('/api/v1/admin/dashboard/global-kpis'),
  getSystemHealth: () => apiClient.get('/api/v1/admin/system-health'),
};

// ─── Console Super-Admin CADC (SaaS) ──────────────────────────────────────────
// Toutes les routes backend exigent require_superadmin (403 sinon).
// Base : /api/v1/saas/console
const CADC_BASE = '/api/v1/saas/console';
export const saasConsoleAPI = {
  // Catalogue des modules allouables
  getModulesCatalog: () => apiClient.get(`${CADC_BASE}/modules-catalog`),

  // Entreprises : CRUD total + logo + allocation modules + accréditations
  listCompanies: (search?: string) =>
    apiClient.get(`${CADC_BASE}/companies`, { params: search ? { search } : undefined }),
  getCompany: (id: number) => apiClient.get(`${CADC_BASE}/companies/${id}`),
  createCompany: (data: Record<string, unknown>) => apiClient.post(`${CADC_BASE}/companies`, data),
  updateCompany: (id: number, data: Record<string, unknown>) =>
    apiClient.patch(`${CADC_BASE}/companies/${id}`, data),
  deleteCompany: (id: number) => apiClient.delete(`${CADC_BASE}/companies/${id}`),
  uploadLogo: (id: number, file: File) => {
    const form = new FormData();
    form.append('file', file);
    return apiClient.post(`${CADC_BASE}/companies/${id}/logo`, form, {
      headers: { 'Content-Type': 'multipart/form-data' },
    });
  },
  allocateModules: (id: number, modules: string[]) =>
    apiClient.put(`${CADC_BASE}/companies/${id}/modules`, { modules }),

  // Admins entreprise (designes par le CADC - Phase 2)
  listCompanyAdmins: (id: number) =>
    apiClient.get(`${CADC_BASE}/companies/${id}/admins`),
  createCompanyAdmin: (id: number, data: Record<string, unknown>) =>
    apiClient.post(`${CADC_BASE}/companies/${id}/admins`, data),

  // File des demandes d'accreditation emises par les admins entreprise
  listPendingAccreditationRequests: () =>
    apiClient.get(`${CADC_BASE}/accreditations/demandes`),
  // Phase 3 — arbitrage CADC : conversion en place de la demande
  // (approuver -> accreditation active datee) ou refus trace (refuser).
  approveAccreditationRequest: (
    requestId: number,
    data: { date_debut?: string; date_fin?: string; motif?: string },
  ) => apiClient.post(`${CADC_BASE}/accreditations/demandes/${requestId}/approuver`, data),
  rejectAccreditationRequest: (requestId: number, data?: { motif?: string }) =>
    apiClient.post(`${CADC_BASE}/accreditations/demandes/${requestId}/refuser`, data || {}),

  listCompanyAccreditations: (id: number) =>
    apiClient.get(`${CADC_BASE}/companies/${id}/accreditations`),
  grantCompanyAccreditation: (id: number, data: Record<string, unknown>) =>
    apiClient.post(`${CADC_BASE}/companies/${id}/accreditations`, data),
  revokeCompanyAccreditation: (id: number, accredId: number) =>
    apiClient.delete(`${CADC_BASE}/companies/${id}/accreditations/${accredId}`),

  // Plans d'abonnement (paliers SaaS) : CRUD + verrou max_modules
  listPlans: () => apiClient.get(`${CADC_BASE}/plans`),
  createPlan: (data: Record<string, unknown>) => apiClient.post(`${CADC_BASE}/plans`, data),
  updatePlan: (id: number, data: Record<string, unknown>) =>
    apiClient.patch(`${CADC_BASE}/plans/${id}`, data),
  deletePlan: (id: number) => apiClient.delete(`${CADC_BASE}/plans/${id}`),

  // Annuaire prestataires (écriture réservée CADC)
  listPrestataires: (params?: Record<string, unknown>) =>
    apiClient.get(`${CADC_BASE}/prestataires`, { params }),
  createPrestataire: (data: Record<string, unknown>) =>
    apiClient.post(`${CADC_BASE}/prestataires`, data),
  updatePrestataire: (id: number, data: Record<string, unknown>) =>
    apiClient.patch(`${CADC_BASE}/prestataires/${id}`, data),
  deletePrestataire: (id: number) => apiClient.delete(`${CADC_BASE}/prestataires/${id}`),
};

// ─── Administration interne Entreprise (Phase 2 - niveau 1) ──────────────────
// Backend : /api/v1/company-admin, garde require_company_admin + scope entreprise.
// Un admin entreprise est epingle a sa societe ; le CADC passe un company_id explicite.
const CA_BASE = '/api/v1/company-admin';
export const companyAdminAPI = {
  getProfile: (companyId?: number) =>
    apiClient.get(`${CA_BASE}/profil`, { params: companyId ? { company_id: companyId } : undefined }),
  updateProfile: (data: Record<string, unknown>, companyId?: number) =>
    apiClient.patch(`${CA_BASE}/profil`, data, { params: companyId ? { company_id: companyId } : undefined }),

  listMembers: (params?: Record<string, unknown>, companyId?: number) =>
    apiClient.get(`${CA_BASE}/utilisateurs`, { params: { ...params, ...(companyId ? { company_id: companyId } : {}) } }),
  createMember: (data: Record<string, unknown>, companyId?: number) =>
    apiClient.post(`${CA_BASE}/utilisateurs`, data, { params: companyId ? { company_id: companyId } : undefined }),
  updateMember: (id: number, data: Record<string, unknown>) =>
    apiClient.put(`${CA_BASE}/utilisateurs/${id}`, data),
  setMemberRoles: (id: number, roles: string[]) =>
    apiClient.patch(`${CA_BASE}/utilisateurs/${id}/responsabilites`, { roles }),
  toggleMemberStatus: (id: number) =>
    apiClient.patch(`${CA_BASE}/utilisateurs/${id}/statut`),

  modulesOverview: (companyId?: number) =>
    apiClient.get(`${CA_BASE}/modules`, { params: companyId ? { company_id: companyId } : undefined }),
  requestModule: (data: { module: string; libelle?: string; motif?: string }, companyId?: number) =>
    apiClient.post(`${CA_BASE}/modules/demandes`, data, { params: companyId ? { company_id: companyId } : undefined }),
  cancelModuleRequest: (requestId: number) =>
    apiClient.delete(`${CA_BASE}/modules/demandes/${requestId}`),
};

// ─── Espace Departement (Phase 3 - niveau 2, chef de departement) ────────────
// Backend : /api/v1/departement, garde require_department_head + perimetre
// departement. Un chef est epingle a SON departement ; admin entreprise (1) et
// CADC (0) ciblent un departement de leur entreprise via department_id.
const DEPT_BASE = '/api/v1/departement';
export const departmentAPI = {
  getOverview: (departmentId?: number) =>
    apiClient.get(`${DEPT_BASE}/overview`, { params: departmentId ? { department_id: departmentId } : undefined }),
  listMembers: (params?: Record<string, unknown>, departmentId?: number) =>
    apiClient.get(`${DEPT_BASE}/membres`, { params: { ...params, ...(departmentId ? { department_id: departmentId } : {}) } }),
  // Tranche B (ecritures scopees) : un chef affecte/retire des collaborateurs de
  // SON departement ; l'allocation des modules releve de l'admin entreprise / CADC.
  affectMember: (memberId: number, departmentId?: number) =>
    apiClient.post(`${DEPT_BASE}/membres/${memberId}/affecter`, undefined, { params: departmentId ? { department_id: departmentId } : undefined }),
  removeMember: (memberId: number, departmentId?: number) =>
    apiClient.post(`${DEPT_BASE}/membres/${memberId}/retirer`, undefined, { params: departmentId ? { department_id: departmentId } : undefined }),
  listCandidates: (params?: Record<string, unknown>, departmentId?: number) =>
    apiClient.get(`${DEPT_BASE}/candidats`, { params: { ...params, ...(departmentId ? { department_id: departmentId } : {}) } }),
  setModules: (modules: string[], departmentId?: number) =>
    apiClient.put(`${DEPT_BASE}/modules`, { modules }, { params: departmentId ? { department_id: departmentId } : undefined }),
  // Phase 4 (lecture scopee departement) : planning des tours de garde et presence.
  getPlanning: (params?: { semaine?: string; departmentId?: number }) =>
    apiClient.get(`${DEPT_BASE}/planning`, { params: { semaine: params?.semaine, ...(params?.departmentId ? { department_id: params.departmentId } : {}) } }),
  getPresence: (params?: { date?: string; departmentId?: number }) =>
    apiClient.get(`${DEPT_BASE}/presence`, { params: { date: params?.date, ...(params?.departmentId ? { department_id: params.departmentId } : {}) } }),
  // Phase 4 Tranche B (ecriture) : le chef gere les tours de garde et valide les pointages.
  createPlanning: (data: { employe_id: number; date_jour: string; quart: string; poste_assigne: string; statut?: string; observations?: string }, departmentId?: number) =>
    apiClient.post(`${DEPT_BASE}/planning`, data, { params: departmentId ? { department_id: departmentId } : undefined }),
  updatePlanning: (id: number, data: { quart?: string; poste_assigne?: string; statut?: string; observations?: string }, departmentId?: number) =>
    apiClient.put(`${DEPT_BASE}/planning/${id}`, data, { params: departmentId ? { department_id: departmentId } : undefined }),
  deletePlanning: (id: number, departmentId?: number) =>
    apiClient.delete(`${DEPT_BASE}/planning/${id}`, { params: departmentId ? { department_id: departmentId } : undefined }),
  validatePresence: (pointageId: number, departmentId?: number) =>
    apiClient.post(`${DEPT_BASE}/presence/${pointageId}/valider`, undefined, { params: departmentId ? { department_id: departmentId } : undefined }),
};

/** RBAC granulaire : catalogue de permissions, rôles effectifs, accréditations
 *  et modules communs (acces partages) par entreprise. */
export const rbacAPI = {
  getPermissionCatalog: () => apiClient.get('/api/rbac/permissions/catalog'),
  listRolesWithPermissions: () => apiClient.get('/api/rbac/roles'),
  getRolePermissions: (roleId: number) => apiClient.get(`/api/rbac/roles/${roleId}/permissions`),
  setRolePermissions: (roleId: number, codes: string[]) =>
    apiClient.put(`/api/rbac/roles/${roleId}/permissions`, { codes }),
  checkPermission: (data: { user_id: number; tenant_id?: number; permission_code: string }) =>
    apiClient.post('/api/rbac/permissions/check', data),
  listAccreditations: (params?: Record<string, unknown>) => apiClient.get('/api/accreditations/', { params }),
  myAccreditations: () => apiClient.get('/api/accreditations/mes-accreditations'),
  createAccreditation: (data: any, companyId?: number) =>
    apiClient.post('/api/accreditations/', data, { params: companyId ? { company_id: companyId } : {} }),
  updateAccreditation: (id: number, data: any) => apiClient.put(`/api/accreditations/${id}`, data),
  deleteAccreditation: (id: number) => apiClient.delete(`/api/accreditations/${id}`),
  listSharedAccess: (params?: Record<string, unknown>) => apiClient.get('/api/shared-access/', { params }),
  setSharedAccess: (data: { module_key: string; libelle?: string; autorise_tous_utilisateurs: boolean }, companyId?: number) =>
    apiClient.post('/api/shared-access/', data, { params: companyId ? { company_id: companyId } : {} }),
  deleteSharedAccess: (id: number) => apiClient.delete(`/api/shared-access/${id}`),
  seedSharedAccess: (companyId?: number) =>
    apiClient.post('/api/shared-access/initialiser', null, { params: companyId ? { company_id: companyId } : {} }),
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
  // 2FA / TOTP : le toggle bidonne a ete remplace par le vrai flux backend
  // (status -> setup -> enable | disable), le secret n'est jamais relus.
  get2FAStatus: () =>
    apiClient.get('/api/v1/auth/2fa/status'),
  setup2FA: (code?: string) =>
    apiClient.post('/api/v1/auth/2fa/setup', code ? { code } : {}),
  enable2FA: (code: string) =>
    apiClient.post('/api/v1/auth/2fa/enable', { code }),
  disable2FA: (password: string) =>
    apiClient.post('/api/v1/auth/2fa/disable', { password }),
  verify2FA: (data: { two_factor_token: string; code: string }) =>
    apiClient.post('/api/v1/auth/2fa/verify', data),
  // Codes de secours 2FA : la base ne stocke que des hachages, le solde seul
  // est relus. Les codes en clair n'apparaissent que dans la reponse d'emission.
  getRecoveryCodesStatus: () =>
    apiClient.get('/api/v1/auth/2fa/recovery-codes'),
  regenerateRecoveryCodes: (password: string) =>
    apiClient.post('/api/v1/auth/2fa/recovery-codes', { password }),
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
  getFuel: (params?: Record<string, unknown>) =>
    apiClient.get('/api/transport/fuel', { params }),
  getTicketsCarburant: (params?: Record<string, unknown>) =>
    apiClient.get('/api/transport/carburant/tickets', { params }),
  createTicketCarburant: (data: unknown) =>
    apiClient.post('/api/transport/carburant/tickets', data),
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
  // `source` (exploitation | ohada) : deux tables de factures coexistent et le
  // backend ne peut pas deviner laquelle porte l'id a corriger.
  updateFacture: (id: number, data: unknown, source?: string) =>
    apiClient.put(`/api/finance/factures/${id}`, data, { params: source ? { source } : undefined }),
  getFacturePdf: (id: number) =>
    apiClient.get(`/api/finance/factures/${id}/pdf`, { responseType: 'blob' }),
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
    apiClient.get('/api/finance/plan-comptable', { params }),
  createChartAccount: (data: unknown) =>
    apiClient.post('/api/finance/plan-comptable', data),
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
    apiClient.get('/api/magasin/articles', { params }),
  getArticle: (id: number) =>
    apiClient.get(`/api/magasin/articles/${id}`),
  createArticle: (data: unknown) =>
    apiClient.post('/api/magasin/articles', data),
  updateArticle: (id: number, data: unknown) =>
    apiClient.put(`/api/magasin/articles/${id}`, data),
  deleteArticle: (id: number) =>
    apiClient.delete(`/api/magasin/articles/${id}`),
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
  getEntrepotsOccupation: () =>
    apiClient.get('/api/magasin/entrepots/occupation'),
  getClients: (params?: Record<string, unknown>) =>
    apiClient.get('/api/magasin/clients', { params }),
  createClient: (data: unknown) =>
    apiClient.post('/api/magasin/clients', data),
  updateClient: (id: number, data: unknown) =>
    apiClient.put(`/api/magasin/clients/${id}`, data),
  deleteClient: (id: number) =>
    apiClient.delete(`/api/magasin/clients/${id}`),
  getReceptions: (params?: Record<string, unknown>) =>
    apiClient.get('/api/magasin-avance/receptions', { params }),
  createReception: async (data: any) => {
    const response = await apiClient.post('/api/magasin-avance/receptions', data)
    return response.data
  },
  createRemovalSlip: async (data: any) => {
    const response = await apiClient.post('/api/magasin/removal-slips', data)
    return response.data
  },
  createReceptionMag3: (data: unknown) =>
    apiClient.post('/api/magasin/receptions-mag3', data),
  getDeclarations: (params?: Record<string, unknown>) =>
    apiClient.get('/api/magasin-douane/declarations', { params }),
  getDeclaration: (id: number) =>
    apiClient.get(`/api/magasin-douane/declarations/${id}`),
  getDeclarationReceptionsSummary: (id: number) =>
    apiClient.get(`/api/magasin/declarations/${id}/receptions-summary`),
  getDeclarationReceptionsHistory: (id: number) =>
    apiClient.get(`/api/magasin/declarations/${id}/receptions-history`),
  completeReception: (data: unknown) =>
    apiClient.post('/api/magasin-avance/receptions', data),
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
    apiClient.post('/api/magasin-douane/declarations', data),
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
    apiClient.post(`/api/magasin/bandes-livraison/from-ordre-transfert/${otId}`, null, { params: { prepare_par } }),
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
  // Decision sur une demande : le backend expose PUT /conges/{id}/approuver et
  // PUT /conges/{id}/rejeter, le motif de refus étant obligatoire au rejet.
  deciderConge: (id: number, approuve: boolean, commentaire = '') =>
    approuve
      ? apiClient.put(`/api/rh/conges/${id}/approuver`, null, { params: { commentaire } })
      : apiClient.put(`/api/rh/conges/${id}/rejeter`, null, { params: { motif_refus: commentaire } }),
  getPaie: (params?: Record<string, unknown>) => apiClient.get('/api/rh/paie/bulletin', { params }),
  createFichePaie: (data: unknown) => apiClient.post('/api/rh/paie/bulletin', data),
  importEmployesExcel: (data: FormData) => apiClient.post('/api/rh/employes/import-excel', data, {
    headers: { 'Content-Type': 'multipart/form-data' },
  }),
};

// ─── Service Portail Employé RH (Self-Service Salarié) ─────────────
export const portailRHAPI = {
  getMonProfil: () => apiClient.get('/api/v1/rh/portail/me'),
  getMesBulletins: () => apiClient.get('/api/v1/rh/portail/bulletins'),
  getCalendrierPaie: () => apiClient.get('/api/v1/rh/portail/calendrier-paie'),
  getMesConges: () => apiClient.get('/api/v1/rh/portail/conges'),
  soumettreConge: (data: { type_conge: string; date_debut: string; date_fin: string; motif?: string }) =>
    apiClient.post('/api/v1/rh/portail/conges', data),
  getDocumentsRH: () => apiClient.get('/api/v1/rh/portail/documents'),
  // Les pièces du portail sont derrière une authentification Bearer : un lien
  // <a href="/api/v1/..."> part sans jeton et revient en 401. Le fichier est
  // donc récupéré par le client HTTP, qui porte l'en-tête d'authentification,
  // puis présenté via une URL objet locale.
  telechargerBulletin: (id: number | string) =>
    apiClient.get(`/api/v1/rh/portail/bulletins/${id}/telecharger`, { responseType: 'blob' }),
  telechargerDocument: (documentId: number) =>
    apiClient.get(`/api/v1/rh/portail/documents/${documentId}/fichier`, { responseType: 'blob' }),
  telechargerAttestationTravail: () =>
    apiClient.get('/api/v1/rh/portail/documents/attestation-travail', { responseType: 'blob' }),
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
  getPasserellesEnAttente: () => apiClient.get('/api/v1/gateway', { params: { statut: 'en_attente' } }).then(r => r.data),
  getPasserelles: () => apiClient.get('/api/v1/gateway').then(r => r.data),
  getAll: (params?: Record<string, unknown>) => apiClient.get('/api/v1/gateway', { params }),
  getStats: () => apiClient.get('/api/v1/gateway/stats'),
  getById: (id: number) => apiClient.get(`/api/v1/gateway/${id}`),
  create: (data: unknown) => apiClient.post('/api/v1/gateway', data),
  update: (id: number, data: unknown) => apiClient.put(`/api/v1/gateway/${id}`, data),
  ping: (id: number) => apiClient.post(`/api/v1/gateway/${id}/ping`),
  delete: (id: number) => apiClient.delete(`/api/v1/gateway/${id}`),
};

export const aiAPI = {
  sendMessage: (message: string) => apiClient.post('/api/v1/ai/assistant/chat', { message })
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
  getTransits: (params?: Record<string, unknown>) => apiClient.get('/api/v1/transit/dossiers', { params }),
  getTransit: (id: number) => apiClient.get(`/api/v1/transit-avance/dossiers/${id}`),
  createTransit: (data: unknown) => apiClient.post('/api/v1/transit-avance/dossiers', data),
  updateTransit: (id: number, data: unknown) => apiClient.put(`/api/v1/transit-avance/dossiers/${id}`, data),
  deleteTransit: (id: number) => apiClient.delete(`/api/v1/transit-avance/dossiers/${id}`)
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
  getCotations: () => apiClient.get('/api/v1/k-modules/cotations'),
  createCotation: (data: unknown) => apiClient.post('/api/v1/k-modules/cotations', data),
};

// ─── Service Tracking & e-POD ──────────────────────────────────────────
export const trackingAPI = {
  getEpods: () => apiClient.get('/api/v1/transport-international/preuves-livraison'),
  createEpod: (data: unknown) => apiClient.post('/api/v1/transport-international/preuves-livraison', data),
};

// ─── Service FuelGuard Anti-Fraude ──────────────────────────────────────────
export const fuelGuardAPI = {
  getSensors: () => apiClient.get('/api/v1/k-modules/fuel-guard/sensors'),
  createSensor: (data: unknown) => apiClient.post('/api/v1/k-modules/fuel-guard/sensors', data),
};

// ─── Service Procurement & Achats ──────────────────────────────────────────
export const procurementAPI = {
  getOrders: () => apiClient.get('/api/v1/k-modules/procurement/orders'),
  createOrder: (data: unknown) => apiClient.post('/api/v1/k-modules/procurement/orders', data),
};

// ─── Service Compliance & Réglementation ──────────────────────────────────────────
export const complianceAPI = {
  getAudits: () => apiClient.get('/api/v1/k-modules/compliance/audits'),
  createAudit: (data: unknown) => apiClient.post('/api/v1/k-modules/compliance/audits', data),
};

// ─── Service BI & Analytics Executive ──────────────────────────────────────────
export const biAnalyticsAPI = {
  getSummary: () => apiClient.get('/api/v1/k-modules/bi-analytics/executive-summary'),
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
  getDossiers: (clientId?: number) => apiClient.get('/api/v1/b2b-portal/dossiers', { params: clientId ? { client_id: clientId } : undefined }),
  getFactures: (clientId?: number) => apiClient.get('/api/v1/b2b-portal/factures', { params: clientId ? { client_id: clientId } : undefined }),
  createQuote: (data: unknown) => apiClient.post('/api/v1/b2b-portal/quotes', data),
  createBooking: (data: unknown) => apiClient.post('/api/v1/b2b-portal/booking', data),
  trackCargo: (query: string) => apiClient.get(`/api/v1/b2b-portal/tracking/${encodeURIComponent(query)}`),
  processPayment: (data: unknown) => apiClient.post('/api/v1/b2b-portal/payments/checkout', data),
  getNotificationPreferences: (clientId?: number) => apiClient.get('/api/v1/b2b-portal/notifications/preferences', { params: clientId ? { client_id: clientId } : undefined }),
  updateNotificationPreferences: (data: unknown, clientId?: number) => apiClient.put('/api/v1/b2b-portal/notifications/preferences', data, { params: clientId ? { client_id: clientId } : undefined }),
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
  // Batch 16 (circuit de signature) : refus motivé obligatoire et édition PDF.
  // Un bon ne se « valide » JAMAIS par update() : statut figé côté backend.
  refuse: (id: number, motif: string) =>
    apiClient.post(`/api/v1/magasin/removal-slips/${id}/refuse`, { motif }),
  getPdf: (id: number) =>
    apiClient.get(`/api/v1/magasin/removal-slips/${id}/pdf`, { responseType: 'blob' }),
  delete: (id: number) => apiClient.delete(`/api/v1/magasin/removal-slips/${id}`),
};

// ─── Inventaires tournants (circuit réel Batch 18, /magasin-avance) ─────
// POST /inventaires ouvre une campagne (numero genere cote route),
// POST /inventaires/{id}/lignes enregistre un comptage (theorique lu sur
// la colonne reelle), PUT /inventaires/{id}/valider ajuste le stock ET
// journalise chaque ecart dans MouvementStock. Ne pas confondre avec
// /magasin-avance/receptions (bons de reception fournisseur, Batch 19).
export const inventaireAPI = {
  create: (data: {
    entrepot_id: number;
    date_debut: string;
    date_fin?: string;
    type_inventaire?: string;
    notes?: string;
  }) => apiClient.post('/api/v1/magasin-avance/inventaires', data),
  ajouterLigne: (inventaireId: number, data: {
    stock_id: number;
    quantite_comptee: number;
    operateur?: number;
    commentaires?: string;
  }) => apiClient.post(`/api/v1/magasin-avance/inventaires/${inventaireId}/lignes`, data),
  valider: (inventaireId: number) =>
    apiClient.put(`/api/v1/magasin-avance/inventaires/${inventaireId}/valider`),
  precision: (inventaireId: number) =>
    apiClient.get(`/api/v1/magasin-avance/inventaires/${inventaireId}/precision`),
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

// --- Service Documents / GED (archivage legal inclus) -------------------------
// L'ecran d'archive ne telecharge rien : la GED ne possede pas de route de
// delivrance de fichier. Seules les routes existantes du routeur
// /api/v1/documents sont exposees ici.
export const documentsAPI = {
  getDocuments: (params?: Record<string, unknown>) =>
    apiClient.get('/api/v1/documents/', { params }),
  getArchivagesLegal: (params?: Record<string, unknown>) =>
    apiClient.get('/api/v1/documents/archivages-legal', { params }),
  creerArchivageLegal: (data: {
    document_id: number;
    type_archivage: string;
    duree_conservation: number;
    autorite_archivage: string;
    classification?: string;
  }) => apiClient.post('/api/v1/documents/archivages-legal', data),
  mettreAJourArchivageLegal: (id: number, data: Record<string, unknown>) =>
    apiClient.put(`/api/v1/documents/archivages-legal/${id}`, data),
};

export default apiClient;

