/**
 * Types du module Transport International — alignés sur les vrais schémas
 * backend (`app/schemas/transport_international.py`, `app/models/
 * transport_international.py::StatutTransport`).
 *
 * Historique (batch 12) :
 *   `transport-international/page.tsx` lisait `o.numero_ordre`, `o.mode_transport`,
 *   `o.pays_depart`, `o.incoterm`, `o.poids_kg` — **aucun** de ces champs
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

/** StatutTransport (models/transport_international.py::StatutTransport) —
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
