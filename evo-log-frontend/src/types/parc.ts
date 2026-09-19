// API Service for Parc Module

export interface Vehicle {
  id: string;
  plaque: string;
  type: 'camion' | 'remorque' | 'engin';
  chassis: string;
  chauffeur: string;
  pole: string;
  status: 'active' | 'maintenance' | 'inactive';
  fuelLevel: number;
  odometer: number;
  lastMaintenance: string;
}

export interface MaintenanceOrder {
  id: string;
  vehicleId: string;
  type: 'preventive' | 'corrective';
  priority: 'low' | 'medium' | 'high' | 'critical';
  description: string;
  status: 'pending' | 'in_progress' | 'completed';
  createdAt: string;
  completedAt?: string;
}

export interface WorkshopRepair {
  id: number;
  reference: string;
  camion_id: number;
  type_intervention: string;
  description: string;
  statut: string;
  cout_estime: number | null;
  date_entree: string;
  date_sortie_prevue: string | null;
  mecanicien_en_charge: string | null;
}

export interface WorkOrder {
  id: string;
  vehicleId: string;
  description: string;
  parts: Array<{ code: string; quantity: number; price: number }>;
  laborCost: number;
  totalCost: number;
  status: 'draft' | 'submitted' | 'approved' | 'completed';
}

export interface EmplacementParc {
  id: number;
  code_emplacement: string;
  type_emplacement: string;
  statut: string;
  coordonnee_x: number;
  coordonnee_y: number;
}

export interface StockPhysiqueParc {
  id: number;
  numero_conteneur: string;
  type_conteneur: string;
  poids_kg: number;
  date_entree: string;
  statut: string;
  emplacement_id: number;
}

