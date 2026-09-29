/**
 * Types du module Transport  ALIGNED avec les vrais schémas backend.
 *
 * Historique (P1 #5 quick-win, batch 10) :
 *   ce fichier déclarait une interface `Mission` avec `id: string`,
 *   `origin`, `destination`, `merchandise`, `status: 'pending' |
 *   'in_progress' | ...`  AUCUN de ces champs n'existe dans
 *   `MissionResponse` backend (schemas/transport.py). Le type était du
 *   coup jamais importé (grep `from '@/types/transport'` : 0 résultat),
 *   et les pages roulaient en `any`. Résultat : une faute de frappe sur
 *   `point_depart` ou une comparaison `statut === 'PLANIFIEE'` passait
 *   inaperçue (le bug des KPI figés à 0 en est la trace).
 *
 * Règle : chaque champ listé ici correspond EXACTEMENT à un champ
 * Pydantic exposé par l'API. Les datetime sont sérialisés en ISO string.
 * Toute jointure (camion / chauffeur) est récupérée par une REQUÊTE
 * séparée côté page : `MissionResponse` ne renvoie que les FK brutes.
 */

/** MissionStatus (app/schemas/transport.py::MissionStatus) */
export type MissionStatut =
  | 'planifiee'
  | 'en_cours'
  | 'terminee'
  | 'annulee'
  | 'en_retard';

/** CamionStatus (app/schemas/transport.py::CamionStatus) */
export type CamionStatut =
  | 'active'
  | 'in_maintenance'
  | 'out_of_service'
  | 'reserved';

/**
 * MissionResponse (schemas/transport.py::MissionResponse)  GET /missions
 * inclut les colonnes de rattachement documentaire ajoutées par la
 * migration 024 (conteneur_id, numero_bl) : elles ne sont JAMAIS déduites,
 * seulement saisies explicitement sur la ligne.
 */
export interface MissionResponse {
  id: number;
  reference: string;
  camion_id: number | null;
  conducteur_id: number | null;
  client_id: number | null;
  conteneur_id?: number | null;
  numero_bl?: string | null;
  type_mission: string | null;
  statut: MissionStatut;
  point_depart: string | null;
  point_arrivee: string | null;
  distance_km: number | null;
  cout_estime: number | null;
  cout_reel: number | null;
  notes: string | null;
  date_debut_prevue: string | null;
  date_fin_prevue: string | null;
  date_debut_reelle: string | null;
  date_fin_reelle: string | null;
  created_at: string;
  updated_at: string | null;
}

/**
 * CamionResponse (schemas/transport.py::CamionResponse).
 * Attention : `c.status` (nom backend) et non `c.statut`  le backend
 * mélange les deux selon les modules, celui-ci a retenu `status`.
 */
export interface CamionResponse {
  id: number;
  immatriculation: string;
  marque: string | null;
  modele: string | null;
  annee: number | null;
  capacite_tonnage: number | null;
  status: CamionStatut;
  kilometrage: number;
  date_mise_service: string | null;
  derniere_maintenance: string | null;
  prochaine_maintenance: string | null;
  is_active: boolean;
  created_at: string;
  updated_at: string | null;
}

/** ConducteurResponse (schemas/transport.py::ConducteurResponse). */
export interface ConducteurResponse {
  id: number;
  nom: string;
  prenom: string;
  numero_permis: string;
  date_expiration_permis: string | null;
  telephone: string;
  email: string | null;
  adresse: string | null;
  is_active: boolean;
  date_embauche: string | null;
  created_at: string;
  updated_at: string | null;
}

/** Point de passage d'un corridor CEMAC (services/transport_international_service). */
export interface CorridorPointPassage {
  ville: string;
  statut: 'ACTIF' | 'FERME';
  lat: number | null;
  lng: number | null;
}

/** Corridor renvoyé par GET /api/v1/transport/corridors-cemac. */
export interface CorridorCEMAC {
  code: string;
  axe: string;
  distance_km: number | null;
  duree_moyenne_jours: number | null;
  convois_actifs: number;
  points_passage: CorridorPointPassage[];
  regime_douane: string;
  etat_route: string | null;
  risques: string[];
  escorte_douaniere_obligatoire: null;
}

/** Réponse de /corridors-cemac : `total_camions_en_transit` est NULL si
 *  la base ne le prouve pas (conventions zéro-mock). */
export interface CorridorsCEMACResponse {
  zone: string;
  total_camions_en_transit: number | null;
  corridors: CorridorCEMAC[];
  source: string;
  last_check: string;
}

/** Alerte de maintenance prédictive (get_tco_fleet_analytics). */
export interface AlerteMaintenancePredictive {
  camion_id: number;
  immatriculation: string;
  type: string;
  km_compteur: number | null;
  alerte: string;
  echeance: string | null;
  panne_reference?: string;
  priorite: 'CRITIQUE' | 'HAUTE' | string;
}

/** Réponse de GET /api/v1/transport/flotte/tco. */
export interface TcoFleetResponse {
  flotte_totale_vehicules: number;
  vehicules_en_maintenance: number;
  cout_global_moyen_km_xaf: number | null;
  missions_terminees_prises_en_compte: number;
  distance_totale_km_prouvee: number;
  total_frais_justifies_xaf: number;
  devis_monetaire: 'XAF';
  repartition_tco: Record<string, number>;
  alertes_maintenance_predictive: AlerteMaintenancePredictive[];
  source: string;
  note: string | null;
}

/* --------------------------------------------------------------------------
 * Alias de compatibilité (NE PAS UTILISER dans du nouveau code) :
 * d'anciens écrans importeront peut-être encore `Mission` sous ce nom.
 * L'alias renvoie désormais vers la forme RÉELLE ; les consumers qui
 * lisaient `origin` / `destination` / `status` en anglais cassent au
 * typage → tsc les signale explicitement.
 * -------------------------------------------------------------------------- */
export type Mission = MissionResponse;
