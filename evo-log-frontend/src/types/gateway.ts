import { apiClient } from '@/lib/api-client';

export interface Passerelle {
  id: number;
  source_module: string;
  source_id: number;
  cible_module: string;
  cible_id?: number;
  type_passerelle: string;
  statut: string;
  donnees_json: Record<string, any>;
  message_erreur?: string;
  date_creation: string;
  date_traitement?: string;
  cree_par?: string;
}

