import { apiClient } from './client';

// Types for Magasin/WMS
export interface Article {
  id: string;
  sku: string;
  name: string;
  description?: string;
  category: string;
  unit: string;
  minStock: number;
  maxStock: number;
  currentStock: number;
  location?: string;
  unitPrice: number;
  supplierId?: string;
}

export interface Reception {
  id: string;
  reference: string;
  supplierId: string;
  purchaseOrderId?: string;
  status: 'PENDING' | 'IN_PROGRESS' | 'COMPLETED' | 'CANCELLED';
  items: ReceptionItem[];
  receivedDate?: string;
  receivedBy?: string;
  notes?: string;
}

export interface ReceptionItem {
  articleId: string;
  quantity: number;
  receivedQuantity?: number;
  condition: 'OK' | 'DAMAGED' | 'PARTIAL';
  location?: string;
  batchNumber?: string;
}

export interface StockMovement {
  id: string;
  articleId: string;
  type: 'IN' | 'OUT' | 'TRANSFER' | 'ADJUSTMENT';
  quantity: number;
  reference: string;
  fromLocation?: string;
  toLocation?: string;
  performedBy?: string;
  timestamp: string;
  notes?: string;
}

export const magasinApi = {
  // Articles
  getArticles: (params?: { category?: string; lowStock?: boolean; search?: string }) =>
    apiClient.get<{ data: Article[]; total: number }>('/magasin/articles', { params }),
  
  getArticle: (id: string) => apiClient.get<Article>(`/magasin/articles/${id}`),
  
  createArticle: (data: Partial<Article>) => apiClient.post<Article>('/magasin/articles', data),
  
  updateArticle: (id: string, data: Partial<Article>) => apiClient.patch<Article>(`/magasin/articles/${id}`, data),

  // Receptions
  getReceptions: (params?: { status?: string; date?: string }) =>
    apiClient.get<{ data: Reception[] }>('/magasin/receptions', { params }),
  
  getReception: (id: string) => apiClient.get<Reception>(`/magasin/receptions/${id}`),
  
  createReception: (data: Partial<Reception>) => apiClient.post<Reception>('/magasin/receptions', data),
  
  updateReception: (id: string, data: Partial<Reception>) => apiClient.patch<Reception>(`/magasin/receptions/${id}`, data),
  
  validateReception: (id: string, items: ReceptionItem[]) =>
    apiClient.post<Reception>(`/magasin/receptions/${id}/validate`, { items }),

  // Stock Movements
  getMovements: (params?: { articleId?: string; type?: string; dateFrom?: string; dateTo?: string }) =>
    apiClient.get<{ data: StockMovement[] }>('/magasin/movements', { params }),
  
  createMovement: (data: Partial<StockMovement>) => apiClient.post<StockMovement>('/magasin/movements', data),

  // Inventory
  triggerInventory: (data: { location?: string; articleIds?: string[] }) =>
    apiClient.post<{ id: string }>('/magasin/inventory/trigger', data),
  
  getInventoryStatus: () => apiClient.get<{ inProgress: boolean; lastCompleted?: string }>('/magasin/inventory/status'),

  // Locations
  getLocations: () => apiClient.get<{ data: Array<{ id: string; name: string; zone: string; capacity: number; currentStock: number }> }>('/magasin/locations'),

  // Stats
  getStats: () => apiClient.get<{
    totalArticles: number;
    lowStockCount: number;
    movementsToday: number;
    receptionsPending: number;
    occupancyRate: number;
  }>('/magasin/stats'),
};

export default magasinApi;