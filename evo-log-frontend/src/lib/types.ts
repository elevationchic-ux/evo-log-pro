/**
 * TypeScript type definitions for EVO-LOG
 * Matches backend Pydantic schemas
 */

export interface User {
  id: number
  username: string
  email: string
  full_name?: string
  is_active: boolean
  is_superuser: boolean
  agency_id?: number
  roles?: Role[]
}

export interface Role {
  id: number
  name: string
  description?: string
  modules_allowed?: string
  is_active: boolean
}

export interface Agency {
  id: number
  code: string
  name: string
  city?: string
  is_active: boolean
  is_headquarters: boolean
}

export interface Tiers {
  id: number
  code: string
  type: 'client' | 'fournisseur' | 'partenaire'
  name: string
  email?: string
  phone?: string
  address?: string
  city?: string
  is_active: boolean
  credit_limit: number
  balance: number
}

export interface Camion {
  id: number
  immatriculation: string
  marque?: string
  modele?: string
  annee?: number
  capacite_tonnage?: number
  status: string
  kilometrage: number
  is_active: boolean
}

export interface Mission {
  id: number
  reference: string
  camion_id?: number
  conducteur_id?: number
  client_id?: number
  type_mission?: string
  statut: string
  date_debut_prevue?: string
  date_fin_prevue?: string
  point_depart?: string
  point_arrivee?: string
  cout_estime?: number
  cout_reel?: number
}

export interface Facture {
  id: number
  numero: string
  client_id?: number
  date_emission: string
  date_echeance?: string
  statut: string
  montant_ht: number
  montant_tva: number
  montant_ttc: number
  montant_paye: number
  reste_a_payer: number
  devise: string
}

export interface Stock {
  id: number
  code_article: string
  designation: string
  categorie?: string
  unite_mesure?: string
  quantite_disponible: number
  quantite_minimum?: number
  prix_unitaire?: number
  emplacement?: string
  entrepot_id?: number
}

export interface Navire {
  id: number
  nom: string
  imo?: string
  pavillon?: string
  type_navire?: string
  longueur?: number
  largeur?: number
  tonnage?: number
  is_active: boolean
}

export interface Escale {
  id: number
  numero_escale: string
  navire_id?: number
  statut: string
  date_arrivee_prevue?: string
  date_arrivee_reelle?: string
  date_depart_prevue?: string
  date_depart_reelle?: string
  tonnage?: number
  nombre_conteneurs?: number
}

export interface Incident {
  id: number
  reference: string
  type_incident?: string
  severite: string
  statut: string
  date_incident: string
  lieu?: string
  description?: string
  victimes: number
  blesses: number
  deces: number
}