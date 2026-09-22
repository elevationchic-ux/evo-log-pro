// Types généraux pour l'application ERP
export * from './auth'
export * from './magasin'
// export * from './commandes' // Avoid StatutCommande conflict

// Types Transport (placeholder)
export interface Mission {
  id: number
  numero: string
  reference?: string
  statut: string
  chauffeur?: string
  vehicule?: string
  origine?: string
  destination?: string
  type_mission?: string
  type_marchandise?: string
  date_creation: string
}

// Types généraux
export interface User {
  id: number
  email: string
  nom: string
  prenom?: string
  role: string
}

export interface ApiResponse<T> {
  data: T
  message?: string
  success: boolean
}