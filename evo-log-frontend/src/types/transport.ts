// API Service for Transport Module

export interface Mission {
  id: string;
  reference: string;
  origin: string;
  destination: string;
  merchandise: string;
  status: 'pending' | 'in_progress' | 'completed' | 'cancelled';
  createdAt: string;
}

export interface FuelTicket {
  id: string;
  vehicleId: string;
  driverId: string;
  date: string;
  volume: number;
  unitPrice: number;
  total: number;
  fuelType: 'diesel' | 'essence';
}

export interface Container {
  id: string;
  number: string;
  blNumber: string;
  type: string;
  status: 'pending' | 'loaded' | 'unloaded';
  vgm: number;
}

export interface GoodsDeclaration {
  id: string;
  numero_declaration: string;
  code_article: string;
  code_transit: string;
  description: string;
  quantite: number;
  unite: string;
  poids_kg: number;
  valeur_xaf: number;
  origine: string;
  destination: string;
  numero_conteneur: string;
  observations: string;
  statut: string;
  cree_par: string;
  date_creation: string;
  date_modification: string;
}

