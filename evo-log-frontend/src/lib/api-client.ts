/**
 * Unified API client exports
 * Re-exports apiClient and specific API modules
 */
export { default as api } from './api'

// Basic API modules
export const financeAPI = {
  getKpis: async () => {
    const response = await import('./api').then(m => m.default.get('/api/v1/finance/kpis'))
    return response.data
  },
  getAnalyticsChartData: async () => {
    const response = await import('./api').then(m => m.default.get('/api/v1/finance/analytics'))
    return response.data
  }
}

export const transportAPI = {
  getKpis: async () => {
    const response = await import('./api').then(m => m.default.get('/api/v1/transport/kpis'))
    return response.data
  },
  getEmplacements: async () => {
    const response = await import('./api').then(m => m.default.get('/api/v1/parc/emplacements'))
    return response.data
  },
  getStocksActifs: async () => {
    const response = await import('./api').then(m => m.default.get('/api/v1/parc/stocks-actifs'))
    return response.data
  },
  createChauffeur: async (data: any) => {
    const response = await import('./api').then(m => m.default.post('/api/v1/transport/chauffeurs', data))
    return response.data
  },
  getChauffeurs: async () => {
    const response = await import('./api').then(m => m.default.get('/api/v1/transport/chauffeurs'))
    return response.data
  }
}

export const adminAPI = {
  getDashboardKpis: async () => {
    const response = await import('./api').then(m => m.default.get('/api/v1/admin/dashboard-kpis'))
    return response.data
  }
}

export const parcAPI = {
  getEmplacements: async () => {
    const response = await import('./api').then(m => m.default.get('/api/v1/parc/emplacements'))
    return response.data
  },
  getStocksActifs: async () => {
    const response = await import('./api').then(m => m.default.get('/api/v1/parc/stocks-actifs'))
    return response.data
  },
  getZones: async () => {
    const response = await import('./api').then(m => m.default.get('/api/v1/parc/zones'))
    return response.data
  }
}

export const procurementAPI = {
  getOrders: async () => {
    const response = await import('./api').then(m => m.default.get('/api/v1/procurement/orders'))
    return response.data
  },
  createOrder: async (data: any) => {
    const response = await import('./api').then(m => m.default.post('/api/v1/procurement/orders', data))
    return response.data
  }
}