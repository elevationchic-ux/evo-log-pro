import { apiClient } from './client';

// Types
export interface Mission {
  id: string;
  vehicleId: string;
  driverId: string;
  clientId: string;
  origin: string;
  destination: string;
  status: 'PENDING' | 'ASSIGNED' | 'IN_PROGRESS' | 'DELIVERED' | 'CANCELLED';
  estimatedDeparture: string;
  estimatedArrival: string;
  actualDeparture?: string;
  actualArrival?: string;
  cargoDescription?: string;
  weight?: number;
  volume?: number;
  podSignature?: string;
  podPhoto?: string;
  notes?: string;
}

export interface Vehicle {
  id: string;
  registrationNumber: string;
  type: string;
  brand: string;
  model: string;
  year: number;
  status: 'AVAILABLE' | 'IN_MAINTENANCE' | 'OUT_OF_SERVICE' | 'IN_USE';
  mileage: number;
  lastMaintenance?: string;
  nextMaintenance?: string;
  insuranceExpiry?: string;
  technicalControlExpiry?: string;
}

export interface Driver {
  id: string;
  employeeId: string;
  firstName: string;
  lastName: string;
  phone: string;
  licenseNumber: string;
  licenseExpiry: string;
  status: 'AVAILABLE' | 'ON_MISSION' | 'ON_LEAVE' | 'UNAVAILABLE';
  currentVehicleId?: string;
}

// API Functions
export const transportApi = {
  // Missions
  getMissions: (params?: { status?: string; date?: string; page?: number; limit?: number }) =>
    apiClient.get<{ data: Mission[]; total: number }>('/transport/missions', { params }),
  
  getMission: (id: string) => apiClient.get<Mission>(`/transport/missions/${id}`),
  
  createMission: (data: Partial<Mission>) => apiClient.post<Mission>('/transport/missions', data),
  
  updateMission: (id: string, data: Partial<Mission>) => apiClient.patch<Mission>(`/transport/missions/${id}`, data),
  
  assignMission: (missionId: string, vehicleId: string, driverId: string) =>
    apiClient.post<Mission>(`/transport/missions/${missionId}/assign`, { vehicleId, driverId }),
  
  completeMission: (missionId: string, podData: { signature: string; photo?: string; notes?: string }) =>
    apiClient.post<Mission>(`/transport/missions/${missionId}/complete`, podData),

  // Vehicles
  getVehicles: (params?: { status?: string; type?: string }) =>
    apiClient.get<{ data: Vehicle[] }>('/transport/vehicles', { params }),
  
  getVehicle: (id: string) => apiClient.get<Vehicle>(`/transport/vehicles/${id}`),
  
  createVehicle: (data: Partial<Vehicle>) => apiClient.post<Vehicle>('/transport/vehicles', data),
  
  updateVehicle: (id: string, data: Partial<Vehicle>) => apiClient.patch<Vehicle>(`/transport/vehicles/${id}`, data),

  // Drivers
  getDrivers: (params?: { status?: string }) =>
    apiClient.get<{ data: Driver[] }>('/transport/drivers', { params }),
  
  getDriver: (id: string) => apiClient.get<Driver>(`/transport/drivers/${id}`),

  // GPS Tracking
  getVehicleLocation: (vehicleId: string) =>
    apiClient.get<{ lat: number; lng: number; speed: number; heading: string; timestamp: string }>
      (`/transport/gps/${vehicleId}/location`),
  
  getFleetLocations: () =>
    apiClient.get<{ data: Array<{ vehicleId: string; lat: number; lng: number; status: string }> }>
      ('/transport/gps/fleet'),

  // Statistics
  getStats: () => apiClient.get<{
    totalMissions: number;
    activeMissions: number;
    completedToday: number;
    onTimeRate: number;
    activeVehicles: number;
    availableDrivers: number;
  }>('/transport/stats'),
};

export default transportApi;