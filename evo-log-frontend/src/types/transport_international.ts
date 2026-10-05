/**
 * Types du module Transport International  alignés sur les vrais schémas
 * backend (`app/schemas/transport_international.py`, `app/models/
 * transport_international.py::StatutTransport`).
 *
 * Historique (batch 12) :
 *   `transport-international/page.tsx` lisait `o.numero_ordre`, `o.mode_transport`,
 *   `o.pays_depart`, `o.incoterm`, `o.poids_kg`  **aucun** de ces champs
 *   n'existe dans `OrdreTransportResponse` (le backend a `numero_ot`,
 *   `type_transit`, `lieu_chargement`, pas d'incoterm, `poids_net` /
 *   `poids_brut`). Les comparaisons de statut utilisaient des chaînes
 *   accentuées ('"livré"', "'annulé'", "'créé'") alors que l'enum backend est
 *   non accentué (`LIVRE = "livre"`, `ANNULE = "annule"`, `PLANIFIE = "planifie"`).
 *   Comme aucune de ces fautes n'était typée, le tableau s'affichait
 *   systématiquement vide, les compteurs "En transit / Livrés" restaient
 *   à 0, et aucun bouton d'action ne se déclenchait.
 *
 * Règle : chaque champ correspond EXACTEMENT au Pydantic du backend.
 * Date/DateTime Pydantic → string ISO côté JSON.
 */

/** StatutTransport (models/transport_international.py::StatutTransport) 
 *  valeurs NON accentuées, telles que sérialisées par l'API. */
export type StatutTransport =
  | 'planifie'
  | 'en_chargement'
  | 'en_transit'
  | 'livre'
  | 'retard'
  | 'annule'
  | 'incident';

/** TypeTransitRoutier (models/transport_international.py::TypeTransitRoutier). */
export type TypeTransitRoutier = 'tir' | 't1' | 't2' | 'national';

/**
 * OrdreTransportResponse (schemas/transport_international.py::OrdreTransportResponse).
 * GET /api/v1/transport-international/ordres-transport (ajouté batch 12)
 * renvoie List[OrdreTransportResponse].
 */
export interface OrdreTransportResponse {
  id: number;
  numero_ot: string;
  client_id: number;
  transporteur_id: number;
  camion_id: number;
  conducteur_id: number;
  type_transit: TypeTransitRoutier | string;
  lieu_chargement: string;
  lieu_livraison: string;
  pays_destination: string;
  code_pays_destination: string;
  marchandise: string;
  poids_net: number;
  poids_brut: number;
  nombre_colis: number;
  valeur_marchandise: number;
  montant_freight: number;
  statut: StatutTransport | string;
  date_creation: string;
  date_chargement_prevue: string | null;
  date_chargement_reelle: string | null;
  date_livraison_prevue: string | null;
  date_livraison_reelle: string | null;
  volume_m3: number | null;
  devise: string;
  devis: string | null;
  observations: string | null;
  created_at: string;
  updated_at: string | null;
}

/**
 * CarnetTIRResponse (schemas/transport_international.py::CarnetTIRResponse).
 * GET /api/v1/transport-international/carnets-tir (ajouté batch 12).
 * Le champ `statut` est une chaîne libre (modèle SQLAlchemy, pas d'enum),
 * valeurs posées par le service : "actif" | "utilise" | "cloture" | "annule".
 */
export interface CarnetTIRResponse {
  id: number;
  numero_carnet: string;
  ordre_transport_id: number;
  pays_emission: string;
  code_pays_emission: string;
  bureau_depart: string;
  bureau_arrivee: string;
  montant_garantie: number;
  date_emission: string;
  date_validite: string;
  nombre_virements: number;
  bureau_transit: string | null;
  devise: string;
  statut: string;
  observations: string | null;
  created_at: string;
  updated_at: string | null;
}

/**
 * CMRResponse (schemas/transport_international.py::CMRResponse).
 * GET /api/v1/transport-international/cmr renvoie List[CMRResponse].
 * `statut` est une chaîne libre posée par le service : "emis" | "signe" |
 * "livre" | "annule".
 */
export interface CMRResponse {
  id: number;
  numero_cmr: string;
  ordre_transport_id: number;
  expediteur: string;
  destinataire: string;
  transporteur: string;
  lieu_chargement: string;
  lieu_livraison: string;
  marchandise: string;
  poids_net: number;
  poids_brut: number;
  nombre_colis: number;
  type_emballage: string;
  valeur_marchandise: number;
  date_emission: string;
  date_chargement: string | null;
  date_livraison: string | null;
  devise: string;
  instructions_speciales: string | null;
  reserve: string | null;
  signature_expediteur: boolean;
  signature_transporteur: boolean;
  signature_destinataire: boolean;
  statut: string;
  created_at: string;
  updated_at: string | null;
}

/**
 * CorridorCEMACResponse (schemas/transport_international.py::CorridorCEMACResponse).
 * GET /api/v1/transport-international/corridors-cemac renvoie List[...].
 */
export interface CorridorCEMACResponse {
  id: number;
  nom: string;
  pays_depart: string;
  code_pays_depart: string;
  pays_arrivee: string;
  code_pays_arrivee: string;
  distance_km: number;
  duree_estimee_heures: number;
  points_controle: string | null;
  dangers: string | null;
  recommandations: string | null;
  statut: string;
  created_at: string;
  updated_at: string | null;
}

/**
 * GET /api/v1/transport-international/statistiques — agrégats RÉELS calculés
 * en base (comptes/sommes SQL), et non `Array.length` tronqué à la taille de
 * la page. Utilisé pour des KPI exacts quelle que soit la volumétrie.
 */
export interface StatistiquesTransportInternational {
  ordres_transport: {
    total: number;
    par_statut: Record<string, number>;
    tonnage_net: number;
  };
  carnets_tir: number;
  cmr: number;
  corridors_cemac: number;
}

/**
 * CMRResponse (schemas/transport_international.py::CMRResponse).
 * GET /api/v1/transport-international/cmr renvoie List[CMRResponse].
 * `statut` est une chaîne libre posée par le service : "emis" | "signe" |
 * "livre" | "annule".
 */
export interface CMRResponse {
  id: number;
  numero_cmr: string;
  ordre_transport_id: number;
  expediteur: string;
  destinataire: string;
  transporteur: string;
  lieu_chargement: string;
  lieu_livraison: string;
  marchandise: string;
  poids_net: number;
  poids_brut: number;
  nombre_colis: number;
  type_emballage: string;
  valeur_marchandise: number;
  date_emission: string;
  date_chargement: string | null;
  date_livraison: string | null;
  devise: string;
  instructions_speciales: string | null;
  reserve: string | null;
  signature_expediteur: boolean;
  signature_transporteur: boolean;
  signature_destinataire: boolean;
  statut: string;
  created_at: string;
  updated_at: string | null;
}

/**
 * CorridorCEMACResponse (schemas/transport_international.py::CorridorCEMACResponse).
 * GET /api/v1/transport-international/corridors-cemac renvoie List[...].
 */
export interface CorridorCEMACResponse {
  id: number;
  nom: string;
  pays_depart: string;
  code_pays_depart: string;
  pays_arrivee: string;
  code_pays_arrivee: string;
  distance_km: number;
  duree_estimee_heures: number;
  points_controle: string | null;
  dangers: string | null;
  recommandations: string | null;
  statut: string;
  created_at: string;
  updated_at: string | null;
}

/**
 * GET /api/v1/transport-international/statistiques — agrégats RÉELS calculés
 * en base (comptes/sommes SQL), et non `Array.length` tronqué à la taille de
 * la page. Utilisé pour des KPI exacts quelle que soit la volumétrie.
 */
export interface StatistiquesTransportInternational {
  ordres_transport: {
    total: number;
    par_statut: Record<string, number>;
    tonnage_net: number;
  };
  carnets_tir: number;
  cmr: number;
  corridors_cemac: number;
}
