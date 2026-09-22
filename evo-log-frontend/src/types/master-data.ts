import { apiClient } from '@/lib/api-client';

export interface Article {
  id: string;
  code: string;
  description: string;
  unit: string;
  materialGroup: string;
  weight: number;
  volume: number;
  materialType: string;
  storageConditions: string;
  taxClassification: string;
}

export interface Tier {
  id: string;
  type: 'client' | 'supplier' | 'partner';
  name: string;
  acronym: string;
  entityType: string;
  niu: string;
  rccm: string;
  address: string;
  poBox: string;
  city: string;
  region: string;
  phone: string;
  email: string;
  paymentTerms: string;
  currency: string;
  creditLimit: number;
}

export interface ClientProfile {
  id: string;
  companyName: string;
  acronym: string;
  entityType: string;
  niu: string;
  rccm: string;
  address: string;
  poBox: string;
  city: string;
  region: string;
  phone: string;
  email: string;
  paymentTerms: string;
  currency: string;
  creditLimit: number;
  keyContacts: Array<{ name: string; role: string; phone: string; email: string }>;
}

export interface Supplier {
  id: string;
  code_fournisseur: string;
  raison_sociale: string;
  acronyme: string;
  type_entite: string;
  niu: string;
  rccm: string;
  id_fiscal: string;
  adresse: string;
  boite_postale: string;
  ville: string;
  region: string;
  pays: string;
  telephone: string;
  email: string;
  conditions_paiement: string;
  devise: string;
  limite_credit_xaf: number;
  compte_bancaire: string;
  nom_banque: string;
  categorie: string;
  statut: string;
  est_actif: boolean;
  cree_par: string;
  date_creation: string;
  date_modification: string;
}

